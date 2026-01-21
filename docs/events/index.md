# :material-calendar-sync:{ .lg .middle } **Script Events Overview**

Events in EPMware are actions performed by a user or by a scheduled process in various modules. These interactions may need a Logic Script to execute specific transformations either prior to or after the event is run.
This section will provide details on where Logic Scripts are associated for all Logic Script event types.


## Script Events


| # | Script Type | Purpose | Configuration Location |
|---|-------------|---------|------------------------|
| 1 | **Dimension Mapping** | Synchronize hierarchies across applications | Configuration → Dimension → Mapping |
| 2 | **Property Mapping** | Synchronize property values using custom logic | Configuration → Property → Mapping |
| 3 | **Pre Hierarchy Actions** | Execute logic *before* hierarchy actions | Configuration → Dimension → Hierarchy Actions |
| 4 | **Post Hierarchy Actions** | Execute logic *after* hierarchy actions | Configuration → Dimension → Hierarchy Actions |
| 5 | **Property Derivations** | Calculate and derive property values | Configuration → Property → Derivations |
| 6 | **Property Validations** | Validate property values against business rules | Configuration → Property → Validations |
| 7 | **On Submit Workflow** | Validate before workflow submission | Workflow → Builder |
| 8 | **On Request Line Approval** | Validate on line approval | Workflow → Approve/Review Tasks |
| 9 | **Workflow Custom Task** | Perform custom workflow tasks | Workflow → Custom Tasks |
| 10 | **Deployment Tasks** | Pre/post deployment operations | Deployment Configuration |
| 11 | **ERP Interface Tasks** | Pre/post ERP import execution | ERP Import → Builder |
| 12 | **Pre Export Generation Tasks** | Execute before export file generation |  Export |
| 13 | **Post Export Generation Tasks** | Execute after export file generation |  Export |


## Next Steps

- [Dimension Mapping](dimension-mapping/index.md) - Synchronize hierarchies
- [Property Mapping](property-mapping/index.md) - Synchronize hierarchies
- [Property Validations](property-validations/index.md) - Enforce rules
- [Workflow Tasks](workflow-custom_task/index.md) - Automate processes
- [ERP Interface](erp-interface/index.md) - Integration logic
