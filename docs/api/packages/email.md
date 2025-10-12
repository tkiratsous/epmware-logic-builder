# Email API Functions

The Email API provides functions for sending email notifications, including support for HTML content, attachments, and distribution lists.

**Package**: `EW_EMAIL`  
**Usage**: `ew_email.<function_name>`

## Overview

The Email API enables:
- Plain text and HTML email messages
- Multiple recipients (TO, CC, BCC)
- File attachments
- Template-based emails
- Distribution list management
- Email queuing and scheduling

## Core Functions

### Send Email

#### send_email

Sends an email message with various options.

```sql
PROCEDURE send_email(
  p_to         IN VARCHAR2,
  p_cc         IN VARCHAR2 DEFAULT NULL,
  p_bcc        IN VARCHAR2 DEFAULT NULL,
  p_subject    IN VARCHAR2,
  p_body       IN VARCHAR2,
  p_body_html  IN VARCHAR2 DEFAULT NULL,
  p_attachment IN VARCHAR2 DEFAULT NULL,
  p_priority   IN VARCHAR2 DEFAULT 'NORMAL'
);
```

**Parameters:**
- `p_to` - Recipient email addresses (semicolon separated)
- `p_cc` - CC recipients (optional)
- `p_bcc` - BCC recipients (optional)
- `p_subject` - Email subject line
- `p_body` - Plain text body
- `p_body_html` - HTML body (optional)
- `p_attachment` - File path for attachment (optional)
- `p_priority` - Email priority (HIGH, NORMAL, LOW)

**Example:**
```sql
BEGIN
  -- Simple text email
  ew_email.send_email(
    p_to      => 'user@company.com',
    p_subject => 'Process Complete',
    p_body    => 'The data import process has completed successfully.'
  );
  
  -- HTML email with CC
  ew_email.send_email(
    p_to        => 'team@company.com',
    p_cc        => 'manager@company.com',
    p_subject   => 'Weekly Report',
    p_body      => 'Please see HTML version',
    p_body_html => '<h2>Weekly Summary</h2><p>All tasks completed.</p>'
  );
  
  -- Email with attachment
  ew_email.send_email(
    p_to         => 'finance@company.com',
    p_subject    => 'Export File Ready',
    p_body       => 'Attached is the requested export file.',
    p_attachment => '/exports/financial_data.csv'
  );
END;
```

### Send Templated Email

#### send_template_email

Sends an email using a predefined template.

```sql
PROCEDURE send_template_email(
  p_template_name IN VARCHAR2,
  p_to            IN VARCHAR2,
  p_placeholders  IN ew_global.g_name_value_tbl DEFAULT NULL
);
```

**Parameters:**
- `p_template_name` - Name of email template
- `p_to` - Recipient email addresses
- `p_placeholders` - Name-value pairs for template variables

**Example:**
```sql
DECLARE
  l_placeholders ew_global.g_name_value_tbl;
BEGIN
  -- Set template variables
  l_placeholders('USER_NAME') := 'John Doe';
  l_placeholders('REQUEST_ID') := '12345';
  l_placeholders('STATUS') := 'Approved';
  
  -- Send templated email
  ew_email.send_template_email(
    p_template_name => 'REQUEST_APPROVAL',
    p_to            => 'user@company.com',
    p_placeholders  => l_placeholders
  );
END;
```

### Queue Email

#### queue_email

Queues an email for later sending.

```sql
FUNCTION queue_email(
  p_to           IN VARCHAR2,
  p_subject      IN VARCHAR2,
  p_body         IN VARCHAR2,
  p_send_after   IN DATE DEFAULT SYSDATE,
  p_max_retries  IN NUMBER DEFAULT 3
) RETURN NUMBER; -- Returns queue ID
```

**Example:**
```sql
DECLARE
  l_queue_id NUMBER;
BEGIN
  -- Queue email for later
  l_queue_id := ew_email.queue_email(
    p_to         => 'user@company.com',
    p_subject    => 'Scheduled Notification',
    p_body       => 'This is a scheduled message',
    p_send_after => SYSDATE + 1/24  -- Send in 1 hour
  );
  
  DBMS_OUTPUT.PUT_LINE('Email queued with ID: ' || l_queue_id);
END;
```

## Distribution Lists

### send_to_distribution_list

Sends email to a predefined distribution list.

```sql
PROCEDURE send_to_distribution_list(
  p_list_name  IN VARCHAR2,
  p_subject    IN VARCHAR2,
  p_body       IN VARCHAR2,
  p_body_html  IN VARCHAR2 DEFAULT NULL
);
```

**Example:**
```sql
BEGIN
  ew_email.send_to_distribution_list(
    p_list_name => 'FINANCE_TEAM',
    p_subject   => 'Monthly Close Complete',
    p_body      => 'The monthly close process has been completed.'
  );
END;
```

### manage_distribution_list

Manages distribution list members.

```sql
PROCEDURE manage_distribution_list(
  p_list_name  IN VARCHAR2,
  p_action     IN VARCHAR2, -- ADD, REMOVE, REPLACE
  p_email      IN VARCHAR2
);
```

**Example:**
```sql
-- Add member to list
ew_email.manage_distribution_list(
  p_list_name => 'APPROVERS',
  p_action    => 'ADD',
  p_email     => 'newapprover@company.com'
);

-- Remove member
ew_email.manage_distribution_list(
  p_list_name => 'APPROVERS',
  p_action    => 'REMOVE',
  p_email     => 'oldapprover@company.com'
);
```

## Email Templates

### Creating HTML Email Content

```sql
FUNCTION generate_html_table(
  p_query IN VARCHAR2
) RETURN CLOB;
```

**Example:**
```sql
DECLARE
  l_html_body CLOB;
BEGIN
  -- Generate HTML table from query
  l_html_body := '<html><body><h2>Request Summary</h2>';
  l_html_body := l_html_body || ew_email.generate_html_table(
    p_query => 'SELECT request_id, request_name, status ' ||
               'FROM requests WHERE created_date > SYSDATE - 7'
  );
  l_html_body := l_html_body || '</body></html>';
  
  -- Send HTML email
  ew_email.send_email(
    p_to        => 'manager@company.com',
    p_subject   => 'Weekly Request Summary',
    p_body      => 'See HTML version',
    p_body_html => l_html_body
  );
END;
```

### Common Email Templates

#### Approval Notification

```sql
PROCEDURE send_approval_notification(
  p_request_id IN NUMBER
) IS
  l_html CLOB;
BEGIN
  l_html := '
    <html>
    <head>
      <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: #4CAF50; color: white; padding: 10px; }
        .content { padding: 20px; }
        .button { background-color: #4CAF50; color: white; 
                  padding: 10px 20px; text-decoration: none; }
      </style>
    </head>
    <body>
      <div class="header">
        <h2>Approval Required</h2>
      </div>
      <div class="content">
        <p>Request #' || p_request_id || ' requires your approval.</p>
        <p><a href="http://epmware/approve?id=' || p_request_id || '" 
              class="button">Review Request</a></p>
      </div>
    </body>
    </html>';
  
  ew_email.send_email(
    p_to        => get_approvers(p_request_id),
    p_subject   => 'Action Required: Request #' || p_request_id,
    p_body      => 'Request requires approval',
    p_body_html => l_html
  );
END;
```

#### Error Notification

```sql
PROCEDURE send_error_notification(
  p_process_name IN VARCHAR2,
  p_error_msg    IN VARCHAR2
) IS
BEGIN
  ew_email.send_email(
    p_to      => 'support@company.com',
    p_subject => 'ERROR: ' || p_process_name || ' Failed',
    p_body    => 'Process: ' || p_process_name || CHR(10) ||
                 'Error: ' || p_error_msg || CHR(10) ||
                 'Time: ' || TO_CHAR(SYSDATE, 'DD-MON-YYYY HH24:MI:SS') || CHR(10) ||
                 'User: ' || USER,
    p_priority => 'HIGH'
  );
END;
```

## Advanced Features

### Bulk Email Operations

```sql
DECLARE
  TYPE t_recipient_list IS TABLE OF VARCHAR2(255);
  l_recipients t_recipient_list;
  l_personalized_body VARCHAR2(4000);
BEGIN
  -- Get recipient list
  SELECT email
    BULK COLLECT INTO l_recipients
    FROM users
   WHERE department = 'FINANCE';
  
  -- Send personalized emails
  FOR i IN 1..l_recipients.COUNT LOOP
    l_personalized_body := 'Dear ' || get_user_name(l_recipients(i)) || ',' ||
                          CHR(10) || CHR(10) || 'Your report is ready...';
    
    ew_email.queue_email(
      p_to      => l_recipients(i),
      p_subject => 'Personal Report Ready',
      p_body    => l_personalized_body
    );
  END LOOP;
  
  -- Process queue
  ew_email.process_email_queue();
END;
```

### Email with Multiple Attachments

```sql
DECLARE
  l_attachments VARCHAR2(4000);
BEGIN
  -- Build attachment list (semicolon separated)
  l_attachments := '/reports/summary.pdf;/reports/details.xlsx;/reports/chart.png';
  
  ew_email.send_email(
    p_to         => 'executive@company.com',
    p_subject    => 'Monthly Report Package',
    p_body       => 'Please find attached the monthly reports.',
    p_attachment => l_attachments
  );
END;
```

### Conditional Email Sending

```sql
DECLARE
  l_threshold NUMBER := 100;
  l_error_count NUMBER;
BEGIN
  -- Check condition
  SELECT COUNT(*)
    INTO l_error_count
    FROM error_log
   WHERE error_date > SYSDATE - 1;
  
  -- Send alert if threshold exceeded
  IF l_error_count > l_threshold THEN
    ew_email.send_email(
      p_to      => 'alerts@company.com',
      p_subject => 'ALERT: Error Threshold Exceeded',
      p_body    => 'Error count in last 24 hours: ' || l_error_count ||
                   ' (Threshold: ' || l_threshold || ')',
      p_priority => 'HIGH'
    );
  END IF;
END;
```

## Email Configuration

### Setting Email Server Parameters

```sql
-- Configure SMTP settings
BEGIN
  ew_email.configure_smtp(
    p_host     => 'smtp.company.com',
    p_port     => 25,
    p_username => 'epmware@company.com',
    p_password => 'encrypted_password',
    p_use_ssl  => 'N'
  );
END;
```

### Default Settings

```sql
-- Set default sender
ew_email.set_default_sender('noreply@company.com');

-- Set default footer
ew_email.set_default_footer(
  'This is an automated message from EPMware. Do not reply.'
);
```

## Error Handling

### Email Validation

```sql
FUNCTION validate_email(p_email VARCHAR2) RETURN VARCHAR2 IS
BEGIN
  IF REGEXP_LIKE(p_email, 
     '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') THEN
    RETURN 'Y';
  ELSE
    RETURN 'N';
  END IF;
END;

-- Usage
IF validate_email('user@company.com') = 'Y' THEN
  ew_email.send_email(...);
END IF;
```

### Handling Send Failures

```sql
BEGIN
  ew_email.send_email(
    p_to      => 'user@company.com',
    p_subject => 'Test',
    p_body    => 'Test message'
  );
EXCEPTION
  WHEN ew_email.smtp_error THEN
    -- Log error and queue for retry
    log_email_error(SQLERRM);
    queue_for_retry();
  WHEN OTHERS THEN
    log_error('Unexpected email error: ' || SQLERRM);
END;
```

## Best Practices

1. **Validate Email Addresses**
   ```sql
   IF ew_email.validate_email_address(p_email) = 'Y' THEN
     ew_email.send_email(...);
   END IF;
   ```

2. **Use Templates for Consistency**
   ```sql
   ew_email.send_template_email(
     p_template_name => 'STANDARD_NOTIFICATION',
     p_to            => l_recipient
   );
   ```

3. **Handle Large Recipient Lists**
   ```sql
   -- Use BCC for large distributions
   ew_email.send_email(
     p_to  => 'notifications@company.com',
     p_bcc => l_large_recipient_list
   );
   ```

4. **Include Context in Subjects**
   ```sql
   p_subject => '[' || l_env || '] Process Complete - ' || 
                TO_CHAR(SYSDATE, 'DD-MON')
   ```

5. **Queue Non-Critical Emails**
   ```sql
   -- Queue to avoid blocking process
   l_queue_id := ew_email.queue_email(...);
   ```

## Performance Considerations

- Email sending is synchronous by default
- Use queuing for bulk operations
- Consider attachment size limits
- Implement retry logic for failures

## Common Issues

### SMTP Connection Errors
- Verify SMTP server settings
- Check firewall rules
- Confirm authentication credentials

### Invalid Recipients
- Validate email format
- Check for typos
- Verify distribution lists

### Attachment Issues
- Ensure file exists and is readable
- Check file size limits
- Verify file path accessibility

## Next Steps

- [Request APIs](request.md)
- [Workflow APIs](workflow.md)
- [String APIs](string.md)