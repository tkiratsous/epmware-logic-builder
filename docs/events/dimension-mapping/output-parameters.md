# Dimension Mapping Output Parameters

Output parameters control how EPMware processes the mapping results. By setting these parameters, you can override default behavior, transform member names, redirect to different hierarchies, or skip processing entirely.

## Standard Output Parameters

All Logic Scripts must set these standard outputs:

### Status and Message

| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| `g_status` | VARCHAR2 | Yes | Script execution status | 'S' (Success), 'E' (Error) |
| `g_message` | VARCHAR2 | No | User-facing message | Any text up to 4000 chars |

```sql
-- Success example
ew_lb_api.g_status := ew_lb_api.g_success;  -- 'S'
ew_lb_api.g_message := 'Member mapped successfully';

-- Error example
ew_lb_api.g_status := ew_lb_api.g_error;    -- 'E'
ew_lb_api.g_message := 'Invalid member name format';
```

## Mapping Control Parameters

These parameters control the mapping behavior:

### Target Member Names

| Parameter | Type | Description | When to Use |
|-----------|------|-------------|-------------|
| `g_out_tgt_new_member_name` | VARCHAR2 | Target member name | Transform member names during mapping |
| `g_out_tgt_parent_member_name` | VARCHAR2 | Target parent name | Redirect to different parent |
| `g_out_tgt_old_member_name` | VARCHAR2 | Old name for rename | Specify different name to rename |

### Processing Control

| Parameter | Type | Description | Values |
|-----------|------|-------------|---------|
| `g_out_ignore_flag` | VARCHAR2 | Skip standard processing | 'Y' or 'N' (default) |
| `g_out_skip_sync` | VARCHAR2 | Skip automatic sync | 'Y' or 'N' (default) |

## Parameter Usage Examples

### Transform Member Names
```sql
BEGIN
  -- Add prefix to all members
  ew_lb_api.g_out_tgt_new_member_name := 
    'RPT_' || ew_lb_api.g_member_name;
  
  -- Keep same parent structure
  ew_lb_api.g_out_tgt_parent_member_name := 
    ew_lb_api.g_parent_member_name;
    
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Redirect to Different Parent
```sql
BEGIN
  -- Map all cost centers under a single parent
  IF ew_lb_api.g_member_name LIKE 'CC_%' THEN
    ew_lb_api.g_out_tgt_parent_member_name := 'ALL_COST_CENTERS';
    ew_lb_api.g_out_tgt_new_member_name := ew_lb_api.g_member_name;
  END IF;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Skip Certain Members
```sql
BEGIN
  -- Skip test members
  IF ew_lb_api.g_member_name LIKE 'TEST_%' THEN
    ew_lb_api.g_out_ignore_flag := 'Y';
    ew_lb_api.g_status := ew_lb_api.g_success;
    ew_lb_api.g_message := 'Test member skipped';
    RETURN;
  END IF;
  
  -- Process normal members
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SMARTSYNC',
    x_status        => ew_lb_api.g_status,
    x_message       => ew_lb_api.g_message
  );
END;
```

## Advanced Output Patterns

### Conditional Parent Assignment
```sql
DECLARE
  l_level NUMBER;
BEGIN
  -- Get member level
  l_level := ew_statistics.get_level(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_id       => ew_lb_api.g_member_id
  );
  
  -- Assign parent based on level
  IF l_level = 0 THEN
    -- Base members under detail parent
    ew_lb_api.g_out_tgt_parent_member_name := 'DETAIL_MEMBERS';
  ELSIF l_level <= 2 THEN
    -- Mid-level under summary parent
    ew_lb_api.g_out_tgt_parent_member_name := 'SUMMARY_MEMBERS';
  ELSE
    -- High-level keep original structure
    ew_lb_api.g_out_tgt_parent_member_name := 
      ew_lb_api.g_parent_member_name;
  END IF;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Dynamic Name Generation
```sql
DECLARE
  l_date_suffix VARCHAR2(10);
  l_seq_number NUMBER;
BEGIN
  -- Generate date suffix
  l_date_suffix := TO_CHAR(SYSDATE, 'YYYYMMDD');
  
  -- Get next sequence number
  SELECT seq_mapping.NEXTVAL INTO l_seq_number FROM DUAL;
  
  -- Create unique target name
  ew_lb_api.g_out_tgt_new_member_name := 
    ew_lb_api.g_member_name || '_' || 
    l_date_suffix || '_' || 
    LPAD(l_seq_number, 4, '0');
    
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Cross-Reference Mapping
```sql
DECLARE
  l_target_info VARCHAR2(200);
BEGIN
  -- Look up mapping table
  BEGIN
    SELECT target_member || '|' || target_parent
    INTO l_target_info
    FROM custom_mapping_xref
    WHERE source_member = ew_lb_api.g_member_name
    AND source_app = ew_lb_api.g_src_app_name;
    
    -- Parse target info
    ew_lb_api.g_out_tgt_new_member_name := 
      SUBSTR(l_target_info, 1, INSTR(l_target_info, '|') - 1);
    ew_lb_api.g_out_tgt_parent_member_name := 
      SUBSTR(l_target_info, INSTR(l_target_info, '|') + 1);
      
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- No mapping found, skip
      ew_lb_api.g_out_ignore_flag := 'Y';
      ew_lb_api.g_message := 'No mapping defined for ' || 
                              ew_lb_api.g_member_name;
  END;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

## Output Parameter Combinations

### Scenario: Create with Rename
```sql
-- Input: Creating member "DEPT_100"
-- Output: Create as "D100" under specific parent
ew_lb_api.g_out_tgt_new_member_name := 'D100';
ew_lb_api.g_out_tgt_parent_member_name := 'ALL_DEPARTMENTS';
```

### Scenario: Move with Rename
```sql
-- Input: Moving member "OLD_CC_100"
-- Output: Rename to "CC_100" and move to new parent
IF ew_lb_api.g_action_code = 'ZC' THEN
  ew_lb_api.g_out_tgt_new_member_name := 
    REPLACE(ew_lb_api.g_member_name, 'OLD_', '');
  ew_lb_api.g_out_tgt_parent_member_name := 'ACTIVE_COST_CENTERS';
END IF;
```

### Scenario: Conditional Skip
```sql
-- Skip mapping if target already exists
IF ew_hierarchy.chk_member_exists(
     p_app_dimension_id => ew_lb_api.g_tgt_dim_id,
     p_member_name     => ew_lb_api.g_member_name
   ) = 'Y' THEN
  ew_lb_api.g_out_ignore_flag := 'Y';
  ew_lb_api.g_message := 'Member already exists in target';
ELSE
  -- Proceed with mapping
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SMARTSYNC',
    x_status        => ew_lb_api.g_status,
    x_message       => ew_lb_api.g_message
  );
END IF;
```

## Error Handling

### Setting Error Status
```sql
BEGIN
  -- Validation check
  IF LENGTH(ew_lb_api.g_member_name) > 50 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Member name exceeds 50 characters';
    RETURN;  -- Stop processing
  END IF;
  
  -- Continue with mapping
  -- ...
END;
```

### Accumulating Errors
```sql
DECLARE
  l_errors VARCHAR2(4000);
  l_has_error BOOLEAN := FALSE;
BEGIN
  -- Check multiple conditions
  IF condition1_fails THEN
    l_errors := l_errors || 'Condition 1 failed; ';
    l_has_error := TRUE;
  END IF;
  
  IF condition2_fails THEN
    l_errors := l_errors || 'Condition 2 failed; ';
    l_has_error := TRUE;
  END IF;
  
  IF l_has_error THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := l_errors;
  ELSE
    ew_lb_api.g_status := ew_lb_api.g_success;
  END IF;
END;
```

## Best Practices

### 1. Always Initialize Output Parameters
```sql
BEGIN
  -- Initialize at start
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  ew_lb_api.g_out_ignore_flag := 'N';
  
  -- Your logic here
END;
```

### 2. Provide Meaningful Messages
```sql
-- Good: Specific and actionable
ew_lb_api.g_message := 'Member CC_100 renamed to COST_100 and moved under Finance';

-- Bad: Generic
ew_lb_api.g_message := 'Processed';
```

### 3. Validate Output Values
```sql
-- Check that target names are valid
IF ew_lb_api.g_out_tgt_new_member_name IS NOT NULL THEN
  IF LENGTH(ew_lb_api.g_out_tgt_new_member_name) > 80 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Target member name too long';
    RETURN;
  END IF;
END IF;
```

### 4. Use Ignore Flag Appropriately
```sql
-- Use ignore flag for business logic skips
IF member_should_not_sync THEN
  ew_lb_api.g_out_ignore_flag := 'Y';
  ew_lb_api.g_status := ew_lb_api.g_success;  -- Still success
  ew_lb_api.g_message := 'Member excluded per business rules';
END IF;

-- Use error status for actual failures
IF critical_validation_fails THEN
  ew_lb_api.g_status := ew_lb_api.g_error;  -- Error status
  ew_lb_api.g_message := 'Critical validation failed';
END IF;
```

## Performance Considerations

### Minimize Database Calls
```sql
-- Cache results when setting multiple outputs
DECLARE
  l_target_parent VARCHAR2(100);
BEGIN
  -- Single lookup
  l_target_parent := lookup_target_parent(ew_lb_api.g_member_name);
  
  -- Reuse for multiple outputs
  ew_lb_api.g_out_tgt_parent_member_name := l_target_parent;
  
  IF l_target_parent IS NULL THEN
    ew_lb_api.g_out_ignore_flag := 'Y';
  END IF;
END;
```

### Batch Processing
```sql
-- When processing multiple members, use bulk operations
DECLARE
  TYPE t_member_map IS TABLE OF VARCHAR2(100) INDEX BY VARCHAR2(100);
  l_mapping t_member_map;
BEGIN
  -- Load all mappings once
  load_all_mappings(l_mapping);
  
  -- Use cached mappings
  IF l_mapping.EXISTS(ew_lb_api.g_member_name) THEN
    ew_lb_api.g_out_tgt_new_member_name := 
      l_mapping(ew_lb_api.g_member_name);
  END IF;
END;
```

## Testing Output Parameters

### Debug Logging
```sql
DECLARE
  PROCEDURE log_outputs IS
  BEGIN
    ew_debug.log('=== Output Parameters ===');
    ew_debug.log('Status: ' || ew_lb_api.g_status);
    ew_debug.log('Message: ' || ew_lb_api.g_message);
    ew_debug.log('Target Member: ' || 
                 NVL(ew_lb_api.g_out_tgt_new_member_name, 'Not Set'));
    ew_debug.log('Target Parent: ' || 
                 NVL(ew_lb_api.g_out_tgt_parent_member_name, 'Not Set'));
    ew_debug.log('Ignore Flag: ' || 
                 NVL(ew_lb_api.g_out_ignore_flag, 'N'));
  END;
BEGIN
  -- Your mapping logic
  
  -- Log outputs before returning
  log_outputs();
END;
```

## Next Steps

- [Examples](examples.md) - Complete mapping scenarios
- [Input Parameters](input-parameters.md) - Available input data
- [API Reference](../../api/packages/hierarchy.md) - Supporting APIs

---

!!! warning "Important"
    Always set `g_status` and provide a `g_message` when returning an error. This ensures users understand what went wrong and can take corrective action.