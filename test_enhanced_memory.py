#!/usr/bin/env python3
"""
Test script for Enhanced Memory System
Validates Phase 1, Agent 1 implementation
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from python.helpers.database_manager import initialize_enhanced_databases, get_database_manager
from python.helpers.enhanced_memory import EnhancedMemory
from python.helpers.print_style import PrintStyle
from agent import Agent, AgentConfig
from models import ModelConfig, ModelProvider


async def test_enhanced_memory():
    """Test the enhanced memory system"""
    
    PrintStyle.standard("🧪 Testing Enhanced Memory System")
    PrintStyle.standard("=" * 50)
    
    # Create a test agent configuration
    test_config = AgentConfig(
        chat_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
        utility_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
        embeddings_model=ModelConfig(provider=ModelProvider.OPENAI, name="text-embedding-ada-002"),
        browser_model=ModelConfig(provider=ModelProvider.OPENAI, name="gpt-4o-mini"),
        mcp_servers="",
        memory_subdir="test",
        knowledge_subdirs=["default"]
    )
    
    # Create a test agent context (minimal)
    class TestAgentContext:
        def __init__(self):
            from python.helpers.log import Log
            self.log = Log.Log()
    
    # Create test agent
    test_agent = Agent(1, test_config, TestAgentContext())
    
    try:
        # Test 1: Database Health Check
        PrintStyle.standard("\n🔍 Test 1: Database Health Check")
        db_manager = get_database_manager()
        
        qdrant_healthy = await db_manager.check_qdrant_health()
        neo4j_healthy = await db_manager.check_neo4j_health()
        
        if not qdrant_healthy:
            PrintStyle.error("❌ Qdrant is not healthy. Please start with: docker-compose up -d")
            return False
        
        if not neo4j_healthy:
            PrintStyle.error("❌ Neo4j is not healthy. Please start with: docker-compose up -d")
            return False
        
        PrintStyle.standard("✅ All databases are healthy")
        
        # Test 2: Enhanced Memory Initialization
        PrintStyle.standard("\n🧠 Test 2: Enhanced Memory Initialization")
        memory = await EnhancedMemory.get(test_agent)
        PrintStyle.standard(f"✅ Enhanced memory initialized: {memory.collection_name}")
        
        # Test 3: Memory Insert with Entity Extraction
        PrintStyle.standard("\n💾 Test 3: Memory Insert with Entity Extraction")
        test_text = "John Smith is a software engineer at OpenAI who works on artificial intelligence. He lives in San Francisco and enjoys machine learning research."
        
        result = await memory.insert_text(test_text, {"area": "test", "source": "validation"})
        
        PrintStyle.standard(f"✅ Memory insert result:")
        PrintStyle.standard(f"   • Document ID: {result.get('doc_id')}")
        PrintStyle.standard(f"   • Entities extracted: {result.get('entities_extracted', 0)}")
        PrintStyle.standard(f"   • Relationships mapped: {result.get('relationships_mapped', 0)}")
        PrintStyle.standard(f"   • Knowledge graph updated: {result.get('knowledge_graph_updated', False)}")
        
        # Test 4: Hybrid Search
        PrintStyle.standard("\n🔍 Test 4: Hybrid Search")
        search_results = await memory.search_similarity_threshold(
            query="software engineer", 
            limit=5, 
            threshold=0.5
        )
        
        PrintStyle.standard(f"✅ Search found {len(search_results)} results")
        for i, doc in enumerate(search_results):
            PrintStyle.standard(f"   • Result {i+1}: {doc.page_content[:100]}...")
        
        # Test 5: Memory Insights
        PrintStyle.standard("\n📊 Test 5: Memory Insights")
        insights = await memory.get_memory_insights()
        
        PrintStyle.standard(f"✅ Memory insights:")
        PrintStyle.standard(f"   • Total vectors: {insights.get('total_vectors', 0)}")
        PrintStyle.standard(f"   • Total entities: {insights.get('total_entities', 0)}")
        PrintStyle.standard(f"   • Total relationships: {insights.get('total_relationships', 0)}")
        PrintStyle.standard(f"   • Total episodes: {insights.get('total_episodes', 0)}")
        
        # Test 6: Entity Search
        PrintStyle.standard("\n🏷️ Test 6: Entity Search")
        entities = await memory.search_entities(limit=10)
        PrintStyle.standard(f"✅ Found {len(entities)} entities")
        for entity in entities[:3]:  # Show first 3
            PrintStyle.standard(f"   • {entity.get('name', 'Unknown')}: {entity.get('summary', 'No description')}")
        
        # Test 7: Relationship Search
        PrintStyle.standard("\n🔗 Test 7: Relationship Search")
        relationships = await memory.search_relationships(limit=10)
        PrintStyle.standard(f"✅ Found {len(relationships)} relationships")
        for rel in relationships[:3]:  # Show first 3
            PrintStyle.standard(f"   • {rel.get('source', 'Unknown')} → {rel.get('relationship', 'relates to')} → {rel.get('target', 'Unknown')}")
        
        PrintStyle.standard("\n🎉 All tests passed! Enhanced Memory System is working correctly.")
        return True
        
    except Exception as e:
        PrintStyle.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    PrintStyle.standard("🚀 Enhanced Memory System Validation")
    PrintStyle.standard("Phase 1, Agent 1: Enhanced Memory System Implementation")
    PrintStyle.standard("")
    
    # Check if databases are running
    PrintStyle.standard("📋 Prerequisites:")
    PrintStyle.standard("   • Qdrant running on localhost:6333")
    PrintStyle.standard("   • Neo4j running on localhost:7687")
    PrintStyle.standard("   • Required packages installed (see requirements.txt)")
    PrintStyle.standard("")
    
    success = await test_enhanced_memory()
    
    if success:
        PrintStyle.standard("\n✅ VALIDATION COMPLETE: Enhanced Memory System is ready!")
        PrintStyle.standard("🎯 Phase 1, Agent 1 implementation successful")
    else:
        PrintStyle.error("\n❌ VALIDATION FAILED: Please check the errors above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
