# Standard Property Validations

EPMware provides built-in standard validations that can be configured without writing custom Logic Scripts. These validations cover common data quality requirements and can be quickly applied to properties.

## Available Standard Validations

### 1. Required Field Validation

Ensures a property value is not empty or NULL.

**Configuration:**
```yaml
Type: Required
Allow Blank: No
Error Message: "This field is required"
```

**Behavior:**
- Triggers when field is empty
- Prevents saving until populated
- Can allow spaces with "Allow Blank" option

![Required Field Validation](../../assets/images/required-field-validation.png)
*Figure: Required field validation configuration*

### 2. Numeric Range Validation

Validates that numeric values fall within specified bounds.

**Configuration:**
```yaml
Type: Numeric Range
Minimum Value: 0
Maximum Value: 100
Include Minimum: Yes
Include Maximum: Yes
Decimal Places: 2
Error Message: "Value must be between 0 and 100"
```

**Options:**
| Parameter | Description | Example |
|-----------|-------------|---------|
| Minimum Value | Lower bound | 0 |
| Maximum Value | Upper bound | 999999 |
| Include Min/Max | Inclusive bounds | Yes/No |
| Decimal Places | Precision allowed | 0, 2, 4 |
| Allow Negative | Permit negative values | Yes/No |

### 3. Text Length Validation

Enforces minimum and maximum character lengths.

**Configuration:**
```yaml
Type: Text Length
Minimum Length: 3
Maximum Length: 50
Count Spaces: Yes
Error Message: "Must be between 3 and 50 characters"
```

**Use Cases:**
- Member codes (exact length)
- Descriptions (min/max length)
- Abbreviations (max length)

### 4. Pattern/Format Validation

Uses regular expressions to validate format.

**Configuration:**
```yaml
Type: Pattern Match
Pattern: ^[A-Z]{3}[0-9]{4}$
Case Sensitive: Yes
Error Message: "Format must be: 3 letters + 4 numbers (e.g., ABC1234)"
```

**Common Patterns:**

| Pattern Type | Regular Expression | Example |
|--------------|-------------------|---------|
| Email | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` | user@domain.com |
| Phone (US) | `^\([0-9]{3}\) [0-9]{3}-[0-9]{4}$` | (555) 123-4567 |
| Date (MM/DD/YYYY) | `^(0[1-9]|1[0-2])/(0[1-9]|[12][0-9]|3[01])/[0-9]{4}$` | 12/31/2024 |
| Postal Code (US) | `^[0-9]{5}(-[0-9]{4})?$` | 12345 or 12345-6789 |
| Currency | `^\$?[0-9]{1,3}(,[0-9]{3})*(\.[0-9]{2})?$` | $1,234.56 |

### 5. List of Values Validation

Restricts input to predefined values.

**Configuration:**
```yaml
Type: List of Values
Values: Active, Inactive, Pending, Suspended
Case Sensitive: No
Allow Custom: No
Error Message: "Please select from the list"
```

**Implementation Options:**
- Static list (defined in configuration)
- Dynamic list (from lookup table)
- Hierarchical list (with categories)

### 6. Date Validation

Validates date formats and ranges.

**Configuration:**
```yaml
Type: Date
Format: MM/DD/YYYY
Minimum Date: 01/01/2000
Maximum Date: SYSDATE
Allow Future: No
Error Message: "Date must be between 01/01/2000 and today"
```

**Date Validation Rules:**
| Rule | Description |
|------|-------------|
| Format Check | Validates date format |
| Range Check | Within min/max dates |
| Business Day | Only weekdays allowed |
| Fiscal Period | Within fiscal calendar |
| Relative Date | Before/after another date |

### 7. Unique Value Validation

Ensures property value is unique across dimension.

**Configuration:**
```yaml
Type: Unique
Scope: Dimension
Case Sensitive: No
Exclude Inactive: Yes
Error Message: "This value already exists"
```

**Scope Options:**
- **Dimension**: Unique across entire dimension
- **Parent**: Unique among siblings
- **Level**: Unique at same hierarchy level
- **Application**: Unique across application

### 8. Cross-Property Validation

Validates relationships between multiple properties.

**Configuration:**
```yaml
Type: Cross-Property
Rule: End_Date > Start_Date
Properties: Start_Date, End_Date
Error Message: "End date must be after start date"
```

**Common Cross-Validations:**
- Date relationships
- Sum validations (percentages = 100%)
- Conditional requirements
- Mutual exclusivity

## Configuring Standard Validations

### Step 1: Navigate to Property Validations

**Path:** Configuration → Properties → Validations

### Step 2: Select Property

Choose the application, dimension, and property to validate.

### Step 3: Choose Validation Type

Select from standard validation types or custom Logic Script.

![Standard Validation Selection](../../assets/images/standard-validation-selection.png)
*Figure: Selecting standard validation type*

### Step 4: Configure Parameters

Set validation-specific parameters and error messages.

### Step 5: Set Execution Options

| Option | Description | Default |
|--------|-------------|---------|
| Enabled | Activate validation | Yes |
| Real-time | Validate on keystroke | Yes |
| On Save | Validate before saving | Yes |
| Severity | Error or Warning | Error |
| Order | Execution sequence | 100 |

## Combining Multiple Validations

Properties can have multiple validations:

```yaml
Property: Email
Validations:
  1. Required: Yes
  2. Pattern: Email format
  3. Unique: Within dimension
  4. Length: Max 100 characters
```

**Execution Order:**
1. Required check (fastest)
2. Length check
3. Pattern match
4. Uniqueness (slowest)

## Standard Validation Examples

### Example 1: Cost Center Code

```yaml
Property: Cost_Center_Code
Validations:
  - Type: Pattern
    Pattern: ^CC[0-9]{6}$
    Message: "Format: CC + 6 digits (e.g., CC123456)"
  
  - Type: Unique
    Scope: Dimension
    Message: "Cost center code already exists"
```

### Example 2: Budget Amount

```yaml
Property: Budget_Amount
Validations:
  - Type: Required
    Message: "Budget amount is required"
  
  - Type: Numeric Range
    Min: 0
    Max: 999999999.99
    Decimals: 2
    Message: "Amount must be positive with max 2 decimals"
```

### Example 3: Status Field

```yaml
Property: Status
Validations:
  - Type: Required
    Message: "Status is required"
  
  - Type: List of Values
    Values: [Active, Inactive, Pending, Closed]
    Message: "Invalid status value"
```

### Example 4: Email Address

```yaml
Property: Email
Validations:
  - Type: Pattern
    Pattern: Email regex
    Message: "Invalid email format"
  
  - Type: Length
    Max: 255
    Message: "Email too long"
  
  - Type: Unique
    Scope: Application
    Message: "Email already registered"
```

## Performance Considerations

### Validation Performance Impact

| Validation Type | Performance | Impact |
|-----------------|-------------|---------|
| Required | Instant | Minimal |
| Length | Instant | Minimal |
| Pattern | Fast | Low |
| Range | Fast | Low |
| List (Static) | Fast | Low |
| List (Dynamic) | Medium | Medium |
| Unique | Slow | High |
| Cross-Property | Variable | Variable |

### Optimization Tips

1. **Order validations by speed** - Fast checks first
2. **Cache list values** - For dynamic lists
3. **Index unique fields** - Improve uniqueness checks
4. **Limit real-time validation** - For expensive checks
5. **Use async validation** - For complex rules

## Error Message Best Practices

### Good Error Messages

✅ **Specific and Actionable**
```
"Email must contain @ symbol and valid domain (e.g., user@company.com)"
```

✅ **Include Format Example**
```
"Date must be in MM/DD/YYYY format (e.g., 12/31/2024)"
```

✅ **Explain Requirements**
```
"Password must be 8-20 characters with at least one number and symbol"
```

### Poor Error Messages

❌ **Too Generic**
```
"Invalid value"
```

❌ **Technical Jargon**
```
"Regex pattern match failed"
```

❌ **No Guidance**
```
"Error in field"
```

## Migrating to Standard Validations

### From Custom Scripts

If you have custom validation scripts that match standard patterns, consider migrating:

**Before (Custom Script):**
```sql
IF ew_lb_api.g_prop_value IS NULL THEN
  ew_lb_api.g_status := 'E';
  ew_lb_api.g_message := 'Required field';
END IF;
```

**After (Standard Validation):**
```yaml
Type: Required
Message: "Required field"
```

**Benefits:**
- No code maintenance
- Better performance
- Consistent behavior
- Easier configuration

## Validation Testing

### Test Checklist

For each standard validation:

- [ ] Valid values pass
- [ ] Invalid values fail with correct message
- [ ] Edge cases handled
- [ ] NULL handling correct
- [ ] Performance acceptable
- [ ] Error messages clear
- [ ] Works with bulk operations

### Test Data Examples

```sql
-- Test required validation
NULL          -- Should fail
''            -- Should fail
' '           -- Should fail (unless Allow Blank)
'Valid'       -- Should pass

-- Test numeric range (0-100)
-1            -- Should fail
0             -- Should pass
50.5          -- Should pass
100           -- Should pass
101           -- Should fail
'ABC'         -- Should fail

-- Test pattern (CC######)
'CC123456'    -- Should pass
'CC12345'     -- Should fail (too short)
'PC123456'    -- Should fail (wrong prefix)
'CC1234567'   -- Should fail (too long)
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Validation not triggering | Not configured properly | Check property configuration |
| Always passing | Incorrect parameters | Review validation settings |
| Performance slow | Complex validation | Consider custom script for optimization |
| Incorrect error message | Default message used | Customize error message |

### Debug Standard Validations

Enable debug logging to troubleshoot:

1. Navigate to System Settings
2. Enable "Debug Property Validations"
3. Check Debug Messages report
4. Review validation execution details

## Next Steps

- [Examples](examples.md) - Real-world validation scenarios
- [Custom Validations](index.md) - When standard validations aren't enough
- [API Reference](../../api/packages/hierarchy.md) - Supporting functions

---

!!! tip "Best Practice"
    Start with standard validations whenever possible. They're optimized, tested, and require no code maintenance. Only create custom validation scripts when standard validations cannot meet your requirements.