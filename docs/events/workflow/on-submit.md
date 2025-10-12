# On Submit Workflow Tasks

On Submit tasks execute before a request enters workflow, providing a validation gate to ensure request completeness and correctness. These scripts can prevent workflow initiation if validation fails.

## Overview

On Submit validation ensures:
- **Request Completeness**: All required information present
- **Business Rules**: Request meets policy requirements
- **Data Quality**: Information is valid and consistent
- **Prerequisites**: Required conditions are met
- **Authorization**: User can submit this request type

![On Submit Validation Flow](../../assets/images/on-submit-flow.png)
*Figure: On Submit validation before workflow entry*

## When to Use

On Submit scripts are essential for:
- Validating complete request before workflow
- Checking business rule compliance
- Ensuring required attachments exist
- Verifying approval thresholds
- Validating cross-line item rules
- Preventing invalid requests from entering workflow

## Key Characteristics

- **Blocking**: Can prevent workflow entry
- **Synchronous**: User waits for validation
- **All-or-nothing**: Entire request validated
- **User-facing**: Messages shown immediately
- **Performance critical**: Users expect quick response

## Configuration

### Step 1: Create the Script

Navigate to **Configuration → Logic Builder**:

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'ON_SUBMIT_VALIDATION';
  l_total_amount NUMBER;
  l_line_count NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('On Submit validation for request: ' || ew_lb_api.g_request_id);
  
  -- Get request details
  SELECT COUNT(*), SUM(amount)
  INTO l_line_count, l_total_amount
  FROM ew_request_lines
  WHERE request_id = ew_lb_api.g_request_id;
  
  -- Validation logic
  IF l_line_count = 0 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Request must contain at least one line item';
  ELSIF l_total_amount > 1000000 THEN
    -- Check for required approvals
    IF NOT has_executive_pre_approval(ew_lb_api.g_request_id) THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 'Requests over $1M require executive pre-approval';
    END IF;
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Step 2: Configure in Workflow Builder

Navigate to **Workflow → Builder**:

1. Select the workflow
2. Go to "On Submit" tab
3. Add Logic Script
4. Select your validation script
5. Set execution order (if multiple)

![On Submit Configuration](../../assets/images/on-submit-configuration.png)
*Figure: Configuring On Submit validation in Workflow Builder*

## Common Validation Patterns

### Pattern 1: Check Required Fields

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CHECK_REQUIRED_FIELDS';
  l_missing_fields VARCHAR2(4000);
  
  PROCEDURE check_field(
    p_field_name VARCHAR2,
    p_field_value VARCHAR2
  ) IS
  BEGIN
    IF p_field_value IS NULL OR TRIM(p_field_value) IS NULL THEN
      IF l_missing_fields IS NOT NULL THEN
        l_missing_fields := l_missing_fields || ', ';
      END IF;
      l_missing_fields := l_missing_fields || p_field_name;
    END IF;
  END;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Check required fields
  FOR req IN (
    SELECT request_id, business_reason, cost_center,
           budget_year, department_head_approval
    FROM ew_request_headers
    WHERE request_id = ew_lb_api.g_request_id
  ) LOOP
    check_field('Business Reason', req.business_reason);
    check_field('Cost Center', req.cost_center);
    check_field('Budget Year', req.budget_year);
    
    -- Conditional requirement
    IF get_request_amount() > 50000 THEN
      check_field('Department Head Approval', req.department_head_approval);
    END IF;
  END LOOP;
  
  IF l_missing_fields IS NOT NULL THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Required fields missing: ' || l_missing_fields;
  END IF;
END;
```

### Pattern 2: Validate Line Items

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VALIDATE_LINE_ITEMS';
  l_errors VARCHAR2(4000);
  l_line_num NUMBER := 0;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Validate each line item
  FOR line IN (
    SELECT line_number, member_name, amount, 
           effective_date, account_code
    FROM ew_request_lines
    WHERE request_id = ew_lb_api.g_request_id
    ORDER BY line_number
  ) LOOP
    l_line_num := l_line_num + 1;
    
    -- Check amount is positive
    IF line.amount <= 0 THEN
      l_errors := l_errors || 'Line ' || l_line_num || 
                  ': Amount must be positive; ';
    END IF;
    
    -- Check effective date is future
    IF line.effective_date < TRUNC(SYSDATE) THEN
      l_errors := l_errors || 'Line ' || l_line_num || 
                  ': Effective date must be future; ';
    END IF;
    
    -- Validate account code exists
    IF NOT is_valid_account(line.account_code) THEN
      l_errors := l_errors || 'Line ' || l_line_num || 
                  ': Invalid account code; ';
    END IF;
    
    -- Check member exists
    IF ew_hierarchy.chk_member_exists(
         p_app_dimension_id => get_app_dimension_id(),
         p_member_name     => line.member_name
       ) = 'N' THEN
      l_errors := l_errors || 'Line ' || l_line_num || 
                  ': Member does not exist; ';
    END IF;
  END LOOP;
  
  IF l_errors IS NOT NULL THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Line item errors: ' || l_errors;
  END IF;
END;
```

### Pattern 3: Check Attachments

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CHECK_ATTACHMENTS';
  l_attachment_count NUMBER;
  l_amount NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get request amount
  SELECT SUM(amount)
  INTO l_amount
  FROM ew_request_lines
  WHERE request_id = ew_lb_api.g_request_id;
  
  -- Check attachment requirements based on amount
  IF l_amount > 100000 THEN
    -- Count attachments
    SELECT COUNT(*)
    INTO l_attachment_count
    FROM ew_request_attachments
    WHERE request_id = ew_lb_api.g_request_id
    AND attachment_type IN ('QUOTE', 'PROPOSAL', 'CONTRACT');
    
    IF l_attachment_count = 0 THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Requests over $100,000 require supporting documentation ' ||
        '(Quote, Proposal, or Contract)';
    END IF;
    
    -- Check for specific document
    IF NOT has_attachment_type(ew_lb_api.g_request_id, 'BUDGET_APPROVAL') THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Budget approval document required for amounts over $100,000';
    END IF;
  END IF;
END;
```

### Pattern 4: Cross-Validation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CROSS_VALIDATION';
  l_total_percent NUMBER;
  l_budget_available NUMBER;
  l_requested_amount NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Check percentage allocations sum to 100
  SELECT SUM(allocation_percent)
  INTO l_total_percent
  FROM ew_request_lines
  WHERE request_id = ew_lb_api.g_request_id;
  
  IF ABS(l_total_percent - 100) > 0.01 THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Allocation percentages must sum to 100% (currently ' || 
      l_total_percent || '%)';
    RETURN;
  END IF;
  
  -- Check budget availability
  l_budget_available := get_available_budget(
    p_cost_center => get_request_cost_center(ew_lb_api.g_request_id),
    p_year       => get_request_year(ew_lb_api.g_request_id)
  );
  
  SELECT SUM(amount)
  INTO l_requested_amount
  FROM ew_request_lines
  WHERE request_id = ew_lb_api.g_request_id;
  
  IF l_requested_amount > l_budget_available THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Insufficient budget. Available: $' || 
      TO_CHAR(l_budget_available, '999,999,999.99') ||
      ', Requested: $' || 
      TO_CHAR(l_requested_amount, '999,999,999.99');
  END IF;
END;
```

### Pattern 5: Business Rule Validation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'BUSINESS_RULE_VALIDATION';
  l_request_type VARCHAR2(50);
  l_urgency VARCHAR2(20);
  l_lead_time NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get request details
  SELECT request_type, urgency, 
         effective_date - TRUNC(SYSDATE) as lead_time
  INTO l_request_type, l_urgency, l_lead_time
  FROM ew_request_headers
  WHERE request_id = ew_lb_api.g_request_id;
  
  -- Apply business rules based on request type
  CASE l_request_type
    WHEN 'CAPITAL_EXPENDITURE' THEN
      -- Requires 30-day lead time
      IF l_lead_time < 30 THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'Capital expenditure requests require 30-day advance notice';
      END IF;
      
    WHEN 'EMERGENCY_PURCHASE' THEN
      -- Requires justification
      IF NOT has_emergency_justification(ew_lb_api.g_request_id) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'Emergency purchases require detailed justification';
      END IF;
      
    WHEN 'BUDGET_TRANSFER' THEN
      -- Check transfer rules
      IF NOT validate_budget_transfer_rules(ew_lb_api.g_request_id) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'Budget transfer violates policy (see help for details)';
      END IF;
  END CASE;
  
  -- Check urgency justification
  IF l_urgency = 'HIGH' AND l_request_type != 'EMERGENCY_PURCHASE' THEN
    IF NOT has_urgency_approval(ew_lb_api.g_request_id) THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'High urgency requests require manager pre-approval';
    END IF;
  END IF;
END;
```

## Best Practices

### 1. Fail Fast
```sql
-- Check simplest validations first
IF simple_check_fails THEN
  ew_lb_api.g_status := ew_lb_api.g_error;
  ew_lb_api.g_message := 'Simple check failed';
  RETURN; -- Don't continue
END IF;

-- Then complex validations
IF complex_check_fails THEN
  -- ...
END IF;
```

### 2. Accumulate All Errors
```sql
DECLARE
  l_errors VARCHAR2(4000);
  
  PROCEDURE add_error(p_msg VARCHAR2) IS
  BEGIN
    IF l_errors IS NOT NULL THEN
      l_errors := l_errors || '; ';
    END IF;
    l_errors := l_errors || p_msg;
  END;
  
BEGIN
  -- Check all validations
  IF check1_fails THEN add_error('Check 1 failed'); END IF;
  IF check2_fails THEN add_error('Check 2 failed'); END IF;
  IF check3_fails THEN add_error('Check 3 failed'); END IF;
  
  -- Return all errors at once
  IF l_errors IS NOT NULL THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := l_errors;
  END IF;
END;
```

### 3. Provide Helpful Messages
```sql
-- Good: Specific and actionable
ew_lb_api.g_message := 
  'Budget approval attachment missing. Please attach signed ' ||
  'budget approval form (template available in Help menu)';

-- Bad: Generic
ew_lb_api.g_message := 'Missing attachment';
```

### 4. Performance Optimization
```sql
-- Use single query for multiple checks
SELECT 
  CASE 
    WHEN business_reason IS NULL THEN 'Y' 
    ELSE 'N' 
  END as missing_reason,
  CASE 
    WHEN amount > 100000 AND attachment_count = 0 THEN 'Y' 
    ELSE 'N' 
  END as missing_attachment,
  CASE 
    WHEN effective_date < SYSDATE THEN 'Y' 
    ELSE 'N' 
  END as invalid_date
INTO l_missing_reason, l_missing_attachment, l_invalid_date
FROM request_summary_view
WHERE request_id = ew_lb_api.g_request_id;
```

## Testing On Submit Scripts

### Test Matrix

| Scenario | Test Case | Expected Result |
|----------|-----------|-----------------|
| Valid Request | All fields complete | Pass validation |
| Missing Required | Leave field empty | Error with field name |
| Invalid Amount | Negative or zero | Error message |
| Missing Attachment | High value, no docs | Attachment error |
| Budget Exceeded | Request > available | Budget error |
| Multiple Errors | Several issues | All errors listed |

### Debug Logging
```sql
-- Enable detailed logging
ew_debug.log('=== On Submit Validation ===');
ew_debug.log('Request ID: ' || ew_lb_api.g_request_id);
ew_debug.log('Request Type: ' || l_request_type);
ew_debug.log('Total Amount: ' || l_total_amount);
ew_debug.log('Line Count: ' || l_line_count);

-- Log validation results
ew_debug.log('Validation Status: ' || ew_lb_api.g_status);
IF ew_lb_api.g_status = ew_lb_api.g_error THEN
  ew_debug.log('Error: ' || ew_lb_api.g_message);
END IF;
```

## Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Validation too slow | Complex queries | Optimize queries, add indexes |
| Users confused | Unclear messages | Improve error messages |
| False positives | Logic too strict | Review business rules |
| Validation missed | Incomplete checks | Add missing validations |

## Performance Considerations

### Query Optimization
```sql
-- Create indexes for validation queries
CREATE INDEX idx_request_validation 
ON ew_request_lines(request_id, amount, effective_date);

-- Use EXISTS instead of COUNT
-- Good
IF EXISTS (SELECT 1 FROM attachments WHERE ...) THEN

-- Less efficient
SELECT COUNT(*) INTO l_count FROM attachments WHERE ...
IF l_count > 0 THEN
```

### Caching
```sql
-- Cache reference data
g_valid_accounts VARCHAR2(4000);

IF g_valid_accounts IS NULL THEN
  SELECT LISTAGG(account_code, ',')
  INTO g_valid_accounts
  FROM valid_accounts
  WHERE active = 'Y';
END IF;
```

## Next Steps

- [Custom Tasks](custom-tasks.md) - Complex workflow logic
- [Request Line Approval](request-line-approval.md) - Approval validation
- [Workflow Index](index.md) - Workflow overview

---

!!! warning "Performance Critical"
    On Submit scripts directly impact user experience. Keep validation logic fast and provide clear, actionable error messages. Consider deferring complex checks to later workflow stages when possible.