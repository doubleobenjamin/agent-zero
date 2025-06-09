# Agent Zero Codebase Adaptation Guide

## Overview

This guide details how to adapt the existing Agent Zero codebase to integrate enhanced capabilities while preserving the current architecture and patterns. The approach extends existing classes and systems rather than replacing them.

## Current Architecture Analysis

### Core Components

#### 1. Agent Class (`agent.py`)
```python
# Current structure
class Agent:
    def __init__(self, number: int, config: AgentConfig, context: AgentContext | None = None):
        self.config = config
        self.context = context or AgentContext(config)
        self.number = number
        self.agent_name = f"Agent {self.number}"
        self.history = history.History(self)
        self.data = {}  # Free data object for tools
    
    async def monologue(self):
        # Main message loop with extensions
        
    async def process_tools(self, agent_response):
        # Tool execution logic
```

**Adaptation Strategy**: Extend the existing Agent class with optional enhanced capabilities controlled by configuration flags.

#### 2. Memory System (`python/helpers/memory.py`)
```python
# Current structure (FAISS-based)
class Memory:
    index: dict[str, "MyFaiss"] = {}  # Static index of FAISS databases

    def __init__(self, agent: Agent, db: MyFaiss, memory_subdir: str):
        self.agent = agent
        self.db = db  # FAISS vector database
        self.memory_subdir = memory_subdir

    async def search_similarity_threshold(self, query: str, limit: int, threshold: float):
        # Vector similarity search

    async def insert_text(self, text, metadata: dict = {}):
        # Insert text into vector database
```

**Implementation Strategy**: Replace FAISS with Qdrant and integrate Graphiti + Cognee by default. Build new Memory class with enhanced capabilities from the ground up.

#### 3. Tool System (`python/tools/`)
```python
# Current pattern - each tool is a separate file
class Tool:
    async def execute(self, **kwargs):
        # Tool implementation
        
# Examples:
# - memory_save.py
# - memory_load.py  
# - call_subordinate.py
# - code_execution_tool.py
```

**Adaptation Strategy**: Create enhanced versions of existing tools that can optionally use ACI while maintaining backward compatibility.

#### 4. Extension System (`python/extensions/`)
```python
# Current pattern - extensions modify behavior at specific points
# - monologue_start/
# - message_loop_start/
# - message_loop_prompts_before/
# - message_loop_prompts_after/
# - message_loop_end/
# - monologue_end/
```

**Adaptation Strategy**: Add new extensions for enhanced capabilities while preserving existing extension points.

## Adaptation Strategies

### 1. Enhanced Memory System

#### Replace FAISS with Qdrant + Integrate Graphiti/Cognee by Default
```python
class EnhancedMemory(Memory):
    def __init__(self, agent: Agent, memory_subdir: str):
        self.agent = agent
        self.memory_subdir = memory_subdir

        # Replace FAISS with Qdrant
        self.qdrant_client = QdrantVectorDB(
            collection_name=f"agent_{agent.number}_{memory_subdir}",
            embedding_model=agent.config.embeddings_model
        )

        # Graphiti + Cognee enabled by default
        self.graphiti_service = GraphitiService(
            agent=agent,
            namespace=f"agent_{agent.number}",
            memory_subdir=memory_subdir
        )
        self.cognee_processor = CogneeProcessor(
            agent=agent,
            dataset_name=f"agent_{agent.number}_{memory_subdir}"
        )

        # Hybrid search combining all systems
        self.hybrid_search = HybridSearchEngine(
            qdrant=self.qdrant_client,
            graphiti=self.graphiti_service,
            cognee=self.cognee_processor
        )

    async def insert_text(self, text, metadata: dict = {}):
        # Multi-system storage by default

        # 1. Store in Qdrant for vector similarity
        doc_id = await self.qdrant_client.insert_text(text, metadata)

        # 2. Process through Cognee for entity extraction and knowledge graphs
        cognee_result = await self.cognee_processor.add_and_cognify(text, metadata)

        # 3. Store in Graphiti for temporal queries and namespace isolation
        await self.graphiti_service.save_episode(
            name=f"memory_{doc_id}",
            episode_body=text,
            source_description=metadata.get('area', 'main'),
            reference_time=datetime.now(),
            group_id=f"agent_{self.agent.number}",
            entities=cognee_result.get('entities', []),
            relationships=cognee_result.get('relationships', [])
        )

        return {
            'doc_id': doc_id,
            'entities_extracted': len(cognee_result.get('entities', [])),
            'relationships_mapped': len(cognee_result.get('relationships', [])),
            'knowledge_graph_updated': True
        }

    async def search_similarity_threshold(self, query: str, limit: int, threshold: float):
        """Maintain existing interface but use hybrid search"""
        return await self.hybrid_search.search(
            query=query,
            search_type="semantic",
            limit=limit,
            threshold=threshold
        )

    async def search_enhanced(self, query: str, search_type: str = "hybrid", limit: int = 5):
        """Enhanced search with multiple types"""
        return await self.hybrid_search.search(
            query=query,
            search_type=search_type,
            limit=limit
        )
```

#### Update Memory Tools
```python
# Enhanced memory_save.py with rich feedback
class MemorySave(Tool):
    async def execute(self, text: str, area: str = "main"):
        memory = await Memory.get(self.agent)

        # Enhanced memory is now the default
        result = await memory.insert_text(text, {"area": area})

        # Rich feedback from multi-system storage
        if isinstance(result, dict):
            feedback = f"✅ Memory saved successfully!\n"
            feedback += f"📄 Document ID: {result['doc_id']}\n"
            feedback += f"🏷️ Entities extracted: {result['entities_extracted']}\n"
            feedback += f"🔗 Relationships mapped: {result['relationships_mapped']}\n"
            feedback += f"📊 Knowledge graph updated: {result['knowledge_graph_updated']}\n"
            feedback += f"🗂️ Area: {area}"
            return feedback
        else:
            # Fallback for simple doc_id return
            return f"Memory saved with ID {result}"

# Enhanced memory_load.py with multiple search types
class MemoryLoad(Tool):
    async def execute(self, query: str, area: str = "all", limit: int = 5, search_type: str = "hybrid"):
        memory = await Memory.get(self.agent)

        # Use enhanced search capabilities
        if hasattr(memory, 'search_enhanced'):
            results = await memory.search_enhanced(
                query=query,
                search_type=search_type,
                limit=limit
            )

            # Rich results formatting
            if results and len(results) > 0:
                feedback = f"🔍 Found {len(results)} relevant memories:\n\n"
                for i, result in enumerate(results, 1):
                    feedback += f"{i}. {result.get('text', result)[:200]}...\n"
                    if 'entities' in result:
                        feedback += f"   🏷️ Entities: {', '.join(result['entities'][:3])}\n"
                    if 'confidence' in result:
                        feedback += f"   📊 Relevance: {result['confidence']:.2f}\n"
                    feedback += "\n"
                return feedback
            else:
                return f"No memories found for query: {query}"
        else:
            # Fallback to existing search
            return await self.existing_memory_load(query, area, limit)
```

### 2. Enhanced Agent Orchestration

#### Extend Existing Agent Class
```python
class Agent:
    def __init__(self, number: int, config: AgentConfig, context: AgentContext | None = None):
        # Existing initialization
        self.config = config
        self.context = context or AgentContext(config)
        self.number = number
        self.agent_name = f"Agent {self.number}"
        self.history = history.History(self)
        self.data = {}
        
        # Enhanced capabilities (enabled by default)
        self.agno_orchestrator = AgnoOrchestrator(self)
        self.agent_registry = AgentRegistry()
        self.task_analyzer = TaskAnalyzer(self)

        # ACI tools (optional, can be disabled)
        if config.additional.get('aci_tools', True):  # Default enabled
            self.aci_interface = ACIToolInterface(self)
    
    async def enhanced_task_delegation(self, task: str, task_type: str = "general"):
        """Enhanced task delegation with intelligent orchestration (default behavior)"""
        # Analyze task complexity using enhanced capabilities
        analysis = await self.task_analyzer.analyze_task_requirements(task)

        if analysis["complexity"] == "simple":
            # Handle directly with enhanced tools and memory
            return await self.handle_with_enhanced_tools(task)
        elif analysis["complexity"] == "specialist":
            # Get or create specialist agent
            specialist = await self.agno_orchestrator.get_or_create_specialist(
                analysis["required_expertise"][0]
            )
            return await specialist.handle_task(task)
        else:
            # Create coordinated team
            team = await self.agno_orchestrator.create_team(
                task, analysis["required_expertise"], analysis["coordination_mode"]
            )
            return await team.execute_task(task)
```

#### Update Call Subordinate Tool
```python
# Enhance existing call_subordinate.py
class CallSubordinate(Tool):
    async def execute(self, message: str, reset: str = "true"):
        # Check if enhanced orchestration is available
        if hasattr(self.agent, 'agno_orchestrator') and reset == "true":
            # Use enhanced delegation
            return await self.agent.enhanced_task_delegation(message)
        else:
            # Use existing subordinate creation logic
            return await self.existing_subordinate_logic(message, reset)
```

### 3. Enhanced Tool System

#### Create ACI Tool Interface
```python
class ACIToolInterface:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.aci_enabled = agent.config.additional.get('aci_tools', False)
        self.tool_registry = ACIToolRegistry()
    
    async def execute_tool(self, tool_name: str, **kwargs):
        if self.aci_enabled and await self.is_aci_tool(tool_name):
            # Use ACI unified interface
            return await self.tool_registry.execute(tool_name, **kwargs)
        else:
            # Fall back to existing tool system
            return await self.execute_existing_tool(tool_name, **kwargs)
    
    async def discover_tools(self, category: str = None):
        """Discover available tools through ACI"""
        if self.aci_enabled:
            return await self.tool_registry.discover_tools(category)
        else:
            return self.get_existing_tools()
```

#### Enhance Existing Tools
```python
# Enhance existing search_engine.py
class SearchEngine(Tool):
    async def execute(self, query: str, num_results: int = 5):
        # Check if ACI tools are available
        if hasattr(self.agent, 'aci_interface') and self.agent.aci_interface.aci_enabled:
            # Use ACI unified search
            return await self.agent.aci_interface.execute_tool("web_search", 
                                                              query=query, 
                                                              num_results=num_results)
        else:
            # Use existing search implementation
            return await self.existing_search_logic(query, num_results)
```

### 4. Configuration Enhancement

#### Extend AgentConfig
```python
@dataclass
class AgentConfig:
    # Existing fields
    chat_model: ModelConfig
    utility_model: ModelConfig
    embeddings_model: ModelConfig
    browser_model: ModelConfig
    mcp_servers: str
    prompts_subdir: str = ""
    memory_subdir: str = ""
    knowledge_subdirs: list[str] = field(default_factory=lambda: ["default", "custom"])
    
    # Enhanced capabilities (new defaults)
    additional: Dict[str, Any] = field(default_factory=lambda: {
        # Memory enhancements (enabled by default)
        'enhanced_memory': True,            # Graphiti + Cognee hybrid memory (default)
        'knowledge_graphs': True,           # Automatic knowledge graph construction (default)
        'multi_modal_memory': True,         # Multi-modal data processing (default)

        # Agent orchestration (enabled by default)
        'agno_orchestration': True,         # Multi-agent orchestration (default)
        'persistent_agents': True,          # Persistent expert agents (default)
        'team_coordination': True,          # Team coordination modes (default)

        # Tool enhancements (optional but recommended)
        'aci_tools': True,                  # ACI unified tool interface (default enabled)
        'dynamic_tool_discovery': True,    # Runtime tool discovery (default enabled)
        'enhanced_authentication': True,   # Advanced auth management (default enabled)

        # Database configuration (production-ready defaults)
        'neo4j_uri': 'bolt://localhost:7687',
        'neo4j_user': 'neo4j',
        'neo4j_password': 'password',
        'vector_db_provider': 'qdrant',     # Qdrant as default (production-ready)
        'vector_db_url': 'http://localhost:6333',
        'qdrant_collection_prefix': 'agent_zero',

        # Cognee configuration
        'cognee_graph_db': 'neo4j',         # Use same Neo4j instance
        'cognee_vector_db': 'qdrant',       # Use same Qdrant instance

        # Performance settings
        'enable_caching': True,
        'cache_ttl': 3600,                  # 1 hour cache TTL
        'max_concurrent_agents': 10,
        'memory_optimization': True
    })
```

### 5. Extension System Enhancement

#### Add New Extension Points
```python
# New extension: enhanced_memory_processing
# python/extensions/message_loop_end/_60_enhanced_memory_processing.py
async def execute(agent, loop_data):
    if agent.config.additional.get('enhanced_memory', False):
        # Process conversation through Cognee
        conversation_text = loop_data.last_response
        if conversation_text and hasattr(agent, 'enhanced_memory'):
            await agent.enhanced_memory.cognee_processor.process_conversation(
                conversation_text, 
                {"agent_id": agent.number, "timestamp": datetime.now()}
            )

# New extension: orchestration_monitoring  
# python/extensions/monologue_end/_60_orchestration_monitoring.py
async def execute(agent, loop_data):
    if hasattr(agent, 'agno_orchestrator'):
        # Monitor and learn from agent performance
        await agent.agno_orchestrator.record_performance_metrics(loop_data)
```

## Implementation Strategy

### Phase 1: Foundation
1. Build enhanced classes with new capabilities from the ground up
2. Implement Qdrant + Neo4j database architecture
3. Create enhanced memory system with Graphiti + Cognee integration
4. Build ACI tool interface for unified tool access

### Phase 2: Integration
1. Implement enhanced tools with rich capabilities
2. Add new extensions for enhanced processing
3. Setup fresh database initialization and configuration
4. Create enhanced prompt templates and variables

### Phase 3: Optimization
1. Performance tune hybrid systems
2. Add monitoring and metrics collection
3. Optimize database queries and caching
4. Fine-tune orchestration algorithms

## Benefits of This Approach

### 1. Clean Implementation
- Fresh start with no legacy constraints
- Optimized for enhanced capabilities from day one
- No technical debt from previous implementations

### 2. Enhanced Performance
- Production-ready Qdrant vector database
- Optimized Neo4j graph database setup
- Advanced capabilities enabled by default

### 3. Reduces Development Complexity
- Building on proven Agent Zero patterns
- Clean architecture with clear separation of concerns
- No backward compatibility constraints

### 4. Immediate Value
- Users get enhanced capabilities immediately
- Rich feedback and advanced search out of the box
- Knowledge graphs and entity extraction by default

This adaptation strategy leverages Agent Zero's existing strengths while adding powerful new capabilities through careful extension and enhancement of the current codebase.
