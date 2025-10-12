# Dimension Mapping Output Parameters

Output parameters control how the dimension mapping operation is executed in the target dimension. These parameters must be set correctly to ensure proper synchronization.

## Core Output Parameters

### Status and Message

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `g_status` | VARCHAR2 | Yes | Operation status ('S' or 'E') |
| `g_message` | VARCHAR2 | Conditional | Error message when status is 'E' |

**Setting Status:**
```sql
-- Success
ew_lb_api.g_status := ew_lb_api.g_success;  -- Sets 'S'

-- Error
ew_lb_api.g_status := ew_lb_api.g_error;    -- Sets 'E'
ew_lb_api.g_message := 'Custom error message';
```

### Operation Control

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `g_out_ignore_flag` | VARCHAR2 | 'N' | Set to 'Y' to skip this operation |
| `g_out_allow_dup_flag` | VARCHAR2 | 'N' | Allow duplicate members ('Y'/'N') |

![Operation Control Flow](../../assets/images/operation-control-flow.png)
*Figure: How output parameters control dimension mapping operations*

## Member Mapping Parameters

### Basic Member Mapping

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_out_member_name` | VARCHAR2 | Mapped member name in target |
| `g_out_parent_member_name` | VARCHAR2 | Mapped parent name in target |

**Example - Transform Member Names:**
```sql
-- Add prefix to member names
ew_lb_api.g_out_member_name := 'BU_' || ew_lb_api.g_member_name;
ew_lb_api.g_out_parent_member_name := 'BU_' || ew_lb_api.g_parent_member_name;
```

### Rename Operations

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_out_new_member_name` | VARCHAR2 | New name for rename operations |
| `g_out_old_member_name` | VARCHAR2 | Original name for tracking |

**Example - Handle Renames:**
```sql
IF ew_lb_api.g_action_code = 'R' THEN
  ew_lb_api.g_out_old_member_name := ew_lb_api.g_renamed_from_member_name;
  ew_lb_api.g_out_new_member_name := 'NEW_' || ew_lb_api.g_member_name;
END IF;
```

### Move Operations

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_out_moved_to_member_name` | VARCHAR2 | Target parent for move operations |
| `g_out_moved_from_member_name` | VARCHAR2 | Source parent for tracking |

**Example - Redirect Moves:**
```sql
IF ew_lb_api.g_action_code IN ('M', 'ZC') THEN
  -- Redirect all moves to a specific parent
  ew_lb_api.g_out_moved_to_member_name := 'UNMAPPED_ENTITIES';
END IF;
```

## Advanced Mapping Parameters

### Shared Members

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_out_shared_members_tbl` | ARRAY | Array of shared member locations |
| `g_out_shared_parent_tbl` | ARRAY | Parents for shared members |

**Working with Shared Members:**
```sql
DECLARE
  l_idx NUMBER := 0;
BEGIN
  -- Add shared member instances
  l_idx := l_idx + 1;
  ew_lb_api.g_out_shared_members_tbl(l_idx) := 'SharedMember1';
  ew_lb_api.g_out_shared_parent_tbl(l_idx) := 'Parent1';
  
  l_idx := l_idx + 1;
  ew_lb_api.g_out_shared_members_tbl(l_idx) := 'SharedMember1';
  ew_lb_api.g_out_shared_parent_tbl(l_idx) := 'Parent2';
END;
```

### Property Synchronization

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_out_prop_names_tbl` | ARRAY | Property names to sync |
| `g_out_prop_values_tbl` | ARRAY | Property values to sync |

**Example - Map Properties:**
```sql
-- Map specific properties to target
ew_lb_api.g_out_prop_names_tbl(1) := 'ACCOUNT_TYPE';
ew_lb_api.g_out_prop_values_tbl(1) := 'Revenue';

ew_lb_api.g_out_prop_names_tbl(2) := 'CONSOLIDATION';
ew_lb_api.g_out_prop_values_tbl(2) := 'FULL';
```

## Mapping Methods

### Smart Sync Fallback

When custom logic is not needed, use the Smart Sync method:

```sql
BEGIN
  -- Use EPMware's standard mapping logic
  ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
  
  -- This automatically sets all output parameters
  -- based on the configuration
END;
```

### Sync Method

For direct 1:1 mapping:

```sql
BEGIN
  -- Direct synchronization without transformation
  ew_hierarchy.set_dim_mapping_method('SYNC');
END;
```

## Common Patterns

### Pattern 1: Conditional Mapping

```sql
BEGIN
  IF member_should_be_mapped() THEN
    -- Map with transformation
    ew_lb_api.g_out_member_name := transform_name(ew_lb_api.g_member_name);
    ew_lb_api.g_out_parent_member_name := transform_name(ew_lb_api.g_parent_member_name);
  ELSE
    -- Skip this member
    ew_lb_api.g_out_ignore_flag := 'Y';
  END IF;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Pattern 2: Validation Before Mapping

```sql
BEGIN
  -- Validate before mapping
  IF NOT is_valid_for_target() THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Member does not meet target requirements';
    RETURN;
  END IF;
  
  -- Proceed with mapping
  ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
END;
```

### Pattern 3: Complex Transformation

```sql
BEGIN
  CASE ew_lb_api.g_action_code
    WHEN 'CMC' THEN
      -- Custom create logic
      ew_lb_api.g_out_member_name := 'TGT_' || ew_lb_api.g_member_name;
      ew_lb_api.g_out_parent_member_name := map_parent(ew_lb_api.g_parent_member_name);
      
    WHEN 'R' THEN
      -- Custom rename logic
      ew_lb_api.g_out_old_member_name := ew_lb_api.g_renamed_from_member_name;
      ew_lb_api.g_out_new_member_name := 'TGT_' || ew_lb_api.g_member_name;
      
    ELSE
      -- Use default for other actions
      ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
  END CASE;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

## Best Practices

1. **Always Set Status**: Every path must set `g_status`
2. **Clear Error Messages**: Provide actionable error messages
3. **Use Ignore Flag**: Better than erroring for filtered members
4. **Leverage Smart Sync**: Don't reinvent standard logic
5. **Log Transformations**: Document mapping decisions

## Related Topics

- [Input Parameters](input-parameters.md)
- [Dimension Mapping Examples](examples.md)
- [API Reference - Hierarchy](../../api/packages/hierarchy.md)