# Property Mapping Examples

This page provides comprehensive examples of Property Mapping scripts for various real-world scenarios. Each example includes complete code, configuration steps, and testing guidelines.

## Example 1: Status Code Transformation

**Scenario**: Transform single-character status codes to full descriptions across applications.

### Mapping Table Setup
```sql
-- Create reference table for status mappings
CREATE TABLE status_code_mappings (
  code VARCHAR2(10) PRIMARY KEY,
  description VARCHAR2(100),
  active_flag VARCHAR2(1) DEFAULT 'Y'
);

INSERT INTO status_code_mappings VALUES ('A', 'Active', 'Y');
INSERT INTO status_code_mappings VALUES ('I', 'Inactive', 'Y');
INSERT INTO status_code_mappings VALUES ('P', 'Pending Review', 'Y');
INSERT INTO status_code_mappings VALUES ('S', 'Suspended', 'Y');
INSERT INTO status_code_mappings VALUES ('T', 'Terminated', 'Y');
COMMIT;
```

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_STATUS_CODES';
  l_description VARCHAR2(100);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Mapping status for member: ' || ew_lb_api.g_member_name);
  log('Input value: ' || ew_lb_api.g_prop_value);
  
  -- Skip if NULL
  IF ew_lb_api.g_prop_value IS NULL THEN
    ew_lb_api.g_out_prop_value := 'Not Specified';
    log('NULL value mapped to: Not Specified');
    RETURN;
  END IF;
  
  -- Look up description
  BEGIN
    SELECT description
    INTO l_description
    FROM status_code_mappings
    WHERE code = ew_lb_api.g_prop_value
    AND active_flag = 'Y';
    
    ew_lb_api.g_out_prop_value := l_description;
    log('Mapped to: ' || l_description);
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- Unknown code - keep original
      ew_lb_api.g_out_prop_value := 'Unknown (' || ew_lb_api.g_prop_value || ')';
      log('Unknown code, mapped to: ' || ew_lb_api.g_out_prop_value);
      
    WHEN OTHERS THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Error mapping status: ' || SQLERRM;
      log('Error: ' || SQLERRM);
  END;
  
END;
```

### Test Cases
| Input Code | Expected Output |
|------------|----------------|
| A | Active |
| I | Inactive |
| P | Pending Review |
| NULL | Not Specified |
| X | Unknown (X) |

---

## Example 2: Currency Conversion Property

**Scenario**: Convert amounts between currencies based on member's country property.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_CURRENCY_AMOUNTS';
  l_source_currency VARCHAR2(10);
  l_target_currency VARCHAR2(10);
  l_amount NUMBER;
  l_rate NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION get_exchange_rate(
    p_from_curr VARCHAR2,
    p_to_curr VARCHAR2,
    p_date DATE DEFAULT SYSDATE
  ) RETURN NUMBER IS
    l_rate NUMBER;
  BEGIN
    -- Simplified rate lookup (replace with actual rate table)
    IF p_from_curr = p_to_curr THEN
      RETURN 1;
    END IF;
    
    -- Sample rates (implement actual rate retrieval)
    CASE 
      WHEN p_from_curr = 'USD' AND p_to_curr = 'EUR' THEN l_rate := 0.85;
      WHEN p_from_curr = 'USD' AND p_to_curr = 'GBP' THEN l_rate := 0.73;
      WHEN p_from_curr = 'EUR' AND p_to_curr = 'USD' THEN l_rate := 1.18;
      WHEN p_from_curr = 'GBP' AND p_to_curr = 'USD' THEN l_rate := 1.37;
      ELSE l_rate := 1;
    END CASE;
    
    RETURN l_rate;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only process amount properties
  IF ew_lb_api.g_prop_name NOT IN ('Budget_Amount', 'Forecast_Amount') THEN
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    RETURN;
  END IF;
  
  log('Converting amount for: ' || ew_lb_api.g_member_name);
  
  -- Get source currency from member's country
  l_source_currency := ew_hierarchy.get_member_prop_value(
    p_app_name    => ew_lb_api.g_src_app_name,
    p_dim_name    => ew_lb_api.g_src_dim_name,
    p_member_name => ew_lb_api.g_member_name,
    p_prop_label  => 'Currency'
  );
  
  -- Target currency (could be parameterized)
  l_target_currency := 'USD';
  
  -- Convert amount
  BEGIN
    l_amount := TO_NUMBER(ew_lb_api.g_prop_value);
    l_rate := get_exchange_rate(l_source_currency, l_target_currency);
    
    ew_lb_api.g_out_prop_value := 
      TO_CHAR(ROUND(l_amount * l_rate, 2));
      
    log('Converted ' || l_amount || ' ' || l_source_currency || 
        ' to ' || ew_lb_api.g_out_prop_value || ' ' || l_target_currency);
        
  EXCEPTION
    WHEN VALUE_ERROR THEN
      -- Not a number, keep original
      ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
      log('Non-numeric value, no conversion');
  END;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Currency conversion error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 3: Concatenated Property Creation

**Scenario**: Create a combined description property from multiple source properties.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_COMBINED_DESCRIPTION';
  l_dept_code VARCHAR2(50);
  l_dept_name VARCHAR2(100);
  l_location VARCHAR2(100);
  l_manager VARCHAR2(100);
  l_combined VARCHAR2(500);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION get_prop(p_prop_name VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_src_app_name,
      p_dim_name    => ew_lb_api.g_src_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => p_prop_name
    );
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only process for Description property
  IF ew_lb_api.g_prop_name != 'Description' THEN
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    RETURN;
  END IF;
  
  log('Creating combined description for: ' || ew_lb_api.g_member_name);
  
  -- Get component properties
  l_dept_code := ew_lb_api.g_member_name;
  l_dept_name := get_prop('Department_Name');
  l_location := get_prop('Location');
  l_manager := get_prop('Manager_Name');
  
  -- Build combined description
  l_combined := l_dept_code;
  
  IF l_dept_name IS NOT NULL THEN
    l_combined := l_combined || ' - ' || l_dept_name;
  END IF;
  
  IF l_location IS NOT NULL THEN
    l_combined := l_combined || ' (' || l_location || ')';
  END IF;
  
  IF l_manager IS NOT NULL THEN
    l_combined := l_combined || ' [Mgr: ' || l_manager || ']';
  END IF;
  
  ew_lb_api.g_out_prop_value := l_combined;
  log('Combined description: ' || l_combined);
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error creating description: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Example Output
```
Input Properties:
- Member Name: "FIN001"
- Department_Name: "Finance"
- Location: "New York"
- Manager_Name: "John Smith"

Output Description:
"FIN001 - Finance (New York) [Mgr: John Smith]"
```

---

## Example 4: Date Format Conversion

**Scenario**: Convert date properties between different formats for various applications.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_DATE_FORMATS';
  l_input_date DATE;
  l_source_format VARCHAR2(30);
  l_target_format VARCHAR2(30);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Only process date properties
  IF ew_lb_api.g_prop_name NOT IN ('Start_Date', 'End_Date', 'Review_Date') THEN
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    RETURN;
  END IF;
  
  log('Converting date for: ' || ew_lb_api.g_member_name);
  log('Input value: ' || ew_lb_api.g_prop_value);
  
  -- Determine format based on source/target applications
  l_source_format := CASE ew_lb_api.g_src_app_name
                       WHEN 'SAP' THEN 'YYYYMMDD'
                       WHEN 'ORACLE_ERP' THEN 'DD-MON-YYYY'
                       ELSE 'MM/DD/YYYY'
                     END;
                     
  l_target_format := CASE ew_lb_api.g_tgt_app_name
                       WHEN 'HFM' THEN 'MM/DD/YYYY'
                       WHEN 'PLANNING' THEN 'DD/MM/YYYY'
                       ELSE 'YYYY-MM-DD'
                     END;
  
  -- Convert date
  BEGIN
    -- Parse input date
    l_input_date := TO_DATE(ew_lb_api.g_prop_value, l_source_format);
    
    -- Format for target
    ew_lb_api.g_out_prop_value := TO_CHAR(l_input_date, l_target_format);
    
    log('Converted to: ' || ew_lb_api.g_out_prop_value);
    
  EXCEPTION
    WHEN OTHERS THEN
      -- Invalid date, keep original or set default
      ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
      log('Invalid date format, keeping original');
  END;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Date conversion error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Example 5: Hierarchical Property Inheritance

**Scenario**: If a property is not set at member level, inherit from parent.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_INHERIT_PROPERTY';
  l_current_value VARCHAR2(500);
  l_parent_name VARCHAR2(100);
  l_parent_value VARCHAR2(500);
  l_max_levels NUMBER := 5;
  l_level_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Properties that support inheritance
  IF ew_lb_api.g_prop_name NOT IN ('Region', 'Currency', 'Tax_Rate') THEN
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    RETURN;
  END IF;
  
  log('Checking inheritance for: ' || ew_lb_api.g_member_name);
  
  l_current_value := ew_lb_api.g_prop_value;
  
  -- If value exists, use it
  IF l_current_value IS NOT NULL AND l_current_value != 'INHERIT' THEN
    ew_lb_api.g_out_prop_value := l_current_value;
    log('Using member''s own value: ' || l_current_value);
    RETURN;
  END IF;
  
  -- Walk up hierarchy to find inherited value
  l_parent_name := ew_lb_api.g_member_name;
  
  WHILE l_level_count < l_max_levels LOOP
    -- Get parent
    l_parent_name := ew_hierarchy.get_primary_parent_name(
      p_app_dimension_id => ew_lb_api.g_app_dimension_id,
      p_member_name     => l_parent_name
    );
    
    EXIT WHEN l_parent_name IS NULL;
    
    -- Check parent's property
    l_parent_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_src_app_name,
      p_dim_name    => ew_lb_api.g_src_dim_name,
      p_member_name => l_parent_name,
      p_prop_label  => ew_lb_api.g_prop_name
    );
    
    IF l_parent_value IS NOT NULL AND l_parent_value != 'INHERIT' THEN
      ew_lb_api.g_out_prop_value := l_parent_value;
      log('Inherited from ' || l_parent_name || ': ' || l_parent_value);
      RETURN;
    END IF;
    
    l_level_count := l_level_count + 1;
  END LOOP;
  
  -- No inherited value found, use default
  ew_lb_api.g_out_prop_value := CASE ew_lb_api.g_prop_name
                                   WHEN 'Region' THEN 'GLOBAL'
                                   WHEN 'Currency' THEN 'USD'
                                   WHEN 'Tax_Rate' THEN '0'
                                   ELSE 'DEFAULT'
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

## Example 6: Validation with Auto-Correction

**Scenario**: Validate property values and auto-correct common issues.

### Script Implementation
```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_VALIDATE_CORRECT';
  l_original_value VARCHAR2(500);
  l_corrected_value VARCHAR2(500);
  l_validation_msg VARCHAR2(1000);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
  FUNCTION validate_email(p_email VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Basic email validation and correction
    IF p_email IS NULL THEN
      RETURN NULL;
    END IF;
    
    -- Remove spaces
    RETURN LOWER(TRIM(REPLACE(p_email, ' ', '')));
  END;
  
  FUNCTION validate_phone(p_phone VARCHAR2) RETURN VARCHAR2 IS
    l_digits VARCHAR2(20);
  BEGIN
    -- Extract only digits
    l_digits := REGEXP_REPLACE(p_phone, '[^0-9]', '');
    
    -- Format as standard
    IF LENGTH(l_digits) = 10 THEN
      RETURN SUBSTR(l_digits, 1, 3) || '-' || 
             SUBSTR(l_digits, 4, 3) || '-' || 
             SUBSTR(l_digits, 7, 4);
    ELSE
      RETURN p_phone; -- Keep original if not 10 digits
    END IF;
  END;
  
  FUNCTION validate_postal_code(p_code VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- US ZIP code validation
    IF REGEXP_LIKE(p_code, '^[0-9]{5}$') THEN
      RETURN p_code;
    ELSIF REGEXP_LIKE(p_code, '^[0-9]{9}$') THEN
      -- Format 9-digit ZIP
      RETURN SUBSTR(p_code, 1, 5) || '-' || SUBSTR(p_code, 6, 4);
    ELSE
      -- Remove spaces and uppercase
      RETURN UPPER(REPLACE(p_code, ' ', ''));
    END IF;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  l_original_value := ew_lb_api.g_prop_value;
  
  log('Validating ' || ew_lb_api.g_prop_name || 
      ' for ' || ew_lb_api.g_member_name);
  
  -- Apply validation based on property type
  CASE ew_lb_api.g_prop_name
    WHEN 'Email' THEN
      l_corrected_value := validate_email(l_original_value);
      
    WHEN 'Phone' THEN
      l_corrected_value := validate_phone(l_original_value);
      
    WHEN 'Postal_Code' THEN
      l_corrected_value := validate_postal_code(l_original_value);
      
    WHEN 'Country_Code' THEN
      -- Uppercase and trim
      l_corrected_value := UPPER(TRIM(l_original_value));
      
    ELSE
      -- No validation needed
      l_corrected_value := l_original_value;
  END CASE;
  
  -- Set output
  ew_lb_api.g_out_prop_value := l_corrected_value;
  
  -- Log if corrected
  IF l_original_value != l_corrected_value THEN
    log('Corrected from "' || l_original_value || 
        '" to "' || l_corrected_value || '"');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

---

## Testing and Validation

### Test Framework
```sql
-- Create test harness for property mapping
DECLARE
  PROCEDURE test_mapping(
    p_member_name VARCHAR2,
    p_prop_name VARCHAR2,
    p_prop_value VARCHAR2,
    p_expected VARCHAR2
  ) IS
    l_result VARCHAR2(500);
  BEGIN
    -- Set test values
    ew_lb_api.g_member_name := p_member_name;
    ew_lb_api.g_prop_name := p_prop_name;
    ew_lb_api.g_prop_value := p_prop_value;
    
    -- Execute mapping script
    -- (Script execution here)
    
    -- Check result
    IF ew_lb_api.g_out_prop_value = p_expected THEN
      DBMS_OUTPUT.PUT_LINE('PASS: ' || p_prop_name || 
                           ' = ' || p_expected);
    ELSE
      DBMS_OUTPUT.PUT_LINE('FAIL: ' || p_prop_name || 
                           ' expected ' || p_expected || 
                           ' got ' || ew_lb_api.g_out_prop_value);
    END IF;
  END;
BEGIN
  -- Run test cases
  test_mapping('CC100', 'Status', 'A', 'Active');
  test_mapping('CC100', 'Status', 'I', 'Inactive');
  test_mapping('CC100', 'Email', 'JOHN.DOE @EXAMPLE.COM', 
               'john.doe@example.com');
  test_mapping('CC100', 'Phone', '(555) 123-4567', '555-123-4567');
END;
```

### Performance Monitoring
```sql
-- Monitor property mapping performance
SELECT pm.mapping_id,
       pm.source_property,
       pm.target_property,
       COUNT(*) as execution_count,
       AVG(pm.execution_time) as avg_time_ms,
       MAX(pm.execution_time) as max_time_ms,
       MIN(pm.execution_time) as min_time_ms
FROM   property_mapping_log pm
WHERE  pm.execution_date >= TRUNC(SYSDATE)
GROUP BY pm.mapping_id, 
         pm.source_property, 
         pm.target_property
ORDER BY avg_time_ms DESC;
```

## Best Practices Summary

1. **Always validate input**: Check for NULL and invalid formats
2. **Implement error handling**: Gracefully handle exceptions
3. **Use caching**: Cache frequently accessed lookup data
4. **Log appropriately**: Balance detail with performance
5. **Test thoroughly**: Cover all edge cases and data types
6. **Document transformations**: Clear comments in code
7. **Monitor performance**: Track execution times
8. **Version control**: Maintain script versions

## Next Steps

- [Configuration](configuration.md) - Setup guide
- [API Reference](../../api/packages/hierarchy.md) - Supporting functions
- [Property Validations](../property-validations/) - Related validation scripts

---

!!! tip "Testing Tip"
    Create a dedicated test dimension with sample data covering all scenarios. This allows safe testing without affecting production data.