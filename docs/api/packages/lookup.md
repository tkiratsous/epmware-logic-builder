# Lookup API Functions

The Lookup API provides functions for managing and retrieving lookup values, codes, and system-defined lists used throughout EPMware.

**Package**: `EW_LOOKUP`  
**Usage**: `ew_lookup.<function_name>`

## Overview

The Lookup API enables:
- Lookup value retrieval
- Code validation
- List management
- Custom lookup creation
- Cached lookup access
- Hierarchical lookups

## Basic Lookup Functions

### get_lookup_value

Retrieves the display value for a lookup code.

```sql
FUNCTION get_lookup_value(
  p_lookup_type IN VARCHAR2,
  p_lookup_code IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_display_value VARCHAR2(255);
BEGIN
  l_display_value := ew_lookup.get_lookup_value(
    p_lookup_type => 'ACTION_CODE',
    p_lookup_code => 'CMC'
  );
  -- Result: 'Create Member as Child'
  DBMS_OUTPUT.PUT_LINE('Action: ' || l_display_value);
END;
```

### get_lookup_code

Retrieves the code for a given display value.

```sql
FUNCTION get_lookup_code(
  p_lookup_type  IN VARCHAR2,
  p_lookup_value IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_code VARCHAR2(50);
BEGIN
  l_code := ew_lookup.get_lookup_code(
    p_lookup_type  => 'MEMBER_TYPE',
    p_lookup_value => 'Parent Member'
  );
  -- Result: 'PARENT'
  DBMS_OUTPUT.PUT_LINE('Code: ' || l_code);
END;
```

### lookup_exists

Checks if a lookup code exists.

```sql
FUNCTION lookup_exists(
  p_lookup_type IN VARCHAR2,
  p_lookup_code IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

## Lookup List Functions

### get_lookup_list

Returns all lookups for a specific type.

```sql
FUNCTION get_lookup_list(
  p_lookup_type IN VARCHAR2,
  p_active_only IN VARCHAR2 DEFAULT 'Y'
) RETURN lookup_list_tbl;
```

**Example:**
```sql
DECLARE
  l_action_codes ew_lookup.lookup_list_tbl;
BEGIN
  l_action_codes := ew_lookup.get_lookup_list(
    p_lookup_type => 'ACTION_CODE',
    p_active_only => 'Y'
  );
  
  DBMS_OUTPUT.PUT_LINE('Available Action Codes:');
  FOR i IN 1..l_action_codes.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(
      l_action_codes(i).lookup_code || ' - ' ||
      l_action_codes(i).lookup_value
    );
  END LOOP;
END;
```

### get_lookup_types

Returns all available lookup types.

```sql
FUNCTION get_lookup_types
RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_types ew_global.g_value_tbl;
BEGIN
  l_types := ew_lookup.get_lookup_types();
  
  DBMS_OUTPUT.PUT_LINE('Lookup Types:');
  FOR i IN 1..l_types.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(i || '. ' || l_types(i));
  END LOOP;
END;
```

## Standard Lookup Types

### Common System Lookups

```sql
-- Action Codes
l_value := ew_lookup.get_lookup_value('ACTION_CODE', 'CMC');
-- Result: 'Create Member as Child'

-- Member Types
l_value := ew_lookup.get_lookup_value('MEMBER_TYPE', 'LEAF');
-- Result: 'Leaf Member'

-- Request Status
l_value := ew_lookup.get_lookup_value('REQUEST_STATUS', 'APPROVED');
-- Result: 'Approved'

-- Workflow Stages
l_value := ew_lookup.get_lookup_value('WORKFLOW_STAGE', 'REVIEW');
-- Result: 'Under Review'

-- Priority Levels
l_value := ew_lookup.get_lookup_value('PRIORITY', 'HIGH');
-- Result: 'High Priority'
```

### Application-Specific Lookups

```sql
-- Account Types
l_value := ew_lookup.get_lookup_value('ACCOUNT_TYPE', 'REVENUE');

-- Consolidation Methods
l_value := ew_lookup.get_lookup_value('CONSOLIDATION_METHOD', 'FULL');

-- Time Balance Types
l_value := ew_lookup.get_lookup_value('TIME_BALANCE', 'FLOW');

-- Data Storage Types
l_value := ew_lookup.get_lookup_value('DATA_STORAGE', 'STORE');
```

## Custom Lookup Management

### create_custom_lookup

Creates a custom lookup type.

```sql
PROCEDURE create_custom_lookup(
  p_lookup_type   IN VARCHAR2,
  p_description   IN VARCHAR2,
  p_lookup_values IN lookup_value_tbl
);
```

**Example:**
```sql
DECLARE
  l_values ew_lookup.lookup_value_tbl;
BEGIN
  -- Define lookup values
  l_values(1).lookup_code := 'DEPT01';
  l_values(1).lookup_value := 'Finance';
  l_values(1).sort_order := 1;
  
  l_values(2).lookup_code := 'DEPT02';
  l_values(2).lookup_value := 'Marketing';
  l_values(2).sort_order := 2;
  
  l_values(3).lookup_code := 'DEPT03';
  l_values(3).lookup_value := 'Operations';
  l_values(3).sort_order := 3;
  
  -- Create custom lookup
  ew_lookup.create_custom_lookup(
    p_lookup_type   => 'DEPARTMENT_CODES',
    p_description   => 'Company Department Codes',
    p_lookup_values => l_values
  );
END;
```

### add_lookup_value

Adds a value to existing lookup type.

```sql
PROCEDURE add_lookup_value(
  p_lookup_type  IN VARCHAR2,
  p_lookup_code  IN VARCHAR2,
  p_lookup_value IN VARCHAR2,
  p_description  IN VARCHAR2 DEFAULT NULL,
  p_sort_order   IN NUMBER DEFAULT NULL
);
```

### update_lookup_value

Updates an existing lookup value.

```sql
PROCEDURE update_lookup_value(
  p_lookup_type     IN VARCHAR2,
  p_lookup_code     IN VARCHAR2,
  p_new_value       IN VARCHAR2 DEFAULT NULL,
  p_new_description IN VARCHAR2 DEFAULT NULL,
  p_active_flag     IN VARCHAR2 DEFAULT NULL
);
```

### delete_lookup_value

Deletes a lookup value.

```sql
PROCEDURE delete_lookup_value(
  p_lookup_type IN VARCHAR2,
  p_lookup_code IN VARCHAR2
);
```

## Hierarchical Lookups

### get_child_lookups

Returns child lookups for hierarchical lookup types.

```sql
FUNCTION get_child_lookups(
  p_lookup_type   IN VARCHAR2,
  p_parent_code   IN VARCHAR2
) RETURN lookup_list_tbl;
```

**Example:**
```sql
DECLARE
  l_regions ew_lookup.lookup_list_tbl;
BEGIN
  -- Get regions under North America
  l_regions := ew_lookup.get_child_lookups(
    p_lookup_type => 'GEOGRAPHIC_REGION',
    p_parent_code => 'NORTH_AMERICA'
  );
  
  FOR i IN 1..l_regions.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(l_regions(i).lookup_value);
  END LOOP;
  -- Output: 'United States', 'Canada', 'Mexico'
END;
```

### get_lookup_hierarchy

Returns complete hierarchy for a lookup type.

```sql
FUNCTION get_lookup_hierarchy(
  p_lookup_type IN VARCHAR2
) RETURN lookup_hierarchy_tbl;
```

## Lookup Validation

### validate_lookup_code

Validates if a code is valid for a lookup type.

```sql
FUNCTION validate_lookup_code(
  p_lookup_type IN VARCHAR2,
  p_lookup_code IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' if valid, 'N' if invalid
```

**Example:**
```sql
BEGIN
  IF ew_lookup.validate_lookup_code('ACTION_CODE', 'CMC') = 'Y' THEN
    DBMS_OUTPUT.PUT_LINE('Valid action code');
  ELSE
    DBMS_OUTPUT.PUT_LINE('Invalid action code');
  END IF;
END;
```

### validate_lookup_combination

Validates combinations of lookup values.

```sql
FUNCTION validate_lookup_combination(
  p_lookup_type1 IN VARCHAR2,
  p_lookup_code1 IN VARCHAR2,
  p_lookup_type2 IN VARCHAR2,
  p_lookup_code2 IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' if valid combination
```

## Cached Lookups

### refresh_lookup_cache

Refreshes the lookup cache.

```sql
PROCEDURE refresh_lookup_cache(
  p_lookup_type IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  -- Refresh specific lookup type
  ew_lookup.refresh_lookup_cache('ACTION_CODE');
  
  -- Refresh all lookups
  ew_lookup.refresh_lookup_cache();
END;
```

### get_cached_lookup

Retrieves lookup from cache for better performance.

```sql
FUNCTION get_cached_lookup(
  p_lookup_type IN VARCHAR2,
  p_lookup_code IN VARCHAR2
) RETURN VARCHAR2;
```

## Advanced Features

### Lookup Dependencies

```sql
DECLARE
  l_dependencies ew_global.g_value_tbl;
BEGIN
  -- Get lookups that depend on a value
  l_dependencies := ew_lookup.get_lookup_dependencies(
    p_lookup_type => 'ACCOUNT_TYPE',
    p_lookup_code => 'REVENUE'
  );
  
  IF l_dependencies.COUNT > 0 THEN
    DBMS_OUTPUT.PUT_LINE('Dependent lookups found:');
    FOR i IN 1..l_dependencies.COUNT LOOP
      DBMS_OUTPUT.PUT_LINE('  - ' || l_dependencies(i));
    END LOOP;
  END IF;
END;
```

### Lookup Translation

```sql
DECLARE
  l_translated VARCHAR2(255);
BEGIN
  -- Get translated lookup value
  l_translated := ew_lookup.get_translated_value(
    p_lookup_type => 'ACTION_CODE',
    p_lookup_code => 'CMC',
    p_language    => 'FR'
  );
  -- Result: 'Créer membre comme enfant'
END;
```

### Dynamic Lookup Generation

```sql
DECLARE
  l_lookup_values ew_lookup.lookup_list_tbl;
BEGIN
  -- Generate lookups from query
  l_lookup_values := ew_lookup.generate_lookups_from_query(
    p_query => 'SELECT DISTINCT department_code, department_name ' ||
               'FROM departments WHERE active = ''Y'' ' ||
               'ORDER BY department_name'
  );
  
  -- Create lookup type with generated values
  ew_lookup.create_lookup_from_list(
    p_lookup_type => 'ACTIVE_DEPARTMENTS',
    p_lookup_list => l_lookup_values
  );
END;
```

## Lookup Reporting

### get_lookup_usage

Returns where a lookup is used.

```sql
FUNCTION get_lookup_usage(
  p_lookup_type IN VARCHAR2,
  p_lookup_code IN VARCHAR2
) RETURN usage_list_tbl;
```

### export_lookups

Exports lookups to XML or JSON.

```sql
FUNCTION export_lookups(
  p_lookup_type IN VARCHAR2 DEFAULT NULL,
  p_format      IN VARCHAR2 DEFAULT 'XML'  -- 'XML' or 'JSON'
) RETURN CLOB;
```

**Example:**
```sql
DECLARE
  l_export CLOB;
BEGIN
  -- Export all action codes to XML
  l_export := ew_lookup.export_lookups(
    p_lookup_type => 'ACTION_CODE',
    p_format      => 'XML'
  );
  
  -- Save to file
  save_clob_to_file('lookups_export.xml', l_export);
END;
```

## Error Handling

```sql
BEGIN
  l_value := ew_lookup.get_lookup_value('INVALID_TYPE', 'CODE');
EXCEPTION
  WHEN ew_lookup.lookup_not_found THEN
    DBMS_OUTPUT.PUT_LINE('Lookup not found');
  WHEN ew_lookup.invalid_lookup_type THEN
    DBMS_OUTPUT.PUT_LINE('Invalid lookup type');
  WHEN OTHERS THEN
    DBMS_OUTPUT.PUT_LINE('Error: ' || SQLERRM);
END;
```

## Best Practices

1. **Cache Frequently Used Lookups**
   ```sql
   -- Use cached version for performance
   l_value := ew_lookup.get_cached_lookup('ACTION_CODE', 'CMC');
   ```

2. **Validate Before Use**
   ```sql
   IF ew_lookup.validate_lookup_code(p_type, p_code) = 'Y' THEN
     -- Safe to use lookup
   END IF;
   ```

3. **Handle Missing Lookups**
   ```sql
   l_value := NVL(ew_lookup.get_lookup_value(p_type, p_code), 
                  'Unknown');
   ```

4. **Use Appropriate Functions**
   ```sql
   -- Use exists check instead of retrieving value
   IF ew_lookup.lookup_exists(p_type, p_code) = 'Y' THEN...
   ```

## Next Steps

- [Security APIs](security.md)
- [Export APIs](export.md)
- [Agent APIs](agent.md)