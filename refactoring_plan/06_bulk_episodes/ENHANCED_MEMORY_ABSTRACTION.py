"""
Enhanced Memory Abstraction Layer with Bulk Processing Support
Extends the existing memory abstraction layer with bulk episode processing capabilities
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, TYPE_CHECKING
import os

if TYPE_CHECKING:
    from agent import Agent

@dataclass
class MemoryDocument:
    """Document returned from memory operations"""
    id: str
    page_content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None

@dataclass
class MemoryConfig:
    """Memory backend configuration with bulk processing support"""
    backend_type: str  # "faiss" or "graphiti"
    memory_subdir: str
    embeddings_model: Any
    graphiti_config: Optional[Dict[str, str]] = None
    # Bulk processing configuration
    bulk_processing_enabled: bool = True
    bulk_batch_size: int = 100
    bulk_timeout: int = 300

class EnhancedMemoryBackend(ABC):
    """Enhanced abstract base class for memory backends with bulk processing"""

    @abstractmethod
    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize the memory backend"""
        pass

    @abstractmethod
    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Insert text and return document ID"""
        pass

    @abstractmethod
    async def search_similarity_threshold(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryDocument]:
        """Search for similar documents"""
        pass

    @abstractmethod
    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Delete documents by IDs and return deleted documents"""
        pass

    @abstractmethod
    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Get documents by their IDs"""
        pass

    @abstractmethod
    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction"""
        pass

    # New bulk processing methods
    @abstractmethod
    async def add_episode_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
        """Add multiple episodes efficiently"""
        pass

    @abstractmethod
    async def insert_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple knowledge documents with entity extraction"""
        pass

    def supports_bulk_processing(self) -> bool:
        """Check if backend supports bulk processing"""
        return hasattr(self, 'add_episode_bulk') and callable(getattr(self, 'add_episode_bulk'))

class EnhancedMemoryAbstractionLayer:
    """Enhanced abstraction layer for unified memory and knowledge operations with bulk processing"""

    def __init__(self, agent: 'Agent'):
        self.agent = agent
        self.backend: Optional[EnhancedMemoryBackend] = None
        self.config: Optional[MemoryConfig] = None

    async def initialize(self) -> None:
        """Initialize the appropriate backend based on configuration"""
        backend_type = self._get_backend_type()

        if backend_type == "graphiti":
            from .enhanced_graphiti_backend import EnhancedGraphitiBackend
            self.backend = EnhancedGraphitiBackend()
        else:
            from .enhanced_faiss_backend import EnhancedFaissBackend
            self.backend = EnhancedFaissBackend()

        self.config = self._build_config(backend_type)
        if self.backend is not None:
            await self.backend.initialize(self.config)
        else:
            print(f"Error: Memory backend '{backend_type}' could not be initialized.")

    def _get_backend_type(self) -> str:
        """Determine which backend to use based on configuration"""
        # Check environment variable first
        backend_type = os.getenv("MEMORY_BACKEND", "").lower()
        if backend_type in ["graphiti", "faiss"]:
            return backend_type

        # Check agent configuration
        if hasattr(self.agent, 'config') and hasattr(self.agent.config, 'memory_backend'):
            return self.agent.config.memory_backend.lower()

        # Default to faiss for backward compatibility
        return "faiss"

    def _build_config(self, backend_type: str) -> MemoryConfig:
        """Build configuration for the selected backend"""
        # Extract basic configuration from agent
        memory_subdir = getattr(self.agent.config, 'memory_subdir', 'default')
        embeddings_model = getattr(self.agent.config, 'embeddings_model', None)

        # Bulk processing configuration
        bulk_enabled = os.getenv("MEMORY_BULK_PROCESSING_ENABLED", "true").lower() == "true"
        bulk_batch_size = int(os.getenv("GRAPHITI_BULK_BATCH_SIZE", "100"))
        bulk_timeout = int(os.getenv("GRAPHITI_BULK_TIMEOUT", "300"))

        config = MemoryConfig(
            backend_type=backend_type,
            memory_subdir=memory_subdir,
            embeddings_model=embeddings_model,
            bulk_processing_enabled=bulk_enabled,
            bulk_batch_size=bulk_batch_size,
            bulk_timeout=bulk_timeout
        )

        # Add Graphiti-specific configuration
        if backend_type == "graphiti":
            config.graphiti_config = {
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "password"),
                "group_id": os.getenv("GRAPHITI_GROUP_ID", "agent-zero-default"),
                "embeddings_model": os.getenv("GRAPHITI_EMBEDDINGS_MODEL", "text-embedding-ada-002"),
                "bulk_batch_size": str(bulk_batch_size),
                "bulk_timeout": str(bulk_timeout)
            }

        return config

    async def _ensure_initialized(self):
        """Ensure the backend is initialized"""
        if self.backend is None:
            await self.initialize()

    # Standard memory operations (unchanged from existing implementation)
    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_initialized()
        return await self.backend.insert_text(text, metadata)

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryDocument]:
        await self._ensure_initialized()
        return await self.backend.search_similarity_threshold(query, limit, threshold, filter)

    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_initialized()
        return await self.backend.delete_documents_by_ids(ids)

    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_initialized()
        return await self.backend.get_documents_by_ids(ids)

    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_initialized()
        return await self.backend.insert_knowledge_document(content, metadata)

    async def insert_content(self, content: str, content_type: str, metadata: Dict[str, Any]) -> str:
        """Insert content with type-specific processing"""
        await self._ensure_initialized()

        metadata.setdefault("content_type", content_type)

        if content_type == "knowledge_document":
            return await self.backend.insert_knowledge_document(content, metadata)
        elif content_type == "agent_memory":
            return await self.backend.insert_text(content, metadata)
        else:
            raise ValueError(f"Invalid content_type: {content_type}")

    # Enhanced bulk processing methods
    async def add_episodes_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
        """Add multiple episodes efficiently"""
        await self._ensure_initialized()
        
        if not self.config.bulk_processing_enabled or not self.backend.supports_bulk_processing():
            # Fallback to individual processing
            return await self._process_episodes_individually(episodes)
        
        return await self.backend.add_episode_bulk(episodes)

    async def process_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Process multiple knowledge documents efficiently with entity extraction"""
        await self._ensure_initialized()

        if not documents:
            return []

        # Prepare documents for bulk processing
        prepared_docs = []
        for doc in documents:
            if "content" not in doc:
                continue

            metadata = doc.get("metadata", {})
            prepared_doc = {
                "name": metadata.get("name", f"Knowledge Document: {metadata.get('filename', 'Unknown')}"),
                "content": doc["content"],
                "source": "json" if isinstance(doc["content"], dict) else "text",
                "source_description": metadata.get("source_description", 
                                                 f"agent-zero-knowledge-{metadata.get('area', 'main')}"),
                "reference_time": metadata.get("timestamp"),
                "metadata": {k: v for k, v in metadata.items() 
                           if k not in ["name", "timestamp", "source_description"]}
            }
            prepared_docs.append(prepared_doc)

        # Use bulk processing if available and enabled
        if (self.config.bulk_processing_enabled and 
            self.backend.supports_bulk_processing() and 
            hasattr(self.backend, 'insert_knowledge_documents_bulk')):
            return await self.backend.insert_knowledge_documents_bulk(prepared_docs)
        else:
            # Fallback to individual processing
            doc_ids = []
            for doc in prepared_docs:
                doc_id = await self.backend.insert_knowledge_document(
                    doc["content"], 
                    doc.get("metadata", {})
                )
                doc_ids.append(doc_id)
            return doc_ids

    async def _process_episodes_individually(self, episodes: List[Dict[str, Any]]) -> List[str]:
        """Fallback method to process episodes individually"""
        episode_ids = []
        for episode in episodes:
            try:
                # Determine content type and process accordingly
                content = episode["content"]
                metadata = episode.get("metadata", {})
                
                if episode.get("source") == "knowledge" or metadata.get("content_type") == "knowledge_document":
                    episode_id = await self.backend.insert_knowledge_document(content, metadata)
                else:
                    episode_id = await self.backend.insert_text(content, metadata)
                
                episode_ids.append(episode_id)
            except Exception as e:
                print(f"Failed to process individual episode: {e}")
                continue
        
        return episode_ids

    def backend_supports_bulk(self) -> bool:
        """Check if the current backend supports bulk processing"""
        return (self.backend is not None and 
                self.backend.supports_bulk_processing() and 
                self.config.bulk_processing_enabled)

    async def get_bulk_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about bulk processing capabilities and configuration"""
        await self._ensure_initialized()
        
        return {
            "backend_type": self.config.backend_type,
            "bulk_processing_enabled": self.config.bulk_processing_enabled,
            "bulk_batch_size": self.config.bulk_batch_size,
            "bulk_timeout": self.config.bulk_timeout,
            "backend_supports_bulk": self.backend.supports_bulk_processing(),
            "effective_bulk_enabled": self.backend_supports_bulk()
        }
