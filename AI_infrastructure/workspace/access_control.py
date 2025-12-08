"""
Access Control - Workspace Permission System

Handles permission checking and access control for workspaces and threads.
Implements role-based access control (RBAC) with hierarchical permissions.
Uses Supabase PostgreSQL via get_database_connection('ai_infrastructure')
"""

import sys
from typing import Optional, List
from pathlib import Path
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection

from .constants import (
    WorkspaceRole,
    WorkspaceStatus,
    WorkspaceVisibility
)

from .exceptions import (
    WorkspaceNotFoundError,
    WorkspacePermissionError,
    MemberNotFoundError
)


class Permission(str, Enum):
    """Granular permission types"""
    # Workspace permissions
    VIEW_WORKSPACE = "view_workspace"
    EDIT_WORKSPACE = "edit_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    MANAGE_SETTINGS = "manage_settings"
    
    # Member permissions
    VIEW_MEMBERS = "view_members"
    ADD_MEMBERS = "add_members"
    REMOVE_MEMBERS = "remove_members"
    UPDATE_MEMBER_ROLES = "update_member_roles"
    
    # Thread permissions
    CREATE_THREADS = "create_threads"
    VIEW_ALL_THREADS = "view_all_threads"
    EDIT_ALL_THREADS = "edit_all_threads"
    DELETE_ALL_THREADS = "delete_all_threads"
    
    # Invitation permissions
    SEND_INVITATIONS = "send_invitations"
    MANAGE_INVITATIONS = "manage_invitations"


class AccessControl:
    """
    Access Control System
    
    Implements role-based permissions for workspaces and resources.
    
    Methods:
        check_permission() - Check if user has specific permission
        can_access_workspace() - Check workspace access
        can_manage_members() - Check member management permission
        can_create_threads() - Check thread creation permission
        get_user_role() - Get user's role in workspace
        has_role() - Check if user has specific role
        is_workspace_owner() - Check if user is owner
        get_accessible_workspaces() - Get workspaces user can access
    """
    
    # Permission matrix: Role → Permissions
    ROLE_PERMISSIONS = {
        WorkspaceRole.OWNER: [
            # Owner has ALL permissions
            Permission.VIEW_WORKSPACE,
            Permission.EDIT_WORKSPACE,
            Permission.DELETE_WORKSPACE,
            Permission.MANAGE_SETTINGS,
            Permission.VIEW_MEMBERS,
            Permission.ADD_MEMBERS,
            Permission.REMOVE_MEMBERS,
            Permission.UPDATE_MEMBER_ROLES,
            Permission.CREATE_THREADS,
            Permission.VIEW_ALL_THREADS,
            Permission.EDIT_ALL_THREADS,
            Permission.DELETE_ALL_THREADS,
            Permission.SEND_INVITATIONS,
            Permission.MANAGE_INVITATIONS,
        ],
        WorkspaceRole.ADMIN: [
            # Admin has most permissions except delete workspace
            Permission.VIEW_WORKSPACE,
            Permission.EDIT_WORKSPACE,
            Permission.MANAGE_SETTINGS,
            Permission.VIEW_MEMBERS,
            Permission.ADD_MEMBERS,
            Permission.REMOVE_MEMBERS,
            Permission.UPDATE_MEMBER_ROLES,
            Permission.CREATE_THREADS,
            Permission.VIEW_ALL_THREADS,
            Permission.EDIT_ALL_THREADS,
            Permission.DELETE_ALL_THREADS,
            Permission.SEND_INVITATIONS,
            Permission.MANAGE_INVITATIONS,
        ],
        WorkspaceRole.MEMBER: [
            # Member has standard access
            Permission.VIEW_WORKSPACE,
            Permission.VIEW_MEMBERS,
            Permission.CREATE_THREADS,
            Permission.VIEW_ALL_THREADS,
        ],
        WorkspaceRole.VIEWER: [
            # Viewer has minimal read-only access
            Permission.VIEW_WORKSPACE,
        ]
    }
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize AccessControl
        
        Args:
            db_path: Path to ai_infrastructure.db
        """
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        
        self.db_path = str(db_path)
    
    def _get_connection(self):
        """Get Supabase PostgreSQL connection for ai_infrastructure schema"""
        return get_database_connection('ai_infrastructure')
    
    def get_user_role(self, workspace_id: int, user_id: int) -> Optional[WorkspaceRole]:
        """
        Get user's role in workspace
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
        
        Returns:
            WorkspaceRole or None: User's role if member, None otherwise
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if owner
        cursor.execute("""
            SELECT owner_id FROM workspaces WHERE id = %s
        """, (workspace_id,))
        
        workspace_row = cursor.fetchone()
        if not workspace_row:
            conn.close()
            return None
        
        if workspace_row['owner_id'] == user_id:
            conn.close()
            return WorkspaceRole.OWNER
        
        # Check membership
        cursor.execute("""
            SELECT role FROM workspace_users 
            WHERE workspace_id = %s AND user_id = %s AND removed_at IS NULL
        """, (workspace_id, user_id))
        
        member_row = cursor.fetchone()
        conn.close()
        
        if not member_row:
            return None
        
        return WorkspaceRole(member_row['role'])
    
    def check_permission(
        self,
        workspace_id: int,
        user_id: int,
        permission: Permission
    ) -> bool:
        """
        Check if user has specific permission in workspace
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            permission: Permission to check
        
        Returns:
            bool: True if user has permission
        """
        role = self.get_user_role(workspace_id, user_id)
        
        if not role:
            return False
        
        # Check if role has permission
        allowed_permissions = self.ROLE_PERMISSIONS.get(role, [])
        return permission in allowed_permissions
    
    def require_permission(
        self,
        workspace_id: int,
        user_id: int,
        permission: Permission
    ) -> None:
        """
        Require permission or raise exception
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            permission: Required permission
        
        Raises:
            WorkspacePermissionError: If user lacks permission
        """
        if not self.check_permission(workspace_id, user_id, permission):
            raise WorkspacePermissionError(user_id, workspace_id, permission.value)
    
    def has_role(
        self,
        workspace_id: int,
        user_id: int,
        role: WorkspaceRole
    ) -> bool:
        """
        Check if user has specific role
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            role: Role to check
        
        Returns:
            bool: True if user has role
        """
        user_role = self.get_user_role(workspace_id, user_id)
        return user_role == role
    
    def is_workspace_owner(self, workspace_id: int, user_id: int) -> bool:
        """Check if user is workspace owner"""
        return self.has_role(workspace_id, user_id, WorkspaceRole.OWNER)
    
    def is_workspace_admin(self, workspace_id: int, user_id: int) -> bool:
        """Check if user is admin or owner"""
        role = self.get_user_role(workspace_id, user_id)
        return role in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]
    
    def can_access_workspace(self, workspace_id: int, user_id: int) -> bool:
        """Check if user can access workspace"""
        return self.check_permission(workspace_id, user_id, Permission.VIEW_WORKSPACE)
    
    def can_edit_workspace(self, workspace_id: int, user_id: int) -> bool:
        """Check if user can edit workspace"""
        return self.check_permission(workspace_id, user_id, Permission.EDIT_WORKSPACE)
    
    def can_manage_members(self, workspace_id: int, user_id: int) -> bool:
        """Check if user can manage members"""
        return self.check_permission(workspace_id, user_id, Permission.ADD_MEMBERS)
    
    def can_create_threads(self, workspace_id: int, user_id: int) -> bool:
        """Check if user can create threads"""
        return self.check_permission(workspace_id, user_id, Permission.CREATE_THREADS)
    
    def can_view_all_threads(self, workspace_id: int, user_id: int) -> bool:
        """Check if user can view all workspace threads"""
        return self.check_permission(workspace_id, user_id, Permission.VIEW_ALL_THREADS)
    
    def can_send_invitations(self, workspace_id: int, user_id: int) -> bool:
        """Check if user can send invitations"""
        return self.check_permission(workspace_id, user_id, Permission.SEND_INVITATIONS)
    
    def get_accessible_workspaces(self, user_id: int) -> List[int]:
        """
        Get list of workspace IDs user can access
        
        Args:
            user_id: User ID
        
        Returns:
            List[int]: Workspace IDs user is member of
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get workspaces where user is owner or member
        cursor.execute("""
            SELECT DISTINCT w.id FROM workspaces w
            LEFT JOIN workspace_users wu ON w.id = wu.workspace_id
            WHERE w.owner_id = %s 
               OR (wu.user_id = %s AND wu.removed_at IS NULL)
        """, (user_id, user_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [row['id'] for row in rows]
    
    def get_user_permissions(
        self,
        workspace_id: int,
        user_id: int
    ) -> List[Permission]:
        """
        Get all permissions user has in workspace
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
        
        Returns:
            List[Permission]: Permissions user has
        """
        role = self.get_user_role(workspace_id, user_id)
        
        if not role:
            return []
        
        return self.ROLE_PERMISSIONS.get(role, [])
    
    def validate_workspace_access(
        self,
        workspace_id: int,
        user_id: int,
        required_permission: Optional[Permission] = None
    ) -> bool:
        """
        Validate user can access workspace and optionally has specific permission
        
        Args:
            workspace_id: Workspace ID
            user_id: User ID
            required_permission: Optional specific permission
        
        Returns:
            bool: True if validation passes
        
        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspacePermissionError: If user lacks access/permission
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check workspace exists
        cursor.execute("SELECT id, status FROM workspaces WHERE id = %s", (workspace_id,))
        workspace_row = cursor.fetchone()
        conn.close()
        
        if not workspace_row:
            raise WorkspaceNotFoundError(workspace_id=workspace_id)
        
        # Check basic access
        if not self.can_access_workspace(workspace_id, user_id):
            raise WorkspacePermissionError(user_id, workspace_id, "access workspace")
        
        # Check specific permission if required
        if required_permission:
            if not self.check_permission(workspace_id, user_id, required_permission):
                raise WorkspacePermissionError(user_id, workspace_id, required_permission.value)
        
        return True
    
    def filter_accessible_resources(
        self,
        user_id: int,
        resource_workspace_ids: List[int]
    ) -> List[int]:
        """
        Filter list of workspace IDs to only those user can access
        
        Args:
            user_id: User ID
            resource_workspace_ids: List of workspace IDs to filter
        
        Returns:
            List[int]: Workspace IDs user can access
        """
        accessible = self.get_accessible_workspaces(user_id)
        return [wid for wid in resource_workspace_ids if wid in accessible]
    
    def get_role_hierarchy_level(self, role: WorkspaceRole) -> int:
        """
        Get numeric level for role (higher = more permissions)
        
        Args:
            role: WorkspaceRole
        
        Returns:
            int: Hierarchy level (0-3)
        """
        hierarchy = {
            WorkspaceRole.GUEST: 0,
            WorkspaceRole.MEMBER: 1,
            WorkspaceRole.ADMIN: 2,
            WorkspaceRole.OWNER: 3
        }
        return hierarchy.get(role, 0)
    
    def can_modify_role(
        self,
        workspace_id: int,
        modifier_user_id: int,
        target_user_id: int,
        new_role: WorkspaceRole
    ) -> bool:
        """
        Check if user can modify another user's role
        
        Args:
            workspace_id: Workspace ID
            modifier_user_id: User trying to modify role
            target_user_id: User whose role is being modified
            new_role: Proposed new role
        
        Returns:
            bool: True if modification is allowed
        
        Rules:
            - Only owners and admins can modify roles
            - Cannot modify your own role
            - Cannot grant role higher than your own
            - Only owner can grant owner role
        """
        # Cannot modify own role
        if modifier_user_id == target_user_id:
            return False
        
        modifier_role = self.get_user_role(workspace_id, modifier_user_id)
        if not modifier_role:
            return False
        
        # Must have UPDATE_MEMBER_ROLES permission
        if not self.check_permission(workspace_id, modifier_user_id, Permission.UPDATE_MEMBER_ROLES):
            return False
        
        # Only owner can grant owner role
        if new_role == WorkspaceRole.OWNER and modifier_role != WorkspaceRole.OWNER:
            return False
        
        # Cannot grant role higher than your own
        modifier_level = self.get_role_hierarchy_level(modifier_role)
        new_role_level = self.get_role_hierarchy_level(new_role)
        
        if new_role_level > modifier_level:
            return False
        
        return True
    
    def check_thread_access(
        self,
        workspace_id: int,
        user_id: int,
        thread_owner_id: int
    ) -> bool:
        """
        Check if user can access specific thread
        
        Args:
            workspace_id: Workspace ID thread belongs to
            user_id: User trying to access
            thread_owner_id: Thread owner's user ID
        
        Returns:
            bool: True if user can access thread
        
        Rules:
            - Thread owner can always access
            - Users with VIEW_ALL_THREADS permission can access
            - Otherwise no access (unless explicitly shared)
        """
        # Owner can always access own threads
        if user_id == thread_owner_id:
            return True
        
        # Check if user can view all threads in workspace
        return self.check_permission(workspace_id, user_id, Permission.VIEW_ALL_THREADS)
