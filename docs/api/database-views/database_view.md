# :material-database-eye:{ .lg .middle } **Database Views**

EPMware provides read-only database views for accessing metadata and request information. These views are optimized for performance and respect security permissions.

## EW_APPS_V

This view holds information about applications configured in the EPMware application.


Key columns are as mentioned below:


| Column Name | Meaning |
| --- | --- |
| APP_ID | Primary key identifier of the App Table |
| NAME | Application Name |
| TARGET_APP_NAME | Target Application Name |
| ENABLED_FLAG | Y/N to indicate whether application is enabled or disabled |
| USER_NAME | Application Username |

**Example Usage:**

```sql

SELECT *
  FROM ew_apps_v
 WHERE name = '<APP_NAME>';

```


## EW_APP_DIMENSIONS_V

This table holds information about dimensions in the EPMware application.


Key columns are as mentioned below:


| Column Name | Meaning |
| --- | --- |
| APP_DIMENSION_ID | Primary key identifier of the Dimensions Table |
| APP_ID | Application ID |
| APP_NAME | Application Name |
| TARGET_APP_NAME | Target Application Name |
| ENABLED_FLAG | Y/N to indicate whether dimension is enabled or disabled |
| APP_ENABLED_FLAG | Y/N to indicate whether application is enabled or disabled |
| APP_TYPE | Internal code for Application Type |
| DIM_CLASS_NAME | Dimension Class Name |
| DIM_NAME | Dimension Name |


**Example Usage:**

```sql

-- get app_dimension_id and dim_name

SELECT app_dimension_id,
       dim_name,
       dim_class_name
  FROM ew_app_dimensions_v
 WHERE app_name = '<APP_NAME>'
   
```


## EW_REQUEST_LINE_MEMBERS_V
This view provides all request lines and its member’s data. Key columns are as mentioned below:



| Column Name | Meaning |
| --- | --- |
| REQUEST_ID | Request ID |
| LINE_NUM | Request Line # |
| ACTION_CODE | Internal Code Request Line Actions, Check [Appendix A](../../appendices/appendix_a_action-codes.md) to understand action codes |
| ACTION_NAME | Action Name such as “Create Member”, “Edit Properties”. |
| APP_DIMENSION_ID | Primary key identifier of the Dimensions Table |
| APP_ID | Primary key identifier of the App Table |
| CHILDLESS_PARENT_MEMBER_NAME | Parent Member Name if it is Childless |
| DEPLOY_DATE | Deploy Date of the request line |
| DIM_CLASS_NAME | Dimension Class Name |
| DIM_NAME | Dimension Name |
| HIERARCHY_ID | Primary identifier of the table that stores nodes. |
| MEMBER_ALIAS | Member Description |
| MEMBER_ID | Member ID. Primary identifier of the table that stores members |
| MEMBER_NAME | Member Name |
| MOVED_FROM_MEMBER_ID | Moved from the Member ID if the line action is Move Member |
| MOVED_FROM_MEMBER_NAME | Moved from the Member Name  if the line action is Move Member |
| ORIG_MEMBER_NAME | Original Member name if the line action is Rename Member |
| PARENT_MEMBER_ID | Parent Member id. Primary identifier of the table that stores members |
| PARENT_MEMBER_NAME | Parent Member Name |
| PREV_SIBLING_MEMBER_NAME | Previous Sibling Member Name |
| PREV_SIBLING_PRIMARY_FLAG | Y/N flag to indicate whether previous member is a primary member or not |
| PRIMARY_FLAG | Y/N flag to indicate whether member is a primary instance or not |
| RELATED_LINE_ID | Request line id to which this line is related to |
| REQUEST_LINE_ID | Request Line id |
| REQUEST_LINE_MEMBER_ID | Request Line Member ID |
| SORT_ORDER | Sort order of the member |
| STATUS | Status of the request line |
| TARGET_APP_NAME | Target Application Name |




## EW_MEMBERS_V
This view provides member data. Key columns are as mentioned below:



| Column Name | Meaning |
| --- | --- |
| APP_NAME | Application Name |
| DIM_NAME | Dimension Name |
| APP_DIMENSION_ID | Primary key identifier of the Dimensions Table |
| APP_ID | Primary key identifier of the App Table |
| MEMBER_ID | Primary identifier for the member |
| MEMBER_NAME | Member Name. Member name has to be unique within the dimension. |
| STATUS | Status of the Member<br>A -> Active (No pending activity)<br>W -> Work in Progress (Some pending activity) |
| ROOT_FLAG | Y/N flag to indicate whether the member is a root member of the dimension |
| CREATION_DATE | Date member was created |
| LAST_UPDATE_DATE | Last update date on the member |



## EW_HIERARCHY_MEMBERS_V


This view provides node data. Key columns are as mentioned below. Node is a combination of member id and parent member id combination. This combination is a unique combination.


| Column Name | Meaning |
| --- | --- |
| HIERARCHY_ID | Primary identifier of the view |
| APP_DIMENSION_ID | Primary key identifier of the Dimensions Table |
| MEMBER_ID | Member ID. Primary identifier of the table that stores members |
| MEMBER_NAME | Member Name |
| MEMBER_STATUS | Status of the Member<br>A -> Active (No pending activity)<br>W -> Work in Progress (Some pending activity) |
| HIERARCHY_STATUS | Status of the Member<br>A -> Active (No pending activity)<br>W -> Work in Progress (Some pending activity) |
| PARENT_MEMBER_ID | Parent Member id |
| PARENT_MEMBER_NAME | Parent Member Name |
| PARENT_ROOT_FLAG | Y/N flag to indicate whether the member is a root member of the dimension |
| SORT_ORDER | Sort order of the member within its parent member |
| PRIMARY_FLAG | Y/N flag to indicate whether a member is a primary instance of the parent member.<br><br>Y -> Primary<br>N -> Shared Instance |




## EW_HIERARCHY_DETAILS_V


This view provides node data. This has all columns that are part of EW_HIERARCHY_MEMBERS_V but in addition it has APP_NAME, DIM_NAME, DIM_CLASS_NAME columns as well.

| Column Name | Meaning |
| --- | --- |
| HIERARCHY_ID | Primary identifier of the view |
| APP_DIMENSION_ID | Primary key identifier of the Dimensions Table |
| MEMBER_ID | Member ID. Primary identifier of the table that stores members |
| MEMBER_NAME | Member Name |
| MEMBER_STATUS | Status of the Member<br>A -> Active (No pending activity)<br>W -> Work in Progress (Some pending activity) |
| HIERARCHY_STATUS | Status of the Member<br>A -> Active (No pending activity)<br>W -> Work in Progress (Some pending activity) |
| PARENT_MEMBER_ID | Parent Member id |
| PARENT_MEMBER_NAME | Parent Member Name |
| PARENT_ROOT_FLAG | Y/N flag to indicate whether the member is a root member of the dimension |
| SORT_ORDER | Sort order of the member within its parent member |
| PRIMARY_FLAG | Y/N flag to indicate whether a member is a primary instance of the parent member.<br><br>Y -> Primary<br>N -> Shared Instance |
| APP_NAME | Application Name |
| DIM_NAME | Dimension Name |
| DIM_CLASS_NAME | Dimension Class (Type) Name |



## EW_MEMBER_PROPS_ALL_V


This view provides all current properties of all members and nodes.



| Column Name | Description |
| --- | --- |
| APP_ID | Application ID |
| APP_NAME | Application Name |
| APP_DIMENSION_ID | Dimension ID |
| DIM_NAME | Dimension Name |
| DIM_CLASS_NAME | Dimension Class (Type) Name |
| MEMBER_NAME | Member Name |
| MEMBER_ID | Member ID |
| MEMBER_STATUS | Member Status (A or W)<br>A -> No active request<br>W -> at least one open request |
| PARENT_MEMBER_NAME | Parent Member Name <br>NULL for member level properties <br>Parent member name for those properties where Hierarchy Type flag is enabled. (For example, Data Storage properties in Hyperion applications) |
| ARRAY_MEMBER_NAME | Alias Member Name (for Alias type properties) |
| ARRAY_MEMBER_ID | Alias Member ID (for Alias type properties) |
| PROP_VALUE | Property Value (not for Large Text Type) |
| HIERARCHY_ID | ID of a node (Parent Member/Member ID combination in a dimension) |
| PRIMARY_FLAG | Y or N (N for Shared instances) |
| CLOB_PROP_VALUE | Property value (For Large Text type only). For example, Member Formulas. Even if formulas are having small text. |
| REF_ID | ID to main tables where properties are saved, Internal use only. |
| CREATION_DATE |  |
| LAST_UPDATE_DATE |  |
| CREATED_BY |  |
| LAST_UPDATED_BY |  |
| VARY_BY_MEMBER_NAMES | For applications where Properties are Large Text type but vary by dimensions (Example, Formulas in OneStream Apps) |
| MEMBER_LEVEL_PROP | Y or N<br>Y => properties are stored at member level (For example, Alias, Currency or Member Formulas)<br>N => properties stored at node level (For example, Data Storage which differs between primary and shared instances of a member) |
| NODE_LEVEL_PROP | Y or N<br>N => properties are stored at member level (For example, Alias, Currency or Member Formulas)<br>Y => properties stored at node level (For example, Data Storage which differs between primary and shared instances of a member) |
| PROP_NAME | Property Name |
| PROP_LABEL | Property Label |
| DEPLOY_PROP_NAME | Property Name used during Deployment only |
| DISPLAY_SEQ_NUM | Display Seq # of the property |
| DEPLOY_DEFAULT_FLAG | Y or N flag to indicate whether to deploy Default Value or not |
| DEFAULT_VALUE | Default Value configured for this property whenever new member or a node is created (for hierarchy type properties) |
| PROP_ID | Property ID |
| BACKUP_FLAG | Y or N<br>Used to save values for custom properties |
| DEPLOY_FLAG | Y or N <br>Deploy or not dpeloy |
| HIERARCHY_TYPE | Y or N<br>Y means property values are saved at a node level<br>N means property values are stored at the member level |
| ARRAY_TYPE | Y or N : Alias Type property |
| CLOB_FLAG | Y or N : Large Text type property |
| DISPLAY_TYPE | Display Type code of this property |
| DISPLAY_FLAG | Y or N : Property displayed or hidden |
| VARY_BY_DIM | Vary by Dimensions configurations |
| VARY_BY_DIM_DEFAULT_MEMBER | Vary by Dimensions Default Members configurations |
| ASSOCIATION_DIM_CLASS | If property is associated to another dimension class |
| MASK_FLAG | Y or N : Property values are masked or not masked |



## EW_MEMBER_PROPS_ARCHIVE_ALL_V


This view provides all archived properties of all members and nodes for each request and each line of the request.

It has all columns that EW_MEMBER_PROPS_ALL_V has but few extra columns as described below.



| Column Name | Description |
| --- | --- |
| REQUEST_ID | Request ID |
| REQUEST_LINE_ID | Request Line ID |
| ACTION_CODE | Hierarchy Action Code |
| ARCHIVE_TYPE | H or R<br>H : When request is created<br>R : when Request is completed |



## EW_LOOKUP_CODES_V

This view provides lookup codes. Procedure APIs are also available. In case all records and other attributes such as TAG or Description are needed, then a view can be useful too.


For example,


```sql

    SELECT lookup_code,meaning, description,seq_num,tag
    FROM ew_lookup_codes_v
    WHERE lookup_name = ‘<Your lookup Name>’
    ORDER BY lookup_code

```

## Next Steps

- [Record Types](record_type.md)
- [Package APIs](../packages/index.md)