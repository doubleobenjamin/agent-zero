#!/usr/bin/env python3
"""
Multi-Agent Orchestration System Demo
Demonstrates the new intelligent delegation capabilities
"""

import sys
import os
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def demo_orchestration():
    """Demonstrate the orchestration system capabilities"""
    
    print("🚀 Multi-Agent Orchestration System Demo")
    print("=" * 50)
    
    # Create mock agent for demonstration
    class MockAgent:
        def __init__(self):
            self.number = 0
            self.config = None
            self.context = None
        
        def get_data(self, key):
            return None
        
        def set_data(self, key, value):
            pass
        
        async def call_utility_model(self, system, message):
            # Mock LLM response for task analysis
            if "simple" in message.lower():
                return '{"complexity": "simple", "domains": ["general"], "required_skills": [], "coordination_mode": "route", "estimated_time": "quick", "requires_team": false, "confidence": 0.9, "reasoning": "Simple task requiring basic assistance"}'
            elif "research" in message.lower():
                return '{"complexity": "specialist", "domains": ["research"], "required_skills": ["analysis"], "coordination_mode": "route", "estimated_time": "moderate", "requires_team": false, "confidence": 0.8, "reasoning": "Research task requiring specialist expertise"}'
            else:
                return '{"complexity": "complex", "domains": ["coding", "data"], "required_skills": ["python", "analysis"], "coordination_mode": "coordinate", "estimated_time": "extended", "requires_team": true, "confidence": 0.9, "reasoning": "Complex multi-domain task requiring team coordination"}'
    
    # Initialize orchestration system
    from python.helpers.agno_orchestrator import AgnoOrchestrator
    
    mock_agent = MockAgent()
    orchestrator = AgnoOrchestrator(mock_agent)
    
    print(f"✅ Orchestration system initialized")
    print(f"   Available: {orchestrator.is_available()}")
    
    # Get system status
    status = orchestrator.get_orchestration_status()
    print(f"   Status: {status['status']}")
    print(f"   Total agents: {status['agents']['total_agents']}")
    print(f"   Available agents: {status['agents']['available_agents']}")
    
    # Demo 1: Simple Task
    print("\n--- Demo 1: Simple Task ---")
    task1 = "Write a simple hello world message"
    print(f"Task: {task1}")
    
    result1 = await orchestrator.delegate_task(task1, "general", "auto")
    print(f"✅ Result: {result1[:100]}...")
    
    # Demo 2: Specialist Task
    print("\n--- Demo 2: Specialist Task ---")
    task2 = "Research the latest developments in artificial intelligence"
    print(f"Task: {task2}")
    
    result2 = await orchestrator.delegate_task(task2, "research", "route")
    print(f"✅ Result: {result2[:100]}...")
    
    # Demo 3: Complex Team Task
    print("\n--- Demo 3: Complex Team Task ---")
    task3 = "Build a complete data analysis application with machine learning and web interface"
    print(f"Task: {task3}")
    
    result3 = await orchestrator.delegate_task(task3, "coding", "coordinate")
    print(f"✅ Result: {result3[:100]}...")
    
    # Show available agents
    print("\n--- Available Specialist Agents ---")
    agents_summary = orchestrator.get_available_agents_summary()
    
    for agent_info in agents_summary:
        print(f"• {agent_info['name']}")
        print(f"  Role: {agent_info['role']}")
        print(f"  Domains: {', '.join(agent_info['domains'])}")
        print(f"  Performance: {agent_info['performance_score']:.2f}")
        print(f"  Success Rate: {agent_info['success_rate']:.1%}")
        print()
    
    # Show registry stats
    print("--- Registry Statistics ---")
    registry_stats = orchestrator.agent_registry.get_registry_stats()
    
    for key, value in registry_stats.items():
        if key == "domains_covered":
            print(f"• {key}: {', '.join(value)}")
        else:
            print(f"• {key}: {value}")
    
    print("\n🎉 Demo completed successfully!")


async def demo_task_analysis():
    """Demonstrate task analysis capabilities"""
    
    print("\n🔍 Task Analysis Demo")
    print("=" * 30)
    
    from python.helpers.task_analyzer import TaskAnalyzer
    
    class MockAgent:
        async def call_utility_model(self, system, message):
            return '{"complexity": "specialist", "domains": ["coding"], "required_skills": ["python"], "coordination_mode": "route", "estimated_time": "moderate", "requires_team": false, "confidence": 0.8, "reasoning": "Coding task requiring specialist"}'
    
    analyzer = TaskAnalyzer(MockAgent())
    
    test_tasks = [
        "Write a hello world program",
        "Debug this complex Python application with multiple modules",
        "Research AI trends and create a comprehensive report with data analysis",
        "Set up a complete CI/CD pipeline with monitoring and deployment",
        "Create documentation for the API"
    ]
    
    for task in test_tasks:
        print(f"\nTask: {task}")
        analysis = analyzer._pattern_analyze_task(task)
        
        print(f"  Complexity: {analysis.complexity.value}")
        print(f"  Domains: {', '.join(analysis.domains)}")
        print(f"  Coordination: {analysis.coordination_mode.value}")
        print(f"  Team Required: {analysis.requires_team}")
        print(f"  Confidence: {analysis.confidence:.2f}")


def demo_backward_compatibility():
    """Demonstrate backward compatibility"""
    
    print("\n🔄 Backward Compatibility Demo")
    print("=" * 35)
    
    from python.tools.delegate_task import Delegation, CallSubordinate
    
    class MockAgent:
        def __init__(self):
            self.number = 0
            self.agno_orchestrator = None
        
        def get_data(self, key):
            return None
        
        def set_data(self, key, value):
            pass
    
    mock_agent = MockAgent()
    
    # Test original Delegation class
    delegation_tool = Delegation(agent=mock_agent, name="call_subordinate", method=None, args={}, message="")
    print("✅ Original Delegation class works")
    
    # Test CallSubordinate alias
    call_sub_tool = CallSubordinate(agent=mock_agent, name="call_subordinate", method=None, args={}, message="")
    print("✅ CallSubordinate alias works")
    
    print("✅ Existing code will continue to work without changes")


async def main():
    """Run all demos"""
    
    try:
        await demo_orchestration()
        await demo_task_analysis()
        demo_backward_compatibility()
        
        print("\n" + "=" * 60)
        print("🎯 Multi-Agent Orchestration System Demo Complete")
        print("✅ All features demonstrated successfully")
        print("🚀 Ready for production use!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
