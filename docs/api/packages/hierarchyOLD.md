# Hierarchy API Functions

The Hierarchy package (`EW_HIERARCHY`) provides comprehensive functions for managing and querying dimension hierarchies, members, and their relationships.

**Package**: `EW_HIERARCHY`  
**Usage**: `ew_hierarchy.<function_name>`

## Core Functions

### Get Member Information

#### get_member_name

Returns the actual member name with correct case sensitivity.

```sql
FUNCTION get_member_name(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN VARCHAR2;
```

**Parameters:**
- `p_app_dimension_id` - Dimension identifier
- `p_member_name` - Member name to verify

**Returns:** Actual member name or NULL if not found

**Example:**
```sql
DECLARE
  l_member_name VARCHAR2(100);
BEGIN
  l_member_name := ew_hierarchy.get_member_name(
    p_app_dimension_id => 123,
    p_member_name      => 'account100'  -- Case insensitive search
  );
  -- Returns: 'Account100' (with correct case)
END;
```

#### get_member_id

Returns the internal member ID for a given member name.

```sql
FUNCTION get_member_id(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN NUMBER;
```

**Example:**
```sql
l_member_id := ew_hierarchy.get_member_id(
  p_app_dimension_id => ew_lb_api.g_app_dimension_id,
  p_member_name      => 'TotalExpenses'
);
```

### Check Member Existence

#### chk_member_exists

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
IF ew_hierarchy.chk_member_exists(
     p_app_name    => 'HFM_PROD',
     p_dim_name    => 'Account',
     p_member_name => 'Revenue'
   ) = 'Y' THEN
  -- Member exists
END IF;
```

### Node Operations

#### chk_node_exists

Checks if a specific parent-child relationship exists.

```sql
FUNCTION chk_node_exists(
  p_app_dimension_id   IN NUMBER,
  p_parent_member_name IN VARCHAR2,
  p_member_name        IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

![Node Existence Check](../../assets/images/node-existence-diagram.png)
*Figure: Node existence checking parent-child relationships*

### Hierarchy Navigation

#### get_primary_parent_name

Returns the primary parent of a member (excluding shared instances).

```sql
FUNCTION get_primary_parent_name(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
l_parent := ew_hierarchy.get_primary_parent_name(
  p_app_dimension_id => 100,
  p_member_name      => 'Account123'
);
```

#### get_branch_member

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
-- Get the 3rd level ancestor from top
l_ancestor := ew_hierarchy.get_branch_member(
  p_app_dimension_id => 100,
  p_member_name      => 'A12345',
  p_level            => 3
);
```

### Property Management

#### get_member_prop_value

Retrieves property values for members.

```sql
-- Simple property retrieval
FUNCTION get_member_prop_value(
  p_app_name    IN VARCHAR2,
  p_dim_name    IN VARCHAR2,
  p_member_name IN VARCHAR2,
  p_prop_label  IN VARCHAR2
) RETURN VARCHAR2;

-- With array member support (for aliases)
FUNCTION get_member_prop_value(
  p_prop_label   IN VARCHAR2,
  p_hierarchy_id IN NUMBER,
  p_app_dimension_id IN NUMBER
) RETURN VARCHAR2;
```

**Example with Alias:**
```sql
-- Get English alias
l_alias := ew_hierarchy.get_member_prop_value(
  p_app_name    => 'PLANNING',
  p_dim_name    => 'Entity',
  p_member_name => 'E100',
  p_prop_label  => 'Alias:English'
);
```

### Member Type Checking

#### is_leaf

Determines if a member is a base (leaf) member.

```sql
FUNCTION is_leaf(
  p_member_id        IN NUMBER,
  p_app_dimension_id IN NUMBER
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

#### is_parent_member

Checks if a member has children.

```sql
FUNCTION is_parent_member(
  p_member_id IN NUMBER
) RETURN VARCHAR2;
```

### Descendant Operations

#### get_descendants_count

Returns the count of all descendants under a member.

```sql
FUNCTION get_descendants_count(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2
) RETURN NUMBER;
```

#### get_descendants

Retrieves all descendants into a collection.

```sql
PROCEDURE get_descendants(
  p_app_dimension_id  IN NUMBER,
  p_member_id         IN NUMBER,
  p_node_type         IN VARCHAR2,
  x_hier_members_tbl OUT g_hier_members_tbl
);
```

**Parameters:**
- `p_node_type` - Filter by type: 'BASE_MEMBERS', 'PARENT_MEMBERS', 'ALL'

**Example:**
```sql
DECLARE
  l_descendants ew_hierarchy.g_hier_members_tbl;
BEGIN
  ew_hierarchy.get_descendants(
    p_app_dimension_id => 100,
    p_member_id        => 5000,
    p_node_type        => 'BASE_MEMBERS',
    x_hier_members_tbl => l_descendants
  );
  
  FOR i IN 1..l_descendants.COUNT LOOP
    DBMS_OUTPUT.put_line(l_descendants(i).member_name);
  END LOOP;
END;
```

### Branch Validation

#### chk_primary_branch_exists

Verifies if a member exists under a specific top-level parent.

```sql
FUNCTION chk_primary_branch_exists(
  p_app_dimension_id   IN NUMBER,
  p_parent_member_name IN VARCHAR2,  -- Top level parent
  p_member_name        IN VARCHAR2,
  p_chk_deleted        IN VARCHAR2 DEFAULT 'N'
) RETURN VARCHAR2;
```

![Branch Validation Example](../../assets/images/branch-validation.png)
*Figure: Branch validation checking member hierarchy paths*

**Use Case:** Verify if account 'A12345' exists under 'BalanceSheet' branch:

```sql
IF ew_hierarchy.chk_primary_branch_exists(
     p_app_dimension_id   => 100,
     p_parent_member_name => 'BalanceSheet',
     p_member_name        => 'A12345'
   ) = 'Y' THEN
  -- Member is in Balance Sheet branch
END IF;
```

### Advanced Property Search

#### ancestors_having_prop_value

Finds ancestors with specific property values.

```sql
FUNCTION ancestors_having_prop_value(
  p_app_dimension_id IN NUMBER,
  p_member_name      IN VARCHAR2,
  p_prop_name        IN VARCHAR2,
  p_prop_value       IN VARCHAR2,
  p_sep              IN VARCHAR2 DEFAULT ',',
  p_list_or_count    IN VARCHAR2 DEFAULT 'LIST',
  p_append_wildcard  IN VARCHAR2 DEFAULT 'N'
) RETURN VARCHAR2;
```

**Parameters:**
- `p_list_or_count` - Return format: 'LIST', 'COUNT', 'EXISTS', 'FIRST', 'LAST'
- `p_append_wildcard` - Use wildcards in property value matching

**Example:**
```sql
-- Find all ancestors with AccountType = 'Asset'
l_ancestors := ew_hierarchy.ancestors_having_prop_value(
  p_app_dimension_id => 100,
  p_member_name      => 'A12345',
  p_prop_name        => 'AccountType',
  p_prop_value       => 'Asset',
  p_list_or_count    => 'LIST'
);
-- Returns: 'Assets,CurrentAssets,CashAndEquivalents'
```

### Utility Functions

#### set_dim_mapping_method

Applies standard mapping methods within custom scripts.

```sql
PROCEDURE set_dim_mapping_method(
  p_mapping_method IN VARCHAR2,  -- 'SYNC' or 'SMARTSYNC'
  x_status        OUT VARCHAR2,
  x_message       OUT VARCHAR2
);
```

**Use Case:** Fallback to standard sync for certain conditions:

```sql
IF l_use_standard_sync THEN
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SMARTSYNC',
    x_status         => ew_lb_api.g_status,
    x_message        => ew_lb_api.g_message
  );
END IF;
```

## Collection Types

### g_hier_members_tbl

Table type for hierarchy member records:

```sql
TYPE g_hier_members_tbl IS TABLE OF ew_hierarchy_members_v%ROWTYPE
  INDEX BY BINARY_INTEGER;
```

**Record Fields:**
- `hierarchy_id` - Unique node identifier
- `member_id` - Member identifier
- `member_name` - Member name
- `parent_member_id` - Parent identifier
- `parent_member_name` - Parent name
- `primary_flag` - Primary instance indicator ('Y'/'N')
- `sort_order` - Position within parent

## Performance Best Practices

### 1. Cache Frequently Used Values

```sql
-- Bad: Multiple calls
FOR i IN 1..100 LOOP
  IF ew_hierarchy.is_leaf(p_member_id, p_dim_id) = 'Y' THEN...
END LOOP;

-- Good: Cache the result
l_is_leaf := ew_hierarchy.is_leaf(p_member_id, p_dim_id);
FOR i IN 1..100 LOOP
  IF l_is_leaf = 'Y' THEN...
END LOOP;
```

### 2. Use Member IDs When Available

```sql
-- Slower: Using names (requires lookup)
l_parent := ew_hierarchy.get_parent_member_name(p_dim_id, 'Account123');

-- Faster: Using IDs (direct access)
l_parent_id := ew_hierarchy.get_primary_parent_id(l_member_id);
```

### 3. Bulk Operations for Multiple Members

```sql
-- Use get_descendants for bulk retrieval instead of loops
ew_hierarchy.get_descendants(
  p_app_dimension_id => l_dim_id,
  p_member_id        => l_parent_id,
  p_node_type        => 'ALL',
  x_hier_members_tbl => l_members
);
```

## Common Patterns

### Pattern 1: Validate Member Before Operations

```sql
BEGIN
  -- Always check existence before operations
  IF ew_hierarchy.chk_member_exists(
       p_app_dimension_id => l_dim_id,
       p_member_name      => l_new_member
     ) = 'N' THEN
    
    -- Safe to create new member
    ew_req_api.create_line_new_member(...);
    
  ELSE
    -- Member exists, handle accordingly
    ew_lb_api.g_message := 'Member already exists: ' || l_new_member;
  END IF;
END;
```

### Pattern 2: Navigate Hierarchy Safely

```sql
DECLARE
  l_current_member VARCHAR2(100) := p_start_member;
  l_level          NUMBER := 0;
BEGIN
  -- Navigate up the hierarchy
  WHILE l_current_member IS NOT NULL AND l_level < 10 LOOP
    -- Process current member
    process_member(l_current_member);
    
    -- Get parent
    l_current_member := ew_hierarchy.get_primary_parent_name(
      p_app_dimension_id => l_dim_id,
      p_member_name      => l_current_member
    );
    
    l_level := l_level + 1;
  END LOOP;
END;
```

## Error Handling

Always include proper exception handling when using hierarchy APIs:

```sql
BEGIN
  l_member_id := ew_hierarchy.get_member_id(
    p_app_dimension_id => l_dim_id,
    p_member_name      => l_member
  );
  
  IF l_member_id IS NULL THEN
    RAISE_APPLICATION_ERROR(-20001, 'Member not found: ' || l_member);
  END IF;
  
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    ew_lb_api.g_message := 'Invalid hierarchy structure';
  WHEN OTHERS THEN
    ew_lb_api.g_message := 'Hierarchy API error: ' || SQLERRM;
    ew_debug.log('Error in hierarchy operation: ' || SQLERRM);
END;
```

## Related APIs

- [Request APIs](request.md) - For creating hierarchy change requests
- [Statistics APIs](statistics.md) - For hierarchy statistics and metrics
- [String APIs](string.md) - For member name manipulation
- [In-Memory Functions](in-memory.md) - For accessing uncommitted changes