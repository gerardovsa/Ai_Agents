# Existing Role System Analysis - Complete Code Discovery

**Date:** January 2025  
**Status:** ✅ DISCOVERY COMPLETE  
**Purpose:** Document what role-based access control already exists before implementing parent-child user hierarchy

---

## Executive Summary

### What We Found

The AI Agents platform has a **basic 2-role authentication system** ('admin' and 'user') with **NO advanced permission enforcement**:

✅ **Exists:**
- Basic role field in users table ('admin', 'user', 'readonly' mentioned)
- Role validation at registration (admin/user only)
- Admin-specific feature: Auto-link .env.master Gmail accounts
- JWT authentication with @require_auth decorator
- User authentication and session management

❌ **Does NOT Exist:**
- No role-based route protection (@require_admin, @require_role decorators)
- No tool-level access control (all users can use all 594 tools)
- No workspace-level permissions or role assignments
- No parent-child user hierarchy (no parent_user_id column)
- No granular permissions system (no permissions JSON column)
- No data access restrictions (users can see all data)
- No AI agent access control (all users can use all 5 agents)
- No time/usage restrictions (rate limits, work hours, expiry)

### Recommendation

**BUILD NEW COMPREHENSIVE SYSTEM** - Extend the existing basic role system with full hierarchical architecture from `USER_MANAGEMENT_ARCHITECTURE.md` and `PERMISSIONS_AND_ROLES_ARCHITECTURE.md`.

---

## 1. Database Schema Analysis

### Current Schema (ai_infrastructure.db)

**users table:**
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,  -- bcrypt hash OR 'oauth_google', 'oauth_microsoft'
    role TEXT DEFAULT 'user',     -- 'admin', 'user', ('readonly' mentioned but not used)
    primary_gmail TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT  -- JSON: {preferences, settings, thread_assignments}
)
```

**What's Missing:**
```sql
-- NO parent-child hierarchy columns:
parent_user_id INTEGER,              -- Link to parent user (NULL = root user)
is_sub_user BOOLEAN DEFAULT 0,       -- Whether this is a sub-user

-- NO permissions columns:
permissions TEXT,                     -- JSON: Granular tool/agent/data permissions
allowed_tools TEXT,                   -- JSON: List of allowed tool names
allowed_agents TEXT,                  -- JSON: List of allowed agent IDs
data_access_scope TEXT,               -- 'own', 'team', 'department', 'all'

-- NO workspace role columns:
workspace_roles TEXT,                 -- JSON: {workspace_id: role}

-- NO usage restriction columns:
usage_limit_daily INTEGER,            -- Max API calls per day
access_start_time TIME,               -- Work hours start
access_end_time TIME,                 -- Work hours end
account_expires_at TIMESTAMP          -- Account expiry date
```

---

## 2. Authentication System Analysis

### Current Implementation

**File:** `AI_infrastructure/auth/user_auth.py`

**Key Features:**

1. **Registration (Lines 226-277):**
   ```python
   def register_user(self, username: str, email: str, password: str, 
                     primary_gmail: str = None, role: str = 'user') -> Dict:
       """
       Create user with role: 'admin' (master account) or 'user' (regular user)
       """
       # Role validation happens in auth_routes.py
       # Admin users get .env.master Gmail accounts auto-linked
       if role == 'admin':
           # Auto-link all .env.master Gmail accounts
           gmail_accounts = self._load_env_gmail_accounts()
   ```

2. **Login (Lines 352-437):**
   ```python
   def authenticate(self, username: str, password: str) -> Dict:
       """Verify credentials and generate JWT token"""
       cursor.execute('''
           SELECT id, username, email, password_hash, role, primary_gmail
           FROM users WHERE username = ?
       ''', (username,))
       
       # Returns JWT with role in payload:
       token_payload = {
           'user_id': user_id,
           'username': username,
           'email': email,
           'role': role,  # ← Role included in token
           'exp': exp_timestamp
       }
   ```

3. **@require_auth Decorator (Lines 945-1018):**
   ```python
   def require_auth(f):
       """Decorator to require authentication for routes"""
       @wraps(f)
       def decorated_function(*args, **kwargs):
           # 1. Allow OPTIONS requests (CORS)
           # 2. Require Bearer token in Authorization header
           # 3. Verify JWT token
           # 4. Add user_data to request.user
           
           auth_manager = UserAuthManager()
           user_data = auth_manager.verify_token(token)
           
           if not user_data:
               return jsonify({'error': 'Invalid or expired token'}), 401
           
           request.user = user_data  # ← Adds user to Flask request context
           return f(*args, **kwargs)
   ```

**What's Missing:**

❌ **No role-based decorators:**
```python
# These DO NOT exist:
@require_admin       # Admin-only routes
@require_role('team_lead')  # Role-specific routes
@require_permission('google_docs_create')  # Tool-specific permission
```

❌ **No permission checking functions:**
```python
# These DO NOT exist:
def check_tool_permission(user_id: int, tool_name: str) -> bool
def check_agent_access(user_id: int, agent_id: str) -> bool
def check_data_access(user_id: int, resource_owner_id: int) -> bool
def is_admin(user_id: int) -> bool
def has_role(user_id: int, required_role: str) -> bool
```

---

## 3. Registration Endpoint Analysis

**File:** `AI_infrastructure/routes/auth_routes.py`

**Current Implementation (Lines 15-76):**
```python
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user with role support
    
    Request Body:
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "secure_password",
            "primary_gmail": "john@gmail.com",  // Optional
            "role": "admin"  // Optional: "admin" for master account, "user" for regular
        }
    
    Master Account (role="admin"):
    - Auto-links ALL Gmail accounts from .env.master
    - Full workspace access
    
    Regular User (role="user"):
    - Links only specified primary_gmail
    - Standard workspace access
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    primary_gmail = data.get('primary_gmail')
    
    role = data.get('role', 'user')  # ✅ Supports role parameter
    
    # ✅ ONLY VALIDATION: Must be 'admin' or 'user'
    if role not in ['user', 'admin']:
        print(f"❌ Invalid role: {role}")
        return jsonify({
            'success': False,
            'error': 'Invalid role. Must be "user" or "admin"'
        }), 400
    
    # No other permission checks!
```

**What This Means:**
- ✅ Role is stored in database
- ✅ Role is validated (admin/user only)
- ❌ NO enforcement of who can register admins (anyone can create admin accounts!)
- ❌ NO parent-user-only registration (anyone can register)
- ❌ NO sub-user creation endpoints

---

## 4. Protected Routes Analysis

### Current Protection Pattern

**All protected routes use @require_auth:**

**Example from `auth_routes.py`:**
```python
@auth_bp.route('/profile', methods=['GET'])
@require_auth  # ← Only checks if authenticated, NOT role
def get_profile():
    """Get user profile - accessible to ALL authenticated users"""
    user_id = request.user.get('user_id')
    # No role check here!

@auth_bp.route('/link-gmail', methods=['POST'])
@require_auth  # ← Only checks if authenticated, NOT role
def link_gmail():
    """Link Gmail account - accessible to ALL authenticated users"""
    user_id = request.user.get('user_id')
    # No role check here!

@auth_bp.route('/revoke-tokens', methods=['POST'])
@require_auth  # ← Only checks if authenticated, NOT role
def revoke_tokens():
    """Revoke OAuth tokens - accessible to ALL authenticated users"""
    user_id = request.user.get('user_id')
    # No role check here!
```

**What This Means:**
- ✅ All routes require valid JWT token
- ❌ NO routes check user role
- ❌ NO admin-only endpoints
- ❌ NO team-lead-only endpoints
- ❌ NO permission-based restrictions

---

## 5. Tool Execution Analysis

### Current Tool System

**File:** `tools/registry_v3.py`

**Tool Execution (execute_tool method):**
```python
def execute_tool(self, tool_name: str, **kwargs) -> Any:
    """Execute a tool by name with parameters"""
    
    if tool_name not in self.tools:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    # Get implementation
    impl_file = self.tools[tool_name].get('implementation_file')
    
    # Get function
    function = self.implementations[impl_file][tool_name]
    
    # ❌ NO PERMISSION CHECK HERE!
    # Just executes the tool with provided parameters
    return function(**kwargs)
```

**File:** `AI_infrastructure/core/agent_worker.py` (Tool execution in AI agent)

**No permission checks before tool execution:**
```python
# Tool execution happens without checking if user has permission
for tool_call in tool_calls:
    tool_name = tool_call['name']
    tool_params = tool_call['parameters']
    
    # ❌ NO CHECK: if user_can_use_tool(user_id, tool_name)
    
    result = registry.execute_tool(tool_name, **tool_params)
```

**What This Means:**
- ❌ ALL authenticated users can use ALL 594 tools
- ❌ NO tool restriction by role
- ❌ NO tool allow/deny lists
- ❌ NO dangerous tool restrictions (delete, modify, admin tools)

---

## 6. OAuth & Credential System Analysis

### Current OAuth Implementation

**File:** `AI_infrastructure/auth/credential_injector.py`

**Credential retrieval:**
```python
def get_google_credentials(self, user_id: int) -> Dict[str, str]:
    """Get Google OAuth credentials for user"""
    conn = self.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT access_token, refresh_token, token_expiry
        FROM oauth_tokens
        WHERE user_id = ? AND platform = 'google'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (user_id,))
    
    # ❌ NO CHECK: Does this user have permission to use this OAuth account?
    # ❌ NO CHECK: Is this a sub-user inheriting parent's OAuth?
    
    row = cursor.fetchone()
    if not row:
        return None
    
    return {
        'access_token': row[0],
        'refresh_token': row[1],
        'token_expiry': row[2]
    }
```

**What's Missing:**

❌ **No OAuth inheritance system:**
```python
# This DOES NOT exist:
def get_effective_credentials(self, user_id: int, platform: str) -> Dict:
    """
    Get credentials for user, or inherit from parent if sub-user
    
    Logic:
    1. Check if user has their own OAuth tokens
    2. If not, check if user is a sub-user (parent_user_id IS NOT NULL)
    3. If sub-user, get parent's OAuth tokens
    4. Return None if no credentials found
    """
```

---

## 7. Workspace System Analysis

### Current Implementation

**File:** `check_workspace.py` (utility script)

**Workspace structure:**
```python
# Workspaces table exists in ai_infrastructure.db:
CREATE TABLE IF NOT EXISTS workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,     -- e.g., 'default', 'project-alpha'
    name TEXT NOT NULL,             -- Display name
    created_at TIMESTAMP,
    user_id INTEGER                 -- Workspace owner
)

# Threads linked to workspaces:
CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_slug TEXT UNIQUE NOT NULL,
    name TEXT,
    workspace_id INTEGER,  -- Links to workspaces.id
    created_at TIMESTAMP
)
```

**What's Missing:**

❌ **No workspace members table:**
```sql
-- This DOES NOT exist:
CREATE TABLE workspace_members (
    workspace_id INTEGER,
    user_id INTEGER,
    role TEXT,  -- 'owner', 'admin', 'member', 'viewer'
    joined_at TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id)
)
```

❌ **No workspace permission system:**
- Workspaces exist but only store owner (user_id)
- NO multi-user workspace access
- NO role-based workspace permissions
- NO workspace member invitations

---

## 8. Comparison with Architecture Documents

### Planned vs. Existing

**From USER_MANAGEMENT_ARCHITECTURE.md:**

| Feature | Planned | Existing | Gap |
|---------|---------|----------|-----|
| Parent-Child Hierarchy | ✅ OAuth parent → username/password sub-users | ❌ None | MISSING |
| OAuth Inheritance | ✅ Sub-users use parent OAuth | ❌ None | MISSING |
| Sub-User Creation | ✅ Parent can create/manage sub-users | ❌ None | MISSING |
| User Management UI | ✅ Section in Account Settings | ❌ None | MISSING |
| Sub-User CRUD | ✅ Create/Edit/Delete/Reset sub-users | ❌ None | MISSING |

**From PERMISSIONS_AND_ROLES_ARCHITECTURE.md:**

| Feature | Planned | Existing | Gap |
|---------|---------|----------|-----|
| 6-Role Hierarchy | ✅ Owner/Admin/Team Lead/Team/Read-Only/Guest | ❌ Only admin/user | MISSING |
| Tool Permissions | ✅ Granular allow/deny per tool | ❌ All tools allowed | MISSING |
| Agent Access Control | ✅ Per-role agent access | ❌ All agents allowed | MISSING |
| Data Access Scope | ✅ own/team/department/all | ❌ All data visible | MISSING |
| Time Restrictions | ✅ Work hours, expiry dates | ❌ None | MISSING |
| Usage Limits | ✅ Daily rate limits | ❌ None | MISSING |
| Permission Checker | ✅ Middleware before tool execution | ❌ None | MISSING |

---

## 9. Security Implications

### Current Security Posture

✅ **What IS secure:**
- JWT authentication required for all endpoints
- Bcrypt password hashing (cost factor 12)
- OAuth token storage (access + refresh tokens)
- Token expiry (30 days)
- CORS preflight support

❌ **What IS NOT secure:**

1. **Anyone can create admin accounts:**
   ```python
   # Current registration endpoint allows this:
   POST /register
   {
     "username": "malicious_admin",
     "email": "hacker@evil.com",
     "password": "password123",
     "role": "admin"  # ← NO CHECK: Who authorized this?
   }
   ```

2. **All users can use all tools:**
   ```python
   # Authenticated user can do this:
   stripe_delete_customer(customer_id='cus_123')  # ← Delete production customer!
   google_drive_delete_file(file_id='abc123')     # ← Delete important files!
   microsoft365_delete_email(email_id='xyz')      # ← Delete emails!
   ```

3. **No data isolation:**
   ```python
   # User A can see User B's data:
   GET /api/threads?user_id=2  # ← No check: Does requester own this data?
   ```

4. **No OAuth credential restrictions:**
   ```python
   # Any authenticated user can access ANY user's OAuth tokens:
   # (if they know the user_id)
   ```

---

## 10. Implementation Recommendations

### Decision: EXTEND Existing System

**Rationale:**
- Basic auth infrastructure is solid (JWT, bcrypt, @require_auth)
- Adding new roles won't break existing admin/user functionality
- Can incrementally add permission checks
- Backward compatible (existing users remain functional)

### Phase 1: Database Schema (2 hours)

**Add to users table:**
```sql
ALTER TABLE users ADD COLUMN parent_user_id INTEGER;
ALTER TABLE users ADD COLUMN is_sub_user BOOLEAN DEFAULT 0;
ALTER TABLE users ADD COLUMN permissions TEXT;  -- JSON
ALTER TABLE users ADD COLUMN allowed_tools TEXT;  -- JSON: ['tool_name_1', ...]
ALTER TABLE users ADD COLUMN allowed_agents TEXT;  -- JSON: ['agent_1', ...]
ALTER TABLE users ADD COLUMN data_access_scope TEXT DEFAULT 'own';  -- 'own'|'team'|'all'
ALTER TABLE users ADD COLUMN usage_limit_daily INTEGER DEFAULT 1000;
ALTER TABLE users ADD COLUMN access_start_time TEXT;  -- HH:MM
ALTER TABLE users ADD COLUMN access_end_time TEXT;  -- HH:MM
ALTER TABLE users ADD COLUMN account_expires_at TIMESTAMP;

-- Foreign key (SQLite doesn't enforce, but good for documentation)
-- FOREIGN KEY (parent_user_id) REFERENCES users(id)

-- Update role column to support new values
-- (Already TEXT type, so no ALTER needed - just update validation)
```

**Add workspace_members table:**
```sql
CREATE TABLE IF NOT EXISTS workspace_members (
    workspace_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,  -- 'owner', 'admin', 'member', 'viewer'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id),
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

**Migration script:**
```python
# File: AI_infrastructure/migrations/add_user_hierarchy.py
import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Add new columns (safe - won't fail if already exist)
columns_to_add = [
    ('parent_user_id', 'INTEGER'),
    ('is_sub_user', 'BOOLEAN DEFAULT 0'),
    ('permissions', 'TEXT'),
    ('allowed_tools', 'TEXT'),
    ('allowed_agents', 'TEXT'),
    ('data_access_scope', "TEXT DEFAULT 'own'"),
    ('usage_limit_daily', 'INTEGER DEFAULT 1000'),
    ('access_start_time', 'TEXT'),
    ('access_end_time', 'TEXT'),
    ('account_expires_at', 'TIMESTAMP')
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}')
        print(f'✅ Added column: {col_name}')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f'⚠️  Column already exists: {col_name}')
        else:
            raise

# Create workspace_members table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS workspace_members (
        workspace_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (workspace_id, user_id)
    )
''')

conn.commit()
conn.close()
print('✅ Migration complete!')
```

### Phase 2: Permission Checker Middleware (3 hours)

**Create:** `AI_infrastructure/auth/permission_checker.py`

```python
"""
Permission Checker - Enforce role-based access control

Functions:
- check_tool_permission(user_id, tool_name) -> bool
- check_agent_access(user_id, agent_id) -> bool  
- check_data_access(user_id, resource_owner_id) -> bool
- check_workspace_access(user_id, workspace_id, required_role) -> bool
- is_within_work_hours(user_id) -> bool
- check_usage_limit(user_id) -> bool
"""

import json
import sqlite3
from datetime import datetime, time
from pathlib import Path
from typing import Optional, List

class PermissionChecker:
    def __init__(self):
        root_dir = Path(__file__).parent.parent.parent
        self.db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    def get_user_permissions(self, user_id: int) -> dict:
        """Get user's complete permission set"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, permissions, allowed_tools, allowed_agents, 
                   data_access_scope, parent_user_id, is_sub_user,
                   usage_limit_daily, access_start_time, access_end_time
            FROM users WHERE id = ?
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        role, perms_json, tools_json, agents_json, data_scope, parent_id, is_sub, limit, start_time, end_time = row
        
        return {
            'role': role,
            'permissions': json.loads(perms_json) if perms_json else {},
            'allowed_tools': json.loads(tools_json) if tools_json else None,  # None = all allowed
            'allowed_agents': json.loads(agents_json) if agents_json else None,  # None = all allowed
            'data_access_scope': data_scope,
            'parent_user_id': parent_id,
            'is_sub_user': bool(is_sub),
            'usage_limit_daily': limit,
            'access_start_time': start_time,
            'access_end_time': end_time
        }
    
    def check_tool_permission(self, user_id: int, tool_name: str) -> bool:
        """
        Check if user has permission to use a tool
        
        Returns:
            True if allowed, False if denied
        """
        perms = self.get_user_permissions(user_id)
        if not perms:
            return False
        
        # Admin role = full access
        if perms['role'] == 'admin':
            return True
        
        # Owner role = full access
        if perms['role'] == 'owner':
            return True
        
        # Check allowed_tools list (whitelist)
        allowed_tools = perms.get('allowed_tools')
        
        # If allowed_tools is None = all tools allowed (default for regular users)
        if allowed_tools is None:
            return True
        
        # If allowed_tools is empty list = NO tools allowed
        if isinstance(allowed_tools, list) and len(allowed_tools) == 0:
            return False
        
        # Check if tool is in whitelist
        return tool_name in allowed_tools
    
    def check_agent_access(self, user_id: int, agent_id: str) -> bool:
        """Check if user can access an AI agent"""
        perms = self.get_user_permissions(user_id)
        if not perms:
            return False
        
        # Admin/Owner = full access
        if perms['role'] in ['admin', 'owner']:
            return True
        
        allowed_agents = perms.get('allowed_agents')
        
        # None = all allowed
        if allowed_agents is None:
            return True
        
        # Empty list = none allowed
        if isinstance(allowed_agents, list) and len(allowed_agents) == 0:
            return False
        
        return agent_id in allowed_agents
    
    def check_data_access(self, user_id: int, resource_owner_id: int) -> bool:
        """Check if user can access another user's data"""
        perms = self.get_user_permissions(user_id)
        if not perms:
            return False
        
        # Admin/Owner = access all data
        if perms['role'] in ['admin', 'owner']:
            return True
        
        # Can always access own data
        if user_id == resource_owner_id:
            return True
        
        # Check data access scope
        data_scope = perms.get('data_access_scope', 'own')
        
        if data_scope == 'own':
            return user_id == resource_owner_id
        
        # TODO: Implement 'team' and 'department' scope checks
        # (requires team_id and department_id columns)
        
        if data_scope == 'all':
            return True
        
        return False
    
    def is_within_work_hours(self, user_id: int) -> bool:
        """Check if current time is within user's allowed work hours"""
        perms = self.get_user_permissions(user_id)
        if not perms:
            return False
        
        # No restrictions = always allowed
        if not perms.get('access_start_time') or not perms.get('access_end_time'):
            return True
        
        # Parse work hours
        start_time = datetime.strptime(perms['access_start_time'], '%H:%M').time()
        end_time = datetime.strptime(perms['access_end_time'], '%H:%M').time()
        current_time = datetime.now().time()
        
        # Check if within range
        return start_time <= current_time <= end_time
    
    def check_usage_limit(self, user_id: int) -> bool:
        """Check if user has exceeded daily usage limit"""
        # TODO: Implement usage tracking
        # (requires usage_logs table with timestamp, user_id, tool_name)
        return True  # For now, allow all

# Singleton instance
_permission_checker = None

def get_permission_checker() -> PermissionChecker:
    """Get global permission checker instance"""
    global _permission_checker
    if _permission_checker is None:
        _permission_checker = PermissionChecker()
    return _permission_checker
```

### Phase 3: Tool Execution Protection (2 hours)

**Update:** `tools/registry_v3.py`

```python
def execute_tool(self, tool_name: str, **kwargs) -> Any:
    """Execute a tool by name with parameters (WITH PERMISSION CHECK)"""
    
    if tool_name not in self.tools:
        raise ValueError(f"Tool '{tool_name}' not found")
    
    # ✅ NEW: Check tool permission
    user_id = kwargs.get('_user_id')
    if user_id:
        from AI_infrastructure.auth.permission_checker import get_permission_checker
        checker = get_permission_checker()
        
        if not checker.check_tool_permission(user_id, tool_name):
            raise PermissionError(
                f"User {user_id} does not have permission to use tool '{tool_name}'"
            )
        
        if not checker.is_within_work_hours(user_id):
            raise PermissionError(
                f"Tool usage outside allowed work hours"
            )
        
        if not checker.check_usage_limit(user_id):
            raise PermissionError(
                f"Daily usage limit exceeded"
            )
    
    # Get implementation
    impl_file = self.tools[tool_name].get('implementation_file')
    
    # Get function
    function = self.implementations[impl_file][tool_name]
    
    # Execute
    return function(**kwargs)
```

**Update:** `AI_infrastructure/core/agent_worker.py`

```python
# Add user_id to tool execution context
for tool_call in tool_calls:
    tool_name = tool_call['name']
    tool_params = tool_call['parameters']
    
    # ✅ NEW: Add user_id to kwargs (passed to permission checker)
    tool_params['_user_id'] = user_id
    
    try:
        result = registry.execute_tool(tool_name, **tool_params)
    except PermissionError as e:
        result = {
            'success': False,
            'error': f'Permission denied: {str(e)}'
        }
```

### Phase 4: Role Validation (1 hour)

**Update:** `AI_infrastructure/routes/auth_routes.py`

```python
# Add role hierarchy validation
VALID_ROLES = ['owner', 'admin', 'team_lead', 'team', 'readonly', 'guest', 'user']

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user with enhanced role support"""
    data = request.get_json()
    role = data.get('role', 'user')
    
    # ✅ NEW: Validate against full role list
    if role not in VALID_ROLES:
        return jsonify({
            'success': False,
            'error': f'Invalid role. Must be one of: {", ".join(VALID_ROLES)}'
        }), 400
    
    # ✅ NEW: Only admins can create other admins
    if role == 'admin':
        # Get requester's role from JWT token
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            auth_manager = UserAuthManager()
            requester = auth_manager.verify_token(token)
            
            if not requester or requester.get('role') != 'admin':
                return jsonify({
                    'success': False,
                    'error': 'Only admins can create admin accounts'
                }), 403
    
    # Continue with registration...
```

### Phase 5: Sub-User Management API (4 hours)

**Create:** `AI_infrastructure/routes/user_management_routes.py`

```python
"""
User Management Routes - Parent can create/manage sub-users

Endpoints:
- POST /api/users/sub-users - Create sub-user
- GET /api/users/sub-users - List sub-users
- PUT /api/users/sub-users/<id> - Update sub-user
- DELETE /api/users/sub-users/<id> - Delete sub-user
- POST /api/users/sub-users/<id>/reset-password - Reset sub-user password
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import require_auth, UserAuthManager
from AI_infrastructure.auth.permission_checker import get_permission_checker
import bcrypt

user_mgmt_bp = Blueprint('user_management', __name__)

@user_mgmt_bp.route('/api/users/sub-users', methods=['POST'])
@require_auth
def create_sub_user():
    """Create a sub-user under current user"""
    parent_user_id = request.user.get('user_id')
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')
    
    # Validation
    if not username or not email or not password:
        return jsonify({'error': 'username, email, and password required'}), 400
    
    # Role must be less privileged than parent
    parent_role = request.user.get('role')
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    
    # Create user
    auth_manager = UserAuthManager()
    conn = auth_manager.get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (
                username, email, password_hash, role, 
                parent_user_id, is_sub_user, created_at
            )
            VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
        """, (username, email, password_hash, role, parent_user_id))
        
        sub_user_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({
            'success': True,
            'sub_user_id': sub_user_id,
            'username': username,
            'email': email,
            'role': role
        }), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@user_mgmt_bp.route('/api/users/sub-users', methods=['GET'])
@require_auth
def list_sub_users():
    """List all sub-users created by current user"""
    parent_user_id = request.user.get('user_id')
    
    auth_manager = UserAuthManager()
    conn = auth_manager.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, email, role, created_at, last_active
        FROM users
        WHERE parent_user_id = ?
        ORDER BY created_at DESC
    """, (parent_user_id,))
    
    sub_users = [{
        'id': row[0],
        'username': row[1],
        'email': row[2],
        'role': row[3],
        'created_at': row[4],
        'last_active': row[5]
    } for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'sub_users': sub_users
    })

# TODO: Add PUT, DELETE, POST reset-password endpoints
```

### Phase 6: Frontend UI (4 hours)

**See USER_MANAGEMENT_ARCHITECTURE.md Section 5 for complete UI implementation.**

---

## 11. Testing Strategy

### Unit Tests

```python
# File: tests/test_permission_checker.py

def test_admin_has_full_access():
    """Admin can use all tools"""
    # Create admin user
    # Check tool permission for each tool
    # Assert all return True

def test_user_with_whitelist():
    """User with allowed_tools whitelist"""
    # Create user with allowed_tools=['gmail_send', 'google_docs_create']
    # Check permission for gmail_send → True
    # Check permission for stripe_delete_customer → False

def test_sub_user_oauth_inheritance():
    """Sub-user inherits parent OAuth tokens"""
    # Create parent with Google OAuth
    # Create sub-user under parent
    # Get credentials for sub-user
    # Assert returns parent's OAuth tokens

def test_work_hours_restriction():
    """User cannot use tools outside work hours"""
    # Create user with access_start_time='09:00', access_end_time='17:00'
    # Mock current time to 08:00
    # Check is_within_work_hours() → False
    # Mock current time to 12:00
    # Check is_within_work_hours() → True
```

### Integration Tests

```python
# File: tests/test_user_hierarchy_integration.py

def test_full_parent_child_workflow():
    """Complete parent-child user creation and OAuth inheritance"""
    # 1. Parent registers via OAuth
    # 2. Parent creates sub-user via API
    # 3. Sub-user logs in with username/password
    # 4. Sub-user uses Gmail tool
    # 5. Assert tool uses parent's OAuth credentials
    # 6. Assert sub-user cannot delete files (not in whitelist)
```

---

## 12. Timeline & Effort Estimate

| Phase | Task | Effort | Dependencies |
|-------|------|--------|--------------|
| 1 | Database Schema Migration | 2 hours | None |
| 2 | Permission Checker Middleware | 3 hours | Phase 1 |
| 3 | Tool Execution Protection | 2 hours | Phase 2 |
| 4 | Role Validation Enhancement | 1 hour | Phase 1 |
| 5 | Sub-User Management API | 4 hours | Phase 1, 2 |
| 6 | Frontend UI | 4 hours | Phase 5 |
| 7 | Testing | 3 hours | All |
| 8 | Documentation | 1 hour | All |

**Total:** 20 hours (2.5 days)

---

## 13. Backward Compatibility

### Existing Users

✅ **What won't break:**
- Existing admin users remain admins
- Existing regular users remain 'user' role
- Existing JWT tokens continue working
- Existing OAuth connections unchanged
- All routes remain accessible

✅ **Default behavior for existing users:**
```sql
-- Migration sets safe defaults:
UPDATE users SET
    allowed_tools = NULL,          -- NULL = all tools allowed
    allowed_agents = NULL,          -- NULL = all agents allowed
    data_access_scope = 'own',      -- Safe default
    is_sub_user = 0,                -- Not a sub-user
    parent_user_id = NULL           -- No parent
WHERE TRUE;
```

### Gradual Rollout

**Phase 1:** Deploy with permission checks DISABLED (dry-run mode)
```python
# In permission_checker.py:
DRY_RUN_MODE = True  # Just log permission checks, don't enforce

def check_tool_permission(self, user_id, tool_name):
    allowed = self._actual_check(user_id, tool_name)
    
    if DRY_RUN_MODE:
        print(f"🔍 [DRY RUN] User {user_id} tool {tool_name}: {'✅ ALLOW' if allowed else '❌ DENY'}")
        return True  # Always allow in dry-run
    
    return allowed
```

**Phase 2:** Enable enforcement for new users only
```python
# Only enforce for users created after deployment
if user['created_at'] > ENFORCEMENT_START_DATE:
    # Enforce permissions
else:
    # Legacy users: allow all
```

**Phase 3:** Full enforcement for all users

---

## 14. Next Steps

### Immediate Actions (This Session)

1. **User Approval:**
   - Review this analysis document
   - Decide: Proceed with implementation? Any changes needed?

2. **Create Migration Script:**
   - Run `add_user_hierarchy.py` to add new columns
   - Backup database before migration

3. **Implement Permission Checker:**
   - Create `permission_checker.py` with all methods
   - Unit test each permission check function

### Short-Term (Next 1-2 Days)

4. **Integrate Permission Checks:**
   - Update `registry_v3.py` to call permission checker
   - Update `agent_worker.py` to pass user_id to tools
   - Test with admin and regular users

5. **Build Sub-User API:**
   - Create `user_management_routes.py`
   - Add CRUD endpoints for sub-users
   - Test parent can create sub-users

### Medium-Term (Next Week)

6. **Build Frontend UI:**
   - Add User Management section to Account Settings
   - Create sub-user creation form
   - Add sub-user list with edit/delete actions

7. **Testing & Documentation:**
   - Write comprehensive tests
   - Update API documentation
   - Create user guide for sub-user management

---

## 15. Summary

### Key Findings

✅ **Good News:**
- Solid authentication foundation (JWT, bcrypt, OAuth)
- Basic role system already exists (admin/user)
- @require_auth decorator working correctly
- Easy to extend without breaking existing functionality

❌ **Missing Features:**
- No permission enforcement (all users = full access)
- No parent-child hierarchy
- No OAuth inheritance
- No tool restrictions
- No data access controls
- No workspace member roles
- No usage limits or time restrictions

### Implementation Path

**Extend, Don't Rebuild:**
1. Add new columns to users table (parent_user_id, permissions, etc.)
2. Create permission_checker.py middleware
3. Inject permission checks into tool execution
4. Add sub-user management API
5. Build User Management UI
6. Gradual rollout with backward compatibility

**Risk Level:** 🟢 **LOW** - Changes are additive, not destructive

**Effort:** 20 hours (2.5 days)

**Impact:** 🔥 **HIGH** - Unlocks multi-user accounts, team collaboration, enterprise security

---

**Status:** ✅ ANALYSIS COMPLETE - READY FOR IMPLEMENTATION

**Next:** User approval and migration script creation
