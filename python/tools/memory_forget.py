from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response
from python.tools.memory_load import DEFAULT_THRESHOLD


class MemoryForget(Tool):

    async def execute(self, query="", area="", threshold=DEFAULT_THRESHOLD, **kwargs): # Signature changed as per prompt
        memory_layer = await Memory.get_abstraction_layer(self.agent)

        # Construct filter for MAL if area is specified
        query_filter = None
        if area:
            query_filter = {"area": area}
        if kwargs: # Add any other filterable kwargs
            if query_filter is None: query_filter = {}
            query_filter.update(kwargs)

        deleted_documents = await memory_layer.delete_documents_by_query(
            query=query,
            threshold=threshold,
            filter=query_filter
        )

        if deleted_documents:
            result = self.agent.read_prompt("fw.memories_deleted.md", num_deleted=len(deleted_documents))
        else:
            result = self.agent.read_prompt("fw.memories_not_found.md", query=query)
        return Response(message=result, break_loop=False)
