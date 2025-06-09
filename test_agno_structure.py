#!/usr/bin/env python3
"""
Test Script for Agno Integration Structure
Tests the integration without requiring API keys or full Agent Zero environment
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_success(message):
    print(f"✅ {message}")


def print_error(message):
    print(f"❌ {message}")


def print_info(message):
    print(f"ℹ️  {message}")


def test_agno_imports():
    """Test that Agno can be imported"""
    print_info("Testing Agno imports...")
    
    try:
        # Add agno to path
        agno_path = os.path.join(os.path.dirname(__file__), 'agno', 'libs', 'agno')
        if agno_path not in sys.path:
            sys.path.insert(0, agno_path)
        
        from agno.agent import Agent as AgnoAgent
        print_success("Agno Agent imported successfully")
        
        from agno.team.team import Team as AgnoTeam
        print_success("Agno Team imported successfully")
        
        from agno.models.openai import OpenAIChat
        print_success("Agno OpenAI model imported successfully")
        
        return True
        
    except Exception as e:
        print_error(f"Agno import failed: {e}")
        return False


def test_orchestrator_structure():
    """Test orchestrator structure without execution"""
    print_info("Testing Agno orchestrator structure...")
    
    try:
        from python.helpers.agno_orchestrator import AgnoOrchestrator, AGNO_AVAILABLE
        
        print_success(f"AGNO_AVAILABLE: {AGNO_AVAILABLE}")
        
        if not AGNO_AVAILABLE:
            print_error("Agno not available for orchestrator")
            return False
        
        # Test class structure
        print_success("AgnoOrchestrator class imported")
        
        # Test methods exist
        methods = ['delegate_task', 'get_orchestration_status', 'get_available_agents_summary', 'is_available']
        for method in methods:
            if hasattr(AgnoOrchestrator, method):
                print_success(f"Method {method} exists")
            else:
                print_error(f"Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print_error(f"Orchestrator structure test failed: {e}")
        return False


def test_task_analyzer():
    """Test task analyzer structure"""
    print_info("Testing task analyzer...")
    
    try:
        from python.helpers.task_analyzer import TaskAnalyzer, TaskComplexity, CoordinationMode
        
        print_success("TaskAnalyzer imported")
        print_success(f"TaskComplexity values: {[c.value for c in TaskComplexity]}")
        print_success(f"CoordinationMode values: {[c.value for c in CoordinationMode]}")
        
        # Test pattern analysis without LLM
        class MockAgent:
            pass
        
        analyzer = TaskAnalyzer(MockAgent())
        
        # Test pattern-based analysis
        result = analyzer._pattern_analyze_task("Write a Python function to parse CSV files")
        print_success(f"Pattern analysis works: {result.complexity.value}")
        
        return True
        
    except Exception as e:
        print_error(f"Task analyzer test failed: {e}")
        return False


def test_delegate_task_tool():
    """Test delegate task tool structure"""
    print_info("Testing delegate task tool...")
    
    try:
        from python.tools.delegate_task import DelegateTask, Delegation, CallSubordinate
        
        print_success("DelegateTask imported")
        print_success("Delegation (backward compatibility) imported")
        print_success("CallSubordinate (alias) imported")
        
        # Test method exists
        if hasattr(DelegateTask, 'execute'):
            print_success("DelegateTask.execute method exists")
        else:
            print_error("DelegateTask.execute method missing")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Delegate task tool test failed: {e}")
        return False


def test_agno_agent_creation():
    """Test Agno agent creation structure"""
    print_info("Testing Agno agent creation...")
    
    try:
        # Add agno to path
        agno_path = os.path.join(os.path.dirname(__file__), 'agno', 'libs', 'agno')
        if agno_path not in sys.path:
            sys.path.insert(0, agno_path)
        
        from agno.agent import Agent as AgnoAgent
        from agno.models.openai import OpenAIChat
        
        # Test agent creation (without API call)
        model = OpenAIChat(id="gpt-4o")
        print_success("OpenAI model created")
        
        agent = AgnoAgent(
            name="Test Agent",
            role="Test role",
            model=model,
            instructions=["Test instruction"],
            markdown=True
        )
        print_success("Agno agent created successfully")
        
        # Test agent attributes
        assert agent.name == "Test Agent"
        assert agent.role == "Test role"
        print_success("Agent attributes set correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Agno agent creation test failed: {e}")
        return False


def test_agno_team_creation():
    """Test Agno team creation structure"""
    print_info("Testing Agno team creation...")
    
    try:
        # Add agno to path
        agno_path = os.path.join(os.path.dirname(__file__), 'agno', 'libs', 'agno')
        if agno_path not in sys.path:
            sys.path.insert(0, agno_path)
        
        from agno.agent import Agent as AgnoAgent
        from agno.team.team import Team as AgnoTeam
        from agno.models.openai import OpenAIChat
        
        # Create test agents
        model = OpenAIChat(id="gpt-4o")
        
        agent1 = AgnoAgent(name="Agent 1", role="Role 1", model=model)
        agent2 = AgnoAgent(name="Agent 2", role="Role 2", model=model)
        
        # Create team
        team = AgnoTeam(
            name="Test Team",
            members=[agent1, agent2],
            mode="coordinate",
            model=model,
            instructions=["Test team instruction"]
        )
        print_success("Agno team created successfully")
        
        # Test team attributes
        assert team.name == "Test Team"
        assert team.mode == "coordinate"
        assert len(team.members) == 2
        print_success("Team attributes set correctly")
        
        return True
        
    except Exception as e:
        print_error(f"Agno team creation test failed: {e}")
        return False


def main():
    """Run all structure tests"""
    print("🚀 Agno Integration Structure Tests")
    print("=" * 50)
    
    tests = [
        ("Agno Imports", test_agno_imports),
        ("Orchestrator Structure", test_orchestrator_structure),
        ("Task Analyzer", test_task_analyzer),
        ("Delegate Task Tool", test_delegate_task_tool),
        ("Agno Agent Creation", test_agno_agent_creation),
        ("Agno Team Creation", test_agno_team_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print_error(f"Test {test_name} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎯 Structure Test Results")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("🎉 All structure tests passed!")
        print_info("Agno integration is properly structured and ready for use")
        return True
    else:
        print_error(f"💥 {total - passed} structure tests failed.")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"💥 Test execution failed: {e}")
        sys.exit(1)
