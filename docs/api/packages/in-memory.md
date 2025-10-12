# In Memory Functions

The In Memory API provides session-specific temporary data storage capabilities, allowing scripts to maintain state and share data within a database session.

**Package**: `EW_IN_MEMORY`  
**Usage**: `ew_in_memory.<function_name>`

## Overview

In Memory functions enable:
- Temporary data storage during script execution
- Cross-script data sharing within a session
- Performance optimization through caching
- Reduced database I/O operations

![In Memory Storage](../../assets/images/in-memory-storage.png)
*Figure: In Memory data storage lifecycle*

## Key Functions

### Store and Retrieve Data

#### put_value

Stores a value in session memory.

```sql
PROCEDURE put_value(
  p_key   IN VARCHAR2,
  p_value IN VARCHAR2
);
```

**Parameters:**
- `p_key` - Unique identifier for the value
- `p_value` - Value to store (up to 4000 characters)

**Example:**
```sql
-- Store configuration value
ew_in_memory.put_value('BATCH_SIZE', '1000');

-- Store processing flag
ew_in_memory.put_value('PROCESSING_STATUS', 'RUNNING');

-- Store timestamp
ew_in_memory.put_value('START_TIME', TO_CHAR(SYSTIMESTAMP));
```

#### get_value

Retrieves a value from session memory.

```sql
FUNCTION get_value(
  p_key IN VARCHAR2
) RETURN VARCHAR2;
```

**Parameters:**
- `p_key` - Key to retrieve

**Returns:** Stored value or NULL if not found

**Example:**
```sql
DECLARE
  l_batch_size NUMBER;
  l_status VARCHAR2(50);
BEGIN
  l_batch_size := TO_NUMBER(ew_in_memory.get_value('BATCH_SIZE'));
  l_status := ew_in_memory.get_value('PROCESSING_STATUS');
  
  IF l_status = 'RUNNING' THEN
    -- Continue processing
    process_batch(l_batch_size);
  END IF;
END;
```

### Collection Management

#### put_collection

Stores an array/collection in memory.

```sql
PROCEDURE put_collection(
  p_key        IN VARCHAR2,
  p_collection IN ew_global.g_value_tbl
);
```

**Example:**
```sql
DECLARE
  l_members ew_global.g_value_tbl;
BEGIN
  -- Build collection
  l_members(1) := 'Account1';
  l_members(2) := 'Account2';
  l_members(3) := 'Account3';
  
  -- Store in memory
  ew_in_memory.put_collection('MEMBER_LIST', l_members);
END;
```

#### get_collection

Retrieves a collection from memory.

```sql
FUNCTION get_collection(
  p_key IN VARCHAR2
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_members ew_global.g_value_tbl;
BEGIN
  -- Retrieve collection
  l_members := ew_in_memory.get_collection('MEMBER_LIST');
  
  -- Process members
  FOR i IN 1..l_members.COUNT LOOP
    process_member(l_members(i));
  END LOOP;
END;
```

### Memory Management

#### clear_value

Removes a specific value from memory.

```sql
PROCEDURE clear_value(
  p_key IN VARCHAR2
);
```

**Example:**
```sql
-- Clear specific value
ew_in_memory.clear_value('TEMP_DATA');
```

#### clear_all

Clears all values from session memory.

```sql
PROCEDURE clear_all;
```

**Example:**
```sql
-- Clear all session data
BEGIN
  -- Process complete, clean up
  ew_in_memory.clear_all;
END;
```

#### exists_value

Checks if a key exists in memory.

```sql
FUNCTION exists_value(
  p_key IN VARCHAR2
) RETURN VARCHAR2; -- Returns 'Y' or 'N'
```

**Example:**
```sql
IF ew_in_memory.exists_value('CONFIG_LOADED') = 'N' THEN
  -- Load configuration
  load_configuration();
  ew_in_memory.put_value('CONFIG_LOADED', 'Y');
END IF;
```

## Advanced Features

### Structured Data Storage

Store complex data structures using delimiters:

```sql
DECLARE
  l_config VARCHAR2(4000);
BEGIN
  -- Store multiple values as delimited string
  l_config := 'BATCH_SIZE=1000|PARALLEL=Y|TIMEOUT=300';
  ew_in_memory.put_value('JOB_CONFIG', l_config);
  
  -- Parse when retrieving
  l_config := ew_in_memory.get_value('JOB_CONFIG');
  parse_config(l_config);
END;
```

### Counter Management

Implement counters for tracking:

```sql
-- Initialize counter
PROCEDURE init_counter(p_name VARCHAR2) IS
BEGIN
  ew_in_memory.put_value(p_name || '_COUNTER', '0');
END;

-- Increment counter
PROCEDURE increment_counter(p_name VARCHAR2) IS
  l_count NUMBER;
BEGIN
  l_count := NVL(TO_NUMBER(ew_in_memory.get_value(p_name || '_COUNTER')), 0);
  l_count := l_count + 1;
  ew_in_memory.put_value(p_name || '_COUNTER', TO_CHAR(l_count));
END;

-- Get counter value
FUNCTION get_counter(p_name VARCHAR2) RETURN NUMBER IS
BEGIN
  RETURN NVL(TO_NUMBER(ew_in_memory.get_value(p_name || '_COUNTER')), 0);
END;
```

### Cache Implementation

Use in-memory storage for caching:

```sql
DECLARE
  c_cache_key VARCHAR2(100) := 'DIM_' || p_dimension_id;
  l_dim_name VARCHAR2(100);
BEGIN
  -- Check cache first
  l_dim_name := ew_in_memory.get_value(c_cache_key);
  
  IF l_dim_name IS NULL THEN
    -- Not in cache, fetch from database
    SELECT dimension_name
      INTO l_dim_name
      FROM dimensions
     WHERE dimension_id = p_dimension_id;
    
    -- Store in cache
    ew_in_memory.put_value(c_cache_key, l_dim_name);
  END IF;
  
  RETURN l_dim_name;
END;
```

## Common Use Cases

### 1. Processing State Management

Track multi-step process state:

```sql
DECLARE
  l_current_step VARCHAR2(50);
BEGIN
  -- Initialize process
  ew_in_memory.put_value('PROCESS_ID', '12345');
  ew_in_memory.put_value('CURRENT_STEP', 'VALIDATION');
  ew_in_memory.put_value('ERROR_COUNT', '0');
  
  -- Step 1: Validation
  validate_data();
  ew_in_memory.put_value('CURRENT_STEP', 'TRANSFORMATION');
  
  -- Step 2: Transformation
  transform_data();
  ew_in_memory.put_value('CURRENT_STEP', 'LOADING');
  
  -- Step 3: Loading
  load_data();
  ew_in_memory.put_value('CURRENT_STEP', 'COMPLETE');
  
EXCEPTION
  WHEN OTHERS THEN
    l_current_step := ew_in_memory.get_value('CURRENT_STEP');
    log_error('Process failed at step: ' || l_current_step);
    RAISE;
END;
```

### 2. Batch Processing

Manage batch processing parameters:

```sql
DECLARE
  l_batch_size NUMBER;
  l_batch_num NUMBER;
  l_total_processed NUMBER;
BEGIN
  -- Initialize batch parameters
  ew_in_memory.put_value('BATCH_SIZE', '1000');
  ew_in_memory.put_value('BATCH_NUM', '1');
  ew_in_memory.put_value('TOTAL_PROCESSED', '0');
  
  -- Process batches
  LOOP
    l_batch_num := TO_NUMBER(ew_in_memory.get_value('BATCH_NUM'));
    l_batch_size := TO_NUMBER(ew_in_memory.get_value('BATCH_SIZE'));
    
    -- Process batch
    process_batch(l_batch_num, l_batch_size);
    
    -- Update counters
    l_total_processed := TO_NUMBER(ew_in_memory.get_value('TOTAL_PROCESSED'));
    l_total_processed := l_total_processed + l_batch_size;
    ew_in_memory.put_value('TOTAL_PROCESSED', TO_CHAR(l_total_processed));
    
    -- Next batch
    ew_in_memory.put_value('BATCH_NUM', TO_CHAR(l_batch_num + 1));
    
    EXIT WHEN no_more_data;
  END LOOP;
  
  -- Report results
  DBMS_OUTPUT.PUT_LINE('Total processed: ' || 
                       ew_in_memory.get_value('TOTAL_PROCESSED'));
END;
```

### 3. Error Collection

Accumulate errors during processing:

```sql
DECLARE
  l_errors ew_global.g_value_tbl;
  l_error_count NUMBER := 0;
  
  PROCEDURE add_error(p_error VARCHAR2) IS
    l_errors ew_global.g_value_tbl;
  BEGIN
    -- Get existing errors
    IF ew_in_memory.exists_value('ERROR_LIST') = 'Y' THEN
      l_errors := ew_in_memory.get_collection('ERROR_LIST');
    END IF;
    
    -- Add new error
    l_errors(l_errors.COUNT + 1) := p_error;
    
    -- Store back
    ew_in_memory.put_collection('ERROR_LIST', l_errors);
  END;
  
BEGIN
  -- Process with error collection
  FOR rec IN (SELECT * FROM data_to_process) LOOP
    BEGIN
      process_record(rec);
    EXCEPTION
      WHEN OTHERS THEN
        add_error('Record ' || rec.id || ': ' || SQLERRM);
    END;
  END LOOP;
  
  -- Check for errors
  IF ew_in_memory.exists_value('ERROR_LIST') = 'Y' THEN
    l_errors := ew_in_memory.get_collection('ERROR_LIST');
    
    -- Report errors
    FOR i IN 1..l_errors.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE('Error: ' || l_errors(i));
    END LOOP;
  END IF;
END;
```

### 4. Configuration Cache

Cache configuration values:

```sql
DECLARE
  FUNCTION get_config_value(p_param VARCHAR2) RETURN VARCHAR2 IS
    l_cache_key VARCHAR2(100) := 'CONFIG_' || p_param;
    l_value VARCHAR2(4000);
  BEGIN
    -- Check cache
    l_value := ew_in_memory.get_value(l_cache_key);
    
    IF l_value IS NULL THEN
      -- Load from database
      SELECT param_value
        INTO l_value
        FROM config_table
       WHERE param_name = p_param;
      
      -- Cache it
      ew_in_memory.put_value(l_cache_key, l_value);
    END IF;
    
    RETURN l_value;
  END;
  
BEGIN
  -- Use cached config values
  IF get_config_value('ENABLE_VALIDATION') = 'Y' THEN
    validate_data();
  END IF;
  
  IF get_config_value('SEND_NOTIFICATIONS') = 'Y' THEN
    send_notifications();
  END IF;
END;
```

## Performance Considerations

### Memory Limits

- Maximum value size: 4000 characters
- Maximum collection size: 32767 elements
- Total session memory: Database dependent

### Best Practices

1. **Clear Unused Data**
   ```sql
   -- Clear as soon as no longer needed
   ew_in_memory.clear_value('TEMP_DATA');
   ```

2. **Use Meaningful Keys**
   ```sql
   -- Good: Descriptive keys
   ew_in_memory.put_value('VALIDATION_ERROR_COUNT', '5');
   
   -- Bad: Cryptic keys
   ew_in_memory.put_value('VEC', '5');
   ```

3. **Check Existence Before Access**
   ```sql
   IF ew_in_memory.exists_value('CONFIG') = 'Y' THEN
     l_config := ew_in_memory.get_value('CONFIG');
   ELSE
     l_config := load_default_config();
   END IF;
   ```

4. **Handle Type Conversions**
   ```sql
   -- Safe number conversion
   l_count := NVL(TO_NUMBER(ew_in_memory.get_value('COUNT')), 0);
   
   -- Safe date conversion
   l_date := TO_DATE(ew_in_memory.get_value('PROCESS_DATE'), 
                     'YYYY-MM-DD HH24:MI:SS');
   ```

## Limitations

### Session Scope

- Data exists only within database session
- Lost on disconnect or session timeout
- Not shared between sessions

### Data Types

- Only VARCHAR2 storage
- Must convert other types
- Size limited to 4000 characters

### No Persistence

- Data not saved to database
- Lost after session ends
- Not included in commits/rollbacks

## Error Handling

```sql
DECLARE
  l_value VARCHAR2(4000);
BEGIN
  -- Safe retrieval with error handling
  BEGIN
    l_value := ew_in_memory.get_value('KEY');
  EXCEPTION
    WHEN OTHERS THEN
      -- Key might not exist
      l_value := 'DEFAULT';
  END;
  
  -- Safe storage with size check
  IF LENGTH(p_large_value) <= 4000 THEN
    ew_in_memory.put_value('KEY', p_large_value);
  ELSE
    -- Split large values
    ew_in_memory.put_value('KEY_1', SUBSTR(p_large_value, 1, 4000));
    ew_in_memory.put_value('KEY_2', SUBSTR(p_large_value, 4001));
  END IF;
END;
```

## Next Steps

- [Hierarchy APIs](hierarchy.md)
- [Request APIs](request.md)
- [String APIs](string.md)