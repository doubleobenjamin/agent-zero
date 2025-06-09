🔍 **Enhanced Memory Search Results**

**Query**: "{{query}}"
**Search Type**: {{search_type}}
**Results Found**: {{results.length}}

{{#if results.cognee_results}}
### 🧠 Cognee Intelligence Results:
{{results.cognee_results}}
{{/if}}

{{#if results.traditional_results}}
### 📁 Traditional Memory Results:
{{results.traditional_results}}
{{/if}}

{{#if results.entities}}
### 🏷️ Related Entities:
{{results.entities}}
{{/if}}

{{#if results.relationships}}
### 🔗 Relationship Context:
{{results.relationships}}
{{/if}}

{{#if results.insights}}
### 💡 Generated Insights:
{{results.insights}}
{{/if}}

{{#if results.temporal_context}}
### ⏰ Temporal Context:
{{results.temporal_context}}
{{/if}}

**Search Capabilities Used**:
- Entity relationship mapping
- Temporal context analysis  
- Semantic similarity matching
- Knowledge graph traversal
- Pattern recognition and insights
