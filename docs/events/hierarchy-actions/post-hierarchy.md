# Post-Hierarchy Action Scripts

Post-Hierarchy Action scripts execute after hierarchy changes are successfully committed, enabling automation, synchronization, and cascading operations. These scripts cannot prevent the change but can perform additional actions in response.

## Overview

Post-Hierarchy Actions automate tasks after changes:
- **Automation**: Create related structures automatically
- **Synchronization**: Update dependent systems
- **Defaults**: Set initial property values
- **Notifications**: Alert users of changes
- **Audit**: Track hierarchy modifications
- **Cleanup**: Remove orphaned data

![Post-Hierarchy Action Flow](../../assets/images/post-hierarchy-flow.png)
*Figure: Post-hierarchy automation after successful changes*

## When to Use

Post-Hierarchy scripts are ideal for:
- Creating supporting members automatically
- Setting default property values
- Synchronizing with external systems
- Sending change notifications
- Updating calculations or aggregations
- Maintaining audit trails

## Key Characteristics

- **Non-blocking**: Cannot prevent the change
- **Asynchronous possible**: Can defer heavy operations
- **Error tolerant**: Should handle failures gracefully
- **Automation focused**: Reduces manual work
- **System integration**: Updates related components

## Common Automation Patterns

### Pattern 1: Auto-Create Child Members

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'POST_CREATE_CHILDREN';
  l_member_type VARCHAR2(50);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  PROCEDURE create_child_member(
    p_parent_name VARCHAR2,
    p_child_suffix VARCHAR2,
    p_description VARCHAR2
  ) IS
    l_child_name VARCHAR2(100);
  BEGIN
    l_child_name := p_parent_name || '_' || p_child_suffix;
    
    -- Check if child already exists
    IF ew_hierarchy.chk_member_exists(
         p_app_dimension_id => ew_lb_api.g_app_dimension_id,
         p_member_name     => l_child_name
       ) = 'N' THEN
      
      -- Create child member
      ew_req_api.create_member(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_parent_name     => p_parent_name,
        p_member_name     => l_child_name,
        p_description     => p_description,
        p_member_type     => 'CHILD'
      );
      
      log('Created child member: ' || l_child_name);
    END IF;
  EXCEPTION
    WHEN OTHERS THEN
      log('Error creating child ' || l_child_name || ': ' || SQLERRM);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only process for new member creation
  IF ew_lb_api.g_action_code = 'CMC' THEN
    
    log('Post-action for new member: ' || ew_lb_api.g_new_member_name);
    
    -- Determine member type from name pattern
    l_member_type := CASE
      WHEN ew_lb_api.g_new_member_name LIKE 'DEPT_%' THEN 'DEPARTMENT'
      WHEN ew_lb_api.g_new_member_name LIKE 'CC_%' THEN 'COST_CENTER'
      WHEN ew_lb_api.g_new_member_name LIKE 'PROJ_%' THEN 'PROJECT'
      ELSE 'OTHER'
    END;
    
    -- Create standard children based on type
    CASE l_member_type
      WHEN 'DEPARTMENT' THEN
        create_child_member(ew_lb_api.g_new_member_name, 'SALARY', 
                           'Salary Expenses');
        create_child_member(ew_lb_api.g_new_member_name, 'BENEFITS', 
                           'Employee Benefits');
        create_child_member(ew_lb_api.g_new_member_name, 'OPEX', 
                           'Operating Expenses');
        create_child_member(ew_lb_api.g_new_member_name, 'CAPEX', 
                           'Capital Expenses');
        
      WHEN 'COST_CENTER' THEN
        create_child_member(ew_lb_api.g_new_member_name, 'BUDGET', 
                           'Budget Allocation');
        create_child_member(ew_lb_api.g_new_member_name, 'ACTUAL', 
                           'Actual Expenses');
        create_child_member(ew_lb_api.g_new_member_name, 'VARIANCE', 
                           'Budget Variance');
        
      WHEN 'PROJECT' THEN
        create_child_member(ew_lb_api.g_new_member_name, 'PHASE1', 
                           'Phase 1 - Planning');
        create_child_member(ew_lb_api.g_new_member_name, 'PHASE2', 
                           'Phase 2 - Execution');
        create_child_member(ew_lb_api.g_new_member_name, 'PHASE3', 
                           'Phase 3 - Closure');
        
      ELSE
        NULL; -- No automatic children for other types
    END CASE;
    
    log('Child member creation completed');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    -- Log error but don't fail the hierarchy change
    log('Post-action error: ' || SQLERRM);
    -- Optionally notify admin
    ew_email.send_admin_alert('Post-hierarchy error', SQLERRM);
END;
```

### Pattern 2: Set Default Properties

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'POST_SET_DEFAULTS';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  PROCEDURE set_property(
    p_member_name VARCHAR2,
    p_prop_name VARCHAR2,
    p_prop_value VARCHAR2
  ) IS
  BEGIN
    ew_req_api.set_member_property(
      p_app_dimension_id => ew_lb_api.g_app_dimension_id,
      p_member_name     => p_member_name,
      p_property_name   => p_prop_name,
      p_property_value  => p_prop_value
    );
    
    log('Set ' || p_prop_name || ' = ' || p_prop_value);
  EXCEPTION
    WHEN OTHERS THEN
      log('Error setting property ' || p_prop_name || ': ' || SQLERRM);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Set defaults for new members
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
    
    log('Setting default properties for: ' || ew_lb_api.g_new_member_name);
    
    -- Set creation metadata
    set_property(ew_lb_api.g_new_member_name, 'Created_Date', 
                 TO_CHAR(SYSDATE, 'MM/DD/YYYY'));
    set_property(ew_lb_api.g_new_member_name, 'Created_By', 
                 USER);
    
    -- Set status
    set_property(ew_lb_api.g_new_member_name, 'Status', 'Active');
    
    -- Inherit properties from parent
    DECLARE
      l_parent_currency VARCHAR2(10);
      l_parent_region VARCHAR2(50);
    BEGIN
      l_parent_currency := ew_hierarchy.get_member_prop_value(
        p_app_name    => ew_lb_api.g_app_name,
        p_dim_name    => ew_lb_api.g_dim_name,
        p_member_name => ew_lb_api.g_parent_member_name,
        p_prop_label  => 'Currency'
      );
      
      l_parent_region := ew_hierarchy.get_member_prop_value(
        p_app_name    => ew_lb_api.g_app_name,
        p_dim_name    => ew_lb_api.g_dim_name,
        p_member_name => ew_lb_api.g_parent_member_name,
        p_prop_label  => 'Region'
      );
      
      IF l_parent_currency IS NOT NULL THEN
        set_property(ew_lb_api.g_new_member_name, 'Currency', 
                     l_parent_currency);
      END IF;
      
      IF l_parent_region IS NOT NULL THEN
        set_property(ew_lb_api.g_new_member_name, 'Region', 
                     l_parent_region);
      END IF;
    END;
    
    -- Set type-specific defaults
    IF ew_lb_api.g_new_member_name LIKE 'CC_%' THEN
      set_property(ew_lb_api.g_new_member_name, 'Member_Type', 
                   'Cost_Center');
      set_property(ew_lb_api.g_new_member_name, 'Budget_Status', 
                   'Pending');
    END IF;
    
    log('Default properties set successfully');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Post-action error: ' || SQLERRM);
END;
```

### Pattern 3: Send Notifications

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'POST_SEND_NOTIFICATIONS';
  l_email_list VARCHAR2(500);
  l_subject VARCHAR2(200);
  l_body VARCHAR2(4000);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Processing notifications for action: ' || ew_lb_api.g_action_code);
  
  -- Get notification list based on dimension
  l_email_list := CASE ew_lb_api.g_dim_name
    WHEN 'Entity' THEN 'entity-admins@company.com'
    WHEN 'Account' THEN 'account-admins@company.com'
    WHEN 'Department' THEN 'dept-managers@company.com'
    ELSE 'admin@company.com'
  END;
  
  -- Build notification based on action
  CASE ew_lb_api.g_action_code
    WHEN 'CMC' THEN
      l_subject := 'New Member Created: ' || ew_lb_api.g_new_member_name;
      l_body := 'A new member has been created in ' || ew_lb_api.g_dim_name ||
                CHR(10) || CHR(10) ||
                'Member Name: ' || ew_lb_api.g_new_member_name || CHR(10) ||
                'Parent: ' || ew_lb_api.g_parent_member_name || CHR(10) ||
                'Created By: ' || USER || CHR(10) ||
                'Created Date: ' || TO_CHAR(SYSDATE, 'MM/DD/YYYY HH24:MI:SS');
      
    WHEN 'DM' THEN
      l_subject := 'Member Deleted: ' || ew_lb_api.g_member_name;
      l_body := 'A member has been deleted from ' || ew_lb_api.g_dim_name ||
                CHR(10) || CHR(10) ||
                'Member Name: ' || ew_lb_api.g_member_name || CHR(10) ||
                'Deleted By: ' || USER || CHR(10) ||
                'Deleted Date: ' || TO_CHAR(SYSDATE, 'MM/DD/YYYY HH24:MI:SS');
      
    WHEN 'ZC' THEN
      l_subject := 'Member Moved: ' || ew_lb_api.g_member_name;
      l_body := 'A member has been moved in ' || ew_lb_api.g_dim_name ||
                CHR(10) || CHR(10) ||
                'Member Name: ' || ew_lb_api.g_member_name || CHR(10) ||
                'Old Parent: ' || ew_lb_api.g_old_parent_member_name || CHR(10) ||
                'New Parent: ' || ew_lb_api.g_parent_member_name || CHR(10) ||
                'Moved By: ' || USER || CHR(10) ||
                'Moved Date: ' || TO_CHAR(SYSDATE, 'MM/DD/YYYY HH24:MI:SS');
      
    WHEN 'RNM' THEN
      l_subject := 'Member Renamed: ' || ew_lb_api.g_member_name;
      l_body := 'A member has been renamed in ' || ew_lb_api.g_dim_name ||
                CHR(10) || CHR(10) ||
                'Old Name: ' || ew_lb_api.g_member_name || CHR(10) ||
                'New Name: ' || ew_lb_api.g_new_member_name || CHR(10) ||
                'Renamed By: ' || USER || CHR(10) ||
                'Renamed Date: ' || TO_CHAR(SYSDATE, 'MM/DD/YYYY HH24:MI:SS');
      
    ELSE
      -- No notification for other actions
      RETURN;
  END CASE;
  
  -- Send email notification
  BEGIN
    ew_email.send_email(
      p_to_list    => l_email_list,
      p_subject    => l_subject,
      p_body       => l_body,
      p_from_email => 'epmware-system@company.com'
    );
    
    log('Notification sent to: ' || l_email_list);
  EXCEPTION
    WHEN OTHERS THEN
      log('Failed to send notification: ' || SQLERRM);
  END;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Post-action notification error: ' || SQLERRM);
END;
```

### Pattern 4: Update Audit Trail

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'POST_AUDIT_TRAIL';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  PROCEDURE create_audit_entry IS
    PRAGMA AUTONOMOUS_TRANSACTION;
  BEGIN
    INSERT INTO hierarchy_audit_log (
      audit_id,
      action_date,
      action_code,
      dimension_name,
      member_name,
      new_member_name,
      parent_name,
      old_parent_name,
      user_id,
      session_id,
      request_id,
      ip_address,
      details
    ) VALUES (
      hierarchy_audit_seq.NEXTVAL,
      SYSDATE,
      ew_lb_api.g_action_code,
      ew_lb_api.g_dim_name,
      ew_lb_api.g_member_name,
      ew_lb_api.g_new_member_name,
      ew_lb_api.g_parent_member_name,
      ew_lb_api.g_old_parent_member_name,
      USER,
      ew_lb_api.g_session_id,
      ew_lb_api.g_request_id,
      SYS_CONTEXT('USERENV', 'IP_ADDRESS'),
      'Post-hierarchy action completed'
    );
    
    COMMIT;
    log('Audit entry created');
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      log('Failed to create audit entry: ' || SQLERRM);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Create audit entry for all actions
  create_audit_entry();
  
  -- Additional tracking for sensitive operations
  IF ew_lb_api.g_action_code = 'DM' THEN
    -- Archive deleted member data
    BEGIN
      INSERT INTO deleted_members_archive
      SELECT * FROM ew_members
      WHERE member_id = ew_lb_api.g_member_id;
      
      log('Member data archived before deletion');
    EXCEPTION
      WHEN OTHERS THEN
        log('Archive failed: ' || SQLERRM);
    END;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Audit trail error: ' || SQLERRM);
END;
```

### Pattern 5: Synchronize External Systems

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'POST_SYNC_EXTERNAL';
  l_sync_status VARCHAR2(100);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  PROCEDURE sync_to_erp IS
    l_request CLOB;
    l_response CLOB;
  BEGIN
    -- Build sync request
    l_request := JSON_OBJECT(
      'action' VALUE ew_lb_api.g_action_code,
      'dimension' VALUE ew_lb_api.g_dim_name,
      'member' VALUE NVL(ew_lb_api.g_new_member_name, 
                         ew_lb_api.g_member_name),
      'parent' VALUE ew_lb_api.g_parent_member_name,
      'timestamp' VALUE TO_CHAR(SYSTIMESTAMP, 'YYYY-MM-DD"T"HH24:MI:SS.FF3"Z"')
    );
    
    -- Call ERP web service
    l_response := ew_integration.call_web_service(
      p_url     => 'https://erp.company.com/api/hierarchy',
      p_method  => 'POST',
      p_payload => l_request,
      p_headers => 'Content-Type: application/json'
    );
    
    -- Parse response
    l_sync_status := JSON_VALUE(l_response, '$.status');
    
    IF l_sync_status = 'SUCCESS' THEN
      log('ERP sync successful');
    ELSE
      log('ERP sync failed: ' || JSON_VALUE(l_response, '$.error'));
    END IF;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('ERP sync error: ' || SQLERRM);
  END;
  
  PROCEDURE sync_to_reporting IS
  BEGIN
    -- Queue async job for reporting sync
    DBMS_SCHEDULER.CREATE_JOB(
      job_name   => 'SYNC_' || ew_lb_api.g_request_id,
      job_type   => 'STORED_PROCEDURE',
      job_action => 'sync_reporting_hierarchy',
      start_date => SYSTIMESTAMP,
      enabled    => TRUE,
      auto_drop  => TRUE,
      comments   => 'Sync hierarchy change to reporting'
    );
    
    log('Reporting sync job queued');
  EXCEPTION
    WHEN OTHERS THEN
      log('Failed to queue sync job: ' || SQLERRM);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only sync for production environment
  IF ew_lb_api.g_app_name LIKE '%PROD%' THEN
    
    log('Synchronizing to external systems');
    
    -- Sync to different systems based on dimension
    CASE ew_lb_api.g_dim_name
      WHEN 'Entity' THEN
        sync_to_erp();
        
      WHEN 'Account' THEN
        sync_to_reporting();
        
      ELSE
        log('No external sync configured for ' || ew_lb_api.g_dim_name);
    END CASE;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    -- Log but don't fail
    log('External sync error: ' || SQLERRM);
    -- Optionally queue for retry
    ew_integration.queue_retry('HIERARCHY_SYNC', ew_lb_api.g_request_id);
END;
```

## Configuration Examples

### Example 1: Department Automation

```sql
-- Complete department setup automation
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'POST_DEPT_AUTOMATION';
BEGIN
  IF ew_lb_api.g_action_code = 'CMC' AND 
     ew_lb_api.g_new_member_name LIKE 'DEPT_%' THEN
    
    -- 1. Create standard accounts
    FOR acc IN (SELECT account_code, account_name
                FROM department_standard_accounts) LOOP
      ew_req_api.create_member(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_parent_name     => ew_lb_api.g_new_member_name,
        p_member_name     => ew_lb_api.g_new_member_name || '_' || acc.account_code,
        p_description     => acc.account_name
      );
    END LOOP;
    
    -- 2. Copy security from template
    ew_security.copy_member_security(
      p_from_member => 'DEPT_TEMPLATE',
      p_to_member   => ew_lb_api.g_new_member_name
    );
    
    -- 3. Initialize budget allocation
    ew_req_api.set_member_property(
      p_app_dimension_id => ew_lb_api.g_app_dimension_id,
      p_member_name     => ew_lb_api.g_new_member_name,
      p_property_name   => 'Initial_Budget',
      p_property_value  => '0'
    );
    
    -- 4. Add to reporting dimension
    ew_integration.add_to_reporting_dim(ew_lb_api.g_new_member_name);
  END IF;
END;
```

### Example 2: Cascading Updates

```sql
-- Handle cascading updates after moves
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'POST_CASCADE_UPDATES';
BEGIN
  IF ew_lb_api.g_action_code = 'ZC' THEN
    -- Update all descendants' region property
    FOR member IN (
      SELECT member_name
      FROM ew_hierarchy_members
      START WITH member_name = ew_lb_api.g_member_name
      CONNECT BY PRIOR member_id = parent_id
    ) LOOP
      ew_req_api.set_member_property(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_member_name     => member.member_name,
        p_property_name   => 'Region',
        p_property_value  => get_parent_region(ew_lb_api.g_parent_member_name)
      );
    END LOOP;
  END IF;
END;
```

## Error Handling Best Practices

### Graceful Failure

```sql
BEGIN
  -- Attempt operation
  perform_post_action();
EXCEPTION
  WHEN OTHERS THEN
    -- Log error but don't propagate
    ew_debug.log('Post-action failed: ' || SQLERRM);
    
    -- Optionally queue for retry
    queue_for_retry();
    
    -- Don't set error status - hierarchy change already complete
    ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Autonomous Transactions

```sql
PROCEDURE log_independently IS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO action_log VALUES (...);
  COMMIT;
EXCEPTION
  WHEN OTHERS THEN
    ROLLBACK;
END;
```

## Performance Considerations

### Asynchronous Processing

```sql
-- Queue heavy operations
DBMS_SCHEDULER.CREATE_JOB(
  job_name   => 'POST_' || ew_lb_api.g_request_id,
  job_type   => 'PLSQL_BLOCK',
  job_action => 'BEGIN heavy_processing(:1, :2); END;',
  start_date => SYSTIMESTAMP + INTERVAL '5' SECOND,
  enabled    => TRUE
);
```

### Batch Operations

```sql
-- Collect changes for batch processing
INSERT INTO pending_post_actions (
  action_type,
  parameters,
  created_date
) VALUES (
  'SYNC_EXTERNAL',
  ew_lb_api.g_member_name,
  SYSDATE
);

-- Process in batch job later
```

## Testing Post-Actions

### Test Checklist

- [ ] Action executes for correct triggers
- [ ] Handles errors gracefully
- [ ] Doesn't block hierarchy change
- [ ] Completes within timeout
- [ ] Handles NULL parameters
- [ ] Works with bulk operations

## Next Steps

- [Pre-Hierarchy Actions](pre-hierarchy.md) - Validation scripts
- [Seeded Scripts](seeded-scripts.md) - EPMware standard scripts
- [API Reference](../../api/packages/hierarchy.md) - Supporting functions

---

!!! tip "Best Practice"
    Post-hierarchy scripts should be resilient and error-tolerant. Since the hierarchy change is already committed, these scripts should log errors and continue rather than failing completely.