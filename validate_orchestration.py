#!/usr/bin/env python3
"""
Validation Script for Multi-Agent Orchestration System
Phase 1, Agent 2 Implementation Validation
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_success(message):
    print(f"✅ {message}")


def print_error(message):
    print(f"❌ {message}")


def print_info(message):
    print(f"ℹ️  {message}")


def test_imports():
    """Test that all orchestration modules can be imported"""
    print_info("Testing module imports...")
    
    try:
        from python.helpers.task_analyzer import TaskAnalyzer, TaskComplexity, CoordinationMode
        print_success("TaskAnalyzer imported successfully")
        
        from python.helpers.agent_registry import AgentRegistry, AgentType, AgentCapabilities
        print_success("AgentRegistry imported successfully")
        
        from python.helpers.team_coordinator import TeamCoordinator
        print_success("TeamCoordinator imported successfully")
        
        from python.helpers.agno_orchestrator import AgnoOrchestrator
        print_success("AgnoOrchestrator imported successfully")
        
        from python.tools.delegate_task import DelegateTask, Delegation
        print_success("DelegateTask tool imported successfully")
        
        return True
        
    except Exception as e:
        print_error(f"Import failed: {e}")
        return False


def test_task_analyzer():
    """Test task analyzer functionality"""
    print_info("Testing TaskAnalyzer...")
    
    try:
        from python.helpers.task_analyzer import TaskAnalyzer, TaskComplexity
        
        class MockAgent:
            async def call_utility_model(self, system, message):
                return '{"complexity": "specialist", "domains": ["coding"], "required_skills": ["python"], "coordination_mode": "route", "estimated_time": "moderate", "requires_team": false, "confidence": 0.8, "reasoning": "Test analysis"}'
        
        analyzer = TaskAnalyzer(MockAgent())
        
        # Test pattern analysis
        result = analyzer._pattern_analyze_task("Write a Python function to process data")
        
        assert result.complexity in [TaskComplexity.SIMPLE, TaskComplexity.SPECIALIST, TaskComplexity.COMPLEX]
        assert isinstance(result.domains, list)
        assert len(result.domains) > 0
        
        print_success("TaskAnalyzer pattern analysis working")
        
        # Test domain detection
        coding_result = analyzer._pattern_analyze_task("Debug this Python code")
        assert "coding" in coding_result.domains
        
        research_result = analyzer._pattern_analyze_task("Research the latest AI trends")
        assert "research" in research_result.domains
        
        print_success("TaskAnalyzer domain detection working")
        
        return True
        
    except Exception as e:
        print_error(f"TaskAnalyzer test failed: {e}")
        return False


def test_agent_registry():
    """Test agent registry functionality"""
    print_info("Testing AgentRegistry...")
    
    try:
        from python.helpers.agent_registry import AgentRegistry, AgentType
        
        class MockAgent:
            def __init__(self):
                self.number = 0
        
        registry = AgentRegistry(MockAgent())
        
        # Test expert templates
        assert len(registry.expert_templates) > 0
        assert "code_expert" in registry.expert_templates
        assert "research_expert" in registry.expert_templates
        
        print_success("Expert templates loaded")
        
        # Test expert creation
        expert_id = registry.create_expert_agent("code_expert")
        assert expert_id is not None
        
        agent_info = registry.get_agent(expert_id)
        assert agent_info is not None
        assert agent_info.agent_type == AgentType.PERSISTENT_EXPERT
        assert "coding" in agent_info.capabilities.domains
        
        print_success("Expert agent creation working")
        
        # Test agent lookup
        available_agents = registry.get_available_agents()
        assert len(available_agents) > 0
        
        coding_agents = registry.get_agents_by_domain("coding")
        assert len(coding_agents) > 0
        
        print_success("Agent lookup working")
        
        # Test performance tracking
        success = registry.update_performance_metrics(expert_id, True, 120.0)
        assert success
        
        updated_agent = registry.get_agent(expert_id)
        assert updated_agent.capabilities.total_tasks == 1
        assert updated_agent.capabilities.successful_tasks == 1
        
        print_success("Performance tracking working")
        
        return True
        
    except Exception as e:
        print_error(f"AgentRegistry test failed: {e}")
        return False


async def test_team_coordinator():
    """Test team coordinator functionality"""
    print_info("Testing TeamCoordinator...")
    
    try:
        from python.helpers.team_coordinator import TeamCoordinator
        from python.helpers.agent_registry import AgentRegistry
        from python.helpers.task_analyzer import TaskAnalysis, TaskComplexity, CoordinationMode
        
        class MockAgent:
            def __init__(self):
                self.number = 0
        
        mock_agent = MockAgent()
        registry = AgentRegistry(mock_agent)
        coordinator = TeamCoordinator(mock_agent, registry)
        
        # Create some expert agents
        code_expert_id = registry.create_expert_agent("code_expert")
        research_expert_id = registry.create_expert_agent("research_expert")
        
        assert code_expert_id and research_expert_id
        print_success("Expert agents created for team testing")
        
        # Create mock task analysis
        task_analysis = TaskAnalysis(
            complexity=TaskComplexity.COMPLEX,
            domains=["coding", "research"],
            required_skills=["python"],
            coordination_mode=CoordinationMode.COORDINATE,
            estimated_time="moderate",
            requires_team=True,
            confidence=0.9,
            reasoning="Test complex task"
        )
        
        # Test team creation
        team_id = await coordinator.create_team(task_analysis, "Test complex task")
        assert team_id is not None
        
        team_info = coordinator.get_team_info(team_id)
        assert team_info is not None
        assert len(team_info.members) > 0
        
        print_success("Team creation working")
        
        # Test team execution
        result = await coordinator.execute_team_task(team_id, "Test task execution")
        assert result is not None
        assert len(result) > 0
        
        print_success("Team execution working")
        
        return True
        
    except Exception as e:
        print_error(f"TeamCoordinator test failed: {e}")
        return False


async def test_agno_orchestrator():
    """Test main orchestration engine"""
    print_info("Testing AgnoOrchestrator...")
    
    try:
        from python.helpers.agno_orchestrator import AgnoOrchestrator
        
        class MockAgent:
            def __init__(self):
                self.number = 0
                self.config = None
                self.context = None
            
            def get_data(self, key):
                return None
            
            def set_data(self, key, value):
                pass
        
        mock_agent = MockAgent()
        orchestrator = AgnoOrchestrator(mock_agent)
        
        # Test initialization
        assert orchestrator.task_analyzer is not None
        assert orchestrator.agent_registry is not None
        assert orchestrator.team_coordinator is not None
        
        print_success("Orchestrator components initialized")
        
        # Test availability check
        is_available = orchestrator.is_available()
        assert is_available
        
        print_success("Orchestrator availability check working")
        
        # Test status reporting
        status = orchestrator.get_orchestration_status()
        assert status["status"] == "active"
        assert "components" in status
        assert "agents" in status
        
        print_success("Orchestration status reporting working")
        
        # Test agent summary
        agents_summary = orchestrator.get_available_agents_summary()
        assert isinstance(agents_summary, list)
        
        print_success("Available agents summary working")
        
        return True
        
    except Exception as e:
        print_error(f"AgnoOrchestrator test failed: {e}")
        return False


def test_delegate_task_tool():
    """Test delegate task tool"""
    print_info("Testing DelegateTask tool...")
    
    try:
        from python.tools.delegate_task import DelegateTask, Delegation
        
        class MockAgent:
            def __init__(self):
                self.number = 0
                self.agno_orchestrator = None
            
            def get_data(self, key):
                return None
            
            def set_data(self, key, value):
                pass
        
        mock_agent = MockAgent()
        
        # Test DelegateTask creation
        tool = DelegateTask(agent=mock_agent, name="delegate_task", method=None, args={}, message="")
        assert hasattr(tool, "execute")
        assert hasattr(tool, "_fallback_delegation")
        
        print_success("DelegateTask tool created successfully")
        
        # Test Delegation (backward compatibility)
        legacy_tool = Delegation(agent=mock_agent, name="call_subordinate", method=None, args={}, message="")
        assert hasattr(legacy_tool, "execute")
        
        print_success("Backward compatibility tool created successfully")
        
        return True
        
    except Exception as e:
        print_error(f"DelegateTask tool test failed: {e}")
        return False


def test_agent_integration():
    """Test integration with Agent class"""
    print_info("Testing Agent class integration...")
    
    try:
        # Test that Agent class has orchestration attributes
        import inspect
        from agent import Agent
        
        # Check if Agent.__init__ has orchestration initialization
        source = inspect.getsource(Agent.__init__)
        assert "agno_orchestrator" in source
        
        print_success("Agent class has orchestration integration")
        
        return True
        
    except Exception as e:
        print_error(f"Agent integration test failed: {e}")
        return False


def test_prompt_enhancer():
    """Test prompt enhancer integration"""
    print_info("Testing PromptEnhancer integration...")
    
    try:
        from python.helpers.prompt_enhancer import PromptEnhancer, get_prompt_enhancer
        
        class MockAgent:
            def __init__(self):
                self.agno_orchestrator = None
        
        mock_agent = MockAgent()
        enhancer = get_prompt_enhancer(mock_agent)
        
        # Test enhanced variables
        variables = enhancer.get_enhanced_variables()
        assert "orchestration_status" in variables
        assert "available_agents" in variables
        
        print_success("PromptEnhancer orchestration variables working")
        
        return True
        
    except Exception as e:
        print_error(f"PromptEnhancer test failed: {e}")
        return False


async def main():
    """Run all validation tests"""
    print("🚀 Multi-Agent Orchestration System Validation")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Task Analyzer", test_task_analyzer),
        ("Agent Registry", test_agent_registry),
        ("Team Coordinator", test_team_coordinator),
        ("Agno Orchestrator", test_agno_orchestrator),
        ("Delegate Task Tool", test_delegate_task_tool),
        ("Agent Integration", test_agent_integration),
        ("Prompt Enhancer", test_prompt_enhancer)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append(result)
        except Exception as e:
            print_error(f"Test {test_name} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Validation Results Summary")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("🎉 All validation tests passed! Phase 1, Agent 2 implementation is complete.")
        return True
    else:
        print_error(f"💥 {total - passed} validation tests failed.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"💥 Validation execution failed: {e}")
        sys.exit(1)
