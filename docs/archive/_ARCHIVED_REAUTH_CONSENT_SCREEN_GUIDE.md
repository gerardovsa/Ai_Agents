# Re-authentication Consent Screen - Complete Guide

**Date:** November 3, 2025  
**Issue:** Consent screen not appearing during re-authentication  
**Status:** ENHANCED with token revocation

---

## 🎯 The Problem

When clicking "Re-authenticate Account", users expect to see the OAuth consent screen again where they must re-approve permissions. However, the consent screen may not appear because:

1. **OAuth Provider Remembers** - Google/Microsoft remembers previous consent
2. **Active Session** - User still logged into Google/Microsoft in their browser
3. **Cached Approval** - OAuth provider has cached the approval decision

---

## ✅ Solution Implemented

### Three-Layer Approach:

1. **Local Token Deletion** - Delete tokens from our database
2. **Provider Token Revocation** - Revoke tokens with Google/Microsoft API
3. **Force Consent Parameter** - Use `prompt=consent` in OAuth URL

---

## 🔧 Implementation Details

### 1. Token Revocation (`auth_routes.py`)

**Enhanced `/api/auth/revoke-tokens` endpoint:**

```python
@auth_bp.route('/revoke-tokens', methods=['POST'])
@require_auth
def revoke_tokens():
    # Step 1: Get existing tokens from database
    cursor.execute('SELECT access_token, refresh_token FROM oauth_tokens WHERE ...')
    token_row = cursor.fetchone()
    
    # Step 2: Revoke with OAuth provider
    if platform == 'google':
        # Google Token Revocation API
        requests.post(
            'https://oauth2.googleapis.com/revoke',
            params={'token': refresh_token}
        )
        # This tells Google to forget the consent
    
    elif platform == 'microsoft':
        # Microsoft revocation requires client credentials
        # Using prompt=consent instead
    
    # Step 3: Delete local tokens
    cursor.execute('DELETE FROM oauth_tokens WHERE user_id = ? AND platform = ?')
    
    # Step 4: Update flags
    cursor.execute('UPDATE users SET has_google_oauth = 0 WHERE ...')
```

**Google Token Revocation:**
- ✅ Calls `https://oauth2.googleapis.com/revoke`
- ✅ Invalidates both access_token and refresh_token
- ✅ Forces Google to "forget" the previous consent
- ✅ Next OAuth flow will show consent screen

**Microsoft Token Revocation:**
- ⚠️ More complex - requires client credentials
- ⚠️ Not fully implemented yet
- ✅ Using `prompt=consent` as alternative

### 2. Google OAuth with Forced Consent

**Enhanced parameters:**

```python
params = {
    'client_id': GOOGLE_CLIENT_ID,
    'redirect_uri': GOOGLE_REDIRECT_URI,
    'response_type': 'code',
    'scope': ' '.join(GOOGLE_SCOPES),
    'state': state,
    'access_type': 'offline',
    'prompt': 'consent',              # ✅ Force consent screen
    'approval_prompt': 'force'         # ✅ Legacy parameter (still works)
}
```

**Two parameters used:**
- `prompt=consent` - Modern OAuth 2.0 standard
- `approval_prompt=force` - Legacy Google parameter (backup)

### 3. Microsoft OAuth with Forced Consent

**Enhanced parameters:**

```python
params = {
    'client_id': client_id,
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'response_mode': 'query',
    'scope': ' '.join(scopes),
    'state': state,
    'prompt': 'consent'  # ✅ Force consent screen
}
```

---

## 🔄 Complete Re-authentication Flow

### Step-by-Step Process:

```
1. User clicks "Re-authenticate Account" button
   │
   ▼
2. Frontend shows confirmation dialog
   │
   ▼
3. User clicks "OK"
   │
   ▼
4. Frontend calls: POST /api/auth/revoke-tokens
   │
   ├─ Backend gets tokens from database
   │
   ├─ Backend revokes with Google API:
   │  POST https://oauth2.googleapis.com/revoke?token=...
   │  └─ Google marks consent as revoked ✅
   │
   ├─ Backend deletes local tokens
   │  DELETE FROM oauth_tokens WHERE user_id = X
   │
   └─ Backend updates flags
      UPDATE users SET has_google_oauth = 0
   │
   ▼
5. Frontend clears local storage
   │
   ▼
6. Frontend redirects with force_consent=true:
   /api/auth/google/login?force_consent=true
   │
   ▼
7. Backend builds OAuth URL with:
   - prompt=consent
   - approval_prompt=force (Google)
   │
   ▼
8. User redirected to OAuth provider
   │
   ▼
9. OAuth provider checks:
   - Token revoked? ✅ Yes (from step 4)
   - prompt=consent? ✅ Yes (from step 7)
   │
   ▼
10. Consent screen APPEARS ✅
    ┌─────────────────────────────────┐
    │ This app wants to:              │
    │ ☐ Read your profile             │
    │ ☐ Access your email             │
    │ ☐ Read/write calendar           │
    │ ☐ Read/write files              │
    │                                 │
    │     [Cancel]  [Allow] ← Click   │
    └─────────────────────────────────┘
   │
   ▼
11. User clicks "Allow"
   │
   ▼
12. OAuth callback
   │
   ▼
13. New tokens stored
   │
   ▼
14. User logged in ✅
```

---

## ⚠️ Why Consent Screen Might Still Not Appear

### Common Issues:

**1. Browser Session**
- **Problem:** User still logged into Google/Microsoft in same browser
- **Solution:** Google/Microsoft might skip consent for "trusted" sessions
- **Workaround:** User should logout from Google/Microsoft first, OR use incognito mode

**2. Organization Policies**
- **Problem:** Admin pre-approved the app for organization
- **Solution:** Organization admin controls consent requirements
- **Workaround:** Contact organization admin

**3. Token Not Fully Revoked**
- **Problem:** Token revocation API call failed
- **Solution:** Check server logs for revocation errors
- **Workaround:** Wait 5-10 minutes for revocation to propagate

**4. Cached Approval**
- **Problem:** OAuth provider caching previous approval
- **Solution:** Clear browser cookies/cache
- **Workaround:** Wait or use incognito mode

---

## 🧪 Testing

### Test Token Revocation:

**1. Check server logs during re-auth:**

```
🔄 [REVOKE TOKENS] User 1 revoking google tokens
🗑️ [REVOKE TOKENS] Revoking Google token via API...
✅ [REVOKE TOKENS] Google token revoked successfully
✅ [REVOKE TOKENS] Deleted 1 local tokens for google
```

**2. Verify Google revocation:**

```powershell
# Check if token is revoked
curl "https://oauth2.googleapis.com/tokeninfo?access_token=YOUR_TOKEN"

# If revoked, you'll get:
# {
#   "error": "invalid_token",
#   "error_description": "Token has been revoked"
# }
```

### Test Consent Screen:

**1. Normal flow (should skip consent):**
```
/api/auth/google/login
→ prompt=select_account
→ Show account picker
→ Skip consent (if already approved)
```

**2. Re-auth flow (should show consent):**
```
/api/auth/google/login?force_consent=true
→ Token revoked via API ✅
→ prompt=consent ✅
→ approval_prompt=force ✅
→ MUST show consent screen ✅
```

---

## 🔍 Debugging

### Check if revocation worked:

**1. Look for these log lines:**
```
✅ [REVOKE TOKENS] Google token revoked successfully
```

**2. If you see this, revocation failed:**
```
⚠️ [REVOKE TOKENS] Google revocation returned 400
⚠️ [REVOKE TOKENS] Google revocation failed: [error]
```

### Check OAuth URL parameters:

**View the redirect URL in browser network tab:**

```
https://accounts.google.com/o/oauth2/v2/auth?
  client_id=...&
  redirect_uri=...&
  response_type=code&
  scope=...&
  state=...&
  access_type=offline&
  prompt=consent&           ← MUST be 'consent'
  approval_prompt=force     ← Should be present
```

---

## 💡 User Instructions

### How to Force Consent Screen:

**Method 1: Use Re-authentication Button (Recommended)**
1. Click profile → "Re-authenticate Account"
2. Confirm dialog
3. Wait for consent screen
4. Approve permissions

**Method 2: Logout from OAuth Provider First**
1. Go to Google/Microsoft and logout
2. Return to app
3. Click "Re-authenticate Account"
4. Login and approve permissions

**Method 3: Use Incognito/Private Window**
1. Open incognito/private window
2. Navigate to app
3. Login (will always show consent)

**Method 4: Revoke Access Manually**
1. Go to Google: https://myaccount.google.com/permissions
2. Find the app and click "Remove Access"
3. Return to app and re-authenticate
4. Will show consent screen

---

## 📊 Comparison

| Method | Token Revocation | Consent Screen | User Experience |
|--------|-----------------|----------------|-----------------|
| **Our Implementation** | ✅ Yes (Google) | ✅ Should appear | One-click |
| **Manual Revoke** | ✅ Yes | ✅ Always | Multi-step |
| **Incognito Mode** | ❌ No | ✅ Always | Clean session |
| **Logout OAuth** | ❌ No | ✅ Usually | Extra step |

---

## 🔒 Google Token Revocation API

### Endpoint:
```
POST https://oauth2.googleapis.com/revoke
```

### Parameters:
```
token: <access_token> or <refresh_token>
```

### Response:
```
200 OK - Token revoked successfully
400 Bad Request - Invalid token or already revoked
```

### Documentation:
https://developers.google.com/identity/protocols/oauth2/web-server#tokenrevoke

---

## 🎯 Expected Behavior

### After Implementation:

**For Google:**
1. ✅ Token revoked via API
2. ✅ `prompt=consent` set
3. ✅ `approval_prompt=force` set
4. ✅ Consent screen should appear
5. ✅ User must re-approve all scopes

**For Microsoft:**
1. ⚠️ Token revocation not implemented (complex)
2. ✅ `prompt=consent` set
3. ⚠️ Consent might not appear if organization pre-approved
4. ℹ️ Depends on tenant admin settings

---

## 📝 Known Limitations

1. **Microsoft Revocation** - Not fully implemented, requires client credentials flow
2. **Organization Pre-approval** - Cannot override organization admin settings
3. **Browser Session** - Consent might skip if trusted session exists
4. **Revocation Propagation** - May take 5-10 minutes to fully propagate

---

## 🚀 Deployment Status

**Google:**
- ✅ Token revocation implemented
- ✅ `prompt=consent` implemented
- ✅ `approval_prompt=force` implemented
- ✅ Production ready

**Microsoft:**
- ⚠️ Token revocation NOT implemented
- ✅ `prompt=consent` implemented
- ⚠️ May not force consent in all scenarios
- ⚠️ Depends on tenant configuration

---

**Last Updated:** November 3, 2025  
**Version:** 1.3.0  
**Status:** Enhanced with Token Revocation (Google)
