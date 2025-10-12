# Property Validation Examples

Property validation scripts ensure data quality by enforcing business rules when users create or modify member properties. These scripts execute before the property value is saved.

## Email Validation

🟢 **Level:** Basic  
**Purpose:** Validate email address format using regular expressions

```sql
/*
  Script: VALIDATE_EMAIL_FORMAT
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Validate email addresses match standard format
  
  Validates: username@domain.extension
  - Allows alphanumeric, dots, underscores, hyphens in username
  - Requires @ symbol
  - Domain must have at least one dot
  - Extension must be 2+ characters
*/
DECLARE
  c_script_name   VARCHAR2(100) := 'VALIDATE_EMAIL_FORMAT';
  c_email_pattern VARCHAR2(200) := '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
  v_email         VARCHAR2(500);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  -- Initialize status
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Get the email value
  v_email := TRIM(ew_lb_api.g_prop_value);
  
  log('Validating email: ' || v_email);
  
  -- Allow NULL emails (optional field)
  IF v_email IS NULL THEN
    log('Email is NULL - allowing');
    RETURN;
  END IF;
  
  -- Validate format
  IF NOT REGEXP_LIKE(v_email, c_email_pattern) THEN
    log('Invalid email format detected');
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Invalid email format. Please use: name@domain.com';
    RETURN;
  END IF;
  
  -- Additional validation: Check for common typos
  IF REGEXP_LIKE(v_email, '\.\.$|@@|^\.|\.$') THEN
    log('Email contains invalid characters');
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Email contains invalid character sequences';
    RETURN;
  END IF;
  
  log('Email validation passed');
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error validating email format';
END;
```

## Cost Center Format Validation

🟢 **Level:** Basic  
**Purpose:** Ensure cost center codes follow organizational standards

```sql
/*
  Script: VALIDATE_COST_CENTER
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Validate cost center format (CC-XXXX-YYY)
  
  Format Rules:
  - Must start with 'CC-'
  - Followed by 4 digits (department)
  - Hyphen separator
  - Ending with 3 digits (sub-department)
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'VALIDATE_COST_CENTER';
  c_cc_pattern     VARCHAR2(100) := '^CC-[0-9]{4}-[0-9]{3}$';
  v_cost_center    VARCHAR2(50);
  v_dept_code      VARCHAR2(4);
  v_sub_dept       VARCHAR2(3);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_cost_center := UPPER(TRIM(ew_lb_api.g_prop_value));
  
  log('Validating cost center: ' || v_cost_center);
  log('Parent member: ' || ew_lb_api.g_parent_member_name);
  
  -- Check basic format
  IF NOT REGEXP_LIKE(v_cost_center, c_cc_pattern) THEN
    log('Invalid format');
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Cost center must follow format: CC-XXXX-YYY (e.g., CC-1234-001)';
    RETURN;
  END IF;
  
  -- Extract components
  v_dept_code := SUBSTR(v_cost_center, 4, 4);
  v_sub_dept  := SUBSTR(v_cost_center, 9, 3);
  
  -- Validate department code range (1000-9999)
  IF TO_NUMBER(v_dept_code) < 1000 THEN
    log('Invalid department code: ' || v_dept_code);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Department code must be between 1000-9999';
    RETURN;
  END IF;
  
  -- Validate sub-department isn't 000
  IF v_sub_dept = '000' THEN
    log('Invalid sub-department: ' || v_sub_dept);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Sub-department cannot be 000';
    RETURN;
  END IF;
  
  log('Cost center validation passed');
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error validating cost center';
END;
```

## Date Range Validation

🟡 **Level:** Intermediate  
**Purpose:** Validate start and end dates with cross-property dependency

```sql
/*
  Script: VALIDATE_DATE_RANGE
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Validate date properties and ensure logical relationships
  
  Rules:
  - Dates must be in format: YYYY-MM-DD
  - Start date must be before end date
  - Dates must be within reasonable range (2000-2050)
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'VALIDATE_DATE_RANGE';
  c_date_pattern   VARCHAR2(100) := '^[0-9]{4}-[0-9]{2}-[0-9]{2}$';
  v_current_date   DATE;
  v_other_date     DATE;
  v_start_date     DATE;
  v_end_date       DATE;
  v_prop_value     VARCHAR2(50);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION get_property_value(p_prop_name IN VARCHAR2) RETURN VARCHAR2 IS
    v_value VARCHAR2(500);
  BEGIN
    -- Use API to get other property value
    v_value := ew_api.get_property_value(
                 p_app_id     => ew_lb_api.g_app_id,
                 p_dim_id     => ew_lb_api.g_dim_id,
                 p_member_name => ew_lb_api.g_member_name,
                 p_prop_name   => p_prop_name
               );
    RETURN v_value;
  END get_property_value;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_prop_value := TRIM(ew_lb_api.g_prop_value);
  
  log('Validating date property: ' || ew_lb_api.g_prop_name);
  log('Value: ' || v_prop_value);
  
  -- Check format
  IF NOT REGEXP_LIKE(v_prop_value, c_date_pattern) THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Date must be in format YYYY-MM-DD';
    RETURN;
  END IF;
  
  -- Convert to date
  BEGIN
    v_current_date := TO_DATE(v_prop_value, 'YYYY-MM-DD');
  EXCEPTION
    WHEN OTHERS THEN
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Invalid date value';
      RETURN;
  END;
  
  -- Check reasonable range
  IF v_current_date < DATE '2000-01-01' OR v_current_date > DATE '2050-12-31' THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Date must be between 2000 and 2050';
    RETURN;
  END IF;
  
  -- Cross-property validation
  IF ew_lb_api.g_prop_name = 'StartDate' THEN
    -- Check if end date exists and validate relationship
    v_other_date := TO_DATE(get_property_value('EndDate'), 'YYYY-MM-DD');
    
    IF v_other_date IS NOT NULL AND v_current_date > v_other_date THEN
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Start date must be before end date';
      RETURN;
    END IF;
    
  ELSIF ew_lb_api.g_prop_name = 'EndDate' THEN
    -- Check if start date exists and validate relationship
    v_other_date := TO_DATE(get_property_value('StartDate'), 'YYYY-MM-DD');
    
    IF v_other_date IS NOT NULL AND v_current_date < v_other_date THEN
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'End date must be after start date';
      RETURN;
    END IF;
  END IF;
  
  log('Date validation passed');
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error validating date';
END;
```

## Account Number Validation with Check Digit

🟡 **Level:** Intermediate  
**Purpose:** Validate account numbers using Luhn algorithm (check digit)

```sql
/*
  Script: VALIDATE_ACCOUNT_WITH_CHECKDIGIT
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Validate account numbers using Luhn check digit algorithm
  
  The Luhn algorithm is commonly used for credit card and account validation
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'VALIDATE_ACCOUNT_WITH_CHECKDIGIT';
  v_account        VARCHAR2(50);
  v_sum            NUMBER := 0;
  v_digit          NUMBER;
  v_double         NUMBER;
  v_position       NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION validate_luhn(p_number IN VARCHAR2) RETURN BOOLEAN IS
    v_sum      NUMBER := 0;
    v_digit    NUMBER;
    v_double   NUMBER;
    v_even     BOOLEAN := FALSE;
  BEGIN
    -- Process digits from right to left
    FOR i IN REVERSE 1..LENGTH(p_number) LOOP
      v_digit := TO_NUMBER(SUBSTR(p_number, i, 1));
      
      IF v_even THEN
        v_double := v_digit * 2;
        IF v_double > 9 THEN
          v_double := v_double - 9;
        END IF;
        v_sum := v_sum + v_double;
      ELSE
        v_sum := v_sum + v_digit;
      END IF;
      
      v_even := NOT v_even;
    END LOOP;
    
    RETURN MOD(v_sum, 10) = 0;
    
  EXCEPTION
    WHEN OTHERS THEN
      RETURN FALSE;
  END validate_luhn;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_account := TRIM(ew_lb_api.g_prop_value);
  
  log('Validating account: ' || v_account);
  
  -- Check if all digits
  IF NOT REGEXP_LIKE(v_account, '^[0-9]+$') THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Account number must contain only digits';
    RETURN;
  END IF;
  
  -- Check length (example: 10-16 digits)
  IF LENGTH(v_account) < 10 OR LENGTH(v_account) > 16 THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Account number must be between 10 and 16 digits';
    RETURN;
  END IF;
  
  -- Validate check digit
  IF NOT validate_luhn(v_account) THEN
    log('Check digit validation failed');
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Invalid account number - check digit verification failed';
    RETURN;
  END IF;
  
  log('Account validation passed');
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error validating account number';
END;
```

## Business Rule: Budget Threshold Validation

🔴 **Level:** Advanced  
**Purpose:** Complex validation involving calculations and database lookups

```sql
/*
  Script: VALIDATE_BUDGET_THRESHOLD
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Validate budget amounts against organizational thresholds
  
  Rules:
  - Budget increases > 10% require justification
  - Budgets > $1M require executive approval flag
  - Department total cannot exceed allocated limit
*/
DECLARE
  c_script_name        VARCHAR2(100) := 'VALIDATE_BUDGET_THRESHOLD';
  c_increase_threshold NUMBER := 0.10; -- 10%
  c_exec_threshold     NUMBER := 1000000; -- $1M
  
  v_new_budget         NUMBER;
  v_old_budget         NUMBER;
  v_increase_pct       NUMBER;
  v_dept_total         NUMBER;
  v_dept_limit         NUMBER;
  v_justification      VARCHAR2(1000);
  v_exec_approval      VARCHAR2(1);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION get_department_total(p_dept IN VARCHAR2) RETURN NUMBER IS
    v_total NUMBER;
  BEGIN
    SELECT SUM(TO_NUMBER(prop_value))
    INTO   v_total
    FROM   ew_member_properties
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    prop_name = 'Budget'
    AND    member_name LIKE p_dept || '%'
    AND    member_name != ew_lb_api.g_member_name;
    
    RETURN NVL(v_total, 0);
  EXCEPTION
    WHEN OTHERS THEN
      RETURN 0;
  END get_department_total;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only validate Budget property
  IF ew_lb_api.g_prop_name != 'Budget' THEN
    RETURN;
  END IF;
  
  log('Validating budget for: ' || ew_lb_api.g_member_name);
  
  -- Parse budget values
  BEGIN
    v_new_budget := TO_NUMBER(ew_lb_api.g_prop_value);
    v_old_budget := TO_NUMBER(NVL(ew_lb_api.g_old_prop_value, '0'));
  EXCEPTION
    WHEN OTHERS THEN
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Budget must be a valid number';
      RETURN;
  END;
  
  -- Check for negative budget
  IF v_new_budget < 0 THEN
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Budget cannot be negative';
    RETURN;
  END IF;
  
  -- Calculate increase percentage
  IF v_old_budget > 0 THEN
    v_increase_pct := (v_new_budget - v_old_budget) / v_old_budget;
    
    log('Old budget: ' || v_old_budget);
    log('New budget: ' || v_new_budget);
    log('Increase %: ' || ROUND(v_increase_pct * 100, 2));
    
    -- Check if increase exceeds threshold
    IF v_increase_pct > c_increase_threshold THEN
      -- Check for justification
      v_justification := ew_api.get_property_value(
                           p_app_id      => ew_lb_api.g_app_id,
                           p_dim_id      => ew_lb_api.g_dim_id,
                           p_member_name => ew_lb_api.g_member_name,
                           p_prop_name   => 'BudgetJustification'
                         );
      
      IF v_justification IS NULL OR LENGTH(v_justification) < 50 THEN
        ew_lb_api.g_status  := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Budget increase >' || 
                               ROUND(c_increase_threshold * 100) || 
                               '% requires justification (min 50 characters)';
        RETURN;
      END IF;
    END IF;
  END IF;
  
  -- Check executive approval requirement
  IF v_new_budget > c_exec_threshold THEN
    v_exec_approval := ew_api.get_property_value(
                         p_app_id      => ew_lb_api.g_app_id,
                         p_dim_id      => ew_lb_api.g_dim_id,
                         p_member_name => ew_lb_api.g_member_name,
                         p_prop_name   => 'ExecutiveApproval'
                       );
    
    IF NVL(v_exec_approval, 'N') != 'Y' THEN
      ew_lb_api.g_status  := ew_lb_api.g_warning;
      ew_lb_api.g_message := 'Budget >' || 
                             TO_CHAR(c_exec_threshold, '$999,999,999') || 
                             ' requires executive approval flag';
    END IF;
  END IF;
  
  -- Check department total
  IF SUBSTR(ew_lb_api.g_member_name, 1, 4) IS NOT NULL THEN
    v_dept_total := get_department_total(SUBSTR(ew_lb_api.g_member_name, 1, 4));
    v_dept_limit := 5000000; -- Example: $5M per department
    
    IF (v_dept_total + v_new_budget) > v_dept_limit THEN
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Department budget limit exceeded. Max: ' ||
                             TO_CHAR(v_dept_limit, '$999,999,999');
      RETURN;
    END IF;
  END IF;
  
  log('Budget validation completed with status: ' || ew_lb_api.g_status);
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error validating budget';
END;
```

## Testing Property Validations

### Test Harness Script

```sql
/*
  Script: TEST_PROPERTY_VALIDATIONS
  Purpose: Test framework for property validation scripts
*/
DECLARE
  c_script_name VARCHAR2(100) := 'TEST_PROPERTY_VALIDATIONS';
  v_test_count  NUMBER := 0;
  v_pass_count  NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END log;
  
  PROCEDURE run_test(p_test_name  IN VARCHAR2,
                     p_prop_value IN VARCHAR2,
                     p_expected   IN VARCHAR2) IS
  BEGIN
    v_test_count := v_test_count + 1;
    
    -- Set test value
    ew_lb_api.g_prop_value := p_prop_value;
    
    -- Run validation (insert your validation logic here)
    -- ... validation code ...
    
    -- Check result
    IF ew_lb_api.g_status = p_expected THEN
      v_pass_count := v_pass_count + 1;
      log('✓ PASS: ' || p_test_name);
    ELSE
      log('✗ FAIL: ' || p_test_name || 
          ' (Expected: ' || p_expected || 
          ', Got: ' || ew_lb_api.g_status || ')');
    END IF;
  END run_test;
  
BEGIN
  log('Starting property validation tests');
  
  -- Email validation tests
  run_test('Valid email', 'user@example.com', 'S');
  run_test('Missing @', 'userexample.com', 'E');
  run_test('Missing domain', 'user@', 'E');
  run_test('Double @', 'user@@example.com', 'E');
  
  -- Cost center tests  
  run_test('Valid cost center', 'CC-1234-001', 'S');
  run_test('Invalid format', 'CC1234001', 'E');
  run_test('Invalid department', 'CC-0999-001', 'E');
  
  log('Test Results: ' || v_pass_count || '/' || v_test_count || ' passed');
  
END;
```

## Best Practices

1. **Always validate NULL values** - Decide if they're allowed
2. **Use appropriate error levels** - ERROR vs WARNING
3. **Provide helpful error messages** - Include format examples
4. **Log validation attempts** - For audit and debugging
5. **Handle exceptions gracefully** - Don't expose system errors
6. **Consider performance** - Optimize for bulk operations
7. **Test edge cases** - Maximum lengths, special characters
8. **Document business rules** - In script comments

## Next Steps

- See [Property Derivation Examples](property-derivation.md)
- Review [API Reference](../api/) for available functions
- Learn about [Performance Optimization](../advanced/performance.md)