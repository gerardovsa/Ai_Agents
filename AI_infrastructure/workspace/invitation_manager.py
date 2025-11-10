"""
Invitation Manager - Workspace Invitation System

Handles sending, accepting, declining, and managing workspace invitations.
"""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
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
    WorkspaceMemberAlreadyExistsError
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
            root_dir = Path(__file__).parent.parent.parent
            db_path = root_dir / 'data' / 'ai_infrastructure.db'
        
        self.db_path = str(db_path)
        self.default_expiry_days = 7  # Invitations expire after 7 days
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
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
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Verify workspace exists
            cursor.execute("SELECT id FROM workspaces WHERE id = ?", (invitation_data.workspace_id,))
            if not cursor.fetchone():
                raise WorkspaceNotFoundError(workspace_id=invitation_data.workspace_id)
            
            # Check if user already invited or member
            if invitation_data.invited_user_id:
                # Check existing membership
                cursor.execute("""
                    SELECT id FROM workspace_users 
                    WHERE workspace_id = ? AND user_id = ? AND removed_at IS NULL
                """, (invitation_data.workspace_id, invitation_data.invited_user_id))
                
                if cursor.fetchone():
                    raise WorkspaceMemberAlreadyExistsError(
                        invitation_data.workspace_id,
                        invitation_data.invited_user_id
                    )
                
                # Check pending invitations
                cursor.execute("""
                    SELECT id FROM workspace_invitations
                    WHERE workspace_id = ? 
                      AND invited_user_id = ?
                      AND status = ?
                      AND expires_at > ?
                """, (
                    invitation_data.workspace_id,
                    invitation_data.invited_user_id,
                    InvitationStatus.PENDING,
                    datetime.now()
                ))
                
                existing = cursor.fetchone()
                if existing:
                    # Return existing invitation instead of creating duplicate
                    cursor.execute("SELECT * FROM workspace_invitations WHERE id = ?", (existing['id'],))
                    row = cursor.fetchone()
                    conn.close()
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
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            
            # Fetch created invitation
            cursor.execute("SELECT * FROM workspace_invitations WHERE id = ?", (invitation_id,))
            row = cursor.fetchone()
            conn.close()
            
            return WorkspaceInvitation(**dict(row))
        
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
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
        """
        if not invitation_id and not token:
            raise ValueError("Either invitation_id or token must be provided")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        if invitation_id:
            cursor.execute("SELECT * FROM workspace_invitations WHERE id = ?", (invitation_id,))
        else:
            cursor.execute("SELECT * FROM workspace_invitations WHERE token = ?", (token,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise InvitationNotFoundError(invitation_id=invitation_id, token=token)
        
        return WorkspaceInvitation(**dict(row))
    
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
        """
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
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Add user to workspace
            cursor.execute("""
                INSERT INTO workspace_users (
                    workspace_id, user_id, role, added_by_user_id, added_at
                ) VALUES (?, ?, ?, ?, ?)
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
                SET status = ?, responded_at = ?
                WHERE id = ?
            """, (InvitationStatus.ACCEPTED, datetime.now(), invitation.id))
            
            conn.commit()
            
            # Get workspace details
            cursor.execute("SELECT * FROM workspaces WHERE id = ?", (invitation.workspace_id,))
            workspace_row = cursor.fetchone()
            conn.close()
            
            return WorkspaceInvitationResponse(
                success=True,
                message="Invitation accepted successfully",
                workspace_id=invitation.workspace_id,
                workspace_name=workspace_row['name'] if workspace_row else None
            )
        
        except Exception as e:
            conn.rollback()
            conn.close()
            raise
    
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
        """
        invitation = self.get_invitation(token=token)
        
        # Validate invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationAlreadyProcessedError(invitation.id, invitation.status)
        
        # Verify user matches invitation
        if invitation.invited_user_id and invitation.invited_user_id != user_id:
            raise ValueError("Invitation not for this user")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE workspace_invitations
            SET status = ?, responded_at = ?
            WHERE id = ?
        """, (InvitationStatus.DECLINED, datetime.now(), invitation.id))
        
        conn.commit()
        conn.close()
        
        return WorkspaceInvitationResponse(
            success=True,
            message="Invitation declined",
            workspace_id=invitation.workspace_id
        )
    
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
        """
        invitation = self.get_invitation(invitation_id=invitation_id)
        
        # Validate can cancel
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationAlreadyProcessedError(invitation.id, invitation.status)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE workspace_invitations
            SET status = ?, responded_at = ?
            WHERE id = ?
        """, (InvitationStatus.CANCELLED, datetime.now(), invitation_id))
        
        conn.commit()
        conn.close()
        
        return True
    
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
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM workspace_invitations WHERE workspace_id = ?"
        params = [workspace_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [WorkspaceInvitation(**dict(row)) for row in rows]
    
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
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM workspace_invitations WHERE invited_user_id = ?"
        params = [user_id]
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [WorkspaceInvitation(**dict(row)) for row in rows]
    
    def expire_old_invitations(self) -> int:
        """
        Mark expired invitations
        
        Returns:
            int: Number of invitations expired
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE workspace_invitations
            SET status = ?
            WHERE status = ?
              AND expires_at < ?
        """, (InvitationStatus.EXPIRED, InvitationStatus.PENDING, datetime.now()))
        
        count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return count
    
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
        """
        invitation = self.get_invitation(invitation_id=invitation_id)
        
        if invitation.status != InvitationStatus.PENDING:
            raise InvitationAlreadyProcessedError(invitation.id, invitation.status)
        
        # Extend expiry
        new_expiry = datetime.now() + timedelta(days=self.default_expiry_days)
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE workspace_invitations
            SET expires_at = ?
            WHERE id = ?
        """, (new_expiry, invitation_id))
        
        conn.commit()
        
        # Fetch updated invitation
        cursor.execute("SELECT * FROM workspace_invitations WHERE id = ?", (invitation_id,))
        row = cursor.fetchone()
        conn.close()
        
        return WorkspaceInvitation(**dict(row))
