from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, Field

from .constants import (
    WorkspaceRole,
    WorkspaceStatus,
    WorkspaceVisibility,
    InvitationStatus,
    DEFAULT_WORKSPACE_SETTINGS
)


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int
    visibility: WorkspaceVisibility = WorkspaceVisibility.PRIVATE
    settings: Optional[Dict] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[WorkspaceVisibility] = None
    settings: Optional[Dict] = None


class Workspace(BaseModel):
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


class WorkspaceMemberCreate(BaseModel):
    workspace_id: int
    user_id: int
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceMemberUpdate(BaseModel):
    role: WorkspaceRole


class WorkspaceMember(BaseModel):
    id: int
    workspace_id: int
    user_id: int
    role: WorkspaceRole
    added_by_user_id: int
    added_at: datetime
    removed_at: Optional[datetime]


class WorkspaceInvitationCreate(BaseModel):
    workspace_id: int
    invited_user_id: Optional[int] = None
    invited_email: str
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceInvitation(BaseModel):
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


class WorkspaceInvitationResponse(BaseModel):
    success: bool
    message: str
    workspace_id: int
    workspace_name: Optional[str] = None
