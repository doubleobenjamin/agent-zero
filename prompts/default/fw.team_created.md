🏗️ **Multi-Agent Team Created**

**Team ID**: {{team_id}}
**Task**: {{task_summary}}
**Coordination Mode**: {{coordination_mode}}

### 👥 Team Composition:
{{#each team_members}}
**{{name}}** - {{role}}
- **Specialization**: {{specialization}}
- **Responsibilities**: {{responsibilities}}
- **Performance History**: {{performance_score}}/10
{{/each}}

### 📋 Coordination Plan:
{{#if coordination_mode == "coordinate"}}
- **Planning Phase**: Team will collaborate on task breakdown
- **Execution Phase**: Coordinated parallel execution with checkpoints
- **Integration Phase**: Results will be merged and validated
{{/if}}
{{#if coordination_mode == "collaborate"}}
- **Shared Context**: All team members have access to shared knowledge base
- **Real-time Collaboration**: Continuous communication and knowledge sharing
- **Joint Problem-Solving**: Collective decision-making and solution development
{{/if}}

### 📊 Success Metrics:
- **Quality Target**: {{quality_target}}/10
- **Timeline**: {{estimated_timeline}}
- **Milestones**: {{milestone_count}} checkpoints planned

**Team Status**: {{team_status}}
**Next Milestone**: {{next_milestone}}
