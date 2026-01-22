# Application API Functions

This package contains some useful functions for getting Application-Level information.

**Package**: `ew_app`  
**Usage**: `ew_app.<function_name>`


## Get Application Property Value

```sql 

  -- Get Application-Level Property Value for a given Application and its Property Name 

  FUNCTION get_app_prop (p_app_id    IN NUMBER                                  
                        ,p_prop_name IN VARCHAR2)
  RETURN VARCHAR2;

```

## Get Target Application Name

```sql

  -- Get Target Application Name for a given application ID */
  
  FUNCTION get_target_app_name (p_app_id IN NUMBER)
  RETURN VARCHAR2;

```

## Get Dimension Property Value

```sql 

  -- Get Dimension Level Property Value
  
  FUNCTION get_app_dim_prop_value (p_app_id           IN NUMBER
                                  ,p_dim_name         IN VARCHAR2
                                  ,p_prop_name        IN VARCHAR2
                                   )
  RETURN VARCHAR2;
  
  FUNCTION get_app_dim_prop_value (p_app_dimension_id IN NUMBER
                                  ,p_prop_name        IN VARCHAR2
                                  )
  RETURN VARCHAR2;

```


## Next Steps

- [Workflow APIs](workflow_api.md)
- [String APIs](string_api.md)
- [Security APIs](security_api.md)
- [Agent APIs](agent_api.md)