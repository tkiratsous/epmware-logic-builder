# **Security API Functions**

The Security API provides functions for managing user access, security groups, permissions.

**Package**: `ew_sec_api`  
**Usage**: `ew_sec_api.<function_name>`


The following table provides common use functions for various Security Module related actions:

 - get_user_groups 
 - is_user_in_group 
 - chk_user_active
 - get_dep_access_type
 - get_wf_access_type
 - chk_wf_access
 - chk_dep_access
 - chk_app_dim_access
 - chk_sec_class_access
 - chk_user_role 
 - chk_group_sec_class_access
 - get_user_id
 - get_user_name



| Purpose | Function Name | Input Parameters | Output Parameters |
| --- | --- | --- | --- |
| Get Group names separated by comma in which contains given user | get_user_groups | User_id (if not passed then current logged in user id is used) | List of group names separated by commas which consist of user id. |
| Check if the user is in the given group name or not | is_user_in_group | Group Name (Required)<br><br>User ID  (if not passed then current logged in user id is used) | Y if the user is in Group else N |
| Check if the user is Active or Disabled | chk_user_active | User Name (Required) | Y if the user is Active else N |
| Get Access Type for the Deployment module | get_dep_access_type | User ID  (if not passed then current logged in user id is used) | R or W or N<br>R -> Read access<br>W -> Write access<br>N -> No access |
| Get Access Type for the Workflow module | get_wf_access_type | User ID  (if not passed then current logged in user id is used) | R or W or N<br>R -> Read access<br>W -> Write access<br>N -> No access |
| Check if user has Read or Write access to Workflow module | chk_wf_access | User ID  (if not passed then current logged in user id is used) | Y if user has access<br>N if user has no access |
| Check if user has Read or Write access to Deployment module | chk_dep_access | User ID  (if not passed then current logged in user id is used) | Y if user has access<br>N if user has no access |
| Check whether the user has access to the App dimension or not. | chk_app_dim_access | App_id<br><br>App_dimension_id<br><br>User ID  (if not passed then current logged in user id is used)<br><br>Access Type (Default is R)<br>Valid Values : R or W | Y if user has access<br>N if user has no access |
| Check whether the user has access to the Security Class or not | chk_sec_class_access | Security Class ID <br><br>User ID  (if not passed then current logged in user id is used)<br><br>Access Type (Default is R)<br>Valid Values:  R or W | Y if user has access<br>N if user has no access |
| Check if user has given role or not | chk_user_role | Role Type Code<br>R -> Requestor<br>V -> Reviewer<br>A -> Approver<br>D -> Default<br><br>User ID  (if not passed then current logged in user id is used) | Y if the user has been assigned the role else N |
| Check whether Group has Read or Write access for given Security Class | chk_group_sec_class_access | p_sec_class_name                     p_group_name<br>p_access_type | Returns Y if the group has access, otherwise N. |
| Get User ID for a given username<br> | get_user_id<br> | User Name<br> | Function will return user id for a given user_name<br> |
| Get Username for a given user id<br> | get_user_name | User ID<br> | Function will return user name for a given user id<br> |


## User Management Security APIs


**Package: ew_sec_api**


These functions can be referred to as ew_sec_api.<Function Name>.


These functions in the Security API package will help automate various functions to manage and maintain Users/Groups and their assignments within the EPMware application.


All of these functions will return “Success” if the task is completed successfully. If not, then it will return “Error:<Error Message>”.



| Purpose | Function Name | Input Parameters |
| --- | --- | --- |
| Create new User | create_user | User Name<br>First Name<br>Last Name<br>Email Address<br>Native Flag (Y/N) (If N then Password is not required as its MSAD or LDAP user)<br>Password<br>Description |
| Enable User | enable_user | User Name |
| Disable User | disable_user | User Name |
| Create New Group | create_group | Group Name |
| Enable Group | enable_group | Group Name |
| Disable Group | disable_group | Group Name |
| Assign user to Group | assign_user_to_group | User Name<br>Group Name<br> |
| Unassign user to Group | unassign_user_to_group | User Name<br>Group Name<br> |





## Next Steps

- [Export APIs](export_api.md)
- [Agent APIs](agent_api.md)
- [Application APIs](application_api.md)