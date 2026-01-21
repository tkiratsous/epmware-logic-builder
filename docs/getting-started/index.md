# Getting Started with Logic Builder

The Logic Builder Module enables you to build custom logic throughout EPMware to provide solutions for custom requirements such as property validations, workflow automation, and system integration.

## Introduction

EPMware's Logic Builder utilizes Oracle PL/SQL as its programming language, with scripts residing within the EPMware database. This powerful framework allows you to automate processes, enforce business rules, and extend standard functionality without exposing business logic in the front-end.

   **On-Premise Customers**: Can optionally create stored database functions and reference them in Logic Scripts

## Quick Navigation

<div class="grid cards">
  <div class="card">
    <h3>🔐 Security Provisioning</h3>
    <p>Configure user access to Logic Builder module</p>
    <a href="security-provisioning" class="md-button">Configure Access →</a>
  </div>
  
  <div class="card">
    <h3>📝 Create Scripts</h3>
    <p>Build your first logic script</p>
    <a href="creating-scripts" class="md-button">Start Building →</a>
  </div>
  
  <div class="card">
    <h3>📋 Script Types</h3>
    <p>Understand different script categories</p>
    <a href="script-types" class="md-button">Learn More →</a>
  </div>
  
  <div class="card">
    <h3>🏗️ Script Structure</h3>
    <p>Master PL/SQL script organization</p>
    <a href="script-structure" class="md-button">View Structure →</a>
  </div>
</div>

## The Two-Step Process

Logic Script execution follows a two-step process:

1. **Create the Logic Script** - Build the script in the Logic Builder module
2. **Assign to Configuration** - Reference it in the related configuration page

Scripts execute when specific events occur. For example:
- Dimension mapping scripts execute when new lines are created in requests.
- On Submit Workflow scripts executes whenever a request is submitted to the workflow.

## Available Script Types

The Logic Builder supports 13 different script types, each designed for specific use cases:

| # | Script Type | Purpose | Configuration Location |
|---|-------------|---------|------------------------|
| 1 | **Dimension Mapping** | Synchronize hierarchies across applications | Configuration → Dimension → Mapping |
| 2 | **Property Mapping** | Synchronize property values using custom logic | Configuration → Property → Mapping |
| 3 | **Pre Hierarchy Actions** | Execute logic *before* hierarchy actions | Configuration → Dimension → Hierarchy Actions |
| 4 | **Post Hierarchy Actions** | Execute logic *after* hierarchy actions | Configuration → Dimension → Hierarchy Actions |
| 5 | **Property Derivations** | Calculate and derive property values | Configuration → Property → Derivations |
| 6 | **Property Validations** | Validate property values against business rules | Configuration → Property → Validations |
| 7 | **On Submit Workflow** | Validate before workflow submission | Workflow → Builder |
| 8 | **On Request Line Approval** | Validate on line approval | Workflow → Approve/Review Tasks |
| 9 | **Workflow Custom Task** | Perform custom workflow tasks | Workflow → Custom Tasks |
| 10 | **Deployment Tasks** | Pre/post deployment operations | Deployment Configuration |
| 11 | **ERP Interface Tasks** | Pre/post ERP import execution | ERP Import → Builder |
| 12 | **Pre Export Generation Tasks** | Execute before export file generation |  Export |
| 13 | **Post Export Generation Tasks** | Execute after export file generation |  Export |


## Best Practices Summary

### Naming Conventions
- Use descriptive names (max 50 characters)
- Apply consistent prefixes for custom scripts
- Avoid "EW_" prefix (reserved for standard scripts)
- Group related scripts with common prefixes

### Script Organization
```sql
/* 
   Author: Implementation Team
   Date: YYYY-MM-DD
   Purpose: Clear description of script purpose
   
   Version History:
   ================
   Date       | Modified By | Notes
   -----------|-------------|------------------
   2025-01-01 | Dev Team    | Initial version
*/

DECLARE
   -- Constants
   c_script_name VARCHAR2(50) := 'MY_SCRIPT_NAME';
   
   -- Local procedures for logging
   PROCEDURE log(p_msg IN VARCHAR2) IS
   BEGIN
       ew_debug.log(p_text => p_msg, 
                   p_source_ref => c_script_name);
   END log;
  
BEGIN
   -- Initialize status
   ew_lb_api.g_status := ew_lb_api.g_success;
   ew_lb_api.g_message := NULL;
   
   -- Your logic here
   
EXCEPTION
   WHEN OTHERS THEN
       ew_lb_api.g_status := ew_lb_api.g_error;
       ew_lb_api.g_message := 'Error: ' || SQLERRM;
       log(ew_lb_api.g_message);
END;
```

## Prerequisites Checklist

Before creating Logic Scripts, ensure you have:

- ✅ **Access Rights**    - Logic Builder module enabled via Security Provisioning
- ✅ **PL/SQL Knowledge** - Understanding of Oracle PL/SQL syntax
- ✅ **Documentation**    - Basic Knowledge of Epmware APIs from logic builder guide
- ✅ **Test Environment** - Always test scripts on test env first

## Getting Help

### Common Questions

??? question "Can I modify standard EPMware scripts?"
    No, never modify scripts with "EW_" prefix. Instead, create a copy with a different name and modify the copy.

??? question "How do I debug my scripts?"
    Use `ew_debug.log()` extensively for logging and check Debug Messages in the Audit module.

??? question "What permissions do I need?"
    Your security group needs the Logic Builder module enabled in Security Provisioning.


## Next Steps

Ready to start building? Follow this learning path:

1. **[Configure Security Access](security-provisioning.md)** - Set up user permissions
2. **[Create Your First Script](creating-scripts.md)** - Step-by-step tutorial
3. **[Understand Script Types](script-types.md)** - Choose the right script type
4. **[Master Script Structure](script-structure.md)** - Learn PL/SQL best practices
5. **[Debug and Test](debugging.md)** - Validate your scripts
6. **[Review Examples](../examples/)** - Learn from real-world scripts

!!! tip "Start Simple"
    Begin with a basic property validation script before attempting complex dimension mappings or workflow automations.

---

## Quick Reference

### Common Status Codes
```sql
-- Success
ew_lb_api.g_status := ew_lb_api.g_success;  -- or 'S'

-- Error
ew_lb_api.g_status := ew_lb_api.g_error;    -- or 'E'
```

### Essential APIs
```sql
-- Logging
ew_debug.log(p_text => 'Message', p_source_ref => 'SCRIPT_NAME');

-- Check member exists
ew_hierarchy.chk_member_exists(p_app_dimension_id => 100, 
                               p_member_name => 'Member1');

-- Get property value
ew_hierarchy.get_member_prop_value(p_app_dimension_id => 100,
                                   p_member_name => 'Member1',
                                   p_prop_name => 'AccountType');
```

### Action Codes Quick Reference
[Action codes](appendices/action-codes.md)
| Code | Action |
|------|--------|
| CMC | Create Member - As Child |
| CMS | Create Member - As Sibling |
| DM | Delete Member |
| P | Edit Properties |
| RM | Rename Member |
| ZC | Move Member |
| ISMC | Insert Shared Member - As Child |
| ISMS | Insert Shared Member - As Sibling |
| RSM | Remove Shared Member |
| AC | Activate Member |
| IC | Inactivate Member |
| RC | Reorder Children |

---

*Continue to [Security Provisioning](security-provisioning.md) →*