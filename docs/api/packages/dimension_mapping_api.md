# **Dimension Mapping API Functions**

This package contains some useful functions for performing activities in the Dimension Mapping Logic Scripts such as whether current application being processed is a Leading Application or not.

**Package**: `EW_DIM_MAPPING_API`  
**Usage**: `ew_dim_mapping_api.<function_name>`

## Is Leading Application

This API can help determine in custom dimension mapping logic scripts whether the current application is a leading application or not.

For example, if there are multiple dimension mappings configuration between applications and if the script need to determine whether the current application is a leading application or not to continue processing or not then this API can help determine that.

```sql

  -- Return Y or N if the given app is a leading app or not
  -- on a given Dimension Mapping
  FUNCTION is_leading_app (p_dim_mapping_label IN VARCHAR2
                          ,p_app_id            IN NUMBER
                          )
  RETURN VARCHAR2;

```

## Copy Branch Members

This API can copy entire branch from source application to the mapped application for a given specific member name. Using the member name all of its ancestors are retrieved from the source dimension and then entire branch gets created in the mapped dimension. 

Optionally it can also copy member properties. If dimension mapping label is provided and its used to copy properties also which are defined for that dimension mapping under Property Mapping Configuration between source and mapped application. If it successful execution then x_status will have value S else E (error) and x_message will hold error message.

```sql

  PROCEDURE copy_branch_members
                  (p_user_id                  IN NUMBER
                  ,p_request_id               IN NUMBER
                  ,p_related_line_id          IN NUMBER DEFAULT NULL
                  ,p_source_app_dimension_id  IN NUMBER
                  ,p_source_member_name       IN VARCHAR2
                  ,p_mapped_app_dimension_id  IN NUMBER
                  ,p_dim_mapping_label        IN VARCHAR2
                  ,p_copy_properties          IN VARCHAR2 DEFAULT 'Y'
                  ,x_status                  OUT VARCHAR2
                  ,x_message                 OUT VARCHAR2
                  )


```


## Copy Branch Members

This API can copy entire branch from source application to the mapped application for a given specific member name. Using the member name all of its ancestors are retrieved from the source dimension and then entire branch gets created in the mapped dimension. 

Optionally it can also copy member properties. If dimension mapping label is provided and its used to copy properties also which are defined for that dimension mapping under Property Mapping Configuration between source and mapped application. If it successful execution then x_status will have value S else E (error) and x_message will hold error message.

```sql

  PROCEDURE copy_branch_members
                  (p_user_id                  IN NUMBER
                  ,p_request_id               IN NUMBER
                  ,p_related_line_id          IN NUMBER DEFAULT NULL
                  ,p_source_app_dimension_id  IN NUMBER
                  ,p_source_member_name       IN VARCHAR2
                  ,p_mapped_app_dimension_id  IN NUMBER
                  ,p_dim_mapping_label        IN VARCHAR2
                  ,p_copy_properties          IN VARCHAR2 DEFAULT 'Y'
                  ,x_status                  OUT VARCHAR2
                  ,x_message                 OUT VARCHAR2
                  )


```

*Example :*<br/>
If requirement is that whenever in the source application if member name with pattern `A*****`.R (Prefix A followed by some numeric value but ending with DOT character and R) then only that new member along with all of its ancestors need to be created in the mapped dimension.<br/>
To achieve this automation, Logic Script of type Post Hierarchy Action can be called to not only create this member but if its ancestors are missing in the mapped dimension then they will be created. Certain properties, if they need to be mapped can also be done by creating dimension mapping configuration. If dimension configuration is not needed, then a dummy mapping can be created just to create property mappings for it.

```sql

/ * Example for reference purposes only – 
    Source App : HFM, Dimension : Account
    Mapped App : ASO, Dimension : Measures
*/
ew_dim_mapping_api.copy_branch_members
       (p_user_id                  => ew_lb_api.g_user_id
       ,p_request_id               => ew_lb_api.g_request_id
       ,p_source_app_dimension_id  => ew_lb_api.g_app_dimension_id
       ,p_source_member_name       => 'A123456.R'
       ,p_mapped_app_dimension_id  => ew_hierarchy.get_app_dimension_id
                                             (p_app_name => 'ASO'
                                             ,p_dim_name => 'Measures'
                                             )
       ,p_dim_mapping_label        => 'HFM_TO_ASO_ACCT_DIM_MAPPINNG'
       ,p_copy_properties          => 'Y'
       ,x_status                   => l_status
       ,x_message                  => l_message
      );

```


## Execute Property Mappings

This API can help execute Property Mappings on demand basis. Typical use of this API is on cases where members are mapped not based on dimension mappings but through custom logic and after that mapping certain properties need to be mapped between two members, and this API can help perform that task. For example, using On submit Workflow members are mapped across applications and once they are mapped (Created), OR identified that Properties such as Alias is edited on the Source Application and now need to be propagated to target dimensions then this API can be called from the On Submit Workflow to map Alias across applications for the mapped members.

```sql
  PROCEDURE exec_prop_mappings
                 (p_user_id                  IN NUMBER
                 ,p_request_id               IN NUMBER
                 ,p_source_line_num          IN NUMBER
                 ,p_source_prop_name         IN VARCHAR2
                 ,p_source_array_member_name IN VARCHAR2 DEFAULT NULL
                 --
                 ,p_target_line_num          IN NUMBER   DEFAULT NULL
                 ,p_target_prop_name         IN VARCHAR2 DEFAULT NULL
                 ,p_target_array_member_name IN VARCHAR2 DEFAULT NULL
                 --
                 ,p_prefix_prop_value        IN VARCHAR2 DEFAULT NULL
                 ,p_source_ref_code          IN VARCHAR2 DEFAULT NULL
                 ,x_status                  OUT VARCHAR2
                 ,x_message                 OUT VARCHAR2
                 )
                ;
```


## Next Steps
- [Application APIs](application_api.md)
- [Workflow APIs](workflow_api.md)
- [String APIs](string_api.md)