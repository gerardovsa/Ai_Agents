# Multi-User Workspace Implementation Plan
## Option B (Includes Option A + Thread-Level Access)

**Date:** November 9, 2025  
**Status:** Planning Phase  
**Goal:** Enable multi-user workspaces with both workspace-level AND thread-level access control

---

## Architecture Overview

```
ai_infrastructure.db (User & Workspace Management)
  ├── users (existing + user_slug)
  ├── workspaces (existing + workspace_slug + created_by_user_id)
  ├── workspace_users (NEW - workspace membership & roles)
  └── workspace_invitations (NEW - invite system)

sessions.db (Thread & Message Management)
  ├── threads (existing + workspace_id as INTEGER FK)
  ├── messages (existing + fixed schema)
  ├── thread_users (NEW - thread-level sharing)
  └── thread_shares (NEW - share history/audit)
```

---

## PHASE 1: Database Schema Changes

### 1.1 Update `users` table (ai_infrastructure.db)

**Changes:**
```sql
-- Add user_slug column
ALTER TABLE users ADD COLUMN user_slug TEXT UNIQUE;

-- Add username_normalized for case-insensitive lookups
ALTER TABLE users ADD COLUMN username_normalized TEXT;

-- Create index for fast slug lookups
CREATE UNIQUE INDEX idx_users_user_slug ON users(user_slug);
CREATE INDEX idx_users_username_normalized ON users(username_normalized);
```

**Migration Logic:**
```python
# Generate user_slugs for existing users
# Format: username-{user_id} or email-prefix-{user_id}
# Example: john-doe-12, admin-1, test-user-5
```

---

### 1.2 Update `workspaces` table (ai_infrastructure.db)

**Changes:**
```sql
-- Add workspace_slug column
ALTER TABLE workspaces ADD COLUMN workspace_slug TEXT UNIQUE;

-- Add created_by_user_id to track workspace creator
ALTER TABLE workspaces ADD COLUMN created_by_user_id INTEGER;

-- Add workspace status and settings
ALTER TABLE workspaces ADD COLUMN is_active INTEGER DEFAULT 1;
ALTER TABLE workspaces ADD COLUMN visibility TEXT DEFAULT 'private'; -- 'private', 'organization', 'public'
ALTER TABLE workspaces ADD COLUMN settings TEXT DEFAULT '{}'; -- JSON config

-- Create indexes
CREATE UNIQUE INDEX idx_workspaces_slug ON workspaces(workspace_slug);
CREATE INDEX idx_workspaces_user_id ON workspaces(user_id);
CREATE INDEX idx_workspaces_created_by ON workspaces(created_by_user_id);
```

**Migration Logic:**
```python
# Generate workspace_slugs for existing workspaces
# Format: {username}-workspace-{workspace_id}
# Example: admin-workspace-1, team-alpha-workspace-2

# Set created_by_user_id = user_id for existing workspaces
```

---

### 1.3 Create `workspace_users` table (ai_infrastructure.db) - NEW

**Schema:**
```sql
CREATE TABLE workspace_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT 'member', -- 'owner', 'admin', 'member', 'viewer'
    permissions TEXT DEFAULT '{}', -- JSON: {"can_create_threads": true, "can_delete_threads": false}
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    invited_by_user_id INTEGER,
    invitation_accepted_at TIMESTAMP,
    last_accessed_at TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by_user_id) REFERENCES users(id) ON DELETE SET NULL,
    
    UNIQUE(workspace_id, user_id) -- User can only be in workspace once
);

-- Indexes for fast lookups
CREATE INDEX idx_workspace_users_workspace ON workspace_users(workspace_id);
CREATE INDEX idx_workspace_users_user ON workspace_users(user_id);
CREATE INDEX idx_workspace_users_role ON workspace_users(role);
CREATE INDEX idx_workspace_users_active ON workspace_users(workspace_id, is_active);
```

**Role Definitions:**
- **owner**: Created workspace, full control, can delete workspace, can change any member's role
- **admin**: Can invite/remove users, create/delete threads, manage workspace settings
- **member**: Can create threads, edit own threads, view all workspace threads
- **viewer**: Read-only access, can view threads but not create/edit

**Default Permissions JSON:**
```json
{
  "owner": {
    "can_create_threads": true,
    "can_delete_threads": true,
    "can_edit_threads": true,
    "can_invite_users": true,
    "can_remove_users": true,
    "can_change_roles": true,
    "can_delete_workspace": true,
    "can_edit_workspace": true
  },
  "admin": {
    "can_create_threads": true,
    "can_delete_threads": true,
    "can_edit_threads": true,
    "can_invite_users": true,
    "can_remove_users": true,
    "can_change_roles": false,
    "can_delete_workspace": false,
    "can_edit_workspace": true
  },
  "member": {
    "can_create_threads": true,
    "can_delete_threads": false,
    "can_edit_threads": false,
    "can_invite_users": false,
    "can_remove_users": false,
    "can_change_roles": false,
    "can_delete_workspace": false,
    "can_edit_workspace": false
  },
  "viewer": {
    "can_create_threads": false,
    "can_delete_threads": false,
    "can_edit_threads": false,
    "can_invite_users": false,
    "can_remove_users": false,
    "can_change_roles": false,
    "can_delete_workspace": false,
    "can_edit_workspace": false
  }
}
```

**Migration Logic:**
```python
# For each existing workspace:
# - Add workspace owner (created_by_user_id) with role='owner'
# - If workspace.user_id != created_by_user_id, add user_id with role='member'
```

---

### 1.4 Create `workspace_invitations` table (ai_infrastructure.db) - NEW

**Schema:**
```sql
CREATE TABLE workspace_invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER NOT NULL,
    invited_user_id INTEGER, -- NULL if email invite to non-user
    invited_email TEXT,
    invited_by_user_id INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT 'member',
    invitation_token TEXT UNIQUE,
    status TEXT DEFAULT 'pending', -- 'pending', 'accepted', 'declined', 'expired', 'cancelled'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- Typically 7 days from creation
    accepted_at TIMESTAMP,
    declined_at TIMESTAMP,
    
    FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_invitations_workspace ON workspace_invitations(workspace_id);
CREATE INDEX idx_invitations_user ON workspace_invitations(invited_user_id);
CREATE INDEX idx_invitations_email ON workspace_invitations(invited_email);
CREATE INDEX idx_invitations_token ON workspace_invitations(invitation_token);
CREATE INDEX idx_invitations_status ON workspace_invitations(status);
```

---

### 1.5 Update `threads` table (sessions.db)

**Changes:**
```sql
-- Change workspace_id from TEXT to INTEGER
-- SQLite doesn't support ALTER COLUMN TYPE, so we need to:
-- 1. Create new column
-- 2. Migrate data
-- 3. Drop old column
-- 4. Rename new column

ALTER TABLE threads ADD COLUMN workspace_id_int INTEGER;

-- Migration: Convert TEXT workspace_id to INTEGER FK
-- UPDATE threads SET workspace_id_int = CAST(workspace_id AS INTEGER) WHERE workspace_id IS NOT NULL;

-- After migration:
-- ALTER TABLE threads DROP COLUMN workspace_id;
-- ALTER TABLE threads RENAME COLUMN workspace_id_int TO workspace_id;

-- Add foreign key (recreate table to add FK constraint)
-- SQLite requires table recreation for foreign keys

-- Add thread visibility settings
ALTER TABLE threads ADD COLUMN visibility TEXT DEFAULT 'workspace'; -- 'workspace', 'private', 'shared'
ALTER TABLE threads ADD COLUMN shared_with_users TEXT DEFAULT '[]'; -- JSON array of user_ids for quick checks

-- Create indexes
CREATE INDEX idx_threads_workspace ON threads(workspace_id);
CREATE INDEX idx_threads_visibility ON threads(visibility);
CREATE INDEX idx_threads_user_workspace ON threads(user_id, workspace_id);
```

**Thread Visibility Options:**
- **workspace**: All workspace members can access (default)
- **private**: Only thread creator + explicitly shared users
- **shared**: Shared with specific users via thread_users table

---

### 1.6 Create `thread_users` table (sessions.db) - NEW (Option B)

**Schema:**
```sql
CREATE TABLE thread_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    access_level TEXT NOT NULL DEFAULT 'viewer', -- 'owner', 'editor', 'commenter', 'viewer'
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shared_by_user_id INTEGER NOT NULL,
    last_accessed_at TIMESTAMP,
    can_reshare INTEGER DEFAULT 0, -- Can user share with others?
    
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
    
    UNIQUE(thread_id, user_id) -- User can only have one access level per thread
);

-- Indexes
CREATE INDEX idx_thread_users_thread ON thread_users(thread_id);
CREATE INDEX idx_thread_users_user ON thread_users(user_id);
CREATE INDEX idx_thread_users_access ON thread_users(access_level);
```

**Access Level Definitions:**
- **owner**: Thread creator, full control
- **editor**: Can add messages, edit thread metadata
- **commenter**: Can add messages, cannot edit metadata
- **viewer**: Read-only access

---

### 1.7 Create `thread_shares` table (sessions.db) - NEW (Audit Trail)

**Schema:**
```sql
CREATE TABLE thread_shares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER NOT NULL,
    shared_with_user_id INTEGER NOT NULL,
    shared_by_user_id INTEGER NOT NULL,
    access_level TEXT NOT NULL,
    shared_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked_at TIMESTAMP,
    revoked_by_user_id INTEGER,
    share_message TEXT, -- Optional message when sharing
    
    FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_thread_shares_thread ON thread_shares(thread_id);
CREATE INDEX idx_thread_shares_user ON thread_shares(shared_with_user_id);
CREATE INDEX idx_thread_shares_shared_by ON thread_shares(shared_by_user_id);
```

---

## PHASE 2: Backend API Changes

### 2.1 New Routes - Workspace Management

**File:** `AI_infrastructure/routes/workspace_routes.py` (NEW)

```python
# Workspace CRUD
POST   /api/workspaces                    # Create workspace
GET    /api/workspaces                    # List user's workspaces
GET    /api/workspaces/<workspace_slug>   # Get workspace details
PUT    /api/workspaces/<workspace_slug>   # Update workspace
DELETE /api/workspaces/<workspace_slug>   # Delete workspace

# Workspace Members
GET    /api/workspaces/<workspace_slug>/members           # List members
POST   /api/workspaces/<workspace_slug>/members           # Add member (direct add)
PUT    /api/workspaces/<workspace_slug>/members/<user_id> # Update member role
DELETE /api/workspaces/<workspace_slug>/members/<user_id> # Remove member

# Workspace Invitations
POST   /api/workspaces/<workspace_slug>/invitations       # Send invitation
GET    /api/workspaces/<workspace_slug>/invitations       # List invitations
POST   /api/invitations/<token>/accept                    # Accept invitation
POST   /api/invitations/<token>/decline                   # Decline invitation
DELETE /api/invitations/<invitation_id>                   # Cancel invitation

# Workspace Settings
GET    /api/workspaces/<workspace_slug>/settings          # Get settings
PUT    /api/workspaces/<workspace_slug>/settings          # Update settings
```

---

### 2.2 Update Routes - Thread Management

**File:** `AI_infrastructure/routes/thread_routes.py` (UPDATE)

**New/Updated Endpoints:**
```python
# Thread visibility & sharing
PUT    /api/threads/<thread_slug>/visibility              # Change visibility
POST   /api/threads/<thread_slug>/share                   # Share thread with user(s)
DELETE /api/threads/<thread_slug>/share/<user_id>         # Revoke thread access
GET    /api/threads/<thread_slug>/shared-users            # List users with access

# Thread access check (internal helper)
GET    /api/threads/<thread_slug>/can-access              # Check if user can access
```

**Updated Endpoints (add workspace_id handling):**
```python
POST   /api/threads/create                # Add workspace_id parameter
GET    /api/threads                        # Filter by workspace_id
GET    /api/threads/<thread_slug>          # Check workspace access
PUT    /api/threads/<thread_slug>          # Check workspace permissions
DELETE /api/threads/<thread_slug>          # Check workspace permissions
```

---

### 2.3 Update ThreadManager Class

**File:** `AI_infrastructure/thread_manager.py` (UPDATE)

**Changes Required:**

1. **Fix `get_thread()` method:**
```python
def get_thread(self, workspace_slug: str, thread_slug: str) -> Dict:
    """
    Get thread by workspace_slug and thread_slug
    
    CHANGES:
    - Look up workspace_id from workspace_slug in ai_infrastructure.db
    - Use INTEGER workspace_id for FK lookups
    - Add workspace access check
    """
```

2. **Fix `add_message()` method:**
```python
def add_message(self, workspace_slug: str, thread_slug: str, ...):
    """
    Add message to thread
    
    CHANGES:
    - Look up workspace from ai_infrastructure.db
    - Verify workspace exists
    - Use workspace.id (INTEGER) not workspace_slug (TEXT)
    """
```

3. **Add new methods:**
```python
def get_workspace_by_slug(self, workspace_slug: str) -> Dict:
    """Look up workspace from ai_infrastructure.db"""
    
def check_workspace_access(self, workspace_id: int, user_id: int) -> bool:
    """Check if user has access to workspace"""
    
def check_thread_access(self, thread_id: int, user_id: int) -> Dict:
    """Check if user has access to thread (workspace + thread_users)"""
    
def share_thread(self, thread_id: int, user_ids: List[int], access_level: str, shared_by_user_id: int):
    """Share thread with specific users"""
    
def revoke_thread_access(self, thread_id: int, user_id: int):
    """Revoke user's access to thread"""
```

---

### 2.4 New Manager Classes

**File:** `AI_infrastructure/workspace_manager.py` (NEW)

```python
class WorkspaceManager:
    """Manages workspaces and workspace membership"""
    
    def __init__(self):
        self.db_path = 'data/ai_infrastructure.db'
    
    def create_workspace(self, name: str, user_id: int, description: str = None) -> Dict:
        """Create workspace and add creator as owner"""
    
    def add_member(self, workspace_id: int, user_id: int, role: str, invited_by: int) -> Dict:
        """Add member to workspace"""
    
    def remove_member(self, workspace_id: int, user_id: int) -> bool:
        """Remove member from workspace"""
    
    def update_member_role(self, workspace_id: int, user_id: int, new_role: str) -> bool:
        """Update member's role"""
    
    def get_workspace_members(self, workspace_id: int) -> List[Dict]:
        """Get all workspace members"""
    
    def check_permission(self, workspace_id: int, user_id: int, permission: str) -> bool:
        """Check if user has specific permission in workspace"""
    
    def send_invitation(self, workspace_id: int, email: str, role: str, invited_by: int) -> Dict:
        """Send workspace invitation"""
    
    def accept_invitation(self, token: str, user_id: int) -> Dict:
        """Accept workspace invitation"""
```

---

## PHASE 3: Frontend UI Changes

### 3.1 Add Workspace Selector

**File:** `UI/business-ai-platform-v2.html` (UPDATE)

**Location:** Top navigation bar (next to user profile)

```html
<!-- Workspace Dropdown -->
<div class="workspace-selector">
    <select id="workspace-select" class="workspace-dropdown">
        <!-- Populated dynamically -->
        <option value="workspace-1">Personal Workspace</option>
        <option value="team-alpha-2025">Team Alpha</option>
    </select>
    <button class="workspace-settings-btn" onclick="openWorkspaceSettings()">
        ⚙️
    </button>
</div>
```

**JavaScript:**
```javascript
// Load user's workspaces
async function loadUserWorkspaces() {
    const response = await fetch('/api/workspaces');
    const workspaces = await response.json();
    // Populate dropdown
}

// Switch workspace
async function switchWorkspace(workspaceSlug) {
    currentWorkspace = workspaceSlug;
    // Reload threads for new workspace
    await loadThreadsForWorkspace(workspaceSlug);
}
```

---

### 3.2 Add Thread Sharing UI

**File:** `UI/business-ai-platform-v2.html` (UPDATE)

**Add to thread menu (hamburger):**
```html
<div class="thread-menu-item" onclick="openShareThreadModal(threadId)">
    🔗 Share Thread
</div>
```

**New Modal:**
```html
<!-- Share Thread Modal -->
<div id="share-thread-modal" class="modal">
    <div class="modal-content">
        <h2>Share Thread</h2>
        
        <!-- Visibility Options -->
        <div class="visibility-options">
            <label>
                <input type="radio" name="visibility" value="workspace" checked>
                All workspace members
            </label>
            <label>
                <input type="radio" name="visibility" value="private">
                Only me
            </label>
            <label>
                <input type="radio" name="visibility" value="shared">
                Specific users
            </label>
        </div>
        
        <!-- User Selection (if visibility=shared) -->
        <div id="user-selection" style="display:none">
            <label>Share with:</label>
            <select multiple id="share-users">
                <!-- Populated from workspace members -->
            </select>
            
            <label>Access Level:</label>
            <select id="access-level">
                <option value="viewer">Viewer (read-only)</option>
                <option value="commenter">Commenter (can reply)</option>
                <option value="editor">Editor (can edit)</option>
            </select>
        </div>
        
        <button onclick="saveThreadSharing()">Save</button>
        <button onclick="closeShareThreadModal()">Cancel</button>
    </div>
</div>
```

---

### 3.3 Add Workspace Settings Modal

**New Modal:**
```html
<!-- Workspace Settings Modal -->
<div id="workspace-settings-modal" class="modal">
    <div class="modal-content">
        <h2>Workspace Settings</h2>
        
        <div class="tabs">
            <button class="tab-btn active" onclick="showTab('general')">General</button>
            <button class="tab-btn" onclick="showTab('members')">Members</button>
            <button class="tab-btn" onclick="showTab('invitations')">Invitations</button>
        </div>
        
        <!-- General Tab -->
        <div id="general-tab" class="tab-content">
            <label>Workspace Name:</label>
            <input type="text" id="workspace-name" value="Team Alpha">
            
            <label>Description:</label>
            <textarea id="workspace-description"></textarea>
            
            <label>Visibility:</label>
            <select id="workspace-visibility">
                <option value="private">Private (invite only)</option>
                <option value="organization">Organization</option>
            </select>
        </div>
        
        <!-- Members Tab -->
        <div id="members-tab" class="tab-content" style="display:none">
            <button onclick="openInviteMemberModal()">+ Invite Member</button>
            
            <table class="members-table">
                <thead>
                    <tr>
                        <th>User</th>
                        <th>Role</th>
                        <th>Joined</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="members-list">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
        
        <!-- Invitations Tab -->
        <div id="invitations-tab" class="tab-content" style="display:none">
            <table class="invitations-table">
                <thead>
                    <tr>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th>Sent</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody id="invitations-list">
                    <!-- Populated dynamically -->
                </tbody>
            </table>
        </div>
    </div>
</div>
```

---

### 3.4 Thread List Filtering

**Update thread list to show workspace context:**
```html
<div class="thread-item">
    <div class="thread-name">My Thread</div>
    <div class="thread-meta">
        <span class="thread-workspace">Team Alpha</span>
        <span class="thread-visibility">🌐 Workspace</span> <!-- or 🔒 Private -->
        <span class="thread-shared-count">Shared with 3 users</span>
    </div>
</div>
```

---

## PHASE 4: Migration Scripts

### 4.1 Add Missing Columns

**File:** `scripts/setup/migrate_workspace_schema.py` (NEW)

```python
"""
Migrate database schema for multi-user workspace support

Steps:
1. Add user_slug to users table
2. Add workspace_slug to workspaces table
3. Create workspace_users table
4. Create workspace_invitations table
5. Update threads.workspace_id (TEXT → INTEGER)
6. Create thread_users table
7. Create thread_shares table
8. Generate slugs for existing data
9. Create initial workspace_users entries
"""
```

---

### 4.2 Generate Slugs

**File:** `scripts/setup/generate_slugs.py` (NEW)

```python
"""
Generate unique slugs for existing users and workspaces

User slugs: username-{user_id} or email-prefix-{user_id}
Workspace slugs: {workspace_name}-workspace-{id}
"""
```

---

### 4.3 Migrate Workspace IDs

**File:** `scripts/setup/migrate_workspace_ids.py` (NEW)

```python
"""
Convert threads.workspace_id from TEXT to INTEGER FK

Steps:
1. Create temporary workspace_id_int column
2. Look up workspace IDs from ai_infrastructure.db
3. Update threads with INTEGER workspace_id
4. Drop old TEXT column
5. Rename new column
"""
```

---

## PHASE 5: Access Control Implementation

### 5.1 Workspace Access Check Middleware

**File:** `AI_infrastructure/middleware/workspace_auth.py` (NEW)

```python
def require_workspace_access(permission: str = None):
    """
    Decorator to check workspace access
    
    Usage:
        @app.route('/api/threads/<thread_slug>')
        @require_workspace_access('can_create_threads')
        def create_thread(thread_slug):
            ...
    """
```

---

### 5.2 Thread Access Check Utility

**File:** `AI_infrastructure/utils/access_control.py` (NEW)

```python
class AccessControl:
    """Centralized access control logic"""
    
    def can_access_workspace(self, user_id: int, workspace_id: int) -> bool:
        """Check workspace access"""
    
    def can_access_thread(self, user_id: int, thread_id: int) -> Dict:
        """
        Check thread access (combines workspace + thread_users)
        
        Returns:
            {
                'can_access': True/False,
                'access_level': 'owner'/'editor'/'viewer'/None,
                'via': 'workspace'/'direct_share'
            }
        """
    
    def get_user_permissions(self, user_id: int, workspace_id: int) -> Dict:
        """Get user's permissions in workspace"""
```

---

## PHASE 6: Testing Plan

### 6.1 Unit Tests

**File:** `tests/test_workspace_access.py` (NEW)

```python
# Test workspace creation
# Test adding/removing members
# Test role changes
# Test permissions
# Test invitations
```

**File:** `tests/test_thread_sharing.py` (NEW)

```python
# Test thread visibility changes
# Test thread sharing
# Test access revocation
# Test access level enforcement
```

---

### 6.2 Integration Tests

**File:** `tests/test_multi_user_workflows.py` (NEW)

```python
# Test: User A creates workspace
# Test: User A invites User B
# Test: User B accepts invitation
# Test: User B creates thread in workspace
# Test: User A can see User B's thread
# Test: User B shares private thread with User A
# Test: User A cannot access User B's private thread (without share)
```

---

## PHASE 7: Documentation

### 7.1 API Documentation

**File:** `docs/API_WORKSPACE_ENDPOINTS.md` (NEW)
- Document all new endpoints
- Request/response examples
- Error codes
- Authentication requirements

---

### 7.2 User Guide

**File:** `docs/USER_GUIDE_WORKSPACES.md` (NEW)
- How to create workspace
- How to invite members
- How to share threads
- Understanding roles and permissions

---

## Summary of Changes

### Database Changes
- ✅ Add `user_slug` to users table (ai_infrastructure.db)
- ✅ Add `workspace_slug`, `created_by_user_id` to workspaces table (ai_infrastructure.db)
- ✅ Create `workspace_users` table (ai_infrastructure.db)
- ✅ Create `workspace_invitations` table (ai_infrastructure.db)
- ✅ Change `threads.workspace_id` from TEXT to INTEGER FK (sessions.db)
- ✅ Add `visibility`, `shared_with_users` to threads table (sessions.db)
- ✅ Create `thread_users` table (sessions.db) - OPTION B
- ✅ Create `thread_shares` table (sessions.db) - OPTION B

### Backend Changes
- ✅ Create `workspace_routes.py` (15+ new endpoints)
- ✅ Create `workspace_manager.py` (workspace CRUD + membership)
- ✅ Update `thread_routes.py` (add sharing endpoints)
- ✅ Update `thread_manager.py` (fix workspace lookups, add access checks)
- ✅ Create `workspace_auth.py` middleware
- ✅ Create `access_control.py` utilities

### Frontend Changes
- ✅ Add workspace selector dropdown
- ✅ Add workspace settings modal (3 tabs)
- ✅ Add thread sharing modal
- ✅ Add invite member modal
- ✅ Update thread list with workspace context
- ✅ Add visibility indicators
- ✅ Add shared user count display

### Migration Scripts
- ✅ `migrate_workspace_schema.py` - Schema changes
- ✅ `generate_slugs.py` - Generate user/workspace slugs
- ✅ `migrate_workspace_ids.py` - Convert TEXT to INTEGER FK

### Total Estimated Changes
- **Files to create:** 12+
- **Files to update:** 5+
- **Database tables to create:** 4
- **Database tables to update:** 3
- **API endpoints to create:** 20+
- **Estimated LOC:** 3,000-4,000 lines

---

## Implementation Order (Recommended)

1. **Phase 1.1-1.2:** Add user_slug and workspace_slug columns ← START HERE
2. **Phase 4.2:** Generate slugs for existing data
3. **Phase 1.3-1.4:** Create workspace_users and workspace_invitations tables
4. **Phase 4.1:** Migrate existing workspace owners to workspace_users
5. **Phase 1.5:** Fix threads.workspace_id (TEXT → INTEGER)
6. **Phase 4.3:** Migrate thread workspace_id values
7. **Phase 2.3:** Fix ThreadManager.add_message() to use INTEGER workspace_id
8. **TEST:** Verify messages now save correctly ← CRITICAL MILESTONE
9. **Phase 2.1:** Create workspace_routes.py and workspace_manager.py
10. **Phase 3.1-3.2:** Add basic UI (workspace selector, thread filtering)
11. **Phase 1.6-1.7:** Add thread_users and thread_shares tables (Option B)
12. **Phase 2.2:** Add thread sharing endpoints
13. **Phase 3.3-3.4:** Add thread sharing UI
14. **Phase 5:** Implement access control middleware
15. **Phase 6:** Testing and QA

---

**READY TO START?** I can begin with Phase 1.1-1.2 (adding slugs) whenever you're ready!
