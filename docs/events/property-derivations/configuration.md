# Property Derivations Configuration

This guide provides comprehensive instructions for configuring Property Derivations in EPMware, including setup procedures, configuration options, and optimization strategies.

## Configuration Overview

Property Derivation configuration consists of:
1. Identifying properties requiring derivation
2. Creating derivation logic scripts
3. Configuring derivation rules
4. Setting execution triggers
5. Testing and validation

![Property Derivations Configuration Flow](../../assets/images/property-derivations-config-flow.png)
*Figure: Property derivations configuration workflow*

## Prerequisites

Before configuring property derivations:
- Application and dimensions configured
- Properties defined in dimension
- Logic Builder module access
- Understanding of property dependencies

## Configuration Steps

### Step 1: Access Property Derivations

Navigate to **Configuration → Properties → Derivations**

![Property Derivations Menu](../../assets/images/property-derivations-menu.png)
*Figure: Accessing Property Derivations configuration*

### Step 2: Select Context

Choose the application and dimension:

| Field | Description | Example |
|-------|-------------|---------|
| Application | Target application | PLANNING_PROD |
| Dimension | Dimension containing properties | Entity |
| Property Class | Optional property grouping | Financial_Properties |

### Step 3: Create Derivation Rule

Click **Add Derivation** to create new rule:

![Add Derivation Rule](../../assets/images/add-derivation-rule.png)
*Figure: Adding new derivation rule*

### Step 4: Configure Derivation Settings

#### Basic Settings

| Setting | Description | Options |
|---------|-------------|---------|
| Property Name | Property to derive | Select from list |
| Derivation Type | How to derive value | Default, Calculate, Inherit, Script |
| Enabled | Activate derivation | Yes/No |
| Override Existing | Replace existing values | Yes/No |

#### Derivation Types

**Default Value**
```yaml
Type: Default
Value: "Active"
When: Member Creation
```

**Calculated**
```yaml
Type: Calculate
Formula: "{Base_Amount} * 1.1"
When: Property Change
```

**Inherited**
```yaml
Type: Inherit
Source: Parent Member
Property: Same Property
```

**Logic Script**
```yaml
Type: Script
Script: DERIVE_COMPLEX_VALUE
When: Multiple Triggers
```

### Step 5: Configure Triggers

Define when derivations execute:

| Trigger | Description | Use Case |
|---------|-------------|----------|
| Member Creation | New member added | Set initial values |
| Property Edit | Property value changed | Update related properties |
| Hierarchy Change | Member moved/renamed | Recalculate hierarchical values |
| Manual Trigger | User-initiated | Bulk updates |
| Scheduled | Time-based execution | Periodic recalculation |

![Derivation Triggers](../../assets/images/derivation-triggers.png)
*Figure: Configuring derivation triggers*

### Step 6: Set Execution Order

When multiple derivations exist:

```yaml
Execution Order:
  1. System Properties (Priority: 100)
  2. Inherited Properties (Priority: 200)
  3. Calculated Properties (Priority: 300)
  4. User Scripts (Priority: 400)
```

### Step 7: Configure Dependencies

Define property dependencies:

```yaml
Property: Total_Cost
Depends On:
  - Base_Cost
  - Tax_Rate
  - Shipping_Cost
Recalculate When: Any dependency changes
```

## Logic Script Configuration

### Creating Derivation Scripts

1. Navigate to Logic Builder
2. Create new script with type "Property Derivations"
3. Implement derivation logic
4. Save and validate

```sql
-- Example derivation script structure
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'DERIVE_PROPERTY_VALUE';
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Derivation logic
  IF ew_lb_api.g_prop_name = 'Department_Code' THEN
    ew_lb_api.g_out_prop_value := 
      generate_department_code(
        p_parent => ew_lb_api.g_parent_member_name,
        p_member => ew_lb_api.g_member_name
      );
  END IF;
END;
```

### Associating Scripts

1. Select the property requiring derivation
2. Choose "Logic Script" as derivation type
3. Select script from dropdown
4. Configure script parameters (if any)

## Advanced Configuration Options

### Conditional Derivations

Configure rules with conditions:

```yaml
Rule: Derive Status
Condition: 
  IF Member_Type = 'Cost_Center'
  AND Region = 'North America'
Then: 
  Derive Status = 'Active'
Else:
  Derive Status = 'Pending'
```

### Batch Processing

Configure batch settings for performance:

| Setting | Description | Recommended |
|---------|-------------|-------------|
| Batch Size | Records per transaction | 500 |
| Parallel Threads | Concurrent processing | 4 |
| Error Threshold | Stop after X errors | 10 |
| Commit Frequency | Commits per batch | Every batch |

### Caching Configuration

Enable caching for better performance:

```yaml
Cache Settings:
  Enable Cache: Yes
  Cache Type: Memory
  Cache Duration: 30 minutes
  Cache Size: 10000 entries
  Refresh Strategy: On-Demand
```

## Configuration Examples

### Example 1: Auto-Generate Member Codes

```yaml
Configuration:
  Property: Member_Code
  Type: Logic Script
  Script: GENERATE_MEMBER_CODE
  Trigger: Member Creation
  Override: No
  
Script Logic:
  - Get parent code prefix
  - Find next available number
  - Format: PREFIX_YYYY_NNNN
  - Ensure uniqueness
```

### Example 2: Inherit Regional Settings

```yaml
Configuration:
  Property: Currency
  Type: Inherit
  Source: Parent Member
  Trigger: Member Creation, Parent Change
  Override: Only if NULL
  
Inheritance Rules:
  - Walk up hierarchy
  - Find first non-null value
  - Maximum levels: 5
  - Default: USD
```

### Example 3: Calculate Derived Metrics

```yaml
Configuration:
  Property: Risk_Score
  Type: Calculate
  Formula: Complex calculation
  Trigger: Related property change
  Dependencies:
    - Revenue
    - Costs
    - Market_Risk
    - Operational_Risk
```

## Performance Optimization

### Indexing Strategy

Create indexes for derivation queries:

```sql
-- Index for property lookups
CREATE INDEX idx_prop_derivation 
ON ew_member_properties(app_dimension_id, prop_name, member_id);

-- Index for hierarchy navigation
CREATE INDEX idx_hierarchy_derive
ON ew_hierarchy_members(parent_id, member_id);
```

### Query Optimization

Optimize derivation queries:

```sql
-- Efficient parent property lookup
WITH parent_hierarchy AS (
  SELECT level, member_id, parent_id, prop_value
  FROM ew_hierarchy_members
  START WITH member_id = :member_id
  CONNECT BY PRIOR parent_id = member_id
  AND level <= 5
)
SELECT prop_value 
FROM parent_hierarchy 
WHERE prop_value IS NOT NULL
AND ROWNUM = 1;
```

### Bulk Derivation

Configure bulk operations:

```sql
-- Bulk derivation for multiple members
FORALL i IN 1..l_members.COUNT
  UPDATE ew_member_properties
  SET prop_value = l_derived_values(i)
  WHERE member_id = l_members(i)
  AND prop_name = :prop_name;
```

## Testing Configuration

### Test Scenarios

1. **New Member Creation**
   - Create member
   - Verify all derivations execute
   - Check derived values

2. **Property Updates**
   - Modify triggering property
   - Verify dependent derivations
   - Check cascade effects

3. **Bulk Operations**
   - Import multiple members
   - Verify batch derivation
   - Check performance

### Validation Queries

```sql
-- Check derivation execution
SELECT d.derivation_id,
       d.property_name,
       COUNT(*) as executions,
       AVG(execution_time) as avg_time
FROM derivation_log d
WHERE d.execution_date >= SYSDATE - 1
GROUP BY d.derivation_id, d.property_name;

-- Verify derived values
SELECT m.member_name,
       p.prop_name,
       p.prop_value,
       p.derived_flag,
       p.derivation_date
FROM ew_members m
JOIN ew_member_properties p ON m.member_id = p.member_id
WHERE p.derived_flag = 'Y'
ORDER BY p.derivation_date DESC;
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Values not derived | Rule disabled | Enable derivation rule |
| Wrong values | Incorrect logic | Debug script logic |
| Circular reference | Properties depend on each other | Review dependencies |
| Poor performance | No indexes | Add appropriate indexes |
| Partial derivation | Errors in batch | Check error logs |

### Debug Techniques

Enable detailed logging:

```sql
-- Enable debug mode
BEGIN
  ew_debug.set_level('DEBUG');
  ew_debug.log('Starting derivation for ' || :member_name);
  -- Derivation logic
  ew_debug.log('Derived value: ' || :derived_value);
END;
```

### Error Recovery

Configure error handling:

```yaml
Error Handling:
  On Error: Log and Continue
  Max Retries: 3
  Retry Delay: 5 seconds
  Notification: Email admin
  Fallback: Use default value
```

## Maintenance

### Regular Tasks

1. **Weekly**
   - Review error logs
   - Check performance metrics
   - Clear old cache entries

2. **Monthly**
   - Analyze derivation patterns
   - Update derivation rules
   - Optimize slow queries

3. **Quarterly**
   - Review all derivations
   - Remove obsolete rules
   - Update documentation

### Monitoring Dashboard

Key metrics to monitor:

```sql
-- Derivation performance dashboard
SELECT 
  property_name,
  derivation_type,
  total_executions,
  successful_count,
  failed_count,
  avg_execution_time,
  last_execution
FROM derivation_metrics_v
WHERE metric_date = TRUNC(SYSDATE)
ORDER BY avg_execution_time DESC;
```

## Best Practices

1. **Keep derivations simple** - Complex logic impacts performance
2. **Avoid circular dependencies** - Can cause infinite loops
3. **Use caching wisely** - Balance memory vs performance
4. **Test thoroughly** - Include edge cases
5. **Document rules** - Maintain clear documentation
6. **Monitor performance** - Track execution times
7. **Version control** - Track script changes

## Next Steps

- [Examples](examples.md) - Real-world scenarios
- [API Reference](../../api/packages/hierarchy.md) - Supporting functions
- [Property Validations](../property-validations/) - Related validation

---

!!! warning "Important"
    Always test derivation rules with a subset of data before enabling for the entire dimension. Monitor performance impact, especially for large hierarchies.