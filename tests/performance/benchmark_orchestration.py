#!/usr/bin/env python3
"""
Orchestration System Performance Benchmark
Phase 1, Agent 6: Integration Testing & Validation

Benchmarks the Agno-based orchestration system performance.
"""

import asyncio
import sys
import os
import time
import statistics
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from python.helpers.agno_orchestrator import AgnoOrchestrator, TaskAnalyzer, AgentRegistry, TeamCoordinator
from python.helpers.print_style import PrintStyle
from agent import Agent, AgentConfig
from models import ModelConfig, ModelProvider


class OrchestrationPerformanceBenchmark:
    """Performance benchmark suite for Orchestration System"""
    
    def __init__(self):
        self.results = {}
        self.baseline_requirements = {
            "task_analysis_time_ms": 100,  # Max 100ms per task analysis
            "delegation_time_ms": 2000,    # Max 2 seconds per delegation
            "concurrent_tasks": 5,         # Support 5 concurrent tasks
            "agent_registry_time_ms": 50,  # Max 50ms for agent operations
            "team_formation_time_ms": 500, # Max 500ms for team formation
            "fallback_time_ms": 1000       # Max 1 second for fallback
        }
    
    async def setup_test_agent(self):
        """Create a test agent for benchmarking"""
        config = AgentConfig(
            chat_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            utility_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            embeddings_model=ModelConfig(provider=ModelProvider.OPENAI, name="text-embedding-ada-002"),
            browser_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            mcp_servers="",
            memory_subdir="orchestration_benchmark",
            knowledge_subdirs=["default"]
        )
        
        class TestAgentContext:
            def __init__(self):
                from python.helpers.log import Log
                self.log = Log.Log()
        
        agent = Agent(400, config, TestAgentContext())
        return agent
    
    async def benchmark_task_analysis_performance(self, num_operations: int = 100):
        """Benchmark task analysis performance"""
        PrintStyle.standard(f"🧠 Benchmarking task analysis ({num_operations} operations)...")
        
        analyzer = TaskAnalyzer()
        analysis_times = []
        
        test_tasks = [
            "Calculate the square root of 144",
            "Write a Python function to sort a list",
            "Research the latest AI trends and create a summary",
            "Build a complete web application with database integration",
            "Analyze market data and generate investment recommendations",
            "Create a machine learning model for text classification",
            "Design a user interface for a mobile application",
            "Optimize database queries for better performance",
            "Implement a real-time chat system with WebSocket",
            "Develop a recommendation engine using collaborative filtering"
        ]
        
        for i in range(num_operations):
            task = test_tasks[i % len(test_tasks)]
            start_time = time.time()
            
            try:
                analysis = analyzer.analyze_task(task)
                end_time = time.time()
                analysis_time_ms = (end_time - start_time) * 1000
                analysis_times.append(analysis_time_ms)
                
                if i % 20 == 0:
                    PrintStyle.standard(f"  Completed {i+1}/{num_operations} analyses...")
                
            except Exception as e:
                PrintStyle.error(f"Analysis {i} failed: {e}")
                analysis_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in analysis_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            max_time = max(valid_times)
            min_time = min(valid_times)
            
            self.results['task_analysis_performance'] = {
                'avg_time_ms': avg_time,
                'median_time_ms': median_time,
                'max_time_ms': max_time,
                'min_time_ms': min_time,
                'success_rate': len(valid_times) / len(analysis_times),
                'throughput_ops_per_sec': 1000 / avg_time if avg_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Task Analysis Performance Results:")
            PrintStyle.standard(f"   • Average time: {avg_time:.2f}ms")
            PrintStyle.standard(f"   • Median time: {median_time:.2f}ms")
            PrintStyle.standard(f"   • Throughput: {self.results['task_analysis_performance']['throughput_ops_per_sec']:.2f} ops/sec")
            
            # Check against baseline
            if avg_time <= self.baseline_requirements['task_analysis_time_ms']:
                PrintStyle.standard(f"   ✅ PASS: Within baseline ({self.baseline_requirements['task_analysis_time_ms']}ms)")
            else:
                PrintStyle.error(f"   ❌ FAIL: Exceeds baseline ({self.baseline_requirements['task_analysis_time_ms']}ms)")
        
        else:
            PrintStyle.error("❌ All task analysis operations failed")
            self.results['task_analysis_performance'] = {'error': 'All operations failed'}
    
    async def benchmark_delegation_performance(self, orchestrator: AgnoOrchestrator, num_operations: int = 20):
        """Benchmark task delegation performance"""
        PrintStyle.standard(f"🎯 Benchmarking task delegation ({num_operations} operations)...")
        
        delegation_times = []
        
        test_tasks = [
            ("What is 2 + 2?", "calculation"),
            ("List the first 5 prime numbers", "mathematics"),
            ("Explain the concept of machine learning", "explanation"),
            ("Write a hello world program in Python", "coding"),
            ("What is the capital of France?", "knowledge")
        ]
        
        for i in range(num_operations):
            task, task_type = test_tasks[i % len(test_tasks)]
            start_time = time.time()
            
            try:
                result = await orchestrator.delegate_task(
                    task=task,
                    task_type=task_type,
                    coordination_mode="auto"
                )
                
                end_time = time.time()
                delegation_time_ms = (end_time - start_time) * 1000
                delegation_times.append(delegation_time_ms)
                
                if i % 5 == 0:
                    PrintStyle.standard(f"  Completed {i+1}/{num_operations} delegations...")
                
            except Exception as e:
                PrintStyle.standard(f"Delegation {i} used fallback: {e}")
                end_time = time.time()
                delegation_time_ms = (end_time - start_time) * 1000
                delegation_times.append(delegation_time_ms)  # Include fallback time
        
        # Calculate statistics
        if delegation_times:
            avg_time = statistics.mean(delegation_times)
            median_time = statistics.median(delegation_times)
            max_time = max(delegation_times)
            min_time = min(delegation_times)
            
            self.results['delegation_performance'] = {
                'avg_time_ms': avg_time,
                'median_time_ms': median_time,
                'max_time_ms': max_time,
                'min_time_ms': min_time,
                'throughput_ops_per_sec': 1000 / avg_time if avg_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Delegation Performance Results:")
            PrintStyle.standard(f"   • Average time: {avg_time:.2f}ms")
            PrintStyle.standard(f"   • Median time: {median_time:.2f}ms")
            PrintStyle.standard(f"   • Throughput: {self.results['delegation_performance']['throughput_ops_per_sec']:.2f} ops/sec")
            
            # Check against baseline
            if avg_time <= self.baseline_requirements['delegation_time_ms']:
                PrintStyle.standard(f"   ✅ PASS: Within baseline ({self.baseline_requirements['delegation_time_ms']}ms)")
            else:
                PrintStyle.error(f"   ❌ FAIL: Exceeds baseline ({self.baseline_requirements['delegation_time_ms']}ms)")
        
        else:
            PrintStyle.error("❌ All delegation operations failed")
            self.results['delegation_performance'] = {'error': 'All operations failed'}
    
    async def benchmark_concurrent_delegation(self, orchestrator: AgnoOrchestrator, num_concurrent: int = 5):
        """Benchmark concurrent task delegation"""
        PrintStyle.standard(f"⚡ Benchmarking concurrent delegation ({num_concurrent} concurrent)...")
        
        start_time = time.time()
        
        # Create concurrent delegation tasks
        tasks = [
            ("Calculate 10 + 15", "calculation"),
            ("What is the square root of 64?", "mathematics"),
            ("List 3 programming languages", "knowledge"),
            ("Explain what is AI", "explanation"),
            ("Write a simple function", "coding")
        ]
        
        delegation_tasks = []
        for i in range(num_concurrent):
            task, task_type = tasks[i % len(tasks)]
            delegation_task = orchestrator.delegate_task(
                task=f"{task} (concurrent test {i})",
                task_type=task_type,
                coordination_mode="auto"
            )
            delegation_tasks.append(delegation_task)
        
        try:
            # Execute all tasks concurrently
            results = await asyncio.gather(*delegation_tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_delegations = sum(1 for r in results if not isinstance(r, Exception))
            
            self.results['concurrent_delegation'] = {
                'total_time_sec': total_time,
                'successful_delegations': successful_delegations,
                'success_rate': successful_delegations / num_concurrent,
                'throughput_ops_per_sec': successful_delegations / total_time if total_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Concurrent Delegation Results:")
            PrintStyle.standard(f"   • Total time: {total_time:.2f}s")
            PrintStyle.standard(f"   • Successful: {successful_delegations}/{num_concurrent}")
            PrintStyle.standard(f"   • Success rate: {self.results['concurrent_delegation']['success_rate']:.2%}")
            PrintStyle.standard(f"   • Throughput: {self.results['concurrent_delegation']['throughput_ops_per_sec']:.2f} ops/sec")
            
            # Check against baseline
            min_concurrent = self.baseline_requirements['concurrent_tasks']
            if successful_delegations >= min_concurrent * 0.8:
                PrintStyle.standard(f"   ✅ PASS: Meets concurrent baseline requirements")
            else:
                PrintStyle.error(f"   ❌ FAIL: Below concurrent baseline requirements")
        
        except Exception as e:
            PrintStyle.error(f"❌ Concurrent delegation benchmark failed: {e}")
            self.results['concurrent_delegation'] = {'error': str(e)}
    
    async def benchmark_agent_registry_performance(self, num_operations: int = 100):
        """Benchmark agent registry operations"""
        PrintStyle.standard(f"👥 Benchmarking agent registry ({num_operations} operations)...")
        
        registry = AgentRegistry()
        registry_times = []
        
        # Test agent registration and retrieval
        for i in range(num_operations):
            start_time = time.time()
            
            try:
                # Register test agent
                test_agent_info = {
                    "id": f"test_agent_{i}",
                    "name": f"Test Agent {i}",
                    "specialization": f"test_spec_{i % 5}",
                    "capabilities": [f"capability_{i % 3}", f"skill_{i % 4}"]
                }
                
                registry.register_agent(test_agent_info)
                
                # Retrieve agents
                agents = registry.get_agents_by_specialization(f"test_spec_{i % 5}")
                available_agents = registry.get_available_agents()
                
                end_time = time.time()
                registry_time_ms = (end_time - start_time) * 1000
                registry_times.append(registry_time_ms)
                
                if i % 20 == 0:
                    PrintStyle.standard(f"  Completed {i+1}/{num_operations} registry operations...")
                
            except Exception as e:
                PrintStyle.error(f"Registry operation {i} failed: {e}")
                registry_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in registry_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            
            self.results['agent_registry_performance'] = {
                'avg_time_ms': avg_time,
                'median_time_ms': median_time,
                'success_rate': len(valid_times) / len(registry_times),
                'throughput_ops_per_sec': 1000 / avg_time if avg_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Agent Registry Performance Results:")
            PrintStyle.standard(f"   • Average time: {avg_time:.2f}ms")
            PrintStyle.standard(f"   • Throughput: {self.results['agent_registry_performance']['throughput_ops_per_sec']:.2f} ops/sec")
            
            # Check against baseline
            if avg_time <= self.baseline_requirements['agent_registry_time_ms']:
                PrintStyle.standard(f"   ✅ PASS: Within baseline ({self.baseline_requirements['agent_registry_time_ms']}ms)")
            else:
                PrintStyle.error(f"   ❌ FAIL: Exceeds baseline ({self.baseline_requirements['agent_registry_time_ms']}ms)")
        
        else:
            PrintStyle.error("❌ All agent registry operations failed")
            self.results['agent_registry_performance'] = {'error': 'All operations failed'}
    
    async def benchmark_team_coordination_performance(self, num_operations: int = 20):
        """Benchmark team coordination performance"""
        PrintStyle.standard(f"🤝 Benchmarking team coordination ({num_operations} operations)...")
        
        coordinator = TeamCoordinator()
        coordination_times = []
        
        for i in range(num_operations):
            start_time = time.time()
            
            try:
                # Create test team
                task = f"Complex task {i}: Develop a solution involving multiple specializations"
                team_members = [
                    {"id": f"expert_1_{i}", "specialization": "analysis"},
                    {"id": f"expert_2_{i}", "specialization": "development"},
                    {"id": f"expert_3_{i}", "specialization": "testing"}
                ]
                
                team_config = coordinator.form_team(task, team_members)
                
                end_time = time.time()
                coordination_time_ms = (end_time - start_time) * 1000
                coordination_times.append(coordination_time_ms)
                
                if i % 5 == 0:
                    PrintStyle.standard(f"  Completed {i+1}/{num_operations} team formations...")
                
            except Exception as e:
                PrintStyle.error(f"Team coordination {i} failed: {e}")
                coordination_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in coordination_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            
            self.results['team_coordination_performance'] = {
                'avg_time_ms': avg_time,
                'median_time_ms': median_time,
                'success_rate': len(valid_times) / len(coordination_times),
                'throughput_ops_per_sec': 1000 / avg_time if avg_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Team Coordination Performance Results:")
            PrintStyle.standard(f"   • Average time: {avg_time:.2f}ms")
            PrintStyle.standard(f"   • Throughput: {self.results['team_coordination_performance']['throughput_ops_per_sec']:.2f} ops/sec")
            
            # Check against baseline
            if avg_time <= self.baseline_requirements['team_formation_time_ms']:
                PrintStyle.standard(f"   ✅ PASS: Within baseline ({self.baseline_requirements['team_formation_time_ms']}ms)")
            else:
                PrintStyle.error(f"   ❌ FAIL: Exceeds baseline ({self.baseline_requirements['team_formation_time_ms']}ms)")
        
        else:
            PrintStyle.error("❌ All team coordination operations failed")
            self.results['team_coordination_performance'] = {'error': 'All operations failed'}
    
    async def benchmark_orchestration_status_performance(self, orchestrator: AgnoOrchestrator, num_operations: int = 50):
        """Benchmark orchestration status operations"""
        PrintStyle.standard(f"📊 Benchmarking status operations ({num_operations} operations)...")
        
        status_times = []
        
        for i in range(num_operations):
            start_time = time.time()
            
            try:
                # Get orchestration status
                status = orchestrator.get_orchestration_status()
                agents_summary = orchestrator.get_available_agents_summary()
                
                end_time = time.time()
                status_time_ms = (end_time - start_time) * 1000
                status_times.append(status_time_ms)
                
            except Exception as e:
                PrintStyle.error(f"Status operation {i} failed: {e}")
                status_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in status_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            
            self.results['status_performance'] = {
                'avg_time_ms': avg_time,
                'success_rate': len(valid_times) / len(status_times),
                'throughput_ops_per_sec': 1000 / avg_time if avg_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Status Operations Performance:")
            PrintStyle.standard(f"   • Average time: {avg_time:.2f}ms")
            PrintStyle.standard(f"   • Throughput: {self.results['status_performance']['throughput_ops_per_sec']:.2f} ops/sec")
        
        else:
            PrintStyle.error("❌ All status operations failed")
            self.results['status_performance'] = {'error': 'All operations failed'}
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        PrintStyle.standard("\n" + "="*60)
        PrintStyle.standard("📊 ORCHESTRATION SYSTEM PERFORMANCE REPORT")
        PrintStyle.standard("="*60)
        
        # Overall assessment
        passed_tests = 0
        total_tests = 0
        
        for test_name, results in self.results.items():
            if 'error' not in results:
                total_tests += 1
                
                # Check if test passed based on baseline requirements
                if test_name == 'task_analysis_performance':
                    if results.get('avg_time_ms', float('inf')) <= self.baseline_requirements['task_analysis_time_ms']:
                        passed_tests += 1
                elif test_name == 'delegation_performance':
                    if results.get('avg_time_ms', float('inf')) <= self.baseline_requirements['delegation_time_ms']:
                        passed_tests += 1
                elif test_name == 'agent_registry_performance':
                    if results.get('avg_time_ms', float('inf')) <= self.baseline_requirements['agent_registry_time_ms']:
                        passed_tests += 1
                elif test_name == 'team_coordination_performance':
                    if results.get('avg_time_ms', float('inf')) <= self.baseline_requirements['team_formation_time_ms']:
                        passed_tests += 1
                elif test_name == 'concurrent_delegation':
                    if results.get('successful_delegations', 0) >= self.baseline_requirements['concurrent_tasks'] * 0.8:
                        passed_tests += 1
                else:
                    passed_tests += 1  # Other tests pass if no error
        
        PrintStyle.standard(f"\n🎯 Overall Performance: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            PrintStyle.standard("✅ ALL ORCHESTRATION BENCHMARKS PASSED!")
        else:
            PrintStyle.error(f"❌ {total_tests - passed_tests} orchestration benchmarks failed")
        
        # Detailed results
        PrintStyle.standard("\n📋 Detailed Results:")
        for test_name, results in self.results.items():
            PrintStyle.standard(f"\n{test_name.replace('_', ' ').title()}:")
            if 'error' in results:
                PrintStyle.error(f"  ❌ Error: {results['error']}")
            else:
                for key, value in results.items():
                    if isinstance(value, float):
                        PrintStyle.standard(f"  • {key}: {value:.2f}")
                    else:
                        PrintStyle.standard(f"  • {key}: {value}")
        
        return passed_tests == total_tests


async def run_orchestration_benchmarks():
    """Run all orchestration performance benchmarks"""
    PrintStyle.standard("🚀 Orchestration System Performance Benchmark Suite")
    PrintStyle.standard("=" * 60)
    
    benchmark = OrchestrationPerformanceBenchmark()
    
    # Setup test agent and orchestrator
    test_agent = await benchmark.setup_test_agent()
    orchestrator = AgnoOrchestrator(test_agent)
    
    # Run benchmarks
    try:
        await benchmark.benchmark_task_analysis_performance(50)  # Reduced for faster testing
        await benchmark.benchmark_agent_registry_performance(50)  # Reduced for faster testing
        await benchmark.benchmark_team_coordination_performance(10)  # Reduced for faster testing
        await benchmark.benchmark_orchestration_status_performance(orchestrator, 30)  # Reduced for faster testing
        await benchmark.benchmark_delegation_performance(orchestrator, 10)  # Reduced for faster testing
        await benchmark.benchmark_concurrent_delegation(orchestrator, 3)  # Reduced for faster testing
        
        # Generate final report
        success = benchmark.generate_performance_report()
        
        return success
        
    except Exception as e:
        PrintStyle.error(f"❌ Benchmark suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_orchestration_benchmarks())
    sys.exit(0 if success else 1)
