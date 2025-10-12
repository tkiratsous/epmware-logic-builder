# Workflow API Functions

The Workflow API provides functions for managing workflow processes, stages, tasks, and approvals within EPMware's request management system.

**Package**: `EW_WORKFLOW`  
**Usage**: `ew_workflow.<function_name>`

## Overview

The Workflow API enables:
- Workflow stage management
- Task creation and assignment
- Approval processing
- Stage transitions
- Workflow routing
- Task delegation

## Workflow Information

### get_workflow_stage

Returns the current workflow stage for a request.

```sql
FUNCTION get_workflow_stage(
  p_request_id IN NUMBER
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_stage VARCHAR2(100);
BEGIN
  l_stage := ew_workflow.get_workflow_stage(p_request_id => 12345);
  
  DBMS_OUTPUT.PUT_LINE('Current Stage: ' || l_stage);
  
  IF l_stage = 'APPROVAL' THEN
    -- Process approval stage
    process_approvals(12345);
  END IF;
END;
```

### get_workflow_info

Returns complete workflow information for a request.

```sql
FUNCTION get_workflow_info(
  p_request_id IN NUMBER
) RETURN workflow_info_rec;
```

**Record Structure:**
```sql
TYPE workflow_info_rec IS RECORD (
  workflow_id        NUMBER,
  workflow_name      VARCHAR2(100),
  current_stage      VARCHAR2(100),
  current_stage_id   NUMBER,
  stage_status       VARCHAR2(50),
  assigned_to        VARCHAR2(100),
  assigned_date      DATE,
  due_date          DATE
);
```

## Stage Management

### move_to_next_stage

Moves request to the next workflow stage.

```sql
PROCEDURE move_to_next_stage(
  p_request_id IN NUMBER,
  p_comments   IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  -- Complete current stage and move to next
  ew_workflow.move_to_next_stage(
    p_request_id => 12345,
    p_comments   => 'Initial review complete, moving to approval'
  );
  COMMIT;
  
  DBMS_OUTPUT.PUT_LINE('Moved to next stage successfully');
EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error moving stage: ' || SQLERRM);
    ROLLBACK;
END;
```

### move_to_stage

Moves request to a specific stage.

```sql
PROCEDURE move_to_stage(
  p_request_id  IN NUMBER,
  p_stage_name  IN VARCHAR2,
  p_comments    IN VARCHAR2 DEFAULT NULL
);
```

### rewind_to_stage

Rewinds request to a previous stage.

```sql
PROCEDURE rewind_to_stage(
  p_request_id  IN NUMBER,
  p_stage_name  IN VARCHAR2,
  p_reason      IN VARCHAR2
);
```

**Example:**
```sql
BEGIN
  -- Send back for revision
  ew_workflow.rewind_to_stage(
    p_request_id => 12345,
    p_stage_name => 'REVIEW',
    p_reason     => 'Additional information required'
  );
END;
```

## Task Management

### create_task

Creates a new workflow task.

```sql
FUNCTION create_task(
  p_request_id    IN NUMBER,
  p_task_type     IN VARCHAR2,
  p_assigned_to   IN VARCHAR2,
  p_description   IN VARCHAR2,
  p_due_date      IN DATE DEFAULT NULL
) RETURN NUMBER;  -- Returns task_id
```

**Example:**
```sql
DECLARE
  l_task_id NUMBER;
BEGIN
  l_task_id := ew_workflow.create_task(
    p_request_id  => 12345,
    p_task_type   => 'REVIEW',
    p_assigned_to => 'JSMITH',
    p_description => 'Review account changes',
    p_due_date    => SYSDATE + 3
  );
  
  DBMS_OUTPUT.PUT_LINE('Created task: ' || l_task_id);
END;
```

### complete_task

Marks a task as complete.

```sql
PROCEDURE complete_task(
  p_task_id    IN NUMBER,
  p_comments   IN VARCHAR2 DEFAULT NULL,
  p_outcome    IN VARCHAR2 DEFAULT 'COMPLETED'
);
```

### reassign_task

Reassigns a task to another user.

```sql
PROCEDURE reassign_task(
  p_task_id       IN NUMBER,
  p_new_assignee  IN VARCHAR2,
  p_reason        IN VARCHAR2 DEFAULT NULL
);
```

### get_user_tasks

Returns all pending tasks for a user.

```sql
FUNCTION get_user_tasks(
  p_user_name IN VARCHAR2 DEFAULT USER
) RETURN task_list_tbl;
```

**Example:**
```sql
DECLARE
  l_tasks ew_workflow.task_list_tbl;
BEGIN
  l_tasks := ew_workflow.get_user_tasks(p_user_name => USER);
  
  DBMS_OUTPUT.PUT_LINE('You have ' || l_tasks.COUNT || ' pending tasks:');
  
  FOR i IN 1..l_tasks.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(i || '. ' || l_tasks(i).task_description ||
                         ' (Due: ' || l_tasks(i).due_date || ')');
  END LOOP;
END;
```

## Approval Functions

### approve_request

Approves a request at the current stage.

```sql
PROCEDURE approve_request(
  p_request_id IN NUMBER,
  p_comments   IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  -- Approve with comments
  ew_workflow.approve_request(
    p_request_id => 12345,
    p_comments   => 'Approved - all validations passed'
  );
  
  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Request approved successfully');
EXCEPTION
  WHEN ew_workflow.already_approved THEN
    DBMS_OUTPUT.PUT_LINE('Request already approved');
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE;
END;
```

### reject_request

Rejects a request with reason.

```sql
PROCEDURE reject_request(
  p_request_id IN NUMBER,
  p_reason     IN VARCHAR2
);
```

### approve_request_lines

Approves specific request lines.

```sql
PROCEDURE approve_request_lines(
  p_request_id      IN NUMBER,
  p_line_ids        IN ew_global.g_number_tbl,
  p_comments        IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
DECLARE
  l_lines_to_approve ew_global.g_number_tbl;
BEGIN
  -- Select specific lines to approve
  l_lines_to_approve(1) := 101;
  l_lines_to_approve(2) := 102;
  l_lines_to_approve(3) := 105;
  
  ew_workflow.approve_request_lines(
    p_request_id => 12345,
    p_line_ids   => l_lines_to_approve,
    p_comments   => 'Approved selected lines only'
  );
END;
```

## Delegation and Escalation

### delegate_approval

Delegates approval authority to another user.

```sql
PROCEDURE delegate_approval(
  p_from_user   IN VARCHAR2,
  p_to_user     IN VARCHAR2,
  p_start_date  IN DATE DEFAULT SYSDATE,
  p_end_date    IN DATE DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  -- Set up vacation delegation
  ew_workflow.delegate_approval(
    p_from_user  => 'JSMITH',
    p_to_user    => 'MJONES',
    p_start_date => SYSDATE,
    p_end_date   => SYSDATE + 14
  );
END;
```

### escalate_task

Escalates a task to supervisor.

```sql
PROCEDURE escalate_task(
  p_task_id    IN NUMBER,
  p_reason     IN VARCHAR2
);
```

## Workflow Configuration

### get_workflow_definition

Returns workflow definition for a request type.

```sql
FUNCTION get_workflow_definition(
  p_workflow_name IN VARCHAR2
) RETURN workflow_def_rec;
```

### set_workflow_parameter

Sets a workflow parameter value.

```sql
PROCEDURE set_workflow_parameter(
  p_request_id     IN NUMBER,
  p_parameter_name IN VARCHAR2,
  p_parameter_value IN VARCHAR2
);
```

**Example:**
```sql
BEGIN
  -- Set workflow routing parameter
  ew_workflow.set_workflow_parameter(
    p_request_id      => 12345,
    p_parameter_name  => 'APPROVAL_LEVEL',
    p_parameter_value => 'EXECUTIVE'
  );
  
  -- Set notification preference
  ew_workflow.set_workflow_parameter(
    p_request_id      => 12345,
    p_parameter_name  => 'NOTIFY_ON_APPROVAL',
    p_parameter_value => 'Y'
  );
END;
```

## Advanced Workflow Features

### Parallel Approvals

```sql
DECLARE
  l_approvers ew_global.g_value_tbl;
  l_task_ids ew_global.g_number_tbl;
BEGIN
  -- Set up parallel approval tasks
  l_approvers(1) := 'MANAGER1';
  l_approvers(2) := 'MANAGER2';
  l_approvers(3) := 'MANAGER3';
  
  FOR i IN 1..l_approvers.COUNT LOOP
    l_task_ids(i) := ew_workflow.create_task(
      p_request_id  => 12345,
      p_task_type   => 'PARALLEL_APPROVAL',
      p_assigned_to => l_approvers(i),
      p_description => 'Parallel approval required'
    );
  END LOOP;
  
  -- Wait for all approvals
  ew_workflow.wait_for_tasks(l_task_ids);
END;
```

### Conditional Routing

```sql
DECLARE
  l_amount NUMBER;
  l_next_stage VARCHAR2(100);
BEGIN
  -- Get request amount
  SELECT total_amount
    INTO l_amount
    FROM request_summary
   WHERE request_id = 12345;
  
  -- Determine routing based on amount
  IF l_amount > 1000000 THEN
    l_next_stage := 'EXECUTIVE_APPROVAL';
  ELSIF l_amount > 100000 THEN
    l_next_stage := 'MANAGER_APPROVAL';
  ELSE
    l_next_stage := 'AUTO_APPROVE';
  END IF;
  
  -- Route to appropriate stage
  ew_workflow.move_to_stage(
    p_request_id => 12345,
    p_stage_name => l_next_stage
  );
END;
```

### Auto-Approval Logic

```sql
DECLARE
  l_auto_approve VARCHAR2(1) := 'Y';
  l_validation_errors ew_global.g_value_tbl;
BEGIN
  -- Check auto-approval conditions
  l_validation_errors := validate_for_auto_approval(12345);
  
  IF l_validation_errors.COUNT > 0 THEN
    l_auto_approve := 'N';
  END IF;
  
  IF l_auto_approve = 'Y' THEN
    -- Auto-approve
    ew_workflow.approve_request(
      p_request_id => 12345,
      p_comments   => 'Auto-approved - all conditions met'
    );
    
    -- Move to next stage
    ew_workflow.move_to_next_stage(p_request_id => 12345);
  ELSE
    -- Route to manual approval
    ew_workflow.move_to_stage(
      p_request_id => 12345,
      p_stage_name => 'MANUAL_REVIEW'
    );
  END IF;
END;
```

## Workflow Monitoring

### get_workflow_history

Returns workflow history for a request.

```sql
FUNCTION get_workflow_history(
  p_request_id IN NUMBER
) RETURN workflow_history_tbl;
```

**Example:**
```sql
DECLARE
  l_history ew_workflow.workflow_history_tbl;
BEGIN
  l_history := ew_workflow.get_workflow_history(p_request_id => 12345);
  
  DBMS_OUTPUT.PUT_LINE('Workflow History:');
  FOR i IN 1..l_history.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(
      l_history(i).stage_name || ' - ' ||
      l_history(i).action || ' by ' ||
      l_history(i).user_name || ' on ' ||
      TO_CHAR(l_history(i).action_date, 'DD-MON-YYYY HH24:MI')
    );
  END LOOP;
END;
```

### get_pending_approvals

Returns all pending approvals for a user.

```sql
FUNCTION get_pending_approvals(
  p_user_name IN VARCHAR2 DEFAULT USER
) RETURN approval_list_tbl;
```

## Notification Management

### send_task_notification

Sends notification for a task.

```sql
PROCEDURE send_task_notification(
  p_task_id         IN NUMBER,
  p_notification_type IN VARCHAR2  -- 'ASSIGNED', 'REMINDER', 'OVERDUE'
);
```

### set_notification_preference

Sets user notification preferences.

```sql
PROCEDURE set_notification_preference(
  p_user_name       IN VARCHAR2,
  p_event_type      IN VARCHAR2,
  p_notify_method   IN VARCHAR2  -- 'EMAIL', 'SMS', 'BOTH', 'NONE'
);
```

## Error Handling

```sql
BEGIN
  ew_workflow.approve_request(p_request_id => 12345);
EXCEPTION
  WHEN ew_workflow.not_authorized THEN
    DBMS_OUTPUT.PUT_LINE('You are not authorized to approve');
  WHEN ew_workflow.invalid_stage THEN
    DBMS_OUTPUT.PUT_LINE('Request not in approval stage');
  WHEN ew_workflow.already_processed THEN
    DBMS_OUTPUT.PUT_LINE('Request already processed');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
```

## Best Practices

1. **Check Stage Before Actions**
   ```sql
   IF get_workflow_stage(p_request_id) = 'APPROVAL' THEN
     approve_request(p_request_id);
   END IF;
   ```

2. **Include Comments**
   ```sql
   -- Always provide meaningful comments
   approve_request(
     p_request_id => 12345,
     p_comments   => 'Validated against policy XYZ'
   );
   ```

3. **Handle Task Delegation**
   ```sql
   -- Set up delegation before absence
   delegate_approval(USER, 'BACKUP_USER', SYSDATE, SYSDATE+7);
   ```

4. **Monitor Overdue Tasks**
   ```sql
   -- Check for overdue tasks regularly
   FOR rec IN (SELECT * FROM get_overdue_tasks()) LOOP
     escalate_task(rec.task_id, 'Overdue by ' || rec.days_overdue);
   END LOOP;
   ```

## Next Steps

- [String APIs](string.md)
- [Lookup APIs](lookup.md)
- [Security APIs](security.md)