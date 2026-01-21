# **Appendix C - ERP Import Table (EW_IF_LINES)**

The `EW_IF_LINES` table This table can be referred to by Pre / Post ERP Import Logic scripts for adding custom logic based on the data uploaded by either file (using REST API) or direct insert into this table (for On Premise customers).

Columns which are marked Yes for “System Managed” can be ignored by the developer as ERP Import engine will manage values in those columns.


## Table Structure

| Column(s) | Required | System Managed | Description | Example |
| --- | --- | --- | --- | --- |
| NAME | Yes |  | ERP Import Name | EW_LOAD_EMPLOYEES |
| STATUS | Yes |  | Status of Records<br>N for New Records | N |
| IF_LINE_ID |  | Yes |  |  |
| IF_CONFIG_ID |  | Yes |  |  |
| IF_EXEC_ID |  | Yes |  |  |
| MESSAGE |  | Yes |  |  |
| REFERENCE_NUMBER |  |  | Future use |  |
| REQUESTOR_USER_NAME |  | Yes | ERP Import Header level Mapping can provide value for this column |  |
| REQUESTED_BY |  | Yes | System will assign user id of the requestor |  |
| REQUEST_ID |  |  | If one request is being created then this column hold request id |  |
| REQUEST_DATE |  |  | Request Date (in case new request is being created) |  |
| DUE_DATE |  |  | Due Date (in case new request is being created) |  |
| DESCRIPTION |  |  | Description (in case new request is being created) |  |
| UDF1 to UDF3 |  |  | User Defined Fields (1 to 3) (in case new request is being created) |  |
| LINE_NUM |  |  | Either system assigned OR user assigned request line numbers |  |
| ACTION_CODE | Yes |  | Either mapping assigns value for the Hierarchy Action Code in this column or Logic builder API assigns it (Mapping type Import for Action Code)<br><br>Refer to the Next Section for list of Action Codes |  |
| PARENT_MEMBER_NAME |  |  | Specify Parent member |  |
| MEMBER_NAME |  |  | Specify member name |  |
| PREV_SIBLING_MEMBER |  |  | Specify Previous Sibling Member name |  |
| MOVED_TO_PARENT_MEMBER |  |  | For “Move Member’ action this is a required column |  |
| APP_DIMENSION_ID |  | Yes | Dimension ID auto populated for each row by the system |  |
| MEMBER_ID |  | Yes | Member ID |  |
| PARENT_MEMBER_ID<br> |  | Yes | Parent Member ID |  |
| PREV_SIBLING_MEMBER_ID |  | Yes | Member ID of the Previous Sibling member |  |
| MOVED_TO_MEMBER_ID |  | Yes | Member ID of the Moved to member Name |  |
| PROPERTY1 to PROPERTY30 |  |  | 30 Properties user can populated with values |  |
| NEW_MEMBER_NAME |  |  | New Member Name for Rename Action Code |  |
| SORT_ORDER |  |  | Assign new Sort order of the node |  |
| TASK_ID |  | Yes | System will assign runtime Task ID |  |
| FILE_NAME |  |  | If ERP Import is run by users uploading file then its file name is saved for each line in this interface table |  |

