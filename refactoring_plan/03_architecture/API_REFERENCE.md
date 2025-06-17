# Enhanced Memory & Knowledge Abstraction Layer API Reference

## Overview

The Enhanced Memory & Knowledge Abstraction Layer provides a unified interface for both memory and knowledge operations across different backend implementations (FAISS and Graphiti). This API maintains backward compatibility while enabling advanced temporal knowledge graph capabilities with content-type specific processing for maximum intelligence.

## Core Classes

### MemoryDocument

Unified representation of memory documents across all backends.

```python
@dataclass
class MemoryDocument:
    """Unified memory document representation"""
    id: str                    # Unique document identifier
    page_content: str         # Document text content (CORRECTED: matches LangChain Document)
    metadata: Dict[str, Any]  # Document metadata
    score: Optional[float]    # Similarity score (for search results)
```

**Example:**
```python
doc = MemoryDocument(
    id="uuid-123",
    page_content="User prefers Python for scripting tasks",
    metadata={
        "area": "main",
        "timestamp": "2024-01-01T10:00:00Z",
        "source_description": "agent-zero-main"
    },
    score=0.85
)
```

### MemoryConfig

Configuration object for memory backend initialization.

```python
@dataclass  
class MemoryConfig:
    """Memory backend configuration"""
    backend_type: str                           # "faiss" or "graphiti"
    memory_subdir: str                         # Memory storage subdirectory
    embeddings_model: Any                      # Embeddings model configuration
    graphiti_config: Optional[Dict[str, str]]  # Graphiti-specific configuration
```

**Example:**
```python
config = MemoryConfig(
    backend_type="graphiti",
    memory_subdir="production",
    embeddings_model=embeddings_model,
    graphiti_config={
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "password",
        "group_id": "agent-zero-production"
    }
)
```

## Main Interface

### EnhancedMemoryAbstractionLayer

Primary interface for all memory and knowledge operations with content-type specific processing.

#### Initialization

```python
class MemoryAbstractionLayer:
    def __init__(self, agent):
        """Initialize memory abstraction layer for given agent"""
        
    async def initialize(self) -> None:
        """Initialize the appropriate backend based on configuration"""
```

**Usage:**
```python
memory_layer = MemoryAbstractionLayer(agent)
await memory_layer.initialize()
```

#### Core Operations

##### insert_text()

Insert text content into memory.

```python
async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
    """
    Insert text and return document ID
    
    Args:
        text: Text content to store
        metadata: Document metadata (area, timestamp, etc.)
        
    Returns:
        str: Unique document identifier
        
    Raises:
        RuntimeError: If backend not initialized
        ValueError: If required metadata missing
    """
```

**Example:**
```python
doc_id = await memory_layer.insert_text(
    "User's favorite programming language is Python",
    {
        "area": "main",
        "category": "preference",
        "confidence": 0.9
    }
)
```

##### insert_content()

Enhanced content insertion with content-type detection for optimal processing.

```python
async def insert_content(
    self,
    content: str,
    content_type: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Insert content with type-specific processing

    Args:
        content: Text content to store
        content_type: "agent_memory" or "knowledge_document"
        metadata: Document metadata (area, timestamp, etc.)

    Returns:
        str: Unique document identifier

    Raises:
        RuntimeError: If backend not initialized
        ValueError: If invalid content_type or missing metadata
    """
```

**Example:**
```python
# Agent conversation memory (simple episode storage)
memory_id = await memory_layer.insert_content(
    "User asked about Python best practices",
    "agent_memory",
    {"area": "main", "source": "conversation"}
)

# Knowledge document (with entity extraction)
doc_id = await memory_layer.insert_content(
    "Python is a high-level programming language created by Guido van Rossum",
    "knowledge_document",
    {"area": "main", "source": "documentation", "filename": "python_intro.md"}
)
```

##### process_knowledge_documents()

Batch process knowledge documents with enhanced entity extraction.

```python
async def process_knowledge_documents(
    self,
    documents: List[Dict[str, Any]]
) -> List[str]:
    """
    Process multiple knowledge documents with entity extraction

    Args:
        documents: List of document dicts with 'content' and 'metadata' keys

    Returns:
        List[str]: Document IDs of processed documents

    Raises:
        RuntimeError: If backend not initialized
        ValueError: If invalid document format
    """
```

**Example:**
```python
documents = [
    {
        "content": "Machine learning is a subset of artificial intelligence",
        "metadata": {"area": "main", "source": "textbook", "chapter": "1"}
    },
    {
        "content": "Neural networks are inspired by biological neural networks",
        "metadata": {"area": "main", "source": "textbook", "chapter": "2"}
    }
]

doc_ids = await memory_layer.process_knowledge_documents(documents)
print(f"Processed {len(doc_ids)} knowledge documents")
```

##### search_similarity_threshold()

Search for similar documents across both memory and knowledge with threshold filtering.

```python
async def search_similarity_threshold(
    self,
    query: str,
    limit: int = 10,
    threshold: float = 0.7,
    filter: str = ""
) -> List[MemoryDocument]:
    """
    Unified search across agent memory and knowledge documents

    Args:
        query: Search query text
        limit: Maximum number of results
        threshold: Minimum similarity score (0.0-1.0)
        filter: Filter expression for metadata (supports content_type filtering)

    Returns:
        List[MemoryDocument]: Matching documents sorted by relevance (memory + knowledge)

    Raises:
        RuntimeError: If backend not initialized
        ValueError: If invalid parameters
    """
```

**Example:**
```python
# Unified search across memory and knowledge
results = await memory_layer.search_similarity_threshold(
    query="programming languages",
    limit=5,
    threshold=0.6,
    filter="area=='main'"
)

for doc in results:
    content_type = doc.metadata.get('content_type', 'unknown')
    print(f"Score: {doc.score}, Type: {content_type}, Content: {doc.page_content}")

# Search only knowledge documents
knowledge_results = await memory_layer.search_similarity_threshold(
    query="machine learning concepts",
    limit=3,
    threshold=0.7,
    filter="content_type=='knowledge_document'"
)

# Search only agent memory
memory_results = await memory_layer.search_similarity_threshold(
    query="user preferences",
    limit=3,
    threshold=0.7,
    filter="content_type=='agent_memory'"
)
```

##### delete_documents_by_ids()

Delete documents by their IDs.

```python
async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
    """
    Delete documents by IDs
    
    Args:
        ids: List of document IDs to delete
        
    Returns:
        List[MemoryDocument]: Deleted documents
        
    Raises:
        RuntimeError: If backend not initialized
    """
```

**Example:**
```python
deleted = await memory_layer.delete_documents_by_ids(["uuid-123", "uuid-456"])
print(f"Deleted {len(deleted)} documents")
```

##### delete_documents_by_query()

Delete documents matching a search query.

```python
async def delete_documents_by_query(
    self, 
    query: str, 
    threshold: float = 0.75,
    filter: str = ""
) -> List[MemoryDocument]:
    """
    Delete documents by query
    
    Args:
        query: Search query to find documents to delete
        threshold: Minimum similarity score for deletion
        filter: Filter expression for metadata
        
    Returns:
        List[MemoryDocument]: Deleted documents
        
    Raises:
        RuntimeError: If backend not initialized
    """
```

**Example:**
```python
deleted = await memory_layer.delete_documents_by_query(
    query="outdated information",
    threshold=0.8,
    filter="timestamp<'2023-01-01'"
)
```

##### get_documents_by_ids()

Retrieve documents by their IDs.

```python
async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
    """
    Retrieve documents by IDs
    
    Args:
        ids: List of document IDs to retrieve
        
    Returns:
        List[MemoryDocument]: Retrieved documents
        
    Raises:
        RuntimeError: If backend not initialized
    """
```

**Example:**
```python
docs = await memory_layer.get_documents_by_ids(["uuid-123", "uuid-456"])
for doc in docs:
    print(f"ID: {doc.id}, Content: {doc.page_content}")
```

## Backend Interfaces

### MemoryBackend (Abstract Base Class)

Abstract interface that all backend implementations must follow.

```python
class MemoryBackend(ABC):
    """Abstract base class for memory backends"""
    
    @abstractmethod
    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize the memory backend"""
        
    @abstractmethod
    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        """Insert text and return document ID"""
        
    @abstractmethod
    async def search_similarity_threshold(
        self, query: str, limit: int = 10, threshold: float = 0.7, filter: str = ""
    ) -> List[MemoryDocument]:
        """Search for similar documents"""
        
    @abstractmethod
    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Delete documents by IDs"""
        
    @abstractmethod
    async def delete_documents_by_query(
        self, query: str, threshold: float = 0.75, filter: str = ""
    ) -> List[MemoryDocument]:
        """Delete documents by query"""
        
    @abstractmethod
    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        """Retrieve documents by IDs"""
```

## Configuration

### Backend Selection

The abstraction layer automatically selects the appropriate backend based on configuration:

```python
def _get_backend_type(self) -> str:
    """Determine which backend to use based on configuration"""
    import os
    
    # Check environment variable first
    env_backend = os.getenv("MEMORY_BACKEND", "faiss")
    
    # Check agent config for memory backend preference
    # Note: This would need to be added to AgentConfig in agent.py
    memory_backend = getattr(self.agent.config, 'memory_backend', None)

    if memory_backend == "graphiti" or env_backend == "graphiti":
        return "graphiti"
    return "faiss"
```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MEMORY_BACKEND` | Backend type ("faiss" or "graphiti") | "faiss" | No |
| `NEO4J_URI` | Neo4j connection URI | "bolt://localhost:7687" | For Graphiti |
| `NEO4J_USER` | Neo4j username | "neo4j" | For Graphiti |
| `NEO4J_PASSWORD` | Neo4j password | "password" | For Graphiti |
| `GRAPHITI_GROUP_ID` | Namespace for multi-tenant scenarios | "default" | No |
| `OPENAI_API_KEY` | OpenAI API key for Graphiti LLM/embeddings | None | For Graphiti |

## Error Handling

### Common Exceptions

```python
# Backend not initialized
RuntimeError("Backend not initialized")

# Invalid configuration
ValueError("Graphiti configuration is required")

# Connection failures
ConnectionError("Failed to connect to Neo4j")

# Invalid parameters
ValueError("Invalid threshold value: must be between 0.0 and 1.0")
```

### Error Handling Best Practices

```python
try:
    results = await memory_layer.search_similarity_threshold("query")
except RuntimeError as e:
    # Handle backend initialization errors
    logger.error(f"Memory backend error: {e}")
    await memory_layer.initialize()
    results = await memory_layer.search_similarity_threshold("query")
except ValueError as e:
    # Handle parameter validation errors
    logger.error(f"Invalid parameters: {e}")
    results = []
```

## Backend Integration

### Memory Backend Access

The abstraction layer provides unified access to different backends:

```python
from python.helpers.memory import Memory
from python.helpers.memory_abstraction import MemoryAbstractionLayer

# Recommended method - uses abstraction layer
memory_layer = MemoryAbstractionLayer(agent)
await memory_layer.initialize()

# Legacy method - direct FAISS access (for compatibility)
legacy_memory = await Memory.get(agent)
```

### Backend-Specific Features

```python
# Check which backend is active
backend_type = memory_layer.config.backend_type
print(f"Using backend: {backend_type}")

# Access backend-specific features (if needed)
if backend_type == "graphiti":
    graphiti_client = memory_layer.backend.client
    # Use Graphiti-specific features like temporal queries
elif backend_type == "faiss":
    faiss_db = memory_layer.backend.legacy_memory.db
    # Use FAISS-specific features
```

## Performance Considerations

### Batch Operations

For better performance with large datasets:

```python
# Instead of multiple single inserts
for text in texts:
    await memory_layer.insert_text(text, metadata)

# Consider batching (if backend supports it)
# This would be a future enhancement
```

### Caching

The abstraction layer includes automatic caching for frequently accessed data:

```python
# Automatic caching is handled internally
# No explicit cache management required
```

### Connection Pooling

For Graphiti backend, connection pooling is handled automatically by the Neo4j driver.

## Examples

### Complete Usage Example

```python
import asyncio
from python.helpers.memory_abstraction import MemoryAbstractionLayer

async def example_usage(agent):
    # Initialize memory layer
    memory = MemoryAbstractionLayer(agent)
    await memory.initialize()
    
    # Save some memories
    doc_id1 = await memory.insert_text(
        "User prefers Python for data analysis",
        {"area": "main", "category": "preference"}
    )
    
    doc_id2 = await memory.insert_text(
        "User completed machine learning project",
        {"area": "solutions", "category": "achievement"}
    )
    
    # Search for memories
    results = await memory.search_similarity_threshold(
        "Python programming",
        limit=5,
        threshold=0.6
    )
    
    print(f"Found {len(results)} relevant memories:")
    for doc in results:
        print(f"- {doc.page_content} (score: {doc.score})")
    
    # Clean up old memories
    deleted = await memory.delete_documents_by_query(
        "outdated",
        threshold=0.8,
        filter="timestamp<'2023-01-01'"
    )
    
    print(f"Deleted {len(deleted)} outdated memories")

# Run example
# asyncio.run(example_usage(agent))
```
