from datetime import datetime
from typing import Any
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


class ACIHealthMonitor(Extension):
    """
    Monitor ACI service health and handle graceful degradation.
    Complements the direct ACI integration from Phase 1, Agent 3.
    """
    
    HEALTH_CHECK_INTERVAL = 300  # 5 minutes
    
    def __init__(self, agent):
        super().__init__(agent)
        self.last_health_check = 0
        self.aci_healthy = True
        self.consecutive_failures = 0
        self.max_consecutive_failures = 3
        
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs: Any):
        # Only execute if ACI tools are enabled
        if not self.agent.config.additional.get('aci_tools', False):
            return
            
        # Check if health checks are enabled
        if not self.agent.config.additional.get('health_checks_enabled', True):
            return
            
        current_time = time.time()
        
        # Check health periodically
        if current_time - self.last_health_check > self.HEALTH_CHECK_INTERVAL:
            # Run health check in background to avoid blocking
            asyncio.create_task(self._check_aci_health())
            self.last_health_check = current_time
        
        # Always set current health status for tools to check
        self.agent.set_data("aci_healthy", self.aci_healthy)
    
    async def _check_aci_health(self):
        """Check ACI service health"""
        try:
            if not ACI_INTERFACE_AVAILABLE:
                await self._handle_health_change(False, "ACI interface not available")
                return
            
            # Check if ACI interface is enabled
            if not hasattr(aci_interface, 'is_enabled') or not aci_interface.is_enabled():
                await self._handle_health_change(False, "ACI interface is disabled")
                return
            
            # Test basic ACI connectivity
            health_status = await self._test_aci_connectivity()
            
            if health_status:
                await self._handle_health_change(True, "ACI service is healthy")
                self.consecutive_failures = 0
            else:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.max_consecutive_failures:
                    await self._handle_health_change(False, f"ACI service failed {self.consecutive_failures} consecutive health checks")
                
        except Exception as e:
            self.consecutive_failures += 1
            if self.consecutive_failures >= self.max_consecutive_failures:
                await self._handle_health_change(False, f"ACI health check exception: {e}")
    
    async def _test_aci_connectivity(self) -> bool:
        """Test ACI connectivity with a simple operation"""
        try:
            # If aci_interface has a test method, use it
            if hasattr(aci_interface, 'test_connection'):
                return await aci_interface.test_connection()
            
            # Otherwise, check if the interface is properly configured
            if hasattr(aci_interface, 'client') and aci_interface.client:
                return True
            
            # Basic check - if interface exists and is enabled, assume healthy
            return hasattr(aci_interface, 'is_enabled') and aci_interface.is_enabled()
            
        except Exception as e:
            PrintStyle(font_color="yellow", padding=True).print(
                f"⚠ ACI connectivity test failed: {e}"
            )
            return False
    
    async def _handle_health_change(self, is_healthy: bool, message: str):
        """Handle changes in ACI health status"""
        if is_healthy != self.aci_healthy:
            # Health status changed
            if is_healthy:
                # ACI recovered
                PrintStyle(font_color="green", padding=True).print(
                    f"✓ ACI service recovered: {message}"
                )
                self.agent.context.log.log(
                    type="info",
                    content=f"ACI service recovered: {message}"
                )
            else:
                # ACI went down
                PrintStyle(font_color="yellow", padding=True).print(
                    f"⚠ ACI service unhealthy: {message}"
                )
                self.agent.context.log.log(
                    type="warning",
                    content=f"ACI service unhealthy, falling back to legacy tools: {message}"
                )
            
            self.aci_healthy = is_healthy
        
        # Update health status and timestamp
        health_data = {
            "healthy": is_healthy,
            "message": message,
            "last_check": datetime.now().isoformat(),
            "consecutive_failures": self.consecutive_failures
        }
        
        self.agent.set_data("aci_health_status", health_data)
    
    def get_health_status(self) -> dict:
        """Get current health status"""
        return {
            "healthy": self.aci_healthy,
            "last_check": datetime.fromtimestamp(self.last_health_check).isoformat() if self.last_health_check > 0 else None,
            "consecutive_failures": self.consecutive_failures,
            "max_consecutive_failures": self.max_consecutive_failures,
            "health_check_interval": self.HEALTH_CHECK_INTERVAL,
            "aci_interface_available": ACI_INTERFACE_AVAILABLE
        }
    
    def force_health_check(self):
        """Force an immediate health check"""
        self.last_health_check = 0  # Reset timer to force check on next execution
        PrintStyle(font_color="blue", padding=True).print("🔄 Forcing ACI health check...")
    
    def reset_failure_count(self):
        """Reset consecutive failure count"""
        self.consecutive_failures = 0
        PrintStyle(font_color="green", padding=True).print("✓ ACI failure count reset")
    
    def is_healthy(self) -> bool:
        """Quick check if ACI is currently healthy"""
        return self.aci_healthy
    
    def get_health_summary(self) -> str:
        """Get a formatted health summary"""
        status = self.get_health_status()
        
        health_emoji = "✅" if status["healthy"] else "❌"
        interface_emoji = "✅" if status["aci_interface_available"] else "❌"
        
        summary = f"""
ACI Health Status
================
Overall Health: {health_emoji} {'Healthy' if status['healthy'] else 'Unhealthy'}
Interface Available: {interface_emoji} {'Yes' if status['aci_interface_available'] else 'No'}
Consecutive Failures: {status['consecutive_failures']}/{status['max_consecutive_failures']}
Last Check: {status['last_check'] or 'Never'}
Check Interval: {status['health_check_interval']}s
"""
        
        return summary.strip()
