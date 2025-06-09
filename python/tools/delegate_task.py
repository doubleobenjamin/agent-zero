"""
Enhanced Task Delegation Tool
Replaces call_subordinate with intelligent Agno-based orchestration
"""

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle


class DelegateTask(Tool):
    """Advanced task delegation to specialist agents and teams"""
    
    async def execute(self, task: str, task_type: str = "general", 
                     coordination_mode: str = "auto", agents: list = None,
                     priority: str = "normal", **kwargs):
        """
        Delegate task using intelligent orchestration
        
        Args:
            task: Detailed task description and requirements
            task_type: Domain hint (coding, research, analysis, writing, etc.)
            coordination_mode: "auto", "route", "coordinate", "collaborate"
            agents: Optional specific agent list
            priority: "low", "normal", "high", "urgent"
        """
        
        try:
            # Check if orchestration system is available
            if not hasattr(self.agent, 'agno_orchestrator') or not self.agent.agno_orchestrator:
                PrintStyle.standard("Orchestration system not available, using fallback delegation")
                return await self._fallback_delegation(task)
            
            if not self.agent.agno_orchestrator.is_available():
                PrintStyle.standard("Orchestration components not fully initialized, using fallback")
                return await self._fallback_delegation(task)
            
            # Validate parameters
            valid_coordination_modes = ["auto", "route", "coordinate", "collaborate"]
            if coordination_mode not in valid_coordination_modes:
                PrintStyle.error(f"Invalid coordination mode: {coordination_mode}. Using 'auto'")
                coordination_mode = "auto"
            
            valid_priorities = ["low", "normal", "high", "urgent"]
            if priority not in valid_priorities:
                PrintStyle.error(f"Invalid priority: {priority}. Using 'normal'")
                priority = "normal"
            
            # Log delegation attempt
            PrintStyle.standard(f"Delegating task with orchestration: {task[:100]}...")
            PrintStyle.standard(f"Parameters: type={task_type}, mode={coordination_mode}, priority={priority}")
            
            # Delegate through orchestration system
            result = await self.agent.agno_orchestrator.delegate_task(
                task=task,
                task_type=task_type,
                coordination_mode=coordination_mode,
                agents=agents or [],
                priority=priority
            )
            
            if result:
                PrintStyle.standard("Task delegation completed successfully")
                return Response(message=result, break_loop=False)
            else:
                PrintStyle.error("Orchestration delegation failed, using fallback")
                return await self._fallback_delegation(task)
                
        except Exception as e:
            PrintStyle.error(f"Delegation error: {e}")
            return await self._fallback_delegation(task)
    
    async def _fallback_delegation(self, task: str):
        """Fallback to original call_subordinate behavior"""
        
        try:
            from agent import Agent, UserMessage
            
            # Create subordinate agent using the original pattern
            if (
                self.agent.get_data(Agent.DATA_NAME_SUBORDINATE) is None
            ):
                sub = Agent(
                    self.agent.number + 1, 
                    self.agent.config, 
                    self.agent.context
                )
                sub.set_data(Agent.DATA_NAME_SUPERIOR, self.agent)
                self.agent.set_data(Agent.DATA_NAME_SUBORDINATE, sub)
            
            # Add user message to subordinate agent
            subordinate: Agent = self.agent.get_data(Agent.DATA_NAME_SUBORDINATE)
            subordinate.hist_add_user_message(UserMessage(message=task, attachments=[]))
            
            # Run subordinate monologue
            result = await subordinate.monologue()
            
            return Response(message=result, break_loop=False)
            
        except Exception as e:
            error_msg = f"Both orchestration and fallback delegation failed: {e}"
            PrintStyle.error(error_msg)
            return Response(message=error_msg, break_loop=False)


# Maintain backward compatibility with original call_subordinate
class Delegation(DelegateTask):
    """Backward compatibility alias for original call_subordinate tool"""
    
    async def execute(self, message="", reset="", **kwargs):
        """
        Backward compatible execute method
        
        Args:
            message: Task message (maps to 'task' parameter)
            reset: Reset subordinate (ignored in new system)
        """
        
        # Map old parameters to new system
        task = message or "Please help with the current task"
        
        # If reset is requested, we'll still delegate but won't maintain subordinate state
        if str(reset).lower().strip() == "true":
            PrintStyle.standard("Reset requested - creating fresh delegation")
        
        # Delegate using new system
        return await super().execute(
            task=task,
            task_type="general",
            coordination_mode="auto"
        )


# Alternative class name for flexibility
class CallSubordinate(Delegation):
    """Alternative name for backward compatibility"""
    pass
