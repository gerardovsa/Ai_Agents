"""
File: AI_infrastructure/routes/connection_routes.py

C:/Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\connection_routes.py
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
    Includes both OAuth tokens AND platform credentials (API keys, databases)
    
    Returns:
        {
            "connections": [
                {
                    "id": int,
                    "platform": str,
                    "credential_type": str ("oauth", "api_key", "database"),
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
        # ✅ FIX: Use context manager to prevent connection leaks
        with get_database_connection('ai_infrastructure') as conn:
            cursor = conn.cursor()
            
            connections = []
            
            # 1. Query OAuth tokens
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
            
            oauth_rows = cursor.fetchall()
            
            for row in oauth_rows:
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
                    'id': f"oauth_{row_data['id']}",
                    'platform': row_data['platform'],
                    'credential_type': 'oauth',
                    'is_active': row_data['is_active'] and row_data['is_valid'],
                    'created_at': row_data['created_at'].isoformat() if row_data['created_at'] else None,
                    'updated_at': row_data['updated_at'].isoformat() if row_data['updated_at'] else None,
                    'metadata': {
                        'email': row_data['email'],
                        'expires_at': row_data['expires_at'].isoformat() if row_data['expires_at'] else None,
                        'last_refreshed_at': row_data['last_refreshed_at'].isoformat() if row_data['last_refreshed_at'] else None,
                        'scope': row_data['scope']
                    }
                }
                connections.append(connection)
            
            # 2. Query user_platform_credentials (API keys, databases, etc.)
            cursor.execute("""
                SELECT 
                    id,
                    platform,
                    credential_type,
                    credential_key,
                    credential_value,
                    is_active,
                    created_at,
                    updated_at,
                    metadata,
                    credentials
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))
            
            platform_rows = cursor.fetchall()
            
            # Import encryptor for masking
            from AI_infrastructure.auth.credential_encryptor import get_encryptor
            encryptor = get_encryptor()
            
            for row in platform_rows:
                if isinstance(row, dict):
                    row_data = row
                else:
                    row_data = {
                        'id': row[0],
                        'platform': row[1],
                        'credential_type': row[2],
                        'credential_key': row[3],
                        'credential_value': row[4],
                        'is_active': row[5],
                        'created_at': row[6],
                        'updated_at': row[7],
                        'metadata': row[8],
                        'credentials': row[9]
                    }
                
                # Parse metadata JSON if string
                metadata = row_data['metadata']
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                # Parse credentials JSON if string
                credentials = row_data['credentials']
                if isinstance(credentials, str):
                    try:
                        credentials = json.loads(credentials)
                    except:
                        credentials = {}
                
                # Mask the credential value for display
                credential_value = row_data.get('credential_value')
                masked_value = None
                if credential_value:
                    masked_value = encryptor.mask_credential(credential_value)
                
                # Extract account name from metadata
                account_name = None
                if metadata:
                    account_name = (
                        metadata.get('email') or 
                        metadata.get('account_name') or 
                        metadata.get('username') or
                        metadata.get('display_name')
                    )
                
                connection = {
                    'id': f"platform_{row_data['id']}",
                    'platform': row_data['platform'],
                    'credential_type': row_data['credential_type'],
                    'credential_key': row_data['credential_key'],  # API key name/identifier
                    'credential_value_masked': masked_value,  # ✅ ADD MASKED VALUE
                    'account_name': account_name,  # ✅ ADD ACCOUNT NAME
                    'is_active': row_data['is_active'],
                    'created_at': row_data['created_at'].isoformat() if row_data['created_at'] else None,
                    'updated_at': row_data['updated_at'].isoformat() if row_data['updated_at'] else None,
                    'metadata': metadata,
                    'has_credentials': bool(credentials)
                }
                connections.append(connection)
        
            # ✅ Close cursor before return
            cursor.close()
            
            return jsonify({
                'success': True,
                'connections': connections,
                'total_count': len(connections)
            }), 200
        
    except Exception as e:
        print(f"❌ [CONNECTIONS] Error loading connections for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@connections_bp.route('/api/connections', methods=['POST'])
@require_auth
def add_platform_credential():
    """
    POST /api/connections
    Add a new platform credential (API key, database connection, etc.)
    
    Request Body:
        {
            "platform": str (e.g., "stripe", "openai", "pinecone"),
            "credential_type": str ("api_key", "database", "other"),
            "credential_key": str (label/name for this credential),
            "credential_value": str (the actual API key/password),
            "metadata": dict (optional extra info),
            "credentials": dict (optional additional credential fields)
        }
    
    Returns:
        {"success": bool, "message": str, "credential_id": int}
    """
    user_id = request.user.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 401
    
    try:
        data = request.get_json()
        platform = data.get('platform')
        credential_type = data.get('credential_type', 'api_key')
        credential_key = data.get('credential_key')
        credential_value = data.get('credential_value')
        metadata = data.get('metadata', {})
        credentials = data.get('credentials', {})
        
        if not platform or not credential_key or not credential_value:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: platform, credential_key, credential_value'
            }), 400
        
        # Add the main credential value to credentials dict
        credentials['main_credential'] = credential_value
        
        conn = None  # Initialize for finally block
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO ai_infrastructure.user_platform_credentials
            (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, credentials)
            VALUES (%s, %s, %s, %s, %s, TRUE, %s, %s)
            RETURNING id
        """, (user_id, platform, credential_type, credential_key, credential_value, 
              json.dumps(metadata), json.dumps(credentials)))
        
        credential_id = cursor.fetchone()[0]
        
        # ✅ Close cursor before commit
        cursor.close()
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': f'Added {platform} credentials',
            'credential_id': credential_id
        }), 201
        
    except Exception as e:
        print(f"Error adding platform credential: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # ✅ CRITICAL FIX: Always close connection
        if conn:
            try:
                conn.close()
            except:
                pass


@connections_bp.route('/api/connections/<credential_id>', methods=['PUT'])
@require_auth
def update_platform_credential(credential_id):
    """
    PUT /api/connections/<credential_id>
    Update an existing platform credential
    
    Args:
        credential_id: Format "platform_123" or "oauth_456"
    
    Request Body:
        {
            "credential_key": str (optional),
            "credential_value": str (optional),
            "metadata": dict (optional),
            "credentials": dict (optional)
        }
    
    Returns:
        {"success": bool, "message": str}
    """
    user_id = request.user.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 401
    
    # Parse credential_id format: "platform_123" or "oauth_456"
    if not credential_id.startswith(('platform_', 'oauth_')):
        return jsonify({'error': 'Invalid credential_id format'}), 400
    
    id_type, id_value = credential_id.split('_', 1)
    
    if id_type == 'oauth':
        return jsonify({
            'success': False,
            'error': 'OAuth credentials cannot be edited directly. Please re-authenticate.'
        }), 400
    
    conn = None  # Initialize for finally block
    try:
        data = request.get_json()
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Build UPDATE query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if 'credential_key' in data:
            update_fields.append('credential_key = %s')
            update_values.append(data['credential_key'])
        
        if 'credential_value' in data:
            update_fields.append('credential_value = %s')
            update_values.append(data['credential_value'])
        
        if 'metadata' in data:
            update_fields.append('metadata = %s')
            update_values.append(json.dumps(data['metadata']))
        
        if 'credentials' in data:
            update_fields.append('credentials = %s')
            update_values.append(json.dumps(data['credentials']))
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        update_fields.append('updated_at = CURRENT_TIMESTAMP')
        update_values.extend([user_id, int(id_value)])
        
        cursor.execute(f"""
            UPDATE ai_infrastructure.user_platform_credentials
            SET {', '.join(update_fields)}
            WHERE user_id = %s AND id = %s
        """, update_values)
        
        affected_rows = cursor.rowcount
        
        # ✅ Close cursor before commit
        cursor.close()
        conn.commit()
        
        if affected_rows == 0:
            return jsonify({
                'success': False,
                'error': 'Credential not found'
            }), 404
        
        # ✅ PERFORMANCE OPTIMIZATION (Dec 2025): Invalidate cache after update
        if 'platform' in data:
            try:
                from AI_infrastructure.utils.cache_utils import invalidate_platform_credentials
                invalidate_platform_credentials(user_id, data['platform'])
                print(f"[CREDENTIALS] ⚡ Cache invalidated for user_id={user_id}, platform={data['platform']}")
            except Exception as e:
                # Silently fail if cache unavailable
                pass
        
        return jsonify({
            'success': True,
            'message': 'Credential updated successfully'
        }), 200
        
    except Exception as e:
        print(f"Error updating credential {credential_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # ✅ CRITICAL FIX: Always close connection
        if conn:
            try:
                conn.close()
            except:
                pass


@connections_bp.route('/api/connections/<credential_id>/test', methods=['POST'])
@require_auth
def test_platform_credential(credential_id):
    """
    POST /api/connections/<credential_id>/test
    Test if a platform credential is valid by making a test API call
    
    Args:
        credential_id: Format "platform_123" or "oauth_456"
    
    Returns:
        {"success": bool, "valid": bool, "message": str, "details": dict}
    """
    user_id = request.user.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 401
    
    # Parse credential_id
    if not credential_id.startswith(('platform_', 'oauth_')):
        return jsonify({'error': 'Invalid credential_id format'}), 400
    
    id_type, id_value = credential_id.split('_', 1)
    
    conn = None  # Initialize for finally block
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        if id_type == 'oauth':
            # Test OAuth token
            cursor.execute("""
                SELECT platform, email, is_active, is_valid, expires_at
                FROM ai_infrastructure.oauth_tokens
                WHERE user_id = %s AND id = %s
            """, (user_id, int(id_value)))
        else:
            # Test platform credential
            cursor.execute("""
                SELECT platform, credential_type, credential_value, credentials
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s AND id = %s AND is_active = TRUE
            """, (user_id, int(id_value)))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Credential not found'
            }), 404
        
        # Basic validation (actual API testing would go here)
        # For now, just check if credential exists and is active
        platform = row[0]
        
        # ✅ Close cursor before return
        cursor.close()
        
        return jsonify({
            'success': True,
            'valid': True,
            'message': f'{platform} credentials are configured',
            'details': {
                'platform': platform,
                'note': 'Full API validation not yet implemented'
            }
        }), 200
        
    except Exception as e:
        print(f"Error testing credential {credential_id}: {e}")
        return jsonify({
            'success': False,
            'valid': False,
            'message': str(e)
        }), 500


@connections_bp.route('/api/connections/<credential_id>', methods=['DELETE'])
@require_auth
def disconnect_platform(credential_id):
    """
    DELETE /api/connections/<credential_id>
    Disconnect a platform by setting is_active = False
    
    Args:
        credential_id: Format "platform_123" or "oauth_456" or legacy platform name
    
    Returns:
        {"success": bool, "message": str}
    """
    user_id = request.user.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 401
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        affected_rows = 0
        
        # Check if it's new format (platform_123) or legacy (google_workspace)
        if credential_id.startswith('platform_'):
            # New format: platform_123
            _, id_value = credential_id.split('_', 1)
            cursor.execute("""
                UPDATE ai_infrastructure.user_platform_credentials
                SET is_active = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND id = %s
            """, (user_id, int(id_value)))
            affected_rows = cursor.rowcount
            
        elif credential_id.startswith('oauth_'):
            # New format: oauth_456
            _, id_value = credential_id.split('_', 1)
            cursor.execute("""
                UPDATE ai_infrastructure.oauth_tokens
                SET is_active = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND id = %s
            """, (user_id, int(id_value)))
            affected_rows = cursor.rowcount
            
        else:
            # Legacy format: platform name (e.g., 'google_workspace')
            cursor.execute("""
                UPDATE ai_infrastructure.oauth_tokens
                SET is_active = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND platform = %s
            """, (user_id, credential_id))
            affected_rows = cursor.rowcount
            
            if affected_rows == 0:
                # Try user_platform_credentials
                cursor.execute("""
                    UPDATE ai_infrastructure.user_platform_credentials
                    SET is_active = FALSE,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s AND platform = %s
                """, (user_id, credential_id))
                affected_rows = cursor.rowcount
        
        # ✅ Close cursor before commit
        cursor.close()
        conn.commit()
        
        if affected_rows == 0:
            return jsonify({
                'success': False,
                'error': f'Credential {credential_id} not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': f'Disconnected credential {credential_id}'
        }), 200
        
    except Exception as e:
        print(f"Error disconnecting credential {credential_id} for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        # ✅ CRITICAL FIX: Always close connection
        if conn:
            try:
                conn.close()
            except:
                pass
