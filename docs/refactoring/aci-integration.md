# ACI Integration Guide

## Overview

This document details how to integrate ACI's standardized tool interface system to replace Agent Zero's custom tool implementations with unified MCP (Model Context Protocol) servers. ACI provides 600+ tools with multi-tenant authentication, granular permissions, and dynamic tool discovery.

## Current Tool System Analysis

### Agent Zero's Current Implementation

Agent Zero uses custom Python tool classes with direct API integrations:

```python
# Current tool structure in python/tools/
class SearchEngine(Tool):
    async def execute(self, query: str, **kwargs):
        # Direct API integration
        api_key = os.getenv("SEARCH_API_KEY")
        response = requests.get(f"https://api.search.com/search?q={query}")
        return Response(message=response.json())

# Tool discovery in agent.py
def get_tool(self, name: str, method: str | None, args: dict, message: str):
    classes = extract_tools.load_classes_from_folder(
        "python/tools", name + ".py", Tool
    )
    tool_class = classes[0] if classes else Unknown
    return tool_class(agent=self, name=name, ...)
```

### Current Tool Flow
1. **Discovery**: Load tool classes from python/tools/ directory
2. **Instantiation**: Create tool instance with agent context
3. **Execution**: Direct API calls with custom error handling
4. **Authentication**: Individual API key management per tool
5. **Response**: Custom response formatting per tool

### Limitations
- Duplicate API client implementations
- Inconsistent error handling and retry logic
- Manual authentication management
- No centralized rate limiting
- Limited tool discovery and metadata
- Maintenance overhead for each API integration

## ACI Architecture

### Core Components

#### 1. Unified MCP Server
```python
# ACI provides standardized tool access
MCP_SERVER_URL = "https://api.aci.dev/mcp"
APPS_MCP_SERVER_URL = "https://api.aci.dev/apps/mcp"

# Unified interface for all tools
aci_client = ACIClient(
    api_key="your_aci_api_key",
    project_id="your_project_id"
)
```

#### 2. Tool Categories
```python
# ACI tool organization
TOOL_CATEGORIES = {
    "communication": ["slack", "discord", "email", "teams"],
    "productivity": ["calendar", "notion", "airtable", "trello"],
    "development": ["github", "gitlab", "jira", "linear"],
    "data": ["sheets", "databases", "apis", "webhooks"],
    "ai": ["openai", "anthropic", "cohere", "huggingface"],
    "search": ["google", "bing", "serp", "web_scraping"]
}
```

#### 3. Authentication System
```python
# Multi-tenant authentication
class ACIAuth:
    def __init__(self, api_key: str, project_id: str):
        self.api_key = api_key
        self.project_id = project_id
        self.linked_accounts = {}  # OAuth tokens per service
    
    def get_auth_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Project-ID": self.project_id
        }
```

## Integration Architecture

### 1. ACIToolInterface Class

Replace custom tools with unified ACI interface:

```python
class ACIToolInterface:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.aci_client = self._initialize_aci_client()
        self.tool_registry = {}
        self.tool_metadata = {}
        
    def _initialize_aci_client(self):
        """Initialize ACI client with authentication"""
        return ACIClient(
            api_key=os.getenv("ACI_API_KEY"),
            project_id=os.getenv("ACI_PROJECT_ID"),
            base_url=os.getenv("ACI_BASE_URL", "https://api.aci.dev")
        )
    
    async def discover_tools(self) -> dict:
        """Discover available tools from ACI MCP servers"""
        
        # Get tools from unified MCP server
        unified_tools = await self.aci_client.list_tools(
            server="unified"
        )
        
        # Get app-specific tools
        app_tools = await self.aci_client.list_tools(
            server="apps"
        )
        
        # Combine and organize tools
        all_tools = {**unified_tools, **app_tools}
        
        # Cache tool metadata
        for tool_name, tool_info in all_tools.items():
            self.tool_metadata[tool_name] = tool_info
            
        return all_tools
    
    async def execute_tool(self, tool_name: str, args: dict) -> dict:
        """Execute tool via ACI MCP interface"""
        
        try:
            # Route to appropriate MCP server
            if tool_name in self.get_unified_tools():
                server = "unified"
            else:
                server = "apps"
            
            # Execute tool with authentication and error handling
            result = await self.aci_client.call_tool(
                server=server,
                tool_name=tool_name,
                arguments=args,
                timeout=30
            )
            
            return result
            
        except ACIException as e:
            return self._handle_aci_error(e, tool_name, args)
    
    def _handle_aci_error(self, error: ACIException, tool_name: str, args: dict) -> dict:
        """Standardized error handling for ACI tools"""
        
        if error.status_code == 401:
            return {
                "error": "Authentication failed",
                "message": f"Please check your ACI credentials for {tool_name}",
                "retry": False
            }
        elif error.status_code == 429:
            return {
                "error": "Rate limit exceeded", 
                "message": f"Rate limit hit for {tool_name}, please try again later",
                "retry": True,
                "retry_after": error.retry_after
            }
        else:
            return {
                "error": "Tool execution failed",
                "message": f"Error executing {tool_name}: {error.message}",
                "retry": True
            }
```

### 2. Tool Migration Strategy

#### Replace Individual Tools with Unified Interface
```python
# Replace python/tools/search_engine.py
class UnifiedSearchTool(Tool):
    async def execute(self, query: str, engine: str = "google", **kwargs):
        """Search using ACI unified search interface"""
        
        # Map to ACI tool names
        tool_mapping = {
            "google": "google_search",
            "bing": "bing_search", 
            "serp": "serp_api_search",
            "web": "web_search"
        }
        
        aci_tool = tool_mapping.get(engine, "google_search")
        
        result = await self.agent.aci_interface.execute_tool(
            tool_name=aci_tool,
            args={
                "query": query,
                "num_results": kwargs.get("num_results", 10),
                "safe_search": kwargs.get("safe_search", "moderate")
            }
        )
        
        return Response(message=self._format_search_results(result))

# Replace python/tools/browser.py  
class UnifiedBrowserTool(Tool):
    async def execute(self, url: str, action: str = "get_content", **kwargs):
        """Web browsing using ACI browser tools"""
        
        result = await self.agent.aci_interface.execute_tool(
            tool_name="web_browser",
            args={
                "url": url,
                "action": action,
                "wait_for": kwargs.get("wait_for", "load"),
                "timeout": kwargs.get("timeout", 30)
            }
        )
        
        return Response(message=self._format_browser_result(result))
```

#### Dynamic Tool Registration
```python
class DynamicToolRegistry:
    def __init__(self, aci_interface: ACIToolInterface):
        self.aci_interface = aci_interface
        self.registered_tools = {}
        
    async def register_aci_tools(self):
        """Dynamically register all available ACI tools"""
        
        available_tools = await self.aci_interface.discover_tools()
        
        for tool_name, tool_metadata in available_tools.items():
            # Create dynamic tool class
            tool_class = self._create_dynamic_tool_class(tool_name, tool_metadata)
            self.registered_tools[tool_name] = tool_class
    
    def _create_dynamic_tool_class(self, tool_name: str, metadata: dict):
        """Create tool class dynamically from ACI metadata"""
        
        class DynamicACITool(Tool):
            def __init__(self, agent, **kwargs):
                super().__init__(agent, **kwargs)
                self.tool_name = tool_name
                self.metadata = metadata
            
            async def execute(self, **kwargs):
                # Validate arguments against schema
                validated_args = self._validate_arguments(kwargs)
                
                # Execute via ACI interface
                result = await self.agent.aci_interface.execute_tool(
                    tool_name=self.tool_name,
                    args=validated_args
                )
                
                return Response(message=result)
            
            def _validate_arguments(self, args: dict) -> dict:
                """Validate arguments against tool schema"""
                schema = self.metadata.get("input_schema", {})
                # Implement validation logic
                return args
        
        return DynamicACITool
```

### 3. Authentication Management

#### Centralized Credential Management
```python
class ACIAuthManager:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.aci_client = ACIClient(
            api_key=config.aci_api_key,
            project_id=config.aci_project_id
        )
        self.linked_accounts = {}
        
    async def setup_service_auth(self, service: str, auth_type: str = "oauth"):
        """Setup authentication for specific service"""
        
        if auth_type == "oauth":
            # Initiate OAuth flow
            auth_url = await self.aci_client.get_oauth_url(service)
            print(f"Please visit: {auth_url}")
            
            # Wait for callback or manual token entry
            token = await self._wait_for_oauth_completion(service)
            self.linked_accounts[service] = token
            
        elif auth_type == "api_key":
            # Direct API key configuration
            api_key = input(f"Enter API key for {service}: ")
            await self.aci_client.set_service_credentials(service, api_key)
    
    async def refresh_expired_tokens(self):
        """Refresh expired OAuth tokens"""
        
        for service, token_info in self.linked_accounts.items():
            if self._is_token_expired(token_info):
                new_token = await self.aci_client.refresh_token(
                    service, 
                    token_info["refresh_token"]
                )
                self.linked_accounts[service] = new_token
    
    def get_service_status(self) -> dict:
        """Get authentication status for all services"""
        
        status = {}
        for service in self.aci_client.get_available_services():
            status[service] = {
                "authenticated": service in self.linked_accounts,
                "token_valid": self._is_token_valid(service),
                "last_used": self._get_last_used(service)
            }
        
        return status
```

#### Permission Management
```python
class ACIPermissionManager:
    def __init__(self, auth_manager: ACIAuthManager):
        self.auth_manager = auth_manager
        self.permissions = {}
        
    async def configure_tool_permissions(self, agent_id: str, permissions: dict):
        """Configure which tools an agent can access"""
        
        self.permissions[agent_id] = permissions
        
        # Update ACI project permissions
        await self.auth_manager.aci_client.update_agent_permissions(
            agent_id=agent_id,
            permissions=permissions
        )
    
    def can_use_tool(self, agent_id: str, tool_name: str) -> bool:
        """Check if agent has permission to use specific tool"""
        
        agent_permissions = self.permissions.get(agent_id, {})
        
        # Check explicit permissions
        if tool_name in agent_permissions.get("allowed_tools", []):
            return True
        
        # Check category permissions
        tool_category = self._get_tool_category(tool_name)
        if tool_category in agent_permissions.get("allowed_categories", []):
            return True
        
        # Check denied tools
        if tool_name in agent_permissions.get("denied_tools", []):
            return False
        
        # Default permission based on agent role
        return agent_permissions.get("default_permission", False)
```

### 4. Tool Execution Engine

#### Unified Execution Interface
```python
class ACIExecutionEngine:
    def __init__(self, aci_interface: ACIToolInterface):
        self.aci_interface = aci_interface
        self.execution_queue = asyncio.Queue()
        self.rate_limiter = RateLimiter()
        self.retry_handler = RetryHandler()
        
    async def execute_tool_request(self, request: ToolRequest) -> ToolResponse:
        """Execute tool request with full error handling and retry logic"""
        
        # Rate limiting
        await self.rate_limiter.acquire(request.tool_name)
        
        try:
            # Execute with retry logic
            result = await self.retry_handler.execute_with_retry(
                self._execute_single_request,
                request,
                max_retries=3
            )
            
            return ToolResponse(
                success=True,
                data=result,
                execution_time=result.get("execution_time"),
                tool_name=request.tool_name
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                error=str(e),
                tool_name=request.tool_name
            )
        
        finally:
            self.rate_limiter.release(request.tool_name)
    
    async def _execute_single_request(self, request: ToolRequest):
        """Execute single tool request"""
        
        start_time = time.time()
        
        result = await self.aci_interface.execute_tool(
            tool_name=request.tool_name,
            args=request.args
        )
        
        execution_time = time.time() - start_time
        result["execution_time"] = execution_time
        
        return result

class RateLimiter:
    def __init__(self):
        self.tool_limits = {}
        self.current_usage = {}
        
    async def acquire(self, tool_name: str):
        """Acquire rate limit slot for tool"""
        
        limit = self.tool_limits.get(tool_name, 60)  # Default 60/min
        current = self.current_usage.get(tool_name, 0)
        
        if current >= limit:
            wait_time = self._calculate_wait_time(tool_name)
            await asyncio.sleep(wait_time)
        
        self.current_usage[tool_name] = current + 1
    
    def release(self, tool_name: str):
        """Release rate limit slot"""
        
        if tool_name in self.current_usage:
            self.current_usage[tool_name] -= 1

class RetryHandler:
    def __init__(self):
        self.retry_strategies = {
            "rate_limit": ExponentialBackoff(base_delay=1, max_delay=60),
            "network_error": FixedDelay(delay=5),
            "auth_error": NoRetry()
        }
    
    async def execute_with_retry(self, func, *args, max_retries: int = 3):
        """Execute function with appropriate retry strategy"""
        
        last_exception = None
        
        for attempt in range(max_retries + 1):
            try:
                return await func(*args)
                
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries:
                    break
                
                error_type = self._classify_error(e)
                strategy = self.retry_strategies.get(error_type, NoRetry())
                
                if not strategy.should_retry(attempt):
                    break
                
                await asyncio.sleep(strategy.get_delay(attempt))
        
        raise last_exception
```

### 5. Tool Discovery and Metadata

#### Dynamic Tool Discovery
```python
class ACIToolDiscovery:
    def __init__(self, aci_interface: ACIToolInterface):
        self.aci_interface = aci_interface
        self.tool_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
    async def discover_and_cache_tools(self):
        """Discover all available tools and cache metadata"""
        
        tools = await self.aci_interface.discover_tools()
        
        self.tool_cache = {
            "tools": tools,
            "timestamp": time.time(),
            "categories": self._categorize_tools(tools),
            "search_index": self._build_search_index(tools)
        }
        
        return tools
    
    def search_tools(self, query: str, category: str = None) -> List[dict]:
        """Search for tools by name, description, or capability"""
        
        if not self._is_cache_valid():
            asyncio.create_task(self.discover_and_cache_tools())
        
        results = []
        search_terms = query.lower().split()
        
        for tool_name, tool_info in self.tool_cache["tools"].items():
            if category and tool_info.get("category") != category:
                continue
            
            # Score tool based on search terms
            score = self._calculate_relevance_score(tool_info, search_terms)
            
            if score > 0.3:  # Relevance threshold
                results.append({
                    "name": tool_name,
                    "score": score,
                    "metadata": tool_info
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)
    
    def get_tool_documentation(self, tool_name: str) -> dict:
        """Get comprehensive documentation for a tool"""
        
        if tool_name not in self.tool_cache["tools"]:
            return {"error": "Tool not found"}
        
        tool_info = self.tool_cache["tools"][tool_name]
        
        return {
            "name": tool_name,
            "description": tool_info.get("description", ""),
            "input_schema": tool_info.get("input_schema", {}),
            "output_schema": tool_info.get("output_schema", {}),
            "examples": tool_info.get("examples", []),
            "rate_limits": tool_info.get("rate_limits", {}),
            "authentication": tool_info.get("authentication", {}),
            "category": tool_info.get("category", "general")
        }
```

## Implementation Steps

### Step 1: Setup ACI Client
```python
# python/helpers/aci_client.py
class ACIClient:
    def __init__(self, api_key: str, project_id: str, base_url: str):
        self.api_key = api_key
        self.project_id = project_id
        self.base_url = base_url
        self.session = aiohttp.ClientSession()
    
    async def list_tools(self, server: str = "unified") -> dict:
        """List available tools from ACI MCP server"""
        
    async def call_tool(self, server: str, tool_name: str, 
                       arguments: dict, timeout: int = 30) -> dict:
        """Execute tool via ACI MCP interface"""
```

### Step 2: Create ACIToolInterface
```python
# python/helpers/aci_interface.py
class ACIToolInterface:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.client = ACIClient(
            api_key=agent.config.aci_api_key,
            project_id=agent.config.aci_project_id,
            base_url=agent.config.aci_base_url
        )
```

### Step 3: Update Agent Class
```python
# agent.py modifications
class Agent:
    def __init__(self, number: int, config: AgentConfig, 
                 context: AgentContext | None = None):
        # ... existing initialization ...
        
        # Add ACI interface
        self.aci_interface = ACIToolInterface(self)
        self.tool_discovery = ACIToolDiscovery(self.aci_interface)
```

### Step 4: Replace Tool Discovery
```python
# Modify get_tool method in agent.py
def get_tool(self, name: str, method: str | None, args: dict, message: str):
    # Check if it's an ACI tool first
    if self.aci_interface.is_aci_tool(name):
        return ACITool(
            agent=self,
            tool_name=name,
            args=args,
            message=message
        )
    
    # Fallback to legacy tools
    return self._get_legacy_tool(name, method, args, message)
```

## Configuration

### Environment Variables
```bash
# .env additions for ACI
ACI_API_KEY=your_aci_api_key
ACI_PROJECT_ID=your_project_id
ACI_BASE_URL=https://api.aci.dev
ACI_UNIFIED_MCP_URL=https://api.aci.dev/mcp
ACI_APPS_MCP_URL=https://api.aci.dev/apps/mcp
ACI_RATE_LIMIT_ENABLED=true
ACI_RETRY_ENABLED=true
ACI_CACHE_TTL=3600
```

### Agent Configuration
```python
# AgentConfig additions
@dataclass
class AgentConfig:
    # ... existing fields ...
    
    # ACI configuration
    aci_api_key: str = ""
    aci_project_id: str = ""
    aci_base_url: str = "https://api.aci.dev"
    aci_rate_limit_enabled: bool = True
    aci_retry_enabled: bool = True
    aci_cache_ttl: int = 3600
    aci_max_retries: int = 3
    aci_timeout: int = 30
```

This integration replaces Agent Zero's fragmented tool ecosystem with ACI's unified, authenticated, and scalable tool interface, providing access to 600+ tools through standardized MCP servers with enterprise-grade reliability and security.
