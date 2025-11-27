"""
Platform Connections Routes
===========================

API endpoints for managing user platform credentials/connections.
Displays connected platforms in the Account Settings Connections section.

Database: ai_infrastructure.oauth_tokens
"""

from flask import Blueprint, jsonify, request
from AI_infrastructure.auth.user_auth import require_auth
from shared.database_utils import get_database_connection
import json

connections_bp = Blueprint('connections', __name__)


@connections_bp.route('/api/connections', methods=['GET'])
@require_auth
def list_user_connections():
    """
    GET /api/connections
    List all platform connections for the authenticated user
    
    Returns:
        {
            "connections": [
                {
                    "id": int,
                    "platform": str,
                    "credential_type": str,
                    "is_active": bool,
                    "created_at": str,
                    "metadata": dict
                }
            ],
            "total_count": int
        }
    """
    # Extract user_id from request.user dict set by @require_auth
    user_id = request.user.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 401
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query OAuth tokens (actual platform connections)
        cursor.execute("""
            SELECT 
                id,
                platform,
                email,
                is_active,
                is_valid,
                created_at,
                updated_at,
                expires_at,
                last_refreshed_at,
                scope
            FROM ai_infrastructure.oauth_tokens
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        connections = []
        for row in rows:
            # Handle both dict and tuple responses
            if isinstance(row, dict):
                row_data = row
            else:
                row_data = {
                    'id': row[0],
                    'platform': row[1],
                    'email': row[2],
                    'is_active': row[3],
                    'is_valid': row[4],
                    'created_at': row[5],
                    'updated_at': row[6],
                    'expires_at': row[7],
                    'last_refreshed_at': row[8],
                    'scope': row[9]
                }
            
            connection = {
                'id': row_data['id'],
                'platform': row_data['platform'],
                'credential_type': 'oauth',
                'is_active': row_data['is_active'] and row_data['is_valid'],
                'created_at': row_data['created_at'].isoformat() if row_data['created_at'] else None,
                'updated_at': row_data['updated_at'].isoformat() if row_data['updated_at'] else None,
                'scope': row_data['scope'],  # Include scope at top level for easy access
                'metadata': {
                    'email': row_data['email'],
                    'expires_at': row_data['expires_at'].isoformat() if row_data['expires_at'] else None,
                    'last_refreshed_at': row_data['last_refreshed_at'].isoformat() if row_data['last_refreshed_at'] else None,
                    'scope': row_data['scope']
                }
            }
            connections.append(connection)
        
        return jsonify({
            'success': True,
            'connections': connections,
            'total_count': len(connections)
        }), 200
        
    except Exception as e:
        print(f"Error loading connections for user {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@connections_bp.route('/api/connections/<platform>', methods=['DELETE'])
@require_auth
def disconnect_platform(platform):
    """
    DELETE /api/connections/<platform>
    Disconnect a platform by setting is_active = False
    
    Args:
        platform: Platform name (e.g., 'google_workspace', 'microsoft_365')
    
    Returns:
        {"success": bool, "message": str}
    """
    # Extract user_id from request.user dict set by @require_auth
    user_id = request.user.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 401
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Set is_active = False in oauth_tokens instead of deleting
        cursor.execute("""
            UPDATE ai_infrastructure.oauth_tokens
            SET is_active = FALSE,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s AND platform = %s
        """, (user_id, platform))
        
        affected_rows = cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        
        if affected_rows == 0:
            return jsonify({
                'success': False,
                'error': f'Platform {platform} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f'Disconnected from {platform}'
        }), 200
        
    except Exception as e:
        print(f"Error disconnecting platform {platform} for user {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
