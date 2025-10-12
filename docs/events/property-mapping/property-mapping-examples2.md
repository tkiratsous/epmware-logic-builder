# Property Mapping Examples

This page provides practical examples of Property Mapping Logic Scripts for common scenarios.

## Example 1: Simple Alias Transformation

**Scenario:** Add application prefix to aliases when syncing between applications.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'ALIAS_PREFIX_MAPPING';
  c_prefix      CONSTANT VARCHAR2(20)  := '[HFM] ';
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Add prefix to alias
  IF ew_lb_api.g_prop_name = 'ALIAS' THEN
    IF ew_lb_api.g_prop_value IS NOT NULL THEN
      ew_lb_api.g_out_prop_value := c_prefix || ew_lb_api.g_prop_value;
    ELSE
      -- Handle null aliases
      ew_lb_api.g_out_prop_value := c_prefix || ew_lb_api.g_member_name;
    END IF;
  ELSE
    -- Pass through other properties
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END IF;
  
  ew_debug.log('Mapped alias: ' || ew_lb_api.g_prop_value || 
               ' -> ' || ew_lb_api.g_out_prop_value,
               c_script_name);
               
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error in alias mapping: ' || SQLERRM;
END;
```

## Example 2: Account Type Mapping

**Scenario:** Map verbose account types to codes for different application requirements.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'ACCOUNT_TYPE_MAPPER';
  
  FUNCTION map_account_type(p_value VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    RETURN CASE p_value
      -- Planning to HFM mapping
      WHEN 'Revenue'          THEN 'REV'
      WHEN 'Expense'          THEN 'EXP'
      WHEN 'Asset'            THEN 'AST'
      WHEN 'Liability'        THEN 'LIAB'
      WHEN 'Equity'           THEN 'EQU'
      WHEN 'Statistical'      THEN 'STAT'
      -- Reverse mapping (HFM to Planning)
      WHEN 'REV'              THEN 'Revenue'
      WHEN 'EXP'              THEN 'Expense'
      WHEN 'AST'              THEN 'Asset'
      WHEN 'LIAB'             THEN 'Liability'
      WHEN 'EQU'              THEN 'Equity'
      WHEN 'STAT'             THEN 'Statistical'
      -- Default
      ELSE p_value
    END;
  END map_account_type;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  IF ew_lb_api.g_prop_name IN ('ACCOUNT_TYPE', 'ACCOUNTTYPE', 'ACCTYPE') THEN
    ew_lb_api.g_out_prop_value := map_account_type(ew_lb_api.g_prop_value);
    
    ew_debug.log('Account type mapped: ' || ew_lb_api.g_prop_value || 
                 ' -> ' || ew_lb_api.g_out_prop_value,
                 c_script_name);
  ELSE
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := SQLERRM;
END;
```

![Account Type Mapping Flow](../../assets/images/account-type-mapping.png)
*Figure: Account type transformation between applications*

## Example 3: Consolidation Method Mapping

**Scenario:** Map consolidation methods based on ownership percentage and control type.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CONSOLIDATION_MAPPER';
  l_ownership_pct NUMBER;
  l_control_type VARCHAR2(100);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  IF ew_lb_api.g_prop_name = 'CONSOLIDATION_METHOD' THEN
    -- Get related properties for decision
    l_ownership_pct := TO_NUMBER(
      ew_hierarchy.get_member_prop_value(
        p_app_name    => ew_lb_api.g_app_name,
        p_dim_name    => ew_lb_api.g_dim_name,
        p_member_name => ew_lb_api.g_member_name,
        p_prop_label  => 'Ownership%'
      )
    );
    
    l_control_type := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => 'ControlType'
    );
    
    -- Determine consolidation method
    IF l_ownership_pct >= 50 AND l_control_type = 'Full' THEN
      ew_lb_api.g_out_prop_value := 'FULL';
    ELSIF l_ownership_pct >= 20 AND l_ownership_pct < 50 THEN
      ew_lb_api.g_out_prop_value := 'EQUITY';
    ELSIF l_control_type = 'Joint' THEN
      ew_lb_api.g_out_prop_value := 'PROPORTIONAL';
    ELSE
      ew_lb_api.g_out_prop_value := 'NONE';
    END IF;
    
    ew_debug.log('Consolidation: Ownership=' || l_ownership_pct || 
                 '%, Control=' || l_control_type || 
                 ' -> Method=' || ew_lb_api.g_out_prop_value,
                 c_script_name);
  ELSE
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error determining consolidation: ' || SQLERRM;
END;
```

## Example 4: Multi-Language Alias Mapping

**Scenario:** Map aliases across different languages with fallback logic.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MULTI_LANGUAGE_ALIAS';
  l_source_lang VARCHAR2(50);
  l_target_lang VARCHAR2(50);
  l_default_alias VARCHAR2(500);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Determine source and target languages from property label
  IF ew_lb_api.g_prop_label LIKE 'Alias:%' THEN
    l_source_lang := SUBSTR(ew_lb_api.g_prop_label, 7);
    
    -- Determine target language based on application
    l_target_lang := CASE ew_lb_api.g_mapped_app_name
      WHEN 'HFM_US'    THEN 'English'
      WHEN 'HFM_FR'    THEN 'French'
      WHEN 'HFM_DE'    THEN 'German'
      WHEN 'HFM_JP'    THEN 'Japanese'
      ELSE 'Default'
    END;
    
    -- Try to get alias in target language
    ew_lb_api.g_out_prop_value := ew_hierarchy.get_member_prop_value(
      p_app_name    => ew_lb_api.g_app_name,
      p_dim_name    => ew_lb_api.g_dim_name,
      p_member_name => ew_lb_api.g_member_name,
      p_prop_label  => 'Alias:' || l_target_lang
    );
    
    -- Fallback to default alias if target language not available
    IF ew_lb_api.g_out_prop_value IS NULL THEN
      l_default_alias := ew_hierarchy.get_member_prop_value(
        p_app_name    => ew_lb_api.g_app_name,
        p_dim_name    => ew_lb_api.g_dim_name,
        p_member_name => ew_lb_api.g_member_name,
        p_prop_label  => 'Alias:Default'
      );
      
      ew_lb_api.g_out_prop_value := NVL(l_default_alias, ew_lb_api.g_member_name);
    END IF;
    
    ew_debug.log('Language mapping: ' || l_source_lang || 
                 ' -> ' || l_target_lang || 
                 ', Value: ' || ew_lb_api.g_out_prop_value,
                 c_script_name);
  ELSE
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := SQLERRM;
END;
```

## Example 5: Conditional Property Mapping

**Scenario:** Map properties only for specific member types or hierarchy levels.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CONDITIONAL_PROP_MAP';
  l_member_level NUMBER;
  l_is_base VARCHAR2(1);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get member characteristics
  l_is_base := ew_hierarchy.is_leaf(
    p_member_id        => ew_lb_api.g_member_id,
    p_app_dimension_id => ew_lb_api.g_app_dimension_id
  );
  
  -- Get member level in hierarchy
  l_member_level := ew_hierarchy.get_member_level(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_name      => ew_lb_api.g_member_name
  );
  
  -- Apply different mapping rules based on member type
  IF ew_lb_api.g_prop_name = 'PLAN_TYPE' THEN
    IF l_is_base = 'Y' THEN
      -- Map for base members only
      ew_lb_api.g_out_prop_value := 
        CASE ew_lb_api.g_prop_value
          WHEN 'Detailed' THEN 'INPUT'
          WHEN 'Summary'  THEN 'CALC'
          ELSE 'NONE'
        END;
    ELSIF l_member_level <= 3 THEN
      -- Upper level members
      ew_lb_api.g_out_prop_value := 'ROLLUP';
    ELSE
      -- Skip mid-level members
      ew_lb_api.g_out_ignore_flag := 'Y';
    END IF;
    
    ew_debug.log('Member: ' || ew_lb_api.g_member_name || 
                 ', Level: ' || l_member_level || 
                 ', Base: ' || l_is_base || 
                 ', Mapped: ' || ew_lb_api.g_out_prop_value,
                 c_script_name);
  ELSE
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := SQLERRM;
END;
```

## Example 6: Property Value Validation and Cleansing

**Scenario:** Validate and clean property values before mapping.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'PROP_CLEANSE_MAP';
  l_clean_value VARCHAR2(500);
  
  FUNCTION clean_value(p_value VARCHAR2) RETURN VARCHAR2 IS
    l_result VARCHAR2(500);
  BEGIN
    -- Remove special characters
    l_result := REGEXP_REPLACE(p_value, '[^A-Za-z0-9 _-]', '');
    
    -- Trim spaces
    l_result := TRIM(l_result);
    
    -- Convert to upper case for codes
    IF ew_lb_api.g_prop_name IN ('ENTITY_CODE', 'ACCOUNT_CODE') THEN
      l_result := UPPER(l_result);
    END IF;
    
    -- Truncate if too long
    IF LENGTH(l_result) > 50 THEN
      l_result := SUBSTR(l_result, 1, 50);
    END IF;
    
    RETURN l_result;
  END clean_value;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Clean the value
  l_clean_value := clean_value(ew_lb_api.g_prop_value);
  
  -- Validate cleaned value
  IF l_clean_value IS NULL AND ew_lb_api.g_prop_name IN ('REQUIRED_FIELD1', 'REQUIRED_FIELD2') THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Required property ' || ew_lb_api.g_prop_label || 
                           ' cannot be empty';
    RETURN;
  END IF;
  
  -- Additional validation for specific properties
  IF ew_lb_api.g_prop_name = 'EMAIL' THEN
    IF NOT REGEXP_LIKE(l_clean_value, '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Invalid email format: ' || l_clean_value;
      RETURN;
    END IF;
  END IF;
  
  -- Set the cleaned value
  ew_lb_api.g_out_prop_value := l_clean_value;
  
  IF l_clean_value != ew_lb_api.g_prop_value THEN
    ew_debug.log('Cleaned value: "' || ew_lb_api.g_prop_value || 
                 '" -> "' || l_clean_value || '"',
                 c_script_name);
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error cleaning property: ' || SQLERRM;
END;
```

## Example 7: Lookup Table Mapping

**Scenario:** Use lookup tables to map property values.

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'LOOKUP_TABLE_MAP';
  l_mapped_value VARCHAR2(500);
  
  CURSOR cur_lookup IS
    SELECT target_value
    FROM   ew_lookup_mappings
    WHERE  source_app = ew_lb_api.g_app_name
    AND    target_app = ew_lb_api.g_mapped_app_name
    AND    property_name = ew_lb_api.g_prop_name
    AND    source_value = ew_lb_api.g_prop_value;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Try to find mapping in lookup table
  OPEN cur_lookup;
  FETCH cur_lookup INTO l_mapped_value;
  CLOSE cur_lookup;
  
  IF l_mapped_value IS NOT NULL THEN
    ew_lb_api.g_out_prop_value := l_mapped_value;
    
    ew_debug.log('Lookup mapping found: ' || ew_lb_api.g_prop_value || 
                 ' -> ' || l_mapped_value,
                 c_script_name);
  ELSE
    -- No mapping found - use default
    IF ew_lb_api.g_prop_name = 'DEPARTMENT' THEN
      ew_lb_api.g_out_prop_value := 'UNMAPPED_DEPT';
      
      ew_debug.log('No lookup found for: ' || ew_lb_api.g_prop_value || 
                   ', using default',
                   c_script_name);
    ELSE
      ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
    END IF;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Lookup error: ' || SQLERRM;
END;
```

## Testing Property Mapping Scripts

### Test Checklist

- [ ] Test with null/empty values
- [ ] Test with maximum length values
- [ ] Test all property types in configuration
- [ ] Test error conditions
- [ ] Verify transformations are correct
- [ ] Check performance with bulk updates
- [ ] Validate debug messages

### Debug Output Example

```sql
-- Add comprehensive debug output
ew_debug.log('=== Property Mapping Debug ===', c_script_name);
ew_debug.log('Member: ' || ew_lb_api.g_member_name, c_script_name);
ew_debug.log('Property: ' || ew_lb_api.g_prop_label, c_script_name);
ew_debug.log('Source App: ' || ew_lb_api.g_app_name, c_script_name);
ew_debug.log('Target App: ' || ew_lb_api.g_mapped_app_name, c_script_name);
ew_debug.log('Input Value: ' || ew_lb_api.g_prop_value, c_script_name);
ew_debug.log('Output Value: ' || ew_lb_api.g_out_prop_value, c_script_name);
ew_debug.log('Ignore Flag: ' || ew_lb_api.g_out_ignore_flag, c_script_name);
ew_debug.log('==============================', c_script_name);
```

## Related Topics

- [Property Mapping Overview](index.md)
- [Configuration Guide](configuration.md)
- [Property Derivations](../property-derivations/)
- [API Reference](../../api/packages/hierarchy.md)