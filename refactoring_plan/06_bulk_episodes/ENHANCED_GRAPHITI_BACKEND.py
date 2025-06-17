"""
Enhanced Graphiti Backend with Bulk Episode Processing
Extends the existing GraphitiBackend with add_episode_bulk functionality
"""

import os
import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

# Ensure graphiti_core is installed
try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    from graphiti_core.schemas import Episode, Document, Entity, RawEpisode
    from graphiti_core.search.search_config_recipes import (
        NODE_HYBRID_SEARCH_EPISODE_MENTIONS, 
        EPISODE_HYBRID_SEARCH, 
        DOCUMENT_HYBRID_SEARCH
    )
except ImportError:
    print("Error: graphiti-core library is not installed. Please install it to use GraphitiBackend.")
    raise

from .memory_abstraction import MemoryBackend, MemoryDocument, MemoryConfig

# Default model for embeddings if not specified
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"

class EnhancedGraphitiBackend(MemoryBackend):
    """Enhanced Graphiti temporal knowledge graph backend with bulk processing"""

    def __init__(self):
        self.client: Optional[Graphiti] = None
        self.user_node_uuid: Optional[str] = None
        self.agent_node_uuid: Optional[str] = None
        self.group_id: Optional[str] = None
        self.embeddings_model_name: str = DEFAULT_EMBEDDING_MODEL
        self.bulk_batch_size: int = 100  # Default batch size
        self.bulk_timeout: int = 300     # Default timeout in seconds

    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize Graphiti client and create agent/user nodes"""
        graphiti_config = config.graphiti_config
        if not graphiti_config:
            raise ValueError("Graphiti configuration is required for GraphitiBackend")

        # Extract configuration
        self.group_id = graphiti_config.get("group_id", "agent-zero-default")
        self.embeddings_model_name = graphiti_config.get("embeddings_model", DEFAULT_EMBEDDING_MODEL)
        
        # Bulk processing configuration
        self.bulk_batch_size = int(graphiti_config.get("bulk_batch_size", 100))
        self.bulk_timeout = int(graphiti_config.get("bulk_timeout", 300))

        # Initialize Graphiti client
        try:
            self.client = Graphiti(
                uri=graphiti_config["uri"],
                user=graphiti_config["user"],
                password=graphiti_config["password"],
                group_id=self.group_id,
            )
            
            # Ensure OPENAI_API_KEY is set for embeddings
            if not os.getenv("OPENAI_API_KEY"):
                print("Warning: OPENAI_API_KEY not set, Graphiti operations requiring embeddings might fail.")

        except Exception as e:
            print(f"Failed to initialize Graphiti client: {e}")
            raise RuntimeError(f"Graphiti client initialization failed: {e}")

    def _to_memory_document(self, item: Any, score: Optional[float] = None) -> MemoryDocument:
        """Convert a Graphiti Episode or Document to a MemoryDocument"""
        if isinstance(item, Episode):
            return MemoryDocument(
                id=str(item.uuid),
                page_content=item.episode_body,
                metadata={
                    "name": item.name,
                    "source": item.source.value if isinstance(item.source, EpisodeType) else item.source,
                    "reference_time": item.reference_time.isoformat() if item.reference_time else None,
                    "source_description": item.source_description,
                    "group_id": item.group_id,
                    **(item.metadata or {})
                },
                score=score
            )
        elif isinstance(item, Document):
            return MemoryDocument(
                id=str(item.uuid),
                page_content=item.text_content,
                metadata={
                    "name": item.name,
                    "source_uri": item.source_uri,
                    "reference_time": item.reference_time.isoformat() if item.reference_time else None,
                    "source_description": item.source_description,
                    "group_id": item.group_id,
                    **(item.metadata or {})
                },
                score=score
            )
        else:
            # Fallback for unknown types
            return MemoryDocument(
                id=str(getattr(item, 'uuid', uuid.uuid4())),
                page_content=str(item),
                metadata={"type": type(item).__name__},
                score=score
            )

    def _parse_reference_time(self, reference_time: Any) -> datetime:
        """Parse reference time from various formats"""
        if reference_time and isinstance(reference_time, str):
            return datetime.fromisoformat(reference_time.replace("Z", "+00:00"))
        elif isinstance(reference_time, datetime):
            return reference_time
        else:
            return datetime.now(timezone.utc)

    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Insert text as a Graphiti episode (typically for agent memory)"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        area = metadata.get("area", "main")
        source_description = metadata.get("source_description", f"agent-zero-{area}")
        name = metadata.get("name", f"Memory: {area.title()}")
        reference_time = self._parse_reference_time(metadata.get("timestamp"))

        # Remove standard keys from metadata before passing to Graphiti
        graphiti_metadata = {k: v for k, v in metadata.items() 
                           if k not in ["area", "name", "timestamp", "source_description"]}

        episode_uuid = await self.client.add_episode(
            name=name,
            episode_body=text,
            source=EpisodeType.message,
            reference_time=reference_time,
            source_description=source_description,
            embedding_text=text,
            embedding_model=self.embeddings_model_name,
            metadata=graphiti_metadata
        )
        return str(episode_uuid)

    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction using Graphiti"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        source_description = metadata.get("source_description", 
                                        f"agent-zero-knowledge-{metadata.get('area', 'main')}")
        name = metadata.get("name", f"Knowledge Document: {metadata.get('filename', 'Unknown')}")
        reference_time = self._parse_reference_time(metadata.get("timestamp"))
        source_uri = metadata.get("source_uri", f"agent-zero://{metadata.get('filename', 'unknown')}")

        # Remove standard keys from metadata
        graphiti_metadata = {k: v for k, v in metadata.items() 
                           if k not in ["area", "name", "timestamp", "source_description", "source_uri"]}

        # Using add_document for knowledge, which implies entity extraction
        doc_uuid = await self.client.add_document(
            name=name,
            text_content=content,
            source_uri=source_uri,
            reference_time=reference_time,
            source_description=source_description,
            embedding_text=content,
            embedding_model=self.embeddings_model_name,
            metadata=graphiti_metadata
        )
        return str(doc_uuid)

    async def add_episode_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
        """Add multiple episodes efficiently using Graphiti's bulk API"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")
        
        if not episodes:
            return []

        # Convert to RawEpisode format
        raw_episodes = []
        for episode_data in episodes:
            # Determine episode type
            source = episode_data.get("source", EpisodeType.text)
            if isinstance(source, str):
                source = getattr(EpisodeType, source.upper(), EpisodeType.text)
            
            # Handle content based on type
            content = episode_data["content"]
            if isinstance(content, dict):
                content = json.dumps(content)
            
            raw_episode = RawEpisode(
                name=episode_data.get("name", "Bulk Episode"),
                content=content,
                source=source,
                source_description=episode_data.get("source_description", "agent-zero-bulk"),
                reference_time=self._parse_reference_time(episode_data.get("reference_time"))
            )
            raw_episodes.append(raw_episode)

        # Process in batches to avoid overwhelming the system
        all_uuids = []
        for i in range(0, len(raw_episodes), self.bulk_batch_size):
            batch = raw_episodes[i:i + self.bulk_batch_size]
            try:
                # Use Graphiti's bulk API
                batch_uuids = await self.client.add_episode_bulk(batch)
                all_uuids.extend([str(uuid) for uuid in batch_uuids])
            except Exception as e:
                print(f"Bulk processing failed for batch {i//self.bulk_batch_size + 1}: {e}")
                # Fallback to individual processing for this batch
                batch_uuids = await self._process_episodes_individually(batch)
                all_uuids.extend(batch_uuids)

        return all_uuids

    async def _process_episodes_individually(self, raw_episodes: List[RawEpisode]) -> List[str]:
        """Fallback method to process episodes individually"""
        uuids = []
        for raw_episode in raw_episodes:
            try:
                episode_uuid = await self.client.add_episode(
                    name=raw_episode.name,
                    episode_body=raw_episode.content,
                    source=raw_episode.source,
                    source_description=raw_episode.source_description,
                    reference_time=raw_episode.reference_time,
                    embedding_text=raw_episode.content,
                    embedding_model=self.embeddings_model_name
                )
                uuids.append(str(episode_uuid))
            except Exception as e:
                print(f"Failed to process individual episode '{raw_episode.name}': {e}")
                # Continue with other episodes
                continue
        return uuids

    async def insert_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple knowledge documents with entity extraction"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")
        
        if not documents:
            return []

        # For knowledge documents, we can use the episode bulk API with document type
        # or process them individually if they need special handling
        episodes_data = []
        for doc in documents:
            episode_data = {
                "name": doc.get("name", f"Knowledge Document: {doc.get('metadata', {}).get('filename', 'Unknown')}"),
                "content": doc["content"],
                "source": EpisodeType.json if isinstance(doc["content"], dict) else EpisodeType.text,
                "source_description": doc.get("source_description", 
                                            f"agent-zero-knowledge-{doc.get('metadata', {}).get('area', 'main')}"),
                "reference_time": doc.get("reference_time")
            }
            episodes_data.append(episode_data)

        # Use bulk episode processing for knowledge documents
        return await self.add_episode_bulk(episodes_data)

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryDocument]:
        """Search for similar documents using Graphiti's hybrid search"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        try:
            # Use Graphiti's hybrid search for episodes
            search_results = await self.client.search(
                query=query,
                config=EPISODE_HYBRID_SEARCH,
                limit=limit
            )

            # Convert results to MemoryDocument format
            documents = []
            for result in search_results:
                # Apply threshold filtering if score is available
                score = getattr(result, 'score', None)
                if score is not None and score < threshold:
                    continue

                doc = self._to_memory_document(result, score)
                documents.append(doc)

            return documents[:limit]

        except Exception as e:
            print(f"Search failed: {e}")
            return []

    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Delete documents by IDs and return deleted documents"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        deleted_docs = []
        for doc_id_str in ids:
            try:
                doc_uuid = uuid.UUID(doc_id_str)

                # Try to fetch the document first to return it
                try:
                    # This is a simplified approach - in practice, you'd need to determine
                    # if it's an Episode or Document to call the right method
                    episode = await self.client.get_episode(doc_uuid)
                    if episode:
                        deleted_docs.append(self._to_memory_document(episode))
                        await self.client.delete_episode(doc_uuid)
                except:
                    # Try as document if episode fetch fails
                    try:
                        document = await self.client.get_document(doc_uuid)
                        if document:
                            deleted_docs.append(self._to_memory_document(document))
                            await self.client.delete_document(doc_uuid)
                    except:
                        print(f"Could not find or delete document with ID: {doc_id_str}")

            except ValueError:
                print(f"Invalid UUID format: {doc_id_str}")
            except Exception as e:
                print(f"Error deleting document {doc_id_str}: {e}")

        return deleted_docs

    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Get documents by their IDs"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        documents = []
        for doc_id_str in ids:
            try:
                doc_uuid = uuid.UUID(doc_id_str)

                # Try to fetch as episode first
                try:
                    episode = await self.client.get_episode(doc_uuid)
                    if episode:
                        documents.append(self._to_memory_document(episode))
                        continue
                except:
                    pass

                # Try to fetch as document
                try:
                    document = await self.client.get_document(doc_uuid)
                    if document:
                        documents.append(self._to_memory_document(document))
                except:
                    print(f"Could not find document with ID: {doc_id_str}")

            except ValueError:
                print(f"Invalid UUID format: {doc_id_str}")
            except Exception as e:
                print(f"Error fetching document {doc_id_str}: {e}")

        return documents
