# **Appendix A - Request Line Action Codes**

This appendix provides a complete reference of hierarchy action codes used throughout EPMware Logic Builder scripts.

The following is a list of Hierarchy Action codes that can be referenced in various Logic Scripts such as Dimension Mapping and Pre/Post Hierarchy Actions.

## Action Codes Reference Table

| Action Code | Action Name |
| --- | --- |
| CMC | Create Member - As Child |
| CMS | Create Member - As Sibling |
| DM | Delete Member |
| RM | Rename Member |
| ISMC | Insert Shared Member - As Child |
| ISMS | Insert Shared Member - As Sibling |
| P | Edit Properties |
| ZC | Move Member |
| RC | Reorder Children |
| RSM | Remove Shared Member |
| AC | Activate Member |
| IC | Inactivate Member |


## Usage in Logic Scripts

### Accessing Action Codes

Action codes are available through the global variable `g_action_code` in various script types:

```sql
DECLARE
    l_action_code VARCHAR2(10);
BEGIN
    -- Get the current action code
    l_action_code := ew_lb_api.g_action_code;
    
    -- Process based on action
    CASE l_action_code
        WHEN 'CMC' THEN
            log('Processing Create Member as Child');
            -- Create child logic
        WHEN 'DM' THEN
            log('Processing Delete Member');
            -- Delete logic
        WHEN 'ZC' THEN
            log('Processing Move Member');
            -- Move logic
        ELSE
            log('Action code: ' || l_action_code);
    END CASE;
END;
```

## See Also

- [Appendix B](appendix_b_out_of_box_scripts.md) -  Out of the box Logic Scripts 
- [Hierarchy Actions](../events/pre-hierarchy-actions/index.md) -  Pre Hierarchy Actions Details
- [Hierarchy Actions](../events/post-hierarchy-actions/index.md) - Post Hierarchy Actions Details
- [Dimension Mapping](../events/dimension-mapping/index.md) - Dimension Mapping Details 
