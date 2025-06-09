"""
ACI Unified Tool Interface

Provides direct access to ACI's 600+ tools via the official ACI Python SDK,
offering intelligent function discovery, execution, and management.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from python.helpers.print_style import PrintStyle

try:
    from aci import ACI
    from aci.types.enums import FunctionDefinitionFormat
    from aci.types.functions import FunctionExecutionResult
    ACI_AVAILABLE = True
except ImportError:
    ACI_AVAILABLE = False
    PrintStyle(font_color="#FFA500").print(
        "ACI SDK not available. Install with: pip install aci-sdk"
    )


class ACIToolCategory(Enum):
    """ACI tool categories for organization"""
    SEARCH = "search"
    BROWSER = "browser"
    COMMUNICATION = "communication"
    PRODUCTIVITY = "productivity"
    DEVELOPMENT = "development"
    DATA = "data"
    AI = "ai"
    FILE = "file"
    SYSTEM = "system"


@dataclass
class ACIFunctionInfo:
    """Information about an ACI function"""
    name: str
    description: str
    category: ACIToolCategory
    app_name: str
    parameters: Dict[str, Any]


class ACIInterface:
    """
    ACI Unified Tool Interface
    
    Provides direct access to ACI's unified tool ecosystem using the official
    ACI Python SDK, offering:
    - Direct function execution (600+ tools)
    - Intelligent tool discovery and categorization
    - Unified authentication and error handling
    - Performance optimization and caching
    """
    
    def __init__(self):
        self.api_key = os.getenv("ACI_API_KEY", "")
        self.base_url = os.getenv("ACI_BASE_URL", "https://api.aci.dev")
        self.enabled = os.getenv("ACI_TOOLS_ENABLED", "true").lower() == "true"
        self.linked_account_owner_id = os.getenv("ACI_LINKED_ACCOUNT_OWNER_ID", "agent_zero_user")
        
        # ACI client
        self.client: Optional[ACI] = None
        
        # Function cache
        self.functions_cache: Dict[str, ACIFunctionInfo] = {}
        self.cache_ttl = 300  # 5 minutes
        self.last_discovery_time = 0.0
        
        PrintStyle(font_color="#4A90E2", bold=True).print(
            f"ACI Interface initialized - Enabled: {self.enabled}, SDK Available: {ACI_AVAILABLE}"
        )
    
    def is_enabled(self) -> bool:
        """Check if ACI interface is enabled and configured"""
        return (self.enabled and 
                ACI_AVAILABLE and 
                bool(self.api_key) and 
                bool(self.linked_account_owner_id))
    
    def initialize(self) -> bool:
        """
        Initialize the ACI client
        
        Returns:
            True if initialization successful
        """
        if not ACI_AVAILABLE:
            PrintStyle(font_color="#FFA500").print("ACI SDK not available")
            return False
        
        if not self.enabled:
            PrintStyle(font_color="#FFA500").print("ACI Interface disabled")
            return False
        
        if not self.api_key:
            PrintStyle(font_color="#FFA500").print(
                "ACI API key not found. Set ACI_API_KEY environment variable."
            )
            return False
        
        try:
            # Initialize ACI client
            self.client = ACI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            PrintStyle(font_color="#4A90E2", bold=True).print(
                "ACI Interface ready for function execution"
            )
            return True
            
        except Exception as e:
            PrintStyle(font_color="#FF6B6B", bold=True).print(
                f"ACI Interface initialization failed: {str(e)}"
            )
            return False
    
    def discover_functions(self, intent: str = "", app_names: Optional[List[str]] = None, 
                          limit: int = 50, force_refresh: bool = False) -> List[ACIFunctionInfo]:
        """
        Discover available ACI functions
        
        Args:
            intent: Search intent for relevance-based results
            app_names: Filter by specific app names
            limit: Maximum number of functions to return
            force_refresh: Force refresh even if cache is valid
            
        Returns:
            List of ACIFunctionInfo objects
        """
        if not self.is_enabled() or not self.client:
            return []
        
        # Check cache validity
        import time
        current_time = time.time()
        cache_key = f"{intent}:{app_names}:{limit}"
        
        if (not force_refresh and 
            cache_key in self.functions_cache and 
            (current_time - self.last_discovery_time) < self.cache_ttl):
            return list(self.functions_cache.values())
        
        try:
            # Search functions using ACI SDK
            functions_data = self.client.functions.search(
                app_names=app_names,
                intent=intent,
                allowed_apps_only=True,
                format=FunctionDefinitionFormat.OPENAI,
                limit=limit
            )
            
            discovered_functions = []
            for func_data in functions_data:
                func_name = func_data.get("name", "")
                if not func_name:
                    continue
                
                # Extract app name from function name (format: APP_NAME__FUNCTION_NAME)
                app_name = func_name.split("__")[0] if "__" in func_name else "unknown"
                
                # Create function info
                func_info = ACIFunctionInfo(
                    name=func_name,
                    description=func_data.get("description", ""),
                    category=self._categorize_function(func_name, func_data),
                    app_name=app_name,
                    parameters=func_data.get("parameters", {})
                )
                
                discovered_functions.append(func_info)
                self.functions_cache[func_name] = func_info
            
            self.last_discovery_time = current_time
            
            PrintStyle(font_color="#4A90E2").print(
                f"ACI function discovery complete: {len(discovered_functions)} functions found"
            )
            
            return discovered_functions
            
        except Exception as e:
            PrintStyle(font_color="#FF6B6B", bold=True).print(
                f"ACI function discovery failed: {str(e)}"
            )
            return []
    
    def _categorize_function(self, func_name: str, func_data: Dict[str, Any]) -> ACIToolCategory:
        """Categorize a function based on its name and metadata"""
        name_lower = func_name.lower()
        description_lower = func_data.get("description", "").lower()
        
        # Category mapping based on function name patterns
        category_patterns = {
            ACIToolCategory.SEARCH: ["search", "google", "bing", "serp", "web_search", "brave", "tavily"],
            ACIToolCategory.BROWSER: ["browser", "web", "scrape", "crawl", "navigate", "screenshot", "playwright"],
            ACIToolCategory.COMMUNICATION: ["slack", "discord", "email", "teams", "chat", "message", "sms", "gmail"],
            ACIToolCategory.PRODUCTIVITY: ["calendar", "notion", "airtable", "trello", "sheets", "docs", "drive"],
            ACIToolCategory.DEVELOPMENT: ["github", "gitlab", "jira", "linear", "code", "git", "deploy", "docker"],
            ACIToolCategory.DATA: ["database", "sql", "api", "webhook", "json", "csv", "analytics", "postgres"],
            ACIToolCategory.AI: ["openai", "anthropic", "cohere", "huggingface", "llm", "gpt", "claude", "gemini"],
            ACIToolCategory.FILE: ["file", "upload", "download", "storage", "s3", "drive", "dropbox", "aws"],
            ACIToolCategory.SYSTEM: ["system", "command", "terminal", "shell", "monitor", "process", "secrets"]
        }
        
        # Check patterns
        for category, patterns in category_patterns.items():
            if any(pattern in name_lower or pattern in description_lower for pattern in patterns):
                return category
        
        # Default category
        return ACIToolCategory.SYSTEM
    
    def execute_function(self, function_name: str, function_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an ACI function directly
        
        Args:
            function_name: Name of the function to execute
            function_arguments: Function arguments
            
        Returns:
            Function execution result
        """
        if not self.is_enabled() or not self.client:
            return {
                "success": False,
                "error": "ACI interface is not enabled or configured",
                "data": None
            }
        
        try:
            # Execute function using ACI SDK
            result: FunctionExecutionResult = self.client.functions.execute(
                function_name=function_name,
                function_arguments=function_arguments,
                linked_account_owner_id=self.linked_account_owner_id
            )
            
            return result.model_dump(exclude_none=True)
            
        except Exception as e:
            error_msg = f"Function execution failed: {str(e)}"
            PrintStyle(font_color="#FF6B6B", bold=True).print(
                f"ACI function execution error for '{function_name}': {error_msg}"
            )
            
            return {
                "success": False,
                "error": error_msg,
                "data": None
            }
    
    def handle_function_call(self, function_name: str, function_arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle function call using ACI's unified handler
        
        Args:
            function_name: Name of the function to call
            function_arguments: Function arguments
            
        Returns:
            Function execution result
        """
        if not self.is_enabled() or not self.client:
            return {
                "success": False,
                "error": "ACI interface is not enabled or configured",
                "data": None
            }
        
        try:
            # Use ACI's unified function call handler
            result = self.client.handle_function_call(
                function_name=function_name,
                function_arguments=function_arguments,
                linked_account_owner_id=self.linked_account_owner_id,
                allowed_apps_only=True,
                format=FunctionDefinitionFormat.OPENAI
            )
            
            # Ensure consistent return format
            if isinstance(result, dict):
                return result
            else:
                return {
                    "success": True,
                    "data": result,
                    "error": None
                }
            
        except Exception as e:
            error_msg = f"Function call failed: {str(e)}"
            PrintStyle(font_color="#FF6B6B", bold=True).print(
                f"ACI function call error for '{function_name}': {error_msg}"
            )
            
            return {
                "success": False,
                "error": error_msg,
                "data": None
            }
    
    def get_function_recommendations(self, query: str, category: Optional[ACIToolCategory] = None, 
                                   limit: int = 5) -> List[str]:
        """
        Get intelligent function recommendations based on query
        
        Args:
            query: Natural language query describing the task
            category: Optional category filter
            limit: Maximum number of recommendations
            
        Returns:
            List of recommended function names
        """
        if not self.is_enabled():
            return []
        
        try:
            # Use ACI's search with intent for intelligent recommendations
            app_names = None
            if category:
                # Map category to common app names
                category_apps = {
                    ACIToolCategory.SEARCH: ["BRAVE_SEARCH", "TAVILY", "GOOGLE_SEARCH"],
                    ACIToolCategory.COMMUNICATION: ["SLACK", "GMAIL", "DISCORD"],
                    ACIToolCategory.DEVELOPMENT: ["GITHUB", "GITLAB", "JIRA"],
                    ACIToolCategory.PRODUCTIVITY: ["NOTION", "AIRTABLE", "GOOGLE_SHEETS"],
                    ACIToolCategory.AI: ["OPENAI", "ANTHROPIC", "HUGGINGFACE"],
                    ACIToolCategory.FILE: ["AWS_S3", "GOOGLE_DRIVE", "DROPBOX"],
                }
                app_names = category_apps.get(category)
            
            functions = self.discover_functions(
                intent=query,
                app_names=app_names,
                limit=limit
            )
            
            return [func.name for func in functions[:limit]]
            
        except Exception as e:
            PrintStyle(font_color="#FF6B6B").print(
                f"Failed to get function recommendations: {str(e)}"
            )
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get ACI interface status"""
        try:
            functions_count = len(self.functions_cache)
            
            return {
                "enabled": self.enabled,
                "sdk_available": ACI_AVAILABLE,
                "configured": bool(self.api_key),
                "client_initialized": self.client is not None,
                "functions_cached": functions_count,
                "linked_account_owner_id": self.linked_account_owner_id,
                "base_url": self.base_url
            }
            
        except Exception as e:
            return {
                "enabled": self.enabled,
                "sdk_available": ACI_AVAILABLE,
                "error": str(e)
            }
