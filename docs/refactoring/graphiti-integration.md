# Enhanced Memory System Integration: Graphiti + Cognee

## Overview

This document details how to integrate both Graphiti's temporal knowledge graph system and Cognee's advanced knowledge processing pipeline to create a sophisticated memory system for Agent Zero. This hybrid approach combines Graphiti's namespace isolation and temporal queries with Cognee's powerful data ingestion, entity extraction, and multi-modal processing capabilities.

## Current Memory System Analysis

### Agent Zero's Current Memory Implementation

Agent Zero currently uses a simple file-based memory system:

```python
# Current memory tools in python/tools/
- memory_save.py    # Saves key-value pairs to files
- memory_load.py    # Loads data from memory files
- memory_delete.py  # Removes memory entries
- memory_forget.py  # Clears memory selectively
```

### Current Memory Flow
1. **Storage**: Facts stored as JSON files in `memory/` directory
2. **Retrieval**: Direct file reading with basic search
3. **Context**: Shared via agent data objects
4. **Persistence**: Files persist between sessions
5. **Organization**: Flat file structure with naming conventions

### Limitations
- No semantic search capabilities
- No relationship modeling
- No temporal queries
- No namespace isolation
- Limited scalability
- No graph-based reasoning
- No entity extraction or knowledge graph construction
- No multi-modal data processing

## Cognee Architecture Analysis

### Core Capabilities
Cognee provides advanced knowledge processing capabilities that complement Graphiti:

#### 1. Data Ingestion Pipeline
```python
# Cognee's multi-modal data processing
await cognee.add([text_file, image_file, audio_file])  # Multi-modal support
await cognee.cognify()  # Knowledge graph construction
results = await cognee.search("query", SearchType.GRAPH_COMPLETION)
```

#### 2. Knowledge Graph Construction
```python
# Cognee's data models
class Node(BaseModel):
    id: str
    name: str
    type: str
    description: str

class Edge(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_name: str

class KnowledgeGraph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
```

#### 3. Advanced Search Types
```python
class SearchType(Enum):
    SUMMARIES = "SUMMARIES"
    INSIGHTS = "INSIGHTS"
    CHUNKS = "CHUNKS"
    RAG_COMPLETION = "RAG_COMPLETION"
    GRAPH_COMPLETION = "GRAPH_COMPLETION"
    CODE = "CODE"
    NATURAL_LANGUAGE = "NATURAL_LANGUAGE"
```

#### 4. Multi-Database Support
- **Graph Databases**: Neo4j, Memgraph, FalkorDB, Kuzu, NetworkX
- **Vector Databases**: Weaviate, Qdrant, ChromaDB, LanceDB, PGVector
- **Hybrid Search**: Combines semantic and keyword search

## Hybrid Architecture: Graphiti + Cognee

### Core Components

#### 1. Knowledge Graph Structure
```python
# Graphiti core entities
EntityNode      # Represents entities (people, places, concepts)
EntityEdge      # Relationships between entities
EpisodicNode    # Time-bound events and episodes
CommunityNode   # Clustered entity groups
```

#### 2. Namespace System
```python
# Namespace-based isolation
group_id: str   # Partition identifier for multi-tenancy
- "agent_0"     # Main agent private namespace
- "agent_1"     # Subordinate agent private namespace
- "shared_team" # Collaborative namespace
- "global"      # System-wide facts
```

#### 3. Temporal Model
```python
# Bi-temporal tracking
created_at: datetime    # When fact was recorded
valid_at: datetime      # When fact was true in real world
```

### Integration Strategy

The hybrid approach leverages the strengths of both systems:

1. **Cognee for Data Processing**: Use Cognee's pipeline for data ingestion, entity extraction, and knowledge graph construction
2. **Graphiti for Memory Management**: Use Graphiti's namespace isolation and temporal queries for agent-specific memory
3. **Unified Interface**: Create a hybrid memory system that combines both capabilities

## Integration Architecture

### 1. HybridMemorySystem Class

Replace current memory tools with unified Graphiti + Cognee interface:

```python
class HybridMemorySystem:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.namespace = f"agent_{agent.number}"

        # Initialize Graphiti for namespace isolation and temporal queries
        self.graphiti = Graphiti(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )

        # Initialize Cognee for advanced processing
        self.cognee_config = self._setup_cognee_config()

        # Hybrid search capabilities
        self.search_engines = {
            "graphiti": GraphitiSearchEngine(self.graphiti, self.namespace),
            "cognee": CogneeSearchEngine(self.cognee_config),
            "hybrid": HybridSearchEngine(self.graphiti, self.cognee_config)
        }

    def _setup_cognee_config(self):
        """Configure Cognee for this agent's namespace"""
        import cognee

        # Set agent-specific data directory
        cognee.config.data_root_directory(f"memory/cognee/{self.namespace}")
        cognee.config.system_root_directory(f"memory/cognee_system/{self.namespace}")

        # Configure graph database to use same Neo4j instance as Graphiti
        cognee.config.set_graph_database_provider("neo4j")
        cognee.config.set_graph_database_url("bolt://localhost:7687")
        cognee.config.set_graph_database_username("neo4j")
        cognee.config.set_graph_database_password("password")

        return cognee.config

    async def save_fact(self, subject: str, predicate: str,
                       object: str, context: str = ""):
        """Save a fact using both Graphiti and Cognee"""

        # Save to Graphiti for namespace isolation
        await self.graphiti.add_fact(
            subject=subject,
            predicate=predicate,
            object=object,
            context=context,
            group_id=self.namespace
        )

        # Process through Cognee for entity extraction and relationships
        fact_text = f"{subject} {predicate} {object}. {context}"
        await cognee.add(fact_text, dataset_name=self.namespace)
        await cognee.cognify([self.namespace])

    async def save_episode(self, content: str, source: str, data_type: str = "text"):
        """Save an episode with multi-modal support"""

        # Save to Graphiti for temporal tracking
        await self.graphiti.add_episode(
            name=f"episode_{uuid.uuid4()}",
            episode_body=content,
            source_description=source,
            reference_time=datetime.now(),
            group_id=self.namespace
        )

        # Process through Cognee for advanced analysis
        if data_type == "text":
            await cognee.add(content, dataset_name=self.namespace)
        elif data_type in ["image", "audio", "video"]:
            # Cognee supports multi-modal data
            await cognee.add([content], dataset_name=self.namespace)

        await cognee.cognify([self.namespace])

    async def search_hybrid(self, query: str, search_type: str = "hybrid",
                           limit: int = 10):
        """Unified search across both systems"""

        if search_type == "temporal":
            # Use Graphiti for temporal queries
            return await self.search_engines["graphiti"].search_temporal(
                query, limit=limit
            )
        elif search_type == "semantic":
            # Use Cognee for semantic search
            return await self.search_engines["cognee"].search_semantic(
                query, limit=limit
            )
        elif search_type == "graph":
            # Use Cognee for graph-based completion
            return await cognee.search(
                query,
                SearchType.GRAPH_COMPLETION,
                datasets=[self.namespace]
            )
        else:
            # Hybrid search combining both systems
            return await self.search_engines["hybrid"].search_combined(
                query, limit=limit
            )
```

### 2. Namespace Management

#### Private Namespaces
Each agent gets its own namespace for private thoughts and context:

```python
# Agent-specific namespaces
agent_0_namespace = "agent_0"  # Main agent
agent_1_namespace = "agent_1"  # First subordinate
agent_2_namespace = "agent_2"  # Second subordinate
```

#### Shared Namespaces
Collaborative spaces for team coordination:

```python
# Shared collaboration namespaces
team_namespace = "team_shared"      # Current team context
project_namespace = "project_xyz"   # Project-specific facts
global_namespace = "global"         # System-wide knowledge
```

#### Namespace Hierarchy
```python
# Namespace access patterns
class NamespaceManager:
    def get_readable_namespaces(self, agent_id: str) -> List[str]:
        """Return namespaces agent can read from"""
        return [
            f"agent_{agent_id}",    # Own private namespace
            "team_shared",          # Team collaboration
            "global"                # Global facts
        ]
    
    def get_writable_namespaces(self, agent_id: str) -> List[str]:
        """Return namespaces agent can write to"""
        return [
            f"agent_{agent_id}",    # Own private namespace
            "team_shared"           # Team collaboration only
        ]
```

### 3. Memory Tool Migration

#### Replace memory_save.py
```python
class GraphitiSaveTool(Tool):
    async def execute(self, key: str, value: str, 
                     namespace: str = "private", **kwargs):
        """Save information to Graphiti knowledge graph"""
        
        # Determine target namespace
        if namespace == "private":
            group_id = f"agent_{self.agent.number}"
        elif namespace == "shared":
            group_id = "team_shared"
        else:
            group_id = namespace
            
        # Save as episode for unstructured data
        await self.agent.graphiti_memory.save_episode(
            name=key,
            episode_body=value,
            source_description=f"Agent {self.agent.number} memory save",
            reference_time=datetime.now(),
            group_id=group_id
        )
```

#### Replace memory_load.py
```python
class GraphitiLoadTool(Tool):
    async def execute(self, query: str, namespace: str = "all", 
                     limit: int = 5, **kwargs):
        """Load information from Graphiti knowledge graph"""
        
        # Determine search namespaces
        if namespace == "private":
            group_ids = [f"agent_{self.agent.number}"]
        elif namespace == "shared":
            group_ids = ["team_shared"]
        elif namespace == "all":
            group_ids = self.agent.namespace_manager.get_readable_namespaces(
                str(self.agent.number)
            )
        else:
            group_ids = [namespace]
            
        # Perform hybrid search
        results = await self.agent.graphiti_memory.search_facts(
            query=query,
            group_ids=group_ids,
            limit=limit
        )
        
        return self.format_search_results(results)
```

### 4. Extension Integration

#### Memory Recall Extension
Update `_50_recall_memories.py` to use Graphiti:

```python
class RecallMemoriesExtension(Extension):
    async def execute(self, loop_data: LoopData, **kwargs):
        """Recall relevant memories using Graphiti search"""
        
        if not loop_data.user_message:
            return
            
        # Extract query from user message
        query = loop_data.user_message.content.get("message", "")
        
        # Search across readable namespaces
        memories = await self.agent.graphiti_memory.load_facts(
            query=query,
            limit=10
        )
        
        if memories:
            # Add to loop context
            loop_data.extras_persistent["recalled_memories"] = {
                "type": "memories",
                "content": memories,
                "source": "graphiti_recall"
            }
```

#### Memory Storage Extension
Update `_50_memorize_fragments.py`:

```python
class MemorizeFragmentsExtension(Extension):
    async def execute(self, loop_data: LoopData, **kwargs):
        """Extract and store important facts from conversation"""
        
        # Get recent conversation context
        recent_messages = self.agent.history.get_recent_messages(5)
        
        # Extract facts using LLM
        facts = await self.extract_facts_from_conversation(recent_messages)
        
        # Store each fact in Graphiti
        for fact in facts:
            await self.agent.graphiti_memory.save_fact(
                subject=fact["subject"],
                predicate=fact["predicate"], 
                object=fact["object"],
                context=fact.get("context", "")
            )
```

## Implementation Steps

### Step 1: Setup Graphiti Service
```bash
# Start Neo4j database
docker run -d \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    neo4j:5.26

# Install Graphiti
pip install graphiti-core
```

### Step 2: Create GraphitiMemory Class
```python
# python/helpers/graphiti_memory.py
class GraphitiMemory:
    def __init__(self, agent):
        self.agent = agent
        self.graphiti = self._initialize_graphiti()
        self.namespace_manager = NamespaceManager()
    
    def _initialize_graphiti(self):
        return Graphiti(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", "password")
        )
```

### Step 3: Update Agent Class
```python
# agent.py modifications
class Agent:
    def __init__(self, number: int, config: AgentConfig, 
                 context: AgentContext | None = None):
        # ... existing initialization ...
        
        # Add Graphiti memory
        self.graphiti_memory = GraphitiMemory(self)
        self.namespace_manager = NamespaceManager()
```

### Step 4: Migrate Memory Tools
1. Replace `memory_save.py` with `graphiti_save.py`
2. Replace `memory_load.py` with `graphiti_load.py`
3. Update `memory_delete.py` for Graphiti deletion
4. Modify `memory_forget.py` for namespace-aware forgetting

### Step 5: Update Extensions
1. Modify memory recall extensions
2. Update memorization extensions
3. Add namespace management extensions
4. Create memory migration utilities

## Configuration

### Environment Variables
```bash
# .env additions
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GRAPHITI_NAMESPACE_PREFIX=agent_zero
OPENAI_API_KEY=your_openai_key  # For embeddings
```

### Agent Configuration
```python
# AgentConfig additions
@dataclass
class AgentConfig:
    # ... existing fields ...
    
    # Graphiti configuration
    graphiti_enabled: bool = True
    graphiti_namespace_prefix: str = "agent_zero"
    graphiti_max_search_results: int = 10
    graphiti_embedding_model: str = "text-embedding-3-small"
```

## Testing Strategy

### Unit Tests
```python
# Test namespace isolation
def test_namespace_isolation():
    agent1 = Agent(1, config, context)
    agent2 = Agent(2, config, context)
    
    # Agent 1 saves private fact
    agent1.graphiti_memory.save_fact("user", "likes", "coffee")
    
    # Agent 2 should not see private fact
    results = agent2.graphiti_memory.load_facts("coffee")
    assert len(results) == 0

# Test shared namespace
def test_shared_namespace():
    agent1 = Agent(1, config, context)
    agent2 = Agent(2, config, context)
    
    # Save to shared namespace
    agent1.graphiti_memory.save_fact(
        "project", "status", "active", 
        namespace="team_shared"
    )
    
    # Agent 2 should see shared fact
    results = agent2.graphiti_memory.load_facts("project status")
    assert len(results) > 0
```

### Integration Tests
```python
# Test memory persistence
def test_memory_persistence():
    # Save facts with agent
    agent = Agent(1, config, context)
    agent.graphiti_memory.save_fact("user", "name", "John")
    
    # Restart agent (new instance)
    new_agent = Agent(1, config, context)
    results = new_agent.graphiti_memory.load_facts("user name")
    
    assert "John" in str(results)
```

## Migration Strategy

### Data Migration
```python
# Migration script for existing memory files
class MemoryMigrator:
    def migrate_file_memory_to_graphiti(self, memory_dir: str):
        """Migrate existing file-based memory to Graphiti"""
        
        for memory_file in os.listdir(memory_dir):
            if memory_file.endswith('.json'):
                # Load existing memory
                with open(f"{memory_dir}/{memory_file}") as f:
                    data = json.load(f)
                
                # Convert to Graphiti episode
                self.graphiti.add_episode(
                    name=memory_file.replace('.json', ''),
                    episode_body=json.dumps(data),
                    source_description="Migrated from file memory",
                    reference_time=datetime.now(),
                    group_id="migrated"
                )
```

### Backward Compatibility
```python
# Fallback mechanism during transition
class HybridMemory:
    def __init__(self, agent):
        self.graphiti_memory = GraphitiMemory(agent)
        self.file_memory = FileMemory(agent)  # Legacy system
        
    async def load_facts(self, query: str):
        # Try Graphiti first
        results = await self.graphiti_memory.load_facts(query)
        
        # Fallback to file memory if needed
        if not results:
            results = self.file_memory.load_facts(query)
            
        return results
```

## Performance Considerations

### Optimization Strategies
1. **Connection Pooling**: Reuse Neo4j connections
2. **Query Caching**: Cache frequent queries
3. **Batch Operations**: Group multiple operations
4. **Async Operations**: Non-blocking memory operations
5. **Index Optimization**: Proper Neo4j indexing

### Monitoring
```python
# Performance monitoring
class GraphitiMonitor:
    def __init__(self):
        self.query_times = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    def log_query_time(self, duration: float):
        self.query_times.append(duration)
        
    def get_average_query_time(self) -> float:
        return sum(self.query_times) / len(self.query_times)
```

This integration transforms Agent Zero's memory from simple file storage to a sophisticated temporal knowledge graph, enabling advanced reasoning, relationship discovery, and collaborative memory sharing between agents.
