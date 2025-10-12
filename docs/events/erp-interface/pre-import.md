# Pre-Import ERP Scripts

Pre-Import scripts execute before ERP data is imported into EPMware, providing critical data validation, transformation, and preparation capabilities.

## Overview

Pre-Import scripts are your first line of defense for ensuring data quality and compatibility. They execute after ERP data is extracted but before it's processed into EPMware metadata.

Key responsibilities:
- Data format validation
- Business rule enforcement  
- Value transformation
- Record filtering
- Staging table preparation

![Pre-Import Flow](../../assets/images/pre-import-flow.png)
*Figure: Pre-Import script execution in the ERP import process*

## Input Parameters

### Import Context

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_batch_id` | NUMBER | Unique import batch identifier | 98765 |
| `g_import_name` | VARCHAR2 | Import configuration name | 'GL_DAILY_IMPORT' |
| `g_source_system` | VARCHAR2 | Source ERP system | 'ORACLE_EBS' |
| `g_import_type` | VARCHAR2 | Type of import | 'FULL', 'INCREMENTAL' |
| `g_effective_date` | DATE | Effective date for import | '01-JAN-2025' |

### File Information

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_file_name` | VARCHAR2 | Import file name | 'GL_20250101.csv' |
| `g_file_path` | VARCHAR2 | File location | '/imports/gl/' |
| `g_file_size` | NUMBER | File size in bytes | 1048576 |
| `g_record_count` | NUMBER | Number of records | 5000 |

### Target Information  

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_app_id` | NUMBER | Target application ID | 100 |
| `g_app_name` | VARCHAR2 | Target application | 'HFM_PROD' |
| `g_dimension_name` | VARCHAR2 | Target dimension | 'Account' |

## Output Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `g_status` | VARCHAR2 | Yes | 'S' (Success) or 'E' (Error) |
| `g_message` | VARCHAR2 | No | Status or error message |
| `g_continue_import` | VARCHAR2 | No | 'Y' to continue, 'N' to abort |
| `g_records_processed` | NUMBER | No | Records ready for import |

## Common Pre-Import Tasks

### 1. Data Validation

Validate ERP data against business rules:

```sql
/*
 * Script: PRE_IMPORT_VALIDATE_GL
 * Purpose: Validate GL account data before import
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_IMPORT_VALIDATE_GL';
  l_error_count NUMBER := 0;
  l_warning_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE validate_required_fields IS
    l_null_count NUMBER;
  BEGIN
    -- Check for required fields
    SELECT COUNT(*)
      INTO l_null_count
      FROM erp_staging_table
     WHERE batch_id = ew_lb_api.g_batch_id
       AND (account_code IS NULL 
         OR entity_code IS NULL
         OR period_name IS NULL);
    
    IF l_null_count > 0 THEN
      l_error_count := l_error_count + l_null_count;
      log('ERROR: ' || l_null_count || ' records with missing required fields');
      
      -- Mark invalid records
      UPDATE erp_staging_table
         SET import_status = 'ERROR',
             error_message = 'Required fields missing'
       WHERE batch_id = ew_lb_api.g_batch_id
         AND (account_code IS NULL 
           OR entity_code IS NULL
           OR period_name IS NULL);
    END IF;
  END;
  
  PROCEDURE validate_account_format IS
    l_invalid_count NUMBER;
  BEGIN
    -- Check account code format (must be 8 digits)
    SELECT COUNT(*)
      INTO l_invalid_count
      FROM erp_staging_table
     WHERE batch_id = ew_lb_api.g_batch_id
       AND NOT REGEXP_LIKE(account_code, '^\d{8}$');
    
    IF l_invalid_count > 0 THEN
      l_warning_count := l_warning_count + l_invalid_count;
      log('WARNING: ' || l_invalid_count || ' records with invalid account format');
      
      -- Fix format where possible
      UPDATE erp_staging_table
         SET account_code = LPAD(account_code, 8, '0')
       WHERE batch_id = ew_lb_api.g_batch_id
         AND REGEXP_LIKE(account_code, '^\d+$')
         AND LENGTH(account_code) < 8;
    END IF;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  ew_lb_api.g_continue_import := 'Y';
  
  log('Starting pre-import validation for batch ' || ew_lb_api.g_batch_id);
  
  -- Run validations
  validate_required_fields();
  validate_account_format();
  
  -- Check results
  IF l_error_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation failed: ' || l_error_count || ' errors';
    ew_lb_api.g_continue_import := 'N';
  ELSIF l_warning_count > 0 THEN
    ew_lb_api.g_message := 'Validation completed with ' || l_warning_count || 
                            ' warnings';
  ELSE
    ew_lb_api.g_message := 'Validation successful';
  END IF;
  
  -- Report processed records
  SELECT COUNT(*)
    INTO ew_lb_api.g_records_processed
    FROM erp_staging_table
   WHERE batch_id = ew_lb_api.g_batch_id
     AND NVL(import_status, 'VALID') != 'ERROR';
  
  log('Validation complete: ' || ew_lb_api.g_records_processed || 
      ' records ready for import');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
    ew_lb_api.g_continue_import := 'N';
    log('Exception: ' || SQLERRM);
END;
```

### 2. Data Transformation

Transform ERP codes to EPMware format:

```sql
/*
 * Script: PRE_IMPORT_TRANSFORM_ACCOUNTS
 * Purpose: Transform ERP account codes to EPMware structure
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_IMPORT_TRANSFORM_ACCOUNTS';
  l_transform_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  FUNCTION transform_account_code(p_erp_code VARCHAR2) RETURN VARCHAR2 IS
    l_epm_code VARCHAR2(100);
  BEGIN
    -- Apply transformation rules
    l_epm_code := CASE 
      -- Revenue accounts (4xxxxx)
      WHEN SUBSTR(p_erp_code, 1, 1) = '4' THEN
        'REV_' || SUBSTR(p_erp_code, 2, 3) || '_' || SUBSTR(p_erp_code, 5)
      
      -- Expense accounts (5xxxxx, 6xxxxx)  
      WHEN SUBSTR(p_erp_code, 1, 1) IN ('5', '6') THEN
        'EXP_' || SUBSTR(p_erp_code, 2, 3) || '_' || SUBSTR(p_erp_code, 5)
      
      -- Asset accounts (1xxxxx)
      WHEN SUBSTR(p_erp_code, 1, 1) = '1' THEN
        'AST_' || SUBSTR(p_erp_code, 2, 3) || '_' || SUBSTR(p_erp_code, 5)
      
      -- Liability accounts (2xxxxx)
      WHEN SUBSTR(p_erp_code, 1, 1) = '2' THEN
        'LIB_' || SUBSTR(p_erp_code, 2, 3) || '_' || SUBSTR(p_erp_code, 5)
      
      -- Equity accounts (3xxxxx)
      WHEN SUBSTR(p_erp_code, 1, 1) = '3' THEN
        'EQT_' || SUBSTR(p_erp_code, 2, 3) || '_' || SUBSTR(p_erp_code, 5)
      
      ELSE
        'UNK_' || p_erp_code
    END;
    
    RETURN l_epm_code;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting account transformation for batch ' || ew_lb_api.g_batch_id);
  
  -- Transform account codes
  FOR rec IN (
    SELECT rowid rid, account_code
      FROM erp_staging_table
     WHERE batch_id = ew_lb_api.g_batch_id
       AND account_code IS NOT NULL
  ) LOOP
    UPDATE erp_staging_table
       SET epm_account = transform_account_code(rec.account_code),
           transform_date = SYSDATE
     WHERE rowid = rec.rid;
    
    l_transform_count := l_transform_count + 1;
  END LOOP;
  
  -- Transform entity codes using mapping table
  UPDATE erp_staging_table e
     SET e.epm_entity = (
       SELECT m.epm_entity
         FROM entity_mapping m
        WHERE m.erp_entity = e.entity_code
          AND m.active_flag = 'Y'
     )
   WHERE batch_id = ew_lb_api.g_batch_id;
  
  -- Handle unmapped entities
  UPDATE erp_staging_table
     SET epm_entity = 'UNMAPPED_ENTITIES',
         import_warning = 'Entity not found in mapping table'
   WHERE batch_id = ew_lb_api.g_batch_id
     AND epm_entity IS NULL
     AND entity_code IS NOT NULL;
  
  COMMIT;
  
  log('Transformed ' || l_transform_count || ' account codes');
  ew_lb_api.g_message := 'Transformation completed: ' || 
                          l_transform_count || ' records';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Transformation error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

### 3. Duplicate Detection

Identify and handle duplicate records:

```sql
/*
 * Script: PRE_IMPORT_CHECK_DUPLICATES
 * Purpose: Detect and handle duplicate records
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_IMPORT_CHECK_DUPLICATES';
  l_dup_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Checking for duplicates in batch ' || ew_lb_api.g_batch_id);
  
  -- Mark duplicate records within batch
  UPDATE erp_staging_table e1
     SET import_status = 'DUPLICATE',
         error_message = 'Duplicate record in batch'
   WHERE batch_id = ew_lb_api.g_batch_id
     AND rowid > (
       SELECT MIN(rowid)
         FROM erp_staging_table e2
        WHERE e2.batch_id = e1.batch_id
          AND e2.account_code = e1.account_code
          AND e2.entity_code = e1.entity_code
          AND e2.period_name = e1.period_name
     );
  
  l_dup_count := SQL%ROWCOUNT;
  
  IF l_dup_count > 0 THEN
    log('Found ' || l_dup_count || ' duplicate records');
    
    -- Keep only the latest record (by amount or date)
    UPDATE erp_staging_table e1
       SET import_status = 'VALID'
     WHERE batch_id = ew_lb_api.g_batch_id
       AND import_status = 'DUPLICATE'
       AND transaction_date = (
         SELECT MAX(transaction_date)
           FROM erp_staging_table e2
          WHERE e2.batch_id = e1.batch_id
            AND e2.account_code = e1.account_code
            AND e2.entity_code = e1.entity_code
            AND e2.period_name = e1.period_name
       );
  END IF;
  
  -- Check for duplicates with existing data
  DECLARE
    l_existing_count NUMBER;
  BEGIN
    SELECT COUNT(*)
      INTO l_existing_count
      FROM erp_staging_table e
     WHERE batch_id = ew_lb_api.g_batch_id
       AND EXISTS (
         SELECT 1
           FROM imported_data i
          WHERE i.account_code = e.account_code
            AND i.entity_code = e.entity_code
            AND i.period_name = e.period_name
            AND i.import_date >= TRUNC(SYSDATE)
       );
    
    IF l_existing_count > 0 THEN
      UPDATE erp_staging_table e
         SET import_status = 'SKIP',
             error_message = 'Already imported today'
       WHERE batch_id = ew_lb_api.g_batch_id
         AND EXISTS (
           SELECT 1
             FROM imported_data i
            WHERE i.account_code = e.account_code
              AND i.entity_code = e.entity_code
              AND i.period_name = e.period_name
              AND i.import_date >= TRUNC(SYSDATE)
         );
      
      log('Skipping ' || l_existing_count || ' previously imported records');
    END IF;
  END;
  
  COMMIT;
  
  ew_lb_api.g_message := 'Duplicate check complete';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Duplicate check error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

### 4. Business Rule Application

Apply complex business rules:

```sql
/*
 * Script: PRE_IMPORT_APPLY_BUSINESS_RULES
 * Purpose: Apply company-specific business rules
 */
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_IMPORT_APPLY_BUSINESS_RULES';
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE apply_consolidation_rules IS
  BEGIN
    -- Set consolidation method based on ownership
    UPDATE erp_staging_table
       SET consolidation_method = 
         CASE 
           WHEN ownership_pct >= 80 THEN 'FULL'
           WHEN ownership_pct >= 50 THEN 'PROPORTIONAL'
           WHEN ownership_pct >= 20 THEN 'EQUITY'
           ELSE 'NONE'
         END
     WHERE batch_id = ew_lb_api.g_batch_id
       AND entity_type = 'SUBSIDIARY';
  END;
  
  PROCEDURE apply_intercompany_rules IS
  BEGIN
    -- Flag intercompany transactions
    UPDATE erp_staging_table e1
       SET intercompany_flag = 'Y',
           elimination_flag = 'Y'
     WHERE batch_id = ew_lb_api.g_batch_id
       AND EXISTS (
         SELECT 1
           FROM erp_staging_table e2
          WHERE e2.batch_id = e1.batch_id
            AND e2.entity_code != e1.entity_code
            AND e2.interco_account = e1.account_code
            AND e2.amount = -1 * e1.amount
       );
  END;
  
  PROCEDURE apply_currency_rules IS
  BEGIN
    -- Default currency based on entity
    UPDATE erp_staging_table e
       SET currency_code = NVL(currency_code, 
         (SELECT default_currency
            FROM entity_master m
           WHERE m.entity_code = e.entity_code))
     WHERE batch_id = ew_lb_api.g_batch_id;
    
    -- Calculate USD equivalent
    UPDATE erp_staging_table e
       SET usd_amount = amount * (
         SELECT exchange_rate
           FROM currency_rates r
          WHERE r.from_currency = e.currency_code
            AND r.to_currency = 'USD'
            AND r.rate_date = e.period_end_date
       )
     WHERE batch_id = ew_lb_api.g_batch_id
       AND currency_code != 'USD';
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Applying business rules for batch ' || ew_lb_api.g_batch_id);
  
  -- Apply various business rules
  apply_consolidation_rules();
  apply_intercompany_rules();
  apply_currency_rules();
  
  COMMIT;
  
  log('Business rules applied successfully');
  ew_lb_api.g_message := 'Business rules applied';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Business rule error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

## Error Handling

### Quarantine Bad Records

```sql
-- Move invalid records to error table
INSERT INTO erp_import_errors (
  batch_id,
  record_id,
  error_type,
  error_message,
  original_data,
  error_date
)
SELECT batch_id,
       record_id,
       import_status,
       error_message,
       original_record,
       SYSDATE
  FROM erp_staging_table
 WHERE batch_id = ew_lb_api.g_batch_id
   AND import_status IN ('ERROR', 'DUPLICATE');

-- Remove from staging
DELETE FROM erp_staging_table
 WHERE batch_id = ew_lb_api.g_batch_id
   AND import_status IN ('ERROR', 'DUPLICATE');
```

## Best Practices

1. **Validate Early and Comprehensively**
   - Check all required fields
   - Verify data types and formats
   - Validate against business rules

2. **Transform Consistently**
   - Use standard transformation functions
   - Maintain transformation mappings
   - Log all transformations

3. **Handle Errors Gracefully**
   - Don't abort on first error
   - Collect all errors for reporting
   - Provide clear error messages

4. **Maintain Audit Trail**
   - Keep original values
   - Log transformation details
   - Record validation results

5. **Optimize Performance**
   - Use bulk operations
   - Minimize row-by-row processing
   - Create appropriate indexes

## Next Steps

- [Post-Import Scripts](post-import.md)
- [Export Tasks](../export/)
- [API Reference](../../api/)