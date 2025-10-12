# Hierarchy Statistics API Functions

The Statistics API provides functions for calculating and retrieving statistical information about hierarchies, including member counts, levels, and aggregations.

**Package**: `EW_STATISTICS`  
**Usage**: `ew_statistics.<function_name>`

## Overview

The Statistics API enables:
- Hierarchy depth and breadth analysis
- Member count calculations
- Level and generation statistics
- Performance metrics
- Data density analysis

## Count Functions

### get_total_members

Returns the total number of members in a dimension.

```sql
FUNCTION get_total_members(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_total NUMBER;
BEGIN
  l_total := ew_statistics.get_total_members(
    p_app_dimension_id => 100
  );
  DBMS_OUTPUT.PUT_LINE('Total members: ' || l_total);
END;
```

### get_parent_count

Returns the number of parent members.

```sql
FUNCTION get_parent_count(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

### get_leaf_count

Returns the number of leaf (base) members.

```sql
FUNCTION get_leaf_count(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_parents NUMBER;
  l_leaves NUMBER;
  l_ratio NUMBER;
BEGIN
  l_parents := ew_statistics.get_parent_count(
    p_app_dimension_id => 100
  );
  
  l_leaves := ew_statistics.get_leaf_count(
    p_app_dimension_id => 100
  );
  
  l_ratio := ROUND(l_leaves / NULLIF(l_parents, 0), 2);
  
  DBMS_OUTPUT.PUT_LINE('Parents: ' || l_parents);
  DBMS_OUTPUT.PUT_LINE('Leaves: ' || l_leaves);
  DBMS_OUTPUT.PUT_LINE('Leaf/Parent Ratio: ' || l_ratio);
END;
```

## Hierarchy Depth Analysis

### get_max_level

Returns the maximum level (depth) of the hierarchy.

```sql
FUNCTION get_max_level(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

### get_max_generation

Returns the maximum generation in the hierarchy.

```sql
FUNCTION get_max_generation(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

### get_avg_depth

Returns the average depth of leaf members.

```sql
FUNCTION get_avg_depth(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_max_level NUMBER;
  l_max_gen NUMBER;
  l_avg_depth NUMBER;
BEGIN
  l_max_level := ew_statistics.get_max_level(
    p_app_dimension_id => 100
  );
  
  l_max_gen := ew_statistics.get_max_generation(
    p_app_dimension_id => 100
  );
  
  l_avg_depth := ew_statistics.get_avg_depth(
    p_app_dimension_id => 100
  );
  
  DBMS_OUTPUT.PUT_LINE('Max Level: ' || l_max_level);
  DBMS_OUTPUT.PUT_LINE('Max Generation: ' || l_max_gen);
  DBMS_OUTPUT.PUT_LINE('Average Depth: ' || ROUND(l_avg_depth, 2));
END;
```

## Member Distribution

### get_level_distribution

Returns member counts by level.

```sql
FUNCTION get_level_distribution(
  p_app_dimension_id IN NUMBER
) RETURN ew_global.g_number_tbl;
```

**Example:**
```sql
DECLARE
  l_distribution ew_global.g_number_tbl;
BEGIN
  l_distribution := ew_statistics.get_level_distribution(
    p_app_dimension_id => 100
  );
  
  FOR i IN 0..l_distribution.COUNT-1 LOOP
    DBMS_OUTPUT.PUT_LINE('Level ' || i || ': ' || 
                         l_distribution(i) || ' members');
  END LOOP;
END;
```

### get_children_statistics

Returns statistics about children per parent.

```sql
FUNCTION get_children_statistics(
  p_app_dimension_id IN NUMBER
) RETURN statistics_rec;
```

**Record Structure:**
```sql
TYPE statistics_rec IS RECORD (
  min_children    NUMBER,
  max_children    NUMBER,
  avg_children    NUMBER,
  median_children NUMBER,
  mode_children   NUMBER
);
```

**Example:**
```sql
DECLARE
  l_stats ew_statistics.statistics_rec;
BEGIN
  l_stats := ew_statistics.get_children_statistics(
    p_app_dimension_id => 100
  );
  
  DBMS_OUTPUT.PUT_LINE('Children per parent:');
  DBMS_OUTPUT.PUT_LINE('  Min: ' || l_stats.min_children);
  DBMS_OUTPUT.PUT_LINE('  Max: ' || l_stats.max_children);
  DBMS_OUTPUT.PUT_LINE('  Avg: ' || ROUND(l_stats.avg_children, 2));
  DBMS_OUTPUT.PUT_LINE('  Median: ' || l_stats.median_children);
END;
```

## Property Statistics

### get_property_fill_rate

Returns the percentage of members with a specific property populated.

```sql
FUNCTION get_property_fill_rate(
  p_app_dimension_id IN NUMBER,
  p_property_name    IN VARCHAR2
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_fill_rate NUMBER;
BEGIN
  l_fill_rate := ew_statistics.get_property_fill_rate(
    p_app_dimension_id => 100,
    p_property_name    => 'ACCOUNT_TYPE'
  );
  
  DBMS_OUTPUT.PUT_LINE('Account Type fill rate: ' || 
                       ROUND(l_fill_rate, 1) || '%');
END;
```

### get_property_value_distribution

Returns distribution of property values.

```sql
FUNCTION get_property_value_distribution(
  p_app_dimension_id IN NUMBER,
  p_property_name    IN VARCHAR2
) RETURN ew_global.g_name_value_tbl;
```

**Example:**
```sql
DECLARE
  l_distribution ew_global.g_name_value_tbl;
  l_value VARCHAR2(255);
BEGIN
  l_distribution := ew_statistics.get_property_value_distribution(
    p_app_dimension_id => 100,
    p_property_name    => 'ACCOUNT_TYPE'
  );
  
  l_value := l_distribution.FIRST;
  WHILE l_value IS NOT NULL LOOP
    DBMS_OUTPUT.PUT_LINE(l_value || ': ' || 
                         l_distribution(l_value) || ' members');
    l_value := l_distribution.NEXT(l_value);
  END LOOP;
END;
```

## Shared Member Statistics

### get_shared_member_count

Returns the count of shared members.

```sql
FUNCTION get_shared_member_count(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

### get_sharing_statistics

Returns statistics about member sharing.

```sql
FUNCTION get_sharing_statistics(
  p_app_dimension_id IN NUMBER
) RETURN sharing_stats_rec;
```

**Record Structure:**
```sql
TYPE sharing_stats_rec IS RECORD (
  total_shared_members   NUMBER,
  max_shares_per_member  NUMBER,
  avg_shares_per_member  NUMBER,
  members_shared_once    NUMBER,
  members_shared_multiple NUMBER
);
```

## Performance Metrics

### calculate_hierarchy_complexity

Calculates a complexity score for the hierarchy.

```sql
FUNCTION calculate_hierarchy_complexity(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_complexity NUMBER;
BEGIN
  l_complexity := ew_statistics.calculate_hierarchy_complexity(
    p_app_dimension_id => 100
  );
  
  DBMS_OUTPUT.PUT_LINE('Hierarchy Complexity Score: ' || 
                       ROUND(l_complexity, 2));
  
  IF l_complexity > 80 THEN
    DBMS_OUTPUT.PUT_LINE('Warning: High complexity hierarchy');
  END IF;
END;
```

### get_balancing_score

Returns a score indicating how balanced the hierarchy is.

```sql
FUNCTION get_balancing_score(
  p_app_dimension_id IN NUMBER
) RETURN NUMBER;  -- Returns 0-100 (100 = perfectly balanced)
```

## Data Analysis

### get_orphaned_members

Returns members without valid parents.

```sql
FUNCTION get_orphaned_members(
  p_app_dimension_id IN NUMBER
) RETURN ew_global.g_value_tbl;
```

### get_duplicate_members

Finds duplicate member names.

```sql
FUNCTION get_duplicate_members(
  p_app_dimension_id IN NUMBER
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_orphans ew_global.g_value_tbl;
  l_duplicates ew_global.g_value_tbl;
BEGIN
  -- Check for orphaned members
  l_orphans := ew_statistics.get_orphaned_members(
    p_app_dimension_id => 100
  );
  
  IF l_orphans.COUNT > 0 THEN
    DBMS_OUTPUT.PUT_LINE('Found ' || l_orphans.COUNT || ' orphaned members');
    FOR i IN 1..l_orphans.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE('  - ' || l_orphans(i));
    END LOOP;
  END IF;
  
  -- Check for duplicates
  l_duplicates := ew_statistics.get_duplicate_members(
    p_app_dimension_id => 100
  );
  
  IF l_duplicates.COUNT > 0 THEN
    DBMS_OUTPUT.PUT_LINE('Found duplicates: ' || l_duplicates.COUNT);
  END IF;
END;
```

## Reporting Functions

### generate_hierarchy_report

Generates a comprehensive hierarchy statistics report.

```sql
FUNCTION generate_hierarchy_report(
  p_app_dimension_id IN NUMBER,
  p_format           IN VARCHAR2 DEFAULT 'TEXT'
) RETURN CLOB;
```

**Example:**
```sql
DECLARE
  l_report CLOB;
BEGIN
  l_report := ew_statistics.generate_hierarchy_report(
    p_app_dimension_id => 100,
    p_format           => 'HTML'
  );
  
  -- Save or display report
  save_report_to_file(l_report);
END;
```

### compare_hierarchies

Compares statistics between two hierarchies.

```sql
FUNCTION compare_hierarchies(
  p_app_dimension_id1 IN NUMBER,
  p_app_dimension_id2 IN NUMBER
) RETURN comparison_rec;
```

## Advanced Statistics

### Calculate Growth Rate

```sql
DECLARE
  l_current_count NUMBER;
  l_previous_count NUMBER;
  l_growth_rate NUMBER;
BEGIN
  -- Get current member count
  l_current_count := ew_statistics.get_total_members(
    p_app_dimension_id => 100
  );
  
  -- Get count from 30 days ago (from history)
  SELECT member_count
    INTO l_previous_count
    FROM hierarchy_statistics_history
   WHERE app_dimension_id = 100
     AND stat_date = TRUNC(SYSDATE - 30);
  
  -- Calculate growth rate
  l_growth_rate := ((l_current_count - l_previous_count) / 
                    l_previous_count) * 100;
  
  DBMS_OUTPUT.PUT_LINE('30-day growth rate: ' || 
                       ROUND(l_growth_rate, 2) || '%');
END;
```

### Hierarchy Health Check

```sql
DECLARE
  l_health_score NUMBER := 100;
  l_issues VARCHAR2(4000);
  
  PROCEDURE check_metric(
    p_metric_name  VARCHAR2,
    p_metric_value NUMBER,
    p_threshold    NUMBER,
    p_penalty      NUMBER
  ) IS
  BEGIN
    IF p_metric_value > p_threshold THEN
      l_health_score := l_health_score - p_penalty;
      l_issues := l_issues || p_metric_name || ' exceeds threshold; ';
    END IF;
  END;
  
BEGIN
  -- Check various health metrics
  check_metric(
    'Orphaned Members',
    ew_statistics.get_orphaned_members(100).COUNT,
    0,
    20
  );
  
  check_metric(
    'Max Level',
    ew_statistics.get_max_level(100),
    10,
    10
  );
  
  check_metric(
    'Complexity',
    ew_statistics.calculate_hierarchy_complexity(100),
    75,
    15
  );
  
  DBMS_OUTPUT.PUT_LINE('Hierarchy Health Score: ' || l_health_score);
  IF l_issues IS NOT NULL THEN
    DBMS_OUTPUT.PUT_LINE('Issues: ' || l_issues);
  END IF;
END;
```

## Caching Statistics

```sql
DECLARE
  g_stats_cache ew_statistics.statistics_rec;
  g_cache_time DATE;
  
  FUNCTION get_cached_stats(p_dim_id NUMBER) 
  RETURN ew_statistics.statistics_rec IS
  BEGIN
    -- Refresh cache if older than 1 hour
    IF g_cache_time IS NULL OR 
       g_cache_time < SYSDATE - 1/24 THEN
      g_stats_cache := ew_statistics.get_children_statistics(p_dim_id);
      g_cache_time := SYSDATE;
    END IF;
    RETURN g_stats_cache;
  END;
BEGIN
  -- Use cached statistics
  FOR i IN 1..100 LOOP
    l_stats := get_cached_stats(100);
  END LOOP;
END;
```

## Best Practices

1. **Cache Statistics for Performance**
   ```sql
   -- Store frequently used stats
   g_total_members := ew_statistics.get_total_members(p_dim_id);
   ```

2. **Use Appropriate Granularity**
   ```sql
   -- Get summary vs detailed stats based on need
   IF need_details THEN
     l_dist := get_level_distribution(p_dim_id);
   ELSE
     l_count := get_total_members(p_dim_id);
   END IF;
   ```

3. **Monitor Trends**
   ```sql
   -- Track statistics over time
   INSERT INTO stats_history
   VALUES (SYSDATE, get_total_members(100));
   ```

4. **Set Thresholds**
   ```sql
   IF get_max_level(100) > 10 THEN
     alert('Hierarchy too deep');
   END IF;
   ```

## Next Steps

- [Application APIs](application.md)
- [Workflow APIs](workflow.md)
- [String APIs](string.md)