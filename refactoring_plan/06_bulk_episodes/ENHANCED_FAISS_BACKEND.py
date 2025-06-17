"""
Enhanced FAISS Backend with Bulk Processing Fallback
Extends the existing FAISS backend wrapper with bulk processing methods
"""

from typing import List, Dict, Any, Optional, TYPE_CHECKING, cast
from .enhanced_memory_abstraction import EnhancedMemoryBackend, MemoryDocument, MemoryConfig
from .memory import Memory as LegacyMemory
from .memory import Document as LegacyFaissDocument

if TYPE_CHECKING:
    from agent import Agent

class EnhancedFaissBackend(EnhancedMemoryBackend):
    """Enhanced FAISS backend wrapper with bulk processing fallback"""

    def __init__(self):
        self.legacy_memory: Optional[LegacyMemory] = None
        self.agent_for_legacy: Optional['Agent'] = None
        self.bulk_batch_size: int = 50  # Smaller batches for FAISS
        self.bulk_timeout: int = 300

    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize FAISS backend using existing Memory class"""
        
        # Extract bulk processing configuration
        self.bulk_batch_size = config.bulk_batch_size
        self.bulk_timeout = config.bulk_timeout

        # Create a mock agent object for the legacy memory system
        class MockAgentConfig:
            def __init__(self, memory_config: MemoryConfig):
                self.memory_subdir = memory_config.memory_subdir
                self.embeddings_model = memory_config.embeddings_model
                self.knowledge_subdirs = []  # Empty for now

        class MockAgent:
            def __init__(self, config: MemoryConfig):
                self.config = MockAgentConfig(config)
                self.context = None  # Mock context if needed

        mock_agent_instance = MockAgent(config)
        self.legacy_memory = await LegacyMemory.get(cast('Agent', mock_agent_instance))

    async def _ensure_legacy_initialized(self):
        if not self.legacy_memory:
            raise RuntimeError("FaissBackend (LegacyMemory) not initialized. Call initialize first.")

    def _to_memory_document(self, legacy_doc: LegacyFaissDocument, score: Optional[float] = None) -> MemoryDocument:
        """Convert legacy FAISS document to MemoryDocument"""
        return MemoryDocument(
            id=getattr(legacy_doc, 'id', str(hash(legacy_doc.page_content))),
            page_content=legacy_doc.page_content,
            metadata=legacy_doc.metadata,
            score=score
        )

    # Standard memory operations (from existing implementation)
    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_legacy_initialized()
        area = metadata.get("area", LegacyMemory.Area.MAIN.value)
        doc_id = await self.legacy_memory.insert_text_area(
            text=text,
            area=area,
            metadata=metadata
        )
        return doc_id

    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_legacy_initialized()
        area = metadata.get("area", LegacyMemory.Area.KNOWLEDGE.value)
        doc_id = await self.legacy_memory.insert_text_area(
            text=content,
            area=area,
            metadata=metadata
        )
        return doc_id

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[MemoryDocument]:
        await self._ensure_legacy_initialized()
        
        # Use legacy memory search
        area = filter.get("area") if filter else None
        if area:
            legacy_docs = await self.legacy_memory.search_similarity_threshold(
                query, area, limit, threshold
            )
        else:
            # Search all areas if no specific area filter
            legacy_docs = []
            for area_enum in LegacyMemory.Area:
                area_docs = await self.legacy_memory.search_similarity_threshold(
                    query, area_enum.value, limit, threshold
                )
                legacy_docs.extend(area_docs)
            
            # Sort by score and limit
            legacy_docs.sort(key=lambda x: getattr(x, 'score', 0), reverse=True)
            legacy_docs = legacy_docs[:limit]

        return [self._to_memory_document(doc) for doc in legacy_docs]

    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_legacy_initialized()
        
        deleted_docs = []
        for doc_id in ids:
            # Try to find and delete from all areas
            for area_enum in LegacyMemory.Area:
                try:
                    docs = await self.legacy_memory.get_by_ids([doc_id], area_enum.value)
                    if docs:
                        deleted_docs.extend([self._to_memory_document(doc) for doc in docs])
                        await self.legacy_memory.delete_by_ids([doc_id], area_enum.value)
                        break
                except:
                    continue
        
        return deleted_docs

    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_legacy_initialized()
        
        found_docs = []
        for doc_id in ids:
            # Search all areas for the document
            for area_enum in LegacyMemory.Area:
                try:
                    docs = await self.legacy_memory.get_by_ids([doc_id], area_enum.value)
                    if docs:
                        found_docs.extend([self._to_memory_document(doc) for doc in docs])
                        break
                except:
                    continue
        
        return found_docs

    # Enhanced bulk processing methods (fallback to individual processing)
    async def add_episode_bulk(self, episodes: List[Dict[str, Any]]) -> List[str]:
        """Add multiple episodes (fallback to individual processing for FAISS)"""
        await self._ensure_legacy_initialized()
        
        if not episodes:
            return []

        doc_ids = []
        
        # Process in smaller batches to avoid overwhelming the system
        for i in range(0, len(episodes), self.bulk_batch_size):
            batch = episodes[i:i + self.bulk_batch_size]
            batch_ids = await self._process_episode_batch(batch)
            doc_ids.extend(batch_ids)

        return doc_ids

    async def _process_episode_batch(self, episodes: List[Dict[str, Any]]) -> List[str]:
        """Process a batch of episodes individually"""
        batch_ids = []
        
        for episode in episodes:
            try:
                content = episode["content"]
                metadata = episode.get("metadata", {})
                
                # Determine area from metadata or episode source
                area = metadata.get("area", LegacyMemory.Area.MAIN.value)
                if episode.get("source") == "knowledge":
                    area = LegacyMemory.Area.KNOWLEDGE.value

                doc_id = await self.legacy_memory.insert_text_area(
                    text=content,
                    area=area,
                    metadata=metadata
                )
                batch_ids.append(doc_id)
                
            except Exception as e:
                print(f"Failed to process episode in batch: {e}")
                continue
        
        return batch_ids

    async def insert_knowledge_documents_bulk(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple knowledge documents (fallback to individual processing)"""
        await self._ensure_legacy_initialized()
        
        if not documents:
            return []

        doc_ids = []
        
        # Process in batches
        for i in range(0, len(documents), self.bulk_batch_size):
            batch = documents[i:i + self.bulk_batch_size]
            batch_ids = await self._process_knowledge_batch(batch)
            doc_ids.extend(batch_ids)

        return doc_ids

    async def _process_knowledge_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Process a batch of knowledge documents individually"""
        batch_ids = []
        
        for doc in documents:
            try:
                content = doc["content"]
                metadata = doc.get("metadata", {})
                
                # Knowledge documents go to KNOWLEDGE area by default
                area = metadata.get("area", LegacyMemory.Area.KNOWLEDGE.value)
                
                doc_id = await self.legacy_memory.insert_text_area(
                    text=content,
                    area=area,
                    metadata=metadata
                )
                batch_ids.append(doc_id)
                
            except Exception as e:
                print(f"Failed to process knowledge document in batch: {e}")
                continue
        
        return batch_ids

    def supports_bulk_processing(self) -> bool:
        """FAISS backend supports bulk processing via fallback to individual processing"""
        return True  # We support it via fallback

    async def get_bulk_processing_info(self) -> Dict[str, Any]:
        """Get information about bulk processing capabilities"""
        return {
            "backend_type": "faiss",
            "native_bulk_support": False,
            "fallback_bulk_support": True,
            "batch_size": self.bulk_batch_size,
            "timeout": self.bulk_timeout,
            "processing_method": "individual_fallback"
        }

    # Compatibility methods for legacy integration
    async def preload_knowledge(self, log_item, knowledge_subdirs: List[str], memory_subdir: str):
        """Preload knowledge from subdirectories (legacy compatibility)"""
        await self._ensure_legacy_initialized()
        
        if hasattr(self.legacy_memory, 'preload_knowledge'):
            await self.legacy_memory.preload_knowledge(log_item, knowledge_subdirs, memory_subdir)

    def format_docs_plain(self, docs: List[MemoryDocument]) -> List[str]:
        """Format documents to plain text (legacy compatibility)"""
        return [doc.page_content for doc in docs]

    async def get_area_documents(self, area: str, limit: int = 100) -> List[MemoryDocument]:
        """Get documents from a specific area (legacy compatibility)"""
        await self._ensure_legacy_initialized()
        
        try:
            legacy_docs = await self.legacy_memory.get_area_documents(area, limit)
            return [self._to_memory_document(doc) for doc in legacy_docs]
        except:
            return []

    async def clear_area(self, area: str) -> bool:
        """Clear all documents from a specific area (legacy compatibility)"""
        await self._ensure_legacy_initialized()
        
        try:
            await self.legacy_memory.clear_area(area)
            return True
        except:
            return False
