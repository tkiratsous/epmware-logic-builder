# Core Database Views

Core views provide access to EPMware's fundamental metadata structures including applications, dimensions, members, and hierarchies.

## Application Views

### EW_APPS_V

Provides information about configured applications.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `APP_ID` | NUMBER | Unique application identifier |
| `APP_NAME` | VARCHAR2(100) | Application name |
| `APP_TYPE` | VARCHAR2(50) | Application type (HFM, PLANNING, ESSBASE) |
| `DESCRIPTION` | VARCHAR2(255) | Application description |
| `STATUS` | VARCHAR2(20) | Application status (ACTIVE, INACTIVE) |
| `ENVIRONMENT` | VARCHAR2(50) | Environment (PROD, UAT, DEV) |
| `VERSION` | VARCHAR2(50) | Application version |
| `CREATED_BY` | VARCHAR2(100) | User who created |
| `CREATED_DATE` | DATE | Creation date |
| `UPDATED_BY` | VARCHAR2(100) | Last updated by |
| `UPDATED_DATE` | DATE | Last update date |

**Example Usage:**

```sql
-- Get all active applications
SELECT app_id, app_name, app_type
  FROM ew_apps_v
 WHERE status = 'ACTIVE'
 ORDER BY app_name;

-- Find specific application
SELECT *
  FROM ew_apps_v
 WHERE app_name = 'HFM_PROD'
   AND app_type = 'HFM';
```

### EW_APP_DIMENSIONS_V

Links applications to their dimensions.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `APP_DIMENSION_ID` | NUMBER | Unique app-dimension identifier |
| `APP_ID` | NUMBER | Application ID |
| `APP_NAME` | VARCHAR2(100) | Application name |
| `DIMENSION_ID` | NUMBER | Dimension ID |
| `DIMENSION_NAME` | VARCHAR2(100) | Dimension name |
| `DIMENSION_TYPE` | VARCHAR2(50) | Dimension type (ACCOUNT, ENTITY, etc.) |
| `IS_REQUIRED` | VARCHAR2(1) | Required dimension flag (Y/N) |
| `SORT_ORDER` | NUMBER | Display order |
| `CREATED_BY` | VARCHAR2(100) | Created by user |
| `CREATED_DATE` | DATE | Creation date |

**Example Usage:**

```sql
-- Get all dimensions for an application
SELECT dimension_name, dimension_type, is_required
  FROM ew_app_dimensions_v
 WHERE app_name = 'PLANNING_PROD'
 ORDER BY sort_order;

-- Find app_dimension_id
SELECT app_dimension_id
  FROM ew_app_dimensions_v
 WHERE app_name = 'HFM_PROD'
   AND dimension_name = 'Account';
```

## Member Views

### EW_MEMBERS_V

Comprehensive view of all members across dimensions.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `MEMBER_ID` | NUMBER | Unique member identifier |
| `MEMBER_NAME` | VARCHAR2(255) | Member name |
| `APP_ID` | NUMBER | Application ID |
| `APP_NAME` | VARCHAR2(100) | Application name |
| `DIMENSION_ID` | NUMBER | Dimension ID |
| `DIMENSION_NAME` | VARCHAR2(100) | Dimension name |
| `APP_DIMENSION_ID` | NUMBER | App-dimension ID |
| `PARENT_ID` | NUMBER | Parent member ID |
| `PARENT_NAME` | VARCHAR2(255) | Parent member name |
| `MEMBER_TYPE` | VARCHAR2(50) | Member type (PARENT, LEAF) |
| `DATA_TYPE` | VARCHAR2(50) | Data type |
| `CONSOLIDATION` | VARCHAR2(10) | Consolidation operator |
| `IS_SHARED` | VARCHAR2(1) | Shared member flag |
| `LEVEL_NUMBER` | NUMBER | Level in hierarchy |
| `GENERATION` | NUMBER | Generation number |
| `CREATED_BY` | VARCHAR2(100) | Created by |
| `CREATED_DATE` | DATE | Creation date |
| `UPDATED_BY` | VARCHAR2(100) | Updated by |
| `UPDATED_DATE` | DATE | Update date |

**Example Usage:**

```sql
-- Get all level 0 members
SELECT member_name, parent_name
  FROM ew_members_v
 WHERE app_name = 'HFM_PROD'
   AND dimension_name = 'Account'
   AND level_number = 0;

-- Find specific member
SELECT *
  FROM ew_members_v
 WHERE app_dimension_id = 123
   AND member_name = 'Revenue';

-- Get member with parent info
SELECT m.member_name,
       m.parent_name,
       p.member_name AS grandparent
  FROM ew_members_v m
  LEFT JOIN ew_members_v p
    ON m.parent_id = p.member_id
 WHERE m.app_dimension_id = 123;
```

### EW_MEMBER_PROPERTIES_V

Member property values.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `MEMBER_ID` | NUMBER | Member ID |
| `MEMBER_NAME` | VARCHAR2(255) | Member name |
| `APP_DIMENSION_ID` | NUMBER | App-dimension ID |
| `PROPERTY_ID` | NUMBER | Property ID |
| `PROPERTY_NAME` | VARCHAR2(100) | Property name |
| `PROPERTY_VALUE` | VARCHAR2(4000) | Property value |
| `PROPERTY_TYPE` | VARCHAR2(50) | Property data type |
| `IS_REQUIRED` | VARCHAR2(1) | Required property flag |

**Example Usage:**

```sql
-- Get all properties for a member
SELECT property_name, property_value
  FROM ew_member_properties_v
 WHERE member_name = 'Account123'
   AND app_dimension_id = 100;

-- Find members by property value
SELECT member_name
  FROM ew_member_properties_v
 WHERE property_name = 'ACCOUNT_TYPE'
   AND property_value = 'REVENUE';
```

## Hierarchy Views

### EW_HIERARCHY_MEMBERS_V

Optimized view for hierarchy operations.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `NODE_ID` | NUMBER | Hierarchy node ID |
| `MEMBER_ID` | NUMBER | Member ID |
| `MEMBER_NAME` | VARCHAR2(255) | Member name |
| `PARENT_ID` | NUMBER | Parent member ID |
| `PARENT_NAME` | VARCHAR2(255) | Parent name |
| `APP_DIMENSION_ID` | NUMBER | App-dimension ID |
| `HIERARCHY_TYPE` | VARCHAR2(50) | Hierarchy type |
| `LEVEL_NUMBER` | NUMBER | Level (0=leaf) |
| `GENERATION` | NUMBER | Generation (1=root) |
| `IS_LEAF` | VARCHAR2(1) | Leaf member flag |
| `CHILD_COUNT` | NUMBER | Number of children |
| `DESCENDANT_COUNT` | NUMBER | Total descendants |
| `PATH` | VARCHAR2(4000) | Full hierarchy path |
| `SORT_ORDER` | NUMBER | Sibling sort order |

**Example Usage:**

```sql
-- Get hierarchy tree
SELECT LPAD(' ', (level_number-1)*2) || member_name AS hierarchy,
       level_number,
       child_count
  FROM ew_hierarchy_members_v
 WHERE app_dimension_id = 123
 START WITH parent_name IS NULL
CONNECT BY PRIOR member_id = parent_id
 ORDER SIBLINGS BY sort_order;

-- Get all descendants
SELECT member_name
  FROM ew_hierarchy_members_v
 START WITH member_name = 'TotalExpenses'
CONNECT BY PRIOR member_id = parent_id;

-- Find leaf members under parent
SELECT member_name
  FROM ew_hierarchy_members_v
 WHERE app_dimension_id = 123
   AND is_leaf = 'Y'
 START WITH member_name = 'OperatingExpenses'
CONNECT BY PRIOR member_id = parent_id;
```

## Lookup Views

### EW_LOOKUP_CODES_V

System lookup values and codes.

**Columns:**

| Column Name | Data Type | Description |
|------------|-----------|-------------|
| `LOOKUP_TYPE` | VARCHAR2(50) | Lookup category |
| `LOOKUP_CODE` | VARCHAR2(50) | Code value |
| `LOOKUP_VALUE` | VARCHAR2(255) | Display value |
| `DESCRIPTION` | VARCHAR2(1000) | Description |
| `IS_ACTIVE` | VARCHAR2(1) | Active flag |
| `SORT_ORDER` | NUMBER | Display order |
| `PARENT_CODE` | VARCHAR2(50) | Parent for hierarchical lookups |

**Example Usage:**

```sql
-- Get all action codes
SELECT lookup_code, lookup_value, description
  FROM ew_lookup_codes_v
 WHERE lookup_type = 'ACTION_CODE'
   AND is_active = 'Y'
 ORDER BY sort_order;

-- Get specific lookup value
SELECT lookup_value
  FROM ew_lookup_codes_v
 WHERE lookup_type = 'MEMBER_TYPE'
   AND lookup_code = 'PARENT';
```

## Complex Queries

### Hierarchy Analysis

```sql
-- Member hierarchy with statistics
WITH hierarchy_stats AS (
  SELECT member_id,
         member_name,
         parent_name,
         level_number,
         COUNT(*) OVER (PARTITION BY parent_id) AS sibling_count,
         SUM(child_count) OVER (PARTITION BY parent_id) AS total_siblings_children
    FROM ew_hierarchy_members_v
   WHERE app_dimension_id = 123
)
SELECT member_name,
       parent_name,
       level_number,
       sibling_count,
       total_siblings_children
  FROM hierarchy_stats
 WHERE level_number <= 3
 ORDER BY level_number, member_name;
```

### Property Analysis

```sql
-- Members missing required properties
SELECT m.member_name,
       p.property_name AS missing_property
  FROM ew_members_v m
 CROSS JOIN (
   SELECT property_name
     FROM ew_properties_v
    WHERE is_required = 'Y'
      AND dimension_name = 'Account'
 ) p
 WHERE NOT EXISTS (
   SELECT 1
     FROM ew_member_properties_v mp
    WHERE mp.member_id = m.member_id
      AND mp.property_name = p.property_name
      AND mp.property_value IS NOT NULL
 )
   AND m.dimension_name = 'Account';
```

### Cross-Dimension Analysis

```sql
-- Find matching members across dimensions
SELECT a.member_name AS account_member,
       e.member_name AS entity_member
  FROM ew_members_v a
  JOIN ew_members_v e
    ON SUBSTR(a.member_name, 5) = SUBSTR(e.member_name, 4)
 WHERE a.dimension_name = 'Account'
   AND e.dimension_name = 'Entity'
   AND a.app_name = e.app_name;
```

## Performance Optimization

### Using Indexes

```sql
-- Indexed columns for fast access
-- APP_DIMENSION_ID + MEMBER_NAME
SELECT member_id, parent_name
  FROM ew_members_v
 WHERE app_dimension_id = 123
   AND member_name = 'Account123';

-- APP_ID + DIMENSION_NAME + MEMBER_NAME  
SELECT member_id
  FROM ew_members_v
 WHERE app_id = 10
   AND dimension_name = 'Account'
   AND member_name = 'Revenue';
```

### Avoiding Full Scans

```sql
-- Bad: Functions prevent index usage
SELECT * FROM ew_members_v
 WHERE UPPER(member_name) = 'ACCOUNT123';

-- Good: Direct comparison
SELECT * FROM ew_members_v
 WHERE member_name = 'Account123';

-- Bad: Leading wildcard
SELECT * FROM ew_members_v
 WHERE member_name LIKE '%123';

-- Good: Trailing wildcard
SELECT * FROM ew_members_v
 WHERE member_name LIKE 'Account%';
```

## View Permissions

### Checking Access

```sql
-- Verify view access
SELECT privilege
  FROM user_tab_privs
 WHERE table_name = 'EW_MEMBERS_V';

-- Check accessible columns
SELECT column_name, data_type
  FROM user_tab_columns
 WHERE table_name = 'EW_MEMBERS_V'
 ORDER BY column_id;
```

## Best Practices

1. **Always Filter by App/Dimension**
   - Reduces result set size
   - Improves query performance

2. **Use Specific Columns**
   - Select only needed columns
   - Avoid SELECT *

3. **Leverage Hierarchical Queries**
   - Use START WITH...CONNECT BY
   - More efficient than recursive joins

4. **Cache Static Data**
   - Store dimension IDs in variables
   - Minimize repeated lookups

5. **Handle NULLs Explicitly**
   - Check for NULL parents (root members)
   - Use NVL for default values

## Next Steps

- [Request Views](request-views.md)
- [Package APIs](../packages/)
- [Usage Examples](../../events/)