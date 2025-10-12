# API Reference

The Logic Builder API provides comprehensive functions for interacting with EPMware metadata, managing workflows, and automating processes. This reference covers all available database views, packages, and functions.

## API Categories

### Database Views
Read-only views providing access to EPMware metadata:
- **[Core Views](database-views/core-views.md)** - Application, dimension, and member views
- **[Request Views](database-views/request-views.md)** - Request and workflow views

### Package APIs
Functional APIs organized by domain:

#### Data Management
- **[In Memory Functions](packages/in-memory.md)** - Session-specific data management
- **[Hierarchy APIs](packages/hierarchy.md)** - Member and hierarchy operations
- **[Statistics APIs](packages/statistics.md)** - Hierarchy statistics and calculations

#### Process Automation
- **[Request APIs](packages/request.md)** - Request line and member operations
- **[Workflow APIs](packages/workflow.md)** - Workflow stage and task management
- **[Agent APIs](packages/agent.md)** - Job submission and deployment

#### Communication & Integration
- **[Email APIs](packages/email.md)** - Email notification functions
- **[Export APIs](packages/export.md)** - Export file operations
- **[Application APIs](packages/application.md)** - Application management

#### Utilities
- **[String APIs](packages/string.md)** - String manipulation utilities
- **[Lookup APIs](packages/lookup.md)** - Lookup value functions
- **[Security APIs](packages/security.md)** - Security and access control

## API Usage Guidelines

### General Principles

1. **Always Check Return Values**
   ```sql
   l_result := ew_hierarchy.chk_member_exists(...);
   IF l_result = 'Y' THEN
     -- Member exists, proceed
   END IF;
   ```

2. **Use Named Parameters**
   ```sql
   -- Good: Clear and maintainable
   ew_email.send_email(
     p_to      => 'user@company.com',
     p_subject => 'Notification',
     p_body    => 'Message content'
   );
   ```

3. **Handle Exceptions**
   ```sql
   BEGIN
     l_value := ew_hierarchy.get_member_prop_value(...);
   EXCEPTION
     WHEN NO_DATA_FOUND THEN
       l_value := 'DEFAULT';
   END;
   ```

### Performance Best Practices

1. **Cache Frequently Used Data**
   ```sql
   -- Store in package variable for session
   IF g_app_id IS NULL THEN
     g_app_id := ew_application.get_app_id(p_app_name => 'HFM_PROD');
   END IF;
   ```

2. **Use Bulk Operations**
   ```sql
   -- Process multiple members at once
   FORALL i IN 1..l_member_array.COUNT
     INSERT INTO temp_members VALUES l_member_array(i);
   ```

3. **Minimize Database Calls**
   ```sql
   -- Get multiple values in one call
   SELECT member_id, member_name, parent_name
     INTO l_id, l_name, l_parent
     FROM ew_members_v
    WHERE ...
   ```

## Common API Patterns

### Pattern 1: Check Before Action

```sql
-- Always verify before performing operations
IF ew_hierarchy.chk_member_exists(
     p_app_dimension_id => l_dim_id,
     p_member_name      => l_new_member
   ) = 'N' THEN
  -- Safe to create member
  create_member(l_new_member);
ELSE
  -- Member exists, update instead
  update_member(l_new_member);
END IF;
```

### Pattern 2: Get or Default

```sql
-- Provide defaults for missing values
FUNCTION get_property_with_default(
  p_member_name VARCHAR2,
  p_prop_name   VARCHAR2,
  p_default     VARCHAR2
) RETURN VARCHAR2 IS
  l_value VARCHAR2(255);
BEGIN
  l_value := ew_hierarchy.get_member_prop_value(
    p_app_name    => g_app_name,
    p_dim_name    => g_dim_name,
    p_member_name => p_member_name,
    p_prop_label  => p_prop_name
  );
  RETURN NVL(l_value, p_default);
END;
```

### Pattern 3: Batch Processing

```sql
-- Process in chunks for better performance
DECLARE
  CURSOR c_members IS
    SELECT member_id, member_name
      FROM ew_members_v
     WHERE dimension_name = 'Account';
  
  TYPE t_member_array IS TABLE OF c_members%ROWTYPE;
  l_members t_member_array;
  l_batch_size CONSTANT NUMBER := 1000;
BEGIN
  OPEN c_members;
  LOOP
    FETCH c_members BULK COLLECT INTO l_members LIMIT l_batch_size;
    EXIT WHEN l_members.COUNT = 0;
    
    -- Process batch
    process_member_batch(l_members);
    COMMIT;
  END LOOP;
  CLOSE c_members;
END;
```

## API Security

### Access Control

All APIs respect EPMware security:
- User must have appropriate module access
- Dimension/application security is enforced
- Row-level security applies to views

### Sensitive Operations

Some APIs require elevated privileges:
- `ew_security.*` - Security administration
- `ew_agent.exec_direct_deploy` - Direct deployment
- `ew_export.delete_export` - Export deletion

## Error Handling

### Standard Error Codes

| Code | Description | Action |
|------|-------------|--------|
| -20001 | Invalid parameters | Check input values |
| -20002 | Access denied | Verify security access |
| -20003 | Object not found | Confirm object exists |
| -20004 | Duplicate object | Use update instead of create |
| -20005 | Operation failed | Check logs for details |

### Error Handling Example

```sql
DECLARE
  l_error_code NUMBER;
  l_error_msg  VARCHAR2(4000);
BEGIN
  -- API call
  ew_request.create_request_line(...);
  
EXCEPTION
  WHEN OTHERS THEN
    l_error_code := SQLCODE;
    l_error_msg  := SQLERRM;
    
    -- Log error
    ew_debug.log('API Error: ' || l_error_code || ' - ' || l_error_msg);
    
    -- Handle specific errors
    CASE l_error_code
      WHEN -20001 THEN
        handle_invalid_params();
      WHEN -20002 THEN
        handle_access_denied();
      ELSE
        handle_general_error();
    END CASE;
END;
```

## API Versioning

### Current Version
- API Version: 2.9
- Database Package Version: 2.9.0
- Compatibility: EPMware 2.8+

### Deprecated APIs

The following APIs are deprecated and will be removed in future versions:

| Deprecated API | Replacement | Removal Version |
|----------------|-------------|-----------------|
| `get_member_by_id` | `get_member_name` | 3.0 |
| `check_member` | `chk_member_exists` | 3.0 |
| `send_notification` | `send_email` | 3.0 |

## Troubleshooting

### Common Issues

1. **API Not Found**
   - Verify package exists: `SELECT * FROM user_objects WHERE object_name = 'EW_HIERARCHY'`
   - Check grants: `SELECT * FROM user_tab_privs WHERE table_name = 'EW_HIERARCHY'`

2. **Performance Issues**
   - Enable SQL trace
   - Check execution plans
   - Review index usage

3. **Unexpected Results**
   - Verify input parameters
   - Check data state
   - Review debug logs

### Debug Logging

Enable detailed logging for troubleshooting:

```sql
-- Enable debug mode
ew_debug.set_debug_level(p_level => 'DETAILED');

-- Your API calls here
...

-- View debug messages
SELECT *
  FROM debug_messages
 WHERE source_ref = 'YOUR_SCRIPT'
 ORDER BY created_date DESC;
```

## Support Resources

- **Technical Documentation**: Internal Wiki
- **API Support**: api-support@company.com
- **Bug Reports**: Create ticket in JIRA
- **Enhancement Requests**: Submit through portal

## Next Steps

Explore specific API categories:

- [Database Views](database-views/)
- [Package APIs](packages/)
- [Code Examples](../events/)