# **Export API Functions**

**Package**: `ew_exp_api`  
**Usage**: `ew_exp_api.<function_name>`

The purpose of this package is to run Export Profiles or Export Books.<br/>
For example, customer wants to run an Export when request reaches at a specific stage. More advanced customization requires these export files to be sent to external systems like Databricks or AWS S3 bucket or SFTP server. Post Export Logic Scripts can help transfer export files, but submission of the Export itself will happen using these APIs as part of the custom workflow tasks.



## Run Export

```sql
PROCEDURE run_export
                (p_user_id      IN NUMBER
                ,p_name         IN VARCHAR2 -- Export Profile Name
                ,x_task_id      OUT NUMBER
                ,x_status       OUT VARCHAR2 -- S or E
                ,x_message      OUT VARCHAR2
                );
```

  
## Run Export Book

```sql
-- Execute Export Book
PROCEDURE run_export_book
                (p_user_id      IN NUMBER
                ,p_name         IN VARCHAR2 -- Export Book Name
                ,x_task_id      OUT NUMBER
                ,x_status       OUT VARCHAR2 -- S or E
                ,x_message      OUT VARCHAR2
                );
```



## Next Steps

- [Agent APIs](agent_api.md)
- [Appendices](../../appendices/index.md)
- [API Overview](../index.md)