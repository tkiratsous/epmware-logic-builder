# Dimension Mapping Scripts

Dimension Mapping scripts enable automatic synchronization of hierarchies and members between applications. These scripts execute when hierarchy changes occur in a source dimension that has mapping rules configured.

## Overview

Dimension Mapping provides intelligent synchronization capabilities:
- **Smart Sync**: Replicates exact hierarchy structure
- **Custom Mapping**: Apply business logic during synchronization
- **Selective Sync**: Map specific branches or members
- **Property Sync**: Synchronize properties along with hierarchy

![Dimension Mapping Overview](../../assets/images/dimension-mapping-overview.png)
*Figure: Dimension mapping synchronization between applications*

## When to Use

Dimension Mapping scripts are ideal for:
- Maintaining consistent hierarchies across multiple applications
- Transforming member names or structures during synchronization
- Implementing conditional mapping based on business rules
- Synchronizing specific branches between applications
- Creating audit or reporting hierarchies

## Configuration

### Step 1: Create the Script

Navigate to **Configuration → Logic Builder**:

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'MAP_ENTITY_DIMENSION';
BEGIN
  -- Initialize status
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Custom mapping logic here
  IF ew_lb_api.g_action_code = 'CMC' THEN
    -- Create member as child
    -- Custom logic for member creation
  END IF;
  
  -- Use Smart Sync for standard cases
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SMARTSYNC',
    x_status        => ew_lb_api.g_status,
    x_message       => ew_lb_api.g_message
  );
END;
```

### Step 2: Configure Dimension Mapping

Navigate to **Configuration → Dimension → Mapping**:

1. Select source application and dimension
2. Select target application and dimension
3. Choose mapping type:
   - **Smart Sync**: Automatic replication
   - **Logic Script**: Custom logic
4. Select your Logic Script
5. Configure additional options

![Dimension Mapping Configuration](../../assets/images/dimension-mapping-config.png)
*Figure: Dimension mapping configuration screen*

## Mapping Methods

### Smart Sync
Automatically replicates hierarchy structure:
```sql
ew_hierarchy.set_dim_mapping_method(
  p_mapping_method => 'SMARTSYNC',
  x_status        => ew_lb_api.g_status,
  x_message       => ew_lb_api.g_message
);
```

### Sync (Simple)
Maps members without hierarchy relationships:
```sql
ew_hierarchy.set_dim_mapping_method(
  p_mapping_method => 'SYNC',
  x_status        => ew_lb_api.g_status,
  x_message       => ew_lb_api.g_message
);
```

### Custom Logic
Implement complex mapping rules:
```sql
-- Example: Map only certain branches
IF ew_lb_api.g_parent_member_name LIKE 'REGION_%' THEN
  -- Set target parent
  ew_lb_api.g_out_tgt_parent_member_name := 
    REPLACE(ew_lb_api.g_parent_member_name, 'REGION_', 'LOC_');
  
  -- Set target member
  ew_lb_api.g_out_tgt_new_member_name := 
    'L_' || ew_lb_api.g_member_name;
END IF;
```

## Action Codes

Dimension Mapping scripts handle various hierarchy actions:

| Action Code | Description | Mapping Behavior |
|-------------|-------------|------------------|
| CMC | Create Member as Child | Creates new member in target |
| CMS | Create Member as Sibling | Creates sibling in target |
| DM | Delete Member | Removes member from target |
| RNM | Rename Member | Renames member in target |
| ZC | Move Member (Change Parent) | Moves member in target hierarchy |
| ISMC | Insert Shared Member as Child | Creates shared instance |
| ISMS | Insert Shared Member as Sibling | Creates shared sibling |
| DSHM | Delete Shared Member | Removes shared instance |

## Input/Output Parameters

### Key Input Parameters
- `g_action_code` - Hierarchy action being performed
- `g_member_name` - Source member name
- `g_parent_member_name` - Source parent name
- `g_new_member_name` - New name (for rename)
- `g_sort_order` - Member position

### Key Output Parameters
- `g_out_tgt_new_member_name` - Target member name
- `g_out_tgt_parent_member_name` - Target parent name
- `g_out_tgt_old_member_name` - Old target name (rename)
- `g_out_ignore_flag` - Skip standard processing ('Y'/'N')

## Common Patterns

### Pattern 1: Conditional Mapping
```sql
DECLARE
  l_map_member BOOLEAN := FALSE;
BEGIN
  -- Only map specific branches
  IF ew_hierarchy.is_descendant_of(
       p_member => ew_lb_api.g_member_name,
       p_ancestor => 'CORP_ENTITIES'
     ) = 'Y' THEN
    l_map_member := TRUE;
  END IF;
  
  IF l_map_member THEN
    -- Proceed with mapping
    ew_hierarchy.set_dim_mapping_method(
      p_mapping_method => 'SMARTSYNC',
      x_status        => ew_lb_api.g_status,
      x_message       => ew_lb_api.g_message
    );
  ELSE
    -- Skip this member
    ew_lb_api.g_out_ignore_flag := 'Y';
  END IF;
END;
```

### Pattern 2: Name Transformation
```sql
BEGIN
  -- Transform member names during mapping
  CASE 
    WHEN ew_lb_api.g_member_name LIKE 'CC_%' THEN
      -- Cost Centers: Add prefix
      ew_lb_api.g_out_tgt_new_member_name := 
        'COST_' || SUBSTR(ew_lb_api.g_member_name, 4);
      
    WHEN ew_lb_api.g_member_name LIKE 'PC_%' THEN
      -- Profit Centers: Add prefix
      ew_lb_api.g_out_tgt_new_member_name := 
        'PROFIT_' || SUBSTR(ew_lb_api.g_member_name, 4);
      
    ELSE
      -- Keep original name
      ew_lb_api.g_out_tgt_new_member_name := 
        ew_lb_api.g_member_name;
  END CASE;
  
  -- Continue with Smart Sync
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SMARTSYNC',
    x_status        => ew_lb_api.g_status,
    x_message       => ew_lb_api.g_message
  );
END;
```

### Pattern 3: Cross-Reference Mapping
```sql
DECLARE
  l_target_member VARCHAR2(100);
BEGIN
  -- Look up cross-reference
  BEGIN
    SELECT target_member_name
    INTO   l_target_member
    FROM   custom_mapping_table
    WHERE  source_member_name = ew_lb_api.g_member_name
    AND    source_app = ew_lb_api.g_src_app_name;
    
    -- Use mapped name
    ew_lb_api.g_out_tgt_new_member_name := l_target_member;
    
  EXCEPTION
    WHEN NO_DATA_FOUND THEN
      -- No mapping found, use default
      ew_lb_api.g_out_tgt_new_member_name := 
        ew_lb_api.g_member_name;
  END;
  
  -- Continue with standard processing
  ew_hierarchy.set_dim_mapping_method(
    p_mapping_method => 'SYNC',
    x_status        => ew_lb_api.g_status,
    x_message       => ew_lb_api.g_message
  );
END;
```

## Testing

### Test Scenarios

1. **Create Member**: Add new member in source, verify target
2. **Delete Member**: Remove member, check target cleanup
3. **Move Member**: Change parent, confirm target structure
4. **Rename Member**: Rename in source, verify target update
5. **Shared Members**: Test shared member scenarios

### Validation Steps

1. Check Debug Messages for execution logs
2. Verify target hierarchy structure
3. Confirm property values (if mapped)
4. Review error messages for failures

## Performance Optimization

### Best Practices

1. **Cache Lookups**: Store frequently used data
```sql
IF g_mapping_cache IS NULL THEN
  load_mapping_cache();
END IF;
```

2. **Bulk Operations**: Process multiple members efficiently
```sql
FORALL i IN 1..l_members.COUNT
  INSERT INTO target_table VALUES l_members(i);
```

3. **Conditional Processing**: Skip unnecessary operations
```sql
IF NOT needs_mapping(ew_lb_api.g_member_name) THEN
  ew_lb_api.g_out_ignore_flag := 'Y';
  RETURN;
END IF;
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Members not mapping | Script not associated | Verify dimension mapping configuration |
| Duplicate member errors | Member already exists | Check for existing members before create |
| Performance issues | Complex logic in loops | Optimize queries, use caching |
| Incorrect hierarchy | Wrong parent assignment | Debug parent member logic |

## Advanced Features

### Multi-Level Mapping
Map to different targets based on level:
```sql
IF ew_statistics.get_generation(
     p_app_dimension_id => ew_lb_api.g_app_dimension_id,
     p_member_id       => ew_lb_api.g_member_id
   ) <= 3 THEN
  -- Map to summary dimension
  ew_lb_api.g_out_tgt_dim_name := 'Summary_Entity';
ELSE
  -- Map to detail dimension
  ew_lb_api.g_out_tgt_dim_name := 'Detail_Entity';
END IF;
```

### Property Synchronization
Sync properties along with hierarchy:
```sql
-- After member creation, sync properties
ew_hierarchy.copy_member_props(
  p_src_member_id => ew_lb_api.g_member_id,
  p_tgt_member_id => l_new_member_id
);
```

## Next Steps

- [Input Parameters](input-parameters.md) - Detailed parameter reference
- [Output Parameters](output-parameters.md) - Control mapping behavior
- [Examples](examples.md) - Real-world scenarios
- [API Reference](../../api/packages/hierarchy.md) - Hierarchy functions

---

!!! tip "Best Practice"
    Always test dimension mapping scripts with a small subset of members before enabling for the entire dimension.