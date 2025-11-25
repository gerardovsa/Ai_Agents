"""
Thread Sharing Manager

Handles multi-user thread access, sharing, and permissions.

CRITICAL: Uses sessions.db (thread_users and thread_shares tables)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection
import sqlite3
import secrets
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class ThreadSharingError(Exception):
    """Base exception for thread sharing operations"""
    pass


class ThreadNotFoundError(ThreadSharingError):
    """Thread does not exist"""
    pass


class PermissionDeniedError(ThreadSharingError):
    """User does not have permission for this operation"""
    pass


class ShareNotFoundError(ThreadSharingError):
    """Share record does not exist"""
    pass


class ThreadSharingManager:
    """
    Thread Sharing Manager
    
    Manages multi-user thread access and sharing operations.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with database path"""
        if db_path is None:
            root_dir = Path(__file__).parent.parent.parent
            db_path = root_dir / 'data' / 'sessions.db'
        self.db_path = str(db_path)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = get_database_connection('sessions')
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_thread_by_slug(self, thread_slug: str) -> Optional[Dict[str, Any]]:
        """Get thread by slug"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sessions.threads WHERE thread_slug = %s
        """, (thread_slug,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def _can_share_thread(self, thread_id: int, user_id: int) -> bool:
        """Check if user can share this thread (owner or admin)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if user is thread owner
        cursor.execute("""
            SELECT user_id FROM sessions.threads WHERE id = %s
        """, (thread_id,))
        
        row = cursor.fetchone()
        if row and row['user_id'] == user_id:
            conn.close()
            return True
        
        # Check if user has admin access via thread_users
        cursor.execute("""
            SELECT role FROM sessions.thread_users
            WHERE thread_id = %s AND user_id = %s AND removed_at IS NULL
        """, (thread_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row['role'] in ['owner', 'admin']:
            return True
        
        return False
    
    def share_thread(
        self,
        thread_slug: str,
        shared_by_user_id: int,
        shared_with_user_id: int,
        role: str = 'viewer'
    ) -> Dict[str, Any]:
        """
        Share thread with another user
        
        Args:
            thread_slug: Thread slug (external ID)
            shared_by_user_id: User sharing the thread
            shared_with_user_id: User receiving access
            role: Access role (viewer, editor, admin)
        
        Returns:
            Dict with share details
        
        Raises:
            ThreadNotFoundError: Thread doesn't exist
            PermissionDeniedError: User can't share this thread
        """
        # Get thread
        thread = self._get_thread_by_slug(thread_slug)
        if not thread:
            raise ThreadNotFoundError(f"Thread {thread_slug} not found")
        
        thread_id = thread['id']
        
        # Check permissions
        if not self._can_share_thread(thread_id, shared_by_user_id):
            raise PermissionDeniedError("You don't have permission to share this thread")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if user already has access
            cursor.execute("""
                SELECT id FROM sessions.thread_users
                WHERE thread_id = %s AND user_id = %s AND removed_at IS NULL
            """, (thread_id, shared_with_user_id))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing access
                cursor.execute("""
                    UPDATE sessions.thread_users
                    SET role = %s, access_level = 'read_write', added_by_user_id = %s,
                        added_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (role, shared_by_user_id, existing['id']))
                
                share_action = 'updated'
                user_id = existing['id']
            else:
                # Add new access
                access_level = 'read_write' if role in ['editor', 'admin'] else 'read'
                
                cursor.execute("""
                    INSERT INTO thread_users (
                        thread_id, user_id, role, access_level, 
                        added_by_user_id, added_at
                    ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                """, (thread_id, shared_with_user_id, role, access_level, shared_by_user_id))
                
                user_id = cursor.lastrowid
                share_action = 'added'
            
            # Record share event
            cursor.execute("""
                INSERT INTO thread_shares (
                    thread_id, shared_by_user_id, shared_with_user_id,
                    share_type, action, role_granted, created_at
                ) VALUES (%s, %s, %s, 'direct', %s, %s, CURRENT_TIMESTAMP)
            """, (thread_id, shared_by_user_id, shared_with_user_id, share_action, role))
            
            share_id = cursor.lastrowid
            
            conn.commit()
            
            return {
                'success': True,
                'share_id': share_id,
                'thread_user_id': user_id,
                'thread_slug': thread_slug,
                'thread_id': thread_id,
                'shared_with_user_id': shared_with_user_id,
                'role': role,
                'action': share_action,
                'shared_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            conn.rollback()
            raise ThreadSharingError(f"Failed to share thread: {str(e)}")
        finally:
            conn.close()
    
    def share_thread_by_email(
        self,
        thread_slug: str,
        shared_by_user_id: int,
        email: str,
        role: str = 'viewer'
    ) -> Dict[str, Any]:
        """
        Share thread via email invitation
        
        Args:
            thread_slug: Thread slug
            shared_by_user_id: User sharing the thread
            email: Email address to invite
            role: Access role
        
        Returns:
            Dict with invitation details including token
        """
        # Get thread
        thread = self._get_thread_by_slug(thread_slug)
        if not thread:
            raise ThreadNotFoundError(f"Thread {thread_slug} not found")
        
        thread_id = thread['id']
        
        # Check permissions
        if not self._can_share_thread(thread_id, shared_by_user_id):
            raise PermissionDeniedError("You don't have permission to share this thread")
        
        # Generate invitation token
        share_token = secrets.token_urlsafe(32)
        expires_at = (datetime.now() + timedelta(days=7)).isoformat()
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Record share invitation
            cursor.execute("""
                INSERT INTO thread_shares (
                    thread_id, shared_by_user_id, shared_with_email,
                    share_type, action, role_granted, share_token,
                    created_at, expires_at
                ) VALUES (%s, %s, %s, 'email', 'invited', %s, %s, CURRENT_TIMESTAMP, %s)
            """, (thread_id, shared_by_user_id, email, role, share_token, expires_at))
            
            share_id = cursor.lastrowid
            
            conn.commit()
            
            return {
                'success': True,
                'share_id': share_id,
                'thread_slug': thread_slug,
                'thread_id': thread_id,
                'invited_email': email,
                'role': role,
                'share_token': share_token,
                'expires_at': expires_at,
                'share_link': f"/accept-thread-share/{share_token}"
            }
        
        except Exception as e:
            conn.rollback()
            raise ThreadSharingError(f"Failed to create invitation: {str(e)}")
        finally:
            conn.close()
    
    def accept_thread_share(
        self,
        share_token: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Accept a thread share invitation
        
        Args:
            share_token: Share invitation token
            user_id: User accepting the invitation
        
        Returns:
            Dict with thread access details
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get share invitation
            cursor.execute("""
                SELECT * FROM sessions.thread_shares
                WHERE share_token = %s AND revoked_at IS NULL
            """, (share_token,))
            
            share = cursor.fetchone()
            
            if not share:
                raise ShareNotFoundError("Invalid or expired invitation")
            
            # Check expiration
            if share['expires_at']:
                expires_at = datetime.fromisoformat(share['expires_at'])
                if datetime.now() > expires_at:
                    raise ShareNotFoundError("Invitation has expired")
            
            thread_id = share['thread_id']
            role = share['role_granted']
            access_level = 'read_write' if role in ['editor', 'admin'] else 'read'
            
            # Add user to thread_users
            cursor.execute("""
                INSERT INTO thread_users (
                    thread_id, user_id, role, access_level,
                    added_by_user_id, added_at
                ) VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            """, (thread_id, user_id, role, access_level, share['shared_by_user_id']))
            
            thread_user_id = cursor.lastrowid
            
            # Update share record
            cursor.execute("""
                UPDATE sessions.thread_shares
                SET accessed_at = CURRENT_TIMESTAMP, shared_with_user_id = %s
                WHERE id = %s
            """, (user_id, share['id']))
            
            # Get thread details
            cursor.execute("""
                SELECT thread_slug, title FROM sessions.threads WHERE id = %s
            """, (thread_id,))
            
            thread = cursor.fetchone()
            
            conn.commit()
            
            return {
                'success': True,
                'thread_user_id': thread_user_id,
                'thread_id': thread_id,
                'thread_slug': thread['thread_slug'],
                'thread_title': thread['title'],
                'role': role,
                'access_level': access_level
            }
        
        except Exception as e:
            conn.rollback()
            if isinstance(e, (ShareNotFoundError, ThreadSharingError)):
                raise
            raise ThreadSharingError(f"Failed to accept invitation: {str(e)}")
        finally:
            conn.close()
    
    def revoke_thread_share(
        self,
        thread_slug: str,
        user_id_to_revoke: int,
        revoked_by_user_id: int,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Revoke user's access to thread
        
        Args:
            thread_slug: Thread slug
            user_id_to_revoke: User losing access
            revoked_by_user_id: User revoking access
            reason: Optional reason for revocation
        
        Returns:
            Dict with revocation details
        """
        # Get thread
        thread = self._get_thread_by_slug(thread_slug)
        if not thread:
            raise ThreadNotFoundError(f"Thread {thread_slug} not found")
        
        thread_id = thread['id']
        
        # Check permissions
        if not self._can_share_thread(thread_id, revoked_by_user_id):
            raise PermissionDeniedError("You don't have permission to revoke access")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Remove from thread_users
            cursor.execute("""
                UPDATE sessions.thread_users
                SET removed_at = CURRENT_TIMESTAMP
                WHERE thread_id = %s AND user_id = %s AND removed_at IS NULL
            """, (thread_id, user_id_to_revoke))
            
            if cursor.rowcount == 0:
                raise ShareNotFoundError("User doesn't have access to this thread")
            
            # Record revocation
            cursor.execute("""
                INSERT INTO thread_shares (
                    thread_id, shared_by_user_id, shared_with_user_id,
                    share_type, action, revoked_by_user_id, revoke_reason,
                    created_at, revoked_at
                ) VALUES (%s, %s, %s, 'direct', 'revoked', %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (thread_id, revoked_by_user_id, user_id_to_revoke, revoked_by_user_id, reason))
            
            conn.commit()
            
            return {
                'success': True,
                'thread_slug': thread_slug,
                'revoked_user_id': user_id_to_revoke,
                'revoked_by': revoked_by_user_id,
                'revoked_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            conn.rollback()
            if isinstance(e, (ShareNotFoundError, ThreadSharingError)):
                raise
            raise ThreadSharingError(f"Failed to revoke access: {str(e)}")
        finally:
            conn.close()
    
    def list_thread_collaborators(self, thread_slug: str) -> List[Dict[str, Any]]:
        """
        List all users with access to thread
        
        Args:
            thread_slug: Thread slug
        
        Returns:
            List of collaborators with roles
        """
        # Get thread
        thread = self._get_thread_by_slug(thread_slug)
        if not thread:
            raise ThreadNotFoundError(f"Thread {thread_slug} not found")
        
        thread_id = thread['id']
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get all active collaborators
        cursor.execute("""
            SELECT tu.*, u.username, u.email
            FROM sessions.thread_users tu
            LEFT JOIN users u ON tu.user_id = u.id
            WHERE tu.thread_id = %s AND tu.removed_at IS NULL
            ORDER BY tu.added_at
        """, (thread_id,))
        
        collaborators = []
        for row in cursor.fetchall():
            collaborators.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'email': row['email'],
                'role': row['role'],
                'access_level': row['access_level'],
                'added_at': row['added_at'],
                'last_accessed_at': row['last_accessed_at']
            })
        
        conn.close()
        
        return collaborators
    
    def list_my_shared_threads(self, user_id: int) -> List[Dict[str, Any]]:
        """
        List threads shared with user
        
        Args:
            user_id: User ID
        
        Returns:
            List of shared threads
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.*, tu.role, tu.access_level, tu.added_at,
                   owner.username as owner_username
            FROM sessions.thread_users tu
            JOIN sessions.threads t ON tu.thread_id = t.id
            LEFT JOIN users owner ON t.user_id = owner.id
            WHERE tu.user_id = %s AND tu.removed_at IS NULL AND t.user_id != %s
            ORDER BY tu.added_at DESC
        """, (user_id, user_id))
        
        threads = []
        for row in cursor.fetchall():
            threads.append({
                'thread_id': row['id'],
                'thread_slug': row['thread_slug'],
                'title': row['title'],
                'owner_id': row['user_id'],
                'owner_username': row['owner_username'],
                'my_role': row['role'],
                'my_access_level': row['access_level'],
                'shared_at': row['added_at'],
                'updated_at': row['updated_at']
            })
        
        conn.close()
        
        return threads
    
    def get_thread_access_level(
        self,
        thread_slug: str,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get user's access level for thread
        
        Args:
            thread_slug: Thread slug
            user_id: User ID
        
        Returns:
            Dict with access details or None if no access
        """
        # Get thread
        thread = self._get_thread_by_slug(thread_slug)
        if not thread:
            return None
        
        thread_id = thread['id']
        
        # Check if owner
        if thread['user_id'] == user_id:
            return {
                'has_access': True,
                'role': 'owner',
                'access_level': 'full',
                'is_owner': True
            }
        
        # Check thread_users
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT role, access_level FROM sessions.thread_users
            WHERE thread_id = %s AND user_id = %s AND removed_at IS NULL
        """, (thread_id, user_id))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'has_access': True,
                'role': row['role'],
                'access_level': row['access_level'],
                'is_owner': False
            }
        
        return {
            'has_access': False,
            'role': None,
            'access_level': None,
            'is_owner': False
        }
