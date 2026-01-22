# **In Memory Functions**


## Package : EW_LB_API

This package provides functions that provide information for in-memory values which are not yet committed to the database and scripts may need access to these values for automation or validations.

These functions can be referred to as ->  ew_lb_api."Function Name"

## Get New Member Property Value

```sql
  
  -- Return Member property value for new members for which
  -- Logic Script is being invoked
  
  FUNCTION get_new_member_prop_value (p_prop_label IN VARCHAR2)
  RETURN VARCHAR2;
  
```

## Get Member Property Value

```sql
  
  -- Return Member property value for current hierarchy for which
  -- Logic Script is being invoked
  -- Pass either Property Label OR Property Name

  FUNCTION get_member_prop_value (p_prop_label IN VARCHAR2)
  RETURN VARCHAR2;

```


## Get Parent Member Property Value

```sql
  
  -- Return Parent Member’s property value for current hierarchy 
  -- for which Logic Script is being invoked
  -- Pass either Property Label OR Property Name

  FUNCTION get_parent_prop_value (p_prop_label IN VARCHAR2)
  RETURN VARCHAR2;

```

## Get Member Property Value from Archive

```sql
  
  -- Return Member property value for current hierarchy for which
  -- Logic Script is being invoked during Property Validation
  -- Pass either Property Label OR Property Name

  FUNCTION get_member_prop_value_archive (p_prop_label IN VARCHAR2)
  RETURN VARCHAR2;

  -- This function will use current property which is being validated
  FUNCTION get_member_prop_value_archive
  RETURN VARCHAR2;

```

## Is value Numeric

```sql
  
  -- This function will check if the given string is numeric or not.
  -- If numeric then return TRUE or else FALSE
  
  FUNCTION is_numeric (p_string IN VARCHAR2)
  RETURN BOOLEAN;

```

## Is current member Base Member

```sql
  
  -- Check if current member is leaf or not
  
  FUNCTION is_leaf
  RETURN BOOLEAN;

```

## Get Descendants Count

```sql
  
  -- This function provides count of direct descendants for a given member id
  
  FUNCTION get_descendants_count (p_member_id IN NUMBER)
  RETURN NUMBER;
  
  
  -- This function provides count of direct descendants for a given member name and application dimension id
  
  FUNCTION get_descendants_count (p_app_dimension_id IN NUMBER
                                 ,p_member_name      IN VARCHAR2
                                 )
  RETURN NUMBER;

```

## Get Request Attribute

```sql
  
  FUNCTION get_req_attrib  (p_request_id IN NUMBER
                           ,p_what       IN VARCHAR2
                           )
  RETURN VARCHAR2 ;


```


| p_what | Value |
| --- | --- |
| UDF1 (or UDF2 or UDF3) | Returns value from UDF(1 to3)  field of Request Header |
| REQUESTED_BY | Returns User Name of the Requestor on the request |
| PRIORITY_CODE | Provides code the Priority from the Request Header |
| WORKFLOW_NAME | Provides name of the workflow from the request header |
| DESCRIPTION | Provides description value from the request header |
| REQUEST_DATE | Provides request date in the format DD-MON-RRRR |
| DUE_DATE | Provides request due date in the format DD-MON-RRRR |

## Next Steps

- [Email APIs](email_api.md)
- [Request APIs](request_api.md)
- [String APIs](string_api.md)