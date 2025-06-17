from python.helpers.memory import Memory
from python.helpers.tool import Tool, Response


class MemorySave(Tool):

    async def execute(self, text="", area="", **kwargs):

        if not area:
            area = Memory.Area.MAIN.value # Using enum value for consistency if MAL expects specific strings

        metadata = {"area": area, **kwargs}
        # Consider adding timestamp if standard practice, e.g.:
        # from datetime import datetime, timezone
        # metadata["timestamp"] = datetime.now(timezone.utc).isoformat()

        memory_layer = await Memory.get_abstraction_layer(self.agent)
        doc_id = await memory_layer.insert_text(text, metadata)

        result = self.agent.read_prompt("fw.memory_saved.md", memory_id=doc_id)
        return Response(message=result, break_loop=False)
