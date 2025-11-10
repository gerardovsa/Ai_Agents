"""
Thread Sharing Routes

REST API endpoints for thread sharing functionality.

Endpoints:
- POST /api/threads/<thread_slug>/share - Share thread with user
- POST /api/threads/<thread_slug>/share-email - Share via email
- POST /api/thread-shares/accept/<token> - Accept invitation
- DELETE /api/threads/<thread_slug>/share/<user_id> - Revoke access
- GET /api/threads/<thread_slug>/collaborators - List collaborators
- GET /api/my-shared-threads - List threads shared with me
"""

from flask import Blueprint, request, jsonify, g
from functools import wraps
import sys
from pathlib import Path

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

# Create blueprint
thread_sharing_bp = Blueprint('thread_sharing', __name__)


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get user_id from request (JWT or session)
        user_id = g.get('user_id') or request.json.get('_user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        g.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated_function


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
        
        if not data or 'shared_with_user_id' not in data:
            return jsonify({
                'success': False,
                'error': 'shared_with_user_id required'
            }), 400
        
        shared_with_user_id = data['shared_with_user_id']
        role = data.get('role', 'viewer')
        
        if role not in ['viewer', 'editor', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Invalid role. Must be: viewer, editor, or admin'
            }), 400
        
        manager = ThreadSharingManager()
        result = manager.share_thread(
            thread_slug=thread_slug,
            shared_by_user_id=g.user_id,
            shared_with_user_id=shared_with_user_id,
            role=role
        )
        
        return jsonify(result), 200
    
    except ThreadNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except PermissionDeniedError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403
    
    except ThreadSharingError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


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
        
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'error': 'email required'
            }), 400
        
        email = data['email']
        role = data.get('role', 'viewer')
        
        if role not in ['viewer', 'editor', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Invalid role. Must be: viewer, editor, or admin'
            }), 400
        
        manager = ThreadSharingManager()
        result = manager.share_thread_by_email(
            thread_slug=thread_slug,
            shared_by_user_id=g.user_id,
            email=email,
            role=role
        )
        
        return jsonify(result), 200
    
    except ThreadNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except PermissionDeniedError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403
    
    except ThreadSharingError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


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
        manager = ThreadSharingManager()
        result = manager.accept_thread_share(
            share_token=token,
            user_id=g.user_id
        )
        
        return jsonify(result), 200
    
    except ShareNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except ThreadSharingError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


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
        
        manager = ThreadSharingManager()
        result = manager.revoke_thread_share(
            thread_slug=thread_slug,
            user_id_to_revoke=user_id,
            revoked_by_user_id=g.user_id,
            reason=reason
        )
        
        return jsonify(result), 200
    
    except ThreadNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except PermissionDeniedError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403
    
    except ShareNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except ThreadSharingError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


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
        manager = ThreadSharingManager()
        
        # Check if user has access to view collaborators
        access = manager.get_thread_access_level(thread_slug, g.user_id)
        
        if not access or not access['has_access']:
            return jsonify({
                'success': False,
                'error': 'You do not have access to this thread'
            }), 403
        
        collaborators = manager.list_thread_collaborators(thread_slug)
        
        return jsonify({
            'success': True,
            'thread_slug': thread_slug,
            'collaborators': collaborators
        }), 200
    
    except ThreadNotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    
    except ThreadSharingError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500


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
        manager = ThreadSharingManager()
        shared_threads = manager.list_my_shared_threads(g.user_id)
        
        return jsonify({
            'success': True,
            'shared_threads': shared_threads
        }), 200
    
    except ThreadSharingError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500
