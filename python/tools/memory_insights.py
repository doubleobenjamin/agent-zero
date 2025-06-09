from python.helpers.enhanced_memory import EnhancedMemory
from python.helpers.tool import Tool, Response


class MemoryInsights(Tool):
    """Tool to get insights about the enhanced memory system"""

    async def execute(self, **kwargs):
        """Get comprehensive insights about the memory system"""
        
        # Get enhanced memory instance
        db = await EnhancedMemory.get(self.agent)
        
        # Get memory insights
        insights = await db.get_memory_insights()
        
        if not insights:
            return Response(message="❌ Unable to retrieve memory insights", break_loop=False)
        
        # Format insights into a comprehensive report
        report_parts = [
            "🧠 **Enhanced Memory System Insights**",
            "=" * 50,
            "",
            f"🏷️ **Agent Configuration:**",
            f"  • Collection: {insights.get('collection_name', 'N/A')}",
            f"  • Namespace: {insights.get('namespace', 'N/A')}",
            f"  • Dataset: {insights.get('dataset_name', 'N/A')}",
            "",
            f"📊 **Storage Statistics:**",
            f"  • Vector Documents: {insights.get('total_vectors', 0):,}",
            f"  • Knowledge Entities: {insights.get('total_entities', 0):,}",
            f"  • Relationships: {insights.get('total_relationships', 0):,}",
            f"  • Episodes: {insights.get('total_episodes', 0):,}",
            ""
        ]
        
        # Add system-specific stats
        system_stats = insights.get('system_stats', {})
        
        # Qdrant stats
        qdrant_stats = system_stats.get('qdrant', {})
        if qdrant_stats:
            report_parts.extend([
                f"🔍 **Qdrant Vector Database:**",
                f"  • Total Points: {qdrant_stats.get('points_count', 0):,}",
                f"  • Indexed Vectors: {qdrant_stats.get('indexed_vectors_count', 0):,}",
                f"  • Vector Count: {qdrant_stats.get('vectors_count', 0):,}",
                ""
            ])
        
        # Graphiti stats
        graphiti_stats = system_stats.get('graphiti', {})
        if graphiti_stats:
            report_parts.extend([
                f"🕸️ **Graphiti Knowledge Graph:**",
                f"  • Entities: {graphiti_stats.get('entities', 0):,}",
                f"  • Episodes: {graphiti_stats.get('episodes', 0):,}",
                f"  • Relationships: {graphiti_stats.get('relationships', 0):,}",
                ""
            ])
        
        # Cognee stats
        cognee_stats = system_stats.get('cognee', {})
        if cognee_stats:
            report_parts.extend([
                f"🧮 **Cognee Knowledge Processing:**",
                f"  • Documents: {cognee_stats.get('documents', 0):,}",
                f"  • Entities: {cognee_stats.get('entities', 0):,}",
                f"  • Relationships: {cognee_stats.get('relationships', 0):,}",
                f"  • Last Updated: {cognee_stats.get('last_updated', 'N/A')}",
                ""
            ])
        
        # Add recommendations
        total_items = insights.get('total_vectors', 0) + insights.get('total_entities', 0)
        
        report_parts.extend([
            f"💡 **Recommendations:**"
        ])
        
        if total_items == 0:
            report_parts.append("  • Memory system is empty. Start by saving some information!")
        elif total_items < 10:
            report_parts.append("  • Memory system is getting started. Add more information for better insights.")
        elif total_items < 100:
            report_parts.append("  • Good amount of data. Knowledge graph relationships should be forming.")
        else:
            report_parts.append("  • Rich memory system! Use entity and relationship searches for deep insights.")
        
        if insights.get('total_relationships', 0) == 0:
            report_parts.append("  • No relationships detected yet. Add more contextual information.")
        
        if insights.get('total_entities', 0) > 0:
            report_parts.append("  • Try searching for specific entities using search_type='entities'")
        
        if insights.get('total_relationships', 0) > 0:
            report_parts.append("  • Explore relationships using search_type='relationships'")
        
        report = "\n".join(report_parts)
        return Response(message=report, break_loop=False)
