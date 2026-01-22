# **Workflow API Functions**

**Package**: `EW_WF_API`  
**Usage**: `EW_WF_API.<function_name>`

This package contains some useful functions for Workflow Information as well as automation like conditional approvals, skip tasks based on certain conditions etc.

## Request’s Current Workflow Stage


This procedure will provide information about the current stage of the workflow for a given request ID.

```sql
  PROCEDURE get_req_curr_wf_stage_info
                                 (p_request_id   IN NUMBER
                                 ,x_wf_cycle_id OUT NUMBER
                                 ,x_wf_stage_id OUT NUMBER
                                 ,x_stage_name  OUT VARCHAR2
                                 ,x_stage_num   OUT NUMBER
                                 ,x_action_code OUT VARCHAR2
                                 ,x_action      OUT VARCHAR2
                                 ,x_status      OUT VARCHAR2
                                 );
```


## Request’s Current Workflow Stage Action Code

This procedure will provide information about the current stage action code of the workflow for a given request id.

```sql
  FUNCTION get_req_curr_wf_action_code(p_request_id   IN NUMBER)
  RETURN VARCHAR2;

```

## Request’s Current Workflow Stage Action Name

This procedure will provide information about the current stage action name of the workflow for a given request id.

```sql
  FUNCTION get_req_curr_wf_action(p_request_id   IN NUMBER)
  RETURN VARCHAR2;
```


## Request’s Current Workflow Stage Name


```sql

  -- This procedure will provide information about the current stage name of the workflow
  -- for a given request ID.

  FUNCTION get_req_curr_wf_stage_name(p_request_id   IN NUMBER)
  RETURN VARCHAR2;


  -- This procedure will provide information about the current stage ID of the workflow 
  -- for a given request ID.

  FUNCTION get_req_curr_wf_stage_id(p_request_id   IN NUMBER)
  RETURN NUMBER;


  -- This procedure will provide information about the current stage number of the workflow 
  -- for a given request ID.

  FUNCTION get_req_curr_wf_stage_num(p_request_id   IN NUMBER)
  RETURN NUMBER;
  
  
  --
```


## Next Steps

- [String APIs](string_api.md)
- [Lookup APIs](lookup_functions.md)
- [Security APIs](security_api.md)