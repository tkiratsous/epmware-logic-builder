# 🔽 **Pre Hierarchy Action Input Parameters**

## Input Parameters

The following table lists Input Parameters that are available for Pre Hierarchy Action Logic Scripts.



| Input Parameter | Description |
| --- | --- |
| g_user_id | Current logged User ID |
| g_lb_script_name | Logic Script Name being executed |
| g_request_id | Request ID |
| g_member_name | Member Name |
| g_parent_member_name | Parent Member’s Name |
| g_app_name | Application Name |
| g_dim_name | Dimension Name |
| g_dim_class_name | Dimension Class Name |
| g_wf_code | Workflow Code |
| g_wf_stage_name | Workflow Stage Name (if request is submitted in the workflow) |
| g_req_rec | Request Header Record |
| g_dim_rec | Dimension Record |

 ***Internal IDs*** 
 
| Input Parameter | Description |
| --- | --- |
| g_hierarchy_id | Unique node id. Each combination of Parent Member/Member is given a unique internal numerical value called hierarchy_id |
| g_member_id | Unique member id. Each member in EPMware is given a unique internal numerical value called member_id |
| g_parent_member_id | Parent member’s Member ID |
| g_app_dimension_id | Application dimension ID |
| g_app_id | Application ID |
| g_wf_stage_task_id | Workflow Stage Task ID |




## Next Steps

- [Pre Hierarchy Action Output Parameters](output-parameters.md)
- [Pre Hierarchy Action Examples](examples.md)
- [API Reference](../../api/index.md)
