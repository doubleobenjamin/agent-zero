#!/usr/bin/env python3
"""
Phase 1, Agent 6: Integration Testing & Validation
Main validation script for all enhanced systems

This script runs comprehensive tests and benchmarks for:
- Enhanced Memory System (Agent 1)
- Multi-Agent Orchestration (Agent 2) 
- ACI Tool Interface (Agent 3)
- Enhanced Prompt System (Agent 4)
- Configuration & Extension System (Agent 5)
- End-to-End Integration (Agent 6)
"""

import asyncio
import sys
import os
import time
from typing import Dict, List, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python.helpers.print_style import PrintStyle
from python.helpers.database_manager import get_database_manager


class IntegrationValidationSuite:
    """Main integration validation suite for Phase 1, Agent 6"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    async def check_prerequisites(self):
        """Check system prerequisites before running tests"""
        PrintStyle.standard("🔍 Checking Prerequisites...")
        
        prerequisites = {
            "databases": False,
            "python_packages": False,
            "file_structure": False
        }
        
        # Check database connectivity
        try:
            db_manager = get_database_manager()
            qdrant_healthy = await db_manager.check_qdrant_health()
            neo4j_healthy = await db_manager.check_neo4j_health()
            
            if qdrant_healthy and neo4j_healthy:
                prerequisites["databases"] = True
                PrintStyle.standard("✅ Databases: Qdrant and Neo4j are healthy")
            else:
                PrintStyle.error("❌ Databases: Some databases are not healthy")
                if not qdrant_healthy:
                    PrintStyle.error("   • Qdrant is not accessible")
                if not neo4j_healthy:
                    PrintStyle.error("   • Neo4j is not accessible")
        except Exception as e:
            PrintStyle.error(f"❌ Database check failed: {e}")
        
        # Check Python packages
        try:
            import qdrant_client
            import neo4j
            prerequisites["python_packages"] = True
            PrintStyle.standard("✅ Python packages: Core dependencies available")
        except ImportError as e:
            PrintStyle.error(f"❌ Python packages: Missing dependencies - {e}")
        
        # Check file structure
        required_files = [
            "python/helpers/enhanced_memory.py",
            "python/helpers/agno_orchestrator.py", 
            "python/helpers/aci_interface.py",
            "agent.py",
            "docker-compose.yml"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if not missing_files:
            prerequisites["file_structure"] = True
            PrintStyle.standard("✅ File structure: All required files present")
        else:
            PrintStyle.error(f"❌ File structure: Missing files - {missing_files}")
        
        # Overall prerequisite check
        all_good = all(prerequisites.values())
        if all_good:
            PrintStyle.standard("✅ All prerequisites met - proceeding with tests")
        else:
            PrintStyle.error("❌ Some prerequisites not met - tests may fail")
            PrintStyle.standard("To fix issues:")
            PrintStyle.standard("  • Start databases: docker-compose up -d")
            PrintStyle.standard("  • Install packages: pip install -r requirements.txt")
        
        return all_good, prerequisites
    
    async def run_enhanced_memory_tests(self):
        """Run enhanced memory system tests"""
        PrintStyle.standard("\n" + "="*60)
        PrintStyle.standard("🧠 ENHANCED MEMORY SYSTEM TESTS")
        PrintStyle.standard("="*60)
        
        try:
            # Import and run memory tests
            sys.path.append(os.path.join(os.path.dirname(__file__), 'enhanced'))
            from test_memory_system import run_memory_tests
            
            success = await run_memory_tests()
            self.results['memory_tests'] = {
                'success': success,
                'component': 'Enhanced Memory System (Agent 1)'
            }
            
            return success
            
        except Exception as e:
            PrintStyle.error(f"❌ Memory tests failed to run: {e}")
            self.results['memory_tests'] = {
                'success': False,
                'error': str(e),
                'component': 'Enhanced Memory System (Agent 1)'
            }
            return False
    
    async def run_orchestration_tests(self):
        """Run orchestration system tests"""
        PrintStyle.standard("\n" + "="*60)
        PrintStyle.standard("🤝 MULTI-AGENT ORCHESTRATION TESTS")
        PrintStyle.standard("="*60)
        
        try:
            # Import and run orchestration tests
            sys.path.append(os.path.join(os.path.dirname(__file__), 'enhanced'))
            from test_orchestration import run_orchestration_tests
            
            success = await run_orchestration_tests()
            self.results['orchestration_tests'] = {
                'success': success,
                'component': 'Multi-Agent Orchestration (Agent 2)'
            }
            
            return success
            
        except Exception as e:
            PrintStyle.error(f"❌ Orchestration tests failed to run: {e}")
            self.results['orchestration_tests'] = {
                'success': False,
                'error': str(e),
                'component': 'Multi-Agent Orchestration (Agent 2)'
            }
            return False
    
    async def run_tool_interface_tests(self):
        """Run ACI tool interface tests"""
        PrintStyle.standard("\n" + "="*60)
        PrintStyle.standard("🔧 ACI TOOL INTERFACE TESTS")
        PrintStyle.standard("="*60)
        
        try:
            # Import and run tool interface tests
            sys.path.append(os.path.join(os.path.dirname(__file__), 'enhanced'))
            from test_tool_interface import run_aci_tool_tests
            
            success = await run_aci_tool_tests()
            self.results['tool_interface_tests'] = {
                'success': success,
                'component': 'ACI Tool Interface (Agent 3)'
            }
            
            return success
            
        except Exception as e:
            PrintStyle.error(f"❌ Tool interface tests failed to run: {e}")
            self.results['tool_interface_tests'] = {
                'success': False,
                'error': str(e),
                'component': 'ACI Tool Interface (Agent 3)'
            }
            return False
    
    async def run_integration_tests(self):
        """Run end-to-end integration tests"""
        PrintStyle.standard("\n" + "="*60)
        PrintStyle.standard("🔄 END-TO-END INTEGRATION TESTS")
        PrintStyle.standard("="*60)
        
        try:
            # Import and run integration tests
            sys.path.append(os.path.join(os.path.dirname(__file__), 'enhanced'))
            from test_integration import run_integration_tests
            
            success = await run_integration_tests()
            self.results['integration_tests'] = {
                'success': success,
                'component': 'End-to-End Integration (Agent 6)'
            }
            
            return success
            
        except Exception as e:
            PrintStyle.error(f"❌ Integration tests failed to run: {e}")
            self.results['integration_tests'] = {
                'success': False,
                'error': str(e),
                'component': 'End-to-End Integration (Agent 6)'
            }
            return False
    
    async def run_performance_benchmarks(self):
        """Run performance benchmarks"""
        PrintStyle.standard("\n" + "="*60)
        PrintStyle.standard("⚡ PERFORMANCE BENCHMARKS")
        PrintStyle.standard("="*60)
        
        benchmark_results = {}
        
        # Memory performance benchmark
        try:
            PrintStyle.standard("\n📊 Memory Performance Benchmark...")
            sys.path.append(os.path.join(os.path.dirname(__file__), 'performance'))
            from benchmark_memory import run_memory_benchmarks
            
            memory_success = await run_memory_benchmarks()
            benchmark_results['memory'] = memory_success
            
        except Exception as e:
            PrintStyle.error(f"❌ Memory benchmark failed: {e}")
            benchmark_results['memory'] = False
        
        # Orchestration performance benchmark
        try:
            PrintStyle.standard("\n📊 Orchestration Performance Benchmark...")
            from benchmark_orchestration import run_orchestration_benchmarks
            
            orchestration_success = await run_orchestration_benchmarks()
            benchmark_results['orchestration'] = orchestration_success
            
        except Exception as e:
            PrintStyle.error(f"❌ Orchestration benchmark failed: {e}")
            benchmark_results['orchestration'] = False
        
        # Tool interface performance benchmark
        try:
            PrintStyle.standard("\n📊 Tool Interface Performance Benchmark...")
            from benchmark_tools import run_tool_benchmarks
            
            tools_success = await run_tool_benchmarks()
            benchmark_results['tools'] = tools_success
            
        except Exception as e:
            PrintStyle.error(f"❌ Tool interface benchmark failed: {e}")
            benchmark_results['tools'] = False
        
        # Overall benchmark success
        overall_success = all(benchmark_results.values())
        
        self.results['performance_benchmarks'] = {
            'success': overall_success,
            'details': benchmark_results,
            'component': 'Performance Benchmarks'
        }
        
        return overall_success
    
    def generate_final_report(self):
        """Generate comprehensive final validation report"""
        PrintStyle.standard("\n" + "="*80)
        PrintStyle.standard("🎯 PHASE 1, AGENT 6: INTEGRATION TESTING & VALIDATION REPORT")
        PrintStyle.standard("="*80)
        
        # Calculate overall statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get('success', False))
        
        # Execution time
        if self.start_time and self.end_time:
            execution_time = self.end_time - self.start_time
            PrintStyle.standard(f"\n⏱️ Total Execution Time: {execution_time:.2f} seconds")
        
        # Test results summary
        PrintStyle.standard(f"\n📊 Test Results Summary: {passed_tests}/{total_tests} test suites passed")
        
        # Detailed results
        PrintStyle.standard("\n📋 Detailed Results:")
        for test_name, result in self.results.items():
            component = result.get('component', test_name.replace('_', ' ').title())
            if result.get('success', False):
                PrintStyle.standard(f"  ✅ {component}")
            else:
                PrintStyle.error(f"  ❌ {component}")
                if 'error' in result:
                    PrintStyle.error(f"     Error: {result['error']}")
                if 'details' in result:
                    for detail_name, detail_success in result['details'].items():
                        status = "✅" if detail_success else "❌"
                        PrintStyle.standard(f"     {status} {detail_name.title()}")
        
        # Success criteria assessment
        PrintStyle.standard("\n🎯 Success Criteria Assessment:")
        
        success_criteria = {
            "Enhanced Memory System": self.results.get('memory_tests', {}).get('success', False),
            "Multi-Agent Orchestration": self.results.get('orchestration_tests', {}).get('success', False),
            "ACI Tool Interface": self.results.get('tool_interface_tests', {}).get('success', False),
            "End-to-End Integration": self.results.get('integration_tests', {}).get('success', False),
            "Performance Benchmarks": self.results.get('performance_benchmarks', {}).get('success', False)
        }
        
        for criterion, passed in success_criteria.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            PrintStyle.standard(f"  {status}: {criterion}")
        
        # Overall assessment
        overall_success = passed_tests == total_tests
        
        PrintStyle.standard("\n" + "="*80)
        if overall_success:
            PrintStyle.standard("🎉 PHASE 1, AGENT 6: INTEGRATION TESTING & VALIDATION - COMPLETE!")
            PrintStyle.standard("✅ ALL ENHANCED SYSTEMS VALIDATED AND READY FOR PRODUCTION")
            PrintStyle.standard("\n🚀 Ready for Phase 2: Integration & Optimization")
        else:
            PrintStyle.error("❌ PHASE 1, AGENT 6: INTEGRATION TESTING & VALIDATION - INCOMPLETE")
            PrintStyle.error(f"   {total_tests - passed_tests} test suite(s) failed")
            PrintStyle.standard("\n🔧 Please address the failed tests before proceeding to Phase 2")
        
        PrintStyle.standard("="*80)
        
        return overall_success
    
    async def run_full_validation(self):
        """Run complete validation suite"""
        self.start_time = time.time()
        
        PrintStyle.standard("🚀 PHASE 1, AGENT 6: INTEGRATION TESTING & VALIDATION")
        PrintStyle.standard("Starting comprehensive validation of all enhanced systems...")
        PrintStyle.standard("="*80)
        
        # Check prerequisites
        prerequisites_ok, _ = await self.check_prerequisites()
        
        if not prerequisites_ok:
            PrintStyle.error("❌ Prerequisites not met - aborting validation")
            return False
        
        # Run all test suites
        test_results = []
        
        # Enhanced Memory System Tests
        memory_success = await self.run_enhanced_memory_tests()
        test_results.append(memory_success)
        
        # Multi-Agent Orchestration Tests
        orchestration_success = await self.run_orchestration_tests()
        test_results.append(orchestration_success)
        
        # ACI Tool Interface Tests
        tool_success = await self.run_tool_interface_tests()
        test_results.append(tool_success)
        
        # End-to-End Integration Tests
        integration_success = await self.run_integration_tests()
        test_results.append(integration_success)
        
        # Performance Benchmarks
        performance_success = await self.run_performance_benchmarks()
        test_results.append(performance_success)
        
        self.end_time = time.time()
        
        # Generate final report
        overall_success = self.generate_final_report()
        
        return overall_success


async def main():
    """Main entry point for integration validation"""
    validation_suite = IntegrationValidationSuite()
    
    try:
        success = await validation_suite.run_full_validation()
        
        if success:
            PrintStyle.standard("\n🎯 VALIDATION COMPLETE: All systems validated successfully!")
            sys.exit(0)
        else:
            PrintStyle.error("\n❌ VALIDATION INCOMPLETE: Some tests failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        PrintStyle.error("\n⚠️ Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        PrintStyle.error(f"\n❌ Validation failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
