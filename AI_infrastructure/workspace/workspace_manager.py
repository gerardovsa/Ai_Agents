"""
Workspace Manager - Workspace CRUD Operations

Handles all workspace lifecycle operations including:
- Create, read, update, delete workspaces
- Member management (add, remove, update roles)
- Access control and permissions
- Workspace settings and configuration
- Integration with thread system
"""

import sqlite3
import sys
import secrets
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection
from pathlib import Path

from .constants import (
    WorkspaceRole,
    WorkspaceStatus,
    WorkspaceVisibility,
    WORKSPACE_SLUG_LENGTH,
    WORKSPACE_SLUG_CHARSET,
    MAX_MEMBERS_PER_WORKSPACE,
    TABLE_WORKSPACES,
    TABLE_WORKSPACE_USERS,
    ERROR_WORKSPACE_NOT_FOUND,
    ERROR_PERMISSION_DENIED,
    ERROR_MAX_MEMBERS_REACHED,
    SUCCESS_WORKSPACE_CREATED,
    SUCCESS_WORKSPACE_UPDATED,
    SUCCESS_MEMBER_ADDED,
    SUCCESS_MEMBER_REMOVED
)

from .models import (
    Workspace,
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceMember,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceListParams,
    WorkspaceListResponse,
    WorkspaceStats
)

from .exceptions import (
    WorkspaceNotFoundError,
    WorkspacePermissionError,
    WorkspaceArchivedError,
    InvalidWorkspaceSlugError,
    DuplicateWorkspaceError,
    MaxMembersReachedError,
    UserNotFoundError,
    MemberNotFoundError,
    DuplicateMemberError,
    CannotRemoveSelfError,
    DatabaseError
)


class WorkspaceManager:
    """
    Workspace Manager - Handles workspace lifecycle and operations
    
    Methods:
        create_workspace() - Create new workspace
        get_workspace() - Get workspace by ID or slug
        update_workspace() - Update workspace metadata
        delete_workspace() - Soft delete workspace
        archive_workspace() - Archive workspace
        list_workspaces() - List workspaces with filters
        add_member() - Add user to workspace
        remove_member() - Remove user from workspace
        update_member_role() - Change member role
        get_members() - List workspace members
        check_membership() - Check if user is member
        get_user_workspaces() - Get workspaces for user
        get_workspace_stats() - Get workspace statistics
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize WorkspaceManager
        
        Args:
            db_path: Path to ai_infrastructure.db (defaults to data/ai_infrastructure.db)
        """
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        
        self.db_path = str(db_path)
    
    def _get_connection(self):
        """Get database connection (SQLite or Supabase)"""
        conn = get_database_connection('ai_infrastructure')
        if hasattr(conn, 'row_factory'):  # SQLite
            conn.row_factory = sqlite3.Row
        return conn
    
    def _generate_workspace_slug(self) -> str:
        """Generate unique workspace slug"""
        return ''.join(secrets.choice(WORKSPACE_SLUG_CHARSET) for _ in range(WORKSPACE_SLUG_LENGTH))
    
    def _ensure_unique_slug(self, slug: str) -> str:
        """Ensure workspace slug is unique, regenerate if collision"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        max_attempts = 10
        for attempt in range(max_attempts):
            cursor.execute("SELECT id FROM workspaces WHERE slug = %s", (slug,))
            if cursor.fetchone() is None:
                conn.close()
                return slug
            slug = self._generate_workspace_slug()
        
        conn.close()
        raise DuplicateWorkspaceError(slug)
    
    def create_workspace(self, workspace_data: WorkspaceCreate) -> Workspace:
        """
        Create a new workspace
        
        Args:
            workspace_data: WorkspaceCreate model with workspace details
        
        Returns:
            Workspace: Created workspace object
        
        Raises:
            DuplicateWorkspaceError: If slug collision occurs
            UserNotFoundError: If owner doesn't exist
            DatabaseError: If database operation fails
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Generate unique slug from workspace name
            from .slug_generator import SlugGenerator
            slug_gen = SlugGenerator(self.db_path)
            workspace_slug = slug_gen.generate_workspace_slug(workspace_data.name)
            
            # Verify owner exists
            cursor.execute("SELECT id FROM ai_infrastructure.users WHERE id = %s", (workspace_data.owner_id,))
            if not cursor.fetchone():
                conn.close()
                raise UserNotFoundError(workspace_data.owner_id)
            
            # Insert workspace
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                INSERT INTO workspaces (
                    slug, name, description, user_id, owner_id, status, visibility,
                    settings, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                workspace_slug,
                workspace_data.name,
                workspace_data.description,
                workspace_data.owner_id,  # user_id (legacy column)
                workspace_data.owner_id,  # owner_id (new column)
                WorkspaceStatus.ACTIVE.value,  # New workspaces are active
                workspace_data.visibility.value,
                None,  # settings as JSON
                now,
                now
            ))
            
            workspace_id = cursor.lastrowid
            
            # Add owner as member with OWNER role
            cursor.execute("""
                INSERT INTO workspace_users (
                    workspace_id, user_id, role, added_by_user_id, added_at
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (workspace_id, workspace_data.owner_id, WorkspaceRole.OWNER.value, workspace_data.owner_id, now))
            
            conn.commit()
            
            # Fetch created workspace
            workspace = self.get_workspace(workspace_id=workspace_id)
            conn.close()
            
            return workspace
            
        except (UserNotFoundError, DuplicateWorkspaceError):
            conn.rollback()
            conn.close()
            raise
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("create_workspace", str(e))
    
    def get_workspace(
        self,
        workspace_id: Optional[int] = None,
        workspace_slug: Optional[str] = None,
        slug: Optional[str] = None,
        user_id: Optional[int] = None,
        check_access: bool = False
    ) -> Workspace:
        """
        Get workspace by ID or slug
        
        Args:
            workspace_id: Workspace internal ID
            workspace_slug: Workspace external slug (deprecated, use slug)
            slug: Workspace external slug (preferred parameter name)
            user_id: User ID (for access check)
            check_access: Whether to verify user membership
        
        Returns:
            Workspace: Workspace object
        
        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspacePermissionError: If user lacks access
        """
        # Support both slug and workspace_slug parameter names
        effective_slug = slug or workspace_slug
        
        if not workspace_id and not effective_slug:
            raise ValueError("Must provide either workspace_id or slug")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Query workspace
        if workspace_id:
            cursor.execute("SELECT * FROM workspaces WHERE id = %s", (workspace_id,))
        else:
            cursor.execute("SELECT * FROM workspaces WHERE slug = %s", (effective_slug,))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise WorkspaceNotFoundError(workspace_id=workspace_id, workspace_slug=effective_slug)
        
        # Check access if requested
        if check_access and user_id:
            if not self.check_membership(row['id'], user_id):
                conn.close()
                raise WorkspacePermissionError(user_id, row['id'], "access workspace")
        
        # Get member count
        cursor.execute("""
            SELECT COUNT(*) FROM workspace_users 
            WHERE workspace_id = %s AND removed_at IS NULL
        """, (row['id'],))
        member_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Build Workspace object
        return Workspace(
            id=row['id'],
            slug=row['slug'],
            name=row['name'],
            description=row['description'],
            owner_id=row['owner_id'],
            status=WorkspaceStatus(row['status']),
            visibility=WorkspaceVisibility(row['visibility']),
            member_count=member_count,
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            archived_at=datetime.fromisoformat(row['archived_at']) if row['archived_at'] else None
        )
    
    def update_workspace(
        self,
        workspace_id: int,
        update_data: WorkspaceUpdate,
        user_id: int
    ) -> Workspace:
        """
        Update workspace metadata
        
        Args:
            workspace_id: Workspace ID to update
            update_data: WorkspaceUpdate model with changes
            user_id: User performing update
        
        Returns:
            Workspace: Updated workspace object
        
        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspacePermissionError: If user lacks permission
        """
        # Check permissions (must be owner or admin)
        workspace = self.get_workspace(workspace_id=workspace_id)
        member = self.get_member(workspace_id, user_id)
        
        if member.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
            raise WorkspacePermissionError(user_id, workspace_id, "update workspace")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            updates = []
            params = []
            
            if update_data.name is not None:
                updates.append("name = %s")
                params.append(update_data.name)
            
            if update_data.description is not None:
                updates.append("description = %s")
                params.append(update_data.description)
            
            if update_data.status is not None:
                updates.append("status = %s")
                params.append(update_data.status.value)
                
                if update_data.status == WorkspaceStatus.ARCHIVED:
                    updates.append("archived_at = %s")
                    params.append(datetime.utcnow().isoformat())
            
            if update_data.visibility is not None:
                updates.append("visibility = %s")
                params.append(update_data.visibility.value)
            
            updates.append("updated_at = %s")
            params.append(datetime.utcnow().isoformat())
            
            params.append(workspace_id)
            
            cursor.execute(f"""
                UPDATE workspaces 
                SET {', '.join(updates)}
                WHERE id = %s
            """, params)
            
            conn.commit()
            conn.close()
            
            return self.get_workspace(workspace_id=workspace_id)
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("update_workspace", str(e))
    
    def delete_workspace(self, workspace_id: int, user_id: int, hard_delete: bool = False) -> dict:
        """
        Delete workspace (soft or hard)
        
        Args:
            workspace_id: Workspace ID to delete
            user_id: User performing deletion (must be owner)
            hard_delete: If True, permanently delete
        
        Returns:
            dict: Success message
        
        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspacePermissionError: If user is not owner
        """
        workspace = self.get_workspace(workspace_id=workspace_id)
        
        if workspace.owner_id != user_id:
            raise WorkspacePermissionError(user_id, workspace_id, "delete workspace")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if hard_delete:
                # TODO: Delete all related data (threads, messages, etc.)
                cursor.execute("DELETE FROM workspace_users WHERE workspace_id = %s", (workspace_id,))
                cursor.execute("DELETE FROM workspaces WHERE id = %s", (workspace_id,))
            else:
                # Soft delete
                now = datetime.utcnow().isoformat()
                cursor.execute("""
                    UPDATE workspaces 
                    SET status = %s, archived_at = %s, updated_at = %s
                    WHERE id = %s
                """, (WorkspaceStatus.ARCHIVED.value, now, now, workspace_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "Workspace deleted successfully"}
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("delete_workspace", str(e))
    
    def list_workspaces(self, params: WorkspaceListParams) -> WorkspaceListResponse:
        """
        List workspaces with filters and pagination
        
        Args:
            params: WorkspaceListParams with filters
        
        Returns:
            WorkspaceListResponse: Paginated workspace list
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        where_clauses = []
        query_params = []
        
        if params.owner_id:
            where_clauses.append("owner_id  = %s")
            query_params.append(params.owner_id)
        
        if params.user_id:
            # User is member
            where_clauses.append("""
                id IN (
                    SELECT workspace_id FROM workspace_users 
                    WHERE user_id = %s AND removed_at IS NULL
                )
            """)
            query_params.append(params.user_id)
        
        if params.status:
            where_clauses.append("status  = %s")
            query_params.append(params.status.value)
        
        if params.visibility:
            where_clauses.append("visibility  = %s")
            query_params.append(params.visibility.value)
        
        if params.search:
            where_clauses.append("(name LIKE %s OR description LIKE %s)")
            search_term = f"%{params.search}%"
            query_params.extend([search_term, search_term])
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM workspaces WHERE {where_sql}", query_params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        offset = (params.page - 1) * params.page_size
        sort_order = "ASC" if params.sort_order.lower() == "asc" else "DESC"
        
        cursor.execute(f"""
            SELECT * FROM workspaces 
            WHERE {where_sql}
            ORDER BY {params.sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """, query_params + [params.page_size, offset])
        
        rows = cursor.fetchall()
        conn.close()
        
        workspaces = []
        for row in rows:
            workspace = self.get_workspace(workspace_id=row['id'])
            workspaces.append(workspace)
        
        has_more = (params.page * params.page_size) < total
        
        return WorkspaceListResponse(
            workspaces=workspaces,
            total=total,
            page=params.page,
            page_size=params.page_size,
            has_more=has_more
        )
    
    def add_member(self, member_data: WorkspaceMemberCreate, added_by_user_id: int) -> WorkspaceMember:
        """
        Add user to workspace
        
        Args:
            member_data: WorkspaceMemberCreate with member details
            added_by_user_id: ID of user adding this member
        
        Returns:
            WorkspaceMember: Created member record
        
        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            UserNotFoundError: If user doesn't exist
            DuplicateMemberError: If user is already member
            MaxMembersReachedError: If workspace at capacity
        """
        # Verify workspace exists
        workspace = self.get_workspace(workspace_id=member_data.workspace_id)
        
        # Check if already member
        if self.check_membership(member_data.workspace_id, member_data.user_id):
            raise DuplicateMemberError(member_data.user_id, member_data.workspace_id)
        
        # Check member limit
        if workspace.member_count >= MAX_MEMBERS_PER_WORKSPACE:
            raise MaxMembersReachedError(member_data.workspace_id, MAX_MEMBERS_PER_WORKSPACE)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify user exists
            cursor.execute("SELECT id FROM ai_infrastructure.users WHERE id = %s", (member_data.user_id,))
            if not cursor.fetchone():
                conn.close()
                raise UserNotFoundError(member_data.user_id)
            
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                INSERT INTO workspace_users (
                    workspace_id, user_id, role, added_by_user_id, added_at
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                member_data.workspace_id,
                member_data.user_id,
                member_data.role.value,
                added_by_user_id,
                now
            ))
            
            member_id = cursor.lastrowid
            conn.commit()
            
            # Fetch created member
            cursor.execute("SELECT * FROM workspace_users WHERE id = %s", (member_id,))
            row = cursor.fetchone()
            conn.close()
            
            return WorkspaceMember(
                id=row['id'],
                workspace_id=row['workspace_id'],
                user_id=row['user_id'],
                role=WorkspaceRole(row['role']),
                added_by_user_id=row['added_by_user_id'],
                added_at=datetime.fromisoformat(row['added_at']),
                removed_at=datetime.fromisoformat(row['removed_at']) if row['removed_at'] else None
            )
            
        except (UserNotFoundError, DuplicateMemberError):
            conn.rollback()
            conn.close()
            raise
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("add_member", str(e))
    
    def remove_member(self, workspace_id: int, user_id: int, removed_by: int) -> dict:
        """
        Remove user from workspace
        
        Args:
            workspace_id: Workspace ID
            user_id: User to remove
            removed_by: User performing removal
        
        Returns:
            dict: Success message
        
        Raises:
            MemberNotFoundError: If user is not member
            CannotRemoveSelfError: If trying to remove self
            WorkspacePermissionError: If lacks permission
        """
        if user_id == removed_by:
            raise CannotRemoveSelfError(user_id)
        
        # Check if member exists
        member = self.get_member(workspace_id, user_id)
        
        # Check permissions
        remover = self.get_member(workspace_id, removed_by)
        if remover.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
            raise WorkspacePermissionError(removed_by, workspace_id, "remove members")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                UPDATE workspace_users 
                SET removed_at = %s
                WHERE workspace_id = %s AND user_id = %s
            """, (now, workspace_id, user_id))
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": SUCCESS_MEMBER_REMOVED}
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("remove_member", str(e))
    
    def update_member_role(
        self,
        workspace_id: int,
        user_id: int,
        new_role: WorkspaceRole,
        updated_by: int
    ) -> WorkspaceMember:
        """
        Update member's role
        
        Args:
            workspace_id: Workspace ID
            user_id: User whose role to update
            new_role: New role
            updated_by: User performing update
        
        Returns:
            WorkspaceMember: Updated member
        """
        # Check permissions
        updater = self.get_member(workspace_id, updated_by)
        if updater.role not in [WorkspaceRole.OWNER, WorkspaceRole.ADMIN]:
            raise WorkspacePermissionError(updated_by, workspace_id, "update member roles")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE workspace_users 
                SET role = %s
                WHERE workspace_id = %s AND user_id = %s AND removed_at IS NULL
            """, (new_role.value, workspace_id, user_id))
            
            conn.commit()
            conn.close()
            
            return self.get_member(workspace_id, user_id)
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("update_member_role", str(e))
    
    def get_member(self, workspace_id: int, user_id: int) -> WorkspaceMember:
        """Get workspace member record"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM workspace_users 
            WHERE workspace_id = %s AND user_id = %s AND removed_at IS NULL
        """, (workspace_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise MemberNotFoundError(user_id, workspace_id)
        
        return WorkspaceMember(
            id=row['id'],
            workspace_id=row['workspace_id'],
            user_id=row['user_id'],
            role=WorkspaceRole(row['role']),
            added_by_user_id=row['added_by_user_id'],
            added_at=datetime.fromisoformat(row['added_at']),
            removed_at=datetime.fromisoformat(row['removed_at']) if row['removed_at'] else None
        )
    
    def get_members(self, workspace_id: int) -> List[WorkspaceMember]:
        """List all workspace members"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM workspace_users 
            WHERE workspace_id = %s AND removed_at IS NULL
            ORDER BY added_at ASC
        """, (workspace_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        members = []
        for row in rows:
            members.append(WorkspaceMember(
                id=row['id'],
                workspace_id=row['workspace_id'],
                user_id=row['user_id'],
                role=WorkspaceRole(row['role']),
                added_by_user_id=row['added_by_user_id'],
                added_at=datetime.fromisoformat(row['added_at']),
                removed_at=datetime.fromisoformat(row['removed_at']) if row['removed_at'] else None
            ))
        
        return members
    
    def check_membership(self, workspace_id: int, user_id: int) -> bool:
        """Check if user is workspace member"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM workspace_users 
            WHERE workspace_id = %s AND user_id = %s AND removed_at IS NULL
        """, (workspace_id, user_id))
        
        result = cursor.fetchone()
        conn.close()
        
        return result is not None
    
    def get_user_workspaces(self, user_id: int) -> List[Workspace]:
        """Get all workspaces user is member of"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT workspace_id FROM workspace_users 
            WHERE user_id = %s AND removed_at IS NULL
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        workspaces = []
        for row in rows:
            workspace = self.get_workspace(workspace_id=row['workspace_id'])
            workspaces.append(workspace)
        
        return workspaces
    
    def get_workspace_stats(self, workspace_id: int) -> WorkspaceStats:
        """Get workspace statistics"""
        workspace = self.get_workspace(workspace_id=workspace_id)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get thread count (from sessions.db - will need to query separately)
        # For now, return placeholder
        thread_count = 0
        
        # Get message count
        message_count = 0
        
        # Get active members
        cursor.execute("""
            SELECT COUNT(*) FROM workspace_users 
            WHERE workspace_id = %s AND removed_at IS NULL
        """, (workspace_id,))
        active_members = cursor.fetchone()[0]
        
        conn.close()
        
        return WorkspaceStats(
            workspace_id=workspace_id,
            member_count=active_members,
            thread_count=thread_count,
            message_count=message_count,
            created_at=workspace.created_at
        )
