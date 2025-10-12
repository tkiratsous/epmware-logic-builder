# Debugging and Testing Logic Scripts

This guide covers techniques and best practices for debugging and testing your Logic Builder scripts, ensuring reliable performance and easier troubleshooting.

## Debug Logging Framework

### Using the Debug API

EPMware provides a built-in debug logging API that writes messages to a centralized debug table. Always use this API for troubleshooting:

```sql
ew_debug.log(p_text      => 'Your debug message here',
             p_source_ref => 'SCRIPT_NAME');
```

### Complete Debugging Example

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'VALIDATE_ACCOUNT_CODE';
  v_step        NUMBER := 0;
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END log;
  
BEGIN
  -- Initialize
  v_step := 10;
  log('Starting validation - Step ' || v_step);
  log('Input value: ' || ew_lb_api.g_prop_value);
  
  -- Validation logic
  v_step := 20;
  log('Performing validation check - Step ' || v_step);
  
  IF LENGTH(ew_lb_api.g_prop_value) < 5 THEN
    log('Validation failed: Value too short');
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Account code must be at least 5 characters';
    RETURN;
  END IF;
  
  v_step := 30;
  log('Validation passed - Step ' || v_step);
  ew_lb_api.g_status := ew_lb_api.g_success;
  
EXCEPTION
  WHEN OTHERS THEN
    log('Exception at step ' || v_step || ': ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Unexpected error occurred';
END;
```

## Viewing Debug Messages

### Through the UI

1. Navigate to **Reports → Admin → Debug Messages**
2. Filter by Source Reference (your script name)
3. Set date/time range if needed
4. Click "Search" to view messages

![Debug Messages Report](../assets/images/debug-messages-report.png)
*Figure: Debug Messages report showing script execution logs*

### Through SQL (On-Premise Only)

```sql
SELECT debug_timestamp,
       source_ref,
       debug_text
FROM   ew_debug_messages
WHERE  source_ref = 'YOUR_SCRIPT_NAME'
AND    debug_timestamp >= SYSDATE - 1/24  -- Last hour
ORDER BY debug_timestamp DESC;
```

## Testing Strategies

### Unit Testing

Test individual script components in isolation:

#### 1. Create Test Wrapper Scripts

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'TEST_WRAPPER';
  
  PROCEDURE log(p_msg IN VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text => p_msg, p_source_ref => c_script_name);
  END log;
  
  PROCEDURE test_validation IS
  BEGIN
    -- Set up test data
    ew_lb_api.g_prop_value := 'TEST123';
    ew_lb_api.g_member_name := 'TestMember';
    
    -- Call your validation logic
    -- (Copy your actual validation code here)
    
    -- Check results
    log('Status: ' || ew_lb_api.g_status);
    log('Message: ' || ew_lb_api.g_message);
  END test_validation;
  
BEGIN
  log('Starting unit tests');
  test_validation;
  log('Tests completed');
END;
```

#### 2. Test Edge Cases

```sql
DECLARE
  TYPE t_test_case IS RECORD (
    input_value   VARCHAR2(100),
    expected_status VARCHAR2(1),
    test_description VARCHAR2(200)
  );
  TYPE t_test_cases IS TABLE OF t_test_case;
  
  l_tests t_test_cases := t_test_cases();
  
BEGIN
  -- Define test cases
  l_tests.EXTEND(5);
  l_tests(1) := t_test_case('', 'E', 'Empty value test');
  l_tests(2) := t_test_case('ABC', 'E', 'Too short value');
  l_tests(3) := t_test_case('VALID123', 'S', 'Valid value');
  l_tests(4) := t_test_case(NULL, 'E', 'NULL value test');
  l_tests(5) := t_test_case(RPAD('X', 100, 'X'), 'E', 'Max length test');
  
  -- Run tests
  FOR i IN 1..l_tests.COUNT LOOP
    ew_lb_api.g_prop_value := l_tests(i).input_value;
    
    -- Execute validation logic
    -- (Your validation code here)
    
    -- Log results
    IF ew_lb_api.g_status = l_tests(i).expected_status THEN
      log('PASS: ' || l_tests(i).test_description);
    ELSE
      log('FAIL: ' || l_tests(i).test_description || 
          ' - Expected: ' || l_tests(i).expected_status ||
          ', Got: ' || ew_lb_api.g_status);
    END IF;
  END LOOP;
END;
```

### Integration Testing

Test scripts within the actual EPMware context:

#### 1. Create Test Hierarchies

- Create a dedicated test application/dimension
- Use naming convention like `TEST_*` for test members
- Document test scenarios and expected outcomes

#### 2. Automated Test Execution

```sql
DECLARE
  c_script_name VARCHAR2(100) := 'INTEGRATION_TEST';
  v_test_count  NUMBER := 0;
  v_pass_count  NUMBER := 0;
  
  PROCEDURE run_test(p_test_name IN VARCHAR2,
                     p_action     IN VARCHAR2,
                     p_expected   IN VARCHAR2) IS
  BEGIN
    v_test_count := v_test_count + 1;
    
    -- Perform action (e.g., create member, update property)
    -- Check result
    
    IF (result = p_expected) THEN
      v_pass_count := v_pass_count + 1;
      log('PASS: ' || p_test_name);
    ELSE
      log('FAIL: ' || p_test_name);
    END IF;
  END run_test;
  
BEGIN
  log('Starting integration tests');
  
  run_test('Create valid member', 'CREATE', 'SUCCESS');
  run_test('Duplicate member name', 'CREATE', 'ERROR');
  run_test('Update property', 'UPDATE', 'SUCCESS');
  
  log('Tests completed: ' || v_pass_count || '/' || v_test_count || ' passed');
END;
```

## Common Debugging Scenarios

### Script Not Executing

**Symptoms:** No debug messages, no effect on data

**Debugging Steps:**

1. **Verify Script is Enabled**
   ```sql
   log('Script enabled check - entering script');
   ```

2. **Check Event Association**
   - Navigate to relevant configuration screen
   - Confirm script is assigned to correct event
   - Verify application/dimension selection

3. **Test with Simple Script**
   ```sql
   BEGIN
     ew_debug.log('Test script executed', 'TEST_SCRIPT');
     ew_lb_api.g_status := ew_lb_api.g_success;
   END;
   ```

### Unexpected Results

**Symptoms:** Script executes but produces wrong output

**Debugging Steps:**

1. **Log All Input Parameters**
   ```sql
   log('Member: ' || ew_lb_api.g_member_name);
   log('Parent: ' || ew_lb_api.g_parent_member_name);
   log('Property: ' || ew_lb_api.g_prop_name);
   log('Value: ' || ew_lb_api.g_prop_value);
   log('Old Value: ' || ew_lb_api.g_old_prop_value);
   ```

2. **Trace Execution Path**
   ```sql
   IF condition1 THEN
     log('Entering condition1 branch');
   ELSIF condition2 THEN
     log('Entering condition2 branch');
   ELSE
     log('Entering else branch');
   END IF;
   ```

3. **Validate Data Types**
   ```sql
   log('Value type: ' || SQL%ROWCOUNT);
   log('Value length: ' || LENGTH(ew_lb_api.g_prop_value));
   log('Is numeric: ' || CASE WHEN REGEXP_LIKE(ew_lb_api.g_prop_value, '^\d+$') 
                               THEN 'Yes' ELSE 'No' END);
   ```

### Performance Issues

**Symptoms:** Script executes slowly, times out

**Debugging Steps:**

1. **Add Timing Information**
   ```sql
   DECLARE
     v_start_time TIMESTAMP;
     v_end_time   TIMESTAMP;
   BEGIN
     v_start_time := SYSTIMESTAMP;
     log('Process started at: ' || v_start_time);
     
     -- Your logic here
     
     v_end_time := SYSTIMESTAMP;
     log('Process ended at: ' || v_end_time);
     log('Duration: ' || (v_end_time - v_start_time));
   END;
   ```

2. **Identify Bottlenecks**
   ```sql
   v_start := DBMS_UTILITY.GET_TIME;
   -- Operation 1
   log('Operation 1 took: ' || (DBMS_UTILITY.GET_TIME - v_start) || ' cs');
   
   v_start := DBMS_UTILITY.GET_TIME;
   -- Operation 2
   log('Operation 2 took: ' || (DBMS_UTILITY.GET_TIME - v_start) || ' cs');
   ```

## Debug Levels and Categories

### Implementing Debug Levels

```sql
DECLARE
  c_debug_level NUMBER := 3; -- 1=Error, 2=Warning, 3=Info, 4=Debug
  
  PROCEDURE log(p_msg IN VARCHAR2, p_level IN NUMBER DEFAULT 3) IS
  BEGIN
    IF p_level <= c_debug_level THEN
      ew_debug.log(p_text      => '[L' || p_level || '] ' || p_msg,
                   p_source_ref => c_script_name);
    END IF;
  END log;
  
BEGIN
  log('Critical error occurred', 1);
  log('Warning: Using default value', 2);
  log('Processing member', 3);
  log('Detailed debug info', 4);
END;
```

### Categorizing Debug Messages

```sql
PROCEDURE log(p_msg IN VARCHAR2, p_category IN VARCHAR2 DEFAULT 'GENERAL') IS
BEGIN
  ew_debug.log(p_text      => '[' || p_category || '] ' || p_msg,
               p_source_ref => c_script_name);
END log;

-- Usage
log('Member created successfully', 'AUDIT');
log('Invalid format detected', 'VALIDATION');
log('Sending notification email', 'NOTIFICATION');
log('Database query executed', 'PERFORMANCE');
```

## Production Debugging

### Safe Debugging in Production

1. **Use Conditional Debugging**
   ```sql
   DECLARE
     c_debug_enabled BOOLEAN := FALSE; -- Set via configuration
   BEGIN
     IF c_debug_enabled THEN
       log('Detailed debug information');
     END IF;
   END;
   ```

2. **Implement Debug Flags**
   ```sql
   -- Check for debug member/property
   IF ew_lb_api.g_member_name = 'DEBUG_MODE' THEN
     log('Debug mode activated for testing');
     -- Extra logging here
   END IF;
   ```

3. **Limit Debug Output**
   ```sql
   DECLARE
     v_debug_count NUMBER := 0;
     c_max_debug   NUMBER := 100;
   BEGIN
     IF v_debug_count < c_max_debug THEN
       log('Debug message');
       v_debug_count := v_debug_count + 1;
     END IF;
   END;
   ```

## Error Handling Best Practices

### Comprehensive Exception Handling

```sql
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    log('No data found for criteria');
    ew_lb_api.g_status  := ew_lb_api.g_warning;
    ew_lb_api.g_message := 'No matching records found';
    
  WHEN TOO_MANY_ROWS THEN
    log('Multiple rows returned when expecting one');
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Data integrity issue detected';
    
  WHEN VALUE_ERROR THEN
    log('Value error: ' || SQLERRM);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Invalid data format';
    
  WHEN OTHERS THEN
    log('Unexpected error: ' || SQLCODE || ' - ' || SQLERRM);
    log('Error backtrace: ' || DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);
    ew_lb_api.g_status  := ew_lb_api.g_error;
    ew_lb_api.g_message := 'An unexpected error occurred';
END;
```

### Graceful Degradation

```sql
BEGIN
  BEGIN
    -- Primary logic
    perform_main_operation;
  EXCEPTION
    WHEN OTHERS THEN
      log('Primary operation failed, trying fallback');
      BEGIN
        perform_fallback_operation;
      EXCEPTION
        WHEN OTHERS THEN
          log('Fallback also failed');
          ew_lb_api.g_status := ew_lb_api.g_warning;
          ew_lb_api.g_message := 'Operation completed with warnings';
      END;
  END;
END;
```

## Performance Monitoring

### Query Performance Analysis

```sql
DECLARE
  v_sql_id     VARCHAR2(20);
  v_row_count  NUMBER;
BEGIN
  -- Get SQL ID for analysis
  SELECT prev_sql_id INTO v_sql_id
  FROM v$session
  WHERE sid = SYS_CONTEXT('USERENV', 'SID');
  
  log('SQL ID: ' || v_sql_id);
  
  -- Log row counts
  v_row_count := SQL%ROWCOUNT;
  log('Rows processed: ' || v_row_count);
END;
```

### Memory Usage Tracking

```sql
DECLARE
  v_mem_used NUMBER;
BEGIN
  -- Get current PGA usage
  SELECT value INTO v_mem_used
  FROM v$mystat m, v$statname s
  WHERE m.statistic# = s.statistic#
  AND s.name = 'session pga memory';
  
  log('Memory used: ' || ROUND(v_mem_used/1024/1024, 2) || ' MB');
END;
```

## Troubleshooting Checklist

### Quick Diagnostics

- [ ] Script enabled in Logic Builder?
- [ ] Script associated with correct event?
- [ ] Correct application/dimension selected?
- [ ] Debug logging enabled globally?
- [ ] Syntax validation passed?
- [ ] All required input parameters available?
- [ ] Output parameters properly set?
- [ ] Exception handling in place?
- [ ] Test with simplified script version?
- [ ] Check debug messages report?

### Common Issues and Solutions

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| No debug output | Debug disabled globally | Enable in Configuration → Global Settings |
| Script not triggered | Wrong event association | Review event configuration |
| Partial execution | Unhandled exception | Add comprehensive error handling |
| Slow performance | Inefficient queries | Optimize SQL, add indexes |
| Inconsistent results | Concurrent modifications | Implement locking mechanism |
| Memory errors | Large data sets | Process in batches |

## Next Steps

- Review [Script Examples](../examples/) for debugging patterns
- Explore [API Reference](../api/) for additional debug functions
- Learn about [Performance Optimization](../advanced/performance.md)