"""
Session Management Routes

Endpoints:
- GET /api/auth/sessions - List all active sessions for authenticated user
- DELETE /api/auth/sessions/<session_id> - Revoke a specific session
- DELETE /api/auth/sessions/all - Revoke all sessions except current
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import UserAuthManager
from shared.database_utils import get_database_connection
import jwt
from datetime import datetime

session_management_bp = Blueprint('session_management', __name__)
auth_manager = UserAuthManager()

def get_current_user():
    """Extract user_id from JWT token in Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.replace('Bearer ', '')
    
    try:
        payload = jwt.decode(token, auth_manager.jwt_secret, algorithms=['HS256'])
        return payload.get('user_id'), token
    except jwt.InvalidTokenError:
        return None

@session_management_bp.route('/api/auth/sessions', methods=['GET'])
def list_user_sessions():
    """
    List all active sessions for the authenticated user
    
    Returns:
        {
            "success": true,
            "sessions": [
                {
                    "id": 123,
                    "device_info": {...},
                    "created_at": "2025-11-26T10:30:00",
                    "last_activity": "2025-11-26T15:45:00",
                    "expires_at": "2025-11-27T10:30:00",
                    "is_current": true
                }
            ],
            "total": 3
        }
    """
    try:
        result = get_current_user()
        if not result:
            return jsonify({
                'success': False,
                'error': 'Unauthorized - Invalid or missing token'
            }), 401
        
        user_id, current_token = result
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Get all active sessions for this user
        cursor.execute("""
            SELECT 
                id,
                token,
                device_info,
                TO_CHAR(created_at, 'YYYY-MM-DD"T"HH24:MI:SS') as created_at,
                TO_CHAR(created_at, 'YYYY-MM-DD"T"HH24:MI:SS') as last_activity,
                TO_CHAR(expires_at, 'YYYY-MM-DD"T"HH24:MI:SS') as expires_at,
                ip_address,
                user_agent
            FROM ai_infrastructure.user_sessions
            WHERE user_id = %s 
            AND expires_at > NOW()
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        sessions = []
        for row in rows:
            session_id, token, device_info, created_at, last_activity, expires_at, ip_address, user_agent = row
            
            # Mark current session
            is_current = (token == current_token)
            
            # Parse device_info if it's a JSON string
            if isinstance(device_info, str):
                try:
                    import json
                    device_info = json.loads(device_info)
                except:
                    device_info = {}
            
            sessions.append({
                'id': session_id,
                'device_info': device_info or {},
                'created_at': created_at,
                'last_activity': last_activity,
                'expires_at': expires_at,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'is_current': is_current
            })
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total': len(sessions)
        })
        
    except Exception as e:
        print(f"❌ [SESSION MGMT] Error listing sessions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to list sessions: {str(e)}'
        }), 500

@session_management_bp.route('/api/auth/sessions/<int:session_id>', methods=['DELETE'])
def revoke_session(session_id):
    """
    Revoke a specific session by ID
    
    Args:
        session_id: Session ID to revoke
    
    Returns:
        {"success": true, "message": "Session revoked successfully"}
    """
    try:
        result = get_current_user()
        if not result:
            return jsonify({
                'success': False,
                'error': 'Unauthorized - Invalid or missing token'
            }), 401
        
        user_id, current_token = result
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check if session belongs to this user
        cursor.execute("""
            SELECT token FROM ai_infrastructure.user_sessions
            WHERE id = %s AND user_id = %s
        """, (session_id, user_id))
        
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Session not found or does not belong to you'
            }), 404
        
        session_token = row[0]
        
        # Prevent revoking current session
        if session_token == current_token:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Cannot revoke your current session. Use logout instead.'
            }), 400
        
        # Delete the session
        cursor.execute("""
            DELETE FROM ai_infrastructure.user_sessions
            WHERE id = %s AND user_id = %s
        """, (session_id, user_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ [SESSION MGMT] User {user_id} revoked session {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Session revoked successfully'
        })
        
    except Exception as e:
        print(f"❌ [SESSION MGMT] Error revoking session: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to revoke session: {str(e)}'
        }), 500

@session_management_bp.route('/api/auth/sessions/all', methods=['DELETE'])
def revoke_all_sessions():
    """
    Revoke all sessions except the current one
    
    Returns:
        {"success": true, "revoked_count": 2}
    """
    try:
        result = get_current_user()
        if not result:
            return jsonify({
                'success': False,
                'error': 'Unauthorized - Invalid or missing token'
            }), 401
        
        user_id, current_token = result
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Delete all sessions except current one
        cursor.execute("""
            DELETE FROM ai_infrastructure.user_sessions
            WHERE user_id = %s AND token != %s
            RETURNING id
        """, (user_id, current_token))
        
        revoked_ids = cursor.fetchall()
        revoked_count = len(revoked_ids)
        
        conn.commit()
        conn.close()
        
        print(f"✅ [SESSION MGMT] User {user_id} revoked {revoked_count} sessions")
        
        return jsonify({
            'success': True,
            'revoked_count': revoked_count,
            'message': f'Successfully revoked {revoked_count} session(s)'
        })
        
    except Exception as e:
        print(f"❌ [SESSION MGMT] Error revoking all sessions: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to revoke sessions: {str(e)}'
        }), 500
