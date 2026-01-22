# Lookup API Functions

The Lookup API provides functions for managing and retrieving lookup values, codes, meaninig.

**Package**: `ew_global`  
**Usage**: `ew_global.<function_name>`

## Get All Lookup Codes

```sql

  /* Fetch all lookup codes of a given lookup type and return then in
     comma (or any other char) separated list.
  */
  
  FUNCTION get_lookup_codes_list
                  (p_name          IN VARCHAR2
                  ,p_enabled_only  IN VARCHAR2 DEFAULT 'Y'
                  ,p_sep           IN VARCHAR2 DEFAULT ',' 
                  ,p_encl          IN VARCHAR2 DEFAULT NULL
                  )
  RETURN VARCHAR2;

```

## Get All Lookup Meanings

```sql
  /* Fetch all lookup meanings of a given lookup type and return them 
     in a comma (or any other char) separated list.
  */
  
  FUNCTION get_lookup_meanings_list
                  (p_name          IN VARCHAR2
                  ,p_enabled_only  IN VARCHAR2 DEFAULT 'Y'
                  ,p_sep           IN VARCHAR2 DEFAULT ',' 
                  ,p_encl          IN VARCHAR2 DEFAULT '"'
                  )
  RETURN VARCHAR2;
```


## Get Lookup meaning

```sql

  FUNCTION  get_lookup_meaning
                  (p_lookup_name   IN  VARCHAR2
                  ,p_code          IN  VARCHAR2
                  )
  RETURN VARCHAR2;

```

## Get Lookup Code

```sql

  FUNCTION  get_lookup_code
                  (p_name          IN  VARCHAR2
                  ,p_meaning       IN  VARCHAR2
                  ,p_ignore_case   IN  VARCHAR2
                  )
  RETURN VARCHAR2;
  
```

## Get Lookup Tag

```sql
  FUNCTION  get_lookup_tag
                  (p_name          IN  VARCHAR2,
                   p_code          IN  VARCHAR2
                   )
  RETURN VARCHAR2;
```

## Get Lookup Description


```sql
  FUNCTION  get_lookup_description
                  (p_name          IN  VARCHAR2,
                   p_code          IN  VARCHAR2
                   )
  RETURN VARCHAR2;

```

## Get Lookup Display Sequence Number

```sql
  FUNCTION  get_lookup_disp_seq_number
                  (p_name          IN  VARCHAR2,
                   p_code          IN  VARCHAR2
                   )
  RETURN VARCHAR2;
```



## Check lookup code exists

```sql
  -- check whether lookup code exists or not in a given lookup
  -- Return Y or N
  FUNCTION chk_lookup_code_exists
                  (p_name          IN  VARCHAR2
                  ,p_code          IN  VARCHAR2
                  ,p_ignore_case   IN  VARCHAR2 DEFAULT 'N'
                  )
  RETURN VARCHAR2; --Y/N
```




## Next Steps

- [Security APIs](security_api.md)
- [Export APIs](export_api.md)
- [Agent APIs](agent_api.md)