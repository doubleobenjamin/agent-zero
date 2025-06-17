# CORRECTED: Enhanced Graphiti Backend Implementation
# This file contains the corrected implementation based on actual Graphiti API
# Enhanced to support unified memory and knowledge processing

import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

class EnhancedGraphitiBackend:
    """Enhanced Graphiti temporal knowledge graph backend - CORRECTED"""
    
    def __init__(self):
        self.client: Optional[Graphiti] = None
        self.user_node_uuid: Optional[str] = None
        self.agent_node_uuid: Optional[str] = None
    
    async def initialize(self, config) -> None:
        """Initialize Graphiti client - CORRECTED API usage"""
        graphiti_config = config.graphiti_config
        if not graphiti_config:
            raise ValueError("Graphiti configuration is required")
        
        # CORRECTED: Use actual Graphiti parameter names
        self.client = Graphiti(
            uri=graphiti_config["uri"],           # CORRECTED: uri parameter name
            user=graphiti_config["user"],         # CORRECTED: user parameter name
            password=graphiti_config["password"]  # CORRECTED: password parameter name
        )
        
        # Initialize database schema
        await self.client.build_indices_and_constraints()
        
        # Create or retrieve agent and user nodes
        await self._ensure_agent_nodes(graphiti_config.get("group_id", "default"))
    
    async def _ensure_agent_nodes(self, group_id: str) -> None:
        """Create or retrieve agent and user nodes for this session"""
        try:
            # Create agent node - CORRECTED: Use actual add_episode signature
            agent_episode_uuid = await self.client.add_episode(
                name="Agent Zero Initialization",
                episode_body=f"Agent Zero instance for group {group_id} initialized",
                source_description="agent-zero-system",
                reference_time=datetime.now(timezone.utc),
                source=EpisodeType.message,  # CORRECTED: Default is message, not text
                group_id=group_id
            )
            
            # Create user node  
            user_episode_uuid = await self.client.add_episode(
                name="User Interaction",
                episode_body=f"User interacting with Agent Zero in group {group_id}",
                source_description="agent-zero-user",
                reference_time=datetime.now(timezone.utc),
                source=EpisodeType.message,
                group_id=group_id
            )
            
            # Store UUIDs for later use
            self.agent_node_uuid = agent_episode_uuid
            self.user_node_uuid = user_episode_uuid
            
        except Exception as e:
            print(f"Warning: Could not create agent/user nodes: {e}")
            # Continue without specific nodes
    
    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Insert text as a Graphiti episode - CORRECTED"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")
        
        # Map memory area to episode source description
        area = metadata.get("area", "main")
        source_description = f"agent-zero-{area}"
        
        # CORRECTED: Use actual add_episode signature
        episode_uuid = await self.client.add_episode(
            name=f"Memory: {area.title()}",
            episode_body=text,
            source_description=source_description,
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.message,  # CORRECTED: Use message as default
            group_id=metadata.get("group_id", "default")
        )
        
        return str(episode_uuid)

    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction - CORRECTED"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        # Map memory area to episode source description
        area = metadata.get("area", "main")
        source_description = f"agent-zero-knowledge-{area}"

        # Use document episode type for knowledge documents with entity extraction
        episode_uuid = await self.client.add_episode(
            name=f"Knowledge Document: {metadata.get('filename', 'Unknown')}",
            episode_body=content,
            source=EpisodeType.document,  # Use document type for knowledge
            source_description=source_description,
            reference_time=datetime.now(timezone.utc),
            group_id=metadata.get("group_id", "default"),
            # Additional metadata for knowledge documents
            **{k: v for k, v in metadata.items() if k not in ["area", "content_type", "group_id"]}
        )

        return str(episode_uuid)

    async def search_similarity_threshold(
        self, 
        query: str, 
        limit: int = 10, 
        threshold: float = 0.7,
        filter: str = ""
    ) -> List[Document]:  # CORRECTED: Return Document objects
        """Search Graphiti graph for relevant episodes across memory and knowledge - CORRECTED"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")
        
        try:
            # Use Graphiti search - CORRECTED: Use actual search method
            search_results = await self.client.search(
                query=query,
                limit=limit,
                group_id="default"  # Use default group for now
            )
            
            # Convert to Document objects for compatibility
            documents = []
            for result in search_results:
                # CORRECTED: Create Document objects with page_content and content type detection
                source_desc = getattr(result, 'source_description', '')
                content_type = "knowledge_document" if "knowledge" in source_desc else "agent_memory"

                doc = Document(
                    page_content=getattr(result, 'episode_body', str(result)),
                    metadata={
                        "id": getattr(result, 'uuid', str(uuid.uuid4())),
                        "area": self._extract_area_from_source(source_desc),
                        "content_type": content_type,
                        "timestamp": getattr(result, 'created_at', datetime.now()).isoformat(),
                        "source_description": source_desc,
                        "score": getattr(result, 'score', 1.0)
                    }
                )
                
                # Apply threshold filtering
                score = doc.metadata.get('score', 1.0)
                if score >= threshold:
                    documents.append(doc)
            
            return documents[:limit]
            
        except Exception as e:
            print(f"Search error: {e}")
            return []  # Return empty list on error
    
    def _extract_area_from_source(self, source_description: str) -> str:
        """Extract memory area from Graphiti source description"""
        if source_description.startswith("agent-zero-knowledge-"):
            return source_description.replace("agent-zero-knowledge-", "")
        elif source_description.startswith("agent-zero-"):
            return source_description.replace("agent-zero-", "")
        return "main"
    
    async def delete_documents_by_ids(self, ids: List[str]) -> List[Document]:
        """Delete episodes by IDs - CORRECTED for Graphiti limitations"""
        # Note: Graphiti is designed to be append-only for temporal integrity
        # Instead of deletion, we mark episodes as "deleted" or "deprecated"
        
        deleted_docs = []
        for episode_id in ids:
            try:
                # Add a deprecation episode
                await self.client.add_episode(
                    name="Memory Deletion",
                    episode_body=f"Episode {episode_id} marked as deleted",
                    source_description="agent-zero-deletion",
                    reference_time=datetime.now(timezone.utc),
                    source=EpisodeType.message
                )
                
                # Create a placeholder document for the response
                doc = Document(
                    page_content="[DELETED]",
                    metadata={"id": episode_id, "status": "deleted"}
                )
                deleted_docs.append(doc)
                
            except Exception as e:
                print(f"Failed to mark episode {episode_id} as deleted: {e}")
        
        return deleted_docs
    
    async def delete_documents_by_query(
        self, 
        query: str, 
        threshold: float = 0.75,
        filter: str = ""
    ) -> List[Document]:
        """Delete episodes by query - CORRECTED"""
        # First, find documents matching the query
        documents = await self.search_similarity_threshold(
            query=query, 
            limit=100,  # Large limit to find all matches
            threshold=threshold,
            filter=filter
        )
        
        # Mark each found document as deleted
        ids_to_delete = [doc.metadata["id"] for doc in documents]
        return await self.delete_documents_by_ids(ids_to_delete)
