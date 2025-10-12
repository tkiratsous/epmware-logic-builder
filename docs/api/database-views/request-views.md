# Request Database Views

Request views provide access to workflow requests, request lines, and related metadata operations within EPMware.

## Request Header Views

### EW_REQUESTS_V

Main view for request header information.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `REQUEST_ID` | NUMBER | Unique request identifier |
| `REQUEST_NAME` | VARCHAR2(255) | Request name/title |
| `REQUEST_TYPE` | VARCHAR2(50) | Type of request |
| `DESCRIPTION` | VARCHAR2(4000) | Request description |
| `STATUS` | VARCHAR2(50) | Current status |
| `WORKFLOW_STAGE` | VARCHAR2(100) | Current workflow stage |
| `WORKFLOW_STATUS` | VARCHAR2(50) | Workflow status |
| `PRIORITY` | VARCHAR2(20) | Priority level |
| `DUE_DATE` | DATE | Request due date |
| `SUBMITTED_BY` | VARCHAR2(100) | User who submitted |
| `SUBMITTED_DATE` | DATE | Submission date |
| `APPROVED_BY` | VARCHAR2(100) | Final approver |
| `APPROVED_DATE` | DATE | Approval date |
| `COMPLETED_DATE` | DATE | Completion date |
| `APP_ID` | NUMBER | Application ID |
| `APP_NAME` | VARCHAR2(100) | Application name |
| `CREATED_BY` | VARCHAR2(100) | Created by user |
| `CREATED_DATE` | DATE | Creation date |
| `UPDATED_BY` | VARCHAR2(100) | Last updated by |
| `UPDATED_DATE` | DATE | Last update date |

**Example Usage:**

```sql
-- Get pending requests
SELECT request_id, request_name, workflow_stage
  FROM ew_requests_v
 WHERE status = 'PENDING'
   AND workflow_status = 'IN_PROCESS'
 ORDER BY priority, due_date;

-- Find requests by user
SELECT *
  FROM ew_requests_v
 WHERE submitted_by = USER
   AND created_date >= SYSDATE - 30;

-- Requests awaiting approval
SELECT request_id, request_name, submitted_by, submitted_date
  FROM ew_requests_v
 WHERE workflow_stage = 'APPROVAL'
   AND workflow_status = 'PENDING';
```

### EW_REQUEST_LINES_V

Individual request line items with member operations.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `REQUEST_LINE_ID` | NUMBER | Unique line identifier |
| `REQUEST_ID` | NUMBER | Parent request ID |
| `LINE_NUMBER` | NUMBER | Line sequence number |
| `APP_DIMENSION_ID` | NUMBER | App-dimension ID |
| `DIMENSION_NAME` | VARCHAR2(100) | Dimension name |
| `ACTION_CODE` | VARCHAR2(20) | Action code (CMC, REN, etc.) |
| `ACTION_NAME` | VARCHAR2(100) | Action description |
| `MEMBER_ID` | NUMBER | Member ID (if exists) |
| `MEMBER_NAME` | VARCHAR2(255) | Member name |
| `PARENT_NAME` | VARCHAR2(255) | Parent member name |
| `NEW_NAME` | VARCHAR2(255) | New name (for rename) |
| `STATUS` | VARCHAR2(50) | Line status |
| `ERROR_MESSAGE` | VARCHAR2(4000) | Error details if failed |
| `APPROVED_BY` | VARCHAR2(100) | Line approver |
| `APPROVED_DATE` | DATE | Line approval date |
| `PROCESSED_FLAG` | VARCHAR2(1) | Processed indicator |
| `PROCESSED_DATE` | DATE | Processing date |

**Example Usage:**

```sql
-- Get request lines for a request
SELECT line_number, 
       dimension_name,
       action_name,
       member_name,
       status
  FROM ew_request_lines_v
 WHERE request_id = 12345
 ORDER BY line_number;

-- Find failed lines
SELECT r.request_name,
       l.line_number,
       l.member_name,
       l.error_message
  FROM ew_requests_v r
  JOIN ew_request_lines_v l ON r.request_id = l.request_id
 WHERE l.status = 'ERROR';

-- Lines pending approval
SELECT *
  FROM ew_request_lines_v
 WHERE request_id IN (
   SELECT request_id
     FROM ew_requests_v
    WHERE workflow_stage = 'APPROVAL'
 )
   AND approved_date IS NULL;
```

### EW_REQUEST_LINE_MEMBERS_V

Extended view with full member details for request lines.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `REQUEST_LINE_ID` | NUMBER | Request line ID |
| `REQUEST_ID` | NUMBER | Request ID |
| `REQUEST_NAME` | VARCHAR2(255) | Request name |
| `APP_NAME` | VARCHAR2(100) | Application name |
| `DIMENSION_NAME` | VARCHAR2(100) | Dimension name |
| `ACTION_CODE` | VARCHAR2(20) | Action code |
| `ACTION_NAME` | VARCHAR2(100) | Action name |
| `MEMBER_NAME` | VARCHAR2(255) | Member name |
| `PARENT_NAME` | VARCHAR2(255) | Parent name |
| `NEW_NAME` | VARCHAR2(255) | New name (rename) |
| `LEVEL_NUMBER` | NUMBER | Hierarchy level |
| `MEMBER_TYPE` | VARCHAR2(50) | Member type |
| `LINE_STATUS` | VARCHAR2(50) | Line status |
| `REQUEST_STATUS` | VARCHAR2(50) | Request status |
| `WORKFLOW_STAGE` | VARCHAR2(100) | Current stage |

**Example Usage:**

```sql
-- Get complete request line details
SELECT action_name,
       member_name,
       parent_name,
       level_number
  FROM ew_request_line_members_v
 WHERE request_id = 12345
   AND line_status = 'PENDING';

-- Analyze request by dimension
SELECT dimension_name,
       COUNT(*) AS line_count,
       COUNT(DISTINCT member_name) AS unique_members
  FROM ew_request_line_members_v
 WHERE request_id = 12345
 GROUP BY dimension_name;
```

## Workflow Views

### EW_WORKFLOW_STAGES_V

Workflow stage definitions and current status.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `WORKFLOW_ID` | NUMBER | Workflow ID |
| `WORKFLOW_NAME` | VARCHAR2(100) | Workflow name |
| `STAGE_ID` | NUMBER | Stage ID |
| `STAGE_NAME` | VARCHAR2(100) | Stage name |
| `STAGE_SEQUENCE` | NUMBER | Stage order |
| `STAGE_TYPE` | VARCHAR2(50) | Stage type |
| `IS_APPROVAL` | VARCHAR2(1) | Approval stage flag |
| `AUTO_APPROVE` | VARCHAR2(1) | Auto-approval flag |
| `REQUIRED_APPROVALS` | NUMBER | Required approval count |
| `ESCALATION_DAYS` | NUMBER | Days before escalation |

**Example Usage:**

```sql
-- Get workflow configuration
SELECT stage_sequence,
       stage_name,
       stage_type,
       required_approvals
  FROM ew_workflow_stages_v
 WHERE workflow_name = 'STANDARD_APPROVAL'
 ORDER BY stage_sequence;

-- Find approval stages
SELECT *
  FROM ew_workflow_stages_v
 WHERE is_approval = 'Y'
   AND auto_approve = 'N';
```

### EW_WORKFLOW_TASKS_V

Active workflow tasks and assignments.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `TASK_ID` | NUMBER | Task ID |
| `REQUEST_ID` | NUMBER | Request ID |
| `STAGE_ID` | NUMBER | Stage ID |
| `STAGE_NAME` | VARCHAR2(100) | Stage name |
| `TASK_TYPE` | VARCHAR2(50) | Task type |
| `ASSIGNED_TO` | VARCHAR2(100) | Assigned user |
| `ASSIGNED_GROUP` | VARCHAR2(100) | Assigned group |
| `STATUS` | VARCHAR2(50) | Task status |
| `DUE_DATE` | DATE | Task due date |
| `COMPLETED_BY` | VARCHAR2(100) | Who completed |
| `COMPLETED_DATE` | DATE | Completion date |
| `COMMENTS` | VARCHAR2(4000) | Task comments |

**Example Usage:**

```sql
-- Get user's tasks
SELECT task_id,
       stage_name,
       task_type,
       due_date
  FROM ew_workflow_tasks_v
 WHERE assigned_to = USER
   AND status = 'PENDING'
 ORDER BY due_date;

-- Overdue tasks
SELECT *
  FROM ew_workflow_tasks_v
 WHERE status = 'PENDING'
   AND due_date < SYSDATE;

-- Task summary by stage
SELECT stage_name,
       COUNT(*) AS task_count,
       COUNT(CASE WHEN status = 'PENDING' THEN 1 END) AS pending,
       COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS completed
  FROM ew_workflow_tasks_v
 GROUP BY stage_name;
```

## Property Request Views

### EW_REQUEST_PROPERTIES_V

Property changes within requests.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `REQUEST_LINE_ID` | NUMBER | Request line ID |
| `PROPERTY_NAME` | VARCHAR2(100) | Property name |
| `OLD_VALUE` | VARCHAR2(4000) | Original value |
| `NEW_VALUE` | VARCHAR2(4000) | New value |
| `CHANGE_TYPE` | VARCHAR2(20) | Type of change |
| `VALIDATION_STATUS` | VARCHAR2(50) | Validation result |

**Example Usage:**

```sql
-- Get property changes for request
SELECT l.member_name,
       p.property_name,
       p.old_value,
       p.new_value
  FROM ew_request_lines_v l
  JOIN ew_request_properties_v p
    ON l.request_line_id = p.request_line_id
 WHERE l.request_id = 12345;

-- Find validation errors
SELECT *
  FROM ew_request_properties_v
 WHERE validation_status = 'ERROR';
```

## Complex Request Queries

### Request Summary Dashboard

```sql
-- Request status summary
SELECT 
  status,
  workflow_stage,
  COUNT(*) AS request_count,
  AVG(SYSDATE - created_date) AS avg_age_days,
  MIN(created_date) AS oldest_request
FROM ew_requests_v
WHERE status NOT IN ('COMPLETED', 'CANCELLED')
GROUP BY status, workflow_stage
ORDER BY status, workflow_stage;
```

### Approval Queue Analysis

```sql
-- Approval workload by user
WITH approval_tasks AS (
  SELECT 
    t.assigned_to AS approver,
    r.request_id,
    r.request_name,
    r.priority,
    r.due_date,
    COUNT(l.request_line_id) AS line_count
  FROM ew_workflow_tasks_v t
  JOIN ew_requests_v r ON t.request_id = r.request_id
  JOIN ew_request_lines_v l ON r.request_id = l.request_id
  WHERE t.status = 'PENDING'
    AND t.task_type = 'APPROVAL'
  GROUP BY t.assigned_to, r.request_id, r.request_name, 
           r.priority, r.due_date
)
SELECT 
  approver,
  COUNT(request_id) AS pending_requests,
  SUM(line_count) AS total_lines,
  MIN(due_date) AS next_due
FROM approval_tasks
GROUP BY approver
ORDER BY pending_requests DESC;
```

### Request Line Impact Analysis

```sql
-- Analyze hierarchy impact of requests
SELECT 
  r.request_name,
  l.dimension_name,
  l.action_name,
  l.member_name,
  (SELECT COUNT(*)
   FROM ew_hierarchy_members_v h
   WHERE h.app_dimension_id = l.app_dimension_id
   START WITH h.member_name = l.member_name
   CONNECT BY PRIOR h.member_id = h.parent_id
  ) AS affected_descendants
FROM ew_requests_v r
JOIN ew_request_lines_v l ON r.request_id = l.request_id
WHERE r.status = 'PENDING'
  AND l.action_code IN ('DM', 'ZC', 'ZS')  -- Delete or move actions
ORDER BY affected_descendants DESC;
```

### Historical Request Patterns

```sql
-- Request patterns by month
SELECT 
  TO_CHAR(created_date, 'YYYY-MM') AS month,
  COUNT(*) AS total_requests,
  COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS completed,
  COUNT(CASE WHEN status = 'REJECTED' THEN 1 END) AS rejected,
  AVG(completed_date - created_date) AS avg_completion_days
FROM ew_requests_v
WHERE created_date >= ADD_MONTHS(SYSDATE, -12)
GROUP BY TO_CHAR(created_date, 'YYYY-MM')
ORDER BY month;
```

## Performance Tips

### Efficient Request Queries

```sql
-- Use request_id index
SELECT * FROM ew_request_lines_v
WHERE request_id = 12345;  -- Indexed

-- Avoid functions on indexed columns
-- Bad:
SELECT * FROM ew_requests_v
WHERE TRUNC(created_date) = TRUNC(SYSDATE);

-- Good:
SELECT * FROM ew_requests_v
WHERE created_date >= TRUNC(SYSDATE)
  AND created_date < TRUNC(SYSDATE) + 1;
```

### Join Optimization

```sql
-- Efficient multi-table join
SELECT /*+ LEADING(r) USE_NL(l p) */
       r.request_name,
       l.member_name,
       p.property_value
  FROM ew_requests_v r
  JOIN ew_request_lines_v l
    ON r.request_id = l.request_id
  LEFT JOIN ew_request_properties_v p
    ON l.request_line_id = p.request_line_id
 WHERE r.request_id = 12345;
```

## Security Considerations

### Row-Level Security

```sql
-- Views automatically filter by user security
-- This returns only requests user can see
SELECT * FROM ew_requests_v;

-- To check specific access
SELECT DECODE(COUNT(*), 0, 'No Access', 'Has Access') AS access_check
  FROM ew_requests_v
 WHERE request_id = 12345;
```

## View Maintenance

### Refresh Statistics

```sql
-- Check view performance
SELECT view_name, last_analyzed
  FROM user_views
 WHERE view_name LIKE 'EW_REQUEST%'
 ORDER BY last_analyzed;

-- Gather fresh statistics
BEGIN
  DBMS_STATS.gather_table_stats(
    ownname => USER,
    tabname => 'EW_REQUESTS'
  );
END;
```

## Best Practices

1. **Filter Early**
   - Use request_id when known
   - Filter by date ranges
   - Limit by status

2. **Use Appropriate Views**
   - EW_REQUESTS_V for headers
   - EW_REQUEST_LINES_V for details
   - EW_REQUEST_LINE_MEMBERS_V for full context

3. **Consider Performance**
   - Avoid SELECT *
   - Use indexed columns
   - Limit result sets

4. **Handle NULLs**
   - Check for NULL approved_date
   - Handle missing error_message
   - Account for optional fields

5. **Monitor Long-Running Requests**
   - Check age of pending requests
   - Identify bottlenecks
   - Track completion times

## Next Steps

- [Core Views](core-views.md)
- [Package APIs](../packages/)
- [Workflow Examples](../../events/workflow/)