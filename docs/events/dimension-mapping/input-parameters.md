# 🔽**Dimension Mapping Input Parameters**

This page provides a comprehensive reference for all input parameters available in Dimension Mapping Logic Scripts.<br/>
Understanding these parameters is essential for implementing custom mapping logic.

## Input Parameters

The following table lists Input Parameters that are available for all Hierarchy Actions.


| Input Parameter | Description |
| --- | --- |
| g_user_id | Current logged User ID |
| g_lb_script_name | Logic Script Name being executed |
| g_request_id | Request ID |
| g_member_name | Member Name |
| g_renamed_from_member_name | Original Member name before it was Renamed. Use this variable for the Rename Member action to get the original member’s name. |
| g_parent_member_name | Parent Member’s Name |
| g_prev_sibling_member_name | Previous Sibling Member Name |
| g_moved_from_member_name | When a member is moved from a source parent member to the target parent member then this variable provides the member’s name of the source parent member. |
| g_moved_to_member_name | When a member is moved from a source parent member to the target parent member then this variable provides the member’s name of the target parent member. |
| g_array_member_name | Member Name of the associated Alias or Languages (Such as Default, English etc.) |
| g_app_name | Application Name |
| g_dim_name | Dimension Name |
| g_dim_class_name | Dimension Class Name |
| g_mapped_app_name | Mapped Application Name |
| g_mapped_dim_name | Mapped Dimension Name |
| g_wf_code | Workflow Code |
| g_wf_stage_name | Workflow Stage Name (if request is submitted in the workflow) |
| g_action_code | Request Line Action Code such as CMC, CMS (Create member as child / sibling), P (Edit Properties), RM (Rename Member)  and so on. See full list of Action Codes in [Appendix A](../../appendices/appendix_a_action-codes.md) |
| g_action_name | Request Line Action Name such as Create member, Edit Properties, Rename Member and so on. See full list of Action Codes in [Appendix A](../../appendices/appendix_a_action-codes.md) |
| g_req_rec | Request Header Record |
| g_dim_rec | Dimension Record |

 ***Internal IDs*** 
 
 
| Input Parameter | Description |
| --- | --- |
| g_request_line_id | Request Line ID |
| g_hierarchy_id | Unique node id. Each combination of Parent Member/Member is given a unique internal numerical value called hierarchy_id |
| g_member_id | Unique member id. Each member in EPMware is given a unique internal numerical value called member_id |
| g_parent_member_id | Parent member’s Member ID |
| g_moved_from_hierarchy_id | When a member is moved from a source parent member to the target parent member then this ID provides the hierarchy id of the source parent member. |
| g_moved_from_member_id | When a member is moved from a source parent member to the target parent member then this ID provides the member id of the source parent member. |
| g_moved_to_hierarchy_id | When a member is moved from a source parent member to the target parent member then this ID provides the hierarchy id of the target parent member. |
| g_moved_to_member_id | When a member is moved from a source parent member to the target parent member, then this ID provides the member id of the target parent member. |
| g_app_dimension_id | Application dimension ID |
| g_app_id | Application ID |
| g_prop_id | Property Configuration ID |
| g_array_member_id | Member ID of the Associated alias members (referred internally in EPMware as Array Members) |
| g_mapped_app_dimension_id | Used in Dimension and Property Mappings only. Dimension ID of the mapped application |
| g_mapped_hierarchy_id | Used in Property Mapping. Hierarchy ID of the node in the mapped dimension |
| g_wf_stage_task_id | Workflow Stage Task ID |




## Next Steps

- [Dimension Mapping Output Parameters](output-parameters.md)
- [Dimension Mapping Examples](examples.md)
- [API Reference](../../api/index.md)
- [Dimension Mapping APIs](../../api/packages/dimension_mapping_api.md)

---

!!! tip "Debug Tip"
    Always log input parameters at the start of your script for easier troubleshooting. Use the Debug Messages report to review parameter values during execution.