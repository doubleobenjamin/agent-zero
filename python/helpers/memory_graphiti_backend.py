import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, cast

# Ensure graphiti_core is installed. If not, this will raise an ImportError.
try:
    from graphiti_core import Graphiti
    from graphiti_core.nodes import EpisodeType
    from graphiti_core.schemas import Episode, Document, Entity
    from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_EPISODE_MENTIONS, EPISODE_HYBRID_SEARCH, DOCUMENT_HYBRID_SEARCH
except ImportError:
    # Handle the case where graphiti_core is not installed,
    # perhaps by logging an error or raising a custom exception.
    # For now, we'll re-raise the ImportError to make it clear.
    print("Error: graphiti-core library is not installed. Please install it to use GraphitiBackend.")
    raise

from .memory_abstraction import MemoryBackend, MemoryDocument, MemoryConfig # Relative import

# Default model for embeddings if not specified, aligned with Graphiti's typical usage
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"

class GraphitiBackend(MemoryBackend):
    """Graphiti temporal knowledge graph backend"""

    def __init__(self):
        self.client: Optional[Graphiti] = None
        self.user_node_uuid: Optional[str] = None # Not explicitly used in current methods but kept from guide
        self.agent_node_uuid: Optional[str] = None # Not explicitly used in current methods but kept from guide
        self.group_id: Optional[str] = None
        self.embeddings_model_name: str = DEFAULT_EMBEDDING_MODEL

    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize Graphiti client and create agent/user nodes"""
        graphiti_config = config.graphiti_config
        if not graphiti_config:
            raise ValueError("Graphiti configuration is required for GraphitiBackend")

        self.group_id = graphiti_config.get("group_id", "agent-zero-default")

        # Determine embedding model from agent config or use default
        # Assuming config.embeddings_model might be an object with a 'name' attribute or similar
        if hasattr(config.embeddings_model, 'name'):
            self.embeddings_model_name = config.embeddings_model.name
        elif isinstance(config.embeddings_model, str) and config.embeddings_model:
            self.embeddings_model_name = config.embeddings_model
        else:
            # Fallback if agent.config.embeddings_model is not set or not a string/object with name
            # This could also fetch from OPENAI_EMBEDDINGS_MODEL env var if Graphiti uses it
            self.embeddings_model_name = os.getenv("OPENAI_EMBEDDINGS_MODEL", DEFAULT_EMBEDDING_MODEL)


        # Initialize Graphiti client
        try:
            self.client = Graphiti(
                uri=graphiti_config["uri"],
                user=graphiti_config["user"],
                password=graphiti_config["password"],
                group_id=self.group_id,
                # Graphiti might take embedding model directly or expect it via env var
                # For now, assuming it picks up from env or has its own default if not passed
            )
            # Ensure OPENAI_API_KEY is set for embeddings, Graphiti might check this internally
            if not os.getenv("OPENAI_API_KEY"):
                 print("Warning: OPENAI_API_KEY not set, Graphiti operations requiring embeddings might fail.")

        except Exception as e:
            print(f"Failed to initialize Graphiti client: {e}") # Or use proper logging
            raise RuntimeError(f"Graphiti client initialization failed: {e}")

        # Build database schema (indices and constraints)
        # This is crucial for Graphiti to function correctly.
        try:
            await self.client.build_indices_and_constraints()
        except Exception as e:
            # Log this error, as it might indicate issues with Neo4j connection or permissions
            print(f"Error building Graphiti indices and constraints: {e}")
            # Depending on severity, you might want to raise an exception or allow continuation with a warning
            # raise RuntimeError(f"Failed to build Graphiti schema: {e}")


        # The guide mentions _ensure_agent_nodes, but its direct use for memory ops isn't clear.
        # Graphiti typically associates data with group_id.
        # If specific agent/user nodes are needed for context in searches/inserts,
        # that logic would go here or be part of each operation.
        # For now, relying on group_id for data partitioning.
        # await self._ensure_agent_nodes(self.group_id)
        print(f"GraphitiBackend initialized for group_id: {self.group_id} with embedding model: {self.embeddings_model_name}")


    # The _ensure_agent_nodes from the guide might be for a more complex interaction pattern
    # not directly used by the current set of memory operations.
    # If it becomes necessary, it can be reinstated.
    # async def _ensure_agent_nodes(self, group_id: str) -> None: ...

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
        elif isinstance(item, Document): # Assuming Document is another type from Graphiti
             return MemoryDocument(
                id=str(item.uuid),
                page_content=item.text_content, # Or appropriate field for document text
                metadata={
                    "name": item.name,
                    "source_uri": item.source_uri,
                    "reference_time": item.reference_time.isoformat() if item.reference_time else None,
                    "group_id": item.group_id,
                    **(item.metadata or {})
                },
                score=score
            )
        # Add handling for other types if Graphiti returns them (e.g., Entity)
        raise TypeError(f"Cannot convert type {type(item)} to MemoryDocument")

    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Insert text as a Graphiti episode (typically for agent memory)"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        area = metadata.get("area", "main")
        source_description = metadata.get("source_description", f"agent-zero-{area}")
        name = metadata.get("name", f"Memory: {area.title()}")
        reference_time = metadata.get("timestamp") # Expecting ISO format string or datetime

        if reference_time and isinstance(reference_time, str):
            reference_time = datetime.fromisoformat(reference_time.replace("Z", "+00:00"))
        elif not reference_time:
            reference_time = datetime.now(timezone.utc)

        # Remove standard keys from metadata before passing to Graphiti to avoid conflicts
        graphiti_metadata = {k: v for k, v in metadata.items() if k not in ["area", "name", "timestamp", "source_description"]}

        episode_uuid = await self.client.add_episode(
            name=name,
            episode_body=text,
            source=EpisodeType.message, # As per guide's correction for agent memory
            reference_time=reference_time,
            source_description=source_description,
            embedding_text=text, # Ensure text is passed for embedding
            embedding_model=self.embeddings_model_name,
            metadata=graphiti_metadata
        )
        return str(episode_uuid)

    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction using Graphiti"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        source_description = metadata.get("source_description", f"agent-zero-knowledge-{metadata.get('area', 'main')}")
        name = metadata.get("name", f"Knowledge Document: {metadata.get('filename', 'Unknown')}")
        reference_time = metadata.get("timestamp")

        if reference_time and isinstance(reference_time, str):
            reference_time = datetime.fromisoformat(reference_time.replace("Z", "+00:00"))
        elif not reference_time:
            reference_time = datetime.now(timezone.utc)

        source_uri = metadata.get("source_uri", metadata.get("filename"))

        # Remove standard keys from metadata
        graphiti_metadata = {k: v for k, v in metadata.items() if k not in ["area", "name", "timestamp", "source_description", "filename", "source_uri"]}

        # Using add_document for knowledge, which implies entity extraction if configured in Graphiti
        doc_uuid = await self.client.add_document(
            name=name,
            text_content=content,
            source_uri=source_uri, # Important for identifying the document
            reference_time=reference_time,
            source_description=source_description,
            embedding_text=content, # Ensure text is passed for embedding
            embedding_model=self.embeddings_model_name,
            metadata=graphiti_metadata
            # Entity extraction is usually handled by Graphiti based on its configuration when adding documents
        )
        return str(doc_uuid)

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None # filter is more complex in Graphiti
    ) -> List[MemoryDocument]:
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        # Graphiti's search might involve different parameters for filtering.
        # The 'filter' dict needs to be translated into Graphiti search parameters.
        # This is a simplified example. Graphiti offers more complex search/filter capabilities.
        # For now, we assume filter might contain 'source_description' or 'type' (episode/document)

        search_results = []
        search_config = EPISODE_HYBRID_SEARCH # Default to searching episodes (agent memory)

        # Basic filter interpretation:
        # If filter contains 'content_type': 'knowledge_document', search documents.
        # Otherwise, search episodes. More complex filtering would require more logic.
        if filter and filter.get("content_type") == "knowledge_document":
            search_config = DOCUMENT_HYBRID_SEARCH
            # Potentially use filter values for metadata_filter in Graphiti search
            graphiti_filter = {"metadata": filter} if filter else None
            results = await self.client.search_documents(
                query_text=query,
                search_config=search_config,
                limit=limit,
                # threshold not directly supported in this search call, Graphiti's ranking handles relevance
                # metadata_filter=graphiti_filter
            )
            for doc_node, score in results: # Assuming search_documents returns (node, score)
                if score >= threshold: # Manual threshold application
                    search_results.append(self._to_memory_document(doc_node, score))
        else:
            # Potentially use filter values for metadata_filter in Graphiti search
            graphiti_filter = {"metadata": filter} if filter else None
            results = await self.client.search_episodes(
                query_text=query,
                search_config=search_config,
                limit=limit,
                # threshold not directly supported, Graphiti's ranking handles relevance
                # metadata_filter=graphiti_filter
            )
            for episode_node, score in results: # Assuming search_episodes returns (node, score)
                 if score >= threshold: # Manual threshold application
                    search_results.append(self._to_memory_document(episode_node, score))

        return search_results


    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        deleted_docs_info = []
        # Graphiti might not return full document details on delete.
        # We might need to fetch them first if we need to return them.
        # For now, assume we just confirm deletion.
        # This is a placeholder as Graphiti's delete might be by node UUID directly.

        # Fetch documents first to return their details
        # This assumes IDs are Graphiti UUIDs
        # Graphiti's `get_episode_by_uuid` or `get_document_by_uuid` might be needed
        # For simplicity, let's assume we can't easily retrieve them before deletion in one go.
        # So, we'll return minimal info or an empty list, or modify to fetch first.

        # A more robust way:
        # 1. Fetch docs by IDs.
        # 2. Delete them.
        # 3. Return fetched docs.
        # However, Graphiti's primary delete might be `delete_episode` or `delete_document` by UUID.

        # Let's assume IDs are UUIDs and try to delete.
        # Graphiti's delete operations are usually `delete_episode(uuid)` or `delete_document(uuid)`.
        # These typically don't return the deleted item.
        # The plan asks to return List[MemoryDocument]. This is tricky without fetching first.

        # Simplified: We won't return the full MemoryDocument for now, as Graphiti's delete
        # might not support that directly. Or, we'd need separate get calls.
        # This part needs refinement based on exact Graphiti capabilities for bulk delete + return.

        # Placeholder: Iterate and delete one by one.
        # This is inefficient and might not be how Graphiti is designed for bulk ops.
        for doc_id_str in ids:
            try:
                doc_uuid = uuid.UUID(doc_id_str)
                # Need to know if it's an Episode or Document to call the right delete.
                # This is a design issue if IDs don't carry type information.
                # Assuming generic delete_node for now if Graphiti has it, or try both.

                # Attempt to delete as episode, then as document if that fails.
                # This is not ideal. A better way would be to store type with ID or have typed IDs.
                deleted = False
                try:
                    await self.client.delete_episode(episode_uuid=doc_uuid)
                    # If we need to return the document, we should have fetched it before.
                    # For now, creating a dummy MemoryDocument for successful deletion.
                    deleted_docs_info.append(MemoryDocument(id=doc_id_str, page_content="", metadata={"status": "deleted_as_episode"}))
                    deleted = True
                except Exception: # Replace with specific Graphiti "not found" or "wrong type" error
                    pass

                if not deleted:
                    try:
                        await self.client.delete_document(document_uuid=doc_uuid)
                        deleted_docs_info.append(MemoryDocument(id=doc_id_str, page_content="", metadata={"status": "deleted_as_document"}))
                    except Exception as e: # Replace with specific Graphiti error
                        print(f"Failed to delete node {doc_id_str}: {e}")
            except ValueError:
                print(f"Invalid UUID string: {doc_id_str}")
            except Exception as e:
                print(f"Error deleting document/episode {doc_id_str}: {e}")
        return deleted_docs_info # Returns placeholders

    async def delete_documents_by_query(
        self,
        query: str,
        threshold: float = 0.75,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryDocument]:
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        # 1. Search for documents matching the query.
        # This search should ideally return nodes with their UUIDs.
        docs_to_delete = await self.search_similarity_threshold(query, limit=1000, threshold=threshold, filter=filter) # High limit to get all relevant

        # 2. Extract their IDs.
        doc_ids_to_delete = [doc.id for doc in docs_to_delete]

        # 3. Delete them using the delete_documents_by_ids method.
        if doc_ids_to_delete:
            await self.delete_documents_by_ids(doc_ids_to_delete)
            # delete_documents_by_ids already returns List[MemoryDocument] (placeholders in current impl)
            # So, we can return the result of the search, as these are the ones targeted for deletion.
            return docs_to_delete
        return []

    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        retrieved_docs = []
        for doc_id_str in ids:
            try:
                doc_uuid = uuid.UUID(doc_id_str)
                # Similar to delete, we need to know the type or try fetching as both.
                item = None
                try:
                    # Try fetching as Episode
                    episode_node = await self.client.get_episode_by_uuid(episode_uuid=doc_uuid)
                    if episode_node:
                         item = episode_node
                except Exception: # Catch specific "not found" or type errors
                    pass

                if not item:
                    try:
                        # Try fetching as Document
                        doc_node = await self.client.get_document_by_uuid(document_uuid=doc_uuid)
                        if doc_node:
                            item = doc_node
                    except Exception: # Catch specific "not found" or type errors
                        pass

                if item:
                    retrieved_docs.append(self._to_memory_document(item))
                else:
                    print(f"Document/Episode with ID {doc_id_str} not found.") # Or log
            except ValueError:
                print(f"Invalid UUID string for get: {doc_id_str}")
            except Exception as e:
                print(f"Error fetching document/episode {doc_id_str}: {e}")
        return retrieved_docs
