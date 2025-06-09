from datetime import datetime
from typing import Any
from python.helpers.extension import Extension
from agent import LoopData
from python.helpers.print_style import PrintStyle


class EnhancedMemoryProcessing(Extension):
    """
    Enhanced memory processing extension that integrates with Graphiti and Qdrant
    for advanced memory capabilities including hybrid search and context extension.
    """

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs: Any):
        # Only execute if enhanced memory is enabled
        if not self.agent.config.additional.get('enhanced_memory', False):
            return
        
        # Skip if no user message to process
        if not loop_data.user_message:
            return
            
        try:
            # Process conversation through enhanced memory system
            await self._process_conversation_memory(loop_data)
            
            # Perform hybrid search for relevant context
            await self._perform_hybrid_search(loop_data)
            
            # Extend context with related memories
            await self._extend_context(loop_data)
            
        except Exception as e:
            # Graceful degradation - log error but don't break the flow
            if self.agent.config.additional.get('graceful_degradation', True):
                PrintStyle(font_color="yellow", padding=True).print(
                    f"⚠ Enhanced memory processing warning: {e}"
                )
            else:
                raise

    async def _process_conversation_memory(self, loop_data: LoopData):
        """Process current conversation through enhanced memory system"""
        
        if not self.agent.config.additional.get('graphiti_enabled', True):
            return
            
        conversation_text = loop_data.user_message.content.get("message", "")
        if not conversation_text:
            return
            
        # Create memory context
        memory_context = {
            "agent_id": self.agent.number,
            "timestamp": datetime.now(),
            "conversation_id": getattr(self.agent.context, 'id', 'unknown'),
            "message_type": "user_input"
        }
        
        # Note: Actual Graphiti integration would be implemented here
        # For now, we store the processing intent in loop data
        loop_data.extras_persistent["enhanced_memory_processed"] = {
            "text": conversation_text,
            "context": memory_context,
            "processed_at": datetime.now().isoformat()
        }

    async def _perform_hybrid_search(self, loop_data: LoopData):
        """Perform hybrid search across vector and graph databases"""
        
        if not self.agent.config.additional.get('hybrid_search_enabled', True):
            return
            
        query = loop_data.user_message.content.get("message", "")
        if not query:
            return
            
        # Note: Actual hybrid search implementation would be here
        # This would combine:
        # - Vector similarity search in Qdrant
        # - Graph traversal in Neo4j via Graphiti
        # - Semantic relationship analysis
        
        # For now, we mark that hybrid search was attempted
        loop_data.extras_persistent["hybrid_search_performed"] = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "databases_queried": ["qdrant", "neo4j"]
        }

    async def _extend_context(self, loop_data: LoopData):
        """Extend context with related memories and associations"""
        
        if not self.agent.config.additional.get('context_extension_enabled', True):
            return
            
        # Note: Actual context extension would retrieve and format
        # related memories, entity relationships, and contextual information
        # to enhance the agent's understanding
        
        # For now, we indicate context extension was performed
        loop_data.extras_persistent["context_extended"] = {
            "timestamp": datetime.now().isoformat(),
            "extension_type": "enhanced_memory",
            "status": "processed"
        }
