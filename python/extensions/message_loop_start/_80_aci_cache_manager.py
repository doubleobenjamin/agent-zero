from datetime import datetime
from typing import Any, Dict, Optional
from python.helpers.extension import Extension
from agent import LoopData
from python.helpers.print_style import PrintStyle
import hashlib
import json
import time

# Check if ACI interface is available (from Phase 1, Agent 3)
try:
    from python.helpers.aci_interface import aci_interface
    ACI_INTERFACE_AVAILABLE = True
except ImportError:
    ACI_INTERFACE_AVAILABLE = False


class ACICacheManager(Extension):
    """
    Intelligent caching for ACI function calls to reduce API costs.
    Complements the direct ACI integration from Phase 1, Agent 3.
    """
    
    CACHE_TTL = 3600  # 1 hour default TTL
    MAX_CACHE_SIZE = 1000
    
    def __init__(self, agent):
        super().__init__(agent)
        self.cache: Dict[str, Dict[str, Any]] = {}
        
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs: Any):
        # Only execute if ACI tools are enabled
        if not self.agent.config.additional.get('aci_tools_enabled', False):
            return
            
        # Check if caching is enabled
        if not self.agent.config.additional.get('enable_caching', True):
            return
            
        # Check if ACI interface is available
        if not ACI_INTERFACE_AVAILABLE:
            return
            
        try:
            # Clean expired cache entries
            await self._cleanup_cache()
            
            # Set cache manager on agent for tools to use
            self.agent.set_data("aci_cache_manager", self)
            
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ ACI cache manager warning: {e}"
            )
    
    def get_cache_key(self, function_name: str, arguments: dict) -> str:
        """Generate cache key for function call"""
        cache_data = {
            'function': function_name,
            'args': arguments
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def get_cached_result(self, function_name: str, arguments: dict) -> Optional[Any]:
        """Get cached result if available and not expired"""
        cache_key = self.get_cache_key(function_name, arguments)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            cache_ttl = self.agent.config.additional.get('cache_ttl', self.CACHE_TTL)
            
            if time.time() - entry['timestamp'] < cache_ttl:
                # Update access time for LRU
                entry['last_accessed'] = time.time()
                return entry['result']
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        
        return None
    
    def cache_result(self, function_name: str, arguments: dict, result: Any):
        """Cache function result"""
        cache_key = self.get_cache_key(function_name, arguments)
        
        # Implement cache size limit
        if len(self.cache) >= self.MAX_CACHE_SIZE:
            # Remove oldest entry (LRU)
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k].get('last_accessed', 0))
            del self.cache[oldest_key]
        
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time(),
            'last_accessed': time.time(),
            'function': function_name
        }
    
    async def _cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        cache_ttl = self.agent.config.additional.get('cache_ttl', self.CACHE_TTL)
        
        expired_keys = [
            key for key, entry in self.cache.items()
            if current_time - entry['timestamp'] > cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.MAX_CACHE_SIZE,
            "cache_ttl": self.agent.config.additional.get('cache_ttl', self.CACHE_TTL),
            "cache_enabled": self.agent.config.additional.get('enable_caching', True),
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_cache(self):
        """Clear all cached entries"""
        self.cache.clear()
        PrintStyle(font_color="green", padding=True).print("✓ ACI cache cleared")
    
    def is_cacheable_function(self, function_name: str) -> bool:
        """Determine if a function result should be cached"""
        # Don't cache functions that modify state or are time-sensitive
        non_cacheable_patterns = [
            'send_email', 'create_', 'delete_', 'update_', 'post_',
            'current_time', 'random_', 'generate_token'
        ]
        
        function_lower = function_name.lower()
        return not any(pattern in function_lower for pattern in non_cacheable_patterns)
