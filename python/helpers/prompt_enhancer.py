"""
Enhanced Prompt System for Agent Zero
Provides context-aware prompt generation with orchestration, memory, and tool context.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class PromptEnhancer:
    """
    Context-aware prompt enhancement system that injects dynamic variables
    based on current system state and capabilities.
    """
    
    def __init__(self, agent):
        self.agent = agent
        
    def get_enhanced_variables(self, loop_data=None) -> Dict[str, Any]:
        """
        Generate enhanced template variables for prompt system.
        
        Returns:
            Dict containing all enhanced variables for template substitution
        """
        variables = {}
        
        # Add orchestration context
        variables.update(self._get_orchestration_variables())
        
        # Add memory insights
        variables.update(self._get_memory_variables())
        
        # Add tool context
        variables.update(self._get_tool_variables())
        
        # Add multi-modal context
        variables.update(self._get_multimodal_variables(loop_data))
        
        # Add system capabilities
        variables.update(self._get_system_capabilities())
        
        return variables
    
    def _get_orchestration_variables(self) -> Dict[str, Any]:
        """Get orchestration-related template variables."""
        # TODO: This will be populated when orchestration system is implemented
        # For now, return placeholder structure
        return {
            "orchestration_status": {
                "mode": "standalone",
                "team_size": 1,
                "stage": "ready"
            },
            "available_agents": [],
            "team_status": [],
            "agent_performance": []
        }
    
    def _get_memory_variables(self) -> Dict[str, Any]:
        """Get memory-related template variables."""
        # TODO: This will be populated when hybrid memory system is implemented
        # For now, return placeholder structure
        return {
            "recalled_memories": "",
            "extracted_entities": "",
            "relationship_insights": "",
            "temporal_context": "",
            "multimodal_analysis": "",
            "knowledge_graph": "",
            "memory_namespace": "default",
            "memory_insights": ""  # Added missing variable
        }
    
    def _get_tool_variables(self) -> Dict[str, Any]:
        """Get tool-related template variables."""
        # TODO: This will be populated when ACI integration is implemented
        # For now, return placeholder structure
        return {
            "available_tools": [],
            "tool_categories": [],
            "authentication_status": "pending",
            "tool_recommendations": [],
            "execution_status": "ready"
        }
    
    def _get_multimodal_variables(self, loop_data=None) -> Dict[str, Any]:
        """Get multi-modal processing variables."""
        variables = {}
        
        if loop_data and hasattr(loop_data, 'user_message'):
            user_msg = loop_data.user_message
            if hasattr(user_msg, 'attachments') and user_msg.attachments:
                variables["has_attachments"] = True
                variables["attachment_count"] = len(user_msg.attachments)
                variables["attachment_types"] = self._analyze_attachment_types(user_msg.attachments)
            else:
                variables["has_attachments"] = False
                variables["attachment_count"] = 0
                variables["attachment_types"] = []
        
        return variables
    
    def _get_system_capabilities(self) -> Dict[str, Any]:
        """Get current system capabilities and feature status."""
        return {
            "system_capabilities": {
                "hybrid_memory": False,  # Will be True when implemented
                "orchestration": False,  # Will be True when implemented
                "aci_tools": False,      # Will be True when implemented
                "multimodal": True       # Basic multimodal support exists
            },
            "processing_insights": "",
            "optimization_suggestions": "",
            "collaboration_context": ""
        }
    
    def _analyze_attachment_types(self, attachments: List[str]) -> List[str]:
        """Analyze attachment types for multi-modal context."""
        types = []
        for attachment in attachments:
            if attachment.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                types.append('image')
            elif attachment.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                types.append('video')
            elif attachment.lower().endswith(('.mp3', '.wav', '.flac', '.ogg')):
                types.append('audio')
            elif attachment.lower().endswith(('.pdf', '.doc', '.docx', '.txt')):
                types.append('document')
            elif attachment.lower().endswith(('.py', '.js', '.html', '.css', '.json')):
                types.append('code')
            else:
                types.append('file')
        return list(set(types))  # Remove duplicates
    
    def enhance_prompt_content(self, content: str, **additional_vars) -> str:
        """
        Enhance prompt content with conditional sections based on capabilities.
        
        Args:
            content: Original prompt content
            **additional_vars: Additional variables to include
            
        Returns:
            Enhanced prompt content with conditional sections
        """
        # Get all enhanced variables
        variables = self.get_enhanced_variables()
        variables.update(additional_vars)
        
        # Add conditional content based on capabilities
        enhanced_content = content
        
        # Add orchestration context if available
        if variables.get("available_agents"):
            enhanced_content += "\n\n## Available Specialist Agents\n"
            for agent in variables["available_agents"]:
                enhanced_content += f"- {agent.get('name', 'Unknown')}: {agent.get('capabilities', 'General')}\n"
        
        # Add memory insights if available
        if variables.get("recalled_memories"):
            enhanced_content += "\n\n## Relevant Memory Context\n"
            enhanced_content += variables["recalled_memories"]
        
        # Add multi-modal context if attachments present
        if variables.get("has_attachments"):
            enhanced_content += f"\n\n## Multi-modal Context\n"
            enhanced_content += f"Attachments detected: {variables['attachment_count']} files\n"
            enhanced_content += f"Types: {', '.join(variables['attachment_types'])}\n"
        
        return enhanced_content


def get_prompt_enhancer(agent):
    """Factory function to get a PromptEnhancer instance."""
    return PromptEnhancer(agent)
