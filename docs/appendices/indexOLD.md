# Appendices

This section provides essential reference materials for Logic Builder development, including action codes, standard scripts, and technical specifications.

## Quick Reference

The appendices contain critical reference information for Logic Builder developers:

<div class="grid cards" markdown>

-   :material-code-tags:{ .lg .middle } **[Appendix A - Action Codes](action-codes.md)**

    ---

    Complete list of hierarchy action codes used in dimension mapping and hierarchy action scripts

    [:octicons-arrow-right-24: View action codes](action-codes.md)

-   :material-script-text:{ .lg .middle } **[Appendix B - Standard Scripts](standard-scripts.md)**

    ---

    Out-of-the-box Logic Scripts automatically assigned to various application types

    [:octicons-arrow-right-24: Explore scripts](standard-scripts.md)

-   :material-database:{ .lg .middle } **[Appendix C - ERP Import Table](erp-import-table.md)**

    ---

    Technical specification for the EW_IF_LINES table used in ERP integration

    [:octicons-arrow-right-24: View schema](erp-import-table.md)

</div>

## Reference Overview

### Action Codes Reference

Action codes are fundamental to hierarchy operations in EPMware. They determine the type of operation being performed on dimension members:

- **Create Operations**: CMC (Create as Child), CMS (Create as Sibling)
- **Modify Operations**: RM (Rename), P (Edit Properties), ZC (Move)
- **Delete Operations**: DM (Delete Member), RSM (Remove Shared)
- **Special Operations**: ISMC/ISMS (Insert Shared), AC/IC (Activate/Inactivate)

### Standard Scripts Library

EPMware provides pre-built Logic Scripts that are automatically assigned to specific application types:

| Application Type | Validation Script | Purpose |
|-----------------|-------------------|---------|
| Essbase | EW_ESSBASE_VALIDATIONS | Property validation rules for Essbase |
| HFM | EW_HFM_VALIDATIONS | HFM-specific business rules |
| Planning | EW_HP_VALIDATIONS | Planning application validations |
| PCMCS | EW_PCMCS_VALIDATIONS | Profitability and Cost Management |
| TRCS | EW_TRCS_VALIDATIONS | Tax Reporting validations |
| OneStream | EW_ONESTREAM_VALIDATIONS | OneStream-specific rules |

### ERP Integration Table

The `EW_IF_LINES` table is the primary interface for ERP data integration:

```sql
-- Example: Insert a new employee record
INSERT INTO EW_IF_LINES (
    NAME,
    STATUS,
    ACTION_CODE,
    MEMBER_NAME,
    PARENT_NAME,
    APP_NAME,
    DIM_NAME
) VALUES (
    'EW_LOAD_EMPLOYEES',
    'N',
    'CMC',
    'EMP_12345',
    'All_Employees',
    'HFM_PROD',
    'Entity'
);
```

## Usage Guidelines

### When to Reference These Appendices

1. **During Development**
   - Look up action codes for hierarchy operations
   - Review standard script implementations
   - Understand ERP table structure

2. **Troubleshooting**
   - Verify correct action code usage
   - Compare against standard validations
   - Check ERP import field mappings

3. **Integration Projects**
   - Design ERP interface mappings
   - Plan hierarchy synchronization
   - Configure validation rules

### Best Practices

!!! tip "Action Code Usage"
    Always use the correct action code for the intended operation. Incorrect codes can lead to unexpected hierarchy changes or request failures.

!!! warning "Standard Script Modifications"
    Never modify standard scripts directly. Clone them first, then customize the copy to preserve upgrade compatibility.

!!! info "ERP Integration"
    When populating the EW_IF_LINES table, only populate non-system-managed columns. The ERP Import engine handles system columns automatically.

## Common Scenarios

### Scenario 1: Hierarchy Synchronization

When synchronizing hierarchies between applications:

1. Reference **Appendix A** for correct action codes
2. Use appropriate codes in dimension mapping scripts
3. Handle all action types in your logic

### Scenario 2: Custom Validation Implementation

When implementing custom validations:

1. Review **Appendix B** for standard validation patterns
2. Clone relevant standard scripts as templates
3. Modify for your specific requirements

### Scenario 3: ERP Data Loading

When loading data from ERP systems:

1. Consult **Appendix C** for table structure
2. Map ERP fields to EW_IF_LINES columns
3. Use Pre-Import scripts for data transformation

## Additional Resources

- **[API Reference](../api/)** - Complete API documentation
- **[Events Documentation](../events/)** - Detailed event descriptions
- **[Getting Started Guide](../getting-started/)** - Basic concepts and setup

---

!!! note "Version Information"
    These appendices are current as of EPMware version 7.2.x. Check release notes for updates in newer versions.