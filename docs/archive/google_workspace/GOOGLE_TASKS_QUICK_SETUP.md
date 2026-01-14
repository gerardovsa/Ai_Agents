# 🔐 Google Tasks OAuth Setup - Quick Guide

## STEP 1: Create OAuth 2.0 Credentials

**Browser should now be open at:** https://console.cloud.google.com/apis/credentials?project=vsa-anythingllm-project

### Actions to take:

1. **Click "Create Credentials"** button at top
2. **Select "OAuth 2.0 Client ID"**
3. **If prompted about consent screen:**
   - Click "Configure Consent Screen"
   - Select "Internal" (if G Suite) or "External"
   - Fill in: App name = "AI Agents Platform"
   - User support email = your email
   - Developer contact = your email
   - Click "Save and Continue"
   - Skip Scopes section (click "Save and Continue")
   - Click "Back to Dashboard"
   - Return to Credentials page

4. **Create OAuth Client:**
   - Application type: **Desktop app**
   - Name: **"AI Agents - Google Tasks"**
   - Click **"Create"**

5. **Download credentials:**
   - Click the **Download icon** (⬇️) next to your new OAuth client
   - Save file as: `C:\Users\gpoli\GIT\AI_agents\credentials.json`

---

## STEP 2: Verify credentials.json

Run this to check if file exists:

```powershell
Test-Path C:\Users\gpoli\GIT\AI_agents\credentials.json
```

**Expected:** `True`

If False, download the credentials.json file and save it in the AI_agents folder.

---

## STEP 3: Test Authentication

Run this command to trigger first-time OAuth flow:

```powershell
cd C:\Users\gpoli\GIT\AI_agents
python -c "from google_workspace.google_tasks import google_tasks_list_task_lists; print(google_tasks_list_task_lists())"
```

**What happens:**
1. Browser opens automatically
2. Sign in with your Google account
3. Click "Allow" to grant permissions
4. Browser closes
5. Token saved to `token.json`
6. Shows your task lists

---

## STEP 4: Update .env file

```powershell
# Copy .env.master to .env if not done
if (!(Test-Path .env)) { Copy-Item .env.master .env }

# Verify Google Tasks config in .env
Get-Content .env | Select-String "GOOGLE_TASKS"
```

**Should show:**
```
GOOGLE_TASKS_CREDENTIALS_FILE=C:\Users\gpoli\GIT\AI_agents\credentials.json
GOOGLE_TASKS_TOKEN_FILE=C:\Users\gpoli\GIT\AI_agents\token.json
GOOGLE_TASKS_SCOPES=https://www.googleapis.com/auth/tasks
```

---

## ✅ Once Setup Complete:

Test via CHAT:
```powershell
CHAT List my Google Tasks
CHAT Create a task "Review Google Meet integration" in my task list
```

---

## 🚀 Then Move to Google Meet Implementation

After Google Tasks is working, we'll create Google Meet tools!

**Last Updated:** October 28, 2025
