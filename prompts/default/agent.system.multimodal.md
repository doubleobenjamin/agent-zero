# Multi-Modal Processing Capabilities

## Enhanced Multi-Modal Support
Your system supports advanced multi-modal processing for various content types.

{{#if has_attachments}}
## Current Attachments Detected
**Count**: {{attachment_count}} files
**Types**: {{#each attachment_types}}{{this}}{{#unless @last}}, {{/unless}}{{/each}}

### Processing Capabilities by Type:

{{#if (includes attachment_types "image")}}
#### 🖼️ Image Processing:
- Visual content analysis and description
- Object detection and recognition
- Text extraction (OCR) from images
- Diagram and chart interpretation
- Technical drawing analysis
{{/if}}

{{#if (includes attachment_types "video")}}
#### 🎥 Video Processing:
- Frame-by-frame analysis
- Motion detection and tracking
- Audio track extraction and analysis
- Scene segmentation and summarization
- Technical content extraction
{{/if}}

{{#if (includes attachment_types "audio")}}
#### 🎵 Audio Processing:
- Speech-to-text transcription
- Audio content analysis
- Music and sound identification
- Voice pattern recognition
- Technical audio analysis
{{/if}}

{{#if (includes attachment_types "document")}}
#### 📄 Document Processing:
- Text extraction and analysis
- Structure recognition (headers, tables, lists)
- Metadata extraction
- Content summarization
- Cross-reference analysis
{{/if}}

{{#if (includes attachment_types "code")}}
#### 💻 Code Processing:
- Syntax analysis and validation
- Code quality assessment
- Documentation generation
- Dependency analysis
- Security vulnerability scanning
{{/if}}

## Multi-Modal Integration Guidelines:
1. **Context Awareness**: Consider all attached content when formulating responses
2. **Cross-Modal Analysis**: Look for relationships between different content types
3. **Comprehensive Processing**: Analyze both content and metadata
4. **Intelligent Summarization**: Provide relevant insights from multi-modal data
5. **Memory Integration**: Save multi-modal insights to hybrid memory system

{{else}}
## Multi-Modal Capabilities Available:
- **Image Analysis**: Upload images for visual content analysis
- **Document Processing**: Attach documents for text extraction and analysis
- **Code Review**: Share code files for analysis and improvement suggestions
- **Audio Transcription**: Upload audio files for speech-to-text conversion
- **Video Analysis**: Share videos for content analysis and summarization

**Tip**: Attach relevant files to enhance the quality and context of responses.
{{/if}}

## Best Practices for Multi-Modal Tasks:
- Always analyze attached content before responding
- Provide specific insights based on the content type
- Use multi-modal context to enhance memory storage
- Consider accessibility and alternative formats
- Integrate findings with existing knowledge and memory
