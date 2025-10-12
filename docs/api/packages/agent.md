# Agent API Functions

The Agent API provides functions for job submission, deployment execution, and automated task management within EPMware.

**Package**: `EW_AGENT`  
**Usage**: `ew_agent.<function_name>`

## Overview

The Agent API enables:
- Job submission and management
- Direct deployment execution
- Automated task scheduling
- Batch processing
- Agent configuration
- Job monitoring

## Job Management

### submit_job

Submits a job for execution.

```sql
FUNCTION submit_job(
  p_job_type      IN VARCHAR2,
  p_job_name      IN VARCHAR2,
  p_parameters    IN VARCHAR2 DEFAULT NULL,
  p_priority      IN NUMBER DEFAULT 5,
  p_scheduled_time IN DATE DEFAULT SYSDATE
) RETURN NUMBER;  -- Returns job_id
```

**Example:**
```sql
DECLARE
  l_job_id NUMBER;
BEGIN
  l_job_id := ew_agent.submit_job(
    p_job_type   => 'HIERARCHY_REFRESH',
    p_job_name   => 'Nightly Account Refresh',
    p_parameters => 'APP_NAME=HFM_PROD;DIMENSION=Account',
    p_priority   => 1  -- High priority
  );
  
  DBMS_OUTPUT.PUT_LINE('Job submitted with ID: ' || l_job_id);
END;
```

### get_job_status

Returns the current status of a job.

```sql
FUNCTION get_job_status(
  p_job_id IN NUMBER
) RETURN VARCHAR2;  -- Returns 'PENDING', 'RUNNING', 'COMPLETED', 'FAILED'
```

### cancel_job

Cancels a pending or running job.

```sql
PROCEDURE cancel_job(
  p_job_id IN NUMBER,
  p_reason IN VARCHAR2 DEFAULT NULL
);
```

### get_job_info

Returns complete job information.

```sql
FUNCTION get_job_info(
  p_job_id IN NUMBER
) RETURN job_info_rec;
```

**Record Structure:**
```sql
TYPE job_info_rec IS RECORD (
  job_id          NUMBER,
  job_name        VARCHAR2(255),
  job_type        VARCHAR2(50),
  status          VARCHAR2(50),
  submitted_by    VARCHAR2(100),
  submitted_date  DATE,
  start_time      DATE,
  end_time        DATE,
  duration_sec    NUMBER,
  error_message   VARCHAR2(4000)
);
```

## Direct Deployment

### exec_direct_deploy

Executes direct deployment to an application.

```sql
PROCEDURE exec_direct_deploy(
  p_app_name           IN VARCHAR2,
  p_app_dimension_id   IN NUMBER DEFAULT NULL,
  p_request_line_id    IN NUMBER DEFAULT NULL,
  p_dep_file_name      IN VARCHAR2,
  p_dep_file_data      IN BLOB,
  p_override_params    IN ew_global.g_value_tbl,
  p_dep_config_name    IN VARCHAR2,
  p_user_id            IN NUMBER
);
```

**Example:**
```sql
DECLARE
  l_file_data BLOB;
  l_params ew_global.g_value_tbl;
BEGIN
  -- Load deployment file
  l_file_data := load_file_as_blob('/exports/metadata.xml');
  
  -- Set override parameters
  l_params('VALIDATE_ONLY') := 'N';
  l_params('BACKUP_FIRST') := 'Y';
  
  -- Execute deployment
  ew_agent.exec_direct_deploy(
    p_app_name        => 'HFM_PROD',
    p_dep_file_name   => 'metadata.xml',
    p_dep_file_data   => l_file_data,
    p_override_params => l_params,
    p_dep_config_name => 'STANDARD_DEPLOY',
    p_user_id         => 100
  );
  
  DBMS_OUTPUT.PUT_LINE('Deployment initiated');
END;
```

## Batch Processing

### submit_batch_job

Submits multiple jobs as a batch.

```sql
FUNCTION submit_batch_job(
  p_batch_name    IN VARCHAR2,
  p_job_list      IN job_list_tbl,
  p_parallel      IN VARCHAR2 DEFAULT 'N',
  p_stop_on_error IN VARCHAR2 DEFAULT 'Y'
) RETURN NUMBER;  -- Returns batch_id
```

**Example:**
```sql
DECLARE
  l_jobs ew_agent.job_list_tbl;
  l_batch_id NUMBER;
BEGIN
  -- Define batch jobs
  l_jobs(1).job_type := 'EXPORT';
  l_jobs(1).job_name := 'Export Accounts';
  l_jobs(1).parameters := 'DIMENSION=Account';
  
  l_jobs(2).job_type := 'EXPORT';
  l_jobs(2).job_name := 'Export Entities';
  l_jobs(2).parameters := 'DIMENSION=Entity';
  
  l_jobs(3).job_type := 'ARCHIVE';
  l_jobs(3).job_name := 'Archive Exports';
  l_jobs(3).parameters := 'COMPRESS=Y';
  
  -- Submit batch
  l_batch_id := ew_agent.submit_batch_job(
    p_batch_name    => 'Nightly Export Batch',
    p_job_list      => l_jobs,
    p_parallel      => 'N',  -- Sequential execution
    p_stop_on_error => 'Y'
  );
  
  DBMS_OUTPUT.PUT_LINE('Batch submitted: ' || l_batch_id);
END;
```

### get_batch_status

Returns the status of a batch job.

```sql
FUNCTION get_batch_status(
  p_batch_id IN NUMBER
) RETURN batch_status_rec;
```

**Record Structure:**
```sql
TYPE batch_status_rec IS RECORD (
  batch_id        NUMBER,
  batch_name      VARCHAR2(255),
  status          VARCHAR2(50),
  total_jobs      NUMBER,
  completed_jobs  NUMBER,
  failed_jobs     NUMBER,
  current_job     VARCHAR2(255),
  start_time      DATE,
  estimated_end   DATE
);
```

## Scheduling

### schedule_job

Schedules a job to run at specified intervals.

```sql
PROCEDURE schedule_job(
  p_job_name       IN VARCHAR2,
  p_job_type       IN VARCHAR2,
  p_schedule_type  IN VARCHAR2,  -- 'ONCE', 'DAILY', 'WEEKLY', 'MONTHLY'
  p_start_date     IN DATE,
  p_interval       IN NUMBER DEFAULT NULL,
  p_parameters     IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  -- Schedule daily hierarchy sync
  ew_agent.schedule_job(
    p_job_name      => 'Daily_Hierarchy_Sync',
    p_job_type      => 'HIERARCHY_SYNC',
    p_schedule_type => 'DAILY',
    p_start_date    => TRUNC(SYSDATE) + 1 + 2/24,  -- Tomorrow 2 AM
    p_parameters    => 'SOURCE=HFM;TARGET=PLANNING'
  );
  
  -- Schedule weekly consolidation
  ew_agent.schedule_job(
    p_job_name      => 'Weekly_Consolidation',
    p_job_type      => 'CONSOLIDATION',
    p_schedule_type => 'WEEKLY',
    p_start_date    => NEXT_DAY(TRUNC(SYSDATE), 'SUNDAY') + 6/24,  -- Sunday 6 AM
    p_parameters    => 'SCENARIO=ACTUAL;YEAR=2025'
  );
END;
```

### unschedule_job

Removes a scheduled job.

```sql
PROCEDURE unschedule_job(
  p_job_name IN VARCHAR2
);
```

### get_scheduled_jobs

Returns list of scheduled jobs.

```sql
FUNCTION get_scheduled_jobs(
  p_job_type IN VARCHAR2 DEFAULT NULL
) RETURN scheduled_job_tbl;
```

## Agent Configuration

### configure_agent

Configures agent settings.

```sql
PROCEDURE configure_agent(
  p_agent_name     IN VARCHAR2,
  p_max_threads    IN NUMBER DEFAULT 5,
  p_timeout_min    IN NUMBER DEFAULT 60,
  p_retry_count    IN NUMBER DEFAULT 3,
  p_log_level      IN VARCHAR2 DEFAULT 'INFO'
);
```

### get_agent_status

Returns agent status and health.

```sql
FUNCTION get_agent_status(
  p_agent_name IN VARCHAR2 DEFAULT NULL
) RETURN agent_status_rec;
```

**Record Structure:**
```sql
TYPE agent_status_rec IS RECORD (
  agent_name      VARCHAR2(100),
  status          VARCHAR2(50),
  active_jobs     NUMBER,
  queued_jobs     NUMBER,
  cpu_usage       NUMBER,
  memory_usage    NUMBER,
  last_heartbeat  DATE,
  uptime_hours    NUMBER
);
```

### restart_agent

Restarts an agent.

```sql
PROCEDURE restart_agent(
  p_agent_name IN VARCHAR2,
  p_force      IN VARCHAR2 DEFAULT 'N'
);
```

## Job Queue Management

### get_job_queue

Returns jobs in queue.

```sql
FUNCTION get_job_queue(
  p_status     IN VARCHAR2 DEFAULT NULL,
  p_job_type   IN VARCHAR2 DEFAULT NULL,
  p_max_rows   IN NUMBER DEFAULT 100
) RETURN job_queue_tbl;
```

**Example:**
```sql
DECLARE
  l_pending_jobs ew_agent.job_queue_tbl;
BEGIN
  -- Get all pending jobs
  l_pending_jobs := ew_agent.get_job_queue(
    p_status => 'PENDING',
    p_max_rows => 50
  );
  
  DBMS_OUTPUT.PUT_LINE('Pending jobs: ' || l_pending_jobs.COUNT);
  
  FOR i IN 1..l_pending_jobs.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(
      l_pending_jobs(i).job_name || ' (Priority: ' ||
      l_pending_jobs(i).priority || ')'
    );
  END LOOP;
END;
```

### reprioritize_job

Changes job priority in queue.

```sql
PROCEDURE reprioritize_job(
  p_job_id     IN NUMBER,
  p_new_priority IN NUMBER  -- 1 (highest) to 10 (lowest)
);
```

### pause_job_queue

Pauses job processing.

```sql
PROCEDURE pause_job_queue(
  p_agent_name IN VARCHAR2 DEFAULT NULL
);
```

### resume_job_queue

Resumes job processing.

```sql
PROCEDURE resume_job_queue(
  p_agent_name IN VARCHAR2 DEFAULT NULL
);
```

## Advanced Features

### Job Dependencies

```sql
DECLARE
  l_parent_job_id NUMBER;
  l_child_job_id NUMBER;
BEGIN
  -- Submit parent job
  l_parent_job_id := ew_agent.submit_job(
    p_job_type => 'EXPORT',
    p_job_name => 'Export Metadata'
  );
  
  -- Submit dependent job
  l_child_job_id := ew_agent.submit_dependent_job(
    p_job_type      => 'ARCHIVE',
    p_job_name      => 'Archive Export',
    p_parent_job_id => l_parent_job_id,
    p_dependency    => 'ON_SUCCESS'  -- Only run if parent succeeds
  );
END;
```

### Job Chaining

```sql
DECLARE
  l_chain_id NUMBER;
BEGIN
  -- Create job chain
  l_chain_id := ew_agent.create_job_chain(
    p_chain_name => 'Monthly_Process'
  );
  
  -- Add jobs to chain
  ew_agent.add_to_chain(l_chain_id, 'VALIDATE_DATA', 1);
  ew_agent.add_to_chain(l_chain_id, 'PROCESS_DATA', 2);
  ew_agent.add_to_chain(l_chain_id, 'CONSOLIDATE', 3);
  ew_agent.add_to_chain(l_chain_id, 'REPORT', 4);
  
  -- Execute chain
  ew_agent.execute_chain(l_chain_id);
END;
```

### Parallel Processing

```sql
DECLARE
  l_job_ids ew_global.g_number_tbl;
BEGIN
  -- Submit parallel jobs
  FOR i IN 1..10 LOOP
    l_job_ids(i) := ew_agent.submit_job(
      p_job_type   => 'PROCESS_CHUNK',
      p_job_name   => 'Process Chunk ' || i,
      p_parameters => 'CHUNK_ID=' || i,
      p_parallel   => 'Y'
    );
  END LOOP;
  
  -- Wait for all jobs to complete
  ew_agent.wait_for_jobs(l_job_ids);
  
  DBMS_OUTPUT.PUT_LINE('All parallel jobs completed');
END;
```

## Monitoring and Alerts

### set_job_alert

Sets alert for job events.

```sql
PROCEDURE set_job_alert(
  p_job_type    IN VARCHAR2,
  p_event_type  IN VARCHAR2,  -- 'FAILURE', 'LONG_RUNNING', 'SUCCESS'
  p_alert_email IN VARCHAR2
);
```

### get_job_statistics

Returns job execution statistics.

```sql
FUNCTION get_job_statistics(
  p_job_type   IN VARCHAR2 DEFAULT NULL,
  p_start_date IN DATE DEFAULT NULL,
  p_end_date   IN DATE DEFAULT NULL
) RETURN job_stats_rec;
```

**Record Structure:**
```sql
TYPE job_stats_rec IS RECORD (
  total_jobs      NUMBER,
  successful_jobs NUMBER,
  failed_jobs     NUMBER,
  avg_duration    NUMBER,
  max_duration    NUMBER,
  min_duration    NUMBER
);
```

## Error Handling

```sql
BEGIN
  l_job_id := ew_agent.submit_job(
    p_job_type => 'INVALID_TYPE',
    p_job_name => 'Test Job'
  );
EXCEPTION
  WHEN ew_agent.invalid_job_type THEN
    DBMS_OUTPUT.PUT_LINE('Invalid job type specified');
  WHEN ew_agent.agent_not_available THEN
    DBMS_OUTPUT.PUT_LINE('No agent available to process job');
  WHEN ew_agent.job_submission_failed THEN
    DBMS_OUTPUT.PUT_LINE('Failed to submit job');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
```

## Job Recovery

```sql
DECLARE
  l_failed_jobs ew_agent.job_queue_tbl;
BEGIN
  -- Get failed jobs
  l_failed_jobs := ew_agent.get_job_queue(p_status => 'FAILED');
  
  -- Retry failed jobs
  FOR i IN 1..l_failed_jobs.COUNT LOOP
    BEGIN
      ew_agent.retry_job(
        p_job_id => l_failed_jobs(i).job_id,
        p_reason => 'Manual retry after fix'
      );
    EXCEPTION
      WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('Could not retry job ' || 
                            l_failed_jobs(i).job_id);
    END;
  END LOOP;
END;
```

## Best Practices

1. **Check Agent Availability**
   ```sql
   IF ew_agent.is_agent_available('MAIN_AGENT') = 'Y' THEN
     submit_job(...);
   END IF;
   ```

2. **Handle Job Failures**
   ```sql
   -- Implement retry logic
   IF get_job_status(l_job_id) = 'FAILED' THEN
     retry_job(l_job_id);
   END IF;
   ```

3. **Monitor Long-Running Jobs**
   ```sql
   -- Set timeout for jobs
   configure_agent(p_timeout_min => 30);
   ```

4. **Use Appropriate Priority**
   ```sql
   -- Critical jobs = priority 1-3
   -- Normal jobs = priority 4-6
   -- Low priority = priority 7-10
   ```

## Next Steps

- [Appendices](../../appendices/)
- [API Overview](../)
- [Script Examples](../../events/)