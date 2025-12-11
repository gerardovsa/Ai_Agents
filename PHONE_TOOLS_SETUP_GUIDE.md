# Phone Communication Tools - Setup Guide

## 📋 Overview

The phone communication tools enable AI agents to send coaching documents and alerts via:
- **Email (SMTP)** - Professional HTML emails with coaching content
- **SMS (Twilio)** - Urgent text alerts for high-priority situations

## 🚀 Quick Start

### Prerequisites
```bash
# Install Twilio SDK (optional - email works without it)
pip install twilio
```

### Step 1: Configure Email (Gmail)

#### A. Enable App Password
1. Go to Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification**
3. Scroll down to **App passwords**
4. Click **App passwords** and sign in
5. Select:
   - **App**: Mail
   - **Device**: Other (custom name: "VSA Platform")
6. Click **Generate**
7. **Copy the 16-character password** (format: xxxx xxxx xxxx xxxx)

#### B. Set Environment Variables

**Option 1: Windows PowerShell (Current Session)**
```powershell
$env:SMTP_SERVER = "smtp.gmail.com"
$env:SMTP_PORT = "587"
$env:SMTP_USER = "your_email@gmail.com"
$env:SMTP_PASSWORD = "xxxx xxxx xxxx xxxx"  # App password from step A
$env:SMTP_FROM_EMAIL = "vsa-coaching@vetclinic.com"  # Optional
```

**Option 2: Windows PowerShell (Permanent - System)**
```powershell
[System.Environment]::SetEnvironmentVariable('SMTP_USER', 'your_email@gmail.com', 'User')
[System.Environment]::SetEnvironmentVariable('SMTP_PASSWORD', 'xxxx xxxx xxxx xxxx', 'User')
[System.Environment]::SetEnvironmentVariable('SMTP_SERVER', 'smtp.gmail.com', 'User')
[System.Environment]::SetEnvironmentVariable('SMTP_PORT', '587', 'User')
```

**Option 3: .env File (Development)**
```bash
# Create .env in project root
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=vsa-coaching@vetclinic.com
```

**Option 4: supabase_config.py (Production)**
```python
# Add to tools/implementations/supabase_config.py
SMTP_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'smtp_user': 'your_email@gmail.com',
    'smtp_password': 'xxxx xxxx xxxx xxxx',
    'from_email': 'vsa-coaching@vetclinic.com'
}
```

### Step 2: Configure SMS (Twilio)

#### A. Get Twilio Credentials
1. Sign up: https://www.twilio.com/try-twilio (free $15.50 credit)
2. Go to Console: https://www.twilio.com/console
3. Copy **Account SID** (format: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)
4. Copy **Auth Token** (click "Show" to reveal)
5. Get phone number: https://www.twilio.com/console/phone-numbers
   - Click **Get a Trial Number** (or buy one)
   - Copy number in E.164 format: +15551234567

#### B. Set Environment Variables

**Option 1: Windows PowerShell (Current Session)**
```powershell
$env:TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
$env:TWILIO_AUTH_TOKEN = "your_auth_token_here"
$env:TWILIO_FROM_PHONE = "+15551234567"
```

**Option 2: Windows PowerShell (Permanent)**
```powershell
[System.Environment]::SetEnvironmentVariable('TWILIO_ACCOUNT_SID', 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'User')
[System.Environment]::SetEnvironmentVariable('TWILIO_AUTH_TOKEN', 'your_auth_token_here', 'User')
[System.Environment]::SetEnvironmentVariable('TWILIO_FROM_PHONE', '+15551234567', 'User')
```

**Option 3: .env File**
```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_PHONE=+15551234567
```

### Step 3: Test Email Sending

```python
# Test email (sends to yourself)
from tools.implementations.phone_communication_tools import send_email_veterinary_coaching

result = send_email_veterinary_coaching(
    call_id='TEST_CALL_001',  # Replace with real call ID that has coaching
    to_email='your_email@gmail.com',  # Your test email
    subject='TEST: AI Coaching Document',
    custom_message='This is a test email from the VSA phone tools setup.'
)

print(result)
# Expected: {'success': True, 'message': 'Email sent successfully...', 'sent_at': '2025-12-11T...'}
```

### Step 4: Test SMS Sending

```python
# Test SMS (sends to your phone)
from tools.implementations.phone_communication_tools import send_sms_veterinary_alert

result = send_sms_veterinary_alert(
    call_id='TEST_CALL_001',
    to_phone='+15551234567',  # Your phone number
    message_text='TEST: VSA alert system is now operational!',
    alert_type='SYSTEM_TEST'
)

print(result)
# Expected: {'success': True, 'message': 'SMS sent successfully...', 'sms_sid': 'SM...', 'sent_at': '2025-12-11T...'}
```

## 🔧 Troubleshooting

### Email Issues

#### "SMTP authentication failed"
- **Cause**: Wrong password or not using App Password
- **Solution**: 
  1. Verify you're using App Password (NOT regular Gmail password)
  2. Regenerate App Password if needed
  3. Remove spaces from App Password when setting env var

#### "Connection refused" or "Timeout"
- **Cause**: Firewall blocking port 587
- **Solution**: 
  1. Check firewall settings
  2. Try port 465 (SSL) instead: `SMTP_PORT=465`
  3. Test with: `telnet smtp.gmail.com 587`

#### "Emails going to spam"
- **Cause**: Missing SPF/DKIM records or suspicious content
- **Solution**:
  1. Ask recipients to mark as "Not Spam"
  2. Use professional from_email address
  3. Avoid spam trigger words in subject

#### "Daily sending limit exceeded"
- **Cause**: Gmail limits (500/day for personal, 2000/day for Workspace)
- **Solution**:
  1. Wait 24 hours for reset
  2. Upgrade to Google Workspace
  3. Use dedicated email service (SendGrid, Amazon SES)

### SMS Issues

#### "Twilio SDK not installed"
- **Solution**: `pip install twilio`

#### "Unable to create record: Invalid phone number"
- **Cause**: Phone number not in E.164 format
- **Solution**: Use +1234567890 format (+ country code + number)

#### "Twilio authentication failed"
- **Cause**: Wrong Account SID or Auth Token
- **Solution**:
  1. Verify credentials at https://www.twilio.com/console
  2. Check for extra spaces in env vars
  3. Regenerate Auth Token if needed

#### "Free trial account restrictions"
- **Cause**: Trial accounts can only send to verified numbers
- **Solution**:
  1. Verify recipient phones at: https://www.twilio.com/console/phone-numbers/verified
  2. Or upgrade to paid account ($20 minimum)

#### "SMS not received"
- **Cause**: Carrier filtering or wrong number
- **Solution**:
  1. Check Twilio logs: https://www.twilio.com/console/sms/logs
  2. Verify phone number is correct
  3. Try different phone/carrier

## 📊 Usage Examples

### Example 1: Send Coaching After AI Generation
```python
# After generating coaching for a call
result = send_email_veterinary_coaching(
    call_id='ABC123',
    to_email='drsmith@vetclinic.com',
    subject='AI Coaching Review - Call with Mrs. Johnson',
    custom_message='''Hi Dr. Smith,

Great job on today's call with Mrs. Johnson! I've included the AI-generated 
coaching document below with some suggestions for improving client communication.

Please review and let's discuss during our next 1-on-1.

Thanks,
Manager''',
    include_transcript=False  # Set True if you want full transcript
)
```

### Example 2: Send Urgent Alert via SMS
```python
# For high-priority alerts requiring immediate attention
result = send_sms_veterinary_alert(
    call_id='DEF456',
    to_phone='+15551234567',
    message_text='''🚨 URGENT ALERT - Call DEF456

Client expressed dissatisfaction with wait time and threatened to leave practice.

ACTION REQUIRED: Follow up with Mrs. Brown TODAY to resolve.

View details: [Dashboard Link]''',
    alert_type='CLIENT_EXPERIENCE'
)
```

### Example 3: Batch Send Daily Coaching
```python
# Send coaching to entire team at end of day
from tools.implementations.phone_communication_tools import send_bulk_coaching_emails

result = send_bulk_coaching_emails(
    call_ids=['ABC123', 'DEF456', 'GHI789'],
    to_emails=[
        'drsmith@vetclinic.com',
        'techjones@vetclinic.com',
        'receptionistlee@vetclinic.com'
    ],
    subject_template='Daily Coaching Review - Call {call_id}',
    custom_message='''Team,

Excellent work today! Please review your personalized coaching documents below 
to continue improving our client experience.

Keep up the great work!
- Manager'''
)

print(f"Sent: {result['sent_count']}, Failed: {result['failed_count']}")
for detail in result['details']:
    print(f"{detail['call_id']} → {detail['email']}: {detail['status']}")
```

## 🛡️ Security Best Practices

### Email Security
- ✅ **Always use App Passwords** (never regular Gmail password)
- ✅ **Store credentials in environment variables** (never hardcode)
- ✅ **Use TLS encryption** (port 587 with STARTTLS)
- ✅ **Rotate passwords regularly** (every 90 days)
- ❌ **Never commit credentials to Git**
- ❌ **Never share App Passwords**

### SMS Security
- ✅ **Protect Twilio Auth Token** (treat like password)
- ✅ **Use environment variables** (never hardcode)
- ✅ **Monitor usage/costs** (set up billing alerts)
- ✅ **Verify phone numbers** (before sending)
- ❌ **Never expose credentials in logs**
- ❌ **Never send sensitive patient data via SMS**

### Database Logging
- All email/SMS sends are logged to `call_manager_alerts.manager_alert_notes`
- Logs include: timestamp, recipient, message type
- SMS logs include Twilio SID for tracking
- Check logs for audit trail: `SELECT manager_alert_notes FROM call_manager_alerts WHERE call_id='ABC123'`

## 💰 Cost Analysis

### Email (SMTP/Gmail)
- **Cost per email**: $0 (free with Gmail account)
- **Sending limits**: 
  - Personal Gmail: 500 emails/day
  - Google Workspace: 2,000 emails/day
- **Infrastructure**: No additional servers needed

### SMS (Twilio)
- **Cost per SMS**: $0.0075 - $0.01 USD (US numbers)
- **Free trial**: $15.50 credit (~1,500-2,000 messages)
- **Segments**: Messages >160 chars use multiple segments (e.g., 320 chars = 2×$0.0075 = $0.015)
- **International**: Higher rates (varies by country)

**Monthly Cost Example** (100 staff, daily coaching):
- Email: $0 (free)
- SMS (10 urgent alerts/day): 10 × 30 days × $0.0075 = $2.25/month

## 📚 API Reference

### send_email_veterinary_coaching()
```python
def send_email_veterinary_coaching(
    call_id: str,              # Required: Call ID with coaching
    to_email: str,             # Required: Recipient email
    subject: str = "AI Coaching Document - Call Review",
    custom_message: str = None,  # Optional: Manager's note
    include_transcript: bool = False,  # Optional: Include full transcript
    smtp_config: dict = None   # Optional: Override env vars
) -> dict:
    """
    Returns:
        {
            'success': bool,
            'message': str,
            'sent_at': str,  # ISO timestamp
            'error': str     # If success=False
        }
    """
```

### send_sms_veterinary_alert()
```python
def send_sms_veterinary_alert(
    call_id: str,              # Required: Call ID
    to_phone: str,             # Required: Phone in E.164 format
    message_text: str,         # Required: SMS content (max 1600 chars)
    alert_type: str = None,    # Optional: Alert category
    twilio_config: dict = None # Optional: Override env vars
) -> dict:
    """
    Returns:
        {
            'success': bool,
            'message': str,
            'sms_sid': str,  # Twilio message ID
            'sent_at': str,  # ISO timestamp
            'error': str     # If success=False
        }
    """
```

### send_bulk_coaching_emails()
```python
def send_bulk_coaching_emails(
    call_ids: List[str],       # Required: List of call IDs
    to_emails: List[str],      # Required: List of emails (same length)
    subject_template: str = "AI Coaching Document - Call {call_id}",
    custom_message: str = None,  # Optional: Same message for all
    smtp_config: dict = None   # Optional: Override env vars
) -> dict:
    """
    Returns:
        {
            'success': bool,   # True only if ALL succeeded
            'message': str,
            'sent_count': int,
            'failed_count': int,
            'details': [
                {'call_id': str, 'email': str, 'status': str, 'error': str},
                ...
            ]
        }
    """
```

## 🔗 Related Files

- **Implementation**: `tools/implementations/phone_communication_tools.py`
- **Schemas**: `tools/schemas/phone_communication_tools.json`
- **Config**: `tools/implementations/supabase_config.py`
- **Gap Analysis**: `VSA_PLATFORM_GAP_ANALYSIS.md`
- **Database Connector**: `tools/implementations/unified_database_connector.py`

## 📞 Support

### Email Issues
- Gmail Help: https://support.google.com/accounts/answer/185833
- App Passwords: https://support.google.com/accounts/answer/185833

### SMS Issues
- Twilio Docs: https://www.twilio.com/docs/sms
- Twilio Console: https://www.twilio.com/console
- Twilio Support: https://support.twilio.com

### Database Issues
- Check Supabase connection: `VSADatabaseConnector().test_connection()`
- Verify table schema: `SELECT * FROM call_manager_alerts LIMIT 1`

## ✅ Setup Checklist

### Email Setup
- [ ] Google Account has 2-Step Verification enabled
- [ ] App Password generated for "VSA Platform"
- [ ] Environment variables set (SMTP_USER, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT)
- [ ] Test email sent successfully to your own address
- [ ] Emails arriving (check spam folder)

### SMS Setup
- [ ] Twilio account created (free trial or paid)
- [ ] Account SID and Auth Token copied
- [ ] Twilio phone number acquired
- [ ] Environment variables set (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE)
- [ ] Twilio SDK installed (`pip install twilio`)
- [ ] Test SMS sent successfully to your own phone
- [ ] SMS received (check carrier filtering)

### Database Setup
- [ ] Supabase connection working
- [ ] `call_manager_alerts` table accessible
- [ ] `veterinary_calls` table accessible
- [ ] `manager_alert_notes` column exists
- [ ] Test call ID with coaching document available

### AI Agent Registration
- [ ] `phone_communication_tools.json` schema created
- [ ] Tools registered in AI agent discovery system
- [ ] AI can find and execute phone tools
- [ ] Test AI-initiated email send
- [ ] Test AI-initiated SMS send

---

**Setup Complete!** 🎉

Your phone communication tools are ready. The AI agent can now:
- Send coaching documents via email
- Send urgent alerts via SMS
- Batch process multiple sends
- Log all communications to database

Next steps: See `VSA_PLATFORM_GAP_ANALYSIS.md` for Phase 2 (Follow-up System) and Phase 3 (Analytics Tools).
