# Dimension Mapping Input Parameters

This page provides a comprehensive reference for all input parameters available in Dimension Mapping Logic Scripts. Understanding these parameters is essential for implementing custom mapping logic.

## Standard Input Parameters

These parameters are available in all Dimension Mapping scripts:

### Session and User Context

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `g_user_id` | NUMBER | Current user ID | 1001 |
| `g_session_id` | NUMBER | Current session ID | 987654321 |
| `g_request_id` | NUMBER | Current request ID (if applicable) | 5432 |
| `g_request_line_id` | NUMBER | Request line ID (if applicable) | 12345 |

### Application Context

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `g_src_app_id` | NUMBER | Source application ID | 100 |
| `g_src_app_name` | VARCHAR2 | Source application name | "HFM_PROD" |
| `g_tgt_app_id` | NUMBER | Target application ID | 200 |
| `g_tgt_app_name` | VARCHAR2 | Target application name | "PLANNING_PROD" |

### Dimension Context

| Parameter | Type | Description | Example Value |
|-----------|------|-------------|---------------|
| `g_app_dimension_id` | NUMBER | Source dimension ID | 1234 |
| `g_src_dim_name` | VARCHAR2 | Source dimension name | "Entity" |
| `g_tgt_dim_id` | NUMBER | Target dimension ID | 5678 |
| `g_tgt_dim_name` | VARCHAR2 | Target dimension name | "Entity" |
| `g_dim_class_name` | VARCHAR2 | Dimension class name | "ENTITY" |

## Action-Specific Parameters

Parameters that vary based on the action being performed:

### Hierarchy Action Code

| Parameter | Type | Description | Possible Values |
|-----------|------|-------------|-----------------|
| `g_action_code` | VARCHAR2 | Hierarchy action being performed | CMC, CMS, DM, RNM, ZC, ISMC, ISMS, DSHM |

### Member Information

| Parameter | Type | Description | When Available |
|-----------|------|-------------|----------------|
| `g_member_id` | NUMBER | Source member ID | All actions |
| `g_member_name` | VARCHAR2 | Source member name | All actions |
| `g_parent_member_id` | NUMBER | Parent member ID | CMC, CMS, ZC, ISMC, ISMS |
| `g_parent_member_name` | VARCHAR2 | Parent member name | CMC, CMS, ZC, ISMC, ISMS |
| `g_new_member_name` | VARCHAR2 | New member name | RNM (Rename) |
| `g_old_parent_member_name` | VARCHAR2 | Previous parent name | ZC (Move) |
| `g_sort_order` | NUMBER | Member sort order | CMC, CMS, ISMC, ISMS |

## Property-Related Parameters

Parameters containing member property information:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_node_data_storage` | VARCHAR2 | Data storage type | "STORE", "DYNAMIC_CALC", "LABEL_ONLY" |
| `g_consolidation_method` | VARCHAR2 | Consolidation method | "ADDITION", "SUBTRACTION", "MULTIPLY" |
| `g_two_pass_calc` | VARCHAR2 | Two-pass calculation flag | "Y" or "N" |
| `g_alias_name` | VARCHAR2 | Member alias | "Total Revenue" |
| `g_base_currency` | VARCHAR2 | Base currency | "USD" |

## Workflow Context Parameters

Available when mapping is triggered through workflow:

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_wf_stage_id` | NUMBER | Current workflow stage | 10 |
| `g_wf_stage_name` | VARCHAR2 | Workflow stage name | "Initial Review" |
| `g_wf_task_id` | NUMBER | Current task ID | 20 |
| `g_wf_task_name` | VARCHAR2 | Task name | "Dimension Sync" |

## Accessing Parameters

### Basic Usage
```sql
DECLARE
  l_source_member VARCHAR2(100);
BEGIN
  -- Access input parameters directly
  l_source_member := ew_lb_api.g_member_name;
  
  IF ew_lb_api.g_action_code = 'CMC' THEN
    -- Create member as child logic
    DBMS_OUTPUT.PUT_LINE('Creating: ' || l_source_member);
    DBMS_OUTPUT.PUT_LINE('Under parent: ' || ew_lb_api.g_parent_member_name);
  END IF;
END;
```

### Null Checking
```sql
BEGIN
  -- Always check for NULL values
  IF ew_lb_api.g_parent_member_name IS NOT NULL THEN
    -- Safe to use parent
    process_with_parent(ew_lb_api.g_parent_member_name);
  ELSE
    -- Handle root level members
    process_root_member(ew_lb_api.g_member_name);
  END IF;
END;
```

### Debugging Parameters
```sql
DECLARE
  PROCEDURE log_parameters IS
  BEGIN
    ew_debug.log('=== Dimension Mapping Parameters ===');
    ew_debug.log('Action Code: ' || ew_lb_api.g_action_code);
    ew_debug.log('Member: ' || ew_lb_api.g_member_name);
    ew_debug.log('Parent: ' || NVL(ew_lb_api.g_parent_member_name, 'ROOT'));
    ew_debug.log('Source App: ' || ew_lb_api.g_src_app_name);
    ew_debug.log('Target App: ' || ew_lb_api.g_tgt_app_name);
    ew_debug.log('Sort Order: ' || TO_CHAR(ew_lb_api.g_sort_order));
  END log_parameters;
BEGIN
  log_parameters();
  -- Continue with mapping logic
END;
```

## Parameter Availability by Action

Not all parameters are available for all actions:

### Create Actions (CMC, CMS)
✅ Available:
- Member name
- Parent member name
- Sort order
- All property parameters

❌ Not available:
- Old parent name
- New member name

### Delete Action (DM)
✅ Available:
- Member name
- Member ID

❌ Not available:
- Parent member name
- Sort order
- Property parameters

### Rename Action (RNM)
✅ Available:
- Member name (old)
- New member name
- Member ID

❌ Not available:
- Parent member name
- Sort order

### Move Action (ZC)
✅ Available:
- Member name
- Parent member name (new)
- Old parent member name
- Sort order

❌ Not available:
- New member name

## Advanced Parameter Usage

### Conditional Logic Based on Parameters
```sql
BEGIN
  -- Different logic for different dimension classes
  CASE ew_lb_api.g_dim_class_name
    WHEN 'ACCOUNT' THEN
      handle_account_mapping();
    WHEN 'ENTITY' THEN
      handle_entity_mapping();
    WHEN 'CUSTOM' THEN
      handle_custom_mapping();
    ELSE
      -- Default handling
      ew_hierarchy.set_dim_mapping_method(
        p_mapping_method => 'SMARTSYNC',
        x_status        => ew_lb_api.g_status,
        x_message       => ew_lb_api.g_message
      );
  END CASE;
END;
```

### Using Parameters for Validation
```sql
DECLARE
  l_valid BOOLEAN := TRUE;
  l_error_msg VARCHAR2(4000);
BEGIN
  -- Validate member name format
  IF NOT REGEXP_LIKE(ew_lb_api.g_member_name, '^[A-Z][0-9]{5}$') THEN
    l_valid := FALSE;
    l_error_msg := 'Member name must match format: Letter + 5 digits';
  END IF;
  
  -- Validate parent exists in target
  IF ew_lb_api.g_parent_member_name IS NOT NULL THEN
    IF ew_hierarchy.chk_member_exists(
         p_app_dimension_id => ew_lb_api.g_tgt_dim_id,
         p_member_name     => ew_lb_api.g_parent_member_name
       ) = 'N' THEN
      l_valid := FALSE;
      l_error_msg := l_error_msg || '; Parent does not exist in target';
    END IF;
  END IF;
  
  IF NOT l_valid THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := l_error_msg;
    RETURN;
  END IF;
END;
```

### Parameter-Based Transformations
```sql
DECLARE
  l_prefix VARCHAR2(10);
  l_suffix VARCHAR2(10);
BEGIN
  -- Determine prefix based on source application
  l_prefix := CASE ew_lb_api.g_src_app_name
                WHEN 'HFM_PROD' THEN 'HFM_'
                WHEN 'ESSBASE_PROD' THEN 'ESS_'
                ELSE ''
              END;
  
  -- Add suffix based on dimension
  l_suffix := CASE ew_lb_api.g_src_dim_name
                WHEN 'Entity' THEN '_ENT'
                WHEN 'Account' THEN '_ACC'
                ELSE ''
              END;
  
  -- Transform member name
  ew_lb_api.g_out_tgt_new_member_name := 
    l_prefix || ew_lb_api.g_member_name || l_suffix;
END;
```

## Common Pitfalls

### 1. Not Checking for NULL Values
❌ Wrong:
```sql
IF ew_lb_api.g_parent_member_name = 'ROOT' THEN
```

✅ Correct:
```sql
IF NVL(ew_lb_api.g_parent_member_name, 'ROOT') = 'ROOT' THEN
```

### 2. Assuming Parameters Always Exist
❌ Wrong:
```sql
l_length := LENGTH(ew_lb_api.g_new_member_name);
```

✅ Correct:
```sql
IF ew_lb_api.g_action_code = 'RNM' THEN
  l_length := LENGTH(ew_lb_api.g_new_member_name);
END IF;
```

### 3. Not Considering Action Context
❌ Wrong:
```sql
-- Always using parent member name
create_in_target(ew_lb_api.g_parent_member_name);
```

✅ Correct:
```sql
IF ew_lb_api.g_action_code IN ('CMC', 'CMS', 'ZC') THEN
  create_in_target(ew_lb_api.g_parent_member_name);
END IF;
```

## Next Steps

- [Output Parameters](output-parameters.md) - Control mapping results
- [Examples](examples.md) - Real-world parameter usage
- [API Reference](../../api/) - Complete API documentation

---

!!! tip "Debug Tip"
    Always log input parameters at the start of your script for easier troubleshooting. Use the Debug Messages report to review parameter values during execution.