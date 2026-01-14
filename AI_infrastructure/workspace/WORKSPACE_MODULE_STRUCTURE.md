# Workspace Module Structure

**Date:** November 9, 2025  
**Purpose:** Modular architecture for multi-user workspace management

---

## Directory Structure

```
AI_infrastructure/
├── workspace/                          # NEW MODULE (Multi-user workspace management)
│   ├── __init__.py                    # Module exports
│   ├── constants.py                   # Roles, permissions, enums
│   ├── models.py                      # Pydantic schemas for validation
│   ├── workspace_manager.py           # Core workspace operations
│   ├── access_control.py              # Permission checking
│   ├── invitation_manager.py          # Invitation system
│   ├── slug_generator.py              # Generate unique slugs
│   ├── exceptions.py                  # Custom exceptions
│   └── README.md                      # Module documentation
│
├── routes/
│   └── workspace_routes.py            # NEW (Workspace API endpoints)
│
├── middleware/
│   └── workspace_auth.py              # NEW (Auth decorators)
│
├── migrations/
│   ├── add_workspace_slugs.py         # NEW (Add slug columns)
│   ├── create_workspace_tables.py     # NEW (Create new tables)
│   └── migrate_workspace_ids.py       # NEW (TEXT → INTEGER)
│
└── thread_manager.py                  # UPDATE (Fix workspace lookups)
```

---

## Module Files Overview

### **1. `__init__.py`** - Module Exports
- Exposes main classes and constants
- Makes imports clean: `from AI_infrastructure.workspace import WorkspaceManager`

### **2. `constants.py`** ✅ CREATED
**Purpose:** Central configuration and enums

**Contains:**
- `WorkspaceRole` enum (owner, admin, member, viewer)
- `ThreadAccessLevel` enum (owner, editor, commenter, viewer)
- `ThreadVisibility` enum (workspace, private, shared)
- `InvitationStatus` enum (pending, accepted, declined, expired, cancelled)
- `DefaultPermissions` class (permission sets for each role)
- Configuration constants (expiry days, max members, etc.)

**Used by:** All workspace module files

---

### **3. `models.py`** ✅ CREATED
**Purpose:** Data validation schemas using Pydantic

**Contains:**
- `WorkspaceCreate` - Validate workspace creation
- `WorkspaceUpdate` - Validate workspace updates
- `WorkspaceMemberAdd` - Validate adding members
- `WorkspaceMemberUpdate` - Validate role changes
- `InvitationCreate` - Validate invitation creation
- `ThreadShareRequest` - Validate thread sharing
- Response models for API endpoints

**Used by:** API routes for request/response validation

---

### **4. `workspace_manager.py`** (TO CREATE)
**Purpose:** Core workspace CRUD operations

**Responsibilities:**
```python
class WorkspaceManager:
    # Workspace CRUD
    def create_workspace(name, user_id, description, visibility)
    def get_workspace(workspace_slug)
    def update_workspace(workspace_slug, updates)
    def delete_workspace(workspace_slug)
    def list_user_workspaces(user_id)
    
    # Membership Management
    def add_member(workspace_id, user_id, role, invited_by)
    def remove_member(workspace_id, user_id)
    def update_member_role(workspace_id, user_id, new_role)
    def get_workspace_members(workspace_id)
    def get_member_info(workspace_id, user_id)
    
    # Workspace Queries
    def get_workspace_by_slug(workspace_slug)
    def get_workspace_by_id(workspace_id)
    def count_workspace_members(workspace_id)
    def count_workspace_threads(workspace_id)
```

**Database:** `ai_infrastructure.db` (workspaces, workspace_users tables)

---

### **5. `access_control.py`** (TO CREATE)
**Purpose:** Permission checking and access validation

**Responsibilities:**
```python
class AccessControl:
    # Workspace Access
    def can_access_workspace(user_id, workspace_id) -> bool
    def get_user_role(user_id, workspace_id) -> str
    def get_user_permissions(user_id, workspace_id) -> Dict
    def has_permission(user_id, workspace_id, permission) -> bool
    
    # Thread Access (Option B)
    def can_access_thread(user_id, thread_id) -> Dict
    def get_thread_access_level(user_id, thread_id) -> str
    def can_edit_thread(user_id, thread_id) -> bool
    def can_delete_thread(user_id, thread_id) -> bool
    
    # Validation Helpers
    def validate_workspace_owner(user_id, workspace_id) -> bool
    def validate_workspace_admin(user_id, workspace_id) -> bool
    def is_workspace_member(user_id, workspace_id) -> bool
```

**Used by:** API routes, middleware, thread operations

---

### **6. `invitation_manager.py`** (TO CREATE)
**Purpose:** Workspace invitation system

**Responsibilities:**
```python
class InvitationManager:
    # Send Invitations
    def send_invitation(workspace_id, email, role, invited_by) -> Dict
    def generate_invitation_token() -> str
    
    # Process Invitations
    def accept_invitation(token, user_id) -> Dict
    def decline_invitation(token) -> bool
    def cancel_invitation(invitation_id, user_id) -> bool
    
    # Query Invitations
    def get_invitation_by_token(token) -> Dict
    def list_workspace_invitations(workspace_id) -> List
    def list_user_invitations(email) -> List
    
    # Cleanup
    def expire_old_invitations() -> int
    def delete_invitation(invitation_id) -> bool
```

**Database:** `ai_infrastructure.db` (workspace_invitations table)

---

### **7. `slug_generator.py`** (TO CREATE)
**Purpose:** Generate unique slugs for users and workspaces

**Responsibilities:**
```python
class SlugGenerator:
    # User Slugs
    def generate_user_slug(username, user_id) -> str
    def generate_user_slug_from_email(email, user_id) -> str
    def ensure_unique_user_slug(slug) -> str
    
    # Workspace Slugs
    def generate_workspace_slug(name, workspace_id) -> str
    def ensure_unique_workspace_slug(slug) -> str
    
    # Utilities
    def sanitize_slug(text) -> str  # Remove special chars
    def truncate_slug(slug, max_length) -> str
```

**Format:**
- User: `username-{user_id}` → `john-doe-12`
- Workspace: `{name}-workspace-{id}` → `team-alpha-workspace-2`

---

### **8. `exceptions.py`** (TO CREATE)
**Purpose:** Custom exception classes

**Contains:**
```python
class WorkspaceException(Exception):
    """Base workspace exception"""

class WorkspaceNotFound(WorkspaceException):
    """Workspace doesn't exist"""

class WorkspaceAccessDenied(WorkspaceException):
    """User doesn't have access"""

class WorkspacePermissionDenied(WorkspaceException):
    """User lacks required permission"""

class InvalidWorkspaceRole(WorkspaceException):
    """Invalid role specified"""

class InvitationNotFound(WorkspaceException):
    """Invitation doesn't exist"""

class InvitationExpired(WorkspaceException):
    """Invitation has expired"""

class MemberAlreadyExists(WorkspaceException):
    """User already a member"""

class MaxMembersReached(WorkspaceException):
    """Workspace at capacity"""
```

**Used by:** All workspace module files for error handling

---

## Integration with Existing Code

### **Routes Integration**

**File:** `AI_infrastructure/routes/workspace_routes.py` (NEW)

```python
from flask import Blueprint, request, jsonify
from AI_infrastructure.workspace import (
    WorkspaceManager, 
    AccessControl, 
    InvitationManager
)
from AI_infrastructure.workspace.models import (
    WorkspaceCreate, 
    WorkspaceUpdate,
    WorkspaceMemberAdd
)
from AI_infrastructure.middleware.workspace_auth import require_workspace_access

workspace_bp = Blueprint('workspace', __name__, url_prefix='/api/workspaces')

# Initialize managers
workspace_mgr = WorkspaceManager()
access_ctrl = AccessControl()
invitation_mgr = InvitationManager()

@workspace_bp.route('/', methods=['POST'])
def create_workspace():
    """Create new workspace"""
    data = WorkspaceCreate(**request.json)
    workspace = workspace_mgr.create_workspace(...)
    return jsonify(workspace)

@workspace_bp.route('/<workspace_slug>/members', methods=['POST'])
@require_workspace_access('can_invite_users')
def add_member(workspace_slug):
    """Add member to workspace"""
    # Implementation...
```

**Register in `flask_app.py`:**
```python
from routes.workspace_routes import workspace_bp
app.register_blueprint(workspace_bp)
```

---

### **Middleware Integration**

**File:** `AI_infrastructure/middleware/workspace_auth.py` (NEW)

```python
from functools import wraps
from flask import request, jsonify
from AI_infrastructure.workspace import AccessControl

access_ctrl = AccessControl()

def require_workspace_access(permission=None):
    """
    Decorator to check workspace access
    
    Usage:
        @app.route('/api/threads/<thread_slug>')
        @require_workspace_access('can_create_threads')
        def create_thread(thread_slug):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = request.user_id  # From JWT token
            workspace_slug = kwargs.get('workspace_slug')
            
            # Get workspace
            workspace = workspace_mgr.get_workspace_by_slug(workspace_slug)
            if not workspace:
                return jsonify({'error': 'Workspace not found'}), 404
            
            # Check access
            if not access_ctrl.can_access_workspace(user_id, workspace['id']):
                return jsonify({'error': 'Access denied'}), 403
            
            # Check permission if specified
            if permission:
                if not access_ctrl.has_permission(user_id, workspace['id'], permission):
                    return jsonify({'error': f'Permission denied: {permission}'}), 403
            
            # Add workspace to kwargs
            kwargs['workspace'] = workspace
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

---

### **ThreadManager Integration**

**File:** `AI_infrastructure/thread_manager.py` (UPDATE)

**Add workspace lookup method:**
```python
def get_workspace_by_slug(self, workspace_slug: str) -> Dict:
    """
    Look up workspace from ai_infrastructure.db
    
    Args:
        workspace_slug: Workspace slug (e.g., 'team-alpha-workspace-2')
    
    Returns:
        Dict with workspace details including id (INTEGER)
    """
    import sqlite3
    from pathlib import Path
    
    root_dir = Path(__file__).parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, workspace_slug, name, created_by_user_id, visibility
        FROM workspaces
        WHERE workspace_slug = ?
    """, (workspace_slug,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return dict(row)
```

**Update add_message() to use INTEGER workspace_id:**
```python
def add_message(self, workspace_slug, thread_slug, ...):
    # Look up workspace
    workspace = self.get_workspace_by_slug(workspace_slug)
    if not workspace:
        raise ValueError(f"Workspace '{workspace_slug}' not found")
    
    workspace_id = workspace['id']  # INTEGER, not TEXT
    
    # Look up thread
    thread = self.get_thread(workspace_slug, thread_slug)
    if not thread:
        raise ValueError(f"Thread '{thread_slug}' not found")
    
    # Insert message with INTEGER workspace_id
    cursor.execute('''
        INSERT INTO messages (
            workspace_id, thread_id, role, content, ...
        ) VALUES (?, ?, ?, ?, ...)
    ''', (workspace_id, thread['id'], role, content, ...))
```

---

## Usage Examples

### **Creating a Workspace**
```python
from AI_infrastructure.workspace import WorkspaceManager

workspace_mgr = WorkspaceManager()

workspace = workspace_mgr.create_workspace(
    name="Team Alpha",
    user_id=12,
    description="Engineering team workspace",
    visibility="private"
)

print(f"Created workspace: {workspace['workspace_slug']}")
# Output: team-alpha-workspace-2
```

---

### **Adding Members**
```python
# Add member with default role
workspace_mgr.add_member(
    workspace_id=2,
    user_id=5,
    role="member",
    invited_by=12
)

# Add admin with custom permissions
workspace_mgr.add_member(
    workspace_id=2,
    user_id=7,
    role="admin",
    invited_by=12,
    permissions={
        'can_invite_users': True,
        'can_delete_threads': False
    }
)
```

---

### **Checking Permissions**
```python
from AI_infrastructure.workspace import AccessControl

access_ctrl = AccessControl()

# Check workspace access
if access_ctrl.can_access_workspace(user_id=5, workspace_id=2):
    print("User has access")

# Check specific permission
if access_ctrl.has_permission(user_id=5, workspace_id=2, 'can_create_threads'):
    # Create thread
    pass

# Get all permissions
perms = access_ctrl.get_user_permissions(user_id=5, workspace_id=2)
print(perms)
# Output: {'can_create_threads': True, 'can_delete_threads': False, ...}
```

---

### **Sending Invitations**
```python
from AI_infrastructure.workspace import InvitationManager

invitation_mgr = InvitationManager()

invitation = invitation_mgr.send_invitation(
    workspace_id=2,
    email="john@example.com",
    role="member",
    invited_by=12
)

print(f"Invitation token: {invitation['invitation_token']}")
# Send email with link: /accept-invitation/{token}
```

---

### **API Endpoint with Middleware**
```python
from flask import Blueprint, request, jsonify
from AI_infrastructure.middleware.workspace_auth import require_workspace_access

@app.route('/api/workspaces/<workspace_slug>/threads', methods=['POST'])
@require_workspace_access('can_create_threads')
def create_thread(workspace_slug, workspace):
    """
    Create thread in workspace
    
    - workspace_slug: From URL
    - workspace: Injected by middleware (Dict with workspace details)
    """
    user_id = request.user_id
    
    # workspace parameter has full workspace data
    workspace_id = workspace['id']  # INTEGER for FK
    
    # Create thread
    thread = thread_mgr.create_thread(
        workspace_id=workspace_id,
        user_id=user_id,
        name=request.json['name']
    )
    
    return jsonify(thread), 201
```

---

## Benefits of This Structure

### **1. Separation of Concerns**
- ✅ Workspace logic isolated from thread logic
- ✅ Constants separate from business logic
- ✅ Models separate from database operations

### **2. Reusability**
- ✅ Import only what you need: `from workspace import AccessControl`
- ✅ Use managers in routes, middleware, CLI scripts
- ✅ Share constants across all modules

### **3. Testability**
- ✅ Each file can be unit tested independently
- ✅ Mock database connections easily
- ✅ Test permissions without full Flask app

### **4. Maintainability**
- ✅ Clear file responsibilities
- ✅ Easy to find code (permissions → access_control.py)
- ✅ Add features without touching existing code

### **5. Scalability**
- ✅ Add new roles/permissions in constants.py only
- ✅ Add new invitation methods in invitation_manager.py only
- ✅ Module grows without polluting root folder

---

## Next Steps

1. ✅ Create remaining module files:
   - `workspace_manager.py`
   - `access_control.py`
   - `invitation_manager.py`
   - `slug_generator.py`
   - `exceptions.py`

2. ✅ Create `routes/workspace_routes.py`

3. ✅ Create `middleware/workspace_auth.py`

4. ✅ Update `thread_manager.py` with workspace lookup

5. ✅ Create migration scripts

6. ✅ Register blueprint in `flask_app.py`

7. ✅ Add frontend UI components

---

**Ready to implement?** Let me know and I'll create the remaining files!
