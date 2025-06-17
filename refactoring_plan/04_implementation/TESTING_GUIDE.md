# Testing Guide: Graphiti Memory System

## Overview

This guide provides comprehensive testing strategies for the Graphiti memory system implementation. Since we're working with a fresh repository, we focus on validating the new system functionality rather than migration testing.

## Test Categories

### 1. Unit Tests
- Memory abstraction layer components
- Graphiti backend implementation
- Data transformation functions
- Configuration management

### 2. Integration Tests
- End-to-end memory operations
- Tool and extension functionality
- Cross-component interactions
- Error handling scenarios

### 3. Performance Tests
- Query latency benchmarks
- Memory usage analysis
- Concurrent access patterns
- Large dataset handling

### 4. Manual Tests
- Agent functionality validation
- User experience testing
- Edge case scenarios
- Production readiness

## Test Setup

### Prerequisites

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov

# Ensure Neo4j is running for integration tests
docker ps | grep neo4j

# Set test environment variables
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password
export OPENAI_API_KEY=your_test_api_key
export MEMORY_BACKEND=graphiti
```

### Test Data Setup

Create `tests/fixtures/test_data.py`:

```python
import pytest
from datetime import datetime, timezone

@pytest.fixture
def sample_memories():
    """Sample memory data for testing"""
    return [
        {
            "page_content": "User prefers Python for data analysis",
            "metadata": {"area": "main", "category": "preference"}
        },
        {
            "page_content": "Successfully implemented machine learning model",
            "metadata": {"area": "solutions", "category": "achievement"}
        },
        {
            "page_content": "User asked about file compression libraries",
            "metadata": {"area": "fragments", "category": "question"}
        },
        {
            "page_content": "Custom data processing script created",
            "metadata": {"area": "instruments", "category": "tool"}
        }
    ]

@pytest.fixture
def mock_agent():
    """Mock agent for testing"""
    from unittest.mock import Mock
    
    agent = Mock()
    agent.config = Mock()
    agent.config.memory_subdir = "test"
    agent.config.embeddings_model = Mock()
    agent.config.memory_backend = "graphiti"
    agent.config.additional = {
        "graphiti_config": {
            "uri": "bolt://localhost:7687",
            "user": "neo4j",
            "password": "password",
            "group_id": "test-group"
        }
    }
    
    return agent
```

## Unit Tests

### Test Memory Abstraction Layer

Create `tests/test_memory_abstraction.py`:

```python
import pytest
import asyncio
import os
from unittest.mock import Mock, patch
from python.helpers.memory_abstraction import MemoryAbstractionLayer, MemoryDocument

class TestMemoryAbstractionLayer:
    
    @pytest.mark.asyncio
    async def test_backend_selection_graphiti(self, mock_agent):
        """Test Graphiti backend selection"""
        with patch.dict(os.environ, {"MEMORY_BACKEND": "graphiti"}):
            layer = MemoryAbstractionLayer(mock_agent)
            backend_type = layer._get_backend_type()
            assert backend_type == "graphiti"
    
    @pytest.mark.asyncio
    async def test_backend_selection_faiss(self, mock_agent):
        """Test FAISS backend selection"""
        mock_agent.config.memory_backend = "faiss"
        with patch.dict(os.environ, {"MEMORY_BACKEND": "faiss"}):
            layer = MemoryAbstractionLayer(mock_agent)
            backend_type = layer._get_backend_type()
            assert backend_type == "faiss"
    
    @pytest.mark.asyncio
    async def test_config_building(self, mock_agent):
        """Test configuration building"""
        layer = MemoryAbstractionLayer(mock_agent)
        config = layer._build_config("graphiti")
        
        assert config.backend_type == "graphiti"
        assert config.memory_subdir == "test"
        assert config.graphiti_config is not None
        assert "uri" in config.graphiti_config
    
    @pytest.mark.asyncio
    async def test_initialization(self, mock_agent):
        """Test abstraction layer initialization"""
        with patch('python.helpers.memory_abstraction.GraphitiBackend') as mock_backend:
            layer = MemoryAbstractionLayer(mock_agent)
            await layer.initialize()
            
            assert layer.backend is not None
            assert layer.config is not None
            mock_backend.assert_called_once()
```

### Test Graphiti Backend

Create `tests/test_graphiti_backend.py`:

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from python.helpers.memory_graphiti_backend import GraphitiBackend
from python.helpers.memory_abstraction import MemoryConfig

class TestGraphitiBackend:
    
    @pytest.fixture
    async def graphiti_config(self):
        return MemoryConfig(
            backend_type="graphiti",
            memory_subdir="test",
            embeddings_model=None,
            graphiti_config={
                "uri": "bolt://localhost:7687",
                "user": "neo4j",
                "password": "password",
                "group_id": "test-group"
            }
        )
    
    @pytest.mark.asyncio
    async def test_initialization(self, graphiti_config):
        """Test Graphiti backend initialization"""
        backend = GraphitiBackend()
        
        with patch('python.helpers.memory_graphiti_backend.Graphiti') as mock_graphiti:
            mock_client = Mock()
            mock_graphiti.return_value = mock_client
            mock_client.build_indices_and_constraints = AsyncMock()
            mock_client.add_episode = AsyncMock(return_value="test-uuid")
            mock_client._search = AsyncMock(return_value=Mock(nodes=[Mock(uuid="node-uuid")]))
            
            await backend.initialize(graphiti_config)
            
            assert backend.client is not None
            mock_client.build_indices_and_constraints.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_insert_text(self, graphiti_config):
        """Test text insertion"""
        backend = GraphitiBackend()
        
        with patch('python.helpers.memory_graphiti_backend.Graphiti') as mock_graphiti:
            mock_client = Mock()
            mock_graphiti.return_value = mock_client
            mock_client.build_indices_and_constraints = AsyncMock()
            mock_client.add_episode = AsyncMock(return_value="episode-uuid-123")
            mock_client._search = AsyncMock(return_value=Mock(nodes=[Mock(uuid="node-uuid")]))
            
            await backend.initialize(graphiti_config)
            
            result = await backend.insert_text(
                "Test memory content",
                {"area": "main", "test": True}
            )
            
            assert result == "episode-uuid-123"
            mock_client.add_episode.assert_called()
    
    @pytest.mark.asyncio
    async def test_search_functionality(self, graphiti_config):
        """Test search functionality"""
        backend = GraphitiBackend()
        
        with patch('python.helpers.memory_graphiti_backend.Graphiti') as mock_graphiti:
            mock_client = Mock()
            mock_graphiti.return_value = mock_client
            mock_client.build_indices_and_constraints = AsyncMock()
            mock_client.add_episode = AsyncMock(return_value="episode-uuid")
            mock_client._search = AsyncMock(return_value=Mock(nodes=[Mock(uuid="node-uuid")]))
            
            # Mock search results
            mock_edge = Mock()
            mock_edge.fact = "Test memory content"
            mock_edge.uuid = "test-uuid-123"
            mock_edge.source_description = "agent-zero-main"
            mock_edge.score = 0.9
            mock_edge.created_at = None
            
            mock_client.search = AsyncMock(return_value=[mock_edge])
            
            await backend.initialize(graphiti_config)
            
            results = await backend.search_similarity_threshold(
                "test query", limit=5, threshold=0.7
            )
            
            assert len(results) == 1
            assert results[0].page_content == "Test memory content"
            assert results[0].id == "test-uuid-123"
            assert results[0].score == 0.9
    
    def test_area_mapping(self):
        """Test memory area to episode type mapping"""
        backend = GraphitiBackend()
        
        from graphiti_core.nodes import EpisodeType
        
        assert backend._map_area_to_episode_type("main") == EpisodeType.text
        assert backend._map_area_to_episode_type("fragments") == EpisodeType.message
        assert backend._map_area_to_episode_type("solutions") == EpisodeType.text
        assert backend._map_area_to_episode_type("instruments") == EpisodeType.text
        assert backend._map_area_to_episode_type("unknown") == EpisodeType.text
    
    def test_source_extraction(self):
        """Test area extraction from source description"""
        backend = GraphitiBackend()
        
        assert backend._extract_area_from_source("agent-zero-main") == "main"
        assert backend._extract_area_from_source("agent-zero-fragments") == "fragments"
        assert backend._extract_area_from_source("other-source") == "main"
```

## Integration Tests

### Test Memory Tools Integration

Create `tests/test_memory_tools.py`:

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from python.tools.memory_save import MemorySave
from python.tools.memory_load import MemoryLoad
from python.tools.memory_delete import MemoryDelete
from python.tools.memory_forget import MemoryForget

class TestMemoryToolsIntegration:
    
    @pytest.fixture
    def mock_agent_with_memory(self):
        """Mock agent with memory abstraction layer"""
        agent = Mock()
        agent.config = Mock()
        agent.config.memory_subdir = "test"
        agent.config.memory_backend = "graphiti"
        
        # Mock memory layer
        memory_layer = Mock()
        memory_layer.insert_text = AsyncMock(return_value="test-uuid-123")
        memory_layer.search_similarity_threshold = AsyncMock(return_value=[
            Mock(page_content="Test memory", score=0.9)
        ])
        memory_layer.delete_documents_by_ids = AsyncMock(return_value=[
            Mock(id="test-uuid-123")
        ])
        memory_layer.delete_documents_by_query = AsyncMock(return_value=[
            Mock(id="test-uuid-456")
        ])
        
        agent._memory_abstraction = memory_layer
        agent.read_prompt = Mock(return_value="Success message")
        
        return agent
    
    @pytest.mark.asyncio
    async def test_memory_save_tool(self, mock_agent_with_memory):
        """Test memory save tool"""
        tool = MemorySave()
        tool.agent = mock_agent_with_memory
        
        with patch('python.helpers.memory.Memory.get_abstraction_layer') as mock_get:
            mock_get.return_value = mock_agent_with_memory._memory_abstraction
            
            response = await tool.execute(text="Test memory", area="main")
            
            assert response.message == "Success message"
            mock_agent_with_memory._memory_abstraction.insert_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_memory_load_tool(self, mock_agent_with_memory):
        """Test memory load tool"""
        tool = MemoryLoad()
        tool.agent = mock_agent_with_memory
        
        with patch('python.helpers.memory.Memory.get_abstraction_layer') as mock_get:
            mock_get.return_value = mock_agent_with_memory._memory_abstraction
            
            response = await tool.execute(query="test query")
            
            assert "Test memory" in response.message
            mock_agent_with_memory._memory_abstraction.search_similarity_threshold.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_memory_delete_tool(self, mock_agent_with_memory):
        """Test memory delete tool"""
        tool = MemoryDelete()
        tool.agent = mock_agent_with_memory
        
        with patch('python.helpers.memory.Memory.get_abstraction_layer') as mock_get:
            mock_get.return_value = mock_agent_with_memory._memory_abstraction
            
            response = await tool.execute(ids="test-uuid-123")
            
            assert response.message == "Success message"
            mock_agent_with_memory._memory_abstraction.delete_documents_by_ids.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_memory_forget_tool(self, mock_agent_with_memory):
        """Test memory forget tool"""
        tool = MemoryForget()
        tool.agent = mock_agent_with_memory
        
        with patch('python.helpers.memory.Memory.get_abstraction_layer') as mock_get:
            mock_get.return_value = mock_agent_with_memory._memory_abstraction
            
            response = await tool.execute(query="test query")
            
            assert response.message == "Success message"
            mock_agent_with_memory._memory_abstraction.delete_documents_by_query.assert_called_once()
```

## Performance Tests

### Test Performance Benchmarks

Create `tests/test_performance.py`:

```python
import pytest
import asyncio
import time
from python.helpers.memory_abstraction import MemoryAbstractionLayer

class TestPerformance:
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_search_latency(self, mock_agent, sample_memories):
        """Test search performance"""
        memory_layer = MemoryAbstractionLayer(mock_agent)
        
        # Mock backend for performance testing
        with patch('python.helpers.memory_graphiti_backend.GraphitiBackend') as mock_backend:
            mock_instance = Mock()
            mock_backend.return_value = mock_instance
            mock_instance.initialize = AsyncMock()
            mock_instance.search_similarity_threshold = AsyncMock(return_value=[])
            
            await memory_layer.initialize()
            
            # Measure search latency
            start_time = time.time()
            await memory_layer.search_similarity_threshold("test query")
            end_time = time.time()
            
            latency = end_time - start_time
            assert latency < 2.0  # Should complete within 2 seconds
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_bulk_operations(self, mock_agent, sample_memories):
        """Test performance with bulk operations"""
        memory_layer = MemoryAbstractionLayer(mock_agent)
        
        with patch('python.helpers.memory_graphiti_backend.GraphitiBackend') as mock_backend:
            mock_instance = Mock()
            mock_backend.return_value = mock_instance
            mock_instance.initialize = AsyncMock()
            mock_instance.insert_text = AsyncMock(return_value="test-uuid")
            
            await memory_layer.initialize()
            
            # Measure bulk insert performance
            start_time = time.time()
            
            tasks = []
            for memory in sample_memories * 10:  # 40 total inserts
                task = memory_layer.insert_text(memory["page_content"], memory["metadata"])
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time_per_insert = total_time / 40
            
            assert avg_time_per_insert < 0.5  # Should average < 0.5s per insert
    
    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_concurrent_access(self, mock_agent):
        """Test concurrent memory operations"""
        memory_layer = MemoryAbstractionLayer(mock_agent)
        
        with patch('python.helpers.memory_graphiti_backend.GraphitiBackend') as mock_backend:
            mock_instance = Mock()
            mock_backend.return_value = mock_instance
            mock_instance.initialize = AsyncMock()
            mock_instance.insert_text = AsyncMock(return_value="test-uuid")
            mock_instance.search_similarity_threshold = AsyncMock(return_value=[])
            
            await memory_layer.initialize()
            
            # Test concurrent operations
            async def concurrent_operations():
                tasks = []
                
                # Mix of insert and search operations
                for i in range(10):
                    if i % 2 == 0:
                        task = memory_layer.insert_text(f"Test {i}", {"area": "main"})
                    else:
                        task = memory_layer.search_similarity_threshold(f"query {i}")
                    tasks.append(task)
                
                return await asyncio.gather(*tasks)
            
            start_time = time.time()
            results = await concurrent_operations()
            end_time = time.time()
            
            assert len(results) == 10
            assert end_time - start_time < 5.0  # Should complete within 5 seconds
```

## Running Tests

### Test Execution Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_memory_abstraction.py -v
python -m pytest tests/test_graphiti_backend.py -v
python -m pytest tests/test_memory_tools.py -v

# Run performance tests (marked as slow)
python -m pytest tests/test_performance.py -v -m slow

# Run with coverage
python -m pytest tests/ --cov=python.helpers --cov-report=html --cov-report=term

# Run tests in parallel (if pytest-xdist installed)
python -m pytest tests/ -n auto

# Run tests with detailed output
python -m pytest tests/ -v -s --tb=long
```

### Continuous Integration

Create `.github/workflows/test.yml` for automated testing:

```yaml
name: Test Memory System

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      neo4j:
        image: neo4j:5.22.0
        env:
          NEO4J_AUTH: neo4j/password
        ports:
          - 7687:7687
          - 7474:7474
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.10
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install "graphiti-core[anthropic,groq,google-genai]"
        pip install pytest pytest-asyncio pytest-mock pytest-cov
    
    - name: Run tests
      env:
        NEO4J_URI: bolt://localhost:7687
        NEO4J_USER: neo4j
        NEO4J_PASSWORD: password
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      run: |
        python -m pytest tests/ --cov=python.helpers --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Manual Testing

### Agent Functionality Tests

```bash
# Start agent with Graphiti backend
MEMORY_BACKEND=graphiti python initialize.py

# Test basic memory operations:
# 1. Save a memory: "Remember that I prefer Python for data analysis"
# 2. Search memories: "What do you know about my programming preferences?"
# 3. Delete a memory: Use memory_delete tool with specific ID
# 4. Test extensions: Verify automatic memory recall works

# Test temporal queries:
# 1. Save memories at different times
# 2. Query for recent vs. older memories
# 3. Test relationship-based searches
```

### Performance Validation

```bash
# Monitor memory usage
htop

# Monitor Neo4j performance
docker stats neo4j-agent-zero

# Test with large datasets
# (Create script to insert 1000+ memories and test search performance)
```

## Test Data Management

### Test Database Setup

```bash
# Create separate test database
docker run -d \
  --name neo4j-test \
  -p 7688:7687 \
  -e NEO4J_AUTH=neo4j/testpassword \
  neo4j:5.22.0

# Use test database for testing
export NEO4J_URI=bolt://localhost:7688
export NEO4J_PASSWORD=testpassword
```

### Test Data Cleanup

```python
# Add to test fixtures
@pytest.fixture(autouse=True)
async def cleanup_test_data():
    """Clean up test data after each test"""
    yield
    
    # Clear test database
    from graphiti_core.utils.maintenance.graph_data_operations import clear_data
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver("bolt://localhost:7688", auth=("neo4j", "testpassword"))
    await clear_data(driver)
    driver.close()
```

## Success Criteria

### Test Coverage Goals
- **Unit Tests**: >95% coverage of memory abstraction layer
- **Integration Tests**: All memory tools and extensions tested
- **Performance Tests**: Latency within acceptable limits
- **Manual Tests**: Full agent functionality validated

### Quality Gates
- All tests must pass before deployment
- Performance benchmarks must meet requirements
- Code coverage must exceed 90%
- No critical security vulnerabilities

## Troubleshooting Tests

### Common Test Issues

**Neo4j Connection Failures:**
```bash
# Check if Neo4j is running
docker ps | grep neo4j

# Check connection
python -c "from neo4j import GraphDatabase; print('OK')"
```

**Test Data Conflicts:**
```bash
# Clear test database
docker exec neo4j-test cypher-shell -u neo4j -p testpassword "MATCH (n) DETACH DELETE n"
```

**Slow Test Performance:**
```bash
# Run tests with profiling
python -m pytest tests/ --profile

# Run specific slow tests
python -m pytest tests/ -m slow -v
```

This comprehensive testing strategy ensures the Graphiti memory system is thoroughly validated before production deployment.
