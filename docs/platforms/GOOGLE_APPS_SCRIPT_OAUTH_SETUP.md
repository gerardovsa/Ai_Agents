# Google Apps Script OAuth Setup Guide

**Status**: 🚧 Authentication Required  
**Date**: November 30, 2025

---

## Current Situation

✅ **Tools Built**: All 14 Google Apps Script tools registered and functional  
✅ **Tool Calls Working**: Registry correctly routes execution  
❌ **OAuth Missing**: Access tokens not available for Apps Script API

**Error Seen**:
```python
Result: {'success': False, 'error': 'access_token required but not provided'}
```

---

## Root Cause

Your Google OAuth app is configured with Gmail/Drive/Calendar scopes, but **Apps Script API requires additional scopes** that aren't in your current OAuth consent screen.

**Current Scopes** (from oauth_tokens table):
```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/spreadsheets
... (other Google Workspace scopes)
```

**Missing Scopes** (needed for Apps Script):
```
https://www.googleapis.com/auth/script.projects        ← Read/write script files
https://www.googleapis.com/auth/script.processes       ← View execution logs
https://www.googleapis.com/auth/script.deployments     ← Manage deployments
```

---

## How to Fix (5 Minutes)

### Step 1: Add Apps Script API Scopes

1. **Go to Google Cloud Console**: https://console.cloud.google.com
2. **Select Your Project**: (the one with your OAuth app)
3. **Navigate to**: `APIs & Services` → `OAuth consent screen`
4. **Click**: `EDIT APP` button
5. **Go to**: `Scopes` section → Click `ADD OR REMOVE SCOPES`
6. **Search for**: "Apps Script API"
7. **Check these 3 scopes**:
   ```
   ✅ https://www.googleapis.com/auth/script.projects
   ✅ https://www.googleapis.com/auth/script.processes  
   ✅ https://www.googleapis.com/auth/script.deployments
   ```
8. **Click**: `UPDATE` → `SAVE AND CONTINUE`

**Screenshot Path**: Look for "Google Apps Script API v1" in the scope list

---

### Step 2: Enable Apps Script API

1. **Navigate to**: `APIs & Services` → `Library`
2. **Search for**: "Google Apps Script API"
3. **Click**: The API card
4. **Click**: `ENABLE` button

---

### Step 3: Re-Authenticate

Your existing OAuth tokens don't include the new scopes. You need to re-authenticate:

1. **Visit Auth Endpoint**:
   ```
   http://localhost:5001/api/auth/google/login
   ```

2. **Google will prompt**:
   ```
   "AI Agents wants additional permissions:
   - View and manage your Google Apps Script projects
   - View Google Apps Script execution logs
   - Manage Google Apps Script deployments"
   ```

3. **Click**: `Allow`

4. **Result**: New OAuth token with all scopes saved to database

---

### Step 4: Verify Authentication

Run this test in Python:

```python
from tools.registry_v3 import RegistryV3

registry = RegistryV3()

# Should now work with your OAuth credentials
result = registry.execute_tool(
    tool_name='google_apps_script_list_projects',
    _user_id=12,  # Your user ID
    _injected_credentials=True
)

print(result)
# Expected: {'success': True, 'projects': [...]}
```

---

## Technical Details

### How Credential Injection Works

1. **User calls tool**: `google_apps_script_debug_script(...)`
2. **Registry detects platform**: Tool name starts with `google_apps_script_`
3. **CredentialInjector retrieves token**:
   ```python
   # AI_infrastructure/auth/credential_injector.py
   def get_google_credentials(user_id):
       # Query: SELECT access_token, refresh_token, scopes 
       #        FROM oauth_tokens 
       #        WHERE user_id = ? AND platform = 'google'
       return cred_dict
   ```
4. **Token injected into kwargs**:
   ```python
   kwargs['access_token'] = cred_dict['access_token']
   kwargs['refresh_token'] = cred_dict['refresh_token']
   kwargs['scopes'] = cred_dict['scopes']  # ← Must include Apps Script scopes!
   ```
5. **Tool makes API call**:
   ```python
   # tools/implementations/google_apps_script.py
   headers = {"Authorization": f"Bearer {access_token}"}
   response = requests.get(
       "https://script.googleapis.com/v1/projects",
       headers=headers
   )
   ```

### Current vs Required Scopes

**Your Current oauth_tokens Record**:
```json
{
  "user_id": 12,
  "platform": "google",
  "access_token": "ya29.a0AfB_...",
  "refresh_token": "1//0eXYZ...",
  "scopes": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/drive ..."
}
```

**After Re-Authentication (Expected)**:
```json
{
  "user_id": 12,
  "platform": "google",
  "access_token": "ya29.a0AfB_...",
  "refresh_token": "1//0eXYZ...",
  "scopes": "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/script.projects https://www.googleapis.com/auth/script.processes https://www.googleapis.com/auth/script.deployments ..."
}
```

---

## Verification Checklist

After completing the steps above:

- [ ] Apps Script API enabled in Google Cloud Console
- [ ] Three Apps Script scopes added to OAuth consent screen
- [ ] Re-authenticated via `/api/auth/google/login`
- [ ] New OAuth token saved with Apps Script scopes
- [ ] Test tool execution successful

---

## What Happens Next

Once authentication is set up, you can:

1. **List Your Scripts**:
   ```python
   projects = google_apps_script_list_projects()
   # Returns: All your Apps Script projects including "Northecote File Extractor"
   ```

2. **Debug Failing Script**:
   ```python
   debug = google_apps_script_debug_script(
       script_id="your_northecote_script_id"
   )
   # Returns: Complete diagnostic report with errors and fixes
   ```

3. **Auto-Fix Common Issues**:
   ```python
   fixes = google_apps_script_fix_common_issues(
       script_id="your_northecote_script_id",
       auto_apply=True
   )
   # Returns: Applied fixes (OAuth scopes, deprecated APIs, etc.)
   ```

---

## Troubleshooting

### Issue: "Apps Script API not found in scope list"

**Solution**: Make sure Apps Script API is enabled first (Step 2). The scopes won't appear until the API is enabled.

---

### Issue: "Token still shows 'access_token required'"

**Possible Causes**:
1. **Cached token**: Clear browser cookies and re-authenticate
2. **Database not updated**: Check `oauth_tokens` table:
   ```sql
   SELECT scopes FROM oauth_tokens WHERE user_id = 12;
   ```
   Should include `script.projects`

3. **Wrong user_id**: Verify you're using the correct user ID

---

### Issue: "Scopes prompt not showing during re-auth"

**Solution**: Google caches consent decisions. Force re-consent:
```
http://localhost:5001/api/auth/google/login?prompt=consent
```

---

## Alternative: Service Account (Not Recommended)

If OAuth is problematic, you could use a service account, but this has limitations:

❌ **Limitations**:
- Can't access user's personal scripts
- Can't deploy as user
- Limited to shared/domain scripts only

✅ **OAuth is better** for Apps Script because it:
- Accesses your personal scripts
- Deploys with your permissions
- Manages your projects directly

---

**Ready to proceed?** Follow Steps 1-4 above and let me know when re-authentication is complete!
