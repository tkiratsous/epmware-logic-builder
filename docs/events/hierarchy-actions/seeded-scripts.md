# Seeded Hierarchy Action Scripts

EPMware provides pre-built (seeded) Logic Scripts that handle common hierarchy management scenarios. These scripts are installed with the system and can be used as-is or cloned for customization.

## Available Seeded Scripts

### Standard Scripts Overview

| Script Name | Type | Purpose | Action Codes |
|-------------|------|---------|--------------|
| EW_VALIDATE_MEMBER_NAME | Pre | Validate member naming standards | CMC, CMS, RNM |
| EW_CHECK_DUPLICATES | Pre | Prevent duplicate members | CMC, CMS |
| EW_VALIDATE_HIERARCHY_DEPTH | Pre | Enforce depth limits | CMC, ZC |
| EW_PREVENT_CIRCULAR_REF | Pre | Prevent circular references | ZC |
| EW_CREATE_DEFAULT_CHILDREN | Post | Auto-create standard children | CMC |
| EW_SET_DEFAULT_PROPERTIES | Post | Set initial property values | CMC, CMS |
| EW_AUDIT_HIERARCHY_CHANGES | Post | Track all hierarchy changes | All |
| EW_SYNC_SHARED_MEMBERS | Post | Synchronize shared instances | ISMC, ISMS, DSHM |

![Seeded Scripts List](../../assets/images/seeded-scripts-list.png)
*Figure: Seeded scripts available in Logic Builder*

## Key Seeded Scripts

### EW_VALIDATE_MEMBER_NAME

**Purpose**: Enforce EPMware standard naming conventions

**Configuration**: Pre-hierarchy action for CMC, CMS, RNM

**Validation Rules**:
- Starts with letter or underscore
- Contains only alphanumeric and underscore
- Length between 1-80 characters
- No spaces or special characters
- Case-insensitive duplicate check

**Script Logic**:
```sql
-- Simplified version of seeded script
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'EW_VALIDATE_MEMBER_NAME';
  l_pattern VARCHAR2(100) := '^[A-Za-z_][A-Za-z0-9_]*$';
BEGIN
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS', 'RNM') THEN
    -- Check pattern
    IF NOT REGEXP_LIKE(ew_lb_api.g_new_member_name, l_pattern) THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Invalid member name format';
    END IF;
    
    -- Check length
    IF LENGTH(ew_lb_api.g_new_member_name) > 80 THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Member name exceeds 80 characters';
    END IF;
  END IF;
END;
```

### EW_CHECK_DUPLICATES

**Purpose**: Prevent duplicate member names within dimension

**Configuration**: Pre-hierarchy action for CMC, CMS

**Features**:
- Case-insensitive checking
- Checks across entire dimension
- Clear error messages with existing location

**Script Logic**:
```sql
DECLARE
  l_existing_parent VARCHAR2(100);
BEGIN
  IF ew_lb_api.g_action_code IN ('CMC', 'CMS') THEN
    -- Check if member exists
    IF ew_hierarchy.chk_member_exists(
         p_app_dimension_id => ew_lb_api.g_app_dimension_id,
         p_member_name     => ew_lb_api.g_new_member_name,
         p_case_match      => 'N'
       ) = 'Y' THEN
      
      -- Get parent of existing member
      l_existing_parent := ew_hierarchy.get_primary_parent_name(
        p_app_dimension_id => ew_lb_api.g_app_dimension_id,
        p_member_name     => ew_lb_api.g_new_member_name
      );
      
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Member "' || ew_lb_api.g_new_member_name || 
                              '" already exists under parent "' || 
                              NVL(l_existing_parent, 'ROOT') || '"';
    END IF;
  END IF;
END;
```

### EW_CREATE_DEFAULT_CHILDREN

**Purpose**: Automatically create standard child members

**Configuration**: Post-hierarchy action for CMC

**Default Children Created**:
Based on member name patterns:
- Entity members → Create currency members (USD, Local)
- Department → Create expense categories
- Project → Create phase members
- Time periods → Create months/quarters

**Customization Example**:
```sql
-- Clone and modify for custom patterns
IF ew_lb_api.g_new_member_name LIKE 'CUSTOM_PREFIX_%' THEN
  -- Create your custom children
  create_child(ew_lb_api.g_new_member_name || '_CHILD1');
  create_child(ew_lb_api.g_new_member_name || '_CHILD2');
END IF;
```

### EW_AUDIT_HIERARCHY_CHANGES

**Purpose**: Comprehensive audit trail for all hierarchy modifications

**Configuration**: Post-hierarchy action for all action codes

**Audit Information Captured**:
- Action type and timestamp
- User and session information
- Member names (old and new)
- Parent information
- Request/task context
- IP address and client info

**Audit Table Structure**:
```sql
CREATE TABLE ew_hierarchy_audit (
  audit_id          NUMBER PRIMARY KEY,
  audit_timestamp   TIMESTAMP,
  action_code       VARCHAR2(10),
  app_name          VARCHAR2(100),
  dimension_name    VARCHAR2(100),
  member_name       VARCHAR2(100),
  new_member_name   VARCHAR2(100),
  parent_name       VARCHAR2(100),
  old_parent_name   VARCHAR2(100),
  user_id           VARCHAR2(100),
  session_id        NUMBER,
  request_id        NUMBER,
  ip_address        VARCHAR2(50),
  client_info       VARCHAR2(200)
);
```

## Using Seeded Scripts

### Option 1: Use As-Is

1. Navigate to hierarchy action configuration
2. Select the seeded script from dropdown
3. No modifications needed

![Using Seeded Script](../../assets/images/using-seeded-script.png)
*Figure: Selecting seeded script in configuration*

### Option 2: Clone and Customize

1. **Find the script** in Logic Builder
2. **Clone the script**:
   - Right-click → Clone Script
   - Provide new name (without EW_ prefix)
3. **Modify the logic** as needed
4. **Associate** with hierarchy actions

```sql
-- Example: Customize validation pattern
-- Original seeded pattern
c_pattern VARCHAR2(100) := '^[A-Za-z_][A-Za-z0-9_]*$';

-- Custom pattern (allow hyphens)
c_pattern VARCHAR2(100) := '^[A-Za-z_][A-Za-z0-9_-]*$';
```

### Option 3: Extend with Additional Logic

Create a wrapper script that calls seeded script plus custom logic:

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CUSTOM_VALIDATION_WRAPPER';
BEGIN
  -- First run standard validation
  ew_validate_member_name();
  
  -- If standard validation passed, add custom checks
  IF ew_lb_api.g_status = ew_lb_api.g_success THEN
    -- Additional custom validation
    IF custom_check_fails() THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Custom validation failed';
    END IF;
  END IF;
END;
```

## Seeded Script Configuration

### EW_SET_DEFAULT_PROPERTIES

**Default Property Values Set**:
```yaml
Status: Active
Created_Date: SYSDATE
Created_By: USER
Data_Storage: Store
Consolidation: Addition
Two_Pass_Calc: N
Formula: (blank)
UDA: (blank)
```

**Inheritance Rules**:
- Currency → From parent
- Region → From parent
- Plan_Type → From parent
- Aggregation → Based on member type

### EW_SYNC_SHARED_MEMBERS

**Synchronization Rules**:
- Property changes propagate to all instances
- Rename affects all shared instances
- Delete shared only removes specific instance
- Primary member deletion removes all instances

## Best Practices for Seeded Scripts

### 1. Don't Modify Originals
- Always clone before customizing
- Originals may be updated in upgrades
- Keep reference to original functionality

### 2. Test Cloned Scripts
- Verify all action codes still work
- Test with your specific naming patterns
- Ensure performance is acceptable

### 3. Document Customizations
```sql
/* 
  Script: CUSTOM_VALIDATE_MEMBER
  Based On: EW_VALIDATE_MEMBER_NAME
  Modifications:
    - Allow hyphens in names
    - Maximum length increased to 100
    - Added prefix validation
  Modified By: Admin
  Date: 01/15/2025
*/
```

### 4. Version Control
- Export custom scripts regularly
- Track changes in source control
- Document dependencies

## Disabling Seeded Scripts

If a seeded script conflicts with requirements:

1. **Remove Association**: Unlink from hierarchy actions
2. **Disable Script**: Set Enabled = No in script properties
3. **Create Replacement**: Build custom script for requirement

## Troubleshooting Seeded Scripts

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Validation too restrictive | Standard patterns don't match naming | Clone and modify pattern |
| Wrong children created | Pattern matching incorrect | Customize child creation logic |
| Audit missing information | Custom fields needed | Extend audit table and script |
| Performance impact | Script too generic | Create optimized version |

### Debug Seeded Scripts

Enable debug mode to see execution:
```sql
-- Add to cloned script
ew_debug.log('Seeded script executing: ' || c_script_name);
ew_debug.log('Action: ' || ew_lb_api.g_action_code);
ew_debug.log('Member: ' || ew_lb_api.g_member_name);
```

## EPMware Updates

### Upgrade Considerations

When upgrading EPMware:
1. Seeded scripts may be updated
2. Custom scripts are preserved
3. Review release notes for changes
4. Test hierarchy actions after upgrade

### New Seeded Scripts

Check for new seeded scripts after upgrades:
```sql
SELECT script_name, description, created_date
FROM ew_logic_scripts
WHERE script_name LIKE 'EW_%'
AND created_date >= [last_upgrade_date]
ORDER BY created_date DESC;
```

## Performance Metrics

### Typical Execution Times

| Script | Average Time | Notes |
|--------|--------------|-------|
| EW_VALIDATE_MEMBER_NAME | <100ms | Simple pattern match |
| EW_CHECK_DUPLICATES | 100-500ms | Depends on dimension size |
| EW_CREATE_DEFAULT_CHILDREN | 500-2000ms | Creates multiple members |
| EW_AUDIT_HIERARCHY_CHANGES | <200ms | Single insert operation |

### Optimization Tips

1. **Index Support**: Ensure indexes exist for seeded script queries
2. **Caching**: Some seeded scripts cache data in package variables
3. **Batch Mode**: Seeded scripts detect bulk operations and optimize

## Next Steps

- [Pre-Hierarchy Actions](pre-hierarchy.md) - Validation patterns
- [Post-Hierarchy Actions](post-hierarchy.md) - Automation patterns
- [Creating Scripts](../../getting-started/creating-scripts.md) - Build custom scripts

---

!!! info "Note"
    Seeded scripts are designed to handle common scenarios. For specific business requirements, clone and customize rather than modifying the originals. This ensures upgrades don't override your customizations.