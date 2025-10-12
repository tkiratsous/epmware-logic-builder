# Logic Script Structure

Understanding the structure and components of Logic Scripts is essential for developing robust and maintainable solutions in EPMware.

## Basic Script Anatomy

Every Logic Script consists of three main sections:

```sql
DECLARE
  -- Variable declarations and initialization
BEGIN
  -- Main logic implementation
EXCEPTION
  -- Error handling
END;
```

## Script Components

### Declaration Section

The `DECLARE` section contains:

```sql
DECLARE
  -- Constants
  c_script_name    CONSTANT VARCHAR2(100) := 'MY_SCRIPT_NAME';
  c_max_retries    CONSTANT NUMBER := 3;
  c_default_value  CONSTANT VARCHAR2(50) := 'DEFAULT';
  
  -- Variables
  l_counter        NUMBER := 0;
  l_error_message  VARCHAR2(4000);
  l_member_list    ew_global.g_char_tbl;
  
  -- Cursors
  CURSOR cur_members IS
    SELECT member_name, member_id
    FROM   ew_members_v
    WHERE  app_dimension_id = ew_lb_api.g_app_dimension_id;
  
  -- Local procedures/functions
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  -- Exception definitions
  e_validation_failed EXCEPTION;
  e_member_not_found  EXCEPTION;
```

### Execution Section

The `BEGIN...END` block contains the main logic:

```sql
BEGIN
  -- Always initialize status
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Log script start
  log('Script execution started');
  log('Input parameters:');
  log('  Member: ' || ew_lb_api.g_member_name);
  log('  Action: ' || ew_lb_api.g_action_code);
  
  -- Main logic
  IF ew_lb_api.g_action_code = 'CMC' THEN
    -- Process create member as child
    process_create_member();
  ELSIF ew_lb_api.g_action_code = 'P' THEN
    -- Process property edit
    process_property_edit();
  END IF;
  
  -- Set output parameters
  ew_lb_api.g_out_prop_value := l_calculated_value;
  
  log('Script execution completed successfully');
```

### Exception Section

Proper error handling is crucial:

```sql
EXCEPTION
  WHEN e_validation_failed THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation failed: ' || l_error_message;
    log('Validation error: ' || l_error_message);
    
  WHEN NO_DATA_FOUND THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Required data not found';
    log('No data found for member: ' || ew_lb_api.g_member_name);
    
  WHEN OTHERS THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Unexpected error: ' || SUBSTR(SQLERRM, 1, 200);
    log('Exception: ' || SQLERRM);
    log('Backtrace: ' || DBMS_UTILITY.format_error_backtrace);
END;
```

## Input Parameters

### Common Input Parameters

All script types have access to common parameters through `ew_lb_api`:

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_user_id` | NUMBER | Current logged-in user ID |
| `g_lb_script_name` | VARCHAR2 | Name of executing script |
| `g_request_id` | NUMBER | Current request ID |
| `g_app_name` | VARCHAR2 | Application name |
| `g_dim_name` | VARCHAR2 | Dimension name |
| `g_wf_code` | VARCHAR2 | Workflow code |
| `g_wf_stage_name` | VARCHAR2 | Current workflow stage |

### Script-Specific Parameters

Different script types receive additional parameters:

#### Hierarchy Action Scripts
```sql
g_member_name              -- Member being acted upon
g_parent_member_name       -- Parent of the member
g_new_member_name          -- New member (for creates)
g_action_code              -- Action code (CMC, CMS, DM, etc.)
g_action_name              -- Action name (Create Member, Delete, etc.)
```

#### Property Scripts
```sql
g_prop_name                -- Property internal name
g_prop_label               -- Property display label
g_prop_value               -- Current property value
g_array_member_name        -- For alias-type properties
```

#### Mapping Scripts
```sql
g_mapped_app_name          -- Target application
g_mapped_dim_name          -- Target dimension
g_renamed_from_member_name -- Original name (for renames)
g_moved_from_member_name   -- Source parent (for moves)
g_moved_to_member_name     -- Target parent (for moves)
```

## Output Parameters

### Common Output Parameters

All scripts must set these status parameters:

```sql
-- Status (Required)
ew_lb_api.g_status := ew_lb_api.g_success;  -- or g_error

-- Message (Required on error)
ew_lb_api.g_message := 'Error description';

-- Ignore flag (Optional)
ew_lb_api.g_out_ignore_flag := 'Y';  -- Skip this action
```

### Script-Specific Output Parameters

#### Dimension Mapping
```sql
g_out_member_name          -- Mapped member name
g_out_parent_member_name   -- Mapped parent name
g_out_new_member_name      -- New member for target
g_out_moved_to_member_name -- Target parent for moves
g_out_shared_members_tbl   -- Array for shared members
```

#### Property Derivation
```sql
g_out_prop_value           -- Derived property value
```

#### Workflow Custom Tasks
```sql
g_out_rewind_stages        -- Number of stages to rewind
```

## Debug and Logging

### Debug Logging Implementation

Create a reusable logging procedure:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'MY_SCRIPT';
  c_debug_level VARCHAR2(10)  := 'DEBUG';  -- DEBUG, INFO, ERROR
  
  PROCEDURE log(
    p_msg   IN VARCHAR2,
    p_level IN VARCHAR2 DEFAULT 'INFO'
  ) IS
  BEGIN
    IF c_debug_level = 'DEBUG' OR p_level IN ('ERROR', 'INFO') THEN
      ew_debug.log(
        p_text       => '[' || p_level || '] ' || p_msg,
        p_source_ref => c_script_name
      );
    END IF;
  END log;
BEGIN
  log('Script started', 'INFO');
  log('Processing member: ' || ew_lb_api.g_member_name, 'DEBUG');
  
  -- Main logic...
  
  log('Script completed', 'INFO');
EXCEPTION
  WHEN OTHERS THEN
    log('Error: ' || SQLERRM, 'ERROR');
    RAISE;
END;
```

### Debug Message Retrieval

![Debug Messages Report](../assets/images/debug-messages-report.png)
*Figure: Debug Messages report showing script execution logs*

Access debug messages through:
1. Navigate to **Reports → Admin → Debug Messages**
2. Filter by Source Reference (script name)
3. Set date/time range
4. Export results if needed

### Performance Logging

Track execution time for optimization:

```sql
DECLARE
  l_start_time TIMESTAMP := SYSTIMESTAMP;
  l_end_time   TIMESTAMP;
  l_elapsed    INTERVAL DAY TO SECOND;
BEGIN
  -- Main logic...
  
  l_end_time := SYSTIMESTAMP;
  l_elapsed  := l_end_time - l_start_time;
  
  log('Execution time: ' || 
      EXTRACT(SECOND FROM l_elapsed) || ' seconds');
END;
```

## Exception Handling

### Standard Exception Types

Handle common database exceptions:

```sql
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    -- Handle missing data
    ew_lb_api.g_message := 'Required data not found';
    
  WHEN TOO_MANY_ROWS THEN
    -- Handle unexpected multiple rows
    ew_lb_api.g_message := 'Multiple records found - expected one';
    
  WHEN DUP_VAL_ON_INDEX THEN
    -- Handle duplicate value
    ew_lb_api.g_message := 'Duplicate value exists';
    
  WHEN VALUE_ERROR THEN
    -- Handle data type/size issues
    ew_lb_api.g_message := 'Invalid data type or value';
    
  WHEN OTHERS THEN
    -- Catch-all for unexpected errors
    ew_lb_api.g_message := 'Unexpected error: ' || SQLERRM;
```

### Custom Exceptions

Define and use custom exceptions:

```sql
DECLARE
  e_invalid_format    EXCEPTION;
  e_business_rule     EXCEPTION;
  e_dependency_failed EXCEPTION;
  
  PRAGMA EXCEPTION_INIT(e_invalid_format, -20001);
  PRAGMA EXCEPTION_INIT(e_business_rule, -20002);
BEGIN
  -- Raise custom exception
  IF NOT validate_format(l_value) THEN
    RAISE_APPLICATION_ERROR(-20001, 'Invalid format for value: ' || l_value);
  END IF;
  
EXCEPTION
  WHEN e_invalid_format THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := SQLERRM;
```

### Error Context Preservation

Maintain error context through nested calls:

```sql
DECLARE
  l_context VARCHAR2(4000);
  
  PROCEDURE process_member IS
  BEGIN
    -- Processing logic
  EXCEPTION
    WHEN OTHERS THEN
      l_context := 'Error in process_member for: ' || g_member_name;
      RAISE;
  END;
BEGIN
  process_member();
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_message := l_context || ' - ' || SQLERRM;
    log('Full error: ' || DBMS_UTILITY.format_error_backtrace);
END;
```

## Validation and Testing

### Script Validation

Click **Save** to trigger automatic validation:

![Script Validation](../assets/images/script-validation-process.png)
*Figure: Script validation process showing syntax check*

Validation checks:
- PL/SQL syntax correctness
- Variable declarations
- Procedure/function definitions
- Exception handler presence

### Testing Patterns

#### Test Mode Implementation

```sql
DECLARE
  c_test_mode BOOLEAN := FALSE;  -- Set TRUE for testing
  
  -- Test data
  c_test_member VARCHAR2(100) := 'TEST_MEMBER_001';
  c_test_value  VARCHAR2(100) := 'TEST_VALUE';
BEGIN
  IF c_test_mode THEN
    -- Override with test data
    ew_lb_api.g_member_name := c_test_member;
    ew_lb_api.g_prop_value  := c_test_value;
    log('TEST MODE ACTIVE');
  END IF;
  
  -- Regular processing...
END;
```

#### Assertion Checks

```sql
PROCEDURE assert(
  p_condition IN BOOLEAN,
  p_message   IN VARCHAR2
) IS
BEGIN
  IF NOT p_condition THEN
    RAISE_APPLICATION_ERROR(-20999, 'Assertion failed: ' || p_message);
  END IF;
END;

BEGIN
  -- Use assertions for critical checks
  assert(ew_lb_api.g_member_name IS NOT NULL, 'Member name required');
  assert(LENGTH(ew_lb_api.g_prop_value) <= 50, 'Value too long');
```

## Performance Optimization

### Query Optimization

Use efficient query patterns:

```sql
-- Bad: Multiple queries in loop
FOR rec IN cur_members LOOP
  SELECT prop_value INTO l_value
  FROM   member_props
  WHERE  member_id = rec.member_id;
END LOOP;

-- Good: Single query with join
FOR rec IN (
  SELECT m.member_id, p.prop_value
  FROM   members m
  JOIN   member_props p ON p.member_id = m.member_id
) LOOP
  -- Process...
END LOOP;
```

### Bulk Operations

Use bulk collect for large datasets:

```sql
DECLARE
  TYPE t_member_ids IS TABLE OF NUMBER;
  l_member_ids t_member_ids;
BEGIN
  -- Bulk collect
  SELECT member_id
  BULK COLLECT INTO l_member_ids
  FROM   ew_members_v
  WHERE  app_dimension_id = g_app_dimension_id;
  
  -- Bulk DML
  FORALL i IN l_member_ids.FIRST..l_member_ids.LAST
    UPDATE member_props
    SET    prop_value = 'NEW_VALUE'
    WHERE  member_id = l_member_ids(i);
END;
```

### Caching Strategies

Cache frequently accessed data:

```sql
DECLARE
  -- Cache variables
  g_cached_app_id     NUMBER;
  g_cached_dim_id     NUMBER;
  g_cached_prop_ids   ew_global.g_num_tbl;
  
  FUNCTION get_app_id RETURN NUMBER IS
  BEGIN
    IF g_cached_app_id IS NULL THEN
      g_cached_app_id := ew_hierarchy.get_app_id(ew_lb_api.g_app_name);
    END IF;
    RETURN g_cached_app_id;
  END;
```

## Best Practices

### 1. Always Initialize Output Parameters

```sql
BEGIN
  -- Required initialization
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Script-specific initialization
  ew_lb_api.g_out_prop_value := NULL;
  ew_lb_api.g_out_ignore_flag := 'N';
```

### 2. Use Named Parameters

```sql
-- Good: Named parameters
l_result := ew_hierarchy.chk_member_exists(
  p_app_dimension_id => l_dim_id,
  p_member_name      => l_member,
  p_case_match       => 'Y'
);

-- Bad: Positional parameters
l_result := ew_hierarchy.chk_member_exists(l_dim_id, l_member, 'Y');
```

### 3. Document Complex Logic

```sql
/*
 * Calculate consolidation method based on:
 * 1. Account type (Asset/Liability/Equity)
 * 2. Ownership percentage
 * 3. Control type (Full/Partial/Equity)
 * Returns: FULL, PROPORTIONAL, EQUITY, or NONE
 */
FUNCTION calc_consolidation_method(
  p_account_type IN VARCHAR2,
  p_ownership    IN NUMBER,
  p_control      IN VARCHAR2
) RETURN VARCHAR2 IS
```

### 4. Validate Input Early

```sql
BEGIN
  -- Validate required inputs immediately
  IF ew_lb_api.g_member_name IS NULL THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Member name is required';
    RETURN;
  END IF;
  
  -- Continue with main logic...
```

## Common Patterns

### Pattern: Check-Then-Act

```sql
-- Check existence before creating
IF ew_hierarchy.chk_member_exists(
     p_app_dimension_id => l_dim_id,
     p_member_name      => l_new_member
   ) = 'N' THEN
  -- Safe to create
  create_new_member(l_new_member);
ELSE
  -- Handle existing member
  update_existing_member(l_new_member);
END IF;
```

### Pattern: Accumulate Errors

```sql
DECLARE
  l_errors VARCHAR2(4000);
  
  PROCEDURE add_error(p_msg VARCHAR2) IS
  BEGIN
    IF l_errors IS NOT NULL THEN
      l_errors := l_errors || '; ';
    END IF;
    l_errors := l_errors || p_msg;
  END;
BEGIN
  -- Validate multiple conditions
  IF condition1_fails THEN
    add_error('Condition 1 failed');
  END IF;
  
  IF condition2_fails THEN
    add_error('Condition 2 failed');
  END IF;
  
  -- Check accumulated errors
  IF l_errors IS NOT NULL THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := l_errors;
  END IF;
END;
```

## Next Steps

- [Explore specific script types](../events/)
- [Learn API functions](../api/)
- [Review examples](../events/)