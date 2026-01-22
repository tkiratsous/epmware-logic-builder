# **Email API Functions**


## Package: EW_EMAIL_API

These functions can be referred to as ew_email_api."Function Name"


## Get User Email

Two functions are provided to get the User’s email by passing either User ID or passing User Name’


```sql

FUNCTION get_user_email(p_user_id IN NUMBER) RETURN VARCHAR2;

FUNCTION get_user_email(p_user_name IN VARCHAR2) RETURN VARCHAR2;

```

## Send Email (Specify Recipients)

```sql

 -- return Success / Failure code in x_result out parameter
 -- x_result -> success = 0 failure = 1
 PROCEDURE send_email    (p_recipients IN  VARCHAR2
                         ,p_subject    IN  VARCHAR2
                         ,p_body       IN  VARCHAR2
                         ,p_send_addr  IN  VARCHAR2 DEFAULT NULL
                         ,p_ccs        IN  VARCHAR2 DEFAULT NULL
                         ,p_bccs       IN  VARCHAR2 DEFAULT NULL
                         ,x_result     OUT NUMBER
                         ) ;

```

## Send Email (Email Template)

```sql

PROCEDURE send_email (p_request_id          IN NUMBER
                     ,p_email_template_name IN VARCHAR2
                     ,p_email_vars          IN g_email_vars
                     );
                     
```

G_email_vars is a global variable in the Email API Package with type reference as mentioned below. This parameter can be used to specify the Name/Value type of parameter that can be passed to the template. Email Templates can refer to these variables and replace values in the template.

If the Request ID is passed, then request id-related information can be referenced in the email template.

```sql
TYPE g_email_vars IS TABLE OF VARCHAR2(2000) INDEX BY VARCHAR2(50);
```

## Next Steps

- [Request APIs](request_api.md)
- [ERP Import APIs](erp_import_api.md)
- [Hierarchy APIs](hierarchy_api.md)