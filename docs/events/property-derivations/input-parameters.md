# 🔽**Property Derivations Input Parameters**

## Input Parameters

The following table lists Input Parameters that are available for Property Derivation Logic Scripts.



| Input Parameter | Description |
| --- | --- |
| g_user_id | Current logged User ID |
| g_lb_script_name | Logic Script Name being executed |
| g_request_id | Request ID |
| g_member_name | Member Name |
| g_parent_member_name | Parent Member’s Name |
| g_array_member_name | Member Name of the associated Alias or Languages (Such as Default, English etc.) |
| g_app_name | Application Name |
| g_dim_name | Dimension Name |
| g_dim_class_name | Dimension Class Name |
| g_prop_name | Property Name |
| g_prop_label | Property Label |
| g_wf_code | Workflow Code |
| g_wf_stage_name | Workflow Stage Name (if request is submitted in the workflow) |
| g_req_rec | Request Header Record |
| g_dim_rec | Dimension Record |

 ***Internal IDs*** 
 
| Input Parameter | Description |
| --- | --- |
| g_request_line_id | Request Line ID |
| g_hierarchy_id | Unique node id. Each combination of Parent Member/Member is given a unique internal numerical value called hierarchy_id |
| g_member_id | Unique member id. Each member in EPMware is given a unique internal numerical value called member_id |
| g_parent_member_id | Parent member’s Member ID |
| g_app_dimension_id | Application dimension ID |
| g_app_id | Application ID |
| g_prop_id | Property Configuration ID |
| g_array_member_id | Member ID of the Associated alias members (referred internally in EPMware as Array Members) |
| g_wf_stage_task_id | Workflow Stage Task ID |
| g_member_name | This flag (Y or N value) indicates whether member is a new member being created or not. Property Derivation Logic Script can use this information at the time of new member creation to apply certain business logic if needed. |




## Next Steps

- [Property Derivations Output Parameters](output-parameters.md)
- [Property Derivations Examples](examples.md)
- [API Reference](../../api/index.md)

