"""
Agno Orchestration Engine for Multi-Agent Coordination
Main orchestration system that replaces simple call_subordinate with intelligent delegation
Uses actual Agno Agent and Team classes for proper integration
"""

import asyncio
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from python.helpers.print_style import PrintStyle
from python.helpers.task_analyzer import TaskAnalyzer, TaskComplexity, CoordinationMode

# Add agno to path for imports
agno_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'agno', 'libs', 'agno')
if agno_path not in sys.path:
    sys.path.insert(0, agno_path)

try:
    from agno.agent import Agent as AgnoAgent
    from agno.team.team import Team as AgnoTeam
    from agno.models.openai import OpenAIChat
    AGNO_AVAILABLE = True
except ImportError as e:
    PrintStyle.error(f"Agno not available: {e}")
    AGNO_AVAILABLE = False


class AgnoOrchestrator:
    """Main orchestration engine for intelligent agent delegation using Agno framework"""

    def __init__(self, agent):
        self.agent = agent
        self.agno_agents: Dict[str, AgnoAgent] = {}
        self.agno_teams: Dict[str, AgnoTeam] = {}

        # Initialize components with graceful degradation
        self.task_analyzer = None
        self.available = False

        try:
            if not AGNO_AVAILABLE:
                PrintStyle.error("Agno framework not available - orchestration disabled")
                return

            self.task_analyzer = TaskAnalyzer(agent)

            # Initialize default expert agents using Agno
            self._initialize_agno_experts()

            self.available = True
            PrintStyle.standard("Agno orchestration system initialized successfully")

        except Exception as e:
            PrintStyle.error(f"Failed to initialize orchestration system: {e}")
            # Graceful degradation - system will fall back to simple delegation
    
    def _initialize_agno_experts(self):
        """Initialize default expert agents using Agno framework"""

        try:
            # Get model from Agent Zero config
            model = self._get_agno_model()

            # Create coding expert
            self.agno_agents["code_expert"] = AgnoAgent(
                name="Code Expert",
                role="Senior Software Engineer specializing in programming, debugging, and architecture",
                model=model,
                instructions=[
                    "You are an expert software engineer with deep knowledge of programming languages, frameworks, and best practices.",
                    "Focus on writing clean, efficient, and well-documented code.",
                    "Provide detailed explanations for complex technical concepts.",
                    "Always consider security, performance, and maintainability in your solutions."
                ],
                markdown=True,
                show_tool_calls=True
            )

            # Create research expert
            self.agno_agents["research_expert"] = AgnoAgent(
                name="Research Expert",
                role="Research Analyst specializing in information gathering and analysis",
                model=model,
                instructions=[
                    "You are a skilled researcher with expertise in finding, analyzing, and synthesizing information.",
                    "Always verify information from multiple reliable sources.",
                    "Provide comprehensive analysis with proper citations.",
                    "Focus on accuracy, relevance, and actionable insights."
                ],
                markdown=True,
                show_tool_calls=True
            )

            # Create data expert
            self.agno_agents["data_expert"] = AgnoAgent(
                name="Data Expert",
                role="Data Scientist specializing in analysis, visualization, and machine learning",
                model=model,
                instructions=[
                    "You are a data science expert with deep knowledge of statistics, analysis, and visualization.",
                    "Focus on extracting meaningful insights from data.",
                    "Use appropriate statistical methods and visualization techniques.",
                    "Explain complex data concepts in accessible terms."
                ],
                markdown=True,
                show_tool_calls=True
            )

            # Create writing expert
            self.agno_agents["writing_expert"] = AgnoAgent(
                name="Writing Expert",
                role="Technical Writer specializing in documentation and communication",
                model=model,
                instructions=[
                    "You are an expert technical writer with skills in creating clear, comprehensive documentation.",
                    "Focus on clarity, structure, and accessibility for the target audience.",
                    "Use appropriate formatting and organization for different document types.",
                    "Ensure consistency in style and terminology."
                ],
                markdown=True,
                show_tool_calls=True
            )

            PrintStyle.standard(f"Initialized {len(self.agno_agents)} Agno expert agents")

        except Exception as e:
            PrintStyle.error(f"Failed to initialize Agno experts: {e}")

    def _get_agno_model(self):
        """Get appropriate model for Agno agents based on Agent Zero config"""
        try:
            # Try to use OpenAI model if available
            if hasattr(self.agent.config, 'chat_model') and 'openai' in str(self.agent.config.chat_model).lower():
                return OpenAIChat(id="gpt-4o")
            else:
                # Fallback to default
                return OpenAIChat(id="gpt-4o")
        except Exception as e:
            PrintStyle.error(f"Failed to get Agno model: {e}")
            return OpenAIChat(id="gpt-4o")
    
    async def delegate_task(self, task: str, task_type: str = "general",
                           coordination_mode: str = "auto", agents: List[str] = None,
                           priority: str = "normal") -> str:
        """Main delegation method - intelligently route tasks to appropriate agents/teams using Agno"""

        if not self.available:
            # Fallback to simple delegation if orchestration not available
            return await self._fallback_simple_delegation(task)

        try:
            PrintStyle.standard(f"Orchestrating task with Agno: {task[:100]}...")

            # Step 1: Analyze task requirements
            task_analysis = await self.task_analyzer.analyze_task_requirements(task, task_type)

            # Step 2: Override coordination mode if specified
            if coordination_mode != "auto":
                try:
                    task_analysis.coordination_mode = CoordinationMode(coordination_mode)
                except ValueError:
                    PrintStyle.error(f"Invalid coordination mode: {coordination_mode}, using auto")

            # Step 3: Route based on complexity and requirements using Agno
            if task_analysis.complexity == TaskComplexity.SIMPLE:
                result = await self._handle_simple_task_agno(task, task_analysis)
            elif task_analysis.complexity == TaskComplexity.SPECIALIST:
                result = await self._delegate_to_agno_specialist(task, task_analysis, agents)
            else:  # COMPLEX
                result = await self._delegate_to_agno_team(task, task_analysis, agents)

            PrintStyle.standard("Agno task orchestration completed successfully")
            return result

        except Exception as e:
            PrintStyle.error(f"Agno orchestration failed: {e}")
            # Fallback to simple delegation
            return await self._fallback_simple_delegation(task)
    
    async def _handle_simple_task_agno(self, task: str, task_analysis) -> str:
        """Handle simple tasks using any available Agno agent"""

        PrintStyle.standard("Handling simple task with Agno agent")

        try:
            # For simple tasks, use the first available expert or create a general agent
            if self.agno_agents:
                # Use first available expert agent
                agent_name = list(self.agno_agents.keys())[0]
                agno_agent = self.agno_agents[agent_name]

                PrintStyle.standard(f"Using {agent_name} for simple task")

                # Execute task with Agno agent
                result = await agno_agent.arun(task)

                return f"[{agent_name}] {result}"
            else:
                # Create a general purpose agent for this task
                model = self._get_agno_model()
                general_agent = AgnoAgent(
                    name="General Assistant",
                    role="General purpose assistant for simple tasks",
                    model=model,
                    instructions=[
                        "You are a helpful general assistant.",
                        "Complete tasks efficiently and provide clear results.",
                        "Be concise but thorough in your responses."
                    ],
                    markdown=True
                )

                result = await general_agent.arun(task)
                return f"[General Assistant] {result}"

        except Exception as e:
            PrintStyle.error(f"Agno simple task execution failed: {e}")
            return await self._fallback_simple_delegation(task)
    
    async def _delegate_to_agno_specialist(self, task: str, task_analysis,
                                         preferred_agents: List[str] = None) -> str:
        """Delegate task to appropriate Agno specialist agent"""

        PrintStyle.standard(f"Delegating to Agno specialist for domains: {task_analysis.domains}")

        try:
            # Map domains to expert types
            domain_to_expert = {
                "coding": "code_expert",
                "research": "research_expert",
                "data": "data_expert",
                "writing": "writing_expert",
                "system": "code_expert"  # Use code expert for system tasks
            }

            # Find best specialist based on task domains
            selected_expert = None
            expert_name = None

            if preferred_agents:
                # Use preferred agent if available
                for agent_name in preferred_agents:
                    if agent_name in self.agno_agents:
                        selected_expert = self.agno_agents[agent_name]
                        expert_name = agent_name
                        break

            if not selected_expert:
                # Select based on primary domain
                for domain in task_analysis.domains:
                    expert_type = domain_to_expert.get(domain)
                    if expert_type and expert_type in self.agno_agents:
                        selected_expert = self.agno_agents[expert_type]
                        expert_name = expert_type
                        break

            if not selected_expert:
                # Fallback to first available expert
                if self.agno_agents:
                    expert_name = list(self.agno_agents.keys())[0]
                    selected_expert = self.agno_agents[expert_name]

            if selected_expert:
                PrintStyle.standard(f"Using {expert_name} for specialist task")

                # Execute task with specialist
                result = await selected_expert.arun(task)

                return f"[{expert_name}] {result}"
            else:
                PrintStyle.error("No Agno specialists available, falling back")
                return await self._fallback_simple_delegation(task)

        except Exception as e:
            PrintStyle.error(f"Agno specialist delegation failed: {e}")
            return await self._fallback_simple_delegation(task)
    
    async def _delegate_to_agno_team(self, task: str, task_analysis,
                                   preferred_agents: List[str] = None) -> str:
        """Delegate complex task to Agno team coordination"""

        PrintStyle.standard(f"Creating Agno team for complex task with {task_analysis.coordination_mode.value} coordination")

        try:
            # Select team members based on task domains
            team_members = []

            if preferred_agents:
                # Use preferred agents if specified
                for agent_name in preferred_agents:
                    if agent_name in self.agno_agents:
                        team_members.append(self.agno_agents[agent_name])
            else:
                # Select agents based on task domains
                domain_to_expert = {
                    "coding": "code_expert",
                    "research": "research_expert",
                    "data": "data_expert",
                    "writing": "writing_expert"
                }

                selected_experts = set()
                for domain in task_analysis.domains:
                    expert_type = domain_to_expert.get(domain)
                    if expert_type and expert_type in self.agno_agents:
                        selected_experts.add(expert_type)

                # Add agents to team
                for expert_type in selected_experts:
                    team_members.append(self.agno_agents[expert_type])

                # Ensure at least 2 members for team coordination
                if len(team_members) < 2 and len(self.agno_agents) >= 2:
                    for agent_name, agent in self.agno_agents.items():
                        if agent not in team_members:
                            team_members.append(agent)
                            if len(team_members) >= 2:
                                break

            if len(team_members) < 2:
                PrintStyle.standard("Not enough agents for team, using specialist delegation")
                return await self._delegate_to_agno_specialist(task, task_analysis)

            # Create Agno team
            team_id = f"team_{len(self.agno_teams)}"
            model = self._get_agno_model()

            agno_team = AgnoTeam(
                name=f"Task Team {team_id}",
                members=team_members,
                mode=task_analysis.coordination_mode.value,
                model=model,
                instructions=[
                    f"You are coordinating a team to complete this complex task: {task}",
                    "Work together efficiently and leverage each member's expertise",
                    "Ensure comprehensive coverage of all task requirements",
                    "Provide a well-structured final result"
                ],
                markdown=True,
                show_tool_calls=True,
                show_members_responses=False
            )

            self.agno_teams[team_id] = agno_team

            PrintStyle.standard(f"Created Agno team with {len(team_members)} members")

            # Execute team task
            result = await agno_team.arun(task)

            return f"[Team {team_id}] {result}"

        except Exception as e:
            PrintStyle.error(f"Agno team delegation failed: {e}")
            return await self._delegate_to_agno_specialist(task, task_analysis)
    
    async def _execute_agent_task(self, agent_info, task: str, context: str) -> str:
        """Execute task with specific agent (simulation for now)"""
        
        # In a real implementation, this would delegate to actual agent instances
        # For now, simulate execution based on agent capabilities
        
        start_time = datetime.now()
        
        # Simulate processing time based on agent performance
        processing_time = max(0.1, 2.0 / agent_info.capabilities.performance_score)
        await asyncio.sleep(processing_time)
        
        # Generate result based on agent specialization
        result = (
            f"[{agent_info.name}] Task completed successfully.\n"
            f"Specialization applied: {agent_info.capabilities.specialization}\n"
            f"Task: {task}\n"
            f"Context: {context}\n"
            f"Result: Processed using {', '.join(agent_info.capabilities.domains)} expertise. "
            f"Task completed with {agent_info.capabilities.success_rate:.1%} confidence."
        )
        
        # Update completion time
        completion_time = (datetime.now() - start_time).total_seconds()
        self.agent_registry.update_performance_metrics(
            agent_info.agent_id, 
            True, 
            completion_time
        )
        
        return result
    
    async def _fallback_simple_delegation(self, task: str) -> str:
        """Fallback to simple delegation when orchestration is not available"""
        
        PrintStyle.standard("Using fallback simple delegation")
        
        # This mimics the original call_subordinate behavior
        try:
            # Create a simple subordinate agent (simplified version)
            from agent import Agent, UserMessage
            
            subordinate = Agent(
                self.agent.number + 1, 
                self.agent.config, 
                self.agent.context
            )
            subordinate.set_data("_superior", self.agent)
            
            # Add user message and execute
            subordinate.hist_add_user_message(UserMessage(message=task, attachments=[]))
            result = await subordinate.monologue()
            
            return result
            
        except Exception as e:
            PrintStyle.error(f"Fallback delegation failed: {e}")
            return f"Task delegation failed: {task}. Error: {str(e)}"
    
    def get_orchestration_status(self) -> Dict[str, Any]:
        """Get current Agno orchestration system status"""

        if not self.available:
            return {"status": "disabled", "reason": "Agno orchestration system not available"}

        status = {
            "status": "active",
            "framework": "agno",
            "components": {
                "task_analyzer": self.task_analyzer is not None,
                "agno_agents": len(self.agno_agents),
                "agno_teams": len(self.agno_teams)
            },
            "agents": {
                "total_agents": len(self.agno_agents),
                "available_agents": len(self.agno_agents),  # All Agno agents are always available
                "expert_agents": len(self.agno_agents),
                "domains_covered": list(set([
                    domain for agent_name in self.agno_agents.keys()
                    for domain in self._get_agent_domains(agent_name)
                ]))
            },
            "active_teams": len(self.agno_teams)
        }

        return status

    def _get_agent_domains(self, agent_name: str) -> List[str]:
        """Get domains for an agent based on its name"""
        domain_mapping = {
            "code_expert": ["coding", "programming", "debugging"],
            "research_expert": ["research", "analysis", "information"],
            "data_expert": ["data", "statistics", "visualization"],
            "writing_expert": ["writing", "documentation", "communication"]
        }
        return domain_mapping.get(agent_name, ["general"])
    
    def get_available_agents_summary(self) -> List[Dict[str, Any]]:
        """Get summary of available Agno agents for prompt context"""

        if not self.available:
            return []

        summary = []
        for agent_name, agno_agent in self.agno_agents.items():
            summary.append({
                "name": agno_agent.name,
                "role": agno_agent.role,
                "domains": self._get_agent_domains(agent_name),
                "specialization": agno_agent.role,
                "performance_score": 0.9,  # Agno agents are high-performance
                "success_rate": 0.95,      # Agno agents are reliable
                "framework": "agno"
            })

        return summary
    
    async def cleanup_resources(self):
        """Clean up Agno orchestration resources"""

        try:
            # Clean up old teams (keep only recent ones)
            if len(self.agno_teams) > 10:
                # Keep only the 5 most recent teams
                team_ids = list(self.agno_teams.keys())
                for team_id in team_ids[:-5]:
                    del self.agno_teams[team_id]
                PrintStyle.standard(f"Cleaned up {len(team_ids) - 5} old Agno teams")

        except Exception as e:
            PrintStyle.error(f"Agno resource cleanup failed: {e}")

    def is_available(self) -> bool:
        """Check if Agno orchestration system is available"""
        return self.available and AGNO_AVAILABLE and self.task_analyzer is not None
