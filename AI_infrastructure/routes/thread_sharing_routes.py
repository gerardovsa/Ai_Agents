"""
FILE PATH: C:/Users/gpoli/GIT/AI_agents/AI_infrastructure/routes/thread_sharing_routes.py

Thread Sharing Routes (ENHANCED VERSION)
==========================================

REST API endpoints for thread sharing functionality.

✅ NO CURSOR MANAGEMENT ISSUES - All database operations handled by ThreadSharingManager
✅ ENHANCEMENTS: Logging, validation helpers, better error handling

Endpoints:
- POST /api/threads/<thread_slug>/share - Share thread with user
- POST /api/threads/<thread_slug>/share-email - Share via email
- POST /api/thread-shares/accept/<token> - Accept invitation
- DELETE /api/threads/<thread_slug>/share/<user_id> - Revoke access
- GET /api/threads/<thread_slug>/collaborators - List collaborators
- GET /api/my-shared-threads - List threads shared with me

NOTE: All database cursor management is handled internally by ThreadSharingManager.
      This file has ZERO direct database operations.
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from AI_infrastructure.threads.thread_sharing_manager import (
    ThreadSharingManager,
    ThreadSharingError,
    ThreadNotFoundError,
    PermissionDeniedError,
    ShareNotFoundError
)

# ======================================================================
# SETUP
# ======================================================================

# Create blueprint
thread_sharing_bp = Blueprint('thread_sharing', __name__)

# Setup logging
logger = logging.getLogger(__name__)

# Valid roles constant
VALID_ROLES = ['viewer', 'editor', 'admin']

# ======================================================================
# HELPERS
# ======================================================================

def require_auth(f):
    """
    Decorator to require authentication
    
    Extracts user_id from g.user_id or request JSON and validates.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user_id from request (JWT or session)
        user_id = g.get('user_id') or request.json.get('_user_id') if request.json else None
        
        if not user_id:
            logger.warning(f"Unauthorized access attempt to {request.endpoint}")
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        g.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function


def validate_role(role):
    """
    Validate role parameter
    
    Args:
        role: Role string to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not role:
        return False, 'Role is required'
    
    if role not in VALID_ROLES:
        return False, f'Invalid role. Must be one of: {", ".join(VALID_ROLES)}'
    
    return True, None


def success_response(data, status_code=200):
    """
    Create standardized success response
    
    Args:
        data: Response data dict
        status_code: HTTP status code
    
    Returns:
        tuple: (response, status_code)
    """
    data['success'] = True
    return jsonify(data), status_code


def error_response(error_message, status_code=500):
    """
    Create standardized error response
    
    Args:
        error_message: Error message string
        status_code: HTTP status code
    
    Returns:
        tuple: (response, status_code)
    """
    logger.error(f"Error response: {error_message} (status: {status_code})")
    return jsonify({
        'success': False,
        'error': error_message
    }), status_code


# ======================================================================
# ENDPOINTS
# ======================================================================

@thread_sharing_bp.route('/api/threads/<thread_slug>/share', methods=['POST'])
@require_auth
def share_thread(thread_slug):
    """
    Share thread with another user
    
    POST /api/threads/<thread_slug>/share
    
    Body:
    {
        "shared_with_user_id": 5,
        "role": "viewer"  // viewer, editor, admin
    }
    
    Response:
    {
        "success": true,
        "share_id": 1,
        "thread_slug": "proj-alpha",
        "shared_with_user_id": 5,
        "role": "viewer",
        "action": "added"
    }
    """
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'shared_with_user_id' not in data:
            return error_response('shared_with_user_id required', 400)
        
        shared_with_user_id = data['shared_with_user_id']
        role = data.get('role', 'viewer')
        
        # Validate role
        is_valid, error_msg = validate_role(role)
        if not is_valid:
            return error_response(error_msg, 400)
        
        # Validate user IDs
        if not isinstance(shared_with_user_id, int) or shared_with_user_id < 1:
            return error_response('Invalid shared_with_user_id', 400)
        
        if shared_with_user_id == g.user_id:
            return error_response('Cannot share thread with yourself', 400)
        
        logger.info(f"User {g.user_id} sharing thread '{thread_slug}' with user {shared_with_user_id} (role: {role})")
        
        # Call ThreadSharingManager (handles all database operations internally)
        manager = ThreadSharingManager()
        result = manager.share_thread(
            thread_slug=thread_slug,
            shared_by_user_id=g.user_id,
            shared_with_user_id=shared_with_user_id,
            role=role
        )
        
        logger.info(f"Thread '{thread_slug}' shared successfully with user {shared_with_user_id}")
        return success_response(result, 200)
    
    except ThreadNotFoundError as e:
        return error_response(str(e), 404)
    
    except PermissionDeniedError as e:
        return error_response(str(e), 403)
    
    except ThreadSharingError as e:
        return error_response(str(e), 500)
    
    except Exception as e:
        logger.exception(f"Unexpected error in share_thread: {e}")
        return error_response(f'Internal server error: {str(e)}', 500)


@thread_sharing_bp.route('/api/threads/<thread_slug>/share-email', methods=['POST'])
@require_auth
def share_thread_by_email(thread_slug):
    """
    Share thread via email invitation
    
    POST /api/threads/<thread_slug>/share-email
    
    Body:
    {
        "email": "user@example.com",
        "role": "viewer"
    }
    
    Response:
    {
        "success": true,
        "share_id": 1,
        "thread_slug": "proj-alpha",
        "invited_email": "user@example.com",
        "role": "viewer",
        "share_token": "abc123...",
        "expires_at": "2025-01-15T10:30:00",
        "share_link": "/accept-thread-share/abc123..."
    }
    """
    try:
        data = request.get_json()
        
        # Validate request data
        if not data or 'email' not in data:
            return error_response('email required', 400)
        
        email = data['email']
        role = data.get('role', 'viewer')
        
        # Validate email format (basic validation)
        if not email or '@' not in email or '.' not in email:
            return error_response('Invalid email format', 400)
        
        # Validate role
        is_valid, error_msg = validate_role(role)
        if not is_valid:
            return error_response(error_msg, 400)
        
        logger.info(f"User {g.user_id} sharing thread '{thread_slug}' with email {email} (role: {role})")
        
        # Call ThreadSharingManager (handles all database operations internally)
        manager = ThreadSharingManager()
        result = manager.share_thread_by_email(
            thread_slug=thread_slug,
            shared_by_user_id=g.user_id,
            email=email,
            role=role
        )
        
        logger.info(f"Thread '{thread_slug}' invitation sent to {email}")
        return success_response(result, 200)
    
    except ThreadNotFoundError as e:
        return error_response(str(e), 404)
    
    except PermissionDeniedError as e:
        return error_response(str(e), 403)
    
    except ThreadSharingError as e:
        return error_response(str(e), 500)
    
    except Exception as e:
        logger.exception(f"Unexpected error in share_thread_by_email: {e}")
        return error_response(f'Internal server error: {str(e)}', 500)


@thread_sharing_bp.route('/api/thread-shares/accept/<token>', methods=['POST'])
@require_auth
def accept_thread_share(token):
    """
    Accept a thread share invitation
    
    POST /api/thread-shares/accept/<token>
    
    Response:
    {
        "success": true,
        "thread_user_id": 1,
        "thread_id": 5,
        "thread_slug": "proj-alpha",
        "thread_title": "Project Alpha",
        "role": "viewer",
        "access_level": "read"
    }
    """
    try:
        # Validate token
        if not token or len(token) < 10:
            return error_response('Invalid share token', 400)
        
        logger.info(f"User {g.user_id} accepting thread share (token: {token[:10]}...)")
        
        # Call ThreadSharingManager (handles all database operations internally)
        manager = ThreadSharingManager()
        result = manager.accept_thread_share(
            share_token=token,
            user_id=g.user_id
        )
        
        logger.info(f"User {g.user_id} accepted thread share for thread '{result.get('thread_slug')}'")
        return success_response(result, 200)
    
    except ShareNotFoundError as e:
        return error_response(str(e), 404)
    
    except ThreadSharingError as e:
        return error_response(str(e), 500)
    
    except Exception as e:
        logger.exception(f"Unexpected error in accept_thread_share: {e}")
        return error_response(f'Internal server error: {str(e)}', 500)


@thread_sharing_bp.route('/api/threads/<thread_slug>/share/<int:user_id>', methods=['DELETE'])
@require_auth
def revoke_thread_share(thread_slug, user_id):
    """
    Revoke user's access to thread
    
    DELETE /api/threads/<thread_slug>/share/<user_id>
    
    Body (optional):
    {
        "reason": "Access no longer needed"
    }
    
    Response:
    {
        "success": true,
        "thread_slug": "proj-alpha",
        "revoked_user_id": 5,
        "revoked_by": 1,
        "revoked_at": "2025-01-08T10:30:00"
    }
    """
    try:
        data = request.get_json() or {}
        reason = data.get('reason')
        
        # Validate user_id
        if user_id < 1:
            return error_response('Invalid user_id', 400)
        
        if user_id == g.user_id:
            return error_response('Cannot revoke your own access. Use leave endpoint instead.', 400)
        
        logger.info(f"User {g.user_id} revoking access to thread '{thread_slug}' for user {user_id}")
        
        # Call ThreadSharingManager (handles all database operations internally)
        manager = ThreadSharingManager()
        result = manager.revoke_thread_share(
            thread_slug=thread_slug,
            user_id_to_revoke=user_id,
            revoked_by_user_id=g.user_id,
            reason=reason
        )
        
        logger.info(f"Access revoked for user {user_id} on thread '{thread_slug}'")
        return success_response(result, 200)
    
    except ThreadNotFoundError as e:
        return error_response(str(e), 404)
    
    except PermissionDeniedError as e:
        return error_response(str(e), 403)
    
    except ShareNotFoundError as e:
        return error_response(str(e), 404)
    
    except ThreadSharingError as e:
        return error_response(str(e), 500)
    
    except Exception as e:
        logger.exception(f"Unexpected error in revoke_thread_share: {e}")
        return error_response(f'Internal server error: {str(e)}', 500)


@thread_sharing_bp.route('/api/threads/<thread_slug>/collaborators', methods=['GET'])
@require_auth
def list_thread_collaborators(thread_slug):
    """
    List all users with access to thread
    
    GET /api/threads/<thread_slug>/collaborators
    
    Response:
    {
        "success": true,
        "thread_slug": "proj-alpha",
        "collaborators": [
            {
                "id": 1,
                "user_id": 5,
                "username": "john",
                "email": "john@example.com",
                "role": "viewer",
                "access_level": "read",
                "added_at": "2025-01-08T10:30:00"
            }
        ]
    }
    """
    try:
        logger.info(f"User {g.user_id} listing collaborators for thread '{thread_slug}'")
        
        # Call ThreadSharingManager (handles all database operations internally)
        manager = ThreadSharingManager()
        
        # Check if user has access to view collaborators
        access = manager.get_thread_access_level(thread_slug, g.user_id)
        
        if not access or not access.get('has_access'):
            logger.warning(f"User {g.user_id} attempted to view collaborators without access to thread '{thread_slug}'")
            return error_response('You do not have access to this thread', 403)
        
        collaborators = manager.list_thread_collaborators(thread_slug)
        
        logger.info(f"Retrieved {len(collaborators)} collaborators for thread '{thread_slug}'")
        return success_response({
            'thread_slug': thread_slug,
            'collaborators': collaborators
        }, 200)
    
    except ThreadNotFoundError as e:
        return error_response(str(e), 404)
    
    except ThreadSharingError as e:
        return error_response(str(e), 500)
    
    except Exception as e:
        logger.exception(f"Unexpected error in list_thread_collaborators: {e}")
        return error_response(f'Internal server error: {str(e)}', 500)


@thread_sharing_bp.route('/api/my-shared-threads', methods=['GET'])
@require_auth
def list_my_shared_threads():
    """
    List threads shared with current user
    
    GET /api/my-shared-threads
    
    Response:
    {
        "success": true,
        "shared_threads": [
            {
                "thread_id": 5,
                "thread_slug": "proj-alpha",
                "title": "Project Alpha",
                "owner_id": 1,
                "owner_username": "alice",
                "my_role": "viewer",
                "my_access_level": "read",
                "shared_at": "2025-01-08T10:30:00",
                "updated_at": "2025-01-08T12:00:00"
            }
        ]
    }
    """
    try:
        logger.info(f"User {g.user_id} retrieving list of shared threads")
        
        # Call ThreadSharingManager (handles all database operations internally)
        manager = ThreadSharingManager()
        shared_threads = manager.list_my_shared_threads(g.user_id)
        
        logger.info(f"Retrieved {len(shared_threads)} shared threads for user {g.user_id}")
        return success_response({
            'shared_threads': shared_threads
        }, 200)
    
    except ThreadSharingError as e:
        return error_response(str(e), 500)
    
    except Exception as e:
        logger.exception(f"Unexpected error in list_my_shared_threads: {e}")
        return error_response(f'Internal server error: {str(e)}', 500)


# ======================================================================
# STARTUP LOGGING
# ======================================================================
logger.info("✅ Thread Sharing routes loaded")