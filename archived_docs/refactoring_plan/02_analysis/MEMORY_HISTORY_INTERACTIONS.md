# Memory-History-Knowledge System Interactions Analysis

## Overview

This document details the critical interactions between the memory, history, and knowledge systems that must be preserved during the unified memory-knowledge system refactoring. The enhanced system integrates both agent conversations (memory) and external documents (knowledge) into a single Graphiti backend while maintaining full backward compatibility.

## Current Memory-History Dependencies

### 1. RecallMemories Extension

**File:** `python/extensions/message_loop_prompts_after/_50_recall_memories.py`

**History Dependencies:**
```python
# Line 34: Uses history to generate search queries
msgs_text = self.agent.concat_messages(self.agent.history)

# Line 42: Extracts recent history for query generation  
query = self.agent.concat_messages(self.agent.history, start=-RecallMemories.HISTORY)

# Line 67: Gets memory database
db = await Memory.get(self.agent)

# Line 69-74: Searches memory based on history-derived query
memories = await db.search_similarity_threshold(
    query=query,
    limit=RecallMemories.RESULTS,
    threshold=RecallMemories.THRESHOLD,
    filter=f"area == '{Memory.Area.MAIN.value}' or area == '{Memory.Area.FRAGMENTS.value}'",
)

# Line 87-90: Formats memories using page_content
for memory in memories:
    memories_text += memory.page_content + "\n\n"
```

**Critical Requirements:**
- Must preserve `memory.page_content` property access
- Must maintain same search result format
- Must preserve filter syntax for memory areas
- Must maintain `Memory.Area` enum values

### 2. MemorizeMemories Extension

**File:** `python/extensions/monologue_end/_50_memorize_fragments.py`

**History Dependencies:**
```python
# Line 34: Extracts full conversation history
msgs_text = self.agent.concat_messages(self.agent.history)

# Line 86: Gets memory database
db = await Memory.get(self.agent)

# Line 98-102: Deletes similar memories before inserting new ones
rem += await db.delete_documents_by_query(
    query=txt,
    threshold=self.REPLACE_THRESHOLD,
    filter=f"area=='{Memory.Area.FRAGMENTS.value}'",
)

# Line 104: Formats deleted documents
rem_txt = "\n\n".join(Memory.format_docs_plain(rem))

# Line 108: Inserts new memory
await db.insert_text(text=txt, metadata={"area": Memory.Area.FRAGMENTS.value})
```

**Critical Requirements:**
- Must preserve `Memory.format_docs_plain()` method
- Must maintain same delete_documents_by_query behavior
- Must preserve metadata structure with "area" field
- Must maintain Memory.Area enum compatibility

### 3. MemorizeSolutions Extension

**File:** `python/extensions/monologue_end/_51_memorize_solutions.py`

**History Dependencies:**
```python
# Line 33: Extracts conversation history for solution analysis
msgs_text = self.agent.concat_messages(self.agent.history)

# Line 104-108: Similar deletion pattern as MemorizeMemories
rem += await db.delete_documents_by_query(
    query=txt,
    threshold=self.REPLACE_THRESHOLD,
    filter=f"area=='{Memory.Area.SOLUTIONS.value}'",
)

# Line 110: Uses Memory.format_docs_plain for formatting
rem_txt = "\n\n".join(Memory.format_docs_plain(rem))

# Line 114: Inserts solution memory
await db.insert_text(text=txt, metadata={"area": Memory.Area.SOLUTIONS.value})
```

### 4. RecallSolutions Extension

**File:** `python/extensions/message_loop_prompts_after/_51_recall_solutions.py`

**History Dependencies:**
```python
# Line 42: Uses history for query generation
query = self.agent.concat_messages(self.agent.history, start=-RecallSolutions.HISTORY)

# Line 69-80: Searches both solutions and instruments
solutions = await db.search_similarity_threshold(
    query=query,
    limit=RecallSolutions.SOLUTIONS_COUNT,
    threshold=RecallSolutions.THRESHOLD,
    filter=f"area == '{Memory.Area.SOLUTIONS.value}'",
)
instruments = await db.search_similarity_threshold(
    query=query,
    limit=RecallSolutions.INSTRUMENTS_COUNT,
    threshold=RecallSolutions.THRESHOLD,
    filter=f"area == '{Memory.Area.INSTRUMENTS.value}'",
)
```

### 5. Knowledge System Integration

**Current Knowledge Flow:**
```python
# python/helpers/memory.py - Line 74-77: Knowledge preloading
if agent.config.knowledge_subdirs:
    await wrap.preload_knowledge(
        log_item, agent.config.knowledge_subdirs, memory_subdir
    )

# python/helpers/memory.py - Line 218-291: Knowledge preloading implementation
async def preload_knowledge(self, log_item, kn_dirs, memory_subdir):
    # Loads knowledge documents into same FAISS database as memory
    index = knowledge_import.load_knowledge(...)
    await self.insert_documents(index[file]["documents"])
```

**Knowledge Import API:**
```python
# python/api/import_knowledge.py - Line 32-34: Triggers memory reload
await memory.Memory.reload(context.agent0)
```

**Critical Requirements for Unified System:**
- Knowledge documents must flow through enhanced memory abstraction
- Entity extraction must be applied to knowledge documents only
- Agent conversations get simple episode storage
- Unified search across both memory and knowledge
- Preserve existing knowledge import API compatibility

## Required Compatibility Preservation

### 1. Document Format Compatibility

**Current Usage Pattern:**
```python
# Extensions expect this exact property name
memory.page_content  # NOT memory.content

# Extensions use this formatting method
Memory.format_docs_plain(documents)
```

**Abstraction Layer Requirements:**
- Return `Document` objects with `page_content` property
- Maintain `Memory.format_docs_plain()` static method
- Preserve all metadata fields exactly as they are

### 2. Memory Area Enum Compatibility

**Current Usage:**
```python
Memory.Area.MAIN.value      # "main"
Memory.Area.FRAGMENTS.value # "fragments" 
Memory.Area.SOLUTIONS.value # "solutions"
Memory.Area.INSTRUMENTS.value # "instruments"
```

**Requirements:**
- Preserve exact enum values and structure
- Maintain filter syntax: `area == '{Memory.Area.MAIN.value}'`
- Support area-based filtering in search operations

### 3. Method Signature Compatibility

**Critical Methods:**
```python
# Must maintain exact signatures
await db.insert_text(text: str, metadata: dict)
await db.search_similarity_threshold(query: str, limit: int, threshold: float, filter: str)
await db.delete_documents_by_query(query: str, threshold: float, filter: str)
await db.delete_documents_by_ids(ids: List[str])

# Must maintain static methods
Memory.format_docs_plain(docs: List[Document]) -> List[str]
await Memory.get(agent) -> Memory
```

### 4. History Access Patterns

**Current Patterns:**
```python
# These history access patterns must continue to work
self.agent.history                    # History object access
self.agent.concat_messages(self.agent.history)  # Full history concatenation
self.agent.concat_messages(self.agent.history, start=-N)  # Recent N messages
```

**Requirements:**
- History system remains completely unchanged
- All history methods continue to work exactly as before
- No changes to history data structures or APIs

## Implementation Strategy

### 1. Enhanced Abstraction Layer Design

```python
class EnhancedMemoryAbstractionLayer:
    async def insert_content(self, content: str, content_type: str, metadata: dict):
        """Unified insertion with content-type detection"""
        if content_type == "knowledge_document":
            # Use Graphiti's entity extraction for documents
            await self.backend.add_episode_with_extraction(
                content, source=EpisodeType.document, **metadata
            )
        elif content_type == "agent_memory":
            # Simple episode storage for conversations
            await self.backend.add_episode(
                content, source=EpisodeType.message, **metadata
            )

    async def search_similarity_threshold(self, query, limit, threshold, filter):
        # Backend-specific implementation with unified search
        backend_results = await self.backend.search(...)

        # Convert to Document objects for compatibility
        documents = []
        for result in backend_results:
            doc = Document(
                page_content=result.content,  # Ensure page_content property
                metadata=result.metadata
            )
            documents.append(doc)

        return documents
```

### 2. Memory Class Extension

```python
# Add to existing Memory class in python/helpers/memory.py
class Memory:
    # ... existing methods ...
    
    def __init__(self, agent, db, memory_subdir: str):
        """Add missing constructor"""
        self.agent = agent
        self.db = db
        self.memory_subdir = memory_subdir
    
    @staticmethod
    async def get_abstraction_layer(agent):
        """New method for abstraction layer access"""
        if not hasattr(agent, '_memory_abstraction'):
            agent._memory_abstraction = MemoryAbstractionLayer(agent)
            await agent._memory_abstraction.initialize()
        return agent._memory_abstraction
```

### 3. Gradual Migration Strategy

**Phase 1:** Add abstraction layer alongside existing system
**Phase 2:** Update tools to use abstraction layer
**Phase 3:** Update extensions to use abstraction layer (carefully)
**Phase 4:** Switch backend from FAISS to Graphiti
**Phase 5:** Remove old FAISS code (optional)

## Testing Requirements

### 1. Extension Compatibility Tests

```python
# Test that extensions still work with new abstraction layer
async def test_recall_memories_compatibility():
    # Verify RecallMemories extension works unchanged
    # Verify memory.page_content access works
    # Verify Memory.format_docs_plain() works
    
async def test_memorize_memories_compatibility():
    # Verify MemorizeMemories extension works unchanged
    # Verify delete_documents_by_query works
    # Verify area filtering works
```

### 2. History Integration Tests

```python
async def test_history_memory_integration():
    # Test that history -> memory query generation works
    # Test that memory search based on history works
    # Test that memory storage from history works
```

## Risk Mitigation

### 1. Backward Compatibility

- Maintain all existing method signatures
- Preserve all property names and access patterns
- Keep all enum values and structures unchanged

### 2. Incremental Testing

- Test each extension individually after changes
- Verify history access patterns remain unchanged
- Validate memory operations work exactly as before

### 3. Rollback Plan

- Keep original Memory class methods as fallback
- Maintain ability to switch back to FAISS backend
- Preserve all original functionality during transition

This analysis ensures that the memory system refactoring preserves all critical interactions with the history system while enabling the enhanced capabilities of the Graphiti temporal knowledge graph.
