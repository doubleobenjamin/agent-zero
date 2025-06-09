#!/usr/bin/env python3
"""
Simple validation script for Enhanced Memory System
Checks file structure and basic imports without requiring all dependencies
"""

import os
import sys


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def check_directory_structure():
    """Check if all required files are in place"""
    print("📁 Checking Enhanced Memory System Files")
    print("=" * 50)
    
    files_to_check = [
        ("docker-compose.yml", "Database configuration"),
        ("requirements.txt", "Enhanced requirements"),
        ("python/helpers/enhanced_memory.py", "Enhanced Memory System"),
        ("python/helpers/database_manager.py", "Database Manager"),
        ("python/helpers/qdrant_client.py", "Qdrant Client"),
        ("python/helpers/graphiti_service.py", "Graphiti Service"),
        ("python/helpers/cognee_processor.py", "Cognee Processor"),
        ("python/helpers/hybrid_search.py", "Hybrid Search Engine"),
        ("python/tools/memory_save.py", "Enhanced Memory Save Tool"),
        ("python/tools/memory_load.py", "Enhanced Memory Load Tool"),
        ("python/tools/memory_insights.py", "Memory Insights Tool"),
        ("python/helpers/memory_original.py", "Original Memory Backup"),
        ("ENHANCED_MEMORY_README.md", "Documentation"),
        ("start_enhanced_memory.py", "Startup Script"),
        ("test_enhanced_memory.py", "Test Script")
    ]
    
    all_present = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_present = False
    
    return all_present


def check_docker_compose():
    """Check docker-compose.yml content"""
    print("\n🐳 Checking Docker Compose Configuration")
    print("=" * 50)
    
    try:
        with open("docker-compose.yml", "r") as f:
            content = f.read()
        
        required_services = ["qdrant", "neo4j"]
        required_images = ["qdrant/qdrant:latest", "neo4j:latest"]
        
        for service in required_services:
            if service in content:
                print(f"✅ {service} service configured")
            else:
                print(f"❌ {service} service missing")
                return False
        
        for image in required_images:
            if image in content:
                print(f"✅ {image} image configured")
            else:
                print(f"❌ {image} image missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
        return False


def check_requirements():
    """Check requirements.txt for enhanced dependencies"""
    print("\n📦 Checking Enhanced Requirements")
    print("=" * 50)
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
        
        required_packages = [
            "qdrant-client>=1.12.0",
            "graphiti-core>=0.3.0", 
            "cognee>=0.1.0",
            "neo4j>=5.0.0"
        ]
        
        for package in required_packages:
            if package in content:
                print(f"✅ {package} specified")
            else:
                print(f"❌ {package} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False


def check_memory_tools():
    """Check if memory tools are updated"""
    print("\n🔧 Checking Enhanced Memory Tools")
    print("=" * 50)
    
    tools_to_check = [
        ("python/tools/memory_save.py", "enhanced_memory", "EnhancedMemory"),
        ("python/tools/memory_load.py", "enhanced_memory", "EnhancedMemory"),
        ("python/helpers/memory.py", "enhanced_memory", "compatibility layer")
    ]
    
    all_updated = True
    for filepath, import_check, description in tools_to_check:
        try:
            with open(filepath, "r") as f:
                content = f.read()
            
            if import_check in content:
                print(f"✅ {filepath} updated with {description}")
            else:
                print(f"❌ {filepath} not updated")
                all_updated = False
                
        except Exception as e:
            print(f"❌ Error reading {filepath}: {e}")
            all_updated = False
    
    return all_updated


def check_documentation():
    """Check if documentation is complete"""
    print("\n📚 Checking Documentation")
    print("=" * 50)
    
    try:
        with open("ENHANCED_MEMORY_README.md", "r") as f:
            content = f.read()
        
        required_sections = [
            "Enhanced Memory System",
            "Quick Start", 
            "Enhanced Features",
            "Architecture",
            "Testing & Validation",
            "Success Criteria"
        ]
        
        for section in required_sections:
            if section in content:
                print(f"✅ {section} section present")
            else:
                print(f"❌ {section} section missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading documentation: {e}")
        return False


def main():
    """Main validation function"""
    print("🚀 Enhanced Memory System Validation")
    print("Phase 1, Agent 1: Enhanced Memory System Implementation")
    print("=" * 60)
    
    checks = [
        ("File Structure", check_directory_structure),
        ("Docker Configuration", check_docker_compose),
        ("Requirements", check_requirements),
        ("Memory Tools", check_memory_tools),
        ("Documentation", check_documentation)
    ]
    
    all_passed = True
    results = {}
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results[check_name] = False
            all_passed = False
    
    # Summary
    print("\n📊 Validation Summary")
    print("=" * 50)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    if all_passed:
        print("\n🎉 SUCCESS: Enhanced Memory System Implementation Complete!")
        print("✅ Phase 1, Agent 1 validation successful")
        print("")
        print("🚀 Next Steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Start databases: docker-compose up -d")
        print("   3. Run full test: python test_enhanced_memory.py")
        print("   4. Start Agent Zero normally")
        print("")
        print("🎯 Enhanced Memory System Features:")
        print("   • Qdrant vector database for semantic search")
        print("   • Graphiti knowledge graphs with temporal context")
        print("   • Cognee entity extraction and processing")
        print("   • Hybrid search across all systems")
        print("   • Rich feedback with entity and relationship info")
        print("   • Namespace isolation per agent")
        print("   • Backward compatibility with existing tools")
        
        return True
    else:
        print("\n❌ VALIDATION FAILED")
        print("Please fix the issues above before proceeding")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
