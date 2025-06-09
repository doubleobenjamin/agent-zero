🎯 **Task Delegated Successfully**

**Task**: {{task}}
**Coordination Mode**: {{coordination_mode}}
**Priority**: {{priority}}

{{#if single_agent}}
### 👤 Assigned Agent:
**{{agent_name}}** ({{agent_capabilities}})
- **Performance Score**: {{performance_score}}/10
- **Estimated Completion**: {{estimated_completion}}
{{/if}}

{{#if team_assigned}}
### 👥 Team Assigned:
{{#each team_members}}
- **{{name}}**: {{role}} ({{capabilities}})
{{/each}}
- **Team Size**: {{team_size}} agents
- **Coordination Strategy**: {{coordination_strategy}}
- **Estimated Completion**: {{estimated_completion}}
{{/if}}

**Next Steps**:
{{#each next_steps}}
- {{this}}
{{/each}}

**Monitoring**: Task progress will be tracked and reported automatically.
