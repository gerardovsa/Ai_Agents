"""
Thread Manager - Thread CRUD Operations

Handles all thread lifecycle operations including:
- Create, read, update, delete threads
- Archive and restore threads
- Thread sharing and permissions
- Thread listing and search
- Workspace integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection, convert_sql_placeholders
import psycopg2
from psycopg2.extras import RealDictCursor
import secrets
import string
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from .constants import (
    ThreadStatus,
    ThreadVisibility,
    SharePermission,
    THREAD_SLUG_LENGTH,
    THREAD_SLUG_CHARSET,
    MAX_MESSAGES_PER_THREAD,
    TABLE_THREADS,
    TABLE_THREAD_SHARES,
    ERROR_THREAD_NOT_FOUND,
    ERROR_PERMISSION_DENIED,
    SUCCESS_THREAD_CREATED,
    SUCCESS_THREAD_UPDATED,
    SUCCESS_THREAD_DELETED,
    SUCCESS_THREAD_ARCHIVED,
    SUCCESS_THREAD_SHARED
)

from .models import (
    Thread,
    ThreadCreate,
    ThreadUpdate,
    ThreadListParams,
    ThreadListResponse,
    ThreadShareCreate,
    ThreadShare
)

from .exceptions import (
    ThreadNotFoundError,
    ThreadPermissionError,
    ThreadArchivedError,
    ThreadDeletedError,
    InvalidThreadSlugError,
    DuplicateThreadError,
    DuplicateShareError,
    CannotShareWithSelfError,
    WorkspaceNotFoundError,
    DatabaseError
)


class ThreadManager:
    """
    Thread Manager - Handles thread lifecycle and operations
    
    Methods:
        create_thread() - Create new thread
        get_thread() - Get thread by ID or slug
        update_thread() - Update thread metadata
        delete_thread() - Soft delete thread
        archive_thread() - Archive thread
        restore_thread() - Restore archived/deleted thread
        list_threads() - List threads with filters
        share_thread() - Share thread with user
        revoke_share() - Remove thread share
        check_permission() - Check user permissions
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize ThreadManager
        
        Args:
            db_path: Path to sessions.db (defaults to data/sessions.db)
        """
        if db_path is None:
            root_dir = Path(__file__).parent.parent.parent
            db_path = root_dir / 'data' / 'sessions.db'
        
        self.db_path = str(db_path)
    
    def _get_connection(self) -> psycopg2.extensions.connection:
        """Get database connection (RealDictCursor already configured by get_database_connection)"""
        return get_database_connection('sessions')
    
    def _generate_thread_slug(self) -> str:
        """Generate unique thread slug"""
        return ''.join(secrets.choice(THREAD_SLUG_CHARSET) for _ in range(THREAD_SLUG_LENGTH))
    
    def _ensure_unique_slug(self, slug: str) -> str:
        """Ensure thread slug is unique, regenerate if collision"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            max_attempts = 10
            for attempt in range(max_attempts):
                cursor.execute("SELECT id FROM sessions.threads WHERE thread_slug = %s", (slug,))
                if cursor.fetchone() is None:
                    return slug
                slug = self._generate_thread_slug()
            
            # If we get here, all attempts failed
            raise DuplicateThreadError(slug)
    
    def create_thread(self, thread_data: ThreadCreate) -> Thread:
        """
        Create a new thread
        
        Args:
            thread_data: ThreadCreate model with thread details
        
        Returns:
            Thread: Created thread object
        
        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            DuplicateThreadError: If slug collision occurs
            DatabaseError: If database operation fails
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Generate unique slug
                thread_slug = self._generate_thread_slug()
                thread_slug = self._ensure_unique_slug(thread_slug)
                
                # Verify workspace exists (from ai_infrastructure.db)
                # TODO: Add workspace validation once workspace module is complete
                
                # Generate embedding for thread title (async background job)
                name_embedding = None
                try:
                    from tools.implementations.conversation_memory import generate_embedding
                    # Embed thread name for semantic search
                    if thread_data.name and len(thread_data.name.strip()) > 3:
                        # Combine name + description for richer embedding
                        embed_text = thread_data.name
                        if thread_data.description:
                            embed_text += f". {thread_data.description}"
                        name_embedding = generate_embedding(embed_text[:2000])  # Limit to 2K chars
                except Exception as e:
                    # Non-blocking: Continue even if embedding fails
                    logger.warning(f"Failed to generate thread embedding: {e}")
                
                # Insert thread
                now = datetime.utcnow().isoformat()
                sql, params = convert_sql_placeholders("""
                    INSERT INTO threads (
                        thread_slug, name, description, workspace_id, user_id,
                        agent_id, status, visibility, created_at, updated_at, name_embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    thread_slug,
                    thread_data.name,
                    thread_data.description,
                    thread_data.workspace_id,
                    thread_data.user_id,
                    thread_data.agent_id or "1",
                    thread_data.status.value,
                    thread_data.visibility.value,
                    now,
                    now,
                    name_embedding
                ))

                cursor.execute(sql, params)
                
                thread_id = cursor.lastrowid
                conn.commit()
                
                # Fetch created thread
                thread = self.get_thread(thread_id=thread_id)
                
                return thread
                
            except IntegrityError as e:
                conn.rollback()
                raise DuplicateThreadError(thread_slug)
            except Exception as e:
                conn.rollback()
                raise DatabaseError("create_thread", str(e))
    
    def get_thread(
        self,
        thread_id: Optional[int] = None,
        thread_slug: Optional[str] = None,
        user_id: Optional[int] = None,
        check_permissions: bool = False
    ) -> Thread:
        """
        Get thread by ID or slug
        
        Args:
            thread_id: Thread internal ID
            thread_slug: Thread external slug
            user_id: User ID (for permission check)
            check_permissions: Whether to verify user access
        
        Returns:
            Thread: Thread object
        
        Raises:
            ThreadNotFoundError: If thread doesn't exist
            ThreadPermissionError: If user lacks access
        """
        if not thread_id and not thread_slug:
            raise ValueError("Must provide either thread_id or thread_slug")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Query thread
            if thread_id:
                cursor.execute("SELECT * FROM sessions.threads WHERE id = %s", (thread_id,))
            else:
                cursor.execute("SELECT * FROM sessions.threads WHERE thread_slug = %s", (thread_slug,))
            
            row = cursor.fetchone()
            
            if not row:
                raise ThreadNotFoundError(thread_id=thread_id, thread_slug=thread_slug)
            
            # Check permissions if requested
            if check_permissions and user_id:
                if not self.check_permission(row['id'], user_id, SharePermission.VIEW):
                    raise ThreadPermissionError(user_id, row['id'], SharePermission.VIEW.value)
            
            # Get message count
            cursor.execute("SELECT COUNT(*) FROM sessions.messages WHERE thread_id = %s", (row['id'],))
            message_count = cursor.fetchone()[0]
            
            # Get last message time
            sql, params = convert_sql_placeholders("""
                SELECT created_at FROM sessions.messages 
                WHERE thread_id = %s 
                ORDER BY id DESC LIMIT 1
            """, (row['id'],))

            cursor.execute(sql, params)
            last_msg = cursor.fetchone()
            last_message_at = last_msg[0] if last_msg else None
            
            # Build Thread object
            return Thread(
                id=row['id'],
                thread_slug=row['thread_slug'],
                name=row['name'],
                description=row['description'],
                workspace_id=row['workspace_id'],
                user_id=row['user_id'],
                agent_id=row['agent_id'],
                status=ThreadStatus(row['status']),
                visibility=ThreadVisibility(row['visibility']),
                message_count=message_count,
                last_message_at=last_message_at,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                archived_at=datetime.fromisoformat(row['archived_at']) if row['archived_at'] else None,
                deleted_at=datetime.fromisoformat(row['deleted_at']) if row['deleted_at'] else None
            )
    
    def update_thread(
        self,
        thread_id: int,
        update_data: ThreadUpdate,
        user_id: int
    ) -> Thread:
        """
        Update thread metadata
        
        Args:
            thread_id: Thread ID to update
            update_data: ThreadUpdate model with changes
            user_id: User performing update
        
        Returns:
            Thread: Updated thread object
        
        Raises:
            ThreadNotFoundError: If thread doesn't exist
            ThreadPermissionError: If user lacks permission
            ThreadArchivedError: If thread is archived
        """
        # Check permissions
        thread = self.get_thread(thread_id=thread_id)
        if not self.check_permission(thread_id, user_id, SharePermission.EDIT):
            raise ThreadPermissionError(user_id, thread_id, SharePermission.EDIT.value)
        
        if thread.status == ThreadStatus.ARCHIVED:
            raise ThreadArchivedError(thread_id)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Build update query
            updates = []
            params = []
            
            # Track if we need to regenerate embedding
            regenerate_embedding = False
            
            if update_data.name is not None:
                updates.append("name = ?")
                params.append(update_data.name)
                regenerate_embedding = True
            
            if update_data.description is not None:
                updates.append("description = ?")
                params.append(update_data.description)
                regenerate_embedding = True
            
            # Regenerate embedding if name/description changed
            if regenerate_embedding:
                try:
                    from tools.implementations.conversation_memory import generate_embedding
                    embed_text = update_data.name or thread.name
                    if update_data.description or thread.description:
                        embed_text += f". {update_data.description or thread.description}"
                    name_embedding = generate_embedding(embed_text[:2000])
                    updates.append("name_embedding = ?")
                    params.append(name_embedding)
                except Exception as e:
                    logger.warning(f"Failed to update thread embedding: {e}")
            
            if update_data.status is not None:
                updates.append("status = ?")
                params.append(update_data.status.value)
                
                # Set archived_at if archiving
                if update_data.status == ThreadStatus.ARCHIVED:
                    updates.append("archived_at = ?")
                    params.append(datetime.utcnow().isoformat())
            
            if update_data.visibility is not None:
                updates.append("visibility = ?")
                params.append(update_data.visibility.value)
            
            # Always update updated_at
            updates.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            
            params.append(thread_id)
            
            # Execute update
            cursor.execute(f"""
                UPDATE sessions.threads 
                SET {', '.join(updates)}
                WHERE id = %s
            """, params)
            
            conn.commit()
            conn.close()
            
            # Return updated thread
            return self.get_thread(thread_id=thread_id)
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("update_thread", str(e))
    
    def delete_thread(self, thread_id: int, user_id: int, hard_delete: bool = False) -> dict:
        """
        Delete thread (soft or hard)
        
        Args:
            thread_id: Thread ID to delete
            user_id: User performing deletion
            hard_delete: If True, permanently delete. If False, soft delete.
        
        Returns:
            dict: Success message
        
        Raises:
            ThreadNotFoundError: If thread doesn't exist
            ThreadPermissionError: If user lacks permission
        """
        # Check permissions (must be owner or admin)
        thread = self.get_thread(thread_id=thread_id)
        if thread.user_id != user_id:
            if not self.check_permission(thread_id, user_id, SharePermission.ADMIN):
                raise ThreadPermissionError(user_id, thread_id, SharePermission.ADMIN.value)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if hard_delete:
                # Permanently delete thread and messages
                cursor.execute("DELETE FROM sessions.messages WHERE thread_id = %s", (thread_id,))
                cursor.execute("DELETE FROM sessions.thread_shares WHERE thread_id = %s", (thread_id,))
                cursor.execute("DELETE FROM sessions.threads WHERE id = %s", (thread_id,))
            else:
                # Soft delete
                now = datetime.utcnow().isoformat()
                sql, params = convert_sql_placeholders("""
                    UPDATE sessions.threads 
                    SET status = %s, deleted_at = %s, updated_at = %s
                    WHERE id = %s
                """, (ThreadStatus.DELETED.value, now, now, thread_id))

                cursor.execute(sql, params)
            
            conn.commit()
            conn.close()
            
            return {"success": True, "message": SUCCESS_THREAD_DELETED}
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("delete_thread", str(e))
    
    def archive_thread(self, thread_id: int, user_id: int) -> dict:
        """
        Archive thread
        
        Args:
            thread_id: Thread ID to archive
            user_id: User performing action
        
        Returns:
            dict: Success message
        """
        update_data = ThreadUpdate(status=ThreadStatus.ARCHIVED)
        self.update_thread(thread_id, update_data, user_id)
        return {"success": True, "message": SUCCESS_THREAD_ARCHIVED}
    
    def restore_thread(self, thread_id: int, user_id: int) -> Thread:
        """
        Restore archived or deleted thread
        
        Args:
            thread_id: Thread ID to restore
            user_id: User performing action
        
        Returns:
            Thread: Restored thread
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().isoformat()
            sql, params = convert_sql_placeholders("""
                UPDATE sessions.threads 
                SET status = %s, archived_at = NULL, deleted_at = NULL, updated_at = %s
                WHERE id = %s
            """, (ThreadStatus.ACTIVE.value, now, thread_id))

            cursor.execute(sql, params)
            
            conn.commit()
            conn.close()
            
            return self.get_thread(thread_id=thread_id)
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("restore_thread", str(e))
    
    def list_threads(self, params: ThreadListParams) -> ThreadListResponse:
        """
        List threads with filters and pagination
        
        Args:
            params: ThreadListParams with filters
        
        Returns:
            ThreadListResponse: Paginated thread list
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build WHERE clause
        where_clauses = []
        query_params = []
        
        if params.workspace_id:
            where_clauses.append("workspace_id = %s")
            query_params.append(params.workspace_id)
        
        if params.user_id:
            where_clauses.append("user_id = %s")
            query_params.append(params.user_id)
        
        if params.status:
            where_clauses.append("status = %s")
            query_params.append(params.status.value)
        
        if params.visibility:
            where_clauses.append("visibility = %s")
            query_params.append(params.visibility.value)
        
        if params.search:
            where_clauses.append("(name LIKE %s OR description LIKE %s)")
            search_term = f"%{params.search}%"
            query_params.extend([search_term, search_term])
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) FROM sessions.threads WHERE {where_sql}", query_params)
        total = cursor.fetchone()[0]
        
        # Get paginated results
        offset = (params.page - 1) * params.page_size
        sort_order = "ASC" if params.sort_order.lower() == "asc" else "DESC"
        
        cursor.execute(f"""
            SELECT * FROM sessions.threads 
            WHERE {where_sql}
            ORDER BY {params.sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """, query_params + [params.page_size, offset])
        
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to Thread objects
        threads = []
        for row in rows:
            thread = self.get_thread(thread_id=row['id'])
            threads.append(thread)
        
        has_more = (params.page * params.page_size) < total
        
        return ThreadListResponse(
            threads=threads,
            total=total,
            page=params.page,
            page_size=params.page_size,
            has_more=has_more
        )
    
    def share_thread(self, share_data: ThreadShareCreate) -> ThreadShare:
        """
        Share thread with another user
        
        Args:
            share_data: ThreadShareCreate with share details
        
        Returns:
            ThreadShare: Created share record
        
        Raises:
            ThreadNotFoundError: If thread doesn't exist
            CannotShareWithSelfError: If sharing with self
            DuplicateShareError: If already shared
        """
        # Validate thread exists
        thread = self.get_thread(thread_id=share_data.thread_id)
        
        # Cannot share with self
        if share_data.user_id == share_data.shared_by:
            raise CannotShareWithSelfError(share_data.user_id)
        
        # Check for existing share
        if self.check_permission(share_data.thread_id, share_data.user_id, SharePermission.VIEW):
            raise DuplicateShareError(share_data.user_id, share_data.thread_id)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            now = datetime.utcnow().isoformat()
            sql, params = convert_sql_placeholders("""
                INSERT INTO thread_shares (
                    thread_id, user_id, permission, shared_by, message, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                share_data.thread_id,
                share_data.user_id,
                share_data.permission.value,
                share_data.shared_by,
                share_data.message,
                now
            ))

            cursor.execute(sql, params)
            
            share_id = cursor.lastrowid
            conn.commit()
            
            # Fetch created share
            cursor.execute("SELECT * FROM sessions.thread_shares WHERE id = %s", (share_id,))
            row = cursor.fetchone()
            conn.close()
            
            return ThreadShare(
                id=row['id'],
                thread_id=row['thread_id'],
                user_id=row['user_id'],
                permission=SharePermission(row['permission']),
                shared_by=row['shared_by'],
                message=row['message'],
                accepted=bool(row['accepted']),
                accepted_at=datetime.fromisoformat(row['accepted_at']) if row['accepted_at'] else None,
                created_at=datetime.fromisoformat(row['created_at']),
                revoked_at=datetime.fromisoformat(row['revoked_at']) if row['revoked_at'] else None
            )
            
        except Exception as e:
            conn.rollback()
            conn.close()
            raise DatabaseError("share_thread", str(e))
    
    def check_permission(
        self,
        thread_id: int,
        user_id: int,
        required_permission: SharePermission
    ) -> bool:
        """
        Check if user has required permission for thread
        
        Args:
            thread_id: Thread ID
            user_id: User ID to check
            required_permission: Required permission level
        
        Returns:
            bool: True if user has permission
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if owner
        cursor.execute("SELECT user_id, visibility FROM sessions.threads WHERE id = %s", (thread_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return False
        
        # Owner has all permissions
        if row['user_id'] == user_id:
            conn.close()
            return True
        
        # Check workspace visibility
        # TODO: Implement workspace membership check
        
        # Check explicit share
        sql, params = convert_sql_placeholders("""
            SELECT permission FROM sessions.thread_shares 
            WHERE thread_id = %s AND user_id = %s AND revoked_at IS NULL
        """, (thread_id, user_id))

        cursor.execute(sql, params)
        
        share_row = cursor.fetchone()
        conn.close()
        
        if not share_row:
            return False
        
        # Permission hierarchy: VIEW < COMMENT < EDIT < ADMIN
        permission_levels = {
            SharePermission.VIEW: 1,
            SharePermission.COMMENT: 2,
            SharePermission.EDIT: 3,
            SharePermission.ADMIN: 4
        }
        
        user_level = permission_levels.get(SharePermission(share_row['permission']), 0)
        required_level = permission_levels.get(required_permission, 0)
        
        return user_level >= required_level

