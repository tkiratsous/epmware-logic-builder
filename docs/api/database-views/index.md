# Database Views

EPMware provides read-only database views for accessing metadata and request information. These views are optimized for performance and respect security permissions.

## View Categories

### Core Metadata Views
Views for accessing application and dimension metadata:
- **[Core Views](core-views.md)** - Applications, dimensions, members, and hierarchies
- **[Request Views](request-views.md)** - Requests, request lines, and workflow data

## Security Model

All views enforce EPMware security:
- Row-level security based on user access
- Application and dimension permissions
- Filtered results based on user's security profile

## View Usage Guidelines

### Query Optimization

1. **Always Use Indexes**
   ```sql
   -- Good: Uses index on app_dimension_id
   SELECT * FROM ew_members_v
   WHERE app_dimension_id = 123;
   
   -- Poor: Full table scan
   SELECT * FROM ew_members_v
   WHERE UPPER(member_name) = 'ACCOUNT1';
   ```

2. **Filter Early**
   ```sql
   -- Filter at the view level
   SELECT member_name, parent_name
     FROM ew_members_v
    WHERE app_name = 'HFM_PROD'
      AND dimension_name = 'Account'
      AND level_number <= 3;
   ```

3. **Use Appropriate Views**
   ```sql
   -- Use specialized view for hierarchy
   SELECT * FROM ew_hierarchy_members_v
   WHERE app_dimension_id = 123;
   
   -- Instead of joining multiple views
   ```

## Common View Patterns

### Pattern 1: Member Lookup

```sql
-- Find member with properties
SELECT m.member_id,
       m.member_name,
       m.parent_name,
       m.level_number,
       m.property_value AS account_type
  FROM ew_members_v m
 WHERE m.app_name = 'HFM_PROD'
   AND m.dimension_name = 'Account'
   AND m.property_name = 'ACCOUNT_TYPE'
   AND m.member_name = 'Revenue';
```

### Pattern 2: Hierarchy Navigation

```sql
-- Get all descendants of a member
SELECT member_name,
       parent_name,
       level_number
  FROM ew_hierarchy_members_v
 START WITH member_name = 'TotalRevenue'
CONNECT BY PRIOR member_name = parent_name
 ORDER BY level_number, member_name;
```

### Pattern 3: Request Processing

```sql
-- Get pending request lines
SELECT r.request_id,
       r.request_name,
       l.request_line_id,
       l.member_name,
       l.action_name,
       l.status
  FROM ew_requests_v r
  JOIN ew_request_lines_v l ON r.request_id = l.request_id
 WHERE r.workflow_stage = 'APPROVAL'
   AND l.status = 'PENDING';
```

## View Columns Reference

### Standard Columns

Most views include these standard columns:

| Column | Type | Description |
|--------|------|-------------|
| `created_by` | VARCHAR2(100) | User who created the record |
| `created_date` | DATE | Creation timestamp |
| `updated_by` | VARCHAR2(100) | User who last updated |
| `updated_date` | DATE | Last update timestamp |

### ID Columns

| Column | Type | Description |
|--------|------|-------------|
| `app_id` | NUMBER | Application identifier |
| `dimension_id` | NUMBER | Dimension identifier |
| `app_dimension_id` | NUMBER | App-dimension combination ID |
| `member_id` | NUMBER | Member identifier |
| `request_id` | NUMBER | Request identifier |
| `request_line_id` | NUMBER | Request line identifier |

### Name Columns

| Column | Type | Description |
|--------|------|-------------|
| `app_name` | VARCHAR2(100) | Application name |
| `dimension_name` | VARCHAR2(100) | Dimension name |
| `member_name` | VARCHAR2(255) | Member name |
| `parent_name` | VARCHAR2(255) | Parent member name |

## Performance Tips

### Index Usage

Key indexes on views:

```sql
-- Check index usage
SELECT index_name, column_name, column_position
  FROM user_ind_columns
 WHERE table_name = 'EW_MEMBERS'
 ORDER BY index_name, column_position;
```

### Query Plans

Analyze query performance:

```sql
EXPLAIN PLAN FOR
  SELECT * FROM ew_members_v
  WHERE app_dimension_id = 123;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

### Statistics

Ensure statistics are current:

```sql
-- Check statistics age
SELECT table_name, last_analyzed
  FROM user_tables
 WHERE table_name LIKE 'EW_%'
 ORDER BY last_analyzed;
```

## Joining Views

### Efficient Joins

```sql
-- Good: Join on indexed columns
SELECT m.member_name,
       h.level_number,
       p.property_value
  FROM ew_members_v m
  JOIN ew_hierarchy_members_v h 
    ON m.member_id = h.member_id
   AND m.app_dimension_id = h.app_dimension_id
  LEFT JOIN ew_member_properties_v p
    ON m.member_id = p.member_id
   AND p.property_name = 'ACCOUNT_TYPE'
 WHERE m.app_dimension_id = 123;
```

### Avoiding Cartesian Products

```sql
-- Always include join conditions
SELECT *
  FROM ew_members_v m,
       ew_hierarchy_members_v h
 WHERE m.member_id = h.member_id  -- Critical!
   AND m.app_dimension_id = h.app_dimension_id;
```

## View Limitations

### Read-Only Access

Views are read-only. For modifications, use:
- Package APIs for member operations
- Request APIs for workflow actions
- Direct table access (with proper permissions)

### Performance Considerations

- Views may include complex joins
- Large result sets can impact performance
- Use pagination for large queries

### Security Filtering

- Results filtered by user security
- Row counts may vary by user
- Some columns may be masked

## Troubleshooting

### No Results Returned

Check:
1. User has access to application/dimension
2. Security filters are not too restrictive
3. Data exists in underlying tables

### Performance Issues

1. Add appropriate WHERE clauses
2. Use indexed columns in joins
3. Limit result set size
4. Review execution plans

### Access Denied

Verify:
- User has SELECT privilege on views
- Application security is configured
- Database session is valid

## Best Practices

1. **Cache Frequently Used Data**
   - Store static lookups in PL/SQL variables
   - Minimize repeated queries

2. **Use Bulk Operations**
   - Fetch multiple rows at once
   - Process in batches

3. **Handle NULL Values**
   - Check for NULLs explicitly
   - Use NVL/COALESCE functions

4. **Document Complex Queries**
   - Add comments for business logic
   - Explain join conditions

## Next Steps

- [Explore Core Views](core-views.md)
- [Learn Request Views](request-views.md)
- [Package APIs](../packages/)