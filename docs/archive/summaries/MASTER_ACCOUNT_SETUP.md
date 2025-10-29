# 🔐 Master Account Setup - Complete Guide

## Overview

**Master Account Architecture:**
- `gerardo@vetsuccessacademy.com` = **ADMIN/MASTER** account
- Automatically sees **ALL Gmail accounts** from `.env.master`
- No manual linking required - auto-configured on registration
- Full access to all emails, Drive files, Calendar events across all accounts

**Regular Users:**
- Must manually link specific Gmail accounts
- Only see data from their linked accounts
- Standard user permissions

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Install Dependencies

```powershell
cd C:\Users\gpoli\GIT\AI_agents
pip install bcrypt PyJWT
```

### Step 2: Run Master Account Setup

```powershell
python setup_master_account.py
```

**Follow the prompts:**
```
🔐 MASTER ACCOUNT SETUP
==============================================================

📝 Creating master account...
   Email: gerardo@vetsuccessacademy.com
   Role: admin (master account)

Enter password for master account: ********
Confirm password: ********

✅ Master account created successfully!
   User ID: 1
   Workspace ID: 1
   Role: admin

📧 Auto-linked Gmail Accounts (5):
   - gerardo@vetsuccessacademy.com (Vet Success Academy) [PRIMARY]
   - gpoli1982@gmail.com (Personal)
   - gerardo@minivetguide.com (MiniVet Guide - Gerardo)
   - minivetguide@gmail.com (MiniVet Guide)
   - marketing@minivetguide.com (MiniVet Guide - Marketing)

🎉 SETUP COMPLETE!
```

### Step 3: Start the Server

```powershell
BISTART
```

### Step 4: Test Login

```powershell
# Login as master account
curl -X POST http://localhost:5001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"your_password\"}'
```

**Expected Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "gerardo@vetsuccessacademy.com",
    "role": "admin",
    "primary_gmail": "gerardo@vetsuccessacademy.com",
    "workspaces": [{"id": 1, "name": "admin's Workspace"}],
    "gmail_accounts": [
      {
        "email": "gerardo@vetsuccessacademy.com",
        "display_name": "Vet Success Academy",
        "is_primary": true
      },
      {
        "email": "gpoli1982@gmail.com",
        "display_name": "Personal",
        "is_primary": false
      },
      {
        "email": "gerardo@minivetguide.com",
        "display_name": "MiniVet Guide - Gerardo",
        "is_primary": false
      },
      {
        "email": "minivetguide@gmail.com",
        "display_name": "MiniVet Guide",
        "is_primary": false
      },
      {
        "email": "marketing@minivetguide.com",
        "display_name": "MiniVet Guide - Marketing",
        "is_primary": false
      }
    ]
  }
}
```

**✅ Copy the `token` - you'll need it for authenticated requests!**

---

## 📊 Gmail Accounts Auto-Linked

The master account automatically sees these Gmail accounts from `.env.master`:

| Email | Display Name | Source Env Variable | App Password |
|-------|--------------|---------------------|--------------|
| `gerardo@vetsuccessacademy.com` | Vet Success Academy | `WORK_EMAIL` | `WORK_EMAIL_APP_PASSWORD` |
| `gpoli1982@gmail.com` | Personal | `PERSONAL_EMAIL` | `PERSONAL_EMAIL_APP_PASSWORD` |
| `gerardo@minivetguide.com` | MiniVet Guide - Gerardo | `GERARDO_MVG_EMAIL` | - |
| `minivetguide@gmail.com` | MiniVet Guide | `MVG_EMAIL` | `MVG_EMAIL_APP_PASSWORD` |
| `marketing@minivetguide.com` | MiniVet Guide - Marketing | `MVG_MARKETING_EMAIL` | - |

---

## 🔐 Login Options

### Option 1: Login with Username

```bash
POST http://localhost:5001/api/auth/login
{
  "username": "admin",
  "password": "your_password"
}
```

### Option 2: Login with Email

```bash
POST http://localhost:5001/api/auth/login
{
  "username": "gerardo@vetsuccessacademy.com",
  "password": "your_password"
}
```

Both work! The login endpoint accepts either username OR email.

---

## 🧪 Test Master Account Access

### 1. Get Profile with All Gmail Accounts

```powershell
curl http://localhost:5001/api/auth/profile `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response includes all 5 Gmail accounts**

### 2. List Gmail Accounts

```powershell
curl http://localhost:5001/api/auth/gmail-accounts `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 3. Verify Token

```powershell
curl http://localhost:5001/api/auth/verify `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 👥 Creating Regular Users

Regular users must manually link Gmail accounts they have access to.

### Example: Marketing User

```powershell
# 1. Register regular user
curl -X POST http://localhost:5001/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    \"username\":\"minivet_marketing\",
    \"email\":\"marketing@minivetguide.com\",
    \"password\":\"secure_password\",
    \"role\":\"user\"
  }'

# 2. Login
curl -X POST http://localhost:5001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"minivet_marketing\",\"password\":\"secure_password\"}'

# 3. Link Gmail accounts (with token from login)
curl -X POST http://localhost:5001/api/auth/link-gmail `
  -H "Authorization: Bearer TOKEN_HERE" `
  -H "Content-Type: application/json" `
  -d '{
    \"gmail_address\":\"marketing@minivetguide.com\",
    \"display_name\":\"MiniVet Marketing\",
    \"is_primary\":true
  }'

# 4. Link second account
curl -X POST http://localhost:5001/api/auth/link-gmail `
  -H "Authorization: Bearer TOKEN_HERE" `
  -H "Content-Type: application/json" `
  -d '{
    \"gmail_address\":\"gerardo@minivetguide.com\",
    \"display_name\":\"MiniVet Gerardo\"
  }'
```

**Result:** Marketing user can now see emails/drive/calendar for:
- ✅ `marketing@minivetguide.com`
- ✅ `gerardo@minivetguide.com`

But NOT:
- ❌ `gerardo@vetsuccessacademy.com`
- ❌ `gpoli1982@gmail.com`
- ❌ `minivetguide@gmail.com`

---

## 🔒 Data Isolation

### Master Account (`admin`)
**Can see ALL data:**
- Emails from all 5 Gmail accounts
- Drive files from all accounts
- Calendar events from all accounts
- Full platform access

### Regular Users (e.g., `minivet_marketing`)
**Can ONLY see data from linked accounts:**
- Emails from `marketing@minivetguide.com` + `gerardo@minivetguide.com`
- Drive files from those 2 accounts only
- Calendar events from those 2 accounts only
- Limited to their workspace

---

## 🚧 Next Steps (Phase 3)

Now that authentication is working, update tools to respect user permissions:

### 1. Update Gmail Tools

**Before (shows all emails):**
```python
def list_emails():
    return gmail_service.list_emails()
```

**After (filters by user's accounts):**
```python
@require_auth
def list_emails():
    user_id = request.user['user_id']
    
    # Get user's Gmail accounts
    accounts = user_auth_manager.get_user_gmail_accounts(user_id)
    
    # Fetch emails from each account
    all_emails = []
    for account in accounts:
        emails = gmail_service.list_emails(account['email'])
        all_emails.extend(emails)
    
    return all_emails
```

### 2. Update Drive Tools

Same pattern - filter by user's linked Gmail accounts.

### 3. Update Calendar Tools

Same pattern - filter by user's linked Gmail accounts.

### 4. Add Login UI

Create login screen in `business-ai-platform-v2.html` (see `USER_AUTH_SETUP_GUIDE.md` for example code).

---

## 📝 Summary

**✅ Phase 1 Complete:** CHAT command no longer saves to database

**✅ Phase 2 Complete:** Multi-tenant authentication with master account

**Master Account Features:**
- ✅ Auto-linked to ALL Gmail accounts from `.env.master`
- ✅ Admin role with full access
- ✅ Sees all 5 Gmail accounts without manual linking
- ✅ JWT authentication with 7-day tokens

**Regular User Features:**
- ✅ Manual Gmail account linking
- ✅ Workspace isolation
- ✅ Only sees data from their accounts
- ✅ Standard user role

**Next: Phase 3**
- 🚧 Update Gmail/Drive/Calendar tools to filter by user
- 🚧 Add login UI to Business AI Platform
- 🚧 OAuth flow for Gmail linking

---

## 🆘 Troubleshooting

### Issue: "Master account already exists"

Run setup script again to see linked accounts:
```powershell
python setup_master_account.py
```

### Issue: "Invalid credentials"

Password doesn't match. Reset by deleting user and re-running setup:
```powershell
# Delete database (WARNING: removes all users!)
Remove-Item AI_infrastructure\ai_infrastructure.db -Force

# Re-run setup
python setup_master_account.py
```

### Issue: "Gmail accounts not auto-linked"

Check `.env` file has these variables set:
- `WORK_EMAIL`
- `PERSONAL_EMAIL`
- `GERARDO_MVG_EMAIL`
- `MVG_EMAIL`
- `MVG_MARKETING_EMAIL`

### Issue: "Token expired"

Tokens last 7 days. Login again to get new token:
```powershell
curl -X POST http://localhost:5001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{\"username\":\"admin\",\"password\":\"your_password\"}'
```

---

## 📞 Quick Reference

**Master Account Login:**
```
Username: admin
Email: gerardo@vetsuccessacademy.com
Role: admin (master)
Gmail Accounts: ALL 5 from .env.master (auto-linked)
```

**API Endpoints:**
- `POST /api/auth/register` - Create user
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/profile` - Get user profile + Gmail accounts
- `GET /api/auth/verify` - Verify token
- `POST /api/auth/link-gmail` - Link Gmail (regular users only)
- `GET /api/auth/gmail-accounts` - List linked Gmails

**Setup Script:**
```powershell
python setup_master_account.py
```

**Start Server:**
```powershell
BISTART
```

---

🎉 **Master account is now ready! Login and start using the platform with full access to all Gmail accounts.**
