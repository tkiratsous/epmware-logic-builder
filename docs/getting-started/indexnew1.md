# Getting Started with Logic Builder

Welcome to the EPMware Logic Builder module. This section will guide you through the initial setup and help you understand the fundamentals of creating custom logic scripts.

## Overview

The Logic Builder module enables technical users to extend EPMware's functionality through custom PL/SQL scripts. These scripts can automate processes, validate data, synchronize information across applications, and implement complex business logic.

![Logic Builder Overview](../assets/images/logic-builder-overview.png)
*Figure: Logic Builder module in the EPMware application*

## Prerequisites

Before you begin working with Logic Builder, ensure you have:

- **EPMware Access**: Valid login credentials to EPMware
- **Security Permissions**: Logic Builder module access (read or write)
- **Technical Knowledge**: Basic understanding of:
  - PL/SQL programming language
  - EPMware data model and hierarchy concepts
  - Database concepts (tables, views, procedures)

## Key Concepts

### What are Logic Scripts?

Logic Scripts are custom PL/SQL procedures that execute during specific events in EPMware:
- Member creation or modification
- Property validation and derivation
- Workflow transitions
- Data imports and exports
- Deployment operations

### Script Execution Model

```Script Execution Flow
graph LR
    A[User Action] --> B[EPMware Event]
    B --> C{Logic Script Configured?}
    C -->|Yes| D[Execute Script]
    C -->|No| E[Standard Processing]
    D --> F[Script Results]
    F --> G[Continue/Stop Processing]
```

### Script Types Overview

EPMware supports 13 different script types, each designed for specific use cases:

| Category | Script Types | Purpose |
|----------|--------------|---------|
| **Hierarchy** | Dimension Mapping, Pre/Post Hierarchy Actions | Manage hierarchies and synchronization |
| **Properties** | Property Mapping, Derivations, Validations | Control property values and rules |
| **Workflow** | On Submit, Custom Task, Request Line Approval | Automate workflow processes |
| **Integration** | ERP Interface, Export Tasks, Deployment | Handle external system integration |

## Quick Start Guide

### Step 1: Verify Access

Check if you have Logic Builder access:

1. Log into EPMware
2. Navigate to the **Configuration** menu
3. Look for **Logic Builder** option
4. If not visible, request access through [Security Provisioning](security-provisioning.md)

![Configuration Menu](../assets/images/configuration-menu-logic-builder.png)
*Figure: Logic Builder in the Configuration menu*

### Step 2: Understand the Interface

The Logic Builder interface consists of:

- **Script Tree**: Organized list of all scripts
- **Script Editor**: PL/SQL code editor with syntax highlighting
- **Properties Panel**: Script configuration options
- **Toolbar**: Save, validate, and management functions

![Logic Builder Interface](../assets/images/logic-builder-interface-labeled.png)
*Figure: Main components of the Logic Builder interface*

### Step 3: Create Your First Script

Follow our step-by-step guide to [create your first script](creating-scripts.md).

### Step 4: Learn Script Structure

Understand the [standard structure](script-structure.md) all Logic Scripts follow.

### Step 5: Explore Script Types

Review the different [script types](script-types.md) and their use cases.

## Development Workflow

The typical Logic Builder development process:

1. **Requirements Analysis**
   - Identify business need
   - Determine appropriate script type
   - Plan script logic

2. **Development**
   - Create script in Logic Builder
   - Write PL/SQL code
   - Validate syntax

3. **Configuration**
   - Associate script with appropriate event
   - Configure parameters
   - Set enable/disable status

4. **Testing**
   - Test in development environment
   - Review debug messages
   - Validate results

5. **Deployment**
   - Promote to UAT for user testing
   - Document script functionality
   - Deploy to production

## Best Practices Summary

- **Always use descriptive names** for scripts and variables
- **Include comprehensive error handling** in all scripts
- **Log debug messages** for troubleshooting
- **Test thoroughly** before production deployment
- **Document your code** with comments
- **Follow naming conventions** (avoid EW_ prefix)

## Common Use Cases

### Data Validation
Ensure data quality by validating:
- Member names follow naming standards
- Property values meet business rules
- Required fields are populated

### Process Automation
Automate repetitive tasks:
- Create related members automatically
- Calculate derived values
- Send notifications on events

### System Integration
Synchronize with external systems:
- Map dimensions between applications
- Transform data during imports
- Generate custom export formats

## Getting Help

### Documentation Resources
- [Script Events Guide](../events/) - Detailed event documentation
- [API Reference](../api/) - Complete API documentation
- [Examples](../appendices/) - Sample scripts and patterns

### Support Channels
- **Technical Support**: support@epmware.com
- **Phone**: 408-614-0442
- **Debug Messages**: Use the Debug Messages report for troubleshooting

## Next Steps

Now that you understand the basics, proceed to:

1. [Security Provisioning](security-provisioning.md) - Set up proper access
2. [Creating Scripts](creating-scripts.md) - Build your first script
3. [Script Types](script-types.md) - Explore different script types
4. [Script Structure](script-structure.md) - Learn script anatomy

---

!!! tip "Pro Tip"
    Start with simple validation scripts to familiarize yourself with the Logic Builder environment before attempting complex integrations or workflow automation.