"""
Database Manager for Enhanced Memory System
Handles connections to Qdrant and Neo4j databases
"""

import asyncio
import logging
from typing import Optional
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from neo4j import GraphDatabase, Driver
from python.helpers.print_style import PrintStyle

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections for enhanced memory system"""
    
    def __init__(self, 
                 qdrant_host: str = "localhost",
                 qdrant_port: int = 6333,
                 neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password"):
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        self._qdrant_client: Optional[QdrantClient] = None
        self._neo4j_driver: Optional[Driver] = None
    
    @property
    def qdrant_client(self) -> QdrantClient:
        """Get or create Qdrant client"""
        if self._qdrant_client is None:
            self._qdrant_client = QdrantClient(
                host=self.qdrant_host,
                port=self.qdrant_port,
                timeout=30
            )
        return self._qdrant_client
    
    @property
    def neo4j_driver(self) -> Driver:
        """Get or create Neo4j driver"""
        if self._neo4j_driver is None:
            self._neo4j_driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
        return self._neo4j_driver
    
    async def check_qdrant_health(self) -> bool:
        """Check if Qdrant is healthy and accessible"""
        try:
            client = self.qdrant_client
            # Try to get cluster info as a health check
            info = client.get_cluster_info()
            PrintStyle.standard(f"Qdrant health check passed: {info.status}")
            return True
        except Exception as e:
            PrintStyle.error(f"Qdrant health check failed: {e}")
            return False
    
    async def check_neo4j_health(self) -> bool:
        """Check if Neo4j is healthy and accessible"""
        try:
            driver = self.neo4j_driver
            with driver.session() as session:
                result = session.run("RETURN 1 as health")
                health = result.single()["health"]
                PrintStyle.standard(f"Neo4j health check passed: {health}")
                return True
        except Exception as e:
            PrintStyle.error(f"Neo4j health check failed: {e}")
            return False
    
    async def check_all_health(self) -> bool:
        """Check health of all database systems"""
        qdrant_ok = await self.check_qdrant_health()
        neo4j_ok = await self.check_neo4j_health()
        
        if qdrant_ok and neo4j_ok:
            PrintStyle.standard("All database systems healthy")
            return True
        else:
            PrintStyle.error("Some database systems are unhealthy")
            return False
    
    async def initialize_databases(self) -> bool:
        """Initialize database schemas and configurations"""
        try:
            # Initialize Neo4j constraints and indexes for Graphiti
            await self._initialize_neo4j_schema()
            PrintStyle.standard("Database initialization completed successfully")
            return True
        except Exception as e:
            PrintStyle.error(f"Database initialization failed: {e}")
            return False
    
    async def _initialize_neo4j_schema(self):
        """Initialize Neo4j schema for Graphiti and Cognee"""
        driver = self.neo4j_driver
        
        with driver.session() as session:
            # Create constraints and indexes for Graphiti
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Entity) REQUIRE n.uuid IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Episode) REQUIRE n.uuid IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Community) REQUIRE n.uuid IS UNIQUE",
                "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.name)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Episode) ON (n.created_at)",
                "CREATE INDEX IF NOT EXISTS FOR (n:Entity) ON (n.created_at)"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    PrintStyle.standard(f"Applied constraint: {constraint}")
                except Exception as e:
                    PrintStyle.error(f"Failed to apply constraint {constraint}: {e}")
    
    def close_connections(self):
        """Close all database connections"""
        if self._qdrant_client:
            self._qdrant_client.close()
            self._qdrant_client = None
        
        if self._neo4j_driver:
            self._neo4j_driver.close()
            self._neo4j_driver = None
        
        PrintStyle.standard("Database connections closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


async def initialize_enhanced_databases() -> bool:
    """Initialize enhanced database systems"""
    db_manager = get_database_manager()
    
    # Check health first
    if not await db_manager.check_all_health():
        PrintStyle.error("Database health check failed. Please ensure Qdrant and Neo4j are running.")
        return False
    
    # Initialize schemas
    if not await db_manager.initialize_databases():
        PrintStyle.error("Database initialization failed.")
        return False
    
    PrintStyle.standard("Enhanced database systems initialized successfully")
    return True
