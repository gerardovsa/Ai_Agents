"""
Invitation Manager - Workspace Invitation System

Handles sending, accepting, declining, and managing workspace invitations.
Uses Supabase PostgreSQL via get_database_connection('ai_infrastructure')

File: AI_infrastructure/workspace/invitation_manager.py
Last Updated: 14/12/2025
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.database_utils import get_database_connection
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import secrets

from .constants import (
    WorkspaceRole,
    WorkspaceStatus,
    InvitationStatus
)

from .models import (
    WorkspaceInvitation,
    WorkspaceInvitationCreate,
    WorkspaceInvitationResponse
)

from .exceptions import (
    WorkspaceNotFoundError,
    InvitationNotFoundError,
    InvitationExpiredError,
    InvitationAlreadyProcessedError,
    WorkspaceMemberAlreadyExistsError,
    DatabaseError
)


class InvitationManager:
    """
    Workspace Invitation Manager
    
    Manages lifecycle of workspace invitations.
    
    Methods:
        create_invitation() - Send invitation to user/email
        get_invitation() - Get invitation by ID or token
        accept_invitation() - Accept and join workspace
        decline_invitation() - Decline invitation
        cancel_invitation() - Cancel pending invitation
        list_workspace_invitations() - List invitations for workspace
        list_user_invitations() - List invitations for user
        expire_old_invitations() - Cleanup expired invitations
        resend_invitation() - Resend invitation email
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize InvitationManager
        
        Args:
            db_path: Path to ai_infrastructure.db
        """
        if db_path is None:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
        
        self.db_path = str(db_path)
        self.default_expiry_days = 7  # Invitations expire after 7 days
    
    def _get_connection(self):
        """Get Supabase PostgreSQL connection for ai_infrastructure schema"""
        return get_database_connection('ai_infrastructure')
    
    def _generate_token(self) -> str:
        """Generate secure invitation token"""
        return secrets.token_urlsafe(32)
    
    def create_invitation(
        self,
        invitation_data: WorkspaceInvitationCreate,
        invited_by_user_id: int
    ) -> WorkspaceInvitation:
        """
        Create workspace invitation
        
        Args:
            invitation_data: Invitation data
            invited_by_user_id: User ID sending invitation
        
        Returns:
            WorkspaceInvitation: Created invitation
        
        Raises:
            WorkspaceNotFoundError: If workspace doesn't exist
            WorkspaceMemberAlreadyExistsError: If invited user is already member
        
        ✅ FIXED: Added proper cursor management with multiple queries
        """
        cursor = None
        conn = None
        cursor2 = None  # For fetching created invitation
        cursor3 = None  # For checking existing invitation
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Verify workspace exists
            cursor.execute("SELECT id FROM workspaces WHERE id = %s", (invitation_data.workspace_id,))
            if not cursor.fetchone():
                cursor.close()
                cursor = None
                conn.close()
                conn = None
                raise WorkspaceNotFoundError(workspace_id=invitation_data.workspace_id)
            
            # Check if user already invited or member
            if invitation_data.invited_user_id:
                # Check existing membership
                cursor.execute("""
                    SELECT id FROM workspace_users 
                    WHERE workspace_id = %s AND user_id = %s AND removed_at IS NULL
                """, (invitation_data.workspace_id, invitation_data.invited_user_id))
                
                if cursor.fetchone():
                    cursor.close()
                    cursor = None
                    conn.close()
                    conn = None
                    raise WorkspaceMemberAlreadyExistsError(
                        invitation_data.workspace_id,
                        invitation_data.invited_user_id
                    )
                
                # Check pending invitations
                cursor.execute("""
                    SELECT id FROM workspace_invitations
                    WHERE workspace_id = %s 
                      AND invited_user_id = %s
                      AND status = %s
                      AND expires_at > %s
                """, (
                    invitation_data.workspace_id,
                    invitation_data.invited_user_id,
                    InvitationStatus.PENDING,
                    datetime.now()
                ))
                
                existing = cursor.fetchone()
                if existing:
                    # Close first cursor before second query
                    cursor.close()
                    cursor = None
                    
                    # Return existing invitation instead of creating duplicate
                    cursor3 = conn.cursor()
                    cursor3.execute("SELECT * FROM workspace_invitations WHERE id = %s", (existing['id'],))
                    row = cursor3.fetchone()
                    
                    cursor3.close()
                    cursor3 = None
                    conn.close()
                    conn = None
                    
                    return WorkspaceInvitation(**dict(row))
            
            # Generate invitation token
            token = self._generate_token()
            
            # Calculate expiry
            expires_at = datetime.now() + timedelta(days=self.default_expiry_days)
            
            # Insert invitation
            cursor.execute("""
                INSERT INTO workspace_invitations (
                    workspace_id, invited_user_id, invited_email,
                    role, invited_by_user_id, token, status,
                    created_at, expires_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                invitation_data.workspace_id,
                invitation_data.invited_user_id,
                invitation_data.invited_email,
                invitation_data.role.value,
                invited_by_user_id,
                token,
                InvitationStatus.PENDING.value,
                datetime.now(),
                expires_at
            ))
            
            invitation_id = cursor.lastrowid
            conn.commit()
            
            # Close first cursor before fetching
            cursor.close()
            cursor = None
            
            # Fetch created invitation with new cursor
            cursor2 = conn.cursor()
            cursor2.execute("SELECT * FROM workspace_invitations WHERE id = %s", (invitation_id,))
            row = cursor2.fetchone()
            
            cursor2.close()
            cursor2 = None
            conn.close()
            conn = None
            
            return WorkspaceInvitation(**dict(row))
        
        except (WorkspaceNotFoundError, WorkspaceMemberAlreadyExistsError):
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise DatabaseError("create_invitation", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if cursor2:
                try:
                    cursor2.close()
                except:
                    pass
            if cursor3:
                try:
                    cursor3.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def get_invitation(
        self,
        invitation_id: Optional[int] = None,
        token: Optional[str] = None
    ) -> WorkspaceInvitation:
        """
        Get invitation by ID or token
        
        Args:
            invitation_id: Invitation ID
            token: Invitation token
        
        Returns:
            WorkspaceInvitation: Invitation details
        
        Raises:
            InvitationNotFoundError: If invitation not found
            ValueError: If neither ID nor token provided
        
        ✅ FIXED: Added proper cursor management
        """
        if not invitation_id and not token:
            raise ValueError("Either invitation_id or token must be provided")
        
        cursor = None
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if invitation_id:
                cursor.execute("SELECT * FROM workspace_invitations WHERE id = %s", (invitation_id,))
            else:
                cursor.execute("SELECT * FROM workspace_invitations WHERE token = %s", (token,))
            
            row = cursor.fetchone()
            
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            if not row:
                raise InvitationNotFoundError(invitation_id=invitation_id, token=token)
            
            return WorkspaceInvitation(**dict(row))
            
        except InvitationNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError("get_invitation", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def accept_invitation(
        self,
        token: str,
        user_id: int
    ) -> WorkspaceInvitationResponse:
        """
        Accept workspace invitation
        
        Args:
            token: Invitation token
            user_id: User ID accepting invitation
        
        Returns:
            WorkspaceInvitationResponse: Result with workspace details
        
        Raises:
            InvitationNotFoundError: If invitation not found
            InvitationExpiredError: If invitation expired
            InvitationAlreadyProcessedError: If already accepted/declined
        
        ✅ FIXED: Added proper cursor management with multiple queries
        """
        # Get invitation (opens its own connection)
        invitation = self.get_invitation(token=token)
        
        # Validate invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationAlreadyProcessedError(invitation.id, invitation.status)
        
        # Check expiry
        if invitation.expires_at < datetime.now():
            raise InvitationExpiredError(invitation.id)
        
        # Verify user matches invitation
        if invitation.invited_user_id and invitation.invited_user_id != user_id:
            raise ValueError("Invitation not for this user")
        
        cursor = None
        conn = None
        cursor2 = None  # For fetching workspace
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Add user to workspace
            cursor.execute("""
                INSERT INTO workspace_users (
                    workspace_id, user_id, role, added_by_user_id, added_at
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                invitation.workspace_id,
                user_id,
                invitation.role,
                invitation.invited_by_user_id,
                datetime.now()
            ))
            
            # Mark invitation as accepted
            cursor.execute("""
                UPDATE workspace_invitations
                SET status = %s, responded_at = %s
                WHERE id = %s
            """, (InvitationStatus.ACCEPTED, datetime.now(), invitation.id))
            
            conn.commit()
            
            # Close first cursor before second query
            cursor.close()
            cursor = None
            
            # Get workspace details with new cursor
            cursor2 = conn.cursor()
            cursor2.execute("SELECT * FROM workspaces WHERE id = %s", (invitation.workspace_id,))
            workspace_row = cursor2.fetchone()
            
            cursor2.close()
            cursor2 = None
            conn.close()
            conn = None
            
            return WorkspaceInvitationResponse(
                success=True,
                message="Invitation accepted successfully",
                workspace_id=invitation.workspace_id,
                workspace_name=workspace_row['name'] if workspace_row else None
            )
        
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise DatabaseError("accept_invitation", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if cursor2:
                try:
                    cursor2.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def decline_invitation(self, token: str, user_id: int) -> WorkspaceInvitationResponse:
        """
        Decline workspace invitation
        
        Args:
            token: Invitation token
            user_id: User ID declining invitation
        
        Returns:
            WorkspaceInvitationResponse: Result
        
        Raises:
            InvitationNotFoundError: If invitation not found
            InvitationAlreadyProcessedError: If already processed
        
        ✅ FIXED: Added proper cursor management
        """
        # Get invitation (opens its own connection)
        invitation = self.get_invitation(token=token)
        
        # Validate invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationAlreadyProcessedError(invitation.id, invitation.status)
        
        # Verify user matches invitation
        if invitation.invited_user_id and invitation.invited_user_id != user_id:
            raise ValueError("Invitation not for this user")
        
        cursor = None
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE workspace_invitations
                SET status = %s, responded_at = %s
                WHERE id = %s
            """, (InvitationStatus.DECLINED, datetime.now(), invitation.id))
            
            conn.commit()
            
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            return WorkspaceInvitationResponse(
                success=True,
                message="Invitation declined",
                workspace_id=invitation.workspace_id
            )
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise DatabaseError("decline_invitation", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def cancel_invitation(self, invitation_id: int, user_id: int) -> bool:
        """
        Cancel pending invitation
        
        Args:
            invitation_id: Invitation ID
            user_id: User cancelling (must be inviter or admin)
        
        Returns:
            bool: True if cancelled
        
        Raises:
            InvitationNotFoundError: If invitation not found
            InvitationAlreadyProcessedError: If already processed
        
        ✅ FIXED: Added proper cursor management
        """
        # Get invitation (opens its own connection)
        invitation = self.get_invitation(invitation_id=invitation_id)
        
        # Validate can cancel
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationAlreadyProcessedError(invitation.id, invitation.status)
        
        cursor = None
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE workspace_invitations
                SET status = %s, responded_at = %s
                WHERE id = %s
            """, (InvitationStatus.CANCELLED, datetime.now(), invitation_id))
            
            conn.commit()
            
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            return True
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise DatabaseError("cancel_invitation", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def list_workspace_invitations(
        self,
        workspace_id: int,
        status: Optional[InvitationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WorkspaceInvitation]:
        """
        List invitations for workspace
        
        Args:
            workspace_id: Workspace ID
            status: Optional status filter
            limit: Max results
            offset: Pagination offset
        
        Returns:
            List[WorkspaceInvitation]: Invitations
        
        ✅ FIXED: Added proper cursor management
        """
        cursor = None
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM workspace_invitations WHERE workspace_id = %s"
            params = [workspace_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            return [WorkspaceInvitation(**dict(row)) for row in rows]
            
        except Exception as e:
            raise DatabaseError("list_workspace_invitations", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def list_user_invitations(
        self,
        user_id: int,
        status: Optional[InvitationStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WorkspaceInvitation]:
        """
        List invitations for user
        
        Args:
            user_id: User ID
            status: Optional status filter
            limit: Max results
            offset: Pagination offset
        
        Returns:
            List[WorkspaceInvitation]: User's invitations
        
        ✅ FIXED: Added proper cursor management
        """
        cursor = None
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM workspace_invitations WHERE invited_user_id = %s"
            params = [user_id]
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            return [WorkspaceInvitation(**dict(row)) for row in rows]
            
        except Exception as e:
            raise DatabaseError("list_user_invitations", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def expire_old_invitations(self) -> int:
        """
        Mark expired invitations
        
        Returns:
            int: Number of invitations expired
        
        ✅ FIXED: Added proper cursor management
        """
        cursor = None
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE workspace_invitations
                SET status = %s
                WHERE status = %s
                  AND expires_at < %s
            """, (InvitationStatus.EXPIRED, InvitationStatus.PENDING, datetime.now()))
            
            count = cursor.rowcount
            conn.commit()
            
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            
            return count
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise DatabaseError("expire_old_invitations", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def resend_invitation(self, invitation_id: int) -> WorkspaceInvitation:
        """
        Resend invitation (extend expiry)
        
        Args:
            invitation_id: Invitation ID
        
        Returns:
            WorkspaceInvitation: Updated invitation
        
        Raises:
            InvitationNotFoundError: If invitation not found
            InvitationAlreadyProcessedError: If not pending
        
        ✅ FIXED: Added proper cursor management with multiple queries
        """
        # Get invitation (opens its own connection)
        invitation = self.get_invitation(invitation_id=invitation_id)
        
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationAlreadyProcessedError(invitation.id, invitation.status)
        
        # Extend expiry
        new_expiry = datetime.now() + timedelta(days=self.default_expiry_days)
        
        cursor = None
        conn = None
        cursor2 = None  # For fetching updated invitation
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE workspace_invitations
                SET expires_at = %s
                WHERE id = %s
            """, (new_expiry, invitation_id))
            
            conn.commit()
            
            # Close first cursor before second query
            cursor.close()
            cursor = None
            
            # Fetch updated invitation with new cursor
            cursor2 = conn.cursor()
            cursor2.execute("SELECT * FROM workspace_invitations WHERE id = %s", (invitation_id,))
            row = cursor2.fetchone()
            
            cursor2.close()
            cursor2 = None
            conn.close()
            conn = None
            
            return WorkspaceInvitation(**dict(row))
            
        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            raise DatabaseError("resend_invitation", str(e))
        finally:
            if cursor:
                try:
                    cursor.close()
                except:
                    pass
            if cursor2:
                try:
                    cursor2.close()
                except:
                    pass
            if conn:
                try:
                    conn.close()
                except:
                    pass