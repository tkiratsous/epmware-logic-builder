# Appendix A - Request Line Action Codes

This appendix provides a complete reference of hierarchy action codes used throughout EPMware Logic Builder scripts. These codes are essential for dimension mapping, hierarchy actions, and ERP interface operations.

## Action Codes Reference Table

The following table lists all available hierarchy action codes and their corresponding action names:

| Action Code | Action Name | Description | Usage Context |
|------------|-------------|-------------|---------------|
| **CMC** | Create Member - As Child | Creates a new member as a child of the specified parent | New member creation under existing parent |
| **CMS** | Create Member - As Sibling | Creates a new member as a sibling to the specified member | New member at same level as reference member |
| **DM** | Delete Member | Removes a member from the hierarchy | Member removal operations |
| **RM** | Rename Member | Changes the name of an existing member | Member name modifications |
| **ISMC** | Insert Shared Member - As Child | Inserts a shared member as a child | Creating alternate hierarchies |
| **ISMS** | Insert Shared Member - As Sibling | Inserts a shared member as a sibling | Shared member at same level |
| **P** | Edit Properties | Modifies member properties | Property value changes |
| **ZC** | Move Member | Relocates a member to a different parent | Hierarchy reorganization |
| **RC** | Reorder Children | Changes the order of child members | Member sequence adjustments |
| **RSM** | Remove Shared Member | Removes a shared member instance | Alternate hierarchy cleanup |
| **AC** | Activate Member | Activates an inactive member | Member status management |
| **IC** | Inactivate Member | Deactivates an active member | Member status management |

## Usage in Logic Scripts

### Accessing Action Codes

Action codes are available through the global variable `g_action_code` in various script types:

```sql
DECLARE
    l_action_code VARCHAR2(10);
BEGIN
    -- Get the current action code
    l_action_code := ew_lb_api.g_action_code;
    
    -- Process based on action
    CASE l_action_code
        WHEN 'CMC' THEN
            log('Processing Create Member as Child');
            -- Create child logic
        WHEN 'DM' THEN
            log('Processing Delete Member');
            -- Delete logic
        WHEN 'ZC' THEN
            log('Processing Move Member');
            -- Move logic
        ELSE
            log('Action code: ' || l_action_code);
    END CASE;
END;
```

### Action Name Retrieval

You can also access the action name using `g_action_name`:

```sql
DECLARE
    l_action_name VARCHAR2(100);
BEGIN
    l_action_name := ew_lb_api.g_action_name;
    log('Executing action: ' || l_action_name);
END;
```

## Script Type Compatibility

Different script types support different action codes:

### Pre/Post Hierarchy Actions

All action codes are available and can be used to trigger specific logic:

![Hierarchy Actions Configuration](../assets/images/hierarchy-actions-config.png)
*Figure: Configuring action codes for hierarchy scripts*

**Example Configuration:**
```sql
-- Pre-Hierarchy Action Script
BEGIN
    IF ew_lb_api.g_action_code = 'CMC' THEN
        -- Validate before creating child
        IF NOT is_valid_parent(ew_lb_api.g_parent_member_name) THEN
            ew_lb_api.g_status := ew_lb_api.g_error;
            ew_lb_api.g_message := 'Invalid parent for new member';
            RETURN;
        END IF;
    END IF;
END;
```

### Dimension Mapping

Action codes determine how members are synchronized:

```sql
-- Dimension Mapping Script
BEGIN
    -- Map source action to target action
    CASE ew_lb_api.g_action_code
        WHEN 'CMC' THEN
            -- Create in target
            ew_lb_api.g_tgt_action_code := 'CMC';
            ew_lb_api.g_tgt_member_name := 
                UPPER(ew_lb_api.g_src_member_name);
                
        WHEN 'DM' THEN
            -- Skip deletes in target
            ew_lb_api.g_skip := 'Y';
            log('Skipping delete for: ' || ew_lb_api.g_src_member_name);
            
        WHEN 'ZC' THEN
            -- Move in target
            ew_lb_api.g_tgt_action_code := 'ZC';
    END CASE;
END;
```

## ERP Interface Action Codes

When populating the `EW_IF_LINES` table for ERP imports, use these specific action code values:

### ERP-Specific Codes

| Action Code | Purpose | Example Usage |
|-------------|---------|---------------|
| **Create** | Create new member only | New cost centers |
| **Create or Edit** | Create if not exists, otherwise update | Employee records |
| **Delete** | Remove member | Obsolete accounts |
| **Edit** | Update existing member only | Property changes |
| **Insert Shared** | Add shared member | Alternate rollups |
| **Remove Shared** | Remove shared instance | Cleanup alternate hierarchies |
| **Move** | Relocate member | Reorganization |
| **Rename** | Change member name | Code changes |
| **Reorder** | Change sibling order | Priority adjustments |

### ERP Import Example

```sql
-- Pre-Import Logic Script
DECLARE
    CURSOR c_employees IS
        SELECT * FROM EW_IF_LINES
        WHERE NAME = 'EW_LOAD_EMPLOYEES'
        AND STATUS = 'N';
BEGIN
    FOR rec IN c_employees LOOP
        -- Determine action based on business logic
        IF member_exists(rec.MEMBER_NAME) THEN
            -- Update existing
            UPDATE EW_IF_LINES
            SET ACTION_CODE = 'Edit'
            WHERE IF_LINE_ID = rec.IF_LINE_ID;
        ELSE
            -- Create new
            UPDATE EW_IF_LINES
            SET ACTION_CODE = 'Create'
            WHERE IF_LINE_ID = rec.IF_LINE_ID;
        END IF;
    END LOOP;
END;
```

## Advanced Action Code Patterns

### Conditional Action Mapping

```sql
-- Map actions with conditions
DECLARE
    l_target_action VARCHAR2(20);
BEGIN
    -- Complex mapping logic
    IF ew_lb_api.g_action_code = 'CMC' THEN
        IF is_shared_dimension() THEN
            l_target_action := 'ISMC';  -- Create as shared
        ELSE
            l_target_action := 'CMC';   -- Create as base
        END IF;
    END IF;
    
    ew_lb_api.g_tgt_action_code := l_target_action;
END;
```

### Action Code Validation

```sql
-- Validate allowed actions for dimension
DECLARE
    TYPE t_allowed_actions IS TABLE OF VARCHAR2(10);
    l_allowed t_allowed_actions := t_allowed_actions('CMC', 'RM', 'P');
    l_valid BOOLEAN := FALSE;
BEGIN
    -- Check if action is allowed
    FOR i IN 1..l_allowed.COUNT LOOP
        IF ew_lb_api.g_action_code = l_allowed(i) THEN
            l_valid := TRUE;
            EXIT;
        END IF;
    END LOOP;
    
    IF NOT l_valid THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Action ' || ew_lb_api.g_action_code || 
                               ' not allowed for this dimension';
    END IF;
END;
```

## Common Issues and Solutions

### Issue 1: Shared Member Position
**Problem**: Shared member created before base member  
**Solution**: Use action code validation

```sql
IF ew_lb_api.g_action_code IN ('ISMC', 'ISMS') THEN
    IF NOT base_member_exists(ew_lb_api.g_member_name) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Base member must exist before shared';
    END IF;
END IF;
```

### Issue 2: Invalid Parent for Move
**Problem**: Moving member to invalid parent  
**Solution**: Validate target parent

```sql
IF ew_lb_api.g_action_code = 'ZC' THEN
    IF creates_circular_reference() THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Move would create circular reference';
    END IF;
END IF;
```

## Best Practices

!!! tip "Action Code Constants"
    Define constants for frequently used action codes to improve code readability and maintenance:
    ```sql
    c_create_child   CONSTANT VARCHAR2(10) := 'CMC';
    c_delete_member  CONSTANT VARCHAR2(10) := 'DM';
    c_move_member    CONSTANT VARCHAR2(10) := 'ZC';
    ```

!!! warning "Case Sensitivity"
    Action codes are case-sensitive. Always use uppercase values as shown in the reference table.

!!! info "Performance Consideration"
    When processing multiple actions, use CASE statements instead of multiple IF-THEN conditions for better performance.

---

## See Also

- [Hierarchy Actions](../events/hierarchy-actions/) - Detailed hierarchy action documentation
- [Dimension Mapping](../events/dimension-mapping/) - Using action codes in mapping
- [ERP Interface](../events/erp-interface/) - ERP import operations