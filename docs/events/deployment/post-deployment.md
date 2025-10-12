# Post-Deployment Scripts

Post-Deployment scripts execute after successful deployment operations, enabling automated tasks such as notifications, validation, cleanup, and integration with external systems.

## Overview

Post-Deployment scripts are triggered after EPMware completes a deployment to target applications. These scripts can:

- Send deployment completion notifications
- Validate deployed metadata
- Update tracking tables
- Trigger downstream processes
- Archive deployment artifacts
- Integrate with external monitoring systems

![Post-Deployment Flow](../../assets/images/post-deployment-flow.png)
*Figure: Post-Deployment script execution flow*

## Configuration

### Setting Up Post-Deployment Scripts

1. Navigate to **Deployment Configuration**
2. Select the deployment configuration
3. In the **Post-Deployment Script** field, select your Logic Script
4. Configure any additional parameters

![Post-Deployment Configuration](../../assets/images/post-deployment-config.png)
*Figure: Configuring Post-Deployment scripts*

## Input Parameters

### Deployment Context

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_deployment_id` | NUMBER | Unique deployment identifier | 12345 |
| `g_deployment_name` | VARCHAR2 | Deployment configuration name | 'PROD_DAILY_DEPLOY' |
| `g_deployment_status` | VARCHAR2 | Deployment result status | 'SUCCESS', 'PARTIAL', 'FAILED' |
| `g_deployment_date` | DATE | Deployment execution date | SYSDATE |

### Application Information

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_app_id` | NUMBER | Target application ID | 100 |
| `g_app_name` | VARCHAR2 | Target application name | 'HFM_PROD' |
| `g_app_type` | VARCHAR2 | Application type | 'HFM', 'PLANNING', 'ESSBASE' |
| `g_environment` | VARCHAR2 | Environment name | 'PRODUCTION' |

### Deployment Statistics

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_members_deployed` | NUMBER | Count of members deployed | 1543 |
| `g_properties_updated` | NUMBER | Count of properties updated | 3086 |
| `g_errors_count` | NUMBER | Number of errors encountered | 0 |
| `g_warnings_count` | NUMBER | Number of warnings | 5 |
| `g_deployment_duration` | NUMBER | Deployment time in seconds | 245 |

## Output Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `g_status` | VARCHAR2 | Yes | Script execution status ('S' or 'E') |
| `g_message` | VARCHAR2 | No | Status or error message |
| `g_continue_flag` | VARCHAR2 | No | Whether to continue with next steps ('Y'/'N') |

## Common Use Cases

### 1. Email Notification

Send deployment summary to stakeholders:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'POST_DEPLOY_NOTIFICATION';
  l_email_body VARCHAR2(4000);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Build email body
  l_email_body := 
    '<h2>Deployment Completed</h2>' ||
    '<p><b>Configuration:</b> ' || ew_lb_api.g_deployment_name || '</p>' ||
    '<p><b>Target:</b> ' || ew_lb_api.g_app_name || '</p>' ||
    '<p><b>Status:</b> ' || ew_lb_api.g_deployment_status || '</p>' ||
    '<p><b>Members Deployed:</b> ' || ew_lb_api.g_members_deployed || '</p>' ||
    '<p><b>Properties Updated:</b> ' || ew_lb_api.g_properties_updated || '</p>' ||
    '<p><b>Duration:</b> ' || 
    ROUND(ew_lb_api.g_deployment_duration/60, 1) || ' minutes</p>';
  
  -- Add error/warning information if present
  IF ew_lb_api.g_errors_count > 0 THEN
    l_email_body := l_email_body || 
      '<p style="color:red"><b>Errors:</b> ' || 
      ew_lb_api.g_errors_count || '</p>';
  END IF;
  
  IF ew_lb_api.g_warnings_count > 0 THEN
    l_email_body := l_email_body || 
      '<p style="color:orange"><b>Warnings:</b> ' || 
      ew_lb_api.g_warnings_count || '</p>';
  END IF;
  
  -- Send email
  ew_email.send_email(
    p_to        => 'admin@company.com',
    p_cc        => 'team@company.com',
    p_subject   => 'Deployment ' || ew_lb_api.g_deployment_status || 
                   ': ' || ew_lb_api.g_app_name,
    p_body      => l_email_body,
    p_body_html => l_email_body
  );
  
  log('Notification sent for deployment ' || ew_lb_api.g_deployment_id);
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Failed to send notification: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### 2. Validation Check

Validate critical metadata after deployment:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'POST_DEPLOY_VALIDATION';
  l_validation_errors VARCHAR2(4000);
  l_error_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE add_error(p_error VARCHAR2) IS
  BEGIN
    l_error_count := l_error_count + 1;
    IF l_validation_errors IS NOT NULL THEN
      l_validation_errors := l_validation_errors || '; ';
    END IF;
    l_validation_errors := l_validation_errors || p_error;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting post-deployment validation for ' || ew_lb_api.g_app_name);
  
  -- Check critical members exist
  FOR rec IN (
    SELECT member_name
      FROM critical_members_list
     WHERE app_name = ew_lb_api.g_app_name
  ) LOOP
    IF ew_hierarchy.chk_member_exists(
         p_app_name    => ew_lb_api.g_app_name,
         p_dim_name    => 'Account',
         p_member_name => rec.member_name
       ) = 'N' THEN
      add_error('Missing critical member: ' || rec.member_name);
    END IF;
  END LOOP;
  
  -- Check required properties are populated
  DECLARE
    l_null_count NUMBER;
  BEGIN
    SELECT COUNT(*)
      INTO l_null_count
      FROM ew_members_v m
     WHERE m.app_id = ew_lb_api.g_app_id
       AND m.property_value IS NULL
       AND m.property_name IN ('ACCOUNT_TYPE', 'CONSOLIDATION');
    
    IF l_null_count > 0 THEN
      add_error('Found ' || l_null_count || 
                ' members with missing required properties');
    END IF;
  END;
  
  -- Report validation results
  IF l_error_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation failed: ' || l_validation_errors;
    
    -- Log detailed errors
    log('Post-deployment validation failed');
    log('Errors: ' || l_validation_errors);
    
    -- Send alert
    ew_email.send_email(
      p_to      => 'admin@company.com',
      p_subject => 'URGENT: Post-Deployment Validation Failed',
      p_body    => 'Validation errors detected after deployment to ' ||
                   ew_lb_api.g_app_name || ': ' || l_validation_errors
    );
  ELSE
    log('Post-deployment validation completed successfully');
    ew_lb_api.g_message := 'All validations passed';
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
END;
```

### 3. Archive and Cleanup

Archive deployment files and clean temporary data:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'POST_DEPLOY_ARCHIVE';
  l_archive_path VARCHAR2(500);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Archive deployment files
  l_archive_path := '/archive/' || 
    TO_CHAR(ew_lb_api.g_deployment_date, 'YYYY/MM/DD/') ||
    ew_lb_api.g_deployment_name || '_' || 
    ew_lb_api.g_deployment_id || '/';
  
  -- Move deployment files to archive
  BEGIN
    -- Archive metadata files
    archive_deployment_files(
      p_deployment_id => ew_lb_api.g_deployment_id,
      p_archive_path  => l_archive_path
    );
    
    -- Archive logs
    archive_deployment_logs(
      p_deployment_id => ew_lb_api.g_deployment_id,
      p_archive_path  => l_archive_path
    );
    
    log('Archived deployment to: ' || l_archive_path);
  END;
  
  -- Clean temporary tables
  BEGIN
    DELETE FROM deployment_temp_data
     WHERE deployment_id = ew_lb_api.g_deployment_id
       AND created_date < SYSDATE - 1;
    
    log('Cleaned ' || SQL%ROWCOUNT || ' temporary records');
  END;
  
  -- Update deployment history
  INSERT INTO deployment_history (
    deployment_id,
    deployment_name,
    app_name,
    status,
    members_count,
    properties_count,
    duration_seconds,
    archive_path,
    created_date,
    created_by
  ) VALUES (
    ew_lb_api.g_deployment_id,
    ew_lb_api.g_deployment_name,
    ew_lb_api.g_app_name,
    ew_lb_api.g_deployment_status,
    ew_lb_api.g_members_deployed,
    ew_lb_api.g_properties_updated,
    ew_lb_api.g_deployment_duration,
    l_archive_path,
    ew_lb_api.g_deployment_date,
    ew_lb_api.g_user_name
  );
  
  COMMIT;
  log('Deployment history updated');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Archive/cleanup failed: ' || SQLERRM;
    log('Error: ' || SQLERRM);
    ROLLBACK;
END;
```

### 4. Trigger Downstream Process

Initiate dependent processes after deployment:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'POST_DEPLOY_TRIGGER';
  l_job_id NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only trigger on successful deployments
  IF ew_lb_api.g_deployment_status != 'SUCCESS' THEN
    log('Skipping downstream process - deployment not successful');
    RETURN;
  END IF;
  
  -- Trigger different processes based on application
  CASE ew_lb_api.g_app_name
    WHEN 'HFM_PROD' THEN
      -- Trigger consolidation
      l_job_id := submit_consolidation_job(
        p_app_name => ew_lb_api.g_app_name,
        p_scenario => 'ACTUAL',
        p_year     => TO_CHAR(SYSDATE, 'YYYY'),
        p_period   => TO_CHAR(SYSDATE, 'MON')
      );
      log('Submitted consolidation job: ' || l_job_id);
      
    WHEN 'PLANNING_PROD' THEN
      -- Trigger calculation
      l_job_id := submit_calculation_job(
        p_app_name => ew_lb_api.g_app_name,
        p_database => 'Plan1',
        p_script   => 'AggAll'
      );
      log('Submitted calculation job: ' || l_job_id);
      
    WHEN 'ESSBASE_PROD' THEN
      -- Trigger data load
      l_job_id := submit_data_load(
        p_app_name => ew_lb_api.g_app_name,
        p_database => 'Sample',
        p_load_rule => 'ActualLoad'
      );
      log('Submitted data load job: ' || l_job_id);
      
    ELSE
      log('No downstream process defined for ' || ew_lb_api.g_app_name);
  END CASE;
  
  -- Update tracking table
  IF l_job_id IS NOT NULL THEN
    INSERT INTO downstream_process_tracking (
      deployment_id,
      process_type,
      job_id,
      submitted_date
    ) VALUES (
      ew_lb_api.g_deployment_id,
      'AUTO_TRIGGERED',
      l_job_id,
      SYSDATE
    );
    COMMIT;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Failed to trigger downstream process: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

## Error Handling

### Deployment Status Checks

```sql
-- Check deployment status before proceeding
IF ew_lb_api.g_deployment_status = 'FAILED' THEN
  -- Handle failed deployment
  send_failure_alert();
  ew_lb_api.g_continue_flag := 'N';
  RETURN;
ELSIF ew_lb_api.g_deployment_status = 'PARTIAL' THEN
  -- Handle partial deployment
  log_partial_deployment_issues();
END IF;
```

### Rollback Considerations

```sql
-- Implement rollback logic if needed
IF critical_validation_failed THEN
  -- Initiate rollback
  BEGIN
    rollback_deployment(
      p_deployment_id => ew_lb_api.g_deployment_id,
      p_app_name      => ew_lb_api.g_app_name
    );
    ew_lb_api.g_message := 'Deployment rolled back due to validation failure';
  EXCEPTION
    WHEN OTHERS THEN
      -- Log rollback failure but don't stop
      log('Rollback failed: ' || SQLERRM);
  END;
END IF;
```

## Best Practices

1. **Always Check Deployment Status**
   - Different actions for SUCCESS, PARTIAL, FAILED
   - Don't assume successful deployment

2. **Implement Comprehensive Logging**
   - Log all actions taken
   - Include timing information
   - Record any issues encountered

3. **Use Appropriate Error Handling**
   - Don't fail silently
   - Send notifications for critical issues
   - Consider automated recovery options

4. **Archive Important Data**
   - Keep deployment history
   - Archive configuration files
   - Maintain audit trail

5. **Consider Performance Impact**
   - Post-deployment scripts shouldn't delay next deployments
   - Use asynchronous processing for long-running tasks

## Testing Considerations

### Test Scenarios

1. **Success Path**
   - All members deployed successfully
   - Properties updated correctly
   - No errors or warnings

2. **Partial Deployment**
   - Some members failed
   - Warnings present
   - Verify appropriate handling

3. **Failed Deployment**
   - Complete failure scenario
   - Rollback testing
   - Alert mechanisms

4. **Performance Testing**
   - Large deployments
   - Multiple simultaneous deployments
   - Resource consumption

## Next Steps

- [Pre-Deployment Scripts](pre-deployment.md)
- [ERP Interface Tasks](../erp-interface/)
- [Export Tasks](../export/)