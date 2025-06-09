from python.helpers.enhanced_memory import EnhancedMemory
from python.helpers.tool import Tool, Response

DEFAULT_THRESHOLD = 0.7
DEFAULT_LIMIT = 10


class MemoryLoad(Tool):

    async def execute(self, query="", threshold=DEFAULT_THRESHOLD, limit=DEFAULT_LIMIT, filter="", search_type="hybrid", **kwargs):
        # Use enhanced memory system
        db = await EnhancedMemory.get(self.agent)

        if search_type == "entities":
            # Search for entities
            entities = await db.search_entities(entity_name=query, limit=limit)
            if not entities:
                result = f"🔍 No entities found matching: {query}"
            else:
                result_parts = [f"🏷️ **Found {len(entities)} entities:**"]
                for entity in entities:
                    result_parts.append(f"  • **{entity.get('name', 'Unknown')}** - {entity.get('summary', 'No description')}")
                result = "\n".join(result_parts)

        elif search_type == "relationships":
            # Search for relationships
            relationships = await db.search_relationships(entity_name=query, limit=limit)
            if not relationships:
                result = f"🔗 No relationships found for: {query}"
            else:
                result_parts = [f"🔗 **Found {len(relationships)} relationships:**"]
                for rel in relationships:
                    result_parts.append(f"  • {rel.get('source', 'Unknown')} → {rel.get('relationship', 'relates to')} → {rel.get('target', 'Unknown')}")
                result = "\n".join(result_parts)

        else:
            # Default hybrid search
            docs = await db.search_similarity_threshold(query=query, limit=limit, threshold=threshold, filter=filter)

            if len(docs) == 0:
                result = self.agent.read_prompt("fw.memories_not_found.md", query=query)
            else:
                # Enhanced formatting with source information
                result_parts = [f"🔍 **Found {len(docs)} relevant memories:**\n"]

                for i, doc in enumerate(docs, 1):
                    source = doc.metadata.get('source', 'unknown')
                    area = doc.metadata.get('area', 'main')
                    timestamp = doc.metadata.get('timestamp', 'unknown')

                    result_parts.append(f"**Memory {i}** (Source: {source}, Area: {area})")
                    result_parts.append(f"📅 {timestamp}")
                    result_parts.append(f"📄 {doc.page_content}")
                    result_parts.append("---")

                result = "\n".join(result_parts)

        return Response(message=result, break_loop=False)
