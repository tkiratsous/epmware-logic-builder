# EPMware Logic Builder Guide

Welcome to the EPMware Logic Builder Guide. This comprehensive guide provides detailed instructions for creating and managing custom logic scripts to extend EPMware's functionality and automate complex business processes.

## About This Guide

The Logic Builder Module allows users to build custom logic in various modules within EPMware to provide solutions for custom requirements such as property validations, custom workflow tasks, and automated hierarchy actions. This guide is designed for developers, administrators, and power users responsible for:

- Creating and maintaining custom logic scripts
- Implementing business rules and validations
- Automating metadata management processes
- Extending EPMware functionality through scripting
- Building custom workflow tasks and integrations

!!! info "Version Information"
    This guide covers EPMware Logic Builder version 2.9, updated September 2025

## Key Features

### Oracle PL/SQL Based
The Logic Builder utilizes Oracle PL/SQL as its programming language, with scripts residing within the EPMware database for optimal performance and security.

### Event-Driven Architecture
Logic Scripts are triggered by specific events in EPMware, such as:
- Hierarchy changes (create, rename, move members)
- Property modifications
- Workflow stage transitions
- Deployment executions
- Export operations

### Rich API Library
Access a comprehensive library of APIs for:
- Hierarchy manipulation
- Property management
- Workflow automation
- Security operations
- Email notifications
- External integrations

## Quick Start

New to Logic Builder? Follow these steps to get started:

1. **[Enable Security Access](getting-started/security-provisioning.md)** - Grant Logic Builder access to appropriate user groups
2. **[Create Your First Script](getting-started/creating-scripts.md)** - Build a simple validation script
3. **[Understand Script Types](getting-started/script-types.md)** - Learn about different script categories
4. **[Configure Script Events](events/)** - Associate scripts with EPMware events
5. **[Test and Debug](getting-started/script-structure.md#debug-and-logging)** - Use logging and error handling

## Script Types Overview

Logic Builder supports multiple script types for different purposes:

| Script Type | Purpose | Common Use Cases |
|------------|---------|------------------|
| **Dimension Mapping** | Synchronize hierarchies across applications | Cross-application member synchronization |
| **Property Mapping** | Map property values between dimensions | Attribute synchronization |
| **Property Validation** | Validate property values | Business rule enforcement |
| **Property Derivation** | Auto-populate property values | Default value assignment |
| **Hierarchy Actions** | Execute logic before/after hierarchy changes | Audit trails, automated tasks |
| **Workflow Tasks** | Custom workflow automation | Conditional approvals, notifications |
| **Deployment Tasks** | Pre/post deployment operations | Validation checks, notifications |
| **ERP Interface** | ERP import/export automation | Data transformation |

## Prerequisites

Before using this guide, ensure you have:

- Administrative or developer access to your EPMware environment
- Basic understanding of Oracle PL/SQL syntax
- Familiarity with EPMware metadata management concepts
- Understanding of your target EPM applications (HFM, Planning, Essbase, etc.)
- Access to the Logic Builder module (via Security Provisioning)

!!! warning "Important Note"
    For cloud deployments, stored database functions are not available. All logic must be implemented within the Script Editor interface.

## Support & Resources

- **Technical Support**: support@epmware.com
- **Phone**: 408-614-0442
- **Website**: [www.epmware.com](https://www.epmware.com)
- **Administrator Guide**: For general EPMware administration topics

---

## Documentation Sections

Explore the complete Logic Builder documentation:

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } **Getting Started**

    ---

    Set up security, create your first script, and learn the basics

    [:octicons-arrow-right-24: Get started](getting-started/)

-   :material-calendar-clock:{ .lg .middle } **Script Events**

    ---

    Configure scripts for dimension mapping, property validation, and workflow automation

    [:octicons-arrow-right-24: Explore events](events/)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete reference for all Logic Builder APIs, functions, and database views

    [:octicons-arrow-right-24: View APIs](api/)

-   :material-code-tags:{ .lg .middle } **Dimension Mapping**

    ---

    Synchronize hierarchies and members across applications

    [:octicons-arrow-right-24: Learn mapping](events/dimension-mapping/)

-   :material-checkbox-marked:{ .lg .middle } **Property Validation**

    ---

    Implement custom validation rules for member properties

    [:octicons-arrow-right-24: Build validations](events/property-validations/)

-   :material-sitemap:{ .lg .middle } **Workflow Automation**

    ---

    Create custom workflow tasks and conditional logic

    [:octicons-arrow-right-24: Automate workflows](events/workflow/)

-   :material-database-import:{ .lg .middle } **ERP Integration**

    ---

    Build custom logic for ERP import and export processes

    [:octicons-arrow-right-24: Integrate ERP](events/erp-interface/)

-   :material-book-open-variant:{ .lg .middle } **Appendices**

    ---

    Action codes, standard scripts, and technical references

    [:octicons-arrow-right-24: Reference](appendices/)

</div>