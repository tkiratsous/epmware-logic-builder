# Appendix C - ERP Import Table (EW_IF_LINES)

The `EW_IF_LINES` table is the primary interface table for ERP data integration with EPMware. This table can be populated through file uploads (using REST API) or direct database inserts (for On-Premise customers) and is processed by Pre/Post ERP Import Logic Scripts.

!!! info "System-Managed Columns"
    Columns marked as "System Managed" are handled automatically by the ERP Import engine and should not be populated by developers.

## Table Structure

### Primary Columns

| Column Name | Required | System Managed | Data Type | Description | Example |
|------------|----------|----------------|-----------|-------------|---------|
| **NAME** | Yes | No | VARCHAR2(100) | ERP Import configuration name | `EW_LOAD_EMPLOYEES` |
| **STATUS** | Yes | No | VARCHAR2(1) | Record status (N=New, P=Processing, S=Success, E=Error) | `N` |
| **IF_LINE_ID** | No | Yes | NUMBER | Unique line identifier | Auto-generated |
| **IF_CONFIG_ID** | No | Yes | NUMBER | Configuration ID | Auto-generated |
| **IF_EXEC_ID** | No | Yes | NUMBER | Execution batch ID | Auto-generated |
| **MESSAGE** | No | Yes | VARCHAR2(4000) | Processing message/error | System-populated |
| **REFERENCE_NUMBER** | No | No | VARCHAR2(100) | External reference (future use) | `ERP_BATCH_001` |

### User Information Columns

| Column Name | Required | System Managed | Data Type | Description | Example |
|------------|----------|----------------|-----------|-------------|---------|
| **REQUESTOR_USER_NAME** | No | Yes | VARCHAR2(100) | User initiating the import | Auto-populated |
| **REQUESTOR_EMAIL** | No | No | VARCHAR2(200) | Requestor email address | `user@company.com` |
| **ASSIGNEE** | No | No | VARCHAR2(100) | Assigned user for processing | `ADMIN_USER` |

### Hierarchy Columns

| Column Name | Required | Description | Example |
|------------|----------|-------------|---------|
| **ACTION_CODE** | Yes | Hierarchy action (Create, Edit, Delete, Move, etc.) | `Create` |
| **APP_NAME** | Yes | Target application name | `HFM_PROD` |
| **DIM_NAME** | Yes | Target dimension name | `Entity` |
| **MEMBER_NAME** | Yes | Member being processed | `CC_1001` |
| **PARENT_NAME** | Conditional | Parent member (required for Create, Move) | `All_CostCenters` |
| **NEW_MEMBER_NAME** | Conditional | New name (required for Rename) | `CC_1001_NEW` |
| **NEW_PARENT_NAME** | Conditional | New parent (required for Move) | `Region_NA` |
| **HIERARCHY_TYPE** | No | Hierarchy type (Primary/Shared) | `Primary` |

### Property Columns

The table includes 50 generic property columns (PROP_VALUE_1 through PROP_VALUE_50) for member properties:

| Column Pattern | Data Type | Description | Example |
|---------------|-----------|-------------|---------|
| **PROP_VALUE_1** | VARCHAR2(4000) | First property value | `Active` |
| **PROP_VALUE_2** | VARCHAR2(4000) | Second property value | `USD` |
| **...** | VARCHAR2(4000) | ... | ... |
| **PROP_VALUE_50** | VARCHAR2(4000) | Fiftieth property value | `CustomValue` |

## Action Code Values

The following action codes are supported in the ACTION_CODE column:

| Action Code | Description | Required Fields |
|------------|-------------|-----------------|
| **Create** | Create new member | MEMBER_NAME, PARENT_NAME |
| **Create or Edit** | Create if not exists, otherwise update | MEMBER_NAME, PARENT_NAME (for create) |
| **Delete** | Delete member | MEMBER_NAME |
| **Edit** | Update existing member properties | MEMBER_NAME, PROP_VALUE_* |
| **Insert Shared** | Add shared member | MEMBER_NAME, PARENT_NAME |
| **Remove Shared** | Remove shared instance | MEMBER_NAME, PARENT_NAME |
| **Move** | Move member to new parent | MEMBER_NAME, NEW_PARENT_NAME |
| **Rename** | Rename member | MEMBER_NAME, NEW_MEMBER_NAME |
| **Reorder** | Change member order | MEMBER_NAME, PARENT_NAME |

## Usage Examples

### Direct Table Population (On-Premise)

```sql
-- Example 1: Create new cost centers
INSERT INTO EW_IF_LINES (
    NAME,
    STATUS,
    ACTION_CODE,
    APP_NAME,
    DIM_NAME,
    MEMBER_NAME,
    PARENT_NAME,
    PROP_VALUE_1,  -- Alias
    PROP_VALUE_2,  -- Currency
    PROP_VALUE_3   -- Status
) VALUES (
    'EW_LOAD_COSTCENTERS',
    'N',
    'Create',
    'PLANNING_PROD',
    'Entity',
    'CC_2001',
    'All_CostCenters',
    'Marketing Department',
    'USD',
    'Active'
);

-- Example 2: Move existing member
INSERT INTO EW_IF_LINES (
    NAME,
    STATUS,
    ACTION_CODE,
    APP_NAME,
    DIM_NAME,
    MEMBER_NAME,
    NEW_PARENT_NAME
) VALUES (
    'EW_REORG_ENTITIES',
    'N',
    'Move',
    'HFM_PROD',
    'Entity',
    'E10001',
    'Region_EMEA'
);

-- Example 3: Update member properties
INSERT INTO EW_IF_LINES (
    NAME,
    STATUS,
    ACTION_CODE,
    APP_NAME,
    DIM_NAME,
    MEMBER_NAME,
    PROP_VALUE_1,  -- Description
    PROP_VALUE_2   -- Manager
) VALUES (
    'EW_UPDATE_ACCOUNTS',
    'N',
    'Edit',
    'ESSBASE_PROD',
    'Account',
    'Revenue_Total',
    'Total Revenue Account',
    'John Smith'
);
```

### Pre-Import Logic Script Processing

```sql
-- Pre-Import Script: Validate and enrich data
DECLARE
    CURSOR c_new_records IS
        SELECT * FROM EW_IF_LINES
        WHERE NAME = ew_lb_api.g_if_config_name
        AND STATUS = 'N';
        
    l_parent_exists NUMBER;
BEGIN
    log('Pre-Import processing started');
    
    FOR rec IN c_new_records LOOP
        -- Validation: Check parent exists for Create actions
        IF rec.ACTION_CODE = 'Create' THEN
            SELECT COUNT(*)
            INTO l_parent_exists
            FROM ew_members_v
            WHERE member_name = rec.PARENT_NAME
            AND app_name = rec.APP_NAME
            AND dim_name = rec.DIM_NAME;
            
            IF l_parent_exists = 0 THEN
                -- Update status to error
                UPDATE EW_IF_LINES
                SET STATUS = 'E',
                    MESSAGE = 'Parent member does not exist: ' || rec.PARENT_NAME
                WHERE IF_LINE_ID = rec.IF_LINE_ID;
                CONTINUE;
            END IF;
        END IF;
        
        -- Data enrichment: Set default currency if not provided
        IF rec.ACTION_CODE IN ('Create', 'Create or Edit') THEN
            IF rec.PROP_VALUE_2 IS NULL THEN  -- Currency property
                UPDATE EW_IF_LINES
                SET PROP_VALUE_2 = get_default_currency(rec.PARENT_NAME)
                WHERE IF_LINE_ID = rec.IF_LINE_ID;
            END IF;
        END IF;
        
        -- Check for member moves
        IF should_move_member(rec.MEMBER_NAME, rec.PARENT_NAME) THEN
            -- Insert additional move record
            INSERT INTO EW_IF_LINES (
                NAME, STATUS, ACTION_CODE,
                APP_NAME, DIM_NAME,
                MEMBER_NAME, NEW_PARENT_NAME
            ) VALUES (
                rec.NAME, 'N', 'Move',
                rec.APP_NAME, rec.DIM_NAME,
                rec.MEMBER_NAME, get_new_parent(rec.MEMBER_NAME)
            );
            
            log('Move action added for: ' || rec.MEMBER_NAME);
        END IF;
    END LOOP;
    
    log('Pre-Import processing completed');
    
EXCEPTION
    WHEN OTHERS THEN
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Pre-Import error: ' || SQLERRM;
END;
```

### Post-Import Logic Script Processing

```sql
-- Post-Import Script: Cleanup and notifications
DECLARE
    l_success_count NUMBER;
    l_error_count   NUMBER;
BEGIN
    -- Count results
    SELECT 
        SUM(CASE WHEN STATUS = 'S' THEN 1 ELSE 0 END),
        SUM(CASE WHEN STATUS = 'E' THEN 1 ELSE 0 END)
    INTO 
        l_success_count, l_error_count
    FROM 
        EW_IF_LINES
    WHERE 
        IF_EXEC_ID = ew_lb_api.g_if_exec_id;
    
    log('Import completed - Success: ' || l_success_count || 
        ', Errors: ' || l_error_count);
    
    -- Send notification if errors exist
    IF l_error_count > 0 THEN
        send_error_notification();
    END IF;
    
    -- Archive processed records
    INSERT INTO EW_IF_LINES_ARCHIVE
    SELECT * FROM EW_IF_LINES
    WHERE IF_EXEC_ID = ew_lb_api.g_if_exec_id;
    
    -- Clean up processed records
    DELETE FROM EW_IF_LINES
    WHERE IF_EXEC_ID = ew_lb_api.g_if_exec_id
    AND STATUS IN ('S', 'E');
    
    COMMIT;
    
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        ew_lb_api.g_status := ew_lb_api.g_error;
        ew_lb_api.g_message := 'Post-Import error: ' || SQLERRM;
END;
```

## REST API Usage

For cloud deployments, populate the table using REST API:

### Upload File Format (CSV)

```csv
NAME,ACTION_CODE,APP_NAME,DIM_NAME,MEMBER_NAME,PARENT_NAME,PROP_VALUE_1,PROP_VALUE_2
EW_LOAD_EMPLOYEES,Create,HFM_PROD,Entity,E12345,All_Entities,John Doe,Active
EW_LOAD_EMPLOYEES,Edit,HFM_PROD,Entity,E12344,,Jane Smith,Inactive
EW_LOAD_EMPLOYEES,Move,HFM_PROD,Entity,E12343,Region_APAC,,
```

### API Call Example

```bash
# Upload CSV file via REST API
curl -X POST https://epmware-instance.com/api/v1/erp/import \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@employees.csv" \
  -F "config_name=EW_LOAD_EMPLOYEES"
```

## Configuration in EPMware

### Setting Up ERP Import

1. Navigate to **ERP Import → Builder**
2. Create new import configuration
3. Map CSV columns to EW_IF_LINES columns
4. Assign Pre/Post Import Logic Scripts

![ERP Import Configuration](../assets/images/erp-import-builder-config.png)
*Figure: ERP Import Builder configuration screen*

### Property Mapping Configuration

Map source file columns to property columns:

| Source Column | Target Column | Property Name |
|--------------|---------------|---------------|
| ALIAS | PROP_VALUE_1 | Alias |
| CURRENCY | PROP_VALUE_2 | Currency |
| STATUS | PROP_VALUE_3 | MemberStatus |
| MANAGER | PROP_VALUE_4 | Manager |
| DEPARTMENT | PROP_VALUE_5 | Department |

## Performance Considerations

### Batch Processing

```sql
-- Process records in batches
DECLARE
    l_batch_size CONSTANT NUMBER := 1000;
    l_processed  NUMBER := 0;
BEGIN
    LOOP
        -- Process batch
        UPDATE EW_IF_LINES
        SET STATUS = 'P'
        WHERE NAME = ew_lb_api.g_if_config_name
        AND STATUS = 'N'
        AND ROWNUM <= l_batch_size;
        
        l_processed := SQL%ROWCOUNT;
        EXIT WHEN l_processed = 0;
        
        -- Process batch
        process_batch();
        
        COMMIT;
    END LOOP;
END;
```

### Index Recommendations

For optimal performance, ensure indexes exist on:

```sql
-- Recommended indexes
CREATE INDEX IDX_IF_LINES_NAME_STATUS ON EW_IF_LINES(NAME, STATUS);
CREATE INDEX IDX_IF_LINES_EXEC_ID ON EW_IF_LINES(IF_EXEC_ID);
CREATE INDEX IDX_IF_LINES_CONFIG_ID ON EW_IF_LINES(IF_CONFIG_ID);
```

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Records stuck in 'N' status | Import not triggered | Check scheduler/manual execution |
| Duplicate member errors | Member already exists | Use 'Create or Edit' action |
| Parent not found | Invalid parent name | Validate parent exists before import |
| Property mapping fails | Column mismatch | Verify property column assignments |

### Debug Queries

```sql
-- Check import status
SELECT STATUS, COUNT(*) 
FROM EW_IF_LINES 
WHERE NAME = 'YOUR_IMPORT_NAME'
GROUP BY STATUS;

-- View recent errors
SELECT * FROM EW_IF_LINES
WHERE STATUS = 'E'
AND NAME = 'YOUR_IMPORT_NAME'
ORDER BY IF_LINE_ID DESC;

-- Check processing history
SELECT 
    IF_EXEC_ID,
    MIN(CREATED_DATE) start_time,
    MAX(UPDATED_DATE) end_time,
    COUNT(*) record_count
FROM EW_IF_LINES
WHERE NAME = 'YOUR_IMPORT_NAME'
GROUP BY IF_EXEC_ID
ORDER BY IF_EXEC_ID DESC;
```

## Best Practices

!!! tip "Data Validation"
    Always validate data in Pre-Import scripts rather than letting the import fail. This provides better error messages and recovery options.

!!! warning "Transaction Management"
    Use appropriate commit intervals to balance performance with recoverability. Large transactions can cause performance issues.

!!! info "Error Handling"
    Implement comprehensive error handling to capture and log issues without losing the entire batch.

!!! note "Property Column Usage"
    Document which PROP_VALUE columns map to which properties for maintainability.

---

## See Also

- [ERP Interface Tasks](../events/erp-interface/) - Complete ERP integration documentation
- [Pre-Import Tasks](../events/erp-interface/pre-import.md) - Pre-import script examples
- [Post-Import Tasks](../events/erp-interface/post-import.md) - Post-import script examples