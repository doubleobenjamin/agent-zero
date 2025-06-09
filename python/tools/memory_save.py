from python.helpers.enhanced_memory import EnhancedMemory
from python.helpers.tool import Tool, Response


class MemorySave(Tool):

    async def execute(self, text="", area="", **kwargs):

        if not area:
            area = EnhancedMemory.Area.MAIN.value

        metadata = {"area": area, **kwargs}

        # Use enhanced memory system
        db = await EnhancedMemory.get(self.agent)
        result = await db.insert_text(text, metadata)

        # Create rich feedback message
        feedback_parts = [
            f"✅ Memory saved successfully!",
            f"📄 Document ID: {result.get('doc_id', 'N/A')}",
            f"🧠 Entities extracted: {result.get('entities_extracted', 0)}",
            f"🔗 Relationships mapped: {result.get('relationships_mapped', 0)}",
            f"📊 Knowledge graph updated: {'Yes' if result.get('knowledge_graph_updated') else 'No'}"
        ]

        # Add entity details if available
        if result.get('entities'):
            feedback_parts.append("\n🏷️ **Extracted Entities:**")
            for entity in result.get('entities', [])[:5]:  # Show first 5 entities
                feedback_parts.append(f"  • {entity.get('name', 'Unknown')} ({entity.get('type', 'Unknown type')})")

        # Add relationship details if available
        if result.get('relationships'):
            feedback_parts.append("\n🔗 **Mapped Relationships:**")
            for rel in result.get('relationships', [])[:3]:  # Show first 3 relationships
                feedback_parts.append(f"  • {rel.get('source', 'Unknown')} → {rel.get('relationship', 'relates to')} → {rel.get('target', 'Unknown')}")

        # Add summary if available
        if result.get('summary'):
            feedback_parts.append(f"\n📝 **Summary:** {result.get('summary')}")

        feedback_message = "\n".join(feedback_parts)
        return Response(message=feedback_message, break_loop=False)
