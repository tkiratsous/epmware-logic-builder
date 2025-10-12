# Property Mapping Configuration

This page provides detailed instructions for configuring Property Mapping in EPMware.

## Configuration Overview

Property Mapping configuration involves three main steps:
1. Creating the Logic Script
2. Setting up the Property Mapping
3. Testing and validation

![Property Mapping Configuration Flow](../../assets/images/property-mapping-config-flow.png)
*Figure: Complete configuration workflow for Property Mapping*

## Step-by-Step Configuration

### Step 1: Access Property Mapping Configuration

Navigate to the Property Mapping configuration screen:

1. Open the **Configuration** menu
2. Select **Property**
3. Click **Mapping**

![Navigation to Property Mapping](../../assets/images/nav-property-mapping.png)
*Figure: Navigation path to Property Mapping configuration*

### Step 2: Create New Mapping

Click the **Add** button to create a new property mapping:

![Add Property Mapping](../../assets/images/add-property-mapping.png)
*Figure: Adding a new property mapping*

### Step 3: Configure Mapping Details

#### Source Configuration

| Field | Description | Example |
|-------|-------------|---------|
| **Source Application** | Application containing source dimension | HFM_PROD |
| **Source Dimension** | Dimension to map from | Account |
| **Source Property** | Property to synchronize | Alias:Default |

#### Target Configuration

| Field | Description | Example |
|-------|-------------|---------|
| **Target Application** | Application containing target dimension | PLANNING_PROD |
| **Target Dimension** | Dimension to map to | Account |
| **Target Property** | Property to update | Alias:English |

#### Mapping Options

| Option | Description | When to Use |
|--------|-------------|-------------|
| **Sync Method** | Direct 1:1 mapping | Simple synchronization |
| **Smart Sync** | Intelligent mapping with rules | Complex transformations |
| **Logic Script** | Custom transformation logic | Business-specific rules |

### Step 4: Assign Logic Script

If using custom logic:

1. Select **Logic Script** as the mapping method
2. Choose your script from the dropdown
3. Configure script parameters if applicable

```sql
-- Example Logic Script assignment
Script Name: TRANSFORM_ACCOUNT_ALIASES
Script Type: Property Mapping
Status: Enabled
```

![Logic Script Assignment](../../assets/images/property-mapping-script-assign.png)
*Figure: Assigning a Logic Script to property mapping*

## Advanced Configuration

### Multiple Property Mapping

Configure multiple properties in a single mapping:

1. Click **Add Property** in the mapping configuration
2. Select additional source and target properties
3. Each property can have its own transformation logic

```sql
-- Handle multiple properties in one script
CASE ew_lb_api.g_prop_name
  WHEN 'ALIAS' THEN
    ew_lb_api.g_out_prop_value := transform_alias(ew_lb_api.g_prop_value);
  WHEN 'ACCOUNT_TYPE' THEN
    ew_lb_api.g_out_prop_value := map_account_type(ew_lb_api.g_prop_value);
  WHEN 'CONSOLIDATION' THEN
    ew_lb_api.g_out_prop_value := map_consolidation(ew_lb_api.g_prop_value);
  ELSE
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
END CASE;
```

### Conditional Mapping

Configure mapping to execute only under specific conditions:

#### By Member Type
```sql
-- Only map base-level members
IF ew_hierarchy.is_leaf(
     p_member_id        => ew_lb_api.g_member_id,
     p_app_dimension_id => ew_lb_api.g_app_dimension_id
   ) = 'Y' THEN
  -- Apply mapping
  ew_lb_api.g_out_prop_value := transform_value(ew_lb_api.g_prop_value);
ELSE
  -- Skip parent members
  ew_lb_api.g_out_ignore_flag := 'Y';
END IF;
```

#### By Property Value
```sql
-- Map only non-empty values
IF ew_lb_api.g_prop_value IS NOT NULL THEN
  ew_lb_api.g_out_prop_value := 'Mapped: ' || ew_lb_api.g_prop_value;
ELSE
  ew_lb_api.g_out_ignore_flag := 'Y';
END IF;
```

### Bi-Directional Mapping

Configure two-way synchronization between applications:

1. Create mapping from App A to App B
2. Create reverse mapping from App B to App A
3. Use logic to prevent infinite loops

```sql
-- Prevent mapping loops
DECLARE
  l_last_update_source VARCHAR2(100);
BEGIN
  -- Check if this update originated from mapping
  l_last_update_source := get_update_source(ew_lb_api.g_member_id);
  
  IF l_last_update_source != 'PROPERTY_MAPPING' THEN
    -- Safe to map
    ew_lb_api.g_out_prop_value := transform_value(ew_lb_api.g_prop_value);
  ELSE
    -- Skip to prevent loop
    ew_lb_api.g_out_ignore_flag := 'Y';
  END IF;
END;
```

## Configuration Settings

### Mapping Execution Options

| Setting | Description | Options |
|---------|-------------|---------|
| **Execution Mode** | When mapping executes | Immediate / Scheduled |
| **Error Handling** | How errors are handled | Stop / Continue / Log Only |
| **Batch Size** | Records per batch | 100 / 500 / 1000 |
| **Timeout** | Maximum execution time | 30 / 60 / 120 seconds |

### Performance Optimization

#### Enable Caching
```sql
-- Cache frequently used lookups
DECLARE
  TYPE t_cache IS TABLE OF VARCHAR2(100) INDEX BY VARCHAR2(100);
  g_cache t_cache;
BEGIN
  -- Check cache first
  IF g_cache.EXISTS(ew_lb_api.g_prop_value) THEN
    ew_lb_api.g_out_prop_value := g_cache(ew_lb_api.g_prop_value);
  ELSE
    -- Perform lookup and cache result
    ew_lb_api.g_out_prop_value := expensive_lookup(ew_lb_api.g_prop_value);
    g_cache(ew_lb_api.g_prop_value) := ew_lb_api.g_out_prop_value;
  END IF;
END;
```

#### Bulk Processing
Configure mapping to process multiple properties together:

```sql
-- Process all properties for a member at once
FOR i IN 1..ew_lb_api.g_prop_names_tbl.COUNT LOOP
  process_property(
    p_name  => ew_lb_api.g_prop_names_tbl(i),
    p_value => ew_lb_api.g_prop_values_tbl(i)
  );
END LOOP;
```

## Testing Configuration

### Test Scenarios

1. **Single Property Update**
   - Modify one property value
   - Verify correct transformation
   - Check target update

2. **Bulk Property Updates**
   - Update multiple properties
   - Confirm all transformations
   - Monitor performance

3. **Error Conditions**
   - Test with invalid values
   - Verify error handling
   - Check error messages

### Validation Steps

1. **Pre-Mapping Validation**
   ```sql
   -- Verify source member exists in target
   IF NOT target_member_exists(ew_lb_api.g_member_name) THEN
     ew_lb_api.g_status := ew_lb_api.g_error;
     ew_lb_api.g_message := 'Target member does not exist';
     RETURN;
   END IF;
   ```

2. **Post-Mapping Verification**
   ```sql
   -- Log mapping result
   ew_debug.log('Mapped ' || ew_lb_api.g_prop_label || 
                ': ' || ew_lb_api.g_prop_value || 
                ' -> ' || ew_lb_api.g_out_prop_value,
                'PROP_MAP_VALIDATION');
   ```

## Monitoring and Maintenance

### Debug Messages

Monitor property mapping execution through Debug Messages:

![Debug Messages for Property Mapping](../../assets/images/property-mapping-debug.png)
*Figure: Debug Messages showing property mapping execution*

### Performance Metrics

Track key metrics:
- Properties mapped per minute
- Average transformation time
- Error rate
- Cache hit ratio

### Regular Maintenance

1. **Review Mappings Monthly**
   - Check for unused mappings
   - Update transformation rules
   - Optimize performance

2. **Archive Old Logs**
   - Export debug messages
   - Clear old entries
   - Maintain performance

3. **Update Documentation**
   - Document mapping rules
   - Update test cases
   - Record configuration changes

## Troubleshooting Guide

### Common Configuration Issues

| Issue | Symptoms | Solution |
|-------|----------|----------|
| Mapping not triggered | No updates in target | Verify mapping is enabled |
| Wrong property mapped | Incorrect values | Check property name mapping |
| Performance degradation | Slow updates | Optimize script logic |
| Circular updates | Infinite loop | Implement loop detection |

### Configuration Checklist

- [ ] Source and target applications selected
- [ ] Dimensions correctly mapped
- [ ] Properties properly configured
- [ ] Logic Script assigned (if needed)
- [ ] Mapping enabled
- [ ] Error handling configured
- [ ] Testing completed
- [ ] Documentation updated

## Related Topics

- [Property Mapping Overview](index.md)
- [Property Mapping Examples](examples.md)
- [Logic Script Structure](../../getting-started/script-structure.md)
- [API Reference](../../api/packages/hierarchy.md)