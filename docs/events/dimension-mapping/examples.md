# Dimension Mapping Examples

This page provides real-world examples of Dimension Mapping scripts for common scenarios. Each example includes the complete code, configuration steps, and testing approach.

## Example 1: Simple Name Prefix Mapping

**Scenario**: Add application prefix to all members when mapping from HFM to Planning.

### Script Code
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_ADD_APP_PREFIX';
  l_prefix VARCHAR2(10);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Processing member: ' || ew_lb_api.g_member_name);
  log('Action code: ' || ew_lb_api.g_action_code);
  
  -- Determine prefix based on source application
  l_prefix := CASE ew_lb_api.g_src_app_name
                WHEN 'HFM_PROD' THEN 'HFM_'
                WHEN 'HFM_DEV' THEN 'HFMD_'
                ELSE 'OTH_'
              END;
  
  -- Apply prefix to member name
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS', 'RNM') THEN
    ew_lb_api.g_out_tgt_new_member_name := 
      l_prefix || ew_lb_api.g_member_name;
    log('Mapped to: ' || ew_lb_api.g_out_tgt_new_member_name);
  END IF;
  
  -- For rename, handle old name
  IF ew_lb_api.g_action_code = 'RNM' THEN
    ew_lb_api.g_out_tgt_old_member_name := 
      l_prefix || ew_lb_api.g_member_name;
  END IF;
  
  -- Use Smart Sync for hierarchy structure
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SMARTSYNC',
    x_status        => ew_lb_api.g_status,
    x_message       => ew_lb_api.g_message
  );
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error: ' || SQLERRM;
    log('Error in script: ' || SQLERRM);
END;
```

### Configuration
1. Create script in Logic Builder with type "Dimension Mapping"
2. Navigate to Configuration → Dimension → Mapping
3. Select source: HFM_PROD / Entity dimension
4. Select target: PLANNING_PROD / Entity dimension
5. Choose "Logic Script" and select this script

### Testing
Create member "Region01" in HFM → Creates "HFM_Region01" in Planning

---

## Example 2: Selective Branch Mapping

**Scenario**: Map only specific branches of the hierarchy based on member attributes.

### Script Code
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_SELECTIVE_BRANCHES';
  l_map_branch BOOLEAN := FALSE;
  l_branch_root VARCHAR2(100);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION should_map_branch(p_member_name VARCHAR2) RETURN BOOLEAN IS
    l_property_value VARCHAR2(100);
  BEGIN
    -- Check if member has specific property value
    l_property_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_src_app_name,
      p_dim_name    => ew_lb_api.g_src_dim_name,
      p_member_name => p_member_name,
      p_prop_label  => 'MapToPlanning'
    );
    
    RETURN (l_property_value = 'Y');
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Evaluating member: ' || ew_lb_api.g_member_name);
  
  -- Check if this branch should be mapped
  -- Walk up the hierarchy to find a mapping flag
  l_branch_root := ew_lb_api.g_member_name;
  
  WHILE l_branch_root IS NOT NULL LOOP
    IF should_map_branch(l_branch_root) THEN
      l_map_branch := TRUE;
      log('Found mapping flag at: ' || l_branch_root);
      EXIT;
    END IF;
    
    -- Get parent
    l_branch_root := ew_hierarchy.get_primary_parent_name(
      p_app_dimension_id => ew_lb_api.g_app_dimension_id,
      p_member_name     => l_branch_root
    );
  END LOOP;
  
  IF l_map_branch THEN
    -- Proceed with mapping
    log('Mapping member to target');
    
    -- Optional: Transform the name
    IF ew_lb_api.g_member_name LIKE 'DEPT_%' THEN
      ew_lb_api.g_out_tgt_new_member_name := 
        'PLN_' || ew_lb_api.g_member_name;
    END IF;
    
    -- Use Smart Sync
    ew_hierarchy.set_dim_mapping_method(
      p_mapping_method => 'SMARTSYNC',
      x_status        => ew_lb_api.g_status,
      x_message       => ew_lb_api.g_message
    );
  ELSE
    -- Skip this member
    log('Skipping member - no mapping flag found');
    ew_lb_api.g_out_ignore_flag := 'Y';
    ew_lb_api.g_message := 'Branch not configured for mapping';
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Configuration
Set "MapToPlanning" property to "Y" on root members of branches to map.

---

## Example 3: Cross-Reference Table Mapping

**Scenario**: Use a custom mapping table to translate members between applications.

### Setup Script
```sql
-- Create mapping table (run once)
CREATE TABLE custom_dim_mapping (
  source_app      VARCHAR2(50),
  source_member   VARCHAR2(100),
  target_member   VARCHAR2(100),
  target_parent   VARCHAR2(100),
  active_flag     VARCHAR2(1) DEFAULT 'Y',
  created_date    DATE DEFAULT SYSDATE,
  CONSTRAINT pk_custom_dim_mapping 
    PRIMARY KEY (source_app, source_member)
);

-- Insert sample mappings
INSERT INTO custom_dim_mapping VALUES 
  ('HFM_PROD', 'CC_100', 'COST_100', 'ALL_COSTS', 'Y', SYSDATE);
INSERT INTO custom_dim_mapping VALUES 
  ('HFM_PROD', 'CC_200', 'COST_200', 'ALL_COSTS', 'Y', SYSDATE);
COMMIT;
```

### Mapping Script
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_USING_XREF_TABLE';
  l_target_member VARCHAR2(100);
  l_target_parent VARCHAR2(100);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Looking up mapping for: ' || ew_lb_api.g_member_name);
  
  -- Lookup mapping
  BEGIN
    SELECT target_member, target_parent
    INTO l_target_member, l_target_parent
    FROM custom_dim_mapping
    WHERE source_app = ew_lb_api.g_src_app_name
    AND source_member = ew_lb_api.g_member_name
    AND active_flag = 'Y';
    
    log('Found mapping: ' || l_target_member || ' under ' || l_target_parent);
    
    -- Apply mapping
    ew_lb_api.g_out_tgt_new_member_name := l_target_member;
    
    IF l_target_parent IS NOT NULL THEN
      ew_lb_api.g_out_tgt_parent_member_name := l_target_parent;
    END IF;
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      log('No mapping found - using default');
      -- Use standard Smart Sync if no mapping
      ew_hierarchy.set_dim_mapping_method(
        p_mapping_method => 'SMARTSYNC',
        x_status        => ew_lb_api.g_status,
        x_message       => ew_lb_api.g_message
      );
      
    WHEN TOO_MANY_ROWS THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Duplicate mapping found for ' || 
                              ew_lb_api.g_member_name;
  END;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 4: Level-Based Reorganization

**Scenario**: Reorganize hierarchy based on member levels during mapping.

### Script Code
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_LEVEL_REORG';
  l_member_level NUMBER;
  l_member_gen NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Get member level and generation
  l_member_level := ew_statistics.get_level(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_id       => ew_lb_api.g_member_id
  );
  
  l_member_gen := ew_statistics.get_generation(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_id       => ew_lb_api.g_member_id
  );
  
  log('Member: ' || ew_lb_api.g_member_name || 
      ' Level: ' || l_member_level || 
      ' Gen: ' || l_member_gen);
  
  -- Reorganize based on level
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
    
    IF l_member_level = 0 THEN
      -- All base members under one parent
      ew_lb_api.g_out_tgt_parent_member_name := 'ALL_BASE_MEMBERS';
      ew_lb_api.g_out_tgt_new_member_name := 
        'BASE_' || ew_lb_api.g_member_name;
        
    ELSIF l_member_level <= 2 THEN
      -- Mid-level members under summary parent
      ew_lb_api.g_out_tgt_parent_member_name := 'MID_LEVEL_SUMMARY';
      ew_lb_api.g_out_tgt_new_member_name := 
        'MID_' || ew_lb_api.g_member_name;
        
    ELSIF l_member_gen <= 3 THEN
      -- Top level members keep structure
      ew_hierarchy.set_dim_mapping_method(
        p_mapping_method => 'SMARTSYNC',
        x_status        => ew_lb_api.g_status,
        x_message       => ew_lb_api.g_message
      );
      RETURN;
      
    ELSE
      -- Other members in catch-all
      ew_lb_api.g_out_tgt_parent_member_name := 'OTHER_MEMBERS';
    END IF;
    
    log('Mapped to parent: ' || ew_lb_api.g_out_tgt_parent_member_name);
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 5: Conditional Property Sync

**Scenario**: Map members and selectively sync properties based on conditions.

### Script Code
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_WITH_PROP_SYNC';
  l_sync_properties BOOLEAN := FALSE;
  l_member_type VARCHAR2(50);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  PROCEDURE sync_selected_properties IS
    l_prop_value VARCHAR2(4000);
  BEGIN
    -- Sync specific properties only
    
    -- Get and set Alias
    l_prop_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_src_app_name,
      p_dim_name    => ew_lb_api.g_src_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => 'Alias:English'
    );
    
    IF l_prop_value IS NOT NULL THEN
      -- Set in target (would need additional API call)
      log('Syncing alias: ' || l_prop_value);
    END IF;
    
    -- Get and set custom property
    l_prop_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_src_app_name,
      p_dim_name    => ew_lb_api.g_src_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => 'Cost_Center_Type'
    );
    
    IF l_prop_value IS NOT NULL THEN
      log('Syncing CC Type: ' || l_prop_value);
    END IF;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Processing: ' || ew_lb_api.g_member_name);
  
  -- Determine member type
  IF ew_lb_api.g_member_name LIKE 'CC_%' THEN
    l_member_type := 'COST_CENTER';
    l_sync_properties := TRUE;
  ELSIF ew_lb_api.g_member_name LIKE 'PC_%' THEN
    l_member_type := 'PROFIT_CENTER';
    l_sync_properties := TRUE;
  ELSE
    l_member_type := 'OTHER';
    l_sync_properties := FALSE;
  END IF;
  
  -- Map member with type prefix
  ew_lb_api.g_out_tgt_new_member_name := 
    l_member_type || '_' || ew_lb_api.g_member_name;
  
  -- Sync hierarchy
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SMARTSYNC',
    x_status        => ew_lb_api.g_status,
    x_message       => ew_lb_api.g_message
  );
  
  -- Conditionally sync properties
  IF l_sync_properties AND ew_lb_api.g_status = ew_lb_api.g_success THEN
    sync_selected_properties();
  END IF;
  
  log('Mapping complete');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 6: Error Handling and Validation

**Scenario**: Comprehensive error handling with validation before mapping.

### Script Code
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_WITH_VALIDATION';
  l_errors VARCHAR2(4000);
  l_warnings VARCHAR2(4000);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  PROCEDURE add_error(p_msg VARCHAR2) IS
  BEGIN
    IF l_errors IS NOT NULL THEN
      l_errors := l_errors || '; ';
    END IF;
    l_errors := l_errors || p_msg;
  END;
  
  PROCEDURE add_warning(p_msg VARCHAR2) IS
  BEGIN
    IF l_warnings IS NOT NULL THEN
      l_warnings := l_warnings || '; ';
    END IF;
    l_warnings := l_warnings || p_msg;
  END;
  
  FUNCTION validate_member RETURN BOOLEAN IS
    l_valid BOOLEAN := TRUE;
  BEGIN
    -- Check member name length
    IF LENGTH(ew_lb_api.g_member_name) > 50 THEN
      add_error('Member name too long (max 50 chars)');
      l_valid := FALSE;
    END IF;
    
    -- Check for invalid characters
    IF REGEXP_LIKE(ew_lb_api.g_member_name, '[^A-Za-z0-9_]') THEN
      add_error('Member name contains invalid characters');
      l_valid := FALSE;
    END IF;
    
    -- Check if parent exists in target (for create actions)
    IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
      IF ew_lb_api.g_parent_member_name IS NOT NULL THEN
        IF ew_hierarchy.chk_member_exists(
             p_app_dimension_id => ew_lb_api.g_tgt_dim_id,
             p_member_name     => ew_lb_api.g_parent_member_name
           ) = 'N' THEN
          add_error('Parent does not exist in target: ' || 
                    ew_lb_api.g_parent_member_name);
          l_valid := FALSE;
        END IF;
      END IF;
    END IF;
    
    -- Check for duplicate in target (warning only)
    IF ew_lb_api.g_action_code = 'CMC' THEN
      IF ew_hierarchy.chk_member_exists(
           p_app_dimension_id => ew_lb_api.g_tgt_dim_id,
           p_member_name     => ew_lb_api.g_member_name
         ) = 'Y' THEN
        add_warning('Member already exists in target');
      END IF;
    END IF;
    
    RETURN l_valid;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  l_errors := NULL;
  l_warnings := NULL;
  
  log('Starting validation for: ' || ew_lb_api.g_member_name);
  
  -- Validate before processing
  IF NOT validate_member() THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation failed: ' || l_errors;
    log('Validation errors: ' || l_errors);
    RETURN;
  END IF;
  
  -- Log warnings but continue
  IF l_warnings IS NOT NULL THEN
    log('Warnings: ' || l_warnings);
  END IF;
  
  -- Proceed with mapping
  BEGIN
    -- Custom transformation
    IF ew_lb_api.g_member_name LIKE 'TEMP_%' THEN
      -- Skip temporary members
      ew_lb_api.g_out_ignore_flag := 'Y';
      ew_lb_api.g_message := 'Temporary member skipped';
    ELSE
      -- Normal mapping
      ew_hierarchy.set_dim_mapping_method(
        p_mapping_method => 'SMARTSYNC',
        x_status        => ew_lb_api.g_status,
        x_message       => ew_lb_api.g_message
      );
    END IF;
    
  EXCEPTION
    WHEN OTHERS THEN
      -- Catch any mapping errors
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Mapping error: ' || SQLERRM;
      log('Mapping error: ' || SQLERRM);
  END;
  
  -- Add warnings to message if successful
  IF ew_lb_api.g_status = ew_lb_api.g_success AND l_warnings IS NOT NULL THEN
    ew_lb_api.g_message := NVL(ew_lb_api.g_message, 'Success') || 
                           ' (Warnings: ' || l_warnings || ')';
  END IF;
  
  log('Processing complete. Status: ' || ew_lb_api.g_status);
  
EXCEPTION
  WHEN OTHERS THEN
    -- Global exception handler
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Unexpected error: ' || SQLERRM;
    log('Unexpected error: ' || SQLERRM);
    log('Error backtrace: ' || DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
END;
```

---

## Testing Guidelines

### Unit Test Cases

For each mapping script, test:

1. **Create Member as Child (CMC)**
   - Create new member under existing parent
   - Verify name transformation
   - Check parent assignment

2. **Delete Member (DM)**
   - Delete member from source
   - Verify removal from target

3. **Rename Member (RNM)**
   - Rename in source
   - Verify rename in target with transformation

4. **Move Member (ZC)**
   - Change parent in source
   - Verify move in target

5. **Edge Cases**
   - Null parent (root level)
   - Special characters in names
   - Very long member names
   - Circular references

### Debug and Monitoring

Enable debug logging during testing:

```sql
-- In your script
ew_debug.log('=== Test Case: Create Member ===');
ew_debug.log('Input: ' || ew_lb_api.g_member_name);
ew_debug.log('Output: ' || ew_lb_api.g_out_tgt_new_member_name);
```

View results in Debug Messages report filtered by script name.

## Next Steps

- [Input Parameters](input-parameters.md) - Complete parameter reference
- [Output Parameters](output-parameters.md) - Control mapping behavior
- [API Reference](../../api/packages/hierarchy.md) - Supporting APIs

---

!!! tip "Development Tip"
    Start with a simple mapping script and gradually add complexity. Always test with a small subset of members before running on the entire dimension.