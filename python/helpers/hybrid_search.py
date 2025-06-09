"""
Hybrid Search Engine for Enhanced Memory System
Combines Qdrant vector search, Graphiti knowledge graph, and Cognee processing
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from python.helpers.qdrant_client import QdrantVectorDB
from python.helpers.graphiti_service import GraphitiService
from python.helpers.cognee_processor import CogneeProcessor
from python.helpers.print_style import PrintStyle
from agent import Agent


class HybridSearchResult:
    """Result from hybrid search combining multiple sources"""
    
    def __init__(self, document: Document, source: str, score: float = 0.0, 
                 entities: List[Dict] = None, relationships: List[Dict] = None):
        self.document = document
        self.source = source  # 'qdrant', 'graphiti', 'cognee'
        self.score = score
        self.entities = entities or []
        self.relationships = relationships or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.document.page_content,
            "metadata": self.document.metadata,
            "source": self.source,
            "score": self.score,
            "entities": self.entities,
            "relationships": self.relationships
        }


class HybridSearchEngine:
    """Hybrid search engine combining vector, graph, and knowledge search"""
    
    def __init__(self, qdrant_client: QdrantVectorDB, 
                 graphiti_service: GraphitiService,
                 cognee_processor: CogneeProcessor):
        self.qdrant_client = qdrant_client
        self.graphiti_service = graphiti_service
        self.cognee_processor = cognee_processor
    
    async def search(self, query: str, limit: int = 10, 
                    threshold: float = 0.7,
                    sources: List[str] = None,
                    filter_dict: Dict = None) -> List[HybridSearchResult]:
        """
        Perform hybrid search across all systems
        
        Args:
            query: Search query
            limit: Maximum results per source
            threshold: Minimum similarity threshold
            sources: List of sources to search ['qdrant', 'graphiti', 'cognee']
            filter_dict: Additional filters
        """
        if sources is None:
            sources = ['qdrant', 'graphiti', 'cognee']
        
        results = []
        
        # Search Qdrant vector database
        if 'qdrant' in sources:
            qdrant_results = await self._search_qdrant(query, limit, threshold, filter_dict)
            results.extend(qdrant_results)
        
        # Search Graphiti knowledge graph
        if 'graphiti' in sources:
            graphiti_results = await self._search_graphiti(query, limit)
            results.extend(graphiti_results)
        
        # Search Cognee knowledge base
        if 'cognee' in sources:
            cognee_results = await self._search_cognee(query, limit)
            results.extend(cognee_results)
        
        # Sort by score and limit total results
        results.sort(key=lambda x: x.score, reverse=True)
        
        PrintStyle.standard(f"Hybrid search found {len(results)} total results")
        return results[:limit * len(sources)]
    
    async def _search_qdrant(self, query: str, limit: int, 
                           threshold: float, filter_dict: Dict = None) -> List[HybridSearchResult]:
        """Search Qdrant vector database"""
        try:
            docs = await self.qdrant_client.search_similarity(
                query=query, 
                limit=limit, 
                threshold=threshold, 
                filter_dict=filter_dict
            )
            
            results = []
            for doc in docs:
                result = HybridSearchResult(
                    document=doc,
                    source='qdrant',
                    score=doc.metadata.get('score', 0.8)  # Default score if not available
                )
                results.append(result)
            
            PrintStyle.standard(f"Qdrant search found {len(results)} results")
            return results
            
        except Exception as e:
            PrintStyle.error(f"Qdrant search failed: {e}")
            return []
    
    async def _search_graphiti(self, query: str, limit: int) -> List[HybridSearchResult]:
        """Search Graphiti knowledge graph"""
        try:
            episodes = await self.graphiti_service.search_episodes(query, limit)
            
            results = []
            for episode in episodes:
                # Convert episode to Document
                doc = Document(
                    page_content=episode.get('episode_body', ''),
                    metadata={
                        'source': 'graphiti',
                        'episode_name': episode.get('name', ''),
                        'created_at': episode.get('created_at', ''),
                        'group_id': episode.get('group_id', '')
                    }
                )
                
                result = HybridSearchResult(
                    document=doc,
                    source='graphiti',
                    score=episode.get('score', 0.7)
                )
                results.append(result)
            
            PrintStyle.standard(f"Graphiti search found {len(results)} results")
            return results
            
        except Exception as e:
            PrintStyle.error(f"Graphiti search failed: {e}")
            return []
    
    async def _search_cognee(self, query: str, limit: int) -> List[HybridSearchResult]:
        """Search Cognee knowledge base"""
        try:
            knowledge_results = await self.cognee_processor.search_knowledge(query, limit)
            
            results = []
            for knowledge in knowledge_results:
                # Convert knowledge to Document
                doc = Document(
                    page_content=knowledge.get('content', ''),
                    metadata={
                        'source': 'cognee',
                        **knowledge.get('metadata', {})
                    }
                )
                
                result = HybridSearchResult(
                    document=doc,
                    source='cognee',
                    score=knowledge.get('score', 0.6)
                )
                results.append(result)
            
            PrintStyle.standard(f"Cognee search found {len(results)} results")
            return results
            
        except Exception as e:
            PrintStyle.error(f"Cognee search failed: {e}")
            return []
    
    async def search_entities(self, entity_name: str = None, 
                            limit: int = 50) -> List[Dict[str, Any]]:
        """Search for entities across knowledge systems"""
        try:
            entities = await self.graphiti_service.get_entities(limit)
            
            if entity_name:
                # Filter entities by name
                entities = [e for e in entities if entity_name.lower() in e.get('name', '').lower()]
            
            PrintStyle.standard(f"Found {len(entities)} entities")
            return entities
            
        except Exception as e:
            PrintStyle.error(f"Entity search failed: {e}")
            return []
    
    async def search_relationships(self, entity_name: str = None,
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """Search for relationships in knowledge graph"""
        try:
            relationships = await self.graphiti_service.get_relationships(
                entity_name=entity_name, 
                limit=limit
            )
            
            PrintStyle.standard(f"Found {len(relationships)} relationships")
            return relationships
            
        except Exception as e:
            PrintStyle.error(f"Relationship search failed: {e}")
            return []
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get statistics from all systems"""
        stats = {
            "qdrant": {},
            "graphiti": {},
            "cognee": {}
        }
        
        try:
            # Qdrant stats
            collection_info = self.qdrant_client.get_collection_info()
            if collection_info:
                stats["qdrant"] = {
                    "vectors_count": collection_info.vectors_count,
                    "indexed_vectors_count": collection_info.indexed_vectors_count,
                    "points_count": collection_info.points_count
                }
            
            # Graphiti stats
            stats["graphiti"] = await self.graphiti_service.get_namespace_stats()
            
            # Cognee stats
            stats["cognee"] = await self.cognee_processor.get_dataset_stats()
            
            PrintStyle.standard(f"System stats: {stats}")
            return stats
            
        except Exception as e:
            PrintStyle.error(f"Failed to get system stats: {e}")
            return stats
