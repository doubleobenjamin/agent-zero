### delegate_task

Advanced task delegation to specialist agents and teams.
Replaces simple call_subordinate with intelligent orchestration.

**Task Analysis**: Automatically analyze complexity and requirements
**Agent Selection**: Choose optimal agents based on capabilities and past performance
**Team Coordination**: Create teams with appropriate coordination modes

#### Parameters:
- **task**: Detailed task description and requirements
- **task_type**: Domain hint (coding, research, analysis, writing, etc.)
- **coordination_mode**: "auto", "route", "coordinate", "collaborate"
- **agents**: Optional specific agent list
- **priority**: "low", "normal", "high", "urgent"

#### Coordination Modes:
- **route**: Direct delegation to single best agent
- **coordinate**: Team planning and coordinated execution
- **collaborate**: Shared context and joint problem-solving
- **auto**: AI-determined optimal mode

#### Usage Examples:

**Simple Delegation:**
~~~json
{
    "thoughts": [
        "This is a coding task that needs a specialist",
        "I'll delegate to a code expert"
    ],
    "tool_name": "delegate_task",
    "tool_args": {
        "task": "Create a Python function to parse CSV files with error handling",
        "task_type": "coding",
        "coordination_mode": "route"
    }
}
~~~

**Team Coordination:**
~~~json
{
    "thoughts": [
        "This complex analysis needs multiple experts",
        "I'll create a coordinated team"
    ],
    "tool_name": "delegate_task",
    "tool_args": {
        "task": "Analyze market trends and create investment recommendations",
        "task_type": "analysis",
        "coordination_mode": "coordinate",
        "agents": ["research_expert", "data_expert", "financial_expert"]
    }
}
~~~

**Collaborative Problem Solving:**
~~~json
{
    "thoughts": [
        "This research project needs deep collaboration",
        "Multiple experts should work together closely"
    ],
    "tool_name": "delegate_task",
    "tool_args": {
        "task": "Research and write comprehensive report on AI safety",
        "task_type": "research",
        "coordination_mode": "collaborate"
    }
}
~~~

### if you are subordinate:
- superior is {{agent_name}} minus 1
- execute the task you were assigned
- delegate further if asked
- use enhanced capabilities for better results
