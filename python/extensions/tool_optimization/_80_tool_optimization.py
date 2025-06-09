from datetime import datetime
from typing import Any, Dict
from python.helpers.extension import Extension
from agent import LoopData
from python.helpers.print_style import PrintStyle
import asyncio
import time

# Check if ACI interface is available (from Phase 1, Agent 3)
try:
    from python.helpers.aci_interface import aci_interface
    ACI_INTERFACE_AVAILABLE = True
except ImportError:
    ACI_INTERFACE_AVAILABLE = False


class ACIInfrastructure(Extension):
    """
    Infrastructure support for ACI tools - monitoring, caching, health checks.
    Complements the direct ACI integration from Phase 1, Agent 3.
    """

    def __init__(self, agent):
        super().__init__(agent)
        self.performance_metrics = {}
        self.cache = {}
        self.last_health_check = 0

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs: Any):
        # Only execute if ACI tools are enabled
        if not self.agent.config.additional.get('aci_tools_enabled', False):
            return

        # Check if ACI interface is available
        if not ACI_INTERFACE_AVAILABLE:
            if self.agent.config.additional.get('graceful_degradation', True):
                PrintStyle(font_color="yellow", padding=True).print(
                    "⚠ ACI interface not available from Phase 1, Agent 3"
                )
                return
            else:
                raise ImportError("ACI interface not available from Phase 1, Agent 3")

        try:
            # Background infrastructure tasks - don't block execution
            asyncio.create_task(self._monitor_performance(loop_data))
            asyncio.create_task(self._health_check())
            asyncio.create_task(self._manage_cache())

        except Exception as e:
            # Graceful degradation - log error but don't break the flow
            if self.agent.config.additional.get('graceful_degradation', True):
                PrintStyle(font_color="yellow", padding=True).print(
                    f"⚠ ACI infrastructure warning: {e}"
                )
            else:
                raise

    async def _monitor_performance(self, loop_data: LoopData):
        """Monitor ACI tool performance in background"""
        try:
            # Check if there are any ACI tools being used
            if not hasattr(loop_data, 'tool_calls'):
                return

            aci_tools_used = []
            for tool_call in getattr(loop_data, 'tool_calls', []):
                tool_name = tool_call.get('name', '')
                if "__" in tool_name or tool_name.startswith('aci_'):
                    aci_tools_used.append({
                        'name': tool_name,
                        'execution_time': tool_call.get('execution_time', 0),
                        'success': tool_call.get('success', False),
                        'timestamp': datetime.now().isoformat()
                    })

            if aci_tools_used:
                # Store performance metrics for analysis
                self.performance_metrics[datetime.now().isoformat()] = aci_tools_used

                # Keep only last 100 entries to prevent memory bloat
                if len(self.performance_metrics) > 100:
                    oldest_key = min(self.performance_metrics.keys())
                    del self.performance_metrics[oldest_key]

        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ Performance monitoring failed: {e}"
            )

    async def _health_check(self):
        """Perform health check on ACI interface"""
        try:
            current_time = time.time()

            # Only check every 5 minutes
            if current_time - self.last_health_check < 300:
                return

            self.last_health_check = current_time

            # Test ACI interface health
            if hasattr(aci_interface, 'is_enabled') and aci_interface.is_enabled():
                # Store health status for tools to check
                self.agent.set_data("aci_healthy", True)
            else:
                self.agent.set_data("aci_healthy", False)
                PrintStyle(font_color="yellow", padding=True).print(
                    "⚠ ACI interface appears to be disabled"
                )

        except Exception as e:
            self.agent.set_data("aci_healthy", False)
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ ACI health check failed: {e}"
            )

    async def _manage_cache(self):
        """Manage cache cleanup and optimization"""
        try:
            current_time = time.time()
            cache_ttl = self.agent.config.additional.get('cache_ttl', 3600)

            # Clean expired cache entries
            expired_keys = []
            for key, entry in self.cache.items():
                if current_time - entry.get('timestamp', 0) > cache_ttl:
                    expired_keys.append(key)

            for key in expired_keys:
                del self.cache[key]

            # Limit cache size
            max_cache_size = 1000
            if len(self.cache) > max_cache_size:
                # Remove oldest entries
                sorted_items = sorted(
                    self.cache.items(),
                    key=lambda x: x[1].get('timestamp', 0)
                )
                items_to_remove = len(self.cache) - max_cache_size
                for i in range(items_to_remove):
                    del self.cache[sorted_items[i][0]]

        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ Cache management failed: {e}"
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get summary of ACI tool performance metrics"""
        if not self.performance_metrics:
            return {"status": "no_data"}

        total_calls = 0
        successful_calls = 0
        total_time = 0

        for timestamp, tools in self.performance_metrics.items():
            for tool in tools:
                total_calls += 1
                if tool.get('success', False):
                    successful_calls += 1
                total_time += tool.get('execution_time', 0)

        return {
            "total_calls": total_calls,
            "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
            "average_execution_time": total_time / total_calls if total_calls > 0 else 0,
            "cache_size": len(self.cache),
            "last_updated": datetime.now().isoformat()
        }
