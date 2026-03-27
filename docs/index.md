# **EPMware Logic Builder Guide**

Welcome to the **EPMware Logic Builder Guide**...!!!  
This guide provides comprehensive instructions for creating and managing custom logic scripts to extend EPMware functionality and automate complex business processes.


## 📘 About This Guide

The Logic Builder module enables users to build custom logic across multiple EPMware modules to address advanced business requirements such as:

- Custom property validations  
- Executing custom tasks within workflows  
- Automating metadata and system processes



## 🧩 Script Development Options

The Logic Builder uses Oracle PL/SQL as its programming language, and all scripts reside within the EPMware database.

For On-Premise customers only, it is also possible to:

- Develop stored database functions  
- Reference those functions from Logic Scripts  

This approach allows business logic to remain hidden from the front-end, improving security and maintainability.



## 🔗 Script Assignment & Execution

All Logic Scripts must be assigned to their respective configurations to be executed.

The execution flow follows a two-step process:

  1. Create the Logic Script in the Logic Builder module  
  2. Assign the script in its related configuration screen

For example:
  - A Dimension Mapping logic script executes only when it is referenced in the Dimension Mapping configuration
  - The script runs when a triggering event occurs, such as creating a new request line for a mapped dimension

In summary, Logic Scripts are executed only when both:
  - They are correctly configured
  - A related system event is triggered

---

!!! tip
    Always verify script assignment in the configuration screen to ensure the script executes as expected.


## Prerequisites

Before using this guide, ensure you have:

- Access to your EPMware environment
- Basic understanding of Oracle PL/SQL syntax
- Familiarity with EPMware metadata management concepts
- Access to the Logic Builder module (via Security Provisioning)

!!! warning "Important Note"
    For cloud deployments, stored database functions are not available. All logic must be implemented within the Script Editor interface.


## Quick Start

Explore the complete Logic Builder documentation:

<div class="grid cards" markdown>

-   :material-lock:{ .lg .middle } **[Security Provisioning](getting-started/security-provisioning)**


    Configure user access to Logic Builder module

    [:octicons-arrow-right-24: Get started](getting-started/security-provisioning.md)

-   :material-puzzle:{ .lg .middle } **[Create Logic Builder Scripts](getting-started/creating-scripts)**


    Build your first logic script

    [:octicons-arrow-right-24: Start Building](getting-started/creating-scripts.md)

-   :material-calendar-clock:{ .lg .middle } **[Logic Script Events](events/index.md)** 


    Understand script events eg. dimension mapping, property validation, property derivation etc.

    [:octicons-arrow-right-24: Explore events](events/)

-   :material-code-braces:{ .lg .middle } **[Logic Builder Script Body](getting-started/logic-script-body)** 
    
    Understand Logic Script Structure, Validation, Association, debug and logging

    [:octicons-arrow-right-24: View Script Structure](getting-started/logic-script-body)
    
-   :material-chart-box:{ .lg .middle } **[Logic Script Usage Report ](getting-started/logic-script-usage-report)** 


    Report to view logic script usage across different applications.

    [:octicons-arrow-right-24: Get started](getting-started/logic-script-usage-report)

-   :material-api:{ .lg .middle } **[Logic Builder API Library](api/)** 


    Complete reference for all Logic Builder APIs, functions, and database views

    [:octicons-arrow-right-24: View APIs](api/)

<!--
-   :material-code-tags:{ .lg .middle } **[Dimension Mapping](events/dimension-mapping/)** 

    ---

    Synchronize hierarchies and members across applications

    [:octicons-arrow-right-24: Learn mapping](events/dimension-mapping/)

-   :material-checkbox-marked:{ .lg .middle } **[Property Validation](events/property-validations/)**

    ---

    Implement custom validation rules for member properties

    [:octicons-arrow-right-24: Build validations](events/property-validations/)

-   :material-sitemap:{ .lg .middle } **[Workflow Automation](events/workflow-custom_task/)**

    ---

    Create custom workflow tasks and conditional logic

    [:octicons-arrow-right-24: Automate workflows](events/workflow-custom_task/)

-   :material-database-import:{ .lg .middle } **[ERP Interface Tasks](events/erp-interface/)**

    ---

    Build custom logic for ERP import and export processes

    [:octicons-arrow-right-24: Integrate ERP](events/erp-interface/)
-->
-   :material-book-open-variant:{ .lg .middle } **[Appendices](appendices/)** 


    Action codes, standard scripts, and technical references

    [:octicons-arrow-right-24: Reference](appendices/)

</div>

## Support & Resources

- **Technical Support**: support@epmware.com
- **Phone**: 408-614-0166
- **Website**: [www.epmware.com](https://www.epmware.com)
- **Administrator Guide**: For general EPMware administration topics
