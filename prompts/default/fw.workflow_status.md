📊 **Workflow Status Update**

**Workflow ID**: {{workflow_id}}
**Overall Progress**: {{overall_progress}}%
**Status**: {{workflow_status}}

### 🎯 Active Tasks:
{{#each active_tasks}}
**{{task_name}}**
- **Assigned to**: {{assigned_agent}}
- **Progress**: {{progress}}%
- **Status**: {{status}}
- **ETA**: {{estimated_completion}}
{{/each}}

### ✅ Completed Tasks:
{{#each completed_tasks}}
- **{{task_name}}** ({{completion_time}}) - Quality: {{quality_score}}/10
{{/each}}

### ⏳ Pending Tasks:
{{#each pending_tasks}}
- **{{task_name}}** - Waiting for: {{dependencies}}
{{/each}}

### 🚨 Issues & Blockers:
{{#if issues}}
{{#each issues}}
- **{{issue_type}}**: {{description}} (Priority: {{priority}})
{{/each}}
{{else}}
No current issues or blockers.
{{/if}}

### 📈 Performance Metrics:
- **Team Efficiency**: {{team_efficiency}}%
- **Quality Average**: {{average_quality}}/10
- **On-time Delivery**: {{on_time_percentage}}%

**Next Review**: {{next_review_time}}
