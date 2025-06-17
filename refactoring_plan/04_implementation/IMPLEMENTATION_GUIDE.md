# Implementation Guide: Unified Graphiti Memory & Knowledge System

## Overview

This guide provides step-by-step instructions for implementing Graphiti's temporal knowledge graph as a unified memory and knowledge system for agent-zero. The enhanced system handles both agent conversations (simple episode storage) and knowledge documents (with entity extraction) through a single abstraction layer for maximum intelligence capabilities. Since we're working with a fresh repository, we can implement the new system directly without migration concerns.

## Phase 1: Environment Setup

### Step 1: Install Dependencies

```bash
# Install Graphiti with all LLM providers
pip install "graphiti-core[anthropic,groq,google-genai]"

# Install additional testing dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Verify installation
python -c "import graphiti_core; print('✅ Graphiti installed successfully')"
```

### Step 2: Set Up Neo4j Database

#### Option A: Docker (Recommended)
```bash
# Start Neo4j container
docker run -d \
  --name neo4j-agent-zero \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_dbms_memory_heap_initial__size=1G \
  -e NEO4J_dbms_memory_heap_max__size=2G \
  -e NEO4J_dbms_memory_pagecache_size=1G \
  neo4j:5.22.0

# Verify Neo4j is running
docker ps | grep neo4j
```

#### Option B: Local Installation
```bash
# Download and install Neo4j Community Edition
# Follow instructions at: https://neo4j.com/download/

# Start Neo4j service
neo4j start

# Access Neo4j Browser at http://localhost:7474
```

### Step 3: Configure Environment Variables

Create `.env` file in project root:
```bash
# Graphiti Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GRAPHITI_GROUP_ID=agent-zero-default

# Memory Backend Selection
MEMORY_BACKEND=graphiti
GRAPHITI_ENABLED=true

# LLM Configuration (required for Graphiti)
OPENAI_API_KEY=your_openai_api_key
MODEL_NAME=gpt-4.1-mini

# Optional: Alternative LLM providers
# ANTHROPIC_API_KEY=your_anthropic_key
# GOOGLE_API_KEY=your_google_key
```

### Step 4: Test Connections

```bash
# Test Neo4j connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1 as test')
    print('✅ Neo4j connection successful')
driver.close()
"

# Test OpenAI API
python -c "
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
models = client.models.list()
print('✅ OpenAI API connection successful')
"
```

## Phase 2: Core Implementation

### Step 5: Create Enhanced Memory & Knowledge Abstraction Layer

Create `python/helpers/memory_abstraction.py`:

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MemoryDocument:
    """Unified memory document representation"""
    id: str
    page_content: str  # CORRECTED: Use page_content for LangChain compatibility
    metadata: Dict[str, Any]
    score: Optional[float] = None

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
    ) -> List[MemoryDocument]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Delete documents by IDs"""
        pass
    
    @abstractmethod
    async def delete_documents_by_query(
        self, 
        query: str, 
        threshold: float = 0.75,
        filter: str = ""
    ) -> List[MemoryDocument]:
        """Delete documents by query"""
        pass
    
    @abstractmethod
    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Retrieve documents by IDs"""
        pass

    @abstractmethod
    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction"""
        pass

class EnhancedMemoryAbstractionLayer:
    """Enhanced abstraction layer for unified memory and knowledge operations"""

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
                "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                "user": os.getenv("NEO4J_USER", "neo4j"),
                "password": os.getenv("NEO4J_PASSWORD", "password"),
                "group_id": os.getenv("GRAPHITI_GROUP_ID", "agent-zero-default")
            }
        
        return config
    
    # Delegate all memory operations to the backend
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
    ) -> List[MemoryDocument]:
        if not self.backend:
            await self.initialize()
        return await self.backend.search_similarity_threshold(query, limit, threshold, filter)
    
    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        if not self.backend:
            await self.initialize()
        return await self.backend.delete_documents_by_ids(ids)
    
    async def delete_documents_by_query(
        self, 
        query: str, 
        threshold: float = 0.75,
        filter: str = ""
    ) -> List[MemoryDocument]:
        if not self.backend:
            await self.initialize()
        return await self.backend.delete_documents_by_query(query, threshold, filter)
    
    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        if not self.backend:
            await self.initialize()
        return await self.backend.get_documents_by_ids(ids)

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
```

### Step 6: Implement Graphiti Backend

Create `python/helpers/memory_graphiti_backend.py`:

```python
import os
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from .memory_abstraction import MemoryBackend, MemoryDocument, MemoryConfig

class GraphitiBackend(MemoryBackend):
    """Graphiti temporal knowledge graph backend"""
    
    def __init__(self):
        self.client: Optional[Graphiti] = None
        self.user_node_uuid: Optional[str] = None
        self.agent_node_uuid: Optional[str] = None
    
    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize Graphiti client and create agent/user nodes"""
        graphiti_config = config.graphiti_config
        if not graphiti_config:
            raise ValueError("Graphiti configuration is required")
        
        # Initialize Graphiti client
        self.client = Graphiti(
            uri=graphiti_config["uri"],
            user=graphiti_config["user"],
            password=graphiti_config["password"]
        )
        
        # Build database schema
        await self.client.build_indices_and_constraints()
        
        # Create or retrieve agent and user nodes
        await self._ensure_agent_nodes(graphiti_config.get("group_id", "default"))
    
    async def _ensure_agent_nodes(self, group_id: str) -> None:
        """Create or retrieve agent and user nodes for this session"""
        # Create agent node
        agent_episode = await self.client.add_episode(
            name="Agent Zero Initialization",
            episode_body=f"Agent Zero instance for group {group_id} initialized",
            source=EpisodeType.message,  # CORRECTED: Use message as default
            reference_time=datetime.now(timezone.utc),
            source_description="agent-zero-system"
        )
        
        # Search for agent node
        from graphiti_core.search.search_config_recipes import NODE_HYBRID_SEARCH_EPISODE_MENTIONS
        agent_search = await self.client._search("Agent Zero", NODE_HYBRID_SEARCH_EPISODE_MENTIONS)
        if agent_search.nodes:
            self.agent_node_uuid = agent_search.nodes[0].uuid
        
        # Create user node
        user_episode = await self.client.add_episode(
            name="User Interaction",
            episode_body=f"User interacting with Agent Zero in group {group_id}",
            source=EpisodeType.message,  # CORRECTED: Use message as default
            reference_time=datetime.now(timezone.utc),
            source_description="agent-zero-user"
        )
        
        # Search for user node
        user_search = await self.client._search("User", NODE_HYBRID_SEARCH_EPISODE_MENTIONS)
        if user_search.nodes:
            self.user_node_uuid = user_search.nodes[0].uuid
    
    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Insert text as a Graphiti episode"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")
        
        # Map memory area to episode source description
        area = metadata.get("area", "main")
        source_description = f"agent-zero-{area}"
        
        # Determine episode type based on area
        episode_type = self._map_area_to_episode_type(area)
        
        # Create episode
        episode_uuid = await self.client.add_episode(
            name=f"Memory: {area.title()}",
            episode_body=text,
            source=episode_type,
            reference_time=datetime.now(timezone.utc),
            source_description=source_description,
            **{k: v for k, v in metadata.items() if k != "area"}
        )
        
        return str(episode_uuid)
    
    def _map_area_to_episode_type(self, area: str) -> EpisodeType:
        """Map memory areas to Graphiti episode types"""
        mapping = {
            "main": EpisodeType.message,      # CORRECTED: Use message as default
            "fragments": EpisodeType.message,
            "solutions": EpisodeType.message,
            "instruments": EpisodeType.message
        }
        return mapping.get(area, EpisodeType.message)  # CORRECTED: Default to message

    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Insert knowledge document with entity extraction"""
        if not self.client:
            raise RuntimeError("Graphiti client not initialized")

        # Map memory area to episode source description
        area = metadata.get("area", "main")
        source_description = f"agent-zero-knowledge-{area}"

        # Use document episode type for knowledge documents
        episode_uuid = await self.client.add_episode(
            name=f"Knowledge Document: {metadata.get('filename', 'Unknown')}",
            episode_body=content,
            source=EpisodeType.document,  # Use document type for knowledge
            reference_time=datetime.now(timezone.utc),
            source_description=source_description,
            **{k: v for k, v in metadata.items() if k not in ["area", "content_type"]}
        )

        return str(episode_uuid)

    # ... (continue with search, delete, and other methods)
```

### Step 7: Create FAISS Backend Wrapper

Create `python/helpers/memory_faiss_backend.py` for backward compatibility:

```python
from typing import List, Dict, Any
from .memory_abstraction import MemoryBackend, MemoryDocument, MemoryConfig
from .memory import Memory as LegacyMemory

class FaissBackend(MemoryBackend):
    """FAISS backend wrapper for the existing memory system"""
    
    def __init__(self):
        self.legacy_memory = None
    
    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize FAISS backend using existing Memory class"""
        # Create a mock agent object with the required config
        class MockAgent:
            def __init__(self, config):
                self.config = config
        
        mock_agent = MockAgent(config)
        self.legacy_memory = await LegacyMemory.get(mock_agent)
    
    # ... (implement all required methods using legacy memory system)
```

## Phase 3: Integration

### Step 8: Update Agent Configuration

Modify `agent.py` to add Graphiti configuration:

```python
@dataclass
class AgentConfig:
    chat_model: ModelConfig
    utility_model: ModelConfig
    embeddings_model: ModelConfig
    browser_model: ModelConfig
    mcp_servers: str
    prompts_subdir: str = ""
    memory_subdir: str = ""
    knowledge_subdirs: list[str] = field(default_factory=lambda: ["default", "custom"])

    # Add memory backend selection
    memory_backend: str = "faiss"  # "faiss" or "graphiti"

    # Use additional field for Graphiti configuration
    additional: Dict[str, Any] = field(default_factory=dict)

    # ... rest of existing configuration
```

### Step 9: Update Memory Helper

Modify `python/helpers/memory.py` to add abstraction layer access:

```python
# Add to the top of the file after existing imports
from .memory_abstraction import MemoryAbstractionLayer

# Add new method to Memory class
class Memory:
    # ... existing code ...
    
    @staticmethod
    async def get_abstraction_layer(agent):
        """Get the new memory abstraction layer"""
        if not hasattr(agent, '_memory_abstraction'):
            agent._memory_abstraction = MemoryAbstractionLayer(agent)
            await agent._memory_abstraction.initialize()
        return agent._memory_abstraction
```

### Step 10: Update Memory Tools

Update all memory tools to use the abstraction layer:

**`python/tools/memory_save.py`:**
```python
from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response

class MemorySave(Tool):
    async def execute(self, text="", area="", **kwargs):
        if not area:
            area = Memory.Area.MAIN.value

        metadata = {"area": area, **kwargs}

        # Use abstraction layer instead of direct Memory access
        memory_layer = await Memory.get_abstraction_layer(self.agent)
        id = await memory_layer.insert_text(text, metadata)

        result = self.agent.read_prompt("fw.memory_saved.md", memory_id=id)
        return Response(message=result, break_loop=False)
```

Apply similar changes to:
- `python/tools/memory_load.py`
- `python/tools/memory_delete.py`
- `python/tools/memory_forget.py`

### Step 11: Update Memory Extensions

Update all memory extensions to use the abstraction layer:

**`python/extensions/message_loop_prompts_after/_50_recall_memories.py`:**
```python
# Replace direct Memory.get() calls with:
memory_layer = await Memory.get_abstraction_layer(self.agent)
memories = await memory_layer.search_similarity_threshold(...)
```

Apply similar changes to all memory extensions.

### Step 12: Update Knowledge Import System

Update the knowledge import system to use the enhanced memory abstraction layer:

**`python/helpers/knowledge_import.py`:**
```python
# Add import for enhanced memory abstraction
from python.helpers.memory import Memory

# Update the load_knowledge function to route through abstraction layer
async def load_knowledge_enhanced(
    log_item: LogItem | None,
    knowledge_dir: str,
    index: Dict[str, KnowledgeImport],
    metadata: dict[str, Any] = {},
    filename_pattern: str = "**/*",
    agent=None  # Add agent parameter
) -> Dict[str, KnowledgeImport]:
    """Enhanced knowledge loading with Graphiti integration"""

    # Get enhanced memory abstraction layer
    if agent:
        memory_layer = await Memory.get_abstraction_layer(agent)

    # Process documents as before
    for file_path in glob.glob(os.path.join(knowledge_dir, filename_pattern), recursive=True):
        # ... existing file processing logic ...

        # Enhanced: Route through memory abstraction for knowledge documents
        if agent and memory_layer:
            # Process as knowledge documents with entity extraction
            documents_data = []
            for doc in file_data["documents"]:
                documents_data.append({
                    "content": doc.page_content,
                    "metadata": {**doc.metadata, **metadata, "filename": file_name}
                })

            # Use enhanced processing for knowledge documents
            doc_ids = await memory_layer.process_knowledge_documents(documents_data)
            file_data["document_ids"] = doc_ids

        index[file_path] = KnowledgeImport(**file_data)

    return index
```

**`python/helpers/memory.py`:**
```python
# Update preload_knowledge to use enhanced processing
async def preload_knowledge(self, log_item, kn_dirs, memory_subdir):
    """Enhanced knowledge preloading with Graphiti integration"""

    # Get enhanced memory abstraction layer
    memory_layer = await Memory.get_abstraction_layer(self.agent)

    for kn_dir in kn_dirs:
        knowledge_dir = os.path.join(self.agent.config.dirs.knowledge, kn_dir)

        # Use enhanced knowledge loading
        index = await knowledge_import.load_knowledge_enhanced(
            log_item, knowledge_dir, {},
            metadata={"area": memory_subdir},
            agent=self.agent
        )

        # Knowledge documents are now processed through enhanced abstraction
        # No need for separate insert_documents call
```

**`python/api/import_knowledge.py`:**
```python
# Update to use enhanced memory abstraction
@api.post("/import_knowledge")
async def import_knowledge(file: UploadFile):
    """Enhanced knowledge import with entity extraction"""

    # ... existing file processing logic ...

    # Get enhanced memory abstraction layer
    memory_layer = await Memory.get_abstraction_layer(context.agent0)

    # Process uploaded file as knowledge document
    doc_id = await memory_layer.insert_content(
        content=file_content,
        content_type="knowledge_document",
        metadata={
            "area": "main",
            "filename": file.filename,
            "upload_time": datetime.now().isoformat(),
            "source": "api_upload"
        }
    )

    # Reload memory to include new knowledge
    await memory.Memory.reload(context.agent0)

    return {"status": "success", "document_id": doc_id}
```

## Phase 4: Testing and Validation

### Step 13: Create Test Suite

Create comprehensive tests in `tests/` directory:

```bash
# Create test files
touch tests/test_memory_abstraction.py
touch tests/test_graphiti_backend.py
touch tests/test_memory_integration.py
touch tests/test_memory_tools.py
```

### Step 14: Run Tests

```bash
# Run unit tests
python -m pytest tests/test_memory_abstraction.py -v

# Run integration tests  
python -m pytest tests/test_memory_integration.py -v

# Run full test suite
python -m pytest tests/ -v

# Generate coverage report
python -m pytest tests/ --cov=python.helpers --cov-report=html
```

### Step 15: Manual Testing

```bash
# Start agent with Graphiti enabled
MEMORY_BACKEND=graphiti python initialize.py

# Test memory operations in agent chat:
# 1. Save a new memory
# 2. Search for memories
# 3. Test memory recall extensions
# 4. Verify temporal queries work
```

## Phase 5: Production Deployment

### Step 16: Production Configuration

Update production environment variables:
```bash
export MEMORY_BACKEND=graphiti
export GRAPHITI_ENABLED=true
export NEO4J_URI=bolt://your-production-neo4j:7687
export NEO4J_USER=your-neo4j-user
export NEO4J_PASSWORD=your-neo4j-password
export GRAPHITI_GROUP_ID=agent-zero-production
```

### Step 17: Deploy and Monitor

```bash
# Start agent with new backend
python initialize.py

# Monitor for errors
tail -f logs/agent.log

# Validate functionality
python scripts/validate_memory_system.py
```

## Completion Checklist

- [ ] Environment setup complete
- [ ] Neo4j database running
- [ ] Graphiti dependencies installed
- [ ] Enhanced memory & knowledge abstraction layer implemented
- [ ] Graphiti backend with knowledge processing implemented
- [ ] Memory tools updated
- [ ] Memory extensions updated
- [ ] Knowledge import system updated for enhanced processing
- [ ] Knowledge API updated for entity extraction
- [ ] Tests created and passing (including knowledge processing tests)
- [ ] Manual testing successful (memory + knowledge integration)
- [ ] Production deployment ready

## Next Steps

1. **Review** the architecture document for design details
2. **Implement** following this step-by-step guide
3. **Test** thoroughly using the testing guide
4. **Deploy** with confidence to production

The new temporal knowledge graph system will provide enhanced memory capabilities while maintaining full compatibility with existing agent functionality.
