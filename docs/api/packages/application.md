# Application API Functions

The Application API provides functions for managing EPMware applications, including retrieval of application metadata, configuration, and properties.

**Package**: `EW_APPLICATION`  
**Usage**: `ew_application.<function_name>`

## Overview

The Application API enables:
- Application information retrieval
- Dimension management
- Application properties
- Configuration settings
- Application status management

## Application Information

### get_app_id

Returns the application ID for a given application name.

```sql
FUNCTION get_app_id(
  p_app_name IN VARCHAR2
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_app_id NUMBER;
BEGIN
  l_app_id := ew_application.get_app_id(
    p_app_name => 'HFM_PROD'
  );
  DBMS_OUTPUT.PUT_LINE('Application ID: ' || l_app_id);
END;
```

### get_app_name

Returns the application name for a given application ID.

```sql
FUNCTION get_app_name(
  p_app_id IN NUMBER
) RETURN VARCHAR2;
```

### get_app_info

Returns complete application information.

```sql
FUNCTION get_app_info(
  p_app_id IN NUMBER
) RETURN app_info_rec;
```

**Record Structure:**
```sql
TYPE app_info_rec IS RECORD (
  app_id          NUMBER,
  app_name        VARCHAR2(100),
  app_type        VARCHAR2(50),
  description     VARCHAR2(255),
  status          VARCHAR2(20),
  environment     VARCHAR2(50),
  version         VARCHAR2(50),
  created_date    DATE,
  last_updated    DATE
);
```

**Example:**
```sql
DECLARE
  l_app_info ew_application.app_info_rec;
BEGIN
  l_app_info := ew_application.get_app_info(p_app_id => 100);
  
  DBMS_OUTPUT.PUT_LINE('Application: ' || l_app_info.app_name);
  DBMS_OUTPUT.PUT_LINE('Type: ' || l_app_info.app_type);
  DBMS_OUTPUT.PUT_LINE('Status: ' || l_app_info.status);
  DBMS_OUTPUT.PUT_LINE('Environment: ' || l_app_info.environment);
END;
```

### get_app_type

Returns the application type (HFM, PLANNING, ESSBASE, etc.).

```sql
FUNCTION get_app_type(
  p_app_name IN VARCHAR2
) RETURN VARCHAR2;
```

## Application Status

### is_app_active

Checks if an application is active.

```sql
FUNCTION is_app_active(
  p_app_id IN NUMBER
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
IF ew_application.is_app_active(p_app_id => 100) = 'Y' THEN
  -- Process active application
  process_application();
ELSE
  DBMS_OUTPUT.PUT_LINE('Application is inactive');
END IF;
```

### set_app_status

Updates the application status.

```sql
PROCEDURE set_app_status(
  p_app_id IN NUMBER,
  p_status IN VARCHAR2  -- 'ACTIVE', 'INACTIVE', 'MAINTENANCE'
);
```

## Dimension Management

### get_app_dimensions

Returns all dimensions for an application.

```sql
FUNCTION get_app_dimensions(
  p_app_id IN NUMBER
) RETURN dimension_tbl;
```

**Example:**
```sql
DECLARE
  l_dimensions ew_application.dimension_tbl;
BEGIN
  l_dimensions := ew_application.get_app_dimensions(p_app_id => 100);
  
  FOR i IN 1..l_dimensions.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('Dimension: ' || l_dimensions(i).dimension_name ||
                         ' Type: ' || l_dimensions(i).dimension_type);
  END LOOP;
END;
```

### get_app_dimension_id

Returns the app_dimension_id for a specific dimension.

```sql
FUNCTION get_app_dimension_id(
  p_app_name IN VARCHAR2,
  p_dim_name IN VARCHAR2
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_app_dim_id NUMBER;
BEGIN
  l_app_dim_id := ew_application.get_app_dimension_id(
    p_app_name => 'HFM_PROD',
    p_dim_name => 'Account'
  );
  
  -- Use for other operations
  process_dimension(l_app_dim_id);
END;
```

### dimension_exists

Checks if a dimension exists in an application.

```sql
FUNCTION dimension_exists(
  p_app_id   IN NUMBER,
  p_dim_name IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

## Application Properties

### get_app_property

Retrieves an application property value.

```sql
FUNCTION get_app_property(
  p_app_id        IN NUMBER,
  p_property_name IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_currency VARCHAR2(10);
  l_fiscal_start VARCHAR2(20);
BEGIN
  l_currency := ew_application.get_app_property(
    p_app_id        => 100,
    p_property_name => 'DEFAULT_CURRENCY'
  );
  
  l_fiscal_start := ew_application.get_app_property(
    p_app_id        => 100,
    p_property_name => 'FISCAL_YEAR_START'
  );
  
  DBMS_OUTPUT.PUT_LINE('Currency: ' || l_currency);
  DBMS_OUTPUT.PUT_LINE('Fiscal Year Start: ' || l_fiscal_start);
END;
```

### set_app_property

Updates an application property value.

```sql
PROCEDURE set_app_property(
  p_app_id        IN NUMBER,
  p_property_name IN VARCHAR2,
  p_property_value IN VARCHAR2
);
```

### get_all_app_properties

Returns all properties for an application.

```sql
FUNCTION get_all_app_properties(
  p_app_id IN NUMBER
) RETURN ew_global.g_name_value_tbl;
```

## Application Lists

### get_active_applications

Returns list of all active applications.

```sql
FUNCTION get_active_applications
RETURN app_list_tbl;
```

**Example:**
```sql
DECLARE
  l_apps ew_application.app_list_tbl;
BEGIN
  l_apps := ew_application.get_active_applications();
  
  DBMS_OUTPUT.PUT_LINE('Active Applications:');
  FOR i IN 1..l_apps.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('  ' || l_apps(i).app_name || 
                         ' (' || l_apps(i).app_type || ')');
  END LOOP;
END;
```

### get_applications_by_type

Returns applications of a specific type.

```sql
FUNCTION get_applications_by_type(
  p_app_type IN VARCHAR2  -- 'HFM', 'PLANNING', 'ESSBASE', etc.
) RETURN app_list_tbl;
```

### get_user_applications

Returns applications accessible to a specific user.

```sql
FUNCTION get_user_applications(
  p_user_name IN VARCHAR2 DEFAULT USER
) RETURN app_list_tbl;
```

## Application Configuration

### get_app_connection_info

Returns connection information for an application.

```sql
FUNCTION get_app_connection_info(
  p_app_id IN NUMBER
) RETURN connection_info_rec;
```

**Record Structure:**
```sql
TYPE connection_info_rec IS RECORD (
  server_name     VARCHAR2(255),
  server_port     NUMBER,
  database_name   VARCHAR2(100),
  connection_type VARCHAR2(50),
  url            VARCHAR2(500)
);
```

### refresh_app_metadata

Refreshes application metadata cache.

```sql
PROCEDURE refresh_app_metadata(
  p_app_id IN NUMBER
);
```

**Example:**
```sql
BEGIN
  -- Refresh metadata after changes
  ew_application.refresh_app_metadata(p_app_id => 100);
  COMMIT;
  DBMS_OUTPUT.PUT_LINE('Metadata refreshed successfully');
EXCEPTION
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Refresh failed: ' || SQLERRM);
END;
```

## Application Utilities

### copy_application_config

Copies configuration from one application to another.

```sql
PROCEDURE copy_application_config(
  p_source_app_id IN NUMBER,
  p_target_app_id IN NUMBER,
  p_include_security IN VARCHAR2 DEFAULT 'N'
);
```

### export_app_metadata

Exports application metadata to XML.

```sql
FUNCTION export_app_metadata(
  p_app_id IN NUMBER,
  p_include_data IN VARCHAR2 DEFAULT 'N'
) RETURN CLOB;
```

**Example:**
```sql
DECLARE
  l_metadata CLOB;
BEGIN
  l_metadata := ew_application.export_app_metadata(
    p_app_id       => 100,
    p_include_data => 'N'
  );
  
  -- Save to file
  save_clob_to_file(
    p_directory => 'EXPORT_DIR',
    p_filename  => 'app_metadata.xml',
    p_clob      => l_metadata
  );
END;
```

## Advanced Features

### Application Comparison

```sql
DECLARE
  l_differences ew_global.g_value_tbl;
BEGIN
  -- Compare two applications
  l_differences := ew_application.compare_applications(
    p_app_id1 => 100,
    p_app_id2 => 101
  );
  
  IF l_differences.COUNT > 0 THEN
    DBMS_OUTPUT.PUT_LINE('Differences found:');
    FOR i IN 1..l_differences.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE('  - ' || l_differences(i));
    END LOOP;
  END IF;
END;
```

### Application Health Check

```sql
DECLARE
  l_health_status VARCHAR2(20);
  l_issues ew_global.g_value_tbl;
BEGIN
  -- Check application health
  ew_application.check_app_health(
    p_app_id => 100,
    p_status => l_health_status,
    p_issues => l_issues
  );
  
  DBMS_OUTPUT.PUT_LINE('Health Status: ' || l_health_status);
  
  IF l_issues.COUNT > 0 THEN
    DBMS_OUTPUT.PUT_LINE('Issues detected:');
    FOR i IN 1..l_issues.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE('  - ' || l_issues(i));
    END LOOP;
  END IF;
END;
```

### Multi-Application Operations

```sql
DECLARE
  l_apps ew_application.app_list_tbl;
  l_success_count NUMBER := 0;
BEGIN
  -- Get all production applications
  l_apps := ew_application.get_applications_by_environment('PRODUCTION');
  
  -- Process each application
  FOR i IN 1..l_apps.COUNT LOOP
    BEGIN
      -- Perform operation
      process_application(l_apps(i).app_id);
      l_success_count := l_success_count + 1;
    EXCEPTION
      WHEN OTHERS THEN
        log_error('Failed for ' || l_apps(i).app_name);
    END;
  END LOOP;
  
  DBMS_OUTPUT.PUT_LINE('Processed ' || l_success_count || 
                       ' of ' || l_apps.COUNT || ' applications');
END;
```

## Caching Application Data

```sql
DECLARE
  -- Cache application data
  g_app_cache ew_application.app_info_rec;
  g_cache_app_id NUMBER;
  
  FUNCTION get_cached_app_info(p_app_id NUMBER)
  RETURN ew_application.app_info_rec IS
  BEGIN
    IF g_cache_app_id IS NULL OR g_cache_app_id != p_app_id THEN
      g_app_cache := ew_application.get_app_info(p_app_id);
      g_cache_app_id := p_app_id;
    END IF;
    RETURN g_app_cache;
  END;
BEGIN
  -- Use cached data
  FOR i IN 1..100 LOOP
    l_info := get_cached_app_info(100);
  END LOOP;
END;
```

## Error Handling

```sql
BEGIN
  l_app_id := ew_application.get_app_id('INVALID_APP');
  
  IF l_app_id IS NULL THEN
    DBMS_OUTPUT.PUT_LINE('Application not found');
  END IF;
  
EXCEPTION
  WHEN ew_application.app_not_found THEN
    DBMS_OUTPUT.PUT_LINE('Application does not exist');
  WHEN ew_application.access_denied THEN
    DBMS_OUTPUT.PUT_LINE('No access to application');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
```

## Best Practices

1. **Cache Application IDs**
   ```sql
   -- Store frequently used IDs
   g_hfm_app_id := ew_application.get_app_id('HFM_PROD');
   ```

2. **Check Application Status**
   ```sql
   IF ew_application.is_app_active(p_app_id) = 'Y' THEN
     -- Process only active applications
   END IF;
   ```

3. **Use Appropriate Functions**
   ```sql
   -- Get specific property vs all properties
   l_value := get_app_property(p_app_id, 'CURRENCY');
   -- Instead of getting all and filtering
   ```

4. **Handle Missing Applications**
   ```sql
   l_app_id := NVL(get_app_id(p_app_name), 0);
   IF l_app_id > 0 THEN
     -- Process
   END IF;
   ```

## Next Steps

- [Workflow APIs](workflow.md)
- [Security APIs](security.md)
- [Agent APIs](agent.md)