# 🔷 Microsoft 365 Email Integration Setup Guide

Complete guide to integrating Microsoft 365 Outlook email capabilities into the AI Agent Platform.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Azure AD App Registration](#azure-ad-app-registration)
3. [Environment Configuration](#environment-configuration)
4. [Testing Authentication](#testing-authentication)
5. [Using Outlook Tools](#using-outlook-tools)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

✅ **What you need:**
- Microsoft 365 account (personal or work/school)
- Azure account (free tier works fine)
- AI Agent Platform running (BISTART command)
- Access to Azure Portal: https://portal.azure.com

---

## Azure AD App Registration

### Step 1: Create Azure AD Application

1. **Navigate to Azure Portal:**
   - Go to https://portal.azure.com
   - Sign in with your Microsoft account

2. **Register New Application:**
   - Search for "Azure Active Directory" in top search bar
   - Click **App registrations** in left sidebar
   - Click **+ New registration**

3. **Configure Application:**
   ```
   Name: AI Agent Platform Email
   Supported account types: Accounts in any organizational directory and personal Microsoft accounts
   Redirect URI: 
     - Platform: Web
     - URI: http://localhost:4000/api/auth/microsoft/callback
   ```

4. **Click "Register"**

### Step 2: Configure API Permissions

1. **Add Microsoft Graph Permissions:**
   - In your app, go to **API permissions** (left sidebar)
   - Click **+ Add a permission**
   - Select **Microsoft Graph**
   - Choose **Delegated permissions**
   
2. **Add these scopes:**
   ```
   ✅ User.Read (read user profile)
   ✅ Mail.Read (read emails)
   ✅ Mail.Send (send emails)
   ✅ Mail.ReadWrite (full email access)
   ✅ MailboxSettings.ReadWrite (manage mailbox settings)
   ```

3. **Grant Admin Consent:**
   - Click **✓ Grant admin consent for [Your Organization]**
   - Confirm the consent

### Step 3: Create Client Secret

1. **Generate Secret:**
   - Go to **Certificates & secrets** (left sidebar)
   - Click **+ New client secret**
   - Description: `AI Agent Email Access`
   - Expires: Choose duration (recommend: 24 months)
   - Click **Add**

2. **⚠️ IMPORTANT - Copy Secret Value:**
   ```
   The secret VALUE will only be shown ONCE!
   Copy it immediately and save it securely.
   ```

### Step 4: Get Client ID

1. **Find Application (client) ID:**
   - Go to **Overview** page
   - Copy the **Application (client) ID** (looks like: `12345678-1234-1234-1234-123456789abc`)

---

## Environment Configuration

### Step 1: Update `.env` or `.env.master`

Add these variables to your environment file:

```bash
# ========================================
# MICROSOFT 365 OAUTH 2.0 CREDENTIALS
# ========================================
MICROSOFT_CLIENT_ID=12345678-1234-1234-1234-123456789abc
MICROSOFT_CLIENT_SECRET=your~secret~value~here
MICROSOFT_REDIRECT_URI=http://localhost:4000/api/auth/microsoft/callback
MICROSOFT_TENANT=common
```

**Tenant Configuration Options:**
- `common` - Multi-tenant (personal + work/school accounts) ✅ **Recommended**
- `organizations` - Work/school accounts only
- `consumers` - Personal Microsoft accounts only
- `<tenant-id>` - Specific Azure AD tenant

### Step 2: Restart Server

```powershell
# Stop server
BISTOP

# Wait 5 seconds

# Start server
BISTART

# Wait 10-15 seconds for tools to load
Start-Sleep -Seconds 12
```

---

## Testing Authentication

### Test 1: Initiate OAuth Flow

1. **Open browser and navigate to:**
   ```
   http://localhost:4000/api/auth/microsoft/login?user_id=test_user_123
   ```

2. **You should see:**
   - Redirect to Microsoft login page
   - Permission consent screen
   - List of requested permissions
   - "Accept" button

3. **After accepting:**
   - Redirected back to `http://localhost:4000/api/auth/microsoft/callback`
   - JSON response with success message:
     ```json
     {
       "success": true,
       "message": "Microsoft authentication successful",
       "user": {
         "email": "your-email@outlook.com",
         "display_name": "Your Name",
         "microsoft_user_id": "..."
       },
       "scopes": [...],
       "expires_at": "2025-10-24T12:34:56"
     }
     ```

### Test 2: Check Authentication Status

```powershell
# Using curl/PowerShell
Invoke-RestMethod -Uri "http://localhost:4000/api/auth/microsoft/status?user_id=test_user_123"
```

**Expected response:**
```json
{
  "success": true,
  "authenticated": true,
  "email": "your-email@outlook.com",
  "microsoft_user_id": "...",
  "token_expired": false,
  "token_expiry": "2025-10-24T12:34:56",
  "last_updated": "2025-10-24T11:34:56"
}
```

### Test 3: Send Test Email (via CHAT)

```powershell
CHAT Send me a test email via Outlook to myemail@example.com
```

**Expected behavior:**
- AI agent loads Microsoft Outlook tools
- Calls `outlook_send_email()` function
- Email sent successfully
- Returns confirmation message

---

## Using Outlook Tools

### Available Tools (26 Total)

**Basic Email Operations:**
```javascript
// Send email
outlook_send_email({
  to: ["recipient@example.com"],
  subject: "Test Email",
  body: "<h1>Hello!</h1><p>This is a test.</p>",
  body_type: "html",
  cc: ["cc@example.com"],
  importance: "high"
})

// List inbox
outlook_list_messages({
  folder: "inbox",
  max_results: 50,
  unread_only: true
})

// Search emails
outlook_search_messages({
  query: "invoice",
  from_email: "accounting@company.com",
  has_attachments: true,
  date_from: "2025-10-01"
})

// Reply to message
outlook_reply_to_message({
  message_id: "AAMkAG...",
  body: "Thanks for the email!",
  reply_all: false
})
```

**SMART Automation Tools:**
```javascript
// Bulk send personalized emails (mail merge)
outlook_smart_bulk_send_personalized({
  subject_template: "Hi {{name}}, here's your report",
  body_template: "<p>Dear {{name}},</p><p>Your {{report_type}} is attached.</p>",
  recipients: [
    {email: "john@example.com", merge_fields: {name: "John", report_type: "Monthly"}},
    {email: "jane@example.com", merge_fields: {name: "Jane", report_type: "Quarterly"}}
  ],
  delay_seconds: 2
})

// Auto-organize inbox
outlook_smart_organize_inbox({
  rules: [
    {
      name: "Move invoices",
      folder: "Finance/Invoices",
      from_contains: ["billing@", "invoices@"],
      subject_contains: ["invoice", "receipt"],
      mark_as_read: false
    },
    {
      name: "Move newsletters",
      folder: "Reading/Newsletters",
      from_contains: ["newsletter@", "news@"],
      mark_as_read: true
    }
  ],
  create_folders: true
})

// Generate inbox summary
outlook_smart_email_summary({
  days_back: 7,
  unread_only: true,
  group_by: "sender"
})
```

**Advanced Features:**
```javascript
// Create server-side inbox rule
outlook_create_inbox_rule({
  display_name: "Auto-file receipts",
  conditions: {
    from_addresses: ["receipts@amazon.com"],
    subject_contains: ["Your order"]
  },
  actions: {
    move_to_folder: "Personal/Receipts",
    mark_as_read: true,
    mark_importance: "low"
  }
})

// Manage folders
outlook_create_folder({
  display_name: "Projects/2025/Q4",
  parent_folder: null
})

// Flag messages for follow-up
outlook_flag_message({
  message_ids: ["AAMkAG..."],
  flag_status: "flagged",
  due_date: "2025-10-30T17:00:00Z"
})
```

### Example AI Agent Conversations

**Example 1: Send Email**
```
User: Send an email to john@example.com about tomorrow's meeting

AI Agent:
1. Loads outlook_send_email tool
2. Composes professional email
3. Sends via Microsoft Graph API
4. Returns: "Email sent successfully to john@example.com"
```

**Example 2: Organize Inbox**
```
User: Organize my inbox - move all newsletters to a Reading folder and mark as read

AI Agent:
1. Loads outlook_smart_organize_inbox tool
2. Creates rules for newsletter detection
3. Creates "Reading" folder if needed
4. Moves matching messages
5. Marks as read
6. Returns: "Organized 23 messages into Reading folder"
```

**Example 3: Bulk Personalized Emails**
```
User: Send personalized welcome emails to these 5 new customers: [provides list]

AI Agent:
1. Loads outlook_smart_bulk_send_personalized tool
2. Extracts customer names and emails
3. Creates personalized templates with {{name}} placeholders
4. Sends emails with 2-second delays (rate limiting)
5. Returns: "Sent 5 personalized emails successfully"
```

---

## Troubleshooting

### Issue 1: "Microsoft OAuth not configured" Error

**Symptoms:**
```json
{
  "success": false,
  "error": "Microsoft OAuth not configured. Set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET in .env"
}
```

**Solution:**
1. Check `.env` or `.env.master` has correct variables
2. Verify variable names are exact: `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`
3. Restart server: `BISTOP` then `BISTART`
4. Check server logs for "Microsoft 365 authentication routes registered"

---

### Issue 2: "Token exchange failed" After Login

**Symptoms:**
- Login works, but callback shows error
- Error: "Token exchange failed"

**Common Causes:**
1. **Wrong Redirect URI:**
   - Azure App: `http://localhost:4000/api/auth/microsoft/callback`
   - .env: `MICROSOFT_REDIRECT_URI=http://localhost:4000/api/auth/microsoft/callback`
   - Must match EXACTLY

2. **Invalid Client Secret:**
   - Secret might have expired
   - Copy error when saving secret
   - Solution: Generate new secret in Azure Portal

3. **Wrong Tenant:**
   - If using work account, might need specific tenant ID
   - Try changing `MICROSOFT_TENANT=organizations`

---

### Issue 3: "No Microsoft credentials found"

**Symptoms:**
- Authentication worked, but tools can't access mailbox
- Error: "No Microsoft credentials found"

**Solution:**
```powershell
# Check authentication status
Invoke-RestMethod -Uri "http://localhost:4000/api/auth/microsoft/status?user_id=YOUR_USER_ID"

# If not authenticated, re-authenticate:
# 1. Open browser
# 2. Navigate to: http://localhost:4000/api/auth/microsoft/login?user_id=YOUR_USER_ID
# 3. Complete OAuth flow
```

---

### Issue 4: "Token expired" Errors

**Symptoms:**
- Tools worked before, now failing
- Error: "Token expired" or "401 Unauthorized"

**Solution:**
```powershell
# Refresh token manually
Invoke-RestMethod -Uri "http://localhost:4000/api/auth/microsoft/refresh" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"user_id": "YOUR_USER_ID"}'
```

**Automatic Refresh:**
The system automatically refreshes tokens when they expire (within 5 minutes of expiry).

---

### Issue 5: Rate Limiting Errors

**Symptoms:**
- Error: "429 Too Many Requests"
- Bulk operations failing

**Solution:**
```javascript
// Use delay_seconds parameter in bulk operations
outlook_smart_bulk_send_personalized({
  subject_template: "...",
  body_template: "...",
  recipients: [...],
  delay_seconds: 3  // Increase delay between emails
})
```

**Microsoft Graph API Limits:**
- 10,000 requests per 10 minutes (per app)
- 4 concurrent requests per mailbox
- Solution: Add delays, reduce batch sizes

---

### Issue 6: Permission Errors

**Symptoms:**
- Error: "403 Forbidden"
- Error: "Insufficient privileges"

**Solution:**
1. **Check Azure AD permissions:**
   - Go to Azure Portal → App registrations → Your app
   - Check **API permissions**
   - Ensure all required permissions granted:
     - User.Read ✅
     - Mail.Read ✅
     - Mail.Send ✅
     - Mail.ReadWrite ✅
     - MailboxSettings.ReadWrite ✅

2. **Grant admin consent:**
   - Click "✓ Grant admin consent for [Organization]"

3. **Re-authenticate:**
   - User must log out and log in again
   - Navigate to login URL again
   - Accept new permissions

---

### Debug Commands

**Check Server Status:**
```powershell
# Check if server running
Invoke-RestMethod -Uri "http://localhost:4000/health"

# Check loaded tools
CHAT What tools are available?

# Check Microsoft tools specifically
CHAT List all Microsoft Outlook tools
```

**Check Database Credentials:**
```powershell
# Check if credentials stored
python -c "
import sqlite3
conn = sqlite3.connect('ai_agent.db')
cursor = conn.cursor()
cursor.execute('SELECT user_id, platform, platform_email, token_expiry FROM user_platform_credentials WHERE platform=\"microsoft\"')
print(cursor.fetchall())
"
```

**Check Environment Variables:**
```powershell
# In PowerShell
$env:MICROSOFT_CLIENT_ID
$env:MICROSOFT_CLIENT_SECRET
$env:MICROSOFT_REDIRECT_URI
```

---

## Next Steps

**After successful setup:**

1. **Add to Instruction-Request System:**
   - Create platform guide in `agent_routes.py`
   - Add Microsoft Outlook to available platforms
   - Document SMART tool workflows

2. **Create Workflow Examples:**
   - Customer onboarding emails
   - Invoice distribution
   - Newsletter campaigns
   - Support ticket responses

3. **Test Advanced Features:**
   - Server-side inbox rules
   - Email categorization
   - Follow-up reminders
   - Bulk operations

4. **Monitor Usage:**
   - Track API rate limits
   - Monitor token refresh
   - Log email operations
   - Set up error alerts

---

## Resources

**Microsoft Documentation:**
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/overview)
- [Mail API Reference](https://docs.microsoft.com/en-us/graph/api/resources/mail-api-overview)
- [OAuth 2.0 in Azure AD](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)

**Azure Portal:**
- [App Registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
- [API Permissions](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-configure-app-access-web-apis)

**Tool Schema:**
- `tools/schemas/microsoft_outlook_tools.json` - Complete tool definitions
- `tools/microsoft_outlook_tools.py` - Python implementations

---

**Status:** ✅ Ready for Production  
**Version:** 1.0.0  
**Last Updated:** October 24, 2025
