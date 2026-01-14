"""
Workspace Module - Multi-User Workspace Management

This module provides workspace functionality including:
- Workspace CRUD operations
- Workspace membership management
- Access control and permissions
- Invitation system
- Thread-level sharing (Option B)

Structure:
- workspace_manager.py - Core workspace operations
- access_control.py - Permission checking and validation
- invitation_manager.py - Invitation system
- models.py - Data models and schemas
- constants.py - Role definitions, permissions, etc.

Usage:
    from AI_infrastructure.workspace import WorkspaceManager, AccessControl
    
    workspace_mgr = WorkspaceManager()
    access_ctrl = AccessControl()
"""

from .workspace_manager import WorkspaceManager
from .access_control import AccessControl, Permission
from .invitation_manager import InvitationManager
from .slug_generator import SlugGenerator
from .constants import (
    WorkspaceRole, 
    WorkspaceStatus,
    WorkspaceVisibility,
    InvitationStatus,
    ThreadAccessLevel, 
    DefaultPermissions,
    DEFAULT_WORKSPACE_SETTINGS
)
from .models import (
    Workspace,
    WorkspaceCreate,
    WorkspaceUpdate,
    WorkspaceMember,
    WorkspaceMemberCreate,
    WorkspaceMemberUpdate,
    WorkspaceInvitation,
    WorkspaceInvitationCreate,
    WorkspaceInvitationResponse
)
from .exceptions import (
    WorkspaceError,
    WorkspaceNotFoundError,
    WorkspaceSlugExistsError,
    WorkspacePermissionError,
    WorkspaceArchivedError,
    WorkspaceCapacityError,
    WorkspaceMemberNotFoundError,
    WorkspaceMemberAlreadyExistsError,
    CannotRemoveSelfError,
    InvitationError,
    InvitationNotFoundError,
    InvitationExpiredError,
    InvitationAlreadyProcessedError,
    InvalidRoleError,
    SlugError,
    InvalidSlugError,
    ReservedSlugError,
    MemberNotFoundError
)

__all__ = [
    # Managers
    'WorkspaceManager',
    'AccessControl',
    'Permission',
    'InvitationManager',
    'SlugGenerator',
    
    # Constants
    'WorkspaceRole',
    'WorkspaceStatus',
    'WorkspaceVisibility',
    'InvitationStatus',
    'ThreadAccessLevel',
    'DefaultPermissions',
    'DEFAULT_WORKSPACE_SETTINGS',
    
    # Models
    'Workspace',
    'WorkspaceCreate',
    'WorkspaceUpdate',
    'WorkspaceMember',
    'WorkspaceMemberCreate',
    'WorkspaceMemberUpdate',
    'WorkspaceInvitation',
    'WorkspaceInvitationCreate',
    'WorkspaceInvitationResponse',
    
    # Exceptions
    'WorkspaceError',
    'WorkspaceNotFoundError',
    'WorkspaceSlugExistsError',
    'WorkspacePermissionError',
    'WorkspaceArchivedError',
    'WorkspaceCapacityError',
    'WorkspaceMemberNotFoundError',
    'WorkspaceMemberAlreadyExistsError',
    'CannotRemoveSelfError',
    'InvitationError',
    'InvitationNotFoundError',
    'InvitationExpiredError',
    'InvitationAlreadyProcessedError',
    'InvalidRoleError',
    'SlugError',
    'InvalidSlugError',
    'ReservedSlugError',
    'MemberNotFoundError'
]
