# Database Setup for Enhanced Agent Zero

## Overview

The enhanced Agent Zero requires two primary databases to replace the current FAISS-based memory system:

1. **Qdrant** - Production-ready vector database for semantic search
2. **Neo4j** - Graph database for Graphiti temporal knowledge graphs and Cognee knowledge processing

## Database Architecture

### Shared Database Strategy
```
┌─────────────────┐    ┌─────────────────┐
│     Qdrant      │    │     Neo4j       │
│  Vector Store   │    │  Graph Store    │
├─────────────────┤    ├─────────────────┤
│ • Embeddings    │    │ • Graphiti KG   │
│ • Similarity    │    │ • Cognee KG     │
│ • Fast Search   │    │ • Relationships │
│ • Namespaces    │    │ • Temporal Data │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌─────────────────┐
         │ Enhanced Memory │
         │ Hybrid Search   │
         └─────────────────┘
```

## Qdrant Setup

### Installation Options

#### Option 1: Docker (Recommended)
```bash
# Start Qdrant with persistent storage
docker run -d \
    --name qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -v qdrant_storage:/qdrant/storage \
    qdrant/qdrant:latest
```

#### Option 2: Local Installation
```bash
# Download and install Qdrant
curl -L https://github.com/qdrant/qdrant/releases/latest/download/qdrant-x86_64-unknown-linux-gnu.tar.gz | tar xz
./qdrant
```

#### Option 3: Qdrant Cloud
```bash
# Use Qdrant Cloud service
# Configure with API key and cluster URL
```

### Qdrant Configuration
```python
# Agent Zero Qdrant configuration
QDRANT_CONFIG = {
    'url': 'http://localhost:6333',
    'api_key': None,  # For cloud deployments
    'collection_config': {
        'vector_size': 1536,  # OpenAI ada-002 embedding size
        'distance': 'Cosine',
        'on_disk_payload': True,  # Store metadata on disk
        'optimizers_config': {
            'default_segment_number': 2,
            'max_segment_size': 20000,
            'memmap_threshold': 50000,
            'indexing_threshold': 20000,
            'flush_interval_sec': 30,
            'max_optimization_threads': 2
        }
    }
}
```

### Collection Structure
```python
# Agent Zero collections in Qdrant
collections = {
    f"agent_{agent_number}_main": "Main memory area",
    f"agent_{agent_number}_fragments": "Memory fragments", 
    f"agent_{agent_number}_solutions": "Solution patterns",
    f"agent_{agent_number}_metadata": "System metadata",
    f"team_shared": "Shared team memory",
    f"global_knowledge": "Global knowledge base"
}
```

## Neo4j Setup

### Installation Options

#### Option 1: Docker (Recommended)
```bash
# Start Neo4j with persistent storage
docker run -d \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/agent_zero_password \
    -e NEO4J_PLUGINS='["apoc", "graph-data-science"]' \
    -v neo4j_data:/data \
    -v neo4j_logs:/logs \
    neo4j:5.26-community
```

#### Option 2: Neo4j Desktop
```bash
# Download Neo4j Desktop
# Create new database with APOC and GDS plugins
# Configure for Agent Zero usage
```

#### Option 3: Neo4j AuraDB (Cloud)
```bash
# Use Neo4j AuraDB cloud service
# Configure with connection string and credentials
```

### Neo4j Configuration
```python
# Agent Zero Neo4j configuration
NEO4J_CONFIG = {
    'uri': 'bolt://localhost:7687',
    'user': 'neo4j',
    'password': 'agent_zero_password',
    'database': 'neo4j',  # Default database
    'max_connection_lifetime': 3600,
    'max_connection_pool_size': 50,
    'connection_acquisition_timeout': 60,
    'trust': 'TRUST_ALL_CERTIFICATES',  # For development
    'encrypted': False  # Set to True for production
}
```

### Database Schema
```cypher
-- Graphiti namespace isolation
CREATE CONSTRAINT graphiti_episode_id IF NOT EXISTS FOR (e:Episode) REQUIRE e.uuid IS UNIQUE;
CREATE CONSTRAINT graphiti_entity_id IF NOT EXISTS FOR (n:Entity) REQUIRE n.uuid IS UNIQUE;
CREATE INDEX graphiti_group_id IF NOT EXISTS FOR (e:Episode) ON (e.group_id);
CREATE INDEX graphiti_timestamp IF NOT EXISTS FOR (e:Episode) ON (e.created_at);

-- Cognee knowledge graphs
CREATE CONSTRAINT cognee_entity_id IF NOT EXISTS FOR (e:CogneeEntity) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT cognee_relationship_id IF NOT EXISTS FOR (r:CogneeRelationship) REQUIRE r.id IS UNIQUE;
CREATE INDEX cognee_dataset IF NOT EXISTS FOR (e:CogneeEntity) ON (e.dataset);
CREATE INDEX cognee_type IF NOT EXISTS FOR (e:CogneeEntity) ON (e.type);

-- Agent Zero specific indexes
CREATE INDEX agent_namespace IF NOT EXISTS FOR (n) ON (n.agent_id);
CREATE INDEX temporal_queries IF NOT EXISTS FOR (n) ON (n.timestamp);
```

## Database Integration

### Unified Database Client
```python
class DatabaseManager:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.qdrant_client = None
        self.neo4j_driver = None
        
    async def initialize(self):
        """Initialize both database connections"""
        # Initialize Qdrant
        self.qdrant_client = QdrantClient(
            url=self.config.additional['vector_db_url'],
            api_key=self.config.additional.get('qdrant_api_key')
        )
        
        # Initialize Neo4j
        self.neo4j_driver = GraphDatabase.driver(
            self.config.additional['neo4j_uri'],
            auth=(
                self.config.additional['neo4j_user'],
                self.config.additional['neo4j_password']
            )
        )
        
        # Setup collections and schema
        await self.setup_qdrant_collections()
        await self.setup_neo4j_schema()
    
    async def health_check(self):
        """Check health of both databases"""
        qdrant_health = await self.qdrant_client.get_collections()
        neo4j_health = self.neo4j_driver.verify_connectivity()
        
        return {
            'qdrant': len(qdrant_health.collections) > 0,
            'neo4j': neo4j_health is None,  # None means success
            'timestamp': datetime.now()
        }
```

### Fresh Database Initialization
```python
class DatabaseInitializer:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.qdrant_client = QdrantClient()
        self.neo4j_driver = GraphDatabase.driver()

    async def initialize_fresh_databases(self):
        """Initialize clean databases for new Agent Zero instance"""

        # Create Qdrant collections for this agent
        await self.create_agent_collections()

        # Setup Neo4j schema and constraints
        await self.setup_neo4j_schema()

        # Initialize Cognee dataset
        await self.initialize_cognee_dataset()

        # Setup Graphiti namespace
        await self.initialize_graphiti_namespace()

        return "Fresh databases initialized successfully"

    async def create_agent_collections(self):
        """Create Qdrant collections for agent memory areas"""

        collections = [
            f"agent_{self.agent.number}_main",
            f"agent_{self.agent.number}_fragments",
            f"agent_{self.agent.number}_solutions",
            f"agent_{self.agent.number}_metadata"
        ]

        for collection_name in collections:
            await self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=1536,  # OpenAI ada-002 embedding size
                    distance=Distance.COSINE
                ),
                optimizers_config=OptimizersConfig(
                    default_segment_number=2,
                    max_segment_size=20000,
                    memmap_threshold=50000,
                    indexing_threshold=20000,
                    flush_interval_sec=30
                )
            )

    async def initialize_cognee_dataset(self):
        """Initialize Cognee dataset for this agent"""
        dataset_name = f"agent_{self.agent.number}"
        await cognee.prune.prune_data(dataset_name)  # Ensure clean start
        await cognee.config.set_dataset(dataset_name)

    async def initialize_graphiti_namespace(self):
        """Initialize Graphiti namespace for this agent"""
        namespace = f"agent_{self.agent.number}"
        # Graphiti will automatically create namespace on first use
        # No explicit initialization needed
```

## Performance Optimization

### Qdrant Optimization
```python
# Optimize Qdrant for Agent Zero workloads
QDRANT_OPTIMIZATION = {
    'indexing': {
        'threshold': 20000,  # Start indexing after 20k vectors
        'max_segment_size': 20000,  # Optimal for memory usage
        'memmap_threshold': 50000,  # Use memory mapping for large segments
    },
    'search': {
        'hnsw_ef': 128,  # Higher ef for better recall
        'exact': False,  # Use approximate search for speed
        'quantization': {
            'scalar': {
                'type': 'int8',  # Reduce memory usage
                'quantile': 0.99,
                'always_ram': True
            }
        }
    },
    'storage': {
        'on_disk_payload': True,  # Store metadata on disk
        'compression': 'gzip'  # Compress stored data
    }
}
```

### Neo4j Optimization
```cypher
-- Optimize Neo4j for Agent Zero queries
CALL db.index.fulltext.createNodeIndex('entity_search', ['Entity', 'CogneeEntity'], ['name', 'description']);
CALL db.index.fulltext.createRelationshipIndex('relationship_search', ['RELATES_TO', 'MENTIONS'], ['type', 'description']);

-- Configure memory settings
CALL dbms.setConfigValue('dbms.memory.heap.initial_size', '2G');
CALL dbms.setConfigValue('dbms.memory.heap.max_size', '4G');
CALL dbms.setConfigValue('dbms.memory.pagecache.size', '2G');
```

## Monitoring and Maintenance

### Health Monitoring
```python
class DatabaseMonitor:
    async def check_system_health(self):
        """Monitor database health and performance"""
        
        # Qdrant metrics
        qdrant_info = await self.qdrant_client.get_cluster_info()
        qdrant_collections = await self.qdrant_client.get_collections()
        
        # Neo4j metrics
        with self.neo4j_driver.session() as session:
            neo4j_stats = session.run("CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Store file sizes')").single()
        
        return {
            'qdrant': {
                'status': 'healthy' if qdrant_info else 'unhealthy',
                'collections': len(qdrant_collections.collections),
                'memory_usage': qdrant_info.get('memory_usage', 0)
            },
            'neo4j': {
                'status': 'healthy' if neo4j_stats else 'unhealthy',
                'store_size': neo4j_stats.get('value', {}).get('TotalStoreSize', 0),
                'node_count': session.run("MATCH (n) RETURN count(n) as count").single()['count']
            }
        }
```

### Backup Strategy
```bash
#!/bin/bash
# Database backup script

# Backup Qdrant
docker exec qdrant qdrant-backup create --collection-name "agent_*" --output /backups/qdrant_$(date +%Y%m%d_%H%M%S).tar.gz

# Backup Neo4j
docker exec neo4j neo4j-admin database dump --database=neo4j --to-path=/backups/neo4j_$(date +%Y%m%d_%H%M%S).dump

# Cleanup old backups (keep last 7 days)
find /backups -name "*.tar.gz" -mtime +7 -delete
find /backups -name "*.dump" -mtime +7 -delete
```

## Environment Configuration

### Docker Compose Setup
```yaml
# docker-compose.yml for Agent Zero databases
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: agent_zero_qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_storage:/qdrant/storage
      - ./qdrant_config:/qdrant/config
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped

  neo4j:
    image: neo4j:5.26-community
    container_name: agent_zero_neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
      - neo4j_plugins:/plugins
    environment:
      - NEO4J_AUTH=neo4j/agent_zero_password
      - NEO4J_PLUGINS=["apoc", "graph-data-science"]
      - NEO4J_dbms_security_procedures_unrestricted=apoc.*,gds.*
      - NEO4J_dbms_memory_heap_initial__size=2G
      - NEO4J_dbms_memory_heap_max__size=4G
      - NEO4J_dbms_memory_pagecache_size=2G
    restart: unless-stopped

volumes:
  qdrant_storage:
  neo4j_data:
  neo4j_logs:
  neo4j_plugins:
```

### Environment Variables
```bash
# .env file for Agent Zero databases
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty for local deployment

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=agent_zero_password
NEO4J_DATABASE=neo4j

# Performance settings
QDRANT_COLLECTION_PREFIX=agent_zero
NEO4J_MAX_CONNECTIONS=50
DATABASE_TIMEOUT=60

# Backup settings
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=7
BACKUP_PATH=/backups
```

This database setup provides a robust, scalable foundation for the enhanced Agent Zero memory system, replacing FAISS with production-ready Qdrant while enabling advanced knowledge graph capabilities through Neo4j.
