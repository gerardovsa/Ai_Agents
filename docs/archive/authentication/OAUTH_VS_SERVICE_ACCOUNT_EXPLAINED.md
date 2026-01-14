# 🔐 Google Tasks OAuth Setup - Detailed Guide

## Why OAuth for Tasks?

### The Key Difference

**Service Account (Already Working):**
```
Service Account → Organization Data → Gmail/Docs/Sheets/Drive/etc.
Works because: Accessing shared/organization resources
```

**OAuth 2.0 (Needed for Tasks):**
```
OAuth 2.0 → Personal User Data → Google Tasks (your personal task lists)
Required because: Tasks are always personal, never shared
```

---

## 🔑 Authentication Types Comparison

### Service Account vs OAuth 2.0

| Feature | Service Account | OAuth 2.0 |
|---------|----------------|-----------|
| **File** | `vsa-anythingllm-project-ab7c8caf8c47.json` | `credentials.json` + `token.json` |
| **Access** | Organization/shared data | Personal user data |
| **Setup** | One-time (already done ✅) | One-time + first auth |
| **User Interaction** | None | Browser login first time |
| **Platforms** | Gmail, Docs, Sheets, Slides, Drive, Calendar, Forms, Meet, Cloud Run, Analytics | **Only Google Tasks** |

---

## 📋 Step-by-Step OAuth Setup

### Step 1: Create OAuth 2.0 Client ID

**Current Status:** You have Google Cloud Console open at:
`https://console.cloud.google.com/apis/credentials?project=vsa-anythingllm-project`

**Actions:**

1. **Click "Create Credentials"** button (top of page)
   
2. **Select "OAuth 2.0 Client ID"** from dropdown

3. **Configure Consent Screen** (if prompted):
   - Click "Configure Consent Screen"
   - Choose **"Internal"** if available (for organization)
   - Or choose **"External"** (for personal use)
   - Click "Create"
   
   **Fill in required fields:**
   - App name: `AI Agents Platform - Google Tasks`
   - User support email: `your-email@example.com`
   - Developer contact: `your-email@example.com`
   - Click "Save and Continue"
   
   **Scopes screen:**
   - Click "Add or Remove Scopes"
   - Search for: `Google Tasks API`
   - Select: `https://www.googleapis.com/auth/tasks`
   - Click "Update"
   - Click "Save and Continue"
   
   **Test users** (if External):
   - Add your email address
   - Click "Save and Continue"
   
   **Summary:**
   - Review and click "Back to Dashboard"

4. **Return to Credentials page** and click "Create Credentials" → "OAuth 2.0 Client ID" again

5. **Application Type:**
   - Select: **"Desktop app"** ⭐ (Important!)
   - Name: `AI Agents - Google Tasks`
   - Click "Create"

6. **Download Credentials:**
   - Pop-up appears with "OAuth client created"
   - Click **"Download JSON"** button
   - Save file as: `credentials.json`
   - Move to: `C:\Users\gpoli\GIT\AI_agents\credentials.json`

---

### Step 2: First-Time Authentication

**Run this command:**

```powershell
cd C:\Users\gpoli\GIT\AI_agents

python -c "from google_workspace.google_tasks import google_tasks_list_task_lists; print(google_tasks_list_task_lists())"
```

**What Happens:**

1. **Browser Opens Automatically**
   - Google OAuth consent screen appears
   
2. **Sign In**
   - Use your Google account (the one with task lists)
   
3. **Grant Permission**
   - Shows: "AI Agents Platform - Google Tasks wants to access your Google Account"
   - Shows scope: "See, edit, create, and delete all your Google Tasks"
   - Click **"Continue"** or **"Allow"**

4. **Token Saved**
   - `token.json` file created automatically in `C:\Users\gpoli\GIT\AI_agents\`
   - You're authenticated! ✅

5. **Command Output**
   - Should show your task lists:
   ```json
   {
     "task_lists": [
       {"id": "abc123", "title": "My Tasks"},
       {"id": "def456", "title": "Work Tasks"}
     ],
     "count": 2
   }
   ```

---

### Step 3: Verify Setup

**Check files exist:**

```powershell
# Check credentials.json
Test-Path C:\Users\gpoli\GIT\AI_agents\credentials.json
# Should return: True

# Check token.json (after first auth)
Test-Path C:\Users\gpoli\GIT\AI_agents\token.json
# Should return: True (after running first auth)
```

**Test via AI Agent:**

```powershell
# Restart agent
BISTOP
BISTART

# Wait 10-15 seconds for tools to load

# Test Tasks tools
CHAT List my Google Tasks
CHAT Create a task "Test Google Tasks integration"
CHAT Complete the task "Test Google Tasks integration"
```

---

## ❓ FAQ

### Q: Do I need OAuth for all Google Workspace platforms?

**A: NO! Only for Google Tasks.**

**Breakdown:**

| Platform | Authentication | Why |
|----------|---------------|-----|
| Gmail | Service Account ✅ | Organization emails |
| Docs | Service Account ✅ | Shared documents |
| Sheets | Service Account ✅ | Shared spreadsheets |
| Slides | Service Account ✅ | Shared presentations |
| Drive | Service Account ✅ | Shared files/folders |
| Calendar | Service Account ✅ | Organization calendars |
| Forms | Service Account ✅ | Organization forms |
| Meet | Service Account ✅ | Organization meetings |
| Cloud Run | Service Account ✅ | GCP deployments |
| Analytics | Service Account ✅ | Website analytics |
| **Tasks** | **OAuth 2.0** ❌ | **Personal task lists** |

---

### Q: Why is Tasks different?

**A: Google Tasks is inherently personal.**

**Technical Reasons:**

1. **No Organization Concept**
   - Gmail has "organization inbox" → Service account works
   - Drive has "shared folders" → Service account works
   - Calendar has "organization calendars" → Service account works
   - **Tasks has NO shared lists** → Must be personal user ❌

2. **API Design**
   - Google Tasks API **only** reads/writes to the authenticated user's personal task lists
   - No way to access "organization tasks" (doesn't exist)
   - Service accounts **cannot** impersonate users for Tasks API

3. **Privacy by Design**
   - Google considers task lists highly personal
   - Requires explicit user consent via OAuth
   - Cannot be delegated to service accounts

---

### Q: What permissions do I need for the service account?

**A: None! Service account doesn't work with Tasks.**

The service account you have (`vsa-anythingllm-project-ab7c8caf8c47.json`) is perfect for all other platforms but **cannot** be used for Google Tasks.

**You enabled:**
- ✅ Google Tasks API (correct - needed for Tasks to work)
- ❌ API Key (not needed - OAuth uses Client ID instead)

**What you actually need:**
- ✅ OAuth 2.0 Client ID (Desktop app) ← Download this as `credentials.json`

---

### Q: What's the difference between API Key and OAuth credentials?

| Type | Purpose | Used For | File |
|------|---------|----------|------|
| **Service Account** | Machine-to-machine auth | Organization data (Gmail, Docs, etc.) | `vsa-anythingllm-project-ab7c8caf8c47.json` |
| **API Key** | Public API access | Maps, YouTube (public data) | Not needed for Tasks |
| **OAuth 2.0 Client ID** | User consent & personal data | Personal task lists | `credentials.json` + `token.json` |

**You need:** OAuth 2.0 Client ID (not API Key)

---

### Q: Is OAuth 2.0 secure?

**A: Yes, very secure!**

**Security Features:**

1. **User Consent Required**
   - User must explicitly grant permission in browser
   - Can see exactly what access is requested
   - Can revoke access anytime

2. **Token-Based**
   - Access token stored in `token.json`
   - Refresh token auto-renews expired tokens
   - No passwords stored

3. **Scoped Access**
   - Only requests `https://www.googleapis.com/auth/tasks` scope
   - Cannot access Gmail, Drive, or other services
   - Limited to task lists only

4. **Revocable**
   - User can revoke access at: https://myaccount.google.com/permissions
   - Delete `token.json` to force re-authentication

---

### Q: Do I need to authenticate every time?

**A: No! Only first time.**

**Authentication Flow:**

1. **First Time:**
   - Browser opens → Sign in → Grant permission
   - `token.json` created with access + refresh tokens

2. **Subsequent Uses:**
   - Reads `token.json` automatically
   - Uses cached access token
   - No browser, no sign-in needed ✅

3. **Token Expiry:**
   - Access token expires after 1 hour
   - Refresh token used to get new access token automatically
   - No user interaction needed

4. **Re-authentication Only If:**
   - `token.json` deleted
   - User revokes access in Google Account settings
   - Refresh token expires (very rare - usually 6 months+)

---

### Q: Can I use the same OAuth credentials for multiple users?

**A: Yes, but each user authenticates separately.**

**How It Works:**

1. **One `credentials.json`**
   - Same OAuth Client ID for all users
   - Download once, use for everyone

2. **Multiple `token.json` Files**
   - Each user gets their own `token.json`
   - Stores their personal access/refresh tokens
   - Option 1: Different filenames (`token_user1.json`, `token_user2.json`)
   - Option 2: Different directories per user

**Example Multi-User Setup:**

```python
# User 1
token_file = "tokens/user1_token.json"
service = build_tasks_service(token_file=token_file)

# User 2
token_file = "tokens/user2_token.json"
service = build_tasks_service(token_file=token_file)
```

---

## 🔍 Troubleshooting

### Issue: "File credentials.json not found"

**Solution:**
1. Download OAuth credentials from Google Cloud Console
2. Save as `credentials.json` (exact filename)
3. Place in: `C:\Users\gpoli\GIT\AI_agents\credentials.json`
4. Verify: `Test-Path C:\Users\gpoli\GIT\AI_agents\credentials.json`

---

### Issue: "This app isn't verified" warning during OAuth

**Explanation:** Google shows this for apps in testing mode

**Solution:**
1. Click "Advanced" (bottom left)
2. Click "Go to AI Agents Platform - Google Tasks (unsafe)"
3. This is YOUR app, it's safe!
4. Alternative: Submit app for verification (optional)

---

### Issue: OAuth consent screen asking for organization approval

**Solution:**
1. If "Internal" app: Contact your Google Workspace admin
2. If "External" app: Add your email to "Test users"
3. Or use personal Google account instead

---

### Issue: "invalid_grant" error

**Solutions:**
1. Delete `token.json`: `Remove-Item C:\Users\gpoli\GIT\AI_agents\token.json`
2. Re-run authentication
3. Browser will open again
4. Grant permission again

---

## 📊 Summary

### What You Have (Service Account)
```
✅ vsa-anythingllm-project-ab7c8caf8c47.json
✅ Works for: Gmail, Docs, Sheets, Slides, Drive, Calendar, Forms, Meet, Cloud Run, Analytics
✅ 82 APIs enabled
✅ No user interaction needed
```

### What You Need (OAuth for Tasks)
```
❌ credentials.json (download from Google Cloud Console)
❌ token.json (created automatically on first auth)
❌ Works for: Google Tasks ONLY
❌ Requires browser sign-in ONCE
```

### Why Tasks is Special
```
🔹 Google Tasks = Personal data (no organization/shared concept)
🔹 Requires explicit user consent
🔹 Cannot use service account
🔹 OAuth 2.0 is the ONLY way
```

---

## 🎯 Your Next Action

**RIGHT NOW:**

1. Go to Google Cloud Console (already open)
2. Click "Create Credentials" → "OAuth 2.0 Client ID"
3. Application type: **"Desktop app"**
4. Name: `AI Agents - Google Tasks`
5. Click "Create"
6. Download JSON → Save as `credentials.json`
7. Move to `C:\Users\gpoli\GIT\AI_agents\credentials.json`

**Then run:**
```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from google_workspace.google_tasks import google_tasks_list_task_lists; print(google_tasks_list_task_lists())"
```

Browser opens → Sign in → Grant permission → Done! ✅

---

**Last Updated:** October 28, 2025  
**Version:** 1.0.0  
**Status:** Ready for OAuth setup
