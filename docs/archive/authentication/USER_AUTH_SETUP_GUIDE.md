# 🔐 User Authentication & Multi-Tenant System

## Overview

Complete user authentication system with Gmail OAuth integration and workspace isolation. Each user can:
- ✅ Register with username/password
- ✅ Link multiple Gmail accounts
- ✅ See only their own data (emails, Drive files, etc.)
- ✅ Separate workspaces per user

---

## 🚀 Phase 1: CHAT Command No Longer Saves (COMPLETED ✅)

**Changes Made:**
1. `unified_session_manager.py` - Added `source` parameter ('cli' vs 'ui')
2. CLI sessions (CHAT command) are now **in-memory only** - NOT saved to database
3. UI sessions (Business AI Platform) continue to save normally

**Test It:**
```powershell
# Run CHAT command
CHAT What's the weather?

# Check database - no new session created!
python -c "import sqlite3; conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db'); print(conn.execute('SELECT COUNT(*) FROM sessions WHERE metadata LIKE \"%cli%\"').fetchone())"
```

---

## 🔐 Phase 2: User Authentication System (NEW)

### Architecture

```
User: gerardo@vetsuccessacademy.com
├── Gmail Accounts:
│   └── gerardo@vetsuccessacademy.com (Primary)
├── Workspace ID: 1
└── Can See: All emails/drive/calendar for gerardo@vetsuccessacademy.com

User: marketing@minivetguide.com
├── Gmail Accounts:
│   ├── gerardo@minivetguide.com (MiniVet Gerardo)
│   └── marketing@minivetguide.com (MiniVet Marketing) [Primary]
├── Workspace ID: 2
└── Can See: All emails/drive/calendar for BOTH Gmail accounts
```

---

## 📋 Database Schema

### New Tables Created:

**1. `users` (Enhanced)**
```sql
- id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash (bcrypt)
- role ('admin' | 'user')
- primary_gmail
- created_at
- last_active
- metadata (JSON)
```

**2. `user_gmail_accounts`**
```sql
- id (Primary Key)
- user_id (Foreign Key → users)
- gmail_address
- display_name ("MiniVet Marketing")
- access_token (OAuth)
- refresh_token (OAuth)
- is_primary (Boolean)
- created_at
```

**3. `user_sessions`**
```sql
- id (Primary Key)
- user_id (Foreign Key)
- token (JWT)
- ip_address
- user_agent
- created_at
- expires_at (7 days)
```

**4. `workspaces` (Updated)**
```sql
- id (Primary Key)
- user_id (Foreign Key → users)
- name
- description
- created_at
- metadata (JSON)
```

---

## 🛠️ Installation

### 1. Install Dependencies

```powershell
pip install bcrypt PyJWT
```

**Or update requirements.txt:**
```txt
bcrypt==4.0.1
PyJWT==2.8.0
```

### 2. Set JWT Secret (Production)

Add to `.env`:
```
JWT_SECRET=your-super-secret-key-change-this-in-production
```

### 3. Initialize Database

Run the setup script:
```powershell
python AI_infrastructure/auth/user_auth.py
```

Or start the server (auto-initializes):
```powershell
BISTART
```

---

## 📡 API Endpoints

### 1. **Register User**

```bash
POST http://localhost:5001/api/auth/register
Content-Type: application/json

{
  "username": "gerardo",
  "email": "gerardo@vetsuccessacademy.com",
  "password": "secure_password",
  "primary_gmail": "gerardo@vetsuccessacademy.com"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "workspace_id": 1,
  "username": "gerardo",
  "email": "gerardo@vetsuccessacademy.com"
}
```

---

### 2. **Login**

```bash
POST http://localhost:5001/api/auth/login
Content-Type: application/json

{
  "username": "gerardo",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "gerardo",
    "email": "gerardo@vetsuccessacademy.com",
    "role": "user",
    "primary_gmail": "gerardo@vetsuccessacademy.com",
    "workspaces": [{"id": 1, "name": "gerardo's Workspace"}],
    "gmail_accounts": []
  }
}
```

**Copy the `token` - you'll need it for all authenticated requests!**

---

### 3. **Link Gmail Account**

```bash
POST http://localhost:5001/api/auth/link-gmail
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN_HERE

{
  "gmail_address": "marketing@minivetguide.com",
  "display_name": "MiniVet Marketing",
  "is_primary": true
}
```

**Response:**
```json
{
  "success": true,
  "gmail": "marketing@minivetguide.com"
}
```

---

### 4. **Get User Profile**

```bash
GET http://localhost:5001/api/auth/profile
Authorization: Bearer YOUR_TOKEN_HERE
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "user_id": 1,
    "username": "gerardo",
    "email": "gerardo@vetsuccessacademy.com",
    "role": "user",
    "gmail_accounts": [
      {
        "email": "gerardo@vetsuccessacademy.com",
        "display_name": "gerardo@vetsuccessacademy.com",
        "is_primary": false
      },
      {
        "email": "marketing@minivetguide.com",
        "display_name": "MiniVet Marketing",
        "is_primary": true
      }
    ],
    "workspace_id": 1
  }
}
```

---

### 5. **Verify Token**

```bash
GET http://localhost:5001/api/auth/verify
Authorization: Bearer YOUR_TOKEN_HERE
```

**Response:**
```json
{
  "success": true,
  "user": {
    "user_id": 1,
    "username": "gerardo",
    "email": "gerardo@vetsuccessacademy.com",
    "role": "user"
  }
}
```

---

## 🧪 Testing Workflow

### Example 1: Gerardo @ Vet Success Academy

```powershell
# 1. Register
curl -X POST http://localhost:5001/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{"username":"gerardo","email":"gerardo@vetsuccessacademy.com","password":"test123"}'

# 2. Login (copy the token!)
curl -X POST http://localhost:5001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"gerardo","password":"test123"}'

# 3. View profile
curl http://localhost:5001/api/auth/profile `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### Example 2: Marketing @ MiniVet Guide

```powershell
# 1. Register
curl -X POST http://localhost:5001/api/auth/register `
  -H "Content-Type: application/json" `
  -d '{"username":"minivet_marketing","email":"marketing@minivetguide.com","password":"test123"}'

# 2. Login
curl -X POST http://localhost:5001/api/auth/login `
  -H "Content-Type: application/json" `
  -d '{"username":"minivet_marketing","password":"test123"}'

# 3. Link second Gmail
curl -X POST http://localhost:5001/api/auth/link-gmail `
  -H "Authorization: Bearer YOUR_TOKEN_HERE" `
  -H "Content-Type: application/json" `
  -d '{"gmail_address":"gerardo@minivetguide.com","display_name":"MiniVet Gerardo"}'

# 4. View all linked accounts
curl http://localhost:5001/api/auth/gmail-accounts `
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🔒 Security Features

✅ **Password Hashing**: bcrypt with salt  
✅ **JWT Tokens**: 7-day expiry, server-side validation  
✅ **Session Management**: Tokens stored in database  
✅ **Protected Routes**: `@require_auth` decorator  
✅ **Workspace Isolation**: Each user has separate workspace_id  
✅ **OAuth Ready**: Token storage for Gmail API access  

---

## 🚧 Next Steps (Phase 3)

### Integrate with Existing Tools

Update Gmail/Drive/Calendar tools to:
1. Accept `user_id` or `workspace_id`
2. Filter results by user's linked Gmail accounts
3. Only show data the user has access to

**Example:**
```python
# OLD (shows all emails from all accounts)
def list_emails():
    return gmail_service.list_emails()

# NEW (shows only user's emails)
def list_emails(user_id):
    gmail_accounts = get_user_gmail_accounts(user_id)
    emails = []
    for account in gmail_accounts:
        emails += gmail_service.list_emails(account['email'])
    return emails
```

---

## 📊 Database Migration Script

Create users from existing data:

```python
# migration_create_users.py
import sqlite3
from AI_infrastructure.auth.user_auth import user_auth_manager

# Create default admin user
result = user_auth_manager.register_user(
    username='admin',
    email='admin@business-ai-platform.com',
    password='change-me-in-production'
)

print(f"Admin user created: {result}")

# Link existing Gmail accounts
user_id = result['user_id']
gmail_accounts = [
    'gerardo@vetsuccessacademy.com',
    'gerardo@minivetguide.com',
    'marketing@minivetguide.com'
]

for gmail in gmail_accounts:
    user_auth_manager.link_gmail_account(
        user_id=user_id,
        gmail_address=gmail,
        display_name=gmail
    )
    print(f"✅ Linked: {gmail}")
```

---

## 🎨 UI Integration

### Login Screen (Next Step)

Add to `business-ai-platform-v2.html`:

```html
<div id="login-screen">
  <h2>Business AI Platform Login</h2>
  <form id="login-form">
    <input type="text" id="username" placeholder="Username">
    <input type="password" id="password" placeholder="Password">
    <button type="submit">Login</button>
  </form>
</div>

<script>
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const response = await fetch('http://localhost:5001/api/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      username: document.getElementById('username').value,
      password: document.getElementById('password').value
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Store token
    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('user_profile', JSON.stringify(data.user));
    
    // Hide login, show main app
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('main-app').style.display = 'block';
    
    // Load user's Gmail accounts
    loadUserGmailAccounts(data.user.gmail_accounts);
  }
});

// Add token to all API requests
function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('auth_token');
  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
}
</script>
```

---

## ✅ Summary

**Phase 1 Complete:**
- ✅ CHAT command no longer saves to database
- ✅ CLI sessions are in-memory only

**Phase 2 Complete:**
- ✅ User registration & login
- ✅ Password hashing (bcrypt)
- ✅ JWT authentication
- ✅ Gmail account linking
- ✅ Workspace isolation
- ✅ API endpoints ready

**Phase 3 To-Do:**
- 🚧 Update Gmail/Drive/Calendar tools to filter by user
- 🚧 Add login UI to Business AI Platform
- 🚧 Migrate existing data to user workspaces
- 🚧 Add OAuth flow for Gmail linking

---

## 📞 Support

Questions? Check:
1. Database: `AI_infrastructure/ai_infrastructure.db`
2. Auth code: `AI_infrastructure/auth/user_auth.py`
3. Routes: `AI_infrastructure/routes/auth_routes.py`

**Test the system:**
```powershell
# Quick test
python -c "from AI_infrastructure.auth.user_auth import user_auth_manager; print(user_auth_manager.register_user('test', 'test@example.com', 'password123'))"
```
