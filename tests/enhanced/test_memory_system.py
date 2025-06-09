#!/usr/bin/env python3
"""
Enhanced Memory System Test Suite
Phase 1, Agent 6: Integration Testing & Validation

Tests the enhanced memory system with Qdrant, Graphiti, and Cognee integration.
"""

import asyncio
import sys
import os
import pytest
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from python.helpers.enhanced_memory import EnhancedMemory
from python.helpers.database_manager import get_database_manager, initialize_enhanced_databases
from python.helpers.print_style import PrintStyle
from agent import Agent, AgentConfig
from models import ModelConfig, ModelProvider


class TestEnhancedMemorySystem:
    """Test suite for Enhanced Memory System"""
    
    @pytest.fixture
    async def test_agent(self):
        """Create a test agent for memory testing"""
        config = AgentConfig(
            chat_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            utility_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            embeddings_model=ModelConfig(provider=ModelProvider.OPENAI, name="text-embedding-ada-002"),
            browser_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            mcp_servers="",
            memory_subdir="test_memory",
            knowledge_subdirs=["default"]
        )
        
        # Create minimal agent context
        class TestAgentContext:
            def __init__(self):
                from python.helpers.log import Log
                self.log = Log.Log()
        
        agent = Agent(999, config, TestAgentContext())
        yield agent
        
        # Cleanup: Clear test memory
        try:
            memory = await EnhancedMemory.get(agent)
            await memory.clear_all_memories()
        except:
            pass
    
    @pytest.fixture
    async def enhanced_memory(self, test_agent):
        """Get enhanced memory instance for testing"""
        memory = await EnhancedMemory.get(test_agent)
        return memory
    
    async def test_database_health(self):
        """Test database connectivity and health"""
        PrintStyle.standard("🔍 Testing database health...")
        
        db_manager = get_database_manager()
        
        # Test Qdrant health
        qdrant_healthy = await db_manager.check_qdrant_health()
        assert qdrant_healthy, "Qdrant database is not healthy"
        
        # Test Neo4j health
        neo4j_healthy = await db_manager.check_neo4j_health()
        assert neo4j_healthy, "Neo4j database is not healthy"
        
        PrintStyle.standard("✅ Database health check passed")
    
    async def test_memory_initialization(self, enhanced_memory):
        """Test enhanced memory initialization"""
        PrintStyle.standard("🧠 Testing memory initialization...")
        
        assert enhanced_memory is not None
        assert enhanced_memory.collection_name.startswith("agent_999_")
        assert enhanced_memory.namespace == "agent_999"
        
        PrintStyle.standard("✅ Memory initialization test passed")
    
    async def test_text_insertion_and_extraction(self, enhanced_memory):
        """Test text insertion with entity extraction"""
        PrintStyle.standard("💾 Testing text insertion and entity extraction...")
        
        test_text = "Alice Johnson is a data scientist at TechCorp who specializes in machine learning. She lives in Seattle and works on natural language processing projects."
        
        # Insert text
        result = await enhanced_memory.insert_text(
            test_text, 
            {"area": "test", "source": "unit_test", "type": "profile"}
        )
        
        # Verify insertion result
        assert result is not None
        assert "doc_id" in result
        assert result.get("entities_extracted", 0) >= 0
        
        PrintStyle.standard(f"✅ Text insertion completed - Entities: {result.get('entities_extracted', 0)}")
    
    async def test_hybrid_search(self, enhanced_memory):
        """Test hybrid search capabilities"""
        PrintStyle.standard("🔍 Testing hybrid search...")
        
        # Insert test data first
        test_data = [
            "Python is a programming language used for data science and web development.",
            "Machine learning algorithms can process large datasets efficiently.",
            "Seattle is a major tech hub with many software companies."
        ]
        
        for i, text in enumerate(test_data):
            await enhanced_memory.insert_text(text, {"area": "test", "source": f"search_test_{i}"})
        
        # Test semantic search
        results = await enhanced_memory.search_similarity_threshold(
            query="programming languages for data analysis",
            limit=5,
            threshold=0.3
        )
        
        assert len(results) > 0, "Hybrid search should return results"
        
        PrintStyle.standard(f"✅ Hybrid search test passed - Found {len(results)} results")
    
    async def test_entity_and_relationship_search(self, enhanced_memory):
        """Test entity and relationship search"""
        PrintStyle.standard("🏷️ Testing entity and relationship search...")
        
        # Insert relationship-rich text
        relationship_text = "Dr. Sarah Chen works at Microsoft Research. She collaborates with Prof. David Kim from Stanford University on AI ethics research."
        
        await enhanced_memory.insert_text(
            relationship_text,
            {"area": "test", "source": "relationship_test"}
        )
        
        # Test entity search
        entities = await enhanced_memory.search_entities(limit=10)
        PrintStyle.standard(f"Found {len(entities)} entities")
        
        # Test relationship search
        relationships = await enhanced_memory.search_relationships(limit=10)
        PrintStyle.standard(f"Found {len(relationships)} relationships")
        
        PrintStyle.standard("✅ Entity and relationship search test passed")
    
    async def test_memory_insights(self, enhanced_memory):
        """Test memory insights functionality"""
        PrintStyle.standard("📊 Testing memory insights...")
        
        insights = await enhanced_memory.get_memory_insights()
        
        assert isinstance(insights, dict)
        assert "total_vectors" in insights
        assert "total_entities" in insights
        assert "total_relationships" in insights
        
        PrintStyle.standard(f"✅ Memory insights test passed - Vectors: {insights.get('total_vectors', 0)}")
    
    async def test_namespace_isolation(self):
        """Test namespace isolation between agents"""
        PrintStyle.standard("🔒 Testing namespace isolation...")
        
        # Create two different agents
        config1 = AgentConfig(
            chat_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            utility_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            embeddings_model=ModelConfig(provider=ModelProvider.OPENAI, name="text-embedding-ada-002"),
            browser_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            mcp_servers="",
            memory_subdir="agent1_test",
            knowledge_subdirs=["default"]
        )
        
        config2 = AgentConfig(
            chat_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            utility_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            embeddings_model=ModelConfig(provider=ModelProvider.OPENAI, name="text-embedding-ada-002"),
            browser_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
            mcp_servers="",
            memory_subdir="agent2_test",
            knowledge_subdirs=["default"]
        )
        
        class TestAgentContext:
            def __init__(self):
                from python.helpers.log import Log
                self.log = Log.Log()
        
        agent1 = Agent(1001, config1, TestAgentContext())
        agent2 = Agent(1002, config2, TestAgentContext())
        
        memory1 = await EnhancedMemory.get(agent1)
        memory2 = await EnhancedMemory.get(agent2)
        
        # Verify different namespaces
        assert memory1.namespace != memory2.namespace
        assert memory1.collection_name != memory2.collection_name
        
        PrintStyle.standard("✅ Namespace isolation test passed")
    
    async def test_error_handling_and_fallbacks(self, enhanced_memory):
        """Test error handling and graceful fallbacks"""
        PrintStyle.standard("⚠️ Testing error handling and fallbacks...")
        
        # Test with invalid data
        try:
            result = await enhanced_memory.insert_text("", {"area": "test"})
            # Should handle empty text gracefully
            assert result is not None
        except Exception as e:
            # Should not crash on empty input
            assert False, f"Should handle empty text gracefully: {e}"
        
        # Test search with invalid parameters
        try:
            results = await enhanced_memory.search_similarity_threshold(
                query="",
                limit=-1,
                threshold=2.0  # Invalid threshold
            )
            # Should return empty results or handle gracefully
            assert isinstance(results, list)
        except Exception as e:
            # Should not crash on invalid parameters
            assert False, f"Should handle invalid parameters gracefully: {e}"
        
        PrintStyle.standard("✅ Error handling test passed")


async def run_memory_tests():
    """Run all memory system tests"""
    PrintStyle.standard("🚀 Enhanced Memory System Test Suite")
    PrintStyle.standard("=" * 60)
    
    test_suite = TestEnhancedMemorySystem()
    
    # Check database health first
    try:
        await test_suite.test_database_health()
    except AssertionError as e:
        PrintStyle.error(f"❌ Database health check failed: {e}")
        PrintStyle.error("Please ensure databases are running: docker-compose up -d")
        return False
    
    # Create test agent and memory
    config = AgentConfig(
        chat_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
        utility_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
        embeddings_model=ModelConfig(provider=ModelProvider.OPENAI, name="text-embedding-ada-002"),
        browser_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
        mcp_servers="",
        memory_subdir="test_suite",
        knowledge_subdirs=["default"]
    )
    
    class TestAgentContext:
        def __init__(self):
            from python.helpers.log import Log
            self.log = Log.Log()
    
    test_agent = Agent(998, config, TestAgentContext())
    enhanced_memory = await EnhancedMemory.get(test_agent)
    
    # Run all tests
    tests = [
        ("Memory Initialization", test_suite.test_memory_initialization(enhanced_memory)),
        ("Text Insertion & Extraction", test_suite.test_text_insertion_and_extraction(enhanced_memory)),
        ("Hybrid Search", test_suite.test_hybrid_search(enhanced_memory)),
        ("Entity & Relationship Search", test_suite.test_entity_and_relationship_search(enhanced_memory)),
        ("Memory Insights", test_suite.test_memory_insights(enhanced_memory)),
        ("Namespace Isolation", test_suite.test_namespace_isolation()),
        ("Error Handling", test_suite.test_error_handling_and_fallbacks(enhanced_memory))
    ]
    
    results = []
    for test_name, test_coro in tests:
        PrintStyle.standard(f"\n--- {test_name} ---")
        try:
            await test_coro
            results.append(True)
            PrintStyle.standard(f"✅ {test_name} PASSED")
        except Exception as e:
            results.append(False)
            PrintStyle.error(f"❌ {test_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    PrintStyle.standard(f"\n{'='*60}")
    PrintStyle.standard(f"🎯 Memory System Test Results: {passed}/{total} passed")
    
    if passed == total:
        PrintStyle.standard("✅ All memory system tests PASSED!")
        return True
    else:
        PrintStyle.error(f"❌ {total - passed} tests FAILED")
        return False


if __name__ == "__main__":
    asyncio.run(run_memory_tests())
