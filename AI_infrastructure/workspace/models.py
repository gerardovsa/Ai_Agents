"""
Workspace Models - Pydantic validation models

Complete data models for workspace system.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator

from .constants import WorkspaceRole, WorkspaceStatus, WorkspaceVisibility, InvitationStatus


class WorkspaceCreate(BaseModel):
    """Create new workspace"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    owner_id: int
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE
    settings: Optional[Dict[str, Any]] = None


class WorkspaceUpdate(BaseModel):
    """Update workspace"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    visibility: Optional[WorkspaceVisibility] = None
    settings: Optional[Dict[str, Any]] = None


class Workspace(BaseModel):
    """Complete workspace record"""
    id: int
    slug: str
    name: str
    description: Optional[str]
    owner_id: int
    visibility: WorkspaceVisibility
    status: WorkspaceStatus
    settings: Optional[Dict[str, Any]] = None
    member_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime]
    archived_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorkspaceMemberCreate(BaseModel):
    """Add member to workspace"""
    workspace_id: int
    user_id: int
    role: WorkspaceRole


class WorkspaceMemberUpdate(BaseModel):
    """Update member role"""
    role: WorkspaceRole


class WorkspaceMember(BaseModel):
    """Workspace member record"""
    id: int
    workspace_id: int
    user_id: int
    role: WorkspaceRole
    added_by_user_id: int
    added_at: datetime
    removed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorkspaceInvitationCreate(BaseModel):
    """Create workspace invitation"""
    workspace_id: int
    invited_user_id: Optional[int] = None
    invited_email: str
    role: WorkspaceRole


class WorkspaceInvitation(BaseModel):
    """Workspace invitation record"""
    id: int
    workspace_id: int
    invited_user_id: Optional[int]
    invited_email: str
    role: WorkspaceRole
    token: str
    status: InvitationStatus
    invited_by_user_id: int
    created_at: datetime
    expires_at: datetime
    responded_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class WorkspaceInvitationResponse(BaseModel):
    """Response after processing invitation"""
    success: bool
    message: str
    workspace_id: int
    workspace_name: Optional[str] = None


class WorkspaceListParams(BaseModel):
    """Parameters for listing workspaces"""
    user_id: int
    limit: int = 50
    offset: int = 0
    status: Optional[WorkspaceStatus] = None
    visibility: Optional[WorkspaceVisibility] = None
    search: Optional[str] = None
    owner_only: bool = False


class WorkspaceListResponse(BaseModel):
    """Response for workspace list"""
    workspaces: List[Workspace]
    total: int
    limit: int
    offset: int


class WorkspaceStats(BaseModel):
    """Workspace statistics"""
    workspace_id: int
    member_count: int
    active_member_count: int
    thread_count: int
    pending_invitation_count: int
    created_at: datetime
