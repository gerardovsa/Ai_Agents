# 🔑 Google Tasks Authentication Setup Guide

## Overview

Google Tasks API has been connected to `.env.master` for centralized authentication management.

**Why OAuth 2.0 (not Service Account)?**
- Google Tasks API requires **user-specific authentication** (OAuth 2.0)
- Tasks are personal to each user - service accounts can't access user tasks
- Service accounts work for Docs/Sheets/Drive (organization-level data)
- Tasks require interactive user consent

---

## 📋 Configuration Added to `.env.master`

```bash
# ========================================
# GOOGLE TASKS AUTHENTICATION
# ========================================
# Used by: Google Tasks API (14 tools)
# Requires: OAuth 2.0 credentials for personal task access
# Note: Tasks API requires user authentication, not service account
# 
# How to set up:
# 1. Go to: https://console.cloud.google.com/apis/credentials
# 2. Select project: colab-ai-processor or vsa-anythingllm-project
# 3. Create OAuth 2.0 Client ID (Desktop app)
# 4. Download credentials.json to: C:\Users\gpoli\GIT\AI_agents\credentials.json
# 5. First run will open browser for authentication
# 6. token.json will be saved automatically
#
# Paths:
GOOGLE_TASKS_CREDENTIALS_FILE=C:\Users\gpoli\GIT\AI_agents\credentials.json
GOOGLE_TASKS_TOKEN_FILE=C:\Users\gpoli\GIT\AI_agents\token.json
GOOGLE_TASKS_SCOPES=https://www.googleapis.com/auth/tasks

# Alternative: Use existing OAuth credentials
# GOOGLE_TASKS_CLIENT_ID=${GOOGLE_OAUTH_CLIENT_ID}
# GOOGLE_TASKS_CLIENT_SECRET=${GOOGLE_OAUTH_CLIENT_SECRET}
```

---

## 🚀 Setup Instructions

### Step 1: Create OAuth 2.0 Credentials

1. **Go to Google Cloud Console:**
   ```
   https://console.cloud.google.com/apis/credentials
   ```

2. **Select Project:**
   - Choose: `colab-ai-processor` or `vsa-anythingllm-project`
   - Or use your existing project with Tasks API enabled

3. **Create OAuth Credentials:**
   - Click **"Create Credentials"** → **"OAuth 2.0 Client ID"**
   - Application type: **"Desktop app"**
   - Name: **"AI Agents - Google Tasks"**
   - Click **"Create"**

4. **Download Credentials:**
   - Click **"Download JSON"** (download icon)
   - Save as: `C:\Users\gpoli\GIT\AI_agents\credentials.json`

### Step 2: Enable Google Tasks API

1. **Go to APIs & Services:**
   ```
   https://console.cloud.google.com/apis/library
   ```

2. **Search for "Google Tasks API"**

3. **Click "Enable"**

### Step 3: Configure Environment Variables

1. **Copy `.env.master` to `.env`** (if not done):
   ```powershell
   Copy-Item .env.master .env
   ```

2. **Verify paths in `.env`:**
   ```bash
   GOOGLE_TASKS_CREDENTIALS_FILE=C:\Users\gpoli\GIT\AI_agents\credentials.json
   GOOGLE_TASKS_TOKEN_FILE=C:\Users\gpoli\GIT\AI_agents\token.json
   GOOGLE_TASKS_SCOPES=https://www.googleapis.com/auth/tasks
   ```

3. **Update paths** if credentials.json is in a different location

### Step 4: First-Time Authentication

1. **Run AI Agent or directly test Google Tasks:**
   ```powershell
   cd C:\Users\gpoli\GIT\AI_agents
   python -c "from google_workspace.google_tasks import google_tasks_list_task_lists; print(google_tasks_list_task_lists())"
   ```

2. **Browser will open automatically** with Google OAuth consent screen

3. **Sign in** with your Google account (the one with tasks)

4. **Grant permissions** to access Google Tasks

5. **Token saved automatically** to `token.json`

6. **Future runs** will use saved token (no browser required)

---

## 🔧 Code Changes

### `google_workspace/google_tasks.py`

**Before:**
```python
def build_tasks_service():
    token_path = Path(__file__).parent.parent / 'token.json'
    credentials_path = Path(__file__).parent.parent / 'credentials.json'
```

**After (using .env variables):**
```python
def build_tasks_service():
    # Get paths from environment or use defaults
    token_path = Path(os.getenv('GOOGLE_TASKS_CREDENTIALS_FILE', 
                                str(Path(__file__).parent.parent / 'token.json')))
    credentials_path = Path(os.getenv('GOOGLE_TASKS_CREDENTIALS_FILE',
                                     str(Path(__file__).parent.parent / 'credentials.json')))
    
    # Get scopes from environment
    scopes_env = os.getenv('GOOGLE_TASKS_SCOPES', 'https://www.googleapis.com/auth/tasks')
    scopes = [s.strip() for s in scopes_env.split(',')]
    
    print(f"🔑 Google Tasks Auth Config:")
    print(f"   Token file: {token_path}")
    print(f"   Credentials file: {credentials_path}")
    print(f"   Scopes: {scopes}")
```

**Enhanced Error Messages:**
- Clear instructions when `credentials.json` is missing
- Step-by-step setup guide in error message
- Links to Google Cloud Console

---

## 🧪 Testing

### Test 1: List Task Lists

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from google_workspace.google_tasks import google_tasks_list_task_lists; import json; print(json.dumps(google_tasks_list_task_lists(), indent=2))"
```

**Expected Output:**
```json
{
  "task_lists": [
    {
      "id": "MTU...",
      "title": "My Tasks",
      "updated": "2025-10-28T..."
    }
  ],
  "count": 1
}
```

### Test 2: Create Task via CHAT

```powershell
CHAT Create a task "Review Google Slides implementation" in my default task list
```

**Expected:**
- AI Agent recognizes Google Tasks tool
- Creates task successfully
- Returns task ID and confirmation

### Test 3: SMART Bundled Action

```powershell
CHAT Create a project plan for "Q1 2026 Goals" with 5 tasks: Research, Planning, Development, Testing, Launch
```

**Expected:**
- Uses `google_tasks_create_project_plan` SMART action
- Creates task list + 5 tasks in one operation
- Returns full project structure

---

## 🔒 Security Best Practices

### Token Management

1. **Never commit tokens to Git:**
   ```gitignore
   # Already in .gitignore
   token.json
   credentials.json
   .env
   ```

2. **Token storage location:**
   - Default: `C:\Users\gpoli\GIT\AI_agents\token.json`
   - Customizable via `GOOGLE_TASKS_TOKEN_FILE`

3. **Token refresh:**
   - Tokens expire after ~1 hour
   - Automatically refreshed using refresh token
   - Refresh tokens last ~6 months
   - Re-authenticate if refresh fails

### Credentials Management

1. **credentials.json** contains:
   - Client ID (public)
   - Client Secret (private - treat as password)
   - Never share credentials.json publicly

2. **token.json** contains:
   - Access token (expires hourly)
   - Refresh token (expires in months)
   - User email
   - More sensitive than credentials.json

3. **Revoke access** if compromised:
   ```
   https://myaccount.google.com/permissions
   ```

---

## 🛠️ Troubleshooting

### Issue: "credentials.json not found"

**Solution:**
1. Download OAuth 2.0 credentials from Google Cloud Console
2. Save as `credentials.json` in project root
3. Or set custom path: `GOOGLE_TASKS_CREDENTIALS_FILE=/path/to/credentials.json`

---

### Issue: "Token expired and refresh failed"

**Solution:**
1. Delete `token.json`
2. Re-run authentication (browser will open)
3. Grant permissions again
4. New token will be saved

---

### Issue: "Access denied" or "Insufficient permissions"

**Cause:** OAuth consent screen restrictions

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Check "Publishing status"
3. If "Testing" mode:
   - Add your email to "Test users"
   - Or publish app (if ready for production)

---

### Issue: "Redirect URI mismatch"

**Cause:** OAuth redirect URI not configured

**Solution:**
1. Go to: https://console.cloud.google.com/apis/credentials
2. Edit OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   ```
   http://localhost:8080/
   http://localhost:8090/
   http://localhost:0/
   ```

---

## 📊 Available Google Tasks Tools

### Core Tools (10)
1. `google_tasks_list_task_lists` - List all task lists
2. `google_tasks_create_task_list` - Create new task list
3. `google_tasks_get_task_list` - Get task list details
4. `google_tasks_delete_task_list` - Delete task list
5. `google_tasks_list_tasks` - List tasks in list
6. `google_tasks_create_task` - Create new task
7. `google_tasks_get_task` - Get task details
8. `google_tasks_update_task` - Update task
9. `google_tasks_complete_task` - Mark task as complete
10. `google_tasks_delete_task` - Delete task

### SMART Bundled Actions (4)
1. `google_tasks_create_project_plan` - Create task list with multiple tasks
2. `google_tasks_create_daily_checklist` - Create daily recurring checklist
3. `google_tasks_bulk_create_tasks` - Create multiple tasks efficiently
4. `google_tasks_organize_by_priority` - Sort and organize tasks by priority

---

## 🔄 Comparison: OAuth vs Service Account

| Feature | OAuth 2.0 (Tasks) | Service Account (Docs/Sheets) |
|---------|-------------------|-------------------------------|
| **Use Case** | Personal user data | Organization data |
| **Auth Flow** | Interactive (browser) | Automatic (JSON key) |
| **Token Type** | User access token | JWT token |
| **Expiration** | 1 hour (auto-refresh) | 1 hour (auto-generated) |
| **Permissions** | User grants consent | Admin grants domain-wide |
| **Best For** | Tasks, Gmail, Calendar | Docs, Sheets, Drive |

**Why Tasks needs OAuth:**
- Tasks are **personal** to each user
- No way to access "team tasks" via service account
- Each user must authenticate individually
- Tasks API doesn't support service account delegation

---

## 🎯 Next Steps

1. ✅ **Google Tasks authentication added to `.env.master`**
2. ✅ **`google_tasks.py` updated to use environment variables**
3. ⏳ **Download credentials.json** from Google Cloud Console
4. ⏳ **Run first authentication** (browser OAuth flow)
5. ⏳ **Test with CHAT command**

---

## 📚 Documentation Links

- **Google Tasks API:** https://developers.google.com/tasks/reference/rest
- **OAuth 2.0 Setup:** https://developers.google.com/identity/protocols/oauth2
- **Google Cloud Console:** https://console.cloud.google.com/
- **API Library:** https://console.cloud.google.com/apis/library
- **Credentials:** https://console.cloud.google.com/apis/credentials

---

**Last Updated:** October 28, 2025  
**Status:** ✅ Connected to .env.master  
**Ready For:** First-time authentication setup
