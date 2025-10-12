# Workflow Custom Tasks

Workflow Custom Tasks provide complex business logic at specific workflow stages, enabling dynamic routing, automated decisions, and sophisticated approval processes. These scripts execute during workflow progression and can modify workflow behavior.

## Overview

Custom Tasks enable:
- **Dynamic Routing**: Change workflow path based on conditions
- **Automated Decisions**: Approve/reject programmatically
- **Stage Management**: Add/remove/skip workflow stages
- **Task Assignment**: Reassign tasks dynamically
- **Complex Logic**: Implement sophisticated business rules
- **Integration**: Call external systems for decisions

![Custom Task Execution](../../assets/images/custom-task-flow.png)
*Figure: Custom task execution within workflow stages*

## When to Use

Custom Tasks are ideal for:
- Conditional workflow branching
- Automated approval decisions
- Dynamic task assignment
- Calculating approval levels
- Integrating external approvals
- Complex business rule implementation
- Workflow optimization (skip unnecessary steps)

## Key Capabilities

### Workflow Modification
- Add/remove stages dynamically
- Skip stages conditionally
- Change approval requirements
- Modify task parameters

### Task Control
- Auto-complete tasks
- Reassign to different users
- Escalate to managers
- Create parallel tasks

### Decision Making
- Approve/reject based on rules
- Calculate approval thresholds
- Determine routing paths
- Set workflow variables

## Configuration

### Step 1: Create Custom Task Script

Navigate to **Configuration → Logic Builder**:

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'WF_CUSTOM_ROUTING';
  l_amount NUMBER;
  l_category VARCHAR2(50);
  l_requires_legal BOOLEAN := FALSE;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Custom task for request: ' || ew_lb_api.g_request_id);
  log('Current stage: ' || ew_lb_api.g_wf_stage_name);
  
  -- Get request details
  SELECT total_amount, category
  INTO l_amount, l_category
  FROM request_headers
  WHERE request_id = ew_lb_api.g_request_id;
  
  -- Determine routing based on amount and category
  IF l_amount > 1000000 THEN
    -- Add executive approval
    ew_workflow.add_wf_stage_name(
      p_request_id   => ew_lb_api.g_request_id,
      p_wf_stage_name => 'Executive_Approval',
      x_sts          => ew_lb_api.g_status,
      x_msg          => ew_lb_api.g_message
    );
    log('Added executive approval stage');
  END IF;
  
  -- Check if legal review needed
  IF l_category IN ('CONTRACT', 'ACQUISITION', 'COMPLIANCE') THEN
    l_requires_legal := TRUE;
  ELSIF l_amount > 500000 THEN
    l_requires_legal := TRUE;
  END IF;
  
  IF l_requires_legal THEN
    -- Add legal review stage
    ew_workflow.add_wf_stage_name(
      p_request_id   => ew_lb_api.g_request_id,
      p_wf_stage_name => 'Legal_Review',
      x_sts          => ew_lb_api.g_status,
      x_msg          => ew_lb_api.g_message
    );
  ELSE
    -- Remove legal review if exists
    ew_workflow.remove_wf_stage_name(
      p_request_id   => ew_lb_api.g_request_id,
      p_wf_stage_name => 'Legal_Review',
      x_sts          => ew_lb_api.g_status,
      x_msg          => ew_lb_api.g_message
    );
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Error in custom task: ' || SQLERRM);
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Routing error: ' || SQLERRM;
END;
```

### Step 2: Configure in Workflow Tasks

Navigate to **Workflow → Tasks**:

1. Select the workflow
2. Choose the stage
3. Add "Custom Function" task type
4. Select your Logic Script
5. Configure task parameters

![Custom Task Configuration](../../assets/images/custom-task-config.png)
*Figure: Configuring custom task in workflow*

## Common Custom Task Patterns

### Pattern 1: Auto-Approval Logic

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'WF_AUTO_APPROVAL';
  l_amount NUMBER;
  l_vendor_status VARCHAR2(50);
  l_auto_approve BOOLEAN := FALSE;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  log('Checking auto-approval criteria');
  
  -- Get request details
  SELECT amount, vendor_status
  INTO l_amount, l_vendor_status
  FROM request_summary_view
  WHERE request_id = ew_lb_api.g_request_id;
  
  -- Auto-approval criteria
  IF l_amount < 5000 AND l_vendor_status = 'PREFERRED' THEN
    l_auto_approve := TRUE;
  ELSIF l_amount < 1000 AND has_blanket_po(ew_lb_api.g_request_id) THEN
    l_auto_approve := TRUE;
  ELSIF is_recurring_payment(ew_lb_api.g_request_id) THEN
    l_auto_approve := TRUE;
  END IF;
  
  IF l_auto_approve THEN
    -- Complete current task with approval
    ew_lb_api.g_wf_task_rec.task_action := 'APPROVE';
    ew_lb_api.g_wf_task_rec.comments := 
      'Auto-approved per policy (Amount: $' || l_amount || ')';
    
    log('Request auto-approved');
    
    -- Skip detailed review stage
    ew_workflow.remove_wf_stage_name(
      p_request_id   => ew_lb_api.g_request_id,
      p_wf_stage_name => 'Detailed_Review',
      x_sts          => ew_lb_api.g_status,
      x_msg          => ew_lb_api.g_message
    );
  END IF;
END;
```

### Pattern 2: Dynamic Task Assignment

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'WF_DYNAMIC_ASSIGNMENT';
  l_department VARCHAR2(50);
  l_amount NUMBER;
  l_assignee VARCHAR2(100);
  l_num_approvals NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get request details
  SELECT department, total_amount
  INTO l_department, l_amount
  FROM request_headers
  WHERE request_id = ew_lb_api.g_request_id;
  
  -- Determine assignee based on department and amount
  IF l_department = 'IT' THEN
    IF l_amount > 50000 THEN
      l_assignee := 'IT_DIRECTOR';
      l_num_approvals := 2; -- Require 2 approvals
    ELSE
      l_assignee := 'IT_MANAGER';
      l_num_approvals := 1;
    END IF;
  ELSIF l_department = 'FINANCE' THEN
    IF l_amount > 100000 THEN
      l_assignee := 'CFO';
      l_num_approvals := 1;
    ELSE
      l_assignee := 'FINANCE_MANAGER';
      l_num_approvals := 1;
    END IF;
  ELSE
    -- Default routing
    l_assignee := get_department_head(l_department);
    l_num_approvals := 1;
  END IF;
  
  -- Update task assignment
  ew_workflow.upd_wf_stage_task_assignee(
    p_request_id    => ew_lb_api.g_request_id,
    p_wf_stage_name => ew_lb_api.g_wf_stage_name,
    p_wf_task_name  => 'Manager_Approval',
    p_assignee      => l_assignee,
    x_sts          => ew_lb_api.g_status,
    x_msg          => ew_lb_api.g_message
  );
  
  -- Update number of required approvals
  ew_workflow.upd_wf_stage_task_approval_cnt(
    p_request_id        => ew_lb_api.g_request_id,
    p_wf_stage_name     => ew_lb_api.g_wf_stage_name,
    p_wf_task_name      => 'Manager_Approval',
    p_num_of_approvals  => l_num_approvals,
    x_sts              => ew_lb_api.g_status,
    x_msg              => ew_lb_api.g_message
  );
  
  ew_debug.log('Task assigned to: ' || l_assignee || 
               ' (Required approvals: ' || l_num_approvals || ')');
END;
```

### Pattern 3: Conditional Stage Management

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'WF_CONDITIONAL_STAGES';
  l_risk_level VARCHAR2(20);
  l_compliance_required BOOLEAN;
  l_current_stage_num NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Calculate risk level
  l_risk_level := calculate_risk_level(ew_lb_api.g_request_id);
  
  -- Get current stage number
  SELECT stage_sequence
  INTO l_current_stage_num
  FROM workflow_stages
  WHERE request_id = ew_lb_api.g_request_id
  AND stage_name = ew_lb_api.g_wf_stage_name;
  
  -- Manage stages based on risk
  CASE l_risk_level
    WHEN 'HIGH' THEN
      -- Add multiple review stages
      add_stage_after_current('Risk_Assessment');
      add_stage_after_current('Compliance_Review');
      add_stage_after_current('Executive_Review');
      
    WHEN 'MEDIUM' THEN
      -- Add single review
      add_stage_after_current('Manager_Review');
      -- Remove unnecessary stages
      ew_workflow.remove_wf_stage_name(
        p_request_id   => ew_lb_api.g_request_id,
        p_wf_stage_name => 'Detailed_Analysis',
        x_sts          => ew_lb_api.g_status,
        x_msg          => ew_lb_api.g_message
      );
      
    WHEN 'LOW' THEN
      -- Fast track - remove most stages
      remove_stages_after_current(
        p_except => 'Final_Approval,Deployment'
      );
      
    ELSE
      NULL; -- Standard flow
  END CASE;
  
  -- Check compliance requirements
  l_compliance_required := check_compliance_needed(
    p_request_id => ew_lb_api.g_request_id,
    p_risk_level => l_risk_level
  );
  
  IF l_compliance_required THEN
    -- Ensure compliance stage exists
    IF NOT stage_exists('Compliance_Check') THEN
      add_stage_before('Final_Approval', 'Compliance_Check');
    END IF;
  END IF;
  
  ew_debug.log('Risk level: ' || l_risk_level || 
               ', Stages adjusted accordingly');
END;
```

### Pattern 4: Recall to Previous Stage

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'WF_RECALL_LOGIC';
  l_validation_errors VARCHAR2(4000);
  l_recall_stage VARCHAR2(100);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Perform validation at approval stage
  IF ew_lb_api.g_wf_stage_name = 'Final_Approval' THEN
    
    -- Validate request completeness
    l_validation_errors := validate_for_final_approval(
      p_request_id => ew_lb_api.g_request_id
    );
    
    IF l_validation_errors IS NOT NULL THEN
      -- Determine which stage to recall to
      IF INSTR(l_validation_errors, 'budget') > 0 THEN
        l_recall_stage := 'Budget_Review';
      ELSIF INSTR(l_validation_errors, 'technical') > 0 THEN
        l_recall_stage := 'Technical_Review';
      ELSE
        l_recall_stage := 'Initial_Review';
      END IF;
      
      -- Set recall parameters
      ew_lb_api.g_wf_recall_stage := l_recall_stage;
      ew_lb_api.g_message := 'Recalled for correction: ' || 
                              l_validation_errors;
      
      -- Add comment to request
      ew_workflow.add_request_comment(
        p_request_id => ew_lb_api.g_request_id,
        p_comment    => 'Recalled to ' || l_recall_stage || 
                        ': ' || l_validation_errors
      );
      
      ew_debug.log('Request recalled to: ' || l_recall_stage);
    END IF;
  END IF;
END;
```

### Pattern 5: Parallel Task Creation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'WF_PARALLEL_TASKS';
  l_reviewers VARCHAR2(500);
  l_review_type VARCHAR2(20);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Determine if parallel review needed
  IF ew_lb_api.g_wf_stage_name = 'Technical_Review' THEN
    
    -- Get list of required reviewers
    l_reviewers := get_technical_reviewers(
      p_request_type => get_request_type(ew_lb_api.g_request_id),
      p_amount      => get_request_amount(ew_lb_api.g_request_id)
    );
    
    -- Determine review type
    IF get_request_urgency(ew_lb_api.g_request_id) = 'HIGH' THEN
      l_review_type := 'ANY'; -- Any one can approve
    ELSE
      l_review_type := 'ALL'; -- All must approve
    END IF;
    
    -- Create parallel tasks
    ew_workflow.create_parallel_tasks(
      p_request_id   => ew_lb_api.g_request_id,
      p_stage_name   => ew_lb_api.g_wf_stage_name,
      p_task_name    => 'Parallel_Review',
      p_assignees    => l_reviewers,
      p_approval_type => l_review_type,
      p_due_days     => 3
    );
    
    ew_debug.log('Created parallel tasks for: ' || l_reviewers);
  END IF;
END;
```

## Advanced Features

### Workflow Variables

Store and retrieve workflow-specific data:

```sql
-- Set workflow variable
ew_workflow.set_wf_variable(
  p_request_id => ew_lb_api.g_request_id,
  p_var_name   => 'RISK_SCORE',
  p_var_value  => TO_CHAR(l_risk_score)
);

-- Get workflow variable
l_risk_score := TO_NUMBER(
  ew_workflow.get_wf_variable(
    p_request_id => ew_lb_api.g_request_id,
    p_var_name   => 'RISK_SCORE'
  )
);
```

### External System Integration

```sql
DECLARE
  l_external_status VARCHAR2(50);
  l_external_ref VARCHAR2(100);
BEGIN
  -- Call external approval system
  l_external_status := call_external_approval(
    p_request_id => ew_lb_api.g_request_id,
    p_amount    => get_request_amount(ew_lb_api.g_request_id),
    p_category  => get_request_category(ew_lb_api.g_request_id)
  );
  
  IF l_external_status = 'APPROVED' THEN
    -- Auto-complete current task
    ew_lb_api.g_wf_task_rec.task_action := 'APPROVE';
    ew_lb_api.g_wf_task_rec.comments := 
      'Approved by external system: ' || l_external_ref;
  ELSIF l_external_status = 'REJECTED' THEN
    -- Reject and stop workflow
    ew_lb_api.g_wf_task_rec.task_action := 'REJECT';
    ew_lb_api.g_wf_task_rec.comments := 
      'Rejected by external system: ' || l_external_ref;
  ELSE
    -- Manual review required
    NULL;
  END IF;
END;
```

### Escalation Logic

```sql
DECLARE
  l_days_pending NUMBER;
  l_escalation_level NUMBER;
  l_new_assignee VARCHAR2(100);
BEGIN
  -- Calculate days pending
  l_days_pending := TRUNC(SYSDATE - get_task_assigned_date(
    p_task_id => ew_lb_api.g_wf_task_id
  ));
  
  -- Determine escalation level
  l_escalation_level := CASE
    WHEN l_days_pending > 7 THEN 3
    WHEN l_days_pending > 5 THEN 2
    WHEN l_days_pending > 3 THEN 1
    ELSE 0
  END;
  
  IF l_escalation_level > 0 THEN
    -- Get escalation assignee
    l_new_assignee := get_escalation_assignee(
      p_current_assignee => get_current_assignee(ew_lb_api.g_wf_task_id),
      p_level           => l_escalation_level
    );
    
    -- Reassign task
    ew_workflow.reassign_task(
      p_task_id      => ew_lb_api.g_wf_task_id,
      p_new_assignee => l_new_assignee,
      p_reason       => 'Escalated after ' || l_days_pending || ' days'
    );
    
    -- Send escalation notification
    send_escalation_email(
      p_to        => l_new_assignee,
      p_request_id => ew_lb_api.g_request_id,
      p_days_pending => l_days_pending
    );
  END IF;
END;
```

## Best Practices

### 1. Idempotent Operations
```sql
-- Check before adding stage
IF NOT stage_exists('Legal_Review') THEN
  add_stage('Legal_Review');
END IF;

-- Check before removing
IF stage_exists('Optional_Review') THEN
  remove_stage('Optional_Review');
END IF;
```

### 2. Error Handling
```sql
BEGIN
  -- Custom task logic
  perform_custom_logic();
EXCEPTION
  WHEN OTHERS THEN
    -- Log error but allow workflow to continue
    ew_debug.log('Custom task error: ' || SQLERRM);
    -- Set warning message for user
    ew_lb_api.g_message := 'Warning: ' || SQLERRM;
    -- Don't fail the task
    ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### 3. Audit Trail
```sql
-- Log all routing decisions
ew_workflow.add_audit_entry(
  p_request_id => ew_lb_api.g_request_id,
  p_action     => 'ROUTE_DECISION',
  p_details    => 'Routed to ' || l_new_stage || 
                  ' based on amount: $' || l_amount
);
```

### 4. Performance
```sql
-- Cache request data for multiple checks
IF NOT g_request_cache.EXISTS(ew_lb_api.g_request_id) THEN
  load_request_to_cache(ew_lb_api.g_request_id);
END IF;

-- Use cached data
l_amount := g_request_cache(ew_lb_api.g_request_id).amount;
```

## Testing Custom Tasks

### Test Scenarios

1. **Normal Flow**: Standard approval path
2. **Auto-Approval**: Meets criteria for automation
3. **Complex Routing**: High-value, special category
4. **Escalation**: Delayed approval
5. **Recall**: Validation failure at final stage
6. **Parallel**: Multiple reviewers

### Debug Techniques
```sql
-- Comprehensive logging
ew_debug.log('=== Custom Task Debug ===');
ew_debug.log('Request: ' || ew_lb_api.g_request_id);
ew_debug.log('Stage: ' || ew_lb_api.g_wf_stage_name);
ew_debug.log('Task: ' || ew_lb_api.g_wf_task_name);
ew_debug.log('Decision: ' || l_routing_decision);
ew_debug.log('Action: ' || ew_lb_api.g_wf_task_rec.task_action);
```

## Performance Considerations

- **Cache Data**: Store frequently accessed data
- **Batch Operations**: Process multiple items together
- **Async Processing**: Defer heavy operations
- **Optimize Queries**: Use appropriate indexes
- **Early Exit**: Return quickly for simple cases

## Next Steps

- [On Submit Tasks](on-submit.md) - Pre-workflow validation
- [Request Line Approval](request-line-approval.md) - Approval validation
- [Workflow Index](index.md) - Workflow overview

---

!!! tip "Best Practice"
    Custom tasks should enhance workflow intelligence without adding complexity. Keep routing logic transparent and well-documented so users understand why requests follow specific paths.