# Google Forms API 500 Error - Diagnostic & Fix

**Date:** November 3, 2025  
**Error:** `HttpError 500: Internal error` from `https://forms.googleapis.com/v1/forms`  
**Status:** Analysis Complete - Provides 3 fix options

---

## Problem Analysis

### What's Happening

```
🔑 Using service account from environment variables
INFO:googleapiclient.discovery_cache:file_cache is only supported with oauth2client<4.0.0
Failed to create form: <HttpError 500 when requesting 
  https://forms.googleapis.com/v1/forms?alt=json 
  returned "Internal error">
```

### Root Cause

**The service account is being used instead of user OAuth credentials.**

Service accounts **cannot** create Google Forms - they can only read/manage with existing credentials. The API returns a generic 500 error when service account tries to create a form.

---

## Why This Happens

### Code Flow

```python
# google_forms.py - Line 161-167
cred_dict = _get_user_credentials_if_available(_user_id, _injected_credentials)

if cred_dict:
    # ✅ Use user OAuth credentials
    service = _get_forms_service(user_id=_user_id, injected_credentials=cred_dict)
else:
    # ❌ Falls back to service account (NO PERMISSION!)
    service = _get_forms_service()  # Uses build_forms_service()
```

### When It Falls Back

The fallback to service account happens when:

1. **No `_user_id` parameter** passed
2. **No `_injected_credentials` parameter** passed
3. **User doesn't have OAuth in database**
4. **Credentials couldn't be loaded** from database

---

## Solution Options

### ✅ Option 1: Use User OAuth Credentials (Recommended)

**Requirement:** User must have Google OAuth credentials stored in database

**How It Works:**
1. User logs in with Google OAuth
2. System stores `access_token` in database
3. Tool execution passes `_user_id` and `_injected_credentials=True`
4. Google Forms uses user's credentials (has permission to create forms)

**Implementation:**

```python
# When calling from AI agent:
execute_tool(
    'google_forms_create_complete_form',
    title='Survey',
    questions=[...],
    _user_id=1,                        # User ID from database
    _injected_credentials=True         # Flag to load from DB
)
```

**Verification:**
```bash
# Check if user has Google OAuth in database:
python -c "
from AI_infrastructure.auth.user_auth import UserAuthManager
auth = UserAuthManager()
creds = auth.get_user_google_oauth_credentials(user_id=1)
print('Has Google OAuth:', creds is not None)
"
```

---

### ✅ Option 2: Use Service Account with Google Workspace Domain

**Requirement:** Set up Google Workspace domain-wide delegation

**How It Works:**
1. Configure service account with domain-wide delegation
2. Service account acts "on behalf of" a domain user
3. That domain user can create forms
4. Service account gets permission through workspace delegation

**Implementation:**

```python
# In google_auth_helper.py - build_forms_service():
from google.auth.identity_pool import Credentials
from googleapiclient.discovery import build

# Service account with domain delegation
credentials = service_account.Credentials.from_service_account_file(
    'service-account.json',
    scopes=['https://www.googleapis.com/auth/forms']
)

# Delegate to workspace user
delegated_credentials = credentials.with_subject('user@your-domain.com')
service = build('forms', 'v1', credentials=delegated_credentials)
```

**Setup Required:**
1. Enable domain-wide delegation in Google Cloud Console
2. Grant delegated scopes in Google Workspace admin
3. Configure user email in environment

---

### ✅ Option 3: Disable Form Creation, Use Templates

**When to use:** If OAuth setup is not feasible

**How It Works:**
1. Create form templates manually in Google Forms
2. Use `google_forms_copy_form()` to duplicate templates
3. Edit the copy with questions/settings
4. Share with users

**Implementation:**

```python
# Instead of creating form:
original_form_id = 'template-form-id'

# Copy the template
copy_result = google_forms_copy_form(
    source_form_id=original_form_id,
    new_title='Survey ' + datetime.now().isoformat(),
    copy_questions=True,
    copy_settings=True
)

# Edit the copy
new_form_id = copy_result['form_id']
# ... modify as needed ...
```

---

## Recommended Fix Priority

### Priority 1: Enable User OAuth (Best)
**Status:** Implement user login with Google OAuth
- ✅ Proper security model
- ✅ Forms created by actual user
- ✅ Full API functionality
- ✅ Transparent to end user

**Action:**
```bash
# Make sure user authenticates with Google first
# Then tools automatically get access
```

---

### Priority 2: Set Up Domain Delegation (Good)
**Status:** Configure Google Workspace admin
- ✅ Works with service account
- ⚠️ Requires Google Workspace domain
- ⚠️ Admin setup required
- ✅ Automatic for all users

**Action:**
```bash
# 1. Enable domain-wide delegation in GCP
# 2. Grant scopes in Google Workspace admin
# 3. Update build_forms_service() to use delegation
```

---

### Priority 3: Use Form Templates (Quick Fix)
**Status:** Create templates manually, copy them
- ✅ Works immediately
- ⚠️ Limited flexibility
- ⚠️ Manual template management
- ✅ No credential issues

**Action:**
```bash
# 1. Create template form in Google Forms
# 2. Note the form ID
# 3. Use copy_form() instead of create_form()
```

---

## Current Status

### Credentials Configuration

**Environment Variable Check:**
```bash
echo %GOOGLE_APPLICATION_CREDENTIALS%
# Should point to service-account.json
```

**Service Account Info:**
```bash
# Check if service account file exists and is valid
python -c "
import json
with open('google_service_account.json') as f:
    sa = json.load(f)
    print('Service Account Email:', sa.get('client_email'))
    print('Project:', sa.get('project_id'))
"
```

**Database OAuth Status:**
```bash
# Check how many users have Google OAuth stored
python -c "
import sqlite3
db = sqlite3.connect('data/ai_infrastructure.db')
c = db.cursor()
c.execute(\"SELECT COUNT(*) FROM user_platform_credentials WHERE platform='google'\")
print('Users with Google OAuth:', c.fetchone()[0])
"
```

---

## Quick Fix for Right Now

### Immediate Workaround

If you need forms to work **right now** without OAuth setup:

**Option A: Use existing form template**
```python
# Use copy_form() instead of create_form()
form = google_forms_copy_form(
    source_form_id='YOUR_TEMPLATE_FORM_ID',
    new_title='Survey'
)
```

**Option B: Create forms manually**
1. Go to `forms.google.com`
2. Create form manually with all questions
3. Copy the form ID
4. Share the link

**Option C: Skip form creation**
```python
# Use Google Sheets for surveys instead
from google_workspace import google_sheets
sheets.create_spreadsheet(title='Survey')
```

---

## Detailed Implementation Guide

### Fix 1: Enable User OAuth

**Step 1: Update login endpoint to include Google**
```python
# AI_infrastructure/routes/google_auth_routes_V2_FIXED.py
# Already implemented! Just needs to be called

# User visits: /api/auth/google/login
# Returns: Authorization URL
```

**Step 2: Store credentials in database**
```python
# Already implemented in:
# AI_infrastructure/routes/google_auth_routes_V2_FIXED.py
# Credentials stored in: user_platform_credentials table
```

**Step 3: Pass credentials to tool**
```python
# In agent_routes_v4.py - already implemented!
# Tools get: _user_id and _injected_credentials
```

**What to do:** 
1. User needs to visit: `http://localhost:5001/api/auth/google/login`
2. Login with Google account
3. Grant permission for Google Forms
4. Credentials automatically stored
5. Now forms will work!

---

### Fix 2: Configure Domain Delegation

**Step 1: Enable in Google Cloud Console**
1. Go to Google Cloud Console
2. Select project
3. Enable Admin SDK
4. Go to Service Accounts
5. Click on service account
6. Go to Security tab
7. Click "Domain-wide delegation"
8. Check "Enable domain-wide delegation"
9. Note the OAuth Client ID

**Step 2: Configure in Google Workspace Admin**
1. Go to google.com/admin
2. Select Security
3. Go to API controls > Domain-wide delegation
4. Click "Add new"
5. Paste OAuth Client ID from step 1
6. Add scopes:
   - `https://www.googleapis.com/auth/forms`
   - `https://www.googleapis.com/auth/drive`

**Step 3: Update build_forms_service()**
```python
# In google_workspace/google_auth_helper.py

def build_forms_service():
    """Build Forms service with domain-wide delegation"""
    from google.oauth2 import service_account
    
    credentials = service_account.Credentials.from_service_account_file(
        'path/to/service-account.json',
        scopes=['https://www.googleapis.com/auth/forms'],
        subject='workspace-user@yourdomain.com'  # Workspace user email
    )
    
    return build('forms', 'v1', credentials=credentials)
```

---

## Testing the Fix

### Test 1: Check Credentials
```python
python -c "
from google_workspace.google_auth_helper import build_forms_service
service = build_forms_service()
print('✅ Service created successfully')
"
```

### Test 2: Create Test Form
```python
from google_workspace import google_forms

form = google_forms.google_forms_create_form(
    title='Test Form',
    description='Testing if fix works'
)

print(f'✅ Form created: {form[\"form_id\"]}')
print(f'✅ Responder URI: {form[\"responder_uri\"]}')
```

### Test 3: Via AI Agent
```bash
CHAT "Create a Google Form called 'Customer Feedback' with questions about service quality"
```

---

## Error Message Explanation

### What "Internal error 500" means

**For Google Forms API specifically:**
- ❌ Service account trying to create form (no permission)
- ❌ Missing required scopes
- ❌ Invalid credentials
- ❌ API quota exceeded
- ❌ Invalid form body (rare)

**NOT a server error** - it's the API telling you something's wrong with your request/auth.

### How to verify which issue

```bash
# Check 1: Is service account in use?
grep "Using service account" /path/to/logs

# Check 2: Do we have user OAuth?
python -c "
from AI_infrastructure.auth.user_auth import UserAuthManager
creds = UserAuthManager().get_user_google_oauth_credentials(1)
print('User has OAuth:', creds is not None)
"

# Check 3: Are scopes correct?
python -c "
import json
with open('google_service_account.json') as f:
    sa = json.load(f)
    # Service accounts don't list scopes - that's the issue!
    print('This service account cannot create forms directly')
"
```

---

## Recommendation

**Implement Priority 1: User OAuth**

1. **Why:** 
   - Most secure (forms created by actual user)
   - Already implemented in codebase
   - Best user experience
   - Full API functionality

2. **How:**
   - User logs in with Google (redirect to `/api/auth/google/login`)
   - Credentials stored in database
   - Tools automatically use those credentials
   - Forms creation works!

3. **Time to implement:** 5 minutes
   - User just needs to login
   - Everything else is already in place

4. **Test:**
   - Have user login via Google
   - Run form creation
   - Should work!

---

## Files to Update

### Current State
- ✅ `google_forms.py` - Already has user credential support
- ✅ `google_auth_routes_V2_FIXED.py` - Already implements OAuth
- ✅ `agent_routes_v4.py` - Already passes credentials to tools
- ⚠️ **Just needs user to authenticate!**

### What to Change
- Nothing in code!
- Just ensure user does OAuth login first

### Where User Logs In
```
http://localhost:5001/api/auth/google/login
```

---

## Status Summary

| Issue | Cause | Solution |
|-------|-------|----------|
| **500 Error from Google Forms** | Service account lacks permission | Use user OAuth |
| **Service account fallback** | No `_user_id` passed to tool | Authenticate user first |
| **"Internal error" message** | Generic API error | Enable user OAuth login |

**Root Fix:** User must authenticate with Google first, then form creation will work!
