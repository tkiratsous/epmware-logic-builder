# Pre-Export Generation Scripts

Pre-Export scripts execute before the export file is generated, allowing you to filter, transform, and prepare data for export.

## Overview

Pre-Export scripts provide critical data preparation capabilities:
- Filter records to include/exclude
- Transform values for external systems
- Add calculated fields
- Apply business rules
- Prepare staging data

![Pre-Export Flow](../../assets/images/pre-export-flow.png)
*Figure: Pre-Export script execution flow*

## Input Parameters

### Export Context

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_export_id` | NUMBER | Unique export identifier | 54321 |
| `g_export_name` | VARCHAR2 | Export configuration name | 'DAILY_METADATA_EXPORT' |
| `g_export_type` | VARCHAR2 | Type of export | 'METADATA', 'DATA', 'BOTH' |
| `g_export_format` | VARCHAR2 | Output format | 'CSV', 'XML', 'JSON' |
| `g_user_name` | VARCHAR2 | User initiating export | 'ADMIN' |

### Target Information

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_app_id` | NUMBER | Source application ID | 100 |
| `g_app_name` | VARCHAR2 | Source application | 'HFM_PROD' |
| `g_dimension_name` | VARCHAR2 | Dimension being exported | 'Account' |
| `g_export_path` | VARCHAR2 | Export file location | '/exports/daily/' |

### Selection Criteria

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_selection_criteria` | VARCHAR2 | Export filter criteria | 'ACTIVE_ONLY' |
| `g_from_date` | DATE | Start date for data | '01-JAN-2025' |
| `g_to_date` | DATE | End date for data | '31-JAN-2025' |
| `g_member_list` | VARCHAR2 | Specific members to export | 'Account1,Account2' |

## Output Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `g_status` | VARCHAR2 | Yes | 'S' (Success) or 'E' (Error) |
| `g_message` | VARCHAR2 | No | Status or error message |
| `g_continue_export` | VARCHAR2 | No | 'Y' to continue, 'N' to abort |
| `g_record_count` | NUMBER | No | Number of records to export |

## Common Pre-Export Tasks

### 1. Data Filtering

Filter data based on business rules:

```sql
/*
 * Script: PRE_EXPORT_FILTER_ACTIVE
 * Purpose: Export only active members and current period data
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_FILTER_ACTIVE';
  l_excluded_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  ew_lb_api.g_continue_export := 'Y';
  
  log('Starting pre-export filtering for export ' || ew_lb_api.g_export_id);
  
  -- Exclude inactive members
  UPDATE export_staging
     SET include_flag = 'N',
         exclusion_reason = 'Inactive member'
   WHERE export_id = ew_lb_api.g_export_id
     AND member_status = 'INACTIVE';
  
  l_excluded_count := SQL%ROWCOUNT;
  log('Excluded ' || l_excluded_count || ' inactive members');
  
  -- Exclude old data (keep only current year)
  UPDATE export_staging
     SET include_flag = 'N',
         exclusion_reason = 'Historical data'
   WHERE export_id = ew_lb_api.g_export_id
     AND data_year < TO_CHAR(SYSDATE, 'YYYY');
  
  l_excluded_count := l_excluded_count + SQL%ROWCOUNT;
  
  -- Exclude members with no data
  UPDATE export_staging e
     SET include_flag = 'N',
         exclusion_reason = 'No data'
   WHERE export_id = ew_lb_api.g_export_id
     AND NOT EXISTS (
       SELECT 1
         FROM member_data d
        WHERE d.member_id = e.member_id
          AND d.has_data = 'Y'
     );
  
  l_excluded_count := l_excluded_count + SQL%ROWCOUNT;
  
  -- Count remaining records
  SELECT COUNT(*)
    INTO ew_lb_api.g_record_count
    FROM export_staging
   WHERE export_id = ew_lb_api.g_export_id
     AND NVL(include_flag, 'Y') = 'Y';
  
  IF ew_lb_api.g_record_count = 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'No records to export after filtering';
    ew_lb_api.g_continue_export := 'N';
  ELSE
    log('Ready to export ' || ew_lb_api.g_record_count || ' records');
    ew_lb_api.g_message := 'Filtered export: ' || ew_lb_api.g_record_count || 
                           ' records (excluded ' || l_excluded_count || ')';
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Filter error: ' || SQLERRM;
    ew_lb_api.g_continue_export := 'N';
    log('Exception: ' || SQLERRM);
END;
```

### 2. Value Transformation

Transform values for target system compatibility:

```sql
/*
 * Script: PRE_EXPORT_TRANSFORM_CODES
 * Purpose: Transform member codes for external system
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_TRANSFORM_CODES';
  l_transform_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  FUNCTION transform_account_code(p_internal_code VARCHAR2) RETURN VARCHAR2 IS
    l_external_code VARCHAR2(50);
  BEGIN
    -- Apply transformation rules for external system
    l_external_code := CASE 
      WHEN p_internal_code LIKE 'REV_%' THEN 
        '4' || LPAD(SUBSTR(p_internal_code, 5), 6, '0')
      WHEN p_internal_code LIKE 'EXP_%' THEN 
        '5' || LPAD(SUBSTR(p_internal_code, 5), 6, '0')
      WHEN p_internal_code LIKE 'AST_%' THEN 
        '1' || LPAD(SUBSTR(p_internal_code, 5), 6, '0')
      WHEN p_internal_code LIKE 'LIB_%' THEN 
        '2' || LPAD(SUBSTR(p_internal_code, 5), 6, '0')
      WHEN p_internal_code LIKE 'EQT_%' THEN 
        '3' || LPAD(SUBSTR(p_internal_code, 5), 6, '0')
      ELSE 
        '9' || LPAD(p_internal_code, 6, '0')
    END;
    
    RETURN l_external_code;
  END;
  
  FUNCTION transform_entity_code(p_internal_code VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Map to external entity codes
    RETURN CASE p_internal_code
      WHEN 'US_CORP' THEN '1000'
      WHEN 'UK_CORP' THEN '2000'
      WHEN 'EU_CORP' THEN '3000'
      WHEN 'AP_CORP' THEN '4000'
      ELSE '9999'
    END;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting code transformation for export ' || ew_lb_api.g_export_id);
  
  -- Transform account codes
  FOR rec IN (
    SELECT rowid rid, member_code, dimension_type
      FROM export_staging
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y'
  ) LOOP
    IF rec.dimension_type = 'ACCOUNT' THEN
      UPDATE export_staging
         SET external_code = transform_account_code(rec.member_code),
             transform_date = SYSDATE
       WHERE rowid = rec.rid;
    ELSIF rec.dimension_type = 'ENTITY' THEN
      UPDATE export_staging
         SET external_code = transform_entity_code(rec.member_code),
             transform_date = SYSDATE
       WHERE rowid = rec.rid;
    END IF;
    
    l_transform_count := l_transform_count + 1;
  END LOOP;
  
  -- Transform date formats
  UPDATE export_staging
     SET external_date = TO_CHAR(effective_date, 'YYYYMMDD'),
         external_period = TO_CHAR(period_date, 'YYYYMM')
   WHERE export_id = ew_lb_api.g_export_id
     AND NVL(include_flag, 'Y') = 'Y';
  
  -- Transform boolean flags to Y/N
  UPDATE export_staging
     SET external_active = CASE active_flag 
                            WHEN 1 THEN 'Y' 
                            WHEN 0 THEN 'N' 
                            ELSE 'N' 
                          END
   WHERE export_id = ew_lb_api.g_export_id
     AND NVL(include_flag, 'Y') = 'Y';
  
  COMMIT;
  
  log('Transformed ' || l_transform_count || ' codes');
  ew_lb_api.g_message := 'Transformation complete: ' || l_transform_count || ' records';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Transformation error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

### 3. Add Calculated Fields

Add derived values and calculations:

```sql
/*
 * Script: PRE_EXPORT_ADD_CALCULATIONS
 * Purpose: Add calculated fields to export data
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_ADD_CALCULATIONS';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE calculate_hierarchy_levels IS
  BEGIN
    -- Add hierarchy level and generation
    UPDATE export_staging e
       SET hierarchy_level = (
         SELECT level_number
           FROM hierarchy_view h
          WHERE h.member_id = e.member_id
       ),
       generation = (
         SELECT generation_number
           FROM hierarchy_view h
          WHERE h.member_id = e.member_id
       ),
       full_path = (
         SELECT hierarchy_path
           FROM hierarchy_view h
          WHERE h.member_id = e.member_id
       )
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y';
  END;
  
  PROCEDURE calculate_aggregations IS
  BEGIN
    -- Calculate parent aggregations
    UPDATE export_staging e
       SET child_count = (
         SELECT COUNT(*)
           FROM hierarchy h
          WHERE h.parent_id = e.member_id
       ),
       descendant_count = (
         SELECT COUNT(*)
           FROM hierarchy h
          START WITH h.parent_id = e.member_id
          CONNECT BY PRIOR h.member_id = h.parent_id
       )
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y'
       AND member_type = 'PARENT';
    
    -- Calculate data aggregations
    UPDATE export_staging e
       SET total_amount = (
         SELECT SUM(amount)
           FROM member_data d
          WHERE d.member_id IN (
            SELECT h.member_id
              FROM hierarchy h
             START WITH h.member_id = e.member_id
             CONNECT BY PRIOR h.member_id = h.parent_id
          )
       ),
       ytd_amount = (
         SELECT SUM(amount)
           FROM member_data d
          WHERE d.member_id = e.member_id
            AND d.period_year = TO_CHAR(SYSDATE, 'YYYY')
            AND d.period_num <= TO_CHAR(SYSDATE, 'MM')
       )
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y';
  END;
  
  PROCEDURE calculate_variances IS
  BEGIN
    -- Calculate variance fields
    UPDATE export_staging
       SET variance_amount = actual_amount - budget_amount,
           variance_percent = CASE 
             WHEN budget_amount = 0 THEN NULL
             ELSE ROUND((actual_amount - budget_amount) / budget_amount * 100, 2)
           END
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y'
       AND actual_amount IS NOT NULL
       AND budget_amount IS NOT NULL;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Adding calculated fields for export ' || ew_lb_api.g_export_id);
  
  -- Add various calculations
  calculate_hierarchy_levels();
  calculate_aggregations();
  calculate_variances();
  
  COMMIT;
  
  log('Calculated fields added successfully');
  ew_lb_api.g_message := 'Calculations complete';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Calculation error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

### 4. Security and Compliance

Apply data security rules:

```sql
/*
 * Script: PRE_EXPORT_APPLY_SECURITY
 * Purpose: Apply security rules and data masking
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_APPLY_SECURITY';
  l_user_security_level VARCHAR2(20);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  FUNCTION get_user_security_level RETURN VARCHAR2 IS
    l_level VARCHAR2(20);
  BEGIN
    SELECT security_level
      INTO l_level
      FROM user_security
     WHERE user_name = ew_lb_api.g_user_name;
    RETURN l_level;
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      RETURN 'BASIC';
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Applying security rules for export ' || ew_lb_api.g_export_id);
  
  -- Get user security level
  l_user_security_level := get_user_security_level();
  
  -- Exclude confidential data for basic users
  IF l_user_security_level = 'BASIC' THEN
    UPDATE export_staging
       SET include_flag = 'N',
           exclusion_reason = 'Insufficient security clearance'
     WHERE export_id = ew_lb_api.g_export_id
       AND confidential_flag = 'Y';
    
    log('Excluded confidential data for basic user');
  END IF;
  
  -- Mask sensitive fields
  UPDATE export_staging
     SET employee_id = 'EMP' || LPAD(ROWNUM, 6, '0'),
         ssn = CASE 
           WHEN l_user_security_level = 'FULL' THEN ssn
           ELSE 'XXX-XX-' || SUBSTR(ssn, -4)
         END,
         salary = CASE
           WHEN l_user_security_level IN ('FULL', 'MANAGER') THEN salary
           ELSE NULL
         END,
         email = CASE
           WHEN l_user_security_level = 'FULL' THEN email
           ELSE SUBSTR(email, 1, 2) || '****@' || 
                SUBSTR(email, INSTR(email, '@') + 1)
         END
   WHERE export_id = ew_lb_api.g_export_id
     AND NVL(include_flag, 'Y') = 'Y';
  
  -- Apply regional restrictions
  IF ew_lb_api.g_user_region IS NOT NULL THEN
    UPDATE export_staging
       SET include_flag = 'N',
           exclusion_reason = 'Regional restriction'
     WHERE export_id = ew_lb_api.g_export_id
       AND region != ew_lb_api.g_user_region
       AND l_user_security_level != 'GLOBAL';
  END IF;
  
  -- Log security actions
  INSERT INTO export_security_log (
    export_id,
    user_name,
    security_level,
    masked_fields,
    excluded_count,
    log_date
  ) VALUES (
    ew_lb_api.g_export_id,
    ew_lb_api.g_user_name,
    l_user_security_level,
    'SSN,SALARY,EMAIL',
    (SELECT COUNT(*) 
       FROM export_staging 
      WHERE export_id = ew_lb_api.g_export_id 
        AND include_flag = 'N'),
    SYSDATE
  );
  
  COMMIT;
  
  log('Security rules applied');
  ew_lb_api.g_message := 'Security filtering complete';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Security error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

### 5. Format Preparation

Prepare data for specific export formats:

```sql
/*
 * Script: PRE_EXPORT_FORMAT_PREP
 * Purpose: Prepare data for specific export format
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_FORMAT_PREP';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE prepare_csv_format IS
  BEGIN
    -- Escape special characters for CSV
    UPDATE export_staging
       SET member_description = REPLACE(REPLACE(member_description, '"', '""'), 
                                       CHR(10), ' '),
           notes = REPLACE(REPLACE(notes, '"', '""'), CHR(10), ' ')
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y';
    
    -- Ensure numeric formats
    UPDATE export_staging
       SET amount_text = TO_CHAR(amount, 'FM999999999990.00'),
           percent_text = TO_CHAR(percent_value, 'FM990.00')
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y';
  END;
  
  PROCEDURE prepare_xml_format IS
  BEGIN
    -- Escape XML special characters
    UPDATE export_staging
       SET xml_safe_desc = DBMS_XMLGEN.CONVERT(member_description),
           xml_safe_notes = DBMS_XMLGEN.CONVERT(notes)
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y';
    
    -- Convert dates to XML format
    UPDATE export_staging
       SET xml_date = TO_CHAR(effective_date, 'YYYY-MM-DD"T"HH24:MI:SS')
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y';
  END;
  
  PROCEDURE prepare_json_format IS
  BEGIN
    -- Prepare JSON-safe strings
    UPDATE export_staging
       SET json_safe_desc = REPLACE(REPLACE(REPLACE(member_description, 
                                                   '\', '\\'),
                                           '"', '\"'),
                                   CHR(10), '\n'),
           json_safe_notes = REPLACE(REPLACE(REPLACE(notes, 
                                                   '\', '\\'),
                                           '"', '\"'),
                                   CHR(10), '\n')
     WHERE export_id = ew_lb_api.g_export_id
       AND NVL(include_flag, 'Y') = 'Y';
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Preparing format for ' || ew_lb_api.g_export_format);
  
  -- Apply format-specific preparation
  CASE ew_lb_api.g_export_format
    WHEN 'CSV' THEN
      prepare_csv_format();
    WHEN 'XML' THEN
      prepare_xml_format();
    WHEN 'JSON' THEN
      prepare_json_format();
    ELSE
      log('No special formatting needed for ' || ew_lb_api.g_export_format);
  END CASE;
  
  COMMIT;
  
  log('Format preparation complete');
  ew_lb_api.g_message := 'Data prepared for ' || ew_lb_api.g_export_format || ' format';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Format preparation error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

## Performance Optimization

### Index Creation for Large Exports

```sql
-- Create temporary indexes for better performance
BEGIN
  -- Create index on export staging
  EXECUTE IMMEDIATE 
    'CREATE INDEX idx_exp_stg_' || ew_lb_api.g_export_id || 
    ' ON export_staging(export_id, include_flag)';
  
  -- Gather statistics
  DBMS_STATS.gather_table_stats(
    ownname => USER,
    tabname => 'EXPORT_STAGING'
  );
END;
```

### Parallel Processing

```sql
-- Enable parallel processing for large datasets
BEGIN
  EXECUTE IMMEDIATE 'ALTER SESSION ENABLE PARALLEL DML';
  
  -- Process in parallel
  UPDATE /*+ PARALLEL(4) */ export_staging
     SET processed_flag = 'Y'
   WHERE export_id = ew_lb_api.g_export_id;
  
  EXECUTE IMMEDIATE 'ALTER SESSION DISABLE PARALLEL DML';
END;
```

## Error Handling

### Validation Checks

```sql
-- Validate export readiness
DECLARE
  l_error_count NUMBER;
BEGIN
  -- Check for required fields
  SELECT COUNT(*)
    INTO l_error_count
    FROM export_staging
   WHERE export_id = ew_lb_api.g_export_id
     AND NVL(include_flag, 'Y') = 'Y'
     AND (member_code IS NULL OR member_name IS NULL);
  
  IF l_error_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Found ' || l_error_count || 
                           ' records with missing required fields';
    ew_lb_api.g_continue_export := 'N';
  END IF;
END;
```

## Best Practices

1. **Filter Early and Efficiently**
   - Apply exclusions before transformations
   - Use indexes for filtering operations

2. **Transform Consistently**
   - Use standard transformation functions
   - Maintain transformation mappings

3. **Validate Thoroughly**
   - Check data completeness
   - Verify format requirements

4. **Consider Performance**
   - Process in batches for large exports
   - Use parallel processing when appropriate

5. **Maintain Audit Trail**
   - Log all filtering decisions
   - Record transformation rules applied

## Next Steps

- [Post-Export Scripts](post-export.md)
- [Export Overview](index.md)
- [API Reference](../../api/)