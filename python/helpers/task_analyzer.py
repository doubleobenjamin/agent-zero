"""
Task Analysis System for Multi-Agent Orchestration
Analyzes task complexity, domain requirements, and optimal coordination strategies
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from python.helpers.print_style import PrintStyle


class TaskComplexity(Enum):
    SIMPLE = "simple"
    SPECIALIST = "specialist"
    COMPLEX = "complex"


class CoordinationMode(Enum):
    ROUTE = "route"          # Direct delegation to single best agent
    COORDINATE = "coordinate"  # Team planning and coordinated execution
    COLLABORATE = "collaborate"  # Shared context and joint problem-solving
    AUTO = "auto"            # AI-determined optimal mode


@dataclass
class TaskAnalysis:
    """Result of task analysis"""
    complexity: TaskComplexity
    domains: List[str]
    required_skills: List[str]
    coordination_mode: CoordinationMode
    estimated_time: str
    requires_team: bool
    confidence: float
    reasoning: str


class TaskAnalyzer:
    """Analyzes tasks to determine optimal agent/team configuration"""
    
    def __init__(self, agent):
        self.agent = agent
        
        # Domain patterns for quick classification
        self.domain_patterns = {
            "coding": [
                r"\b(code|program|script|function|class|debug|fix|implement|develop)\b",
                r"\b(python|javascript|java|c\+\+|html|css|sql|api)\b",
                r"\b(github|git|repository|commit|pull request)\b"
            ],
            "research": [
                r"\b(research|investigate|analyze|study|explore|find information)\b",
                r"\b(search|lookup|discover|learn about|gather data)\b",
                r"\b(article|paper|documentation|source|reference)\b"
            ],
            "data": [
                r"\b(data|dataset|analysis|statistics|visualization|chart|graph)\b",
                r"\b(csv|excel|database|query|report|metrics)\b",
                r"\b(pandas|numpy|matplotlib|analysis|correlation)\b"
            ],
            "writing": [
                r"\b(write|compose|draft|create|document|article|blog|report)\b",
                r"\b(content|text|copy|summary|description|explanation)\b",
                r"\b(markdown|documentation|readme|guide|tutorial)\b"
            ],
            "system": [
                r"\b(system|server|deploy|configure|setup|install|manage)\b",
                r"\b(docker|kubernetes|aws|cloud|infrastructure|devops)\b",
                r"\b(monitoring|logging|backup|security|performance)\b"
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            "simple": [
                r"\b(simple|quick|basic|easy|straightforward)\b",
                r"\b(single|one|just|only|small)\b"
            ],
            "specialist": [
                r"\b(expert|specialized|advanced|technical|specific)\b",
                r"\b(complex|detailed|thorough|comprehensive)\b"
            ],
            "complex": [
                r"\b(multiple|several|many|various|different)\b",
                r"\b(integrate|coordinate|combine|orchestrate)\b",
                r"\b(workflow|pipeline|system|architecture|framework)\b"
            ]
        }
    
    async def analyze_task_requirements(self, task: str, task_type: str = "general") -> TaskAnalysis:
        """Analyze task to determine optimal agent/team configuration"""
        
        try:
            # Use LLM for sophisticated analysis
            analysis_result = await self._llm_analyze_task(task, task_type)
            
            # Combine with pattern-based analysis for validation
            pattern_analysis = self._pattern_analyze_task(task)
            
            # Merge results with LLM taking precedence
            final_analysis = self._merge_analysis(analysis_result, pattern_analysis)
            
            PrintStyle.standard(f"Task analysis: {final_analysis.complexity.value} complexity, {len(final_analysis.domains)} domains")
            return final_analysis
            
        except Exception as e:
            PrintStyle.error(f"Task analysis failed: {e}")
            # Fallback to pattern-based analysis
            return self._pattern_analyze_task(task)
    
    async def _llm_analyze_task(self, task: str, task_type: str) -> TaskAnalysis:
        """Use LLM to analyze task requirements"""
        
        analysis_prompt = f"""
        Analyze this task and determine the optimal agent configuration:
        
        Task: {task}
        Task Type Hint: {task_type}
        
        Provide analysis in JSON format:
        {{
            "complexity": "simple|specialist|complex",
            "domains": ["coding", "research", "data", "writing", "system"],
            "required_skills": ["specific skills needed"],
            "coordination_mode": "route|coordinate|collaborate",
            "estimated_time": "quick|moderate|extended",
            "requires_team": true/false,
            "confidence": 0.0-1.0,
            "reasoning": "explanation of analysis"
        }}
        
        Guidelines:
        - simple: Single-step tasks that can be handled by any agent
        - specialist: Tasks requiring domain expertise (coding, research, etc.)
        - complex: Multi-step tasks requiring coordination between specialists
        - route: Direct delegation to single best agent
        - coordinate: Team planning and coordinated execution
        - collaborate: Shared context and joint problem-solving
        """
        
        try:
            response = await self.agent.call_utility_model(
                system="You are a task analysis expert. Analyze tasks to determine optimal agent configuration.",
                message=analysis_prompt
            )
            
            # Parse JSON response
            analysis_data = json.loads(response.strip())
            
            return TaskAnalysis(
                complexity=TaskComplexity(analysis_data["complexity"]),
                domains=analysis_data["domains"],
                required_skills=analysis_data["required_skills"],
                coordination_mode=CoordinationMode(analysis_data["coordination_mode"]),
                estimated_time=analysis_data["estimated_time"],
                requires_team=analysis_data["requires_team"],
                confidence=analysis_data["confidence"],
                reasoning=analysis_data["reasoning"]
            )
            
        except Exception as e:
            PrintStyle.error(f"LLM task analysis failed: {e}")
            raise
    
    def _pattern_analyze_task(self, task: str) -> TaskAnalysis:
        """Fallback pattern-based task analysis"""
        
        task_lower = task.lower()
        
        # Identify domains
        domains = []
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                if re.search(pattern, task_lower, re.IGNORECASE):
                    domains.append(domain)
                    break
        
        # Determine complexity
        complexity = TaskComplexity.SIMPLE
        for complexity_level, patterns in self.complexity_indicators.items():
            for pattern in patterns:
                if re.search(pattern, task_lower, re.IGNORECASE):
                    if complexity_level == "complex":
                        complexity = TaskComplexity.COMPLEX
                    elif complexity_level == "specialist" and complexity == TaskComplexity.SIMPLE:
                        complexity = TaskComplexity.SPECIALIST
                    break
        
        # If multiple domains detected, likely complex
        if len(domains) > 2:
            complexity = TaskComplexity.COMPLEX
        elif len(domains) == 1 and domains[0] in ["coding", "data", "system"]:
            complexity = TaskComplexity.SPECIALIST
        
        # Determine coordination mode
        coordination_mode = CoordinationMode.ROUTE
        if complexity == TaskComplexity.COMPLEX:
            coordination_mode = CoordinationMode.COORDINATE
        elif len(domains) > 1:
            coordination_mode = CoordinationMode.COLLABORATE
        
        return TaskAnalysis(
            complexity=complexity,
            domains=domains or ["general"],
            required_skills=domains or ["general"],
            coordination_mode=coordination_mode,
            estimated_time="moderate",
            requires_team=len(domains) > 1 or complexity == TaskComplexity.COMPLEX,
            confidence=0.7,  # Pattern-based analysis has moderate confidence
            reasoning=f"Pattern-based analysis: {len(domains)} domains detected, {complexity.value} complexity"
        )
    
    def _merge_analysis(self, llm_analysis: TaskAnalysis, pattern_analysis: TaskAnalysis) -> TaskAnalysis:
        """Merge LLM and pattern analysis results"""
        
        # LLM analysis takes precedence, but validate with patterns
        merged = llm_analysis
        
        # If LLM missed obvious domains, add them from pattern analysis
        for domain in pattern_analysis.domains:
            if domain not in merged.domains:
                merged.domains.append(domain)
        
        # Adjust confidence based on agreement
        if merged.complexity == pattern_analysis.complexity:
            merged.confidence = min(1.0, merged.confidence + 0.1)
        
        return merged
    
    def get_recommended_agents(self, analysis: TaskAnalysis) -> List[str]:
        """Get recommended agent types based on analysis"""
        
        agent_recommendations = []
        
        for domain in analysis.domains:
            if domain == "coding":
                agent_recommendations.append("code_expert")
            elif domain == "research":
                agent_recommendations.append("research_expert")
            elif domain == "data":
                agent_recommendations.append("data_expert")
            elif domain == "writing":
                agent_recommendations.append("writing_expert")
            elif domain == "system":
                agent_recommendations.append("system_expert")
        
        # If no specific domain, recommend general helper
        if not agent_recommendations:
            agent_recommendations.append("general_helper")
        
        return agent_recommendations
