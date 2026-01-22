# 📤**Workflow Custom Task Script Output Parameters**

## Output Parameters

| Output Parameter | Description |
| --- | --- |
| g_status | Status Values are either ‘S’ for Success or ‘E’ for Error.<br><br>Alternatively use the following method to set values in your code.<br><br>ew_lb_api.g_status  := ew_lb_api.g_success<br>OR<br>ew_lb_api.g_status  := ew_lb_api.g_error |
| g_message | Error Message if the status is Error. |
| g_out_rewind_stages | Optionally you can specify # of stages you would like to rewind the request in the workflow. For example, if you specify 1 then the request will get recalled to the one stage prior to the current stage. |



## Next Steps

- [Workflow Custom Task Script - Examples](examples.md) 
- [Workflow Custom Task Script - Input Parameters](input-parameters.md)
- [API Reference](../../api/packages/index.md)
---

!!! warning "Important"
    Always set `g_status` and provide a `g_message` when returning an error. This ensures users understand what went wrong and can take corrective action.