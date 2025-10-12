# Getting Started with Logic Builder

The Logic Builder Module enables you to extend EPMware's functionality through custom PL/SQL scripts that respond to various system events. This section covers the essential concepts and procedures to begin creating custom logic scripts.

## Overview

Logic Scripts in EPMware follow a two-step implementation process:

1. **Create the Script** - Define your custom logic in the Logic Builder module
2. **Configure the Association** - Link the script to specific events or configurations

![Logic Builder Module Interface](../assets/images/logic-builder-interface.png)
*Figure: Logic Builder Module main interface showing script management options*

## Key Concepts

### Script Execution Model

Logic Scripts are event-driven, executing automatically when specific actions occur in EPMware:

- User creates or modifies a member
- Request moves through workflow stages  
- Deployment process begins or completes
- Export operation runs
- ERP data import processes

### Script Types

Each script type serves a specific purpose:

| Type | Trigger Event | Common Uses |
|------|--------------|-------------|
| **Dimension Mapping** | Member hierarchy changes | Cross-application synchronization |
| **Property Validation** | Property value changes | Enforce business rules |
| **Property Derivation** | Member creation/modification | Auto-populate values |
| **Workflow Tasks** | Workflow stage transitions | Conditional approvals |
| **Deployment Tasks** | Deployment execution | Pre/post validations |

## Initial Setup

### 1. Enable Security Access

Before creating scripts, ensure your user group has Logic Builder access:

![Security Provisioning Screen](../assets/images/security-provisioning.png)
*Figure: Configuration → Security → Security Provisioning screen showing Logic Builder module access*

Navigate to **Configuration → Security → Security Provisioning** and enable the Logic Builder module for appropriate security groups.

!!! note
    Only users with Logic Builder write access can create or modify scripts

### 2. Access Logic Builder Module

Once security is configured, access the Logic Builder from the main menu:

1. Click the Configuration menu
2. Select Logic Builder
3. The Scripts management interface will display

### 3. Understand the Interface

The Logic Builder interface consists of:

- **Script Tree** - Organized list of all scripts by type
- **Script Editor** - PL/SQL code editor with syntax highlighting
- **Properties Panel** - Script metadata and configuration
- **Validation Output** - Syntax check results

![Logic Builder Script Editor](../assets/images/script-editor.png)
*Figure: Script Editor showing PL/SQL code with syntax highlighting*

## Creating Your First Script

Let's create a simple property validation script:

### Step 1: Create New Script

1. Click the plus icon (➕) in the Scripts menu
2. Enter the following details:

   - **Script Name**: `VALIDATE_COST_CENTER`
   - **Description**: Validates cost center format (CC-XXXX)
   - **Script Type**: Property Validations
   - **Enabled**: ✓ (checked)

![Create New Script Dialog](../assets/images/create-script-dialog.png)
*Figure: New Script creation dialog with required fields*

### Step 2: Write the Logic

Enter the following code in the Script Editor:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'VALIDATE_COST_CENTER';
  l_pattern     VARCHAR2(20)  := '^CC-[0-9]{4}$';
  
  PROCEDURE log (p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  -- Set default success status
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Validating cost center: ' || ew_lb_api.g_prop_value);
  
  -- Check if value matches pattern CC-XXXX
  IF NOT REGEXP_LIKE(ew_lb_api.g_prop_value, l_pattern) THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Cost Center must be in format CC-XXXX';
    log('Validation failed for: ' || ew_lb_api.g_prop_value);
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
END;
```

### Step 3: Validate the Script

Click the **Save** button to validate syntax:

![Script Validation Results](../assets/images/script-validation.png)
*Figure: Successful validation message after saving script*

### Step 4: Configure the Association

Navigate to **Configuration → Properties → Validations**:

1. Select your application and dimension
2. Choose the Cost Center property
3. Assign the `VALIDATE_COST_CENTER` script

![Property Validation Configuration](../assets/images/property-validation-config.png)
*Figure: Assigning validation script to Cost Center property*

## Best Practices

### Naming Conventions

- Use descriptive prefixes for your custom scripts (e.g., `CUST_`, `VAL_`, `DER_`)
- Reserve `EW_` prefix for EPMware standard scripts
- Use underscores to separate words

### Error Handling

Always include exception handling:

```sql
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Unexpected error: ' || SQLERRM;
    ew_debug.log('Error in ' || c_script_name || ': ' || SQLERRM);
END;
```

### Debug Logging

Use the debug logging API for troubleshooting:

```sql
ew_debug.log(p_text      => 'Debug message here',
             p_source_ref => 'SCRIPT_NAME');
```

### Performance Considerations

- Minimize database calls within loops
- Use bulk operations when processing multiple records
- Cache frequently accessed data in local variables
- Test scripts with realistic data volumes

## Next Steps

With the basics covered, explore these advanced topics:

- [Script Types and Events](script-types.md) - Detailed overview of all script types
- [Input/Output Parameters](script-structure.md) - Understanding script parameters
- [API Reference](../api/) - Complete API documentation
- [Examples](../events/) - Real-world script examples

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Script doesn't execute | Verify script is enabled and properly associated |
| Syntax errors | Check PL/SQL syntax, ensure all variables declared |
| No debug output | Confirm debug logging is enabled in global settings |
| Performance issues | Review execution plans, optimize queries |

### Debug Message Retrieval

To view debug messages:

1. Navigate to **Reports → Admin → Debug Messages**
2. Filter by Source Reference (your script name)
3. Review logged messages

![Debug Messages Report](../assets/images/debug-messages-report.png)
*Figure: Debug Messages report filtered by script name*

!!! tip
    Enable detailed logging during development, but reduce logging levels in production to improve performance