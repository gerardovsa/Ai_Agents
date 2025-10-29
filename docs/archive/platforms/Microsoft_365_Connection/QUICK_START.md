# 📧 Office 365 Email Integration - Quick Start

## ✅ What You Have

You now have a **complete Office 365 email integration** system ready to test!

---

## 🚀 Quick Test (3 Steps)

### 1. Add Your Credentials

**Option A:** Update `config/database-config.json` (Recommended)

Add this to the `"ExternalAPIs"` section:

```json
"Email": {
  "Office365": {
    "Username": "YOUR_EMAIL@domain.com",
    "Password": "YOUR_PASSWORD",
    "FromAddress": "YOUR_EMAIL@domain.com"
  }
}
```

**Option B:** Set Environment Variables

```powershell
$env:OFFICE365_EMAIL = "your-email@domain.com"
$env:OFFICE365_PASSWORD = "your-password"
```

### 2. Run Test Script

```powershell
cd c:\Users\gpoli\GIT\In_House_SQL\G_Folder\Microsoft_365_Connection
& c:/Users/gpoli/GIT/In_House_SQL/.venv/Scripts/Activate.ps1
python test_email_integration.py
```

### 3. Check Your Inbox

You should receive 2 test emails:
- ✅ Simple test email
- ✅ Job completion notification (sample)

---

## 📂 Files Created

| File | Purpose |
|------|---------|
| `test_email_integration.py` | Complete test suite (3 tests) |
| `email_sender.py` | Reusable email utility class |
| `EMAIL_SETUP_GUIDE.md` | Detailed setup instructions |
| `QUICK_START.md` | This file |

---

## 🎯 What Can It Do?

### Send Emails

```python
from email_sender import EmailSender

sender = EmailSender()

# Job completion notification
sender.send_job_completion_email(
    to_email="client@example.com",
    job_number="12345",
    client_name="ABC Company",
    job_description="1000 x A4 Flyers on 350gsm Satin"
)

# Invoice notification (with PDF attachment)
sender.send_invoice_email(
    to_email="client@example.com",
    invoice_number="INV-5678",
    client_name="ABC Company",
    total_amount=450.00,
    due_date="2025-11-01",
    invoice_file="path/to/invoice.pdf"
)

# Quote confirmation
sender.send_quote_confirmation_email(
    to_email="client@example.com",
    quote_number="Q-9999",
    client_name="ABC Company",
    description="Business cards with logo"
)
```

### Test SMTP Connection

```python
from test_email_integration import Office365EmailTester

tester = Office365EmailTester()
tester.set_credentials("your-email@domain.com", "your-password")
tester.test_smtp_connection()
```

---

## ⚡ Integration Examples

### In Flask Web App

```python
from G_Folder.Microsoft_365_Connection.email_sender import EmailSender

@app.route('/complete-job/<job_id>')
def complete_job(job_id):
    # Mark job complete
    job = mark_job_complete(job_id)
    
    # Send notification
    email = EmailSender()
    email.send_job_completion_email(
        to_email=job.client_email,
        job_number=job.ticket_id,
        client_name=job.client_name,
        job_description=job.description
    )
    
    return {"status": "success"}
```

### In VB.NET (Existing System)

The existing VB.NET system already has `DAL/SendEmail.vb`. You can:

1. **Keep using VB.NET SendEmail class** (already configured)
2. **Call Python script** from VB.NET for advanced templates
3. **Use both** - VB.NET for simple alerts, Python for rich HTML emails

---

## 🔧 Troubleshooting

### Authentication Failed?

1. **Enable App Passwords** in Office 365 account:
   - Settings → Security → App Passwords
   - Create new App Password for "InHouse Print"
   - Use this instead of account password

2. **Check credentials**:
   - Verify email address
   - Verify password (no typos)
   - Try logging into Office 365 webmail

### Connection Failed?

```powershell
# Test connectivity
Test-NetConnection smtp.office365.com -Port 587
```

Should return: `TcpTestSucceeded : True`

### Still Not Working?

Run the test script with debug mode:
```powershell
python test_email_integration.py
```

Check error messages and compare with troubleshooting guide in `EMAIL_SETUP_GUIDE.md`.

---

## 📧 Email Templates

All emails include:
- ✅ Professional HTML design
- ✅ Plain text fallback (for old email clients)
- ✅ Mobile-responsive layout
- ✅ InHouse Print branding
- ✅ Automated timestamps

---

## 🎉 Success Criteria

After running `test_email_integration.py`, you should see:

```
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

## 📞 What You Need from Me

To help you test, I need:

1. **Your Office 365 email address** (e.g., `info@inhouseprint.com.au`)
2. **Your Office 365 password** (or App Password if MFA enabled)
3. **Where to send test emails** (same email or different?)

Once you provide these, we can:
- ✅ Run complete test suite
- ✅ Send real test emails
- ✅ Verify inbox delivery
- ✅ Integrate with job management system

---

## 🚀 Next Steps

1. ✅ **Test email integration** (provide credentials)
2. ✅ **Integrate with job workflow** (send notifications on job completion)
3. ✅ **Add invoice notifications** (send when invoice generated)
4. ✅ **Create custom templates** (for different notification types)
5. ✅ **Monitor email logs** (track delivery success)

---

**Ready to test?** Just provide your email credentials and I'll run the test suite! 🚀

---

**Last Updated:** October 20, 2025  
**Status:** Ready for Testing ✅
