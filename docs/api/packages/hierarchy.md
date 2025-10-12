# Hierarchy API Functions

The Hierarchy package provides comprehensive functions for managing and querying dimension hierarchies, members, and their relationships.

**Package**: `EW_HIERARCHY`  
**Usage**: `ew_hierarchy.<function_name>`

## Member Information Functions

### get_member_name

Returns the actual member name with correct case sensitivity.

```sql
FUNCTION get_member_name(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN VARCHAR2;
```

**Parameters:**
- `p_app_dimension_id` - Dimension identifier
- `p_member_name` - Member name to verify (case-insensitive search)

**Returns:** Actual member name with correct case or NULL if not found

**Example:**
```sql
DECLARE
  l_member_name VARCHAR2(255);
BEGIN
  l_member_name := ew_hierarchy.get_member_name(
    p_app_dimension_id => 123,
    p_member_name      => 'account100'  -- Case insensitive
  );
  -- Returns: 'Account100' (with correct case)
  DBMS_OUTPUT.PUT_LINE('Actual name: ' || l_member_name);
END;
```

### get_member_id

Returns the internal member ID for a given member name.

```sql
FUNCTION get_member_id(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_member_id NUMBER;
BEGIN
  l_member_id := ew_hierarchy.get_member_id(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_name      => 'TotalExpenses'
  );
  
  IF l_member_id IS NOT NULL THEN
    DBMS_OUTPUT.PUT_LINE('Member ID: ' || l_member_id);
  END IF;
END;
```

## Member Existence Checking

### chk_member_exists

Verifies if a member exists in a dimension.

```sql
-- Check by dimension ID
FUNCTION chk_member_exists(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_case_match       IN VARCHAR2 DEFAULT 'N'
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'

-- Check by application and dimension names
FUNCTION chk_member_exists(
  p_app_name    IN VARCHAR2,
  p_dim_name    IN VARCHAR2,
  p_member_name IN VARCHAR2,
  p_case_match  IN VARCHAR2 DEFAULT 'N'
) RETURN VARCHAR2;
```

**Parameters:**
- `p_case_match` - Enforce case-sensitive matching ('Y'/'N')

**Example:**
```sql
BEGIN
  IF ew_hierarchy.chk_member_exists(
       p_app_name    => 'HFM_PROD',
       p_dim_name    => 'Account',
       p_member_name => 'Revenue'
     ) = 'Y' THEN
    DBMS_OUTPUT.PUT_LINE('Member exists');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Member not found');
  END IF;
END;
```

### chk_node_exists

Checks if a specific parent-child relationship exists.

```sql
FUNCTION chk_node_exists(
  p_app_dimension_id   IN NUMBER,
  p_parent_member_name IN VARCHAR2,
  p_member_name        IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
IF ew_hierarchy.chk_node_exists(
     p_app_dimension_id   => 100,
     p_parent_member_name => 'TotalRevenue',
     p_member_name        => 'ProductRevenue'
   ) = 'Y' THEN
  -- Parent-child relationship exists
  DBMS_OUTPUT.PUT_LINE('Node relationship confirmed');
END IF;
```

## Hierarchy Navigation

### get_primary_parent_name

Returns the primary parent of a member (excluding shared instances).

```sql
FUNCTION get_primary_parent_name(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_parent VARCHAR2(255);
BEGIN
  l_parent := ew_hierarchy.get_primary_parent_name(
    p_app_dimension_id => 100,
    p_member_name      => 'Account123'
  );
  DBMS_OUTPUT.PUT_LINE('Primary parent: ' || l_parent);
END;
```

### get_branch_member

Retrieves a specific ancestor at a given level.

```sql
FUNCTION get_branch_member(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_level            IN NUMBER
) RETURN VARCHAR2;
```

**Parameters:**
- `p_level` - Positive: count from top (1=root), Negative: count from member (-1=parent)

**Example:**
```sql
DECLARE
  l_ancestor VARCHAR2(255);
BEGIN
  -- Get the 3rd level ancestor from top
  l_ancestor := ew_hierarchy.get_branch_member(
    p_app_dimension_id => 100,
    p_member_name      => 'A12345',
    p_level            => 3
  );
  
  -- Get immediate parent
  l_ancestor := ew_hierarchy.get_branch_member(
    p_app_dimension_id => 100,
    p_member_name      => 'A12345',
    p_level            => -1
  );
END;
```

### get_all_parents

Returns all parents of a member (including shared).

```sql
FUNCTION get_all_parents(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_parents ew_global.g_value_tbl;
BEGIN
  l_parents := ew_hierarchy.get_all_parents(
    p_app_dimension_id => 100,
    p_member_name      => 'SharedAccount'
  );
  
  FOR i IN 1..l_parents.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('Parent ' || i || ': ' || l_parents(i));
  END LOOP;
END;
```

## Property Management

### get_member_prop_value

Retrieves property values for members.

```sql
-- Simple property retrieval
FUNCTION get_member_prop_value(
  p_app_name    IN VARCHAR2,
  p_dim_name    IN VARCHAR2,
  p_member_name IN VARCHAR2,
  p_prop_label  IN VARCHAR2
) RETURN VARCHAR2;

-- With member ID
FUNCTION get_member_prop_value(
  p_member_id  IN NUMBER,
  p_prop_label IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_account_type VARCHAR2(50);
  l_alias VARCHAR2(255);
BEGIN
  -- Get account type
  l_account_type := ew_hierarchy.get_member_prop_value(
    p_app_name    => 'PLANNING',
    p_dim_name    => 'Account',
    p_member_name => 'Revenue',
    p_prop_label  => 'ACCOUNT_TYPE'
  );
  
  -- Get English alias
  l_alias := ew_hierarchy.get_member_prop_value(
    p_app_name    => 'PLANNING',
    p_dim_name    => 'Entity',
    p_member_name => 'E100',
    p_prop_label  => 'Alias:English'
  );
END;
```

### set_member_prop_value

Updates a member's property value.

```sql
PROCEDURE set_member_prop_value(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_prop_label       IN VARCHAR2,
  p_prop_value       IN VARCHAR2
);
```

**Example:**
```sql
BEGIN
  ew_hierarchy.set_member_prop_value(
    p_app_dimension_id => 100,
    p_member_name      => 'Account123',
    p_prop_label       => 'ACCOUNT_TYPE',
    p_prop_value       => 'EXPENSE'
  );
  COMMIT;
END;
```

## Member Type Functions

### is_leaf

Determines if a member is a base (leaf) member.

```sql
FUNCTION is_leaf(
  p_member_id        IN NUMBER,
  p_app_dimension_id IN NUMBER
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
DECLARE
  l_member_id NUMBER;
  l_is_leaf VARCHAR2(1);
BEGIN
  l_member_id := ew_hierarchy.get_member_id(
    p_app_dimension_id => 100,
    p_member_name      => 'Account123'
  );
  
  l_is_leaf := ew_hierarchy.is_leaf(
    p_member_id        => l_member_id,
    p_app_dimension_id => 100
  );
  
  IF l_is_leaf = 'Y' THEN
    DBMS_OUTPUT.PUT_LINE('Member is a leaf node');
  END IF;
END;
```

### is_parent_member

Checks if a member has children.

```sql
FUNCTION is_parent_member(
  p_member_id IN NUMBER
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### get_member_type

Returns the member's type classification.

```sql
FUNCTION get_member_type(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'PARENT', 'LEAF', 'SHARED', etc.
```

## Descendant Operations

### get_descendants

Retrieves all descendants of a member.

```sql
FUNCTION get_descendants(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_include_shared   IN VARCHAR2 DEFAULT 'N'
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_descendants ew_global.g_value_tbl;
BEGIN
  l_descendants := ew_hierarchy.get_descendants(
    p_app_dimension_id => 100,
    p_member_name      => 'TotalExpenses',
    p_include_shared   => 'Y'
  );
  
  DBMS_OUTPUT.PUT_LINE('Found ' || l_descendants.COUNT || ' descendants');
  
  FOR i IN 1..l_descendants.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(i || ': ' || l_descendants(i));
  END LOOP;
END;
```

### get_descendants_count

Returns the count of all descendants under a member.

```sql
FUNCTION get_descendants_count(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN NUMBER;
```

### get_leaf_descendants

Returns only leaf-level descendants.

```sql
FUNCTION get_leaf_descendants(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_leaves ew_global.g_value_tbl;
  l_total NUMBER;
BEGIN
  -- Get all leaf members under TotalRevenue
  l_leaves := ew_hierarchy.get_leaf_descendants(
    p_app_dimension_id => 100,
    p_member_name      => 'TotalRevenue'
  );
  
  -- Calculate totals for leaf members
  l_total := 0;
  FOR i IN 1..l_leaves.COUNT LOOP
    l_total := l_total + get_member_value(l_leaves(i));
  END LOOP;
  
  DBMS_OUTPUT.PUT_LINE('Total for leaves: ' || l_total);
END;
```

## Sibling Operations

### get_siblings

Returns all siblings of a member.

```sql
FUNCTION get_siblings(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_include_self     IN VARCHAR2 DEFAULT 'N'
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_siblings ew_global.g_value_tbl;
BEGIN
  l_siblings := ew_hierarchy.get_siblings(
    p_app_dimension_id => 100,
    p_member_name      => 'Q1',
    p_include_self     => 'N'
  );
  
  -- Should return Q2, Q3, Q4
  FOR i IN 1..l_siblings.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('Sibling: ' || l_siblings(i));
  END LOOP;
END;
```

### get_next_sibling

Returns the next sibling in order.

```sql
FUNCTION get_next_sibling(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN VARCHAR2;
```

## Advanced Hierarchy Functions

### get_hierarchy_path

Returns the full path from root to member.

```sql
FUNCTION get_hierarchy_path(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_delimiter        IN VARCHAR2 DEFAULT '.'
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_path VARCHAR2(4000);
BEGIN
  l_path := ew_hierarchy.get_hierarchy_path(
    p_app_dimension_id => 100,
    p_member_name      => 'Marketing',
    p_delimiter        => ' > '
  );
  -- Returns: TotalExpenses > Operating > Marketing
  DBMS_OUTPUT.PUT_LINE('Path: ' || l_path);
END;
```

### get_generation_members

Returns all members at a specific generation.

```sql
FUNCTION get_generation_members(
  p_app_dimension_id IN NUMBER,
  p_generation       IN NUMBER
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_gen2_members ew_global.g_value_tbl;
BEGIN
  -- Get all generation 2 members
  l_gen2_members := ew_hierarchy.get_generation_members(
    p_app_dimension_id => 100,
    p_generation       => 2
  );
  
  FOR i IN 1..l_gen2_members.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('Gen 2: ' || l_gen2_members(i));
  END LOOP;
END;
```

### get_level_members

Returns all members at a specific level.

```sql
FUNCTION get_level_members(
  p_app_dimension_id IN NUMBER,
  p_level            IN NUMBER
) RETURN ew_global.g_value_tbl;
```

## Shared Member Functions

### is_shared_member

Checks if a member is shared.

```sql
FUNCTION is_shared_member(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_parent_name      IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### get_shared_locations

Returns all locations where a member is shared.

```sql
FUNCTION get_shared_locations(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_shared_parents ew_global.g_value_tbl;
BEGIN
  l_shared_parents := ew_hierarchy.get_shared_locations(
    p_app_dimension_id => 100,
    p_member_name      => 'SharedAccount'
  );
  
  FOR i IN 1..l_shared_parents.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE('Shared under: ' || l_shared_parents(i));
  END LOOP;
END;
```

## Utility Functions

### copy_member_properties

Copies all properties from one member to another.

```sql
PROCEDURE copy_member_properties(
  p_app_dimension_id IN NUMBER,
  p_source_member    IN VARCHAR2,
  p_target_member    IN VARCHAR2
);
```

**Example:**
```sql
BEGIN
  -- Copy all properties from template member
  ew_hierarchy.copy_member_properties(
    p_app_dimension_id => 100,
    p_source_member    => 'Template_Account',
    p_target_member    => 'New_Account'
  );
  COMMIT;
END;
```

### validate_member_name

Validates if a member name meets requirements.

```sql
FUNCTION validate_member_name(
  p_member_name IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' if valid, 'N' if invalid
```

## Performance Optimization

### Bulk Member Operations

```sql
DECLARE
  l_members ew_global.g_value_tbl;
  l_parents ew_global.g_value_tbl;
BEGIN
  -- Get members and parents in bulk
  SELECT member_name, parent_name
    BULK COLLECT INTO l_members, l_parents
    FROM hierarchy_table
   WHERE app_dimension_id = 100;
  
  -- Process in bulk
  FOR i IN 1..l_members.COUNT LOOP
    -- Process each member efficiently
    NULL;
  END LOOP;
END;
```

### Caching Hierarchy Data

```sql
DECLARE
  -- Cache frequently accessed data
  g_hierarchy_cache ew_global.g_name_value_tbl;
  
  FUNCTION get_cached_parent(p_member VARCHAR2) RETURN VARCHAR2 IS
  BEGIN
    IF NOT g_hierarchy_cache.EXISTS(p_member) THEN
      g_hierarchy_cache(p_member) := ew_hierarchy.get_primary_parent_name(
        p_app_dimension_id => 100,
        p_member_name      => p_member
      );
    END IF;
    RETURN g_hierarchy_cache(p_member);
  END;
BEGIN
  -- Use cached values
  FOR i IN 1..1000 LOOP
    l_parent := get_cached_parent('Account123');
  END LOOP;
END;
```

## Error Handling

```sql
BEGIN
  l_member_id := ew_hierarchy.get_member_id(
    p_app_dimension_id => 100,
    p_member_name      => 'InvalidMember'
  );
  
  IF l_member_id IS NULL THEN
    -- Member not found
    DBMS_OUTPUT.PUT_LINE('Member does not exist');
  END IF;
  
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('Member not found');
  WHEN TOO_MANY_ROWS THEN
    DBMS_OUTPUT.PUT_LINE('Multiple members found - check for duplicates');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
```

## Best Practices

1. **Check Existence Before Operations**
   ```sql
   IF ew_hierarchy.chk_member_exists(...) = 'Y' THEN
     -- Safe to proceed
   END IF;
   ```

2. **Use Appropriate Functions**
   ```sql
   -- Use is_leaf instead of checking children
   IF ew_hierarchy.is_leaf(...) = 'Y' THEN
     -- Process leaf member
   END IF;
   ```

3. **Handle NULL Returns**
   ```sql
   l_parent := NVL(ew_hierarchy.get_primary_parent_name(...), 'NO_PARENT');
   ```

4. **Cache Frequently Used Data**
   ```sql
   -- Store dimension ID once
   g_dim_id := get_app_dimension_id('Account');
   ```

## Next Steps

- [Statistics APIs](statistics.md)
- [Request APIs](request.md)
- [Application APIs](application.md)