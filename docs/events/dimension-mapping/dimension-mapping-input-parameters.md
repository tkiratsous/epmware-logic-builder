# Dimension Mapping Input Parameters

This page details all input parameters available for Dimension Mapping Logic Scripts. These parameters provide comprehensive context about the hierarchy operation being performed.

## Core Parameters

### Member Information

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_member_name` | VARCHAR2 | Member name being processed |
| `g_parent_member_name` | VARCHAR2 | Parent member name |
| `g_member_id` | NUMBER | Internal member ID |
| `g_hierarchy_id` | NUMBER | Unique node ID for parent/member combination |

![Member Information Flow](../../assets/images/member-info-flow.png)
*Figure: How member information flows through dimension mapping*

### Application Context

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_app_name` | VARCHAR2 | Source application name |
| `g_dim_name` | VARCHAR2 | Source dimension name |
| `g_dim_class_name` | VARCHAR2 | Dimension class (Account, Entity, etc.) |
| `g_app_dimension_id` | NUMBER | Application dimension ID |

## Action-Specific Parameters

### Action Codes

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_action_code` | VARCHAR2 | Hierarchy action code |
| `g_action_name` | VARCHAR2 | Human-readable action name |
| `g_action_id` | NUMBER | Internal action ID |

**Common Action Codes:**
- `CMC` - Create Member as Child
- `CMS` - Create Member as Sibling
- `D` - Delete Member
- `R` - Rename Member
- `M` - Move Member
- `ZC` - Move as Child
- `ZS` - Move as Sibling
- `ISMC` - Insert Shared Member as Child
- `ISMS` - Insert Shared Member as Sibling

### Rename Operations

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_renamed_from_member_name` | VARCHAR2 | Original member name before rename |
| `g_renamed_from_member_id` | NUMBER | Original member ID |

**Example Usage:**
```sql
IF ew_lb_api.g_action_code = 'R' THEN
  log('Renaming member from ' || ew_lb_api.g_renamed_from_member_name || 
      ' to ' || ew_lb_api.g_member_name);
END IF;
```

### Move Operations

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_moved_from_member_name` | VARCHAR2 | Original parent for move operations |
| `g_moved_to_member_name` | VARCHAR2 | Target parent for move operations |

**Example Usage:**
```sql
IF ew_lb_api.g_action_code IN ('M', 'ZC', 'ZS') THEN
  log('Moving member from parent ' || ew_lb_api.g_moved_from_member_name || 
      ' to parent ' || ew_lb_api.g_moved_to_member_name);
END IF;
```

## Mapped Dimension Parameters

### Target Information

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_mapped_app_name` | VARCHAR2 | Target application name |
| `g_mapped_dim_name` | VARCHAR2 | Target dimension name |
| `g_mapped_app_dimension_id` | NUMBER | Target application dimension ID |

## Request Context

### Workflow Information

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_request_id` | NUMBER | Current request ID |
| `g_request_line_id` | NUMBER | Request line ID |
| `g_wf_code` | VARCHAR2 | Workflow code |
| `g_wf_stage_name` | VARCHAR2 | Current workflow stage |
| `g_req_rec` | RECORD | Complete request header record |

### User Context

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_user_id` | NUMBER | Current user ID |
| `g_lb_script_name` | VARCHAR2 | Executing script name |

## Property Arrays

### Multiple Properties Support

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_prop_names_tbl` | ARRAY | Property names array |
| `g_prop_labels_tbl` | ARRAY | Property labels array |
| `g_prop_values_tbl` | ARRAY | Property values array |

**Accessing Property Arrays:**
```sql
FOR i IN 1..ew_lb_api.g_prop_names_tbl.COUNT LOOP
  log('Property: ' || ew_lb_api.g_prop_names_tbl(i) || 
      ' = ' || ew_lb_api.g_prop_values_tbl(i));
END LOOP;
```

## Shared Members

### Shared Instance Information

| Parameter | Type | Description |
|-----------|------|-------------|
| `g_shared_member_flag` | VARCHAR2 | 'Y' if processing shared member |
| `g_shared_members_tbl` | ARRAY | Array of shared member locations |

## Best Practices

### 1. Always Check Action Code

```sql
BEGIN
  -- Always handle specific action codes
  CASE ew_lb_api.g_action_code
    WHEN 'CMC' THEN
      handle_create_child();
    WHEN 'R' THEN
      handle_rename();
    WHEN 'D' THEN
      handle_delete();
    ELSE
      -- Default handling
      ew_hierarchy.set_dim_mapping_method('SMARTSYNC');
  END CASE;
END;
```

### 2. Validate Required Parameters

```sql
IF ew_lb_api.g_member_name IS NULL THEN
  ew_lb_api.g_status := ew_lb_api.g_error;
  ew_lb_api.g_message := 'Member name is required';
  RETURN;
END IF;
```

### 3. Use Debug Logging

```sql
ew_debug.log('Processing action ' || ew_lb_api.g_action_code || 
             ' for member ' || ew_lb_api.g_member_name,
             'DIM_MAPPING_SCRIPT');
```

## Related Topics

- [Output Parameters](output-parameters.md)
- [Dimension Mapping Examples](examples.md)
- [Action Codes Reference](../../appendices/action-codes.md)