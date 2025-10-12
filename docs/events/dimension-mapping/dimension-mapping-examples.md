# Dimension Mapping Examples

This page provides practical examples of Dimension Mapping Logic Scripts for common scenarios.

## Example 1: Basic Cross-Application Synchronization

**Scenario:** Synchronize Entity dimension from Planning to HFM with prefix transformation.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_ENTITY_PLAN_TO_HFM';
  c_prefix      CONSTANT VARCHAR2(10)  := 'HFM_';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize status
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Processing action: ' || ew_lb_api.g_action_code);
  log('Member: ' || ew_lb_api.g_member_name);
  
  -- Add prefix to all members
  ew_lb_api.g_out_member_name := c_prefix || ew_lb_api.g_member_name;
  
  IF ew_lb_api.g_parent_member_name IS NOT NULL THEN
    ew_lb_api.g_out_parent_member_name := c_prefix || ew_lb_api.g_parent_member_name;
  END IF;
  
  -- Handle rename operations
  IF ew_lb_api.g_action_code = 'R' THEN
    ew_lb_api.g_out_old_member_name := c_prefix || ew_lb_api.g_renamed_from_member_name;
    ew_lb_api.g_out_new_member_name := c_prefix || ew_lb_api.g_member_name;
  END IF;
  
  -- Handle move operations  
  IF ew_lb_api.g_action_code IN ('M', 'ZC', 'ZS') THEN
    ew_lb_api.g_out_moved_to_member_name := c_prefix || ew_lb_api.g_moved_to_member_name;
  END IF;
  
  log('Mapped to: ' || ew_lb_api.g_out_member_name);
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error in mapping: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

## Example 2: Filtered Synchronization

**Scenario:** Only synchronize cost centers starting with 'CC_' to the target application.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'FILTER_COST_CENTERS';
  
  FUNCTION should_sync_member(p_member_name VARCHAR2) RETURN BOOLEAN IS
  BEGIN
    -- Only sync cost centers
    RETURN SUBSTR(p_member_name, 1, 3) = 'CC_';
  END;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  IF should_sync_member(ew_lb_api.g_member_name) THEN
    -- Proceed with standard mapping
    ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
  ELSE
    -- Skip this member
    ew_lb_api.g_out_ignore_flag := 'Y';
    ew_debug.log('Skipping non-cost center: ' || ew_lb_api.g_member_name,
                 c_script_name);
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := SQLERRM;
END;
```

![Filtered Synchronization Flow](../../assets/images/filtered-sync-flow.png)
*Figure: Filtered synchronization only maps selected members*

## Example 3: Property-Based Conditional Mapping

**Scenario:** Map accounts differently based on their account type property.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'ACCOUNT_TYPE_MAPPING';
  l_account_type VARCHAR2(100);
  l_target_parent VARCHAR2(100);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get account type property
  l_account_type := ew_hierarchy.get_member_prop_value(
    p_app_name    => ew_lb_api.g_app_name,
    p_dim_name    => ew_lb_api.g_dim_name,
    p_member_name => ew_lb_api.g_member_name,
    p_prop_label  => 'Account Type'
  );
  
  -- Determine target parent based on account type
  CASE l_account_type
    WHEN 'Revenue' THEN
      l_target_parent := 'TotalRevenue';
    WHEN 'Expense' THEN
      l_target_parent := 'TotalExpense';
    WHEN 'Asset' THEN
      l_target_parent := 'TotalAssets';
    WHEN 'Liability' THEN
      l_target_parent := 'TotalLiabilities';
    ELSE
      l_target_parent := 'UnmappedAccounts';
  END CASE;
  
  -- Set mapping based on action
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
    -- Create under appropriate parent
    ew_lb_api.g_out_member_name := ew_lb_api.g_member_name;
    ew_lb_api.g_out_parent_member_name := l_target_parent;
  ELSE
    -- Use standard mapping for other actions
    ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
  END IF;
  
  ew_debug.log('Mapped ' || ew_lb_api.g_member_name || 
               ' (Type: ' || l_account_type || ') to parent ' || l_target_parent,
               c_script_name);
               
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error in account mapping: ' || SQLERRM;
END;
```

## Example 4: Complex Hierarchy Transformation

**Scenario:** Flatten a multi-level hierarchy into a two-level structure.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'FLATTEN_HIERARCHY';
  l_top_parent VARCHAR2(100);
  l_member_level NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get the top-level parent (level 2 in hierarchy)
  l_top_parent := ew_hierarchy.get_branch_member(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_name      => ew_lb_api.g_member_name,
    p_level            => 2  -- Second level from top
  );
  
  -- Determine if this is a leaf member
  IF ew_hierarchy.is_leaf(
       p_member_id        => ew_lb_api.g_member_id,
       p_app_dimension_id => ew_lb_api.g_app_dimension_id
     ) = 'Y' THEN
    
    -- Map leaf members directly under their top parent
    ew_lb_api.g_out_member_name := ew_lb_api.g_member_name;
    ew_lb_api.g_out_parent_member_name := NVL(l_top_parent, 'OrphanMembers');
    
  ELSE
    -- Skip intermediate levels
    ew_lb_api.g_out_ignore_flag := 'Y';
  END IF;
  
  ew_debug.log('Flattened ' || ew_lb_api.g_member_name || 
               ' under ' || l_top_parent, c_script_name);
               
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := SQLERRM;
END;
```

## Example 5: Shared Member Handling

**Scenario:** Create shared members in multiple locations based on business rules.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'SHARED_MEMBER_MAPPING';
  l_entity_type VARCHAR2(100);
  l_idx NUMBER := 0;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Check if this is a shared member operation
  IF ew_lb_api.g_action_code IN ('ISMC', 'ISMS') THEN
    
    -- Get entity type to determine sharing rules
    l_entity_type := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => 'EntityType'
    );
    
    -- Add to multiple parents based on type
    IF l_entity_type = 'Global' THEN
      -- Share globally
      l_idx := l_idx + 1;
      ew_lb_api.g_out_shared_members_tbl(l_idx) := ew_lb_api.g_member_name;
      ew_lb_api.g_out_shared_parent_tbl(l_idx) := 'Region_Americas';
      
      l_idx := l_idx + 1;
      ew_lb_api.g_out_shared_members_tbl(l_idx) := ew_lb_api.g_member_name;
      ew_lb_api.g_out_shared_parent_tbl(l_idx) := 'Region_EMEA';
      
      l_idx := l_idx + 1;
      ew_lb_api.g_out_shared_members_tbl(l_idx) := ew_lb_api.g_member_name;
      ew_lb_api.g_out_shared_parent_tbl(l_idx) := 'Region_APAC';
    ELSE
      -- Standard sharing
      ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
    END IF;
    
  ELSE
    -- Non-shared operations
    ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := SQLERRM;
END;
```

## Example 6: Error Handling and Validation

**Scenario:** Validate member names and properties before mapping.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VALIDATED_MAPPING';
  
  FUNCTION validate_member_name(p_name VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Check length
    IF LENGTH(p_name) > 50 THEN
      RETURN 'Member name exceeds 50 characters';
    END IF;
    
    -- Check for invalid characters
    IF REGEXP_LIKE(p_name, '[^A-Za-z0-9_]') THEN
      RETURN 'Member name contains invalid characters';
    END IF;
    
    RETURN NULL; -- No errors
  END;
  
  l_error_msg VARCHAR2(4000);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Validate member name
  l_error_msg := validate_member_name(ew_lb_api.g_member_name);
  
  IF l_error_msg IS NOT NULL THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := l_error_msg;
    RETURN;
  END IF;
  
  -- Check if target parent exists
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
    IF ew_hierarchy.chk_member_exists(
         p_app_dimension_id => ew_lb_api.g_mapped_app_dimension_id,
         p_member_name      => ew_lb_api.g_parent_member_name
       ) = 'N' THEN
      
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Target parent does not exist: ' || 
                             ew_lb_api.g_parent_member_name;
      RETURN;
    END IF;
  END IF;
  
  -- Proceed with mapping
  ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
  
  ew_debug.log('Successfully validated and mapped: ' || ew_lb_api.g_member_name,
               c_script_name);
               
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Unexpected error: ' || SQLERRM;
    ew_debug.log('Error: ' || SQLERRM, c_script_name);
END;
```

## Testing Your Mapping Scripts

### 1. Create Test Members

Create test members in your source dimension to validate mapping logic.

### 2. Check Debug Messages

Monitor the Debug Messages report for execution details:

![Debug Messages Report](../../assets/images/mapping-debug-report.png)
*Figure: Debug Messages showing mapping execution details*

### 3. Verify Target Dimension

Confirm members are created correctly in the target dimension with expected:
- Names and hierarchy structure
- Property values
- Shared member instances

### 4. Test All Action Codes

Ensure your script handles all relevant action codes:
- Create (CMC, CMS)
- Delete (D)
- Rename (R)
- Move (M, ZC, ZS)
- Shared members (ISMC, ISMS)

## Related Topics

- [Input Parameters](input-parameters.md)
- [Output Parameters](output-parameters.md)
- [Dimension Mapping Overview](index.md)
- [API Reference - Hierarchy](../../api/packages/hierarchy.md)