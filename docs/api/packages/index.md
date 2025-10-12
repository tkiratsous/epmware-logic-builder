# Package APIs

EPMware Logic Builder provides comprehensive PL/SQL packages for programmatic interaction with the system. These packages offer functions for data management, workflow automation, and system integration.

## Package Categories

### Core Data Management
- **[In Memory Functions](in-memory.md)** - Session-specific temporary data storage
- **[Hierarchy APIs](hierarchy.md)** - Member and hierarchy manipulation functions
- **[Statistics APIs](statistics.md)** - Hierarchy statistics and calculations

### Request and Workflow
- **[Request APIs](request.md)** - Request line creation and management
- **[Workflow APIs](workflow.md)** - Workflow stage and task control
- **[Agent APIs](agent.md)** - Job submission and deployment execution

### Integration and Communication
- **[Email APIs](email.md)** - Email notification and distribution
- **[Export APIs](export.md)** - Export file generation and management
- **[Application APIs](application.md)** - Application-level operations

### Utilities and Security
- **[String APIs](string.md)** - String manipulation and formatting
- **[Lookup APIs](lookup.md)** - Lookup value management
- **[Security APIs](security.md)** - User and group security functions

## Package Naming Convention

All EPMware packages follow the naming pattern:

| Prefix | Description | Example |
|--------|-------------|---------|
| `EW_` | EPMware standard package | `EW_HIERARCHY` |
| `EW_LB_` | Logic Builder specific | `EW_LB_API` |
| `EW_UTIL_` | Utility packages | `EW_UTIL_STRING` |

## Common Package Components

### Standard Functions

Most packages include these standard functions:

```sql
-- Check existence
FUNCTION chk_<object>_exists(parameters) RETURN VARCHAR2;

-- Get identifier
FUNCTION get_<object>_id(parameters) RETURN NUMBER;

-- Get name/value
FUNCTION get_<object>_name(parameters) RETURN VARCHAR2;

-- Create/Update/Delete
PROCEDURE create_<object>(parameters);
PROCEDURE update_<object>(parameters);
PROCEDURE delete_<object>(parameters);
```

### Return Value Conventions

| Return Value | Meaning |
|--------------|---------|
| `'Y'` | Yes/True/Exists |
| `'N'` | No/False/Not exists |
| `'S'` | Success |
| `'E'` | Error |
| `NULL` | Not found/No value |

### Error Handling

Standard error codes across packages:

```sql
-- Standard exceptions
e_invalid_parameter EXCEPTION;
PRAGMA EXCEPTION_INIT(e_invalid_parameter, -20001);

e_access_denied EXCEPTION;
PRAGMA EXCEPTION_INIT(e_access_denied, -20002);

e_object_not_found EXCEPTION;
PRAGMA EXCEPTION_INIT(e_object_not_found, -20003);
```

## Package Dependencies

### Dependency Hierarchy

```
EW_LB_API (Global Logic Builder API)
    ├── EW_HIERARCHY (Member operations)
    ├── EW_REQUEST (Request management)
    ├── EW_WORKFLOW (Workflow control)
    ├── EW_EMAIL (Notifications)
    ├── EW_SECURITY (Access control)
    └── EW_UTIL_* (Utilities)
```

### Common Dependencies

```sql
-- Most scripts will use these packages
DECLARE
  -- Core APIs
  l_member_exists VARCHAR2(1);
  l_request_id NUMBER;
  
BEGIN
  -- Check member existence
  l_member_exists := ew_hierarchy.chk_member_exists(...);
  
  -- Create request
  l_request_id := ew_request.create_request(...);
  
  -- Send notification
  ew_email.send_email(...);
END;
```

## Package Execution Context

### Session Variables

Packages maintain session-level variables:

```sql
-- Available throughout session
ew_lb_api.g_request_id     -- Current request
ew_lb_api.g_user_id        -- Current user
ew_lb_api.g_app_name       -- Current application
ew_lb_api.g_status         -- Operation status
ew_lb_api.g_message        -- Status message
```

### Transaction Management

```sql
-- Packages handle transactions appropriately
BEGIN
  -- Start transaction
  ew_request.create_request_line(...);
  ew_request.create_request_line(...);
  
  -- Commit handled by package
  ew_request.submit_request(...);
  
EXCEPTION
  WHEN OTHERS THEN
    -- Rollback on error
    ROLLBACK;
    RAISE;
END;
```

## Performance Considerations

### Package State

```sql
-- Packages maintain state during session
-- First call initializes
ew_hierarchy.init_session(p_app_id => 100);

-- Subsequent calls use cached data
FOR i IN 1..1000 LOOP
  -- Uses cached app_id
  l_exists := ew_hierarchy.chk_member_exists(...);
END LOOP;
```

### Bulk Operations

```sql
-- Many packages support bulk operations
DECLARE
  TYPE t_member_array IS TABLE OF VARCHAR2(255);
  l_members t_member_array := t_member_array('M1', 'M2', 'M3');
BEGIN
  -- Bulk create
  ew_hierarchy.create_members_bulk(
    p_members => l_members,
    p_parent  => 'Parent1'
  );
END;
```

## Security Model

### Package Privileges

```sql
-- Check package access
SELECT privilege
  FROM user_tab_privs
 WHERE table_name = 'EW_HIERARCHY'
   AND type = 'PACKAGE';

-- Grant execution
GRANT EXECUTE ON ew_hierarchy TO logic_builder_user;
```

### Security Enforcement

All packages enforce security:
- User authentication required
- Application/dimension access checked
- Row-level security applied
- Audit trail maintained

## Debugging Package Calls

### Enable Debug Mode

```sql
-- Enable detailed logging
BEGIN
  ew_debug.set_debug_level('DETAILED');
  ew_debug.set_debug_user(USER);
END;
```

### Trace Package Execution

```sql
-- Trace specific package
BEGIN
  -- Enable trace
  EXECUTE IMMEDIATE 'ALTER SESSION SET SQL_TRACE = TRUE';
  
  -- Your package calls
  ew_hierarchy.get_member_name(...);
  
  -- Disable trace
  EXECUTE IMMEDIATE 'ALTER SESSION SET SQL_TRACE = FALSE';
END;
```

### View Debug Output

```sql
-- Check debug messages
SELECT timestamp,
       source_ref,
       message_text
  FROM debug_messages
 WHERE user_name = USER
   AND timestamp > SYSDATE - 1/24
 ORDER BY timestamp DESC;
```

## Package Versioning

### Version Information

```sql
-- Get package version
SELECT ew_util.get_package_version('EW_HIERARCHY') FROM dual;

-- Check compatibility
SELECT CASE 
  WHEN ew_util.check_compatibility('2.9') = 'Y' 
  THEN 'Compatible'
  ELSE 'Incompatible'
END AS compatibility
FROM dual;
```

## Best Practices

1. **Use Package Constants**
   ```sql
   -- Use package constants
   ew_lb_api.g_status := ew_lb_api.g_success;
   -- Not hard-coded values
   ew_lb_api.g_status := 'S';
   ```

2. **Check Return Values**
   ```sql
   IF ew_hierarchy.chk_member_exists(...) = 'Y' THEN
     -- Proceed only if exists
   END IF;
   ```

3. **Handle Exceptions**
   ```sql
   BEGIN
     ew_request.submit_request(...);
   EXCEPTION
     WHEN OTHERS THEN
       log_error(SQLERRM);
       RAISE;
   END;
   ```

4. **Use Appropriate APIs**
   ```sql
   -- Use specialized function
   l_parent := ew_hierarchy.get_primary_parent_name(...);
   -- Not generic query
   SELECT parent_name INTO l_parent FROM ...
   ```

5. **Cache When Possible**
   ```sql
   -- Cache frequently used values
   IF g_app_id IS NULL THEN
     g_app_id := ew_application.get_app_id('HFM_PROD');
   END IF;
   ```

## Common Integration Patterns

### Pattern 1: Create and Submit Request

```sql
DECLARE
  l_request_id NUMBER;
  l_line_id NUMBER;
BEGIN
  -- Create request
  l_request_id := ew_request.create_request(
    p_name => 'Monthly Update',
    p_type => 'HIERARCHY_CHANGE'
  );
  
  -- Add lines
  l_line_id := ew_request.create_request_line(
    p_request_id => l_request_id,
    p_action     => 'CREATE_MEMBER',
    p_member     => 'NewAccount'
  );
  
  -- Submit for approval
  ew_workflow.submit_request(l_request_id);
END;
```

### Pattern 2: Query and Update

```sql
DECLARE
  l_member_id NUMBER;
  l_current_value VARCHAR2(255);
BEGIN
  -- Get member info
  l_member_id := ew_hierarchy.get_member_id(
    p_app_dimension_id => 100,
    p_member_name      => 'Account123'
  );
  
  -- Get current property
  l_current_value := ew_hierarchy.get_member_prop_value(
    p_member_id  => l_member_id,
    p_prop_label => 'ACCOUNT_TYPE'
  );
  
  -- Update if needed
  IF l_current_value IS NULL THEN
    ew_hierarchy.update_member_property(
      p_member_id   => l_member_id,
      p_prop_label  => 'ACCOUNT_TYPE',
      p_prop_value  => 'EXPENSE'
    );
  END IF;
END;
```

## Troubleshooting

### Common Issues

1. **Package Not Found**
   - Check spelling and case
   - Verify EXECUTE privilege
   - Confirm package installed

2. **Invalid Identifier**
   - Check function name
   - Verify parameter names
   - Review package specification

3. **No Data Found**
   - Handle NULL returns
   - Check object existence first
   - Verify access permissions

## Next Steps

Explore specific package documentation:

- [In Memory Functions](in-memory.md)
- [Hierarchy APIs](hierarchy.md)
- [Request APIs](request.md)
- [Email APIs](email.md)