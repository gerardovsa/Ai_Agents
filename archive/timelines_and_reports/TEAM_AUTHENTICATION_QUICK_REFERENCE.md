# Team Authentication - Quick Reference Card

## 🔑 Core Architecture

**Team Structure:** Primary User → Team Members (Sub-Users)
- **Primary User:** `is_sub_user = FALSE`, `parent_user_id = NULL`
- **Team Member:** `is_sub_user = TRUE`, `parent_user_id = <primary_user_id>`

---

## 🗂️ Database Tables

### `ai_infrastructure.users`
| Column | Team Member Value | Purpose |
|--------|-------------------|---------|
| `id` | AUTO | Unique user ID (different from parent) |
| `username` | "Team ID" | E.g., "sales_north" |
| `email` | custom@email | Independent email per team member |
| `password_hash` | bcrypt | **Independent password** |
| `is_sub_user` | TRUE | Marks as team member |
| `parent_user_id` | <int> | Links to primary user |
| `allowed_tools` | JSON array | Whitelist of tool names (null = all) |
| `allowed_agents` | JSON array | Whitelist of agent names |
| `data_access_scope` | own/team/dept/all | Visibility scope |

### `sessions.threads` & `sessions.messages`
- `team_id` (threads) - Filters messages by team member
- `sender_team_id`, `recipient_team_id` (messages) - Team-specific message routing

---

## 🔐 Authentication Flow

### Team Member Login
```
POST /api/auth/login
{
  "username": "sales_north",      // Team ID
  "password": "team_password"      // Independent password
}
↓
Backend:
  1. Find user WHERE (username = "sales_north" AND is_sub_user = TRUE)
  2. Verify password_hash (independent validation)
  3. Generate JWT with:
     - user_id: <team_member_id>
     - is_sub_user: true
     - parent_user_id: 1
     - allowed_tools: [...whitelist...]
     - allowed_agents: [...whitelist...]
     - data_access_scope: "team"
↓
Response:
{
  "token": "eyJhbGc...",
  "user": {...},
  "is_sub_user": true,
  "parent_user_id": 1
}
```

### Login Handler
**Location:** `UI/modules_internal/components/account_profile.js` (lines 4-30)
```javascript
async function handleLogin(event) {
  event.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  
  const response = await window.UserAuth.login(username, password);
  if (response.success) {
    // Token stored in localStorage
    // showMainApp() displays interface
  }
}
```

---

## 👥 Team Management Routes

All in `AI_infrastructure/routes/auth_routes.py`

| Endpoint | Method | Purpose | Min Auth |
|----------|--------|---------|----------|
| `/api/auth/team-ids/add` | POST | Create team member | Primary user |
| `/api/auth/team-ids` | GET | List all team members | Primary user |
| `/api/auth/team-ids/<id>` | PUT | Update settings/permissions | Primary user |
| `/api/auth/team-ids/<id>` | DELETE | Delete team member | Primary user |
| `/api/auth/team-ids/stats` | GET | Analytics overview | Primary user |
| `/api/auth/team-ids/<id>/analytics` | GET | Per-member analytics | Primary user |
| `/api/auth/team-ids/export` | GET | CSV export all team | Primary user |
| `/api/auth/team-ids/import` | POST | CSV bulk import | Primary user |

### Create Team Member Example
```python
POST /api/auth/team-ids/add
{
  "team_id": "sales_north",
  "password": "SecurePassword123",
  "email": "sales.north@company.com",
  "permissions": "full",
  "allowed_tools": ["quote_calculator", "message_send"],
  "allowed_agents": ["prime_ai"],
  "data_access_scope": "team",
  "usage_limit_daily": 1000
}

Response:
{
  "id": 42,
  "username": "sales_north",
  "parent_user_id": 1,
  "is_sub_user": true,
  "message": "Team ID created successfully"
}
```

---

## 🔒 Permission Enforcement

**File:** `AI_infrastructure/auth/permission_checker.py`

### Three Levels of Access Control

#### 1. Tool Access
```python
allowed_tools = ["quote_calculator", "message_send"]
# null = all tools allowed
# [] = no tools allowed
# ["tool1", "tool2"] = whitelist only these tools
```

#### 2. Agent Access
```python
allowed_agents = ["prime_ai", "support_bot"]
# null = all agents allowed
# [] = no agents allowed
# ["agent1"] = whitelist only these agents
```

#### 3. Data Access Scope
```python
data_access_scope = "team"  # Options:
# "own" - only their own data
# "team" - team member's data + parent's data
# "department" - dept-level access
# "all" - full access (like primary user)
```

**Enforcement Point:** Every tool call checks permissions
```python
def check_tool_permission(user_id, tool_name):
    user = get_user_permissions(user_id)
    
    if user.allowed_tools is None:
        return True  # No restriction
    
    if tool_name not in user.allowed_tools:
        return False  # Denied
    
    return True  # Allowed
```

---

## 📧 Message & Thread Isolation

Team members' messages are **automatically filtered** by `team_id`:

```sql
-- Message retrieval for team member
SELECT * FROM sessions.messages
WHERE (
  (sender_id = :user_id)
  OR (receiver_id = :user_id)
  OR (thread_id IN (
    SELECT id FROM sessions.threads 
    WHERE team_id = :username OR team_id IS NULL
  ))
)
```

**Result:** Team member only sees:
- Their own sent/received messages
- Messages in threads tagged with their team_id
- Messages in shared threads (team_id = NULL)

---

## 🔑 Credential Storage

**File:** `AI_infrastructure/auth/credential_injector.py`

### Per-User Credentials
Each user (primary or team member) stores their **own** credentials:
```sql
INSERT INTO user_platform_credentials (
  user_id,           -- Team member ID or Primary user ID
  platform,          -- "shopify", "xero", "anthropic", etc.
  credential_value,  -- Encrypted: "enc:v1:<fernet_token>"
)
```

### Inheritance Pattern
```python
def get_platform_credentials(user_id, platform):
    # 1. Check user's own credentials
    cred = fetch_user_credentials(user_id, platform)
    if cred exists:
        return decrypt(cred)
    
    # 2. Check parent's credentials (with permission)
    if is_team_member(user_id):
        parent_id = get_parent_id(user_id)
        parent_cred = fetch_user_credentials(parent_id, platform)
        if parent_cred AND permission_checker.allows(user_id, platform):
            return decrypt(parent_cred)
    
    # 3. No credentials found
    raise CredentialNotFound()
```

---

## 🔍 Key Files Quick Lookup

| File | Purpose | Key Function |
|------|---------|-------------|
| `auth_routes.py` | Team routes | `add_team_id()`, `delete_team_id()` |
| `user_auth.py` | Auth core | `login()`, `register_user()` |
| `permission_checker.py` | Access control | `check_tool_permission()` |
| `credential_injector.py` | Credential retrieval | `get_platform_credentials()` |
| `account_profile.js` | Login form handler | `handleLogin()` |
| `business-ai-platform-v2.html` | Frontend | Login form (line 18508) |
| Team migrations | Schema | `team_id_management_migration.sql` |

---

## 🎯 Common Scenarios

### Scenario 1: Team Member Logs In
1. Form captures "Team ID" + password
2. Backend: `POST /api/auth/login` → validates independent password
3. JWT generated with `is_sub_user: true`
4. Token stored in localStorage
5. App loads with team member's tool/agent restrictions

### Scenario 2: Team Member Uses Shopify Tool
1. `check_tool_permission(team_member_id, "shopify")` runs
2. If not in `allowed_tools` whitelist → 403 Forbidden
3. Gets credentials via `get_platform_credentials()`
   - Tries team member's own credentials first
   - Falls back to parent's if permission allows
4. Tool executes with available credentials

### Scenario 3: Message Between Team Members
1. Team member A sends message to Team member B
2. Backend sets `sender_team_id = "team_member_a_username"`
3. Message stored in `sessions.messages`
4. Team member B's message query filters by `team_id`
5. Message appears in their inbox

### Scenario 4: Team Member Deleted
1. Primary user requests delete of team member
2. Trigger `cascade_team_id_deletion()` executes:
   - Sets all messages from deleted team → visible to parent only
   - Deactivates team member's user row
   - Revokes active sessions
3. Team member can't log in anymore

---

## 🧪 Testing Checklist

- [ ] Create team member via `/api/auth/team-ids/add`
- [ ] Login as team member (use Team ID as username)
- [ ] Verify JWT includes `is_sub_user: true` and `parent_user_id`
- [ ] Test tool access with `allowed_tools` whitelist
- [ ] Send message and verify `team_id` filtering
- [ ] Test credential fallback (use parent's credential)
- [ ] Delete team member and verify cascade cleanup
- [ ] Update permissions and verify tool access changes

---

## 🚀 Deployment Notes

1. **Database**: All migration scripts are idempotent (safe to rerun)
2. **ENV Variables**: No new variables needed (uses existing JWT_SECRET)
3. **JWT Tokens**: 30-day expiry, invalidated on role changes via `jwt_version`
4. **Cascade Triggers**: Automatic cleanup on team member deletion
5. **UTF-8 Encoding**: Run `.vscode/fix-bom.ps1` before deploying

---

## 📚 Full Reference

For complete documentation with diagrams, security details, and debugging steps:
→ See [TEAM_AUTHENTICATION_ARCHITECTURE.md](TEAM_AUTHENTICATION_ARCHITECTURE.md)

---

**Last Updated:** March 2026  
**Status:** ✅ Fully Implemented & Production Ready
