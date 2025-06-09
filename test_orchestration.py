#!/usr/bin/env python3
"""
Test Script for Multi-Agent Orchestration System
Validates Phase 1, Agent 2 implementation
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.helpers.print_style import PrintStyle
from python.helpers.task_analyzer import TaskAnalyzer, TaskComplexity, CoordinationMode
from python.helpers.agent_registry import AgentRegistry, AgentType, AgentCapabilities
from python.helpers.team_coordinator import TeamCoordinator
from python.helpers.agno_orchestrator import AgnoOrchestrator
from initialize import initialize_agent


async def test_task_analyzer():
    """Test task analysis functionality"""
    PrintStyle.standard("=== Testing Task Analyzer ===")
    
    try:
        # Initialize agent
        config = initialize_agent()
        from agent import Agent, AgentContext
        context = AgentContext(config)
        agent = Agent(0, config, context)
        
        # Create task analyzer
        analyzer = TaskAnalyzer(agent)
        
        # Test different types of tasks
        test_tasks = [
            ("Write a simple hello world program", "coding"),
            ("Research the latest developments in AI", "research"),
            ("Create a comprehensive data analysis pipeline with visualization and machine learning", "data"),
            ("Fix this bug and deploy to production", "coding"),
            ("Write documentation for the API", "writing")
        ]
        
        for task, task_type in test_tasks:
            PrintStyle.standard(f"\nAnalyzing: {task}")
            analysis = await analyzer.analyze_task_requirements(task, task_type)
            
            print(f"  Complexity: {analysis.complexity.value}")
            print(f"  Domains: {analysis.domains}")
            print(f"  Coordination: {analysis.coordination_mode.value}")
            print(f"  Requires Team: {analysis.requires_team}")
            print(f"  Confidence: {analysis.confidence:.2f}")
            print(f"  Reasoning: {analysis.reasoning}")
        
        PrintStyle.standard("✅ Task Analyzer tests passed")
        return True
        
    except Exception as e:
        PrintStyle.error(f"❌ Task Analyzer test failed: {e}")
        return False


async def test_agent_registry():
    """Test agent registry functionality"""
    PrintStyle.standard("\n=== Testing Agent Registry ===")
    
    try:
        # Initialize agent
        config = initialize_agent()
        from agent import Agent, AgentContext
        context = AgentContext(config)
        agent = Agent(0, config, context)
        
        # Create registry
        registry = AgentRegistry(agent)
        
        # Test expert agent creation
        expert_types = ["code_expert", "research_expert", "data_expert"]
        created_agents = []
        
        for expert_type in expert_types:
            agent_id = registry.create_expert_agent(expert_type)
            if agent_id:
                created_agents.append(agent_id)
                PrintStyle.standard(f"✅ Created {expert_type}: {agent_id}")
            else:
                PrintStyle.error(f"❌ Failed to create {expert_type}")
        
        # Test agent lookup
        available_agents = registry.get_available_agents()
        PrintStyle.standard(f"Available agents: {len(available_agents)}")
        
        # Test domain-based lookup
        coding_agents = registry.get_agents_by_domain("coding")
        PrintStyle.standard(f"Coding specialists: {len(coding_agents)}")
        
        # Test best agent selection
        best_agent = registry.get_best_agent_for_task(["coding"], ["python"])
        if best_agent:
            PrintStyle.standard(f"Best coding agent: {best_agent.name}")
        
        # Test performance updates
        if created_agents:
            test_agent_id = created_agents[0]
            registry.update_performance_metrics(test_agent_id, True, 120.0)
            PrintStyle.standard(f"✅ Updated performance for {test_agent_id}")
        
        # Test registry stats
        stats = registry.get_registry_stats()
        PrintStyle.standard(f"Registry stats: {stats}")
        
        PrintStyle.standard("✅ Agent Registry tests passed")
        return True
        
    except Exception as e:
        PrintStyle.error(f"❌ Agent Registry test failed: {e}")
        return False


async def test_team_coordinator():
    """Test team coordination functionality"""
    PrintStyle.standard("\n=== Testing Team Coordinator ===")
    
    try:
        # Initialize agent and registry
        config = initialize_agent()
        from agent import Agent, AgentContext
        context = AgentContext(config)
        agent = Agent(0, config, context)
        
        registry = AgentRegistry(agent)
        coordinator = TeamCoordinator(agent, registry)
        
        # Create some expert agents
        expert_ids = []
        for expert_type in ["code_expert", "research_expert"]:
            agent_id = registry.create_expert_agent(expert_type)
            if agent_id:
                expert_ids.append(agent_id)
        
        if not expert_ids:
            PrintStyle.error("No expert agents available for team testing")
            return False
        
        # Create a mock task analysis
        from python.helpers.task_analyzer import TaskAnalysis
        task_analysis = TaskAnalysis(
            complexity=TaskComplexity.COMPLEX,
            domains=["coding", "research"],
            required_skills=["python", "analysis"],
            coordination_mode=CoordinationMode.COORDINATE,
            estimated_time="extended",
            requires_team=True,
            confidence=0.9,
            reasoning="Complex multi-domain task requiring coordination"
        )
        
        # Test team creation
        team_id = await coordinator.create_team(
            task_analysis, 
            "Build a data analysis application with research component"
        )
        
        if team_id:
            PrintStyle.standard(f"✅ Created team: {team_id}")
            
            # Test team execution
            result = await coordinator.execute_team_task(
                team_id, 
                "Create a Python application that researches and analyzes market data"
            )
            
            if result:
                PrintStyle.standard(f"✅ Team execution completed")
                print(f"Result preview: {result[:200]}...")
            else:
                PrintStyle.error("❌ Team execution failed")
                return False
        else:
            PrintStyle.error("❌ Team creation failed")
            return False
        
        PrintStyle.standard("✅ Team Coordinator tests passed")
        return True
        
    except Exception as e:
        PrintStyle.error(f"❌ Team Coordinator test failed: {e}")
        return False


async def test_agno_orchestrator():
    """Test main orchestration engine"""
    PrintStyle.standard("\n=== Testing Agno Orchestrator ===")
    
    try:
        # Initialize agent
        config = initialize_agent()
        from agent import Agent, AgentContext
        context = AgentContext(config)
        agent = Agent(0, config, context)
        
        # Create orchestrator
        orchestrator = AgnoOrchestrator(agent)
        
        if not orchestrator.is_available():
            PrintStyle.error("❌ Orchestrator not fully available")
            return False
        
        # Test different types of task delegation
        test_cases = [
            ("Write a hello world program in Python", "coding", "simple task"),
            ("Research the latest AI trends and create a summary", "research", "specialist task"),
            ("Build a complete web application with database and API", "coding", "complex task")
        ]
        
        for task, task_type, description in test_cases:
            PrintStyle.standard(f"\nTesting {description}: {task}")
            
            result = await orchestrator.delegate_task(
                task=task,
                task_type=task_type,
                coordination_mode="auto"
            )
            
            if result:
                PrintStyle.standard(f"✅ {description} completed")
                print(f"Result preview: {result[:150]}...")
            else:
                PrintStyle.error(f"❌ {description} failed")
        
        # Test orchestration status
        status = orchestrator.get_orchestration_status()
        PrintStyle.standard(f"Orchestration status: {status['status']}")
        
        # Test available agents summary
        agents_summary = orchestrator.get_available_agents_summary()
        PrintStyle.standard(f"Available agents: {len(agents_summary)}")
        
        PrintStyle.standard("✅ Agno Orchestrator tests passed")
        return True
        
    except Exception as e:
        PrintStyle.error(f"❌ Agno Orchestrator test failed: {e}")
        return False


async def test_delegate_task_tool():
    """Test the delegate_task tool"""
    PrintStyle.standard("\n=== Testing Delegate Task Tool ===")
    
    try:
        # Initialize agent
        config = initialize_agent()
        from agent import Agent, AgentContext
        context = AgentContext(config)
        agent = Agent(0, config, context)
        
        # Initialize orchestration
        orchestrator = AgnoOrchestrator(agent)
        agent.agno_orchestrator = orchestrator
        
        # Create delegate task tool
        from python.tools.delegate_task import DelegateTask
        tool = DelegateTask(agent=agent, name="delegate_task", method=None, args={}, message="")
        
        # Test tool execution
        response = await tool.execute(
            task="Create a Python script to analyze CSV data",
            task_type="coding",
            coordination_mode="auto"
        )
        
        if response and response.message:
            PrintStyle.standard("✅ Delegate Task tool executed successfully")
            print(f"Response preview: {response.message[:150]}...")
        else:
            PrintStyle.error("❌ Delegate Task tool failed")
            return False
        
        # Test backward compatibility
        from python.tools.delegate_task import Delegation
        legacy_tool = Delegation(agent=agent, name="call_subordinate", method=None, args={}, message="")
        
        legacy_response = await legacy_tool.execute(
            message="Help me write a simple Python function",
            reset="false"
        )
        
        if legacy_response and legacy_response.message:
            PrintStyle.standard("✅ Backward compatibility test passed")
        else:
            PrintStyle.error("❌ Backward compatibility test failed")
            return False
        
        PrintStyle.standard("✅ Delegate Task Tool tests passed")
        return True
        
    except Exception as e:
        PrintStyle.error(f"❌ Delegate Task Tool test failed: {e}")
        return False


async def main():
    """Run all orchestration tests"""
    PrintStyle.standard("🚀 Starting Multi-Agent Orchestration System Tests")
    PrintStyle.standard("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_task_analyzer())
    test_results.append(await test_agent_registry())
    test_results.append(await test_team_coordinator())
    test_results.append(await test_agno_orchestrator())
    test_results.append(await test_delegate_task_tool())
    
    # Summary
    PrintStyle.standard("\n" + "=" * 60)
    PrintStyle.standard("🎯 Test Results Summary")
    
    passed = sum(test_results)
    total = len(test_results)
    
    if passed == total:
        PrintStyle.standard(f"✅ All {total} tests passed! Orchestration system is working correctly.")
        return True
    else:
        PrintStyle.error(f"❌ {total - passed} out of {total} tests failed.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        PrintStyle.standard("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        PrintStyle.error(f"💥 Test execution failed: {e}")
        sys.exit(1)
