# Multi-Agent Orchestration Context

## Current Orchestration Status
{{#if orchestration_status}}
**Active Coordination**: {{orchestration_status.mode}}
**Team Size**: {{orchestration_status.team_size}}
**Workflow Stage**: {{orchestration_status.stage}}
{{/if}}

## Available Agents
{{#if available_agents}}
### Specialist Agents Ready:
{{#each available_agents}}
- **{{name}}**: {{capabilities}} (Performance: {{performance_score}})
{{/each}}
{{/if}}

## Team Coordination Modes

### Route Mode
- Direct delegation to single best agent
- Minimal coordination overhead
- Best for: Independent, well-defined tasks

### Coordinate Mode
- Team planning and coordinated execution
- Shared timeline and dependencies
- Best for: Complex multi-step workflows

### Collaborate Mode
- Shared context and joint problem-solving
- Real-time collaboration and knowledge sharing
- Best for: Creative, research, and analysis tasks

## Orchestration Guidelines

### Task Analysis Framework:
1. **Complexity Assessment**: Simple, moderate, complex, or enterprise-level
2. **Domain Requirements**: Technical skills, knowledge areas, tools needed
3. **Coordination Needs**: Independent work vs. collaborative requirements
4. **Timeline Constraints**: Urgent, normal, or flexible scheduling

### Agent Selection Criteria:
- **Capability Match**: Agent skills align with task requirements
- **Performance History**: Past success rates and quality metrics
- **Current Availability**: Agent workload and capacity
- **Collaboration Fit**: Team dynamics and communication style

### Workflow Optimization:
- **Parallel Execution**: Identify tasks that can run simultaneously
- **Dependency Management**: Map task prerequisites and handoffs
- **Resource Allocation**: Balance workload across available agents
- **Quality Assurance**: Built-in review and validation steps

## Current Team Status
{{#if team_status}}
### Active Teams:
{{#each team_status}}
**Team {{id}}**: {{task_summary}}
- **Mode**: {{coordination_mode}}
- **Progress**: {{progress_percentage}}%
- **Members**: {{#each members}}{{name}}{{#unless @last}}, {{/unless}}{{/each}}
- **Next Milestone**: {{next_milestone}}
{{/each}}
{{/if}}

## Performance Insights
{{#if agent_performance}}
### Recent Performance Metrics:
{{#each agent_performance}}
- **{{agent_name}}**: {{success_rate}}% success, avg quality {{quality_score}}/10
{{/each}}
{{/if}}

## Orchestration Best Practices
- Always analyze task complexity before choosing coordination mode
- Consider agent specializations and past performance
- Plan for parallel execution when possible
- Maintain clear communication channels between team members
- Monitor progress and adjust coordination as needed
- Capture and share learnings across the agent ecosystem
