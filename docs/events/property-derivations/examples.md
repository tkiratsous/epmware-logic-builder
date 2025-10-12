# Property Derivations Examples

This page provides comprehensive examples of Property Derivation scripts for common business scenarios. Each example includes complete code, setup instructions, and testing guidelines.

## Example 1: Auto-Generate Sequential IDs

**Scenario**: Automatically generate unique sequential IDs for new cost centers.

### Setup
```sql
-- Create sequence table
CREATE TABLE member_sequences (
  dimension_id NUMBER,
  prefix VARCHAR2(10),
  last_number NUMBER,
  CONSTRAINT pk_member_seq PRIMARY KEY (dimension_id, prefix)
);

-- Initialize sequence
INSERT INTO member_sequences VALUES (:dim_id, 'CC', 1000);
COMMIT;
```

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'DERIVE_SEQUENTIAL_ID';
  l_prefix VARCHAR2(10);
  l_next_number NUMBER;
  l_new_id VARCHAR2(50);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only derive for Member_ID property on new members
  IF ew_lb_api.g_prop_name != 'Member_ID' OR 
     ew_lb_api.g_action_code != 'CMC' THEN
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    RETURN;
  END IF;
  
  log('Generating ID for: ' || ew_lb_api.g_member_name);
  
  -- Determine prefix based on member type
  IF ew_lb_api.g_member_name LIKE 'CC_%' THEN
    l_prefix := 'CC';
  ELSIF ew_lb_api.g_member_name LIKE 'PC_%' THEN
    l_prefix := 'PC';
  ELSE
    l_prefix := 'GEN';
  END IF;
  
  -- Get next number (with lock to prevent duplicates)
  SELECT last_number + 1
  INTO l_next_number
  FROM member_sequences
  WHERE dimension_id = ew_lb_api.g_app_dimension_id
  AND prefix = l_prefix
  FOR UPDATE;
  
  -- Update sequence
  UPDATE member_sequences
  SET last_number = l_next_number
  WHERE dimension_id = ew_lb_api.g_app_dimension_id
  AND prefix = l_prefix;
  
  -- Generate ID
  l_new_id := l_prefix || TO_CHAR(SYSDATE, 'YY') || 
              LPAD(l_next_number, 6, '0');
  
  ew_lb_api.g_out_prop_value := l_new_id;
  log('Generated ID: ' || l_new_id);
  
  COMMIT; -- Commit sequence update
  
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    -- Initialize sequence if not found
    INSERT INTO member_sequences 
    VALUES (ew_lb_api.g_app_dimension_id, l_prefix, 1000);
    
    ew_lb_api.g_out_prop_value := l_prefix || 
                                   TO_CHAR(SYSDATE, 'YY') || '001000';
    COMMIT;
    
  WHEN OTHERS THEN
    ROLLBACK;
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error generating ID: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Expected Results
```
Member Name: CC_Finance_Dept
Generated ID: CC24001001

Member Name: PC_Sales_Region
Generated ID: PC24001001
```

---

## Example 2: Inherit and Override Properties

**Scenario**: Inherit properties from parent with ability to override at member level.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'DERIVE_INHERITED_PROPS';
  l_parent_value VARCHAR2(500);
  l_override_flag VARCHAR2(1);
  l_inheritance_level NUMBER := 0;
  l_max_levels CONSTANT NUMBER := 10;
  l_current_parent VARCHAR2(100);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION get_override_flag RETURN VARCHAR2 IS
    l_flag VARCHAR2(1);
  BEGIN
    -- Check if member has override flag set
    SELECT NVL(prop_value, 'N')
    INTO l_flag
    FROM ew_member_properties
    WHERE member_id = ew_lb_api.g_member_id
    AND prop_name = ew_lb_api.g_prop_name || '_Override'
    AND ROWNUM = 1;
    
    RETURN l_flag;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN 'N';
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Properties that support inheritance
  IF ew_lb_api.g_prop_name NOT IN ('Region', 'Currency', 'Tax_Rate', 
                                    'Department_Type', 'Cost_Center_Group') THEN
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    RETURN;
  END IF;
  
  log('Processing inheritance for: ' || ew_lb_api.g_member_name || 
      '.' || ew_lb_api.g_prop_name);
  
  -- Check for override flag
  l_override_flag := get_override_flag();
  
  -- If override is set and value exists, keep it
  IF l_override_flag = 'Y' AND ew_lb_api.g_prop_value IS NOT NULL THEN
    log('Override flag set, keeping value: ' || ew_lb_api.g_prop_value);
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    RETURN;
  END IF;
  
  -- Walk up hierarchy to find inherited value
  l_current_parent := ew_lb_api.g_parent_member_name;
  
  WHILE l_inheritance_level < l_max_levels AND 
        l_current_parent IS NOT NULL LOOP
    
    -- Get parent's property value
    l_parent_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => l_current_parent,
      p_prop_label  => ew_lb_api.g_prop_name
    );
    
    IF l_parent_value IS NOT NULL THEN
      log('Inherited from ' || l_current_parent || 
          ' (level ' || l_inheritance_level || '): ' || l_parent_value);
      ew_lb_api.g_out_prop_value := l_parent_value;
      RETURN;
    END IF;
    
    -- Move up hierarchy
    l_current_parent := ew_hierarchy.get_primary_parent_name(
      p_app_dimension_id => ew_lb_api.g_app_dimension_id,
      p_member_name     => l_current_parent
    );
    
    l_inheritance_level := l_inheritance_level + 1;
  END LOOP;
  
  -- No inherited value found, use defaults
  ew_lb_api.g_out_prop_value := 
    CASE ew_lb_api.g_prop_name
      WHEN 'Region' THEN 'GLOBAL'
      WHEN 'Currency' THEN 'USD'
      WHEN 'Tax_Rate' THEN '0'
      WHEN 'Department_Type' THEN 'Standard'
      WHEN 'Cost_Center_Group' THEN 'Default'
      ELSE NULL
    END;
    
  log('No inheritance found, using default: ' || ew_lb_api.g_out_prop_value);
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Inheritance error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 3: Calculate Composite Properties

**Scenario**: Calculate complex property values based on multiple inputs and business rules.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'DERIVE_COMPOSITE_VALUES';
  l_base_score NUMBER;
  l_risk_factor NUMBER;
  l_size_category VARCHAR2(20);
  l_final_score NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION get_numeric_prop(p_prop_name VARCHAR2) RETURN NUMBER IS
    l_value VARCHAR2(100);
  BEGIN
    l_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => p_prop_name
    );
    
    RETURN TO_NUMBER(NVL(l_value, '0'));
  EXCEPTION
    WHEN VALUE_ERROR THEN
      RETURN 0;
  END;
  
  FUNCTION calculate_risk_score RETURN NUMBER IS
    l_revenue NUMBER;
    l_costs NUMBER;
    l_employees NUMBER;
    l_score NUMBER;
  BEGIN
    -- Get component values
    l_revenue := get_numeric_prop('Annual_Revenue');
    l_costs := get_numeric_prop('Operating_Costs');
    l_employees := get_numeric_prop('Employee_Count');
    
    -- Calculate base score
    IF l_revenue > 0 THEN
      l_score := ((l_revenue - l_costs) / l_revenue) * 50;
    ELSE
      l_score := 0;
    END IF;
    
    -- Adjust for size
    IF l_employees > 1000 THEN
      l_score := l_score * 1.2;
    ELSIF l_employees < 100 THEN
      l_score := l_score * 0.8;
    END IF;
    
    -- Normalize to 0-100 range
    l_score := LEAST(GREATEST(l_score, 0), 100);
    
    RETURN ROUND(l_score, 2);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Handle different composite properties
  CASE ew_lb_api.g_prop_name
    WHEN 'Risk_Score' THEN
      l_final_score := calculate_risk_score();
      ew_lb_api.g_out_prop_value := TO_CHAR(l_final_score);
      log('Calculated Risk Score: ' || l_final_score);
      
    WHEN 'Size_Category' THEN
      l_base_score := get_numeric_prop('Employee_Count');
      
      l_size_category := CASE
        WHEN l_base_score >= 10000 THEN 'Enterprise'
        WHEN l_base_score >= 1000 THEN 'Large'
        WHEN l_base_score >= 100 THEN 'Medium'
        WHEN l_base_score >= 10 THEN 'Small'
        ELSE 'Micro'
      END;
      
      ew_lb_api.g_out_prop_value := l_size_category;
      log('Derived Size Category: ' || l_size_category);
      
    WHEN 'Priority_Level' THEN
      -- Complex priority calculation
      l_risk_factor := get_numeric_prop('Risk_Score');
      l_base_score := get_numeric_prop('Strategic_Value');
      
      l_final_score := (l_risk_factor * 0.4) + (l_base_score * 0.6);
      
      ew_lb_api.g_out_prop_value := CASE
        WHEN l_final_score >= 80 THEN 'Critical'
        WHEN l_final_score >= 60 THEN 'High'
        WHEN l_final_score >= 40 THEN 'Medium'
        WHEN l_final_score >= 20 THEN 'Low'
        ELSE 'Minimal'
      END;
      
      log('Calculated Priority: ' || ew_lb_api.g_out_prop_value);
      
    ELSE
      -- No derivation needed
      ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END CASE;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Calculation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 4: Date-Based Derivations

**Scenario**: Derive date-related properties with business day calculations.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'DERIVE_DATE_PROPERTIES';
  l_start_date DATE;
  l_end_date DATE;
  l_duration NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION add_business_days(p_date DATE, p_days NUMBER) RETURN DATE IS
    l_result DATE := p_date;
    l_days_added NUMBER := 0;
  BEGIN
    WHILE l_days_added < p_days LOOP
      l_result := l_result + 1;
      -- Skip weekends
      IF TO_CHAR(l_result, 'DY', 'NLS_DATE_LANGUAGE=ENGLISH') 
         NOT IN ('SAT', 'SUN') THEN
        l_days_added := l_days_added + 1;
      END IF;
    END LOOP;
    
    RETURN l_result;
  END;
  
  FUNCTION calculate_business_days(p_start DATE, p_end DATE) RETURN NUMBER IS
    l_days NUMBER := 0;
    l_current DATE := p_start;
  BEGIN
    WHILE l_current <= p_end LOOP
      IF TO_CHAR(l_current, 'DY', 'NLS_DATE_LANGUAGE=ENGLISH') 
         NOT IN ('SAT', 'SUN') THEN
        l_days := l_days + 1;
      END IF;
      l_current := l_current + 1;
    END LOOP;
    
    RETURN l_days;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Deriving date property: ' || ew_lb_api.g_prop_name);
  
  CASE ew_lb_api.g_prop_name
    WHEN 'Creation_Date' THEN
      -- Set current date for new members
      IF ew_lb_api.g_action_code = 'CMC' THEN
        ew_lb_api.g_out_prop_value := TO_CHAR(SYSDATE, 'MM/DD/YYYY');
      ELSE
        ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
      END IF;
      
    WHEN 'Review_Date' THEN
      -- Set review date 90 business days from creation
      l_start_date := SYSDATE;
      l_end_date := add_business_days(l_start_date, 90);
      ew_lb_api.g_out_prop_value := TO_CHAR(l_end_date, 'MM/DD/YYYY');
      log('Review date set to: ' || ew_lb_api.g_out_prop_value);
      
    WHEN 'Project_Duration' THEN
      -- Calculate duration between start and end dates
      l_start_date := TO_DATE(
        ew_hierarchy.get_member_prop_value(
          p_app_name    => ew_lb_api.g_app_name,
          p_dim_name    => ew_lb_api.g_dim_name,
          p_member_name => ew_lb_api.g_member_name,
          p_prop_label  => 'Start_Date'
        ), 'MM/DD/YYYY'
      );
      
      l_end_date := TO_DATE(
        ew_hierarchy.get_member_prop_value(
          p_app_name    => ew_lb_api.g_app_name,
          p_dim_name    => ew_lb_api.g_dim_name,
          p_member_name => ew_lb_api.g_member_name,
          p_prop_label  => 'End_Date'
        ), 'MM/DD/YYYY'
      );
      
      IF l_start_date IS NOT NULL AND l_end_date IS NOT NULL THEN
        l_duration := calculate_business_days(l_start_date, l_end_date);
        ew_lb_api.g_out_prop_value := TO_CHAR(l_duration) || ' days';
      END IF;
      
    WHEN 'Fiscal_Quarter' THEN
      -- Derive fiscal quarter from date
      l_start_date := NVL(
        TO_DATE(ew_lb_api.g_prop_value, 'MM/DD/YYYY'),
        SYSDATE
      );
      
      ew_lb_api.g_out_prop_value := 
        'FY' || TO_CHAR(l_start_date, 'YY') || '-Q' ||
        TO_CHAR(CEIL(TO_NUMBER(TO_CHAR(l_start_date, 'MM')) / 3));
      
    ELSE
      ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END CASE;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Date derivation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 5: Lookup Table Derivations

**Scenario**: Use reference tables to derive standardized values.

### Setup
```sql
-- Create lookup tables
CREATE TABLE derivation_lookups (
  lookup_type VARCHAR2(50),
  lookup_key VARCHAR2(100),
  lookup_value VARCHAR2(500),
  effective_date DATE,
  end_date DATE,
  CONSTRAINT pk_derivation_lookups 
    PRIMARY KEY (lookup_type, lookup_key)
);

-- Populate sample data
INSERT INTO derivation_lookups VALUES 
  ('COUNTRY_CURRENCY', 'USA', 'USD', SYSDATE-365, NULL);
INSERT INTO derivation_lookups VALUES 
  ('COUNTRY_CURRENCY', 'UK', 'GBP', SYSDATE-365, NULL);
INSERT INTO derivation_lookups VALUES 
  ('DEPT_CATEGORY', 'FIN', 'Finance & Accounting', SYSDATE-365, NULL);
INSERT INTO derivation_lookups VALUES 
  ('DEPT_CATEGORY', 'MKT', 'Marketing & Sales', SYSDATE-365, NULL);
COMMIT;
```

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'DERIVE_FROM_LOOKUP';
  l_lookup_key VARCHAR2(100);
  l_lookup_value VARCHAR2(500);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION get_lookup_value(
    p_type VARCHAR2,
    p_key VARCHAR2,
    p_date DATE DEFAULT SYSDATE
  ) RETURN VARCHAR2 IS
    l_value VARCHAR2(500);
  BEGIN
    SELECT lookup_value
    INTO l_value
    FROM derivation_lookups
    WHERE lookup_type = p_type
    AND lookup_key = p_key
    AND p_date BETWEEN effective_date 
                   AND NVL(end_date, p_date + 1);
    
    RETURN l_value;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN NULL;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Lookup derivation for: ' || ew_lb_api.g_prop_name);
  
  CASE ew_lb_api.g_prop_name
    WHEN 'Currency' THEN
      -- Derive currency from country
      l_lookup_key := ew_hierarchy.get_member_prop_value(
        p_app_name    => ew_lb_api.g_app_name,
        p_dim_name    => ew_lb_api.g_dim_name,
        p_member_name => ew_lb_api.g_member_name,
        p_prop_label  => 'Country'
      );
      
      l_lookup_value := get_lookup_value('COUNTRY_CURRENCY', l_lookup_key);
      
      ew_lb_api.g_out_prop_value := NVL(l_lookup_value, 'USD');
      log('Derived currency: ' || ew_lb_api.g_out_prop_value);
      
    WHEN 'Department_Category' THEN
      -- Derive category from department code
      l_lookup_key := SUBSTR(ew_lb_api.g_member_name, 1, 3);
      
      l_lookup_value := get_lookup_value('DEPT_CATEGORY', l_lookup_key);
      
      IF l_lookup_value IS NOT NULL THEN
        ew_lb_api.g_out_prop_value := l_lookup_value;
      ELSE
        ew_lb_api.g_out_prop_value := 'General';
      END IF;
      
      log('Derived category: ' || ew_lb_api.g_out_prop_value);
      
    ELSE
      ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END CASE;
  
  -- Cache frequently used lookups (optional)
  IF ew_lb_api.g_status = ew_lb_api.g_success THEN
    -- Store in package variable for session cache
    NULL; -- Implement caching logic if needed
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Lookup error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Testing Framework

### Comprehensive Test Script
```sql
DECLARE
  PROCEDURE test_derivation(
    p_test_name VARCHAR2,
    p_member_name VARCHAR2,
    p_prop_name VARCHAR2,
    p_input_value VARCHAR2,
    p_expected_output VARCHAR2
  ) IS
    l_result VARCHAR2(500);
  BEGIN
    -- Set context
    ew_lb_api.g_member_name := p_member_name;
    ew_lb_api.g_prop_name := p_prop_name;
    ew_lb_api.g_prop_value := p_input_value;
    ew_lb_api.g_action_code := 'CMC';
    
    -- Execute derivation
    -- (Call appropriate script here)
    
    -- Verify result
    IF ew_lb_api.g_out_prop_value = p_expected_output THEN
      DBMS_OUTPUT.PUT_LINE('✓ PASS: ' || p_test_name);
    ELSE
      DBMS_OUTPUT.PUT_LINE('✗ FAIL: ' || p_test_name);
      DBMS_OUTPUT.PUT_LINE('  Expected: ' || p_expected_output);
      DBMS_OUTPUT.PUT_LINE('  Actual: ' || ew_lb_api.g_out_prop_value);
    END IF;
  END;
  
BEGIN
  DBMS_OUTPUT.PUT_LINE('=== Property Derivation Tests ===');
  
  -- Test sequential ID generation
  test_derivation('Sequential ID', 'CC_Test', 'Member_ID', 
                  NULL, 'CC24001001');
  
  -- Test inheritance
  test_derivation('Inherit Currency', 'CC_Child', 'Currency', 
                  NULL, 'USD');
  
  -- Test calculation
  test_derivation('Calculate Risk', 'CC_Risk', 'Risk_Score', 
                  NULL, '75.5');
  
  -- Test date derivation
  test_derivation('Review Date', 'CC_New', 'Review_Date', 
                  NULL, TO_CHAR(SYSDATE + 90, 'MM/DD/YYYY'));
  
  DBMS_OUTPUT.PUT_LINE('=== Tests Complete ===');
END;
```

## Performance Optimization Tips

1. **Use Bulk Operations**
```sql
-- Process multiple derivations at once
FORALL i IN 1..l_members.COUNT
  UPDATE ew_member_properties
  SET prop_value = l_derived_values(i),
      last_updated = SYSDATE
  WHERE member_id = l_member_ids(i)
  AND prop_name = :prop_name;
```

2. **Implement Caching**
```sql
-- Package-level cache
CREATE OR REPLACE PACKAGE derivation_cache AS
  TYPE t_cache IS TABLE OF VARCHAR2(500) 
    INDEX BY VARCHAR2(200);
  g_cache t_cache;
  
  PROCEDURE clear_cache;
  FUNCTION get_cached(p_key VARCHAR2) RETURN VARCHAR2;
  PROCEDURE set_cached(p_key VARCHAR2, p_value VARCHAR2);
END;
```

3. **Optimize Queries**
```sql
-- Use indexes and minimize lookups
CREATE INDEX idx_derive_props 
ON ew_member_properties(app_dimension_id, member_id, prop_name);
```

## Next Steps

- [Configuration](configuration.md) - Setup guide
- [API Reference](../../api/packages/hierarchy.md) - Supporting functions
- [Property Validations](../property-validations/) - Validation scripts

---

!!! tip "Best Practice"
    Always test derivation scripts with edge cases including NULL values, maximum lengths, and boundary conditions before deploying to production.