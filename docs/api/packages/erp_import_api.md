# **ERP Import API Functions**


## Package: EW_IF_API

These functions can be referred to as ew_if_api."Function Name"


## Load Data Using Application Import

Using this API, Application Import gets executed and file is retrieved is used as a source to run ERP Import. For example, if user wants to load data using DataBricks Agent. In this case, DataBricks SQL can be registered as an application and called using this API to retrieve data in the ERP Import logic script.

```sql

  -- Load Interface data using App Import process
  PROCEDURE load_data_using_app_import
                (p_user_id             IN NUMBER
                ,p_name                IN VARCHAR2 -- ERP Import Name
                ,p_app_name            IN VARCHAR2
                ,x_status             OUT VARCHAR2 -- S or E
                ,x_message            OUT VARCHAR2
                );

```


## Process Delta Only

Using this API, Interface lines which have Edit Action can be checked and those lines where there is no change in any of the property values can be deleted OR marked as Ignored.
```sql

  -- Detect interface records with Edit action (OR Create or Edit action
  -- with member already exists) where no property is changed
  -- and remove them if not changed.
  
  PROCEDURE process_delta_only(p_name         IN VARCHAR2 -- ERP Import Name
                              ,p_option       IN VARCHAR2 -- Delete or Ignore
                              ,p_chk_no_props IN VARCHAR2 DEFAULT 'N'
                              ,x_status      OUT VARCHAR2 -- S or E
                              ,x_message     OUT VARCHAR2
                              );


```



## Next Steps


- [Hierarchy APIs](hierarchy_api.md)
- [Hierarchy Stats APIs](hierarchy_stats_api.md)
- [Workflow APIs](workflow_api.md)
