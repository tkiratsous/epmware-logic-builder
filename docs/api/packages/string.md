# String API Functions

The String API provides utility functions for string manipulation, parsing, and formatting within Logic Builder scripts.

**Package**: `EW_STRING`  
**Usage**: `ew_string.<function_name>`

## Overview

The String API enables:
- String parsing and splitting
- Format conversion
- Pattern matching
- Text manipulation
- Encoding/decoding
- String validation

## Basic String Functions

### split_string

Splits a delimited string into an array.

```sql
FUNCTION split_string(
  p_string    IN VARCHAR2,
  p_delimiter IN VARCHAR2 DEFAULT ','
) RETURN ew_global.g_value_tbl;
```

**Example:**
```sql
DECLARE
  l_values ew_global.g_value_tbl;
BEGIN
  l_values := ew_string.split_string(
    p_string    => 'Account1,Account2,Account3',
    p_delimiter => ','
  );
  
  FOR i IN 1..l_values.COUNT LOOP
    DBMS_OUTPUT.PUT_LINE(i || ': ' || l_values(i));
  END LOOP;
END;
```

### join_string

Joins array elements into a delimited string.

```sql
FUNCTION join_string(
  p_array     IN ew_global.g_value_tbl,
  p_delimiter IN VARCHAR2 DEFAULT ','
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_array ew_global.g_value_tbl;
  l_result VARCHAR2(4000);
BEGIN
  l_array(1) := 'Value1';
  l_array(2) := 'Value2';
  l_array(3) := 'Value3';
  
  l_result := ew_string.join_string(
    p_array     => l_array,
    p_delimiter => '|'
  );
  -- Result: 'Value1|Value2|Value3'
  DBMS_OUTPUT.PUT_LINE(l_result);
END;
```

### trim_all

Removes all leading and trailing spaces, tabs, and newlines.

```sql
FUNCTION trim_all(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

## Case Conversion

### proper_case

Converts string to proper case (title case).

```sql
FUNCTION proper_case(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_result VARCHAR2(100);
BEGIN
  l_result := ew_string.proper_case('JOHN DOE');
  -- Result: 'John Doe'
  
  l_result := ew_string.proper_case('mcdonald');
  -- Result: 'Mcdonald'
  
  DBMS_OUTPUT.PUT_LINE(l_result);
END;
```

### camel_case

Converts string to camelCase.

```sql
FUNCTION camel_case(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

### snake_case

Converts string to snake_case.

```sql
FUNCTION snake_case(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

## Pattern Matching

### like_pattern

Checks if string matches a pattern (supports wildcards).

```sql
FUNCTION like_pattern(
  p_string  IN VARCHAR2,
  p_pattern IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
IF ew_string.like_pattern('Account123', 'Account%') = 'Y' THEN
  DBMS_OUTPUT.PUT_LINE('Pattern matches');
END IF;
```

### regex_match

Performs regular expression matching.

```sql
FUNCTION regex_match(
  p_string  IN VARCHAR2,
  p_pattern IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
-- Check if string contains only numbers
IF ew_string.regex_match('12345', '^\d+$') = 'Y' THEN
  DBMS_OUTPUT.PUT_LINE('String is numeric');
END IF;

-- Check email format
IF ew_string.regex_match('user@example.com', 
   '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') = 'Y' THEN
  DBMS_OUTPUT.PUT_LINE('Valid email format');
END IF;
```

### extract_pattern

Extracts substring matching a pattern.

```sql
FUNCTION extract_pattern(
  p_string  IN VARCHAR2,
  p_pattern IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_result VARCHAR2(100);
BEGIN
  -- Extract numbers from string
  l_result := ew_string.extract_pattern('Account123ABC', '\d+');
  -- Result: '123'
  
  -- Extract email domain
  l_result := ew_string.extract_pattern('user@company.com', '@(.+)');
  -- Result: 'company.com'
END;
```

## String Parsing

### parse_key_value

Parses key-value pairs from a string.

```sql
FUNCTION parse_key_value(
  p_string      IN VARCHAR2,
  p_delimiter   IN VARCHAR2 DEFAULT ';',
  p_key_value_sep IN VARCHAR2 DEFAULT '='
) RETURN ew_global.g_name_value_tbl;
```

**Example:**
```sql
DECLARE
  l_params ew_global.g_name_value_tbl;
  l_key VARCHAR2(100);
BEGIN
  l_params := ew_string.parse_key_value(
    p_string        => 'name=John;age=30;city=NYC',
    p_delimiter     => ';',
    p_key_value_sep => '='
  );
  
  l_key := l_params.FIRST;
  WHILE l_key IS NOT NULL LOOP
    DBMS_OUTPUT.PUT_LINE(l_key || ' = ' || l_params(l_key));
    l_key := l_params.NEXT(l_key);
  END LOOP;
END;
```

### get_token

Extracts a specific token from a delimited string.

```sql
FUNCTION get_token(
  p_string    IN VARCHAR2,
  p_position  IN NUMBER,
  p_delimiter IN VARCHAR2 DEFAULT ','
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_token VARCHAR2(100);
BEGIN
  l_token := ew_string.get_token('A,B,C,D', 3, ',');
  -- Result: 'C'
  DBMS_OUTPUT.PUT_LINE('Third token: ' || l_token);
END;
```

## String Manipulation

### replace_multiple

Replaces multiple strings in one operation.

```sql
FUNCTION replace_multiple(
  p_string       IN VARCHAR2,
  p_search_list  IN ew_global.g_value_tbl,
  p_replace_list IN ew_global.g_value_tbl
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_search ew_global.g_value_tbl;
  l_replace ew_global.g_value_tbl;
  l_result VARCHAR2(4000);
BEGIN
  l_search(1) := 'OLD';
  l_replace(1) := 'NEW';
  l_search(2) := 'LEGACY';
  l_replace(2) := 'MODERN';
  
  l_result := ew_string.replace_multiple(
    p_string       => 'OLD system with LEGACY code',
    p_search_list  => l_search,
    p_replace_list => l_replace
  );
  -- Result: 'NEW system with MODERN code'
END;
```

### remove_special_chars

Removes special characters from a string.

```sql
FUNCTION remove_special_chars(
  p_string        IN VARCHAR2,
  p_keep_spaces   IN VARCHAR2 DEFAULT 'Y',
  p_allowed_chars IN VARCHAR2 DEFAULT NULL
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_clean VARCHAR2(100);
BEGIN
  l_clean := ew_string.remove_special_chars(
    p_string      => 'Account#123-ABC!',
    p_keep_spaces => 'N'
  );
  -- Result: 'Account123ABC'
  
  l_clean := ew_string.remove_special_chars(
    p_string        => 'Value_123.45',
    p_allowed_chars => '_.'
  );
  -- Result: 'Value_123.45' (keeps underscore and period)
END;
```

### truncate_string

Truncates string to specified length with optional ellipsis.

```sql
FUNCTION truncate_string(
  p_string    IN VARCHAR2,
  p_max_length IN NUMBER,
  p_ellipsis  IN VARCHAR2 DEFAULT '...'
) RETURN VARCHAR2;
```

## String Validation

### is_numeric

Checks if string contains only numeric characters.

```sql
FUNCTION is_numeric(
  p_string IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### is_alpha

Checks if string contains only alphabetic characters.

```sql
FUNCTION is_alpha(
  p_string IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

### is_alphanumeric

Checks if string contains only alphanumeric characters.

```sql
FUNCTION is_alphanumeric(
  p_string IN VARCHAR2
) RETURN VARCHAR2;  -- Returns 'Y' or 'N'
```

**Example:**
```sql
BEGIN
  IF ew_string.is_numeric('12345') = 'Y' THEN
    DBMS_OUTPUT.PUT_LINE('Valid number');
  END IF;
  
  IF ew_string.is_alpha('ABC') = 'Y' THEN
    DBMS_OUTPUT.PUT_LINE('Only letters');
  END IF;
  
  IF ew_string.is_alphanumeric('ABC123') = 'Y' THEN
    DBMS_OUTPUT.PUT_LINE('Letters and numbers only');
  END IF;
END;
```

## Encoding Functions

### encode_html

Encodes special HTML characters.

```sql
FUNCTION encode_html(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_html VARCHAR2(4000);
BEGIN
  l_html := ew_string.encode_html('<script>alert("XSS")</script>');
  -- Result: '&lt;script&gt;alert(&quot;XSS&quot;)&lt;/script&gt;'
  DBMS_OUTPUT.PUT_LINE(l_html);
END;
```

### encode_url

URL encodes a string.

```sql
FUNCTION encode_url(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

### decode_url

URL decodes a string.

```sql
FUNCTION decode_url(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

## Advanced String Operations

### word_wrap

Wraps text at specified width.

```sql
FUNCTION word_wrap(
  p_string IN VARCHAR2,
  p_width  IN NUMBER DEFAULT 80
) RETURN VARCHAR2;
```

### extract_numbers

Extracts all numbers from a string.

```sql
FUNCTION extract_numbers(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_numbers VARCHAR2(100);
BEGIN
  l_numbers := ew_string.extract_numbers('Account123ABC456');
  -- Result: '123456'
  DBMS_OUTPUT.PUT_LINE('Numbers: ' || l_numbers);
END;
```

### generate_random_string

Generates a random string.

```sql
FUNCTION generate_random_string(
  p_length IN NUMBER,
  p_type   IN VARCHAR2 DEFAULT 'ALPHANUMERIC'  
  -- Options: 'ALPHA', 'NUMERIC', 'ALPHANUMERIC', 'HEX'
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_password VARCHAR2(20);
  l_code VARCHAR2(10);
BEGIN
  -- Generate random password
  l_password := ew_string.generate_random_string(12, 'ALPHANUMERIC');
  
  -- Generate verification code
  l_code := ew_string.generate_random_string(6, 'NUMERIC');
  
  DBMS_OUTPUT.PUT_LINE('Password: ' || l_password);
  DBMS_OUTPUT.PUT_LINE('Code: ' || l_code);
END;
```

## String Comparison

### fuzzy_match

Performs fuzzy string matching.

```sql
FUNCTION fuzzy_match(
  p_string1  IN VARCHAR2,
  p_string2  IN VARCHAR2,
  p_threshold IN NUMBER DEFAULT 80
) RETURN VARCHAR2;  -- Returns 'Y' if similarity >= threshold
```

### levenshtein_distance

Calculates edit distance between strings.

```sql
FUNCTION levenshtein_distance(
  p_string1 IN VARCHAR2,
  p_string2 IN VARCHAR2
) RETURN NUMBER;
```

**Example:**
```sql
DECLARE
  l_distance NUMBER;
BEGIN
  l_distance := ew_string.levenshtein_distance('kitten', 'sitting');
  -- Result: 3
  DBMS_OUTPUT.PUT_LINE('Edit distance: ' || l_distance);
  
  IF ew_string.fuzzy_match('John Smith', 'Jon Smyth', 70) = 'Y' THEN
    DBMS_OUTPUT.PUT_LINE('Names are similar');
  END IF;
END;
```

## Utility Functions

### reverse_string

Reverses a string.

```sql
FUNCTION reverse_string(
  p_string IN VARCHAR2
) RETURN VARCHAR2;
```

### repeat_string

Repeats a string n times.

```sql
FUNCTION repeat_string(
  p_string IN VARCHAR2,
  p_count  IN NUMBER
) RETURN VARCHAR2;
```

### pad_string

Pads string to specified length.

```sql
FUNCTION pad_string(
  p_string    IN VARCHAR2,
  p_length    IN NUMBER,
  p_pad_char  IN VARCHAR2 DEFAULT ' ',
  p_direction IN VARCHAR2 DEFAULT 'RIGHT'  -- 'LEFT', 'RIGHT', 'BOTH'
) RETURN VARCHAR2;
```

**Example:**
```sql
DECLARE
  l_result VARCHAR2(100);
BEGIN
  -- Pad with zeros on left
  l_result := ew_string.pad_string('123', 8, '0', 'LEFT');
  -- Result: '00000123'
  
  -- Pad with spaces on right
  l_result := ew_string.pad_string('ABC', 10, ' ', 'RIGHT');
  -- Result: 'ABC       '
  
  -- Center text
  l_result := ew_string.pad_string('TITLE', 20, '-', 'BOTH');
  -- Result: '-------TITLE--------'
END;
```

## Best Practices

1. **Handle NULL Values**
   ```sql
   l_result := ew_string.trim_all(NVL(p_input, ''));
   ```

2. **Check String Length**
   ```sql
   IF LENGTH(p_string) > 4000 THEN
     -- Handle large strings appropriately
   END IF;
   ```

3. **Use Appropriate Functions**
   ```sql
   -- Use is_numeric instead of regex for simple checks
   IF ew_string.is_numeric(l_value) = 'Y' THEN...
   ```

4. **Consider Performance**
   ```sql
   -- Cache regex patterns for reuse
   g_email_pattern := '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$';
   ```

## Next Steps

- [Lookup APIs](lookup.md)
- [Security APIs](security.md)
- [Export APIs](export.md)