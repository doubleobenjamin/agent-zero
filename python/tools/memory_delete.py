from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response


class MemoryDelete(Tool):

    async def execute(self, memory_ids: list[str], area: str = "", **kwargs): # Signature changed as per prompt
        memory_layer = await Memory.get_abstraction_layer(self.agent)

        # The MAL's delete_documents_by_ids expects List[str] of IDs.
        # The 'area' parameter is not directly used by memory_layer.delete_documents_by_ids.
        # If area is crucial for deletion (especially for Faiss backend),
        # IDs might need to be area-qualified (e.g., ["main::id1"])
        # or the FaissBackend's heuristic for "area::id" might be relied upon if area is part of ID strings.
        # This tool's signature now includes 'area', but it's not passed to MAL's delete method directly.
        # It could be used to pre-process memory_ids if needed, e.g., prefixing them with the area.
        # For now, directly passing memory_ids as per the provided snippet.

        # Ensure memory_ids is actually a list, as old tool took a string.
        # This change implies the caller (LLM or dispatcher) needs to provide a list.
        if isinstance(memory_ids, str):
            # Attempt to handle if it's still passed as a comma-separated string for some compatibility.
            # This is a deviation from the strict new signature but might be practical.
            actual_memory_ids = [id_str.strip() for id_str in memory_ids.split(",") if id_str.strip()]
        elif not isinstance(memory_ids, list):
            # Handle cases where it's not a list or string (e.g. single ID string not in a list)
            # For robustness, convert to list if it's a single non-list item, or raise error.
            # This part depends on how strictly the new signature is enforced by callers.
            # For now, assuming it will be a list as per new type hint.
            actual_memory_ids = memory_ids
        else:
            actual_memory_ids = memory_ids

        if not actual_memory_ids:
             return Response(message="No memory IDs provided for deletion.", break_loop=False)

        deleted_documents = await memory_layer.delete_documents_by_ids(actual_memory_ids)

        if deleted_documents:
            # Assuming fw.memories_deleted.md expects num_deleted
            result = self.agent.read_prompt("fw.memories_deleted.md", num_deleted=len(deleted_documents))
        else:
            # This message might need adjustment if delete_documents_by_ids returns empty on failure vs. no docs found
            result = self.agent.read_prompt("fw.memories_not_found.md", query=", ".join(actual_memory_ids))
        return Response(message=result, break_loop=False)
