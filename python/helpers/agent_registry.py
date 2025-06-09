"""
Agent Registry for Multi-Agent Orchestration
Manages persistent expert agents with performance tracking and lifecycle management
"""

import uuid
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from python.helpers.print_style import PrintStyle


class AgentStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    INITIALIZING = "initializing"


class AgentType(Enum):
    PERSISTENT_EXPERT = "persistent_expert"
    EPHEMERAL_HELPER = "ephemeral_helper"
    TEAM_LEADER = "team_leader"


@dataclass
class AgentCapabilities:
    """Agent capabilities and specializations"""
    domains: List[str]
    tools: List[str]
    specialization: str
    performance_score: float = 0.8
    success_rate: float = 0.9
    avg_completion_time: float = 300.0  # seconds
    total_tasks: int = 0
    successful_tasks: int = 0


@dataclass
class AgentInfo:
    """Complete agent information"""
    agent_id: str
    name: str
    role: str
    agent_type: AgentType
    status: AgentStatus
    capabilities: AgentCapabilities
    created_at: datetime
    last_used: datetime
    current_task: Optional[str] = None
    namespace: Optional[str] = None


class AgentRegistry:
    """Registry for managing persistent and ephemeral agents"""
    
    def __init__(self, main_agent):
        self.main_agent = main_agent
        self.agents: Dict[str, AgentInfo] = {}
        self.expert_templates = self._load_expert_templates()
        
        PrintStyle.standard("Agent registry initialized")
    
    def _load_expert_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load expert agent templates"""
        return {
            "code_expert": {
                "role": "Senior Software Engineer",
                "domains": ["coding", "debugging", "architecture"],
                "tools": ["code_execution", "github", "documentation"],
                "specialization": "Programming, debugging, code review, software architecture",
                "memory_namespace": "code_expert"
            },
            "research_expert": {
                "role": "Research Analyst",
                "domains": ["research", "analysis", "information"],
                "tools": ["search_engine", "webpage_content", "knowledge_tool"],
                "specialization": "Information gathering, analysis, synthesis, fact-checking",
                "memory_namespace": "research_expert"
            },
            "data_expert": {
                "role": "Data Scientist",
                "domains": ["data", "analysis", "visualization"],
                "tools": ["code_execution", "visualization", "analysis"],
                "specialization": "Data analysis, statistics, visualization, machine learning",
                "memory_namespace": "data_expert"
            },
            "writing_expert": {
                "role": "Content Writer",
                "domains": ["writing", "documentation", "communication"],
                "tools": ["documentation", "knowledge_tool"],
                "specialization": "Technical writing, documentation, content creation",
                "memory_namespace": "writing_expert"
            },
            "system_expert": {
                "role": "System Administrator",
                "domains": ["system", "infrastructure", "deployment"],
                "tools": ["code_execution", "system_tools"],
                "specialization": "System administration, DevOps, infrastructure management",
                "memory_namespace": "system_expert"
            }
        }
    
    def register_agent(self, agent_id: str, name: str, role: str, 
                      agent_type: AgentType, capabilities: AgentCapabilities,
                      namespace: str = None) -> bool:
        """Register a new agent in the registry"""
        
        try:
            agent_info = AgentInfo(
                agent_id=agent_id,
                name=name,
                role=role,
                agent_type=agent_type,
                status=AgentStatus.AVAILABLE,
                capabilities=capabilities,
                created_at=datetime.now(),
                last_used=datetime.now(),
                namespace=namespace
            )
            
            self.agents[agent_id] = agent_info
            PrintStyle.standard(f"Registered agent: {name} ({role})")
            return True
            
        except Exception as e:
            PrintStyle.error(f"Failed to register agent {name}: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information by ID"""
        return self.agents.get(agent_id)
    
    def get_available_agents(self) -> Dict[str, AgentInfo]:
        """Get all available agents"""
        return {
            agent_id: info for agent_id, info in self.agents.items()
            if info.status == AgentStatus.AVAILABLE
        }
    
    def get_agents_by_domain(self, domain: str) -> List[AgentInfo]:
        """Get agents specialized in a specific domain"""
        matching_agents = []
        for agent_info in self.agents.values():
            if domain in agent_info.capabilities.domains:
                matching_agents.append(agent_info)
        
        # Sort by performance score
        matching_agents.sort(key=lambda x: x.capabilities.performance_score, reverse=True)
        return matching_agents
    
    def get_best_agent_for_task(self, required_domains: List[str], 
                               required_skills: List[str] = None) -> Optional[AgentInfo]:
        """Find the best available agent for specific requirements"""
        
        if required_skills is None:
            required_skills = []
        
        available_agents = self.get_available_agents()
        if not available_agents:
            return None
        
        scored_agents = []
        
        for agent_info in available_agents.values():
            score = self._calculate_capability_score(
                required_domains, 
                required_skills,
                agent_info.capabilities
            )
            scored_agents.append((agent_info, score))
        
        # Sort by score (descending)
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        if scored_agents and scored_agents[0][1] > 0:
            return scored_agents[0][0]
        
        return None
    
    def _calculate_capability_score(self, required_domains: List[str], 
                                  required_skills: List[str],
                                  capabilities: AgentCapabilities) -> float:
        """Calculate how well an agent matches task requirements"""
        
        score = 0.0
        
        # Domain match score (40% weight)
        domain_matches = len(set(required_domains) & set(capabilities.domains))
        domain_score = domain_matches / max(len(required_domains), 1) * 0.4
        score += domain_score
        
        # Skill match score (30% weight)
        if required_skills:
            skill_matches = len(set(required_skills) & set(capabilities.domains + capabilities.tools))
            skill_score = skill_matches / len(required_skills) * 0.3
            score += skill_score
        else:
            score += 0.3  # No specific skills required
        
        # Performance score (20% weight)
        performance_score = capabilities.performance_score * 0.2
        score += performance_score
        
        # Success rate (10% weight)
        success_score = capabilities.success_rate * 0.1
        score += success_score
        
        return score
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, 
                           current_task: str = None) -> bool:
        """Update agent status"""
        
        if agent_id not in self.agents:
            return False
        
        self.agents[agent_id].status = status
        self.agents[agent_id].current_task = current_task
        
        if status == AgentStatus.AVAILABLE:
            self.agents[agent_id].last_used = datetime.now()
        
        return True
    
    def update_performance_metrics(self, agent_id: str, task_successful: bool, 
                                 completion_time: float = None) -> bool:
        """Update agent performance metrics"""
        
        if agent_id not in self.agents:
            return False
        
        agent_info = self.agents[agent_id]
        capabilities = agent_info.capabilities
        
        # Update task counts
        capabilities.total_tasks += 1
        if task_successful:
            capabilities.successful_tasks += 1
        
        # Update success rate
        capabilities.success_rate = capabilities.successful_tasks / capabilities.total_tasks
        
        # Update completion time
        if completion_time is not None:
            if capabilities.avg_completion_time == 0:
                capabilities.avg_completion_time = completion_time
            else:
                # Exponential moving average
                capabilities.avg_completion_time = (
                    0.8 * capabilities.avg_completion_time + 0.2 * completion_time
                )
        
        # Update performance score (weighted combination)
        capabilities.performance_score = (
            0.6 * capabilities.success_rate +
            0.3 * min(1.0, 300.0 / max(capabilities.avg_completion_time, 1.0)) +  # Speed factor
            0.1 * min(1.0, capabilities.total_tasks / 10.0)  # Experience factor
        )
        
        PrintStyle.standard(f"Updated performance for {agent_info.name}: "
                          f"success_rate={capabilities.success_rate:.2f}, "
                          f"performance_score={capabilities.performance_score:.2f}")
        
        return True
    
    def create_expert_agent(self, expert_type: str) -> Optional[str]:
        """Create a persistent expert agent"""
        
        if expert_type not in self.expert_templates:
            PrintStyle.error(f"Unknown expert type: {expert_type}")
            return None
        
        template = self.expert_templates[expert_type]
        agent_id = f"{expert_type}_{uuid.uuid4().hex[:8]}"
        
        capabilities = AgentCapabilities(
            domains=template["domains"],
            tools=template["tools"],
            specialization=template["specialization"]
        )
        
        success = self.register_agent(
            agent_id=agent_id,
            name=f"{template['role']} Agent",
            role=template["role"],
            agent_type=AgentType.PERSISTENT_EXPERT,
            capabilities=capabilities,
            namespace=template["memory_namespace"]
        )
        
        return agent_id if success else None
    
    def create_ephemeral_helper(self, task_description: str, 
                               required_domains: List[str]) -> Optional[str]:
        """Create a temporary helper agent for specific task"""
        
        agent_id = f"helper_{uuid.uuid4().hex[:8]}"
        
        capabilities = AgentCapabilities(
            domains=required_domains,
            tools=["general"],
            specialization=f"Task-specific helper: {task_description[:50]}..."
        )
        
        success = self.register_agent(
            agent_id=agent_id,
            name=f"Helper Agent",
            role="Task Helper",
            agent_type=AgentType.EPHEMERAL_HELPER,
            capabilities=capabilities,
            namespace="ephemeral"
        )
        
        return agent_id if success else None
    
    def cleanup_idle_agents(self, max_idle_hours: int = 24) -> int:
        """Remove agents that haven't been used recently"""
        
        cutoff_time = datetime.now() - timedelta(hours=max_idle_hours)
        removed_count = 0
        
        # Only cleanup ephemeral agents
        agents_to_remove = []
        for agent_id, agent_info in self.agents.items():
            if (agent_info.agent_type == AgentType.EPHEMERAL_HELPER and 
                agent_info.last_used < cutoff_time and
                agent_info.status == AgentStatus.AVAILABLE):
                agents_to_remove.append(agent_id)
        
        for agent_id in agents_to_remove:
            del self.agents[agent_id]
            removed_count += 1
        
        if removed_count > 0:
            PrintStyle.standard(f"Cleaned up {removed_count} idle ephemeral agents")
        
        return removed_count
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        
        stats = {
            "total_agents": len(self.agents),
            "available_agents": len(self.get_available_agents()),
            "expert_agents": len([a for a in self.agents.values() 
                                if a.agent_type == AgentType.PERSISTENT_EXPERT]),
            "helper_agents": len([a for a in self.agents.values() 
                                if a.agent_type == AgentType.EPHEMERAL_HELPER]),
            "domains_covered": list(set(
                domain for agent in self.agents.values() 
                for domain in agent.capabilities.domains
            )),
            "avg_performance": sum(a.capabilities.performance_score for a in self.agents.values()) / 
                            max(len(self.agents), 1)
        }
        
        return stats
