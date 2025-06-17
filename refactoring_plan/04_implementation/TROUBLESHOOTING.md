# Troubleshooting Guide: Graphiti Memory System

## Overview

This guide provides solutions for common issues encountered during the implementation and operation of the Graphiti temporal knowledge graph memory system. Since we're working with a fresh repository, this focuses on implementation and runtime issues rather than migration problems.

## Environment Setup Issues

### 1. Neo4j Connection Problems

#### Problem: Cannot connect to Neo4j database
```
ConnectionError: Failed to connect to bolt://localhost:7687
```

**Solutions:**
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Start Neo4j if not running
docker run -d \
  --name neo4j-agent-zero \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.22.0

# Test connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('✅ Neo4j connection successful')
driver.close()
"

# Check Neo4j logs if still failing
docker logs neo4j-agent-zero
```

#### Problem: Neo4j authentication failed
```
AuthError: The client is unauthorized due to authentication failure
```

**Solutions:**
```bash
# Reset Neo4j password
docker exec neo4j-agent-zero cypher-shell -u neo4j -p neo4j
# Then run: ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'password';

# Or recreate container with correct auth
docker rm -f neo4j-agent-zero
docker run -d \
  --name neo4j-agent-zero \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.22.0
```

### 2. Dependency Installation Issues

#### Problem: Graphiti installation fails
```
ERROR: Could not find a version that satisfies the requirement graphiti-core
```

**Solutions:**
```bash
# Update pip first
pip install --upgrade pip

# Install with specific Python version
python3.10 -m pip install "graphiti-core[anthropic,groq,google-genai]"

# If still failing, try without extras first
pip install graphiti-core
pip install anthropic openai google-generativeai

# Verify installation
python -c "import graphiti_core; print('✅ Graphiti installed')"
```

#### Problem: OpenAI API key issues
```
ValueError: OpenAI API key is required for Graphiti
```

**Solutions:**
```bash
# Set OpenAI API key
export OPENAI_API_KEY=your_openai_api_key

# Add to .env file
echo "OPENAI_API_KEY=your_openai_api_key" >> .env

# Verify API key works
python -c "
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
models = client.models.list()
print('✅ OpenAI API key valid')
"
```

## Implementation Issues

### 3. Backend Selection Problems

#### Problem: Wrong backend being selected
```
Expected Graphiti backend but got FAISS
```

**Solutions:**
```bash
# Check environment variables
echo "MEMORY_BACKEND: $MEMORY_BACKEND"
echo "GRAPHITI_ENABLED: $GRAPHITI_ENABLED"

# Set correct backend
export MEMORY_BACKEND=graphiti
export GRAPHITI_ENABLED=true

# Verify in Python
python -c "
import os
print(f'Backend: {os.getenv(\"MEMORY_BACKEND\", \"faiss\")}')
print(f'Enabled: {os.getenv(\"GRAPHITI_ENABLED\", \"false\")}')
"

# Check agent configuration
python -c "
from agent import AgentConfig
# Verify graphiti_enabled is True in config
"
```

#### Problem: Configuration not loading
```
AttributeError: 'AgentConfig' object has no attribute 'graphiti_enabled'
```

**Solutions:**
```python
# Update agent.py to include Graphiti configuration
@dataclass
class AgentConfig:
    # ... existing fields ...
    
    # Add these fields
    graphiti_enabled: bool = False
    graphiti_neo4j_uri: str = "bolt://localhost:7687"
    graphiti_neo4j_user: str = "neo4j"
    graphiti_neo4j_password: str = "password"
    graphiti_group_id: str = "default"
```

### 4. Abstraction Layer Issues

#### Problem: Memory backend not initialized
```
RuntimeError: Memory backend not initialized
```

**Solutions:**
```python
# Check abstraction layer initialization
from python.helpers.memory import Memory

# Ensure proper initialization
memory_layer = await Memory.get_abstraction_layer(agent)
if not memory_layer.backend:
    await memory_layer.initialize()

# Debug initialization
print(f"Backend type: {memory_layer.config.backend_type if memory_layer.config else 'None'}")
print(f"Backend instance: {type(memory_layer.backend) if memory_layer.backend else 'None'}")
```

#### Problem: Import errors for abstraction layer
```
ModuleNotFoundError: No module named 'python.helpers.memory_abstraction'
```

**Solutions:**
```bash
# Ensure file exists
ls python/helpers/memory_abstraction.py

# Check Python path
python -c "import sys; print(sys.path)"

# Add project root to Python path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Verify import works
python -c "from python.helpers.memory_abstraction import MemoryAbstractionLayer; print('✅ Import successful')"
```

## Runtime Issues

### 5. Graphiti Backend Problems

#### Problem: Episode creation fails
```
GraphitiError: Failed to create episode
```

**Solutions:**
```python
# Check Graphiti client initialization
from python.helpers.memory_graphiti_backend import GraphitiBackend
from python.helpers.memory_abstraction import MemoryConfig

config = MemoryConfig(
    backend_type="graphiti",
    memory_subdir="test",
    embeddings_model=None,
    graphiti_config={
        "neo4j_uri": "bolt://localhost:7687",
        "neo4j_user": "neo4j",
        "neo4j_password": "password",
        "group_id": "test"
    }
)

backend = GraphitiBackend()
await backend.initialize(config)

# Test episode creation
episode_uuid = await backend.client.add_episode(
    name="Test Episode",
    episode_body="Test content",
    source=EpisodeType.text,
    reference_time=datetime.now(timezone.utc),
    source_description="test"
)
print(f"Created episode: {episode_uuid}")
```

#### Problem: Search returns no results
```
Search completed but returned 0 results
```

**Solutions:**
```python
# Check if data exists in Neo4j
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
with driver.session() as session:
    result = session.run("MATCH (n) RETURN count(n) as count")
    count = result.single()["count"]
    print(f"Total nodes in database: {count}")

# Check search parameters
results = await backend.search_similarity_threshold(
    query="test",
    limit=10,
    threshold=0.0  # Lower threshold to find more results
)
print(f"Found {len(results)} results with threshold 0.0")

# Verify center node exists
if backend.user_node_uuid:
    print(f"User node UUID: {backend.user_node_uuid}")
else:
    print("Warning: No user node found")
```

### 6. Memory Tool Issues

#### Problem: Memory tools return errors
```
AttributeError: 'MemoryDocument' object has no attribute 'page_content'
```

**Solutions:**
```python
# Update memory tools to use new document format
# In memory_load.py, change:
# text = "\n\n".join(Memory.format_docs_plain(docs))
# To:
text = "\n\n".join([doc.content for doc in docs])

# In extensions, update document access:
# Old: doc.page_content
# New: doc.content

# Old: doc.metadata["id"]
# New: doc.id
```

#### Problem: Extensions not working
```
TypeError: RecallMemories.search_memories() missing required arguments
```

**Solutions:**
```python
# Update extensions to use abstraction layer
# In RecallMemories extension:

async def search_memories(self, loop_data: LoopData = LoopData(), **kwargs):
    try:
        # Replace direct Memory.get() with abstraction layer
        memory_layer = await Memory.get_abstraction_layer(self.agent)
        
        # Use new search method
        memories = await memory_layer.search_similarity_threshold(
            query=query,
            limit=RecallMemories.RESULTS,
            threshold=RecallMemories.THRESHOLD,
            filter=f"area == 'main' or area == 'fragments'"
        )
        
        # Convert to text format
        if memories:
            memories_text = "\n\n".join([doc.content for doc in memories])
            # ... rest of processing
            
    except Exception as e:
        self.agent.context.log.log(type="error", content=f"Memory recall failed: {str(e)}")
```

## Performance Issues

### 7. Slow Memory Operations

#### Problem: Memory operations are very slow
```
Memory search took 10+ seconds to complete
```

**Solutions:**
```bash
# Check Neo4j performance
docker exec neo4j-agent-zero cypher-shell -u neo4j -p password \
  "CALL dbms.listQueries()"

# Check database indices
docker exec neo4j-agent-zero cypher-shell -u neo4j -p password \
  "SHOW INDEXES"

# Create missing indices if needed
docker exec neo4j-agent-zero cypher-shell -u neo4j -p password \
  "CREATE INDEX IF NOT EXISTS FOR (n:Episode) ON (n.name)"

# Increase Neo4j memory allocation
docker rm -f neo4j-agent-zero
docker run -d \
  --name neo4j-agent-zero \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  -e NEO4J_dbms_memory_heap_initial__size=2G \
  -e NEO4J_dbms_memory_heap_max__size=4G \
  -e NEO4J_dbms_memory_pagecache_size=2G \
  neo4j:5.22.0
```

#### Problem: High memory usage
```
Agent process using excessive RAM
```

**Solutions:**
```bash
# Monitor memory usage
htop
docker stats neo4j-agent-zero

# Reduce search result limits
results = await memory_layer.search_similarity_threshold(
    query="test",
    limit=5,      # Reduce from default 10
    threshold=0.8 # Increase threshold for fewer results
)

# Clear Python caches periodically
import gc
gc.collect()

# Restart Neo4j if memory usage is high
docker restart neo4j-agent-zero
```

## Development Issues

### 8. Testing Problems

#### Problem: Tests fail with connection errors
```
ConnectionError: Failed to connect to test database
```

**Solutions:**
```bash
# Start separate test database
docker run -d \
  --name neo4j-test \
  -p 7688:7687 \
  -e NEO4J_AUTH=neo4j/testpassword \
  neo4j:5.22.0

# Use test database in tests
export NEO4J_URI=bolt://localhost:7688
export NEO4J_PASSWORD=testpassword

# Clean test database between tests
docker exec neo4j-test cypher-shell -u neo4j -p testpassword \
  "MATCH (n) DETACH DELETE n"
```

#### Problem: Mock objects not working
```
AttributeError: Mock object has no attribute 'async_method'
```

**Solutions:**
```python
# Use AsyncMock for async methods
from unittest.mock import AsyncMock, Mock

mock_client = Mock()
mock_client.add_episode = AsyncMock(return_value="test-uuid")
mock_client.search = AsyncMock(return_value=[])
mock_client.build_indices_and_constraints = AsyncMock()

# For async context managers
mock_client.__aenter__ = AsyncMock(return_value=mock_client)
mock_client.__aexit__ = AsyncMock(return_value=None)
```

## Debugging Tools

### 9. Diagnostic Scripts

#### Memory System Health Check

Create `scripts/health_check.py`:
```python
#!/usr/bin/env python3
import asyncio
import os
from python.helpers.memory_abstraction import MemoryAbstractionLayer

async def health_check():
    print("🔍 Memory System Health Check")
    print("-" * 40)
    
    # Check environment
    print(f"Backend: {os.getenv('MEMORY_BACKEND', 'faiss')}")
    print(f"Neo4j URI: {os.getenv('NEO4J_URI', 'not set')}")
    print(f"OpenAI Key: {'set' if os.getenv('OPENAI_API_KEY') else 'not set'}")
    
    try:
        # Test Neo4j connection
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(
            os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            auth=(os.getenv('NEO4J_USER', 'neo4j'), os.getenv('NEO4J_PASSWORD', 'password'))
        )
        with driver.session() as session:
            session.run("RETURN 1")
        print("✅ Neo4j connection: OK")
        driver.close()
        
        # Test Graphiti import
        import graphiti_core
        print("✅ Graphiti import: OK")
        
        # Test OpenAI connection
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        models = client.models.list()
        print("✅ OpenAI connection: OK")
        
        print("\n🎉 All health checks passed!")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(health_check())
```

#### Configuration Validator

Create `scripts/validate_config.py`:
```python
#!/usr/bin/env python3
import os

def validate_config():
    print("🔧 Configuration Validation")
    print("-" * 30)
    
    # Required environment variables
    required_vars = {
        "MEMORY_BACKEND": "graphiti",
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
        "OPENAI_API_KEY": "your_api_key"
    }
    
    all_good = True
    for var, expected in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == "OPENAI_API_KEY":
                print(f"✅ {var}: {'*' * 20}")  # Hide API key
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET (expected: {expected})")
            all_good = False
    
    # Check file permissions
    paths = ["python/helpers/", "logs/"]
    for path in paths:
        if os.path.exists(path):
            readable = os.access(path, os.R_OK)
            writable = os.access(path, os.W_OK)
            status = "✅" if readable and writable else "❌"
            print(f"{status} {path}: {'R/W' if readable and writable else 'Limited access'}")
    
    if all_good:
        print("\n🎉 Configuration is valid!")
    else:
        print("\n❌ Configuration issues found. Please fix and retry.")
    
    return all_good

if __name__ == "__main__":
    validate_config()
```

### 10. Logging and Monitoring

#### Enable Debug Logging

```python
# Add to your code for detailed logging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In memory operations
logger.debug(f"Searching for: {query}")
logger.debug(f"Found {len(results)} results")
logger.debug(f"Backend type: {self.config.backend_type}")
```

#### Monitor Neo4j Performance

```bash
# Check query performance
docker exec neo4j-agent-zero cypher-shell -u neo4j -p password \
  "CALL dbms.listQueries()"

# Check memory usage
docker exec neo4j-agent-zero cypher-shell -u neo4j -p password \
  "CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Memory Pools')"

# Monitor in real-time
watch -n 5 'docker stats neo4j-agent-zero --no-stream'
```

## Getting Help

### 11. Support Resources

#### Log Analysis

```bash
# Check agent logs
tail -f logs/agent.log | grep -i memory

# Check Neo4j logs
docker logs neo4j-agent-zero | tail -50

# Check Python errors
python -c "
import traceback
try:
    # Your problematic code here
    pass
except Exception as e:
    traceback.print_exc()
"
```

#### Community Support

- **GitHub Issues**: Report bugs and get help
- **Graphiti Documentation**: https://github.com/getzep/graphiti
- **Neo4j Community**: https://community.neo4j.com/
- **Agent-Zero Discussions**: Check repository discussions

#### Professional Support

For production deployments:
- Neo4j professional support
- Custom development services
- Performance optimization consulting

### 12. Prevention Best Practices

#### Development Practices

```bash
# Always test in development first
export ENVIRONMENT=development
export MEMORY_BACKEND=graphiti

# Use version control for configuration
git add .env.example
git commit -m "Add example environment configuration"

# Regular health checks
crontab -e
# Add: 0 9 * * * /path/to/scripts/health_check.py
```

#### Monitoring Setup

```bash
# Set up monitoring alerts
# Monitor Neo4j memory usage
# Monitor query performance
# Monitor error rates

# Regular maintenance
# Weekly: Check logs for errors
# Monthly: Review performance metrics
# Quarterly: Update dependencies
```

This troubleshooting guide covers the most common issues you'll encounter when implementing and running the Graphiti memory system. Keep this handy during development and deployment!
