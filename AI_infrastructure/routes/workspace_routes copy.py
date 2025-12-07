"""
Workspace Management Routes

REST API endpoints for workspace CRUD operations, member management, and invitations.

Routes:
- POST   /api/workspaces                    - Create workspace
- GET    /api/workspaces                    - List user's workspaces
- GET    /api/workspaces/<slug>             - Get workspace details
- PUT    /api/workspaces/<slug>             - Update workspace
- DELETE /api/workspaces/<slug>             - Archive workspace
- GET    /api/workspaces/<slug>/stats       - Get workspace statistics

Member Management:
- POST   /api/workspaces/<slug>/members     - Add member
- GET    /api/workspaces/<slug>/members     - List members
- PUT    /api/workspaces/<slug>/members/<user_id> - Update member role
- DELETE /api/workspaces/<slug>/members/<user_id> - Remove member

Invitations:
- POST   /api/workspaces/<slug>/invitations      - Create invitation
- GET    /api/workspaces/<slug>/invitations      - List invitations
- POST   /api/invitations/<token>/accept         - Accept invitation
- POST   /api/invitations/<token>/decline        - Decline invitation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify
from datetime import datetime
from typing import Dict, Any

from workspace.workspace_manager import WorkspaceManager
from workspace.invitation_manager import InvitationManager
from workspace.access_control import AccessControl
from workspace.models import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceMemberCreate,
    WorkspaceInvitationCreate, WorkspaceListParams
)
from workspace.exceptions import (
    WorkspaceNotFoundError, WorkspacePermissionError, InvalidWorkspaceSlugError,
    DuplicateWorkspaceError, MaxMembersReachedError, UserNotFoundError,
    DuplicateMemberError, InvitationNotFoundError, InvitationExpiredError
)
from workspace.constants import WorkspaceRole, WorkspaceVisibility

# Create blueprint
workspace_bp = Blueprint('workspace', __name__)

# Initialize managers
DB_PATH = 'data/ai_infrastructure.db'
workspace_mgr = WorkspaceManager(DB_PATH)
invitation_mgr = InvitationManager(DB_PATH)
access_control = AccessControl(DB_PATH)


def get_user_id() -> int:
    """Extract user_id from request (placeholder - implement proper auth)"""
    # TODO: Replace with actual JWT token extraction
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        user_id = request.args.get('user_id')
    if not user_id:
        user_id = request.json.get('user_id') if request.json else None
    
    if not user_id:
        raise ValueError("user_id required")
    
    return int(user_id)


def success_response(data: Any, message: str = None, status: int = 200) -> tuple:
    """Standard success response format"""
    response = {
        'success': True,
        'data': data
    }
    if message:
        response['message'] = message
    return jsonify(response), status


def error_response(error: str, message: str = None, status: int = 400) -> tuple:
    """Standard error response format"""
    response = {
        'success': False,
        'error': error
    }
    if message:
        response['message'] = message
    return jsonify(response), status


# ============================================================================
# WORKSPACE CRUD ROUTES
# ============================================================================

@workspace_bp.route('/api/workspaces', methods=['POST'])
def create_workspace():
    """Create new workspace"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        # Create workspace data
        workspace_data = WorkspaceCreate(
            name=data['name'],
            description=data.get('description'),
            owner_id=user_id,
            visibility=WorkspaceVisibility(data.get('visibility', 'private')),
            settings=data.get('settings')
        )
        
        # Create workspace
        workspace = workspace_mgr.create_workspace(workspace_data)
        
        return success_response(
            workspace.dict(),
            message=f"Workspace '{workspace.name}' created successfully",
            status=201
        )
        
    except DuplicateWorkspaceError as e:
        return error_response('duplicate_workspace', str(e), 409)
    except InvalidWorkspaceSlugError as e:
        return error_response('invalid_slug', str(e), 400)
    except ValueError as e:
        return error_response('validation_error', str(e), 400)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces', methods=['GET'])
def list_workspaces():
    """List user's workspaces"""
    try:
        user_id = get_user_id()
        
        # Get query params
        params = WorkspaceListParams(
            user_id=user_id,
            include_archived=request.args.get('include_archived', 'false').lower() == 'true',
            visibility=request.args.get('visibility'),
            page=int(request.args.get('page', 1)),
            per_page=int(request.args.get('per_page', 20))
        )
        
        # Get workspaces
        result = workspace_mgr.list_workspaces(params)
        
        return success_response(result.dict())
        
    except ValueError as e:
        return error_response('validation_error', str(e), 400)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>', methods=['GET'])
def get_workspace(slug: str):
    """Get workspace details"""
    try:
        user_id = get_user_id()
        
        # Get workspace with access check
        workspace = workspace_mgr.get_workspace(
            slug=slug,
            user_id=user_id,
            check_access=True
        )
        
        return success_response(workspace.dict())
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>', methods=['PUT'])
def update_workspace(slug: str):
    """Update workspace"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug)
        
        # Check permissions
        if not access_control.can_manage_workspace(workspace.id, user_id):
            raise WorkspacePermissionError(user_id, workspace.id, "update workspace")
        
        # Create update data
        update_data = WorkspaceUpdate(
            name=data.get('name'),
            description=data.get('description'),
            visibility=WorkspaceVisibility(data['visibility']) if 'visibility' in data else None,
            settings=data.get('settings')
        )
        
        # Update workspace
        updated_workspace = workspace_mgr.update_workspace(workspace.id, update_data)
        
        return success_response(
            updated_workspace.dict(),
            message=f"Workspace '{updated_workspace.name}' updated successfully"
        )
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except ValueError as e:
        return error_response('validation_error', str(e), 400)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>', methods=['DELETE'])
def archive_workspace(slug: str):
    """Archive workspace"""
    try:
        user_id = get_user_id()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug)
        
        # Check permissions (only owner can archive)
        if workspace.owner_id != user_id:
            raise WorkspacePermissionError(user_id, workspace.id, "archive workspace")
        
        # Archive workspace
        result = workspace_mgr.archive_workspace(workspace.id)
        
        return success_response(
            result,
            message=f"Workspace '{workspace.name}' archived successfully"
        )
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>/stats', methods=['GET'])
def get_workspace_stats(slug: str):
    """Get workspace statistics"""
    try:
        user_id = get_user_id()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug, user_id=user_id, check_access=True)
        
        # Get stats
        stats = workspace_mgr.get_workspace_stats(workspace.id)
        
        return success_response(stats.dict())
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except Exception as e:
        return error_response('server_error', str(e), 500)


# ============================================================================
# MEMBER MANAGEMENT ROUTES
# ============================================================================

@workspace_bp.route('/api/workspaces/<slug>/members', methods=['POST'])
def add_member(slug: str):
    """Add member to workspace"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug)
        
        # Check permissions
        if not access_control.can_add_members(workspace.id, user_id):
            raise WorkspacePermissionError(user_id, workspace.id, "add members")
        
        # Create member data
        member_data = WorkspaceMemberCreate(
            workspace_id=workspace.id,
            user_id=data['user_id'],
            role=WorkspaceRole(data.get('role', 'member'))
        )
        
        # Add member
        member = workspace_mgr.add_member(member_data, added_by_user_id=user_id)
        
        return success_response(
            member.dict(),
            message=f"User {member.user_id} added to workspace",
            status=201
        )
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except UserNotFoundError as e:
        return error_response('user_not_found', str(e), 404)
    except DuplicateMemberError as e:
        return error_response('duplicate_member', str(e), 409)
    except MaxMembersReachedError as e:
        return error_response('max_members_reached', str(e), 400)
    except ValueError as e:
        return error_response('validation_error', str(e), 400)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>/members', methods=['GET'])
def list_members(slug: str):
    """List workspace members"""
    try:
        user_id = get_user_id()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug, user_id=user_id, check_access=True)
        
        # Get members
        members = workspace_mgr.get_members(workspace.id)
        
        return success_response([m.dict() for m in members])
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>/members/<int:member_user_id>', methods=['PUT'])
def update_member_role(slug: str, member_user_id: int):
    """Update member role"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug)
        
        # Check permissions
        if not access_control.can_manage_members(workspace.id, user_id):
            raise WorkspacePermissionError(user_id, workspace.id, "manage members")
        
        # Update role
        new_role = WorkspaceRole(data['role'])
        member = workspace_mgr.update_member_role(workspace.id, member_user_id, new_role)
        
        return success_response(
            member.dict(),
            message=f"Member role updated to {new_role.value}"
        )
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except ValueError as e:
        return error_response('validation_error', str(e), 400)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>/members/<int:member_user_id>', methods=['DELETE'])
def remove_member(slug: str, member_user_id: int):
    """Remove member from workspace"""
    try:
        user_id = get_user_id()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug)
        
        # Check permissions
        if not access_control.can_remove_members(workspace.id, user_id):
            raise WorkspacePermissionError(user_id, workspace.id, "remove members")
        
        # Remove member
        result = workspace_mgr.remove_member(workspace.id, member_user_id, removed_by=user_id)
        
        return success_response(
            result,
            message=f"Member removed from workspace"
        )
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except Exception as e:
        return error_response('server_error', str(e), 500)


# ============================================================================
# INVITATION ROUTES
# ============================================================================

@workspace_bp.route('/api/workspaces/<slug>/invitations', methods=['POST'])
def create_invitation(slug: str):
    """Create workspace invitation"""
    try:
        user_id = get_user_id()
        data = request.get_json()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug)
        
        # Check permissions
        if not access_control.can_invite_members(workspace.id, user_id):
            raise WorkspacePermissionError(user_id, workspace.id, "invite members")
        
        # Create invitation data
        invitation_data = WorkspaceInvitationCreate(
            workspace_id=workspace.id,
            invited_email=data['email'],
            role=WorkspaceRole(data.get('role', 'member')),
            invited_user_id=data.get('user_id')
        )
        
        # Create invitation
        invitation = invitation_mgr.create_invitation(invitation_data, invited_by_user_id=user_id)
        
        return success_response(
            invitation.dict(),
            message=f"Invitation sent to {invitation.invited_email}",
            status=201
        )
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except ValueError as e:
        return error_response('validation_error', str(e), 400)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/workspaces/<slug>/invitations', methods=['GET'])
def list_invitations(slug: str):
    """List workspace invitations"""
    try:
        user_id = get_user_id()
        
        # Get workspace
        workspace = workspace_mgr.get_workspace(slug=slug)
        
        # Check permissions
        if not access_control.can_manage_workspace(workspace.id, user_id):
            raise WorkspacePermissionError(user_id, workspace.id, "view invitations")
        
        # Get invitations
        invitations = invitation_mgr.list_invitations(workspace.id)
        
        return success_response([inv.dict() for inv in invitations])
        
    except WorkspaceNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except WorkspacePermissionError as e:
        return error_response('permission_denied', str(e), 403)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/invitations/<token>/accept', methods=['POST'])
def accept_invitation(token: str):
    """Accept workspace invitation"""
    try:
        user_id = get_user_id()
        
        # Accept invitation
        result = invitation_mgr.accept_invitation(token, user_id)
        
        return success_response(
            result.dict(),
            message=f"Successfully joined workspace"
        )
        
    except InvitationNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except InvitationExpiredError as e:
        return error_response('invitation_expired', str(e), 400)
    except DuplicateMemberError as e:
        return error_response('already_member', str(e), 409)
    except Exception as e:
        return error_response('server_error', str(e), 500)


@workspace_bp.route('/api/invitations/<token>/decline', methods=['POST'])
def decline_invitation(token: str):
    """Decline workspace invitation"""
    try:
        user_id = get_user_id()
        
        # Decline invitation
        result = invitation_mgr.decline_invitation(token, user_id)
        
        return success_response(
            result,
            message="Invitation declined"
        )
        
    except InvitationNotFoundError as e:
        return error_response('not_found', str(e), 404)
    except Exception as e:
        return error_response('server_error', str(e), 500)


# Health check
@workspace_bp.route('/api/workspaces/health', methods=['GET'])
def health_check():
    """Workspace system health check"""
    return success_response({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'managers': {
            'workspace': workspace_mgr is not None,
            'invitation': invitation_mgr is not None,
            'access_control': access_control is not None
        }
    })
