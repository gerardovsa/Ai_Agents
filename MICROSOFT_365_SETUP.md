# Microsoft 365 Test Account Setup

## 📧 Test Account Credentials

**Email**: gerardo@minivetguide.onmicrosoft.com  
**Password**: Vetsuccess11!  
**Organization**: minivetguide  
**Domain**: minivetguide.onmicrosoft.com  

---

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```powershell
# 1. Ensure Flask is running
cd C:\Users\gpoli\GIT\AI_agents
BISTART

# 2. Run authentication test
python test_microsoft_auth.py
```

**What it does:**
- ✅ Checks if Flask is running
- ✅ Creates/finds user in database
- ✅ Opens browser for Microsoft OAuth
- ✅ Stores tokens in database
- ✅ Tests credentials with Graph API

---

### Option 2: Manual Setup

```powershell
# 1. Start Flask
BISTART

# 2. Open browser
Start-Process "http://localhost:5001/api/auth/microsoft/login"

# 3. Sign in with:
#    Email: gerardo@minivetguide.onmicrosoft.com
#    Password: Vetsuccess11!

# 4. Accept permissions

# 5. Verify storage
python -c "import sqlite3; conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db'); creds = conn.execute('SELECT user_id, platform, credential_key FROM user_platform_credentials WHERE platform=\"microsoft365\"').fetchall(); print('Microsoft Credentials:', creds); conn.close()"
```

---

## ✅ Verification

### Check Credentials in Database

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python check_microsoft_creds.py
```

**Expected output:**
```
Microsoft credentials: 2+
  - User X: microsoft365 (access_token)
  - User X: microsoft365 (refresh_token)
```

### Test with AI Agent

```powershell
# List Outlook emails
CHAT "Show me my Outlook inbox"

# List OneDrive files
CHAT "List files in my OneDrive"

# Create Excel file
CHAT "Create an Excel spreadsheet called 'Test Data'"

# Send Outlook email
CHAT "Send a test email via Outlook to gerardo@minivetguide.onmicrosoft.com"
```

---

## 🔧 Available Microsoft Tools

Once authenticated, AI agent can use:

### Email & Communication
- ✅ **Outlook**: Send/receive emails, manage folders
- ✅ **Teams**: Post messages, create channels, schedule meetings

### File Storage & Documents
- ✅ **OneDrive**: Upload, download, share files
- ✅ **SharePoint**: Access sites, manage documents
- ✅ **Word**: Create/edit documents, export to PDF
- ✅ **Excel**: Create workbooks, manipulate data, charts
- ✅ **OneNote**: Create notebooks, pages, sections

### Productivity
- ✅ **Calendar**: Create events, manage schedules
- ✅ **To-Do**: Create tasks, manage lists
- ✅ **Forms**: Create surveys, collect responses

**Total**: 100+ Microsoft 365 tools available

---

## 🗄️ Database Structure

```sql
-- Database: AI_infrastructure/ai_infrastructure.db
-- Table: user_platform_credentials

INSERT INTO user_platform_credentials (
    user_id,
    platform,
    credential_key,
    credential_value,
    metadata,
    created_at
) VALUES (
    <user_id>,
    'microsoft365',
    'access_token',
    '<actual_token>',
    '{"refresh_token": "...", "expires_at": "...", "microsoft_email": "gerardo@minivetguide.onmicrosoft.com"}',
    '<timestamp>'
);
```

---

## 🔐 Security Notes

⚠️ **Important:**
- Credentials stored in `test_credentials_m365.txt`
- File is in `.gitignore` - will NOT be committed to GitHub
- For development/testing only
- OAuth tokens stored securely in SQLite database
- Tokens auto-refresh using refresh_token

---

## 🧪 Testing Checklist

After setup, verify:

- [ ] Flask server running (port 5001)
- [ ] User exists in database
- [ ] Microsoft OAuth tokens stored
- [ ] Access token works with Graph API
- [ ] CHAT command can use Microsoft tools
- [ ] AI agent can send Outlook email
- [ ] AI agent can list OneDrive files
- [ ] AI agent can access Calendar events

---

## 📊 Integration Status

| Platform | Email | Status | Tools Available |
|----------|-------|--------|-----------------|
| **Google** | gerardo@vetsuccessacademy.com | ✅ ACTIVE | 29 Gmail + 50+ Workspace tools |
| **Microsoft** | gerardo@minivetguide.onmicrosoft.com | ⏳ PENDING AUTH | 100+ M365 tools |

**Once both authenticated**: AI agent has access to **564 tools across 29 platforms!**

---

## 🆘 Troubleshooting

### Issue: "Flask server not running"
```powershell
cd C:\Users\gpoli\GIT\AI_agents
BISTART
# Wait 15 seconds for initialization
```

### Issue: "User not found"
The test script will automatically create the user if not found.

### Issue: "OAuth callback failed"
1. Check redirect URI in Azure AD: `http://localhost:5001/api/auth/microsoft/callback`
2. Ensure all API permissions granted (admin consent)
3. Check MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET in .env.master

### Issue: "Access token expired"
Tokens auto-refresh using refresh_token. If refresh fails, re-authenticate:
```powershell
Start-Process "http://localhost:5001/api/auth/microsoft/login"
```

---

## 📞 Next Steps

1. ✅ Run `python test_microsoft_auth.py`
2. ✅ Complete OAuth flow in browser
3. ✅ Verify credentials stored
4. ✅ Test with CHAT command
5. ✅ Enjoy 564 AI agent tools! 🎉

---

**Created**: October 29, 2025  
**Status**: Ready for testing  
**Account**: Test/Development  
