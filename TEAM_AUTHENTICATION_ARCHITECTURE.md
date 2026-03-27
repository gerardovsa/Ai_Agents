# Team Authentication Architecture - Complete Reference

**Last Updated:** March 26, 2026  
**Status:** PRODUCTION - Fully documented and implemented

---

## Executive Summary

This system implements **multi-user team management** where a primary user (account owner) can create Team IDs (sub-users) that share the parent's context. Each team member has:
- Independent username (Team ID)
- Independent password
- Independent email address
- Role-based restricted access to parent's tools/agents
- Data scope restrictions (own, team, department, all)

Team members **do NOT automatically inherit** parent's credentials by reference - they store their own credential copies or have access controlled by JSON permission fields.

---

## Part 1: Database Schema & Team Structure

### Users Table Structure (ai_infrastructure.users)

```sql
-- Primary / Parent User
id: 1
username: "gerardo"
email: "gerardo@example.com"
password_hash: bcrypt("password123")
parent_user_id: NULL          -- Primary users have NULL
is_sub_user: FALSE            -- Primary users = FALSE
organisation_id: 1
org_role: "owner"             -- Owner has full access

-- Team Member / Sub-User
id: 42
username: "sales_north"       -- Team ID (display name for team)
email: "sarah@company.com"    -- Can be different from parent
password_hash: bcrypt("team_password") -- Independent password
parent_user_id: 1             -- Links back to parent
is_sub_user: TRUE             -- Marked as sub-user
organisation_id: 1            -- Same org as parent
org_role: "user"              -- Restricted role
permissions: { ... }          -- JSON with custom permissions
allowed_tools: ["tool1", "tool2"]  -- Whitelist of tools
allowed_agents: ["prime"]     -- Whitelist of agents
data_access_scope: "own"      -- own | team | department | all
usage_limit_daily: 1000       -- Daily API call limit
```

### Key Columns Explained

| Column | Type | Purpose | Primary User | Team Member |
|--------|------|---------|--------------|-------------|
| `parent_user_id` | INT FK | Links team member to parent | NULL | Parent's user_id |
| `is_sub_user` | BOOLEAN | Marks as team member vs primary | FALSE | TRUE |
| `username` | TEXT | Unique login ID | Email-based (gerardo) | Team ID (sales_north) |
| `email` | TEXT | Contact email | user@domain.com | team@team.local or custom |
| `password_hash` | TEXT | Independent bcrypt hash | Own password | **Own independent password** |
| `permissions` | JSON | Custom permission rules | Admin-defined | Restricted subset |
| `allowed_tools` | JSON | Tool access whitelist | null (all) | Restricted list |
| `allowed_agents` | JSON | AI agent access whitelist | null (all) | Restricted list |
| `data_access_scope` | TEXT | Data visibility boundary | "all" | "own" / "team" |
| `organisation_id` | INT | Multi-tenant org link | set | set (same as parent) |
| `org_role` | VARCHAR | Org-level role | owner/admin | member/user |

### Related Tables

**sessions.threads** - Thread/conversation data
- `team_id` (TEXT) - Team ID of creator (e.g., "sales_north" for team member, NULL for primary)
- `user_id` (INT) - Parent user ID or team member ID
- Composite index: `(user_id, team_id)` for efficient filtering

**sessions.messages** - Message history
- `sender_team_id` (TEXT) - Username of team member who sent (NULL for primary user)
- `recipient_team_id` (TEXT) - Target team member (NULL for broadcast)
- `sender_id` (INT) - User ID of sender
- Indexes on sender_team_id, recipient_team_id for filtering

**ai_infrastructure.user_platform_credentials** - API credentials
- `user_id` (INT) - Links to parent or team member user
- `platform` (VARCHAR) - Platform name (shopify, xero, etc.)
- `credentials` (JSONB) - **ENCRYPTED** credential dict
- Unique constraint: `(user_id, platform)` - Each user has one credential per platform

---

## Part 2: Database Migrations

### Migration: team_id_management_migration.sql

**Location:** `AI_infrastructure/migrations/team_id_management_migration.sql`

**Creates:**
1. `parent_user_id COLUMN` - links team member to parent
2. `is_sub_user COLUMN` - boolean flag for team members
3. `sender_team_id` in messages table
4. `recipient_team_id` in messages table
5. `team_id` in threads table
6. Indexes for efficient team-id filtering

**Sample additions:**
```sql
-- Add parent_user_id column to users
ALTER TABLE ai_infrastructure.users 
ADD COLUMN parent_user_id INTEGER REFERENCES ai_infrastructure.users(id);

-- Add is_sub_user flag
ALTER TABLE ai_infrastructure.users 
ADD COLUMN is_sub_user BOOLEAN DEFAULT FALSE;

-- Add messaging columns
ALTER TABLE sessions.messages 
ADD COLUMN sender_team_id TEXT;
ADD COLUMN recipient_team_id TEXT;

-- Index for team-based filtering
CREATE INDEX IF NOT EXISTS idx_threads_team_id 
ON sessions.threads(team_id) WHERE team_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_users_parent_user_id 
ON ai_infrastructure.users(parent_user_id);

CREATE INDEX IF NOT EXISTS idx_users_is_sub_user 
ON ai_infrastructure.users(is_sub_user);
```

### Migration: add_idempotency_and_cascade.sql

**Location:** `AI_infrastructure/migrations/add_idempotency_and_cascade.sql`

**Creates cascade cleanup trigger:**
- When a team member (sub-user) is deleted, their threads' `team_id` is set to NULL
- Trigger function: `cascade_team_id_deletion()`
- Prevents orphaned team_id references

```sql
CREATE TRIGGER team_id_cascade_delete
AFTER DELETE ON ai_infrastructure.users
FOR EACH ROW WHEN (OLD.is_sub_user = TRUE)
EXECUTE FUNCTION cascade_team_id_deletion();
```

---

## Part 3: Team Member Authentication Flow

### Creating a Team ID (POST /api/auth/team-ids/add)

**File:** `AI_infrastructure/routes/auth_routes.py` - lines 456-538

**Request:**
```json
{
  "team_id": "sales_north",
  "password": "secure_password_for_team",
  "email": "sarah@company.com",
  "permissions": { "custom": "permissions" },
  "allowed_tools": ["gmail_send", "xero_invoice"],
  "allowed_agents": ["prime"],
  "data_access_scope": "own",
  "usage_limit_daily": 1000
}
```

**Flow:**
1. Current authenticated user's ID is extracted from JWT
2. **Check uniqueness:** Verify team_id doesn't already exist for this parent
3. **Hash password:** Team member's password is independently bcrypt-hashed
4. **Create user row:**
   ```sql
   INSERT INTO ai_infrastructure.users (
       username, email, password_hash, role,
       parent_user_id, is_sub_user, display_name,
       permissions, allowed_tools, allowed_agents,
       data_access_scope, usage_limit_daily, is_active
   ) VALUES (
       'sales_north', 'sarah@company.com', <bcrypt>, 'user',
       1, TRUE, 'sales_north',
       {...}, '["gmail_send"...]', '["prime"]',
       'own', 1000, TRUE
   )
   ```
5. **Return success** with team_id

### Team Member Login (POST /api/auth/login)

**File:** `AI_infrastructure/routes/auth_routes.py` - lines 152-355

**Request:**
```json
{
  "username": "sales_north",    // Team ID, not email
  "password": "secure_password_for_team"
}
```

**Flow:**
1. **Lookup user:**
   ```sql
   SELECT id, username, email, password_hash, role, parent_user_id, is_sub_user
   FROM ai_infrastructure.users
   WHERE username = 'sales_north' OR email = 'sales_north'
   ```
   
2. **Verify password:** Use bcrypt to check team member's password_hash
3. **Extract is_sub_user flag:** Determines if user is team member
4. **Generate JWT token** with:
   ```json
   {
     "user_id": 42,
     "username": "sales_north",
     "email": "sarah@company.com",
     "role": "user",
     "organisation_id": 1,
     "org_role": "user",
     "is_sub_user": true,
     "parent_user_id": 1,
     "jwt_version": 1,
     "plan_tier": "professional",
     "exp": <timestamp 30 days from now>
   }
   ```

5. **Store session** in `user_sessions` table with IP/User-Agent

**Key difference from primary user login:**
- Team member's own user_id is in JWT (not parent's)
- `is_sub_user: true` flag is included
- `parent_user_id: 1` is included for reference

---

## Part 4: Credential Management for Team Members

### How Credentials Are Stored (NOT Shared)

**Pattern:** Each user (primary OR team member) has their OWN credential entries

```sql
-- Parent user's credentials
SELECT * FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 1 AND platform = 'shopify';
-- Result: {..., credential_value: "enc:v1:<encrypted>"}

-- Team member's credentials (SEPARATE entry)
SELECT * FROM ai_infrastructure.user_platform_credentials
WHERE user_id = 42 AND platform = 'shopify';
-- Result: {..., credential_value: "enc:v1:<encrypted>"}
-- DIFFERENT encrypted value - team member uses different API key if stored
```

### Permission-Based Credential Access

There are **THREE patterns** for team member credential access:

#### Pattern 1: Use Parent's Credentials (No Copy)

When `allowed_tools` includes platform-specific tools:
```python
# In auth/permission_checker.py - check_tool_permission()
if 'gmail_send' in allowed_tools:
    # Team member CAN use this tool
    # But they need credentials - check if they have their own
    creds = get_platform_credentials(user_id=42, platform='gmail')
    if not creds:
        # Fall back to parent's credentials
        creds = get_platform_credentials(user_id=1, platform='gmail')
```

#### Pattern 2: Restricted Data Access Scope

`data_access_scope` determines what data they can access:

| Scope | Access | Example |
|-------|--------|---------|
| `own` | Only their own threads/creatures | Team member only sees their own created items |
| `team` | Own + parent's + sibling team members' | Entire team's shared data |
| `department` | Larger grouping (future) | Multiple teams in a department |
| `all` | Everything | Rare - near-admin access |

#### Pattern 3: Tool Whitelist Controls

`allowed_tools = None` = All tools allowed (default)
`allowed_tools = []` = No tools allowed
`allowed_tools = ["tool1", "tool2"]` = Only these tools

**Enforced in:** `ai_infrastructure/auth/permission_checker.py` - `check_tool_permission()`

### Encrypted Credential Storage

**File:** `AI_infrastructure/auth/credential_encryptor.py`

**Algorithm:** Fernet (AES-128-CBC + HMAC-SHA256) - Authenticated symmetric encryption

**Storage format:** `enc:v1:<fernet_token>`
- Prefix `enc:v1:` marks encrypted values
- Without prefix = legacy plaintext

**Encryption happens at:** `user_auth.py` - `store_platform_credential()`

```python
from AI_infrastructure.auth.credential_encryptor import get_encryptor

encryptor = get_encryptor()
encrypted_creds = encryptor.encrypt_dict({
    "api_key": "sk-ant-...",
    "shop_url": "myshop.myshopify.com"
})
# Result: {'api_key': 'enc:v1:<token>', 'shop_url': 'enc:v1:<token>'}

credentials_json = json.dumps(encrypted_creds)
# Save to DB: JSONB column contains encrypted values
```

---

## Part 5: Login Page (Frontend)

### HTML Structure (business-ai-platform-v2.html, lines 18508+)

```html
<form class="login-form" id="loginForm" onsubmit="handleLogin(event)">
    <div class="login-error" id="loginError"></div>
    
    <!-- OAuth buttons (primary method) -->
    <button type="button" class="oauth-btn microsoft" onclick="signInWithMicrosoft()">
        <i class="fab fa-microsoft"></i>
        <span>Sign in with Microsoft 365</span>
    </button>
    
    <button type="button" class="oauth-btn google" onclick="signInWithGoogle()">
        <svg>...</svg>
        <span>Sign in with Google</span>
    </button>
    
    <div class="oauth-divider">OR</div>
    
    <!-- Traditional login -->
    <div class="form-group">
        <label for="username">Username or Email</label>
        <input type="text" id="username" name="username" required 
               placeholder="admin or email@example.com">
    </div>
    
    <div class="form-group">
        <label for="password">Password</label>
        <input type="password" id="password" name="password" required 
               placeholder="Enter your password">
    </div>
    
    <button type="submit" class="login-btn" id="loginBtn">
        <i class="fas fa-sign-in-alt"></i> Sign In
    </button>
</form>
```

### handleLogin() Function

**File:** `UI/modules_internal/components/account_profile.js` - lines 4-30

```javascript
// Login form handler
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginBtn = document.getElementById('loginBtn');
    const errorDiv = document.getElementById('loginError');

    // Disable button during submission
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
    errorDiv.classList.remove('show');

    // Call UserAuth.login() (in user_auth.js)
    const result = await UserAuth.login(username, password);

    if (result.success) {
        // UserAuth.login() already called showMainApp() on success
        console.log('Login successful');
    } else {
        // Show error to user
        errorDiv.textContent = result.error;
        errorDiv.classList.add('show');

        // Re-enable button
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Sign In';
    }
}
```

### UserAuth.login() - Core Logic

**File:** `UI/modules_internal/components/user_auth.js`

```javascript
async login(username, password) {
    // POST to /api/auth/login
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    
    if (data.success) {
        // Store JWT token
        this.token = data.token;
        localStorage.setItem('jwt_token', data.token);
        
        // Store user profile
        this.user = data.user;
        localStorage.setItem('userProfile', JSON.stringify(data.user));
        
        // Set main app initialized flag
        this.mainAppInitialized = false;  // Force re-init
        
        // Show main UI
        await this.showMainApp();
        
        return { success: true };
    } else {
        return { success: false, error: data.error };
    }
}
```

### Login Response Structure

**Response from POST /api/auth/login:**
```json
{
  "success": true,
  "token": "eyJhbGc...",  // JWT token (30-day expiry)
  "user": {
    "id": 42,
    "username": "sales_north",
    "email": "sarah@company.com",
    "role": "user",
    "organisation_id": 1,
    "org_role": "user",
    "is_sub_user": true,
    "parent_user_id": 1,
    "primary_gmail": "sarah@company.com",
    "workspaces": [...],
    "gmail_accounts": [...]
  }
}
```

### OAuth Login Buttons

**Available OAuth methods:**
- `signInWithMicrosoft()` - Microsoft 365 / Azure AD
- `signInWithGoogle()` - Google Workspace

**Flow:**
1. User clicks button
2. Backend returns authorization URL
3. User redirected to OAuth provider
4. Provider redirects back with token
5. Token validated, JWT issued, login complete

---

## Part 6: Permission Enforcement

### Permission Checker (ai_infrastructure/auth/permission_checker.py)

**Checks performed on every tool execution:**

```python
class PermissionChecker:
    def check_tool_permission(user_id: int, tool_name: str) -> bool:
        """
        Logic:
        1. owner/admin = full access
        2. allowed_tools = None → all tools allowed (default)
        3. allowed_tools = [] → no tools allowed
        4. allowed_tools = ['tool1'] → only listed tools
        """
        perms = get_user_permissions(user_id)
        
        if perms['role'] in ['owner', 'admin']:
            return True
        
        allowed_tools = perms.get('allowed_tools')
        
        if allowed_tools is None:  # Default = all allowed
            return True
        
        if isinstance(allowed_tools, list) and len(allowed_tools) == 0:
            raise PermissionError("No tool access")
        
        if tool_name not in allowed_tools:
            raise PermissionError(f"Tool '{tool_name}' not allowed")
        
        return True
```

### Agent Access Control

```python
def check_agent_access(user_id: int, agent_id: str) -> bool:
    """
    Similar to tool check:
    - owner/admin = full access to all agents
    - allowed_agents = None → all agents allowed
    - allowed_agents = [] → no agents allowed
    - allowed_agents = ['prime'] → only 'prime' agent
    """
    perms = get_user_permissions(user_id)
    
    if perms['role'] in ['owner', 'admin']:
        return True
    
    allowed = perms.get('allowed_agents')
    
    if allowed is None:
        return True
    
    if isinstance(allowed, list) and len(allowed) == 0:
        raise PermissionError("No agent access")
    
    if agent_id not in allowed:
        raise PermissionError(f"Agent '{agent_id}' not allowed")
    
    return True
```

### Data Access Control

```python
def check_data_access(user_id: int, resource_owner_id: int) -> bool:
    """
    Data scope determines visibility:
    - 'own': Only own data
    - 'team': Own + team members' data
    - 'department': Own + department data
    - 'all': All data
    """
    perms = get_user_permissions(user_id)
    
    # Admin/owner can access all data
    if perms['role'] in ['admin', 'owner']:
        return True
    
    # Always access own data
    if user_id == resource_owner_id:
        return True
    
    # Check data scope
    scope = perms.get('data_access_scope', 'own')
    
    if scope == 'own':
        raise PermissionError("Only own data allowed")
    
    if scope == 'team':
        # Check if resource_owner is team member of same parent
        return is_team_member(user_id, resource_owner_id)
    
    if scope == 'all':
        return True
    
    return False
```

---

## Part 7: Team ID Management Routes

**All routes in:** `AI_infrastructure/routes/auth_routes.py`

### Route Summary

| Method | Endpoint | Auth | Purpose | Lines |
|--------|----------|------|---------|-------|
| POST | `/team-ids/add` | require_auth | Create team member | 456-538 |
| GET | `/team-ids` | require_auth | List team members | 539-614 |
| PUT | `/team-ids/<id>` | require_auth | Update team member | 616-693 |
| DELETE | `/team-ids/<id>` | require_auth | Delete team member | 695-753 |
| GET | `/team-ids/stats` | require_auth | Team statistics | 756-833 |
| GET | `/team-ids/<id>/analytics` | require_auth | Team analytics | 834-940 |
| GET | `/team-ids/export` | require_auth | Export CSV | 941-1010 |
| POST | `/team-ids/import` | require_auth | Import CSV | 1012-1090 |

### List Team IDs (GET /team-ids)

```python
@auth_bp.route('/team-ids', methods=['GET'])
@require_auth
def list_team_ids():
    """List all Team IDs for authenticated user"""
    user_id = request.user['user_id']
    
    cursor.execute('''
        SELECT id, username, email, display_name, 
               allowed_tools, allowed_agents, data_access_scope,
               permissions, is_active, created_at
        FROM ai_infrastructure.users
        WHERE parent_user_id = %s AND is_sub_user = TRUE
        ORDER BY created_at DESC
    ''', (user_id,))
    
    team_ids = cursor.fetchall()
    
    return jsonify({
        'success': True,
        'team_ids': [
            {
                'team_id': row['username'],
                'email': row['email'],
                'display_name': row['display_name'],
                'allowed_tools': json.loads(row['allowed_tools']) if row['allowed_tools'] else None,
                'allowed_agents': json.loads(row['allowed_agents']) if row['allowed_agents'] else None,
                'data_access_scope': row['data_access_scope'],
                'is_active': row['is_active'],
                'created_at': row['created_at']
            }
            for row in team_ids
        ],
        'total': len(team_ids)
    })
```

---

## Part 8: Message Filtering by Team ID

### Team-Specific Message Queries

**File:** `AI_infrastructure/routes/message_operations.py`

When a team member sends a message:
```python
def save_message_with_team_id(
    user_id: int,
    thread_id: str,
    message_text: str,
    sender_role: str = 'user'
):
    """
    Save message with team_id if sender is sub-user
    """
    # Get sender's team_id (username if is_sub_user = TRUE)
    sender = get_user(user_id)
    
    if sender['is_sub_user']:
        sender_team_id = sender['username']  # e.g., 'sales_north'
    else:
        sender_team_id = None  # Primary user
    
    # Insert message with team_id
    cursor.execute('''
        INSERT INTO sessions.messages (
            user_id, thread_id, message_text,
            sender_team_id, timestamp
        ) VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
    ''', (user_id, thread_id, message_text, sender_team_id))
```

### Filter Messages by Team

**Frontend (business-ai-platform-v2.html, lines 29432+):**
```javascript
async function applyTeamIdFilter() {
    const selectedTeamIds = [];
    document.querySelectorAll('input[name="team-id-filter"]:checked')
        .forEach(checkbox => {
            selectedTeamIds.push(checkbox.value);
        });
    
    // Fetch filtered messages
    const response = await fetch(`${API_BASE_URL}/api/threads/filter-by-team`, {
        method: 'GET',
        headers: getAuthHeaders(),
        body: JSON.stringify({ team_ids: selectedTeamIds })
    });
    
    const data = await response.json();
    // Render filtered messages
}
```

---

## Part 9: Complete Authentication Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ USER LOGIN (Team Member: "sales_north")                         │
└─────────────────────────────────────────────────────────────────┘

STEP 1: User submits login form
   username: "sales_north"
   password: "password123"
        ↓
        ├─→ handleLogin(event) [account_profile.js]
        │   ├─→ UserAuth.login(username, password)
        │   └─→ POST /api/auth/login
        │
STEP 2: Backend authenticates
   └─→ auth_routes.py:login()
       ├─→ Query: SELECT ... FROM users WHERE username = 'sales_north'
       │   Result: is_sub_user=TRUE, parent_user_id=1, password_hash=bcrypt(...)
       │
       ├─→ bcrypt.checkpw(password, password_hash)
       │   ✓ Match
       │
       ├─→ Generate JWT with payload:
       │   {
       │     "user_id": 42,
       │     "username": "sales_north",
       │     "parent_user_id": 1,
       │     "is_sub_user": true,
       │     "role": "user",
       │     "organisation_id": 1,
       │     "org_role": "user",
       │     "allowed_tools": ["tool1"],
       │     "allowed_agents": ["prime"],
       │     "data_access_scope": "own",
       │     "exp": <timestamp>
       │   }
       │
       └─→ Return:
           {
             "success": true,
             "token": "eyJhbGc...",
             "user": { ... }
           }
        ↓
STEP 3: Frontend stores token
   localStorage.setItem('jwt_token', token)
   this.token = token
        ↓
STEP 4: Show main app
   UserAuth.showMainApp()
   └─→ Hide login overlay
   └─→ Show main dashboard
   └─→ Initialize modules for team member's restricted access
```

---

## Part 10: Security Considerations

### Password Storage
- **Algorithm:** bcrypt with salt rounds
- **Hash stored:** `password_hash` column in users table
- **Verification:** `bcrypt.checkpw()` on each login

### JWT Token Security
- **Duration:** 30 days
- **Storage:** localStorage (vulnerable to XSS - mitigated by no inline scripts)
- **Transmission:** Authorization header with Bearer scheme
- **Validation:** Verified on every protected route via @require_auth

### Credential Storage
- **Encryption:** Fernet (AES-128-CBC + HMAC-SHA256)
- **Format:** `enc:v1:<token>` stored in JSONB column
- **Key management:** `CREDENTIAL_ENCRYPTION_KEY` from .env

### Role-Based Access Control
- **Hierarchy:** viewer (1) < member (2) < manager (3) < admin (4) < owner (5)
- **Tool restrictions:** Whitelist-based (allowed_tools JSON array)
- **Agent restrictions:** Whitelist-based (allowed_agents JSON array)
- **Data scope:** own | team | department | all

### Cascade Cleanup
- When team member deleted: `team_id` in threads set to NULL
- Prevents orphaned references
- Trigger: `team_id_cascade_delete` on users DELETE

---

## Part 11: Quick Reference Commands

### Create Team ID
```bash
curl -X POST http://localhost:5000/api/auth/team-ids/add \
  -H "Authorization: Bearer <parent_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": "sales_north",
    "password": "password123",
    "email": "sarah@company.com",
    "allowed_tools": ["gmail_send", "shopify_lookup"],
    "allowed_agents": ["prime"],
    "data_access_scope": "own"
  }'
```

### Team Member Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "sales_north",
    "password": "password123"
  }'
```

### List Team Members
```bash
curl -X GET http://localhost:5000/api/auth/team-ids \
  -H "Authorization: Bearer <parent_token>"
```

### Update Team Member Permissions
```bash
curl -X PUT http://localhost:5000/api/auth/team-ids/sales_north \
  -H "Authorization: Bearer <parent_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "allowed_tools": ["gmail_send"],
    "usage_limit_daily": 500
  }'
```

---

## Part 12: Debugging Checklist

- [ ] Team ID created with `is_sub_user = TRUE`
- [ ] Parent ID correctly set in `parent_user_id` column
- [ ] Team member can login with own username (Team ID)
- [ ] Team member has own independent password_hash
- [ ] JWT includes `is_sub_user: true` and `parent_user_id`
- [ ] Permission checks respect `allowed_tools` array
- [ ] Messages tagged with `sender_team_id` if sub-user
- [ ] Threads tagged with `team_id` if created by sub-user
- [ ] Data access respects `data_access_scope`
- [ ] Cascade deletion removes team_id on user delete

---

## Related Documentation Files

- `.github/copilot-instructions.md` - Org/Platform/Module System details
- `.github/MODULE_VISIBILITY_ARCHITECTURE.md` - Module sidebar gating
- [Org section in copilot-instructions] - Organisation & credential vault system
- `ORGANISATION_CREDENTIALS_ARCHITECTURE.md` - Credential vault detailed design

---

**End of Team Authentication Architecture Document**
