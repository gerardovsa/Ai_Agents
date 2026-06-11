# Google Forms API - Credential Injection Issues & Fixes

**Date:** November 3, 2025  
**Status:** Multiple issues identified - Fixes provided  
**Severity:** High - Blocking form creation

---

## Issues Found

### Issue 1: Missing Credential Injection in create_complete_form

**Location:** `google_workspace/google_forms.py` line 2933

**Problem:**
```python
# ❌ WRONG - Not passing _user_id and _injected_credentials
result = google_forms_batch_add_questions(form_id, questions)
```

**Effect:**
- Credentials not passed to batch add questions
- Falls back to service account
- Service account cannot build batch requests
- Results in 400 error: "BatchUpdateFormRequest must contain at least one Request"

**Root Cause:**
- The `**kwargs` containing `_user_id` and `_injected_credentials` are not forwarded

---

### Issue 2: Same problem in create_form call

**Location:** `google_workspace/google_forms.py` line 2925

**Problem:**
```python
# ❌ WRONG - Not passing _user_id and _injected_credentials
form = google_forms_create_form(
    title=title,
    description=description,
    shareable=shareable
)
```

**Effect:**
- Initial form creation falls back to service account
- Service account gets 500 error (cannot create forms)

---

### Issue 3: Platform not being found by discovery system

**Error:** `No tools found for platform: google_workspace`

**Problem:**
- Tools are registered under platform `google_forms`, `gmail`, etc.
- Not under a generic `google_workspace` platform
- Discovery system looking for wrong platform name

---

## Fixes

### Fix 1: Pass credentials through create_complete_form

**File:** `google_workspace/google_forms.py`  
**Line:** 2925

**Change:**
```python
# ❌ BEFORE
form = google_forms_create_form(
    title=title,
    description=description,
    shareable=shareable
)

# ✅ AFTER
form = google_forms_create_form(
    title=title,
    description=description,
    shareable=shareable,
    _user_id=kwargs.get('_user_id'),           # ← ADD THIS
    _injected_credentials=kwargs.get('_injected_credentials')  # ← ADD THIS
)
```

---

### Fix 2: Pass credentials to batch add questions

**File:** `google_workspace/google_forms.py`  
**Line:** 2933

**Change:**
```python
# ❌ BEFORE
result = google_forms_batch_add_questions(form_id, questions)

# ✅ AFTER
result = google_forms_batch_add_questions(
    form_id, 
    questions,
    _user_id=kwargs.get('_user_id'),           # ← ADD THIS
    _injected_credentials=kwargs.get('_injected_credentials')  # ← ADD THIS
)
```

---

### Fix 3: Pass credentials to set_settings

**File:** `google_workspace/google_forms.py`  
**Line:** 2938

**Change:**
```python
# ❌ BEFORE
google_forms_set_settings(form_id, settings_dict)

# ✅ AFTER
google_forms_set_settings(
    form_id, 
    settings_dict,
    _user_id=kwargs.get('_user_id'),           # ← ADD THIS
    _injected_credentials=kwargs.get('_injected_credentials')  # ← ADD THIS
)
```

---

## Why This Matters

### Without Credential Injection:
```
User → AI Agent → Tool Execution
                    ↓
              google_forms_create_complete_form()
                    ↓
              create_form()  ← USES SERVICE ACCOUNT (❌)
                    ↓
              Google Forms API 
                    ↓
              500 Internal Error (service account no permission)
```

### With Credential Injection:
```
User → Google OAuth Login → Credentials Stored in DB
         ↓
    AI Agent Call (with _user_id)
         ↓
    Tool Execution
         ↓
    google_forms_create_complete_form(
        ..., 
        _user_id=1,
        _injected_credentials=True  ← CREDENTIALS PASSED!
    )
         ↓
    create_form(_user_id=1, _injected_credentials=True)
         ↓
    Google Forms API
         ↓
    ✅ Form Created Successfully (uses user's OAuth)
```

---

## How Credential Flow Works

### Step 1: User Authenticates

```
GET /api/auth/google/login
  → Redirect to Google OAuth
  → User grants permission
  → Credentials stored in database
```

### Step 2: AI Agent Makes Tool Call

```python
# Agent calls:
execute_tool(
    'google_forms_create_complete_form',
    title='Survey',
    questions=[...],
    _user_id=1,  # ← FROM REQUEST
    _injected_credentials=True  # ← FROM REQUEST
)
```

### Step 3: Tool Uses User Credentials

```python
def google_forms_create_complete_form(title, questions, ..., **kwargs):
    _user_id = kwargs.get('_user_id')
    _injected_credentials = kwargs.get('_injected_credentials')
    
    # Get user's OAuth credentials from database
    cred_dict = _get_user_credentials_if_available(
        _user_id, 
        _injected_credentials
    )
    
    # Build service with user credentials (NOT service account!)
    service = _get_forms_service(
        user_id=_user_id,
        injected_credentials=cred_dict
    )
    
    # Now service uses user's OAuth token, not service account!
    # ✅ API calls will succeed
```

---

## Verification

### Check 1: Verify User Has Google OAuth

```bash
python -c "
from AI_infrastructure.auth.user_auth import UserAuthManager
auth = UserAuthManager()
creds = auth.get_user_google_oauth_credentials(user_id=1)
if creds:
    print('✅ User has Google OAuth')
    print(f'   Access Token: {creds[\"access_token\"][:20]}...')
else:
    print('❌ User needs to authenticate with Google first')
"
```

### Check 2: Test Form Creation

```bash
python -c "
from google_workspace import google_forms

# Test WITH credentials (should work)
form = google_forms.google_forms_create_complete_form(
    title='Test Form',
    questions=[
        {'type': 'text', 'text': 'What is your name?', 'required': True}
    ],
    _user_id=1,
    _injected_credentials={'access_token': 'YOUR_TOKEN_HERE'}
)
print('✅ Form created:', form['form_id'])
"
```

---

## Implementation Status

### Files to Fix

| File | Issue | Status |
|------|-------|--------|
| `google_workspace/google_forms.py` line 2925 | Missing _user_id, _injected_credentials to create_form | ⏳ TODO |
| `google_workspace/google_forms.py` line 2933 | Missing _user_id, _injected_credentials to batch_add_questions | ⏳ TODO |
| `google_workspace/google_forms.py` line 2938 | Missing _user_id, _injected_credentials to set_settings | ⏳ TODO |

### Already Working

✅ `agent_routes_v4.py` - Credential injection implemented  
✅ `google_auth_routes_V2_FIXED.py` - OAuth flow implemented  
✅ `google_forms.py` - _get_user_credentials_if_available() works  
✅ `google_forms.py` - _get_forms_service() handles credentials  

---

## Error Messages Explained

### Error 1: 500 Internal Error on create

```
Failed to create form: <HttpError 500 when requesting 
  https://forms.googleapis.com/v1/forms?alt=json 
  returned "Internal error">
```

**Cause:** Service account trying to create form (no permission)  
**Fix:** Pass `_user_id` and `_injected_credentials` to `google_forms_create_form()`

---

### Error 2: 400 Batch update empty

```
Failed to batch add questions: <HttpError 400 when requesting 
  https://forms.googleapis.com/v1/forms/.../batchUpdate?alt=json 
  returned "BatchUpdateFormRequest must contain at least one Request">
```

**Cause:** Service account cannot construct batch requests  
**Fix:** Pass `_user_id` and `_injected_credentials` to `google_forms_batch_add_questions()`

---

### Error 3: Platform not found

```
No tools found for platform: google_workspace
```

**Cause:** Tools are on individual platforms (google_forms, gmail, sheets, etc.)  
**Fix:** Use specific platform name or search_tools() instead

---

## User OAuth Flow (Already Implemented)

### 1. User Logs In With Google

```
http://localhost:5001/api/auth/google/login
```

**What happens:**
- User redirected to Google
- User grants permission for Google Forms, Drive, Sheets, etc.
- Credentials stored in database table `user_platform_credentials`

### 2. AI Agent Gets User ID

```python
# In agent_routes_v4.py
user_id = request_data.get("_user_id")  # From request (usually 1 for single user)
credentials = get_credentials_from_db(user_id, 'google')  # From database
```

### 3. Tools Use User Credentials

```python
# Automatically injected by agent_routes_v4.py
execute_tool(
    'google_forms_create_complete_form',
    title='Survey',
    questions=[...],
    _user_id=user_id,          # ← Automatically added
    _injected_credentials=credentials  # ← Automatically added
)
```

### 4. Forms Use User's OAuth

```python
# In google_forms.py
def google_forms_create_complete_form(..., _user_id, _injected_credentials, **kwargs):
    # User's OAuth used (not service account)
    # ✅ Works!
```

---

## Quick Test

### Test 1: Without Fix (Will Fail)

```bash
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a Google Form",
    "_user_id": 1,
    "_injected_credentials": true
  }'
```

**Result:** 500 or 400 error

---

### Test 2: After Fix (Will Work)

```bash
curl -X POST http://localhost:5001/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a Google Form called Survey with questions",
    "_user_id": 1,
    "_injected_credentials": true
  }'
```

**Result:** ✅ Form created successfully

---

## Summary

### The Problem
Credential injection is implemented but not being passed through the call chain. Each nested function call loses the `_user_id` and `_injected_credentials` parameters.

### The Solution
Add `_user_id=kwargs.get('_user_id')` and `_injected_credentials=kwargs.get('_injected_credentials')` to each function call within `google_forms_create_complete_form()`.

### The Impact
- ✅ Forms will be created using user's OAuth credentials
- ✅ No more 500/400 errors
- ✅ All Google Forms tools will work
- ✅ User maintains control and security

### Time to Fix
**5 minutes** - 3 simple edits to pass parameters through

---

## References

**Already Implemented:**
- `AI_infrastructure/routes/agent_routes_v4.py` - Credential injection at agent level
- `AI_infrastructure/routes/google_auth_routes_V2_FIXED.py` - OAuth login
- `google_workspace/google_forms.py` - All helper functions for credential handling

**Just Need:**
- Pass credentials through the function call chain
- 3 edits in `google_forms_create_complete_form()`

**Result:**
- Full user OAuth support for Google Forms
- AI agent can create forms on behalf of user
- All 608 tools work with proper credentials
