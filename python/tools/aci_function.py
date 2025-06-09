"""
ACI Function Tool

Executes ACI functions directly using the ACI Python SDK.
This tool provides access to 600+ standardized tools through ACI's unified interface.
"""

import json
from typing import Dict, Any

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.aci_interface import ACIInterface


class ACIFunction(Tool):
    """
    ACI Function Execution Tool
    
    Executes ACI functions directly using the official ACI Python SDK.
    Provides access to 600+ standardized tools with intelligent error handling
    and unified authentication.
    """
    
    async def execute(self, **kwargs) -> Response:
        """
        Execute an ACI function
        
        Args:
            function_name: Name of the ACI function to execute (e.g., "BRAVE_SEARCH__WEB_SEARCH")
            function_arguments: Arguments to pass to the function
            
        Returns:
            Response with function execution results
        """
        function_name = self.args.get("function_name", "")
        function_arguments = self.args.get("function_arguments", {})
        
        if not function_name:
            return Response(
                message="Error: function_name is required for ACI function execution",
                break_loop=False
            )
        
        try:
            # Initialize ACI interface
            aci_interface = ACIInterface()
            
            if not aci_interface.is_enabled():
                return Response(
                    message="ACI interface is not enabled or configured. Please set ACI_API_KEY and ACI_LINKED_ACCOUNT_OWNER_ID environment variables.",
                    break_loop=False
                )
            
            # Initialize client
            if not aci_interface.initialize():
                return Response(
                    message="Failed to initialize ACI client. Check your API key and configuration.",
                    break_loop=False
                )
            
            # Execute the function
            result = aci_interface.execute_function(function_name, function_arguments)
            
            # Format response
            if result.get("success", False):
                response_parts = []
                response_parts.append(f"✅ **ACI Function Executed Successfully**: {function_name}")
                response_parts.append("")
                
                # Format the data
                data = result.get("data", {})
                if isinstance(data, dict):
                    if "results" in data:
                        # Handle search results format
                        results = data["results"]
                        if isinstance(results, list) and len(results) > 0:
                            response_parts.append("## Results:")
                            for i, item in enumerate(results[:10], 1):  # Limit to 10 results
                                if isinstance(item, dict):
                                    title = item.get("title", "No title")
                                    url = item.get("url", "")
                                    snippet = item.get("snippet", item.get("description", ""))
                                    
                                    response_parts.append(f"**{i}. {title}**")
                                    if url:
                                        response_parts.append(f"   URL: {url}")
                                    if snippet:
                                        response_parts.append(f"   {snippet}")
                                    response_parts.append("")
                        else:
                            response_parts.append(f"Results: {json.dumps(results, indent=2)}")
                    else:
                        # Handle other data formats
                        response_parts.append("## Function Output:")
                        response_parts.append(f"```json\n{json.dumps(data, indent=2)}\n```")
                else:
                    response_parts.append("## Function Output:")
                    response_parts.append(str(data))
                
                return Response(
                    message="\n".join(response_parts),
                    break_loop=False
                )
            else:
                error_msg = result.get("error", "Unknown error occurred")
                return Response(
                    message=f"❌ **ACI Function Failed**: {function_name}\n\nError: {error_msg}",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle(font_color="#FF6B6B", bold=True).print(
                f"ACI Function execution error: {str(e)}"
            )
            return Response(
                message=f"Error executing ACI function '{function_name}': {str(e)}",
                break_loop=False
            )
    
    async def before_execution(self, **kwargs):
        """Override to provide custom logging for ACI functions"""
        function_name = self.args.get("function_name", "unknown")
        function_arguments = self.args.get("function_arguments", {})
        
        PrintStyle(font_color="#4A90E2", padding=True, background_color="white", bold=True).print(
            f"{self.agent.agent_name}: Executing ACI function '{function_name}'"
        )
        
        self.log = self.get_log_object()
        
        # Log function details
        PrintStyle(font_color="#4A90E2", bold=True).stream("Function: ")
        PrintStyle(font_color="#4A90E2").stream(function_name)
        PrintStyle().print()
        
        if function_arguments:
            PrintStyle(font_color="#4A90E2", bold=True).stream("Arguments: ")
            PrintStyle(font_color="#4A90E2", padding=True).stream(
                json.dumps(function_arguments, indent=2)
            )
            PrintStyle().print()
    
    def get_log_object(self):
        """Override to provide custom log heading for ACI functions"""
        function_name = self.args.get("function_name", "unknown")
        heading = f"{self.agent.agent_name}: Executing ACI function '{function_name}'"
        return self.agent.context.log.log(
            type="tool", 
            heading=heading, 
            content="", 
            kvps=self.args
        )
