# Post-Export Generation Scripts

Post-Export scripts execute after the export file has been generated, enabling file distribution, notifications, archiving, and integration with external systems.

## Overview

Post-Export scripts handle critical post-processing tasks:
- Distribute files to multiple destinations
- Send completion notifications
- Archive export files
- Trigger downstream processes
- Update tracking systems
- Clean up temporary data

![Post-Export Flow](../../assets/images/post-export-flow.png)
*Figure: Post-Export script execution flow*

## Input Parameters

### Export Results

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_export_id` | NUMBER | Export identifier | 54321 |
| `g_export_status` | VARCHAR2 | Export completion status | 'SUCCESS', 'PARTIAL', 'FAILED' |
| `g_export_file` | VARCHAR2 | Generated file name | 'METADATA_20250110.csv' |
| `g_export_path` | VARCHAR2 | File location | '/exports/daily/' |
| `g_file_size` | NUMBER | File size in bytes | 2048576 |
| `g_record_count` | NUMBER | Records exported | 1500 |

### Export Context

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `g_export_name` | VARCHAR2 | Export configuration | 'DAILY_METADATA_EXPORT' |
| `g_export_format` | VARCHAR2 | File format | 'CSV', 'XML', 'JSON' |
| `g_export_duration` | NUMBER | Export time in seconds | 45 |
| `g_export_date` | DATE | Export timestamp | SYSDATE |
| `g_user_name` | VARCHAR2 | User who initiated | 'ADMIN' |

## Output Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `g_status` | VARCHAR2 | Yes | 'S' (Success) or 'E' (Error) |
| `g_message` | VARCHAR2 | No | Status or error message |
| `g_distribution_status` | VARCHAR2 | No | Distribution result |

## Common Post-Export Tasks

### 1. File Distribution

Distribute export files to various destinations:

```sql
/*
 * Script: POST_EXPORT_DISTRIBUTE
 * Purpose: Distribute export file to multiple destinations
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_EXPORT_DISTRIBUTE';
  l_full_path VARCHAR2(500);
  l_distribution_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE copy_to_network_share IS
    l_target_path VARCHAR2(500);
  BEGIN
    l_target_path := '\\fileserver\shared\exports\' || 
                     TO_CHAR(SYSDATE, 'YYYY\MM\DD\') ||
                     ew_lb_api.g_export_file;
    
    -- Copy file to network share
    UTL_FILE.FCOPY(
      src_location  => 'EXPORT_DIR',
      src_filename  => ew_lb_api.g_export_file,
      dest_location => 'NETWORK_SHARE',
      dest_filename => ew_lb_api.g_export_file
    );
    
    log('File copied to network share: ' || l_target_path);
    l_distribution_count := l_distribution_count + 1;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Failed to copy to network share: ' || SQLERRM);
  END;
  
  PROCEDURE upload_to_ftp IS
    l_conn UTL_TCP.connection;
  BEGIN
    -- Connect to FTP server
    l_conn := ftp_pkg.login(
      p_host => 'ftp.partner.com',
      p_port => 21,
      p_user => 'export_user',
      p_pass => get_encrypted_password('FTP_PARTNER')
    );
    
    -- Upload file
    ftp_pkg.put_file(
      p_conn => l_conn,
      p_file => l_full_path,
      p_remote_dir => '/incoming/epmware/'
    );
    
    -- Close connection
    ftp_pkg.logout(l_conn);
    
    log('File uploaded to FTP server');
    l_distribution_count := l_distribution_count + 1;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('FTP upload failed: ' || SQLERRM);
  END;
  
  PROCEDURE upload_to_cloud IS
    l_response VARCHAR2(4000);
  BEGIN
    -- Upload to cloud storage (S3, Azure, etc.)
    l_response := cloud_storage_api.upload_file(
      p_bucket => 'company-exports',
      p_key => 'epmware/' || TO_CHAR(SYSDATE, 'YYYY/MM/DD/') || 
               ew_lb_api.g_export_file,
      p_file_path => l_full_path,
      p_metadata => JSON_OBJECT(
        'source' VALUE 'EPMware',
        'export_id' VALUE ew_lb_api.g_export_id,
        'export_date' VALUE TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS')
      )
    );
    
    log('File uploaded to cloud storage: ' || l_response);
    l_distribution_count := l_distribution_count + 1;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Cloud upload failed: ' || SQLERRM);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting file distribution for export ' || ew_lb_api.g_export_id);
  
  -- Build full file path
  l_full_path := ew_lb_api.g_export_path || ew_lb_api.g_export_file;
  
  -- Only distribute successful exports
  IF ew_lb_api.g_export_status != 'SUCCESS' THEN
    log('Skipping distribution - export status: ' || ew_lb_api.g_export_status);
    ew_lb_api.g_message := 'Distribution skipped for non-successful export';
    RETURN;
  END IF;
  
  -- Distribute to various destinations
  copy_to_network_share();
  upload_to_ftp();
  upload_to_cloud();
  
  -- Update distribution log
  INSERT INTO export_distribution_log (
    export_id,
    file_name,
    destinations,
    distribution_count,
    distribution_date
  ) VALUES (
    ew_lb_api.g_export_id,
    ew_lb_api.g_export_file,
    'NETWORK,FTP,CLOUD',
    l_distribution_count,
    SYSDATE
  );
  
  COMMIT;
  
  ew_lb_api.g_distribution_status := 'DISTRIBUTED';
  ew_lb_api.g_message := 'File distributed to ' || l_distribution_count || ' destinations';
  log('Distribution complete');
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Distribution error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
END;
```

### 2. Email Notification

Send export completion notifications:

```sql
/*
 * Script: POST_EXPORT_NOTIFY
 * Purpose: Send email notifications with export summary
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_EXPORT_NOTIFY';
  l_email_body CLOB;
  l_recipients VARCHAR2(1000);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  FUNCTION get_recipients RETURN VARCHAR2 IS
    l_list VARCHAR2(1000);
  BEGIN
    -- Get recipients based on export type
    SELECT LISTAGG(email, ';') WITHIN GROUP (ORDER BY email)
      INTO l_list
      FROM export_notification_list
     WHERE export_name = ew_lb_api.g_export_name
       AND active = 'Y';
    
    RETURN l_list;
  END;
  
  FUNCTION generate_email_body RETURN CLOB IS
    l_body CLOB;
    l_file_size_mb NUMBER;
  BEGIN
    l_file_size_mb := ROUND(ew_lb_api.g_file_size / 1024 / 1024, 2);
    
    l_body := '<html><body>';
    l_body := l_body || '<h2>Export Completed Successfully</h2>';
    l_body := l_body || '<table border="0" cellpadding="5">';
    l_body := l_body || '<tr><td><b>Export Name:</b></td><td>' || 
              ew_lb_api.g_export_name || '</td></tr>';
    l_body := l_body || '<tr><td><b>File Name:</b></td><td>' || 
              ew_lb_api.g_export_file || '</td></tr>';
    l_body := l_body || '<tr><td><b>Format:</b></td><td>' || 
              ew_lb_api.g_export_format || '</td></tr>';
    l_body := l_body || '<tr><td><b>Records Exported:</b></td><td>' || 
              TO_CHAR(ew_lb_api.g_record_count, 'FM999,999,999') || '</td></tr>';
    l_body := l_body || '<tr><td><b>File Size:</b></td><td>' || 
              l_file_size_mb || ' MB</td></tr>';
    l_body := l_body || '<tr><td><b>Export Duration:</b></td><td>' || 
              ew_lb_api.g_export_duration || ' seconds</td></tr>';
    l_body := l_body || '<tr><td><b>Export Date:</b></td><td>' || 
              TO_CHAR(ew_lb_api.g_export_date, 'DD-MON-YYYY HH24:MI:SS') || '</td></tr>';
    l_body := l_body || '<tr><td><b>Exported By:</b></td><td>' || 
              ew_lb_api.g_user_name || '</td></tr>';
    l_body := l_body || '</table>';
    
    -- Add file location information
    l_body := l_body || '<h3>File Locations</h3>';
    l_body := l_body || '<ul>';
    l_body := l_body || '<li>Network Share: \\fileserver\exports\' || 
              ew_lb_api.g_export_file || '</li>';
    l_body := l_body || '<li>FTP: ftp.partner.com/incoming/' || 
              ew_lb_api.g_export_file || '</li>';
    l_body := l_body || '<li>Cloud Storage: s3://company-exports/epmware/' || 
              ew_lb_api.g_export_file || '</li>';
    l_body := l_body || '</ul>';
    
    -- Add download link if available
    IF get_download_url(ew_lb_api.g_export_id) IS NOT NULL THEN
      l_body := l_body || '<p><a href="' || get_download_url(ew_lb_api.g_export_id) || 
                '">Download Export File</a></p>';
    END IF;
    
    l_body := l_body || '<hr>';
    l_body := l_body || '<p><small>This is an automated notification from EPMware Export Service.</small></p>';
    l_body := l_body || '</body></html>';
    
    RETURN l_body;
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Sending notifications for export ' || ew_lb_api.g_export_id);
  
  -- Get recipient list
  l_recipients := get_recipients();
  
  IF l_recipients IS NULL THEN
    log('No recipients configured for ' || ew_lb_api.g_export_name);
    ew_lb_api.g_message := 'No notifications sent - no recipients configured';
    RETURN;
  END IF;
  
  -- Generate email body
  l_email_body := generate_email_body();
  
  -- Send email
  ew_email.send_email(
    p_to        => l_recipients,
    p_subject   => 'Export Complete: ' || ew_lb_api.g_export_name || 
                   ' [' || TO_CHAR(ew_lb_api.g_export_date, 'DD-MON-YYYY') || ']',
    p_body      => 'Export completed successfully. See HTML version for details.',
    p_body_html => l_email_body,
    p_attachment => CASE 
                     WHEN ew_lb_api.g_file_size < 10485760 THEN -- Less than 10MB
                       ew_lb_api.g_export_path || ew_lb_api.g_export_file
                     ELSE NULL
                   END
  );
  
  -- Log notification
  INSERT INTO notification_log (
    export_id,
    notification_type,
    recipients,
    sent_date,
    status
  ) VALUES (
    ew_lb_api.g_export_id,
    'EMAIL',
    l_recipients,
    SYSDATE,
    'SENT'
  );
  
  COMMIT;
  
  log('Notifications sent to: ' || l_recipients);
  ew_lb_api.g_message := 'Notifications sent successfully';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Notification error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
END;
```

### 3. Archive Management

Archive export files and manage retention:

```sql
/*
 * Script: POST_EXPORT_ARCHIVE
 * Purpose: Archive export files and manage retention policy
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_EXPORT_ARCHIVE';
  l_archive_path VARCHAR2(500);
  l_retention_days NUMBER := 90;
  l_deleted_count NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE archive_export_file IS
  BEGIN
    -- Create archive path
    l_archive_path := '/archive/exports/' || 
                     TO_CHAR(ew_lb_api.g_export_date, 'YYYY/MM/DD/') ||
                     ew_lb_api.g_export_file;
    
    -- Move file to archive
    UTL_FILE.FRENAME(
      src_location  => 'EXPORT_DIR',
      src_filename  => ew_lb_api.g_export_file,
      dest_location => 'ARCHIVE_DIR',
      dest_filename => TO_CHAR(ew_lb_api.g_export_date, 'YYYY/MM/DD/') || 
                      ew_lb_api.g_export_file,
      overwrite     => FALSE
    );
    
    -- Compress archived file
    compress_file(l_archive_path);
    
    log('File archived to: ' || l_archive_path || '.gz');
  END;
  
  PROCEDURE clean_old_exports IS
    l_cutoff_date DATE;
  BEGIN
    l_cutoff_date := SYSDATE - l_retention_days;
    
    -- Delete old export records
    DELETE FROM export_log
     WHERE export_date < l_cutoff_date
       AND archive_flag = 'Y';
    
    l_deleted_count := SQL%ROWCOUNT;
    
    -- Delete old archive files
    FOR rec IN (
      SELECT archive_path
        FROM export_archive
       WHERE archive_date < l_cutoff_date
    ) LOOP
      BEGIN
        delete_file(rec.archive_path);
        log('Deleted old archive: ' || rec.archive_path);
      EXCEPTION
        WHEN OTHERS THEN
          log('Could not delete: ' || rec.archive_path);
      END;
    END LOOP;
    
    -- Clean archive records
    DELETE FROM export_archive
     WHERE archive_date < l_cutoff_date;
    
    log('Cleaned ' || l_deleted_count || ' old export records');
  END;
  
  PROCEDURE update_archive_catalog IS
  BEGIN
    -- Update archive catalog
    MERGE INTO export_archive_catalog c
    USING (
      SELECT ew_lb_api.g_export_id AS export_id,
             ew_lb_api.g_export_name AS export_name,
             ew_lb_api.g_export_file AS file_name,
             l_archive_path || '.gz' AS archive_path,
             ew_lb_api.g_file_size AS original_size,
             get_file_size(l_archive_path || '.gz') AS compressed_size,
             ew_lb_api.g_record_count AS record_count,
             ew_lb_api.g_export_date AS export_date,
             SYSDATE AS archive_date
        FROM dual
    ) s
    ON (c.export_id = s.export_id)
    WHEN NOT MATCHED THEN
      INSERT (export_id, export_name, file_name, archive_path,
              original_size, compressed_size, record_count,
              export_date, archive_date)
      VALUES (s.export_id, s.export_name, s.file_name, s.archive_path,
              s.original_size, s.compressed_size, s.record_count,
              s.export_date, s.archive_date);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting archive process for export ' || ew_lb_api.g_export_id);
  
  -- Archive the export file
  archive_export_file();
  
  -- Update catalog
  update_archive_catalog();
  
  -- Clean old exports based on retention policy
  clean_old_exports();
  
  -- Update export log
  UPDATE export_log
     SET archive_flag = 'Y',
         archive_path = l_archive_path || '.gz',
         archive_date = SYSDATE
   WHERE export_id = ew_lb_api.g_export_id;
  
  COMMIT;
  
  log('Archive process complete');
  ew_lb_api.g_message := 'File archived, ' || l_deleted_count || ' old exports cleaned';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Archive error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

### 4. Trigger Downstream Processing

Initiate dependent processes after export:

```sql
/*
 * Script: POST_EXPORT_TRIGGER_DOWNSTREAM
 * Purpose: Trigger downstream processes after successful export
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_EXPORT_TRIGGER_DOWNSTREAM';
  l_job_id NUMBER;
  l_api_response VARCHAR2(4000);
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
  PROCEDURE trigger_data_warehouse_load IS
  BEGIN
    -- Call DW load API
    l_api_response := call_rest_api(
      p_url => 'https://datawarehouse.company.com/api/load',
      p_method => 'POST',
      p_headers => 'Content-Type: application/json',
      p_body => JSON_OBJECT(
        'source' VALUE 'EPMware',
        'export_id' VALUE ew_lb_api.g_export_id,
        'file_name' VALUE ew_lb_api.g_export_file,
        'file_path' VALUE ew_lb_api.g_export_path,
        'record_count' VALUE ew_lb_api.g_record_count,
        'load_type' VALUE 'INCREMENTAL'
      )
    );
    
    -- Parse response
    IF JSON_VALUE(l_api_response, '$.status') = 'accepted' THEN
      l_job_id := JSON_VALUE(l_api_response, '$.job_id');
      log('DW load triggered, job ID: ' || l_job_id);
    ELSE
      log('DW load failed: ' || l_api_response);
    END IF;
  END;
  
  PROCEDURE trigger_reporting_refresh IS
  BEGIN
    -- Submit reporting refresh job
    DBMS_SCHEDULER.create_job(
      job_name => 'REFRESH_REPORTS_' || ew_lb_api.g_export_id,
      job_type => 'STORED_PROCEDURE',
      job_action => 'refresh_reporting_tables',
      start_date => SYSTIMESTAMP,
      comments => 'Triggered by export ' || ew_lb_api.g_export_id
    );
    
    log('Reporting refresh job submitted');
  END;
  
  PROCEDURE notify_external_system IS
    l_message_id VARCHAR2(100);
  BEGIN
    -- Send message to queue/topic
    send_to_message_queue(
      p_queue => 'export-notifications',
      p_message => JSON_OBJECT(
        'event' VALUE 'export_complete',
        'export_id' VALUE ew_lb_api.g_export_id,
        'export_name' VALUE ew_lb_api.g_export_name,
        'file_name' VALUE ew_lb_api.g_export_file,
        'timestamp' VALUE TO_CHAR(SYSDATE, 'YYYY-MM-DD"T"HH24:MI:SS')
      ),
      p_message_id => l_message_id
    );
    
    log('Message sent to queue, ID: ' || l_message_id);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Triggering downstream processes for export ' || ew_lb_api.g_export_id);
  
  -- Only trigger for successful exports
  IF ew_lb_api.g_export_status != 'SUCCESS' THEN
    log('Skipping downstream triggers - export not successful');
    RETURN;
  END IF;
  
  -- Trigger various downstream processes
  BEGIN
    trigger_data_warehouse_load();
  EXCEPTION
    WHEN OTHERS THEN
      log('DW trigger failed: ' || SQLERRM);
  END;
  
  BEGIN
    trigger_reporting_refresh();
  EXCEPTION
    WHEN OTHERS THEN
      log('Reporting trigger failed: ' || SQLERRM);
  END;
  
  BEGIN
    notify_external_system();
  EXCEPTION
    WHEN OTHERS THEN
      log('External notification failed: ' || SQLERRM);
  END;
  
  -- Log downstream triggers
  INSERT INTO downstream_trigger_log (
    export_id,
    trigger_date,
    processes_triggered,
    status
  ) VALUES (
    ew_lb_api.g_export_id,
    SYSDATE,
    'DW_LOAD,REPORTING,EXTERNAL',
    'TRIGGERED'
  );
  
  COMMIT;
  
  log('Downstream processes triggered');
  ew_lb_api.g_message := 'Downstream processes initiated';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Downstream trigger error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
END;
```

### 5. Cleanup and Maintenance

Clean up temporary data and maintain export system:

```sql
/*
 * Script: POST_EXPORT_CLEANUP
 * Purpose: Clean up temporary data and perform maintenance
 */
DECLARE
  c_script_name VARCHAR2(100) := 'POST_EXPORT_CLEANUP';
  l_rows_cleaned NUMBER := 0;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting cleanup for export ' || ew_lb_api.g_export_id);
  
  -- Clean staging table
  DELETE FROM export_staging
   WHERE export_id = ew_lb_api.g_export_id
     AND NVL(include_flag, 'Y') = 'Y';
  
  l_rows_cleaned := SQL%ROWCOUNT;
  log('Cleaned ' || l_rows_cleaned || ' staging records');
  
  -- Clean temporary indexes
  BEGIN
    EXECUTE IMMEDIATE 'DROP INDEX idx_exp_stg_' || ew_lb_api.g_export_id;
  EXCEPTION
    WHEN OTHERS THEN
      NULL; -- Index might not exist
  END;
  
  -- Update export statistics
  UPDATE export_statistics
     SET last_export_date = ew_lb_api.g_export_date,
         last_record_count = ew_lb_api.g_record_count,
         total_exports = total_exports + 1,
         total_records = total_records + ew_lb_api.g_record_count
   WHERE export_name = ew_lb_api.g_export_name;
  
  IF SQL%ROWCOUNT = 0 THEN
    INSERT INTO export_statistics (
      export_name,
      last_export_date,
      last_record_count,
      total_exports,
      total_records
    ) VALUES (
      ew_lb_api.g_export_name,
      ew_lb_api.g_export_date,
      ew_lb_api.g_record_count,
      1,
      ew_lb_api.g_record_count
    );
  END IF;
  
  -- Gather table statistics
  DBMS_STATS.gather_table_stats(
    ownname => USER,
    tabname => 'EXPORT_STAGING'
  );
  
  COMMIT;
  
  log('Cleanup complete');
  ew_lb_api.g_message := 'Cleaned ' || l_rows_cleaned || ' temporary records';
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Cleanup error: ' || SQLERRM;
    log('Exception: ' || SQLERRM);
    ROLLBACK;
END;
```

## Error Handling

### Export Failure Notification

```sql
-- Handle export failures
IF ew_lb_api.g_export_status = 'FAILED' THEN
  -- Send failure alert
  ew_email.send_email(
    p_to => 'support@company.com',
    p_subject => 'URGENT: Export Failed - ' || ew_lb_api.g_export_name,
    p_body => 'Export ' || ew_lb_api.g_export_id || ' failed. ' ||
              'Error: ' || get_export_error(ew_lb_api.g_export_id)
  );
  
  -- Create incident ticket
  create_support_ticket(
    p_type => 'EXPORT_FAILURE',
    p_priority => 'HIGH',
    p_description => 'Export failed: ' || ew_lb_api.g_export_name
  );
END IF;
```

## Best Practices

1. **Handle All Export Statuses**
   - Different actions for SUCCESS, PARTIAL, FAILED
   - Don't assume successful export

2. **Implement Reliable Distribution**
   - Use error handling for each destination
   - Log successful and failed distributions
   - Provide fallback mechanisms

3. **Maintain Audit Trail**
   - Log all post-export actions
   - Track distribution destinations
   - Record cleanup operations

4. **Optimize for Large Files**
   - Stream large files rather than loading into memory
   - Use compression for archives
   - Implement chunked transfers

5. **Security Considerations**
   - Encrypt sensitive exports
   - Use secure transfer protocols
   - Verify recipient authorization

## Next Steps

- [Pre-Export Scripts](pre-export.md)
- [Export Overview](index.md)
- [API Reference](../../api/)