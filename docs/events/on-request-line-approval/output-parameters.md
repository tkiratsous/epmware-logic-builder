# 📤**On Request Line Approval Task Script Output Parameters**

## Output Parameters

| Output Parameter | Description |
| --- | --- |
| g_status | Status Values are either ‘S’ for Success or ‘E’ for Error.<br><br>Alternatively use the following method to set values in your code.<br><br>ew_lb_api.g_status  := ew_lb_api.g_success<br>OR<br>ew_lb_api.g_status  := ew_lb_api.g_error |
| g_message | Error Message if the status is Error. |



## Next Steps

- [On Request Line Approval Task Script - Examples](examples.md) 
- [On Request Line Approval Task Script - Input Parameters](input-parameters.md)
- [API Reference](../../api/packages/index.md)
---

!!! warning "Important"
    Always set `g_status` and provide a `g_message` when returning an error. This ensures users understand what went wrong and can take corrective action.