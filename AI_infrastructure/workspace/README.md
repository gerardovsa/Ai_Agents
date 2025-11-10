# Workspace Module

**Multi-user workspace management system with role-based access control.**

## Overview

This module provides complete workspace lifecycle management including:
- Workspace CRUD operations
- Member management with role-based permissions
- Invitation system with email support
- URL-safe slug generation
- Granular permission checking
- Thread-level access control

## Architecture

```
workspace/
├── __init__.py              # Module exports
├── workspace_manager.py     # Core workspace operations (650 lines, 16 methods)
├── invitation_manager.py    # Invitation lifecycle (570 lines, 11 methods)
├── access_control.py        # Permission system (400 lines, 20 methods)
├── slug_generator.py        # Unique slug generation (360 lines, 10 methods)
├── constants.py             # Enums and configuration (320 lines)
├── models.py                # Pydantic validation models (480 lines, 9 models)
└── exceptions.py            # Custom error classes (170 lines, 16 exceptions)
```

**Total:** 2,950 lines across 8 files

## Quick Start

```python
from AI_infrastructure.workspace import (
    WorkspaceManager,
    AccessControl,
    InvitationManager,
    WorkspaceRole
)

# Initialize managers
workspace_mgr = WorkspaceManager()
access_ctrl = AccessControl()
invite_mgr = InvitationManager()

# Create workspace
from .models import WorkspaceCreate

workspace_data = WorkspaceCreate(
    name="AI Research Team",
    description="Collaborative AI research workspace",
    owner_id=1
)

workspace = workspace_mgr.create_workspace(workspace_data)
# Result: Workspace(id=1, slug="ai-research-team", ...)

# Add member
from .models import WorkspaceMemberCreate

member_data = WorkspaceMemberCreate(
    workspace_id=workspace.id,
    user_id=2,
    role=WorkspaceRole.MEMBER
)

member = workspace_mgr.add_member(member_data)

# Check permissions
can_edit = access_ctrl.can_edit_workspace(workspace.id, user_id=2)
# False - MEMBERs cannot edit workspace

can_create = access_ctrl.can_create_threads(workspace.id, user_id=2)
# True - MEMBERs can create threads

# Send invitation
from .models import WorkspaceInvitationCreate

invite_data = WorkspaceInvitationCreate(
    workspace_id=workspace.id,
    invited_email="colleague@example.com",
    role=WorkspaceRole.MEMBER
)

invitation = invite_mgr.create_invitation(invite_data, invited_by_user_id=1)
# Result: WorkspaceInvitation(token="secure_token_here", expires_at=...)

# Accept invitation
result = invite_mgr.accept_invitation(invitation.token, user_id=3)
# Result: WorkspaceInvitationResponse(success=True, workspace_id=1, ...)
```

## Components

### 1. WorkspaceManager

**Purpose:** Core workspace CRUD and member management

**Key Methods:**
- `create_workspace()` - Create with unique slug, auto-add owner
- `get_workspace()` - Retrieve by ID or slug
- `update_workspace()` - Modify metadata (admin/owner only)
- `delete_workspace()` - Soft or hard delete (owner only)
- `list_workspaces()` - Paginated listing with filters
- `add_member()` - Add user with role validation
- `remove_member()` - Remove user (cannot remove self)
- `update_member_role()` - Change member permissions
- `get_members()` - List all active members
- `check_membership()` - Quick membership check
- `get_user_workspaces()` - All workspaces for user
- `get_workspace_stats()` - Statistics and analytics

**Example:**
```python
# Create workspace
workspace = workspace_mgr.create_workspace(WorkspaceCreate(
    name="Marketing Team",
    description="Marketing collaboration space",
    owner_id=1,
    visibility=WorkspaceVisibility.PRIVATE
))

# Add member
workspace_mgr.add_member(WorkspaceMemberCreate(
    workspace_id=workspace.id,
    user_id=5,
    role=WorkspaceRole.ADMIN
))

# List members
members = workspace_mgr.get_members(workspace.id)
# [WorkspaceMember(user_id=1, role=OWNER), WorkspaceMember(user_id=5, role=ADMIN)]

# Get user's workspaces
my_workspaces = workspace_mgr.get_user_workspaces(user_id=1)
```

### 2. AccessControl

**Purpose:** Permission checking and role validation

**Permission Types:**
- `VIEW_WORKSPACE` - View workspace details
- `EDIT_WORKSPACE` - Edit workspace metadata
- `DELETE_WORKSPACE` - Delete workspace (owner only)
- `MANAGE_SETTINGS` - Manage workspace settings
- `VIEW_MEMBERS` - View member list
- `ADD_MEMBERS` - Add new members
- `REMOVE_MEMBERS` - Remove members
- `UPDATE_MEMBER_ROLES` - Change member roles
- `CREATE_THREADS` - Create new threads
- `VIEW_ALL_THREADS` - View all workspace threads
- `EDIT_ALL_THREADS` - Edit any thread
- `DELETE_ALL_THREADS` - Delete any thread
- `SEND_INVITATIONS` - Send workspace invitations
- `MANAGE_INVITATIONS` - Manage invitations

**Role Hierarchy:**
```
OWNER > ADMIN > MEMBER > GUEST
```

**Permission Matrix:**

| Permission | OWNER | ADMIN | MEMBER | GUEST |
|------------|-------|-------|--------|-------|
| VIEW_WORKSPACE | ✅ | ✅ | ✅ | ✅ |
| EDIT_WORKSPACE | ✅ | ✅ | ❌ | ❌ |
| DELETE_WORKSPACE | ✅ | ❌ | ❌ | ❌ |
| ADD_MEMBERS | ✅ | ✅ | ❌ | ❌ |
| CREATE_THREADS | ✅ | ✅ | ✅ | ❌ |
| VIEW_ALL_THREADS | ✅ | ✅ | ✅ | ❌ |

**Example:**
```python
# Check specific permission
has_permission = access_ctrl.check_permission(
    workspace_id=1,
    user_id=5,
    permission=Permission.ADD_MEMBERS
)

# Get user's role
role = access_ctrl.get_user_role(workspace_id=1, user_id=5)
# WorkspaceRole.ADMIN

# Check if can modify role
can_modify = access_ctrl.can_modify_role(
    workspace_id=1,
    modifier_user_id=1,  # Owner
    target_user_id=5,    # Admin
    new_role=WorkspaceRole.MEMBER
)
# True

# Require permission (raises exception if denied)
access_ctrl.require_permission(
    workspace_id=1,
    user_id=5,
    permission=Permission.EDIT_WORKSPACE
)
# No exception - user has permission
```

### 3. InvitationManager

**Purpose:** Workspace invitation lifecycle

**Key Methods:**
- `create_invitation()` - Send invitation
- `accept_invitation()` - Accept and join
- `decline_invitation()` - Decline invitation
- `cancel_invitation()` - Cancel pending invitation
- `list_workspace_invitations()` - Workspace's invitations
- `list_user_invitations()` - User's invitations
- `expire_old_invitations()` - Cleanup expired
- `resend_invitation()` - Extend expiry

**Invitation Statuses:**
- `PENDING` - Awaiting response
- `ACCEPTED` - Accepted (user joined)
- `DECLINED` - Declined by recipient
- `CANCELLED` - Cancelled by sender
- `EXPIRED` - Expired (7 days default)

**Example:**
```python
# Create invitation
invitation = invite_mgr.create_invitation(
    WorkspaceInvitationCreate(
        workspace_id=1,
        invited_email="newuser@example.com",
        role=WorkspaceRole.MEMBER
    ),
    invited_by_user_id=1
)

# Token: invitation.token (for URL)
# Expires: invitation.expires_at (7 days from now)

# Accept invitation
result = invite_mgr.accept_invitation(
    token=invitation.token,
    user_id=10  # Newly registered user
)

# List workspace invitations
invitations = invite_mgr.list_workspace_invitations(
    workspace_id=1,
    status=InvitationStatus.PENDING
)

# Expire old invitations (cleanup job)
expired_count = invite_mgr.expire_old_invitations()
```

### 4. SlugGenerator

**Purpose:** Generate unique URL-safe slugs

**Key Methods:**
- `generate_workspace_slug()` - Unique workspace slug
- `generate_thread_slug()` - Unique thread slug (workspace-scoped)
- `is_slug_available()` - Check availability
- `validate_slug()` - Format validation
- `suggest_workspace_slugs()` - Multiple suggestions
- `get_workspace_by_slug()` - Lookup by slug

**Slug Rules:**
- 3-63 characters
- Lowercase letters, numbers, hyphens only
- Cannot start/end with hyphen
- Cannot be reserved word (admin, api, settings, etc.)

**Example:**
```python
from .slug_generator import SlugGenerator

slug_gen = SlugGenerator()

# Generate workspace slug
slug = slug_gen.generate_workspace_slug("AI Research Team")
# Result: "ai-research-team"

# Handle collision
slug2 = slug_gen.generate_workspace_slug("AI Research Team")
# Result: "ai-research-team-1" (automatic collision resolution)

# Validate slug
is_valid = slug_gen.validate_slug("my-workspace")
# True

is_valid = slug_gen.validate_slug("My Workspace")
# False (uppercase not allowed)

is_valid = slug_gen.validate_slug("admin")
# False (reserved word)

# Get suggestions
suggestions = slug_gen.suggest_workspace_slugs("Marketing", count=5)
# ["marketing", "marketing-1", "marketing-2", "marketing-a7f3", "marketing-b2e1"]

# Lookup by slug
workspace_id = slug_gen.get_workspace_by_slug("ai-research-team")
```

## Models

### Workspace Models

```python
class WorkspaceCreate(BaseModel):
    """Create workspace"""
    name: str  # Display name
    description: Optional[str]
    owner_id: int
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE
    settings: Optional[Dict] = DEFAULT_WORKSPACE_SETTINGS

class WorkspaceUpdate(BaseModel):
    """Update workspace"""
    name: Optional[str]
    description: Optional[str]
    visibility: Optional[WorkspaceVisibility]
    settings: Optional[Dict]

class Workspace(BaseModel):
    """Full workspace record"""
    id: int
    slug: str
    name: str
    description: Optional[str]
    owner_id: int
    visibility: WorkspaceVisibility
    status: WorkspaceStatus
    settings: Dict
    created_at: datetime
    updated_at: Optional[datetime]
    archived_at: Optional[datetime]
```

### Member Models

```python
class WorkspaceMemberCreate(BaseModel):
    """Add member"""
    workspace_id: int
    user_id: int
    role: WorkspaceRole

class WorkspaceMember(BaseModel):
    """Member record"""
    id: int
    workspace_id: int
    user_id: int
    role: WorkspaceRole
    added_by_user_id: int
    added_at: datetime
    removed_at: Optional[datetime]
```

### Invitation Models

```python
class WorkspaceInvitationCreate(BaseModel):
    """Create invitation"""
    workspace_id: int
    invited_user_id: Optional[int]  # If known
    invited_email: str
    role: WorkspaceRole

class WorkspaceInvitation(BaseModel):
    """Invitation record"""
    id: int
    workspace_id: int
    invited_user_id: Optional[int]
    invited_email: str
    role: WorkspaceRole
    token: str  # Secure token for URL
    status: InvitationStatus
    invited_by_user_id: int
    created_at: datetime
    expires_at: datetime
    responded_at: Optional[datetime]
```

## Exceptions

All exceptions inherit from `WorkspaceError`.

**Workspace Exceptions:**
- `WorkspaceNotFoundError` - Workspace doesn't exist
- `WorkspaceSlugExistsError` - Slug already taken
- `WorkspacePermissionError` - Insufficient permissions
- `WorkspaceArchivedError` - Workspace archived
- `WorkspaceCapacityError` - Member limit reached

**Member Exceptions:**
- `WorkspaceMemberNotFoundError` - Member doesn't exist
- `WorkspaceMemberAlreadyExistsError` - User already member
- `CannotRemoveSelfError` - Cannot remove yourself
- `MemberNotFoundError` - Member record not found

**Invitation Exceptions:**
- `InvitationNotFoundError` - Invitation doesn't exist
- `InvitationExpiredError` - Invitation expired
- `InvitationAlreadyProcessedError` - Already accepted/declined

**Slug Exceptions:**
- `InvalidSlugError` - Invalid format
- `ReservedSlugError` - Reserved word

**Example:**
```python
try:
    workspace = workspace_mgr.get_workspace(workspace_id=999)
except WorkspaceNotFoundError as e:
    print(f"Workspace not found: {e.workspace_id}")

try:
    access_ctrl.require_permission(
        workspace_id=1,
        user_id=5,
        permission=Permission.DELETE_WORKSPACE
    )
except WorkspacePermissionError as e:
    print(f"User {e.user_id} lacks permission: {e.permission}")
```

## Database Schema

### workspaces Table

```sql
CREATE TABLE workspaces (
    id INTEGER PRIMARY KEY,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL,
    visibility TEXT NOT NULL,  -- PUBLIC, PRIVATE, UNLISTED
    status TEXT NOT NULL,      -- ACTIVE, ARCHIVED
    settings TEXT,             -- JSON
    created_at TEXT NOT NULL,
    updated_at TEXT,
    archived_at TEXT,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);
```

### workspace_users Table

```sql
CREATE TABLE workspace_users (
    id INTEGER PRIMARY KEY,
    workspace_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL,        -- OWNER, ADMIN, MEMBER, GUEST
    added_by_user_id INTEGER NOT NULL,
    added_at TEXT NOT NULL,
    removed_at TEXT,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(workspace_id, user_id)
);
```

### workspace_invitations Table

```sql
CREATE TABLE workspace_invitations (
    id INTEGER PRIMARY KEY,
    workspace_id INTEGER NOT NULL,
    invited_user_id INTEGER,
    invited_email TEXT NOT NULL,
    role TEXT NOT NULL,
    token TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL,      -- PENDING, ACCEPTED, DECLINED, CANCELLED, EXPIRED
    invited_by_user_id INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    responded_at TEXT,
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);
```

## Integration

### With Threads Module

```python
from AI_infrastructure.workspace import WorkspaceManager, AccessControl
from AI_infrastructure.threads import ThreadManager

workspace_mgr = WorkspaceManager()
access_ctrl = AccessControl()
thread_mgr = ThreadManager()

# Create thread in workspace
if access_ctrl.can_create_threads(workspace_id=1, user_id=5):
    thread = thread_mgr.create_thread(ThreadCreate(
        workspace_id=1,
        owner_id=5,
        title="Project Discussion"
    ))
```

### With Flask Routes

```python
from flask import Blueprint, request, jsonify
from AI_infrastructure.workspace import WorkspaceManager, AccessControl

workspace_bp = Blueprint('workspace', __name__)
workspace_mgr = WorkspaceManager()
access_ctrl = AccessControl()

@workspace_bp.route('/api/workspaces', methods=['POST'])
def create_workspace():
    user_id = get_current_user_id()
    data = request.json
    
    workspace = workspace_mgr.create_workspace(WorkspaceCreate(
        name=data['name'],
        description=data.get('description'),
        owner_id=user_id
    ))
    
    return jsonify(workspace.dict()), 201

@workspace_bp.route('/api/workspaces/<int:workspace_id>/members', methods=['POST'])
def add_member(workspace_id):
    user_id = get_current_user_id()
    
    # Check permission
    access_ctrl.require_permission(
        workspace_id=workspace_id,
        user_id=user_id,
        permission=Permission.ADD_MEMBERS
    )
    
    # Add member
    data = request.json
    member = workspace_mgr.add_member(WorkspaceMemberCreate(
        workspace_id=workspace_id,
        user_id=data['user_id'],
        role=data['role']
    ))
    
    return jsonify(member.dict()), 201
```

## Testing

```python
# Test workspace creation
workspace = workspace_mgr.create_workspace(WorkspaceCreate(
    name="Test Workspace",
    owner_id=1
))

assert workspace.slug == "test-workspace"
assert workspace.status == WorkspaceStatus.ACTIVE

# Test member management
member = workspace_mgr.add_member(WorkspaceMemberCreate(
    workspace_id=workspace.id,
    user_id=2,
    role=WorkspaceRole.MEMBER
))

assert member.role == WorkspaceRole.MEMBER

# Test permissions
assert access_ctrl.can_create_threads(workspace.id, user_id=2) == True
assert access_ctrl.can_edit_workspace(workspace.id, user_id=2) == False
assert access_ctrl.can_edit_workspace(workspace.id, user_id=1) == True

# Test invitation
invitation = invite_mgr.create_invitation(
    WorkspaceInvitationCreate(
        workspace_id=workspace.id,
        invited_email="test@example.com",
        role=WorkspaceRole.MEMBER
    ),
    invited_by_user_id=1
)

assert invitation.status == InvitationStatus.PENDING
assert len(invitation.token) == 43  # URL-safe token
```

## Status

**Phase 2 Complete:** All workspace module files implemented
**Lines of Code:** 2,950
**Files:** 8
**Methods:** 57 total
**Tests:** Pending (Phase 7)
**Documentation:** Complete

## Next Steps

1. **Phase 3:** Database migrations (add slug columns, create tables)
2. **Phase 4:** Backend routes integration
3. **Phase 5:** Frontend UI components
4. **Phase 6:** Comprehensive testing
5. **Phase 7:** Production deployment

---

**Last Updated:** November 9, 2025 22:30
**Version:** 1.0.0
**Status:** Module Complete, Ready for Integration
