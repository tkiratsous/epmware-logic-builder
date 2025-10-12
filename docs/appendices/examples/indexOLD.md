# Logic Builder Script Examples

This section contains real-world examples of Logic Builder scripts organized by type and use case. Each example includes complete, production-ready code with detailed explanations.

## Script Categories

### [Property Validation](property-validation.md)
Scripts that enforce business rules and data quality standards:
- Email format validation
- Cost center format validation
- Date range validation
- Cross-property dependencies
- Custom business rule enforcement

### [Property Derivation](property-derivation.md)
Scripts that automatically populate property values:
- Auto-generate member aliases
- Calculate derived values
- Set default properties
- Concatenate multiple fields
- Apply naming conventions

### [Dimension Mapping](dimension-mapping.md)
Scripts for cross-application synchronization:
- HFM to Planning mappings
- Essbase dimension sync
- Multi-application coordination
- Alternate hierarchy management
- Member relationship validation

### [Workflow Tasks](workflow-tasks.md)
Custom workflow automation scripts:
- Conditional approvals
- Email notifications
- Automated validations
- Stage-based actions
- Integration triggers

### [Hierarchy Actions](hierarchy-actions.md)
Scripts triggered by hierarchy changes:
- Member creation auditing
- Automatic child member creation
- Hierarchy validation
- Move/rename tracking
- Cascading updates

### [Advanced Patterns](advanced-patterns.md)
Complex scripting patterns and techniques:
- Bulk operations
- Recursive processing
- Performance optimization
- Error recovery
- Integration with external systems

## Quick Reference

### Most Common Use Cases

| Use Case | Script Type | Example |
|----------|------------|---------|
| Validate email format | Property Validation | [Email Validator](property-validation.md#email-validation) |
| Auto-populate alias | Property Derivation | [Alias Generator](property-derivation.md#auto-generate-alias) |
| Sync to Planning | Dimension Mapping | [HFM to Planning](dimension-mapping.md#hfm-to-planning) |
| Approval notifications | Workflow Task | [Email on Approval](workflow-tasks.md#approval-notification) |
| Audit member creation | Hierarchy Action | [Creation Audit](hierarchy-actions.md#audit-trail) |

## Best Practices Demonstrated

Each example follows these best practices:

✅ **Error Handling** - Comprehensive exception management  
✅ **Debug Logging** - Detailed logging for troubleshooting  
✅ **Performance** - Optimized for large data volumes  
✅ **Documentation** - Clear comments and explanations  
✅ **Reusability** - Modular, adaptable code structure  

## How to Use These Examples

### 1. Copy and Customize

Each example is designed to be copied and customized for your specific needs:

```sql
-- 1. Copy the entire script
-- 2. Update the script name constant
-- 3. Modify business logic as needed
-- 4. Test in development environment
-- 5. Deploy to production
```

### 2. Understanding the Structure

All examples follow a consistent structure:

```sql
DECLARE
  -- Constants and variables
  c_script_name VARCHAR2(100) := 'YOUR_SCRIPT_NAME';
  
  -- Local procedures
  PROCEDURE log(p_msg IN VARCHAR2) IS...
  
BEGIN
  -- Main logic
  
EXCEPTION
  -- Error handling
END;
```

### 3. Testing Examples

Before using in production:

1. Create test hierarchies/properties
2. Enable debug logging
3. Run through all scenarios
4. Verify debug messages
5. Test error conditions

## Example Complexity Levels

### 🟢 Basic
Simple scripts for common tasks:
- Basic validations
- Simple derivations
- Standard notifications

### 🟡 Intermediate
More complex business logic:
- Multi-step workflows
- Cross-dimension operations
- Conditional processing

### 🔴 Advanced
Sophisticated implementations:
- Bulk processing
- Complex integrations
- Performance-critical operations

## Contributing Examples

If you have useful Logic Builder scripts to share:

1. Follow the example format
2. Include comprehensive comments
3. Add debug logging
4. Test thoroughly
5. Document any prerequisites

## Need Help?

- Review [Getting Started](../getting-started/) for basics
- Check [API Reference](../api/) for available functions
- See [Debugging Guide](../getting-started/debugging.md) for troubleshooting

---

*Browse the examples in the navigation menu or use the quick reference table above to find relevant scripts for your use case.*