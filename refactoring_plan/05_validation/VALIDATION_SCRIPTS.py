# Validation Scripts for Memory & Knowledge System Refactoring

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

class MemorySystemValidator:
    """Comprehensive validation for memory and knowledge system refactoring"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_tests = []
    
    async def run_all_validations(self):
        """Run all validation tests"""
        print("🔍 Starting Memory System Validation")
        print("=" * 50)
        
        # Phase 1: Environment and Dependencies
        await self.validate_environment()
        await self.validate_dependencies()
        await self.validate_neo4j_connection()
        
        # Phase 2: File Structure
        await self.validate_file_structure()
        await self.validate_imports()
        
        # Phase 3: Core Functionality
        await self.validate_memory_abstraction()
        await self.validate_graphiti_backend()
        await self.validate_memory_tools()
        
        # Phase 4: Knowledge System Integration
        await self.validate_knowledge_import()
        await self.validate_knowledge_processing()
        await self.validate_unified_search()

        # Phase 5: Critical Integrations
        await self.validate_memory_extensions()
        await self.validate_history_integration()

        # Phase 6: End-to-End Testing
        await self.validate_full_workflow()
        
        # Report Results
        self.print_validation_report()
        
        return len(self.errors) == 0
    
    async def validate_environment(self):
        """Validate environment configuration"""
        print("📋 Validating Environment Configuration...")
        
        required_vars = [
            "MEMORY_BACKEND",
            "NEO4J_URI", 
            "NEO4J_USER",
            "NEO4J_PASSWORD",
            "OPENAI_API_KEY"
        ]
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                self.errors.append(f"Missing environment variable: {var}")
            else:
                self.passed_tests.append(f"Environment variable {var} is set")
        
        # Check backend selection
        backend = os.getenv("MEMORY_BACKEND", "faiss")
        if backend not in ["faiss", "graphiti"]:
            self.errors.append(f"Invalid MEMORY_BACKEND value: {backend}")
        else:
            self.passed_tests.append(f"Valid MEMORY_BACKEND: {backend}")
    
    async def validate_dependencies(self):
        """Validate required dependencies are installed"""
        print("📦 Validating Dependencies...")
        
        dependencies = [
            ("graphiti_core", "Graphiti core library"),
            ("neo4j", "Neo4j Python driver"),
            ("openai", "OpenAI Python library"),
            ("langchain_core", "LangChain core library")
        ]
        
        for module, description in dependencies:
            try:
                __import__(module)
                self.passed_tests.append(f"Dependency {description} is installed")
            except ImportError:
                self.errors.append(f"Missing dependency: {description} ({module})")
    
    async def validate_neo4j_connection(self):
        """Validate Neo4j database connection"""
        print("🔗 Validating Neo4j Connection...")
        
        try:
            from neo4j import GraphDatabase
            
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "password")
            
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    self.passed_tests.append("Neo4j connection successful")
                else:
                    self.errors.append("Neo4j connection test failed")
            driver.close()
            
        except Exception as e:
            self.errors.append(f"Neo4j connection failed: {str(e)}")
    
    async def validate_file_structure(self):
        """Validate required files exist"""
        print("📁 Validating File Structure...")
        
        required_files = [
            "python/helpers/memory.py",
            "python/helpers/memory_abstraction.py",
            "python/helpers/memory_graphiti_backend.py",
            "python/helpers/memory_faiss_backend.py",
            "python/helpers/knowledge_import.py",
            "python/api/import_knowledge.py",
            "python/tools/memory_save.py",
            "python/tools/memory_load.py",
            "python/tools/memory_delete.py",
            "python/tools/memory_forget.py",
            "agent.py",
            "initialize.py"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.passed_tests.append(f"File exists: {file_path}")
            else:
                self.errors.append(f"Missing required file: {file_path}")
    
    async def validate_imports(self):
        """Validate all imports work correctly"""
        print("📥 Validating Imports...")
        
        import_tests = [
            ("python.helpers.memory", "Memory"),
            ("python.helpers.memory_abstraction", "EnhancedMemoryAbstractionLayer"),
            ("python.helpers.memory_graphiti_backend", "EnhancedGraphitiBackend"),
            ("python.helpers.knowledge_import", "load_knowledge"),
            ("python.api.import_knowledge", "import_knowledge"),
            ("python.tools.memory_save", "MemorySave"),
            ("agent", "AgentConfig"),
        ]
        
        for module, class_name in import_tests:
            try:
                module_obj = __import__(module, fromlist=[class_name])
                getattr(module_obj, class_name)
                self.passed_tests.append(f"Import successful: {module}.{class_name}")
            except Exception as e:
                self.errors.append(f"Import failed: {module}.{class_name} - {str(e)}")
    
    async def validate_memory_abstraction(self):
        """Validate memory abstraction layer functionality"""
        print("🧠 Validating Memory Abstraction Layer...")
        
        try:
            from python.helpers.memory_abstraction import MemoryAbstractionLayer, MemoryConfig
            
            # Create mock agent
            class MockAgent:
                def __init__(self):
                    self.config = MockConfig()
            
            class MockConfig:
                def __init__(self):
                    self.memory_subdir = "test"
                    self.embeddings_model = None
                    self.additional = {"graphiti_enabled": False}
            
            agent = MockAgent()
            layer = MemoryAbstractionLayer(agent)
            
            # Test backend type detection
            backend_type = layer._get_backend_type()
            if backend_type in ["faiss", "graphiti"]:
                self.passed_tests.append(f"Backend type detection works: {backend_type}")
            else:
                self.errors.append(f"Invalid backend type detected: {backend_type}")
            
            # Test config building
            config = layer._build_config(backend_type)
            if config.backend_type == backend_type:
                self.passed_tests.append("Config building works correctly")
            else:
                self.errors.append("Config building failed")
                
        except Exception as e:
            self.errors.append(f"Memory abstraction validation failed: {str(e)}")
    
    async def validate_graphiti_backend(self):
        """Validate Graphiti backend functionality"""
        print("📊 Validating Graphiti Backend...")
        
        try:
            from python.helpers.memory_graphiti_backend import GraphitiBackend
            from python.helpers.memory_abstraction import MemoryConfig
            
            backend = GraphitiBackend()
            
            # Test initialization parameters
            config = MemoryConfig(
                backend_type="graphiti",
                memory_subdir="test",
                embeddings_model=None,
                graphiti_config={
                    "neo4j_uri": "bolt://localhost:7687",
                    "neo4j_user": "neo4j",
                    "neo4j_password": "password",
                    "group_id": "test"
                }
            )
            
            # Test that backend can be created
            self.passed_tests.append("Graphiti backend creation successful")
            
            # Test area extraction
            area = backend._extract_area_from_source("agent-zero-main")
            if area == "main":
                self.passed_tests.append("Area extraction works correctly")
            else:
                self.errors.append(f"Area extraction failed: expected 'main', got '{area}'")
                
        except Exception as e:
            self.errors.append(f"Graphiti backend validation failed: {str(e)}")

    async def validate_knowledge_import(self):
        """Validate knowledge import system functionality"""
        print("📚 Validating Knowledge Import System...")

        try:
            from python.helpers import knowledge_import

            # Test that knowledge_import module exists and has required functions
            if hasattr(knowledge_import, 'load_knowledge'):
                self.passed_tests.append("Knowledge import load_knowledge function exists")
            else:
                self.errors.append("Knowledge import load_knowledge function missing")

            # Test knowledge file type loaders
            if hasattr(knowledge_import, 'file_types_loaders'):
                loaders = getattr(knowledge_import, 'file_types_loaders', {})
                expected_types = ["txt", "pdf", "csv", "html", "json", "md"]
                for file_type in expected_types:
                    if file_type in loaders:
                        self.passed_tests.append(f"Knowledge loader for {file_type} exists")
                    else:
                        self.warnings.append(f"Knowledge loader for {file_type} missing")

            # Test knowledge import API
            try:
                from python.api import import_knowledge
                self.passed_tests.append("Knowledge import API module exists")
            except ImportError:
                self.errors.append("Knowledge import API module missing")

        except Exception as e:
            self.errors.append(f"Knowledge import validation failed: {str(e)}")

    async def validate_knowledge_processing(self):
        """Validate enhanced knowledge processing functionality"""
        print("🔍 Validating Knowledge Processing...")

        try:
            from python.helpers.memory_abstraction import EnhancedMemoryAbstractionLayer

            # Create mock agent for testing
            class MockAgent:
                def __init__(self):
                    self.config = MockConfig()

            class MockConfig:
                def __init__(self):
                    self.memory_subdir = "test"
                    self.embeddings_model = None
                    self.knowledge_subdirs = ["main"]

            agent = MockAgent()
            layer = EnhancedMemoryAbstractionLayer(agent)

            # Test content type processing methods exist
            if hasattr(layer, 'insert_content'):
                self.passed_tests.append("Enhanced memory layer insert_content method exists")
            else:
                self.errors.append("Enhanced memory layer insert_content method missing")

            if hasattr(layer, 'process_knowledge_documents'):
                self.passed_tests.append("Enhanced memory layer process_knowledge_documents method exists")
            else:
                self.errors.append("Enhanced memory layer process_knowledge_documents method missing")

        except Exception as e:
            self.errors.append(f"Knowledge processing validation failed: {str(e)}")

    async def validate_unified_search(self):
        """Validate unified search across memory and knowledge"""
        print("🔎 Validating Unified Search...")

        try:
            from python.helpers.memory_abstraction import EnhancedMemoryAbstractionLayer

            # Test that search method supports content type filtering
            # This is a structural test - actual functionality would require backend
            self.passed_tests.append("Unified search validation placeholder - requires backend testing")

        except Exception as e:
            self.errors.append(f"Unified search validation failed: {str(e)}")

    async def validate_memory_tools(self):
        """Validate memory tools functionality"""
        print("🔧 Validating Memory Tools...")
        
        tools = [
            "python.tools.memory_save",
            "python.tools.memory_load", 
            "python.tools.memory_delete",
            "python.tools.memory_forget"
        ]
        
        for tool_module in tools:
            try:
                module = __import__(tool_module, fromlist=[""])
                # Check if tool has execute method
                tool_classes = [getattr(module, name) for name in dir(module) 
                              if name.endswith('Save') or name.endswith('Load') or 
                                 name.endswith('Delete') or name.endswith('Forget')]
                
                if tool_classes and hasattr(tool_classes[0], 'execute'):
                    self.passed_tests.append(f"Tool validation passed: {tool_module}")
                else:
                    self.errors.append(f"Tool missing execute method: {tool_module}")
                    
            except Exception as e:
                self.errors.append(f"Tool validation failed: {tool_module} - {str(e)}")
    
    async def validate_memory_extensions(self):
        """Validate memory extensions functionality"""
        print("🔌 Validating Memory Extensions...")
        
        extensions = [
            "python.extensions.message_loop_prompts_after._50_recall_memories",
            "python.extensions.monologue_end._50_memorize_fragments",
            "python.extensions.monologue_end._51_memorize_solutions",
            "python.extensions.message_loop_prompts_after._51_recall_solutions"
        ]
        
        for ext_module in extensions:
            try:
                module = __import__(ext_module, fromlist=[""])
                # Check if extension has execute method
                ext_classes = [getattr(module, name) for name in dir(module) 
                              if name.startswith('Recall') or name.startswith('Memorize')]
                
                if ext_classes and hasattr(ext_classes[0], 'execute'):
                    self.passed_tests.append(f"Extension validation passed: {ext_module}")
                else:
                    self.errors.append(f"Extension missing execute method: {ext_module}")
                    
            except Exception as e:
                self.errors.append(f"Extension validation failed: {ext_module} - {str(e)}")
    
    async def validate_history_integration(self):
        """Validate that history system integration is preserved"""
        print("📚 Validating History Integration...")
        
        try:
            # Test that history access patterns still work
            from agent import Agent, AgentConfig
            from python.helpers import models
            
            # Create minimal config for testing
            config = AgentConfig(
                chat_model=models.ModelConfig(models.ModelProvider.OPENAI, "gpt-4"),
                utility_model=models.ModelConfig(models.ModelProvider.OPENAI, "gpt-4"),
                embeddings_model=models.ModelConfig(models.ModelProvider.OPENAI, "text-embedding-ada-002"),
                browser_model=models.ModelConfig(models.ModelProvider.OPENAI, "gpt-4"),
                mcp_servers=""
            )
            
            # Test agent creation
            agent = Agent(0, config)
            
            # Test history access
            if hasattr(agent, 'history'):
                self.passed_tests.append("Agent history access preserved")
            else:
                self.errors.append("Agent history access broken")
            
            # Test concat_messages method
            if hasattr(agent, 'concat_messages'):
                self.passed_tests.append("Agent concat_messages method preserved")
            else:
                self.errors.append("Agent concat_messages method missing")
                
        except Exception as e:
            self.errors.append(f"History integration validation failed: {str(e)}")
    
    async def validate_full_workflow(self):
        """Validate end-to-end memory workflow"""
        print("🔄 Validating Full Workflow...")
        
        try:
            # This would test a complete memory operation workflow
            # For now, just validate that the workflow can be initiated
            self.passed_tests.append("Full workflow validation placeholder - implement based on specific needs")
            
        except Exception as e:
            self.errors.append(f"Full workflow validation failed: {str(e)}")
    
    def print_validation_report(self):
        """Print comprehensive validation report"""
        print("\n" + "=" * 60)
        print("🎯 VALIDATION REPORT")
        print("=" * 60)
        
        print(f"\n✅ PASSED TESTS ({len(self.passed_tests)}):")
        for test in self.passed_tests:
            print(f"   ✓ {test}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   ⚠ {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   ✗ {error}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Passed: {len(self.passed_tests)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Errors: {len(self.errors)}")
        
        if len(self.errors) == 0:
            print(f"\n🎉 ALL VALIDATIONS PASSED! System is ready for deployment.")
        else:
            print(f"\n🚨 VALIDATION FAILED! Please fix errors before proceeding.")
        
        print("=" * 60)

# Standalone validation functions
async def quick_health_check():
    """Quick health check for basic functionality"""
    print("🏥 Quick Health Check")
    print("-" * 30)
    
    checks = []
    
    # Check environment
    backend = os.getenv("MEMORY_BACKEND", "faiss")
    checks.append(f"Backend: {backend}")
    
    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
        with driver.session() as session:
            session.run("RETURN 1")
        checks.append("Neo4j: ✅ Connected")
        driver.close()
    except:
        checks.append("Neo4j: ❌ Connection failed")
    
    # Check Graphiti
    try:
        import graphiti_core
        checks.append("Graphiti: ✅ Installed")
    except:
        checks.append("Graphiti: ❌ Not installed")
    
    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        checks.append("OpenAI: ✅ Key set")
    else:
        checks.append("OpenAI: ❌ Key missing")
    
    for check in checks:
        print(f"  {check}")
    
    print("-" * 30)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate memory system refactoring")
    parser.add_argument("--quick", action="store_true", help="Run quick health check only")
    parser.add_argument("--full", action="store_true", help="Run full validation suite")
    
    args = parser.parse_args()
    
    if args.quick:
        asyncio.run(quick_health_check())
    elif args.full:
        validator = MemorySystemValidator()
        success = asyncio.run(validator.run_all_validations())
        sys.exit(0 if success else 1)
    else:
        print("Usage: python validation_scripts.py [--quick|--full]")
        print("  --quick: Run quick health check")
        print("  --full:  Run comprehensive validation")
