from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from agent import Agent # Assuming Agent class is in agent.py at the root

@dataclass
class MemoryDocument:
    """Unified memory document representation"""
    id: str
    page_content: str  # CORRECTED: Use page_content for LangChain compatibility
    metadata: Dict[str, Any]
    score: Optional[float] = None

@dataclass
class MemoryConfig:
    """Memory backend configuration"""
    backend_type: str  # "faiss" or "graphiti"
    memory_subdir: str
    # Assuming embeddings_model is a type, replace Any with a more specific type if available
    # For now, using Any to match the guide.
    embeddings_model: Any
    graphiti_config: Optional[Dict[str, str]] = None

class MemoryBackend(ABC):
    """Abstract base class for memory backends"""

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
        filter: Optional[Dict[str, Any]] = None # Changed from filter: str to Dict for more structured filtering
    ) -> List[MemoryDocument]:
        """Search for similar documents"""
        pass

    @abstractmethod
    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]: # Return type changed to List[MemoryDocument] to match guide's intent
        """Delete documents by IDs and return deleted documents"""
        pass

    @abstractmethod
    async def delete_documents_by_query( # Return type changed to List[MemoryDocument]
        self,
        query: str,
        threshold: float = 0.75,
        filter: Optional[Dict[str, Any]] = None # Changed from filter: str to Dict
    ) -> List[MemoryDocument]:
        """Delete documents by query and return deleted documents"""
        pass

    @abstractmethod
    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Retrieve documents by IDs"""
        pass

    @abstractmethod
    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction"""
        pass

class EnhancedMemoryAbstractionLayer:
    """Enhanced abstraction layer for unified memory and knowledge operations"""

    def __init__(self, agent: 'Agent'):
        self.agent = agent
        self.backend: Optional[MemoryBackend] = None
        self.config: Optional[MemoryConfig] = None

    async def initialize(self) -> None:
        """Initialize the appropriate backend based on configuration"""
        backend_type = self._get_backend_type()

        if backend_type == "graphiti":
            from .memory_graphiti_backend import GraphitiBackend # Relative import
            self.backend = GraphitiBackend()
        else:
            from .memory_faiss_backend import FaissBackend  # Relative import
            self.backend = FaissBackend()

        self.config = self._build_config(backend_type)
        if self.backend is not None: # Check if backend was successfully initialized
            await self.backend.initialize(self.config)
        else:
            # Handle case where backend couldn't be determined or initialized
            # This might involve logging an error or raising an exception
            print(f"Error: Memory backend '{backend_type}' could not be initialized.") # Or use proper logging
            # Potentially raise an exception here: raise RuntimeError("Failed to initialize memory backend")


    def _get_backend_type(self) -> str:
        """Determine which backend to use based on configuration"""
        import os

        # Check environment variable first
        env_backend = os.getenv("MEMORY_BACKEND", "faiss")

        # Check agent config for memory backend preference
        # Ensure agent.config exists and has memory_backend attribute
        memory_backend_config_value = "faiss" # Default
        if hasattr(self.agent, 'config') and self.agent.config is not None:
             memory_backend_config_value = getattr(self.agent.config, 'memory_backend', "faiss")


        if memory_backend_config_value == "graphiti" or env_backend == "graphiti":
            # Check if GRAPHITI_ENABLED is explicitly set to true in env
            if os.getenv("GRAPHITI_ENABLED", "false").lower() == "true" or memory_backend_config_value == "graphiti":
                 return "graphiti"
        return "faiss"

    def _build_config(self, backend_type: str) -> MemoryConfig:
        """Build configuration for the selected backend"""
        import os

        # Ensure agent.config and its attributes exist
        memory_subdir_val = "default"
        if hasattr(self.agent, 'config') and self.agent.config is not None:
            memory_subdir_val = getattr(self.agent.config, 'memory_subdir', "default") or "default"

        embeddings_model_val = None # Default or placeholder
        if hasattr(self.agent, 'config') and self.agent.config is not None:
            embeddings_model_val = getattr(self.agent.config, 'embeddings_model', None)

        config = MemoryConfig(
            backend_type=backend_type,
            memory_subdir=memory_subdir_val,
            embeddings_model=embeddings_model_val
        )

        if backend_type == "graphiti":
            config.graphiti_config = {
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "password"),
                "group_id": os.getenv("GRAPHITI_GROUP_ID", "agent-zero-default")
            }

        return config

    async def _ensure_initialized(self):
        if not self.backend or not self.config:
            await self.initialize()
        if not self.backend: # Add a check after trying to initialize
            raise RuntimeError("Memory backend failed to initialize and is not available.")

    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_initialized()
        # self.backend should not be None here due to _ensure_initialized
        return await self.backend.insert_text(text, metadata) # type: ignore

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None # Matching type hint in base class
    ) -> List[MemoryDocument]:
        await self._ensure_initialized()
        return await self.backend.search_similarity_threshold(query, limit, threshold, filter) # type: ignore

    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_initialized()
        return await self.backend.delete_documents_by_ids(ids) # type: ignore

    async def delete_documents_by_query(
        self,
        query: str,
        threshold: float = 0.75,
        filter: Optional[Dict[str, Any]] = None # Matching type hint in base class
    ) -> List[MemoryDocument]:
        await self._ensure_initialized()
        return await self.backend.delete_documents_by_query(query, threshold, filter) # type: ignore

    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_initialized()
        return await self.backend.get_documents_by_ids(ids) # type: ignore

    async def insert_content(self, content: str, content_type: str, metadata: Dict[str, Any]) -> str:
        """Insert content with type-specific processing"""
        await self._ensure_initialized()

        # Add content type to metadata if not already present
        metadata.setdefault("content_type", content_type)

        if content_type == "knowledge_document":
            # Enhanced processing for knowledge documents
            # self.backend should not be None here
            return await self.backend.insert_knowledge_document(content, metadata) # type: ignore
        elif content_type == "agent_memory":
            # Simple processing for agent conversations
            return await self.backend.insert_text(content, metadata) # type: ignore
        else:
            raise ValueError(f"Invalid content_type: {content_type}")

    async def process_knowledge_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Process multiple knowledge documents with entity extraction"""
        await self._ensure_initialized()

        doc_ids = []
        for doc in documents:
            # Ensure 'content' and 'metadata' keys exist
            if "content" not in doc or "metadata" not in doc:
                # Log or handle missing keys appropriately
                print(f"Skipping document due to missing 'content' or 'metadata': {doc.get('id', 'Unknown ID')}")
                continue

            doc_id = await self.insert_content(
                doc["content"],
                "knowledge_document", # Explicitly set content_type
                doc["metadata"]
            )
            doc_ids.append(doc_id)

        return doc_ids
