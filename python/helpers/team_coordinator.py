"""
Team Coordination System for Multi-Agent Orchestration
Manages team formation and coordination modes (route, coordinate, collaborate)
"""

import uuid
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from python.helpers.print_style import PrintStyle
from python.helpers.task_analyzer import CoordinationMode, TaskAnalysis
from python.helpers.agent_registry import AgentInfo, AgentStatus


class TeamStatus(Enum):
    FORMING = "forming"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TeamMember:
    """Team member information"""
    agent_id: str
    agent_info: AgentInfo
    role_in_team: str
    assigned_tasks: List[str]
    status: str = "ready"


@dataclass
class TeamInfo:
    """Team information and coordination data"""
    team_id: str
    name: str
    coordination_mode: CoordinationMode
    members: List[TeamMember]
    leader_id: Optional[str]
    status: TeamStatus
    created_at: datetime
    task_description: str
    shared_context: Dict[str, Any]
    results: Dict[str, Any]


class TeamCoordinator:
    """Coordinates team formation and execution"""
    
    def __init__(self, main_agent, agent_registry):
        self.main_agent = main_agent
        self.agent_registry = agent_registry
        self.active_teams: Dict[str, TeamInfo] = {}
        
        PrintStyle.standard("Team coordinator initialized")
    
    async def create_team(self, task_analysis: TaskAnalysis, task_description: str,
                         selected_agents: List[AgentInfo] = None) -> Optional[str]:
        """Create a team based on task analysis"""
        
        try:
            team_id = f"team_{uuid.uuid4().hex[:8]}"
            
            # Select agents if not provided
            if selected_agents is None:
                selected_agents = await self._select_team_members(task_analysis)
            
            if not selected_agents:
                PrintStyle.error("No suitable agents found for team formation")
                return None
            
            # Create team members
            team_members = []
            for i, agent_info in enumerate(selected_agents):
                role = self._determine_team_role(agent_info, task_analysis, i == 0)
                member = TeamMember(
                    agent_id=agent_info.agent_id,
                    agent_info=agent_info,
                    role_in_team=role,
                    assigned_tasks=[]
                )
                team_members.append(member)
                
                # Update agent status
                self.agent_registry.update_agent_status(
                    agent_info.agent_id, 
                    AgentStatus.BUSY, 
                    f"Team {team_id}"
                )
            
            # Determine team leader
            leader_id = team_members[0].agent_id if team_members else None
            
            # Create team info
            team_info = TeamInfo(
                team_id=team_id,
                name=f"Team for: {task_description[:50]}...",
                coordination_mode=task_analysis.coordination_mode,
                members=team_members,
                leader_id=leader_id,
                status=TeamStatus.FORMING,
                created_at=datetime.now(),
                task_description=task_description,
                shared_context={},
                results={}
            )
            
            self.active_teams[team_id] = team_info
            
            PrintStyle.standard(f"Created team {team_id} with {len(team_members)} members "
                              f"in {task_analysis.coordination_mode.value} mode")
            
            return team_id
            
        except Exception as e:
            PrintStyle.error(f"Failed to create team: {e}")
            return None
    
    async def _select_team_members(self, task_analysis: TaskAnalysis) -> List[AgentInfo]:
        """Select optimal team members based on task analysis"""
        
        selected_agents = []
        
        # For each required domain, find the best agent
        for domain in task_analysis.domains:
            domain_agents = self.agent_registry.get_agents_by_domain(domain)
            available_agents = [a for a in domain_agents if a.status == AgentStatus.AVAILABLE]
            
            if available_agents:
                # Select best available agent for this domain
                best_agent = available_agents[0]
                if best_agent not in selected_agents:
                    selected_agents.append(best_agent)
        
        # If no domain-specific agents found, get general best agent
        if not selected_agents:
            best_agent = self.agent_registry.get_best_agent_for_task(
                task_analysis.domains, 
                task_analysis.required_skills
            )
            if best_agent:
                selected_agents.append(best_agent)
        
        # Limit team size based on coordination mode
        max_team_size = self._get_max_team_size(task_analysis.coordination_mode)
        return selected_agents[:max_team_size]
    
    def _get_max_team_size(self, coordination_mode: CoordinationMode) -> int:
        """Get maximum team size for coordination mode"""
        if coordination_mode == CoordinationMode.ROUTE:
            return 1
        elif coordination_mode == CoordinationMode.COORDINATE:
            return 3
        elif coordination_mode == CoordinationMode.COLLABORATE:
            return 5
        else:  # AUTO
            return 3
    
    def _determine_team_role(self, agent_info: AgentInfo, task_analysis: TaskAnalysis, 
                           is_leader: bool) -> str:
        """Determine agent's role in the team"""
        
        if is_leader:
            return "Team Leader"
        
        # Assign role based on agent's primary domain
        primary_domain = agent_info.capabilities.domains[0] if agent_info.capabilities.domains else "general"
        
        role_mapping = {
            "coding": "Developer",
            "research": "Researcher", 
            "data": "Data Analyst",
            "writing": "Writer",
            "system": "System Specialist"
        }
        
        return role_mapping.get(primary_domain, "Specialist")
    
    async def execute_team_task(self, team_id: str, task: str) -> Optional[str]:
        """Execute task using team coordination"""
        
        if team_id not in self.active_teams:
            PrintStyle.error(f"Team {team_id} not found")
            return None
        
        team_info = self.active_teams[team_id]
        team_info.status = TeamStatus.ACTIVE
        
        try:
            if team_info.coordination_mode == CoordinationMode.ROUTE:
                result = await self._execute_route_mode(team_info, task)
            elif team_info.coordination_mode == CoordinationMode.COORDINATE:
                result = await self._execute_coordinate_mode(team_info, task)
            elif team_info.coordination_mode == CoordinationMode.COLLABORATE:
                result = await self._execute_collaborate_mode(team_info, task)
            else:
                # Auto mode - choose best approach
                result = await self._execute_auto_mode(team_info, task)
            
            team_info.status = TeamStatus.COMPLETED
            team_info.results["final_result"] = result
            
            # Update agent performance metrics
            for member in team_info.members:
                self.agent_registry.update_performance_metrics(
                    member.agent_id, 
                    task_successful=True
                )
                # Release agent
                self.agent_registry.update_agent_status(
                    member.agent_id, 
                    AgentStatus.AVAILABLE
                )
            
            PrintStyle.standard(f"Team {team_id} completed task successfully")
            return result
            
        except Exception as e:
            PrintStyle.error(f"Team {team_id} task execution failed: {e}")
            team_info.status = TeamStatus.FAILED
            
            # Update agent performance metrics for failure
            for member in team_info.members:
                self.agent_registry.update_performance_metrics(
                    member.agent_id, 
                    task_successful=False
                )
                # Release agent
                self.agent_registry.update_agent_status(
                    member.agent_id, 
                    AgentStatus.AVAILABLE
                )
            
            return None
    
    async def _execute_route_mode(self, team_info: TeamInfo, task: str) -> str:
        """Execute task in route mode - direct delegation to single agent"""
        
        if not team_info.members:
            raise Exception("No team members available")
        
        # Route to the best member (first one, as they're sorted by capability)
        selected_member = team_info.members[0]
        
        PrintStyle.standard(f"Routing task to {selected_member.agent_info.name}")
        
        # Simulate agent execution (in real implementation, this would delegate to actual agent)
        result = await self._simulate_agent_execution(
            selected_member.agent_info, 
            task,
            f"You are the {selected_member.role_in_team} handling this task independently."
        )
        
        return result
    
    async def _execute_coordinate_mode(self, team_info: TeamInfo, task: str) -> str:
        """Execute task in coordinate mode - team planning and coordinated execution"""
        
        PrintStyle.standard(f"Coordinating team of {len(team_info.members)} members")
        
        # Step 1: Team planning
        plan = await self._create_team_plan(team_info, task)
        team_info.shared_context["plan"] = plan
        
        # Step 2: Assign subtasks to team members
        subtasks = self._break_down_task(task, len(team_info.members))
        
        # Step 3: Execute subtasks in parallel
        results = []
        tasks = []
        
        for i, member in enumerate(team_info.members):
            if i < len(subtasks):
                member.assigned_tasks.append(subtasks[i])
                task_coroutine = self._simulate_agent_execution(
                    member.agent_info,
                    subtasks[i],
                    f"You are the {member.role_in_team}. Work with your team to complete this subtask. "
                    f"Team plan: {plan}"
                )
                tasks.append(task_coroutine)
        
        # Wait for all subtasks to complete
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Step 4: Synthesize results
        final_result = await self._synthesize_team_results(team_info, results)
        
        return final_result
    
    async def _execute_collaborate_mode(self, team_info: TeamInfo, task: str) -> str:
        """Execute task in collaborate mode - shared context and joint problem-solving"""
        
        PrintStyle.standard(f"Collaborating with team of {len(team_info.members)} members")
        
        # Collaborative execution with shared context
        shared_context = {
            "task": task,
            "team_members": [m.agent_info.name for m in team_info.members],
            "collaboration_notes": []
        }
        
        # Each member contributes to the solution
        contributions = []
        
        for member in team_info.members:
            context_prompt = (
                f"You are the {member.role_in_team} collaborating with: "
                f"{', '.join([m.agent_info.name for m in team_info.members if m != member])}. "
                f"Previous contributions: {contributions[-3:] if contributions else 'None yet'}. "
                f"Build on the team's work and add your expertise."
            )
            
            contribution = await self._simulate_agent_execution(
                member.agent_info,
                task,
                context_prompt
            )
            
            contributions.append(f"{member.role_in_team}: {contribution}")
            shared_context["collaboration_notes"].append(contribution)
        
        # Final synthesis
        final_result = await self._synthesize_collaborative_result(team_info, contributions)
        
        return final_result
    
    async def _execute_auto_mode(self, team_info: TeamInfo, task: str) -> str:
        """Execute task in auto mode - AI determines best approach"""
        
        # For now, choose based on team size
        if len(team_info.members) == 1:
            team_info.coordination_mode = CoordinationMode.ROUTE
            return await self._execute_route_mode(team_info, task)
        elif len(team_info.members) <= 3:
            team_info.coordination_mode = CoordinationMode.COORDINATE
            return await self._execute_coordinate_mode(team_info, task)
        else:
            team_info.coordination_mode = CoordinationMode.COLLABORATE
            return await self._execute_collaborate_mode(team_info, task)
    
    async def _simulate_agent_execution(self, agent_info: AgentInfo, task: str, context: str) -> str:
        """Simulate agent execution (placeholder for actual agent delegation)"""
        
        # In real implementation, this would delegate to actual agent instances
        # For now, simulate based on agent capabilities
        
        await asyncio.sleep(0.1)  # Simulate processing time
        
        result = (
            f"[{agent_info.name}] Completed task: {task[:50]}... "
            f"Using specialization: {agent_info.capabilities.specialization}. "
            f"Context: {context[:100]}..."
        )
        
        return result
    
    async def _create_team_plan(self, team_info: TeamInfo, task: str) -> str:
        """Create a coordination plan for the team"""
        
        plan = (
            f"Team Plan for: {task}\n"
            f"Team Members: {', '.join([m.agent_info.name for m in team_info.members])}\n"
            f"Coordination Mode: {team_info.coordination_mode.value}\n"
            f"Approach: Divide task among specialists and coordinate results"
        )
        
        return plan
    
    def _break_down_task(self, task: str, num_subtasks: int) -> List[str]:
        """Break down task into subtasks"""
        
        # Simple task breakdown (in real implementation, this would be more sophisticated)
        subtasks = []
        
        if num_subtasks == 1:
            subtasks.append(task)
        elif num_subtasks == 2:
            subtasks.extend([
                f"Research and analyze: {task}",
                f"Implement and validate: {task}"
            ])
        else:
            subtasks.extend([
                f"Research phase: {task}",
                f"Implementation phase: {task}",
                f"Testing and validation: {task}"
            ])
            
            # Add more subtasks if needed
            for i in range(3, num_subtasks):
                subtasks.append(f"Additional work {i}: {task}")
        
        return subtasks
    
    async def _synthesize_team_results(self, team_info: TeamInfo, results: List[str]) -> str:
        """Synthesize results from coordinated team execution"""
        
        synthesis = (
            f"Team Results Synthesis:\n"
            f"Task: {team_info.task_description}\n"
            f"Team: {', '.join([m.agent_info.name for m in team_info.members])}\n\n"
            f"Combined Results:\n"
        )
        
        for i, result in enumerate(results):
            if not isinstance(result, Exception):
                synthesis += f"{i+1}. {result}\n"
        
        synthesis += "\nTeam coordination completed successfully."
        
        return synthesis
    
    async def _synthesize_collaborative_result(self, team_info: TeamInfo, contributions: List[str]) -> str:
        """Synthesize results from collaborative team execution"""
        
        synthesis = (
            f"Collaborative Team Result:\n"
            f"Task: {team_info.task_description}\n\n"
            f"Team Contributions:\n"
        )
        
        for contribution in contributions:
            synthesis += f"• {contribution}\n"
        
        synthesis += "\nCollaborative solution completed with all team member input."
        
        return synthesis
    
    def get_team_info(self, team_id: str) -> Optional[TeamInfo]:
        """Get team information"""
        return self.active_teams.get(team_id)
    
    def cleanup_completed_teams(self, max_age_hours: int = 24) -> int:
        """Clean up old completed teams"""
        
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        teams_to_remove = []
        
        for team_id, team_info in self.active_teams.items():
            if (team_info.status in [TeamStatus.COMPLETED, TeamStatus.FAILED] and
                team_info.created_at.timestamp() < cutoff_time):
                teams_to_remove.append(team_id)
        
        for team_id in teams_to_remove:
            del self.active_teams[team_id]
        
        if teams_to_remove:
            PrintStyle.standard(f"Cleaned up {len(teams_to_remove)} old teams")
        
        return len(teams_to_remove)
