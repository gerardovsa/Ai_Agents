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
            
            # Fetch user's organisation_id and org_role for Tier 2 and role gating
            cursor.execute("""
                SELECT organisation_id, org_role, is_sub_user, parent_user_id
                FROM ai_infrastructure.users
                WHERE id = %s
            """, (user_id,))
            user_meta_row = cursor.fetchone()
            if isinstance(user_meta_row, dict):
                org_id = user_meta_row.get('organisation_id')
                user_org_role = user_meta_row.get('org_role')
                is_sub_user = user_meta_row.get('is_sub_user')
                parent_user_id = user_meta_row.get('parent_user_id')
            elif user_meta_row:
                org_id = user_meta_row[0]
                user_org_role = user_meta_row[1]
                is_sub_user = user_meta_row[2]
                parent_user_id = user_meta_row[3]
            else:
                org_id = None
                user_org_role = None
                is_sub_user = False
                parent_user_id = None

            # Tier 1.5: Sub-users with no org_id inherit parent's organisation_id
            if not org_id and is_sub_user and parent_user_id:
                cursor.execute("""
                    SELECT organisation_id, org_role
                    FROM ai_infrastructure.users
                    WHERE id = %s
                """, (parent_user_id,))
                parent_row = cursor.fetchone()
                if isinstance(parent_row, dict):
                    org_id = parent_row.get('organisation_id')
                    user_org_role = parent_row.get('org_role')
                elif parent_row:
                    org_id = parent_row[0]
                    user_org_role = parent_row[1]

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
                    'is_org_level': False,
                    'created_at': row_data['created_at'].isoformat() if row_data['created_at'] else None,
                    'updated_at': row_data['updated_at'].isoformat() if row_data['updated_at'] else None,
                    'metadata': metadata,
                    'has_credentials': bool(credentials)
                }
                connections.append(connection)

            # 3. Query organisation_platform_credentials (Tier 2 - org vault)
            if org_id:
                # Track platforms already shown from personal credentials (to avoid duplicates)
                user_platforms = {c['platform'] for c in connections}

                cursor.execute("""
                    SELECT
                        id,
                        platform,
                        display_name,
                        credential_value,
                        credentials,
                        is_active,
                        created_at,
                        updated_at,
                        environment
                    FROM ai_infrastructure.organisation_platform_credentials
                    WHERE organisation_id = %s AND is_active = TRUE
                    ORDER BY created_at DESC
                """, (org_id,))

                org_rows = cursor.fetchall()

                for row in org_rows:
                    if isinstance(row, dict):
                        r = row
                    else:
                        r = {
                            'id': row[0], 'platform': row[1], 'display_name': row[2],
                            'credential_value': row[3], 'credentials': row[4],
                            'is_active': row[5], 'created_at': row[6],
                            'updated_at': row[7], 'environment': row[8]
                        }

                    # Skip platforms already covered by personal credentials
                    if r['platform'] in user_platforms:
                        continue

                    connections.append({
                        'id': f"org_{r['id']}",
                        'platform': r['platform'],
                        'credential_type': 'api_key',
                        'credential_key': r['display_name'],
                        'credential_value_masked': '••••••••',
                        'account_name': None,
                        'is_active': r['is_active'],
                        'is_org_level': True,
                        'created_at': r['created_at'].isoformat() if r['created_at'] else None,
                        'updated_at': r['updated_at'].isoformat() if r['updated_at'] else None,
                        'metadata': {'environment': r['environment']} if r.get('environment') else {},
                        'has_credentials': True
                    })
        
            # ✅ Close cursor before return
            cursor.close()
            
            return jsonify({
                'success': True,
                'connections': connections,
                'total_count': len(connections),
                'user_org_role': user_org_role
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
    Uses UPSERT to handle existing credentials for the same platform.
    
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
        {"success": bool, "message": str, "credential_id": int, "is_update": bool}
    """
    user_id = request.user.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID not found in session'}), 401
    
    conn = None  # Initialize for finally block
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

        # ── Smart Tier routing ────────────────────────────────────────────────────
        # These platforms are intrinsically org-wide (AI providers, transactional
        # email, shipping APIs, etc.).  When an admin/owner of an org submits one
        # of them via this form, route the credential to Tier 2
        # (organisation_platform_credentials) so every org member benefits.
        # All other platforms — and any org-platform submitted by a member without
        # admin/owner role — fall through to the normal Tier 1 path below.
        ORG_PLATFORMS = {
            'anthropic', 'openai', 'deepseek', 'assemblyai',
            'pinecone', 'auspost', 'stripe', 'sendgrid', 'twilio',
        }

        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()

        if platform in ORG_PLATFORMS:
            cursor.execute("""
                SELECT organisation_id, org_role
                FROM ai_infrastructure.users
                WHERE id = %s
            """, (user_id,))
            user_row = cursor.fetchone()
            if isinstance(user_row, dict):
                org_id = user_row.get('organisation_id')
                org_role = user_row.get('org_role')
            elif user_row:
                org_id, org_role = user_row[0], user_row[1]
            else:
                org_id, org_role = None, None

            if org_id and org_role in ('admin', 'owner'):
                # Check for an existing active credential for this org + platform
                cursor.execute("""
                    SELECT id
                    FROM ai_infrastructure.organisation_platform_credentials
                    WHERE organisation_id = %s AND platform = %s AND is_active = TRUE
                    LIMIT 1
                """, (org_id, platform))
                existing = cursor.fetchone()
                existing_id = (
                    existing.get('id') if isinstance(existing, dict) else existing[0]
                ) if existing else None

                if existing_id:
                    cursor.execute("""
                        UPDATE ai_infrastructure.organisation_platform_credentials
                        SET display_name = %s,
                            credential_value = %s,
                            credentials = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (credential_key, credential_value, json.dumps(credentials), existing_id))
                    result_id = existing_id
                    is_insert = False
                else:
                    cursor.execute("""
                        INSERT INTO ai_infrastructure.organisation_platform_credentials
                            (organisation_id, platform, display_name, credential_value,
                             credentials, is_active, created_by_user_id)
                        VALUES (%s, %s, %s, %s, %s, TRUE, %s)
                        RETURNING id
                    """, (org_id, platform, credential_key, credential_value,
                          json.dumps(credentials), user_id))
                    result = cursor.fetchone()
                    result_id = (
                        result.get('id') if isinstance(result, dict) else result[0]
                    ) if result else None
                    is_insert = True

                cursor.close()
                conn.commit()
                return jsonify({
                    'success': True,
                    'message': f'{"Added" if is_insert else "Updated"} {platform} credentials (shared with org)',
                    'credential_id': f'org_{result_id}',
                    'is_update': not is_insert,
                    'tier': 2
                }), 201 if is_insert else 200

        # ── Tier 1: personal credential ───────────────────────────────────────────
        # ✅ FIX: Use UPSERT (INSERT ... ON CONFLICT) to handle existing credentials
        # Since there's a UNIQUE constraint on (user_id, platform),
        # we update if it exists, insert if it doesn't
        cursor.execute("""
            INSERT INTO ai_infrastructure.user_platform_credentials
            (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, credentials, updated_at)
            VALUES (%s, %s, %s, %s, %s, TRUE, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, platform) DO UPDATE SET
                credential_type = EXCLUDED.credential_type,
                credential_key = EXCLUDED.credential_key,
                credential_value = EXCLUDED.credential_value,
                is_active = TRUE,
                metadata = EXCLUDED.metadata,
                credentials = EXCLUDED.credentials,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, (xmax = 0) as is_insert
        """, (user_id, platform, credential_type, credential_key, credential_value,
              json.dumps(metadata), json.dumps(credentials)))

        result = cursor.fetchone()
        if result:
            credential_id = result[0]
            is_insert = result[1] if len(result) > 1 else True
        else:
            raise Exception("Failed to insert/update credential")

        # ✅ Close cursor before commit
        cursor.close()
        conn.commit()

        return jsonify({
            'success': True,
            'message': f'{"Added" if is_insert else "Updated"} {platform} credentials',
            'credential_id': credential_id,
            'is_update': not is_insert
        }), 201 if is_insert else 200
        
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        print(f"Error adding/updating platform credential for user {user_id}: {e}")
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
    
    # Parse credential_id format: "platform_123" or "oauth_456" or "org_789"
    if not credential_id.startswith(('platform_', 'oauth_', 'org_')):
        return jsonify({'error': 'Invalid credential_id format'}), 400
    
    id_type, id_value = credential_id.split('_', 1)
    
    if id_type == 'oauth':
        return jsonify({
            'success': False,
            'error': 'OAuth credentials cannot be edited directly. Please re-authenticate.'
        }), 400

    # Org-level credentials require admin or owner role
    if id_type == 'org':
        conn = None
        try:
            data = request.get_json()
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()

            # Verify user is admin/owner of the org that owns this credential
            cursor.execute("""
                SELECT u.org_role
                FROM ai_infrastructure.users u
                JOIN ai_infrastructure.organisation_platform_credentials opc
                  ON opc.organisation_id = u.organisation_id
                WHERE u.id = %s AND opc.id = %s AND opc.is_active = TRUE
            """, (user_id, int(id_value)))
            perm_row = cursor.fetchone()
            org_role = (perm_row[0] if not isinstance(perm_row, dict) else perm_row.get('org_role')) if perm_row else None

            if org_role not in ('admin', 'owner'):
                cursor.close()
                return jsonify({'success': False, 'error': 'Admin or owner role required to edit org credentials'}), 403

            update_fields = []
            update_values = []
            if 'credential_key' in data:
                update_fields.append('display_name = %s')
                update_values.append(data['credential_key'])
            if 'credential_value' in data and data['credential_value']:
                update_fields.append('credential_value = %s')
                update_values.append(data['credential_value'])
            if not update_fields:
                cursor.close()
                return jsonify({'error': 'No fields to update'}), 400

            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            update_values.append(int(id_value))

            cursor.execute(f"""
                UPDATE ai_infrastructure.organisation_platform_credentials
                SET {', '.join(update_fields)}
                WHERE id = %s AND is_active = TRUE
            """, update_values)

            cursor.close()
            conn.commit()
            return jsonify({'success': True, 'message': 'Org credential updated successfully'}), 200

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                except:
                    pass
            return jsonify({'success': False, 'error': str(e)}), 500
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
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
    if not credential_id.startswith(('platform_', 'oauth_', 'org_')):
        return jsonify({'error': 'Invalid credential_id format'}), 400
    
    id_type, id_value = credential_id.split('_', 1)
    
    # ✅ FIX: Validate id_value is numeric before conversion
    if not id_value.isdigit():
        return jsonify({
            'success': False,
            'valid': False,
            'message': 'Invalid credential ID format - ID must be numeric'
        }), 400
    
    conn = None  # Initialize for finally block
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            if id_type == 'oauth':
                # Test OAuth token
                cursor.execute("""
                    SELECT platform, email, is_active, is_valid, expires_at
                    FROM ai_infrastructure.oauth_tokens
                    WHERE user_id = %s AND id = %s
                """, (user_id, int(id_value)))

            elif id_type == 'org':
                # Test org-level credential — any org member may test
                cursor.execute("""
                    SELECT opc.platform, opc.display_name, opc.is_active
                    FROM ai_infrastructure.organisation_platform_credentials opc
                    JOIN ai_infrastructure.users u ON u.organisation_id = opc.organisation_id
                    WHERE u.id = %s AND opc.id = %s AND opc.is_active = TRUE
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
                cursor.close()
                return jsonify({
                    'success': False,
                    'valid': False,
                    'message': 'Credential not found or not active'
                }), 404
            
            # Basic validation (actual API testing would go here)
            # For now, just check if credential exists and is active
            platform = row[0] if len(row) > 0 else None
            
            if not platform:
                cursor.close()
                return jsonify({
                    'success': False,
                    'valid': False,
                    'message': 'Invalid credential data'
                }), 500
            
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
        
        except (ValueError, TypeError) as e:
            cursor.close()
            return jsonify({
                'success': False,
                'valid': False,
                'message': f'Invalid credential ID: {str(e)}'
            }), 400
            
    except Exception as e:
        print(f"Error testing credential {credential_id} for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'valid': False,
            'message': str(e)
        }), 500
    finally:
        # ✅ CRITICAL FIX: Always close connection
        if conn:
            try:
                conn.close()
            except:
                pass


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

        elif credential_id.startswith('org_'):
            # Org-level credential: check admin/owner role first
            _, id_value = credential_id.split('_', 1)
            cursor.execute("""
                SELECT u.org_role
                FROM ai_infrastructure.users u
                JOIN ai_infrastructure.organisation_platform_credentials opc
                  ON opc.organisation_id = u.organisation_id
                WHERE u.id = %s AND opc.id = %s AND opc.is_active = TRUE
            """, (user_id, int(id_value)))
            perm_row = cursor.fetchone()
            org_role = (perm_row[0] if not isinstance(perm_row, dict) else perm_row.get('org_role')) if perm_row else None
            if org_role not in ('admin', 'owner'):
                cursor.close()
                return jsonify({'success': False, 'error': 'Admin or owner role required'}), 403
            cursor.execute("""
                UPDATE ai_infrastructure.organisation_platform_credentials
                SET is_active = FALSE,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (int(id_value),))
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
