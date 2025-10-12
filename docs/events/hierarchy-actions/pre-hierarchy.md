# Pre-Hierarchy Action Scripts

Pre-Hierarchy Action scripts execute before hierarchy changes are committed, providing a validation gate to ensure data integrity and enforce business rules. These scripts can prevent invalid operations by returning an error status.

## Overview

Pre-Hierarchy Actions serve as gatekeepers for:
- **Validation**: Ensure changes meet business rules
- **Authorization**: Verify user permissions
- **Integrity**: Prevent invalid hierarchy structures
- **Compliance**: Enforce naming standards
- **Dependencies**: Check for conflicts

![Pre-Hierarchy Validation Flow](../../assets/images/pre-hierarchy-flow.png)
*Figure: Pre-hierarchy validation preventing invalid changes*

## When to Use

Pre-Hierarchy scripts are essential for:
- Enforcing naming conventions
- Preventing duplicate members
- Validating hierarchy depth limits
- Checking referential integrity
- Ensuring data consistency
- Blocking unauthorized changes

## Key Characteristics

- **Blocking**: Can prevent the action
- **Synchronous**: User waits for completion
- **Transactional**: Part of the change transaction
- **Performance Critical**: Must be fast
- **User-Facing**: Messages shown to user

## Common Validation Patterns

### Pattern 1: Member Name Validation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_VALIDATE_MEMBER_NAME';
  c_name_pattern CONSTANT VARCHAR2(100) := '^[A-Z][A-Z0-9_]{2,49}$';
  l_exists VARCHAR2(1);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Pre-validation for action: ' || ew_lb_api.g_action_code);
  
  -- Validate for create and rename actions
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS', 'RNM') THEN
    
    -- Check naming convention
    IF NOT REGEXP_LIKE(ew_lb_api.g_new_member_name, c_name_pattern) THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Member name must start with a letter, ' ||
                              'be 3-50 characters, contain only letters, ' ||
                              'numbers, and underscores';
      log('Invalid name format: ' || ew_lb_api.g_new_member_name);
      RETURN;
    END IF;
    
    -- Check for reserved words
    IF ew_lb_api.g_new_member_name IN ('SYSTEM', 'ADMIN', 'ROOT', 'TOTAL') THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Cannot use reserved name: ' || 
                              ew_lb_api.g_new_member_name;
      RETURN;
    END IF;
    
    -- Check for duplicates (case-insensitive)
    l_exists := ew_hierarchy.chk_member_exists(
      p_app_dimension_id => ew_lb_api.g_app_dimension_id,
      p_member_name     => ew_lb_api.g_new_member_name,
      p_case_match      => 'N'
    );
    
    IF l_exists = 'Y' AND ew_lb_api.g_action_code != 'RNM' THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Member already exists: ' || 
                              ew_lb_api.g_new_member_name;
      RETURN;
    END IF;
  END IF;
  
  log('Validation passed');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Pattern 2: Hierarchy Depth Validation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_CHECK_HIERARCHY_DEPTH';
  c_max_depth CONSTANT NUMBER := 15;
  l_current_depth NUMBER;
  l_member_depth NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION calculate_depth(p_parent_name VARCHAR2) RETURN NUMBER IS
    l_depth NUMBER := 0;
    l_current_parent VARCHAR2(100) := p_parent_name;
  BEGIN
    WHILE l_current_parent IS NOT NULL AND l_depth < c_max_depth + 1 LOOP
      l_depth := l_depth + 1;
      
      l_current_parent := ew_hierarchy.get_primary_parent_name(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_member_name     => l_current_parent
      );
    END LOOP;
    
    RETURN l_depth;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Check depth for create and move actions
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS', 'ZC') THEN
    
    -- Calculate depth from new parent to root
    l_current_depth := calculate_depth(ew_lb_api.g_parent_member_name);
    
    log('Current depth from parent: ' || l_current_depth);
    
    -- For move action, also consider depth of subtree being moved
    IF ew_lb_api.g_action_code = 'ZC' THEN
      l_member_depth := ew_statistics.get_max_depth(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_member_id       => ew_lb_api.g_member_id
      );
      
      log('Member subtree depth: ' || l_member_depth);
      l_current_depth := l_current_depth + l_member_depth;
    END IF;
    
    IF l_current_depth > c_max_depth THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Operation would exceed maximum hierarchy depth of ' || 
                              c_max_depth || ' levels. Current depth: ' || 
                              l_current_depth;
      log('Depth limit exceeded');
    END IF;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Depth check error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Pattern 3: Deletion Protection

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_PROTECT_DELETION';
  l_child_count NUMBER;
  l_data_exists VARCHAR2(1);
  l_is_system VARCHAR2(1);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION has_data(p_member_id NUMBER) RETURN VARCHAR2 IS
    l_count NUMBER;
  BEGIN
    -- Check if member has associated data
    SELECT COUNT(*)
    INTO l_count
    FROM member_data_table
    WHERE member_id = p_member_id
    AND ROWNUM = 1;
    
    RETURN CASE WHEN l_count > 0 THEN 'Y' ELSE 'N' END;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only check for delete actions
  IF ew_lb_api.g_action_code IN ('DM', 'DSHM') THEN
    
    log('Checking deletion protection for: ' || ew_lb_api.g_member_name);
    
    -- Check if system member
    l_is_system := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => 'System_Member'
    );
    
    IF l_is_system = 'Y' THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Cannot delete system member: ' || 
                              ew_lb_api.g_member_name;
      RETURN;
    END IF;
    
    -- Check for children (only for full delete, not shared)
    IF ew_lb_api.g_action_code = 'DM' THEN
      l_child_count := ew_statistics.get_child_count(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_parent_member_id => ew_lb_api.g_member_id
      );
      
      IF l_child_count > 0 THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Cannot delete member with ' || 
                                l_child_count || ' children. Delete children first.';
        RETURN;
      END IF;
      
      -- Check for data
      l_data_exists := has_data(ew_lb_api.g_member_id);
      
      IF l_data_exists = 'Y' THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Cannot delete member with existing data. ' ||
                                'Archive or transfer data first.';
        RETURN;
      END IF;
    END IF;
    
    log('Deletion checks passed');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Deletion check error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Pattern 4: Circular Reference Prevention

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_PREVENT_CIRCULAR_REF';
  l_is_descendant VARCHAR2(1);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION is_descendant(
    p_potential_child VARCHAR2,
    p_potential_parent VARCHAR2
  ) RETURN VARCHAR2 IS
    l_current VARCHAR2(100) := p_potential_parent;
    l_iterations NUMBER := 0;
  BEGIN
    -- Walk up from potential parent to see if we find potential child
    WHILE l_current IS NOT NULL AND l_iterations < 100 LOOP
      IF l_current = p_potential_child THEN
        RETURN 'Y'; -- Circular reference detected
      END IF;
      
      l_current := ew_hierarchy.get_primary_parent_name(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_member_name     => l_current
      );
      
      l_iterations := l_iterations + 1;
    END LOOP;
    
    RETURN 'N';
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Check for move actions
  IF ew_lb_api.g_action_code = 'ZC' THEN
    
    log('Checking circular reference: ' || 
        ew_lb_api.g_member_name || ' → ' || 
        ew_lb_api.g_parent_member_name);
    
    -- Check if new parent is a descendant of member being moved
    l_is_descendant := is_descendant(
      p_potential_child  => ew_lb_api.g_member_name,
      p_potential_parent => ew_lb_api.g_parent_member_name
    );
    
    IF l_is_descendant = 'Y' THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Cannot move member to its own descendant. ' ||
                              'This would create a circular reference.';
      log('Circular reference detected');
    ELSE
      log('No circular reference');
    END IF;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Circular reference check error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

## Configuration Examples

### Example 1: Department Hierarchy Rules

```sql
-- Enforce department structure rules
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_DEPT_HIERARCHY_RULES';
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Rules for department hierarchy
  IF ew_lb_api.g_dim_name = 'Department' THEN
    
    -- Rule 1: Departments must start with DEPT_
    IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
      IF SUBSTR(ew_lb_api.g_new_member_name, 1, 5) != 'DEPT_' THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Department codes must start with DEPT_';
        RETURN;
      END IF;
    END IF;
    
    -- Rule 2: Sub-departments under specific parents only
    IF ew_lb_api.g_action_code = 'CMC' THEN
      IF ew_lb_api.g_parent_member_name NOT LIKE 'DEPT_%' AND
         ew_lb_api.g_parent_member_name != 'ALL_DEPARTMENTS' THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Departments can only be created under department parents';
        RETURN;
      END IF;
    END IF;
    
    -- Rule 3: Max 3 levels of departments
    IF ew_lb_api.g_action_code IN ('CMC', 'ZC') THEN
      DECLARE
        l_parent_level NUMBER;
      BEGIN
        l_parent_level := ew_statistics.get_level(
          p_app_dimension_id => ew_lb_api.g_app_dimension_id,
          p_member_name     => ew_lb_api.g_parent_member_name
        );
        
        IF l_parent_level >= 2 THEN
          ew_lb_api.g_status := ew_lb_api.g_error;
          ew_lb_api.g_message := 'Maximum 3 levels of department hierarchy allowed';
        END IF;
      END;
    END IF;
  END IF;
END;
```

### Example 2: Time Period Validation

```sql
-- Validate time period hierarchy changes
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PRE_TIME_PERIOD_RULES';
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  IF ew_lb_api.g_dim_name = 'Time' THEN
    
    -- Prevent structural changes to time dimension
    IF ew_lb_api.g_action_code IN ('DM', 'ZC', 'RNM') THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Time dimension structure is locked. ' ||
                              'Contact administrator for changes.';
      RETURN;
    END IF;
    
    -- Only allow specific member patterns
    IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
      IF NOT REGEXP_LIKE(ew_lb_api.g_new_member_name, 
                          '^(FY|Q|M)[0-9]{2,4}$') THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Time members must follow pattern: ' ||
                                'FY20, Q1, M01, etc.';
      END IF;
    END IF;
  END IF;
END;
```

## Performance Optimization

### Best Practices for Speed

1. **Exit Early on First Error**
```sql
IF quick_check_fails THEN
  ew_lb_api.g_status := ew_lb_api.g_error;
  ew_lb_api.g_message := 'Quick check failed';
  RETURN; -- Don't continue checking
END IF;
```

2. **Cache Validation Data**
```sql
-- Package-level cache
g_valid_parents VARCHAR2(4000);

-- Load once per session
IF g_valid_parents IS NULL THEN
  SELECT LISTAGG(member_name, ',')
  INTO g_valid_parents
  FROM valid_parent_members;
END IF;
```

3. **Use Indexes**
```sql
-- Ensure indexes exist for validation queries
CREATE INDEX idx_member_validate 
ON ew_members(app_dimension_id, member_name, active_flag);
```

4. **Minimize Database Calls**
```sql
-- Bad: Multiple queries
FOR i IN 1..10 LOOP
  check_something(i);
END LOOP;

-- Good: Single query
check_all_at_once();
```

## Testing Pre-Hierarchy Scripts

### Test Matrix

| Action | Test Case | Expected Result |
|--------|-----------|-----------------|
| CMC | Valid new member | Success |
| CMC | Duplicate name | Error message |
| CMC | Invalid format | Error message |
| DM | Leaf member | Success |
| DM | Parent with children | Error message |
| ZC | Valid move | Success |
| ZC | Circular reference | Error message |
| RNM | Unique new name | Success |
| RNM | Existing name | Error message |

### Debug Techniques

```sql
-- Enable detailed logging
ew_debug.set_level('DEBUG');

-- Log all parameters
ew_debug.log('Action: ' || ew_lb_api.g_action_code);
ew_debug.log('Member: ' || ew_lb_api.g_member_name);
ew_debug.log('New Name: ' || ew_lb_api.g_new_member_name);
ew_debug.log('Parent: ' || ew_lb_api.g_parent_member_name);

-- Time validation
l_start := DBMS_UTILITY.GET_TIME;
-- validation logic
l_elapsed := (DBMS_UTILITY.GET_TIME - l_start) / 100;
ew_debug.log('Validation time: ' || l_elapsed || ' seconds');
```

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow validation | Complex queries | Optimize queries, add indexes |
| Always fails | Logic error | Debug with test cases |
| Inconsistent behavior | Missing action codes | Handle all relevant actions |
| Blocks valid changes | Too restrictive | Review business rules |

## Next Steps

- [Post-Hierarchy Actions](post-hierarchy.md) - Automation after changes
- [Seeded Scripts](seeded-scripts.md) - EPMware standard scripts
- [Examples](../index.md#common-patterns) - More script patterns

---

!!! warning "Performance Critical"
    Pre-hierarchy scripts directly impact user experience. Keep validation logic fast and efficient. Consider deferring complex operations to post-hierarchy actions when possible.