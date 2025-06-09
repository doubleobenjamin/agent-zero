## Hybrid Memory Management Tools

Advanced memory system combining Graphiti (temporal knowledge graphs) and Cognee (intelligent processing).

### hybrid_memory_save
Save information with intelligent processing and entity extraction.

**Enhanced Features:**
- Multi-modal support (text, images, audio, video, code)
- Automatic entity and relationship extraction
- Knowledge graph construction
- Namespace isolation per agent

#### Parameters:
- **content**: Text, file path, or data to save
- **data_type**: "text", "conversation", "image", "audio", "video", "code", "document"
- **namespace**: "private", "shared", "team", or specific namespace
- **context**: Additional context for better understanding
- **tags**: Optional tags for organization

#### Usage Examples:

**Text with Entity Extraction:**
~~~json
{
    "thoughts": [
        "I need to save this important information",
        "The system will extract entities and relationships"
    ],
    "tool_name": "hybrid_memory_save",
    "tool_args": {
        "content": "John Smith from Acme Corp called about the Q3 project deadline being moved to December 15th",
        "data_type": "conversation",
        "namespace": "private",
        "context": "Client communication about project timeline"
    }
}
~~~

**Multi-modal Data:**
~~~json
{
    "thoughts": [
        "I need to save this image with analysis",
        "Cognee will process the visual content"
    ],
    "tool_name": "hybrid_memory_save",
    "tool_args": {
        "content": "/path/to/diagram.png",
        "data_type": "image",
        "namespace": "shared",
        "context": "System architecture diagram for project planning"
    }
}
~~~

### hybrid_memory_search
Advanced search with multiple search types and intelligence.

#### Parameters:
- **query**: Search query or question
- **search_type**: "hybrid", "semantic", "temporal", "insights", "graph", "contextual"
- **namespace**: "all", "private", "shared", "team", or specific namespace
- **time_range**: Optional time filter for temporal searches
- **limit**: Maximum results (default: 10)

#### Search Types:
- **hybrid**: Combines semantic, keyword, and graph search
- **semantic**: Vector similarity search
- **temporal**: Time-aware queries with date ranges
- **insights**: AI-generated insights and patterns
- **graph**: Knowledge graph traversal and completion
- **contextual**: Extended context with relationship awareness

#### Usage Examples:

**Semantic Search:**
~~~json
{
    "thoughts": [
        "I need to find information about project deadlines",
        "Semantic search will understand the context"
    ],
    "tool_name": "hybrid_memory_search",
    "tool_args": {
        "query": "project deadlines and timeline changes",
        "search_type": "semantic",
        "namespace": "all",
        "limit": 5
    }
}
~~~

**Temporal Query:**
~~~json
{
    "thoughts": [
        "I need to see what happened last week",
        "Temporal search will filter by time"
    ],
    "tool_name": "hybrid_memory_search",
    "tool_args": {
        "query": "client communications",
        "search_type": "temporal",
        "time_range": ["2024-01-01", "2024-01-07"],
        "namespace": "private"
    }
}
~~~

**Insights Generation:**
~~~json
{
    "thoughts": [
        "I need to understand patterns in our data",
        "Insights search will generate analysis"
    ],
    "tool_name": "hybrid_memory_search",
    "tool_args": {
        "query": "What patterns emerge in client feedback?",
        "search_type": "insights",
        "namespace": "shared"
    }
}
~~~

### hybrid_memory_analyze
Analyze relationships and extract insights from memory.

#### Parameters:
- **focus**: What to analyze ("entities", "relationships", "patterns", "trends")
- **query**: Specific analysis question
- **namespace**: Target namespace for analysis
- **depth**: Analysis depth ("surface", "deep", "comprehensive")

#### Usage Example:
~~~json
{
    "thoughts": [
        "I need to understand the relationships between entities",
        "This will help me see the bigger picture"
    ],
    "tool_name": "hybrid_memory_analyze",
    "tool_args": {
        "focus": "relationships",
        "query": "How are our clients connected to different projects?",
        "namespace": "shared",
        "depth": "deep"
    }
}
~~~
