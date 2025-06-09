"""
Cognee Entity Extraction and Knowledge Processing for Enhanced Memory System
Provides advanced knowledge processing and entity extraction
"""

from typing import List, Dict, Any, Optional
from python.helpers.print_style import PrintStyle
from agent import Agent

try:
    import cognee
    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    PrintStyle.error("Cognee not available. Install with: pip install cognee")


class CogneeProcessor:
    """Cognee processor for entity extraction and knowledge processing"""
    
    def __init__(self, agent: Agent, dataset_name: str):
        self.agent = agent
        self.dataset_name = dataset_name
        
        if not COGNEE_AVAILABLE:
            PrintStyle.error("Cognee is not available. Entity extraction features disabled.")
            return
        
        try:
            # Configure Cognee
            self._configure_cognee()
            PrintStyle.standard(f"Initialized Cognee processor for dataset: {dataset_name}")
        except Exception as e:
            PrintStyle.error(f"Failed to initialize Cognee: {e}")
    
    def _configure_cognee(self):
        """Configure Cognee with appropriate settings"""
        if not COGNEE_AVAILABLE:
            return
        
        try:
            # Set up Cognee configuration
            # Use the agent's LLM configuration for Cognee
            llm_config = {
                "provider": self.agent.config.chat_model.provider.name.lower(),
                "model": self.agent.config.chat_model.name
            }
            
            # Configure Cognee with agent's LLM
            cognee.config.set_llm_config(llm_config)
            
            # Set dataset
            cognee.config.set_dataset(self.dataset_name)
            
        except Exception as e:
            PrintStyle.error(f"Failed to configure Cognee: {e}")
    
    async def add_and_cognify(self, text: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add text to Cognee and extract entities/relationships"""
        if not COGNEE_AVAILABLE:
            return {"entities": [], "relationships": [], "summary": ""}
        
        try:
            if metadata is None:
                metadata = {}
            
            # Add text to Cognee
            await cognee.add(text, dataset_name=self.dataset_name)
            
            # Run cognification process
            result = await cognee.cognify()
            
            # Extract entities and relationships
            entities = await self._extract_entities(text)
            relationships = await self._extract_relationships(text)
            summary = await self._generate_summary(text)
            
            cognee_result = {
                "entities": entities,
                "relationships": relationships,
                "summary": summary,
                "cognee_result": result
            }
            
            PrintStyle.standard(f"Processed text with Cognee: {len(entities)} entities, {len(relationships)} relationships")
            return cognee_result
            
        except Exception as e:
            PrintStyle.error(f"Failed to process with Cognee: {e}")
            return {"entities": [], "relationships": [], "summary": ""}
    
    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities from text using Cognee"""
        if not COGNEE_AVAILABLE:
            return []
        
        try:
            # Use Cognee's entity extraction
            entities_result = await cognee.search("entities", query=text)
            
            entities = []
            if entities_result:
                for entity in entities_result:
                    entities.append({
                        "name": entity.get("name", ""),
                        "type": entity.get("type", ""),
                        "description": entity.get("description", ""),
                        "confidence": entity.get("confidence", 0.0)
                    })
            
            return entities
            
        except Exception as e:
            PrintStyle.error(f"Failed to extract entities: {e}")
            return []
    
    async def _extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """Extract relationships from text using Cognee"""
        if not COGNEE_AVAILABLE:
            return []
        
        try:
            # Use Cognee's relationship extraction
            relationships_result = await cognee.search("relationships", query=text)
            
            relationships = []
            if relationships_result:
                for rel in relationships_result:
                    relationships.append({
                        "source": rel.get("source", ""),
                        "target": rel.get("target", ""),
                        "relationship": rel.get("relationship", ""),
                        "confidence": rel.get("confidence", 0.0)
                    })
            
            return relationships
            
        except Exception as e:
            PrintStyle.error(f"Failed to extract relationships: {e}")
            return []
    
    async def _generate_summary(self, text: str) -> str:
        """Generate summary of the text using Cognee"""
        if not COGNEE_AVAILABLE:
            return ""
        
        try:
            # Use Cognee's summarization
            summary_result = await cognee.search("summary", query=text)
            
            if summary_result and len(summary_result) > 0:
                return summary_result[0].get("summary", "")
            
            return ""
            
        except Exception as e:
            PrintStyle.error(f"Failed to generate summary: {e}")
            return ""
    
    async def search_knowledge(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge using Cognee"""
        if not COGNEE_AVAILABLE:
            return []
        
        try:
            # Search using Cognee
            results = await cognee.search(query, dataset_name=self.dataset_name)
            
            # Format results
            formatted_results = []
            if results:
                for result in results[:limit]:
                    formatted_results.append({
                        "content": result.get("content", ""),
                        "score": result.get("score", 0.0),
                        "metadata": result.get("metadata", {})
                    })
            
            PrintStyle.standard(f"Found {len(formatted_results)} knowledge results for: {query}")
            return formatted_results
            
        except Exception as e:
            PrintStyle.error(f"Failed to search knowledge: {e}")
            return []
    
    async def get_dataset_stats(self) -> Dict[str, Any]:
        """Get statistics for the dataset"""
        if not COGNEE_AVAILABLE:
            return {}
        
        try:
            # Get dataset information
            stats = await cognee.get_dataset_info(self.dataset_name)
            
            if not stats:
                stats = {
                    "documents": 0,
                    "entities": 0,
                    "relationships": 0,
                    "last_updated": None
                }
            
            PrintStyle.standard(f"Dataset {self.dataset_name} stats: {stats}")
            return stats
            
        except Exception as e:
            PrintStyle.error(f"Failed to get dataset stats: {e}")
            return {}
    
    async def reset_dataset(self) -> bool:
        """Reset the dataset (clear all data)"""
        if not COGNEE_AVAILABLE:
            return False
        
        try:
            await cognee.reset_dataset(self.dataset_name)
            PrintStyle.standard(f"Reset dataset: {self.dataset_name}")
            return True
            
        except Exception as e:
            PrintStyle.error(f"Failed to reset dataset: {e}")
            return False
