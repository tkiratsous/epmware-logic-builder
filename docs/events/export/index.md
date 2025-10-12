# Export Task Scripts

Export Task scripts enable custom logic during metadata and data export operations, providing transformation, filtering, and post-processing capabilities.

## Overview

Export scripts are triggered during the export process:
- **Pre-Export**: Before export file generation
- **Post-Export**: After export file creation

These scripts enable:
- Data filtering and selection
- Format transformation
- File enrichment
- Distribution automation
- Archive management

![Export Tasks Flow](../../assets/images/export-tasks-flow.png)
*Figure: Export script execution flow*

## Configuration

### Setting Up Export Scripts

1. Navigate to **Administration → Export**
2. Select your export configuration
3. Configure scripts:
   - **Pre Export Logic Script**: Executes before file generation
   - **Post Export Logic Script**: Executes after file creation

![Export Configuration](../../assets/images/export-config.png)
*Figure: Export configuration with Logic Scripts*

## Script Types

### Pre-Export Scripts
Execute before export to:
- Filter data to export
- Transform values
- Add calculated fields
- Prepare staging data
- Validate export criteria

### Post-Export Scripts
Execute after export to:
- Distribute files
- Archive exports
- Send notifications
- Trigger downstream processes
- Clean up temporary data

## Common Export Patterns

### 1. Filtered Export

Export only specific members based on criteria:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_FILTER';
BEGIN
  -- Filter to export only active accounts
  UPDATE export_staging
     SET include_flag = 'N'
   WHERE export_id = ew_lb_api.g_export_id
     AND member_status = 'INACTIVE';
  
  -- Include only current year data
  UPDATE export_staging
     SET include_flag = 'N'
   WHERE export_id = ew_lb_api.g_export_id
     AND fiscal_year < TO_CHAR(SYSDATE, 'YYYY');
  
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_debug.log('Filtered export data for active accounts only');
END;
```

### 2. Format Transformation

Transform data format for external systems:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_TRANSFORM';
BEGIN
  -- Transform member codes for external system
  UPDATE export_staging
     SET external_code = 
       CASE 
         WHEN member_type = 'ACCOUNT' THEN 'GL_' || member_code
         WHEN member_type = 'ENTITY' THEN 'LE_' || member_code
         WHEN member_type = 'COSTCENTER' THEN 'CC_' || member_code
         ELSE member_code
       END
   WHERE export_id = ew_lb_api.g_export_id;
  
  -- Format dates for target system
  UPDATE export_staging
     SET formatted_date = TO_CHAR(effective_date, 'MM/DD/YYYY')
   WHERE export_id = ew_lb_api.g_export_id;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_debug.log('Transformed export data format');
END;
```

### 3. File Distribution

Distribute exported files to various destinations:

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'POST_EXPORT_DISTRIBUTE';
  l_file_name VARCHAR2(200);
BEGIN
  -- Get export file name
  SELECT file_name
    INTO l_file_name
    FROM export_log
   WHERE export_id = ew_lb_api.g_export_id;
  
  -- Copy to network share
  copy_file_to_share(
    p_source => l_file_name,
    p_destination => '\\fileserver\exports\' || l_file_name
  );
  
  -- FTP to external system
  ftp_file(
    p_server => 'ftp.partner.com',
    p_file => l_file_name,
    p_remote_dir => '/incoming/'
  );
  
  -- Send email with attachment
  ew_email.send_email(
    p_to => 'recipients@company.com',
    p_subject => 'Export Complete: ' || l_file_name,
    p_body => 'Export file attached',
    p_attachment => l_file_name
  );
  
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_debug.log('Distributed export file: ' || l_file_name);
END;
```

## Export Formats

### Supported Export Types

| Format | Description | Common Use Cases |
|--------|-------------|------------------|
| **CSV** | Comma-separated values | Data warehouse loads |
| **XML** | Structured XML | System integrations |
| **JSON** | JavaScript Object Notation | Web services, APIs |
| **Fixed Width** | Fixed column positions | Legacy systems |
| **Excel** | XLSX format | Business user consumption |
| **Custom** | User-defined format | Special requirements |

### Format-Specific Processing

#### CSV Export Enhancement

```sql
-- Add header row with metadata
DECLARE
  l_header VARCHAR2(4000);
BEGIN
  l_header := 'Export Date: ' || TO_CHAR(SYSDATE, 'YYYY-MM-DD') || CHR(10);
  l_header := l_header || 'Application: ' || ew_lb_api.g_app_name || CHR(10);
  l_header := l_header || 'Record Count: ' || ew_lb_api.g_record_count || CHR(10);
  l_header := l_header || CHR(10); -- Blank line
  
  -- Prepend header to export file
  prepend_to_file(
    p_file_name => ew_lb_api.g_export_file,
    p_content => l_header
  );
END;
```

#### XML Structure Modification

```sql
-- Add custom XML elements
DECLARE
  l_xml XMLTYPE;
BEGIN
  -- Load export XML
  SELECT XMLTYPE(file_content)
    INTO l_xml
    FROM export_files
   WHERE export_id = ew_lb_api.g_export_id;
  
  -- Add metadata element
  SELECT APPENDCHILDXML(
    l_xml,
    '/root',
    XMLELEMENT("metadata",
      XMLELEMENT("exportDate", SYSDATE),
      XMLELEMENT("exportUser", ew_lb_api.g_user_name),
      XMLELEMENT("recordCount", ew_lb_api.g_record_count)
    )
  ) INTO l_xml
  FROM dual;
  
  -- Save modified XML
  UPDATE export_files
     SET file_content = l_xml.getClobVal()
   WHERE export_id = ew_lb_api.g_export_id;
END;
```

## Performance Optimization

### Large Export Handling

```sql
-- Process large exports in chunks
DECLARE
  CURSOR c_export_data IS
    SELECT *
      FROM export_staging
     WHERE export_id = ew_lb_api.g_export_id
     ORDER BY member_id;
  
  TYPE t_export_array IS TABLE OF c_export_data%ROWTYPE;
  l_data t_export_array;
  l_chunk_size CONSTANT NUMBER := 10000;
BEGIN
  OPEN c_export_data;
  LOOP
    FETCH c_export_data BULK COLLECT INTO l_data LIMIT l_chunk_size;
    EXIT WHEN l_data.COUNT = 0;
    
    -- Process chunk
    process_export_chunk(l_data);
    
    -- Write to file
    append_to_export_file(l_data);
    
    COMMIT;
  END LOOP;
  CLOSE c_export_data;
END;
```

### Parallel Export Processing

```sql
-- Enable parallel processing
BEGIN
  EXECUTE IMMEDIATE 'ALTER SESSION ENABLE PARALLEL DML';
  
  -- Parallel data preparation
  INSERT /*+ PARALLEL(4) */ INTO export_staging
  SELECT /*+ PARALLEL(4) */ 
         member_id,
         member_name,
         properties,
         calculated_values
    FROM source_data
   WHERE export_criteria = 'Y';
  
  EXECUTE IMMEDIATE 'ALTER SESSION DISABLE PARALLEL DML';
END;
```

## Security and Compliance

### Data Masking

```sql
-- Mask sensitive data in exports
DECLARE
  c_script_name VARCHAR2(100) := 'PRE_EXPORT_MASK_DATA';
BEGIN
  -- Mask SSN
  UPDATE export_staging
     SET ssn = 'XXX-XX-' || SUBSTR(ssn, -4)
   WHERE export_id = ew_lb_api.g_export_id
     AND ssn IS NOT NULL;
  
  -- Mask email addresses
  UPDATE export_staging
     SET email = SUBSTR(email, 1, 2) || '****@' || 
                 SUBSTR(email, INSTR(email, '@') + 1)
   WHERE export_id = ew_lb_api.g_export_id
     AND email IS NOT NULL;
  
  -- Hash account numbers
  UPDATE export_staging
     SET account_number = DBMS_CRYPTO.HASH(
       UTL_RAW.CAST_TO_RAW(account_number),
       DBMS_CRYPTO.HASH_SH256
     )
   WHERE export_id = ew_lb_api.g_export_id
     AND account_number IS NOT NULL;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_debug.log('Sensitive data masked for export');
END;
```

### Audit Trail

```sql
-- Create audit record for export
INSERT INTO export_audit (
  export_id,
  export_date,
  exported_by,
  record_count,
  file_name,
  file_hash,
  recipients,
  export_purpose
) VALUES (
  ew_lb_api.g_export_id,
  SYSDATE,
  ew_lb_api.g_user_name,
  ew_lb_api.g_record_count,
  ew_lb_api.g_export_file,
  calculate_file_hash(ew_lb_api.g_export_file),
  ew_lb_api.g_recipients,
  ew_lb_api.g_export_purpose
);
```

## Error Handling

### Export Validation

```sql
-- Validate export completeness
DECLARE
  l_expected_count NUMBER;
  l_actual_count NUMBER;
BEGIN
  -- Get expected record count
  SELECT COUNT(*)
    INTO l_expected_count
    FROM source_data
   WHERE export_flag = 'Y';
  
  -- Get actual exported count
  SELECT COUNT(*)
    INTO l_actual_count
    FROM export_log_details
   WHERE export_id = ew_lb_api.g_export_id;
  
  IF l_actual_count < l_expected_count THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Export incomplete: Expected ' || 
                           l_expected_count || ' records, exported ' ||
                           l_actual_count;
    
    -- Mark export as partial
    UPDATE export_log
       SET status = 'PARTIAL',
           error_message = ew_lb_api.g_message
     WHERE export_id = ew_lb_api.g_export_id;
  END IF;
END;
```

### Recovery Mechanism

```sql
-- Implement export recovery
DECLARE
  l_restart_point NUMBER;
BEGIN
  -- Check for previous partial export
  BEGIN
    SELECT last_record_id
      INTO l_restart_point
      FROM export_recovery
     WHERE export_name = ew_lb_api.g_export_name
       AND status = 'PARTIAL';
    
    -- Resume from last point
    ew_debug.log('Resuming export from record ' || l_restart_point);
    resume_export_from(l_restart_point);
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- Start fresh export
      start_new_export();
  END;
END;
```

## Scheduling and Automation

### Automated Export Scheduling

```sql
-- Schedule regular exports
BEGIN
  DBMS_SCHEDULER.create_job(
    job_name => 'DAILY_METADATA_EXPORT',
    job_type => 'STORED_PROCEDURE',
    job_action => 'run_export_with_scripts',
    start_date => SYSTIMESTAMP,
    repeat_interval => 'FREQ=DAILY; BYHOUR=2; BYMINUTE=0',
    enabled => TRUE
  );
END;
```

### Conditional Export Triggers

```sql
-- Trigger export based on conditions
DECLARE
  l_changes_detected BOOLEAN;
BEGIN
  -- Check for metadata changes
  SELECT CASE WHEN COUNT(*) > 0 THEN TRUE ELSE FALSE END
    INTO l_changes_detected
    FROM metadata_changes
   WHERE change_date > (
     SELECT MAX(export_date)
       FROM export_log
      WHERE export_type = 'METADATA'
   );
  
  IF l_changes_detected THEN
    -- Trigger export
    ew_export_api.run_export(
      p_export_name => 'METADATA_DELTA_EXPORT',
      p_parameters => 'CHANGES_ONLY=Y'
    );
  END IF;
END;
```

## Best Practices

1. **Validate Before Export**
   - Check data completeness
   - Verify export criteria
   - Ensure file system space

2. **Transform Appropriately**
   - Apply format conversions
   - Handle special characters
   - Maintain data types

3. **Secure Sensitive Data**
   - Mask confidential information
   - Encrypt export files
   - Control distribution

4. **Monitor and Log**
   - Track export metrics
   - Log all distributions
   - Maintain audit trail

5. **Handle Failures Gracefully**
   - Implement retry logic
   - Provide clear error messages
   - Enable recovery options

## Next Steps

- [Pre-Export Scripts](pre-export.md)
- [Post-Export Scripts](post-export.md)
- [API Reference](../../api/)