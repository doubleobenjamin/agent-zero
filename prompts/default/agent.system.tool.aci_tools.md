### ACI Unified Tool Interface

Access to 600+ standardized tools through direct function calling with the ACI Python SDK.

#### Enhanced Tool Capabilities:
- **Direct Function Calling**: Execute ACI functions directly without MCP overhead
- **Unified Authentication**: Centralized OAuth and API key management via linked accounts
- **Dynamic Discovery**: Runtime tool registration and intelligent recommendations
- **Error Recovery**: Built-in retry mechanisms and error handling
- **Performance Optimization**: Direct API calls with intelligent caching
- **Categorization**: Tools organized by function (search, communication, development, etc.)

#### Available Tool Categories:
- **search**: Web search engines (Brave, Google, Tavily)
- **browser**: Web browsing, scraping, navigation tools
- **communication**: Messaging, email, chat (Slack, Gmail, Discord)
- **productivity**: Calendar, notes, task management (Notion, Airtable)
- **development**: Code, version control, project tools (GitHub, GitLab, Jira)
- **data**: Database, API, analytics tools
- **ai**: AI models, language processing (OpenAI, Anthropic, Hugging Face)
- **file**: File management, storage (S3, Google Drive, Dropbox)
- **system**: System operations, utilities, monitoring

#### Tool Discovery:
Use the `aci_discover` tool to find functions for your task:

**Get recommendations by query:**
```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "search the web for information",
        "limit": 5
    }
}
```

**Filter by category:**
```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "send a message",
        "category": "communication",
        "limit": 3
    }
}
```

**Filter by specific apps:**
```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "search",
        "app_names": ["BRAVE_SEARCH", "TAVILY"]
    }
}
```

#### Direct Function Execution:
ACI functions can be called directly using their function names as tool names:

**Web Search Example:**
```json
{
    "tool_name": "BRAVE_SEARCH__WEB_SEARCH",
    "tool_args": {
        "query": "latest AI developments",
        "count": 10
    }
}
```

**Send Slack Message:**
```json
{
    "tool_name": "SLACK__SEND_MESSAGE",
    "tool_args": {
        "channel": "#general",
        "text": "Hello from Agent Zero!"
    }
}
```

**GitHub Operations:**
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

#### Alternative: Explicit ACI Function Tool
You can also use the explicit `aci_function` tool:

```json
{
    "tool_name": "aci_function",
    "tool_args": {
        "function_name": "BRAVE_SEARCH__WEB_SEARCH",
        "function_arguments": {
            "query": "latest AI developments",
            "count": 10
        }
    }
}
```

#### Status and Configuration:
Use the `aci_status` tool to manage ACI setup:

**Check status:**
```json
{
    "tool_name": "aci_status",
    "tool_args": {
        "action": "status"
    }
}
```

**Test connection:**
```json
{
    "tool_name": "aci_status",
    "tool_args": {
        "action": "test"
    }
}
```

**Get setup instructions:**
```json
{
    "tool_name": "aci_status",
    "tool_args": {
        "action": "setup"
    }
}
```

#### Benefits Over Individual Tools:
- **Massive Scale**: 600+ tools vs. limited individual implementations
- **Standardized Interface**: Consistent function calling format
- **Automatic Updates**: New tools available without code changes
- **Better Performance**: Direct API calls, no MCP overhead
- **Enhanced Security**: Centralized authentication via linked accounts
- **Intelligent Discovery**: AI-powered function recommendations

#### Best Practices:
1. **Discover First**: Use `aci_discover` to find the right function for your task
2. **Check Status**: Ensure ACI is configured with `aci_status`
3. **Use Categories**: Filter by category for targeted recommendations
4. **Linked Accounts**: Ensure required apps are linked in ACI platform
5. **Error Handling**: ACI provides detailed error messages and suggestions

The ACI unified tool interface provides direct access to a vast ecosystem of standardized tools through intelligent function calling, dramatically expanding Agent Zero's capabilities.
