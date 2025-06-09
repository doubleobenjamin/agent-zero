# Enhanced Memory System - Compatibility Layer
# This file provides backward compatibility while using the enhanced memory system

from python.helpers.enhanced_memory import EnhancedMemory
from python.helpers.print_style import PrintStyle
from agent import Agent

# Re-export for compatibility
Memory = EnhancedMemory

# Compatibility functions
def get_memory_subdir_abs(agent: Agent) -> str:
    """Get absolute path to memory subdirectory"""
    from python.helpers import files
    return files.get_abs_path("memory", agent.config.memory_subdir or "default")

def get_custom_knowledge_subdir_abs(agent: Agent) -> str:
    """Get absolute path to custom knowledge subdirectory"""
    from python.helpers import files
    for dir in agent.config.knowledge_subdirs:
        if dir != "default":
            return files.get_abs_path("knowledge", dir)
    raise Exception("No custom knowledge subdir set")

def reload():
    """Clear the memory index to force reload"""
    EnhancedMemory.index = {}

# Print notification about enhanced memory system
PrintStyle.standard("🚀 Enhanced Memory System Active: Qdrant + Graphiti + Cognee")


