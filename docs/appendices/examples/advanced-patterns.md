# Advanced Pattern Examples

This section demonstrates sophisticated Logic Builder scripting patterns for complex scenarios, performance optimization, error recovery, and enterprise-scale implementations.

## Bulk Processing with Batch Optimization

🔴 **Level:** Advanced  
**Purpose:** Process large volumes of members efficiently using batch techniques

```sql
/*
  Script: BULK_PROCESS_OPTIMIZATION
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Efficiently process large member sets with batch optimization
  
  Features:
  - Batch processing with configurable size
  - Progress tracking
  - Error recovery per batch
  - Performance monitoring
  - Memory management
*/
DECLARE
  c_script_name    VARCHAR2(100) := 'BULK_PROCESS_OPTIMIZATION';
  c_batch_size     CONSTANT NUMBER := 1000;
  c_commit_interval CONSTANT NUMBER := 5000;
  
  v_total_members   NUMBER;
  v_processed       NUMBER := 0;
  v_batch_count     NUMBER := 0;
  v_errors          NUMBER := 0;
  v_start_time      TIMESTAMP;
  v_batch_start     TIMESTAMP;
  
  -- Bulk collection types
  TYPE t_member_list IS TABLE OF VARCHAR2(100);
  TYPE t_property_list IS TABLE OF VARCHAR2(500);
  TYPE t_number_list IS TABLE OF NUMBER;
  
  v_members         t_member_list;
  v_properties      t_property_list;
  v_results         t_number_list;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  PROCEDURE log_performance(p_operation IN VARCHAR2,
                           p_count      IN NUMBER,
                           p_start_time IN TIMESTAMP) IS
    v_duration NUMBER;
  BEGIN
    v_duration := EXTRACT(SECOND FROM (SYSTIMESTAMP - p_start_time));
    log(p_operation || ': Processed ' || p_count || 
        ' records in ' || ROUND(v_duration, 2) || ' seconds. ' ||
        'Rate: ' || ROUND(p_count / NULLIF(v_duration, 0), 0) || ' rec/sec');
  END log_performance;
  
  PROCEDURE process_batch(p_members IN t_member_list) IS
    v_batch_errors NUMBER := 0;
  BEGIN
    v_batch_start := SYSTIMESTAMP;
    
    -- Bulk collect properties for all members in batch
    FORALL i IN 1..p_members.COUNT SAVE EXCEPTIONS
      UPDATE ew_member_properties
      SET    prop_value = CASE
               WHEN prop_name = 'ProcessedDate' THEN TO_CHAR(SYSDATE, 'YYYY-MM-DD')
               WHEN prop_name = 'Status' THEN 'Processed'
               WHEN prop_name = 'BatchId' THEN TO_CHAR(v_batch_count)
               ELSE prop_value
             END,
             last_modified = SYSDATE,
             modified_by = 'BULK_PROCESS'
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = p_members(i)
      AND    prop_name IN ('ProcessedDate', 'Status', 'BatchId');
    
    -- Handle exceptions
    IF SQL%BULK_EXCEPTIONS.COUNT > 0 THEN
      FOR i IN 1..SQL%BULK_EXCEPTIONS.COUNT LOOP
        v_batch_errors := v_batch_errors + 1;
        log('Error in batch at position ' || 
            SQL%BULK_EXCEPTIONS(i).ERROR_INDEX || ': ' ||
            SQLERRM(-SQL%BULK_EXCEPTIONS(i).ERROR_CODE));
      END LOOP;
    END IF;
    
    v_errors := v_errors + v_batch_errors;
    
    log_performance('Batch ' || v_batch_count, 
                   p_members.COUNT - v_batch_errors, 
                   v_batch_start);
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Batch processing error: ' || SQLERRM);
      v_errors := v_errors + p_members.COUNT;
  END process_batch;
  
  PROCEDURE optimize_memory IS
    v_pga_used NUMBER;
  BEGIN
    -- Check PGA usage
    SELECT value/1024/1024 INTO v_pga_used
    FROM   v$mystat m, v$statname s
    WHERE  m.statistic# = s.statistic#
    AND    s.name = 'session pga memory';
    
    log('Current PGA usage: ' || ROUND(v_pga_used, 2) || ' MB');
    
    -- Force garbage collection if memory usage is high
    IF v_pga_used > 100 THEN
      DBMS_SESSION.FREE_UNUSED_USER_MEMORY;
      log('Memory optimization performed');
    END IF;
    
  END optimize_memory;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  v_start_time := SYSTIMESTAMP;
  
  log('Starting bulk processing');
  
  -- Get total count
  SELECT COUNT(*)
  INTO   v_total_members
  FROM   ew_hierarchy
  WHERE  app_id = ew_lb_api.g_app_id
  AND    dim_id = ew_lb_api.g_dim_id
  AND    member_level = 0; -- Leaf members only
  
  log('Total members to process: ' || v_total_members);
  
  -- Process in batches using cursor
  DECLARE
    CURSOR c_members IS
      SELECT member_name
      FROM   ew_hierarchy
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_level = 0
      ORDER BY member_name; -- Ordered for consistent processing
  BEGIN
    OPEN c_members;
    
    LOOP
      -- Fetch batch
      FETCH c_members BULK COLLECT INTO v_members LIMIT c_batch_size;
      
      EXIT WHEN v_members.COUNT = 0;
      
      v_batch_count := v_batch_count + 1;
      
      -- Process batch
      process_batch(v_members);
      
      v_processed := v_processed + v_members.COUNT;
      
      -- Progress reporting
      IF MOD(v_processed, c_commit_interval) = 0 THEN
        COMMIT;
        log('Progress: ' || v_processed || '/' || v_total_members || 
            ' (' || ROUND(v_processed * 100 / v_total_members, 1) || '%)');
        
        -- Memory optimization
        optimize_memory();
      END IF;
      
      -- Clear collections
      v_members.DELETE;
      
    END LOOP;
    
    CLOSE c_members;
  END;
  
  -- Final commit
  COMMIT;
  
  -- Log summary
  log_performance('Total processing', v_processed, v_start_time);
  
  IF v_errors > 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Processed ' || v_processed || 
                          ' members with ' || v_errors || ' errors';
  ELSE
    ew_lb_api.g_message := 'Successfully processed ' || v_processed || 
                          ' members in ' || v_batch_count || ' batches';
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Critical error: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Bulk processing failed: ' || SQLERRM;
    ROLLBACK;
END;
```

## Recursive Hierarchy Processing

🔴 **Level:** Advanced  
**Purpose:** Process hierarchies recursively with cycle detection

```sql
/*
  Script: RECURSIVE_HIERARCHY_PROCESSOR
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Recursively process hierarchy with cycle detection
  
  Features:
  - Recursive tree walking
  - Cycle detection
  - Level-based processing
  - Aggregation rollup
  - Path tracking
*/
DECLARE
  c_script_name      VARCHAR2(100) := 'RECURSIVE_HIERARCHY_PROCESSOR';
  c_max_depth        CONSTANT NUMBER := 20;
  
  TYPE t_member_path IS TABLE OF VARCHAR2(100);
  TYPE t_visited_set IS TABLE OF VARCHAR2(100) INDEX BY VARCHAR2(100);
  
  v_visited          t_visited_set;
  v_cycle_detected   BOOLEAN := FALSE;
  v_total_processed  NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION is_visited(p_member IN VARCHAR2) RETURN BOOLEAN IS
  BEGIN
    RETURN v_visited.EXISTS(p_member);
  END is_visited;
  
  PROCEDURE mark_visited(p_member IN VARCHAR2) IS
  BEGIN
    v_visited(p_member) := p_member;
  END mark_visited;
  
  PROCEDURE process_member_recursive(
    p_member_name IN VARCHAR2,
    p_level       IN NUMBER,
    p_path        IN t_member_path
  ) IS
    v_children_sum NUMBER := 0;
    v_child_count  NUMBER := 0;
    v_new_path     t_member_path;
    v_properties   VARCHAR2(4000);
  BEGIN
    -- Check max depth
    IF p_level > c_max_depth THEN
      log('Max depth reached at member: ' || p_member_name);
      RETURN;
    END IF;
    
    -- Check for cycles
    IF is_visited(p_member_name) THEN
      log('Cycle detected at member: ' || p_member_name);
      v_cycle_detected := TRUE;
      
      -- Log the cycle path
      DECLARE
        v_path_str VARCHAR2(4000);
      BEGIN
        FOR i IN 1..p_path.COUNT LOOP
          v_path_str := v_path_str || p_path(i) || ' -> ';
        END LOOP;
        v_path_str := v_path_str || p_member_name;
        log('Cycle path: ' || v_path_str);
      END;
      
      RETURN;
    END IF;
    
    -- Mark as visited
    mark_visited(p_member_name);
    
    -- Build new path
    v_new_path := p_path;
    v_new_path.EXTEND;
    v_new_path(v_new_path.COUNT) := p_member_name;
    
    -- Process current member
    log('Processing: ' || p_member_name || ' at level ' || p_level);
    
    -- Get member properties for processing
    SELECT LISTAGG(prop_name || '=' || prop_value, ',') 
           WITHIN GROUP (ORDER BY prop_name)
    INTO   v_properties
    FROM   ew_member_properties
    WHERE  app_id = ew_lb_api.g_app_id
    AND    dim_id = ew_lb_api.g_dim_id
    AND    member_name = p_member_name
    AND    prop_name IN ('Value', 'Weight', 'Factor');
    
    -- Process children recursively
    FOR child IN (SELECT member_name
                  FROM   ew_hierarchy
                  WHERE  app_id = ew_lb_api.g_app_id
                  AND    dim_id = ew_lb_api.g_dim_id
                  AND    parent_member_name = p_member_name
                  ORDER BY sort_order, member_name)
    LOOP
      v_child_count := v_child_count + 1;
      
      -- Recursive call
      process_member_recursive(
        p_member_name => child.member_name,
        p_level       => p_level + 1,
        p_path        => v_new_path
      );
      
      -- Aggregate child values (example)
      BEGIN
        SELECT TO_NUMBER(prop_value)
        INTO   v_children_sum
        FROM   ew_member_properties
        WHERE  app_id = ew_lb_api.g_app_id
        AND    dim_id = ew_lb_api.g_dim_id
        AND    member_name = child.member_name
        AND    prop_name = 'CalculatedValue';
        
        v_children_sum := v_children_sum + NVL(v_children_sum, 0);
      EXCEPTION
        WHEN OTHERS THEN
          NULL; -- Skip if no value
      END;
    END LOOP;
    
    -- Update parent with aggregated value
    IF v_child_count > 0 THEN
      UPDATE ew_member_properties
      SET    prop_value = TO_CHAR(v_children_sum),
             last_modified = SYSDATE
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = p_member_name
      AND    prop_name = 'AggregatedValue';
      
      log('Updated ' || p_member_name || ' with aggregated value: ' || 
          v_children_sum);
    END IF;
    
    v_total_processed := v_total_processed + 1;
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Error processing ' || p_member_name || ': ' || SQLERRM);
  END process_member_recursive;
  
  PROCEDURE process_hierarchy_recursive(p_root_member IN VARCHAR2) IS
    v_initial_path t_member_path := t_member_path();
  BEGIN
    log('Starting recursive processing from root: ' || p_root_member);
    
    -- Clear visited set
    v_visited.DELETE;
    v_cycle_detected := FALSE;
    
    -- Start recursive processing
    process_member_recursive(
      p_member_name => p_root_member,
      p_level       => 0,
      p_path        => v_initial_path
    );
    
    log('Recursive processing completed');
    log('Total members processed: ' || v_total_processed);
    
    IF v_cycle_detected THEN
      log('WARNING: Cycles were detected in the hierarchy');
    END IF;
    
  END process_hierarchy_recursive;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  -- Process entire dimension hierarchy
  process_hierarchy_recursive(ew_lb_api.g_dim_name);
  
  IF v_cycle_detected THEN
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Hierarchy processed with cycle warnings. ' ||
                          'Processed ' || v_total_processed || ' members.';
  ELSE
    ew_lb_api.g_message := 'Successfully processed ' || v_total_processed || 
                          ' members recursively.';
  END IF;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Critical error: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Recursive processing failed: ' || SQLERRM;
    ROLLBACK;
END;
```

## Dynamic SQL Generation and Execution

🔴 **Level:** Advanced  
**Purpose:** Generate and execute dynamic SQL based on configuration

```sql
/*
  Script: DYNAMIC_SQL_EXECUTOR
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Generate and execute dynamic SQL with safety checks
  
  Features:
  - SQL injection prevention
  - Dynamic query building
  - Bind variable handling
  - Result set processing
  - Performance monitoring
*/
DECLARE
  c_script_name      VARCHAR2(100) := 'DYNAMIC_SQL_EXECUTOR';
  c_max_sql_length   CONSTANT NUMBER := 32767;
  
  v_sql_statement    VARCHAR2(32767);
  v_where_clause     VARCHAR2(4000);
  v_bind_count       NUMBER := 0;
  v_row_count        NUMBER;
  
  TYPE t_bind_var IS RECORD (
    bind_name  VARCHAR2(30),
    bind_value VARCHAR2(4000),
    bind_type  VARCHAR2(20)
  );
  
  TYPE t_bind_vars IS TABLE OF t_bind_var;
  v_bind_vars t_bind_vars := t_bind_vars();
  
  TYPE t_result_cursor IS REF CURSOR;
  v_cursor t_result_cursor;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION sanitize_input(p_input IN VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    -- Remove SQL injection attempts
    IF REGEXP_LIKE(p_input, '(;|--|\bunion\b|\bdrop\b|\bdelete\b|\binsert\b)', 'i') THEN
      RAISE_APPLICATION_ERROR(-20001, 'Potential SQL injection detected');
    END IF;
    
    -- Escape single quotes
    RETURN REPLACE(p_input, '''', '''''');
  END sanitize_input;
  
  PROCEDURE add_bind_variable(p_name  IN VARCHAR2,
                              p_value IN VARCHAR2,
                              p_type  IN VARCHAR2 DEFAULT 'VARCHAR2') IS
  BEGIN
    v_bind_count := v_bind_count + 1;
    v_bind_vars.EXTEND;
    v_bind_vars(v_bind_count).bind_name := p_name;
    v_bind_vars(v_bind_count).bind_value := p_value;
    v_bind_vars(v_bind_count).bind_type := p_type;
    
    log('Added bind variable: ' || p_name || ' = ' || p_value);
  END add_bind_variable;
  
  FUNCTION build_dynamic_where RETURN VARCHAR2 IS
    v_where VARCHAR2(4000);
    v_conditions NUMBER := 0;
  BEGIN
    v_where := ' WHERE 1=1';
    
    -- Add conditions based on context
    IF ew_lb_api.g_app_id IS NOT NULL THEN
      v_where := v_where || ' AND app_id = :app_id';
      add_bind_variable('app_id', TO_CHAR(ew_lb_api.g_app_id), 'NUMBER');
      v_conditions := v_conditions + 1;
    END IF;
    
    IF ew_lb_api.g_dim_id IS NOT NULL THEN
      v_where := v_where || ' AND dim_id = :dim_id';
      add_bind_variable('dim_id', TO_CHAR(ew_lb_api.g_dim_id), 'NUMBER');
      v_conditions := v_conditions + 1;
    END IF;
    
    -- Add dynamic conditions from configuration
    FOR cond IN (SELECT condition_sql, bind_name, bind_value
                 FROM   ew_dynamic_conditions
                 WHERE  is_active = 'Y'
                 AND    script_name = c_script_name)
    LOOP
      v_where := v_where || ' AND ' || cond.condition_sql;
      
      IF cond.bind_name IS NOT NULL THEN
        add_bind_variable(cond.bind_name, cond.bind_value);
      END IF;
      
      v_conditions := v_conditions + 1;
    END LOOP;
    
    log('Built WHERE clause with ' || v_conditions || ' conditions');
    
    RETURN v_where;
  END build_dynamic_where;
  
  PROCEDURE execute_dynamic_sql IS
    v_cursor_id    INTEGER;
    v_exec_result  INTEGER;
  BEGIN
    log('Executing SQL: ' || SUBSTR(v_sql_statement, 1, 1000));
    
    -- Open cursor
    v_cursor_id := DBMS_SQL.OPEN_CURSOR;
    
    -- Parse statement
    DBMS_SQL.PARSE(v_cursor_id, v_sql_statement, DBMS_SQL.NATIVE);
    
    -- Bind variables
    FOR i IN 1..v_bind_vars.COUNT LOOP
      CASE v_bind_vars(i).bind_type
        WHEN 'NUMBER' THEN
          DBMS_SQL.BIND_VARIABLE(v_cursor_id, 
                                 v_bind_vars(i).bind_name,
                                 TO_NUMBER(v_bind_vars(i).bind_value));
        WHEN 'DATE' THEN
          DBMS_SQL.BIND_VARIABLE(v_cursor_id,
                                 v_bind_vars(i).bind_name,
                                 TO_DATE(v_bind_vars(i).bind_value, 'YYYY-MM-DD'));
        ELSE
          DBMS_SQL.BIND_VARIABLE(v_cursor_id,
                                 v_bind_vars(i).bind_name,
                                 v_bind_vars(i).bind_value);
      END CASE;
    END LOOP;
    
    -- Execute
    v_exec_result := DBMS_SQL.EXECUTE(v_cursor_id);
    
    v_row_count := DBMS_SQL.LAST_ROW_COUNT;
    
    log('Execution completed. Rows affected: ' || v_row_count);
    
    -- Close cursor
    DBMS_SQL.CLOSE_CURSOR(v_cursor_id);
    
  EXCEPTION
    WHEN OTHERS THEN
      IF DBMS_SQL.IS_OPEN(v_cursor_id) THEN
        DBMS_SQL.CLOSE_CURSOR(v_cursor_id);
      END IF;
      RAISE;
  END execute_dynamic_sql;
  
  PROCEDURE process_dynamic_results IS
    TYPE t_member_rec IS RECORD (
      member_name VARCHAR2(100),
      prop_value  VARCHAR2(500)
    );
    v_rec t_member_rec;
  BEGIN
    -- Build SELECT statement
    v_sql_statement := 'SELECT member_name, prop_value ' ||
                      'FROM ew_member_properties' ||
                      build_dynamic_where() ||
                      ' ORDER BY member_name';
    
    -- Execute and process results
    IF v_bind_vars.COUNT = 0 THEN
      OPEN v_cursor FOR v_sql_statement;
    ELSIF v_bind_vars.COUNT = 1 THEN
      OPEN v_cursor FOR v_sql_statement 
        USING v_bind_vars(1).bind_value;
    ELSIF v_bind_vars.COUNT = 2 THEN
      OPEN v_cursor FOR v_sql_statement 
        USING v_bind_vars(1).bind_value, v_bind_vars(2).bind_value;
    -- Add more cases as needed
    END IF;
    
    LOOP
      FETCH v_cursor INTO v_rec;
      EXIT WHEN v_cursor%NOTFOUND;
      
      -- Process each record
      log('Processing: ' || v_rec.member_name || ' = ' || v_rec.prop_value);
      
      -- Apply dynamic transformation
      EXECUTE IMMEDIATE
        'UPDATE ew_member_properties ' ||
        'SET prop_value = :new_value ' ||
        'WHERE member_name = :member_name ' ||
        'AND app_id = :app_id'
      USING 'PROCESSED_' || v_rec.prop_value,
            v_rec.member_name,
            ew_lb_api.g_app_id;
    END LOOP;
    
    CLOSE v_cursor;
    
  END process_dynamic_results;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting dynamic SQL execution');
  
  -- Example: Dynamic UPDATE
  v_sql_statement := 'UPDATE ew_member_properties SET ' ||
                    'last_modified = SYSDATE, ' ||
                    'modified_by = :user_name' ||
                    build_dynamic_where();
  
  add_bind_variable('user_name', ew_lb_api.g_user_name);
  
  -- Validate SQL length
  IF LENGTH(v_sql_statement) > c_max_sql_length THEN
    RAISE_APPLICATION_ERROR(-20002, 'SQL statement too long');
  END IF;
  
  -- Execute
  execute_dynamic_sql();
  
  -- Process SELECT results
  process_dynamic_results();
  
  ew_lb_api.g_message := 'Dynamic SQL executed successfully. ' ||
                        v_row_count || ' rows processed.';
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Error in dynamic SQL: ' || SQLERRM);
    log('SQL: ' || SUBSTR(v_sql_statement, 1, 4000));
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Dynamic SQL execution failed: ' || SQLERRM;
    ROLLBACK;
END;
```

## Error Recovery with Savepoints

🔴 **Level:** Advanced  
**Purpose:** Implement sophisticated error recovery using savepoints

```sql
/*
  Script: ERROR_RECOVERY_SAVEPOINTS
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Advanced error recovery using savepoints and retry logic
  
  Features:
  - Savepoint management
  - Partial rollback
  - Retry mechanisms
  - Error categorization
  - Recovery strategies
*/
DECLARE
  c_script_name      VARCHAR2(100) := 'ERROR_RECOVERY_SAVEPOINTS';
  c_max_retries      CONSTANT NUMBER := 3;
  c_retry_delay      CONSTANT NUMBER := 2; -- seconds
  
  v_operation_count  NUMBER := 0;
  v_success_count    NUMBER := 0;
  v_failure_count    NUMBER := 0;
  v_recovered_count  NUMBER := 0;
  
  e_recoverable      EXCEPTION;
  e_non_recoverable  EXCEPTION;
  PRAGMA EXCEPTION_INIT(e_recoverable, -20100);
  PRAGMA EXCEPTION_INIT(e_non_recoverable, -20101);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION is_recoverable_error(p_sqlcode IN NUMBER) RETURN BOOLEAN IS
  BEGIN
    -- Define recoverable errors
    RETURN p_sqlcode IN (
      -54,    -- Resource busy
      -60,    -- Deadlock
      -1555,  -- Snapshot too old
      -30006, -- Resource busy
      -20100  -- Custom recoverable
    );
  END is_recoverable_error;
  
  PROCEDURE wait_and_retry(p_seconds IN NUMBER) IS
  BEGIN
    log('Waiting ' || p_seconds || ' seconds before retry...');
    DBMS_LOCK.SLEEP(p_seconds);
  END wait_and_retry;
  
  PROCEDURE operation_with_savepoint(
    p_operation_id   IN NUMBER,
    p_operation_name IN VARCHAR2,
    p_data           IN VARCHAR2
  ) IS
    v_savepoint_name VARCHAR2(30);
    v_retry_count    NUMBER := 0;
    v_completed      BOOLEAN := FALSE;
    v_error_code     NUMBER;
    v_error_msg      VARCHAR2(4000);
  BEGIN
    v_savepoint_name := 'SP_' || p_operation_id;
    
    WHILE NOT v_completed AND v_retry_count < c_max_retries LOOP
      BEGIN
        -- Create savepoint
        EXECUTE IMMEDIATE 'SAVEPOINT ' || v_savepoint_name;
        log('Savepoint created: ' || v_savepoint_name);
        
        -- Simulate operation that might fail
        log('Executing operation: ' || p_operation_name);
        
        -- Example operation
        UPDATE ew_member_properties
        SET    prop_value = p_data,
               last_modified = SYSDATE
        WHERE  app_id = ew_lb_api.g_app_id
        AND    dim_id = ew_lb_api.g_dim_id
        AND    member_name = p_operation_name;
        
        -- Simulate potential errors (for demonstration)
        IF MOD(p_operation_id, 5) = 0 AND v_retry_count = 0 THEN
          RAISE e_recoverable;
        END IF;
        
        -- Success
        v_completed := TRUE;
        v_success_count := v_success_count + 1;
        log('Operation completed successfully: ' || p_operation_name);
        
      EXCEPTION
        WHEN e_recoverable OR OTHERS THEN
          v_error_code := SQLCODE;
          v_error_msg := SQLERRM;
          
          -- Rollback to savepoint
          EXECUTE IMMEDIATE 'ROLLBACK TO ' || v_savepoint_name;
          log('Rolled back to savepoint: ' || v_savepoint_name);
          
          IF is_recoverable_error(v_error_code) THEN
            v_retry_count := v_retry_count + 1;
            log('Recoverable error (' || v_error_code || '). Retry ' || 
                v_retry_count || '/' || c_max_retries);
            
            IF v_retry_count < c_max_retries THEN
              wait_and_retry(c_retry_delay * v_retry_count);
            ELSE
              log('Max retries exceeded for: ' || p_operation_name);
              v_failure_count := v_failure_count + 1;
              v_completed := TRUE; -- Exit loop
            END IF;
          ELSE
            -- Non-recoverable error
            log('Non-recoverable error: ' || v_error_msg);
            v_failure_count := v_failure_count + 1;
            v_completed := TRUE; -- Exit loop
          END IF;
      END;
    END LOOP;
    
    IF v_retry_count > 0 AND v_completed AND v_error_code IS NULL THEN
      v_recovered_count := v_recovered_count + 1;
      log('Operation recovered after ' || v_retry_count || ' retries');
    END IF;
    
  END operation_with_savepoint;
  
  PROCEDURE batch_operations_with_recovery IS
    v_batch_savepoint VARCHAR2(30) := 'BATCH_MAIN';
  BEGIN
    -- Main batch savepoint
    SAVEPOINT BATCH_MAIN;
    
    -- Process multiple operations
    FOR i IN 1..10 LOOP
      v_operation_count := v_operation_count + 1;
      
      BEGIN
        operation_with_savepoint(
          p_operation_id   => i,
          p_operation_name => 'MEMBER_' || i,
          p_data          => 'VALUE_' || i
        );
        
      EXCEPTION
        WHEN OTHERS THEN
          log('Unexpected error in operation ' || i || ': ' || SQLERRM);
          
          -- Decide whether to continue or abort batch
          IF v_failure_count > v_operation_count * 0.5 THEN
            log('Too many failures. Aborting batch.');
            ROLLBACK TO BATCH_MAIN;
            RAISE;
          END IF;
      END;
    END LOOP;
    
  END batch_operations_with_recovery;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting operations with error recovery');
  
  -- Execute batch with recovery
  batch_operations_with_recovery();
  
  -- Log summary
  log('Operations Summary:');
  log('  Total: ' || v_operation_count);
  log('  Successful: ' || v_success_count);
  log('  Failed: ' || v_failure_count);
  log('  Recovered: ' || v_recovered_count);
  
  -- Set status based on results
  IF v_failure_count = 0 THEN
    ew_lb_api.g_message := 'All operations completed successfully';
  ELSIF v_failure_count < v_operation_count THEN
    ew_lb_api.g_status := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'Partial success: ' || v_success_count || 
                          ' completed, ' || v_failure_count || ' failed';
  ELSE
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'All operations failed';
  END IF;
  
  COMMIT;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Critical error: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Batch processing failed: ' || SQLERRM;
    ROLLBACK;
END;
```

## Parallel Processing Pattern

🔴 **Level:** Advanced  
**Purpose:** Implement parallel processing using DBMS_PARALLEL_EXECUTE

```sql
/*
  Script: PARALLEL_PROCESSING_PATTERN
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Parallel processing of large datasets
  
  Features:
  - Parallel execution
  - Chunk management
  - Load balancing
  - Progress monitoring
  - Resource management
*/
DECLARE
  c_script_name     VARCHAR2(100) := 'PARALLEL_PROCESSING_PATTERN';
  c_task_name       VARCHAR2(100) := 'PARALLEL_TASK_' || TO_CHAR(SYSDATE, 'YYYYMMDDHH24MISS');
  c_parallel_degree NUMBER := 4;
  c_chunk_size      NUMBER := 1000;
  
  v_task_status     NUMBER;
  v_sql_chunk       VARCHAR2(4000);
  v_sql_execute     VARCHAR2(4000);
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  PROCEDURE setup_parallel_task IS
  BEGIN
    log('Setting up parallel task: ' || c_task_name);
    
    -- Create the task
    DBMS_PARALLEL_EXECUTE.CREATE_TASK(
      task_name => c_task_name,
      comment   => 'Parallel processing for ' || ew_lb_api.g_dim_name
    );
    
    -- Define chunks based on ROWID
    v_sql_chunk := 
      'SELECT MIN(ROWID), MAX(ROWID) ' ||
      'FROM ew_hierarchy ' ||
      'WHERE app_id = ' || ew_lb_api.g_app_id ||
      ' AND dim_id = ' || ew_lb_api.g_dim_id;
    
    DBMS_PARALLEL_EXECUTE.CREATE_CHUNKS_BY_ROWID(
      task_name   => c_task_name,
      table_owner => USER,
      table_name  => 'EW_HIERARCHY',
      by_row      => TRUE,
      chunk_size  => c_chunk_size
    );
    
    log('Chunks created for parallel processing');
    
  END setup_parallel_task;
  
  PROCEDURE execute_parallel_task IS
  BEGIN
    -- Define the SQL to execute for each chunk
    v_sql_execute := 
      'BEGIN ' ||
      '  UPDATE ew_member_properties ' ||
      '  SET prop_value = ''PARALLEL_'' || prop_value, ' ||
      '      last_modified = SYSDATE ' ||
      '  WHERE ROWID BETWEEN :start_rowid AND :end_rowid ' ||
      '  AND app_id = ' || ew_lb_api.g_app_id || '; ' ||
      '  COMMIT; ' ||
      'END;';
    
    log('Starting parallel execution with degree: ' || c_parallel_degree);
    
    -- Run the task in parallel
    DBMS_PARALLEL_EXECUTE.RUN_TASK(
      task_name      => c_task_name,
      sql_stmt       => v_sql_execute,
      language_flag  => DBMS_SQL.NATIVE,
      parallel_level => c_parallel_degree
    );
    
    log('Parallel execution initiated');
    
  END execute_parallel_task;
  
  PROCEDURE monitor_parallel_task IS
    v_chunks_total    NUMBER;
    v_chunks_complete NUMBER;
    v_percent_done    NUMBER;
  BEGIN
    LOOP
      -- Get task status
      v_task_status := DBMS_PARALLEL_EXECUTE.TASK_STATUS(c_task_name);
      
      -- Count chunks
      SELECT COUNT(*),
             SUM(CASE WHEN status = 'PROCESSED' THEN 1 ELSE 0 END)
      INTO   v_chunks_total, v_chunks_complete
      FROM   USER_PARALLEL_EXECUTE_CHUNKS
      WHERE  task_name = c_task_name;
      
      v_percent_done := ROUND(v_chunks_complete * 100 / NULLIF(v_chunks_total, 0), 1);
      
      log('Progress: ' || v_chunks_complete || '/' || v_chunks_total || 
          ' chunks (' || v_percent_done || '%)');
      
      EXIT WHEN v_task_status != DBMS_PARALLEL_EXECUTE.PROCESSING;
      
      DBMS_LOCK.SLEEP(5); -- Check every 5 seconds
    END LOOP;
    
    -- Check final status
    IF v_task_status = DBMS_PARALLEL_EXECUTE.FINISHED THEN
      log('Parallel task completed successfully');
    ELSE
      log('Parallel task failed with status: ' || v_task_status);
      
      -- Log failed chunks
      FOR chunk IN (SELECT chunk_id, status, error_message
                    FROM   USER_PARALLEL_EXECUTE_CHUNKS
                    WHERE  task_name = c_task_name
                    AND    status = 'PROCESSED_WITH_ERROR')
      LOOP
        log('Chunk ' || chunk.chunk_id || ' failed: ' || chunk.error_message);
      END LOOP;
    END IF;
    
  END monitor_parallel_task;
  
  PROCEDURE cleanup_parallel_task IS
  BEGIN
    DBMS_PARALLEL_EXECUTE.DROP_TASK(c_task_name);
    log('Parallel task cleaned up');
  EXCEPTION
    WHEN OTHERS THEN
      log('Cleanup error: ' || SQLERRM);
  END cleanup_parallel_task;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting parallel processing pattern');
  
  BEGIN
    -- Setup
    setup_parallel_task();
    
    -- Execute
    execute_parallel_task();
    
    -- Monitor
    monitor_parallel_task();
    
    -- Cleanup
    cleanup_parallel_task();
    
    ew_lb_api.g_message := 'Parallel processing completed successfully';
    
  EXCEPTION
    WHEN OTHERS THEN
      log('Parallel processing error: ' || SQLERRM);
      
      -- Attempt cleanup
      BEGIN
        cleanup_parallel_task();
      EXCEPTION
        WHEN OTHERS THEN
          NULL;
      END;
      
      ew_lb_api.g_status  := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Parallel processing failed: ' || SQLERRM;
  END;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Critical error: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Script execution failed: ' || SQLERRM;
END;
```

## Caching Pattern for Performance

🔴 **Level:** Advanced  
**Purpose:** Implement intelligent caching for frequently accessed data

```sql
/*
  Script: INTELLIGENT_CACHING_PATTERN
  Author: Logic Builder Team
  Date: 2025-01-15
  Purpose: Implement caching for performance optimization
  
  Features:
  - Memory-based caching
  - Cache invalidation
  - TTL management
  - Hit ratio tracking
  - Adaptive caching
*/
DECLARE
  c_script_name     VARCHAR2(100) := 'INTELLIGENT_CACHING_PATTERN';
  c_cache_ttl       CONSTANT NUMBER := 300; -- 5 minutes in seconds
  c_cache_max_size  CONSTANT NUMBER := 10000;
  
  -- Cache types
  TYPE t_cache_entry IS RECORD (
    cache_key    VARCHAR2(200),
    cache_value  VARCHAR2(4000),
    created_time TIMESTAMP,
    access_count NUMBER,
    last_access  TIMESTAMP
  );
  
  TYPE t_cache IS TABLE OF t_cache_entry INDEX BY VARCHAR2(200);
  
  g_cache          t_cache;
  v_cache_hits     NUMBER := 0;
  v_cache_misses   NUMBER := 0;
  v_cache_evictions NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
  FUNCTION get_cache_key(p_type IN VARCHAR2,
                        p_id1  IN VARCHAR2,
                        p_id2  IN VARCHAR2 DEFAULT NULL) RETURN VARCHAR2 IS
  BEGIN
    RETURN p_type || ':' || p_id1 || 
           CASE WHEN p_id2 IS NOT NULL THEN ':' || p_id2 ELSE NULL END;
  END get_cache_key;
  
  FUNCTION is_cache_valid(p_entry IN t_cache_entry) RETURN BOOLEAN IS
    v_age_seconds NUMBER;
  BEGIN
    v_age_seconds := EXTRACT(SECOND FROM (SYSTIMESTAMP - p_entry.created_time));
    RETURN v_age_seconds <= c_cache_ttl;
  END is_cache_valid;
  
  PROCEDURE evict_lru_entries IS
    TYPE t_lru_list IS TABLE OF VARCHAR2(200);
    v_lru_keys t_lru_list := t_lru_list();
    v_key VARCHAR2(200);
  BEGIN
    -- Check if eviction needed
    IF g_cache.COUNT < c_cache_max_size * 0.9 THEN
      RETURN;
    END IF;
    
    log('Cache eviction triggered. Size: ' || g_cache.COUNT);
    
    -- Collect keys sorted by last access (simplified)
    v_key := g_cache.FIRST;
    WHILE v_key IS NOT NULL LOOP
      IF NOT is_cache_valid(g_cache(v_key)) THEN
        v_lru_keys.EXTEND;
        v_lru_keys(v_lru_keys.COUNT) := v_key;
      END IF;
      v_key := g_cache.NEXT(v_key);
    END LOOP;
    
    -- Evict entries
    FOR i IN 1..v_lru_keys.COUNT LOOP
      g_cache.DELETE(v_lru_keys(i));
      v_cache_evictions := v_cache_evictions + 1;
      
      EXIT WHEN g_cache.COUNT < c_cache_max_size * 0.7;
    END LOOP;
    
    log('Evicted ' || v_lru_keys.COUNT || ' entries');
    
  END evict_lru_entries;
  
  FUNCTION get_from_cache(p_key IN VARCHAR2) RETURN VARCHAR2 IS
    v_entry t_cache_entry;
  BEGIN
    IF g_cache.EXISTS(p_key) THEN
      v_entry := g_cache(p_key);
      
      IF is_cache_valid(v_entry) THEN
        -- Update access info
        v_entry.access_count := v_entry.access_count + 1;
        v_entry.last_access := SYSTIMESTAMP;
        g_cache(p_key) := v_entry;
        
        v_cache_hits := v_cache_hits + 1;
        RETURN v_entry.cache_value;
      ELSE
        -- Expired entry
        g_cache.DELETE(p_key);
      END IF;
    END IF;
    
    v_cache_misses := v_cache_misses + 1;
    RETURN NULL;
    
  END get_from_cache;
  
  PROCEDURE put_in_cache(p_key IN VARCHAR2, p_value IN VARCHAR2) IS
    v_entry t_cache_entry;
  BEGIN
    -- Check cache size
    IF g_cache.COUNT >= c_cache_max_size THEN
      evict_lru_entries();
    END IF;
    
    -- Create cache entry
    v_entry.cache_key := p_key;
    v_entry.cache_value := p_value;
    v_entry.created_time := SYSTIMESTAMP;
    v_entry.access_count := 1;
    v_entry.last_access := SYSTIMESTAMP;
    
    g_cache(p_key) := v_entry;
    
  END put_in_cache;
  
  FUNCTION get_member_property_cached(p_member IN VARCHAR2,
                                     p_prop   IN VARCHAR2) RETURN VARCHAR2 IS
    v_cache_key VARCHAR2(200);
    v_value     VARCHAR2(4000);
  BEGIN
    v_cache_key := get_cache_key('PROP', p_member, p_prop);
    
    -- Try cache first
    v_value := get_from_cache(v_cache_key);
    
    IF v_value IS NULL THEN
      -- Cache miss - fetch from database
      SELECT prop_value
      INTO   v_value
      FROM   ew_member_properties
      WHERE  app_id = ew_lb_api.g_app_id
      AND    dim_id = ew_lb_api.g_dim_id
      AND    member_name = p_member
      AND    prop_name = p_prop;
      
      -- Store in cache
      put_in_cache(v_cache_key, v_value);
    END IF;
    
    RETURN v_value;
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- Cache negative result
      put_in_cache(v_cache_key, 'NULL');
      RETURN NULL;
  END get_member_property_cached;
  
  PROCEDURE log_cache_statistics IS
    v_hit_ratio NUMBER;
  BEGIN
    IF (v_cache_hits + v_cache_misses) > 0 THEN
      v_hit_ratio := ROUND(v_cache_hits * 100 / 
                          (v_cache_hits + v_cache_misses), 2);
    ELSE
      v_hit_ratio := 0;
    END IF;
    
    log('Cache Statistics:');
    log('  Size: ' || g_cache.COUNT || '/' || c_cache_max_size);
    log('  Hits: ' || v_cache_hits);
    log('  Misses: ' || v_cache_misses);
    log('  Hit Ratio: ' || v_hit_ratio || '%');
    log('  Evictions: ' || v_cache_evictions);
    
  END log_cache_statistics;
  
BEGIN
  ew_lb_api.g_status  := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Starting cached processing');
  
  -- Process members using cache
  FOR member IN (SELECT member_name
                 FROM   ew_hierarchy
                 WHERE  app_id = ew_lb_api.g_app_id
                 AND    dim_id = ew_lb_api.g_dim_id
                 AND    ROWNUM <= 1000) -- Limit for demo
  LOOP
    -- Multiple property accesses benefit from caching
    DECLARE
      v_prop1 VARCHAR2(500);
      v_prop2 VARCHAR2(500);
      v_prop3 VARCHAR2(500);
    BEGIN
      v_prop1 := get_member_property_cached(member.member_name, 'Currency');
      v_prop2 := get_member_property_cached(member.member_name, 'Status');
      v_prop3 := get_member_property_cached(member.member_name, 'Currency'); -- Cached hit
    END;
  END LOOP;
  
  -- Log final statistics
  log_cache_statistics();
  
  ew_lb_api.g_message := 'Processing completed with cache optimization. ' ||
                        'Hit ratio: ' || 
                        ROUND(v_cache_hits * 100 / 
                             NULLIF(v_cache_hits + v_cache_misses, 0), 1) || '%';
  
EXCEPTION
  WHEN OTHERS THEN
    log('Error: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Processing failed: ' || SQLERRM;
END;
```

## Best Practices Summary

### Performance Optimization
1. **Use bulk operations** - Process data in batches
2. **Implement caching** - Reduce database hits
3. **Parallel processing** - Leverage multiple CPU cores
4. **Optimize SQL** - Use appropriate indexes and hints
5. **Monitor resource usage** - Track memory and CPU

### Error Handling
1. **Use savepoints** - Enable partial rollback
2. **Implement retry logic** - Handle transient failures
3. **Categorize errors** - Different handling for different types
4. **Log comprehensively** - Track all operations
5. **Provide recovery options** - Allow graceful degradation

### Code Organization
1. **Modularize code** - Use procedures and functions
2. **Handle edge cases** - Validate inputs and outputs
3. **Document thoroughly** - Explain complex logic
4. **Test extensively** - Cover all scenarios
5. **Version control** - Track changes and rollback

### Security
1. **Prevent SQL injection** - Sanitize inputs
2. **Use bind variables** - Avoid dynamic concatenation
3. **Validate permissions** - Check user access
4. **Audit operations** - Track who did what
5. **Encrypt sensitive data** - Protect confidential information

## Next Steps

- Review [API Reference](../api/) for available functions
- Learn about [Performance Tuning](../advanced/performance.md)
- Explore [Security Best Practices](../advanced/security.md)