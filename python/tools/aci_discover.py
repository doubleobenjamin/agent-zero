"""
ACI Function Discovery Tool

Discovers and recommends ACI functions based on natural language queries.
Provides intelligent tool selection from 600+ available functions.
"""

import json
from typing import List, Optional

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.aci_interface import ACIInterface, ACIToolCategory


class ACIDiscover(Tool):
    """
    ACI Function Discovery Tool
    
    Discovers and recommends ACI functions based on natural language queries,
    providing intelligent tool selection from ACI's 600+ function ecosystem.
    """
    
    async def execute(self, **kwargs) -> Response:
        """
        Discover ACI functions based on query
        
        Args:
            query: Natural language description of what you want to do
            category: Optional category filter (search, browser, communication, etc.)
            limit: Maximum number of functions to return (default: 10)
            app_names: Optional list of specific app names to filter by
            
        Returns:
            Response with discovered functions and usage examples
        """
        query = self.args.get("query", "")
        category_str = self.args.get("category", "")
        limit = int(self.args.get("limit", "10"))
        app_names = self.args.get("app_names", [])
        
        if not query:
            return Response(
                message=self._get_usage_help(),
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
            
            # Parse category if provided
            category = None
            if category_str:
                try:
                    category = ACIToolCategory(category_str.lower())
                except ValueError:
                    valid_categories = [cat.value for cat in ACIToolCategory]
                    return Response(
                        message=f"Invalid category '{category_str}'. Valid categories: {', '.join(valid_categories)}",
                        break_loop=False
                    )
            
            # Discover functions
            functions = aci_interface.discover_functions(
                intent=query,
                app_names=app_names if app_names else None,
                limit=limit
            )
            
            # Filter by category if specified
            if category:
                functions = [f for f in functions if f.category == category]
            
            # Format response
            response_parts = []
            response_parts.append(f"# ACI Function Discovery Results")
            response_parts.append(f"**Query**: {query}")
            if category:
                response_parts.append(f"**Category**: {category.value}")
            if app_names:
                response_parts.append(f"**Apps**: {', '.join(app_names)}")
            response_parts.append(f"**Found**: {len(functions)} functions")
            response_parts.append("")
            
            if not functions:
                response_parts.append("No functions found matching your criteria.")
                response_parts.append("")
                response_parts.append("**Suggestions:**")
                response_parts.append("- Try a different query or broader terms")
                response_parts.append("- Remove category filter")
                response_parts.append("- Check available categories with no query")
                return Response(
                    message="\n".join(response_parts),
                    break_loop=False
                )
            
            # Show discovered functions
            response_parts.append("## Recommended Functions")
            
            for i, func in enumerate(functions[:limit], 1):
                response_parts.append(f"### {i}. {func.name}")
                response_parts.append(f"**App**: {func.app_name}")
                response_parts.append(f"**Category**: {func.category.value}")
                response_parts.append(f"**Description**: {func.description}")
                
                # Show parameters if available
                if func.parameters and isinstance(func.parameters, dict):
                    properties = func.parameters.get("properties", {})
                    if properties:
                        response_parts.append("**Parameters**:")
                        for param_name, param_info in list(properties.items())[:5]:  # Limit to 5 params
                            param_type = param_info.get("type", "string")
                            param_desc = param_info.get("description", "")
                            required = param_name in func.parameters.get("required", [])
                            req_marker = " (required)" if required else ""
                            response_parts.append(f"- `{param_name}` ({param_type}){req_marker}: {param_desc}")
                
                response_parts.append("")
            
            # Add usage examples
            response_parts.append("## Usage Examples")
            
            if functions:
                example_func = functions[0]
                response_parts.append("### Direct Function Call")
                response_parts.append("```json")
                response_parts.append("{")
                response_parts.append('    "tool_name": "aci_function",')
                response_parts.append('    "tool_args": {')
                response_parts.append(f'        "function_name": "{example_func.name}",')
                response_parts.append('        "function_arguments": {')
                
                # Add example parameters
                if example_func.parameters and isinstance(example_func.parameters, dict):
                    properties = example_func.parameters.get("properties", {})
                    required_params = example_func.parameters.get("required", [])
                    
                    example_params = []
                    for param_name, param_info in properties.items():
                        if param_name in required_params:
                            param_type = param_info.get("type", "string")
                            if param_type == "string":
                                example_params.append(f'            "{param_name}": "your_value_here"')
                            elif param_type == "integer":
                                example_params.append(f'            "{param_name}": 10')
                            elif param_type == "boolean":
                                example_params.append(f'            "{param_name}": true')
                            else:
                                example_params.append(f'            "{param_name}": "value"')
                    
                    if example_params:
                        response_parts.extend(example_params[:3])  # Limit to 3 examples
                
                response_parts.append('        }')
                response_parts.append('    }')
                response_parts.append('}')
                response_parts.append("```")
            
            response_parts.append("")
            response_parts.append("### Meta Function Search")
            response_parts.append("For dynamic discovery during execution:")
            response_parts.append("```json")
            response_parts.append("{")
            response_parts.append('    "tool_name": "aci_function",')
            response_parts.append('    "tool_args": {')
            response_parts.append('        "function_name": "ACI_SEARCH_FUNCTIONS",')
            response_parts.append('        "function_arguments": {')
            response_parts.append(f'            "intent": "{query}",')
            response_parts.append('            "limit": 5')
            response_parts.append('        }')
            response_parts.append('    }')
            response_parts.append('}')
            response_parts.append("```")
            
            return Response(
                message="\n".join(response_parts),
                break_loop=False
            )
            
        except Exception as e:
            PrintStyle(font_color="#FF6B6B", bold=True).print(
                f"ACI Discovery error: {str(e)}"
            )
            return Response(
                message=f"Error during ACI function discovery: {str(e)}",
                break_loop=False
            )
    
    def _get_usage_help(self) -> str:
        """Get usage help for the ACI discovery tool"""
        return """# ACI Function Discovery Tool

Discover and get recommendations for ACI functions based on natural language queries.

## Usage Examples

### Basic Discovery
```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "search the web for information"
    }
}
```

### Category-Filtered Discovery
```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "send a message",
        "category": "communication",
        "limit": 5
    }
}
```

### App-Specific Discovery
```json
{
    "tool_name": "aci_discover",
    "tool_args": {
        "query": "search",
        "app_names": ["BRAVE_SEARCH", "TAVILY"],
        "limit": 3
    }
}
```

## Available Categories
- **search**: Web search, information retrieval
- **browser**: Web browsing, scraping, navigation
- **communication**: Messaging, email, chat
- **productivity**: Calendar, notes, task management
- **development**: Code, version control, project tools
- **data**: Database, API, analytics tools
- **ai**: AI models, language processing
- **file**: File management, storage
- **system**: System operations, utilities

## Parameters
- **query** (required): Natural language description of what you want to do
- **category** (optional): Filter by tool category
- **limit** (optional): Maximum number of results (default: 10)
- **app_names** (optional): List of specific app names to filter by

The tool will return relevant ACI functions with usage examples and parameter information."""
