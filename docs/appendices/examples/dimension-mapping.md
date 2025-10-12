# Dimension Mapping Examples

Dimension mapping scripts synchronize hierarchies and member properties across different EPM applications, ensuring consistency and automating cross-application data management.

## HFM to Planning Synchronization

🟢 **Level:** Basic  
**Purpose:** Map HFM entities to Planning entities with property translation

```sql
/*
  Script: MAP_HFM_TO_PLANNING
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Synchronize HFM Entity dimension to Planning Entity dimension
  
  Mapping Rules:
  - Member names remain the same
  - HFM currencies map to Planning currencies
  - Only active entities are synchronized
  - Consolidation methods are translated
*/
DECLARE
  c_script_name        VARCHAR2(100) := 'MAP_HFM_TO_PLANNING';
  v_source_member      VARCHAR2(100);
  v_target_member      VARCHAR2(100);
  v_source_currency    VARCHAR2(10);
  v_target_currency    VARCHAR2(10);
  v_consolidation      VARCHAR2(50);
  v_status            VARCHAR2(20);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION map_currency(p_hfm_currency IN VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Map HFM currency codes to Planning codes
    RETURN CASE p_hfm_currency
             WHEN 'USD' THEN 'USD'
             WHEN 'EUR' THEN 'EUR'
             WHEN 'GBP' THEN 'GBP'
             WHEN 'JPY' THEN 'JPY'
             WHEN 'CAD' THEN 'CAD'
             WHEN 'AUD' THEN 'AUD'
             WHEN 'CHF' THEN 'CHF'
             WHEN 'CNY' THEN 'CNY'
             ELSE 'USD' -- Default
           END;
  END map_currency;
  
  FUNCTION map_consolidation(p_hfm_method IN VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Map HFM consolidation methods to Planning
    RETURN CASE p_hfm_method
             WHEN 'SUBSIDIARY' THEN 'Addition'
             WHEN 'PROPORTIONAL' THEN 'Addition'
             WHEN 'EQUITY' THEN 'Ignore'
             WHEN 'NOTCONSOLIDATED' THEN 'Ignore'
             ELSE 'Addition'
           END;
  END map_consolidation;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Get source member information from HFM
  v_source_member := ew_lb_api.g_member_name;
  v_status := ew_lb_api.g_prop_value; -- Assuming this triggers on status change
  
  log('Processing HFM member: ' || v_source_member);
  log('Status: ' || v_status);
  
  -- Only sync active entities
  IF v_status != 'Active' THEN
    log('Skipping inactive entity');
    RETURN;
  END IF;
  
  -- Get HFM properties
  v_source_currency := ew_api.get_property_value(
                         p_app_id      => ew_lb_api.g_app_id,
                         p_dim_id      => ew_lb_api.g_dim_id,
                         p_member_name => v_source_member,
                         p_prop_name   => 'DefCurrency'
                       );
  
  v_consolidation := ew_api.get_property_value(
                       p_app_id      => ew_lb_api.g_app_id,
                       p_dim_id      => ew_lb_api.g_dim_id,
                       p_member_name => v_source_member,
                       p_prop_name   => 'ConsolidationMethod'
                     );
  
  -- Map values for Planning
  v_target_member := v_source_member; -- Keep same member name
  v_target_currency := map_currency(v_source_currency);
  v_consolidation := map_consolidation(v_consolidation);
  
  log('Mapped currency: ' || v_source_currency || ' -> ' || v_target_currency);
  log('Mapped consolidation: ' || v_consolidation);
  
  -- Set output parameters for Planning
  ew_lb_api.g_target_member_name := v_target_member;
  ew_lb_api.g_target_parent_name := ew_lb_api.g_parent_member_name;
  
  -- Set Planning properties
  ew_lb_api.set_target_property('Currency', v_target_currency);
  ew_lb_api.set_target_property('ConsolidationOperator', v_consolidation);
  ew_lb_api.set_target_property('DataStorage', 'StoreData');
  ew_lb_api.set_target_property('TwoPassCalculation', 'False');
  
  -- Copy description if exists
  DECLARE
    v_description VARCHAR2(500);
  BEGIN
    v_description := ew_api.get_property_value(
                       p_app_id      => ew_lb_api.g_app_id,
                       p_dim_id      => ew_lb_api.g_dim_id,
                       p_member_name => v_source_member,
                       p_prop_name   => 'Description'
                     );
    
    IF v_description IS NOT NULL THEN
      ew_lb_api.set_target_property('Alias', v_description);
    END IF;
  END;
  
  log('Mapping completed successfully');
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Mapping failed: ' || SQLERRM;
END;
```

## Account Dimension Cross-Application Sync

🟡 **Level:** Intermediate  
**Purpose:** Synchronize account hierarchies with intelligent property mapping

```sql
/*
  Script: MAP_ACCOUNTS_CROSS_APP
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Intelligent account mapping across applications
  
  Features:
  - Account type detection and mapping
  - Formula translation
  - Variance reporting flag sync
  - Time balance property mapping
*/
DECLARE
  c_script_name       VARCHAR2(100) := 'MAP_ACCOUNTS_CROSS_APP';
  v_source_app        VARCHAR2(50);
  v_target_app        VARCHAR2(50);
  v_account_number    VARCHAR2(50);
  v_account_type      VARCHAR2(50);
  v_time_balance      VARCHAR2(50);
  v_variance_rep      VARCHAR2(50);
  v_formula           VARCHAR2(4000);
  v_mapped_formula    VARCHAR2(4000);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION detect_account_type(p_account IN VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Intelligent account type detection based on account number
    IF p_account LIKE '1%' THEN
      RETURN 'Asset';
    ELSIF p_account LIKE '2%' THEN
      RETURN 'Liability';
    ELSIF p_account LIKE '3%' THEN
      RETURN 'Equity';
    ELSIF p_account LIKE '4%' THEN
      RETURN 'Revenue';
    ELSIF p_account LIKE '5%' OR p_account LIKE '6%' THEN
      RETURN 'Expense';
    ELSIF p_account LIKE '9%' THEN
      RETURN 'Statistical';
    ELSE
      -- Check parent's account type
      DECLARE
        v_parent_type VARCHAR2(50);
      BEGIN
        SELECT prop_value
        INTO   v_parent_type
        FROM   ew_member_properties
        WHERE  app_id = ew_lb_api.g_app_id
        AND    dim_id = ew_lb_api.g_dim_id
        AND    member_name = ew_lb_api.g_parent_member_name
        AND    prop_name = 'AccountType';
        
        RETURN v_parent_type;
      EXCEPTION
        WHEN OTHERS THEN
          RETURN 'Expense'; -- Default
      END;
    END IF;
  END detect_account_type;
  
  FUNCTION map_time_balance(p_account_type IN VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Map time balance based on account type
    RETURN CASE p_account_type
             WHEN 'Asset' THEN 'Balance'
             WHEN 'Liability' THEN 'Balance'
             WHEN 'Equity' THEN 'Balance'
             WHEN 'Revenue' THEN 'Flow'
             WHEN 'Expense' THEN 'Flow'
             WHEN 'Statistical' THEN 'Average'
             ELSE 'Flow'
           END;
  END map_time_balance;
  
  FUNCTION translate_formula(p_formula IN VARCHAR2,
                            p_source_app IN VARCHAR2,
                            p_target_app IN VARCHAR2) RETURN VARCHAR2 IS
    v_translated VARCHAR2(4000);
  BEGIN
    v_translated := p_formula;
    
    -- Replace application-specific references
    IF p_source_app = 'HFM' AND p_target_app = 'Planning' THEN
      -- HFM to Planning formula translation
      v_translated := REPLACE(v_translated, '[Account].', '');
      v_translated := REPLACE(v_translated, '[ICP].', '');
      v_translated := REPLACE(v_translated, '[None]', '#Missing');
      v_translated := REPLACE(v_translated, '.CurrentMember', '');
      
    ELSIF p_source_app = 'Planning' AND p_target_app = 'Essbase' THEN
      -- Planning to Essbase formula translation
      v_translated := REPLACE(v_translated, '@MEMBER(@NAME(', '@');
      v_translated := REPLACE(v_translated, '))', ')');
      v_translated := REPLACE(v_translated, 'IIF(', '@IF(');
    END IF;
    
    RETURN v_translated;
    
  END translate_formula;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_account_number := ew_lb_api.g_member_name;
  v_source_app := ew_lb_api.g_app_name;
  v_target_app := ew_lb_api.g_target_app_name;
  
  log('Mapping account: ' || v_account_number);
  log('Source app: ' || v_source_app || ', Target app: ' || v_target_app);
  
  -- Detect or get account type
  v_account_type := ew_api.get_property_value(
                      p_app_id      => ew_lb_api.g_app_id,
                      p_dim_id      => ew_lb_api.g_dim_id,
                      p_member_name => v_account_number,
                      p_prop_name   => 'AccountType'
                    );
  
  IF v_account_type IS NULL THEN
    v_account_type := detect_account_type(v_account_number);
    log('Detected account type: ' || v_account_type);
  END IF;
  
  -- Map time balance property
  v_time_balance := map_time_balance(v_account_type);
  
  -- Determine variance reporting
  v_variance_rep := CASE v_account_type
                      WHEN 'Revenue' THEN 'NonExpense'
                      WHEN 'Asset' THEN 'NonExpense'
                      WHEN 'Liability' THEN 'Expense'
                      WHEN 'Expense' THEN 'Expense'
                      ELSE 'NonExpense'
                    END;
  
  -- Get and translate formula if exists
  v_formula := ew_api.get_property_value(
                 p_app_id      => ew_lb_api.g_app_id,
                 p_dim_id      => ew_lb_api.g_dim_id,
                 p_member_name => v_account_number,
                 p_prop_name   => 'Formula'
               );
  
  IF v_formula IS NOT NULL THEN
    v_mapped_formula := translate_formula(v_formula, v_source_app, v_target_app);
    log('Formula translated: ' || SUBSTR(v_mapped_formula, 1, 200));
  END IF;
  
  -- Set target member and properties
  ew_lb_api.g_target_member_name := v_account_number;
  ew_lb_api.g_target_parent_name := ew_lb_api.g_parent_member_name;
  
  -- Set mapped properties
  ew_lb_api.set_target_property('AccountType', v_account_type);
  ew_lb_api.set_target_property('TimeBalance', v_time_balance);
  ew_lb_api.set_target_property('VarianceReporting', v_variance_rep);
  
  IF v_mapped_formula IS NOT NULL THEN
    ew_lb_api.set_target_property('MemberFormula', v_mapped_formula);
    ew_lb_api.set_target_property('DataStorage', 'DynamicCalc');
  ELSE
    ew_lb_api.set_target_property('DataStorage', 'StoreData');
  END IF;
  
  -- Set consolidation operator based on account type
  IF v_account_type IN ('Asset', 'Liability', 'Equity') THEN
    ew_lb_api.set_target_property('ConsolidationOperator', '+');
  ELSE
    ew_lb_api.set_target_property('ConsolidationOperator', 
                                  ew_api.get_property_value(
                                    p_app_id      => ew_lb_api.g_app_id,
                                    p_dim_id      => ew_lb_api.g_dim_id,
                                    p_member_name => v_account_number,
                                    p_prop_name   => 'ConsolidationOperator'
                                  ));
  END IF;
  
  log('Account mapping completed');
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Account mapping failed: ' || SQLERRM;
END;
```

## Multi-Application Hierarchy Synchronization

🔴 **Level:** Advanced  
**Purpose:** Complex multi-application synchronization with conflict resolution

```sql
/*
  Script: MAP_MULTI_APP_HIERARCHY
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Synchronize hierarchies across multiple EPM applications
  
  Features:
  - Sync to multiple target applications
  - Conflict detection and resolution
  - Shared member handling
  - Alternate hierarchy support
  - Audit trail
*/
DECLARE
  c_script_name         VARCHAR2(100) := 'MAP_MULTI_APP_HIERARCHY';
  TYPE t_app_list IS TABLE OF VARCHAR2(50);
  v_target_apps         t_app_list := t_app_list('Planning', 'Essbase', 'FCCS');
  v_source_member       VARCHAR2(100);
  v_source_parent       VARCHAR2(100);
  v_sync_count          NUMBER := 0;
  v_error_count         NUMBER := 0;
  v_conflict_detected   BOOLEAN := FALSE;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION check_member_exists(p_app_name IN VARCHAR2,
                               p_dim_name IN VARCHAR2,
                               p_member   IN VARCHAR2) RETURN BOOLEAN IS
    v_count NUMBER;
  BEGIN
    SELECT COUNT(*)
    INTO   v_count
    FROM   ew_hierarchy h
    JOIN   ew_applications a ON h.app_id = a.app_id
    JOIN   ew_dimensions d ON h.dim_id = d.dim_id
    WHERE  a.app_name = p_app_name
    AND    d.dim_name = p_dim_name
    AND    h.member_name = p_member;
    
    RETURN v_count > 0;
  END check_member_exists;
  
  FUNCTION detect_conflict(p_app_name    IN VARCHAR2,
                          p_member_name IN VARCHAR2,
                          p_parent_name IN VARCHAR2) RETURN BOOLEAN IS
    v_existing_parent VARCHAR2(100);
  BEGIN
    -- Check if member exists with different parent
    SELECT parent_member_name
    INTO   v_existing_parent
    FROM   ew_hierarchy h
    JOIN   ew_applications a ON h.app_id = a.app_id
    WHERE  a.app_name = p_app_name
    AND    h.member_name = p_member_name
    AND    ROWNUM = 1;
    
    IF v_existing_parent != p_parent_name THEN
      log('Conflict detected: ' || p_member_name || 
          ' exists under ' || v_existing_parent || 
          ' in ' || p_app_name);
      RETURN TRUE;
    END IF;
    
    RETURN FALSE;
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN FALSE; -- No conflict if member doesn't exist
  END detect_conflict;
  
  PROCEDURE resolve_conflict(p_app_name    IN VARCHAR2,
                            p_member_name IN VARCHAR2,
                            p_parent_name IN VARCHAR2) IS
    v_resolution_type VARCHAR2(50);
  BEGIN
    -- Get conflict resolution strategy from configuration
    SELECT resolution_strategy
    INTO   v_resolution_type
    FROM   ew_sync_configuration
    WHERE  source_app = ew_lb_api.g_app_name
    AND    target_app = p_app_name
    AND    ROWNUM = 1;
    
    CASE v_resolution_type
      WHEN 'CREATE_SHARED' THEN
        -- Create as shared member
        log('Creating shared member: ' || p_member_name);
        ew_api.create_shared_member(
          p_app_name    => p_app_name,
          p_dim_name    => ew_lb_api.g_dim_name,
          p_member_name => p_member_name,
          p_parent_name => p_parent_name
        );
        
      WHEN 'SKIP' THEN
        -- Skip this member
        log('Skipping conflicted member: ' || p_member_name);
        
      WHEN 'MOVE' THEN
        -- Move to new parent
        log('Moving member to new parent');
        ew_api.move_member(
          p_app_name    => p_app_name,
          p_dim_name    => ew_lb_api.g_dim_name,
          p_member_name => p_member_name,
          p_parent_name => p_parent_name
        );
        
      ELSE
        -- Default: create alternate hierarchy
        log('Creating in alternate hierarchy');
        ew_api.create_member(
          p_app_name    => p_app_name,
          p_dim_name    => ew_lb_api.g_dim_name || '_Alt',
          p_member_name => p_member_name,
          p_parent_name => p_parent_name
        );
    END CASE;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Conflict resolution failed: ' || SQLERRM);
  END resolve_conflict;
  
  PROCEDURE sync_to_application(p_target_app IN VARCHAR2) IS
    v_app_id     NUMBER;
    v_dim_id     NUMBER;
    v_sync_success BOOLEAN := TRUE;
  BEGIN
    log('Syncing to ' || p_target_app);
    
    -- Get target application and dimension IDs
    BEGIN
      SELECT a.app_id, d.dim_id
      INTO   v_app_id, v_dim_id
      FROM   ew_applications a
      JOIN   ew_dimensions d ON a.app_id = d.app_id
      WHERE  a.app_name = p_target_app
      AND    d.dim_name = ew_lb_api.g_dim_name;
    EXCEPTION
      WHEN NO_DATA_FOUND THEN
        log('Target dimension not found in ' || p_target_app);
        RETURN;
    END;
    
    -- Check for conflicts
    IF detect_conflict(p_target_app, v_source_member, v_source_parent) THEN
      v_conflict_detected := TRUE;
      resolve_conflict(p_target_app, v_source_member, v_source_parent);
    ELSE
      -- No conflict, proceed with normal sync
      BEGIN
        -- Create or update member
        IF check_member_exists(p_target_app, ew_lb_api.g_dim_name, v_source_member) THEN
          -- Update existing member
          ew_api.update_member(
            p_app_id      => v_app_id,
            p_dim_id      => v_dim_id,
            p_member_name => v_source_member,
            p_parent_name => v_source_parent
          );
        ELSE
          -- Create new member
          ew_api.create_member(
            p_app_id      => v_app_id,
            p_dim_id      => v_dim_id,
            p_member_name => v_source_member,
            p_parent_name => v_source_parent
          );
        END IF;
        
        -- Sync properties
        FOR prop IN (SELECT prop_name, prop_value
                    FROM   ew_member_properties
                    WHERE  app_id = ew_lb_api.g_app_id
                    AND    dim_id = ew_lb_api.g_dim_id
                    AND    member_name = v_source_member
                    AND    prop_name NOT IN ('LastModified', 'CreatedBy'))
        LOOP
          BEGIN
            ew_api.set_property_value(
              p_app_id      => v_app_id,
              p_dim_id      => v_dim_id,
              p_member_name => v_source_member,
              p_prop_name   => prop.prop_name,
              p_prop_value  => prop.prop_value
            );
          EXCEPTION
            WHEN OTHERS THEN
              log('Failed to sync property ' || prop.prop_name || ': ' || SQLERRM);
          END;
        END LOOP;
        
      EXCEPTION
        WHEN OTHERS THEN
          log('Sync failed to ' || p_target_app || ': ' || SQLERRM);
          v_sync_success := FALSE;
          v_error_count := v_error_count + 1;
      END;
    END IF;
    
    -- Log sync audit
    INSERT INTO ew_sync_audit
      (sync_id, source_app, target_app, member_name, 
       sync_date, sync_status, conflict_detected)
    VALUES
      (ew_sync_seq.NEXTVAL, ew_lb_api.g_app_name, p_target_app,
       v_source_member, SYSDATE, 
       CASE WHEN v_sync_success THEN 'SUCCESS' ELSE 'FAILED' END,
       CASE WHEN v_conflict_detected THEN 'Y' ELSE 'N' END);
    
    IF v_sync_success THEN
      v_sync_count := v_sync_count + 1;
    END IF;
    
  END sync_to_application;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_source_member := ew_lb_api.g_member_name;
  v_source_parent := ew_lb_api.g_parent_member_name;
  
  log('Starting multi-application sync for: ' || v_source_member);
  
  -- Check if member should be synced
  DECLARE
    v_sync_flag VARCHAR2(1);
  BEGIN
    v_sync_flag := ew_api.get_property_value(
                     p_app_id      => ew_lb_api.g_app_id,
                     p_dim_id      => ew_lb_api.g_dim_id,
                     p_member_name => v_source_member,
                     p_prop_name   => 'SyncEnabled'
                   );
    
    IF NVL(v_sync_flag, 'Y') = 'N' THEN
      log('Sync disabled for this member');
      RETURN;
    END IF;
  END;
  
  -- Sync to each target application
  FOR i IN 1..v_target_apps.COUNT LOOP
    BEGIN
      sync_to_application(v_target_apps(i));
    EXCEPTION
      WHEN OTHERS THEN
        log('Critical error syncing to ' || v_target_apps(i) || ': ' || SQLERRM);
        v_error_count := v_error_count + 1;
    END;
  END LOOP;
  
  -- Set return status
  IF v_error_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Sync completed with ' || v_error_count || 
                          ' errors. Successfully synced to ' || 
                          v_sync_count || ' applications.';
  ELSE
    ew_lb_api.g_message := 'Successfully synced to ' || 
                          v_sync_count || ' applications.';
  END IF;
  
  IF v_conflict_detected THEN
    ew_lb_api.g_message := ew_lb_api.g_message || 
                          ' Conflicts were detected and resolved.';
  END IF;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Critical exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Multi-app sync failed: ' || SQLERRM;
    ROLLBACK;
END;
```

## Smart Property Mapping with Rules Engine

🔴 **Level:** Advanced  
**Purpose:** Rule-based property mapping with transformation logic

```sql
/*
  Script: MAP_PROPERTIES_RULE_ENGINE
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Intelligent property mapping using configurable rules
  
  Features:
  - Dynamic rule evaluation
  - Property transformation functions
  - Conditional mapping
  - Default value handling
  - Mapping validation
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'MAP_PROPERTIES_RULE_ENGINE';
  v_source_member  VARCHAR2(100);
  v_mapping_count  NUMBER := 0;
  
  TYPE t_property_map IS RECORD (
    source_prop    VARCHAR2(100),
    target_prop    VARCHAR2(100),
    transform_rule VARCHAR2(500),
    default_value  VARCHAR2(500),
    is_required    VARCHAR2(1)
  );
  
  TYPE t_property_maps IS TABLE OF t_property_map;
  v_mappings t_property_maps;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION load_mapping_rules RETURN t_property_maps IS
    v_maps t_property_maps := t_property_maps();
    i NUMBER := 0;
  BEGIN
    -- Load mapping rules from configuration
    FOR rec IN (SELECT source_property,
                       target_property,
                       transformation_rule,
                       default_value,
                       is_required
                FROM   ew_property_mapping_rules
                WHERE  source_app = ew_lb_api.g_app_name
                AND    target_app = ew_lb_api.g_target_app_name
                AND    is_active = 'Y'
                ORDER BY mapping_order)
    LOOP
      i := i + 1;
      v_maps.EXTEND;
      v_maps(i).source_prop := rec.source_property;
      v_maps(i).target_prop := rec.target_property;
      v_maps(i).transform_rule := rec.transformation_rule;
      v_maps(i).default_value := rec.default_value;
      v_maps(i).is_required := rec.is_required;
    END LOOP;
    
    RETURN v_maps;
  END load_mapping_rules;
  
  FUNCTION apply_transformation(p_value IN VARCHAR2,
                               p_rule  IN VARCHAR2) RETURN VARCHAR2 IS
    v_result VARCHAR2(500);
  BEGIN
    IF p_rule IS NULL THEN
      RETURN p_value;
    END IF;
    
    -- Parse and apply transformation rule
    CASE 
      WHEN p_rule = 'UPPERCASE' THEN
        v_result := UPPER(p_value);
        
      WHEN p_rule = 'LOWERCASE' THEN
        v_result := LOWER(p_value);
        
      WHEN p_rule LIKE 'PREFIX:%' THEN
        v_result := SUBSTR(p_rule, 8) || p_value;
        
      WHEN p_rule LIKE 'SUFFIX:%' THEN
        v_result := p_value || SUBSTR(p_rule, 8);
        
      WHEN p_rule LIKE 'REPLACE:%' THEN
        -- Format: REPLACE:old_value:new_value
        DECLARE
          v_old VARCHAR2(100);
          v_new VARCHAR2(100);
          v_pos NUMBER;
        BEGIN
          v_pos := INSTR(p_rule, ':', 9);
          v_old := SUBSTR(p_rule, 9, v_pos - 9);
          v_new := SUBSTR(p_rule, v_pos + 1);
          v_result := REPLACE(p_value, v_old, v_new);
        END;
        
      WHEN p_rule LIKE 'MAP:%' THEN
        -- Lookup mapping table
        BEGIN
          SELECT target_value
          INTO   v_result
          FROM   ew_value_mappings
          WHERE  mapping_set = SUBSTR(p_rule, 5)
          AND    source_value = p_value;
        EXCEPTION
          WHEN NO_DATA_FOUND THEN
            v_result := p_value; -- Keep original if not mapped
        END;
        
      WHEN p_rule LIKE 'FORMULA:%' THEN
        -- Execute dynamic formula
        EXECUTE IMMEDIATE 'SELECT ' || SUBSTR(p_rule, 9) || ' FROM DUAL'
        INTO v_result
        USING p_value;
        
      WHEN p_rule = 'DATE_FORMAT' THEN
        -- Convert date format
        v_result := TO_CHAR(TO_DATE(p_value, 'MM/DD/YYYY'), 'YYYY-MM-DD');
        
      WHEN p_rule = 'REMOVE_SPECIAL' THEN
        -- Remove special characters
        v_result := REGEXP_REPLACE(p_value, '[^A-Za-z0-9]', '');
        
      ELSE
        -- No transformation
        v_result := p_value;
    END CASE;
    
    RETURN v_result;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Transformation error: ' || SQLERRM);
      RETURN p_value; -- Return original on error
  END apply_transformation;
  
  PROCEDURE map_property(p_mapping IN t_property_map) IS
    v_source_value VARCHAR2(500);
    v_target_value VARCHAR2(500);
  BEGIN
    -- Get source value
    v_source_value := ew_api.get_property_value(
                        p_app_id      => ew_lb_api.g_app_id,
                        p_dim_id      => ew_lb_api.g_dim_id,
                        p_member_name => v_source_member,
                        p_prop_name   => p_mapping.source_prop
                      );
    
    -- Apply transformation or use default
    IF v_source_value IS NOT NULL THEN
      v_target_value := apply_transformation(v_source_value, 
                                            p_mapping.transform_rule);
    ELSIF p_mapping.default_value IS NOT NULL THEN
      v_target_value := p_mapping.default_value;
    ELSIF p_mapping.is_required = 'Y' THEN
      RAISE_APPLICATION_ERROR(-20001, 
        'Required property missing: ' || p_mapping.source_prop);
    ELSE
      RETURN; -- Skip optional empty properties
    END IF;
    
    -- Set target property
    ew_lb_api.set_target_property(p_mapping.target_prop, v_target_value);
    
    log('Mapped ' || p_mapping.source_prop || ' -> ' || 
        p_mapping.target_prop || ': ' || v_target_value);
    
    v_mapping_count := v_mapping_count + 1;
    
  END map_property;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_source_member := ew_lb_api.g_member_name;
  
  log('Starting rule-based property mapping for: ' || v_source_member);
  log('Source: ' || ew_lb_api.g_app_name || 
      ', Target: ' || ew_lb_api.g_target_app_name);
  
  -- Load mapping rules
  v_mappings := load_mapping_rules();
  
  IF v_mappings.COUNT = 0 THEN
    log('No mapping rules found');
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'No property mapping rules configured';
    RETURN;
  END IF;
  
  -- Set target member name (can also be transformed)
  ew_lb_api.g_target_member_name := v_source_member;
  ew_lb_api.g_target_parent_name := ew_lb_api.g_parent_member_name;
  
  -- Apply each mapping rule
  FOR i IN 1..v_mappings.COUNT LOOP
    BEGIN
      map_property(v_mappings(i));
    EXCEPTION
      WHEN OTHERS THEN
        log('Error mapping property: ' || v_mappings(i).source_prop || 
            ' - ' || SQLERRM);
        
        IF v_mappings(i).is_required = 'Y' THEN
          -- Required property failed - stop processing
          ew_lb_api.g_status := ew_lb_api.g_error;
          ew_lb_api.g_message := 'Required property mapping failed: ' || 
                                v_mappings(i).source_prop;
          RETURN;
        END IF;
    END;
  END LOOP;
  
  log('Property mapping completed. ' || v_mapping_count || ' properties mapped');
  
  -- Validate mapped values
  DECLARE
    v_validation_errors VARCHAR2(4000);
  BEGIN
    -- Run target application validation rules
    FOR rec IN (SELECT validation_rule, error_message
                FROM   ew_target_validations
                WHERE  target_app = ew_lb_api.g_target_app_name
                AND    is_active = 'Y')
    LOOP
      BEGIN
        EXECUTE IMMEDIATE rec.validation_rule;
      EXCEPTION
        WHEN OTHERS THEN
          v_validation_errors := v_validation_errors || 
                               rec.error_message || '; ';
      END;
    END LOOP;
    
    IF v_validation_errors IS NOT NULL THEN
      ew_lb_api.g_status := ew_lb_api.g_warning;
      ew_lb_api.g_message := 'Validation warnings: ' || v_validation_errors;
    END IF;
  END;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Critical exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Property mapping failed: ' || SQLERRM;
END;
```

## Testing Dimension Mapping Scripts

### Mapping Test Framework

```sql
/*
  Script: TEST_DIMENSION_MAPPINGS
  Purpose: Test framework for dimension mapping scripts
*/
DECLARE
  c_script_name VARCHAR2(100) := 'TEST_DIMENSION_MAPPINGS';
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END log;
  
  PROCEDURE test_mapping(p_source_member IN VARCHAR2,
                        p_source_parent IN VARCHAR2,
                        p_target_app    IN VARCHAR2) IS
  BEGIN
    -- Set mapping context
    ew_lb_api.g_member_name := p_source_member;
    ew_lb_api.g_parent_member_name := p_source_parent;
    ew_lb_api.g_target_app_name := p_target_app;
    
    -- Clear previous mappings
    ew_lb_api.g_target_member_name := NULL;
    ew_lb_api.g_target_parent_name := NULL;
    
    log('Testing mapping: ' || p_source_member || ' -> ' || p_target_app);
    
    -- Execute mapping logic
    -- (Insert your mapping code here)
    
    -- Log results
    log('Target member: ' || NVL(ew_lb_api.g_target_member_name, 'NOT SET'));
    log('Target parent: ' || NVL(ew_lb_api.g_target_parent_name, 'NOT SET'));
    log('Status: ' || ew_lb_api.g_status);
    
  END test_mapping;
  
BEGIN
  log('Starting dimension mapping tests');
  
  -- Test different mapping scenarios
  test_mapping('Entity001', 'North America', 'Planning');
  test_mapping('Account_4100', 'Revenue', 'Essbase');
  test_mapping('CC-1234-001', 'CostCenters', 'FCCS');
  
  log('Dimension mapping tests completed');
  
END;
```

## Best Practices

1. **Handle missing members gracefully** - Check existence before mapping
2. **Map properties intelligently** - Use transformation rules
3. **Detect and resolve conflicts** - Implement conflict resolution strategies
4. **Log all mapping decisions** - For audit and troubleshooting
5. **Consider performance** - Batch operations for large hierarchies
6. **Validate target data** - Ensure mapped data meets target requirements
7. **Support rollback** - Keep mapping history for reversal
8. **Document mapping rules** - In configuration tables and comments

## Next Steps

- See [Hierarchy Action Examples](hierarchy-actions.md)
- Review [Advanced Patterns](advanced-patterns.md)
- Learn about [Performance Optimization](../advanced/performance.md)