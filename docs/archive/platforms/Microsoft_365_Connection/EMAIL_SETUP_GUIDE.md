# Office 365 Email Integration Setup Guide

## 📧 Email Configuration for InHouse Print System

This guide explains how to set up and test Office 365 email integration for automated notifications in the InHouse Print Management System.

---

## 🔑 What You Need

1. **Office 365 Email Account**
   - Email address (e.g., `noreply@inhouseprint.com.au` or `info@inhouseprint.com.au`)
   - Password or App Password

2. **Email Credentials**
   - Username: Your Office 365 email address
   - Password: Account password OR App Password (recommended if MFA enabled)

3. **Network Access**
   - Outbound connection to `smtp.office365.com:587` (TLS/STARTTLS)

---

## 📋 Step 1: Add Email Configuration

### Option A: Add to `database-config.json` (Recommended)

Open `c:\Users\gpoli\GIT\In_House_SQL\config\database-config.json` and add this section:

```json
{
  "DatabaseConnections": { ... },
  "AI": { ... },
  "ExternalAPIs": {
    "Xero": { ... },
    "Shopify": { ... },
    "Email": {
      "Office365": {
        "SmtpServer": "smtp.office365.com",
        "SmtpPort": 587,
        "Username": "YOUR_EMAIL@domain.com",
        "Password": "YOUR_PASSWORD_OR_APP_PASSWORD",
        "FromAddress": "YOUR_EMAIL@domain.com",
        "UseSsl": true,
        "EnableNotifications": true
      }
    }
  }
}
```

**Replace:**
- `YOUR_EMAIL@domain.com` - Your Office 365 email address
- `YOUR_PASSWORD_OR_APP_PASSWORD` - Your password or App Password

### Option B: Use Environment Variables

Set these environment variables in PowerShell:

```powershell
# Temporary (current session only)
$env:OFFICE365_EMAIL = "your-email@domain.com"
$env:OFFICE365_PASSWORD = "your-password"

# Permanent (all sessions)
[System.Environment]::SetEnvironmentVariable('OFFICE365_EMAIL', 'your-email@domain.com', 'User')
[System.Environment]::SetEnvironmentVariable('OFFICE365_PASSWORD', 'your-password', 'User')
```

---

## 🧪 Step 2: Test Email Integration

### Run the Test Script

```powershell
# Navigate to Microsoft 365 Connection folder
cd c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Microsoft_365_Connection

# Activate virtual environment
& c:/Users/gpoli/GIT/In_House_SQL/.venv/Scripts/Activate.ps1

# Run test script
python test_email_integration.py
```

### Interactive Test Flow

The script will:

1. **Load credentials** from config or prompt you to enter them
2. **Test SMTP connection** to Office 365
3. **Send test email** with formatted HTML
4. **Send job completion notification** (sample)
5. **Display test results** (PASS/FAIL for each test)

### Expected Output

```
======================================================================
OFFICE 365 EMAIL INTEGRATION TEST SUITE
InHouse Print Management System
======================================================================

Test Email: your-test-email@domain.com
From Email: noreply@inhouseprint.com.au
SMTP Server: smtp.office365.com:587

======================================================================
TEST 1: SMTP Connection to Office 365
======================================================================
✓ SMTP connection successful!

✅ TEST 1 PASSED - SMTP connection working

======================================================================
TEST 2: Send Test Email via SMTP
======================================================================
✓ Test email sent successfully!

✅ TEST 2 PASSED - Email sent to your-test-email@domain.com
   Check inbox for test message

======================================================================
TEST 3: Send Job Completion Notification
======================================================================
✓ Job completion notification sent successfully!

✅ TEST 3 PASSED - Notification sent to your-test-email@domain.com

======================================================================
TEST SUMMARY
======================================================================
✅ PASS - Smtp Connection
✅ PASS - Test Email
✅ PASS - Job Notification

Results: 3/3 tests passed

🎉 ALL TESTS PASSED - Email integration working!
======================================================================
```

---

## ❓ Troubleshooting

### Authentication Failed Error

**Error:** `SMTPAuthenticationError: (535, b'5.7.3 Authentication unsuccessful')`

**Solutions:**

1. **Enable App Passwords** (if MFA enabled):
   - Go to Office 365 account settings
   - Security → Additional security verification → App passwords
   - Create new App Password named "InHouse Print System"
   - Use this App Password instead of account password

2. **Check credentials**:
   - Verify email address is correct
   - Verify password has no typos
   - Try logging into Office 365 webmail to confirm credentials work

3. **Account requirements**:
   - Ensure Office 365 account is active
   - Confirm account has SMTP sending permissions
   - Check if account is locked or suspended

### Connection Timeout Error

**Error:** `TimeoutError` or `Connection refused`

**Solutions:**

1. **Check internet connection**:
   ```powershell
   Test-NetConnection smtp.office365.com -Port 587
   ```

2. **Firewall rules**:
   - Ensure port 587 outbound is allowed
   - Check Windows Firewall settings
   - Check corporate firewall if applicable

3. **Network proxy**:
   - If behind proxy, configure SMTP proxy settings
   - Contact IT department for proxy configuration

### SSL/TLS Error

**Error:** `ssl.SSLError` or certificate error

**Solutions:**

1. **Update Python SSL certificates**:
   ```powershell
   pip install --upgrade certifi
   ```

2. **Check system time**:
   - Ensure system clock is accurate (SSL certificates are time-sensitive)

---

## 📧 Email Templates

### Job Completion Notification

**Subject:** `Job #{job_number} Complete - InHouse Print`

**Body:**
```
Dear {client_name},

Your printing job has been completed and is ready for collection or dispatch.

Job Details:
- Job Number: {job_number}
- Description: {job_description}
- Completion Date: {completion_date}

Please contact us to arrange collection or confirm delivery details.

Thank you for your business!
```

### Invoice Notification

**Subject:** `Invoice #{invoice_number} - InHouse Print`

**Body:**
```
Dear {client_name},

Your invoice is ready.

Invoice Details:
- Invoice Number: {invoice_number}
- Amount: ${total_amount}
- Due Date: {due_date}

Attached is your invoice for reference.

Please contact us if you have any questions.
```

### Quote Request Confirmation

**Subject:** `Quote Request #{quote_number} Received - InHouse Print`

**Body:**
```
Dear {client_name},

We have received your quote request and will respond within 24 hours.

Quote Request Details:
- Quote Number: {quote_number}
- Description: {description}
- Requested Date: {request_date}

Thank you for choosing InHouse Print!
```

---

## 🔧 Integration with System

### Using Email in Python

```python
from G_Folder.Microsoft_365_Connection.test_email_integration import Office365EmailTester

# Initialize email sender
email_sender = Office365EmailTester()

# Send job completion notification
email_sender.send_job_completion_notification(
    to_address="client@example.com",
    job_number="12345",
    client_name="ABC Company",
    job_description="1000 x A4 Flyers on 350gsm Satin"
)
```

### Using Email in VB.NET

The existing VB.NET system has email functionality in:
- `DAL/SendEmail.vb` - Email sending class
- Uses Office 365 SMTP settings

**Example:**
```vb
Dim emailSender As New SendEmail()
emailSender.SendJobCompletionNotification(
    toAddress:="client@example.com",
    jobNumber:="12345",
    clientName:="ABC Company"
)
```

---

## 🎯 Next Steps After Testing

1. **✅ Test email integration** (this guide)
2. **Add automated notifications** for:
   - Job completion
   - Invoice generation
   - Quote requests
   - Order confirmations
   - Shipping notifications
3. **Create email templates** for each notification type
4. **Integrate with workflow** in VB.NET job management system
5. **Monitor email logs** for delivery success/failures

---

## 📞 Support

If you encounter issues:

1. **Check test results** - Run `test_email_integration.py`
2. **Review error messages** - Check console output for specific errors
3. **Verify credentials** - Ensure Office 365 login works in webmail
4. **Check network** - Ensure SMTP port 587 is accessible
5. **Enable App Passwords** - Required if MFA is enabled on account

---

## 📚 Additional Resources

- [Office 365 SMTP Settings](https://learn.microsoft.com/en-us/exchange/mail-flow-best-practices/how-to-set-up-a-multifunction-device-or-application-to-send-email-using-microsoft-365-or-office-365)
- [App Passwords Setup](https://support.microsoft.com/en-us/account-billing/manage-app-passwords-for-two-step-verification-d6dc8c6d-4bf7-4851-ad95-6d07799387e9)
- [Python SMTP Documentation](https://docs.python.org/3/library/smtplib.html)

---

**Document Version:** 1.0  
**Last Updated:** October 20, 2025  
**Author:** InHouse Print Development Team
