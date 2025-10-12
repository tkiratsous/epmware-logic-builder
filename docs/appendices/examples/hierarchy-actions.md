# Hierarchy Action Examples

Hierarchy action scripts execute automatically when members are created, moved, renamed, or deleted, enabling audit trails, cascading updates, and automated hierarchy management.

## Audit Trail for Member Creation

🟢 **Level:** Basic  
**Purpose:** Track all member creation events with detailed logging

```sql
/*
  Script: AUDIT_MEMBER_CREATION
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Create comprehensive audit trail for member creation
  
  Tracks:
  - Who created the member
  - When it was created
  - Initial properties
  - Parent hierarchy
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'AUDIT_MEMBER_CREATION';
  v_audit_id       NUMBER;
  v_member_name    VARCHAR2(100);
  v_parent_name    VARCHAR2(100);
  v_created_by     VARCHAR2(100);
  v_client_machine VARCHAR2(100);
  v_properties     CLOB;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_member_name := ew_lb_api.g_new_member_name;
  v_parent_name := ew_lb_api.g_parent_member_name;
  v_created_by  := NVL(ew_lb_api.g_user_name, USER);
  
  log('Auditing creation of member: ' || v_member_name);
  
  -- Get client information
  BEGIN
    SELECT SYS_CONTEXT('USERENV', 'HOST')
    INTO   v_client_machine
    FROM   DUAL;
  EXCEPTION
    WHEN OTHERS THEN
      v_client_machine := 'Unknown';
  END;
  
  -- Collect all initial properties
  v_properties := '{';
  FOR prop IN (SELECT prop_name, prop_value
               FROM   ew_member_properties
               WHERE  app_id = ew_lb_api.g_app_id
               AND    dim_id = ew_lb_api.g_dim_id
               AND    member_name = v_member_name)
  LOOP
    v_properties := v_properties || 
                   '"' || prop.prop_name || '":"' || 
                   prop.prop_value || '",';
  END LOOP;
  v_properties := RTRIM(v_properties, ',') || '}';
  
  -- Insert audit record
  INSERT INTO ew_hierarchy_audit
    (audit_id, action_type, app_name, dim_name,
     member_name, parent_name, created_by, created_date,
     client_machine, initial_properties)
  VALUES
    (ew_audit_seq.NEXTVAL, 'CREATE', ew_lb_api.g_app_name, 
     ew_lb_api.g_dim_name, v_member_name, v_parent_name,
     v_created_by, SYSDATE, v_client_machine, v_properties)
  RETURNING audit_id INTO v_audit_id;
  
  log('Audit record created with ID: ' || v_audit_id);
  
  -- Send notification for sensitive hierarchies
  IF ew_lb_api.g_dim_name IN ('Entity', 'Account', 'Organization') THEN
    ew_email_api.send_email(
      p_to      => 'admin@company.com',
      p_subject => 'Member Created in ' || ew_lb_api.g_dim_name,
      p_body    => 'User ' || v_created_by || ' created member ' || 
                   v_member_name || ' under ' || v_parent_name ||
                   ' at ' || TO_CHAR(SYSDATE, 'DD-MON-YYYY HH24:MI:SS')
    );
  END IF;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Audit logging failed: ' || SQLERRM);
    -- Don't fail the member creation due to audit failure
    ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

## Automatic Child Member Creation

🟡 **Level:** Intermediate  
**Purpose:** Automatically create standard child members for specific parent types

```sql
/*
  Script: AUTO_CREATE_CHILDREN
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Automatically create standard child members
  
  Business Rule:
  - When creating a department, auto-create budget categories
  - When creating a region, auto-create country placeholders
  - When creating a product group, auto-create variance members
*/
DECLARE
  c_script_name      VARCHAR2(100) := 'AUTO_CREATE_CHILDREN';
  v_parent_member    VARCHAR2(100);
  v_member_type      VARCHAR2(50);
  v_children_created NUMBER := 0;
  
  TYPE t_child_template IS RECORD (
    child_name   VARCHAR2(100),
    child_suffix VARCHAR2(50),
    prop_name    VARCHAR2(100),
    prop_value   VARCHAR2(500)
  );
  
  TYPE t_child_templates IS TABLE OF t_child_template;
  v_templates t_child_templates;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  PROCEDURE create_child_member(p_parent     IN VARCHAR2,
                                p_child_name IN VARCHAR2,
                                p_prop_name  IN VARCHAR2 DEFAULT NULL,
                                p_prop_value IN VARCHAR2 DEFAULT NULL) IS
  BEGIN
    -- Create the child member
    ew_api.create_member(
      p_app_id      => ew_lb_api.g_app_id,
      p_dim_id      => ew_lb_api.g_dim_id,
      p_member_name => p_child_name,
      p_parent_name => p_parent
    );
    
    -- Set property if provided
    IF p_prop_name IS NOT NULL THEN
      ew_api.set_property_value(
        p_app_id      => ew_lb_api.g_app_id,
        p_dim_id      => ew_lb_api.g_dim_id,
        p_member_name => p_child_name,
        p_prop_name   => p_prop_name,
        p_prop_value  => p_prop_value
      );
    END IF;
    
    v_children_created := v_children_created + 1;
    log('Created child member: ' || p_child_name);
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Failed to create child ' || p_child_name || ': ' || SQLERRM);
  END create_child_member;
  
  FUNCTION get_member_type(p_member IN VARCHAR2) RETURN VARCHAR2 IS
    v_type VARCHAR2(50);
  BEGIN
    -- Determine member type from properties or naming convention
    v_type := ew_api.get_property_value(
                p_app_id      => ew_lb_api.g_app_id,
                p_dim_id      => ew_lb_api.g_dim_id,
                p_member_name => p_member,
                p_prop_name   => 'MemberType'
              );
    
    IF v_type IS NULL THEN
      -- Infer from naming convention
      IF p_member LIKE 'DEPT_%' THEN
        v_type := 'Department';
      ELSIF p_member LIKE 'REG_%' THEN
        v_type := 'Region';
      ELSIF p_member LIKE 'PROD_%' THEN
        v_type := 'ProductGroup';
      END IF;
    END IF;
    
    RETURN v_type;
  END get_member_type;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_parent_member := ew_lb_api.g_new_member_name;
  v_member_type := get_member_type(v_parent_member);
  
  log('Processing new member: ' || v_parent_member);
  log('Member type: ' || NVL(v_member_type, 'Unknown'));
  
  -- Define child templates based on member type
  CASE v_member_type
    
    WHEN 'Department' THEN
      -- Create standard budget categories
      v_templates := t_child_templates();
      v_templates.EXTEND(5);
      
      v_templates(1) := t_child_template(NULL, '_Salaries', 
                                         'AccountType', 'Expense');
      v_templates(2) := t_child_template(NULL, '_Benefits', 
                                         'AccountType', 'Expense');
      v_templates(3) := t_child_template(NULL, '_Operations', 
                                         'AccountType', 'Expense');
      v_templates(4) := t_child_template(NULL, '_Capital', 
                                         'AccountType', 'Asset');
      v_templates(5) := t_child_template(NULL, '_Other', 
                                         'AccountType', 'Expense');
      
      -- Create each template
      FOR i IN 1..v_templates.COUNT LOOP
        create_child_member(
          p_parent     => v_parent_member,
          p_child_name => v_parent_member || v_templates(i).child_suffix,
          p_prop_name  => v_templates(i).prop_name,
          p_prop_value => v_templates(i).prop_value
        );
      END LOOP;
      
    WHEN 'Region' THEN
      -- Create placeholder countries
      IF v_parent_member = 'REG_NA' THEN
        create_child_member(v_parent_member, 'USA', 'Currency', 'USD');
        create_child_member(v_parent_member, 'Canada', 'Currency', 'CAD');
        create_child_member(v_parent_member, 'Mexico', 'Currency', 'MXN');
        
      ELSIF v_parent_member = 'REG_EU' THEN
        create_child_member(v_parent_member, 'Germany', 'Currency', 'EUR');
        create_child_member(v_parent_member, 'France', 'Currency', 'EUR');
        create_child_member(v_parent_member, 'UK', 'Currency', 'GBP');
        
      ELSIF v_parent_member = 'REG_APAC' THEN
        create_child_member(v_parent_member, 'Japan', 'Currency', 'JPY');
        create_child_member(v_parent_member, 'China', 'Currency', 'CNY');
        create_child_member(v_parent_member, 'Australia', 'Currency', 'AUD');
      END IF;
      
    WHEN 'ProductGroup' THEN
      -- Create variance calculation members
      create_child_member(v_parent_member, v_parent_member || '_Actual',
                         'DataType', 'Actual');
      create_child_member(v_parent_member, v_parent_member || '_Budget',
                         'DataType', 'Budget');
      create_child_member(v_parent_member, v_parent_member || '_Variance',
                         'Formula', '[' || v_parent_member || '_Actual] - [' || 
                         v_parent_member || '_Budget]');
      create_child_member(v_parent_member, v_parent_member || '_Variance_Pct',
                         'Formula', '([' || v_parent_member || '_Variance] / [' ||
                         v_parent_member || '_Budget]) * 100');
      
    ELSE
      log('No auto-creation rules for member type: ' || 
          NVL(v_member_type, 'Unknown'));
  END CASE;
  
  IF v_children_created > 0 THEN
    ew_lb_api.g_message := 'Created ' || v_children_created || 
                          ' child members automatically';
  END IF;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    -- Don't fail parent creation
    ew_lb_api.g_status := ew_lb_api.g_success;
    ROLLBACK;
END;
```

## Hierarchy Move Validation and Tracking

🟡 **Level:** Intermediate  
**Purpose:** Validate and track member movements within hierarchy

```sql
/*
  Script: VALIDATE_AND_TRACK_MOVES
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Validate hierarchy moves and maintain movement history
  
  Validates:
  - Circular reference prevention
  - Business rule compliance
  - Impact assessment
  
  Tracks:
  - Movement history
  - Affected calculations
  - Downstream impacts
*/
DECLARE
  c_script_name        VARCHAR2(100) := 'VALIDATE_AND_TRACK_MOVES';
  v_member_name        VARCHAR2(100);
  v_old_parent         VARCHAR2(100);
  v_new_parent         VARCHAR2(100);
  v_validation_passed  BOOLEAN := TRUE;
  v_validation_message VARCHAR2(4000);
  v_impact_count       NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION check_circular_reference(p_member IN VARCHAR2,
                                   p_new_parent IN VARCHAR2) RETURN BOOLEAN IS
    v_current_parent VARCHAR2(100);
    v_iterations     NUMBER := 0;
  BEGIN
    v_current_parent := p_new_parent;
    
    -- Walk up the hierarchy from new parent
    WHILE v_current_parent IS NOT NULL AND v_iterations < 100 LOOP
      IF v_current_parent = p_member THEN
        -- Circular reference detected
        RETURN TRUE;
      END IF;
      
      -- Get parent of current
      SELECT parent_member_name
      INTO   v_current_parent
      FROM   ew_hierarchy
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = v_current_parent
      AND    ROWNUM = 1;
      
      v_iterations := v_iterations + 1;
    END LOOP;
    
    RETURN FALSE;
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN FALSE;
  END check_circular_reference;
  
  FUNCTION assess_move_impact RETURN NUMBER IS
    v_count NUMBER := 0;
  BEGIN
    -- Count affected calculations
    SELECT COUNT(*)
    INTO   v_count
    FROM   ew_member_properties
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    prop_name = 'Formula'
    AND    (prop_value LIKE '%[' || v_member_name || ']%'
            OR prop_value LIKE '%[' || v_old_parent || ']%'
            OR prop_value LIKE '%[' || v_new_parent || ']%');
    
    RETURN v_count;
  END assess_move_impact;
  
  PROCEDURE record_move_history IS
    v_history_id NUMBER;
  BEGIN
    INSERT INTO ew_hierarchy_move_history
      (history_id, app_name, dim_name, member_name,
       old_parent, new_parent, moved_by, moved_date,
       affected_formulas, validation_status)
    VALUES
      (ew_history_seq.NEXTVAL, ew_lb_api.g_app_name,
       ew_lb_api.g_dim_name, v_member_name,
       v_old_parent, v_new_parent, ew_lb_api.g_user_name,
       SYSDATE, v_impact_count,
       CASE WHEN v_validation_passed THEN 'PASSED' ELSE 'FAILED' END)
    RETURNING history_id INTO v_history_id;
    
    log('Move history recorded with ID: ' || v_history_id);
    
    -- Record affected members
    FOR rec IN (SELECT member_name
                FROM   ew_member_properties
                WHERE  app_id = ew_lb_api.g_app_id
                AND    dim_id = ew_lb_api.g_dim_id
                AND    prop_name = 'Formula'
                AND    (prop_value LIKE '%[' || v_member_name || ']%'
                        OR prop_value LIKE '%[' || v_old_parent || ']%'
                        OR prop_value LIKE '%[' || v_new_parent || ']%'))
    LOOP
      INSERT INTO ew_move_impact_details
        (history_id, affected_member, impact_type)
      VALUES
        (v_history_id, rec.member_name, 'FORMULA');
    END LOOP;
    
  END record_move_history;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_member_name := ew_lb_api.g_member_name;
  v_old_parent  := ew_lb_api.g_old_parent_name;
  v_new_parent  := ew_lb_api.g_new_parent_name;
  
  log('Validating move: ' || v_member_name || 
      ' from ' || v_old_parent || ' to ' || v_new_parent);
  
  -- Validation 1: Check for circular reference
  IF check_circular_reference(v_member_name, v_new_parent) THEN
    v_validation_passed := FALSE;
    v_validation_message := 'Circular reference detected';
    log('Validation failed: Circular reference');
  END IF;
  
  -- Validation 2: Check business rules
  IF v_validation_passed THEN
    -- Example: Don't allow moving budget members to actual
    IF v_old_parent LIKE '%Budget%' AND v_new_parent LIKE '%Actual%' THEN
      v_validation_passed := FALSE;
      v_validation_message := 'Cannot move budget members to actual hierarchy';
      log('Validation failed: Business rule violation');
    END IF;
  END IF;
  
  -- Validation 3: Check member type compatibility
  IF v_validation_passed THEN
    DECLARE
      v_old_type VARCHAR2(50);
      v_new_type VARCHAR2(50);
    BEGIN
      SELECT prop_value INTO v_old_type
      FROM   ew_member_properties
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = v_old_parent
      AND    prop_name = 'HierarchyType';
      
      SELECT prop_value INTO v_new_type
      FROM   ew_member_properties
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = v_new_parent
      AND    prop_name = 'HierarchyType';
      
      IF v_old_type != v_new_type THEN
        v_validation_passed := FALSE;
        v_validation_message := 'Incompatible hierarchy types';
        log('Validation failed: Type mismatch');
      END IF;
      
    EXCEPTION
      WHEN OTHERS THEN
        NULL; -- Skip if properties not found
    END;
  END IF;
  
  -- Assess impact
  v_impact_count := assess_move_impact();
  log('Move will impact ' || v_impact_count || ' formulas');
  
  -- Record history (pass or fail)
  record_move_history();
  
  -- Set result
  IF NOT v_validation_passed THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := v_validation_message;
  ELSIF v_impact_count > 10 THEN
    ew_lb_api.g_status  := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Move will impact ' || v_impact_count || 
                           ' calculations. Please review.';
  ELSE
    ew_lb_api.g_message := 'Move validated successfully';
  END IF;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Move validation error: ' || SQLERRM;
    ROLLBACK;
END;
```

## Cascading Deletion Handler

🔴 **Level:** Advanced  
**Purpose:** Handle complex member deletion with cascading effects

```sql
/*
  Script: CASCADE_DELETION_HANDLER
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Manage cascading effects of member deletion
  
  Handles:
  - Orphaned references cleanup
  - Formula adjustments
  - Shared member removal
  - Audit trail
  - Rollback capability
*/
DECLARE
  c_script_name         VARCHAR2(100) := 'CASCADE_DELETION_HANDLER';
  v_member_to_delete    VARCHAR2(100);
  v_deletion_id         NUMBER;
  v_children_count      NUMBER;
  v_reference_count     NUMBER;
  v_can_delete          BOOLEAN := TRUE;
  v_deletion_impact     CLOB;
  
  TYPE t_affected_member IS RECORD (
    member_name   VARCHAR2(100),
    prop_name     VARCHAR2(100),
    old_value     VARCHAR2(4000),
    new_value     VARCHAR2(4000),
    impact_type   VARCHAR2(50)
  );
  
  TYPE t_affected_members IS TABLE OF t_affected_member;
  v_affected_members t_affected_members := t_affected_members();
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION count_children(p_member IN VARCHAR2) RETURN NUMBER IS
    v_count NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO   v_count
    FROM   ew_hierarchy
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    parent_member_name = p_member;
    
    RETURN v_count;
  END count_children;
  
  FUNCTION count_references(p_member IN VARCHAR2) RETURN NUMBER IS
    v_count NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO   v_count
    FROM   ew_member_properties
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    prop_name IN ('Formula', 'ValidationRule', 'SourceMember')
    AND    prop_value LIKE '%' || p_member || '%';
    
    RETURN v_count;
  END count_references;
  
  PROCEDURE analyze_deletion_impact IS
    i NUMBER := 0;
  BEGIN
    -- Find all formulas referencing this member
    FOR rec IN (SELECT member_name, prop_name, prop_value
                FROM   ew_member_properties
                WHERE  app_id = ew_lb_api.g_app_id
                AND    dim_id = ew_lb_api.g_dim_id
                AND    prop_name = 'Formula'
                AND    prop_value LIKE '%[' || v_member_to_delete || ']%')
    LOOP
      i := i + 1;
      v_affected_members.EXTEND;
      v_affected_members(i).member_name := rec.member_name;
      v_affected_members(i).prop_name := rec.prop_name;
      v_affected_members(i).old_value := rec.prop_value;
      
      -- Determine new formula (remove reference or set to #Missing)
      v_affected_members(i).new_value := 
        REPLACE(rec.prop_value, 
                '[' || v_member_to_delete || ']', 
                '#Missing');
      
      v_affected_members(i).impact_type := 'FORMULA_UPDATE';
      
      log('Formula impact on ' || rec.member_name);
    END LOOP;
    
    -- Find shared members
    FOR rec IN (SELECT member_name, parent_member_name
                FROM   ew_hierarchy
                WHERE  app_id = ew_lb_api.g_app_id
                AND    dim_id = ew_lb_api.g_dim_id
                AND    member_name = v_member_to_delete
                AND    is_shared = 'Y')
    LOOP
      i := i + 1;
      v_affected_members.EXTEND;
      v_affected_members(i).member_name := rec.member_name;
      v_affected_members(i).prop_name := 'SharedMember';
      v_affected_members(i).old_value := rec.parent_member_name;
      v_affected_members(i).new_value := 'DELETED';
      v_affected_members(i).impact_type := 'SHARED_REMOVAL';
      
      log('Shared member in: ' || rec.parent_member_name);
    END LOOP;
    
  END analyze_deletion_impact;
  
  PROCEDURE create_deletion_backup IS
  BEGIN
    -- Create backup record
    INSERT INTO ew_deletion_backup
      (deletion_id, app_name, dim_name, member_name,
       deletion_date, deleted_by, backup_data)
    VALUES
      (ew_deletion_seq.NEXTVAL, ew_lb_api.g_app_name,
       ew_lb_api.g_dim_name, v_member_to_delete,
       SYSDATE, ew_lb_api.g_user_name,
       ew_api.export_member_to_json(
         p_app_id => ew_lb_api.g_app_id,
         p_dim_id => ew_lb_api.g_dim_id,
         p_member_name => v_member_to_delete
       ))
    RETURNING deletion_id INTO v_deletion_id;
    
    -- Backup affected members
    FOR i IN 1..v_affected_members.COUNT LOOP
      INSERT INTO ew_deletion_impact
        (deletion_id, affected_member, impact_type,
         old_value, new_value)
      VALUES
        (v_deletion_id, v_affected_members(i).member_name,
         v_affected_members(i).impact_type,
         v_affected_members(i).old_value,
         v_affected_members(i).new_value);
    END LOOP;
    
    log('Deletion backup created with ID: ' || v_deletion_id);
    
  END create_deletion_backup;
  
  PROCEDURE apply_cascading_changes IS
  BEGIN
    FOR i IN 1..v_affected_members.COUNT LOOP
      BEGIN
        CASE v_affected_members(i).impact_type
          
          WHEN 'FORMULA_UPDATE' THEN
            -- Update formula to remove reference
            UPDATE ew_member_properties
            SET    prop_value = v_affected_members(i).new_value,
                   last_modified = SYSDATE,
                   modified_by = ew_lb_api.g_user_name
            WHERE  app_id = ew_lb_api.g_app_id
            AND    dim_id = ew_lb_api.g_dim_id
            AND    member_name = v_affected_members(i).member_name
            AND    prop_name = v_affected_members(i).prop_name;
            
            log('Updated formula for: ' || v_affected_members(i).member_name);
            
          WHEN 'SHARED_REMOVAL' THEN
            -- Remove shared member
            DELETE FROM ew_hierarchy
            WHERE  app_id = ew_lb_api.g_app_id
            AND    dim_id = ew_lb_api.g_dim_id
            AND    member_name = v_member_to_delete
            AND    parent_member_name = v_affected_members(i).old_value
            AND    is_shared = 'Y';
            
            log('Removed shared member from: ' || 
                v_affected_members(i).old_value);
            
        END CASE;
        
      EXCEPTION
        WHEN OTHERS THEN
          log('Failed to apply change: ' || SQLERRM);
      END;
    END LOOP;
  END apply_cascading_changes;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_member_to_delete := ew_lb_api.g_member_name;
  
  log('Processing deletion request for: ' || v_member_to_delete);
  
  -- Check if member has children
  v_children_count := count_children(v_member_to_delete);
  IF v_children_count > 0 THEN
    v_can_delete := FALSE;
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Cannot delete member with ' || 
                          v_children_count || ' children';
    log('Deletion blocked: Has children');
    RETURN;
  END IF;
  
  -- Count references
  v_reference_count := count_references(v_member_to_delete);
  log('Found ' || v_reference_count || ' references to member');
  
  -- Analyze impact
  analyze_deletion_impact();
  
  -- Check deletion rules
  DECLARE
    v_protected VARCHAR2(1);
  BEGIN
    v_protected := ew_api.get_property_value(
                     p_app_id      => ew_lb_api.g_app_id,
                     p_dim_id      => ew_lb_api.g_dim_id,
                     p_member_name => v_member_to_delete,
                     p_prop_name   => 'Protected'
                   );
    
    IF v_protected = 'Y' THEN
      v_can_delete := FALSE;
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Member is protected from deletion';
      log('Deletion blocked: Protected member');
      RETURN;
    END IF;
  END;
  
  IF v_can_delete THEN
    -- Create backup before deletion
    create_deletion_backup();
    
    -- Apply cascading changes
    apply_cascading_changes();
    
    -- Log successful preparation
    log('Deletion prepared successfully');
    
    -- Set message
    IF v_affected_members.COUNT > 0 THEN
      ew_lb_api.g_status := ew_lb_api.g_warning;
      ew_lb_api.g_message := 'Deletion will affect ' || 
                            v_affected_members.COUNT || 
                            ' other members. Backup ID: ' || v_deletion_id;
    ELSE
      ew_lb_api.g_message := 'Member can be safely deleted. Backup ID: ' || 
                            v_deletion_id;
    END IF;
    
    COMMIT;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Deletion handler error: ' || SQLERRM;
    ROLLBACK;
END;
```

## Member Rename Impact Analysis

🔴 **Level:** Advanced  
**Purpose:** Analyze and handle the impact of member renaming

```sql
/*
  Script: MEMBER_RENAME_HANDLER
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Handle member rename with full impact analysis
  
  Features:
  - Update all references
  - Maintain rename history
  - Handle external references
  - Notification system
*/
DECLARE
  c_script_name      VARCHAR2(100) := 'MEMBER_RENAME_HANDLER';
  v_old_name         VARCHAR2(100);
  v_new_name         VARCHAR2(100);
  v_updates_required NUMBER := 0;
  v_updates_applied  NUMBER := 0;
  v_external_refs    NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  PROCEDURE update_formula_references IS
    v_count NUMBER := 0;
  BEGIN
    -- Update all formulas containing the old member name
    FOR rec IN (SELECT member_name, prop_value
                FROM   ew_member_properties
                WHERE  app_id = ew_lb_api.g_app_id
                AND    dim_id = ew_lb_api.g_dim_id
                AND    prop_name = 'Formula'
                AND    prop_value LIKE '%[' || v_old_name || ']%')
    LOOP
      UPDATE ew_member_properties
      SET    prop_value = REPLACE(prop_value, 
                                  '[' || v_old_name || ']',
                                  '[' || v_new_name || ']'),
             last_modified = SYSDATE,
             modified_by = ew_lb_api.g_user_name || '_RENAME'
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = rec.member_name
      AND    prop_name = 'Formula';
      
      v_count := v_count + 1;
    END LOOP;
    
    log('Updated ' || v_count || ' formula references');
    v_updates_applied := v_updates_applied + v_count;
    
  END update_formula_references;
  
  PROCEDURE update_mapping_references IS
    v_count NUMBER := 0;
  BEGIN
    -- Update dimension mapping references
    UPDATE ew_dimension_mappings
    SET    source_member = v_new_name,
           last_modified = SYSDATE
    WHERE  source_member = v_old_name
    AND    source_app = ew_lb_api.g_app_name
    AND    source_dim = ew_lb_api.g_dim_name;
    
    v_count := SQL%ROWCOUNT;
    
    UPDATE ew_dimension_mappings
    SET    target_member = v_new_name,
           last_modified = SYSDATE
    WHERE  target_member = v_old_name
    AND    target_app = ew_lb_api.g_app_name
    AND    target_dim = ew_lb_api.g_dim_name;
    
    v_count := v_count + SQL%ROWCOUNT;
    
    log('Updated ' || v_count || ' mapping references');
    v_updates_applied := v_updates_applied + v_count;
    
  END update_mapping_references;
  
  PROCEDURE record_rename_history IS
    v_rename_id NUMBER;
  BEGIN
    INSERT INTO ew_rename_history
      (rename_id, app_name, dim_name, old_name, new_name,
       renamed_by, renamed_date, formulas_updated, 
       mappings_updated, external_refs)
    VALUES
      (ew_rename_seq.NEXTVAL, ew_lb_api.g_app_name,
       ew_lb_api.g_dim_name, v_old_name, v_new_name,
       ew_lb_api.g_user_name, SYSDATE,
       v_updates_applied, v_updates_required, v_external_refs)
    RETURNING rename_id INTO v_rename_id;
    
    log('Rename history recorded with ID: ' || v_rename_id);
    
    -- Store detailed changes
    INSERT INTO ew_rename_details
      (rename_id, change_type, object_name, old_value, new_value)
    SELECT v_rename_id, 
           'FORMULA',
           member_name,
           prop_value,
           REPLACE(prop_value, '[' || v_old_name || ']', 
                              '[' || v_new_name || ']')
    FROM   ew_member_properties
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    prop_name = 'Formula'
    AND    prop_value LIKE '%[' || v_old_name || ']%';
    
  END record_rename_history;
  
  PROCEDURE check_external_references IS
  BEGIN
    -- Check for references in other applications
    SELECT COUNT(*)
    INTO   v_external_refs
    FROM   ew_cross_app_references
    WHERE  referenced_member = v_old_name
    AND    referenced_app = ew_lb_api.g_app_name
    AND    referenced_dim = ew_lb_api.g_dim_name;
    
    IF v_external_refs > 0 THEN
      -- Send notifications about external references
      FOR rec IN (SELECT DISTINCT source_app, owner_email
                  FROM   ew_cross_app_references r
                  JOIN   ew_applications a ON r.source_app = a.app_name
                  WHERE  referenced_member = v_old_name
                  AND    referenced_app = ew_lb_api.g_app_name
                  AND    referenced_dim = ew_lb_api.g_dim_name)
      LOOP
        ew_email_api.send_email(
          p_to      => rec.owner_email,
          p_subject => 'Member Rename Alert: ' || v_old_name,
          p_body    => 'Member ' || v_old_name || ' has been renamed to ' ||
                      v_new_name || ' in ' || ew_lb_api.g_app_name || '.' ||
                      ew_lb_api.g_dim_name || '. Please update references in ' ||
                      rec.source_app || '.',
          p_priority => 'HIGH'
        );
      END LOOP;
    END IF;
    
    log('Found ' || v_external_refs || ' external references');
    
  END check_external_references;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_old_name := ew_lb_api.g_old_member_name;
  v_new_name := ew_lb_api.g_new_member_name;
  
  log('Processing rename: ' || v_old_name || ' -> ' || v_new_name);
  
  -- Count required updates
  SELECT COUNT(*)
  INTO   v_updates_required
  FROM   ew_member_properties
  WHERE  app_id = ew_lb_api.g_app_id
  AND    dim_id = ew_lb_api.g_dim_id
  AND    prop_value LIKE '%' || v_old_name || '%';
  
  log('Updates required: ' || v_updates_required);
  
  -- Validate new name
  IF NOT REGEXP_LIKE(v_new_name, '^[A-Za-z][A-Za-z0-9_]{0,99}$') THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Invalid member name format';
    RETURN;
  END IF;
  
  -- Check if new name already exists
  DECLARE
    v_exists NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO   v_exists
    FROM   ew_hierarchy
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    member_name = v_new_name;
    
    IF v_exists > 0 THEN
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Member name already exists: ' || v_new_name;
      RETURN;
    END IF;
  END;
  
  -- Update all references
  update_formula_references();
  update_mapping_references();
  check_external_references();
  
  -- Record history
  record_rename_history();
  
  -- Set result message
  IF v_external_refs > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Rename completed. Updated ' || v_updates_applied ||
                          ' references. WARNING: ' || v_external_refs ||
                          ' external references need manual update.';
  ELSE
    ew_lb_api.g_message := 'Rename completed successfully. Updated ' ||
                          v_updates_applied || ' references.';
  END IF;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Rename handler error: ' || SQLERRM;
    ROLLBACK;
END;
```

## Testing Hierarchy Action Scripts

### Hierarchy Action Test Framework

```sql
/*
  Script: TEST_HIERARCHY_ACTIONS
  Purpose: Test framework for hierarchy action scripts
*/
DECLARE
  c_script_name VARCHAR2(100) := 'TEST_HIERARCHY_ACTIONS';
  v_test_member VARCHAR2(100);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END log;
  
  PROCEDURE test_member_creation IS
  BEGIN
    v_test_member := 'TEST_' || TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS');
    
    -- Set context for creation
    ew_lb_api.g_new_member_name := v_test_member;
    ew_lb_api.g_parent_member_name := 'TestParent';
    ew_lb_api.g_action := 'CREATE';
    
    log('Testing member creation: ' || v_test_member);
    
    -- Execute creation logic
    -- (Insert your hierarchy action code here)
    
    log('Creation test completed');
  END test_member_creation;
  
  PROCEDURE test_member_move IS
  BEGIN
    -- Set context for move
    ew_lb_api.g_member_name := v_test_member;
    ew_lb_api.g_old_parent_name := 'TestParent';
    ew_lb_api.g_new_parent_name := 'NewTestParent';
    ew_lb_api.g_action := 'MOVE';
    
    log('Testing member move');
    
    -- Execute move logic
    -- (Insert your hierarchy action code here)
    
    log('Move test completed');
  END test_member_move;
  
  PROCEDURE test_member_rename IS
  BEGIN
    -- Set context for rename
    ew_lb_api.g_old_member_name := v_test_member;
    ew_lb_api.g_new_member_name := v_test_member || '_RENAMED';
    ew_lb_api.g_action := 'RENAME';
    
    log('Testing member rename');
    
    -- Execute rename logic
    -- (Insert your hierarchy action code here)
    
    log('Rename test completed');
  END test_member_rename;
  
BEGIN
  log('Starting hierarchy action tests');
  
  test_member_creation();
  test_member_move();
  test_member_rename();
  
  log('All hierarchy action tests completed');
  
END;
```

## Best Practices

1. **Always create audit trails** - Track who, what, when, why
2. **Validate before allowing changes** - Prevent data corruption
3. **Handle cascading effects** - Update dependent objects
4. **Create backups before deletion** - Enable rollback capability
5. **Check for circular references** - Maintain hierarchy integrity
6. **Notify stakeholders** - Keep users informed of impacts
7. **Use batch processing** - For performance with large hierarchies
8. **Implement rollback procedures** - Provide recovery options

## Next Steps

- See [Advanced Patterns](advanced-patterns.md)
- Review [Performance Optimization](../advanced/performance.md)
- Learn about [API Reference](../api/)