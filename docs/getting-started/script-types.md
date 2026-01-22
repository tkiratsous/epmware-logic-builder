# :material-notebook:{ .lg .middle } **Logic Builder Script Types**

EPMware Logic Builder supports multiple script types, each designed for specific events and use cases within the metadata management lifecycle.

## Script Type Overview

| # | Script Type | Purpose |
| --- | --- | --- |
| 1 | Dimension Mapping | Synchronize hierarchies across applications. |
| 2 | Property Mapping | Synchronize property values across applications using custom logic mapped nodes |
| 3 | Pre Hierarchy Actions | Execute custom logic before a specific hierarchy action is performed on a member, such as Create Member. |
| 4 | Post Hierarchy Actions | Execute custom logic after a specific hierarchy action is performed on a member, such as Create Member. |
| 5 | Property Derivations | Derive Property Values |
| 6 | Property Validations | Validate Property Values |
| 7 | On Submit Workflow<br><br> | Execute the script whenever a request is submitted to the workflow. If the Logic Script returns with the Error status, then the request will not be submitted into the workflow and all error messages returned by the script will be shown to the requestor. |
| 8 | On Request Line Approval | Execute the script when user approves a request line OR performs Mass Approval on a request. |
| 9 | Workflow Custom Task | Used to perform custom tasks in workflow (custom type of task) |
| 10 | Deployment Tasks | Used in Pre and Post Deployment Tasks |
| 11 | ERP Interface Tasks | Used in Pre and Post ERP Import execution tasks |
| 12 | Pre Export Generation Tasks | Execute custom script before Export module generates file |
| 13 | Post Export Generation Tasks | Execute custom script after Export module generates file |


## Next Steps

- [Script structure](logic-script-body.md)
- [Script Associations](logic-script-associations.md)
- [Script Usage Report](logic-script-usage-report.md)
- [Explore specific script Events](../events/index.md)