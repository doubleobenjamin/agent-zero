# ACI Unified Tool Interface

Agent Zero now includes integrated access to ACI's unified tool interface, providing direct access to 600+ standardized tools via the ACI Python SDK.

## Overview

The ACI Unified Tool Interface enhances Agent Zero's capabilities by:

- **Direct Function Calling**: Execute ACI functions directly without MCP overhead
- **Standardized Access**: Unified interface to 600+ tools across multiple categories
- **Intelligent Discovery**: AI-powered tool recommendation based on task context
- **Dynamic Registration**: Runtime tool discovery and metadata caching
- **Unified Authentication**: Centralized OAuth and API key management via linked accounts
- **Error Recovery**: Built-in retry mechanisms and detailed error handling
- **Performance Optimization**: Direct API calls with intelligent caching

## Quick Start

### 1. Install ACI SDK

```bash
pip install aci-sdk
```

### 2. Configuration

Add these environment variables to your `.env` file:

```bash
# ACI Unified Tool Interface
ACI_API_KEY=your_aci_api_key
ACI_LINKED_ACCOUNT_OWNER_ID=your_user_identifier
ACI_TOOLS_ENABLED=true
ACI_BASE_URL=https://api.aci.dev
```

### 3. Linked Account Setup

1. Go to [ACI Platform](https://platform.aci.dev)
2. Navigate to "Linked Accounts"
3. Link accounts for the apps you want to use (e.g., Gmail, Slack, GitHub)
4. Use the same `linked_account_owner_id` as in your environment

### 4. Tool Discovery

Use the `aci_discover` tool to find the best functions for your tasks:

```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "search the web for information"
    }
}
```

## Tool Categories

ACI tools are organized into the following categories:

### Search Tools
- Web search engines (Google, Bing, DuckDuckGo)
- Academic search (arXiv, PubMed, Google Scholar)
- Specialized search (news, images, videos)

### Browser Tools
- Web scraping and crawling
- Page content extraction
- Screenshot capture
- Form automation

### Communication Tools
- Email (Gmail, Outlook, SMTP)
- Messaging (Slack, Discord, Teams)
- Social media (Twitter, LinkedIn)
- Notifications (webhooks, push notifications)

### Productivity Tools
- Calendar management (Google Calendar, Outlook)
- Note-taking (Notion, Obsidian, OneNote)
- Task management (Trello, Asana, Todoist)
- Document processing (Google Docs, Office 365)

### Development Tools
- Version control (GitHub, GitLab, Bitbucket)
- Project management (Jira, Linear, GitHub Issues)
- Code analysis and review
- CI/CD integration

### Data Tools
- Database operations (SQL, NoSQL)
- API interactions (REST, GraphQL)
- Data processing and analytics
- File format conversions

### AI Tools
- Language models (OpenAI, Anthropic, Cohere)
- Image generation and processing
- Speech-to-text and text-to-speech
- Machine learning model inference

### File Tools
- Cloud storage (Google Drive, Dropbox, S3)
- File upload and download
- Format conversion
- Compression and archiving

### System Tools
- System monitoring and diagnostics
- Process management
- Network utilities
- Security tools

## How Agents Access ACI Tools

### Direct Function Calling
Agents can call ACI functions directly using the function name as the tool name. The `get_tool` method in Agent Zero automatically detects ACI function names (format: `APP_NAME__FUNCTION_NAME`) and routes them through the ACI interface.

### Web Search
```json
{
    "tool_name": "BRAVE_SEARCH__WEB_SEARCH",
    "tool_args": {
        "query": "latest developments in AI",
        "count": 10
    }
}
```

### Send Slack Message
```json
{
    "tool_name": "SLACK__SEND_MESSAGE",
    "tool_args": {
        "channel": "#general",
        "text": "Hello from Agent Zero!"
    }
}
```

### GitHub Operations
```json
{
    "tool_name": "GITHUB__CREATE_ISSUE",
    "tool_args": {
        "owner": "username",
        "repo": "repository",
        "title": "Bug Report",
        "body": "Description of the issue"
    }
}
```

### File Upload
```json
{
    "tool_name": "AWS_S3__UPLOAD_FILE",
    "tool_args": {
        "file_path": "/path/to/file.pdf",
        "bucket": "my-bucket",
        "key": "folder/file.pdf"
    }
}
```

### Alternative: Explicit ACI Function Tool
```json
{
    "tool_name": "aci_function",
    "tool_args": {
        "function_name": "BRAVE_SEARCH__WEB_SEARCH",
        "function_arguments": {
            "query": "latest developments in AI",
            "count": 10
        }
    }
}
```

## Configuration Management

### Check Status
```json
{
    "tool_name": "aci_config",
    "tool_args": {
        "action": "status"
    }
}
```

### Validate Setup
```json
{
    "tool_name": "aci_config",
    "tool_args": {
        "action": "validate"
    }
}
```

### Get Setup Instructions
```json
{
    "tool_name": "aci_config",
    "tool_args": {
        "action": "instructions"
    }
}
```

### Reset Configuration
```json
{
    "tool_name": "aci_config",
    "tool_args": {
        "action": "reset"
    }
}
```

## Tool Discovery

### Get Recommendations by Query
```json
{
    "tool_name": "aci_tool_discovery",
    "tool_args": {
        "query": "send an email",
        "limit": 5
    }
}
```

### Filter by Category
```json
{
    "tool_name": "aci_tool_discovery",
    "tool_args": {
        "query": "manage tasks",
        "category": "productivity",
        "limit": 3
    }
}
```

### Show All Available Tools
```json
{
    "tool_name": "aci_tool_discovery",
    "tool_args": {
        "show_all": true
    }
}
```

## Architecture

### Agent Access Mechanism

The ACI integration works through a **modified `get_tool` method** in `agent.py` that provides seamless access to ACI functions:

```python
def get_tool(self, name: str, method: str | None, args: dict, message: str, **kwargs):
    # Check ACI tools first
    if aci_interface.is_enabled() and ("__" in name or name.startswith("aci_")):
        return ACIUnifiedTool(agent=self, name=name, ...)

    # Fall back to legacy tools
    return legacy_tool_class(agent=self, name=name, ...)
```

### Integration Flow

1. **Function Name Detection**: Agent detects ACI function names (format: `APP_NAME__FUNCTION_NAME`)
2. **ACI Interface Routing**: Requests are routed through the ACI Python SDK
3. **Direct Function Execution**: Functions are executed via ACI's unified API
4. **Response Formatting**: Results are formatted for Agent Zero consumption
5. **Fallback Support**: Automatic fallback to legacy tools if ACI is unavailable

## Benefits

### For Users
- **More Tools**: Access to 600+ tools vs. 20+ legacy tools
- **Better Reliability**: Standardized error handling and retry logic
- **Consistent Interface**: Uniform request/response format across all tools
- **Automatic Updates**: New tools and capabilities added without code changes

### For Developers
- **Simplified Integration**: No need to implement individual tool wrappers
- **Standardized Authentication**: Centralized credential management
- **Performance Optimization**: Built-in caching and rate limiting
- **Enhanced Monitoring**: Detailed usage analytics and error tracking

## Troubleshooting

### Common Issues

1. **ACI tools not available**
   - Check that `ACI_TOOLS_ENABLED=true`
   - Verify `ACI_API_KEY` and `ACI_PROJECT_ID` are set
   - Run `aci_config` with `action: "validate"`

2. **Authentication errors**
   - Verify API key is correct and active
   - Check project ID matches your ACI account
   - Ensure sufficient API quota/credits

3. **Tool not found**
   - Use `aci_tool_discovery` to find available tools
   - Check tool name format: `server_name.tool_name`
   - Verify the tool exists in the specified category

4. **Performance issues**
   - Check network connectivity to ACI servers
   - Review rate limiting settings
   - Monitor tool usage statistics

### Getting Help

- Use `aci_config` with `action: "instructions"` for setup guidance
- Use `aci_tool_discovery` to explore available tools
- Check Agent Zero logs for detailed error messages
- Refer to ACI documentation for tool-specific help

## Migration from Legacy Tools

ACI tools automatically provide fallback to legacy implementations, so existing workflows continue to work while gaining access to enhanced capabilities. The system intelligently routes requests to the best available tool implementation.

Legacy tools that benefit from ACI enhancement:
- `search_engine` → `aci_unified.google_search`
- `browser` → `aci_unified.web_browser`
- `webpage_content_tool` → `aci_unified.web_scraper`

The ACI unified tool interface represents a significant enhancement to Agent Zero's capabilities, providing access to a vast ecosystem of standardized, reliable, and continuously updated tools.
