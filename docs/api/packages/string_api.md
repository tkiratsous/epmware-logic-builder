# **String API Functions**


**Package**: `EW_STRING`  
**Usage**: `ew_string.<function_name>`

This package contains some useful functions for string manipulations. Oracle PL/SQL provides very rich string functions but these are some additional functions.

## IS_ALPHA String

Pass a string to determine whether the string has all characters which are between A-Z, a-z, 0-9 and an underscore character. If it is then return “Y” else return “N”. Second parameter is optional which allows space to be eligible character or not.


```sql
  FUNCTION is_alpha_str (p_str IN VARCHAR2 
                        ,p_allow_space  IN VARCHAR2 DEFAULT 'Y'
                         )
  RETURN VARCHAR2; -- Return Y or N
```


## IS_ALPHA String

Pass a string to determine whether the string has all characters which are between A-Z, a-z, 0-9 and an underscore character. If it is then return “Y” else return “N”. Second parameter is optional which allows space to be eligible character or not.

```sql

  FUNCTION is_alpha_str (p_str IN VARCHAR2 
                        ,p_allow_space  IN VARCHAR2 DEFAULT 'Y'
                         )
  RETURN VARCHAR2; -- Return Y or N
```

## SPLIT String

If a string contains multiple values separated by a character such as a comma, then you can use the “cut” function as shown below to separate each value from the string into an array.

Output from this procedure is an array type. You will need to define a local variable of values_list type.

```sql

  /*
  ** cut - to take a string and split it into a table of values where the values are separated by and enclosed by specified characters
  */
  PROCEDURE cut (p_string       IN            VARCHAR2
                ,p_sep          IN            VARCHAR2
                ,p_encl         IN            VARCHAR2
                ,p_list            OUT NOCOPY values_list
                )
  
TYPE values_list IS TABLE OF VARCHAR2(4000) INDEX BY BINARY_INTEGER;

```

Note: Refer to EW_SHARED_NODE_POSITION Logic Script as an example of this procedure.

Declaration of local variables of values_list type (l_primary_sorts as an example)


## SPLIT_NUMERIC String

If a string contains a numerical value but has either a prefix or suffix or both with some alphanumerical values, then this procedure will split into three parts and return three components in return values.

```sql
  -- From a given string split numerical value and prefix and suffix values
  -- For example, 
  -- AB1000 will return 1000, AB as prefix nothing for suffix
  -- 1000CD will return 1000, nothing for prefix CD for suffix
  -- 190000 will return 190000, nothing for both prefix and suffix
  -- AB1000CD will return 1000, AB for prefix and CD for suffix
 
  PROCEDURE split_numeric(p_str     IN VARCHAR2
                         ,x_number OUT NUMBER
                         ,x_prefix OUT VARCHAR2
                         ,x_suffix OUT VARCHAR2
                         );
```


## REPLACE_ALPHA_STR
The purpose of this function is to remove Alphanumeric characters and return remaining characters from a string. One of the main purposes of this function is to determine whether a string has any special characters or not. 

For example, customers may prefer a member name or a description to have only Alphanumeric values and if they have any other characters then throw validation errors.  This API can help build such validations.


*replace_alpha_str* : Replace Alpha chars from the string and Return Remaining Chars. Replace characters A - Z, a - z, 0 - 9 or _and space. Additionally specify chars that are to be removed, like # * $ and so on.


```sql

  FUNCTION replace_alpha_str (p_str          IN VARCHAR2
                             ,p_allow_space  IN VARCHAR2 DEFAULT 'Y'
                             ,p_repl_chars   IN VARCHAR2 DEFAULT NULL
                             )
  RETURN VARCHAR2;
  
```
  
  
## KEEP_ALPHA_STR

The purpose of this function is to remove non-Alphanumeric characters and return remaining characters from a string. One of the main purposes of this function is to remove non-alphanumeric values from the given string.


*keep_alpha_str* : Replace non-Alpha chars from the string and return remaining Chars. Keep characters A - Z, a - z, 0 - 9 or _ and space. Additionally specify chars that are to be kept, like #*$ and so on.


```SQL

  FUNCTION keep_alpha_str (p_str          IN VARCHAR2
                          ,p_allow_space  IN VARCHAR2 DEFAULT 'N'
                          ,p_keep_chars   IN VARCHAR2 DEFAULT NULL
                          )
  RETURN VARCHAR2;

```

## APPEND_STR
The purpose of this function is to append a string to the given string and return a concatenated string. If the separator character is not provided, then comma will be used as a default separator character.

```sql
  PROCEDURE append_str(p_add IN VARCHAR2
                      ,x_str IN OUT VARCHAR2                      
                      ,p_sep IN VARCHAR2 DEFAULT ','
                      );

```


## GET_POSITION_IN_STR

The purpose of this function is to provide the position (Element #) of a string in a given string.


```sql
  -- Get position of a string in a list
  -- For example, A101,A102,A103 is a given string and we need to know in this list
  -- position of A102 which is # 2
  --
  FUNCTION get_position_in_str (p_string  IN VARCHAR2
                               ,p_value   IN VARCHAR2
                               ,p_sep     IN VARCHAR2 DEFAULT ','
                               ,p_encl    IN VARCHAR2 DEFAULT '"'
                               )
  RETURN NUMBER;

```


## COMPARE_VALUE

The purpose of this function is to compare values of two strings either numerically OR text basis and return Y or N. p_str1 is compared with p_str2 string. P_str2 can be a multi value string separated by a character (for example comma) and if that is the case p_str1 will be compared with each element of p_str2. For example, p_str1 => ‘A’ and p_str2 => ‘X,’Y,’A’. 

```sql
FUNCTION compare_value (p_str1       IN VARCHAR2
                       ,p_str2       IN VARCHAR2
                       ,p_numerical  IN VARCHAR2 DEFAULT 'N'
                       ,p_case_match IN VARCHAR2 DEFAULT 'Y'
                       ,p_sep        IN VARCHAR2 DEFAULT NULL
                       ,p_encl       IN VARCHAR2 DEFAULT NULL
                       )
RETURN VARCHAR2;
```


## STR_HAS_NUMERICAL_VALUE

The purpose of this function is to check whether given string has at least one numerical character (0 to 9) in it or not. 

```sql

FUNCTION str_has_numerical_char (p_str IN VARCHAR2)
RETURN VARCHAR2; -- Y or N

```


## GET_CLOB_LENGTH

CLOB means Large Text. Such properties are typically Member Formulas type of properties of a member and hold large text (>2000 characters). This API provides its Length. 


```sql
  -- Get CLOB Length
  FUNCTION get_clob_length (p_clob IN CLOB)
  RETURN NUMBER;
```


## GET_CHAR_COUNT_IN_CLOB

CLOB means Large Text. Such properties are typically Member Formulas type of properties of a member and hold large text (>2000 characters). This API provides count of specific character in it.


```sql
  -- Count # of occurrences of a character in CLOB
  FUNCTION get_char_count_in_clob (p_clob IN CLOB
                                  ,p_char IN VARCHAR2
                                  )
  RETURN NUMBER;

```

## REPLACE_STR_IN_CLOB
 
CLOB means Large Text. Such properties are typically Member Formulas type of properties of a member and hold large text (>2000 characters). This API replaces a specific string in CLOB with the given string and returns CLOB.


```sql
  -- This function will search for a given string and replace it with 
  -- the given string and return new CLOB
  FUNCTION replace_str_in_clob (p_src_clob    IN CLOB
                               ,p_search_str  IN VARCHAR2
                               ,p_replace_str IN VARCHAR2
                               )
  RETURN CLOB;
```


## REMOVE_COMMENTS_IN_CLOB

CLOB means Large Text. Such properties are typically Member Formulas type of properties of a member and hold large text (>2000 characters). This API scans typical comments section which usually starts with /* and ends with */ characters and remove comments and returns resultant text as CLOB.

```sql
  -- Scan CLOB and remove comments within the CLOB text
  FUNCTION remove_comments_in_clob (p_clob      IN CLOB
                                   ,p_start_str IN VARCHAR2
                                   ,p_end_str   IN VARCHAR2
                                   )
  RETURN CLOB;

```


## CHK_STRING_IN_CLOB

CLOB means Large Text. Such properties are typically Member Formulas type of properties of a member and hold large text (>2000 characters). This API checks for a specific string in CLOB and returns Y if the string is found else N. This API can be used if user wants to find a specific member or a value like Alias of a member in the Large Text (like member formula).


```sql
  -- Check if the CLOB has a string in it - Return Y if exists
  -- For example, search for a string [TEST] in CLOB  
  -- TOTCASH * [TEST]
  -- If p_string_prefix is provided and if the CLOB has a string
  -- with the first character being with that prefix 
  -- followed by p_string then it will be considered as a valid find.
  -- p_clob_src is used mainly for logging purposes in case there is
  -- any error.
  FUNCTION chk_string_in_clob
                 (p_clob                 IN CLOB
                 ,p_string               IN VARCHAR2
                 ,p_remove_comments      IN VARCHAR2 DEFAULT 'N'
                 ,p_comments_begin_str   IN VARCHAR2 DEFAULT '/*'
                 ,p_comments_end_str     IN VARCHAR2 DEFAULT '*/'
                 ,p_encl_char_begin      IN VARCHAR2 DEFAULT '['
                 ,p_encl_char_end        IN VARCHAR2 DEFAULT ']'
                 ,p_case_match           IN VARCHAR2 DEFAULT 'N'
                 ,p_string_prefix        IN VARCHAR2 DEFAULT '&'
                 ,p_clob_src             IN VARCHAR2 DEFAULT NULL
                 )
  RETURN VARCHAR2; -- Y or N

```


## GET_SUBSTRINGS_IN_CLOB

CLOB means Large Text. Such properties are typically Member Formulas type of properties of a member and hold large text (>2000 characters). This API checks CLOB for all texts within a specific start and closing strings and returns list of such texts in a PIPELINED Table format. This API can be used if user wants to find a specific member or a value like Alias of a member in the Large Text (like member formula).

```sql
  -- For example, get a string [TEST] in CLOB  
  -- TOTCASH * [TEST]
  -- If p_string_prefix is provided and if the CLOB has a string
  -- with the first character being with that prefix 
  -- followed by p_string then it will be considered as a valid find.
  -- p_clob_src is used mainly for logging purposes in case there is
  -- any error.
  
 
  FUNCTION get_substrings_in_clob
      (p_clob                 IN CLOB
      ,p_remove_comments      IN VARCHAR2 DEFAULT 'N'
      ,p_comments_begin_str   IN VARCHAR2 DEFAULT '/*'
      ,p_comments_end_str     IN VARCHAR2 DEFAULT '*/'
      ,p_encl_char_begin      IN VARCHAR2 DEFAULT '['
      ,p_encl_char_end        IN VARCHAR2 DEFAULT ']'
      ,p_string_prefix        IN VARCHAR2 DEFAULT '&'
      ,p_clob_src             IN VARCHAR2 DEFAULT NULL -- for debugging
      )
  RETURN ew_varchar2_row_type PIPELINED;

```


For example, following query can return all members referred to in Member Formulas for a given Application.

```sql
  --
  
  SELECT 
      a.member_name member_formula_member_name
     ,a.dim_name    member_formula_dim_name
     ,a.clob_prop_value
     ,m.member_name
     ,x.column_value
     ,'MEMBER_NAME' check_type 
  FROM ew_member_props_all_v a
    ,TABLE (ew_string.get_substrings_in_clob
                 (p_clob                => a.clob_prop_value
                 ,p_remove_comments     => 'Y'
                 ,p_comments_begin_str  => '/*'
                 ,p_comments_end_str    => '*/'
                 ,p_encl_char_begin     => '['
                 ,p_encl_char_end       => ']'
                 ,p_string_prefix       => '&'
                 ,p_clob_src => a.member_name||'-'||a.prop_label
                 )) x
     ,ew_members_v m
  WHERE 1=1
  AND a.clob_flag = 'Y'
  AND a.prop_label LIKE ‘%Formula%’ /*check Member Formulas*/
  AND a.app_id = :p_app_id
  AND a.app_id = m.app_id
  AND UPPER(m.member_name) = UPPER(x.column_value)
  ORDER BY m.member_name
  
  --
```


## Next Steps

- [Lookup APIs](lookup_functions.md)
- [Security APIs](security_api.md)
- [Export APIs](export_api.md)