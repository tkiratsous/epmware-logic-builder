# Security API Functions

The Security API provides functions for managing user access, security groups, permissions, and authentication within EPMware.

**Package**: `EW_SECURITY`  
**Usage**: `ew_security.<function_name>`

## Overview

The Security API enables:
- User authentication and authorization
- Security group management
- Permission checking
- Access control
- Audit trail
- Session management

## User Management

### get_user_info

Returns user information.

```sql
FUNCTION get_user_info(
  p_user_name IN VARCHAR2 DEFAULT USER
) RETURN user_info_rec;
```

**Record Structure:**
```sql
TYPE user_info_rec IS RECORD (
  user_id         NUMBER,
  user_name       VARCHAR2(100),
  full_name       VARCHAR2(255),
  email          VARCHAR2(255),
  status         VARCHAR2(20),
  last_login     DATE,
  created_date   DATE
);
```

**Example:**
```sql
DECLARE
  l_user_info ew_security.user_info_rec;
BEGIN
  l_user_info := ew_security.get_user_info(p_user_name => 'JSMITH');
  
  DBMS_OUTPUT.PUT_LINE('User: ' || l_user_info.full_name);
  DBMS_OUTPUT.PUT_LINE('Email: ' || l_user_info.email);
  DBMS_OUTPUT.PUT_LINE('Last Login: ' || l_user_info.last_login);
END;
```

### user_exists

Checks if a user exists.

```sql
FUNCTION user_exists(
  p_user_name IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### is_user_active

Checks if a user account is active.

```sql
FUNCTION is_user_active(
  p_user_name IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

## Permission Checking

### has_permission

Checks if user has specific permission.

```sql
FUNCTION has_permission(
  p_user_name  IN VARCHAR2,
  p_permission IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
BEGIN
  IF ew_security.has_permission(USER, 'LOGIC_BUILDER_WRITE') = 'Y' THEN
    -- User can create/modify scripts
    create_logic_script();
  ELSE
    DBMS_OUTPUT.PUT_LINE('Insufficient permissions');
  END IF;
END;
```

### has_module_access

Checks if user has access to a module.

```sql
FUNCTION has_module_access(
  p_user_name   IN VARCHAR2,
  p_module_name IN VARCHAR2,
  p_access_type IN VARCHAR2 DEFAULT 'READ'  -- 'READ' or 'WRITE'
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
IF ew_security.has_module_access(
     p_user_name   => USER,
     p_module_name => 'LOGIC_BUILDER',
     p_access_type => 'WRITE'
   ) = 'Y' THEN
  -- User has write access to Logic Builder
  enable_script_editing();
END IF;
```

### has_app_access

Checks if user has access to an application.

```sql
FUNCTION has_app_access(
  p_user_name IN VARCHAR2,
  p_app_name  IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### has_dimension_access

Checks if user has access to a dimension.

```sql
FUNCTION has_dimension_access(
  p_user_name     IN VARCHAR2,
  p_app_name      IN VARCHAR2,
  p_dimension_name IN VARCHAR2,
  p_access_type   IN VARCHAR2 DEFAULT 'READ'
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

## Security Group Management

### get_user_groups

Returns security groups for a user.

```sql
FUNCTION get_user_groups(
  p_user_name IN VARCHAR2
) RETURN group_list_tbl;
```

**Example:**
```sql
DECLARE
  l_groups ew_security.group_list_tbl;
BEGIN
  l_groups := ew_security.get_user_groups(p_user_name => USER);
  
  DBMS_OUTPUT.PUT_LINE('User belongs to groups:');
  FOR i IN 1..l_groups.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('  - ' || l_groups(i).group_name || 
                         ' (' || l_groups(i).group_type || ')');
  END LOOP;
END;
```

### is_member_of_group

Checks if user is member of a group.

```sql
FUNCTION is_member_of_group(
  p_user_name  IN VARCHAR2,
  p_group_name IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### add_user_to_group

Adds user to a security group.

```sql
PROCEDURE add_user_to_group(
  p_user_name  IN VARCHAR2,
  p_group_name IN VARCHAR2
);
```

### remove_user_from_group

Removes user from a security group.

```sql
PROCEDURE remove_user_from_group(
  p_user_name  IN VARCHAR2,
  p_group_name IN VARCHAR2
);
```

## Role Management

### get_user_roles

Returns roles assigned to a user.

```sql
FUNCTION get_user_roles(
  p_user_name IN VARCHAR2
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_roles ew_global.g_value_tbl;
BEGIN
  l_roles := ew_security.get_user_roles(p_user_name => USER);
  
  FOR i IN 1..l_roles.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('Role: ' || l_roles(i));
  END LOOP;
END;
```

### has_role

Checks if user has a specific role.

```sql
FUNCTION has_role(
  p_user_name IN VARCHAR2,
  p_role_name IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### grant_role

Grants a role to a user.

```sql
PROCEDURE grant_role(
  p_user_name IN VARCHAR2,
  p_role_name IN VARCHAR2
);
```

## Session Management

### get_session_info

Returns current session information.

```sql
FUNCTION get_session_info
RETURN session_info_rec;
```

**Record Structure:**
```sql
TYPE session_info_rec IS RECORD (
  session_id      NUMBER,
  user_name       VARCHAR2(100),
  login_time      DATE,
  ip_address      VARCHAR2(50),
  client_info     VARCHAR2(255)
);
```

### validate_session

Validates current session.

```sql
FUNCTION validate_session
RETURN VARCHAR2;  -- Returns 'Y' if valid
```

### terminate_session

Terminates a user session.

```sql
PROCEDURE terminate_session(
  p_session_id IN NUMBER DEFAULT NULL
);
```

## Access Control Lists (ACL)

### check_acl

Checks ACL permissions for an object.

```sql
FUNCTION check_acl(
  p_user_name   IN VARCHAR2,
  p_object_type IN VARCHAR2,
  p_object_id   IN NUMBER,
  p_permission  IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
-- Check if user can modify a specific request
IF ew_security.check_acl(
     p_user_name   => USER,
     p_object_type => 'REQUEST',
     p_object_id   => 12345,
     p_permission  => 'MODIFY'
   ) = 'Y' THEN
  update_request(12345);
END IF;
```

### grant_acl_permission

Grants ACL permission on an object.

```sql
PROCEDURE grant_acl_permission(
  p_user_name   IN VARCHAR2,
  p_object_type IN VARCHAR2,
  p_object_id   IN NUMBER,
  p_permission  IN VARCHAR2
);
```

### revoke_acl_permission

Revokes ACL permission on an object.

```sql
PROCEDURE revoke_acl_permission(
  p_user_name   IN VARCHAR2,
  p_object_type IN VARCHAR2,
  p_object_id   IN NUMBER,
  p_permission  IN VARCHAR2
);
```

## Audit Functions

### audit_access

Records access audit entry.

```sql
PROCEDURE audit_access(
  p_user_name   IN VARCHAR2,
  p_object_type IN VARCHAR2,
  p_object_id   IN NUMBER,
  p_action      IN VARCHAR2,
  p_result      IN VARCHAR2,
  p_details     IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  -- Audit script execution
  ew_security.audit_access(
    p_user_name   => USER,
    p_object_type => 'LOGIC_SCRIPT',
    p_object_id   => 100,
    p_action      => 'EXECUTE',
    p_result      => 'SUCCESS',
    p_details     => 'Script completed in 2.5 seconds'
  );
END;
```

### get_audit_trail

Retrieves audit trail for an object.

```sql
FUNCTION get_audit_trail(
  p_object_type IN VARCHAR2,
  p_object_id   IN NUMBER,
  p_start_date  IN DATE DEFAULT NULL,
  p_end_date    IN DATE DEFAULT NULL
) RETURN audit_trail_tbl;
```

## Advanced Security Features

### Password Management

```sql
-- Validate password strength
FUNCTION validate_password(
  p_password IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' if valid

-- Change user password
PROCEDURE change_password(
  p_user_name     IN VARCHAR2,
  p_old_password  IN VARCHAR2,
  p_new_password  IN VARCHAR2
);

-- Reset password
PROCEDURE reset_password(
  p_user_name IN VARCHAR2
);

-- Check password expiry
FUNCTION is_password_expired(
  p_user_name IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### Data Security

```sql
-- Apply row-level security
FUNCTION apply_row_security(
  p_user_name IN VARCHAR2,
  p_query     IN VARCHAR2
) RETURN VARCHAR2;  -- Returns modified query with security filters

-- Mask sensitive data
FUNCTION mask_sensitive_data(
  p_data      IN VARCHAR2,
  p_data_type IN VARCHAR2
) RETURN VARCHAR2;
```

### Security Configuration

```sql
-- Get security configuration
FUNCTION get_security_config(
  p_param_name IN VARCHAR2
) RETURN VARCHAR2;

-- Set security configuration
PROCEDURE set_security_config(
  p_param_name  IN VARCHAR2,
  p_param_value IN VARCHAR2
);
```

## Security Validation

### Complete Security Check

```sql
DECLARE
  l_access_granted BOOLEAN := TRUE;
  l_message VARCHAR2(4000);
BEGIN
  -- Check multiple security levels
  
  -- 1. User active?
  IF ew_security.is_user_active(USER) != 'Y' THEN
    l_access_granted := FALSE;
    l_message := 'User account inactive';
  END IF;
  
  -- 2. Module access?
  IF l_access_granted AND 
     ew_security.has_module_access(USER, 'LOGIC_BUILDER', 'WRITE') != 'Y' THEN
    l_access_granted := FALSE;
    l_message := 'No Logic Builder write access';
  END IF;
  
  -- 3. Application access?
  IF l_access_granted AND 
     ew_security.has_app_access(USER, 'HFM_PROD') != 'Y' THEN
    l_access_granted := FALSE;
    l_message := 'No application access';
  END IF;
  
  -- 4. Valid session?
  IF l_access_granted AND 
     ew_security.validate_session() != 'Y' THEN
    l_access_granted := FALSE;
    l_message := 'Invalid session';
  END IF;
  
  IF l_access_granted THEN
    -- Proceed with operation
    perform_secured_operation();
  ELSE
    RAISE_APPLICATION_ERROR(-20002, 'Access Denied: ' || l_message);
  END IF;
END;
```

## Error Handling

```sql
BEGIN
  ew_security.add_user_to_group('JSMITH', 'ADMIN');
EXCEPTION
  WHEN ew_security.user_not_found THEN
    DBMS_OUTPUT.PUT_LINE('User does not exist');
  WHEN ew_security.group_not_found THEN
    DBMS_OUTPUT.PUT_LINE('Security group does not exist');
  WHEN ew_security.insufficient_privilege THEN
    DBMS_OUTPUT.PUT_LINE('Insufficient privileges for this operation');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Security error: ' || SQLERRM);
END;
```

## Best Practices

1. **Always Check Permissions**
   ```sql
   IF ew_security.has_permission(USER, 'DELETE_MEMBER') = 'Y' THEN
     -- Proceed with deletion
   END IF;
   ```

2. **Audit Sensitive Operations**
   ```sql
   ew_security.audit_access(
     p_user_name   => USER,
     p_object_type => 'CRITICAL_DATA',
     p_action      => 'DELETE'
   );
   ```

3. **Validate Sessions**
   ```sql
   IF ew_security.validate_session() != 'Y' THEN
     -- Re-authenticate user
   END IF;
   ```

4. **Use Appropriate Security Level**
   ```sql
   -- Check at appropriate granularity
   has_app_access() -- Application level
   has_dimension_access() -- Dimension level
   check_acl() -- Object level
   ```

## Next Steps

- [Export APIs](export.md)
- [Agent APIs](agent.md)
- [Application APIs](application.md)