"""
Workspace Constants - Roles, Permissions, and Configuration

FILE: AI_infrastructure/workspace/constants.py
PURPOSE: Define workspace roles, permissions, access levels, and configuration

EXPORTS:
- WorkspaceRole - Enum for workspace roles
- ThreadAccessLevel - Enum for thread access levels
- DefaultPermissions - Permission sets for each role
- InvitationStatus - Invitation states
- ThreadVisibility - Thread visibility options

USED BY:
- workspace/workspace_manager.py (role validation)
- workspace/access_control.py (permission checks)
- routes/workspace_routes.py (API validation)

LAST MODIFIED: 2025-11-09 - Initial creation
"""

from enum import Enum
from typing import Dict, List


class WorkspaceRole(Enum):
    """Workspace membership roles"""
    OWNER = 'owner'      # Created workspace, full control
    ADMIN = 'admin'      # Can manage members and settings
    MEMBER = 'member'    # Can create and view threads
    VIEWER = 'viewer'    # Read-only access
    
    @classmethod
    def is_valid(cls, role: str) -> bool:
        """Check if role string is valid"""
        return role in [r.value for r in cls]
    
    @classmethod
    def all_values(cls) -> List[str]:
        """Get all valid role values"""
        return [r.value for r in cls]


class ThreadAccessLevel(Enum):
    """Thread-level access permissions (Option B)"""
    OWNER = 'owner'          # Thread creator, full control
    EDITOR = 'editor'        # Can add messages and edit metadata
    COMMENTER = 'commenter'  # Can add messages only
    VIEWER = 'viewer'        # Read-only access
    
    @classmethod
    def is_valid(cls, level: str) -> bool:
        """Check if access level string is valid"""
        return level in [l.value for l in cls]
    
    @classmethod
    def all_values(cls) -> List[str]:
        """Get all valid access level values"""
        return [l.value for l in cls]


class WorkspaceStatus(Enum):
    """Workspace status states"""
    ACTIVE = 'active'        # Normal active workspace
    ARCHIVED = 'archived'    # Archived but not deleted
    DELETED = 'deleted'      # Soft-deleted
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if status string is valid"""
        return status in [s.value for s in cls]


class WorkspaceVisibility(Enum):
    """Workspace visibility levels"""
    PRIVATE = 'private'      # Only members can see
    PUBLIC = 'public'        # Anyone can discover
    UNLISTED = 'unlisted'    # Accessible via link only
    
    @classmethod
    def is_valid(cls, visibility: str) -> bool:
        """Check if visibility string is valid"""
        return visibility in [v.value for v in cls]


class ThreadVisibility(Enum):
    """Thread visibility options"""
    WORKSPACE = 'workspace'  # All workspace members can access
    PRIVATE = 'private'      # Only creator and explicitly shared users
    SHARED = 'shared'        # Shared with specific users
    
    @classmethod
    def is_valid(cls, visibility: str) -> bool:
        """Check if visibility string is valid"""
        return visibility in [v.value for v in cls]


class InvitationStatus(Enum):
    """Workspace invitation states"""
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    EXPIRED = 'expired'
    CANCELLED = 'cancelled'
    
    @classmethod
    def is_valid(cls, status: str) -> bool:
        """Check if status string is valid"""
        return status in [s.value for s in cls]


class DefaultPermissions:
    """
    Default permission sets for each workspace role
    
    Permission Keys:
    - can_create_threads: Create new threads in workspace
    - can_delete_threads: Delete any thread in workspace
    - can_edit_threads: Edit any thread metadata
    - can_invite_users: Send workspace invitations
    - can_remove_users: Remove members from workspace
    - can_change_roles: Change member roles
    - can_delete_workspace: Delete entire workspace
    - can_edit_workspace: Edit workspace settings
    - can_view_members: View workspace member list
    - can_share_threads: Share threads with specific users
    """
    
    OWNER: Dict[str, bool] = {
        'can_create_threads': True,
        'can_delete_threads': True,
        'can_edit_threads': True,
        'can_invite_users': True,
        'can_remove_users': True,
        'can_change_roles': True,
        'can_delete_workspace': True,
        'can_edit_workspace': True,
        'can_view_members': True,
        'can_share_threads': True
    }
    
    ADMIN: Dict[str, bool] = {
        'can_create_threads': True,
        'can_delete_threads': True,
        'can_edit_threads': True,
        'can_invite_users': True,
        'can_remove_users': True,
        'can_change_roles': False,  # Cannot change roles
        'can_delete_workspace': False,  # Cannot delete workspace
        'can_edit_workspace': True,
        'can_view_members': True,
        'can_share_threads': True
    }
    
    MEMBER: Dict[str, bool] = {
        'can_create_threads': True,
        'can_delete_threads': False,  # Can only delete own threads
        'can_edit_threads': False,    # Can only edit own threads
        'can_invite_users': False,
        'can_remove_users': False,
        'can_change_roles': False,
        'can_delete_workspace': False,
        'can_edit_workspace': False,
        'can_view_members': True,
        'can_share_threads': True     # Can share own threads
    }
    
    VIEWER: Dict[str, bool] = {
        'can_create_threads': False,
        'can_delete_threads': False,
        'can_edit_threads': False,
        'can_invite_users': False,
        'can_remove_users': False,
        'can_change_roles': False,
        'can_delete_workspace': False,
        'can_edit_workspace': False,
        'can_view_members': True,
        'can_share_threads': False
    }
    
    @classmethod
    def get_permissions(cls, role: str) -> Dict[str, bool]:
        """Get permission set for role"""
        role_map = {
            WorkspaceRole.OWNER.value: cls.OWNER,
            WorkspaceRole.ADMIN.value: cls.ADMIN,
            WorkspaceRole.MEMBER.value: cls.MEMBER,
            WorkspaceRole.VIEWER.value: cls.VIEWER
        }
        return role_map.get(role, {})
    
    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        """Check if role has specific permission"""
        permissions = cls.get_permissions(role)
        return permissions.get(permission, False)


# Configuration Constants
INVITATION_EXPIRY_DAYS = 7  # Invitations expire after 7 days
MAX_WORKSPACE_MEMBERS = 100  # Maximum members per workspace
MAX_MEMBERS_PER_WORKSPACE = 100  # Alias for consistency
MAX_WORKSPACES_PER_USER = 50  # Maximum workspaces a user can own/join
DEFAULT_WORKSPACE_NAME = "{username}'s Workspace"
DEFAULT_WORKSPACE_DESCRIPTION = "Default workspace"

# Table Names
TABLE_WORKSPACES = 'workspaces'
TABLE_WORKSPACE_USERS = 'workspace_users'
TABLE_WORKSPACE_INVITATIONS = 'workspace_invitations'

# Error Messages
ERROR_WORKSPACE_NOT_FOUND = 'Workspace not found'
ERROR_PERMISSION_DENIED = 'Permission denied'
ERROR_MAX_MEMBERS_REACHED = 'Maximum members limit reached'
ERROR_SLUG_EXISTS = 'Slug already exists'

# Success Messages
SUCCESS_WORKSPACE_CREATED = 'Workspace created successfully'
SUCCESS_WORKSPACE_UPDATED = 'Workspace updated successfully'
SUCCESS_MEMBER_ADDED = 'Member added successfully'
SUCCESS_MEMBER_REMOVED = 'Member removed successfully'

# Slug Generation
USER_SLUG_FORMAT = "{username}-{user_id}"  # e.g., john-doe-12
WORKSPACE_SLUG_FORMAT = "{name}-workspace-{id}"  # e.g., team-alpha-workspace-2
MAX_SLUG_LENGTH = 100
WORKSPACE_SLUG_LENGTH = 63  # Maximum workspace slug length
WORKSPACE_SLUG_CHARSET = 'abcdefghijklmnopqrstuvwxyz0123456789-'  # Allowed characters

# Database Paths
AI_INFRASTRUCTURE_DB = 'data/ai_infrastructure.db'
SESSIONS_DB = 'data/sessions.db'

# Default Workspace Settings
DEFAULT_WORKSPACE_SETTINGS = {
    'member_limit': MAX_WORKSPACE_MEMBERS,
    'allow_member_invites': True,
    'require_approval': False,
    'thread_default_visibility': 'workspace',
    'enable_thread_sharing': True
}
