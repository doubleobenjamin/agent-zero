"""
Graphiti Knowledge Graph Service for Enhanced Memory System
Provides temporal knowledge graphs with namespace isolation
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from python.helpers.database_manager import get_database_manager
from python.helpers.print_style import PrintStyle
from agent import Agent

try:
    from graphiti import Graphiti
    from graphiti.nodes import EpisodeType
    GRAPHITI_AVAILABLE = True
except ImportError:
    GRAPHITI_AVAILABLE = False
    PrintStyle.error("Graphiti not available. Install with: pip install graphiti-core")


class GraphitiService:
    """Graphiti knowledge graph service for agent memory"""
    
    def __init__(self, agent: Agent, namespace: str):
        self.agent = agent
        self.namespace = namespace
        self.db_manager = get_database_manager()
        
        if not GRAPHITI_AVAILABLE:
            PrintStyle.error("Graphiti is not available. Knowledge graph features disabled.")
            self.client = None
            return
        
        # Initialize Graphiti client
        try:
            self.client = Graphiti(
                neo4j_uri=self.db_manager.neo4j_uri,
                neo4j_user=self.db_manager.neo4j_user,
                neo4j_password=self.db_manager.neo4j_password
            )
            PrintStyle.standard(f"Initialized Graphiti service for namespace: {namespace}")
        except Exception as e:
            PrintStyle.error(f"Failed to initialize Graphiti: {e}")
            self.client = None
    
    async def save_episode(self, name: str, episode_body: str, 
                          source_description: str = "", 
                          reference_time: Optional[datetime] = None,
                          group_id: Optional[str] = None,
                          entities: List[Dict] = None,
                          relationships: List[Dict] = None) -> Optional[str]:
        """Save an episode to the knowledge graph"""
        if not self.client:
            PrintStyle.error("Graphiti client not available")
            return None
        
        try:
            if reference_time is None:
                reference_time = datetime.now()
            
            if group_id is None:
                group_id = self.namespace
            
            # Create episode
            episode_id = str(uuid.uuid4())
            
            # Use Graphiti's add_episode method
            result = await self.client.add_episode(
                name=name,
                episode_body=episode_body,
                source_description=source_description or f"Agent {self.agent.number} memory",
                reference_time=reference_time,
                group_id=group_id
            )
            
            PrintStyle.standard(f"Saved episode to knowledge graph: {name}")
            return episode_id
            
        except Exception as e:
            PrintStyle.error(f"Failed to save episode: {e}")
            return None
    
    async def search_episodes(self, query: str, limit: int = 10,
                            group_id: Optional[str] = None) -> List[Dict]:
        """Search episodes in the knowledge graph"""
        if not self.client:
            return []
        
        try:
            if group_id is None:
                group_id = self.namespace
            
            # Use Graphiti's search functionality
            results = await self.client.search(
                query=query,
                limit=limit,
                group_id=group_id
            )
            
            PrintStyle.standard(f"Found {len(results)} episodes for query: {query}")
            return results
            
        except Exception as e:
            PrintStyle.error(f"Failed to search episodes: {e}")
            return []
    
    async def get_entities(self, limit: int = 50, 
                          group_id: Optional[str] = None) -> List[Dict]:
        """Get entities from the knowledge graph"""
        if not self.client:
            return []
        
        try:
            if group_id is None:
                group_id = self.namespace
            
            # Query entities using Neo4j driver directly
            driver = self.db_manager.neo4j_driver
            
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (e:Entity)
                    WHERE e.group_id = $group_id
                    RETURN e.name as name, e.uuid as uuid, 
                           e.created_at as created_at, e.summary as summary
                    ORDER BY e.created_at DESC
                    LIMIT $limit
                    """,
                    group_id=group_id,
                    limit=limit
                )
                
                entities = []
                for record in result:
                    entities.append({
                        "name": record["name"],
                        "uuid": record["uuid"],
                        "created_at": record["created_at"],
                        "summary": record["summary"]
                    })
                
                PrintStyle.standard(f"Retrieved {len(entities)} entities")
                return entities
                
        except Exception as e:
            PrintStyle.error(f"Failed to get entities: {e}")
            return []
    
    async def get_relationships(self, entity_name: str = None,
                              limit: int = 50,
                              group_id: Optional[str] = None) -> List[Dict]:
        """Get relationships from the knowledge graph"""
        if not self.client:
            return []
        
        try:
            if group_id is None:
                group_id = self.namespace
            
            driver = self.db_manager.neo4j_driver
            
            with driver.session() as session:
                if entity_name:
                    # Get relationships for specific entity
                    result = session.run(
                        """
                        MATCH (e1:Entity)-[r]->(e2:Entity)
                        WHERE (e1.name = $entity_name OR e2.name = $entity_name)
                        AND e1.group_id = $group_id AND e2.group_id = $group_id
                        RETURN e1.name as source, type(r) as relationship, 
                               e2.name as target, r.created_at as created_at
                        ORDER BY r.created_at DESC
                        LIMIT $limit
                        """,
                        entity_name=entity_name,
                        group_id=group_id,
                        limit=limit
                    )
                else:
                    # Get all relationships
                    result = session.run(
                        """
                        MATCH (e1:Entity)-[r]->(e2:Entity)
                        WHERE e1.group_id = $group_id AND e2.group_id = $group_id
                        RETURN e1.name as source, type(r) as relationship,
                               e2.name as target, r.created_at as created_at
                        ORDER BY r.created_at DESC
                        LIMIT $limit
                        """,
                        group_id=group_id,
                        limit=limit
                    )
                
                relationships = []
                for record in result:
                    relationships.append({
                        "source": record["source"],
                        "relationship": record["relationship"],
                        "target": record["target"],
                        "created_at": record["created_at"]
                    })
                
                PrintStyle.standard(f"Retrieved {len(relationships)} relationships")
                return relationships
                
        except Exception as e:
            PrintStyle.error(f"Failed to get relationships: {e}")
            return []
    
    async def get_namespace_stats(self, group_id: Optional[str] = None) -> Dict[str, int]:
        """Get statistics for the namespace"""
        if not self.client:
            return {}
        
        try:
            if group_id is None:
                group_id = self.namespace
            
            driver = self.db_manager.neo4j_driver
            
            with driver.session() as session:
                result = session.run(
                    """
                    MATCH (e:Entity) WHERE e.group_id = $group_id
                    WITH count(e) as entity_count
                    MATCH (ep:Episode) WHERE ep.group_id = $group_id
                    WITH entity_count, count(ep) as episode_count
                    MATCH (e1:Entity)-[r]->(e2:Entity)
                    WHERE e1.group_id = $group_id AND e2.group_id = $group_id
                    RETURN entity_count, episode_count, count(r) as relationship_count
                    """,
                    group_id=group_id
                )
                
                record = result.single()
                if record:
                    stats = {
                        "entities": record["entity_count"],
                        "episodes": record["episode_count"],
                        "relationships": record["relationship_count"]
                    }
                else:
                    stats = {"entities": 0, "episodes": 0, "relationships": 0}
                
                PrintStyle.standard(f"Namespace {group_id} stats: {stats}")
                return stats
                
        except Exception as e:
            PrintStyle.error(f"Failed to get namespace stats: {e}")
            return {"entities": 0, "episodes": 0, "relationships": 0}
