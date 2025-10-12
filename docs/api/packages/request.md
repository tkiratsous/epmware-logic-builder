# Request API Functions

The Request API provides functions for creating and managing metadata change requests, request lines, and their properties within EPMware's workflow system.

**Package**: `EW_REQUEST`  
**Usage**: `ew_request.<function_name>`

## Overview

The Request API enables:
- Request creation and management
- Request line operations
- Property updates
- Status management
- Bulk operations
- Request validation

## Core Request Functions

### Create Request

#### create_request

Creates a new request header.

```sql
FUNCTION create_request(
  p_request_name   IN VARCHAR2,
  p_request_type   IN VARCHAR2 DEFAULT 'STANDARD',
  p_description    IN VARCHAR2 DEFAULT NULL,
  p_priority       IN VARCHAR2 DEFAULT 'MEDIUM',
  p_due_date       IN DATE DEFAULT NULL
) RETURN NUMBER; -- Returns request_id
```

**Parameters:**
- `p_request_name` - Name/title of request
- `p_request_type` - Type of request
- `p_description` - Request description
- `p_priority` - Priority (HIGH, MEDIUM, LOW)
- `p_due_date` - Request due date

**Example:**
```sql
DECLARE
  l_request_id NUMBER;
BEGIN
  l_request_id := ew_request.create_request(
    p_request_name => 'Q1 Account Updates',
    p_request_type => 'HIERARCHY_CHANGE',
    p_description  => 'Quarterly account structure updates',
    p_priority     => 'HIGH',
    p_due_date     => SYSDATE + 7
  );
  
  DBMS_OUTPUT.PUT_LINE('Created request: ' || l_request_id);
END;
```

### Get Request Information

#### get_request_status

Returns the current status of a request.

```sql
FUNCTION get_request_status(
  p_request_id IN NUMBER
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_status VARCHAR2(50);
BEGIN
  l_status := ew_request.get_request_status(p_request_id => 12345);
  
  IF l_status = 'APPROVED' THEN
    -- Process approved request
    process_approved_request(12345);
  END IF;
END;
```

#### get_request_info

Returns complete request information.

```sql
FUNCTION get_request_info(
  p_request_id IN NUMBER
) RETURN ew_request.request_rec;
```

**Example:**
```sql
DECLARE
  l_request_info ew_request.request_rec;
BEGIN
  l_request_info := ew_request.get_request_info(p_request_id => 12345);
  
  DBMS_OUTPUT.PUT_LINE('Request: ' || l_request_info.request_name);
  DBMS_OUTPUT.PUT_LINE('Status: ' || l_request_info.status);
  DBMS_OUTPUT.PUT_LINE('Created: ' || l_request_info.created_date);
END;
```

## Request Line Functions

### Create Request Lines

#### create_request_line

Creates a single request line for member operations.

```sql
FUNCTION create_request_line(
  p_request_id       IN NUMBER,
  p_app_dimension_id IN NUMBER,
  p_action_code      IN VARCHAR2,
  p_member_name      IN VARCHAR2,
  p_parent_name      IN VARCHAR2 DEFAULT NULL,
  p_new_name         IN VARCHAR2 DEFAULT NULL
) RETURN NUMBER; -- Returns request_line_id
```

**Parameters:**
- `p_request_id` - Parent request ID
- `p_app_dimension_id` - Application-dimension ID
- `p_action_code` - Action to perform (CMC, REN, DM, etc.)
- `p_member_name` - Member name
- `p_parent_name` - Parent for create/move operations
- `p_new_name` - New name for rename operations

**Example:**
```sql
DECLARE
  l_request_id NUMBER := 12345;
  l_line_id NUMBER;
BEGIN
  -- Create new member
  l_line_id := ew_request.create_request_line(
    p_request_id       => l_request_id,
    p_app_dimension_id => 100,
    p_action_code      => 'CMC',
    p_member_name      => 'NewAccount',
    p_parent_name      => 'TotalRevenue'
  );
  
  -- Rename member
  l_line_id := ew_request.create_request_line(
    p_request_id       => l_request_id,
    p_app_dimension_id => 100,
    p_action_code      => 'REN',
    p_member_name      => 'OldName',
    p_new_name         => 'NewName'
  );
  
  -- Delete member
  l_line_id := ew_request.create_request_line(
    p_request_id       => l_request_id,
    p_app_dimension_id => 100,
    p_action_code      => 'DM',
    p_member_name      => 'ObsoleteAccount'
  );
END;
```

#### create_request_lines_bulk

Creates multiple request lines in a single operation.

```sql
PROCEDURE create_request_lines_bulk(
  p_request_id       IN NUMBER,
  p_app_dimension_id IN NUMBER,
  p_action_codes     IN ew_global.g_value_tbl,
  p_member_names     IN ew_global.g_value_tbl,
  p_parent_names     IN ew_global.g_value_tbl DEFAULT NULL
);
```

**Example:**
```sql
DECLARE
  l_request_id NUMBER := 12345;
  l_actions ew_global.g_value_tbl;
  l_members ew_global.g_value_tbl;
  l_parents ew_global.g_value_tbl;
BEGIN
  -- Prepare arrays
  l_actions(1) := 'CMC'; l_members(1) := 'Account1'; l_parents(1) := 'Parent1';
  l_actions(2) := 'CMC'; l_members(2) := 'Account2'; l_parents(2) := 'Parent1';
  l_actions(3) := 'CMC'; l_members(3) := 'Account3'; l_parents(3) := 'Parent2';
  
  -- Bulk create
  ew_request.create_request_lines_bulk(
    p_request_id       => l_request_id,
    p_app_dimension_id => 100,
    p_action_codes     => l_actions,
    p_member_names     => l_members,
    p_parent_names     => l_parents
  );
END;
```

### Get Request Line Information

#### get_req_line_id

Retrieves request line ID based on criteria.

```sql
FUNCTION get_req_line_id(
  p_request_id         IN NUMBER,
  p_app_dimension_id   IN NUMBER,
  p_member_name        IN VARCHAR2,
  p_action_code        IN VARCHAR2
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_line_id NUMBER;
BEGIN
  l_line_id := ew_request.get_req_line_id(
    p_request_id       => 12345,
    p_app_dimension_id => 100,
    p_member_name      => 'Revenue',
    p_action_code      => 'CMC'
  );
  
  IF l_line_id IS NOT NULL THEN
    -- Update line properties
    update_line_properties(l_line_id);
  END IF;
END;
```

#### get_request_line_status

Returns the status of a specific request line.

```sql
FUNCTION get_request_line_status(
  p_request_line_id IN NUMBER
) RETURN VARCHAR2;
```

## Property Operations

### Add/Update Properties

#### add_property_to_line

Adds or updates a property value for a request line.

```sql
PROCEDURE add_property_to_line(
  p_request_line_id IN NUMBER,
  p_property_name   IN VARCHAR2,
  p_property_value  IN VARCHAR2
);
```

**Example:**
```sql
DECLARE
  l_line_id NUMBER := 54321;
BEGIN
  -- Add account properties
  ew_request.add_property_to_line(
    p_request_line_id => l_line_id,
    p_property_name   => 'ACCOUNT_TYPE',
    p_property_value  => 'REVENUE'
  );
  
  ew_request.add_property_to_line(
    p_request_line_id => l_line_id,
    p_property_name   => 'CONSOLIDATION',
    p_property_value  => '+'
  );
  
  ew_request.add_property_to_line(
    p_request_line_id => l_line_id,
    p_property_name   => 'DATA_STORAGE',
    p_property_value  => 'STORE'
  );
END;
```

#### bulk_update_properties

Updates multiple properties at once.

```sql
PROCEDURE bulk_update_properties(
  p_request_line_id IN NUMBER,
  p_property_names  IN ew_global.g_value_tbl,
  p_property_values IN ew_global.g_value_tbl
);
```

**Example:**
```sql
DECLARE
  l_line_id NUMBER := 54321;
  l_prop_names ew_global.g_value_tbl;
  l_prop_values ew_global.g_value_tbl;
BEGIN
  -- Prepare property arrays
  l_prop_names(1) := 'ACCOUNT_TYPE';    l_prop_values(1) := 'EXPENSE';
  l_prop_names(2) := 'TIME_BALANCE';    l_prop_values(2) := 'FLOW';
  l_prop_names(3) := 'SKIP_VALUE';      l_prop_values(3) := 'MISSING';
  l_prop_names(4) := 'EXCHANGE_RATE';   l_prop_values(4) := 'AVG';
  
  -- Bulk update
  ew_request.bulk_update_properties(
    p_request_line_id => l_line_id,
    p_property_names  => l_prop_names,
    p_property_values => l_prop_values
  );
END;
```

## Request Management

### Submit Request

#### submit_request

Submits a request to workflow for approval.

```sql
PROCEDURE submit_request(
  p_request_id    IN NUMBER,
  p_validate_only IN VARCHAR2 DEFAULT 'N'
);
```

**Example:**
```sql
BEGIN
  -- Validate first
  ew_request.submit_request(
    p_request_id    => 12345,
    p_validate_only => 'Y'
  );
  
  -- If validation passes, submit
  ew_request.submit_request(
    p_request_id    => 12345,
    p_validate_only => 'N'
  );
  
EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Submit failed: ' || SQLERRM);
END;
```

### Cancel Request

#### cancel_request

Cancels a request and all its lines.

```sql
PROCEDURE cancel_request(
  p_request_id IN NUMBER,
  p_reason     IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  ew_request.cancel_request(
    p_request_id => 12345,
    p_reason     => 'Requirements changed'
  );
END;
```

### Clone Request

#### clone_request

Creates a copy of an existing request.

```sql
FUNCTION clone_request(
  p_source_request_id IN NUMBER,
  p_new_request_name  IN VARCHAR2
) RETURN NUMBER; -- Returns new request_id
```

**Example:**
```sql
DECLARE
  l_new_request_id NUMBER;
BEGIN
  l_new_request_id := ew_request.clone_request(
    p_source_request_id => 12345,
    p_new_request_name  => 'Q2 Account Updates (Copy)'
  );
  
  DBMS_OUTPUT.PUT_LINE('Cloned request: ' || l_new_request_id);
END;
```

## Advanced Features

### Request Templates

Create requests from templates:

```sql
DECLARE
  l_request_id NUMBER;
  l_template_name VARCHAR2(100) := 'MONTHLY_ACCOUNT_UPDATES';
BEGIN
  -- Create request from template
  l_request_id := ew_request.create_from_template(
    p_template_name => l_template_name,
    p_request_name  => 'January Account Updates',
    p_parameters    => 'PERIOD=JAN-2025;ENTITY=US_CORP'
  );
  
  -- Template automatically creates standard lines
  DBMS_OUTPUT.PUT_LINE('Created request ' || l_request_id || ' from template');
END;
```

### Batch Request Processing

Process multiple requests together:

```sql
DECLARE
  TYPE t_request_ids IS TABLE OF NUMBER;
  l_requests t_request_ids := t_request_ids(12345, 12346, 12347);
  l_success_count NUMBER := 0;
  l_error_count NUMBER := 0;
BEGIN
  FOR i IN 1..l_requests.COUNT LOOP
    BEGIN
      ew_request.submit_request(p_request_id => l_requests(i));
      l_success_count := l_success_count + 1;
    EXCEPTION
      WHEN OTHERS THEN
        l_error_count := l_error_count + 1;
        log_error('Failed to submit request ' || l_requests(i));
    END;
  END LOOP;
  
  DBMS_OUTPUT.PUT_LINE('Submitted: ' || l_success_count || 
                       ', Failed: ' || l_error_count);
END;
```

### Request Validation

Comprehensive validation before submission:

```sql
DECLARE
  l_request_id NUMBER := 12345;
  l_validation_errors ew_global.g_value_tbl;
BEGIN
  -- Validate request
  l_validation_errors := ew_request.validate_request(p_request_id => l_request_id);
  
  IF l_validation_errors.COUNT > 0 THEN
    DBMS_OUTPUT.PUT_LINE('Validation errors found:');
    FOR i IN 1..l_validation_errors.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE(i || ': ' || l_validation_errors(i));
    END LOOP;
  ELSE
    -- Safe to submit
    ew_request.submit_request(p_request_id => l_request_id);
  END IF;
END;
```

## Request Line Examples

### Complex Hierarchy Changes

```sql
DECLARE
  l_request_id NUMBER;
  l_line_id NUMBER;
BEGIN
  -- Create request
  l_request_id := ew_request.create_request(
    p_request_name => 'Restructure Operating Expenses'
  );
  
  -- Move existing members
  l_line_id := ew_request.create_request_line(
    p_request_id       => l_request_id,
    p_app_dimension_id => 100,
    p_action_code      => 'ZC',  -- Move as child
    p_member_name      => 'Marketing',
    p_parent_name      => 'Sales_Marketing'
  );
  
  -- Create new parent
  l_line_id := ew_request.create_request_line(
    p_request_id       => l_request_id,
    p_app_dimension_id => 100,
    p_action_code      => 'CMC',
    p_member_name      => 'Sales_Marketing',
    p_parent_name      => 'Operating_Expenses'
  );
  
  -- Create shared member
  l_line_id := ew_request.create_request_line(
    p_request_id       => l_request_id,
    p_app_dimension_id => 100,
    p_action_code      => 'ISMC',  -- Insert shared member
    p_member_name      => 'Marketing',
    p_parent_name      => 'Total_Marketing'
  );
  
  -- Submit for approval
  ew_request.submit_request(p_request_id => l_request_id);
END;
```

### Property Updates with Validation

```sql
DECLARE
  l_request_id NUMBER;
  l_line_id NUMBER;
  l_valid VARCHAR2(1);
BEGIN
  -- Create request for property updates
  l_request_id := ew_request.create_request(
    p_request_name => 'Update Account Properties'
  );
  
  -- For each account needing update
  FOR rec IN (SELECT member_name FROM accounts_to_update) LOOP
    -- Create update line
    l_line_id := ew_request.create_request_line(
      p_request_id       => l_request_id,
      p_app_dimension_id => 100,
      p_action_code      => 'UPD',  -- Update
      p_member_name      => rec.member_name
    );
    
    -- Validate and add properties
    l_valid := validate_account_type(rec.member_name);
    
    IF l_valid = 'Y' THEN
      ew_request.add_property_to_line(
        p_request_line_id => l_line_id,
        p_property_name   => 'ACCOUNT_TYPE',
        p_property_value  => get_account_type(rec.member_name)
      );
    ELSE
      -- Mark line with error
      ew_request.update_line_status(
        p_request_line_id => l_line_id,
        p_status          => 'ERROR',
        p_error_message   => 'Invalid account type'
      );
    END IF;
  END LOOP;
END;
```

## Error Handling

### Request Creation Errors

```sql
BEGIN
  l_request_id := ew_request.create_request(
    p_request_name => 'Test Request'
  );
EXCEPTION
  WHEN ew_request.duplicate_request THEN
    -- Handle duplicate name
    l_request_id := ew_request.create_request(
      p_request_name => 'Test Request ' || TO_CHAR(SYSDATE, 'YYYYMMDD_HH24MISS')
    );
  WHEN OTHERS THEN
    log_error('Request creation failed: ' || SQLERRM);
    RAISE;
END;
```

### Line Creation Errors

```sql
BEGIN
  l_line_id := ew_request.create_request_line(...);
EXCEPTION
  WHEN ew_request.invalid_action_code THEN
    DBMS_OUTPUT.PUT_LINE('Invalid action code specified');
  WHEN ew_request.member_not_found THEN
    DBMS_OUTPUT.PUT_LINE('Member does not exist');
  WHEN ew_request.duplicate_line THEN
    DBMS_OUTPUT.PUT_LINE('Line already exists for this member/action');
END;
```

## Performance Optimization

### Bulk Operations

```sql
-- Use bulk operations for better performance
DECLARE
  TYPE t_members IS TABLE OF VARCHAR2(255);
  l_members t_members;
BEGIN
  -- Collect members to process
  SELECT member_name
    BULK COLLECT INTO l_members
    FROM source_table
   WHERE process_flag = 'Y';
  
  -- Process in bulk
  ew_request.create_lines_for_members(
    p_request_id => l_request_id,
    p_members    => l_members,
    p_action     => 'CMC'
  );
END;
```

### Request Caching

```sql
-- Cache request info for repeated access
DECLARE
  g_request_cache ew_request.request_rec;
  
  FUNCTION get_cached_request(p_request_id NUMBER) 
  RETURN ew_request.request_rec IS
  BEGIN
    IF g_request_cache.request_id != p_request_id THEN
      g_request_cache := ew_request.get_request_info(p_request_id);
    END IF;
    RETURN g_request_cache;
  END;
BEGIN
  -- Use cached info
  FOR i IN 1..100 LOOP
    l_request := get_cached_request(12345);
    -- Process using cached data
  END LOOP;
END;
```

## Best Practices

1. **Validate Before Submission**
   ```sql
   IF ew_request.validate_request(l_request_id) = 'Y' THEN
     ew_request.submit_request(l_request_id);
   END IF;
   ```

2. **Use Meaningful Names**
   ```sql
   p_request_name => 'Q1-2025 Account Restructure - Finance'
   ```

3. **Handle All Action Codes**
   ```sql
   CASE p_action_code
     WHEN 'CMC' THEN create_child();
     WHEN 'CMS' THEN create_sibling();
     WHEN 'REN' THEN rename_member();
     ELSE raise_application_error(-20001, 'Unknown action');
   END CASE;
   ```

4. **Clean Up Failed Requests**
   ```sql
   IF request_failed THEN
     ew_request.cancel_request(l_request_id, 'Process failed');
   END IF;
   ```

## Next Steps

- [Workflow APIs](workflow.md)
- [Hierarchy APIs](hierarchy.md)
- [Email APIs](email.md)