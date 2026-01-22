# 📤**ERP Interface Scripts Output Parameters**

## Output Parameters

| Output Parameter | Description |
| --- | --- |
| g_status | Status Values are either ‘S’ for Success or ‘E’ for Error.<br><br>Alternatively use the following method to set values in your code.<br><br>ew_lb_api.g_status  := ew_lb_api.g_success<br>OR<br>ew_lb_api.g_status  := ew_lb_api.g_error |
| g_message | Error Message if the status is Error. |


Refer to [Appendix C](../../appendices/appendix_c_erp-import-table.md) for table structure EW_IF_LINES

ERP Import interface table expects following values for the Action Code column in the table. This is useful when the user is populating records in the table either directly (for On Premise customers) OR via Pre ERP-Import logic script.


 - Create
 - Create or Edit
 - Delete
 - Edit
 - Insert Shared
 - Remove Shared
 - Move
 - Rename
 - Reorder


## Next Steps

- [ERP Interface Scrtips Examples](examples.md)
- [ERP Interface Scripts Input Parameters](input-parameters.md)
- [ERP Import APIs Reference](../../api/packages/erp_import_api.md)

---

!!! warning "Important"
    Always set `g_status` and provide a `g_message` when returning an error. This ensures users understand what went wrong and can take corrective action.