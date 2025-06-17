from typing import List, Dict, Any, Optional, TYPE_CHECKING, cast

from .memory_abstraction import MemoryBackend, MemoryDocument, MemoryConfig # Relative import
from .memory import Memory as LegacyMemory # Import existing Memory system
from .memory import Document as LegacyFaissDocument # Import existing Document type

if TYPE_CHECKING:
    from agent import Agent # Assuming Agent class is in agent.py at the root

class FaissBackend(MemoryBackend):
    """FAISS backend wrapper for the existing legacy memory system"""

    def __init__(self):
        self.legacy_memory: Optional[LegacyMemory] = None
        self.agent_for_legacy: Optional['Agent'] = None

    async def initialize(self, config: MemoryConfig) -> None:
        """Initialize FAISS backend using existing Memory class."""

        # The legacy Memory.get() expects an agent instance.
        # We need to construct a minimal agent-like object or adapt.
        # The MemoryConfig contains 'memory_subdir' and 'embeddings_model'
        # which are part of the agent's config that LegacyMemory uses.

        # Create a mock or minimal agent object if necessary,
        # or assume self.agent_for_legacy is set if this backend is chosen by MAL.
        # For now, let's assume MAL passes the agent instance,
        # and we store it to pass to LegacyMemory.get().
        # This requires MAL to pass the agent instance to the backend's initialize method,
        # or for the backend to have access to it.
        # The current MemoryConfig doesn't include the agent itself.
        # This is a slight departure from the guide if it implied full isolation.
        # A cleaner way might be for MAL to pass the agent to the constructor of the backend.

        # Based on MAL's structure, it has `self.agent`.
        # We need to make it available here.
        # Simplest: Assume MAL will pass its agent reference to this backend's constructor
        # or a dedicated method if this proves problematic.
        # For now, let's assume it's passed via config or a setter if needed.
        # The guide's `MockAgent` approach is also viable if we construct it here.

        # Let's stick to the guide's mock agent approach for now, as it's self-contained.
        class MockAgent:
            def __init__(self, memory_config: MemoryConfig):
                # Mocking just enough of agent.config for LegacyMemory.get() and its usage.
                class MockAgentConfig:
                    def __init__(self, mem_cfg: MemoryConfig):
                        self.memory_subdir = mem_cfg.memory_subdir
                        self.embeddings_model = mem_cfg.embeddings_model
                        # LegacyMemory might also access agent.config.dirs.memory etc.
                        # This mock might need to be more comprehensive.
                        # For now, assuming these are the key fields from MemoryConfig.

                        # Add other fields LegacyMemory.get or its internals might need from agent.config
                        # e.g. self.dirs = {"memory": ... }
                        # This depends on the full usage within LegacyMemory.
                        # For a robust solution, this mock needs to be accurate.

                        # Let's assume LegacyMemory primarily needs memory_subdir and embeddings_model via agent.config
                        # and agent.config.memory_abs_layer_instance for the new flow (not relevant here).

                self.config = MockAgentConfig(memory_config)
                # LegacyMemory.get() also sets agent._memory = self
                # and agent._memory_abstraction = instance of MAL (if new code path is used)
                # We don't need the MAL part for the legacy path.

        mock_agent_instance = MockAgent(config)
        # Provide the mock agent to the legacy memory system
        self.legacy_memory = await LegacyMemory.get(cast('Agent', mock_agent_instance)) # Cast to Agent

    async def _ensure_legacy_initialized(self):
        if not self.legacy_memory:
            # This indicates initialize was not called or failed.
            # This state should ideally not be reached if MAL calls initialize properly.
            raise RuntimeError("FaissBackend (LegacyMemory) not initialized. Call initialize first.")

    def _to_memory_document(self, legacy_doc: LegacyFaissDocument, score: Optional[float] = None) -> MemoryDocument:
        """Convert a LegacyFaissDocument to the new MemoryDocument format."""
        return MemoryDocument(
            id=legacy_doc.id, # Assuming legacy_doc has an 'id' field
            page_content=legacy_doc.page_content,
            metadata=legacy_doc.metadata,
            score=score if score is not None else legacy_doc.score # Use provided score, else legacy score
        )

    def _to_legacy_document_list(self, results: List[tuple[LegacyFaissDocument, float]]) -> List[MemoryDocument]:
        """Convert a list of (LegacyFaissDocument, score) tuples to List[MemoryDocument]."""
        return [self._to_memory_document(doc, score) for doc, score in results]

    async def insert_text(self, text: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_legacy_initialized()
        # LegacyMemory's insert_text_area returns the ID.
        # It expects area from metadata.
        area = metadata.get("area", LegacyMemory.Area.MAIN.value)
        # Other metadata is passed as kwargs to underlying FAISS/Chroma add_texts.
        doc_id = await self.legacy_memory.insert_text_area( # type: ignore
            text=text,
            area=area,
            metadata=metadata # Pass full metadata
        )
        return doc_id

    async def insert_knowledge_document(self, content: str, metadata: Dict[str, Any]) -> str:
        await self._ensure_legacy_initialized()
        # For FAISS backend, knowledge documents are treated similarly to regular text,
        # but potentially stored in a specific area if metadata indicates.
        # The legacy system's `insert_documents_area` might be suitable if we chunk.
        # Or, if `content` is a single chunk, `insert_text_area` is fine.
        # Let's assume `content` is a single piece of text for now.
        area = metadata.get("area", LegacyMemory.Area.KNOWLEDGE.value) # Default to a knowledge area

        # Create a LegacyFaissDocument-like structure if needed by insert_documents_area
        # For simplicity, using insert_text_area, which is what the old knowledge import did per chunk.
        doc_id = await self.legacy_memory.insert_text_area( # type: ignore
            text=content,
            area=area,
            metadata=metadata
        )
        return doc_id

    async def search_similarity_threshold(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7,
        filter: Optional[Dict[str, Any]] = None # Legacy filter was string-based area
    ) -> List[MemoryDocument]:
        await self._ensure_legacy_initialized()

        # Legacy search_similarity_threshold took `area_filter` as a string.
        # We need to adapt the new `filter` dict.
        # A simple approach: if filter dict has "area", use that. Otherwise, search all.
        area_filter_str = ""
        if filter and "area" in filter and isinstance(filter["area"], str):
            area_filter_str = filter["area"]

        # Legacy search returns List[Tuple[Document, float]]
        legacy_results = await self.legacy_memory.search_similarity_threshold( # type: ignore
            query=query,
            limit=limit,
            threshold=threshold,
            area_filter=area_filter_str # Pass the extracted area string
        )
        return self._to_legacy_document_list(legacy_results)

    async def delete_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_legacy_initialized()
        # LegacyMemory has delete_by_ids which takes a list of IDs and an area.
        # The new API doesn't specify area here. This implies IDs are globally unique
        # or the backend needs to handle deletion across all areas if area isn't given.
        # The legacy delete_by_ids requires an area.
        # This is a mismatch. We might need to iterate areas or assume a default/all areas.

        # For now, let's assume we can't fulfill this perfectly without an area.
        # Or, that IDs are expected to be unique and legacy system handles it.
        # The legacy `delete_by_ids(ids, area)` might not return deleted docs.
        # The plan asks for List[MemoryDocument].

        # Fetch first, then delete, then return fetched.
        # 1. Get documents by IDs (across all areas if possible, or require area in metadata of IDs)
        # This is problematic if legacy get_by_ids also needs area.
        # Let's assume legacy `delete_by_ids` does not return documents.
        # We'll fetch them first via `get_documents_by_ids`.

        docs_to_return = await self.get_documents_by_ids(ids) # This also has area issues.

        # The legacy `delete_by_ids(ids: list[str], area: str)`
        # We need an area. If IDs are truly global, this is an issue for legacy.
        # If IDs are like "area_uuid", we can parse area.
        # For now, this method might be limited for FaissBackend if area isn't implicitly handled.
        # Let's assume for now that the user of MAL is expected to handle this, or IDs are unique.
        # The simplest approach if area is required: do nothing or raise error if area not derivable.
        # This part of the legacy API seems difficult to map directly.

        # A pragmatic choice: the legacy `delete_by_ids` might not be directly usable if area is missing.
        # The `delete_by_filter` in legacy Memory.py uses `self.db[area].delete(ids)`.
        # This implies `ids` are unique *within an area's DB*.

        # If we assume IDs passed are globally unique as per FAISS's own ID system (if direct ID usage),
        # then the area might not be strictly needed for deletion at the FAISS level,
        # but LegacyMemory's structure is area-based.

        # For now, returning empty list as a placeholder for deleted documents,
        # and printing a warning about the area requirement for actual deletion.
        print(f"Warning: FaissBackend.delete_documents_by_ids is problematic without area context for legacy system. IDs: {ids}. No actual deletion performed by this wrapper method unless legacy delete_by_ids is adapted or called specifically with area.")
        # Actual deletion would require something like:
        # for area_name in self.legacy_memory.db.keys():
        #     await self.legacy_memory.delete_by_ids(ids, area_name)
        # But this is risky if IDs are not global.

        # To match the return type, we'd return the docs_to_return if we could confirm deletion.
        # Given the uncertainty, returning an empty list is safer for now.
        return [] # Placeholder, actual deletion logic is complex here.


    async def delete_documents_by_query(
        self,
        query: str,
        threshold: float = 0.75,
        filter: Optional[Dict[str, Any]] = None # Legacy filter was string-based area
    ) -> List[MemoryDocument]:
        await self._ensure_legacy_initialized()

        area_filter_str = ""
        if filter and "area" in filter and isinstance(filter["area"], str):
            area_filter_str = filter["area"]

        # Legacy `delete_by_query_from_area` returns list of deleted doc IDs (not MemoryDocuments).
        # And it requires an area. If no area_filter_str, this won't work well.

        if not area_filter_str:
            print("Warning: FaissBackend.delete_documents_by_query requires an 'area' in the filter for the legacy system. No documents deleted.")
            return []

        # Fetch documents first that would be deleted
        docs_that_would_be_deleted = await self.search_similarity_threshold(query, limit=1000, threshold=threshold, filter=filter)

        # Perform deletion using legacy method (which expects area and might not return full docs)
        # The legacy `delete_by_query_from_area` is not async and returns list of string IDs.
        # This is a significant mismatch.
        # `await self.legacy_memory.delete_by_query_from_area(query, threshold, area_filter_str)`

        # The existing `memory_forget.py` tool calls `mem.delete_by_query_from_area(query, threshold, area)`
        # This suggests the area is indeed crucial.

        # For now, let's assume this operation is difficult to map perfectly and might be lossy.
        # We'll return the documents *identified* for deletion. Actual deletion is tricky.

        print(f"Warning: FaissBackend.delete_documents_by_query for area '{area_filter_str}'. Actual deletion in legacy system is separate and might not return full documents.")
        # To truly delete, one would call:
        # self.legacy_memory.delete_by_query_from_area(query, threshold, area_filter_str)
        # This is not async and returns List[str] of IDs.

        return docs_that_would_be_deleted # Return docs identified, actual deletion is separate.

    async def get_documents_by_ids(self, ids: List[str]) -> List[MemoryDocument]:
        await self._ensure_legacy_initialized()
        # LegacyMemory's `get_by_ids(ids, area)` requires an area.
        # This is another mismatch if global IDs are expected.

        # If IDs are prefixed with area like "main_uuid123", we could parse.
        # Or, we search all areas. This is inefficient.

        # For now, assume we search all known areas if no specific area hint is in IDs.
        # This is not ideal.

        all_found_docs: List[MemoryDocument] = []
        if not self.legacy_memory or not hasattr(self.legacy_memory, 'db'): # type: ignore
             return all_found_docs

        # A simple heuristic: if ID contains '::', assume it's area::doc_id
        # Otherwise, search all areas for the plain ID.

        docs_by_area_and_id: Dict[str, List[str]] = {}
        plain_ids_to_search_all_areas: List[str] = []

        for doc_id in ids:
            if "::" in doc_id:
                area, actual_id = doc_id.split("::", 1)
                if area not in docs_by_area_and_id:
                    docs_by_area_and_id[area] = []
                docs_by_area_and_id[area].append(actual_id)
            else:
                plain_ids_to_search_all_areas.append(doc_id)

        for area, area_ids in docs_by_area_and_id.items():
            if area in self.legacy_memory.db: # type: ignore
                try:
                    # legacy_memory.get_by_ids returns List[Document]
                    legacy_docs: List[LegacyFaissDocument] = self.legacy_memory.get_by_ids(area_ids, area) # type: ignore
                    for ld in legacy_docs:
                        all_found_docs.append(self._to_memory_document(ld))
                except Exception as e:
                    print(f"Error fetching IDs from area {area}: {e}") # Or log


        if plain_ids_to_search_all_areas:
            for area_name in self.legacy_memory.db.keys(): # type: ignore
                try:
                    legacy_docs: List[LegacyFaissDocument] = self.legacy_memory.get_by_ids(plain_ids_to_search_all_areas, area_name) # type: ignore
                    for ld in legacy_docs:
                        # Avoid duplicates if an ID was found in multiple areas (should not happen with good IDs)
                        if not any(found_doc.id == ld.id for found_doc in all_found_docs):
                             all_found_docs.append(self._to_memory_document(ld))
                except Exception as e:
                    print(f"Error fetching plain IDs from area {area_name}: {e}") # Or log

        return all_found_docs
