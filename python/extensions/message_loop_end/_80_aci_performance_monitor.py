from datetime import datetime, timedelta
from typing import Any, Dict, List
from python.helpers.extension import Extension
from agent import LoopData
from python.helpers.print_style import PrintStyle
import json
import os
import time

# Check if ACI interface is available (from Phase 1, Agent 3)
try:
    from python.helpers.aci_interface import aci_interface
    ACI_INTERFACE_AVAILABLE = True
except ImportError:
    ACI_INTERFACE_AVAILABLE = False


class ACIPerformanceMonitor(Extension):
    """
    Monitor ACI tool performance, costs, and usage patterns.
    Complements the direct ACI integration from Phase 1, Agent 3.
    """
    
    METRICS_FILE = "data/aci_metrics.json"
    MAX_METRICS_ENTRIES = 1000
    
    def __init__(self, agent):
        super().__init__(agent)
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure data directory exists"""
        os.makedirs("data", exist_ok=True)
    
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs: Any):
        # Only execute if ACI tools are enabled
        if not self.agent.config.additional.get('aci_tools', False):
            return
            
        # Check if performance monitoring is enabled
        if not self.agent.config.additional.get('performance_monitoring', True):
            return
            
        # Check if ACI interface is available
        if not ACI_INTERFACE_AVAILABLE:
            return
            
        try:
            # Collect metrics from completed loop
            await self._collect_loop_metrics(loop_data)
            await self._update_usage_stats()
            await self._check_rate_limits()
            
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ ACI performance monitor warning: {e}"
            )
    
    async def _collect_loop_metrics(self, loop_data: LoopData):
        """Collect performance metrics for ACI tools used in this loop"""
        aci_tools_used = []
        
        # Check for ACI tool usage in loop data
        if hasattr(loop_data, 'tool_calls'):
            for tool_call in loop_data.tool_calls:
                tool_name = tool_call.get('name', '')
                if self._is_aci_tool(tool_name):
                    aci_tools_used.append({
                        'name': tool_name,
                        'execution_time': tool_call.get('execution_time', 0),
                        'success': tool_call.get('success', False),
                        'error': tool_call.get('error', None),
                        'timestamp': datetime.now().isoformat(),
                        'agent_id': self.agent.number,
                        'iteration': loop_data.iteration
                    })
        
        # Also check for ACI tools in agent's tool usage
        if hasattr(self.agent, 'last_tool_calls'):
            for tool_call in getattr(self.agent, 'last_tool_calls', []):
                tool_name = tool_call.get('name', '')
                if self._is_aci_tool(tool_name):
                    aci_tools_used.append({
                        'name': tool_name,
                        'execution_time': tool_call.get('execution_time', 0),
                        'success': tool_call.get('success', False),
                        'error': tool_call.get('error', None),
                        'timestamp': datetime.now().isoformat(),
                        'agent_id': self.agent.number,
                        'iteration': loop_data.iteration
                    })
        
        if aci_tools_used:
            await self._save_metrics(aci_tools_used)
    
    def _is_aci_tool(self, tool_name: str) -> bool:
        """Check if a tool name indicates an ACI tool"""
        return "__" in tool_name or tool_name.startswith('aci_')
    
    async def _save_metrics(self, metrics: List[Dict]):
        """Save metrics to file for analysis"""
        try:
            # Load existing metrics
            existing_metrics = []
            if os.path.exists(self.METRICS_FILE):
                try:
                    with open(self.METRICS_FILE, 'r') as f:
                        existing_metrics = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_metrics = []
            
            # Append new metrics
            existing_metrics.extend(metrics)
            
            # Keep only last MAX_METRICS_ENTRIES entries
            if len(existing_metrics) > self.MAX_METRICS_ENTRIES:
                existing_metrics = existing_metrics[-self.MAX_METRICS_ENTRIES:]
            
            # Save back to file
            with open(self.METRICS_FILE, 'w') as f:
                json.dump(existing_metrics, f, indent=2)
                
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ Failed to save ACI metrics: {e}"
            )
    
    async def _update_usage_stats(self):
        """Update usage statistics"""
        try:
            stats = self.get_usage_statistics()
            
            # Store stats in agent data for other extensions to use
            self.agent.set_data("aci_usage_stats", stats)
            
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ Failed to update usage stats: {e}"
            )
    
    async def _check_rate_limits(self):
        """Check if we're approaching rate limits"""
        try:
            stats = self.get_usage_statistics()
            
            # Check calls per hour
            calls_last_hour = stats.get('calls_last_hour', 0)
            if calls_last_hour > 500:  # Arbitrary threshold
                PrintStyle(font_color="yellow", padding=True).print(
                    f"⚠ High ACI usage: {calls_last_hour} calls in last hour"
                )
            
            # Check error rate
            error_rate = stats.get('error_rate', 0)
            if error_rate > 0.1:  # 10% error rate
                PrintStyle(font_color="yellow", padding=True).print(
                    f"⚠ High ACI error rate: {error_rate:.1%}"
                )
                
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ Failed to check rate limits: {e}"
            )
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        try:
            if not os.path.exists(self.METRICS_FILE):
                return {"status": "no_data"}
            
            with open(self.METRICS_FILE, 'r') as f:
                metrics = json.load(f)
            
            if not metrics:
                return {"status": "no_data"}
            
            # Calculate statistics
            total_calls = len(metrics)
            successful_calls = sum(1 for m in metrics if m.get('success', False))
            total_time = sum(m.get('execution_time', 0) for m in metrics)
            
            # Time-based statistics
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)
            
            calls_last_hour = sum(
                1 for m in metrics 
                if datetime.fromisoformat(m['timestamp']) > hour_ago
            )
            
            calls_last_day = sum(
                1 for m in metrics 
                if datetime.fromisoformat(m['timestamp']) > day_ago
            )
            
            # Tool usage frequency
            tool_usage = {}
            for metric in metrics:
                tool_name = metric.get('name', 'unknown')
                tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1
            
            most_used_tools = sorted(
                tool_usage.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return {
                "total_calls": total_calls,
                "successful_calls": successful_calls,
                "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
                "error_rate": (total_calls - successful_calls) / total_calls if total_calls > 0 else 0,
                "average_execution_time": total_time / total_calls if total_calls > 0 else 0,
                "calls_last_hour": calls_last_hour,
                "calls_last_day": calls_last_day,
                "most_used_tools": most_used_tools,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_performance_report(self) -> str:
        """Get a formatted performance report"""
        stats = self.get_usage_statistics()
        
        if stats.get("status") == "no_data":
            return "No ACI usage data available"
        
        if stats.get("status") == "error":
            return f"Error generating report: {stats.get('error')}"
        
        report = f"""
ACI Performance Report
=====================
Total Calls: {stats['total_calls']}
Success Rate: {stats['success_rate']:.1%}
Average Execution Time: {stats['average_execution_time']:.2f}s
Calls Last Hour: {stats['calls_last_hour']}
Calls Last Day: {stats['calls_last_day']}

Most Used Tools:
"""
        
        for tool, count in stats['most_used_tools']:
            report += f"  {tool}: {count} calls\n"
        
        return report.strip()
