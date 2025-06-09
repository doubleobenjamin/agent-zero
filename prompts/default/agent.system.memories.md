# Enhanced Memory Context

## Hybrid Memory System Active
Your memory system combines Graphiti (temporal knowledge graphs) and Cognee (intelligent processing).

## Current Memory Context:
{{#if recalled_memories}}
### Recalled Memories:
{{recalled_memories}}
{{/if}}

{{#if extracted_entities}}
### Extracted Entities:
{{extracted_entities}}
{{/if}}

{{#if relationship_insights}}
### Relationship Insights:
{{relationship_insights}}
{{/if}}

{{#if temporal_context}}
### Temporal Context:
{{temporal_context}}
{{/if}}

{{#if multimodal_analysis}}
### Multi-modal Analysis:
{{multimodal_analysis}}
{{/if}}

## Traditional Memory Context:
- Following are memories about current topic
- Do not overly rely on them they might not be relevant

{{memories}}

## Memory Capabilities Available:
- **Entity Recognition**: Automatic identification of people, places, concepts
- **Relationship Mapping**: Understanding connections between entities
- **Temporal Queries**: Time-aware memory retrieval
- **Multi-modal Processing**: Text, images, audio, video, code
- **Insight Generation**: AI-powered pattern recognition
- **Namespace Isolation**: Private, shared, and team memory spaces

## Usage Guidelines:
- Use hybrid_memory_search for intelligent information retrieval
- Leverage entity relationships for better context understanding
- Apply temporal queries when time context matters
- Utilize insights search for pattern discovery
- Save important information with appropriate namespace and context