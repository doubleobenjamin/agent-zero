from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response

DEFAULT_THRESHOLD = 0.7
DEFAULT_LIMIT = 10


class MemoryLoad(Tool):

    async def execute(self, query="", area="", limit=DEFAULT_LIMIT, threshold=DEFAULT_THRESHOLD, **kwargs):
        memory_layer = await Memory.get_abstraction_layer(self.agent)

        # Construct filter for MAL if area is specified
        search_filter = None
        if area:
            search_filter = {"area": area}
        if kwargs: # Add any other filterable kwargs
            if search_filter is None: search_filter = {}
            search_filter.update(kwargs)

        # memories will be List[MemoryDocument]
        memories = await memory_layer.search_similarity_threshold(
            query=query,
            limit=limit,
            threshold=threshold,
            filter=search_filter
        )

        if not memories:
            result = self.agent.read_prompt("fw.memories_not_found.md", query=query)
        else:
            # Memory.format_docs_plain expects List[Document] where Document has .page_content and .metadata
            # MemoryDocument has .page_content and .metadata, so it should be compatible.
            # If it's not, a specific formatter for List[MemoryDocument] would be needed here.
            # Example:
            # formatted_texts = []
            # for mem_doc in memories:
            #     text = f"ID: {mem_doc.id}\n"
            #     if mem_doc.score is not None:
            #         text += f"Score: {mem_doc.score:.4f}\n"
            #     for k, v in mem_doc.metadata.items():
            #         text += f"{k}: {v}\n"
            #     text += f"Content: {mem_doc.page_content}\n"
            #     formatted_texts.append(text)
            # result = "\n\n".join(formatted_texts)

            # Assuming MemoryDocument is compatible with what Memory.format_docs_plain expects
            # or that Memory.format_docs_plain is general enough.
            text = "\n\n".join(Memory.format_docs_plain(memories)) # type: ignore
            result = str(text)

        return Response(message=result, break_loop=False)
