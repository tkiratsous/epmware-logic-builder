# Property Derivation Examples

Property derivation scripts automatically populate member properties based on business logic, reducing manual data entry and ensuring consistency across your EPM applications.

## Auto-Generate Member Alias

🟢 **Level:** Basic  
**Purpose:** Automatically create descriptive aliases from member names and properties

```sql
/*
  Script: DERIVE_MEMBER_ALIAS
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Auto-generate member alias from name and description
  
  Format: [MemberName] - [Description] ([Status])
  Example: CC1234 - Marketing Department (Active)
*/
DECLARE
  c_script_name VARCHAR2(100) := 'DERIVE_MEMBER_ALIAS';
  v_member_name VARCHAR2(100);
  v_description VARCHAR2(500);
  v_status      VARCHAR2(50);
  v_alias       VARCHAR2(500);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Get member information
  v_member_name := ew_lb_api.g_member_name;
  
  log('Generating alias for member: ' || v_member_name);
  
  -- Get related properties
  v_description := ew_api.get_property_value(
                     p_app_id      => ew_lb_api.g_app_id,
                     p_dim_id      => ew_lb_api.g_dim_id,
                     p_member_name => v_member_name,
                     p_prop_name   => 'Description'
                   );
  
  v_status := ew_api.get_property_value(
                p_app_id      => ew_lb_api.g_app_id,
                p_dim_id      => ew_lb_api.g_dim_id,
                p_member_name => v_member_name,
                p_prop_name   => 'Status'
              );
  
  -- Build alias
  v_alias := v_member_name;
  
  IF v_description IS NOT NULL THEN
    v_alias := v_alias || ' - ' || v_description;
  END IF;
  
  IF v_status IS NOT NULL THEN
    v_alias := v_alias || ' (' || v_status || ')';
  END IF;
  
  -- Set the derived value
  ew_lb_api.g_prop_value := v_alias;
  
  log('Generated alias: ' || v_alias);
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    -- On error, use member name as alias
    ew_lb_api.g_prop_value := v_member_name;
    ew_lb_api.g_status := ew_lb_api.g_success; -- Still allow creation
END;
```

## Calculate Full Account Code

🟢 **Level:** Basic  
**Purpose:** Concatenate parent hierarchy codes to create full account string

```sql
/*
  Script: DERIVE_FULL_ACCOUNT_CODE
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Build full account code from hierarchy path
  
  Example Hierarchy:
  - 1000 (Assets)
    - 1100 (Current Assets)
      - 1110 (Cash)
  
  Result: 1000.1100.1110
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'DERIVE_FULL_ACCOUNT_CODE';
  c_separator      VARCHAR2(5) := '.';
  v_full_code      VARCHAR2(500);
  v_current_member VARCHAR2(100);
  v_parent_member  VARCHAR2(100);
  v_level_count    NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION get_parent(p_member IN VARCHAR2) RETURN VARCHAR2 IS
    v_parent VARCHAR2(100);
  BEGIN
    SELECT parent_member_name
    INTO   v_parent
    FROM   ew_hierarchy
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    member_name = p_member
    AND    ROWNUM = 1;
    
    RETURN v_parent;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN NULL;
  END get_parent;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_current_member := ew_lb_api.g_member_name;
  v_full_code := v_current_member;
  
  log('Building full code for: ' || v_current_member);
  
  -- Walk up the hierarchy
  v_parent_member := get_parent(v_current_member);
  
  WHILE v_parent_member IS NOT NULL AND v_level_count < 10 LOOP
    v_level_count := v_level_count + 1;
    
    -- Skip dimension root member
    IF v_parent_member = ew_lb_api.g_dim_name THEN
      EXIT;
    END IF;
    
    v_full_code := v_parent_member || c_separator || v_full_code;
    v_current_member := v_parent_member;
    v_parent_member := get_parent(v_current_member);
  END LOOP;
  
  -- Set the derived value
  ew_lb_api.g_prop_value := v_full_code;
  
  log('Generated full code: ' || v_full_code);
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_prop_value := ew_lb_api.g_member_name;
    ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

## Default Value Based on Parent

🟡 **Level:** Intermediate  
**Purpose:** Set default properties based on parent member characteristics

```sql
/*
  Script: DERIVE_DEFAULT_FROM_PARENT
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Inherit and derive default values from parent hierarchy
  
  Rules:
  - Inherit currency from parent
  - Set consolidation method based on account type
  - Default data storage based on level
*/
DECLARE
  c_script_name        VARCHAR2(100) := 'DERIVE_DEFAULT_FROM_PARENT';
  v_parent_member      VARCHAR2(100);
  v_parent_currency    VARCHAR2(10);
  v_parent_acct_type   VARCHAR2(50);
  v_member_level       NUMBER;
  v_derived_value      VARCHAR2(100);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION get_member_level(p_member IN VARCHAR2) RETURN NUMBER IS
    v_level NUMBER := 0;
    v_parent VARCHAR2(100);
  BEGIN
    v_parent := p_member;
    
    LOOP
      SELECT parent_member_name
      INTO   v_parent
      FROM   ew_hierarchy
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = v_parent
      AND    ROWNUM = 1;
      
      EXIT WHEN v_parent IS NULL OR v_parent = ew_lb_api.g_dim_name;
      v_level := v_level + 1;
      
      EXIT WHEN v_level > 20; -- Prevent infinite loops
    END LOOP;
    
    RETURN v_level;
  EXCEPTION
    WHEN OTHERS THEN
      RETURN 0;
  END get_member_level;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_parent_member := ew_lb_api.g_parent_member_name;
  
  log('Deriving defaults for: ' || ew_lb_api.g_member_name);
  log('Parent: ' || v_parent_member);
  log('Property: ' || ew_lb_api.g_prop_name);
  
  -- Different derivation based on property
  CASE ew_lb_api.g_prop_name
    
    WHEN 'Currency' THEN
      -- Inherit currency from parent
      v_parent_currency := ew_api.get_property_value(
                             p_app_id      => ew_lb_api.g_app_id,
                             p_dim_id      => ew_lb_api.g_dim_id,
                             p_member_name => v_parent_member,
                             p_prop_name   => 'Currency'
                           );
      
      v_derived_value := NVL(v_parent_currency, 'USD');
      log('Derived currency: ' || v_derived_value);
      
    WHEN 'ConsolidationMethod' THEN
      -- Set based on account type
      v_parent_acct_type := ew_api.get_property_value(
                              p_app_id      => ew_lb_api.g_app_id,
                              p_dim_id      => ew_lb_api.g_dim_id,
                              p_member_name => v_parent_member,
                              p_prop_name   => 'AccountType'
                            );
      
      v_derived_value := CASE v_parent_acct_type
                           WHEN 'Revenue' THEN 'SUM'
                           WHEN 'Expense' THEN 'SUM'
                           WHEN 'Asset' THEN 'LAST'
                           WHEN 'Liability' THEN 'LAST'
                           WHEN 'Statistical' THEN 'AVERAGE'
                           ELSE 'SUM'
                         END;
      
      log('Derived consolidation: ' || v_derived_value);
      
    WHEN 'DataStorage' THEN
      -- Set based on hierarchy level
      v_member_level := get_member_level(ew_lb_api.g_member_name);
      
      IF v_member_level = 0 THEN
        v_derived_value := 'StoreData';
      ELSE
        v_derived_value := 'DynamicCalc';
      END IF;
      
      log('Member level: ' || v_member_level);
      log('Derived storage: ' || v_derived_value);
      
    ELSE
      -- No derivation for other properties
      log('No derivation rule for property: ' || ew_lb_api.g_prop_name);
      RETURN;
  END CASE;
  
  -- Set the derived value
  ew_lb_api.g_prop_value := v_derived_value;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    -- Don't fail member creation due to derivation errors
    ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

## Smart Entity Code Generation

🟡 **Level:** Intermediate  
**Purpose:** Generate unique entity codes with sequential numbering

```sql
/*
  Script: DERIVE_ENTITY_CODE
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Generate unique entity codes with intelligent numbering
  
  Format: [Region][Type][Sequence]
  Example: NA-SUB-0001 (North America Subsidiary 0001)
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'DERIVE_ENTITY_CODE';
  v_region_code    VARCHAR2(10);
  v_entity_type    VARCHAR2(10);
  v_next_sequence  NUMBER;
  v_entity_code    VARCHAR2(50);
  v_parent_region  VARCHAR2(100);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION get_next_sequence(p_prefix IN VARCHAR2) RETURN NUMBER IS
    v_max_seq NUMBER;
  BEGIN
    SELECT NVL(MAX(TO_NUMBER(SUBSTR(member_name, -4))), 0) + 1
    INTO   v_max_seq
    FROM   ew_hierarchy
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    member_name LIKE p_prefix || '%'
    AND    REGEXP_LIKE(SUBSTR(member_name, -4), '^[0-9]{4}$');
    
    RETURN v_max_seq;
  EXCEPTION
    WHEN OTHERS THEN
      RETURN 1;
  END get_next_sequence;
  
  FUNCTION get_region_code(p_parent IN VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Map parent to region code
    RETURN CASE 
             WHEN p_parent LIKE '%North America%' THEN 'NA'
             WHEN p_parent LIKE '%Europe%' THEN 'EU'
             WHEN p_parent LIKE '%Asia Pacific%' THEN 'AP'
             WHEN p_parent LIKE '%Latin America%' THEN 'LA'
             WHEN p_parent LIKE '%Middle East%' THEN 'ME'
             ELSE 'GL' -- Global
           END;
  END get_region_code;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only derive for EntityCode property
  IF ew_lb_api.g_prop_name != 'EntityCode' THEN
    RETURN;
  END IF;
  
  log('Generating entity code for: ' || ew_lb_api.g_member_name);
  
  -- Get parent region
  v_parent_region := ew_lb_api.g_parent_member_name;
  v_region_code := get_region_code(v_parent_region);
  
  -- Get entity type from another property
  v_entity_type := ew_api.get_property_value(
                     p_app_id      => ew_lb_api.g_app_id,
                     p_dim_id      => ew_lb_api.g_dim_id,
                     p_member_name => ew_lb_api.g_member_name,
                     p_prop_name   => 'EntityType'
                   );
  
  -- Map entity type to code
  v_entity_type := CASE NVL(v_entity_type, 'OTHER')
                     WHEN 'Subsidiary' THEN 'SUB'
                     WHEN 'Division' THEN 'DIV'
                     WHEN 'Branch' THEN 'BRN'
                     WHEN 'Joint Venture' THEN 'JV'
                     ELSE 'OTH'
                   END;
  
  -- Build prefix
  v_entity_code := v_region_code || '-' || v_entity_type || '-';
  
  -- Get next sequence number
  v_next_sequence := get_next_sequence(v_entity_code);
  
  -- Format with leading zeros
  v_entity_code := v_entity_code || LPAD(v_next_sequence, 4, '0');
  
  -- Set the derived value
  ew_lb_api.g_prop_value := v_entity_code;
  
  log('Generated entity code: ' || v_entity_code);
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    -- Fallback to simple code
    ew_lb_api.g_prop_value := 'ENT-' || 
                               TO_CHAR(SYSDATE, 'YYYYMMDD') || '-' ||
                               SUBSTR(ew_lb_api.g_member_name, 1, 10);
    ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

## Calculate Derived Metrics

🔴 **Level:** Advanced  
**Purpose:** Calculate complex derived values from multiple sources

```sql
/*
  Script: DERIVE_CALCULATED_METRICS
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Calculate derived financial metrics
  
  Calculates:
  - Risk Score (based on multiple factors)
  - Priority Level (based on budget and strategic importance)
  - Allocation Percentage (based on department totals)
*/
DECLARE
  c_script_name       VARCHAR2(100) := 'DERIVE_CALCULATED_METRICS';
  v_metric_type       VARCHAR2(50);
  v_calculated_value  VARCHAR2(100);
  
  -- Risk calculation variables
  v_revenue          NUMBER;
  v_expense          NUMBER;
  v_headcount        NUMBER;
  v_risk_score       NUMBER;
  
  -- Priority calculation variables
  v_budget           NUMBER;
  v_strategic_score  NUMBER;
  v_priority         VARCHAR2(20);
  
  -- Allocation variables
  v_dept_total       NUMBER;
  v_member_amount    NUMBER;
  v_allocation_pct   NUMBER;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION calculate_risk_score RETURN NUMBER IS
    v_score NUMBER := 0;
    v_margin NUMBER;
  BEGIN
    -- Get financial metrics
    v_revenue := TO_NUMBER(NVL(ew_api.get_property_value(
                                  p_app_id      => ew_lb_api.g_app_id,
                                  p_dim_id      => ew_lb_api.g_dim_id,
                                  p_member_name => ew_lb_api.g_member_name,
                                  p_prop_name   => 'Revenue'
                                ), '0'));
    
    v_expense := TO_NUMBER(NVL(ew_api.get_property_value(
                                  p_app_id      => ew_lb_api.g_app_id,
                                  p_dim_id      => ew_lb_api.g_dim_id,
                                  p_member_name => ew_lb_api.g_member_name,
                                  p_prop_name   => 'Expense'
                                ), '0'));
    
    v_headcount := TO_NUMBER(NVL(ew_api.get_property_value(
                                    p_app_id      => ew_lb_api.g_app_id,
                                    p_dim_id      => ew_lb_api.g_dim_id,
                                    p_member_name => ew_lb_api.g_member_name,
                                    p_prop_name   => 'Headcount'
                                  ), '0'));
    
    -- Calculate margin
    IF v_revenue > 0 THEN
      v_margin := (v_revenue - v_expense) / v_revenue;
    ELSE
      v_margin := 0;
    END IF;
    
    -- Risk scoring algorithm
    -- Low margin = higher risk
    IF v_margin < 0 THEN
      v_score := v_score + 40;
    ELSIF v_margin < 0.1 THEN
      v_score := v_score + 25;
    ELSIF v_margin < 0.2 THEN
      v_score := v_score + 10;
    END IF;
    
    -- High expense per headcount = higher risk
    IF v_headcount > 0 THEN
      IF (v_expense / v_headcount) > 200000 THEN
        v_score := v_score + 30;
      ELSIF (v_expense / v_headcount) > 150000 THEN
        v_score := v_score + 15;
      END IF;
    END IF;
    
    -- Revenue dependency
    IF v_revenue < 1000000 THEN
      v_score := v_score + 20;
    ELSIF v_revenue < 5000000 THEN
      v_score := v_score + 10;
    END IF;
    
    -- Ensure score is between 0 and 100
    v_score := LEAST(GREATEST(v_score, 0), 100);
    
    RETURN v_score;
    
  END calculate_risk_score;
  
  FUNCTION calculate_priority RETURN VARCHAR2 IS
    v_priority_score NUMBER := 0;
  BEGIN
    v_budget := TO_NUMBER(NVL(ew_api.get_property_value(
                                p_app_id      => ew_lb_api.g_app_id,
                                p_dim_id      => ew_lb_api.g_dim_id,
                                p_member_name => ew_lb_api.g_member_name,
                                p_prop_name   => 'Budget'
                              ), '0'));
    
    v_strategic_score := TO_NUMBER(NVL(ew_api.get_property_value(
                                          p_app_id      => ew_lb_api.g_app_id,
                                          p_dim_id      => ew_lb_api.g_dim_id,
                                          p_member_name => ew_lb_api.g_member_name,
                                          p_prop_name   => 'StrategicScore'
                                        ), '0'));
    
    -- Weighted priority calculation
    v_priority_score := (v_budget / 1000000) * 0.3 + -- Budget weight: 30%
                       v_strategic_score * 0.7;       -- Strategic weight: 70%
    
    -- Assign priority level
    IF v_priority_score >= 80 THEN
      RETURN 'Critical';
    ELSIF v_priority_score >= 60 THEN
      RETURN 'High';
    ELSIF v_priority_score >= 40 THEN
      RETURN 'Medium';
    ELSIF v_priority_score >= 20 THEN
      RETURN 'Low';
    ELSE
      RETURN 'Minimal';
    END IF;
    
  END calculate_priority;
  
  FUNCTION calculate_allocation_pct RETURN NUMBER IS
    v_parent VARCHAR2(100);
  BEGIN
    v_parent := ew_lb_api.g_parent_member_name;
    
    -- Get member's budget
    v_member_amount := TO_NUMBER(NVL(ew_api.get_property_value(
                                        p_app_id      => ew_lb_api.g_app_id,
                                        p_dim_id      => ew_lb_api.g_dim_id,
                                        p_member_name => ew_lb_api.g_member_name,
                                        p_prop_name   => 'Budget'
                                      ), '0'));
    
    -- Get total for parent's children
    SELECT NVL(SUM(TO_NUMBER(prop_value)), 0)
    INTO   v_dept_total
    FROM   ew_member_properties mp
    JOIN   ew_hierarchy h ON (h.app_id = mp.app_id 
                          AND h.dim_id = mp.dim_id 
                          AND h.member_name = mp.member_name)
    WHERE  mp.app_id = ew_lb_api.g_app_id
    AND    mp.dim_id = ew_lb_api.g_dim_id
    AND    h.parent_member_name = v_parent
    AND    mp.prop_name = 'Budget';
    
    -- Calculate percentage
    IF v_dept_total > 0 THEN
      RETURN ROUND((v_member_amount / v_dept_total) * 100, 2);
    ELSE
      RETURN 0;
    END IF;
    
  END calculate_allocation_pct;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Calculating derived metric: ' || ew_lb_api.g_prop_name);
  log('Member: ' || ew_lb_api.g_member_name);
  
  -- Determine which metric to calculate
  CASE ew_lb_api.g_prop_name
    
    WHEN 'RiskScore' THEN
      v_risk_score := calculate_risk_score();
      v_calculated_value := TO_CHAR(v_risk_score);
      log('Calculated risk score: ' || v_calculated_value);
      
    WHEN 'PriorityLevel' THEN
      v_priority := calculate_priority();
      v_calculated_value := v_priority;
      log('Calculated priority: ' || v_calculated_value);
      
    WHEN 'AllocationPercentage' THEN
      v_allocation_pct := calculate_allocation_pct();
      v_calculated_value := TO_CHAR(v_allocation_pct) || '%';
      log('Calculated allocation: ' || v_calculated_value);
      
    ELSE
      log('No derivation rule for: ' || ew_lb_api.g_prop_name);
      RETURN;
  END CASE;
  
  -- Set the derived value
  ew_lb_api.g_prop_value := v_calculated_value;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception in calculation: ' || SQLERRM);
    -- Set default values on error
    CASE ew_lb_api.g_prop_name
      WHEN 'RiskScore' THEN
        ew_lb_api.g_prop_value := '50'; -- Medium risk default
      WHEN 'PriorityLevel' THEN
        ew_lb_api.g_prop_value := 'Medium';
      WHEN 'AllocationPercentage' THEN
        ew_lb_api.g_prop_value := '0%';
      ELSE
        ew_lb_api.g_prop_value := NULL;
    END CASE;
    ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

## Testing Derivation Scripts

### Derivation Test Framework

```sql
/*
  Script: TEST_DERIVATION_SCRIPTS
  Purpose: Automated testing for property derivations
*/
DECLARE
  c_script_name VARCHAR2(100) := 'TEST_DERIVATION_SCRIPTS';
  v_result      VARCHAR2(500);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END log;
  
  PROCEDURE test_derivation(p_member_name IN VARCHAR2,
                           p_parent_name IN VARCHAR2,
                           p_prop_name   IN VARCHAR2) IS
  BEGIN
    -- Set context
    ew_lb_api.g_member_name := p_member_name;
    ew_lb_api.g_parent_member_name := p_parent_name;
    ew_lb_api.g_prop_name := p_prop_name;
    
    -- Clear previous value
    ew_lb_api.g_prop_value := NULL;
    
    -- Run derivation logic
    -- (Insert your derivation code here)
    
    -- Log result
    log('Derivation test for ' || p_prop_name || ': ' || 
        NVL(ew_lb_api.g_prop_value, 'NULL'));
    
  END test_derivation;
  
BEGIN
  log('Starting derivation tests');
  
  -- Test different scenarios
  test_derivation('TEST001', 'North America', 'EntityCode');
  test_derivation('TEST002', 'Europe', 'EntityCode');
  test_derivation('BUDGET_TEST', 'Department_A', 'AllocationPercentage');
  
  log('Derivation tests completed');
  
END;
```

## Best Practices

1. **Handle NULL values gracefully** - Don't fail on missing data
2. **Use fallback values** - Provide sensible defaults
3. **Log derivation logic** - Track what was calculated
4. **Optimize queries** - Cache frequently accessed data
5. **Consider performance** - Avoid complex calculations for bulk operations
6. **Make derivations idempotent** - Same input = same output
7. **Document business rules** - Explain the derivation logic

## Next Steps

- See [Dimension Mapping Examples](dimension-mapping.md)
- Review [Workflow Task Examples](workflow-tasks.md)
- Learn about [Performance Optimization](../advanced/performance.md)