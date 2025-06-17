# CORRECTED: Enhanced Memory & Knowledge Abstraction Layer
# This file contains the corrected implementation based on actual codebase analysis
# Enhanced to support unified memory and knowledge processing with Graphiti

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid
from langchain_core.documents import Document

@dataclass
class MemoryDocument:
    """Unified memory document representation - CORRECTED to match actual usage"""
    id: str
    page_content: str  # CORRECTED: Extensions expect page_content, not content (LangChain compatibility)
    metadata: Dict[str, Any]
    score: Optional[float] = None

    @classmethod
    def from_langchain_document(cls, doc: Document, score: Optional[float] = None):
        """Create MemoryDocument from LangChain Document"""
        return cls(
            id=doc.metadata.get("id", str(uuid.uuid4())),
            page_content=doc.page_content,
            metadata=doc.metadata,
            score=score
        )

    def to_langchain_document(self) -> Document:
        """Convert to LangChain Document for compatibility"""
        return Document(
            page_content=self.page_content,
            metadata=self.metadata
        )

@dataclass  
class MemoryConfig:
    """Memory backend configuration"""
    backend_type: str  # "faiss" or "graphiti"
    memory_subdir: str
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
        filter: str = ""
    ) -> List[Document]:  # CORRECTED: Return Document objects, not MemoryDocument
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def delete_documents_by_ids(self, ids: List[str]) -> List[Document]:
        """Delete documents by IDs"""
        pass
    
    @abstractmethod
    async def delete_documents_by_query(
        self,
        query: str,
        threshold: float = 0.75,
        filter: str = ""
    ) -> List[Document]:
        """Delete documents by query"""
        pass

    @abstractmethod
    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction"""
        pass

class EnhancedMemoryAbstractionLayer:
    """Enhanced abstraction layer for unified memory and knowledge operations - CORRECTED"""
    
    def __init__(self, agent):
        self.agent = agent
        self.backend: Optional[MemoryBackend] = None
        self.config: Optional[MemoryConfig] = None
    
    async def initialize(self) -> None:
        """Initialize the appropriate backend based on configuration"""
        backend_type = self._get_backend_type()
        
        if backend_type == "graphiti":
            from .memory_graphiti_backend import GraphitiBackend
            self.backend = GraphitiBackend()
        else:
            from .memory_faiss_backend import FaissBackend  
            self.backend = FaissBackend()
        
        self.config = self._build_config(backend_type)
        await self.backend.initialize(self.config)
    
    def _get_backend_type(self) -> str:
        """Determine which backend to use based on configuration"""
        import os
        
        # Check environment variable first
        env_backend = os.getenv("MEMORY_BACKEND", "faiss")
        
        # Check agent config for memory backend preference
        # Note: This would need to be added to AgentConfig in agent.py
        memory_backend = getattr(self.agent.config, 'memory_backend', None)

        if memory_backend == "graphiti" or env_backend == "graphiti":
            return "graphiti"
        return "faiss"
    
    def _build_config(self, backend_type: str) -> MemoryConfig:
        """Build configuration for the selected backend"""
        import os
        
        config = MemoryConfig(
            backend_type=backend_type,
            memory_subdir=self.agent.config.memory_subdir or "default",
            embeddings_model=self.agent.config.embeddings_model
        )
        
        if backend_type == "graphiti":
            config.graphiti_config = {
                "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "neo4j_user": os.getenv("NEO4J_USER", "neo4j"), 
                "neo4j_password": os.getenv("NEO4J_PASSWORD", "password"),
                "group_id": os.getenv("GRAPHITI_GROUP_ID", "agent-zero-default")
            }
        
        return config
    
    # CORRECTED: Delegate methods return Document objects to maintain compatibility
    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        if not self.backend:
            await self.initialize()
        return await self.backend.insert_text(text, metadata)
    
    async def search_similarity_threshold(
        self, 
        query: str, 
        limit: int = 10, 
        threshold: float = 0.7,
        filter: str = ""
    ) -> List[Document]:  # CORRECTED: Return Document objects
        if not self.backend:
            await self.initialize()
        return await self.backend.search_similarity_threshold(query, limit, threshold, filter)
    
    async def delete_documents_by_ids(self, ids: List[str]) -> List[Document]:
        if not self.backend:
            await self.initialize()
        return await self.backend.delete_documents_by_ids(ids)
    
    async def delete_documents_by_query(
        self,
        query: str,
        threshold: float = 0.75,
        filter: str = ""
    ) -> List[Document]:
        if not self.backend:
            await self.initialize()
        return await self.backend.delete_documents_by_query(query, threshold, filter)

    # Enhanced methods for knowledge processing
    async def insert_content(self, content: str, content_type: str, metadata: Dict[str, Any]) -> str:
        """Insert content with type-specific processing"""
        if not self.backend:
            await self.initialize()

        # Add content type to metadata
        metadata["content_type"] = content_type

        if content_type == "knowledge_document":
            # Enhanced processing for knowledge documents
            return await self.backend.insert_knowledge_document(content, metadata)
        elif content_type == "agent_memory":
            # Simple processing for agent conversations
            return await self.backend.insert_text(content, metadata)
        else:
            raise ValueError(f"Invalid content_type: {content_type}")

    async def process_knowledge_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Process multiple knowledge documents with entity extraction"""
        if not self.backend:
            await self.initialize()

        doc_ids = []
        for doc in documents:
            doc_id = await self.insert_content(
                doc["content"],
                "knowledge_document",
                doc["metadata"]
            )
            doc_ids.append(doc_id)

        return doc_ids

# CORRECTED: Add missing Memory class constructor
class MemoryExtension:
    """Extension to add missing constructor to Memory class"""
    
    def __init__(self, agent, db, memory_subdir: str):
        """Initialize Memory instance with agent, database, and subdirectory"""
        self.agent = agent
        self.db = db
        self.memory_subdir = memory_subdir
    
    def get_timestamp(self):
        """Get current timestamp in the format used by Memory class"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_docs_plain(docs: List[Document]) -> List[str]:
        """Format documents to plain text - maintain compatibility"""
        return [doc.page_content for doc in docs]
