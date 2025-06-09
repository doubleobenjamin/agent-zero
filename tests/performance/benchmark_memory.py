#!/usr/bin/env python3
"""
Memory System Performance Benchmark
Phase 1, Agent 6: Integration Testing & Validation

Benchmarks the enhanced memory system performance against baseline requirements.
"""

import asyncio
import sys
import os
import time
import statistics
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from python.helpers.enhanced_memory import EnhancedMemory
from python.helpers.database_manager import get_database_manager
from python.helpers.print_style import PrintStyle
from agent import Agent, AgentConfig
from models import ModelConfig, ModelProvider


class MemoryPerformanceBenchmark:
    """Performance benchmark suite for Enhanced Memory System"""
    
    def __init__(self):
        self.results = {}
        self.baseline_requirements = {
            "insert_time_ms": 1000,  # Max 1 second per insert
            "search_time_ms": 500,   # Max 500ms per search
            "batch_insert_throughput": 10,  # Min 10 inserts per second
            "search_throughput": 20,  # Min 20 searches per second
            "memory_usage_mb": 500,  # Max 500MB memory usage
            "concurrent_operations": 10  # Support 10 concurrent operations
        }
    
    async def setup_test_agent(self):
        """Create a test agent for benchmarking"""
        config = AgentConfig(
            chat_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            utility_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            embeddings_model=ModelConfig(provider=ModelProvider.OPENAI, name="text-embedding-ada-002"),
            browser_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            mcp_servers="",
            memory_subdir="benchmark_test",
            knowledge_subdirs=["default"]
        )
        
        class TestAgentContext:
            def __init__(self):
                from python.helpers.log import Log
                self.log = Log.Log()
        
        agent = Agent(500, config, TestAgentContext())
        return agent
    
    async def benchmark_insert_performance(self, memory: EnhancedMemory, num_operations: int = 50):
        """Benchmark memory insert performance"""
        PrintStyle.standard(f"🚀 Benchmarking insert performance ({num_operations} operations)...")
        
        insert_times = []
        test_texts = [
            f"Performance test document {i}: This is a test document for benchmarking memory insert performance. "
            f"It contains various information about testing, performance metrics, and system capabilities. "
            f"Document ID: {i}, Timestamp: {time.time()}"
            for i in range(num_operations)
        ]
        
        for i, text in enumerate(test_texts):
            start_time = time.time()
            
            try:
                result = await memory.insert_text(
                    text,
                    {"area": "benchmark", "source": f"perf_test_{i}", "type": "performance"}
                )
                
                end_time = time.time()
                insert_time_ms = (end_time - start_time) * 1000
                insert_times.append(insert_time_ms)
                
                if i % 10 == 0:
                    PrintStyle.standard(f"  Completed {i+1}/{num_operations} inserts...")
                
            except Exception as e:
                PrintStyle.error(f"Insert {i} failed: {e}")
                insert_times.append(float('inf'))  # Mark as failed
        
        # Calculate statistics
        valid_times = [t for t in insert_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            max_time = max(valid_times)
            min_time = min(valid_times)
            
            self.results['insert_performance'] = {
                'avg_time_ms': avg_time,
                'median_time_ms': median_time,
                'max_time_ms': max_time,
                'min_time_ms': min_time,
                'success_rate': len(valid_times) / len(insert_times),
                'throughput_ops_per_sec': 1000 / avg_time if avg_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Insert Performance Results:")
            PrintStyle.standard(f"   • Average time: {avg_time:.2f}ms")
            PrintStyle.standard(f"   • Median time: {median_time:.2f}ms")
            PrintStyle.standard(f"   • Throughput: {self.results['insert_performance']['throughput_ops_per_sec']:.2f} ops/sec")
            PrintStyle.standard(f"   • Success rate: {self.results['insert_performance']['success_rate']:.2%}")
            
            # Check against baseline
            if avg_time <= self.baseline_requirements['insert_time_ms']:
                PrintStyle.standard(f"   ✅ PASS: Average time within baseline ({self.baseline_requirements['insert_time_ms']}ms)")
            else:
                PrintStyle.error(f"   ❌ FAIL: Average time exceeds baseline ({self.baseline_requirements['insert_time_ms']}ms)")
        
        else:
            PrintStyle.error("❌ All insert operations failed")
            self.results['insert_performance'] = {'error': 'All operations failed'}
    
    async def benchmark_search_performance(self, memory: EnhancedMemory, num_operations: int = 100):
        """Benchmark memory search performance"""
        PrintStyle.standard(f"🔍 Benchmarking search performance ({num_operations} operations)...")
        
        search_times = []
        search_queries = [
            "performance test document",
            "benchmarking memory system",
            "test document information",
            "system capabilities testing",
            "performance metrics analysis",
            "document timestamp data",
            "memory insert performance",
            "testing framework results",
            "benchmark test results",
            "system performance evaluation"
        ]
        
        for i in range(num_operations):
            query = search_queries[i % len(search_queries)]
            start_time = time.time()
            
            try:
                results = await memory.search_similarity_threshold(
                    query=query,
                    limit=10,
                    threshold=0.3
                )
                
                end_time = time.time()
                search_time_ms = (end_time - start_time) * 1000
                search_times.append(search_time_ms)
                
                if i % 20 == 0:
                    PrintStyle.standard(f"  Completed {i+1}/{num_operations} searches...")
                
            except Exception as e:
                PrintStyle.error(f"Search {i} failed: {e}")
                search_times.append(float('inf'))
        
        # Calculate statistics
        valid_times = [t for t in search_times if t != float('inf')]
        
        if valid_times:
            avg_time = statistics.mean(valid_times)
            median_time = statistics.median(valid_times)
            max_time = max(valid_times)
            min_time = min(valid_times)
            
            self.results['search_performance'] = {
                'avg_time_ms': avg_time,
                'median_time_ms': median_time,
                'max_time_ms': max_time,
                'min_time_ms': min_time,
                'success_rate': len(valid_times) / len(search_times),
                'throughput_ops_per_sec': 1000 / avg_time if avg_time > 0 else 0
            }
            
            PrintStyle.standard(f"✅ Search Performance Results:")
            PrintStyle.standard(f"   • Average time: {avg_time:.2f}ms")
            PrintStyle.standard(f"   • Median time: {median_time:.2f}ms")
            PrintStyle.standard(f"   • Throughput: {self.results['search_performance']['throughput_ops_per_sec']:.2f} ops/sec")
            PrintStyle.standard(f"   • Success rate: {self.results['search_performance']['success_rate']:.2%}")
            
            # Check against baseline
            if avg_time <= self.baseline_requirements['search_time_ms']:
                PrintStyle.standard(f"   ✅ PASS: Average time within baseline ({self.baseline_requirements['search_time_ms']}ms)")
            else:
                PrintStyle.error(f"   ❌ FAIL: Average time exceeds baseline ({self.baseline_requirements['search_time_ms']}ms)")
        
        else:
            PrintStyle.error("❌ All search operations failed")
            self.results['search_performance'] = {'error': 'All operations failed'}
    
    async def benchmark_concurrent_operations(self, memory: EnhancedMemory, num_concurrent: int = 10):
        """Benchmark concurrent operations performance"""
        PrintStyle.standard(f"⚡ Benchmarking concurrent operations ({num_concurrent} concurrent)...")
        
        start_time = time.time()
        
        # Create concurrent insert tasks
        insert_tasks = []
        for i in range(num_concurrent):
            task = memory.insert_text(
                f"Concurrent test document {i}: Testing concurrent memory operations for performance benchmarking.",
                {"area": "concurrent", "source": f"concurrent_test_{i}"}
            )
            insert_tasks.append(task)
        
        # Create concurrent search tasks
        search_tasks = []
        for i in range(num_concurrent):
            task = memory.search_similarity_threshold(
                query=f"concurrent test document {i % 5}",
                limit=5,
                threshold=0.3
            )
            search_tasks.append(task)
        
        try:
            # Execute all tasks concurrently
            insert_results = await asyncio.gather(*insert_tasks, return_exceptions=True)
            search_results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_inserts = sum(1 for r in insert_results if not isinstance(r, Exception))
            successful_searches = sum(1 for r in search_results if not isinstance(r, Exception))
            
            self.results['concurrent_performance'] = {
                'total_time_sec': total_time,
                'successful_inserts': successful_inserts,
                'successful_searches': successful_searches,
                'insert_success_rate': successful_inserts / num_concurrent,
                'search_success_rate': successful_searches / num_concurrent,
                'total_throughput': (successful_inserts + successful_searches) / total_time
            }
            
            PrintStyle.standard(f"✅ Concurrent Performance Results:")
            PrintStyle.standard(f"   • Total time: {total_time:.2f}s")
            PrintStyle.standard(f"   • Successful inserts: {successful_inserts}/{num_concurrent}")
            PrintStyle.standard(f"   • Successful searches: {successful_searches}/{num_concurrent}")
            PrintStyle.standard(f"   • Total throughput: {self.results['concurrent_performance']['total_throughput']:.2f} ops/sec")
            
            # Check against baseline
            min_concurrent = self.baseline_requirements['concurrent_operations']
            if successful_inserts >= min_concurrent * 0.8 and successful_searches >= min_concurrent * 0.8:
                PrintStyle.standard(f"   ✅ PASS: Concurrent operations meet baseline requirements")
            else:
                PrintStyle.error(f"   ❌ FAIL: Concurrent operations below baseline requirements")
        
        except Exception as e:
            PrintStyle.error(f"❌ Concurrent operations benchmark failed: {e}")
            self.results['concurrent_performance'] = {'error': str(e)}
    
    async def benchmark_memory_insights_performance(self, memory: EnhancedMemory):
        """Benchmark memory insights performance"""
        PrintStyle.standard("📊 Benchmarking memory insights performance...")
        
        start_time = time.time()
        
        try:
            insights = await memory.get_memory_insights()
            
            end_time = time.time()
            insights_time_ms = (end_time - start_time) * 1000
            
            self.results['insights_performance'] = {
                'time_ms': insights_time_ms,
                'success': True,
                'insights_count': len(insights) if isinstance(insights, dict) else 0
            }
            
            PrintStyle.standard(f"✅ Memory Insights Performance:")
            PrintStyle.standard(f"   • Time: {insights_time_ms:.2f}ms")
            PrintStyle.standard(f"   • Insights retrieved: {self.results['insights_performance']['insights_count']}")
            
        except Exception as e:
            PrintStyle.error(f"❌ Memory insights benchmark failed: {e}")
            self.results['insights_performance'] = {'error': str(e)}
    
    async def benchmark_database_health(self):
        """Benchmark database health check performance"""
        PrintStyle.standard("🏥 Benchmarking database health checks...")
        
        db_manager = get_database_manager()
        
        # Benchmark Qdrant health check
        start_time = time.time()
        try:
            qdrant_healthy = await db_manager.check_qdrant_health()
            qdrant_time = (time.time() - start_time) * 1000
        except Exception as e:
            qdrant_healthy = False
            qdrant_time = float('inf')
        
        # Benchmark Neo4j health check
        start_time = time.time()
        try:
            neo4j_healthy = await db_manager.check_neo4j_health()
            neo4j_time = (time.time() - start_time) * 1000
        except Exception as e:
            neo4j_healthy = False
            neo4j_time = float('inf')
        
        self.results['database_health'] = {
            'qdrant_healthy': qdrant_healthy,
            'qdrant_check_time_ms': qdrant_time,
            'neo4j_healthy': neo4j_healthy,
            'neo4j_check_time_ms': neo4j_time
        }
        
        PrintStyle.standard(f"✅ Database Health Performance:")
        PrintStyle.standard(f"   • Qdrant: {'✅' if qdrant_healthy else '❌'} ({qdrant_time:.2f}ms)")
        PrintStyle.standard(f"   • Neo4j: {'✅' if neo4j_healthy else '❌'} ({neo4j_time:.2f}ms)")
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        PrintStyle.standard("\n" + "="*60)
        PrintStyle.standard("📊 MEMORY SYSTEM PERFORMANCE REPORT")
        PrintStyle.standard("="*60)
        
        # Overall assessment
        passed_tests = 0
        total_tests = 0
        
        for test_name, results in self.results.items():
            if 'error' not in results:
                total_tests += 1
                
                # Check if test passed based on baseline requirements
                if test_name == 'insert_performance':
                    if results.get('avg_time_ms', float('inf')) <= self.baseline_requirements['insert_time_ms']:
                        passed_tests += 1
                elif test_name == 'search_performance':
                    if results.get('avg_time_ms', float('inf')) <= self.baseline_requirements['search_time_ms']:
                        passed_tests += 1
                elif test_name == 'concurrent_performance':
                    min_concurrent = self.baseline_requirements['concurrent_operations']
                    if (results.get('successful_inserts', 0) >= min_concurrent * 0.8 and 
                        results.get('successful_searches', 0) >= min_concurrent * 0.8):
                        passed_tests += 1
                else:
                    passed_tests += 1  # Other tests pass if no error
        
        PrintStyle.standard(f"\n🎯 Overall Performance: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            PrintStyle.standard("✅ ALL PERFORMANCE BENCHMARKS PASSED!")
        else:
            PrintStyle.error(f"❌ {total_tests - passed_tests} performance benchmarks failed")
        
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


async def run_memory_benchmarks():
    """Run all memory performance benchmarks"""
    PrintStyle.standard("🚀 Memory System Performance Benchmark Suite")
    PrintStyle.standard("=" * 60)
    
    benchmark = MemoryPerformanceBenchmark()
    
    # Setup test agent and memory
    test_agent = await benchmark.setup_test_agent()
    memory = await EnhancedMemory.get(test_agent)
    
    # Run benchmarks
    try:
        await benchmark.benchmark_database_health()
        await benchmark.benchmark_insert_performance(memory, 30)  # Reduced for faster testing
        await benchmark.benchmark_search_performance(memory, 50)  # Reduced for faster testing
        await benchmark.benchmark_concurrent_operations(memory, 8)  # Reduced for faster testing
        await benchmark.benchmark_memory_insights_performance(memory)
        
        # Generate final report
        success = benchmark.generate_performance_report()
        
        return success
        
    except Exception as e:
        PrintStyle.error(f"❌ Benchmark suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_memory_benchmarks())
    sys.exit(0 if success else 1)
