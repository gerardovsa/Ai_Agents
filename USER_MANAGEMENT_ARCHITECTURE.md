# User Management Architecture - Current vs. Proposed

**Date:** November 10, 2025  
**Status:** 🔄 Planning Phase

---

## 🎯 Your Vision (What You Want):

### **Parent-Child User Hierarchy:**

```
PARENT ACCOUNT (OAuth)
├─ john@company.com (Google OAuth)
│  ├─ Sub-User: employee_001 (username/password)
│  ├─ Sub-User: employee_002 (username/password)
│  └─ Sub-User: contractor_john (username/password)
│
└─ jane@company.com (Microsoft OAuth)
   ├─ Sub-User: intern_sarah (username/password)
   └─ Sub-User: temp_mike (username/password)
```

### **Key Principles:**

1. **Only OAuth creates parent accounts**
   - ✅ Google Sign-In → Parent account
   - ✅ Microsoft Sign-In → Parent account
   - ❌ No manual registration on login screen

2. **Parent accounts create sub-users**
   - Parent logs in via OAuth
   - Goes to Account Settings → User Management
   - Creates sub-users with username/password
   - Sub-users inherit parent's OAuth credentials

3. **Sub-users login with username/password**
   - Sub-users don't see OAuth buttons (they can't create their own OAuth accounts)
   - They login with username/password assigned by parent
   - Behind the scenes: Use parent's Google/Microsoft OAuth tokens

4. **Role-based access control**
   - Parent can assign roles to sub-users (Admin, User, Read-only, etc.)
   - Sub-users have limited permissions based on role
   - Sub-users see data from parent's scope + their own restrictions

---

## 📋 Current System (What Exists Today):

### ✅ **Already Built:**

#### 1. **User Profile Dropdown** (Top Right Corner)
```html
Location: UI line 6470-6750
Components:
  - User avatar/name display
  - Dropdown menu with:
    ├─ Account Settings (opens modal)
    ├─ Gmail SMTP Accounts
    ├─ Re-authenticate Account
    ├─ Logout
```

#### 2. **Account Settings Modal** (Full Settings Panel)
```html
Location: UI line 8125-8600
Sections:
  ✅ Personalisation
     - Nickname
     - Communication style
     - Response detail level
     - Auth platform preference
     - Location/timezone
  
  ✅ Connected Accounts
     - OAuth platforms (Google/Microsoft)
     - Re-authentication buttons
     - Account status
  
  ✅ Gmail SMTP Accounts
     - Link Gmail accounts manually
     - View connected accounts
     - Remove accounts
  
  ✅ Preferences
     - Interface settings
     - Notification settings
     - Data handling
```

#### 3. **Backend Authentication** (API Endpoints)
```python
Location: AI_infrastructure/routes/auth_routes.py

✅ Registration: POST /api/auth/register
   - Creates user with username/email/password
   - Role-based (admin/user)
   - Password hashing with bcrypt
   
✅ Login: POST /api/auth/login
   - Username/password authentication
   - Returns JWT token
   
✅ OAuth Login:
   - GET /api/auth/google/login
   - GET /api/auth/microsoft/login
   - Creates parent accounts automatically
```

#### 4. **Database Schema** (Users Table)
```sql
Location: data/ai_infrastructure.db

users table:
  ✅ id (primary key)
  ✅ username
  ✅ email
  ✅ password_hash (for local auth or OAuth marker)
  ✅ role (admin/user)
  ✅ primary_gmail
  ✅ metadata (JSON - can store parent_user_id here!)
  ✅ created_at
  ✅ last_active
  ✅ has_google_oauth
  ✅ has_microsoft_oauth
```

---

## ❌ **What's Missing (To Implement Your Vision):**

### 1. **Login Screen Modifications:**

**Current State:**
```
[ Sign in with Google ]
[ Sign in with Microsoft ]
```

**Needed:**
```
[ Sign in with Google ]     ← Creates PARENT accounts only
[ Sign in with Microsoft ]  ← Creates PARENT accounts only

──────────── OR ────────────

Username: [_____________]   ← For SUB-USERS only
Password: [_____________]   
[Login]

Note: Sub-user accounts must be created by
your organization admin in Account Settings
```

**Implementation:**
- Add username/password fields to login screen
- Add note explaining OAuth = parent, username/password = sub-user
- No "Create Account" button visible

---

### 2. **User Management Section in Account Settings:**

**Add New Section:**
```html
Account Settings Modal
├─ Personalisation
├─ Connected Accounts
├─ Gmail SMTP Accounts
├─ Preferences
└─ 👥 User Management ← NEW SECTION!
   ├─ View Sub-Users (table)
   ├─ Create Sub-User (button)
   ├─ Edit Sub-User (inline)
   └─ Delete Sub-User (inline)
```

**Sub-User Creation Form:**
```html
Create Sub-User Account

Parent Account: john@company.com (Google OAuth)
Organization: John's Workspace

Username: [employee_001____________]
Email:    [employee001@company.com_]
Password: [••••••••••••••••••••••••]
Confirm:  [••••••••••••••••••••••••]

Role: [⬇ Dropdown]
  - Admin (Full access)
  - User (Standard access)
  - Read-only (View only)
  - Custom...

OAuth Inheritance:
☑ Inherit parent's Google OAuth credentials
☑ Access parent's Google Workspace data
☐ Can create own sub-users (delegate)
☐ Can manage organization settings

[Cancel] [Create Sub-User]
```

**Sub-Users Table:**
```html
Your Sub-User Accounts (3)

┌─────────────┬──────────────────────┬─────────┬────────────┬─────────┐
│ Username    │ Email                │ Role    │ Last Login │ Actions │
├─────────────┼──────────────────────┼─────────┼────────────┼─────────┤
│ employee_001│ emp001@company.com   │ User    │ 2 hrs ago  │ [Edit] [Delete] │
│ employee_002│ emp002@company.com   │ User    │ 1 day ago  │ [Edit] [Delete] │
│ contractor_j│ john@freelance.com   │ Readonly│ Never      │ [Edit] [Delete] │
└─────────────┴──────────────────────┴─────────┴────────────┴─────────┘

[+ Create Sub-User]
```

---

### 3. **Backend API Endpoints (New):**

**Location:** `AI_infrastructure/routes/auth_routes.py`

```python
# NEW ENDPOINTS NEEDED:

@auth_bp.route('/sub-users', methods=['GET'])
@require_auth
def list_sub_users():
    """
    Get all sub-users created by this parent account
    
    Returns:
    {
        "sub_users": [
            {
                "id": 2,
                "username": "employee_001",
                "email": "emp001@company.com",
                "role": "user",
                "parent_user_id": 1,
                "created_at": "2025-11-10 10:30:00",
                "last_active": "2025-11-10 14:25:00"
            }
        ]
    }
    """
    pass


@auth_bp.route('/sub-users', methods=['POST'])
@require_auth
def create_sub_user():
    """
    Create a sub-user account
    
    POST /api/auth/sub-users
    {
        "username": "employee_001",
        "email": "emp001@company.com",
        "password": "SecurePassword123",
        "role": "user",
        "inherit_oauth": true
    }
    
    Returns:
    {
        "success": true,
        "sub_user_id": 2,
        "message": "Sub-user created successfully"
    }
    """
    pass


@auth_bp.route('/sub-users/<int:sub_user_id>', methods=['PUT'])
@require_auth
def update_sub_user(sub_user_id):
    """
    Update sub-user details (role, password, etc.)
    """
    pass


@auth_bp.route('/sub-users/<int:sub_user_id>', methods=['DELETE'])
@require_auth
def delete_sub_user(sub_user_id):
    """
    Delete a sub-user account
    """
    pass
```

---

### 4. **Database Schema Changes:**

**Option A: Add `parent_user_id` column to existing `users` table:**
```sql
ALTER TABLE users ADD COLUMN parent_user_id INTEGER;
ALTER TABLE users ADD COLUMN is_sub_user BOOLEAN DEFAULT 0;

-- Example data:
-- Parent account (OAuth):
id=1, username='john', email='john@company.com', password_hash='oauth_google', parent_user_id=NULL, is_sub_user=0

-- Sub-user accounts:
id=2, username='employee_001', email='emp001@company.com', password_hash='$2b$12...', parent_user_id=1, is_sub_user=1
id=3, username='employee_002', email='emp002@company.com', password_hash='$2b$12...', parent_user_id=1, is_sub_user=1
```

**Option B: Create separate `sub_users` table:**
```sql
CREATE TABLE sub_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_user_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,  -- References users table
    inherit_oauth BOOLEAN DEFAULT 1,
    can_create_sub_users BOOLEAN DEFAULT 0,
    custom_permissions TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Recommendation: Option A** (simpler, uses existing `users.metadata` JSON for extra fields)

---

### 5. **OAuth Credential Inheritance Logic:**

**Location:** `AI_infrastructure/auth/credential_injector.py`

```python
def get_google_credentials(self, user_id: int) -> Dict[str, str]:
    """
    Get Google OAuth credentials for user.
    If user is a sub-user, inherit from parent.
    """
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    # Check if this is a sub-user
    cursor.execute("""
        SELECT parent_user_id FROM users WHERE id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    if row and row['parent_user_id']:
        # This is a sub-user - use parent's credentials
        parent_id = row['parent_user_id']
        print(f"🔗 Sub-user {user_id} inheriting OAuth from parent {parent_id}")
        user_id = parent_id  # Switch to parent for credential lookup
    
    # Get OAuth tokens (either for user or their parent)
    cursor.execute("""
        SELECT access_token, refresh_token, token_expiry
        FROM oauth_tokens
        WHERE user_id = ? AND platform = 'google'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id,))
    
    # ... rest of credential fetching logic
```

---

## 📊 Implementation Phases:

### **Phase 1: Database Schema** (2 hours)
- ✅ Add `parent_user_id` column to users table
- ✅ Add `is_sub_user` column to users table
- ✅ Create migration script
- ✅ Test on local database

### **Phase 2: Backend API** (4 hours)
- ✅ Create sub-user creation endpoint
- ✅ Create sub-user listing endpoint
- ✅ Create sub-user update endpoint
- ✅ Create sub-user deletion endpoint
- ✅ Update credential injector for OAuth inheritance
- ✅ Add permission checks (only parent can manage their sub-users)

### **Phase 3: Frontend UI** (6 hours)
- ✅ Add User Management section to Account Settings modal
- ✅ Create sub-user creation form
- ✅ Create sub-users table with edit/delete actions
- ✅ Add username/password fields to login screen
- ✅ Add explanatory text about parent vs sub-user accounts
- ✅ Test full workflow

### **Phase 4: Testing** (2 hours)
- ✅ Test parent account creation via OAuth
- ✅ Test sub-user creation from parent account
- ✅ Test sub-user login with username/password
- ✅ Test OAuth credential inheritance
- ✅ Test permission boundaries
- ✅ Test sub-user deletion and cleanup

---

## 🎨 Current UI Interfaces Summary:

### **1. Login Screen**
```
Location: UI/business-ai-platform-v2.html (lines 6500-6650)
Current:
  - [ Sign in with Google ]
  - [ Sign in with Microsoft ]
Needs:
  - Username/password fields below OAuth buttons
  - Explanatory text
```

### **2. User Profile Dropdown**
```
Location: UI line 6470-6750
Current:
  - User avatar
  - Account Settings link
  - Gmail accounts link
  - Logout
Status: ✅ Complete (no changes needed)
```

### **3. Account Settings Modal**
```
Location: UI line 8125-8600
Current Sections:
  ✅ Personalisation
  ✅ Connected Accounts
  ✅ Gmail SMTP Accounts
  ✅ Preferences
Needs:
  ❌ User Management section (NEW)
```

### **4. Top Navigation Bar**
```
Location: UI line 6400-6500
Current:
  - Sidebar toggle
  - Settings button
  - User profile button (far right)
Status: ✅ Complete (no changes needed)
```

---

## 🔐 Authentication Flow Comparison:

### **Current Flow (All Users Equal):**
```
Login Screen
  ↓
[ Sign in with Google/Microsoft ]
  ↓
OAuth redirects
  ↓
User authenticated (JWT token)
  ↓
Access full platform
```

### **Proposed Flow (Parent-Child Hierarchy):**

**Parent Users:**
```
Login Screen
  ↓
[ Sign in with Google/Microsoft ]
  ↓
OAuth redirects
  ↓
Parent account created/logged in (JWT token)
  ↓
Access full platform
  ↓
Can create sub-users in Account Settings
```

**Sub-Users:**
```
Login Screen
  ↓
Username: employee_001
Password: ••••••••••••
  ↓
Check credentials against database
  ↓
Find parent_user_id in users table
  ↓
Sub-user authenticated (JWT token + parent reference)
  ↓
Access platform with inherited OAuth credentials
  ↓
Cannot create sub-users (unless delegated)
```

---

## 💡 Summary of What You're Asking For:

✅ **You want:**
1. **OAuth = Parent accounts ONLY** (Google/Microsoft creates the "master" account)
2. **Parents create sub-users** with username/password in Account Settings
3. **Sub-users login** with username/password (not OAuth)
4. **Sub-users inherit** parent's OAuth credentials behind the scenes
5. **Role-based permissions** for sub-users (admin/user/readonly/custom)
6. **No self-registration** on login screen (only OAuth or parent-created accounts)

✅ **What exists today:**
- Backend registration/login APIs
- Account Settings modal
- User profile dropdown
- OAuth integration (Google/Microsoft)
- JWT authentication
- Password hashing (bcrypt)

❌ **What's missing:**
- User Management section in Account Settings
- Sub-user creation UI
- Parent-child relationship in database
- OAuth credential inheritance logic
- Username/password fields on login screen (for sub-users)

---

## 🚀 Ready to Implement?

Would you like me to:
1. **Start with Phase 1** (Database schema changes)?
2. **Create the full implementation plan** with code examples?
3. **Show you mockups** of the new UI components?
4. **Explain any part** in more detail?

Let me know which approach you prefer!

---

**Last Updated:** November 10, 2025  
**Author:** AI Agent (GitHub Copilot)  
**Status:** 📋 Planning Document - Ready for Implementation
