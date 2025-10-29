# Gmail Sending Account Configuration

**Date:** October 27, 2025  
**Question:** Which email account is Gmail sending from?

---

## 📧 **Answer: Service Account Email**

The Gmail implementation is currently configured to send emails from:

### **Primary Sending Account**
```
vet-success-academy@appspot.gserviceaccount.com
```

**Account Type:** Google Service Account  
**Project:** colab-ai-processor  
**Configuration File:** `.env.master` (line 30)

---

## 🔧 **How It Works**

### 1. Authentication Flow

**File:** `tools/implementations/google_auth_helper.py`

```python
def get_service_account_credentials(scopes):
    # Gets credentials from environment variables
    service_account_email = os.getenv('SERVICE_ACCOUNT_EMAIL')
    # Returns: vet-success-academy@appspot.gserviceaccount.com
```

### 2. Gmail Service Builder

```python
def build_gmail_service():
    scopes = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    credentials = get_service_account_credentials(scopes)
    service = build('gmail', 'v1', credentials=credentials)
    return service
```

### 3. Email Sending

**File:** `tools/implementations/gmail.py`

```python
def gmail_send_email(to, subject, body, cc=None, bcc=None, attachments=None):
    service = _get_gmail_service()  # Uses service account
    
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    # No 'from' field specified = uses service account email
```

---

## ⚠️ **IMPORTANT: Service Account Limitations**

### **Problem:**
Service accounts **CANNOT directly send Gmail** on behalf of users without domain-wide delegation!

**Why:**
- Service accounts are **machine accounts**, not user accounts
- Gmail API requires **domain-wide delegation** to impersonate users
- Without delegation, emails will appear to come from the service account itself (which may not be deliverable)

### **What Happens When You Try to Send:**
```
❌ Error: "Precondition check failed"
OR
❌ Error: "Delegation denied"
OR
✅ Email sent but from: vet-success-academy@appspot.gserviceaccount.com
```

---

## ✅ **Solution Options**

### **Option 1: Use OAuth2 for User Email (Recommended)**

Send emails from actual user accounts like:
- `gpoli1982@gmail.com` (your personal Gmail)
- `gerardo@vetsuccessacademy.com` (work email)
- `gerardo@minivetguide.com` (MiniVet Guide)

**How to implement:**

1. **Update `google_auth_helper.py`** to support OAuth2:
```python
def build_gmail_service_with_user(user_email):
    """Use OAuth2 to send from actual user account"""
    # Use OAuth2 flow instead of service account
    # Requires user consent
```

2. **Add OAuth2 credentials** from Google Cloud Console:
```bash
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
```

### **Option 2: Domain-Wide Delegation (For G Suite)**

If you have a G Suite/Google Workspace domain:

1. **Enable domain-wide delegation** for service account
2. **Grant Gmail scopes** in Admin Console
3. **Specify user to impersonate:**

```python
def build_gmail_service_as_user(user_email):
    credentials = get_service_account_credentials(scopes)
    delegated_credentials = credentials.with_subject(user_email)
    service = build('gmail', 'v1', credentials=delegated_credentials)
    return service
```

**Usage:**
```python
# Send from Gerardo's email
service = build_gmail_service_as_user('gerardo@vetsuccessacademy.com')
gmail_send_email(
    to='client@example.com',
    subject='Test',
    body='Sent from Gerardo!'
)
```

### **Option 3: SMTP (Simple Alternative)**

Use standard SMTP with app passwords:

```python
import smtplib
from email.mime.text import MIMEText

def send_email_smtp(from_email, from_password, to, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email, from_password)
        smtp.send_message(msg)
```

**Available accounts from `.env.master`:**
```bash
PERSONAL_EMAIL=gpoli1982@gmail.com
PERSONAL_EMAIL_APP_PASSWORD=giizbenppgnpbpf

WORK_EMAIL=gerardo@vetsuccessacademy.com
WORK_EMAIL_APP_PASSWORD=ttdbqnudgbjrcgha
```

---

## 📊 **Available Email Accounts**

From `.env.master` (lines 510-528):

| Account | Email | Password/App Password | Use Case |
|---------|-------|----------------------|----------|
| **Personal** | `gpoli1982@gmail.com` | `giizbenppgnpbpf` | Personal emails |
| **Work** | `gerardo@vetsuccessacademy.com` | `ttdbqnudgbjrcgha` | Business emails |
| **MiniVet** | `gerardo@minivetguide.com` | `MiniVetGAP$` | MiniVet Guide |
| **MVG Gmail** | `minivetguide@gmail` | `minivetguide123` | Marketing |
| **MVG Marketing** | `marketing@minivetguide.com` | `MVGhiveJ25AU$` | Marketing campaigns |

---

## 🚀 **Recommended Implementation**

### **Step 1: Create SMTP-Based Gmail Function**

Add to `tools/implementations/gmail.py`:

```python
def gmail_send_email_smtp(from_email, to, subject, body, app_password=None):
    """
    Send email via SMTP (works with any Gmail account)
    
    Args:
        from_email: Sender email address
        to: Recipient email
        subject: Email subject
        body: Email body
        app_password: Gmail app password (reads from env if not provided)
    """
    import smtplib
    from email.mime.text import MIMEText
    
    # Get app password from environment if not provided
    if not app_password:
        if from_email == os.getenv('PERSONAL_EMAIL'):
            app_password = os.getenv('PERSONAL_EMAIL_APP_PASSWORD')
        elif from_email == os.getenv('WORK_EMAIL'):
            app_password = os.getenv('WORK_EMAIL_APP_PASSWORD')
        else:
            raise ValueError(f"No app password found for {from_email}")
    
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.send_message(msg)
        
        return {
            'success': True,
            'from': from_email,
            'to': to,
            'subject': subject
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }
```

### **Step 2: Add Tool Schema**

Add to `tools/schemas/gmail_tools.json`:

```json
{
  "name": "gmail_send_email_smtp",
  "description": "Send email via SMTP from specific Gmail account",
  "platform": "gmail",
  "parameters": {
    "from_email": {
      "type": "string",
      "description": "Sender email (gpoli1982@gmail.com or gerardo@vetsuccessacademy.com)",
      "required": true
    },
    "to": {
      "type": "string",
      "description": "Recipient email",
      "required": true
    },
    "subject": {
      "type": "string",
      "description": "Email subject",
      "required": true
    },
    "body": {
      "type": "string",
      "description": "Email body",
      "required": true
    }
  }
}
```

### **Step 3: Test It**

```python
from tools import ToolRegistry

registry = ToolRegistry()

# Send from personal Gmail
result = registry.execute_tool(
    'gmail_send_email_smtp',
    from_email='gpoli1982@gmail.com',
    to='test@example.com',
    subject='Test from Personal',
    body='This is sent from my personal Gmail!'
)

# Send from work email
result = registry.execute_tool(
    'gmail_send_email_smtp',
    from_email='gerardo@vetsuccessacademy.com',
    to='test@example.com',
    subject='Test from Work',
    body='This is sent from work email!'
)
```

---

## 🔐 **Security Notes**

### **Current Configuration**
- ✅ Service account private keys stored in `.env.master`
- ✅ App passwords stored in `.env.master`
- ⚠️ File not in Git (confirmed via `.gitignore`)

### **Best Practices**
1. **Never commit** `.env.master` to Git
2. **Use app passwords** instead of real passwords
3. **Rotate keys** every 90 days
4. **Limit scopes** to what you actually need

---

## 📝 **Summary**

**Current Setup:**
- Emails sent from: `vet-success-academy@appspot.gserviceaccount.com` (service account)
- **Problem:** Service accounts can't send Gmail without delegation

**Recommended Solution:**
- Use **SMTP** with your real Gmail accounts
- Available accounts: `gpoli1982@gmail.com`, `gerardo@vetsuccessacademy.com`
- App passwords already configured in `.env.master`

**Next Steps:**
1. Implement SMTP-based `gmail_send_email_smtp()` function
2. Add tool schema for new function
3. Test sending from your actual Gmail accounts

Would you like me to implement the SMTP-based Gmail sending function?
