# Property Validation Examples

This page provides comprehensive examples of Property Validation scripts for various business scenarios. Each example includes complete code, configuration steps, and testing approaches.

## Example 1: Email Validation with Domain Restrictions

**Scenario**: Validate email format and restrict to specific company domains.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VALIDATE_CORPORATE_EMAIL';
  c_email_pattern CONSTANT VARCHAR2(200) := 
    '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
  l_domain VARCHAR2(100);
  l_valid_domains VARCHAR2(500) := 'company.com,company.co.uk,subsidiary.com';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Allow NULL (unless required elsewhere)
  IF ew_lb_api.g_prop_value IS NULL THEN
    RETURN;
  END IF;
  
  log('Validating email: ' || ew_lb_api.g_prop_value);
  
  -- Check basic email format
  IF NOT REGEXP_LIKE(LOWER(ew_lb_api.g_prop_value), c_email_pattern) THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Invalid email format. Example: user@company.com';
    RETURN;
  END IF;
  
  -- Extract domain
  l_domain := LOWER(SUBSTR(ew_lb_api.g_prop_value, 
                           INSTR(ew_lb_api.g_prop_value, '@') + 1));
  
  -- Check if domain is in allowed list
  IF INSTR(l_valid_domains, l_domain) = 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Email must use company domain: ' || 
                            REPLACE(l_valid_domains, ',', ', ');
    log('Invalid domain: ' || l_domain);
    RETURN;
  END IF;
  
  -- Additional validation: Check for consecutive dots
  IF INSTR(ew_lb_api.g_prop_value, '..') > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Email cannot contain consecutive dots';
    RETURN;
  END IF;
  
  log('Email validation passed');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Email validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Test Cases
| Input | Expected Result |
|-------|----------------|
| john.doe@company.com | Pass |
| user@subsidiary.com | Pass |
| user@external.com | Fail - Invalid domain |
| invalid.email | Fail - Missing @ |
| user..name@company.com | Fail - Consecutive dots |

---

## Example 2: Hierarchical Code Validation

**Scenario**: Validate member codes based on their position in hierarchy.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VALIDATE_HIERARCHICAL_CODE';
  l_level NUMBER;
  l_parent_code VARCHAR2(50);
  l_expected_prefix VARCHAR2(20);
  l_code_pattern VARCHAR2(100);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only validate for Code property
  IF ew_lb_api.g_prop_name != 'Member_Code' THEN
    RETURN;
  END IF;
  
  log('Validating code: ' || ew_lb_api.g_prop_value || 
      ' for member: ' || ew_lb_api.g_member_name);
  
  -- Get member level
  l_level := ew_statistics.get_level(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_id       => ew_lb_api.g_member_id
  );
  
  -- Get parent code if not root
  IF ew_lb_api.g_parent_member_name IS NOT NULL THEN
    l_parent_code := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_parent_member_name,
      p_prop_label  => 'Member_Code'
    );
  END IF;
  
  -- Define validation rules by level
  CASE l_level
    WHEN 0 THEN
      -- Base level: Must start with parent code
      IF l_parent_code IS NOT NULL THEN
        l_expected_prefix := l_parent_code || '.';
        IF SUBSTR(ew_lb_api.g_prop_value, 1, LENGTH(l_expected_prefix)) 
           != l_expected_prefix THEN
          ew_lb_api.g_status := ew_lb_api.g_error;
          ew_lb_api.g_message := 'Code must start with parent code: ' || 
                                  l_expected_prefix;
        END IF;
      END IF;
      
    WHEN 1 THEN
      -- Level 1: Format XXX.YYY
      l_code_pattern := '^[A-Z]{3}\.[0-9]{3}$';
      IF NOT REGEXP_LIKE(ew_lb_api.g_prop_value, l_code_pattern) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Level 1 code format: XXX.YYY (e.g., FIN.001)';
      END IF;
      
    WHEN 2 THEN
      -- Level 2: Format XXX
      l_code_pattern := '^[A-Z]{3}$';
      IF NOT REGEXP_LIKE(ew_lb_api.g_prop_value, l_code_pattern) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Level 2 code format: XXX (e.g., FIN)';
      END IF;
      
    ELSE
      -- Root level: No restrictions
      NULL;
  END CASE;
  
  -- Check uniqueness within parent
  IF ew_lb_api.g_status = ew_lb_api.g_success THEN
    DECLARE
      l_count NUMBER;
    BEGIN
      SELECT COUNT(*)
      INTO l_count
      FROM ew_member_properties p
      JOIN ew_hierarchy_members h ON p.member_id = h.member_id
      WHERE p.app_dimension_id = ew_lb_api.g_app_dimension_id
      AND p.prop_name = 'Member_Code'
      AND p.prop_value = ew_lb_api.g_prop_value
      AND h.parent_id = (SELECT parent_id 
                         FROM ew_hierarchy_members 
                         WHERE member_id = ew_lb_api.g_member_id)
      AND p.member_id != ew_lb_api.g_member_id;
      
      IF l_count > 0 THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Code already exists under this parent';
      END IF;
    END;
  END IF;
  
  log('Validation result: ' || ew_lb_api.g_status);
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Code validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 3: Cross-Field Date Validation

**Scenario**: Validate date relationships and business rules across multiple date fields.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VALIDATE_DATE_RELATIONSHIPS';
  l_start_date DATE;
  l_end_date DATE;
  l_review_date DATE;
  l_current_date DATE := TRUNC(SYSDATE);
  l_date_format CONSTANT VARCHAR2(20) := 'MM/DD/YYYY';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION get_date_prop(p_prop_name VARCHAR2) RETURN DATE IS
    l_value VARCHAR2(50);
  BEGIN
    l_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => p_prop_name
    );
    
    IF l_value IS NOT NULL THEN
      RETURN TO_DATE(l_value, l_date_format);
    END IF;
    
    RETURN NULL;
  EXCEPTION
    WHEN OTHERS THEN
      RETURN NULL;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only validate date properties
  IF ew_lb_api.g_prop_name NOT IN ('Start_Date', 'End_Date', 'Review_Date') THEN
    RETURN;
  END IF;
  
  log('Validating date: ' || ew_lb_api.g_prop_name || 
      ' = ' || ew_lb_api.g_prop_value);
  
  -- First, validate date format
  BEGIN
    l_current_date := TO_DATE(ew_lb_api.g_prop_value, l_date_format);
  EXCEPTION
    WHEN OTHERS THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Invalid date format. Use MM/DD/YYYY';
      RETURN;
  END;
  
  -- Get related dates
  l_start_date := get_date_prop('Start_Date');
  l_end_date := get_date_prop('End_Date');
  l_review_date := get_date_prop('Review_Date');
  
  -- Apply validation rules based on property
  CASE ew_lb_api.g_prop_name
    WHEN 'Start_Date' THEN
      l_start_date := TO_DATE(ew_lb_api.g_prop_value, l_date_format);
      
      -- Start date cannot be in the past (more than 30 days)
      IF l_start_date < l_current_date - 30 THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Start date cannot be more than 30 days in the past';
      END IF;
      
      -- If end date exists, start must be before end
      IF l_end_date IS NOT NULL AND l_start_date > l_end_date THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Start date must be before end date';
      END IF;
      
    WHEN 'End_Date' THEN
      l_end_date := TO_DATE(ew_lb_api.g_prop_value, l_date_format);
      
      -- End date must be after start date
      IF l_start_date IS NOT NULL AND l_end_date < l_start_date THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'End date must be after start date ' || 
                                TO_CHAR(l_start_date, l_date_format);
      END IF;
      
      -- End date cannot be more than 5 years in future
      IF l_end_date > ADD_MONTHS(l_current_date, 60) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'End date cannot be more than 5 years in the future';
      END IF;
      
    WHEN 'Review_Date' THEN
      l_review_date := TO_DATE(ew_lb_api.g_prop_value, l_date_format);
      
      -- Review date must be between start and end
      IF l_start_date IS NOT NULL AND l_review_date < l_start_date THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Review date must be after start date';
      END IF;
      
      IF l_end_date IS NOT NULL AND l_review_date > l_end_date THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Review date must be before end date';
      END IF;
      
      -- Review date must be in the future
      IF l_review_date <= l_current_date THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Review date must be in the future';
      END IF;
  END CASE;
  
  log('Date validation result: ' || ew_lb_api.g_status);
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Date validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 4: Percentage Allocation Validation

**Scenario**: Ensure percentage allocations across related members sum to 100%.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VALIDATE_PERCENTAGE_ALLOCATION';
  l_current_value NUMBER;
  l_total_allocation NUMBER;
  l_sibling_count NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only validate percentage properties
  IF ew_lb_api.g_prop_name NOT IN ('Allocation_Percent', 'Ownership_Percent') THEN
    RETURN;
  END IF;
  
  log('Validating percentage: ' || ew_lb_api.g_prop_value);
  
  -- Validate numeric value
  BEGIN
    l_current_value := TO_NUMBER(ew_lb_api.g_prop_value);
  EXCEPTION
    WHEN VALUE_ERROR THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Percentage must be a valid number';
      RETURN;
  END;
  
  -- Check range 0-100
  IF l_current_value < 0 OR l_current_value > 100 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Percentage must be between 0 and 100';
    RETURN;
  END IF;
  
  -- Check precision (max 2 decimal places)
  IF l_current_value != ROUND(l_current_value, 2) THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Maximum 2 decimal places allowed';
    RETURN;
  END IF;
  
  -- Calculate total allocation among siblings
  BEGIN
    SELECT SUM(TO_NUMBER(p.prop_value)) - 
           NVL(TO_NUMBER(ew_lb_api.g_old_prop_value), 0) + 
           l_current_value,
           COUNT(DISTINCT h.member_id)
    INTO l_total_allocation, l_sibling_count
    FROM ew_hierarchy_members h
    JOIN ew_member_properties p ON h.member_id = p.member_id
    WHERE h.parent_id = (SELECT parent_id 
                         FROM ew_hierarchy_members 
                         WHERE member_id = ew_lb_api.g_member_id)
    AND p.prop_name = ew_lb_api.g_prop_name
    AND p.app_dimension_id = ew_lb_api.g_app_dimension_id;
    
    log('Total allocation: ' || l_total_allocation || 
        ' across ' || l_sibling_count || ' siblings');
    
    -- Allow slight variance for rounding (0.01%)
    IF l_total_allocation > 100.01 THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Total allocation exceeds 100% (Current total: ' || 
                              ROUND(l_total_allocation, 2) || '%)';
    END IF;
    
    -- Warning if not equal to 100 (but don't block)
    IF l_sibling_count > 1 AND 
       ABS(l_total_allocation - 100) > 0.01 AND
       l_total_allocation <= 100 THEN
      -- Could set warning status if supported
      log('Warning: Total allocation is ' || ROUND(l_total_allocation, 2) || '%');
    END IF;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Error calculating total: ' || SQLERRM);
  END;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Percentage validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 5: Complex Business Rule Validation

**Scenario**: Validate cost center attributes based on complex business rules.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VALIDATE_COST_CENTER_RULES';
  l_cc_type VARCHAR2(50);
  l_region VARCHAR2(50);
  l_budget NUMBER;
  l_headcount NUMBER;
  l_status VARCHAR2(20);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION get_prop(p_name VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => p_name
    );
  END;
  
  PROCEDURE validate_budget_rules IS
  BEGIN
    l_budget := TO_NUMBER(get_prop('Budget'));
    l_headcount := TO_NUMBER(get_prop('Headcount'));
    l_cc_type := get_prop('CC_Type');
    
    -- Rule 1: Admin cost centers limited budget
    IF l_cc_type = 'Administrative' AND l_budget > 500000 THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Administrative cost centers cannot exceed $500,000 budget';
      RETURN;
    END IF;
    
    -- Rule 2: Budget per headcount ratios
    IF l_headcount > 0 THEN
      DECLARE
        l_per_head NUMBER := l_budget / l_headcount;
      BEGIN
        IF l_cc_type = 'Production' AND l_per_head < 50000 THEN
          ew_lb_api.g_status := ew_lb_api.g_error;
          ew_lb_api.g_message := 'Production cost centers require minimum $50,000 per headcount';
        ELSIF l_cc_type = 'Sales' AND l_per_head < 75000 THEN
          ew_lb_api.g_status := ew_lb_api.g_error;
          ew_lb_api.g_message := 'Sales cost centers require minimum $75,000 per headcount';
        END IF;
      END;
    END IF;
  END;
  
  PROCEDURE validate_regional_rules IS
  BEGIN
    l_region := get_prop('Region');
    l_status := get_prop('Status');
    
    -- Rule: Certain regions require additional approval
    IF l_region IN ('EMEA', 'APAC') AND 
       ew_lb_api.g_prop_name = 'Status' AND
       ew_lb_api.g_prop_value = 'Active' THEN
      
      -- Check for approval flag
      IF NVL(get_prop('Regional_Approval'), 'N') != 'Y' THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'EMEA/APAC cost centers require regional approval before activation';
      END IF;
    END IF;
  END;
  
  PROCEDURE validate_manager_assignment IS
    l_manager VARCHAR2(100);
    l_manager_count NUMBER;
  BEGIN
    IF ew_lb_api.g_prop_name = 'Manager' THEN
      l_manager := ew_lb_api.g_prop_value;
      
      -- Check manager workload
      SELECT COUNT(*)
      INTO l_manager_count
      FROM ew_member_properties
      WHERE app_dimension_id = ew_lb_api.g_app_dimension_id
      AND prop_name = 'Manager'
      AND prop_value = l_manager
      AND member_id != ew_lb_api.g_member_id;
      
      IF l_manager_count >= 10 THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Manager ' || l_manager || 
                                ' already manages 10 cost centers (maximum allowed)';
      END IF;
    END IF;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only validate for cost center members
  IF NOT (ew_lb_api.g_member_name LIKE 'CC_%' OR 
          ew_lb_api.g_member_name LIKE 'COST_%') THEN
    RETURN;
  END IF;
  
  log('Validating business rules for: ' || ew_lb_api.g_member_name || 
      '.' || ew_lb_api.g_prop_name);
  
  -- Apply different validations based on property
  CASE ew_lb_api.g_prop_name
    WHEN 'Budget' THEN
      validate_budget_rules();
      
    WHEN 'Status' THEN
      validate_regional_rules();
      
    WHEN 'Manager' THEN
      validate_manager_assignment();
      
    WHEN 'CC_Type' THEN
      -- Validate against allowed values
      IF ew_lb_api.g_prop_value NOT IN 
         ('Administrative', 'Production', 'Sales', 'Support', 'Research') THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Invalid cost center type';
      END IF;
      
    ELSE
      NULL; -- No validation for other properties
  END CASE;
  
  log('Business rule validation result: ' || ew_lb_api.g_status);
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Business rule validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Testing Framework

### Automated Test Suite
```sql
CREATE OR REPLACE PROCEDURE test_property_validations IS
  PROCEDURE run_test(
    p_test_name VARCHAR2,
    p_prop_name VARCHAR2,
    p_prop_value VARCHAR2,
    p_expected_status VARCHAR2,
    p_expected_msg_pattern VARCHAR2 DEFAULT NULL
  ) IS
  BEGIN
    -- Set context
    ew_lb_api.g_prop_name := p_prop_name;
    ew_lb_api.g_prop_value := p_prop_value;
    ew_lb_api.g_member_name := 'TEST_MEMBER';
    
    -- Execute validation
    -- (Call appropriate validation script)
    
    -- Check results
    IF ew_lb_api.g_status = p_expected_status THEN
      DBMS_OUTPUT.PUT_LINE('✓ PASS: ' || p_test_name);
    ELSE
      DBMS_OUTPUT.PUT_LINE('✗ FAIL: ' || p_test_name);
      DBMS_OUTPUT.PUT_LINE('  Expected: ' || p_expected_status);
      DBMS_OUTPUT.PUT_LINE('  Actual: ' || ew_lb_api.g_status);
    END IF;
    
    -- Check error message pattern if provided
    IF p_expected_msg_pattern IS NOT NULL AND 
       ew_lb_api.g_message NOT LIKE p_expected_msg_pattern THEN
      DBMS_OUTPUT.PUT_LINE('  Message mismatch: ' || ew_lb_api.g_message);
    END IF;
  END;
  
BEGIN
  DBMS_OUTPUT.PUT_LINE('=== Running Property Validation Tests ===');
  
  -- Email validation tests
  run_test('Valid email', 'Email', 'user@company.com', 'S');
  run_test('Invalid email - no @', 'Email', 'usercompany.com', 'E', '%@%');
  run_test('Invalid domain', 'Email', 'user@external.com', 'E', '%domain%');
  
  -- Date validation tests
  run_test('Valid start date', 'Start_Date', TO_CHAR(SYSDATE+10, 'MM/DD/YYYY'), 'S');
  run_test('Past start date', 'Start_Date', '01/01/2000', 'E', '%past%');
  
  -- Percentage tests
  run_test('Valid percentage', 'Allocation_Percent', '25.5', 'S');
  run_test('Over 100%', 'Allocation_Percent', '101', 'E', '%100%');
  run_test('Negative percentage', 'Allocation_Percent', '-5', 'E', '%0%');
  
  DBMS_OUTPUT.PUT_LINE('=== Tests Complete ===');
END;
```

## Performance Considerations

### Optimization Techniques

1. **Cache Frequently Used Data**
```sql
-- Package variable for caching
g_cached_values VARCHAR2(4000);

-- Load once per session
IF g_cached_values IS NULL THEN
  SELECT LISTAGG(code, ',') WITHIN GROUP (ORDER BY code)
  INTO g_cached_values
  FROM valid_codes
  WHERE active = 'Y';
END IF;
```

2. **Minimize Database Calls**
```sql
-- Bad: Multiple queries
FOR i IN 1..10 LOOP
  SELECT ... INTO ... WHERE id = i;
END LOOP;

-- Good: Single query
SELECT ... BULK COLLECT INTO ... WHERE id IN (1,2,3...10);
```

3. **Use Appropriate Validation Timing**
```sql
-- Real-time (keystroke): Simple checks only
IF LENGTH(value) > 50 THEN error; END IF;

-- On field exit: Moderate complexity
validate_format(value);

-- On save: Complex validations
validate_cross_field_rules();
```

## Best Practices Summary

1. **User Experience**
   - Provide clear, actionable error messages
   - Include examples in error text
   - Validate progressively (simple to complex)

2. **Performance**
   - Cache static data
   - Optimize queries
   - Consider validation timing

3. **Maintainability**
   - Use constants for patterns
   - Log validation attempts
   - Document business rules

4. **Testing**
   - Test all validation paths
   - Include edge cases
   - Verify error messages

## Next Steps

- [Standard Validations](standard-validations.md) - Built-in validation types
- [API Reference](../../api/packages/hierarchy.md) - Supporting functions
- [Property Derivations](../property-derivations/) - Related derivation scripts

---

!!! warning "Performance Note"
    Remember that validation scripts execute on every keystroke for real-time validation. Keep the logic lightweight and optimize database queries to maintain UI responsiveness.