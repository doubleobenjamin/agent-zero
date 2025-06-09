"""
ACI Status and Configuration Tool

Provides status information and configuration management for the ACI interface.
"""

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.aci_interface import ACIInterface


class ACIStatus(Tool):
    """
    ACI Status and Configuration Tool
    
    Provides status information, configuration validation, and setup guidance
    for the ACI unified tool interface.
    """
    
    async def execute(self, **kwargs) -> Response:
        """
        Get ACI interface status and configuration information
        
        Args:
            action: Action to perform (default: "status")
                - "status": Show current status
                - "test": Test ACI connection
                - "setup": Show setup instructions
            
        Returns:
            Response with status information
        """
        action = self.args.get("action", "status").lower()
        
        try:
            aci_interface = ACIInterface()
            
            if action == "status":
                return await self._show_status(aci_interface)
            elif action == "test":
                return await self._test_connection(aci_interface)
            elif action == "setup":
                return await self._show_setup_instructions()
            else:
                return Response(
                    message=self._get_usage_help(),
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle(font_color="#FF6B6B", bold=True).print(
                f"ACI Status error: {str(e)}"
            )
            return Response(
                message=f"Error checking ACI status: {str(e)}",
                break_loop=False
            )
    
    async def _show_status(self, aci_interface: ACIInterface) -> Response:
        """Show current ACI status"""
        status = aci_interface.get_status()
        
        response_parts = []
        response_parts.append("# ACI Unified Tool Interface Status")
        response_parts.append("")
        
        # Basic status
        response_parts.append("## Configuration Status")
        response_parts.append(f"- **ACI Enabled**: {'✅' if status.get('enabled') else '❌'} {status.get('enabled', False)}")
        response_parts.append(f"- **SDK Available**: {'✅' if status.get('sdk_available') else '❌'} {status.get('sdk_available', False)}")
        response_parts.append(f"- **API Key Configured**: {'✅' if status.get('configured') else '❌'} {status.get('configured', False)}")
        response_parts.append(f"- **Client Initialized**: {'✅' if status.get('client_initialized') else '❌'} {status.get('client_initialized', False)}")
        response_parts.append("")
        
        # Configuration details
        response_parts.append("## Configuration Details")
        response_parts.append(f"- **Base URL**: {status.get('base_url', 'Not set')}")
        response_parts.append(f"- **Linked Account Owner ID**: {status.get('linked_account_owner_id', 'Not set')}")
        response_parts.append(f"- **Functions Cached**: {status.get('functions_cached', 0)}")
        response_parts.append("")
        
        # Error information
        if 'error' in status:
            response_parts.append("## Error")
            response_parts.append(f"❌ {status['error']}")
            response_parts.append("")
        
        # Quick actions
        response_parts.append("## Quick Actions")
        if not status.get('sdk_available'):
            response_parts.append("- Install ACI SDK: `pip install aci-sdk`")
        elif not status.get('enabled'):
            response_parts.append("- Enable ACI: Set `ACI_TOOLS_ENABLED=true`")
        elif not status.get('configured'):
            response_parts.append('- Configure API key: Set `ACI_API_KEY=your_key`')
            response_parts.append('- Set account owner: Set `ACI_LINKED_ACCOUNT_OWNER_ID=your_user_id`')
        elif not status.get('client_initialized'):
            response_parts.append('- Test connection: `{"action": "test"}`')
        else:
            response_parts.append('- Test connection: `{"action": "test"}`')
            response_parts.append('- Discover functions: Use `aci_discover` tool')
            response_parts.append('- Execute functions: Use `aci_function` tool')
        
        return Response(
            message="\n".join(response_parts),
            break_loop=False
        )
    
    async def _test_connection(self, aci_interface: ACIInterface) -> Response:
        """Test ACI connection"""
        response_parts = []
        response_parts.append("# ACI Connection Test")
        response_parts.append("")
        
        # Check if enabled
        if not aci_interface.is_enabled():
            response_parts.append("❌ **Test Failed**: ACI interface is not enabled or configured")
            response_parts.append("")
            response_parts.append("**Required Actions**:")
            response_parts.append("1. Set `ACI_TOOLS_ENABLED=true`")
            response_parts.append("2. Set `ACI_API_KEY=your_api_key`")
            response_parts.append("3. Set `ACI_LINKED_ACCOUNT_OWNER_ID=your_user_id`")
            response_parts.append("")
            response_parts.append('Run `{"action": "setup"}` for detailed instructions.')
            
            return Response(
                message="\n".join(response_parts),
                break_loop=False
            )
        
        # Test initialization
        if not aci_interface.initialize():
            response_parts.append("❌ **Test Failed**: Could not initialize ACI client")
            response_parts.append("")
            response_parts.append("**Possible Issues**:")
            response_parts.append("- Invalid API key")
            response_parts.append("- Network connectivity problems")
            response_parts.append("- ACI service unavailable")
            
            return Response(
                message="\n".join(response_parts),
                break_loop=False
            )
        
        # Test function discovery
        try:
            functions = aci_interface.discover_functions(
                intent="test connection",
                limit=5
            )
            
            response_parts.append("✅ **Connection Test Successful**")
            response_parts.append("")
            response_parts.append("## Test Results")
            response_parts.append(f"- **Client Initialization**: ✅ Success")
            response_parts.append(f"- **Function Discovery**: ✅ Success")
            response_parts.append(f"- **Functions Found**: {len(functions)}")
            response_parts.append("")
            
            if functions:
                response_parts.append("## Sample Functions Available")
                for func in functions[:3]:
                    response_parts.append(f"- **{func.name}** ({func.category.value}): {func.description}")
                response_parts.append("")
            
            response_parts.append("## Next Steps")
            response_parts.append("1. Use `aci_discover` to find functions for specific tasks")
            response_parts.append("2. Use `aci_function` to execute ACI functions")
            response_parts.append("3. Explore the 600+ available tools!")
            
        except Exception as e:
            response_parts.append("❌ **Test Failed**: Function discovery error")
            response_parts.append("")
            response_parts.append(f"**Error**: {str(e)}")
            response_parts.append("")
            response_parts.append("**Troubleshooting**:")
            response_parts.append("- Verify API key is correct and active")
            response_parts.append("- Check network connectivity")
            response_parts.append("- Ensure linked account is properly configured")
        
        return Response(
            message="\n".join(response_parts),
            break_loop=False
        )
    
    async def _show_setup_instructions(self) -> Response:
        """Show setup instructions"""
        instructions = """# ACI Unified Tool Interface Setup

## Overview
The ACI (Agent-Computer Interface) provides access to 600+ standardized tools through a unified API. This integration allows Agent Zero to use these tools directly via function calling.

## Prerequisites
1. **ACI Account**: Sign up at [https://platform.aci.dev](https://platform.aci.dev)
2. **API Key**: Generate an API key from your ACI dashboard
3. **Linked Account**: Set up linked accounts for the apps you want to use

## Installation

### 1. Install ACI SDK
```bash
pip install aci-sdk
```

### 2. Environment Configuration
Add these variables to your `.env` file:

```bash
# ACI Configuration
ACI_TOOLS_ENABLED=true
ACI_API_KEY=your_aci_api_key_here
ACI_LINKED_ACCOUNT_OWNER_ID=your_user_identifier
ACI_BASE_URL=https://api.aci.dev
```

### 3. Linked Account Setup
1. Go to [ACI Platform](https://platform.aci.dev)
2. Navigate to "Linked Accounts"
3. Link accounts for the apps you want to use (e.g., Gmail, Slack, GitHub)
4. Use the same `linked_account_owner_id` as in your environment

## Usage

### Function Discovery
```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "search the web for information"
    }
}
```

### Function Execution
```json
{
    "tool_name": "aci_function",
    "tool_args": {
        "function_name": "BRAVE_SEARCH__WEB_SEARCH",
        "function_arguments": {
            "query": "latest AI developments"
        }
    }
}
```

### Status Check
```json
{
    "tool_name": "aci_status",
    "tool_args": {
        "action": "test"
    }
}
```

## Available Tool Categories
- **search**: Web search engines (Brave, Google, Tavily)
- **communication**: Messaging (Slack, Discord, Gmail)
- **development**: Code tools (GitHub, GitLab, Jira)
- **productivity**: Organization (Notion, Airtable, Calendar)
- **ai**: AI models (OpenAI, Anthropic, Hugging Face)
- **data**: Database and API tools
- **file**: File management (S3, Google Drive, Dropbox)
- **browser**: Web automation and scraping
- **system**: System utilities and monitoring

## Troubleshooting

### Common Issues
1. **"ACI SDK not available"**
   - Install with: `pip install aci-sdk`

2. **"API key not found"**
   - Set `ACI_API_KEY` environment variable
   - Verify key is correct in ACI dashboard

3. **"Function execution failed"**
   - Check linked accounts are properly configured
   - Verify `ACI_LINKED_ACCOUNT_OWNER_ID` matches your setup
   - Ensure required app permissions are granted

### Getting Help
- Check status: `aci_status`
- Test connection: `{"action": "test"}`
- ACI Documentation: [https://aci.dev/docs](https://aci.dev/docs)
- ACI Platform: [https://platform.aci.dev](https://platform.aci.dev)

## Benefits
- **600+ Tools**: Access to comprehensive tool ecosystem
- **Standardized Interface**: Consistent API across all tools
- **Intelligent Discovery**: AI-powered tool recommendations
- **Unified Authentication**: Centralized credential management
- **Error Recovery**: Built-in retry and fallback mechanisms
- **Performance**: Optimized execution and caching"""
        
        return Response(
            message=instructions,
            break_loop=False
        )
    
    def _get_usage_help(self) -> str:
        """Get usage help for the ACI status tool"""
        return """# ACI Status Tool

Check ACI interface status and configuration.

## Available Actions

### Status Check
```json
{
    "tool_name": "aci_status",
    "tool_args": {
        "action": "status"
    }
}
```

### Connection Test
```json
{
    "tool_name": "aci_status",
    "tool_args": {
        "action": "test"
    }
}
```

### Setup Instructions
```json
{
    "tool_name": "aci_status",
    "tool_args": {
        "action": "setup"
    }
}
```

## Default Action
If no action is specified, "status" is used by default."""
