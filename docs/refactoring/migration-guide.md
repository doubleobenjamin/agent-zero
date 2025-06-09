# Agent Zero Migration Guide: Upgrading to Graphiti + Agno + ACI

## Overview

This guide helps you migrate from the current Agent Zero implementation to the new integrated system featuring Graphiti (temporal knowledge graphs), Agno (multi-agent orchestration), and ACI (standardized tool interfaces). The migration preserves existing functionality while adding powerful new capabilities. Migration speed depends on system complexity and autonomous agent compute capacity.

## Pre-Migration Checklist

### 1. Backup Current System
```bash
# Create backup of current Agent Zero installation
cp -r /path/to/agent-zero /path/to/agent-zero-backup

# Backup memory files
tar -czf memory-backup-$(date +%Y%m%d).tar.gz memory/

# Backup configuration
cp .env .env.backup
cp tmp/settings.json tmp/settings.json.backup
```

### 2. System Requirements
```bash
# Required services
- Docker and Docker Compose
- Python 3.10+
- Neo4j 5.26+ (for Graphiti)
- 8GB+ RAM recommended
- 10GB+ disk space

# Required API keys
- OpenAI API key (for embeddings and LLM)
- ACI API key (for tool access)
- Service-specific keys (Google, Slack, etc.)
```

### 3. Environment Preparation
```bash
# Install additional dependencies
pip install graphiti-core agno aci-python-sdk

# Start Neo4j database
docker run -d \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/password \
    -v neo4j_data:/data \
    neo4j:5.26
```

## Migration Process

### Phase 1: Configuration Migration

#### 1.1 Update Environment Variables
```bash
# Add to .env file
# Graphiti configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
GRAPHITI_NAMESPACE_PREFIX=agent_zero

# ACI configuration  
ACI_API_KEY=your_aci_api_key
ACI_PROJECT_ID=your_project_id
ACI_BASE_URL=https://api.aci.dev

# Agno configuration
AGNO_MAX_CONCURRENT_AGENTS=10
AGNO_AGENT_TIMEOUT=300
AGNO_ENABLE_PERSISTENT_AGENTS=true
```

#### 1.2 Update Agent Configuration
```python
# In initialize.py, update AgentConfig
config = AgentConfig(
    # Existing configuration
    chat_model=chat_llm,
    utility_model=utility_llm,
    embeddings_model=embedding_llm,
    browser_model=browser_llm,
    
    # New Graphiti configuration
    graphiti_enabled=True,
    graphiti_namespace_prefix="agent_zero",
    
    # New Agno configuration  
    agno_enabled=True,
    max_concurrent_agents=10,
    enable_persistent_agents=True,
    
    # New ACI configuration
    aci_api_key=os.getenv("ACI_API_KEY"),
    aci_project_id=os.getenv("ACI_PROJECT_ID"),
    aci_enabled=True
)
```

### Phase 2: Memory Migration

#### 2.1 Migrate File-Based Memory to Graphiti
```python
# Run migration script
python scripts/migrate_memory_to_graphiti.py

# Migration script content:
import json
import os
from datetime import datetime
from graphiti_core import Graphiti

class MemoryMigrator:
    def __init__(self):
        self.graphiti = Graphiti(
            uri=os.getenv("NEO4J_URI"),
            user=os.getenv("NEO4J_USER"), 
            password=os.getenv("NEO4J_PASSWORD")
        )
    
    async def migrate_memory_files(self, memory_dir: str = "memory"):
        """Migrate existing memory files to Graphiti"""
        
        if not os.path.exists(memory_dir):
            print("No memory directory found, skipping migration")
            return
        
        migrated_count = 0
        
        for filename in os.listdir(memory_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(memory_dir, filename)
                
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Convert to Graphiti episode
                    await self.graphiti.add_episode(
                        name=filename.replace('.json', ''),
                        episode_body=json.dumps(data),
                        source_description="Migrated from file memory",
                        reference_time=datetime.now(),
                        group_id="migrated"
                    )
                    
                    migrated_count += 1
                    print(f"Migrated: {filename}")
                    
                except Exception as e:
                    print(f"Error migrating {filename}: {e}")
        
        print(f"Migration complete: {migrated_count} files migrated")

# Run migration
if __name__ == "__main__":
    import asyncio
    migrator = MemoryMigrator()
    asyncio.run(migrator.migrate_memory_files())
```

#### 2.2 Verify Memory Migration
```python
# Test script to verify migration
async def verify_migration():
    from python.helpers.graphiti_memory import GraphitiMemory
    
    # Create test agent
    agent = Agent(0, config, context)
    memory = GraphitiMemory(agent)
    
    # Test memory retrieval
    results = await memory.load_facts("test query", limit=5)
    print(f"Found {len(results)} migrated memories")
    
    # Test memory saving
    await memory.save_fact("test", "migration", "successful")
    print("New memory save successful")

asyncio.run(verify_migration())
```

### Phase 3: Tool Migration

#### 3.1 Set Up ACI Authentication
```python
# Run ACI setup script
python scripts/setup_aci_auth.py

# Setup script content:
import asyncio
from python.helpers.aci_interface import ACIToolInterface

class ACISetup:
    def __init__(self):
        self.aci_interface = ACIToolInterface(None)  # No agent needed for setup
    
    async def setup_authentication(self):
        """Set up ACI authentication for common services"""
        
        print("Setting up ACI authentication...")
        
        # Discover available tools
        tools = await self.aci_interface.discover_tools()
        print(f"Discovered {len(tools)} available tools")
        
        # List tool categories
        categories = {}
        for tool_name, metadata in tools.items():
            category = metadata.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)
        
        print("\nAvailable tool categories:")
        for category, tool_list in categories.items():
            print(f"  {category}: {len(tool_list)} tools")
        
        # Setup authentication for key services
        key_services = ['google', 'github', 'slack', 'notion']
        
        for service in key_services:
            if any(service in tool for tool in tools.keys()):
                print(f"\nSetting up {service} authentication...")
                # Guide user through OAuth setup
                await self._setup_service_auth(service)
    
    async def _setup_service_auth(self, service: str):
        """Guide user through service authentication"""
        
        print(f"1. Visit ACI dashboard: https://app.aci.dev")
        print(f"2. Navigate to Integrations > {service}")
        print(f"3. Follow OAuth setup instructions")
        print(f"4. Verify connection in dashboard")
        
        input(f"Press Enter when {service} authentication is complete...")

# Run setup
if __name__ == "__main__":
    setup = ACISetup()
    asyncio.run(setup.setup_authentication())
```

#### 3.2 Test Tool Migration
```python
# Test ACI tool functionality
async def test_aci_tools():
    from python.helpers.aci_interface import ACIToolInterface
    
    agent = Agent(0, config, context)
    aci = ACIToolInterface(agent)
    
    # Test tool discovery
    tools = await aci.discover_tools()
    print(f"Available tools: {list(tools.keys())[:10]}...")
    
    # Test tool execution
    try:
        result = await aci.execute_tool(
            tool_name="web_search",
            args={"query": "test search", "num_results": 3}
        )
        print("Tool execution successful:", result.get("success", False))
    except Exception as e:
        print(f"Tool execution error: {e}")

asyncio.run(test_aci_tools())
```

### Phase 4: Agent System Migration

#### 4.1 Update Agent Spawning
```python
# Replace call_subordinate usage with delegate_task

# Old usage:
# await agent.process_tools('{"tool_name": "call_subordinate", "tool_args": {"message": "Analyze this data"}}')

# New usage:
await agent.process_tools('{"tool_name": "delegate_task", "tool_args": {"task": "Analyze this data", "task_type": "analysis"}}')
```

#### 4.2 Configure Persistent Agents
```python
# Create persistent agent configuration
PERSISTENT_AGENTS = {
    "code_expert": {
        "role": "Senior Software Engineer",
        "specialization": "Python, JavaScript, debugging",
        "tools": ["code_execution", "github", "documentation"],
        "memory_namespace": "code_expert"
    },
    "research_expert": {
        "role": "Research Analyst",
        "specialization": "Information gathering, analysis",
        "tools": ["web_search", "webpage_content", "knowledge_tool"],
        "memory_namespace": "research_expert"
    }
}

# Initialize persistent agents
async def initialize_persistent_agents():
    agent = Agent(0, config, context)
    
    for expert_type, expert_config in PERSISTENT_AGENTS.items():
        expert_agent = await agent.agno_orchestrator.create_persistent_agent(
            role=expert_config["role"],
            specialization=expert_config["specialization"]
        )
        print(f"Created persistent agent: {expert_type}")

asyncio.run(initialize_persistent_agents())
```

## Backward Compatibility

### 1. Legacy Tool Support
```python
# Hybrid tool system during transition
class HybridToolSystem:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.aci_interface = ACIToolInterface(agent)
        self.legacy_tools = LegacyToolLoader()
    
    def get_tool(self, name: str, **kwargs):
        # Try ACI tools first
        if self.aci_interface.has_tool(name):
            return ACITool(self.agent, name, **kwargs)
        
        # Fallback to legacy tools
        return self.legacy_tools.get_tool(name, **kwargs)
```

### 2. Memory Compatibility
```python
# Hybrid memory system
class HybridMemory:
    def __init__(self, agent: Agent):
        self.graphiti_memory = GraphitiMemory(agent)
        self.file_memory = FileMemory(agent)  # Legacy
    
    async def load_facts(self, query: str):
        # Try Graphiti first
        results = await self.graphiti_memory.load_facts(query)
        
        # Supplement with file memory if needed
        if len(results) < 5:
            file_results = self.file_memory.load_facts(query)
            results.extend(file_results)
        
        return results
```

## Validation and Testing

### 1. System Health Check
```python
# Run comprehensive health check
python scripts/health_check.py

# Health check script:
async def run_health_check():
    checks = {
        "neo4j": check_neo4j_connection(),
        "graphiti": check_graphiti_service(),
        "aci": check_aci_connectivity(),
        "agno": check_agno_functionality(),
        "memory": check_memory_migration(),
        "tools": check_tool_functionality()
    }
    
    results = {}
    for check_name, check_func in checks.items():
        try:
            result = await check_func()
            results[check_name] = {"status": "pass", "details": result}
        except Exception as e:
            results[check_name] = {"status": "fail", "error": str(e)}
    
    # Print results
    print("\n=== System Health Check ===")
    for check_name, result in results.items():
        status = result["status"]
        print(f"{check_name}: {status.upper()}")
        if status == "fail":
            print(f"  Error: {result['error']}")
    
    overall_status = "PASS" if all(r["status"] == "pass" for r in results.values()) else "FAIL"
    print(f"\nOverall Status: {overall_status}")

asyncio.run(run_health_check())
```

### 2. Functionality Testing
```python
# Test key workflows
async def test_workflows():
    agent = Agent(0, config, context)
    
    # Test 1: Memory functionality
    await agent.graphiti_memory.save_fact("user", "name", "John")
    results = await agent.graphiti_memory.load_facts("user name")
    assert len(results) > 0, "Memory save/load failed"
    
    # Test 2: Agent delegation
    result = await agent.agno_orchestrator.delegate_task(
        "Write a simple Python function",
        "coding"
    )
    assert result is not None, "Agent delegation failed"
    
    # Test 3: Tool execution
    result = await agent.aci_interface.execute_tool(
        "web_search",
        {"query": "test", "num_results": 1}
    )
    assert result.get("success"), "Tool execution failed"
    
    print("All workflow tests passed!")

asyncio.run(test_workflows())
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Neo4j Connection Issues
```bash
# Check Neo4j status
docker ps | grep neo4j

# Check logs
docker logs neo4j

# Restart if needed
docker restart neo4j

# Test connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1')
    print('Neo4j connection successful')
driver.close()
"
```

#### 2. ACI Authentication Issues
```bash
# Verify API key
curl -H "Authorization: Bearer $ACI_API_KEY" \
     -H "X-Project-ID: $ACI_PROJECT_ID" \
     https://api.aci.dev/health

# Check project quota
curl -H "Authorization: Bearer $ACI_API_KEY" \
     -H "X-Project-ID: $ACI_PROJECT_ID" \
     https://api.aci.dev/projects/$ACI_PROJECT_ID/quota
```

#### 3. Memory Migration Issues
```python
# Check migration status
async def check_migration_status():
    from python.helpers.graphiti_memory import GraphitiMemory
    
    agent = Agent(0, config, context)
    memory = GraphitiMemory(agent)
    
    # Count migrated episodes
    episodes = await memory.graphiti.search_episodes(
        query="",
        group_ids=["migrated"],
        limit=1000
    )
    
    print(f"Migrated episodes: {len(episodes)}")
    
    # Check for any errors
    for episode in episodes[:5]:
        print(f"Episode: {episode.name}")

asyncio.run(check_migration_status())
```

## Performance Optimization

### 1. Neo4j Optimization
```cypher
-- Create indexes for better performance
CREATE INDEX entity_name_index FOR (n:Entity) ON (n.name);
CREATE INDEX entity_group_index FOR (n:Entity) ON (n.group_id);
CREATE INDEX episode_group_index FOR (n:Episodic) ON (n.group_id);
```

### 2. Memory Configuration
```python
# Optimize memory settings
MEMORY_CONFIG = {
    "cache_size": 1000,
    "query_timeout": 30,
    "max_results": 50,
    "enable_caching": True
}
```

### 3. Agent Pool Configuration
```python
# Optimize agent management
AGENT_CONFIG = {
    "max_concurrent_agents": 10,
    "agent_timeout": 300,
    "cleanup_interval": 3600,
    "enable_agent_reuse": True
}
```

## Rollback Procedure

If issues arise, you can rollback to the previous system:

```bash
# 1. Stop new services
docker stop neo4j

# 2. Restore backup
rm -rf /path/to/agent-zero
cp -r /path/to/agent-zero-backup /path/to/agent-zero

# 3. Restore configuration
cp .env.backup .env
cp tmp/settings.json.backup tmp/settings.json

# 4. Restore memory files
tar -xzf memory-backup-*.tar.gz

# 5. Restart original system
python run_ui.py
```

## Post-Migration Verification

### 1. Feature Verification Checklist
- [ ] Memory persistence across restarts
- [ ] Agent delegation working
- [ ] Tool execution functional
- [ ] Team coordination operational
- [ ] Performance within acceptable limits
- [ ] All existing workflows functional

### 2. Performance Benchmarks
```python
# Run performance tests
python scripts/performance_benchmark.py

# Expected benchmarks:
# - Memory query: < 100ms
# - Agent spawn: < 2s  
# - Tool execution: < 5s
# - Workflow completion: < 30s
```

### 3. User Acceptance Testing
```python
# Test common user scenarios
test_scenarios = [
    "Ask a simple question",
    "Request code generation", 
    "Perform web research",
    "Analyze data",
    "Complex multi-step task"
]

for scenario in test_scenarios:
    print(f"Testing: {scenario}")
    # Execute scenario and verify results
```

The migration is complete when all tests pass and the system performs within expected parameters. The new integrated system provides enhanced capabilities while maintaining full backward compatibility with existing Agent Zero workflows.
