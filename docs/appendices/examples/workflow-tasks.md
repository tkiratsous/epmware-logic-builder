# Workflow Task Examples

Workflow task scripts automate actions during request lifecycle stages, enabling conditional approvals, notifications, validations, and integration triggers based on your business processes.

## Email Notification on Approval

🟢 **Level:** Basic  
**Purpose:** Send email notifications when requests are approved

```sql
/*
  Script: WORKFLOW_APPROVAL_NOTIFICATION
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Send email notification when request is approved
  
  Triggers: On workflow stage transition to "Approved"
*/
DECLARE
  c_script_name     VARCHAR2(100) := 'WORKFLOW_APPROVAL_NOTIFICATION';
  v_request_id      NUMBER;
  v_request_name    VARCHAR2(500);
  v_requester       VARCHAR2(100);
  v_approver        VARCHAR2(100);
  v_email_to        VARCHAR2(500);
  v_email_subject   VARCHAR2(500);
  v_email_body      CLOB;
  v_approval_date   DATE;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Get workflow context
  v_request_id := ew_lb_api.g_request_id;
  v_request_name := ew_lb_api.g_request_name;
  v_requester := ew_lb_api.g_created_by;
  v_approver := ew_lb_api.g_approved_by;
  v_approval_date := SYSDATE;
  
  log('Processing approval notification for request: ' || v_request_id);
  
  -- Get requester email
  SELECT email
  INTO   v_email_to
  FROM   ew_users
  WHERE  username = v_requester;
  
  -- Build email content
  v_email_subject := 'Request Approved: ' || v_request_name;
  
  v_email_body := '<html><body>' ||
                  '<h2>Your request has been approved</h2>' ||
                  '<p>Dear ' || v_requester || ',</p>' ||
                  '<p>Your request has been approved by ' || v_approver || '.</p>' ||
                  '<table border="1" style="border-collapse: collapse;">' ||
                  '<tr><td><b>Request ID:</b></td><td>' || v_request_id || '</td></tr>' ||
                  '<tr><td><b>Request Name:</b></td><td>' || v_request_name || '</td></tr>' ||
                  '<tr><td><b>Approved By:</b></td><td>' || v_approver || '</td></tr>' ||
                  '<tr><td><b>Approval Date:</b></td><td>' || 
                  TO_CHAR(v_approval_date, 'DD-MON-YYYY HH24:MI:SS') || '</td></tr>' ||
                  '</table>' ||
                  '<p>The changes will be processed shortly.</p>' ||
                  '<p>Best regards,<br/>EPMware System</p>' ||
                  '</body></html>';
  
  -- Send email
  ew_email_api.send_email(
    p_to      => v_email_to,
    p_subject => v_email_subject,
    p_body    => v_email_body,
    p_is_html => 'Y'
  );
  
  log('Email sent to: ' || v_email_to);
  
  -- Also notify stakeholders
  FOR rec IN (SELECT email
              FROM   ew_request_stakeholders rs
              JOIN   ew_users u ON rs.username = u.username
              WHERE  rs.request_id = v_request_id)
  LOOP
    ew_email_api.send_email(
      p_to      => rec.email,
      p_subject => 'FYI: ' || v_email_subject,
      p_body    => v_email_body,
      p_is_html => 'Y'
    );
    log('Stakeholder notified: ' || rec.email);
  END LOOP;
  
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    log('User email not found for: ' || v_requester);
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Email notification could not be sent - email not found';
    
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Email notification failed but request processed';
END;
```

## Conditional Auto-Approval

🟡 **Level:** Intermediate  
**Purpose:** Automatically approve requests based on business rules

```sql
/*
  Script: WORKFLOW_AUTO_APPROVAL
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Auto-approve requests meeting specific criteria
  
  Auto-Approval Rules:
  - Budget changes < $10,000
  - Non-financial property changes
  - Requests from approved auto-approval list
  - Within user's approval limit
*/
DECLARE
  c_script_name        VARCHAR2(100) := 'WORKFLOW_AUTO_APPROVAL';
  c_auto_approve_limit NUMBER := 10000;
  v_request_id         NUMBER;
  v_request_type       VARCHAR2(100);
  v_requester          VARCHAR2(100);
  v_total_amount       NUMBER := 0;
  v_can_auto_approve   BOOLEAN := FALSE;
  v_auto_approve_reason VARCHAR2(500);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION check_user_limit(p_username IN VARCHAR2) RETURN NUMBER IS
    v_limit NUMBER;
  BEGIN
    SELECT auto_approval_limit
    INTO   v_limit
    FROM   ew_user_settings
    WHERE  username = p_username;
    
    RETURN NVL(v_limit, 0);
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN 0;
  END check_user_limit;
  
  FUNCTION calculate_impact_amount RETURN NUMBER IS
    v_amount NUMBER := 0;
  BEGIN
    -- Sum all budget-related changes in the request
    SELECT NVL(SUM(
             CASE 
               WHEN prop_name = 'Budget' THEN
                 TO_NUMBER(new_value) - TO_NUMBER(NVL(old_value, '0'))
               ELSE 0
             END
           ), 0)
    INTO   v_amount
    FROM   ew_request_details
    WHERE  request_id = v_request_id
    AND    prop_name IN ('Budget', 'Forecast', 'Actual');
    
    RETURN ABS(v_amount);
  EXCEPTION
    WHEN OTHERS THEN
      RETURN 999999999; -- Large number to prevent auto-approval on error
  END calculate_impact_amount;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_request_id := ew_lb_api.g_request_id;
  v_request_type := ew_lb_api.g_request_type;
  v_requester := ew_lb_api.g_created_by;
  
  log('Evaluating auto-approval for request: ' || v_request_id);
  log('Request type: ' || v_request_type);
  log('Requester: ' || v_requester);
  
  -- Check if request type is eligible for auto-approval
  IF v_request_type NOT IN ('Property Update', 'Member Create', 'Hierarchy Move') THEN
    log('Request type not eligible for auto-approval');
    RETURN; -- No auto-approval for this type
  END IF;
  
  -- Calculate financial impact
  v_total_amount := calculate_impact_amount();
  log('Total financial impact: ' || v_total_amount);
  
  -- Evaluation logic
  IF v_total_amount = 0 THEN
    -- Non-financial change
    v_can_auto_approve := TRUE;
    v_auto_approve_reason := 'Non-financial property change';
    
  ELSIF v_total_amount <= c_auto_approve_limit THEN
    -- Within global auto-approval limit
    v_can_auto_approve := TRUE;
    v_auto_approve_reason := 'Amount within auto-approval limit: $' || 
                            TO_CHAR(v_total_amount, '999,999,999.99');
    
  ELSIF v_total_amount <= check_user_limit(v_requester) THEN
    -- Within user's personal limit
    v_can_auto_approve := TRUE;
    v_auto_approve_reason := 'Within user approval limit';
    
  ELSE
    -- Check for special approval rules
    FOR rec IN (SELECT rule_name, condition_sql
                FROM   ew_approval_rules
                WHERE  is_active = 'Y'
                AND    rule_type = 'AUTO_APPROVE')
    LOOP
      BEGIN
        -- Execute dynamic condition
        EXECUTE IMMEDIATE rec.condition_sql 
        INTO v_can_auto_approve
        USING v_request_id, v_requester, v_total_amount;
        
        IF v_can_auto_approve THEN
          v_auto_approve_reason := 'Special rule: ' || rec.rule_name;
          EXIT;
        END IF;
      EXCEPTION
        WHEN OTHERS THEN
          log('Error evaluating rule ' || rec.rule_name || ': ' || SQLERRM);
      END;
    END LOOP;
  END IF;
  
  -- Process auto-approval decision
  IF v_can_auto_approve THEN
    log('Auto-approving request. Reason: ' || v_auto_approve_reason);
    
    -- Set approval status
    ew_lb_api.g_status := ew_lb_api.g_success;
    ew_lb_api.g_message := 'Auto-approved: ' || v_auto_approve_reason;
    
    -- Update request status
    UPDATE ew_requests
    SET    status = 'Approved',
           approved_by = 'SYSTEM',
           approval_date = SYSDATE,
           approval_notes = v_auto_approve_reason
    WHERE  request_id = v_request_id;
    
    -- Log audit trail
    INSERT INTO ew_audit_trail
      (request_id, action, action_by, action_date, notes)
    VALUES
      (v_request_id, 'AUTO_APPROVED', 'SYSTEM', SYSDATE, v_auto_approve_reason);
    
    COMMIT;
    
  ELSE
    log('Manual approval required. Amount: ' || v_total_amount);
    -- Request continues through normal approval workflow
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    -- On error, require manual approval (safe default)
    ew_lb_api.g_status := ew_lb_api.g_success;
    ROLLBACK;
END;
```

## Pre-Submission Validation

🟡 **Level:** Intermediate  
**Purpose:** Validate request data before submission

```sql
/*
  Script: WORKFLOW_PRE_SUBMIT_VALIDATION
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Comprehensive validation before request submission
  
  Validates:
  - Required fields are populated
  - Business rules are satisfied
  - No conflicting changes
  - User has necessary permissions
*/
DECLARE
  c_script_name      VARCHAR2(100) := 'WORKFLOW_PRE_SUBMIT_VALIDATION';
  v_request_id       NUMBER;
  v_validation_errors VARCHAR2(4000);
  v_error_count      NUMBER := 0;
  v_warning_count    NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  PROCEDURE add_error(p_error IN VARCHAR2) IS
  BEGIN
    v_error_count := v_error_count + 1;
    v_validation_errors := v_validation_errors || 
                          '[ERROR ' || v_error_count || '] ' || 
                          p_error || CHR(10);
    log('Validation error: ' || p_error);
  END add_error;
  
  PROCEDURE add_warning(p_warning IN VARCHAR2) IS
  BEGIN
    v_warning_count := v_warning_count + 1;
    v_validation_errors := v_validation_errors || 
                          '[WARNING] ' || p_warning || CHR(10);
    log('Validation warning: ' || p_warning);
  END add_warning;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_request_id := ew_lb_api.g_request_id;
  
  log('Starting pre-submission validation for request: ' || v_request_id);
  
  -- 1. Check required justification for large changes
  FOR rec IN (SELECT member_name, prop_name, old_value, new_value
              FROM   ew_request_details
              WHERE  request_id = v_request_id
              AND    prop_name = 'Budget'
              AND    ABS(TO_NUMBER(new_value) - TO_NUMBER(NVL(old_value, '0'))) > 50000)
  LOOP
    DECLARE
      v_justification VARCHAR2(4000);
    BEGIN
      SELECT justification
      INTO   v_justification
      FROM   ew_request_justifications
      WHERE  request_id = v_request_id
      AND    member_name = rec.member_name;
      
      IF LENGTH(v_justification) < 100 THEN
        add_error('Budget change for ' || rec.member_name || 
                 ' requires detailed justification (min 100 chars)');
      END IF;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        add_error('Missing justification for large budget change: ' || 
                 rec.member_name);
    END;
  END LOOP;
  
  -- 2. Check for duplicate member names
  FOR rec IN (SELECT member_name, COUNT(*) cnt
              FROM   ew_request_details
              WHERE  request_id = v_request_id
              AND    action_type = 'CREATE'
              GROUP BY member_name
              HAVING COUNT(*) > 1)
  LOOP
    add_error('Duplicate member creation attempted: ' || rec.member_name);
  END LOOP;
  
  -- 3. Validate member naming conventions
  FOR rec IN (SELECT member_name
              FROM   ew_request_details
              WHERE  request_id = v_request_id
              AND    action_type = 'CREATE')
  LOOP
    IF NOT REGEXP_LIKE(rec.member_name, '^[A-Z][A-Z0-9_]{2,29}$') THEN
      add_error('Invalid member name format: ' || rec.member_name || 
               '. Must start with letter, contain only letters, numbers, underscores');
    END IF;
    
    -- Check for reserved names
    IF rec.member_name IN ('SYSTEM', 'ROOT', 'TOTAL', 'NONE', 'DEFAULT') THEN
      add_error('Cannot use reserved name: ' || rec.member_name);
    END IF;
  END LOOP;
  
  -- 4. Check for conflicting changes
  FOR rec IN (
    SELECT d1.member_name, d1.prop_name
    FROM   ew_request_details d1
    WHERE  d1.request_id = v_request_id
    AND    EXISTS (
      SELECT 1
      FROM   ew_requests r
      JOIN   ew_request_details d2 ON r.request_id = d2.request_id
      WHERE  r.status IN ('Pending', 'In Review')
      AND    r.request_id != v_request_id
      AND    d2.member_name = d1.member_name
      AND    d2.prop_name = d1.prop_name
    )
  )
  LOOP
    add_warning('Conflicting change pending for ' || 
               rec.member_name || '.' || rec.prop_name);
  END LOOP;
  
  -- 5. Validate hierarchical relationships
  FOR rec IN (
    SELECT member_name, parent_name
    FROM   ew_request_details
    WHERE  request_id = v_request_id
    AND    action_type IN ('CREATE', 'MOVE')
  )
  LOOP
    -- Check for circular references
    IF rec.member_name = rec.parent_name THEN
      add_error('Cannot make member its own parent: ' || rec.member_name);
    END IF;
    
    -- Check parent exists
    DECLARE
      v_parent_exists NUMBER;
    BEGIN
      SELECT COUNT(*)
      INTO   v_parent_exists
      FROM   ew_hierarchy
      WHERE  member_name = rec.parent_name
      AND    app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id;
      
      IF v_parent_exists = 0 THEN
        add_error('Parent member does not exist: ' || rec.parent_name);
      END IF;
    END;
  END LOOP;
  
  -- 6. Check user permissions
  DECLARE
    v_has_permission NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO   v_has_permission
    FROM   ew_user_permissions
    WHERE  username = ew_lb_api.g_created_by
    AND    app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    permission_type = 'MODIFY';
    
    IF v_has_permission = 0 THEN
      add_error('User lacks permission to modify this dimension');
    END IF;
  END;
  
  -- 7. Validate date properties
  FOR rec IN (
    SELECT member_name, prop_name, new_value
    FROM   ew_request_details
    WHERE  request_id = v_request_id
    AND    prop_name IN ('StartDate', 'EndDate', 'EffectiveDate')
  )
  LOOP
    BEGIN
      IF TO_DATE(rec.new_value, 'YYYY-MM-DD') > SYSDATE + 365 THEN
        add_warning('Date is more than 1 year in future: ' || 
                   rec.member_name || '.' || rec.prop_name);
      END IF;
    EXCEPTION
      WHEN OTHERS THEN
        add_error('Invalid date format for ' || 
                 rec.member_name || '.' || rec.prop_name);
    END;
  END LOOP;
  
  -- Process validation results
  IF v_error_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation failed with ' || v_error_count || 
                           ' error(s):' || CHR(10) || v_validation_errors;
  ELSIF v_warning_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Validation completed with warnings:' || 
                           CHR(10) || v_validation_errors;
  ELSE
    log('Validation passed successfully');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
END;
```

## Escalation Handler

🔴 **Level:** Advanced  
**Purpose:** Automatically escalate requests based on SLA and rules

```sql
/*
  Script: WORKFLOW_ESCALATION_HANDLER
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Handle automatic escalation of pending requests
  
  Escalation Rules:
  - Standard requests: Escalate after 3 days
  - Urgent requests: Escalate after 1 day
  - Critical requests: Escalate after 4 hours
  - Escalate through approval hierarchy
*/
DECLARE
  c_script_name         VARCHAR2(100) := 'WORKFLOW_ESCALATION_HANDLER';
  v_request_id          NUMBER;
  v_priority            VARCHAR2(20);
  v_current_approver    VARCHAR2(100);
  v_next_approver       VARCHAR2(100);
  v_time_pending        NUMBER;
  v_escalation_level    NUMBER;
  v_sla_hours          NUMBER;
  v_should_escalate    BOOLEAN := FALSE;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION get_next_approver(p_current_approver IN VARCHAR2,
                             p_escalation_level IN NUMBER) RETURN VARCHAR2 IS
    v_next VARCHAR2(100);
  BEGIN
    -- Get manager from hierarchy
    SELECT manager_username
    INTO   v_next
    FROM   ew_approval_hierarchy
    WHERE  username = p_current_approver
    AND    level_number = p_escalation_level + 1;
    
    RETURN v_next;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- If no next level, go to default escalation contact
      RETURN 'ADMIN_TEAM';
  END get_next_approver;
  
  PROCEDURE send_escalation_notice(p_old_approver IN VARCHAR2,
                                  p_new_approver IN VARCHAR2,
                                  p_request_id   IN NUMBER) IS
    v_email_body CLOB;
  BEGIN
    v_email_body := '<html><body>' ||
                   '<h2 style="color: red;">⚠ Request Escalated</h2>' ||
                   '<p>Request #' || p_request_id || ' has been escalated due to SLA breach.</p>' ||
                   '<table border="1">' ||
                   '<tr><td>Previous Approver:</td><td>' || p_old_approver || '</td></tr>' ||
                   '<tr><td>New Approver:</td><td>' || p_new_approver || '</td></tr>' ||
                   '<tr><td>Priority:</td><td>' || v_priority || '</td></tr>' ||
                   '<tr><td>Time Pending:</td><td>' || ROUND(v_time_pending/24, 1) || ' days</td></tr>' ||
                   '</table>' ||
                   '<p>Please review and action immediately.</p>' ||
                   '</body></html>';
    
    -- Send to new approver
    ew_email_api.send_email(
      p_to      => p_new_approver || '@company.com',
      p_subject => 'ESCALATED: Approval Required for Request #' || p_request_id,
      p_body    => v_email_body,
      p_is_html => 'Y',
      p_priority => 'HIGH'
    );
    
    -- CC to old approver
    ew_email_api.send_email(
      p_to      => p_old_approver || '@company.com',
      p_subject => 'FYI: Request #' || p_request_id || ' Escalated',
      p_body    => v_email_body,
      p_is_html => 'Y'
    );
    
  END send_escalation_notice;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_request_id := ew_lb_api.g_request_id;
  
  log('Checking escalation for request: ' || v_request_id);
  
  -- Get request details
  SELECT priority,
         current_approver,
         escalation_level,
         (SYSDATE - last_action_date) * 24 AS hours_pending
  INTO   v_priority,
         v_current_approver,
         v_escalation_level,
         v_time_pending
  FROM   ew_requests
  WHERE  request_id = v_request_id
  AND    status = 'Pending Approval';
  
  log('Priority: ' || v_priority);
  log('Current approver: ' || v_current_approver);
  log('Hours pending: ' || v_time_pending);
  
  -- Determine SLA based on priority
  v_sla_hours := CASE v_priority
                   WHEN 'Critical' THEN 4
                   WHEN 'Urgent' THEN 24
                   WHEN 'High' THEN 48
                   WHEN 'Normal' THEN 72
                   ELSE 120 -- Low priority: 5 days
                 END;
  
  -- Check if escalation needed
  IF v_time_pending > v_sla_hours THEN
    v_should_escalate := TRUE;
    log('SLA breached. Time to escalate.');
  END IF;
  
  -- Additional escalation triggers
  IF NOT v_should_escalate THEN
    -- Check for repeated reminder count
    DECLARE
      v_reminder_count NUMBER;
    BEGIN
      SELECT COUNT(*)
      INTO   v_reminder_count
      FROM   ew_workflow_log
      WHERE  request_id = v_request_id
      AND    action = 'REMINDER_SENT'
      AND    action_date > SYSDATE - 7;
      
      IF v_reminder_count >= 3 THEN
        v_should_escalate := TRUE;
        log('Multiple reminders ignored. Escalating.');
      END IF;
    END;
  END IF;
  
  -- Process escalation
  IF v_should_escalate THEN
    v_next_approver := get_next_approver(v_current_approver, 
                                         NVL(v_escalation_level, 0));
    
    log('Escalating to: ' || v_next_approver);
    
    -- Update request
    UPDATE ew_requests
    SET    current_approver = v_next_approver,
           escalation_level = NVL(escalation_level, 0) + 1,
           last_escalation_date = SYSDATE
    WHERE  request_id = v_request_id;
    
    -- Log escalation
    INSERT INTO ew_workflow_log
      (request_id, action, action_by, action_date, notes)
    VALUES
      (v_request_id, 'ESCALATED', 'SYSTEM', SYSDATE,
       'Escalated from ' || v_current_approver || ' to ' || v_next_approver ||
       ' due to SLA breach (' || v_sla_hours || ' hour limit)');
    
    -- Send notifications
    send_escalation_notice(v_current_approver, v_next_approver, v_request_id);
    
    -- Set return message
    ew_lb_api.g_message := 'Request escalated to ' || v_next_approver;
    
    COMMIT;
    
  ELSE
    log('No escalation required at this time');
    
    -- Check if reminder needed
    IF v_time_pending > (v_sla_hours * 0.75) THEN
      log('Sending reminder to current approver');
      
      -- Send reminder
      ew_email_api.send_email(
        p_to      => v_current_approver || '@company.com',
        p_subject => 'Reminder: Request #' || v_request_id || ' Pending Your Approval',
        p_body    => 'Request will be escalated in ' || 
                    ROUND(v_sla_hours - v_time_pending) || ' hours',
        p_priority => 'NORMAL'
      );
      
      -- Log reminder
      INSERT INTO ew_workflow_log
        (request_id, action, action_by, action_date)
      VALUES
        (v_request_id, 'REMINDER_SENT', 'SYSTEM', SYSDATE);
        
      COMMIT;
    END IF;
  END IF;
  
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    log('Request not found or not in pending status');
    
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Escalation check failed: ' || SQLERRM;
    ROLLBACK;
END;
```

## Integration Trigger

🔴 **Level:** Advanced  
**Purpose:** Trigger external system integration on workflow events

```sql
/*
  Script: WORKFLOW_INTEGRATION_TRIGGER
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Trigger external system integrations during workflow
  
  Integrations:
  - ERP system update on approval
  - Data warehouse refresh
  - Notification to external stakeholders
  - Audit system logging
*/
DECLARE
  c_script_name       VARCHAR2(100) := 'WORKFLOW_INTEGRATION_TRIGGER';
  v_request_id        NUMBER;
  v_integration_type  VARCHAR2(50);
  v_payload           CLOB;
  v_response          CLOB;
  v_status_code       NUMBER;
  v_integration_id    NUMBER;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION build_json_payload RETURN CLOB IS
    v_json CLOB;
  BEGIN
    -- Build JSON payload for external system
    v_json := '{' ||
              '"requestId": ' || v_request_id || ',' ||
              '"requestType": "' || ew_lb_api.g_request_type || '",' ||
              '"status": "' || ew_lb_api.g_workflow_stage || '",' ||
              '"timestamp": "' || TO_CHAR(SYSTIMESTAMP, 'YYYY-MM-DD"T"HH24:MI:SS.FF3"Z"') || '",' ||
              '"changes": [';
    
    -- Add change details
    FOR rec IN (SELECT member_name, prop_name, old_value, new_value
                FROM   ew_request_details
                WHERE  request_id = v_request_id)
    LOOP
      v_json := v_json || '{' ||
                '"member": "' || rec.member_name || '",' ||
                '"property": "' || rec.prop_name || '",' ||
                '"oldValue": "' || NVL(rec.old_value, '') || '",' ||
                '"newValue": "' || rec.new_value || '"' ||
                '},';
    END LOOP;
    
    -- Remove trailing comma and close
    v_json := RTRIM(v_json, ',') || '],' ||
              '"metadata": {' ||
              '"application": "' || ew_lb_api.g_app_name || '",' ||
              '"dimension": "' || ew_lb_api.g_dim_name || '",' ||
              '"user": "' || ew_lb_api.g_created_by || '"' ||
              '}}';
    
    RETURN v_json;
  END build_json_payload;
  
  PROCEDURE call_external_api(p_endpoint IN VARCHAR2,
                              p_payload  IN CLOB) IS
    v_request  UTL_HTTP.REQ;
    v_response UTL_HTTP.RESP;
    v_buffer   VARCHAR2(32767);
    v_result   CLOB;
  BEGIN
    -- Initialize HTTP request
    v_request := UTL_HTTP.BEGIN_REQUEST(
                   url    => p_endpoint,
                   method => 'POST'
                 );
    
    -- Set headers
    UTL_HTTP.SET_HEADER(v_request, 'Content-Type', 'application/json');
    UTL_HTTP.SET_HEADER(v_request, 'Authorization', 'Bearer ' || 
                       ew_config.get_param('API_TOKEN'));
    UTL_HTTP.SET_HEADER(v_request, 'Content-Length', LENGTH(p_payload));
    
    -- Send payload
    UTL_HTTP.WRITE_TEXT(v_request, p_payload);
    
    -- Get response
    v_response := UTL_HTTP.GET_RESPONSE(v_request);
    v_status_code := v_response.status_code;
    
    -- Read response body
    BEGIN
      LOOP
        UTL_HTTP.READ_TEXT(v_response, v_buffer, 32767);
        v_result := v_result || v_buffer;
      END LOOP;
    EXCEPTION
      WHEN UTL_HTTP.END_OF_BODY THEN
        NULL;
    END;
    
    UTL_HTTP.END_RESPONSE(v_response);
    
    -- Log response
    log('API Response Code: ' || v_status_code);
    log('API Response: ' || SUBSTR(v_result, 1, 1000));
    
    -- Store response
    v_response := v_result;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('API call failed: ' || SQLERRM);
      IF v_request.http_version IS NOT NULL THEN
        UTL_HTTP.END_RESPONSE(v_response);
      END IF;
      RAISE;
  END call_external_api;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_request_id := ew_lb_api.g_request_id;
  
  log('Processing integration trigger for request: ' || v_request_id);
  log('Workflow stage: ' || ew_lb_api.g_workflow_stage);
  
  -- Determine integration based on workflow stage
  CASE ew_lb_api.g_workflow_stage
    
    WHEN 'Approved' THEN
      -- Trigger ERP update
      v_integration_type := 'ERP_UPDATE';
      v_payload := build_json_payload();
      
      BEGIN
        -- Log integration attempt
        INSERT INTO ew_integration_log
          (request_id, integration_type, payload, created_date, status)
        VALUES
          (v_request_id, v_integration_type, v_payload, SYSDATE, 'PENDING')
        RETURNING integration_id INTO v_integration_id;
        
        -- Call ERP API
        call_external_api(
          p_endpoint => ew_config.get_param('ERP_API_ENDPOINT'),
          p_payload  => v_payload
        );
        
        -- Update integration status
        UPDATE ew_integration_log
        SET    status = 'SUCCESS',
               response = v_response,
               response_code = v_status_code,
               completed_date = SYSDATE
        WHERE  integration_id = v_integration_id;
        
        log('ERP integration successful');
        
      EXCEPTION
        WHEN OTHERS THEN
          -- Log failure but don't stop workflow
          UPDATE ew_integration_log
          SET    status = 'FAILED',
                 error_message = SQLERRM,
                 completed_date = SYSDATE
          WHERE  integration_id = v_integration_id;
          
          log('ERP integration failed: ' || SQLERRM);
          
          -- Set warning status
          ew_lb_api.g_status := ew_lb_api.g_warning;
          ew_lb_api.g_message := 'Request approved but ERP update failed';
      END;
      
    WHEN 'Deployed' THEN
      -- Trigger data warehouse refresh
      v_integration_type := 'DW_REFRESH';
      
      BEGIN
        -- Queue refresh job
        DBMS_SCHEDULER.CREATE_JOB(
          job_name   => 'DW_REFRESH_' || v_request_id,
          job_type   => 'STORED_PROCEDURE',
          job_action => 'EW_DW_INTEGRATION.REFRESH_DIMENSION',
          start_date => SYSTIMESTAMP,
          enabled    => TRUE,
          comments   => 'Triggered by request ' || v_request_id
        );
        
        log('Data warehouse refresh job queued');
        
      EXCEPTION
        WHEN OTHERS THEN
          log('Failed to queue DW refresh: ' || SQLERRM);
      END;
      
    WHEN 'Rejected' THEN
      -- Notify external stakeholders
      v_integration_type := 'EXTERNAL_NOTIFICATION';
      
      -- Send to external notification service
      BEGIN
        call_external_api(
          p_endpoint => ew_config.get_param('NOTIFICATION_API'),
          p_payload  => '{"event": "REQUEST_REJECTED", "id": ' || 
                       v_request_id || '}'
        );
      EXCEPTION
        WHEN OTHERS THEN
          log('External notification failed: ' || SQLERRM);
      END;
      
    ELSE
      log('No integration defined for stage: ' || ew_lb_api.g_workflow_stage);
  END CASE;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception in integration trigger: ' || SQLERRM);
    -- Don't fail the workflow due to integration issues
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Integration error: ' || SUBSTR(SQLERRM, 1, 200);
    ROLLBACK;
END;
```

## Testing Workflow Scripts

### Workflow Test Framework

```sql
/*
  Script: TEST_WORKFLOW_SCRIPTS
  Purpose: Test framework for workflow task scripts
*/
DECLARE
  c_script_name VARCHAR2(100) := 'TEST_WORKFLOW_SCRIPTS';
  v_test_request_id NUMBER;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END log;
  
  PROCEDURE create_test_request RETURN NUMBER IS
    v_id NUMBER;
  BEGIN
    INSERT INTO ew_requests
      (request_name, request_type, created_by, created_date, status)
    VALUES
      ('TEST_' || TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS'),
       'Test Request', 'TEST_USER', SYSDATE, 'Draft')
    RETURNING request_id INTO v_id;
    
    -- Add test details
    INSERT INTO ew_request_details
      (request_id, member_name, prop_name, old_value, new_value)
    VALUES
      (v_id, 'TEST_MEMBER', 'Budget', '1000', '2000');
    
    RETURN v_id;
  END create_test_request;
  
  PROCEDURE test_workflow_stage(p_stage IN VARCHAR2) IS
  BEGIN
    -- Set workflow context
    ew_lb_api.g_request_id := v_test_request_id;
    ew_lb_api.g_workflow_stage := p_stage;
    ew_lb_api.g_created_by := 'TEST_USER';
    
    log('Testing stage: ' || p_stage);
    
    -- Execute workflow logic
    -- (Insert your workflow script logic here)
    
    log('Stage test result - Status: ' || ew_lb_api.g_status || 
        ', Message: ' || NVL(ew_lb_api.g_message, 'None'));
  END test_workflow_stage;
  
BEGIN
  log('Starting workflow script tests');
  
  -- Create test request
  v_test_request_id := create_test_request();
  log('Created test request: ' || v_test_request_id);
  
  -- Test different workflow stages
  test_workflow_stage('Submitted');
  test_workflow_stage('In Review');
  test_workflow_stage('Approved');
  test_workflow_stage('Deployed');
  
  -- Cleanup
  DELETE FROM ew_request_details WHERE request_id = v_test_request_id;
  DELETE FROM ew_requests WHERE request_id = v_test_request_id;
  COMMIT;
  
  log('Workflow tests completed');
  
END;
```

## Best Practices

1. **Handle failures gracefully** - Don't break the workflow
2. **Log all actions** - For audit trail and debugging
3. **Use appropriate status codes** - SUCCESS, WARNING, ERROR
4. **Consider performance** - Async processing for heavy operations
5. **Implement retry logic** - For external integrations
6. **Secure sensitive data** - Don't log passwords or tokens
7. **Test edge cases** - Empty requests, missing data, timeouts
8. **Document business rules** - In script comments

## Next Steps

- See [Hierarchy Action Examples](hierarchy-actions.md)
- Review [Advanced Patterns](advanced-patterns.md)
- Learn about [Performance Optimization](../advanced/performance.md)