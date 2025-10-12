# Logic Builder Script Types

EPMware Logic Builder supports multiple script types, each designed for specific events and use cases within the metadata management lifecycle.

## Script Type Overview

| # | Script Type | Purpose | Event Trigger |
|---|------------|---------|---------------|
| 1 | Dimension Mapping | Synchronize hierarchies across applications | Hierarchy changes in source dimension |
| 2 | Property Mapping | Synchronize property values across applications | Property value changes |
| 3 | Pre Hierarchy Actions | Execute logic **before** hierarchy action | Before member operations |
| 4 | Post Hierarchy Actions | Execute logic **after** hierarchy action | After member operations |
| 5 | Property Derivations | Auto-populate property values | Member creation/modification |
| 6 | Property Validations | Validate property values | Property value changes |
| 7 | On Submit Workflow | Validate before workflow submission | Request submission |
| 8 | Pre Request Line Approval | Validate before line approval | Before approval action |
| 9 | Workflow Custom Task | Perform custom workflow tasks | Workflow stage execution |
| 10 | Deployment Tasks | Pre/post deployment operations | Deployment execution |
| 11 | ERP Interface Tasks | ERP import/export automation | ERP data processing |
| 12 | Pre Export Generation | Execute before export | Before export file creation |
| 13 | Post Export Generation | Execute after export | After export file creation |

## Script Type Details

### 1. Dimension Mapping

**Purpose:** Synchronize hierarchies between source and target dimensions across applications.

**Configuration Location:** Configuration → Dimension → Mapping

![Dimension Mapping Configuration](../assets/images/dimension-mapping-config.png)
*Figure: Dimension Mapping configuration screen*

**Use Cases:**
- Cross-application member synchronization
- Naming convention transformations
- Conditional hierarchy replication

**Key Features:**
- Access to source and target dimension information
- Support for all hierarchy actions (create, rename, move, delete)
- Ability to transform member names and properties

### 2. Property Mapping

**Purpose:** Map and transform property values between dimensions.

**Configuration Location:** Configuration → Property → Mapping

![Property Mapping Configuration](../assets/images/property-mapping-config.png)
*Figure: Property Mapping configuration screen*

**Use Cases:**
- Synchronize attributes across applications
- Transform property values (e.g., full names to codes)
- Maintain consistency across systems

### 3. Pre Hierarchy Actions

**Purpose:** Execute validation or preparation logic before hierarchy changes.

**Configuration Location:** Configuration → Dimension → Hierarchy Actions

![Pre Hierarchy Actions Configuration](../assets/images/pre-hierarchy-actions-config.png)
*Figure: Pre Hierarchy Actions configuration*

**Use Cases:**
- Prevent invalid hierarchy structures
- Enforce naming conventions before creation
- Validate business rules before changes

**Example Actions:**
- Create Member (CMC, CMS)
- Delete Member (DM)
- Move Member (ZC)
- Insert Shared Member (ISMC, ISMS)

### 4. Post Hierarchy Actions

**Purpose:** Execute automation logic after successful hierarchy changes.

**Configuration Location:** Configuration → Dimension → Hierarchy Actions

**Use Cases:**
- Create related members automatically
- Update dependent systems
- Generate audit entries
- Send notifications

### 5. Property Derivations

**Purpose:** Automatically calculate or populate property values.

**Configuration Location:** Configuration → Property → Derivations

![Property Derivations Configuration](../assets/images/property-derivations-config.png)
*Figure: Property Derivations configuration*

**Use Cases:**
- Set default values for new members
- Calculate derived attributes
- Auto-generate codes or descriptions

### 6. Property Validations

**Purpose:** Enforce business rules and data quality standards for property values.

**Configuration Location:** Configuration → Property → Validations

![Property Validations Configuration](../assets/images/property-validations-config.png)
*Figure: Property Validations configuration*

**Use Cases:**
- Validate formats (emails, phone numbers, codes)
- Enforce required fields
- Check value ranges and lists
- Cross-validate related properties

### 7. On Submit Workflow

**Purpose:** Perform validations before a request enters workflow.

**Configuration Location:** Workflow → Builder

![On Submit Workflow Configuration](../assets/images/on-submit-workflow-config.png)
*Figure: Workflow Builder showing On Submit Logic Script configuration*

**Use Cases:**
- Validate complete request before submission
- Check for required approvals
- Enforce business logic across all request lines
- Prevent invalid requests from entering workflow

### 8. Pre Request Line Approval

**Purpose:** Execute validations before users approve request lines.

**Configuration Location:** Workflow → Tasks

**Use Cases:**
- Additional validation at approval time
- Check for required attachments
- Verify supporting documentation
- Enforce approval prerequisites

### 9. Workflow Custom Task

**Purpose:** Implement complex business logic within workflow stages.

**Configuration Location:** Workflow → Tasks

![Workflow Custom Task Configuration](../assets/images/workflow-custom-task-config.png)
*Figure: Workflow Tasks showing Custom Function configuration*

**Use Cases:**
- Conditional routing logic
- Dynamic approval assignments
- Automated decision points
- Integration with external systems

**Special Features:**
- Can recall/rewind workflow stages
- Access to workflow context
- Ability to modify task parameters

### 10. Deployment Tasks

**Purpose:** Execute logic before or after deployment operations.

**Configuration Location:** Deployment Configuration

![Deployment Tasks Configuration](../assets/images/deployment-tasks-config.png)
*Figure: Deployment Configuration with Pre/Post Scripts*

**Script Subtypes:**
- **Pre-Deployment:** Validation and preparation
- **Post-Deployment:** Cleanup and notification

**Use Cases:**
- Validate deployment readiness
- Backup before deployment
- Send deployment notifications
- Update external systems

### 11. ERP Interface Tasks

**Purpose:** Process and transform ERP data during import/export.

**Configuration Location:** ERP Import → Builder

![ERP Interface Tasks Configuration](../assets/images/erp-interface-config.png)
*Figure: ERP Import Builder with Pre/Post Execution Scripts*

**Script Subtypes:**
- **Pre-Import:** Data preparation and validation
- **Post-Import:** Processing and cleanup

**Use Cases:**
- Transform ERP data formats
- Validate data quality
- Generate derived records
- Handle data exceptions

### 12. Pre Export Generation Tasks

**Purpose:** Prepare or modify data before export file generation.

**Configuration Location:** Administration → Export

**Use Cases:**
- Filter export data
- Add calculated fields
- Format transformations
- Data enrichment

### 13. Post Export Generation Tasks

**Purpose:** Process export files after generation.

**Configuration Location:** Administration → Export

![Export Tasks Configuration](../assets/images/export-tasks-config.png)
*Figure: Export configuration with Pre/Post Logic Scripts*

**Use Cases:**
- Send files to external systems
- Archive export files
- Trigger downstream processes
- Generate notifications

## Script Type Selection Guide

### Decision Tree

```
Need to synchronize between applications?
├─ Yes → Hierarchies? → Dimension Mapping
│        Properties? → Property Mapping
│
├─ Need to validate data?
│  ├─ Property values? → Property Validations
│  └─ Before workflow? → On Submit Workflow
│
├─ Need to automate processes?
│  ├─ After hierarchy change? → Post Hierarchy Actions
│  ├─ Property calculation? → Property Derivations
│  └─ Within workflow? → Workflow Custom Task
│
└─ Need integration logic?
   ├─ ERP systems? → ERP Interface Tasks
   ├─ Deployments? → Deployment Tasks
   └─ Exports? → Export Generation Tasks
```

## Script Association Requirements

Each script type requires specific configuration:

| Script Type | Configuration Menu | Association Field |
|------------|-------------------|-------------------|
| Dimension Mapping | Configuration → Dimension → Mapping | Mapping Option |
| Property Mapping | Configuration → Property → Mapping | Mapping Option |
| Pre Hierarchy Actions | Configuration → Dimension → Hierarchy Actions | Pre Action Script Name |
| Post Hierarchy Actions | Configuration → Dimension → Hierarchy Actions | Post Action Script Name |
| Property Derivations | Configuration → Property → Derivations | Script Name |
| Property Validations | Configuration → Property → Validations | Script Name |
| On Submit Workflow | Workflow → Builder | On Submit Logic Script |
| Pre Request Line Approval | Workflow → Tasks | Validation Script |
| Workflow Custom Task | Workflow → Tasks | Custom Function |
| Deployment Tasks | Deployment Configuration | Pre/Post Deployment Script |
| ERP Interface Tasks | ERP Import → Builder | Pre/Post Execution Script |
| Pre Export Generation | Administration → Export | Pre Export Logic Script |
| Post Export Generation | Administration → Export | Post Export Logic Script |

## Multiple Script Associations

Some configurations support multiple scripts:

### Hierarchy Actions
A single hierarchy action can have both:
- Pre-action script (validation/preparation)
- Post-action script (automation/notification)

### Workflow Stages
Multiple custom tasks can exist in a workflow stage:
- Each task executes sequentially
- Failure in one task can stop progression

### Property Validations
Multiple validation scripts per property:
- All validations must pass
- Scripts execute in configuration order

## Script Execution Order

When multiple scripts are configured:

1. **Pre-Action Scripts** (if applicable)
2. **Core Operation** (hierarchy change, property update, etc.)
3. **Mapping Scripts** (if configured)
4. **Post-Action Scripts** (if applicable)
5. **Validation Scripts** (continuous during data entry)

## Performance Considerations

### High-Frequency Scripts
Scripts that execute frequently need optimization:
- Property Validations (every keystroke)
- Property Derivations (every field change)
- Dimension Mapping (every hierarchy change)

### Low-Frequency Scripts
Can accommodate more complex logic:
- Deployment Tasks (scheduled/manual)
- Export Tasks (periodic)
- Workflow Custom Tasks (stage transitions)

## Testing by Script Type

### Unit Testing Requirements

| Script Type | Test Scenarios |
|------------|---------------|
| Validations | Valid/invalid values, boundaries, nulls |
| Mappings | All action codes, error conditions |
| Derivations | New vs existing members, dependencies |
| Workflow | All paths, approval scenarios |
| Deployment | Success/failure conditions |
| ERP Interface | Data formats, transformations |

## Best Practices by Type

### Validation Scripts
- Return clear, actionable error messages
- Check nulls and data types
- Consider performance for real-time validation

### Mapping Scripts
- Handle all action codes
- Verify target member existence
- Log mapping decisions

### Workflow Scripts
- Include comprehensive logging
- Handle all workflow states
- Test with various approval scenarios

### Integration Scripts
- Implement retry logic
- Log external system interactions
- Handle timeout scenarios

## Next Steps

- [Understand script structure](script-structure.md)
- [Create your first script](creating-scripts.md)
- [Explore specific script types](../events/)