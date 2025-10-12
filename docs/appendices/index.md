# Appendices

This section provides essential reference materials for Logic Builder development, including action codes, standard scripts, technical specifications, debugging guides, and comprehensive script examples.

## Quick Reference

The appendices contain critical reference information for Logic Builder developers:

<div class="grid cards" markdown>

-   :material-code-tags:{ .lg .middle } **[Appendix A - Action Codes](action-codes)**

    ---

    Complete list of hierarchy action codes used in dimension mapping and hierarchy action scripts

    [:octicons-arrow-right-24: View action codes](action-codes)

-   :material-script-text:{ .lg .middle } **[Appendix B - Standard Scripts](standard-scripts)**

    ---

    Out-of-the-box Logic Scripts automatically assigned to various application types

    [:octicons-arrow-right-24: Explore scripts](standard-scripts)

-   :material-database:{ .lg .middle } **[Appendix C - ERP Import Table](erp-import-table)**

    ---

    Technical specification for the EW_IF_LINES table used in ERP integration

    [:octicons-arrow-right-24: View schema](erp-import-table)

-   :material-bug:{ .lg .middle } **[Appendix D - Debug and Test Guide](debugging)**

    ---

    Comprehensive debugging techniques, testing strategies, and troubleshooting procedures

    [:octicons-arrow-right-24: Learn debugging](debugging)

-   :material-file-code:{ .lg .middle } **[Appendix E - Script Examples](examples/)**

    ---

    Production-ready script examples organized by type with detailed explanations

    [:octicons-arrow-right-24: Browse examples](examples/)

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

### Debug and Test Guide

The debugging guide provides comprehensive techniques for troubleshooting Logic Builder scripts:

- **Debug Logging Framework** - Using the ew_debug.log API effectively
- **Testing Strategies** - Unit testing, integration testing, and test frameworks
- **Common Debugging Scenarios** - Script not executing, unexpected results, performance issues
- **Production Debugging** - Safe debugging techniques for production environments
- **Error Handling Best Practices** - Comprehensive exception management

### Script Examples Library

Over 30 production-ready script examples organized by functionality:

| Category | Examples | Complexity |
|----------|----------|------------|
| **Property Validation** | Email format, cost center validation, date ranges, business rules | 🟢 Basic to 🟡 Intermediate |
| **Property Derivation** | Auto-generate aliases, calculate values, smart defaults | 🟢 Basic to 🟡 Intermediate |
| **Dimension Mapping** | HFM to Planning sync, cross-app coordination, conflict resolution | 🟡 Intermediate to 🔴 Advanced |
| **Workflow Tasks** | Notifications, auto-approval, validation, escalation | 🟡 Intermediate to 🔴 Advanced |
| **Hierarchy Actions** | Audit trails, auto-creation, move validation, cascading deletion | 🟡 Intermediate to 🔴 Advanced |
| **Advanced Patterns** | Bulk processing, recursion, parallel execution, caching | 🔴 Advanced |

## Usage Guidelines

### When to Reference These Appendices

1. **During Development**
   - Look up action codes for hierarchy operations (Appendix A)
   - Review standard script implementations (Appendix B)
   - Understand ERP table structure (Appendix C)
   - Set up debugging framework (Appendix D)
   - Find example scripts to adapt (Appendix E)

2. **Troubleshooting**
   - Verify correct action code usage (Appendix A)
   - Compare against standard validations (Appendix B)
   - Check ERP import field mappings (Appendix C)
   - Use debugging techniques and troubleshooting checklist (Appendix D)
   - Reference working examples for comparison (Appendix E)

3. **Integration Projects**
   - Design ERP interface mappings (Appendix C)
   - Plan hierarchy synchronization (Appendices A & E)
   - Configure validation rules (Appendices B & E)
   - Implement robust error handling (Appendices D & E)

### Best Practices

!!! tip "Action Code Usage"
    Always use the correct action code for the intended operation. Incorrect codes can lead to unexpected hierarchy changes or request failures. Reference Appendix A for the complete list.

!!! warning "Standard Script Modifications"
    Never modify standard scripts directly. Clone them first, then customize the copy to preserve upgrade compatibility. See Appendix B for standard script details.

!!! info "ERP Integration"
    When populating the EW_IF_LINES table, only populate non-system-managed columns. The ERP Import engine handles system columns automatically. Consult Appendix C for field specifications.

!!! success "Debug Early and Often"
    Enable debug logging during development and use the techniques in Appendix D to catch issues early. The debug framework examples in Appendix E show proper implementation patterns.

!!! example "Learn from Examples"
    Start with the script examples in Appendix E as templates. They demonstrate best practices, error handling, and performance optimization techniques.

## Common Scenarios

### Scenario 1: Hierarchy Synchronization

When synchronizing hierarchies between applications:

1. Reference **Appendix A** for correct action codes
2. Use appropriate codes in dimension mapping scripts
3. Review **Appendix E** for dimension mapping examples
4. Implement debug logging per **Appendix D**

### Scenario 2: Custom Validation Implementation

When implementing custom validations:

1. Review **Appendix B** for standard validation patterns
2. Clone relevant standard scripts as templates
3. Study validation examples in **Appendix E**
4. Test thoroughly using techniques from **Appendix D**

### Scenario 3: ERP Data Loading

When loading data from ERP systems:

1. Consult **Appendix C** for table structure
2. Map ERP fields to EW_IF_LINES columns
3. Use Pre-Import script examples from **Appendix E**
4. Debug import issues using **Appendix D** techniques

### Scenario 4: Performance Optimization

When optimizing script performance:

1. Review advanced patterns in **Appendix E**
2. Implement performance monitoring from **Appendix D**
3. Use bulk processing and caching techniques
4. Test with realistic data volumes

### Scenario 5: Troubleshooting Production Issues

When debugging production problems:

1. Use safe debugging techniques from **Appendix D**
2. Reference the troubleshooting checklist
3. Compare against working examples in **Appendix E**
4. Implement appropriate error recovery strategies

## Additional Resources

- **[API Reference](../api/)** - Complete API documentation
- **[Events Documentation](../events/)** - Detailed event descriptions
- **[Getting Started Guide](../getting-started/)** - Basic concepts and setup

---

!!! note "Version Information"
    These appendices are current as of EPMware version 7.2.x. Check release notes for updates in newer versions.

!!! tip "Quick Navigation"
    Use the cards above to quickly jump to specific appendices, or browse the navigation menu for detailed subsections within each appendix.