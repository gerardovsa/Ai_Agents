# Team Authentication Integration Guide

## How Team Authentication Fits Into Your AI Agents System

---

## 🎯 System Overview

Your AI Agents platform has a **multi-tenant, multi-role architecture**:

```
┌─────────────────────────────────────────────────┐
│           AI Agents V11 Platform                 │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────────────────────────────────────┐  │
│  │    Team Authentication System (Auth)     │  │
│  │  • Primary user login                    │  │
│  │  • Team member sub-user creation         │  │
│  │  • Independent credentials per user      │  │
│  └──────────────────────────────────────────┘  │
│              ↓                                   │
│  ┌──────────────────────────────────────────┐  │
│  │    Permission System (RBAC)              │  │
│  │  • Tool whitelist per team member        │  │
│  │  • Agent access control                  │  │
│  │  • Data scope (own/team/dept/all)        │  │
│  └──────────────────────────────────────────┘  │
│              ↓                                   │
│  ┌──────────────────────────────────────────┐  │
│  │    Tool/Agent Execution                  │  │
│  │  • Quote calculator                      │  │
│  │  • Shopify integration                   │  │
│  │  • Xero accounting                       │  │
│  │  • Custom calculators                    │  │
│  │  • Document processing                   │  │
│  └──────────────────────────────────────────┘  │
│              ↓                                   │
│  ┌──────────────────────────────────────────┐  │
│  │    Data & Messages (Team Isolation)      │  │
│  │  • Messages filtered by team_id          │  │
│  │  • Threads tagged per team               │  │
│  │  • Credentials per user + fallback       │  │
│  └──────────────────────────────────────────┘  │
│                                                   │
└─────────────────────────────────────────────────┘
```

---

## 📊 Data Flow: Team Member Using a Tool

```
1. AUTHENTICATION LAYER
   ┌─────────────────────────────────────────┐
   │ Team member logs in with Team ID        │
   │ username: "sales_north"                │
   │ password: "TeamPassword456!"            │
   │                                          │
   │ Backend: verify independent password    │
   │ Generate JWT with:                      │
   │  - is_sub_user: true                    │
   │  - parent_user_id: 1                    │
   │  - allowed_tools: ["quoteCalc", ...]    │
   │  - allowed_agents: ["prime_ai"]         │
   │  - data_access_scope: "team"            │
   └─────────────────────────────────────────┘
                      ↓

2. AUTHORIZATION LAYER (Permission Checker)
   ┌─────────────────────────────────────────┐
   │ Team member requests tool: "quote_calc" │
   │                                          │
   │ Check: Is "quote_calc" in allowed_tools?│
   │ ✓ YES → Continue                        │
   │ ✗ NO  → Return 403 Forbidden            │
   └─────────────────────────────────────────┘
                      ↓

3. CREDENTIAL LAYER
   ┌─────────────────────────────────────────┐
   │ Tool needs Shopify credentials          │
   │                                          │
   │ Priority 1: Team member's own creds?    │
   │  ✗ NOT FOUND                            │
   │ Priority 2: Parent's creds + permission?│
   │  ✓ FOUND → Use parent's Shopify key     │
   │                                          │
   │ Decrypt: decrypt_credential("enc:v1...")│
   └─────────────────────────────────────────┘
                      ↓

4. TOOL EXECUTION
   ┌─────────────────────────────────────────┐
   │ Execute quote_calculator tool:          │
   │  - With Shopify credentials             │
   │  - In context of team member            │
   │  - With data scope restrictions         │
   │  - Logging user_id as team member       │
   │                                          │
   │ Result: Quote calculated                │
   └─────────────────────────────────────────┘
                      ↓

5. MESSAGE STORAGE & RETRIEVAL
   ┌─────────────────────────────────────────┐
   │ AI response saved to database:          │
   │                                          │
   │ INSERT INTO messages (                  │
   │   user_id: 42 (team member),            │
   │   thread_id: 1001,                      │
   │   content: "Quote calculated...",       │
   │   sender_team_id: "sales_north"         │
   │ )                                        │
   │                                          │
   │ When retrieving messages:                │
   │ SELECT * FROM messages WHERE            │
   │   user_id = 42 AND                      │
   │   (team_id NULL OR                      │
   │    team_id = "sales_north")             │
   │                                          │
   │ Result: Only sees team-relevant msgs    │
   └─────────────────────────────────────────┘
```

---

## 🔌 Integration Points with Other Modules

### 1. **Quote Calculator Module** 
   - **Interaction:** Team member can use quote calculator if tool is in `allowed_tools`
   - **Credentials:** Falls back to parent's Shopify/accounting credentials
   - **Data Isolation:** Quote history filtered by team_id
   - **File:** `UI/modules_external/quote-calculator/`

### 2. **Shopify Integration**
   - **Interaction:** Team member can manage Shopify if authorized
   - **Credentials:** Uses team member's own creds, or parent's if allowed
   - **Data Scope:** Can only see products within their permission scope
   - **File:** `UI/modules_external/shopify/`

### 3. **Xero Accounting**
   - **Interaction:** Team member can view/generate reports if authorized
   - **Credentials:** OAuth tokens stored per-user, fallback to parent
   - **Data Isolation:** Reports filtered by team_id in queries
   - **File:** `UI/modules_external/xero/`

### 4. **Universal Search**
   - **Interaction:** Search results respect data_access_scope
   - **Credentials:** Searches use appropriate credentials per user
   - **Data Visibility:** Team members see only team-relevant results
   - **File:** `AI_infrastructure/routes/universal_search_routes.py`

### 5. **Communication Hub**
   - **Interaction:** Team members can send/receive messages within team
   - **Isolation:** Messages routed via `team_id` filtering
   - **Visibility:** Primary user sees all messages, team members see team-only
   - **File:** `AI_infrastructure/routes/communication_routes.py`

### 6. **Session Management**
   - **Interaction:** JWT token includes `is_sub_user` and `parent_user_id`
   - **Token Expiry:** 30 days (same as primary users)
   - **Invalidation:** `jwt_version` incremented on role change
   - **File:** `AI_infrastructure/auth/user_auth.py`

### 7. **Database Queries**
   - **Interaction:** All queries respect `data_access_scope` via permission checks
   - **Filtering:** Routes automatically filter by team_id when needed
   - **Example:**
     ```sql
     SELECT * FROM sessions.threads
     WHERE (
       user_id = :user_id
       AND (
         team_id IS NULL OR
         team_id IN (SELECT username FROM users WHERE parent_user_id = :user_id)
       )
     )
     ```
   - **File:** `AI_infrastructure/routes/*.py`

---

## 🔐 Security Integration

### 1. **JWT Token Security**
   ```
   Token Structure:
   ├─ Header: { alg: "HS256", typ: "JWT" }
   ├─ Payload:
   │  ├─ user_id (team member ID)
   │  ├─ username (Team ID)
   │  ├─ is_sub_user: true
   │  ├─ parent_user_id: 1
   │  ├─ allowed_tools: [...]
   │  ├─ allowed_agents: [...]
   │  ├─ data_access_scope: "team"
   │  └─ exp: <30 days from now>
   └─ Signature: HMAC-SHA256(header.payload, JWT_SECRET)
   ```

### 2. **Password Security**
   ```
   Storage:
   ├─ Primary user: bcrypt hash (cost=12)
   ├─ Team member: separate bcrypt hash (cost=12)
   └─ Never stored in plaintext
   
   Validation:
   ├─ Independent verification per user
   ├─ Timing-safe comparison
   └─ Failed attempt logging
   ```

### 3. **Credential Encryption**
   ```
   Storage:
   ├─ Algorithm: Fernet (AES-128-CBC + HMAC-SHA256)
   ├─ Format: "enc:v1:<fernet_token>"
   └─ Key: CREDENTIAL_ENCRYPTION_KEY from environment
   
   Retrieval:
   ├─ Decrypt on-demand (never stored plaintext in memory)
   ├─ Audit logging on reveal
   └─ Fallback to parent with permission check
   ```

### 4. **Permission Enforcement**
   ```
   Three-Layer Checks:
   ├─ 1. Tool whitelist: Is tool_name in allowed_tools?
   ├─ 2. Agent whitelist: Is agent_name in allowed_agents?
   └─ 3. Data scope: Can user access this data level?
   
   Failure Mode: 403 Forbidden (request denied)
   ```

### 5. **Message Filtering**
   ```
   At Database Query Level:
   SELECT * FROM messages WHERE
     (sender_id = :user_id OR receiver_id = :user_id) AND
     (thread_team_id IS NULL OR thread_team_id = :team_id)
   
   Result: Only messages visible to this team member
   ```

---

## 📈 Growth Path: Primary User → Team

```
Day 1: User signs up as primary
  └─ Can access all tools with admin role
  └─ Stores own credentials
  └─ No team members yet

Week 1: Primary user wants to delegate
  └─ Creates "sales_north" team member
  └─ Assigns tool whitelist: ["quote_calc", "message_send"]
  └─ Sets data scope: "team"
  └─ Sales team can now use quote calculator independently

Week 2: Multiple team members
  └─ Can create 5-10 team members per primary user
  └─ Each has independent login, password, permissions
  └─ Primary user manages all from Admin Dashboard

Month 1: Scaling operations
  └─ Team isolation ensures data privacy
  └─ Message threads filtered by team_id
  └─ Credentials shared via fallback (with permission)
  └─ Audit trail tracks all team member actions
```

---

## 🔧 Troubleshooting Integration Issues

### Issue 1: Team member can't use tool
**Check points:**
1. Is tool in `allowed_tools` whitelist?
   ```sql
   SELECT allowed_tools FROM ai_infrastructure.users WHERE id = :team_member_id;
   ```

2. Does user have credentials?
   ```sql
   SELECT * FROM user_platform_credentials 
   WHERE user_id = :team_member_id AND platform = 'shopify';
   ```

3. Can they access parent's credentials?
   ```python
   from AI_infrastructure.auth.credential_injector import get_platform_credentials
   try:
       creds = get_platform_credentials(team_member_id, 'shopify')
       print("Credentials retrieved:", bool(creds))
   except Exception as e:
       print("Error:", e)
   ```

### Issue 2: Team member sees other team's messages
**Check points:**
1. Are messages tagged with team_id?
   ```sql
   SELECT id, content, sender_team_id, recipient_team_id FROM sessions.messages 
   WHERE thread_id = :thread_id LIMIT 5;
   ```

2. Is query filtering by team_id?
   ```python
   # Routes should include:
   query += " AND (sender_team_id IS NULL OR sender_team_id = %s)"
   ```

### Issue 3: Team member can't log in
**Check points:**
1. Does user exist with is_sub_user = TRUE?
   ```sql
   SELECT id, username, is_sub_user, parent_user_id 
   FROM ai_infrastructure.users 
   WHERE username = 'sales_north';
   ```

2. Is password_hash correct format?
   ```python
   # Should be bcrypt hash starting with $2b$ or $2y$
   import bcrypt
   is_correct = bcrypt.checkpw(
       password.encode(), 
       stored_hash.encode()
   )
   ```

3. Check recent login attempts in logs
   ```powershell
   Get-Content AI_infrastructure/logs/flask_app.log -Tail 100 | findstr "login"
   ```

---

## 🚀 Deployment Checklist

Before deploying team authentication changes:

- [ ] All migrations are idempotent (can run multiple times safely)
- [ ] `team_id_management_migration.sql` applied to production database
- [ ] `add_idempotency_and_cascade.sql` triggers are active
- [ ] `JWT_SECRET` environment variable is strong (32+ characters)
- [ ] `CREDENTIAL_ENCRYPTION_KEY` is set in .env (base64-encoded Fernet key)
- [ ] Flask app restarted after environment variable changes
- [ ] Test primary user registration and login
- [ ] Test team member creation and login
- [ ] Test tool permission enforcement
- [ ] Validate message filtering works correctly
- [ ] Run `validate_team_authentication.py` test suite
- [ ] Monitor logs for any authentication errors

---

## 📊 Monitoring & Observability

### Key Metrics to Track
```
1. Authentication Success Rate
   - Primary logins / hour
   - Team member logins / hour
   - Failed login attempts / hour

2. Team Member Activity
   - Tools used by team members
   - Data access by scope level
   - Message volume by team_id

3. Permission Enforcement
   - Denied tool access (403s) / hour
   - Whitelisted tools accessed
   - Data scope boundary violations

4. Credential Access
   - Credential fallback uses (team → parent)
   - Credential reveals by team member
   - Encryption/decryption errors
```

### Log Locations
```
Flask Logs:            AI_infrastructure/logs/flask_app.log
Database Logs:         Supabase console
Authentication Errors: Flask logs (search for "auth")
Permission Denials:    Flask logs (search for "permission_denied")
```

---

## 📖 Related Documentation

- [TEAM_AUTHENTICATION_ARCHITECTURE.md](TEAM_AUTHENTICATION_ARCHITECTURE.md) - Complete technical reference
- [TEAM_AUTHENTICATION_QUICK_REFERENCE.md](TEAM_AUTHENTICATION_QUICK_REFERENCE.md) - Quick lookup guide
- [.github/copilot-instructions.md](.github/copilot-instructions.md) - Platform overview
- `.github/MODULE_VISIBILITY_ARCHITECTURE.md` - Module gating by organization/role

---

## ✅ System Status

**Last Updated:** March 2026  
**Status:** ✅ Fully Implemented & Production Ready  
**Test Coverage:** 10 end-to-end validation tests provided  
**Documentation:** 3 comprehensive guides created  

---

**Questions?** Refer to the comprehensive architecture document or validation test suite for detailed implementation examples.
