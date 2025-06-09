"""
ACI Unified Tool Wrapper

This tool wraps ACI function calls and integrates them seamlessly into
Agent Zero's tool system, allowing agents to access ACI tools directly
through the standard tool interface.
"""

import json
from typing import Dict, Any

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.aci_interface import ACIInterface


class ACIUnifiedTool(Tool):
    """
    ACI Unified Tool Wrapper
    
    This tool acts as a bridge between Agent Zero's tool system and ACI's
    function calling interface. It allows agents to seamlessly access ACI
    tools using the standard Agent Zero tool format.
    
    The tool automatically:
    - Detects ACI function names (APP_NAME__FUNCTION_NAME format)
    - Handles authentication via ACI linked accounts
    - Provides intelligent error handling and fallbacks
    - Formats results for Agent Zero consumption
    """
    
    def __init__(self, agent, name: str, method: str | None, args: dict, message: str, **kwargs):
        super().__init__(agent, name, method, args, message, **kwargs)
        self.function_name = name
        self.aci_interface = ACIInterface()
    
    async def execute(self, **kwargs) -> Response:
        """
        Execute an ACI function through the unified interface
        
        This method:
        1. Initializes the ACI interface
        2. Executes the requested ACI function
        3. Formats the response for Agent Zero
        4. Handles errors gracefully
        
        Returns:
            Response with function execution results
        """
        try:
            # Initialize ACI interface
            if not self.aci_interface.is_enabled():
                return Response(
                    message=f"❌ ACI interface is not enabled. Cannot execute function '{self.function_name}'.\n\nTo enable ACI tools:\n1. Set ACI_TOOLS_ENABLED=true\n2. Set ACI_API_KEY=your_api_key\n3. Set ACI_LINKED_ACCOUNT_OWNER_ID=your_user_id",
                    break_loop=False
                )
            
            if not self.aci_interface.initialize():
                return Response(
                    message=f"❌ Failed to initialize ACI client for function '{self.function_name}'.\n\nPlease check:\n1. ACI_API_KEY is valid\n2. ACI_LINKED_ACCOUNT_OWNER_ID is correct\n3. Network connectivity to ACI services",
                    break_loop=False
                )
            
            # Prepare function arguments
            function_arguments = self.args.copy()
            
            # Remove Agent Zero specific arguments that shouldn't be passed to ACI
            agent_zero_args = ['tool_name', 'method', 'message']
            for arg in agent_zero_args:
                function_arguments.pop(arg, None)
            
            # Execute the ACI function
            result = self.aci_interface.execute_function(
                function_name=self.function_name,
                function_arguments=function_arguments
            )
            
            # Format the response
            return self._format_aci_response(result)
            
        except Exception as e:
            error_msg = f"Error executing ACI function '{self.function_name}': {str(e)}"
            PrintStyle(font_color="#FF6B6B", bold=True).print(error_msg)
            
            return Response(
                message=f"❌ **ACI Function Error**: {self.function_name}\n\n{error_msg}\n\n**Troubleshooting:**\n1. Check function name format (APP_NAME__FUNCTION_NAME)\n2. Verify required linked accounts are configured\n3. Use `aci_status` tool to check configuration\n4. Use `aci_discover` to find correct function names",
                break_loop=False
            )
    
    def _format_aci_response(self, result: Dict[str, Any]) -> Response:
        """
        Format ACI function result for Agent Zero consumption
        
        Args:
            result: Raw result from ACI function execution
            
        Returns:
            Formatted Response object
        """
        if not isinstance(result, dict):
            return Response(
                message=f"✅ **ACI Function Executed**: {self.function_name}\n\nResult: {str(result)}",
                break_loop=False
            )
        
        success = result.get("success", True)
        data = result.get("data", result.get("result", {}))
        error = result.get("error")
        
        if not success and error:
            return Response(
                message=f"❌ **ACI Function Failed**: {self.function_name}\n\nError: {error}\n\n**Suggestions:**\n1. Check function parameters\n2. Verify linked account permissions\n3. Use `aci_discover` to see parameter requirements",
                break_loop=False
            )
        
        # Format successful response
        response_parts = []
        response_parts.append(f"✅ **ACI Function Executed Successfully**: {self.function_name}")
        response_parts.append("")
        
        # Handle different data formats
        if isinstance(data, dict):
            # Handle search results
            if "results" in data:
                results = data["results"]
                if isinstance(results, list) and len(results) > 0:
                    response_parts.append("## Search Results:")
                    for i, item in enumerate(results[:10], 1):  # Limit to 10 results
                        if isinstance(item, dict):
                            title = item.get("title", item.get("name", "No title"))
                            url = item.get("url", item.get("link", ""))
                            snippet = item.get("snippet", item.get("description", item.get("content", "")))
                            
                            response_parts.append(f"**{i}. {title}**")
                            if url:
                                response_parts.append(f"   🔗 {url}")
                            if snippet:
                                # Truncate long snippets
                                if len(snippet) > 200:
                                    snippet = snippet[:200] + "..."
                                response_parts.append(f"   📝 {snippet}")
                            response_parts.append("")
                else:
                    response_parts.append(f"Results: {json.dumps(results, indent=2)}")
            
            # Handle message/communication results
            elif "message" in data or "status" in data:
                if "message" in data:
                    response_parts.append(f"**Message**: {data['message']}")
                if "status" in data:
                    response_parts.append(f"**Status**: {data['status']}")
                if "id" in data:
                    response_parts.append(f"**ID**: {data['id']}")
            
            # Handle file operations
            elif "file_url" in data or "download_url" in data:
                url = data.get("file_url", data.get("download_url", ""))
                filename = data.get("filename", data.get("name", "file"))
                size = data.get("size", "")
                
                response_parts.append(f"**File**: {filename}")
                if url:
                    response_parts.append(f"**URL**: {url}")
                if size:
                    response_parts.append(f"**Size**: {size}")
            
            # Handle generic object data
            else:
                response_parts.append("## Function Output:")
                # Pretty print JSON with reasonable limits
                json_str = json.dumps(data, indent=2)
                if len(json_str) > 2000:  # Truncate very long responses
                    json_str = json_str[:2000] + "\n... (truncated)"
                response_parts.append(f"```json\n{json_str}\n```")
        
        elif isinstance(data, list):
            response_parts.append(f"## Results ({len(data)} items):")
            for i, item in enumerate(data[:5], 1):  # Show first 5 items
                response_parts.append(f"{i}. {str(item)}")
            if len(data) > 5:
                response_parts.append(f"... and {len(data) - 5} more items")
        
        else:
            response_parts.append("## Function Output:")
            response_parts.append(str(data))
        
        return Response(
            message="\n".join(response_parts),
            break_loop=False
        )
    
    async def before_execution(self, **kwargs):
        """Override to provide custom logging for ACI functions"""
        PrintStyle(font_color="#4A90E2", padding=True, background_color="white", bold=True).print(
            f"{self.agent.agent_name}: Executing ACI function '{self.function_name}'"
        )
        
        self.log = self.get_log_object()
        
        # Log function details
        PrintStyle(font_color="#4A90E2", bold=True).stream("ACI Function: ")
        PrintStyle(font_color="#4A90E2").stream(self.function_name)
        PrintStyle().print()
        
        if self.args:
            # Filter out Agent Zero internal args for cleaner logging
            clean_args = {k: v for k, v in self.args.items() 
                         if k not in ['tool_name', 'method', 'message']}
            if clean_args:
                PrintStyle(font_color="#4A90E2", bold=True).stream("Arguments: ")
                PrintStyle(font_color="#4A90E2", padding=True).stream(
                    json.dumps(clean_args, indent=2)
                )
                PrintStyle().print()
    
    def get_log_object(self):
        """Override to provide custom log heading for ACI functions"""
        heading = f"{self.agent.agent_name}: Executing ACI function '{self.function_name}'"
        return self.agent.context.log.log(
            type="tool", 
            heading=heading, 
            content="", 
            kvps=self.args
        )
