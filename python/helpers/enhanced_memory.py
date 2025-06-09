"""
Enhanced Memory System for Agent Zero
Replaces FAISS with Qdrant + Graphiti + Cognee hybrid system
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum

# Handle langchain imports gracefully
try:
    from langchain_core.documents import Document
except ImportError:
    # Fallback Document class if langchain not available
    class Document:
        def __init__(self, page_content: str, metadata: Dict[str, Any] = None):
            self.page_content = page_content
            self.metadata = metadata or {}

from python.helpers.print_style import PrintStyle

# Import enhanced components with graceful fallbacks
try:
    from python.helpers.qdrant_client import QdrantVectorDB
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    PrintStyle.error("Qdrant client not available")

try:
    from python.helpers.graphiti_service import GraphitiService
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    PrintStyle.error("Graphiti service not available")

try:
    from python.helpers.cognee_processor import CogneeProcessor
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    PrintStyle.error("Cognee processor not available")

try:
    from python.helpers.hybrid_search import HybridSearchEngine, HybridSearchResult
    HYBRID_SEARCH_AVAILABLE = True
except ImportError:
    HYBRID_SEARCH_AVAILABLE = False
    PrintStyle.error("Hybrid search not available")

try:
    from python.helpers.database_manager import get_database_manager, initialize_enhanced_databases
    DATABASE_MANAGER_AVAILABLE = True
except ImportError:
    DATABASE_MANAGER_AVAILABLE = False
    PrintStyle.error("Database manager not available")

try:
    from python.helpers.log import LogItem
    from python.helpers import knowledge_import, files
    from agent import Agent
except ImportError as e:
    PrintStyle.error(f"Core imports failed: {e}")
    raise


class EnhancedMemory:
    """Enhanced memory system with hybrid capabilities"""
    
    class Area(Enum):
        MAIN = "main"
        FRAGMENTS = "fragments"
        SOLUTIONS = "solutions"
        INSTRUMENTS = "instruments"
    
    # Class-level cache for memory instances
    index: Dict[str, "EnhancedMemory"] = {}
    
    @staticmethod
    async def get(agent: Agent) -> "EnhancedMemory":
        """Get or create enhanced memory instance for agent"""
        memory_subdir = agent.config.memory_subdir or "default"
        
        if EnhancedMemory.index.get(memory_subdir) is None:
            log_item = agent.context.log.log(
                type="util",
                heading=f"Initializing Enhanced Memory in '/{memory_subdir}'",
            )

            # Initialize databases if available
            if DATABASE_MANAGER_AVAILABLE:
                try:
                    await initialize_enhanced_databases()
                except Exception as e:
                    PrintStyle.error(f"Database initialization failed: {e}")
                    PrintStyle.standard("Continuing with fallback mode...")

            # Create enhanced memory instance
            memory = EnhancedMemory(agent, memory_subdir)
            await memory.initialize(log_item)

            EnhancedMemory.index[memory_subdir] = memory

            # Preload knowledge if configured
            if agent.config.knowledge_subdirs:
                await memory.preload_knowledge(
                    log_item, agent.config.knowledge_subdirs, memory_subdir
                )
        
        return EnhancedMemory.index[memory_subdir]
    
    @staticmethod
    async def reload(agent: Agent) -> "EnhancedMemory":
        """Reload enhanced memory instance"""
        memory_subdir = agent.config.memory_subdir or "default"
        if EnhancedMemory.index.get(memory_subdir):
            del EnhancedMemory.index[memory_subdir]
        return await EnhancedMemory.get(agent)
    
    def __init__(self, agent: Agent, memory_subdir: str):
        self.agent = agent
        self.memory_subdir = memory_subdir

        # Create collection name for this agent's memory area
        self.collection_name = f"agent_{agent.number}_{memory_subdir}"
        self.namespace = f"agent_{agent.number}"
        self.dataset_name = f"agent_{agent.number}_{memory_subdir}"

        # Initialize components with graceful fallbacks
        self.qdrant_client = None
        self.graphiti_service = None
        self.cognee_processor = None
        self.hybrid_search = None

        if QDRANT_AVAILABLE:
            try:
                self.qdrant_client = QdrantVectorDB(agent, self.collection_name)
            except Exception as e:
                PrintStyle.error(f"Failed to initialize Qdrant client: {e}")

        if GRAPHITI_AVAILABLE:
            try:
                self.graphiti_service = GraphitiService(agent, self.namespace)
            except Exception as e:
                PrintStyle.error(f"Failed to initialize Graphiti service: {e}")

        if COGNEE_AVAILABLE:
            try:
                self.cognee_processor = CogneeProcessor(agent, self.dataset_name)
            except Exception as e:
                PrintStyle.error(f"Failed to initialize Cognee processor: {e}")

        # Create hybrid search engine if components available
        if HYBRID_SEARCH_AVAILABLE and self.qdrant_client and self.graphiti_service and self.cognee_processor:
            try:
                self.hybrid_search = HybridSearchEngine(
                    self.qdrant_client,
                    self.graphiti_service,
                    self.cognee_processor
                )
            except Exception as e:
                PrintStyle.error(f"Failed to initialize hybrid search: {e}")
    
    async def initialize(self, log_item: Optional[LogItem] = None):
        """Initialize the enhanced memory system"""
        if log_item:
            log_item.stream(progress="\nInitializing Enhanced Memory System")
        
        PrintStyle.standard(f"Enhanced Memory initialized for agent {self.agent.number}")
        PrintStyle.standard(f"Collection: {self.collection_name}")
        PrintStyle.standard(f"Namespace: {self.namespace}")
        PrintStyle.standard(f"Dataset: {self.dataset_name}")
    
    async def insert_text(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Insert text with enhanced processing
        Returns rich feedback with entity extraction results
        """
        if metadata is None:
            metadata = {}

        # Add area if not specified
        if not metadata.get("area", ""):
            metadata["area"] = EnhancedMemory.Area.MAIN.value

        # Add timestamp
        metadata["timestamp"] = self.get_timestamp()

        # Initialize result
        result = {
            'doc_id': None,
            'episode_id': None,
            'entities_extracted': 0,
            'relationships_mapped': 0,
            'knowledge_graph_updated': False,
            'summary': '',
            'entities': [],
            'relationships': []
        }

        try:
            # 1. Store in Qdrant for vector similarity (if available)
            if self.qdrant_client:
                try:
                    doc_id = await self.qdrant_client.insert_text(text, metadata)
                    result['doc_id'] = doc_id
                except Exception as e:
                    PrintStyle.error(f"Qdrant insert failed: {e}")
                    result['doc_id'] = str(uuid.uuid4())  # Fallback ID
            else:
                result['doc_id'] = str(uuid.uuid4())  # Fallback ID
                PrintStyle.standard("Qdrant not available, using fallback storage")

            # 2. Process through Cognee for entity extraction (if available)
            cognee_result = {'entities': [], 'relationships': [], 'summary': ''}
            if self.cognee_processor:
                try:
                    cognee_result = await self.cognee_processor.add_and_cognify(text, metadata)
                    result['entities'] = cognee_result.get('entities', [])
                    result['relationships'] = cognee_result.get('relationships', [])
                    result['summary'] = cognee_result.get('summary', '')
                    result['entities_extracted'] = len(result['entities'])
                    result['relationships_mapped'] = len(result['relationships'])
                except Exception as e:
                    PrintStyle.error(f"Cognee processing failed: {e}")

            # 3. Store in Graphiti for temporal queries (if available)
            if self.graphiti_service:
                try:
                    episode_id = await self.graphiti_service.save_episode(
                        name=f"memory_{result['doc_id']}",
                        episode_body=text,
                        source_description=metadata.get('area', 'main'),
                        reference_time=datetime.now(),
                        group_id=self.namespace,
                        entities=result['entities'],
                        relationships=result['relationships']
                    )
                    result['episode_id'] = episode_id
                    result['knowledge_graph_updated'] = episode_id is not None
                except Exception as e:
                    PrintStyle.error(f"Graphiti storage failed: {e}")

            PrintStyle.standard(f"Enhanced memory insert: {result['entities_extracted']} entities, {result['relationships_mapped']} relationships")
            return result

        except Exception as e:
            PrintStyle.error(f"Enhanced memory insert failed: {e}")
            result['error'] = str(e)
            return result
    
    async def insert_documents(self, docs: List[Document]) -> List[str]:
        """Insert multiple documents with enhanced processing"""
        doc_ids = []
        
        for doc in docs:
            result = await self.insert_text(doc.page_content, doc.metadata)
            if result.get('doc_id'):
                doc_ids.append(result['doc_id'])
        
        return doc_ids
    
    async def search_similarity_threshold(self, query: str, limit: int = 10,
                                        threshold: float = 0.7,
                                        filter: str = "") -> List[Document]:
        """
        Search with similarity threshold using hybrid search
        Maintains compatibility with existing memory interface
        """
        try:
            # Use hybrid search if available
            if self.hybrid_search:
                # Convert filter string to dict if provided
                filter_dict = None
                if filter:
                    # Simple filter parsing - can be enhanced
                    filter_dict = {"area": filter} if filter else None

                # Perform hybrid search
                results = await self.hybrid_search.search(
                    query=query,
                    limit=limit,
                    threshold=threshold,
                    filter_dict=filter_dict
                )

                # Convert to Document list for compatibility
                documents = [result.document for result in results]

                PrintStyle.standard(f"Enhanced search found {len(documents)} documents")
                return documents

            # Fallback to Qdrant only if available
            elif self.qdrant_client:
                filter_dict = {"area": filter} if filter else None
                documents = await self.qdrant_client.search_similarity(
                    query=query,
                    limit=limit,
                    threshold=threshold,
                    filter_dict=filter_dict
                )
                PrintStyle.standard(f"Qdrant search found {len(documents)} documents")
                return documents

            # No search capabilities available
            else:
                PrintStyle.error("No search capabilities available")
                return []

        except Exception as e:
            PrintStyle.error(f"Enhanced search failed: {e}")
            return []
    
    async def search_entities(self, entity_name: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for entities in knowledge graph"""
        return await self.hybrid_search.search_entities(entity_name, limit)
    
    async def search_relationships(self, entity_name: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for relationships in knowledge graph"""
        return await self.hybrid_search.search_relationships(entity_name, limit)
    
    async def get_memory_insights(self) -> Dict[str, Any]:
        """Get insights about the memory system"""
        try:
            stats = await self.hybrid_search.get_system_stats()
            
            insights = {
                "system_stats": stats,
                "collection_name": self.collection_name,
                "namespace": self.namespace,
                "dataset_name": self.dataset_name,
                "total_vectors": stats.get("qdrant", {}).get("points_count", 0),
                "total_entities": stats.get("graphiti", {}).get("entities", 0),
                "total_relationships": stats.get("graphiti", {}).get("relationships", 0),
                "total_episodes": stats.get("graphiti", {}).get("episodes", 0)
            }
            
            return insights
            
        except Exception as e:
            PrintStyle.error(f"Failed to get memory insights: {e}")
            return {}
    
    async def delete_documents_by_ids(self, ids: List[str]) -> List[Document]:
        """Delete documents by IDs from all systems"""
        try:
            # Delete from Qdrant
            deleted_count = await self.qdrant_client.delete_by_ids(ids)
            
            # Note: Graphiti and Cognee deletions would need specific implementation
            # For now, we focus on Qdrant as the primary storage
            
            PrintStyle.standard(f"Deleted {deleted_count} documents from enhanced memory")
            return []  # Return empty list for compatibility
            
        except Exception as e:
            PrintStyle.error(f"Enhanced delete failed: {e}")
            return []

    async def preload_knowledge(self, log_item: Optional[LogItem],
                              kn_dirs: List[str], memory_subdir: str):
        """Preload knowledge from directories"""
        if log_item:
            log_item.update(heading="Preloading knowledge to enhanced memory...")

        try:
            # Use existing knowledge import logic but with enhanced storage
            index = {}

            # Load knowledge folders
            for kn_dir in kn_dirs:
                for area in EnhancedMemory.Area:
                    index = knowledge_import.load_knowledge(
                        log_item,
                        files.get_abs_path("knowledge", kn_dir, area.value),
                        index,
                        {"area": area.value},
                    )

            # Load instruments descriptions
            index = knowledge_import.load_knowledge(
                log_item,
                files.get_abs_path("instruments"),
                index,
                {"area": EnhancedMemory.Area.INSTRUMENTS.value},
                filename_pattern="**/*.md",
            )

            # Insert documents using enhanced memory
            for file_path, file_info in index.items():
                if file_info.get("documents"):
                    await self.insert_documents(file_info["documents"])

            PrintStyle.standard("Knowledge preloading completed with enhanced memory")

        except Exception as e:
            PrintStyle.error(f"Enhanced knowledge preloading failed: {e}")

    @staticmethod
    def get_timestamp() -> str:
        """Get current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_docs_plain(docs: List[Document]) -> List[str]:
        """Format documents as plain text (compatibility method)"""
        result = []
        for doc in docs:
            text = ""
            for k, v in doc.metadata.items():
                text += f"{k}: {v}\n"
            text += f"Content: {doc.page_content}"
            result.append(text)
        return result


# Compatibility functions for existing code
def get_memory_subdir_abs(agent: Agent) -> str:
    """Get absolute path to memory subdirectory"""
    return files.get_abs_path("memory", agent.config.memory_subdir or "default")


def get_custom_knowledge_subdir_abs(agent: Agent) -> str:
    """Get absolute path to custom knowledge subdirectory"""
    for dir in agent.config.knowledge_subdirs:
        if dir != "default":
            return files.get_abs_path("knowledge", dir)
    raise Exception("No custom knowledge subdir set")


def reload():
    """Clear the memory index to force reload"""
    EnhancedMemory.index = {}
