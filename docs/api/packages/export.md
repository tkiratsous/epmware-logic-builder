# Export API Functions

The Export API provides functions for managing export operations, generating export files, and handling export configurations within EPMware.

**Package**: `EW_EXPORT`  
**Usage**: `ew_export.<function_name>`

## Overview

The Export API enables:
- Export file generation
- Export configuration management
- Format handling
- Export scheduling
- File distribution
- Export status tracking

## Export Operations

### run_export

Executes an export based on configuration.

```sql
FUNCTION run_export(
  p_export_name IN VARCHAR2,
  p_parameters  IN VARCHAR2 DEFAULT NULL
) RETURN NUMBER;  -- Returns export_id
```

**Example:**
```sql
DECLARE
  l_export_id NUMBER;
BEGIN
  l_export_id := ew_export.run_export(
    p_export_name => 'DAILY_METADATA_EXPORT',
    p_parameters  => 'APP_NAME=HFM_PROD;FORMAT=CSV'
  );
  
  DBMS_OUTPUT.PUT_LINE('Export started with ID: ' || l_export_id);
END;
```

### run_export_async

Runs export asynchronously.

```sql
FUNCTION run_export_async(
  p_export_name IN VARCHAR2,
  p_parameters  IN VARCHAR2 DEFAULT NULL,
  p_callback    IN VARCHAR2 DEFAULT NULL
) RETURN NUMBER;  -- Returns job_id
```

### get_export_status

Returns the status of an export operation.

```sql
FUNCTION get_export_status(
  p_export_id IN NUMBER
) RETURN VARCHAR2;  -- Returns 'RUNNING', 'COMPLETED', 'FAILED', etc.
```

**Example:**
```sql
DECLARE
  l_status VARCHAR2(50);
  l_export_id NUMBER := 12345;
BEGIN
  LOOP
    l_status := ew_export.get_export_status(p_export_id => l_export_id);
    
    EXIT WHEN l_status IN ('COMPLETED', 'FAILED');
    
    DBMS_OUTPUT.PUT_LINE('Export status: ' || l_status);
    DBMS_LOCK.sleep(5);  -- Wait 5 seconds
  END LOOP;
  
  DBMS_OUTPUT.PUT_LINE('Final status: ' || l_status);
END;
```

## Export Configuration

### create_export_config

Creates a new export configuration.

```sql
PROCEDURE create_export_config(
  p_export_name   IN VARCHAR2,
  p_export_type   IN VARCHAR2,  -- 'METADATA', 'DATA', 'BOTH'
  p_app_name      IN VARCHAR2,
  p_format        IN VARCHAR2,  -- 'CSV', 'XML', 'JSON', 'EXCEL'
  p_parameters    IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  ew_export.create_export_config(
    p_export_name => 'ACCOUNT_HIERARCHY_EXPORT',
    p_export_type => 'METADATA',
    p_app_name    => 'HFM_PROD',
    p_format      => 'CSV',
    p_parameters  => 'DIMENSION=Account;INCLUDE_PROPERTIES=Y'
  );
  
  DBMS_OUTPUT.PUT_LINE('Export configuration created');
END;
```

### update_export_config

Updates existing export configuration.

```sql
PROCEDURE update_export_config(
  p_export_name   IN VARCHAR2,
  p_export_type   IN VARCHAR2 DEFAULT NULL,
  p_format        IN VARCHAR2 DEFAULT NULL,
  p_parameters    IN VARCHAR2 DEFAULT NULL
);
```

### delete_export_config

Deletes an export configuration.

```sql
PROCEDURE delete_export_config(
  p_export_name IN VARCHAR2
);
```

### get_export_config

Retrieves export configuration details.

```sql
FUNCTION get_export_config(
  p_export_name IN VARCHAR2
) RETURN export_config_rec;
```

**Record Structure:**
```sql
TYPE export_config_rec IS RECORD (
  export_name     VARCHAR2(100),
  export_type     VARCHAR2(50),
  app_name        VARCHAR2(100),
  format          VARCHAR2(20),
  parameters      VARCHAR2(4000),
  schedule        VARCHAR2(100),
  enabled         VARCHAR2(1),
  last_run_date   DATE,
  created_date    DATE
);
```

## File Management

### get_export_file

Retrieves the export file path/content.

```sql
FUNCTION get_export_file(
  p_export_id IN NUMBER
) RETURN VARCHAR2;  -- Returns file path
```

### get_export_file_content

Retrieves export file content as CLOB.

```sql
FUNCTION get_export_file_content(
  p_export_id IN NUMBER
) RETURN CLOB;
```

**Example:**
```sql
DECLARE
  l_content CLOB;
BEGIN
  l_content := ew_export.get_export_file_content(p_export_id => 12345);
  
  -- Process or save content
  save_clob_to_file(
    p_directory => 'EXPORT_DIR',
    p_filename  => 'export_12345.csv',
    p_clob      => l_content
  );
END;
```

### delete_export_file

Deletes an export file.

```sql
PROCEDURE delete_export_file(
  p_export_id IN NUMBER
);
```

## Export Scheduling

### schedule_export

Schedules an export to run periodically.

```sql
PROCEDURE schedule_export(
  p_export_name   IN VARCHAR2,
  p_schedule_name IN VARCHAR2,
  p_frequency     IN VARCHAR2,  -- 'DAILY', 'WEEKLY', 'MONTHLY'
  p_start_date    IN DATE DEFAULT SYSDATE,
  p_parameters    IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  -- Schedule daily export at 2 AM
  ew_export.schedule_export(
    p_export_name   => 'DAILY_METADATA_EXPORT',
    p_schedule_name => 'DAILY_2AM',
    p_frequency     => 'DAILY',
    p_start_date    => TRUNC(SYSDATE) + 1 + 2/24,  -- Tomorrow 2 AM
    p_parameters    => 'SEND_EMAIL=Y;RECIPIENTS=admin@company.com'
  );
END;
```

### unschedule_export

Removes export schedule.

```sql
PROCEDURE unschedule_export(
  p_schedule_name IN VARCHAR2
);
```

### get_scheduled_exports

Returns list of scheduled exports.

```sql
FUNCTION get_scheduled_exports
RETURN scheduled_export_tbl;
```

## Export Formats

### set_export_format_options

Sets format-specific options.

```sql
PROCEDURE set_export_format_options(
  p_export_name IN VARCHAR2,
  p_format      IN VARCHAR2,
  p_options     IN VARCHAR2
);
```

**Example:**
```sql
BEGIN
  -- CSV format options
  ew_export.set_export_format_options(
    p_export_name => 'ACCOUNT_EXPORT',
    p_format      => 'CSV',
    p_options     => 'DELIMITER=|;HEADER=Y;QUOTE_CHAR="'
  );
  
  -- Excel format options
  ew_export.set_export_format_options(
    p_export_name => 'HIERARCHY_EXPORT',
    p_format      => 'EXCEL',
    p_options     => 'SHEET_NAME=Hierarchy;AUTO_FILTER=Y'
  );
  
  -- XML format options
  ew_export.set_export_format_options(
    p_export_name => 'METADATA_EXPORT',
    p_format      => 'XML',
    p_options     => 'ROOT_ELEMENT=metadata;INCLUDE_SCHEMA=Y'
  );
END;
```

## Export Filters

### add_export_filter

Adds filter criteria to export.

```sql
PROCEDURE add_export_filter(
  p_export_name   IN VARCHAR2,
  p_filter_name   IN VARCHAR2,
  p_filter_type   IN VARCHAR2,  -- 'INCLUDE', 'EXCLUDE'
  p_filter_value  IN VARCHAR2
);
```

**Example:**
```sql
BEGIN
  -- Include only active members
  ew_export.add_export_filter(
    p_export_name  => 'MEMBER_EXPORT',
    p_filter_name  => 'ACTIVE_ONLY',
    p_filter_type  => 'INCLUDE',
    p_filter_value => 'STATUS=ACTIVE'
  );
  
  -- Exclude temporary members
  ew_export.add_export_filter(
    p_export_name  => 'MEMBER_EXPORT',
    p_filter_name  => 'NO_TEMP',
    p_filter_type  => 'EXCLUDE',
    p_filter_value => 'MEMBER_NAME LIKE ''TEMP%'''
  );
END;
```

### remove_export_filter

Removes filter from export.

```sql
PROCEDURE remove_export_filter(
  p_export_name IN VARCHAR2,
  p_filter_name IN VARCHAR2
);
```

## Export History

### get_export_history

Returns export execution history.

```sql
FUNCTION get_export_history(
  p_export_name IN VARCHAR2,
  p_start_date  IN DATE DEFAULT NULL,
  p_end_date    IN DATE DEFAULT NULL
) RETURN export_history_tbl;
```

**Example:**
```sql
DECLARE
  l_history ew_export.export_history_tbl;
BEGIN
  -- Get last 30 days history
  l_history := ew_export.get_export_history(
    p_export_name => 'DAILY_EXPORT',
    p_start_date  => SYSDATE - 30,
    p_end_date    => SYSDATE
  );
  
  FOR i IN 1..l_history.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(
      l_history(i).export_date || ' - ' ||
      l_history(i).status || ' (' ||
      l_history(i).record_count || ' records)'
    );
  END LOOP;
END;
```

### get_export_statistics

Returns export performance statistics.

```sql
FUNCTION get_export_statistics(
  p_export_name IN VARCHAR2
) RETURN export_stats_rec;
```

**Record Structure:**
```sql
TYPE export_stats_rec IS RECORD (
  total_runs        NUMBER,
  successful_runs   NUMBER,
  failed_runs      NUMBER,
  avg_duration_sec  NUMBER,
  avg_record_count  NUMBER,
  last_run_date    DATE,
  last_status      VARCHAR2(50)
);
```

## Advanced Export Features

### Incremental Export

```sql
DECLARE
  l_export_id NUMBER;
  l_last_export_date DATE;
BEGIN
  -- Get last successful export date
  SELECT MAX(export_date)
    INTO l_last_export_date
    FROM export_history
   WHERE export_name = 'INCREMENTAL_EXPORT'
     AND status = 'SUCCESS';
  
  -- Run incremental export
  l_export_id := ew_export.run_export(
    p_export_name => 'INCREMENTAL_EXPORT',
    p_parameters  => 'FROM_DATE=' || 
                     TO_CHAR(l_last_export_date, 'YYYY-MM-DD')
  );
END;
```

### Multi-Format Export

```sql
DECLARE
  l_formats ew_global.g_value_tbl;
  l_export_id NUMBER;
BEGIN
  l_formats(1) := 'CSV';
  l_formats(2) := 'XML';
  l_formats(3) := 'JSON';
  
  FOR i IN 1..l_formats.COUNT LOOP
    l_export_id := ew_export.run_export(
      p_export_name => 'METADATA_EXPORT',
      p_parameters  => 'FORMAT=' || l_formats(i)
    );
    
    DBMS_OUTPUT.PUT_LINE('Export ' || l_formats(i) || 
                         ' started: ' || l_export_id);
  END LOOP;
END;
```

### Export with Compression

```sql
BEGIN
  -- Configure export with compression
  ew_export.set_export_option(
    p_export_name => 'LARGE_EXPORT',
    p_option_name => 'COMPRESS',
    p_option_value => 'ZIP'
  );
  
  -- Set compression level
  ew_export.set_export_option(
    p_export_name => 'LARGE_EXPORT',
    p_option_name => 'COMPRESSION_LEVEL',
    p_option_value => '9'  -- Maximum compression
  );
END;
```

## Export Distribution

### distribute_export

Distributes export file to destinations.

```sql
PROCEDURE distribute_export(
  p_export_id     IN NUMBER,
  p_distribution  IN VARCHAR2  -- 'EMAIL', 'FTP', 'NETWORK', 'CLOUD'
);
```

**Example:**
```sql
DECLARE
  l_export_id NUMBER;
BEGIN
  -- Run export
  l_export_id := ew_export.run_export('WEEKLY_REPORT');
  
  -- Wait for completion
  WHILE ew_export.get_export_status(l_export_id) = 'RUNNING' LOOP
    DBMS_LOCK.sleep(5);
  END LOOP;
  
  -- Distribute via email
  ew_export.distribute_export(
    p_export_id    => l_export_id,
    p_distribution => 'EMAIL'
  );
  
  -- Distribute to network share
  ew_export.distribute_export(
    p_export_id    => l_export_id,
    p_distribution => 'NETWORK'
  );
END;
```

## Error Handling

```sql
BEGIN
  l_export_id := ew_export.run_export('INVALID_EXPORT');
EXCEPTION
  WHEN ew_export.export_not_found THEN
    DBMS_OUTPUT.PUT_LINE('Export configuration not found');
  WHEN ew_export.export_already_running THEN
    DBMS_OUTPUT.PUT_LINE('Export is already running');
  WHEN ew_export.invalid_format THEN
    DBMS_OUTPUT.PUT_LINE('Invalid export format specified');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Export error: ' || SQLERRM);
END;
```

## Best Practices

1. **Check Export Status**
   ```sql
   -- Wait for export completion
   WHILE ew_export.get_export_status(l_export_id) IN ('RUNNING', 'PENDING') LOOP
     DBMS_LOCK.sleep(10);
   END LOOP;
   ```

2. **Use Appropriate Format**
   ```sql
   -- Choose format based on use case
   -- CSV for data analysis
   -- XML for system integration
   -- JSON for web services
   ```

3. **Implement Error Recovery**
   ```sql
   -- Retry failed exports
   IF get_export_status(l_export_id) = 'FAILED' THEN
     l_export_id := run_export(p_export_name, p_parameters);
   END IF;
   ```

4. **Clean Up Old Exports**
   ```sql
   -- Delete exports older than retention period
   ew_export.cleanup_old_exports(p_days_to_keep => 30);
   ```

## Next Steps

- [Agent APIs](agent.md)
- [Appendices](../../appendices/)
- [API Overview](../)