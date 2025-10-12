# ERP Interface Scripts

ERP Interface scripts enable custom logic during import and export operations with Enterprise Resource Planning systems, providing data transformation, validation, and enrichment capabilities.

## Overview

ERP Interface scripts are triggered during:
- **Pre-Import**: Before ERP data is processed into EPMware
- **Post-Import**: After ERP data has been imported

These scripts enable:
- Data format transformation
- Business rule validation
- Data enrichment and derivation
- Error handling and recovery
- Integration logging and monitoring

![ERP Interface Flow](../../assets/images/erp-interface-flow.png)
*Figure: ERP Interface script execution flow*

## Configuration

### Setting Up ERP Interface Scripts

1. Navigate to **ERP Import → Builder**
2. Select your import configuration
3. Configure scripts:
   - **Pre Execution Script**: Runs before import
   - **Post Execution Script**: Runs after import

![ERP Interface Configuration](../../assets/images/erp-interface-config.png)
*Figure: ERP Import Builder with script configuration*

## Script Types

### Pre-Import Scripts
Execute before data import to:
- Validate source data quality
- Transform data formats
- Apply business rules
- Filter unwanted records
- Prepare staging tables

### Post-Import Scripts
Execute after data import to:
- Validate imported data
- Generate derived records
- Update related data
- Send notifications
- Clean up temporary data

## Common Integration Patterns

### 1. Data Transformation

Transform ERP codes to EPMware format:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'ERP_TRANSFORM_ACCOUNTS';
BEGIN
  -- Transform GL account codes to EPMware structure
  UPDATE erp_staging_table
     SET account_code = 
       CASE 
         WHEN account_code LIKE '4%' THEN 'REV_' || account_code
         WHEN account_code LIKE '5%' THEN 'EXP_' || account_code
         WHEN account_code LIKE '1%' THEN 'AST_' || account_code
         WHEN account_code LIKE '2%' THEN 'LIB_' || account_code
         WHEN account_code LIKE '3%' THEN 'EQT_' || account_code
         ELSE account_code
       END
   WHERE batch_id = ew_lb_api.g_batch_id;
   
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_debug.log('Transformed ' || SQL%ROWCOUNT || ' account codes');
END;
```

### 2. Data Validation

Validate ERP data against business rules:

```sql
DECLARE
  l_error_count NUMBER := 0;
BEGIN
  -- Check for invalid cost centers
  FOR rec IN (
    SELECT DISTINCT cost_center
      FROM erp_staging_table
     WHERE batch_id = ew_lb_api.g_batch_id
       AND cost_center NOT IN (
         SELECT member_name
           FROM ew_members_v
          WHERE dimension_name = 'CostCenter'
       )
  ) LOOP
    l_error_count := l_error_count + 1;
    ew_debug.log('Invalid cost center: ' || rec.cost_center);
  END LOOP;
  
  IF l_error_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Found ' || l_error_count || ' invalid cost centers';
  ELSE
    ew_lb_api.g_status := ew_lb_api.g_success;
  END IF;
END;
```

### 3. Data Enrichment

Add calculated or derived fields:

```sql
BEGIN
  -- Add derived fields based on ERP data
  UPDATE erp_staging_table e
     SET region = (
       SELECT region_code
         FROM cost_center_mapping m
        WHERE m.cost_center = e.cost_center
     ),
     department = SUBSTR(cost_center, 1, 3),
     fiscal_year = TO_CHAR(transaction_date, 'YYYY'),
     fiscal_period = TO_CHAR(transaction_date, 'MM')
   WHERE batch_id = ew_lb_api.g_batch_id;
   
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_debug.log('Enriched ' || SQL%ROWCOUNT || ' records');
END;
```

## ERP System Support

### Supported ERP Systems

EPMware Logic Builder supports integration with:

| ERP System | Import Method | Common Transformations |
|------------|---------------|------------------------|
| **Oracle EBS** | Database Link | GL codes, Cost centers |
| **SAP** | File/Web Service | Company codes, Profit centers |
| **PeopleSoft** | Database/File | Business units, Accounts |
| **JD Edwards** | Database/File | Company/Account format |
| **NetSuite** | Web Service/CSV | Department, Location, Class |
| **Workday** | Web Service | Cost centers, Organizations |

### ERP-Specific Considerations

#### Oracle EBS Integration

```sql
-- Example: Transform Oracle EBS segments
DECLARE
  l_segments VARCHAR2(200);
BEGIN
  -- Parse concatenated segments
  FOR rec IN (
    SELECT code_combination,
           REGEXP_SUBSTR(code_combination, '[^.]+', 1, 1) company,
           REGEXP_SUBSTR(code_combination, '[^.]+', 1, 2) account,
           REGEXP_SUBSTR(code_combination, '[^.]+', 1, 3) cost_center,
           REGEXP_SUBSTR(code_combination, '[^.]+', 1, 4) product
      FROM erp_staging_table
     WHERE batch_id = ew_lb_api.g_batch_id
  ) LOOP
    -- Create hierarchy path
    INSERT INTO import_mapping (
      batch_id,
      entity_path,
      account_code,
      cost_center,
      product_line
    ) VALUES (
      ew_lb_api.g_batch_id,
      'Entity.' || rec.company,
      rec.account,
      rec.cost_center,
      rec.product
    );
  END LOOP;
END;
```

#### SAP Integration

```sql
-- Example: Handle SAP company codes
BEGIN
  -- Map SAP company codes to entities
  UPDATE erp_staging_table
     SET entity_code = 
       CASE company_code
         WHEN '1000' THEN 'US_CORP'
         WHEN '2000' THEN 'EU_CORP'
         WHEN '3000' THEN 'AP_CORP'
         ELSE 'UNMAPPED'
       END
   WHERE batch_id = ew_lb_api.g_batch_id;
END;
```

## Error Handling Strategies

### Data Quality Issues

```sql
DECLARE
  l_bad_records NUMBER;
BEGIN
  -- Move bad records to error table
  INSERT INTO erp_import_errors
  SELECT batch_id,
         record_id,
         'VALIDATION_ERROR' error_type,
         validation_message
    FROM erp_staging_table
   WHERE batch_id = ew_lb_api.g_batch_id
     AND validation_status = 'FAILED';
  
  l_bad_records := SQL%ROWCOUNT;
  
  -- Delete bad records from staging
  DELETE FROM erp_staging_table
   WHERE batch_id = ew_lb_api.g_batch_id
     AND validation_status = 'FAILED';
  
  IF l_bad_records > 0 THEN
    ew_debug.log('Moved ' || l_bad_records || ' bad records to error table');
  END IF;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Recovery Mechanisms

```sql
-- Implement retry logic for transient errors
DECLARE
  l_retry_count NUMBER := 0;
  l_max_retries NUMBER := 3;
  l_success BOOLEAN := FALSE;
BEGIN
  WHILE l_retry_count < l_max_retries AND NOT l_success LOOP
    BEGIN
      -- Attempt ERP connection
      connect_to_erp_system();
      fetch_erp_data();
      l_success := TRUE;
    EXCEPTION
      WHEN connection_error THEN
        l_retry_count := l_retry_count + 1;
        IF l_retry_count < l_max_retries THEN
          DBMS_LOCK.sleep(30); -- Wait 30 seconds
          ew_debug.log('Retry attempt ' || l_retry_count);
        ELSE
          RAISE;
        END IF;
    END;
  END LOOP;
END;
```

## Performance Optimization

### Batch Processing

```sql
-- Process large datasets in chunks
DECLARE
  CURSOR c_erp_data IS
    SELECT *
      FROM erp_staging_table
     WHERE batch_id = ew_lb_api.g_batch_id
     ORDER BY record_id;
  
  TYPE t_erp_data IS TABLE OF c_erp_data%ROWTYPE;
  l_data t_erp_data;
  l_batch_size CONSTANT NUMBER := 1000;
BEGIN
  OPEN c_erp_data;
  LOOP
    FETCH c_erp_data BULK COLLECT INTO l_data LIMIT l_batch_size;
    EXIT WHEN l_data.COUNT = 0;
    
    -- Process batch
    FORALL i IN 1..l_data.COUNT
      INSERT INTO processed_data
      VALUES l_data(i);
    
    COMMIT;
    ew_debug.log('Processed batch of ' || l_data.COUNT || ' records');
  END LOOP;
  CLOSE c_erp_data;
END;
```

### Parallel Processing

```sql
-- Enable parallel processing for large imports
BEGIN
  -- Set parallel degree
  EXECUTE IMMEDIATE 'ALTER SESSION ENABLE PARALLEL DML';
  
  -- Parallel insert
  INSERT /*+ PARALLEL(target, 4) */ INTO target_table
  SELECT /*+ PARALLEL(source, 4) */ *
    FROM erp_staging_table source
   WHERE batch_id = ew_lb_api.g_batch_id;
  
  COMMIT;
  
  -- Reset parallel
  EXECUTE IMMEDIATE 'ALTER SESSION DISABLE PARALLEL DML';
END;
```

## Monitoring and Logging

### Import Statistics

```sql
-- Track import performance
DECLARE
  l_start_time TIMESTAMP := SYSTIMESTAMP;
  l_records_processed NUMBER;
BEGIN
  -- Process import
  process_erp_import();
  
  -- Calculate statistics
  l_records_processed := SQL%ROWCOUNT;
  
  -- Log statistics
  INSERT INTO erp_import_stats (
    batch_id,
    import_date,
    source_system,
    records_count,
    processing_time,
    status
  ) VALUES (
    ew_lb_api.g_batch_id,
    SYSDATE,
    ew_lb_api.g_source_system,
    l_records_processed,
    EXTRACT(SECOND FROM (SYSTIMESTAMP - l_start_time)),
    ew_lb_api.g_status
  );
  
  COMMIT;
END;
```

## Best Practices

1. **Validate Early**
   - Check data quality in pre-import
   - Reject bad records before processing

2. **Use Staging Tables**
   - Don't modify source data directly
   - Maintain audit trail

3. **Implement Error Recovery**
   - Handle partial failures gracefully
   - Provide clear error messages

4. **Monitor Performance**
   - Track import times
   - Identify bottlenecks

5. **Document Transformations**
   - Maintain mapping documentation
   - Log all transformations applied

## Next Steps

- [Pre-Import Scripts](pre-import.md)
- [Post-Import Scripts](post-import.md)
- [Export Tasks](../export/)