# Cognee Integration Guide

## Overview

This document details how Cognee's advanced knowledge processing capabilities are integrated into the enhanced Agent Zero memory system by default. Cognee provides sophisticated data ingestion, entity extraction, knowledge graph construction, and multi-modal processing that significantly enhances Agent Zero's memory capabilities beyond what Graphiti alone can provide. **Cognee is enabled by default** in the enhanced Agent Zero implementation, working seamlessly with Qdrant and Graphiti.

## Cognee Capabilities Analysis

### Core Features
- **Multi-modal Data Processing**: Text, images, audio, video, and code
- **Advanced Entity Extraction**: Automatic identification of entities and relationships
- **Knowledge Graph Construction**: Automated graph building from unstructured data
- **Hybrid Search**: Combines semantic, keyword, and graph-based search
- **Multiple Database Support**: Neo4j, Memgraph, ChromaDB, Weaviate, and more
- **Pipeline Architecture**: Configurable processing pipelines for different data types

### Search Types
```python
class SearchType(Enum):
    SUMMARIES = "SUMMARIES"           # Extract summaries from data
    INSIGHTS = "INSIGHTS"             # Generate insights and patterns
    CHUNKS = "CHUNKS"                 # Retrieve relevant chunks
    RAG_COMPLETION = "RAG_COMPLETION" # RAG-based responses
    GRAPH_COMPLETION = "GRAPH_COMPLETION" # Graph-based responses
    CODE = "CODE"                     # Code-specific search
    NATURAL_LANGUAGE = "NATURAL_LANGUAGE" # Natural language queries
```

### Data Models
```python
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

## Integration Architecture

### 1. CogneeMemoryProcessor Class

```python
class CogneeMemoryProcessor:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.namespace = f"agent_{agent.number}"
        self.dataset_name = f"agent_zero_{self.namespace}"
        
        # Configure Cognee for this agent
        self._setup_cognee_environment()
        
    def _setup_cognee_environment(self):
        """Configure Cognee for agent-specific processing"""
        import cognee
        
        # Set agent-specific directories
        data_dir = f"memory/cognee_data/{self.namespace}"
        system_dir = f"memory/cognee_system/{self.namespace}"
        
        cognee.config.data_root_directory(data_dir)
        cognee.config.system_root_directory(system_dir)
        
        # Configure database connections
        cognee.config.set_graph_database_provider("neo4j")
        cognee.config.set_graph_database_url("bolt://localhost:7687")
        cognee.config.set_graph_database_username("neo4j")
        cognee.config.set_graph_database_password("password")
        
        # Configure vector database
        cognee.config.set_vector_database_provider("chromadb")
        cognee.config.set_vector_database_url(f"memory/chromadb/{self.namespace}")
        
        # Set embedding model to match Agent Zero's configuration
        cognee.config.set_embedding_model(
            provider=self.agent.config.embeddings_model.provider.name,
            model=self.agent.config.embeddings_model.name
        )
    
    async def process_conversation_memory(self, conversation_text: str, 
                                        metadata: dict = None):
        """Process conversation text through Cognee pipeline"""
        
        # Add conversation to Cognee
        await cognee.add(conversation_text, dataset_name=self.dataset_name)
        
        # Process through knowledge graph construction
        await cognee.cognify([self.dataset_name])
        
        # Extract insights and summaries
        insights = await cognee.search(
            "Extract key insights and facts from this conversation",
            SearchType.INSIGHTS,
            datasets=[self.dataset_name]
        )
        
        return {
            "processed": True,
            "insights": insights,
            "dataset": self.dataset_name
        }
    
    async def process_multimodal_data(self, data_files: list, 
                                    data_types: list = None):
        """Process multi-modal data (images, audio, documents)"""
        
        # Cognee supports multi-modal processing
        await cognee.add(data_files, dataset_name=self.dataset_name)
        await cognee.cognify([self.dataset_name])
        
        # Generate summaries for each data type
        summaries = []
        for data_file in data_files:
            summary = await cognee.search(
                f"Summarize the content of {data_file}",
                SearchType.SUMMARIES,
                datasets=[self.dataset_name]
            )
            summaries.append(summary)
        
        return summaries
    
    async def extract_entities_and_relationships(self, text: str):
        """Extract structured entities and relationships"""
        
        # Add text and process
        await cognee.add(text, dataset_name=self.dataset_name)
        await cognee.cognify([self.dataset_name])
        
        # Use graph completion to extract structured data
        entities = await cognee.search(
            "List all entities mentioned in the text",
            SearchType.GRAPH_COMPLETION,
            datasets=[self.dataset_name]
        )
        
        relationships = await cognee.search(
            "List all relationships between entities",
            SearchType.GRAPH_COMPLETION,
            datasets=[self.dataset_name]
        )
        
        return {
            "entities": entities,
            "relationships": relationships
        }
    
    async def search_knowledge_graph(self, query: str, 
                                   search_type: SearchType = SearchType.GRAPH_COMPLETION):
        """Search the constructed knowledge graph"""
        
        return await cognee.search(
            query,
            search_type,
            datasets=[self.dataset_name]
        )
    
    async def get_contextual_insights(self, query: str, context_window: int = 5):
        """Get insights with expanded context"""
        
        # Use Cognee's context extension capabilities
        return await cognee.search(
            query,
            SearchType.GRAPH_COMPLETION_CONTEXT_EXTENSION,
            datasets=[self.dataset_name],
            top_k=context_window
        )
```

### 2. Enhanced Memory Tools

#### Replace memory_save.py with CogneeMemorySave
```python
class CogneeMemorySave(Tool):
    async def execute(self, text="", area="", data_type="text", **kwargs):
        
        if not area:
            area = Memory.Area.MAIN.value
        
        metadata = {"area": area, "data_type": data_type, **kwargs}
        
        # Process through Cognee for advanced analysis
        processor = CogneeMemoryProcessor(self.agent)
        
        if data_type == "conversation":
            result = await processor.process_conversation_memory(text, metadata)
        elif data_type in ["image", "audio", "video"]:
            result = await processor.process_multimodal_data([text], [data_type])
        else:
            # Standard text processing
            await cognee.add(text, dataset_name=processor.dataset_name)
            await cognee.cognify([processor.dataset_name])
            result = {"processed": True, "dataset": processor.dataset_name}
        
        # Also save to traditional memory system for backward compatibility
        db = await Memory.get(self.agent)
        memory_id = await db.insert_text(text, metadata)
        
        response_text = self.agent.read_prompt(
            "fw.memory_saved_enhanced.md", 
            memory_id=memory_id,
            cognee_result=result
        )
        
        return Response(message=response_text, break_loop=False)
```

#### Replace memory_load.py with CogneeMemoryLoad
```python
class CogneeMemoryLoad(Tool):
    async def execute(self, query="", search_type="hybrid", limit=10, **kwargs):
        
        processor = CogneeMemoryProcessor(self.agent)
        
        # Determine search strategy
        if search_type == "insights":
            results = await processor.search_knowledge_graph(
                query, SearchType.INSIGHTS
            )
        elif search_type == "graph":
            results = await processor.search_knowledge_graph(
                query, SearchType.GRAPH_COMPLETION
            )
        elif search_type == "contextual":
            results = await processor.get_contextual_insights(query)
        else:
            # Hybrid search combining Cognee and traditional memory
            cognee_results = await processor.search_knowledge_graph(query)
            
            # Also search traditional memory for backward compatibility
            db = await Memory.get(self.agent)
            traditional_results = await db.search_similarity_threshold(
                query, limit=limit//2, threshold=0.7
            )
            
            results = {
                "cognee_results": cognee_results,
                "traditional_results": traditional_results
            }
        
        response_text = self.agent.read_prompt(
            "fw.memory_loaded_enhanced.md",
            query=query,
            results=results,
            search_type=search_type
        )
        
        return Response(message=response_text, break_loop=False)
```

### 3. Code Analysis Integration

Cognee has specialized code analysis capabilities that can enhance Agent Zero's code understanding:

```python
class CogneeCodeAnalyzer:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.processor = CogneeMemoryProcessor(agent)
    
    async def analyze_codebase(self, repo_path: str, include_docs: bool = True):
        """Analyze entire codebase using Cognee's code graph pipeline"""
        
        from cognee.api.v1.cognify.code_graph_pipeline import run_code_graph_pipeline
        
        # Run Cognee's specialized code analysis
        async for status in run_code_graph_pipeline(repo_path, include_docs):
            if status:
                break
        
        # Search for code patterns and dependencies
        code_insights = await cognee.search(
            "Analyze code structure and dependencies",
            SearchType.CODE,
            datasets=[self.processor.dataset_name]
        )
        
        return code_insights
    
    async def search_code_patterns(self, pattern_query: str):
        """Search for specific code patterns"""
        
        return await cognee.search(
            pattern_query,
            SearchType.CODE,
            datasets=[self.processor.dataset_name]
        )
```

### 4. Multi-Modal Memory Extension

```python
class MultiModalMemoryExtension(Extension):
    async def execute(self, loop_data: LoopData, **kwargs):
        """Process multi-modal inputs through Cognee"""
        
        if not loop_data.user_message:
            return
        
        # Check for multi-modal content
        content = loop_data.user_message.content
        
        if content.get("images") or content.get("audio") or content.get("files"):
            processor = CogneeMemoryProcessor(self.agent)
            
            # Process multi-modal data
            media_files = []
            if content.get("images"):
                media_files.extend(content["images"])
            if content.get("audio"):
                media_files.extend(content["audio"])
            if content.get("files"):
                media_files.extend(content["files"])
            
            if media_files:
                summaries = await processor.process_multimodal_data(media_files)
                
                # Add summaries to loop context
                loop_data.extras_persistent["multimodal_analysis"] = {
                    "type": "cognee_multimodal",
                    "summaries": summaries,
                    "file_count": len(media_files)
                }
```

## Configuration and Setup

### Environment Variables
```bash
# Cognee configuration
COGNEE_DATA_ROOT_DIR=memory/cognee_data
COGNEE_SYSTEM_ROOT_DIR=memory/cognee_system
COGNEE_GRAPH_DB_PROVIDER=neo4j
COGNEE_VECTOR_DB_PROVIDER=chromadb
COGNEE_LLM_PROVIDER=openai
COGNEE_EMBEDDING_PROVIDER=openai
```

### Agent Configuration
```python
@dataclass
class AgentConfig:
    # ... existing fields ...
    
    # Cognee configuration
    cognee_enabled: bool = True
    cognee_multimodal_enabled: bool = True
    cognee_code_analysis_enabled: bool = True
    cognee_hybrid_search_enabled: bool = True
    cognee_context_extension_enabled: bool = True
```

## Benefits of Cognee Integration

### 1. Advanced Entity Extraction
- Automatic identification of people, places, concepts, and relationships
- Structured knowledge graph construction from unstructured data
- Better understanding of context and connections

### 2. Multi-Modal Processing
- Support for images, audio, video, and documents
- Unified processing pipeline for all data types
- Cross-modal relationship understanding

### 3. Enhanced Search Capabilities
- Multiple search types (insights, summaries, graph completion)
- Contextual search with relationship awareness
- Code-specific search and analysis

### 4. Improved Knowledge Retention
- Persistent knowledge graphs that grow over time
- Relationship-aware memory that connects related concepts
- Temporal understanding of how knowledge evolves

### 5. Better Agent Collaboration
- Shared knowledge graphs for team coordination
- Entity-relationship mapping for better context sharing
- Structured knowledge that can be easily queried and reasoned about

This integration transforms Agent Zero's memory from simple vector storage to a sophisticated knowledge processing system capable of understanding, relating, and reasoning about complex multi-modal information.
