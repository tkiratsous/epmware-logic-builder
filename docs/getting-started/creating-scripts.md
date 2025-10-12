# Creating Logic Builder Scripts

This guide walks through the process of creating new Logic Scripts in EPMware, from initial creation to testing and deployment.

## Accessing Logic Builder

Navigate to the Logic Builder module through the Configuration menu:

![Logic Builder Menu Access](../assets/images/logic-builder-menu-access.png)
*Figure: Accessing Logic Builder from the Configuration menu*

## Creating a New Script

### Step 1: Open New Script Dialog

Click the plus sign (➕) in the Scripts menu to create a new Logic Script:

![Create New Script Button](../assets/images/create-script-button.png)
*Figure: Plus icon for creating new scripts*

### Step 2: Configure Script Properties

Enter the following information in the script creation dialog:

![Script Properties Dialog](../assets/images/script-properties-dialog.png)
*Figure: New Script configuration dialog*

#### Required Fields

1. **Script Name** (Required)
   - Maximum 50 characters
   - Must be unique across all script types
   - Use meaningful prefixes (avoid `EW_` which is reserved for EPMware standard scripts)
   - Example: `CUST_VALIDATE_ACCOUNT_FORMAT`

2. **Script Type** (Required)
   - Select from dropdown list
   - Determines when and how the script executes
   - Cannot be changed after creation

3. **Enabled** (Required)
   - Check to activate the script
   - Disabled scripts won't execute even if configured

#### Optional Fields

4. **Description**
   - Provide meaningful description of script purpose
   - Include author and creation date for documentation

5. **DB Function Name** (On-Premise Only)
   - Reference to stored database procedure
   - Format: `PACKAGE_NAME.PROCEDURE_NAME` or `PROCEDURE_NAME`
   - When populated, Script Editor is disabled

!!! warning "Cloud Deployment Restriction"
    The DB Function Name option is **not available** for cloud deployments. All logic must be implemented in the Script Editor.

## Script Editor Interface

Once the script is created, the Script Editor opens:

![Script Editor Interface](../assets/images/script-editor-interface.png)
*Figure: Logic Builder Script Editor with syntax highlighting*

### Editor Features

- **Syntax Highlighting** - PL/SQL keywords, strings, and comments
- **Line Numbers** - For easy reference and debugging
- **Auto-Indentation** - Maintains code structure
- **Find/Replace** - Standard text search functionality
- **Validation** - Automatic syntax check on save

## Writing Your First Script

### Basic Script Structure

Every Logic Script follows this basic structure:

```sql
DECLARE
  -- Constants and Variables
  c_script_name VARCHAR2(100) := 'YOUR_SCRIPT_NAME';
  
  -- Local procedures
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  -- Initialize return status
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Your logic here
  log('Script execution started');
  
  -- Implement your business logic
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error: ' || SQLERRM;
    log('Exception occurred: ' || SQLERRM);
END;
```

### Example: Simple Property Validation

Here's a complete example that validates email format:

```sql
/* 
  Author: Your Name
  Date: Current Date
  Purpose: Validate email address format
*/
DECLARE
  c_script_name VARCHAR2(100) := 'VALIDATE_EMAIL_FORMAT';
  c_email_pattern VARCHAR2(200) := '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  -- Set default success status
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Validating email: ' || ew_lb_api.g_prop_value);
  
  -- Check if email matches pattern
  IF ew_lb_api.g_prop_value IS NOT NULL THEN
    IF NOT REGEXP_LIKE(ew_lb_api.g_prop_value, c_email_pattern) THEN
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Invalid email format. Expected format: user@domain.com';
      log('Validation failed for: ' || ew_lb_api.g_prop_value);
    END IF;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Error: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
END;
```

## Saving and Validating

### Save the Script

Click the **Save** icon to:
1. Save the script to database
2. Validate PL/SQL syntax
3. Display validation results

![Save and Validate](../assets/images/save-validate-script.png)
*Figure: Save button triggers automatic validation*

### Validation Results

Successful validation shows a confirmation message:

![Validation Success](../assets/images/validation-success.png)
*Figure: Successful script validation message*

Validation errors display with line numbers:

![Validation Error](../assets/images/validation-error.png)
*Figure: Script validation error with line number reference*

## Editing Existing Scripts

### Access Script Properties

To modify an existing script:

1. Right-click on the script name in the tree
2. Select "Edit Properties"

![Edit Script Properties](../assets/images/edit-script-properties.png)
*Figure: Right-click menu for editing script properties*

### Modifiable Properties

You can change:
- Script Name (if not referenced elsewhere)
- Description
- Enabled/Disabled status
- Script logic (in editor)

You **cannot** change:
- Script Type (must create new script)
- DB Function Name (for cloud deployments)

## Script Organization

### Naming Conventions

Establish consistent naming patterns:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `VAL_` | Validation scripts | `VAL_COST_CENTER_FORMAT` |
| `DER_` | Derivation scripts | `DER_DEFAULT_CURRENCY` |
| `MAP_` | Mapping scripts | `MAP_ACCOUNT_DIMENSION` |
| `WF_` | Workflow scripts | `WF_APPROVAL_ROUTING` |
| `CUST_` | Custom/client-specific | `CUST_SPECIAL_LOGIC` |

### Script Categories

Organize scripts by functional area:

```
Logic Scripts/
├── Validations/
│   ├── VAL_MEMBER_NAME
│   ├── VAL_PROPERTY_REQUIRED
│   └── VAL_NUMERIC_RANGE
├── Mappings/
│   ├── MAP_ENTITY_DIM
│   └── MAP_ACCOUNT_DIM
├── Workflow/
│   ├── WF_AUTO_APPROVE
│   └── WF_ROUTE_BY_AMOUNT
└── Integrations/
    ├── INT_ERP_TRANSFORM
    └── INT_EXPORT_FORMAT
```

## Version Control

### Header Comments

Always include version information:

```sql
/* 
  Script: VALIDATE_ACCOUNT_CODE
  Author: John Doe
  Created: 01-Jan-2025
  
  Version History:
  =====================================
  Date       | Author    | Description
  -----------|-----------|-------------
  01-Jan-25  | J.Doe     | Initial version
  15-Jan-25  | J.Smith   | Added range validation
  20-Jan-25  | J.Doe     | Fixed bug in error message
  =====================================
*/
```

### Change Management

Document significant changes:

```sql
-- v1.1: Added support for multi-currency (15-Jan-25)
IF g_currency_code IN ('USD', 'EUR', 'GBP') THEN
  -- New logic for multi-currency
END IF;

-- v1.2: Performance optimization (20-Jan-25)
-- Changed from cursor loop to bulk collect
```

## Testing Your Script

### 1. Unit Testing

Test script logic independently:

```sql
-- Add test conditions in development
DECLARE
  l_test_mode BOOLEAN := TRUE;  -- Set to FALSE in production
BEGIN
  IF l_test_mode THEN
    -- Override input parameters for testing
    ew_lb_api.g_prop_value := 'TEST123';
    ew_debug.log('TEST MODE: Using test value');
  END IF;
  
  -- Regular logic continues...
END;
```

### 2. Debug Logging

Enable comprehensive logging during development:

```sql
-- Detailed debug logging
log('=== Script Start ===');
log('User: ' || ew_lb_api.g_user_id);
log('Request: ' || ew_lb_api.g_request_id);
log('Member: ' || ew_lb_api.g_member_name);
log('Action: ' || ew_lb_api.g_action_code);
log('Input Value: ' || ew_lb_api.g_prop_value);

-- Logic execution...

log('Output Value: ' || ew_lb_api.g_out_prop_value);
log('Status: ' || ew_lb_api.g_status);
log('=== Script End ===');
```

### 3. Error Scenarios

Test error handling:

- Null values
- Invalid data types
- Boundary conditions
- Database exceptions
- Concurrent updates

## Best Practices

### 1. Always Initialize Status

```sql
BEGIN
  -- Always set initial status
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
```

### 2. Use Constants for Magic Values

```sql
DECLARE
  -- Define constants instead of hardcoding
  c_max_length    CONSTANT NUMBER := 50;
  c_default_type  CONSTANT VARCHAR2(10) := 'STANDARD';
  c_active_status CONSTANT VARCHAR2(1) := 'A';
```

### 3. Implement Proper Exception Handling

```sql
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Required data not found';
    log('No data found exception');
    
  WHEN TOO_MANY_ROWS THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Multiple records found - expected one';
    log('Too many rows exception');
    
  WHEN OTHERS THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Unexpected error: ' || SUBSTR(SQLERRM, 1, 200);
    log('Other exception: ' || SQLERRM);
END;
```

### 4. Optimize Performance

```sql
-- Cache frequently used values
DECLARE
  l_app_id NUMBER;
BEGIN
  -- Get once and reuse
  l_app_id := ew_hierarchy.get_app_id(ew_lb_api.g_app_name);
  
  -- Use cached value in loops
  FOR i IN 1..100 LOOP
    process_record(l_app_id, ...);
  END LOOP;
END;
```

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Script not saving | Check for syntax errors, verify database connection |
| Validation fails | Review error message, check line number indicated |
| Script not executing | Ensure script is enabled and properly associated |
| No debug output | Verify debug logging is enabled in global settings |
| Performance issues | Review execution plan, add indexes if needed |

### Debug Message Retrieval

View debug messages through:
**Reports → Admin → Debug Messages**

Filter by:
- Source Reference (script name)
- Date/Time range
- User

![Debug Messages Report](../assets/images/debug-messages-filter.png)
*Figure: Debug Messages report filtered by script name*

## Next Steps

After creating your script:
1. [Configure script associations](script-types.md)
2. [Test in development environment](script-structure.md)
3. [Deploy to production](#)