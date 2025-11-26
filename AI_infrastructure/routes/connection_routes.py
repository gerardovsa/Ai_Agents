"""
Platform Connections Routes
===========================

API endpoints for managing user platform credentials/connections.
Displays connected platforms in the Account Settings Connections section.

Database: ai_infrastructure.user_platform_credentials
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
    user_id = request.user_id
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query user's platform credentials
        cursor.execute("""
            SELECT 
                id,
                platform,
                credential_type,
                is_active,
                created_at,
                updated_at,
                metadata
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        connections = []
        for row in rows:
            connection = {
                'id': row[0],
                'platform': row[1],
                'credential_type': row[2],
                'is_active': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'updated_at': row[5].isoformat() if row[5] else None,
                'metadata': row[6] if row[6] else {}
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
    user_id = request.user_id
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Set is_active = False instead of deleting
        cursor.execute("""
            UPDATE ai_infrastructure.user_platform_credentials
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
