#!/usr/bin/env python3
"""
Simple Validation Script for Phase 1, Agent 6
Tests core functionality without requiring all external dependencies
"""

import sys
import os
import asyncio
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_status(message, status="info"):
    """Simple status printer"""
    if status == "success":
        print(f"✅ {message}")
    elif status == "error":
        print(f"❌ {message}")
    elif status == "warning":
        print(f"⚠️ {message}")
    else:
        print(f"ℹ️ {message}")

def test_file_structure():
    """Test that all required files exist"""
    print_status("Testing file structure...")
    
    required_files = [
        # Core files
        "agent.py",
        "models.py",
        "docker-compose.yml",
        
        # Enhanced Memory System (Agent 1)
        "python/helpers/enhanced_memory.py",
        "python/helpers/database_manager.py",
        
        # Multi-Agent Orchestration (Agent 2)
        "python/helpers/agno_orchestrator.py",
        
        # ACI Tool Interface (Agent 3)
        "python/helpers/aci_interface.py",
        "python/tools/aci_discover.py",
        "python/tools/aci_status.py",
        
        # Enhanced Prompt System (Agent 4)
        "prompts/default/agent.system.main.role.md",
        "prompts/default/agent.system.tool.hybrid_memory.md",
        "prompts/default/agent.system.tool.delegate_task.md",
        
        # Test files (Agent 6)
        "tests/enhanced/test_memory_system.py",
        "tests/enhanced/test_orchestration.py",
        "tests/enhanced/test_tool_interface.py",
        "tests/enhanced/test_integration.py",
        "tests/performance/benchmark_memory.py",
        "tests/performance/benchmark_orchestration.py",
        "tests/performance/benchmark_tools.py",
        "tests/integration_validation.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print_status(f"Missing files: {missing_files}", "error")
        return False
    else:
        print_status(f"All {len(required_files)} required files present", "success")
        return True

def test_basic_imports():
    """Test basic Python imports"""
    print_status("Testing basic imports...")
    
    try:
        # Test print style
        from python.helpers.print_style import PrintStyle
        print_status("PrintStyle imported", "success")
        
        # Test database manager
        from python.helpers.database_manager import get_database_manager
        print_status("Database manager imported", "success")
        
        return True
        
    except Exception as e:
        print_status(f"Import error: {e}", "error")
        return False

def test_docker_containers():
    """Test Docker container status"""
    print_status("Testing Docker containers...")
    
    try:
        import subprocess
        
        # Check if containers are running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        
        if result.returncode == 0:
            output = result.stdout
            
            qdrant_running = 'agent-zero-qdrant' in output
            neo4j_running = 'agent-zero-neo4j' in output
            
            if qdrant_running:
                print_status("Qdrant container running", "success")
            else:
                print_status("Qdrant container not running", "warning")
            
            if neo4j_running:
                print_status("Neo4j container running", "success")
            else:
                print_status("Neo4j container not running", "warning")
            
            return qdrant_running and neo4j_running
        else:
            print_status("Docker not available", "error")
            return False
            
    except Exception as e:
        print_status(f"Docker check error: {e}", "error")
        return False

async def test_database_connectivity():
    """Test database connectivity"""
    print_status("Testing database connectivity...")
    
    try:
        # Test Qdrant
        import httpx
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://localhost:6333/health", timeout=5.0)
                if response.status_code == 200:
                    print_status("Qdrant health check passed", "success")
                    qdrant_ok = True
                else:
                    print_status(f"Qdrant health check failed: {response.status_code}", "warning")
                    qdrant_ok = False
            except Exception as e:
                print_status(f"Qdrant connection failed: {e}", "warning")
                qdrant_ok = False
            
            # Test Neo4j (simple connection test)
            try:
                response = await client.get("http://localhost:7474", timeout=5.0)
                if response.status_code in [200, 401]:  # 401 is expected without auth
                    print_status("Neo4j connection test passed", "success")
                    neo4j_ok = True
                else:
                    print_status(f"Neo4j connection test failed: {response.status_code}", "warning")
                    neo4j_ok = False
            except Exception as e:
                print_status(f"Neo4j connection failed: {e}", "warning")
                neo4j_ok = False
        
        return qdrant_ok and neo4j_ok
        
    except ImportError:
        print_status("httpx not available for connectivity test", "warning")
        return False
    except Exception as e:
        print_status(f"Database connectivity test error: {e}", "error")
        return False

def test_completion_reports():
    """Test that completion reports exist for all agents"""
    print_status("Testing completion reports...")
    
    completion_files = [
        "PHASE1_AGENT1_COMPLETE.md",
        "PHASE1_AGENT2_COMPLETE.md", 
        "PHASE1_AGENT3_COMPLETE.md",
        "docs/phase1-agent4-completion-report.md",
        "PHASE1_AGENT5_IMPLEMENTATION_SUMMARY.md"
    ]
    
    missing_reports = []
    for file_path in completion_files:
        if not os.path.exists(file_path):
            missing_reports.append(file_path)
    
    if missing_reports:
        print_status(f"Missing completion reports: {missing_reports}", "warning")
        return False
    else:
        print_status("All completion reports present", "success")
        return True

def test_prompt_system():
    """Test enhanced prompt system files"""
    print_status("Testing enhanced prompt system...")
    
    prompt_files = [
        "prompts/default/agent.system.main.role.md",
        "prompts/default/agent.system.tool.hybrid_memory.md",
        "prompts/default/agent.system.tool.delegate_task.md",
        "prompts/default/agent.system.tool.aci_tools.md",
        "prompts/default/agent.system.memories.md"
    ]
    
    missing_prompts = []
    for file_path in prompt_files:
        if not os.path.exists(file_path):
            missing_prompts.append(file_path)
    
    if missing_prompts:
        print_status(f"Missing prompt files: {missing_prompts}", "warning")
        return False
    else:
        print_status("Enhanced prompt system files present", "success")
        return True

def test_configuration_system():
    """Test configuration and extension system"""
    print_status("Testing configuration system...")
    
    config_files = [
        "python/extensions",
        "docker-compose.yml"
    ]
    
    missing_config = []
    for file_path in config_files:
        if not os.path.exists(file_path):
            missing_config.append(file_path)
    
    if missing_config:
        print_status(f"Missing configuration files: {missing_config}", "warning")
        return False
    else:
        print_status("Configuration system files present", "success")
        return True

async def run_simple_validation():
    """Run simple validation without complex dependencies"""
    print("🚀 Phase 1, Agent 6: Simple Integration Validation")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("File Structure", test_file_structure()),
        ("Basic Imports", test_basic_imports()),
        ("Docker Containers", test_docker_containers()),
        ("Database Connectivity", await test_database_connectivity()),
        ("Completion Reports", test_completion_reports()),
        ("Prompt System", test_prompt_system()),
        ("Configuration System", test_configuration_system())
    ]
    
    results = []
    for test_name, result in tests:
        results.append(result)
        if result:
            print_status(f"{test_name}: PASSED", "success")
        else:
            print_status(f"{test_name}: FAILED", "error")
    
    end_time = time.time()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 SIMPLE VALIDATION RESULTS")
    print("=" * 60)
    
    print(f"⏱️ Execution Time: {end_time - start_time:.2f} seconds")
    print(f"🎯 Tests Passed: {passed}/{total}")
    
    if passed == total:
        print_status("🎉 ALL SIMPLE VALIDATION TESTS PASSED!", "success")
        print_status("✅ Phase 1 enhanced systems are properly integrated", "success")
        print_status("🚀 Ready for comprehensive testing", "success")
        return True
    else:
        print_status(f"❌ {total - passed} tests failed", "error")
        print_status("🔧 Please address the issues before running full validation", "warning")
        return False

def main():
    """Main entry point"""
    try:
        success = asyncio.run(run_simple_validation())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("Validation interrupted by user", "warning")
        sys.exit(1)
    except Exception as e:
        print_status(f"Validation failed: {e}", "error")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
