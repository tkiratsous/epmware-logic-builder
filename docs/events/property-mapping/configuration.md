# Property Mapping Configuration

This guide provides detailed instructions for configuring Property Mapping in EPMware, including setup steps, configuration options, and best practices.

## Configuration Overview

Property Mapping configuration involves:
1. Defining source and target applications
2. Selecting properties to map
3. Choosing mapping method (Direct or Logic Script)
4. Configuring mapping rules
5. Testing and validation

![Property Mapping Flow](../../assets/images/property-mapping-flow.png)
*Figure: Property mapping configuration flow*

## Prerequisites

Before configuring property mapping:
- Source and target applications must exist
- Dimensions must be configured in both applications
- Properties must be defined in both dimensions
- Logic Builder access for custom scripts

## Step-by-Step Configuration

### Step 1: Access Property Mapping

Navigate to **Configuration → Property → Mapping**

![Property Mapping Menu](../../assets/images/property-mapping-menu.png)
*Figure: Accessing Property Mapping from Configuration menu*

### Step 2: Create New Mapping Rule

Click **Add** to create a new property mapping rule:

![Add Property Mapping](../../assets/images/add-property-mapping.png)
*Figure: Adding new property mapping rule*

### Step 3: Configure Source

Select source details:

| Field | Description | Example |
|-------|-------------|---------|
| Source Application | Application containing source properties | HFM_PROD |
| Source Dimension | Dimension with properties to map | Entity |
| Source Property | Specific property or "All Properties" | Cost_Center_Type |

### Step 4: Configure Target

Select target details:

| Field | Description | Example |
|-------|-------------|---------|
| Target Application | Application to receive mapped properties | PLANNING_PROD |
| Target Dimension | Dimension to update | Entity |
| Target Property | Property to update (can differ from source) | CC_Type |

### Step 5: Select Mapping Method

Choose mapping approach:

#### Direct Mapping
- Copies property value as-is
- No transformation logic
- Fastest performance
- Use when values are compatible

```xml
Source: "Active" → Target: "Active"
```

#### Logic Script Mapping
- Applies custom transformation
- Business logic validation
- Value translation
- Complex mappings

```xml
Source: "A" → Script Transform → Target: "Active"
```

![Mapping Method Selection](../../assets/images/mapping-method-selection.png)
*Figure: Selecting between Direct and Logic Script mapping*

### Step 6: Configure Logic Script (if applicable)

If using Logic Script mapping:

1. **Select existing script** from dropdown
2. Or **create new script**:
   - Click "New Script" button
   - Enter script name
   - Write transformation logic
   - Save and validate

```sql
-- Example transformation script
BEGIN
  -- Transform department codes to names
  ew_lb_api.g_out_prop_value := 
    CASE ew_lb_api.g_prop_value
      WHEN 'FIN' THEN 'Finance'
      WHEN 'MKT' THEN 'Marketing'
      WHEN 'OPS' THEN 'Operations'
      ELSE ew_lb_api.g_prop_value
    END;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Step 7: Set Additional Options

Configure optional settings:

| Option | Description | Default |
|--------|-------------|---------|
| Enabled | Activate/deactivate mapping | Enabled |
| Map Null Values | Process NULL property values | No |
| Create If Missing | Create property if not exists in target | No |
| Override Protected | Update read-only properties | No |
| Batch Size | Records per transaction | 100 |

### Step 8: Configure Filters (Optional)

Add filters to limit which members are processed:

```sql
-- Only map for specific member patterns
Member Name Like: 'CC_%'

-- Only map for specific property values
Property Value In: ('Active', 'Pending')

-- Custom filter logic
Custom Filter: "Member Level = 0"
```

![Property Mapping Filters](../../assets/images/property-mapping-filters.png)
*Figure: Configuring property mapping filters*

### Step 9: Save and Validate

1. Click **Save** to store configuration
2. System validates:
   - Source/target compatibility
   - Script syntax (if applicable)
   - Property existence
3. Review validation messages

## Configuration Examples

### Example 1: Simple Direct Mapping

Map aliases between applications:

```yaml
Source:
  Application: HFM_PROD
  Dimension: Account
  Property: Alias:English
  
Target:
  Application: PLANNING_PROD
  Dimension: Account
  Property: Alias:English
  
Method: Direct
Options:
  - Enabled: Yes
  - Map Null Values: Yes
```

### Example 2: Code to Description Mapping

Transform status codes to descriptions:

```yaml
Source:
  Application: ERP_EXTRACT
  Dimension: Entity
  Property: Status_Code
  
Target:
  Application: REPORTING
  Dimension: Entity
  Property: Status_Description
  
Method: Logic Script
Script: TRANSFORM_STATUS_CODES
```

Logic Script:
```sql
BEGIN
  ew_lb_api.g_out_prop_value := 
    CASE ew_lb_api.g_prop_value
      WHEN '1' THEN 'Active - Operating'
      WHEN '2' THEN 'Inactive - Dormant'
      WHEN '3' THEN 'Pending - Under Review'
      WHEN '4' THEN 'Closed - Terminated'
      ELSE 'Unknown Status'
    END;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Example 3: Calculated Property Mapping

Calculate and map derived values:

```yaml
Source:
  Application: BUDGET_APP
  Dimension: Department
  Property: Headcount
  
Target:
  Application: PLANNING_APP
  Dimension: Department
  Property: FTE_Equivalent
  
Method: Logic Script
Script: CALCULATE_FTE
```

Logic Script:
```sql
DECLARE
  l_headcount NUMBER;
  l_fte_ratio NUMBER;
BEGIN
  -- Convert headcount to FTE
  l_headcount := TO_NUMBER(ew_lb_api.g_prop_value);
  
  -- Get FTE ratio for department type
  l_fte_ratio := CASE 
    WHEN ew_lb_api.g_member_name LIKE 'CORP_%' THEN 1.0
    WHEN ew_lb_api.g_member_name LIKE 'FIELD_%' THEN 0.85
    ELSE 0.9
  END;
  
  -- Calculate FTE
  ew_lb_api.g_out_prop_value := 
    TO_CHAR(ROUND(l_headcount * l_fte_ratio, 2));
  
  ew_lb_api.g_status := ew_lb_api.g_success;
  
EXCEPTION
  WHEN VALUE_ERROR THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Invalid headcount value';
END;
```

## Advanced Configuration

### Multi-Property Mapping

Map multiple properties with single rule:

1. Select "Multiple Properties" in source
2. Define property list or pattern
3. Configure transformation for each

```sql
-- Script handling multiple properties
BEGIN
  CASE ew_lb_api.g_prop_name
    WHEN 'Country' THEN
      ew_lb_api.g_out_prop_value := 
        get_country_name(ew_lb_api.g_prop_value);
        
    WHEN 'Currency' THEN
      ew_lb_api.g_out_prop_value := 
        get_currency_code(ew_lb_api.g_prop_value);
        
    WHEN 'Region' THEN
      ew_lb_api.g_out_prop_value := 
        get_region_mapping(ew_lb_api.g_prop_value);
        
    ELSE
      -- Default: direct map
      ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  END CASE;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Conditional Mapping Rules

Configure rules that apply conditionally:

```sql
-- Only map if member meets criteria
DECLARE
  l_member_level NUMBER;
BEGIN
  -- Get member level
  l_member_level := ew_statistics.get_level(
    p_app_dimension_id => ew_lb_api.g_app_dimension_id,
    p_member_id       => ew_lb_api.g_member_id
  );
  
  -- Only map base-level members
  IF l_member_level = 0 THEN
    ew_lb_api.g_out_prop_value := ew_lb_api.g_prop_value;
  ELSE
    ew_lb_api.g_out_ignore_flag := 'Y';
  END IF;
  
  ew_lb_api.g_status := ew_lb_api.g_success;
END;
```

### Mapping Chains

Create dependent mapping sequences:

```yaml
Chain 1: Source → Intermediate
  Map: Raw_Code → Standardized_Code
  
Chain 2: Intermediate → Target
  Map: Standardized_Code → Description
```

## Performance Tuning

### Batch Processing

Configure optimal batch sizes:

| Data Volume | Recommended Batch Size |
|-------------|----------------------|
| < 1,000 members | 100 |
| 1,000 - 10,000 | 500 |
| 10,000 - 100,000 | 1,000 |
| > 100,000 | 2,000 |

### Indexing

Create indexes for better performance:

```sql
-- Index for mapping lookup tables
CREATE INDEX idx_prop_map_lookup 
ON property_mapping_xref(source_prop, source_value);

-- Index for member properties
CREATE INDEX idx_member_props 
ON ew_member_properties(member_id, prop_name);
```

### Caching Strategies

Implement caching in scripts:

```sql
-- Package-level cache
CREATE OR REPLACE PACKAGE prop_map_cache AS
  TYPE t_cache IS TABLE OF VARCHAR2(1000) 
    INDEX BY VARCHAR2(200);
  g_cache t_cache;
  
  PROCEDURE clear_cache;
  FUNCTION get_mapped_value(p_key VARCHAR2) RETURN VARCHAR2;
END;
```

## Monitoring and Maintenance

### Enable Logging

Configure detailed logging:

```sql
-- In mapping script
ew_debug.log('Property Mapping Start: ' || 
  ew_lb_api.g_member_name || '.' || 
  ew_lb_api.g_prop_name);
```

### Monitor Execution

Track mapping performance:

```sql
-- Query to monitor mapping execution
SELECT script_name,
       COUNT(*) as executions,
       AVG(execution_time) as avg_time,
       MAX(execution_time) as max_time
FROM   ew_script_execution_log
WHERE  script_type = 'PROPERTY_MAPPING'
AND    execution_date >= SYSDATE - 1
GROUP BY script_name;
```

### Regular Maintenance

1. **Review mappings monthly**
   - Remove obsolete mappings
   - Update transformation rules
   - Optimize underperforming scripts

2. **Validate mappings quarterly**
   - Check source/target consistency
   - Verify business rules
   - Update documentation

3. **Performance review**
   - Analyze execution times
   - Identify bottlenecks
   - Implement optimizations

## Troubleshooting Guide

### Common Configuration Issues

| Issue | Solution |
|-------|----------|
| Mapping not triggered | Verify mapping is enabled and source property exists |
| Wrong target property updated | Check target property name in configuration |
| Transformation not applied | Ensure Logic Script is selected and associated |
| Performance degradation | Review batch size and implement caching |
| Partial updates | Check error logs for specific failures |

### Validation Checklist

Before activating property mapping:

- [ ] Source and target properties exist
- [ ] Data types are compatible
- [ ] Logic Script is tested (if used)
- [ ] Filters are correctly configured
- [ ] Batch size is appropriate
- [ ] Error handling is implemented
- [ ] Logging is enabled
- [ ] Performance impact assessed

## Next Steps

- [Examples](examples.md) - Real-world mapping scenarios
- [API Reference](../../api/packages/hierarchy.md) - Supporting functions
- [Best Practices](../index.md) - General guidelines

---

!!! warning "Important"
    Always test property mappings in a development environment before deploying to production. Property changes can have cascading effects on calculations and reports.