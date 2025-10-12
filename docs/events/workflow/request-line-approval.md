# Request Line Approval Scripts

Request Line Approval scripts execute before approval actions on individual request lines, providing validation and business logic at the approval moment. These scripts ensure approvers have all necessary information and that approval criteria are met.

## Overview

Line Approval scripts provide:
- **Pre-approval Validation**: Verify before approval
- **Supporting Documentation**: Check attachments/comments
- **Approval Criteria**: Ensure conditions are met
- **Line-level Logic**: Individual line validation
- **Approval Dependencies**: Check related approvals
- **Real-time Checks**: Current data validation

![Line Approval Flow](../../assets/images/line-approval-flow.png)
*Figure: Request line approval validation process*

## When to Use

Line Approval scripts are essential for:
- Validating individual line items before approval
- Checking for required supporting documentation
- Ensuring approval prerequisites are met
- Verifying budget availability at approval time
- Validating cross-line dependencies
- Enforcing approval policies

## Key Characteristics

- **Line-specific**: Executes per request line
- **Blocking**: Can prevent approval
- **Real-time**: Validates current state
- **User-facing**: Messages shown to approver
- **Context-aware**: Access to full request data

## Configuration

### Step 1: Create Line Approval Script

Navigate to **Configuration → Logic Builder**:

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'LINE_APPROVAL_VALIDATION';
  l_line_amount NUMBER;
  l_budget_available NUMBER;
  l_approver_limit NUMBER;
  
  PROCEDURE log(p_msg VARCHAR2) IS
  BEGIN
    ew_debug.log(p_text      => p_msg,
                 p_source_ref => c_script_name);
  END;
  
BEGIN
  -- Initialize
  ew_lb_api.g_status := ew_lb_api.g_success;
  ew_lb_api.g_message := NULL;
  
  log('Line approval for request: ' || ew_lb_api.g_request_id);
  log('Line ID: ' || ew_lb_api.g_request_line_id);
  
  -- Get line details
  SELECT amount, budget_code
  INTO l_line_amount, l_budget_code
  FROM request_lines
  WHERE request_line_id = ew_lb_api.g_request_line_id;
  
  -- Check approver's limit
  l_approver_limit := get_approval_limit(ew_lb_api.g_user_id);
  
  IF l_line_amount > l_approver_limit THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Line amount ($' || TO_CHAR(l_line_amount, '999,999.99') || 
      ') exceeds your approval limit ($' || 
      TO_CHAR(l_approver_limit, '999,999.99') || ')';
    RETURN;
  END IF;
  
  -- Check budget availability
  l_budget_available := get_current_budget(l_budget_code);
  
  IF l_line_amount > l_budget_available THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Insufficient budget. Available: $' || 
      TO_CHAR(l_budget_available, '999,999.99');
  END IF;
  
EXCEPTION
  WHEN OTHERS THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 'Approval validation error: ' || SQLERRM;
    log('Error: ' || SQLERRM);
END;
```

### Step 2: Configure Line Approval

Navigate to appropriate configuration screen based on implementation.

## Common Line Approval Patterns

### Pattern 1: Document Verification

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'VERIFY_LINE_DOCUMENTS';
  l_line_amount NUMBER;
  l_doc_count NUMBER;
  l_doc_types VARCHAR2(500);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get line amount
  SELECT amount
  INTO l_line_amount
  FROM request_lines
  WHERE request_line_id = ew_lb_api.g_request_line_id;
  
  -- Check documentation requirements based on amount
  IF l_line_amount > 10000 THEN
    -- Count required documents
    SELECT COUNT(*), LISTAGG(doc_type, ', ')
    INTO l_doc_count, l_doc_types
    FROM (
      SELECT 'Quote' as doc_type FROM dual WHERE 
        NOT EXISTS (SELECT 1 FROM line_attachments 
                   WHERE line_id = ew_lb_api.g_request_line_id 
                   AND doc_type = 'QUOTE')
      UNION ALL
      SELECT 'Approval' FROM dual WHERE 
        NOT EXISTS (SELECT 1 FROM line_attachments 
                   WHERE line_id = ew_lb_api.g_request_line_id 
                   AND doc_type = 'APPROVAL')
      UNION ALL
      SELECT 'Specification' FROM dual WHERE 
        NOT EXISTS (SELECT 1 FROM line_attachments 
                   WHERE line_id = ew_lb_api.g_request_line_id 
                   AND doc_type = 'SPEC')
    );
    
    IF l_doc_count > 0 THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Missing required documents for amounts over $10,000: ' || 
        l_doc_types;
    END IF;
  END IF;
  
  -- Check for comments/justification
  IF l_line_amount > 5000 THEN
    DECLARE
      l_justification VARCHAR2(4000);
    BEGIN
      SELECT comments
      INTO l_justification
      FROM request_lines
      WHERE request_line_id = ew_lb_api.g_request_line_id;
      
      IF l_justification IS NULL OR LENGTH(l_justification) < 50 THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'Detailed justification required for amounts over $5,000 ' ||
          '(minimum 50 characters)';
      END IF;
    END;
  END IF;
END;
```

### Pattern 2: Cross-Line Dependencies

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CHECK_LINE_DEPENDENCIES';
  l_parent_line_id NUMBER;
  l_parent_status VARCHAR2(50);
  l_total_approved NUMBER;
  l_request_total NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Check if line has parent dependency
  SELECT parent_line_id
  INTO l_parent_line_id
  FROM request_lines
  WHERE request_line_id = ew_lb_api.g_request_line_id;
  
  IF l_parent_line_id IS NOT NULL THEN
    -- Check parent line status
    SELECT approval_status
    INTO l_parent_status
    FROM request_lines
    WHERE request_line_id = l_parent_line_id;
    
    IF l_parent_status != 'APPROVED' THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Parent line must be approved first (Line #' || 
        get_line_number(l_parent_line_id) || ')';
      RETURN;
    END IF;
  END IF;
  
  -- Check total approval limits
  SELECT SUM(CASE WHEN approval_status = 'APPROVED' 
                  THEN amount ELSE 0 END),
         SUM(amount)
  INTO l_total_approved, l_request_total
  FROM request_lines
  WHERE request_id = ew_lb_api.g_request_id;
  
  -- Add current line to approved total
  l_total_approved := l_total_approved + 
    get_line_amount(ew_lb_api.g_request_line_id);
  
  -- Check if total would exceed threshold
  IF l_total_approved > 1000000 AND 
     get_user_role(ew_lb_api.g_user_id) != 'EXECUTIVE' THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Total approved amount would exceed $1M. ' ||
      'Executive approval required.';
  END IF;
END;
```

### Pattern 3: Real-time Budget Check

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'REALTIME_BUDGET_CHECK';
  l_budget_code VARCHAR2(50);
  l_line_amount NUMBER;
  l_current_budget NUMBER;
  l_committed NUMBER;
  l_available NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get line details
  SELECT budget_code, amount
  INTO l_budget_code, l_line_amount
  FROM request_lines
  WHERE request_line_id = ew_lb_api.g_request_line_id;
  
  -- Get current budget (real-time from finance system)
  l_current_budget := get_current_budget_from_erp(
    p_budget_code => l_budget_code,
    p_as_of_date  => SYSDATE
  );
  
  -- Get already committed amount
  l_committed := get_committed_amount(
    p_budget_code => l_budget_code,
    p_exclude_request => ew_lb_api.g_request_id
  );
  
  -- Calculate available
  l_available := l_current_budget - l_committed;
  
  ew_debug.log('Budget check: Current=' || l_current_budget ||
               ', Committed=' || l_committed ||
               ', Available=' || l_available ||
               ', Requested=' || l_line_amount);
  
  IF l_line_amount > l_available THEN
    ew_lb_api.g_status := ew_lb_api.g_error;
    ew_lb_api.g_message := 
      'Insufficient budget for ' || l_budget_code || '. ' ||
      'Available: $' || TO_CHAR(l_available, '999,999.99') || ', ' ||
      'Requested: $' || TO_CHAR(l_line_amount, '999,999.99');
    
    -- Provide alternative suggestion
    IF l_available > 0 THEN
      ew_lb_api.g_message := ew_lb_api.g_message ||
        '. Consider approving partial amount or deferring to next period.';
    END IF;
  END IF;
END;
```

### Pattern 4: Compliance Validation

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'LINE_COMPLIANCE_CHECK';
  l_vendor_id NUMBER;
  l_vendor_status VARCHAR2(50);
  l_compliance_flag VARCHAR2(1);
  l_category VARCHAR2(50);
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Get line details
  SELECT vendor_id, category
  INTO l_vendor_id, l_category
  FROM request_lines
  WHERE request_line_id = ew_lb_api.g_request_line_id;
  
  -- Check vendor compliance
  IF l_vendor_id IS NOT NULL THEN
    SELECT status, compliance_certified
    INTO l_vendor_status, l_compliance_flag
    FROM vendors
    WHERE vendor_id = l_vendor_id;
    
    -- Check vendor status
    IF l_vendor_status != 'ACTIVE' THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Vendor is not active (Status: ' || l_vendor_status || ')';
      RETURN;
    END IF;
    
    -- Check compliance certification
    IF l_category IN ('HAZMAT', 'MEDICAL', 'FINANCIAL') THEN
      IF l_compliance_flag != 'Y' THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 
          'Vendor not certified for ' || l_category || ' category';
        RETURN;
      END IF;
    END IF;
  END IF;
  
  -- Check category-specific requirements
  CASE l_category
    WHEN 'IT_HARDWARE' THEN
      IF NOT has_it_security_review(ew_lb_api.g_request_line_id) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'IT Security review required';
      END IF;
      
    WHEN 'CONTRACTOR' THEN
      IF NOT has_insurance_verification(l_vendor_id) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Contractor insurance verification required';
      END IF;
      
    WHEN 'SUBSCRIPTION' THEN
      IF NOT has_legal_review(ew_lb_api.g_request_line_id) THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Legal review required for subscriptions';
      END IF;
  END CASE;
END;
```

### Pattern 5: Approval History Check

```sql
DECLARE
  c_script_name CONSTANT VARCHAR2(100) := 'CHECK_APPROVAL_HISTORY';
  l_previous_rejections NUMBER;
  l_last_rejection_reason VARCHAR2(4000);
  l_days_since_rejection NUMBER;
  
BEGIN
  ew_lb_api.g_status := ew_lb_api.g_success;
  
  -- Check if line was previously rejected
  SELECT COUNT(*), MAX(rejection_reason), 
         MAX(TRUNC(SYSDATE - rejection_date))
  INTO l_previous_rejections, l_last_rejection_reason,
       l_days_since_rejection
  FROM request_line_history
  WHERE request_line_id = ew_lb_api.g_request_line_id
  AND action = 'REJECTED';
  
  IF l_previous_rejections > 0 THEN
    -- Check if issues were addressed
    IF l_days_since_rejection < 3 THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Line was rejected ' || l_days_since_rejection || 
        ' days ago. Previous rejection reason: ' || 
        l_last_rejection_reason || 
        '. Please ensure issues have been addressed.';
    END IF;
    
    -- Require additional documentation for previously rejected lines
    IF NOT has_rejection_resolution(ew_lb_api.g_request_line_id) THEN
      ew_lb_api.g_status := ew_lb_api.g_error;
      ew_lb_api.g_message := 
        'Previously rejected line requires documentation ' ||
        'explaining how issues were resolved';
    END IF;
  END IF;
  
  -- Check approval patterns
  IF has_suspicious_pattern(ew_lb_api.g_request_id) THEN
    -- Flag for additional review
    ew_lb_api.g_message := 
      'WARNING: Unusual approval pattern detected. ' ||
      'Please review carefully.';
    -- Don't block, just warn
  END IF;
END;
```

## Best Practices

### 1. Provide Context
```sql
-- Good: Specific with context
ew_lb_api.g_message := 
  'Cannot approve Line #' || l_line_num || ' (Part #' || l_part_num || '): ' ||
  'Exceeds remaining budget by $' || TO_CHAR(l_excess, '999,999.99') || '. ' ||
  'Consider reducing quantity from ' || l_quantity || ' to ' || l_max_quantity;

-- Bad: Generic
ew_lb_api.g_message := 'Budget exceeded';
```

### 2. Real-time Validation
```sql
-- Always use current data for approval
l_current_budget := get_realtime_budget(); -- Not cached
l_vendor_status := get_current_vendor_status(); -- Fresh lookup
```

### 3. Performance for Bulk
```sql
-- Optimize for bulk approvals
IF is_bulk_approval() THEN
  -- Use single query for all lines
  validate_all_lines_together();
ELSE
  -- Individual validation
  validate_single_line();
END IF;
```

### 4. Clear Action Items
```sql
-- Tell approver what to do
IF validation_fails THEN
  ew_lb_api.g_message := 
    'Action Required: ' ||
    '1. Request budget increase from Finance, or ' ||
    '2. Reduce line amount to $' || l_available || ' or less, or ' ||
    '3. Defer to next budget period';
END IF;
```

## Testing Line Approval Scripts

### Test Scenarios

| Scenario | Test Case | Expected Result |
|----------|-----------|-----------------|
| Valid Line | All criteria met | Approval allowed |
| Over Limit | Exceeds approver limit | Error with limit info |
| No Budget | Insufficient funds | Error with available amount |
| Missing Docs | Required attachments missing | Error listing documents |
| Dependencies | Parent not approved | Error with dependency |
| Compliance | Vendor not certified | Compliance error |

### Debug Logging
```sql
-- Comprehensive logging for troubleshooting
ew_debug.log('=== Line Approval Validation ===');
ew_debug.log('Request ID: ' || ew_lb_api.g_request_id);
ew_debug.log('Line ID: ' || ew_lb_api.g_request_line_id);
ew_debug.log('Approver: ' || ew_lb_api.g_user_id);
ew_debug.log('Amount: ' || l_line_amount);
ew_debug.log('Budget Available: ' || l_budget_available);
ew_debug.log('Validation Result: ' || ew_lb_api.g_status);
```

## Performance Considerations

### Optimize Queries
```sql
-- Use single query for multiple checks
SELECT 
  amount,
  budget_code,
  (SELECT COUNT(*) FROM line_attachments 
   WHERE line_id = rl.request_line_id) as doc_count,
  (SELECT compliance_flag FROM vendors 
   WHERE vendor_id = rl.vendor_id) as vendor_compliant
INTO l_amount, l_budget_code, l_doc_count, l_vendor_compliant
FROM request_lines rl
WHERE request_line_id = ew_lb_api.g_request_line_id;
```

### Cache Static Data
```sql
-- Cache approval limits (changes rarely)
IF g_approval_limits.EXISTS(ew_lb_api.g_user_id) THEN
  l_limit := g_approval_limits(ew_lb_api.g_user_id);
ELSE
  l_limit := get_approval_limit(ew_lb_api.g_user_id);
  g_approval_limits(ew_lb_api.g_user_id) := l_limit;
END IF;
```

### Async Heavy Operations
```sql
-- Queue complex checks for async processing
IF requires_deep_analysis(ew_lb_api.g_request_line_id) THEN
  queue_for_analysis(ew_lb_api.g_request_line_id);
  ew_lb_api.g_message := 
    'Line queued for detailed analysis. ' ||
    'You will be notified when ready for approval.';
  ew_lb_api.g_status := ew_lb_api.g_warning; -- Custom status
END IF;
```

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow approval | Complex validation | Optimize queries, cache data |
| Confusing messages | Technical jargon | Use business language |
| False blocks | Stale data | Use real-time lookups |
| Bulk approval fails | Not optimized for bulk | Add bulk logic path |

## Next Steps

- [On Submit Tasks](on-submit.md) - Pre-workflow validation
- [Custom Tasks](custom-tasks.md) - Complex workflow logic
- [Workflow Index](index.md) - Workflow overview

---

!!! warning "Important"
    Line approval scripts execute for each line individually. Ensure validations are efficient, especially for requests with many lines. Consider bulk optimization strategies for large requests.