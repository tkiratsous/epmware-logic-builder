# Appendix B - Standard Scripts

EPMware provides a comprehensive library of out-of-the-box Logic Scripts that are automatically assigned to applications upon registration or import. These standard scripts handle common validation and automation requirements across different EPM application types.

!!! warning "Important"
    Never modify standard scripts directly. If customization is needed, clone the script and modify the copy to preserve upgrade compatibility.

## Standard Property Validation Scripts

These scripts are automatically assigned when applications are registered in the Application Configuration page.

### Application-Specific Validation Scripts

| Logic Script Name | Application Types | Auto-Assignment | Purpose |
|-------------------|-------------------|-----------------|---------|
| **EW_ESSBASE_VALIDATIONS** | Essbase (On-Prem & Cloud) | On Registration | Validates Essbase-specific properties like Data Storage, Consolidation |
| **EW_HFM_VALIDATIONS** | Oracle HFM | On Registration | Enforces HFM business rules and metadata constraints |
| **EW_HP_VALIDATIONS** | Planning (On-Prem & Cloud) | On Registration | Validates Planning properties, Smart Lists, UDAs |
| **EW_PCMCS_VALIDATIONS** | Oracle PCMCS Cloud | On Registration | Profitability and Cost Management validations |
| **EW_TRCS_VALIDATIONS** | Oracle TRCS Cloud | On Registration | Tax Reporting compliance validations |
| **EW_FDMEE_VALIDATIONS** | Oracle FDMEE / Data Management | On Registration | Data integration and mapping validations |
| **EW_FUSION_VALIDATIONS** | Oracle EBS (Fusion) | On Registration | Fusion application-specific rules |
| **EW_ONESTREAM_VALIDATIONS** | OneStream (On-Prem & Cloud) | On Registration | OneStream metadata and property validations |

### Validation Script Configuration

![Standard Validations Assignment](../assets/images/standard-validations-assignment.png)
*Figure: Automatic assignment of standard validation scripts*

### Example: EW_ESSBASE_VALIDATIONS

This script validates Essbase-specific properties:

```sql
-- Extract from EW_ESSBASE_VALIDATIONS
BEGIN
    -- Validate Data Storage property
    IF ew_lb_api.g_prop_name = 'DataStorage' THEN
        -- Parent members must be Dynamic Calc or Label Only
        IF is_parent_member(ew_lb_api.g_member_name) THEN
            IF ew_lb_api.g_prop_value NOT IN ('DynamicCalc', 'LabelOnly') THEN
                ew_lb_api.g_status := ew_lb_api.g_error;
                ew_lb_api.g_message := 'Parent members must have ' ||
                    'Data Storage as Dynamic Calc or Label Only';
            END IF;
        END IF;
    END IF;
    
    -- Validate Consolidation property
    IF ew_lb_api.g_prop_name = 'Consolidation' THEN
        IF ew_lb_api.g_prop_value NOT IN ('+', '-', '*', '/', '%', '~', '^') THEN
            ew_lb_api.g_status := ew_lb_api.g_error;
            ew_lb_api.g_message := 'Invalid consolidation operator';
        END IF;
    END IF;
END;
```

## Pre-Hierarchy Action Scripts

These scripts execute before hierarchy changes to enforce application-specific rules.

### EW_SHARED_NODE_POSITION

**Application Types:** Essbase, Planning, PBCS  
**Auto-Assignment:** Yes, for all dimensions  
**Purpose:** Prevents shared members from being created before their base members

![Shared Node Position Configuration](../assets/images/shared-node-position-config.png)
*Figure: Automatic assignment of shared node position validation*

**Script Logic:**

```sql
-- EW_SHARED_NODE_POSITION Script
DECLARE
    l_base_exists NUMBER;
BEGIN
    -- Check if this is a shared member action
    IF ew_lb_api.g_action_code IN ('ISMC', 'ISMS') THEN
        
        -- Check if base member exists
        SELECT COUNT(*)
        INTO   l_base_exists
        FROM   ew_member_v
        WHERE  member_name = ew_lb_api.g_member_name
        AND    app_dimension_id = ew_lb_api.g_app_dimension_id
        AND    shared_flag = 'N';
        
        IF l_base_exists = 0 THEN
            ew_lb_api.g_status := ew_lb_api.g_error;
            ew_lb_api.g_message := 'Shared member cannot be created before ' ||
                                  'its base member. Create base member first.';
            RETURN;
        END IF;
        
        -- Check position in hierarchy
        IF NOT is_base_before_shared() THEN
            ew_lb_api.g_status := ew_lb_api.g_error;
            ew_lb_api.g_message := 'Shared member must appear after ' ||
                                  'base member in hierarchy order';
        END IF;
    END IF;
END;
```

### EW_ONESTREAM_SHARED_NODE_CHECK

**Application Types:** OneStream  
**Auto-Assignment:** Yes, for Extended dimensions only  
**Purpose:** Prevents invalid shared member creation in extended dimensions

![OneStream Shared Node Check](../assets/images/onestream-shared-config.png)
*Figure: OneStream extended dimension configuration*

**Script Logic:**

```sql
-- EW_ONESTREAM_SHARED_NODE_CHECK Script
BEGIN
    -- Check if dimension is extended
    IF is_extended_dimension(ew_lb_api.g_dim_name) THEN
        
        -- Validate shared member belongs to same dimension
        IF ew_lb_api.g_action_code IN ('ISMC', 'ISMS') THEN
            IF NOT shared_belongs_to_dimension() THEN
                ew_lb_api.g_status := ew_lb_api.g_error;
                ew_lb_api.g_message := 'Shared member must belong to ' ||
                                      'the same extended dimension';
            END IF;
        END IF;
    END IF;
END;
```

## Post-Hierarchy Action Scripts

These scripts execute after hierarchy changes to perform automated tasks. They require manual configuration.

### EW_EB_DATA_STORAGE_PROP

**Application Types:** Essbase (On-Prem & Cloud)  
**Auto-Assignment:** No (Manual)  
**Purpose:** Automatically sets Data Storage to "Dynamic Calc" when a base member becomes a parent

![Data Storage Automation Configuration](../assets/images/data-storage-automation-config.png)
*Figure: Manual configuration of Data Storage automation*

**Configuration Steps:**

1. Navigate to Configuration → Dimension → Hierarchy Actions
2. Select the Essbase dimension
3. Assign script to "Create Member - As Child" action
4. Set as Post-Hierarchy Action

**Script Implementation:**

```sql
-- EW_EB_DATA_STORAGE_PROP Script
DECLARE
    l_parent_id     NUMBER;
    l_current_value VARCHAR2(100);
BEGIN
    log('Checking Data Storage for new parent: ' || 
        ew_lb_api.g_parent_member_name);
    
    -- Get parent member ID
    l_parent_id := ew_hierarchy.get_member_id(
        p_member_name => ew_lb_api.g_parent_member_name,
        p_app_dimension_id => ew_lb_api.g_app_dimension_id
    );
    
    -- Get current Data Storage value
    l_current_value := ew_properties.get_property_value(
        p_member_id => l_parent_id,
        p_property_name => 'DataStorage'
    );
    
    -- Update if not already Dynamic Calc
    IF l_current_value NOT IN ('DynamicCalc', 'LabelOnly') THEN
        
        -- Create request line to update property
        ew_request.add_property_line(
            p_request_id => ew_lb_api.g_request_id,
            p_member_id => l_parent_id,
            p_property_name => 'DataStorage',
            p_old_value => l_current_value,
            p_new_value => 'DynamicCalc',
            p_action_code => 'P'
        );
        
        log('Data Storage updated to Dynamic Calc');
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        log('Error updating Data Storage: ' || SQLERRM);
        -- Don't fail the main action
END;
```

### EW_HFM_ENT_SEC_CLASS_AUTOMATION

**Application Types:** HFM  
**Auto-Assignment:** No (Manual)  
**Purpose:** Automatically creates security classes for new entities matching pattern E##### (E followed by 5 digits)

!!! note "Customization Required"
    This script is provided as a template. Clone and modify it according to your security class naming conventions.

![HFM Security Class Automation](../assets/images/hfm-security-automation-config.png)
*Figure: Security class automation configuration*

**Script Implementation:**

```sql
-- EW_HFM_ENT_SEC_CLASS_AUTOMATION Script
DECLARE
    l_entity_name    VARCHAR2(100);
    l_sec_class_name VARCHAR2(100);
    l_pattern        VARCHAR2(20) := '^E[0-9]{5}$';  -- E##### pattern
BEGIN
    l_entity_name := ew_lb_api.g_member_name;
    
    -- Check if entity matches pattern
    IF REGEXP_LIKE(l_entity_name, l_pattern) THEN
        
        -- Generate security class name
        l_sec_class_name := 'SC_' || l_entity_name;
        
        log('Creating security class: ' || l_sec_class_name);
        
        -- Check if security class exists
        IF NOT security_class_exists(l_sec_class_name) THEN
            
            -- Create security class member
            ew_request.add_hierarchy_line(
                p_request_id => ew_lb_api.g_request_id,
                p_app_name => ew_lb_api.g_app_name,
                p_dim_name => 'SecurityClass',
                p_member_name => l_sec_class_name,
                p_parent_name => 'AllSecurityClasses',
                p_action_code => 'CMC',
                p_description => 'Auto-generated for ' || l_entity_name
            );
            
            -- Set security class properties
            ew_request.add_property_line(
                p_request_id => ew_lb_api.g_request_id,
                p_member_name => l_sec_class_name,
                p_property_name => 'EntityAccess',
                p_new_value => l_entity_name,
                p_action_code => 'P'
            );
            
            log('Security class created successfully');
        END IF;
    END IF;
    
EXCEPTION
    WHEN OTHERS THEN
        log('Error creating security class: ' || SQLERRM);
        -- Continue with main process
END;
```

## Cloning and Customizing Standard Scripts

### Step 1: Clone the Script

1. Navigate to Logic Builder
2. Find the standard script to clone
3. Click "Clone" action
4. Provide new name (e.g., `CUSTOM_ESSBASE_VALIDATIONS`)

![Clone Script Process](../assets/images/clone-script-process.png)
*Figure: Cloning a standard script*

### Step 2: Modify the Clone

```sql
-- Example: Customized validation script
-- Based on EW_ESSBASE_VALIDATIONS
DECLARE
    -- Add custom variables
    l_custom_rule VARCHAR2(100);
BEGIN
    -- Keep standard validations
    ew_lb_api.execute_script('EW_ESSBASE_VALIDATIONS');
    
    -- Add custom validations
    IF ew_lb_api.g_prop_name = 'CustomProperty' THEN
        -- Custom validation logic
        IF NOT is_valid_custom_value(ew_lb_api.g_prop_value) THEN
            ew_lb_api.g_status := ew_lb_api.g_error;
            ew_lb_api.g_message := 'Custom validation failed';
        END IF;
    END IF;
END;
```

### Step 3: Update Configuration

1. Navigate to application configuration
2. Replace standard script with custom version
3. Test thoroughly before deployment

## Standard Script Maintenance

### Version Compatibility

Standard scripts are updated with EPMware releases. Consider:

- **Patch Updates**: May include bug fixes to standard scripts
- **Minor Releases**: May add new validations or features
- **Major Releases**: May introduce new standard scripts

### Upgrade Considerations

!!! warning "Upgrade Impact"
    When upgrading EPMware:
    1. Review release notes for standard script changes
    2. Test custom scripts with new version
    3. Merge new standard features into custom scripts if needed

### Monitoring Standard Scripts

Use the Logic Script Usage Report to track standard script usage:

```sql
-- Query to find standard script usage
SELECT 
    ls.script_name,
    ls.script_type,
    ac.app_name,
    ac.dimension_name,
    ac.configuration_type
FROM 
    logic_scripts ls
JOIN 
    app_configurations ac ON ls.script_id = ac.script_id
WHERE 
    ls.script_name LIKE 'EW_%'
ORDER BY 
    ls.script_name, ac.app_name;
```

## Best Practices

1. **Never Modify Originals**: Always clone standard scripts before customization
2. **Document Changes**: Maintain clear documentation of customizations
3. **Test Thoroughly**: Validate custom scripts across all scenarios
4. **Monitor Performance**: Standard scripts are optimized; ensure customizations maintain performance
5. **Regular Review**: Periodically review custom scripts against updated standards

---

## See Also

- [Property Validations](../events/property-validations/standard-validations.md) - Detailed validation documentation
- [Hierarchy Actions](../events/hierarchy-actions/seeded-scripts.md) - Seeded script configurations
- [Script Types](../getting-started/script-types.md) - Overview of all script types