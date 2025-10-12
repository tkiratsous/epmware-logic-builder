# Pre-Deployment Task Scripts

Pre-Deployment scripts execute before deployment operations begin, providing validation, preparation, and safeguarding measures. These scripts can prevent deployments that don't meet requirements or could cause issues.

## Overview

Pre-Deployment tasks ensure:
- **Readiness Validation**: Target environment prepared
- **Prerequisite Checks**: Required conditions met
- **Backup Creation**: Safeguard existing data
- **Conflict Detection**: Identify potential issues
- **Authorization**: Verify deployment approval
- **Resource Availability**: Ensure sufficient resources

![Pre-Deployment Flow](../../assets/images/pre-deployment-flow.png)
*Figure: Pre-deployment validation and preparation flow*

## When to Use

Pre-Deployment scripts are critical for:
- Production deployment validation
- Creating backup points
- Checking maintenance windows
- Verifying approvals
- Ensuring target compatibility
- Preventing conflicting deployments

## Key Characteristics

- **Blocking**: Can prevent deployment
- **Synchronous**: Deployment waits
- **Validation-focused**: Check prerequisites
- **Safety-oriented**: Prevent issues
- **Environment-aware**: Different per environment

## Common Pre-Deployment Patterns

### Pattern 1: Complete Environment Validation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_DEPLOY_VALIDATION';
  l_target_status VARCHAR2(50);
  l_active_users NUMBER;
  l_running_jobs NUMBER;
  l_disk_space NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION check_target_readiness RETURN BOOLEAN IS
  BEGIN
    -- Check application status
    SELECT status INTO l_target_status
    FROM ew_applications
    WHERE app_name = ew_lb_api.g_target_app;
    
    IF l_target_status NOT IN ('ACTIVE', 'MAINTENANCE') THEN
      ew_lb_api.g_message := 'Target application status is ' || 
                              l_target_status || ', expected ACTIVE or MAINTENANCE';
      RETURN FALSE;
    END IF;
    
    -- Check for active users
    SELECT COUNT(*) INTO l_active_users
    FROM ew_user_sessions
    WHERE app_name = ew_lb_api.g_target_app
    AND last_activity > SYSDATE - 1/24; -- Active in last hour
    
    IF l_active_users > 0 AND ew_lb_api.g_deployment_type = 'FULL' THEN
      ew_lb_api.g_message := l_active_users || 
                              ' active users detected. Cannot perform FULL deployment';
      RETURN FALSE;
    END IF;
    
    -- Check running jobs
    SELECT COUNT(*) INTO l_running_jobs
    FROM ew_scheduled_jobs
    WHERE app_name = ew_lb_api.g_target_app
    AND status = 'RUNNING';
    
    IF l_running_jobs > 0 THEN
      ew_lb_api.g_message := l_running_jobs || 
                              ' jobs are running. Wait for completion before deployment';
      RETURN FALSE;
    END IF;
    
    -- Check disk space
    l_disk_space := get_available_disk_space();
    
    IF l_disk_space < 1000 THEN -- Less than 1GB
      ew_lb_api.g_message := 'Insufficient disk space: ' || 
                              l_disk_space || 'MB available';
      RETURN FALSE;
    END IF;
    
    RETURN TRUE;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting pre-deployment validation');
  log('Deployment ID: ' || ew_lb_api.g_deployment_id);
  log('Target App: ' || ew_lb_api.g_target_app);
  log('Deployment Type: ' || ew_lb_api.g_deployment_type);
  
  -- Perform comprehensive validation
  IF NOT check_target_readiness() THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    log('Validation failed: ' || ew_lb_api.g_message);
    RETURN;
  END IF;
  
  log('Pre-deployment validation completed successfully');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Pre-deployment validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Pattern 2: Automated Backup Creation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_DEPLOY_BACKUP';
  l_backup_id NUMBER;
  l_backup_name VARCHAR2(200);
  l_backup_size NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  PROCEDURE create_backup IS
  BEGIN
    -- Generate backup name
    l_backup_name := ew_lb_api.g_target_app || '_' || 
                     TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS') || '_' ||
                     ew_lb_api.g_deployment_id;
    
    log('Creating backup: ' || l_backup_name);
    
    -- Create metadata backup
    ew_backup.create_metadata_backup(
      p_app_name    => ew_lb_api.g_target_app,
      p_backup_name => l_backup_name,
      p_backup_type => 'PRE_DEPLOYMENT',
      p_include_data => CASE 
                          WHEN ew_lb_api.g_target_app LIKE '%PROD%' 
                          THEN 'Y' 
                          ELSE 'N' 
                        END,
      x_backup_id   => l_backup_id
    );
    
    -- Verify backup
    SELECT backup_size_mb
    INTO l_backup_size
    FROM ew_backups
    WHERE backup_id = l_backup_id;
    
    IF l_backup_size = 0 THEN
      RAISE_APPLICATION_ERROR(-20001, 'Backup creation failed - zero size');
    END IF;
    
    log('Backup created successfully. ID: ' || l_backup_id || 
        ', Size: ' || l_backup_size || 'MB');
    
    -- Store backup reference for potential rollback
    INSERT INTO deployment_backups (
      deployment_id,
      backup_id,
      backup_name,
      created_date
    ) VALUES (
      ew_lb_api.g_deployment_id,
      l_backup_id,
      l_backup_name,
      SYSDATE
    );
    
    COMMIT;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Backup creation failed: ' || SQLERRM);
      RAISE;
  END;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only create backup for production or if requested
  IF ew_lb_api.g_target_app LIKE '%PROD%' OR
     get_deployment_param('CREATE_BACKUP') = 'Y' THEN
    
    create_backup();
    
    ew_lb_api.g_message := 'Backup created: ' || l_backup_name;
  ELSE
    log('Backup skipped for non-production environment');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Backup creation failed: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Pattern 3: Maintenance Window Verification

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CHECK_MAINTENANCE_WINDOW';
  l_current_time DATE := SYSDATE;
  l_window_start DATE;
  l_window_end DATE;
  l_is_emergency VARCHAR2(1);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Check if emergency deployment
  l_is_emergency := get_deployment_param('EMERGENCY_DEPLOYMENT');
  
  IF l_is_emergency = 'Y' THEN
    log('Emergency deployment - bypassing maintenance window check');
    
    -- Log emergency deployment
    INSERT INTO emergency_deployments_log (
      deployment_id,
      approver,
      reason,
      deployment_date
    ) VALUES (
      ew_lb_api.g_deployment_id,
      ew_lb_api.g_user_id,
      get_deployment_param('EMERGENCY_REASON'),
      SYSDATE
    );
    
    RETURN;
  END IF;
  
  -- Get maintenance window for target environment
  BEGIN
    SELECT window_start, window_end
    INTO l_window_start, l_window_end
    FROM maintenance_windows
    WHERE app_name = ew_lb_api.g_target_app
    AND TRUNC(l_current_time) = TRUNC(window_date)
    AND active_flag = 'Y';
    
    -- Check if current time is within window
    IF l_current_time NOT BETWEEN l_window_start AND l_window_end THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Deployment only allowed during maintenance window: ' ||
        TO_CHAR(l_window_start, 'HH24:MI') || ' - ' ||
        TO_CHAR(l_window_end, 'HH24:MI');
      log('Outside maintenance window');
    ELSE
      log('Within maintenance window');
    END IF;
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- No maintenance window defined
      IF ew_lb_api.g_target_app LIKE '%PROD%' THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'No maintenance window defined for production deployment';
        log('No maintenance window found');
      ELSE
        log('No maintenance window required for non-production');
      END IF;
  END;
  
END;
```

### Pattern 4: Conflict Detection

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'DETECT_CONFLICTS';
  l_conflict_count NUMBER;
  l_conflict_details VARCHAR2(4000);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Check for concurrent deployments
  SELECT COUNT(*)
  INTO l_conflict_count
  FROM active_deployments
  WHERE target_app = ew_lb_api.g_target_app
  AND deployment_id != ew_lb_api.g_deployment_id
  AND status IN ('RUNNING', 'PENDING');
  
  IF l_conflict_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Another deployment is in progress for ' || ew_lb_api.g_target_app;
    log('Concurrent deployment detected');
    RETURN;
  END IF;
  
  -- Check for metadata conflicts
  FOR conflict IN (
    SELECT member_name, 
           'Modified in target after export' as conflict_type
    FROM deployment_members dm
    WHERE dm.deployment_id = ew_lb_api.g_deployment_id
    AND EXISTS (
      SELECT 1 FROM ew_members m
      WHERE m.app_name = ew_lb_api.g_target_app
      AND m.member_name = dm.member_name
      AND m.last_modified > dm.export_date
    )
  ) LOOP
    l_conflict_details := l_conflict_details || 
                          conflict.member_name || ': ' || 
                          conflict.conflict_type || '; ';
  END LOOP;
  
  IF l_conflict_details IS NOT NULL THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Metadata conflicts detected: ' || l_conflict_details;
    log('Conflicts: ' || l_conflict_details);
  END IF;
  
END;
```

### Pattern 5: Approval Verification

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VERIFY_DEPLOYMENT_APPROVAL';
  l_approval_required VARCHAR2(1);
  l_approval_status VARCHAR2(50);
  l_approver VARCHAR2(100);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Determine if approval required
  l_approval_required := CASE
    WHEN ew_lb_api.g_target_app LIKE '%PROD%' THEN 'Y'
    WHEN ew_lb_api.g_deployment_type = 'FULL' THEN 'Y'
    WHEN is_sensitive_metadata() THEN 'Y'
    ELSE 'N'
  END;
  
  IF l_approval_required = 'Y' THEN
    -- Check for approval
    BEGIN
      SELECT approval_status, approver
      INTO l_approval_status, l_approver
      FROM deployment_approvals
      WHERE deployment_id = ew_lb_api.g_deployment_id;
      
      IF l_approval_status != 'APPROVED' THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'Deployment requires approval. Current status: ' || 
          l_approval_status;
      ELSE
        ew_debug.log('Deployment approved by: ' || l_approver);
      END IF;
      
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'Deployment requires approval. No approval record found.';
    END;
  END IF;
  
END;
```

## Best Practices

### 1. Fast Fail Validation
```sql
-- Check simplest conditions first
IF quick_check_fails THEN
  ew_lb_api.g_status := ew_lb_api.g_error;
  RETURN; -- Don't continue
END IF;

-- Then more complex checks
IF complex_validation_fails THEN
  -- ...
END IF;
```

### 2. Comprehensive Logging
```sql
-- Log all validation steps
log('=== Pre-Deployment Validation ===');
log('Step 1: Checking application status - ' || l_status);
log('Step 2: Verifying disk space - ' || l_space || 'MB');
log('Step 3: Creating backup - ' || l_backup_name);
log('=== Validation Complete ===');
```

### 3. Rollback Preparation
```sql
-- Store rollback information
INSERT INTO deployment_rollback_info (
  deployment_id,
  backup_id,
  original_state,
  rollback_script
) VALUES (
  ew_lb_api.g_deployment_id,
  l_backup_id,
  capture_current_state(),
  generate_rollback_script()
);
```

### 4. Clear Error Messages
```sql
-- Provide actionable feedback
ew_lb_api.g_message := 
  'Cannot deploy: 5 users are actively working in ' || 
  ew_lb_api.g_target_app || '. ' ||
  'Please notify users and retry after they log out, or ' ||
  'schedule deployment for maintenance window (22:00-02:00).';
```

## Testing Pre-Deployment Scripts

### Test Scenarios

| Scenario | Test Case | Expected Result |
|----------|-----------|-----------------|
| Ready Environment | All checks pass | Deployment proceeds |
| Active Users | Users logged in | Block deployment |
| No Backup Space | Disk full | Block with space error |
| Outside Window | Wrong time | Block with window info |
| No Approval | Missing approval | Block with approval request |
| Concurrent Deploy | Another running | Block with conflict error |

## Performance Considerations

- **Timeout Handling**: Set reasonable timeouts
- **Parallel Checks**: Run independent validations concurrently
- **Cache Results**: Cache environment status briefly
- **Quick Checks First**: Fail fast on simple validations

## Next Steps

- [Post-Deployment Tasks](post-deployment.md) - After deployment scripts
- [Deployment Overview](index.md) - General deployment concepts
- [API Reference](../../api/) - Supporting functions

---

!!! warning "Critical"
    Pre-deployment scripts are your last line of defense against problematic deployments. Ensure they are comprehensive, especially for production environments.