# Post-Import ERP Scripts

Post-Import scripts execute after ERP data has been imported into EPMware, providing validation, enrichment, and follow-up processing capabilities.

## Overview

Post-Import scripts handle tasks that must occur after data is successfully loaded:
- Validate imported data integrity
- Generate derived members and calculations
- Update related metadata
- Send import notifications
- Clean up temporary data

![Post-Import Flow](../../assets/images/post-import-flow.png)
*Figure: Post-Import script execution in the ERP import process*

## Input Parameters

### Import Results

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_batch_id` | NUMBER | Import batch identifier | 98765 |
| `g_import_status` | VARCHAR2 | Import result status | 'SUCCESS', 'PARTIAL', 'FAILED' |
| `g_records_imported` | NUMBER | Successfully imported records | 4850 |
| `g_records_failed` | NUMBER | Failed records | 150 |
| `g_import_duration` | NUMBER | Import time in seconds | 125 |

### Import Context

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_app_id` | NUMBER | Target application ID | 100 |
| `g_app_name` | VARCHAR2 | Target application | 'HFM_PROD' |
| `g_dimension_name` | VARCHAR2 | Target dimension | 'Account' |
| `g_import_type` | VARCHAR2 | Import type | 'FULL', 'INCREMENTAL' |
| `g_user_name` | VARCHAR2 | User who initiated import | 'ADMIN' |

## Output Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `g_status` | VARCHAR2 | Yes | 'S' (Success) or 'E' (Error) |
| `g_message` | VARCHAR2 | No | Status or error message |
| `g_followup_action` | VARCHAR2 | No | Next action to trigger |

## Common Post-Import Tasks

### 1. Data Validation

Validate imported data integrity:

```sql
/*
 * Script: POST_IMPORT_VALIDATE_INTEGRITY
 * Purpose: Validate data integrity after import
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_IMPORT_VALIDATE_INTEGRITY';
  l_validation_errors VARCHAR2(4000);
  l_error_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE check_parent_child_relationships IS
    l_orphan_count NUMBER;
  BEGIN
    -- Check for orphaned members
    SELECT COUNT(*)
      INTO l_orphan_count
      FROM ew_members_v m
     WHERE m.batch_id = ew_lb_api.g_batch_id
       AND NOT EXISTS (
         SELECT 1
           FROM ew_members_v p
          WHERE p.member_name = m.parent_name
            AND p.dimension_name = m.dimension_name
       )
       AND m.parent_name != 'ROOT';
    
    IF l_orphan_count > 0 THEN
      l_error_count := l_error_count + 1;
      l_validation_errors := l_validation_errors || 
        'Found ' || l_orphan_count || ' orphaned members; ';
      
      -- Log orphaned members
      FOR rec IN (
        SELECT member_name, parent_name
          FROM ew_members_v m
         WHERE m.batch_id = ew_lb_api.g_batch_id
           AND NOT EXISTS (
             SELECT 1
               FROM ew_members_v p
              WHERE p.member_name = m.parent_name
                AND p.dimension_name = m.dimension_name
           )
           AND m.parent_name != 'ROOT'
      ) LOOP
        log('Orphaned member: ' || rec.member_name || 
            ' (parent: ' || rec.parent_name || ')');
      END LOOP;
    END IF;
  END;
  
  PROCEDURE check_required_properties IS
    l_missing_count NUMBER;
  BEGIN
    -- Check for missing required properties
    SELECT COUNT(*)
      INTO l_missing_count
      FROM imported_members m
     WHERE batch_id = ew_lb_api.g_batch_id
       AND member_type = 'ACCOUNT'
       AND account_type IS NULL;
    
    IF l_missing_count > 0 THEN
      l_error_count := l_error_count + 1;
      l_validation_errors := l_validation_errors || 
        l_missing_count || ' accounts missing account type; ';
      
      -- Set default account type
      UPDATE imported_members
         SET account_type = 'EXPENSE'
       WHERE batch_id = ew_lb_api.g_batch_id
         AND member_type = 'ACCOUNT'
         AND account_type IS NULL;
      
      log('Set default account type for ' || SQL%ROWCOUNT || ' members');
    END IF;
  END;
  
  PROCEDURE check_data_consistency IS
    l_balance_diff NUMBER;
  BEGIN
    -- Check trial balance
    SELECT ABS(SUM(DECODE(account_type, 
                    'ASSET', amount,
                    'EXPENSE', amount,
                    'LIABILITY', -amount,
                    'EQUITY', -amount,
                    'REVENUE', -amount,
                    0)))
      INTO l_balance_diff
      FROM import_data_summary
     WHERE batch_id = ew_lb_api.g_batch_id;
    
    IF l_balance_diff > 0.01 THEN
      l_validation_errors := l_validation_errors || 
        'Trial balance out by ' || l_balance_diff || '; ';
      log('WARNING: Trial balance discrepancy: ' || l_balance_diff);
    END IF;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting post-import validation for batch ' || ew_lb_api.g_batch_id);
  
  -- Run validation checks
  check_parent_child_relationships();
  check_required_properties();
  check_data_consistency();
  
  -- Report results
  IF l_error_count > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation errors: ' || l_validation_errors;
    
    -- Send alert
    ew_email.send_email(
      p_to      => 'data-admin@company.com',
      p_subject => 'Post-Import Validation Errors',
      p_body    => 'Batch ' || ew_lb_api.g_batch_id || ' has validation errors: ' ||
                   CHR(10) || CHR(10) || l_validation_errors
    );
  ELSE
    log('All validations passed');
    ew_lb_api.g_message := 'Post-import validation successful';
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
END;
```

### 2. Generate Derived Members

Create calculated and derived members:

```sql
/*
 * Script: POST_IMPORT_GENERATE_DERIVED
 * Purpose: Generate derived members and calculations
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_IMPORT_GENERATE_DERIVED';
  l_created_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE create_ratio_accounts IS
  BEGIN
    -- Create ratio accounts for imported base accounts
    FOR rec IN (
      SELECT DISTINCT 
             'RATIO_' || REPLACE(member_name, 'REV_', '') AS ratio_name,
             member_name AS numerator,
             'REV_TOTAL' AS denominator,
             parent_name
        FROM imported_members
       WHERE batch_id = ew_lb_api.g_batch_id
         AND member_name LIKE 'REV_%'
         AND member_name != 'REV_TOTAL'
    ) LOOP
      -- Check if ratio account exists
      IF ew_hierarchy.chk_member_exists(
           p_app_name    => ew_lb_api.g_app_name,
           p_dim_name    => 'Account',
           p_member_name => rec.ratio_name
         ) = 'N' THEN
        
        -- Create ratio account
        INSERT INTO member_create_queue (
          app_name,
          dimension_name,
          member_name,
          parent_name,
          member_type,
          formula,
          created_by,
          created_date
        ) VALUES (
          ew_lb_api.g_app_name,
          'Account',
          rec.ratio_name,
          'Ratios',
          'DYNAMIC',
          rec.numerator || ' / ' || rec.denominator || ' * 100',
          ew_lb_api.g_user_name,
          SYSDATE
        );
        
        l_created_count := l_created_count + 1;
      END IF;
    END LOOP;
    
    log('Created ' || l_created_count || ' ratio accounts');
  END;
  
  PROCEDURE create_variance_accounts IS
  BEGIN
    -- Create variance accounts
    FOR rec IN (
      SELECT DISTINCT
             member_name,
             REPLACE(member_name, '_ACT', '_VAR') AS variance_name,
             REPLACE(member_name, '_ACT', '_BUD') AS budget_name,
             parent_name
        FROM imported_members
       WHERE batch_id = ew_lb_api.g_batch_id
         AND member_name LIKE '%_ACT'
    ) LOOP
      -- Check if budget account exists
      IF ew_hierarchy.chk_member_exists(
           p_app_name    => ew_lb_api.g_app_name,
           p_dim_name    => 'Account',
           p_member_name => rec.budget_name
         ) = 'Y' THEN
        
        -- Create variance account if doesn't exist
        IF ew_hierarchy.chk_member_exists(
             p_app_name    => ew_lb_api.g_app_name,
             p_dim_name    => 'Account',
             p_member_name => rec.variance_name
           ) = 'N' THEN
          
          INSERT INTO member_create_queue (
            app_name,
            dimension_name,
            member_name,
            parent_name,
            member_type,
            formula,
            created_by,
            created_date
          ) VALUES (
            ew_lb_api.g_app_name,
            'Account',
            rec.variance_name,
            REPLACE(rec.parent_name, '_ACT', '_VAR'),
            'DYNAMIC',
            rec.member_name || ' - ' || rec.budget_name,
            ew_lb_api.g_user_name,
            SYSDATE
          );
          
          l_created_count := l_created_count + 1;
        END IF;
      END IF;
    END LOOP;
    
    log('Created ' || l_created_count || ' variance accounts');
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Generating derived members for batch ' || ew_lb_api.g_batch_id);
  
  -- Generate various derived members
  create_ratio_accounts();
  create_variance_accounts();
  
  -- Process the queue
  IF l_created_count > 0 THEN
    process_member_create_queue();
    COMMIT;
  END IF;
  
  ew_lb_api.g_message := 'Generated ' || l_created_count || ' derived members';
  log('Derived member generation complete');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error generating derived members: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

### 3. Import Summary Report

Generate and send import summary:

```sql
/*
 * Script: POST_IMPORT_SUMMARY_REPORT
 * Purpose: Generate and send import summary report
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_IMPORT_SUMMARY_REPORT';
  l_report_body CLOB;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  FUNCTION generate_html_report RETURN CLOB IS
    l_html CLOB;
  BEGIN
    l_html := '<html><body>';
    l_html := l_html || '<h2>ERP Import Summary Report</h2>';
    l_html := l_html || '<p><b>Batch ID:</b> ' || ew_lb_api.g_batch_id || '</p>';
    l_html := l_html || '<p><b>Import Date:</b> ' || TO_CHAR(SYSDATE, 'DD-MON-YYYY HH24:MI:SS') || '</p>';
    l_html := l_html || '<p><b>Application:</b> ' || ew_lb_api.g_app_name || '</p>';
    l_html := l_html || '<p><b>Status:</b> ' || ew_lb_api.g_import_status || '</p>';
    
    -- Statistics
    l_html := l_html || '<h3>Import Statistics</h3>';
    l_html := l_html || '<table border="1" cellpadding="5">';
    l_html := l_html || '<tr><th>Metric</th><th>Count</th></tr>';
    l_html := l_html || '<tr><td>Records Imported</td><td>' || ew_lb_api.g_records_imported || '</td></tr>';
    l_html := l_html || '<tr><td>Records Failed</td><td>' || ew_lb_api.g_records_failed || '</td></tr>';
    l_html := l_html || '<tr><td>Duration (seconds)</td><td>' || ew_lb_api.g_import_duration || '</td></tr>';
    l_html := l_html || '</table>';
    
    -- Top-level summary by dimension
    l_html := l_html || '<h3>Members by Dimension</h3>';
    l_html := l_html || '<table border="1" cellpadding="5">';
    l_html := l_html || '<tr><th>Dimension</th><th>New</th><th>Updated</th><th>Errors</th></tr>';
    
    FOR rec IN (
      SELECT dimension_name,
             SUM(DECODE(action_type, 'INSERT', 1, 0)) AS new_count,
             SUM(DECODE(action_type, 'UPDATE', 1, 0)) AS update_count,
             SUM(DECODE(status, 'ERROR', 1, 0)) AS error_count
        FROM import_log
       WHERE batch_id = ew_lb_api.g_batch_id
       GROUP BY dimension_name
       ORDER BY dimension_name
    ) LOOP
      l_html := l_html || '<tr>';
      l_html := l_html || '<td>' || rec.dimension_name || '</td>';
      l_html := l_html || '<td>' || rec.new_count || '</td>';
      l_html := l_html || '<td>' || rec.update_count || '</td>';
      l_html := l_html || '<td>' || rec.error_count || '</td>';
      l_html := l_html || '</tr>';
    END LOOP;
    
    l_html := l_html || '</table>';
    
    -- Error details if any
    IF ew_lb_api.g_records_failed > 0 THEN
      l_html := l_html || '<h3>Error Details (Top 10)</h3>';
      l_html := l_html || '<table border="1" cellpadding="5">';
      l_html := l_html || '<tr><th>Record</th><th>Error</th></tr>';
      
      FOR rec IN (
        SELECT record_identifier, error_message
          FROM import_errors
         WHERE batch_id = ew_lb_api.g_batch_id
         ORDER BY error_date
         FETCH FIRST 10 ROWS ONLY
      ) LOOP
        l_html := l_html || '<tr>';
        l_html := l_html || '<td>' || rec.record_identifier || '</td>';
        l_html := l_html || '<td>' || rec.error_message || '</td>';
        l_html := l_html || '</tr>';
      END LOOP;
      
      l_html := l_html || '</table>';
    END IF;
    
    l_html := l_html || '</body></html>';
    RETURN l_html;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Generating import summary report for batch ' || ew_lb_api.g_batch_id);
  
  -- Generate report
  l_report_body := generate_html_report();
  
  -- Send email report
  ew_email.send_email(
    p_to        => 'finance-team@company.com',
    p_cc        => 'it-support@company.com',
    p_subject   => 'ERP Import Report - ' || ew_lb_api.g_app_name || 
                   ' [' || ew_lb_api.g_import_status || ']',
    p_body      => 'Please see attached HTML report for import details.',
    p_body_html => l_report_body
  );
  
  -- Archive report
  INSERT INTO import_reports (
    batch_id,
    report_date,
    report_type,
    report_content,
    recipients
  ) VALUES (
    ew_lb_api.g_batch_id,
    SYSDATE,
    'POST_IMPORT_SUMMARY',
    l_report_body,
    'finance-team@company.com'
  );
  
  COMMIT;
  
  log('Import summary report sent successfully');
  ew_lb_api.g_message := 'Summary report generated and sent';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Error generating report: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
END;
```

### 4. Cleanup and Archival

Clean temporary data and archive import:

```sql
/*
 * Script: POST_IMPORT_CLEANUP
 * Purpose: Clean up temporary data and archive import
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_IMPORT_CLEANUP';
  l_archive_table VARCHAR2(30);
  l_rows_archived NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting cleanup for batch ' || ew_lb_api.g_batch_id);
  
  -- Archive staging data
  l_archive_table := 'ERP_STAGING_' || TO_CHAR(SYSDATE, 'YYYYMM');
  
  -- Create monthly archive table if doesn't exist
  BEGIN
    EXECUTE IMMEDIATE 
      'CREATE TABLE ' || l_archive_table || 
      ' AS SELECT * FROM erp_staging_table WHERE 1=0';
  EXCEPTION
    WHEN OTHERS THEN
      IF SQLCODE != -955 THEN -- Table already exists
        RAISE;
      END IF;
  END;
  
  -- Move processed records to archive
  EXECUTE IMMEDIATE
    'INSERT INTO ' || l_archive_table ||
    ' SELECT * FROM erp_staging_table' ||
    ' WHERE batch_id = :batch_id' ||
    ' AND import_status IN (''SUCCESS'', ''PROCESSED'')'
  USING ew_lb_api.g_batch_id;
  
  l_rows_archived := SQL%ROWCOUNT;
  
  -- Delete archived records from staging
  DELETE FROM erp_staging_table
   WHERE batch_id = ew_lb_api.g_batch_id
     AND import_status IN ('SUCCESS', 'PROCESSED');
  
  log('Archived ' || l_rows_archived || ' records to ' || l_archive_table);
  
  -- Clean old error records (older than 90 days)
  DELETE FROM import_errors
   WHERE error_date < SYSDATE - 90;
  
  log('Deleted ' || SQL%ROWCOUNT || ' old error records');
  
  -- Update batch statistics
  UPDATE import_batch_log
     SET status = 'COMPLETED',
         end_date = SYSDATE,
         records_processed = ew_lb_api.g_records_imported,
         records_failed = ew_lb_api.g_records_failed,
         archive_table = l_archive_table
   WHERE batch_id = ew_lb_api.g_batch_id;
  
  COMMIT;
  
  -- Gather statistics on affected tables
  DBMS_STATS.gather_table_stats(
    ownname => USER,
    tabname => 'ERP_STAGING_TABLE'
  );
  
  log('Cleanup completed successfully');
  ew_lb_api.g_message := 'Cleanup complete: ' || l_rows_archived || ' records archived';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Cleanup error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

## Integration with Other Systems

### Trigger Downstream Processes

```sql
-- Trigger consolidation after successful import
IF ew_lb_api.g_import_status = 'SUCCESS' THEN
  -- Submit consolidation job
  l_job_id := ew_agent_api.submit_job(
    p_job_type => 'CONSOLIDATION',
    p_app_name => ew_lb_api.g_app_name,
    p_parameters => 'SCENARIO=ACTUAL;YEAR=' || TO_CHAR(SYSDATE, 'YYYY')
  );
  
  log('Triggered consolidation job: ' || l_job_id);
  ew_lb_api.g_followup_action := 'CONSOLIDATION_JOB_' || l_job_id;
END IF;
```

### Update External Systems

```sql
-- Update data warehouse with import status
BEGIN
  -- Call web service to update DW
  l_response := call_web_service(
    p_url => 'https://datawarehouse.company.com/api/import-status',
    p_method => 'POST',
    p_payload => JSON_OBJECT(
      'batch_id' VALUE ew_lb_api.g_batch_id,
      'status' VALUE ew_lb_api.g_import_status,
      'records' VALUE ew_lb_api.g_records_imported,
      'timestamp' VALUE TO_CHAR(SYSDATE, 'YYYY-MM-DD"T"HH24:MI:SS')
    )
  );
  
  log('Data warehouse updated: ' || l_response);
END;
```

## Best Practices

1. **Validate Completeness**
   - Check all expected data was imported
   - Verify relationships and dependencies
   - Validate calculations and balances

2. **Generate Audit Reports**
   - Create detailed import summaries
   - Log all transformations applied
   - Track error patterns

3. **Clean Up Properly**
   - Archive processed data
   - Remove temporary files
   - Update statistics

4. **Communicate Results**
   - Send notifications to stakeholders
   - Provide actionable error reports
   - Include next steps

5. **Prepare for Next Import**
   - Reset sequences and counters
   - Clear staging areas
   - Update control tables

## Next Steps

- [Export Tasks](../export/)
- [API Reference](../../api/)
- [Pre-Import Scripts](pre-import.md)