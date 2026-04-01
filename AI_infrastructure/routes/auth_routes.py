"""
AI_infrastructure/routes/auth_routes.py
Authentication Routes
====================

User login, registration, and Gmail OAuth integration

REFACTORED: 2026-01-01 - Complete cursor leak elimination
CHANGES:
- ✅ Converted ALL cursor = conn.cursor() to with conn.cursor() as cursor:
- ✅ Removed all manual cursor.close() calls (redundant)
- ✅ Removed cursor = None assignments (unnecessary)
- ✅ Removed finally blocks for cursor cleanup (context manager handles it)
- ✅ Proper indentation for all cursor operations
- ✅ 16 functions refactored, 0 cursor leaks remaining
"""

from flask import Blueprint, request, jsonify
from auth.user_auth import user_auth_manager, require_auth, UserAuthManager
from shared.database_utils import get_database_connection, convert_sql_placeholders, is_using_supabase


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register new user
    
    POST /api/auth/register
    {
        "username": "gerardo",
        "email": "gerardo@vetsuccessacademy.com",
        "password": "secure_password",
        "primary_gmail": "gerardo@vetsuccessacademy.com",
        "role": "admin"  // Optional: "admin" for master account, "user" for regular
    }
    
    Master Account (role="admin"):
    - Automatically sees ALL Gmail accounts from .env.master
    - No need to link Gmail accounts manually
    - Full access to all data
    
    Regular User (role="user"):
    - Must manually link Gmail accounts
    - Only sees data from linked accounts
    
    ✅ NO DATABASE OPERATIONS - Safe (uses user_auth_manager)
    """
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        primary_gmail = data.get('primary_gmail', email)
        role = data.get('role', 'user')  # NEW: Support admin role
        
        # Validate role
        if role not in ['user', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Invalid role. Must be "user" or "admin"'
            }), 400
        
        if not all([username, email, password]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: username, email, password'
            }), 400
        
        result = user_auth_manager.register_user(
            username=username,
            email=email,
            password=password,
            primary_gmail=primary_gmail,
            role=role  # Pass role
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST', 'GET'])
def login():
    """
    User login
    
    POST /api/auth/login
    {
        "username": "gerardo",
        "password": "secure_password"
    }
    
    GET /api/auth/login (dev mode - auto-login for localhost)
    
    Returns JWT token + user profile
    
    ✅ NO DATABASE OPERATIONS - Safe (uses user_auth_manager)
    """
    try:
        # DEV MODE: Auto-login for localhost GET requests
        if request.method == 'GET' and request.remote_addr in ['127.0.0.1', 'localhost', '::1']:
            print('[AUTH] Dev mode: Auto-login for localhost')
            # Return a dev token for local testing
            dev_user = {
                'id': 1,
                'username': 'dev-user',
                'email': 'dev@localhost',
                'role': 'admin'
            }
            token = user_auth_manager.generate_jwt(dev_user)
            return jsonify({
                'success': True,
                'token': token,
                'user': dev_user
            }), 200
        
        data = request.get_json() or {}
        
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({
                'success': False,
                'error': 'Missing username or password'
            }), 400
        
        result = user_auth_manager.login(username, password)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        print(f"[AUTH] Login error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/verify', methods=['GET'])
@require_auth
def verify():
    """
    Verify JWT token
    
    GET /api/auth/verify
    Headers: Authorization: Bearer <token>
    
    Returns user info if token valid
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    return jsonify({
        'success': True,
        'user': request.user
    })


@auth_bp.route('/link-gmail', methods=['POST'])
@require_auth
def link_gmail():
    """
    Link Gmail account to user profile
    
    POST /api/auth/link-gmail
    Headers: Authorization: Bearer <token>
    {
        "gmail_address": "marketing@minivetguide.com",
        "display_name": "MiniVet Marketing",
        "is_primary": false
    }
    
    ✅ NO DATABASE OPERATIONS - Safe (uses user_auth_manager)
    """
    try:
        data = request.get_json()
        user_id = request.user['user_id']
        
        gmail_address = data.get('gmail_address')
        display_name = data.get('display_name')
        is_primary = data.get('is_primary', False)
        
        if not gmail_address:
            return jsonify({
                'success': False,
                'error': 'gmail_address required'
            }), 400
        
        result = user_auth_manager.link_gmail_account(
            user_id=user_id,
            gmail_address=gmail_address,
            display_name=display_name,
            is_primary=is_primary
        )
        
        return jsonify(result), 200 if result['success'] else 400
        
    except Exception as e:
        print(f"❌ Gmail link error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/gmail-accounts', methods=['GET'])
@require_auth
def get_gmail_accounts():
    """
    Get all Gmail accounts linked to user
    
    GET /api/auth/gmail-accounts
    Headers: Authorization: Bearer <token>
    
    ✅ NO DATABASE OPERATIONS - Safe (uses user_auth_manager)
    """
    try:
        user_id = request.user['user_id']
        accounts = user_auth_manager.get_user_gmail_accounts(user_id)
        
        return jsonify({
            'success': True,
            'accounts': accounts
        })
        
    except Exception as e:
        print(f"❌ Get Gmail accounts error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    Get user profile with all linked accounts
    
    GET /api/auth/profile
    Headers: Authorization: Bearer <token>
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern for all 4 cursor operations
    - Eliminated cursor leak issues
    """
    try:
        user_id = request.user['user_id']
        
        # Get Gmail accounts (no DB operations in user_auth_manager)
        gmail_accounts = user_auth_manager.get_user_gmail_accounts(user_id)
        
        # Get workspace (no DB operations in user_auth_manager)
        workspace_id = user_auth_manager.get_user_workspace(user_id)
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Query 1: Get user data including display_name and org membership
                sql, params = convert_sql_placeholders(
                    '''SELECT password_hash, display_name, organisation_id, org_role, is_sub_user
                       FROM ai_infrastructure.users WHERE id = %s''',
                    (user_id,)
                )
                cursor.execute(sql, params)
                user_row = cursor.fetchone()
                
                auth_platform = None
                display_name = None
                organisation_id = None
                org_role = None
                is_sub_user = False
                if user_row:
                    display_name = user_row.get('display_name')
                    organisation_id = user_row.get('organisation_id')
                    org_role = user_row.get('org_role')
                    is_sub_user = bool(user_row.get('is_sub_user', False))
                    password_hash = user_row.get('password_hash')
                    if password_hash:
                        if password_hash == 'oauth_google':
                            auth_platform = 'google'
                        elif password_hash == 'oauth_microsoft' or password_hash == 'OAUTH_USER_NO_PASSWORD':
                            # Support both 'oauth_microsoft' (new) and 'OAUTH_USER_NO_PASSWORD' (legacy)
                            # Check OAuth tokens to determine which platform
                            bool_true = True if is_using_supabase() else 1
                            
                            # Query 2: Check OAuth platform
                            sql2, params2 = convert_sql_placeholders('''
                                SELECT platform FROM ai_infrastructure.oauth_tokens 
                                WHERE user_id = %s AND is_active = %s
                                ORDER BY created_at DESC LIMIT 1
                            ''', (user_id, bool_true))
                            cursor.execute(sql2, params2)
                            token_row = cursor.fetchone()
                            if token_row:
                                auth_platform = token_row['platform']  # 'google' or 'microsoft'
                            else:
                                # Default to microsoft for OAUTH_USER_NO_PASSWORD
                                auth_platform = 'microsoft'
                
                # Check if user has active OAuth tokens in user_platform_credentials
                google_oauth_connected = False
                microsoft_oauth_connected = False
                
                # Get database-agnostic boolean and datetime
                bool_true = True if is_using_supabase() else 1
                now_sql = "NOW()" if is_using_supabase() else "datetime('now')"
                
                # Query 3: Check Google OAuth tokens
                sql3, params3 = convert_sql_placeholders(f'''
                    SELECT COUNT(*) as count 
                    FROM ai_infrastructure.oauth_tokens 
                    WHERE user_id = %s 
                    AND platform = 'google' 
                    AND access_token IS NOT NULL
                    AND (is_active = %s OR is_active IS NULL)
                    AND (expires_at IS NULL OR expires_at > {now_sql})
                ''', (user_id, bool_true))
                cursor.execute(sql3, params3)
                result = cursor.fetchone()
                google_oauth_connected = (result['count'] if isinstance(result, dict) else result[0]) > 0 if result else False
                
                # Query 4: Check Microsoft OAuth tokens
                sql4, params4 = convert_sql_placeholders(f'''
                    SELECT COUNT(*) as count 
                    FROM ai_infrastructure.oauth_tokens 
                    WHERE user_id = %s 
                    AND (platform = 'microsoft' OR platform = 'microsoft365')
                    AND access_token IS NOT NULL
                    AND (is_active = %s OR is_active IS NULL)
                    AND (expires_at IS NULL OR expires_at > {now_sql})
                ''', (user_id, bool_true))
                cursor.execute(sql4, params4)
                result = cursor.fetchone()
                microsoft_oauth_connected = (result['count'] if isinstance(result, dict) else result[0]) > 0 if result else False
        
        return jsonify({
            'success': True,
            'profile': {
                **request.user,
                'id': request.user['user_id'],
                'display_name': display_name,
                'organisation_id': organisation_id,
                'org_role': org_role,
                'is_sub_user': is_sub_user,
                'gmail_accounts': gmail_accounts,
                'workspace_id': workspace_id,
                'auth_platform': auth_platform,
                'google_oauth_connected': google_oauth_connected,
                'microsoft_oauth_connected': microsoft_oauth_connected
            }
        })
        
    except Exception as e:
        print(f"❌ Get profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/api/auth/credentials/check', methods=['GET'])
@require_auth
def check_credentials():
    """
    Check if user has Google OAuth credentials connected
    
    GET /api/auth/credentials/check
    Headers: Authorization: Bearer <token>
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders('''
                    SELECT COUNT(*) as count
                    FROM ai_infrastructure.user_platform_credentials
                    WHERE user_id = %s 
                    AND platform = 'google'
                    AND credential_type = 'oauth'
                    AND credential_key = 'access_token'
                    AND is_active = 1
                ''', (user_id,))
                
                cursor.execute(sql, params)
                result = cursor.fetchone()
                
                has_google_oauth = result['count'] > 0
        
        return jsonify({
            'success': True,
            'has_google_oauth': has_google_oauth
        })
        
    except Exception as e:
        print(f"❌ Check credentials error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/update-display-name', methods=['POST'])
@require_auth
def update_display_name():
    """
    Update user's display name for multi-person collaboration
    
    POST /api/auth/update-display-name
    Headers: Authorization: Bearer <token>
    Body: { "display_name": "Sarah" }
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        data = request.get_json()
        
        if not data or 'display_name' not in data:
            return jsonify({'success': False, 'error': 'Missing display_name'}), 400
        
        display_name = str(data['display_name']).strip()[:50]
        
        if not display_name:
            return jsonify({'success': False, 'error': 'Display name cannot be empty'}), 400
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders('''
                    UPDATE ai_infrastructure.users 
                    SET display_name = %s
                    WHERE id = %s
                ''', (display_name, user_id))
                
                cursor.execute(sql, params)
                conn.commit()
        
        return jsonify({
            'success': True,
            'display_name': display_name
        })
        
    except Exception as e:
        print(f"❌ Update display name error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# TEAM ID MANAGEMENT ENDPOINTS (Sub-User System)
# ============================================================================

@auth_bp.route('/team-ids/add', methods=['POST'])
@require_auth
def add_team_id():
    """
    Add a new Team ID (sub-user) to the authenticated user's account
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        data = request.get_json()
        
        team_id = data.get('team_id', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', f"{team_id.lower()}@team.local").strip()
        permissions = data.get('permissions', {})
        allowed_tools = data.get('allowed_tools')
        allowed_agents = data.get('allowed_agents')
        data_access_scope = data.get('data_access_scope', 'own')
        usage_limit_daily = data.get('usage_limit_daily', 1000)
        
        if not team_id or len(team_id) < 2:
            return jsonify({'error': 'Team ID must be at least 2 characters'}), 400
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Check if Team ID already exists for this parent
                sql, params = convert_sql_placeholders('''
                    SELECT id FROM ai_infrastructure.users 
                    WHERE username = %s AND parent_user_id = %s
                ''', (team_id, user_id))
                cursor.execute(sql, params)
                
                if cursor.fetchone():
                    return jsonify({'error': f"Team ID '{team_id}' already exists"}), 400
                
                # Hash password
                import bcrypt
                if password:
                    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                else:
                    import secrets
                    random_password = secrets.token_urlsafe(16)
                    password_hash = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                
                # Insert Team ID as sub-user
                import json
                sql, params = convert_sql_placeholders('''
                    INSERT INTO ai_infrastructure.users (
                        username, email, password_hash, role,
                        parent_user_id, is_sub_user, display_name,
                        permissions, allowed_tools, allowed_agents,
                        data_access_scope, usage_limit_daily, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', [
                    team_id, email, password_hash, 'user',
                    user_id, True, team_id,
                    json.dumps(permissions) if permissions else None,
                    json.dumps(allowed_tools) if allowed_tools is not None else None,
                    json.dumps(allowed_agents) if allowed_agents is not None else None,
                    data_access_scope, usage_limit_daily, True
                ])
                
                cursor.execute(sql, params)
                conn.commit()
        
        print(f"✅ User {user_id} created Team ID '{team_id}'")
        
        return jsonify({
            'success': True,
            'team_id': team_id,
            'message': f"Team ID '{team_id}' created successfully"
        }), 201
        
    except Exception as e:
        print(f"❌ Add Team ID error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/team-ids', methods=['GET'])
@require_auth
def list_team_ids():
    """
    List all Team IDs for the authenticated user
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Get all Team IDs for this parent user
                sql, params = convert_sql_placeholders('''
                    SELECT 
                        id, username, email, is_active,
                        last_active, created_at,
                        permissions, allowed_tools, allowed_agents,
                        data_access_scope, usage_limit_daily
                    FROM ai_infrastructure.users
                    WHERE parent_user_id = %s AND is_sub_user = TRUE
                    ORDER BY created_at DESC
                ''', [user_id])
                
                cursor.execute(sql, params)
                
                team_ids = []
                import json
                for row in cursor.fetchall():
                    # Get active sessions for this Team ID
                    sql2, params2 = convert_sql_placeholders('''
                        SELECT device_info, ip_address, last_active
                        FROM ai_infrastructure.user_sessions
                        WHERE user_id = %s
                        ORDER BY last_active DESC
                        LIMIT 5
                    ''', [row['id'] if isinstance(row, dict) else row[0]])
                    
                    cursor.execute(sql2, params2)
                    
                    sessions = []
                    for session in cursor.fetchall():
                        device_info_raw = session['device_info'] if isinstance(session, dict) else session[0]
                        device_info = json.loads(device_info_raw) if device_info_raw else {}
                        sessions.append({
                            'device': f"{device_info.get('browser', 'Unknown')} on {device_info.get('os', 'Unknown')}",
                            'ip_address': session['ip_address'] if isinstance(session, dict) else session[1],
                            'last_active': (session['last_active'] if isinstance(session, dict) else session[2]).isoformat() if (session['last_active'] if isinstance(session, dict) else session[2]) else None
                        })
                    
                    team_ids.append({
                        'id': row['id'] if isinstance(row, dict) else row[0],
                        'team_id': row['username'] if isinstance(row, dict) else row[1],
                        'email': row['email'] if isinstance(row, dict) else row[2],
                        'is_active': row['is_active'] if isinstance(row, dict) else row[3],
                        'last_active': (row['last_active'] if isinstance(row, dict) else row[4]).isoformat() if (row['last_active'] if isinstance(row, dict) else row[4]) else None,
                        'created_at': (row['created_at'] if isinstance(row, dict) else row[5]).isoformat() if (row['created_at'] if isinstance(row, dict) else row[5]) else None,
                        'permissions': json.loads(row['permissions'] if isinstance(row, dict) else row[6]) if (row['permissions'] if isinstance(row, dict) else row[6]) else {},
                        'allowed_tools': json.loads(row['allowed_tools'] if isinstance(row, dict) else row[7]) if (row['allowed_tools'] if isinstance(row, dict) else row[7]) else None,
                        'allowed_agents': json.loads(row['allowed_agents'] if isinstance(row, dict) else row[8]) if (row['allowed_agents'] if isinstance(row, dict) else row[8]) else None,
                        'data_access_scope': row['data_access_scope'] if isinstance(row, dict) else row[9],
                        'usage_limit_daily': row['usage_limit_daily'] if isinstance(row, dict) else row[10],
                        'sessions': sessions
                    })
        
        return jsonify({'team_ids': team_ids}), 200
        
    except Exception as e:
        print(f"❌ List Team IDs error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/team-ids/<team_id>', methods=['PUT'])
@require_auth
def update_team_id(team_id):
    """
    Update Team ID settings
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        data = request.get_json()
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Verify Team ID belongs to this user
                sql, params = convert_sql_placeholders('''
                    SELECT id FROM ai_infrastructure.users
                    WHERE username = %s AND parent_user_id = %s AND is_sub_user = TRUE
                ''', [team_id, user_id])
                
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Team ID not found'}), 404
                
                sub_user_id = row['id'] if isinstance(row, dict) else row[0]
                
                # Build UPDATE dynamically
                updates = []
                params = []
                
                if 'password' in data:
                    import bcrypt
                    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    updates.append('password_hash = %s')
                    params.append(password_hash)
                
                if 'is_active' in data:
                    updates.append('is_active = %s')
                    params.append(data['is_active'])
                
                if 'permissions' in data:
                    import json
                    updates.append('permissions = %s')
                    params.append(json.dumps(data['permissions']))
                
                if 'allowed_tools' in data:
                    import json
                    updates.append('allowed_tools = %s')
                    params.append(json.dumps(data['allowed_tools']) if data['allowed_tools'] is not None else None)
                
                if 'usage_limit_daily' in data:
                    updates.append('usage_limit_daily = %s')
                    params.append(data['usage_limit_daily'])
                
                if not updates:
                    return jsonify({'error': 'No fields to update'}), 400
                
                params.append(sub_user_id)
                sql = f"UPDATE ai_infrastructure.users SET {', '.join(updates)} WHERE id = %s"
                sql, params = convert_sql_placeholders(sql, params)
                
                cursor.execute(sql, params)
                conn.commit()
        
        print(f"✅ Updated Team ID '{team_id}' for user {user_id}")
        
        return jsonify({'success': True, 'message': f"Team ID '{team_id}' updated"}), 200
        
    except Exception as e:
        print(f"❌ Update Team ID error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/team-ids/<team_id>', methods=['DELETE'])
@require_auth
def delete_team_id(team_id):
    """
    Delete Team ID (soft delete by setting is_active = FALSE)
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Verify Team ID belongs to this user
                sql, params = convert_sql_placeholders('''
                    SELECT id FROM ai_infrastructure.users
                    WHERE username = %s AND parent_user_id = %s AND is_sub_user = TRUE
                ''', [team_id, user_id])
                
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    return jsonify({'error': 'Team ID not found'}), 404
                
                sub_user_id = row['id'] if isinstance(row, dict) else row[0]
                
                # Soft delete
                sql, params = convert_sql_placeholders('''
                    UPDATE ai_infrastructure.users
                    SET is_active = FALSE
                    WHERE id = %s
                ''', [sub_user_id])
                
                cursor.execute(sql, params)
                
                # Revoke all sessions
                sql, params = convert_sql_placeholders('''
                    DELETE FROM ai_infrastructure.user_sessions
                    WHERE user_id = %s
                ''', [sub_user_id])
                
                cursor.execute(sql, params)
                conn.commit()
        
        print(f"✅ Deleted Team ID '{team_id}' for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': f"Team ID '{team_id}' deleted successfully"
        }), 200
        
    except Exception as e:
        print(f"❌ Delete Team ID error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/team-ids/stats', methods=['GET'])
@require_auth
def get_team_ids_stats():
    """
    Get aggregate statistics for all Team IDs
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Get all Team IDs with thread/message counts
                sql, params = convert_sql_placeholders('''
                    SELECT 
                        u.id,
                        u.username as team_id,
                        u.is_active,
                        u.last_active,
                        u.created_at,
                        COUNT(DISTINCT t.id) as thread_count,
                        COUNT(m.id) as message_count,
                        MAX(t.updated_at) as last_thread_activity
                    FROM ai_infrastructure.users u
                    LEFT JOIN sessions.threads t ON t.team_id = u.username
                    LEFT JOIN sessions.messages m ON m.thread_id = t.id
                    WHERE u.parent_user_id = %s AND u.is_sub_user = TRUE
                    GROUP BY u.id, u.username, u.is_active, u.last_active, u.created_at
                    ORDER BY thread_count DESC
                ''', [user_id])
                
                cursor.execute(sql, params)
                
                team_ids = []
                total_threads = 0
                total_messages = 0
                active_count = 0
                
                for row in cursor.fetchall():
                    thread_count = row['thread_count'] if isinstance(row, dict) else row[5]
                    message_count = row['message_count'] if isinstance(row, dict) else row[6]
                    is_active = row['is_active'] if isinstance(row, dict) else row[2]
                    
                    total_threads += thread_count
                    total_messages += message_count
                    if is_active:
                        active_count += 1
                    
                    last_activity = row['last_thread_activity'] if isinstance(row, dict) else row[7]
                    team_ids.append({
                        'id': row['id'] if isinstance(row, dict) else row[0],
                        'team_id': row['team_id'] if isinstance(row, dict) else row[1],
                        'is_active': is_active,
                        'thread_count': thread_count,
                        'message_count': message_count,
                        'last_active': last_activity.isoformat() if last_activity else None,
                        'created_at': (row['created_at'] if isinstance(row, dict) else row[4]).isoformat() if (row['created_at'] if isinstance(row, dict) else row[4]) else None
                    })
        
        return jsonify({
            'success': True,
            'total_team_ids': len(team_ids),
            'active_team_ids': active_count,
            'total_threads': total_threads,
            'total_messages': total_messages,
            'team_ids': team_ids
        }), 200
        
    except Exception as e:
        print(f"❌ Get Team IDs stats error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/team-ids/<team_id>/analytics', methods=['GET'])
@require_auth
def get_team_id_analytics(team_id):
    """
    Get detailed analytics for a specific Team ID
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        days = int(request.args.get('days', 30))
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Verify Team ID belongs to user
                sql, params = convert_sql_placeholders('''
                    SELECT id FROM ai_infrastructure.users
                    WHERE username = %s AND parent_user_id = %s AND is_sub_user = TRUE
                ''', [team_id, user_id])
                
                cursor.execute(sql, params)
                if not cursor.fetchone():
                    return jsonify({'error': 'Team ID not found'}), 404
                
                # Get overall stats
                sql, params = convert_sql_placeholders('''
                    SELECT 
                        COUNT(DISTINCT t.id) as thread_count,
                        COUNT(m.id) as message_count
                    FROM sessions.threads t
                    LEFT JOIN sessions.messages m ON m.thread_id = t.id
                    WHERE t.team_id = %s
                      AND t.created_at >= NOW() - INTERVAL '%s days'
                ''', [team_id, days])
                
                cursor.execute(sql, params)
                row = cursor.fetchone()
                thread_count = row['thread_count'] if isinstance(row, dict) else row[0]
                message_count = row['message_count'] if isinstance(row, dict) else row[1]
                avg_messages = (message_count / thread_count) if thread_count > 0 else 0
                
                # Get daily activity
                sql, params = convert_sql_placeholders('''
                    SELECT 
                        DATE(t.created_at) as date,
                        COUNT(DISTINCT t.id) as threads,
                        COUNT(m.id) as messages
                    FROM sessions.threads t
                    LEFT JOIN sessions.messages m ON m.thread_id = t.id
                    WHERE t.team_id = %s
                      AND t.created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY DATE(t.created_at)
                    ORDER BY date DESC
                    LIMIT 30
                ''', [team_id, days])
                
                cursor.execute(sql, params)
                daily_activity = []
                for row in cursor.fetchall():
                    daily_activity.append({
                        'date': (row['date'] if isinstance(row, dict) else row[0]).isoformat(),
                        'threads': row['threads'] if isinstance(row, dict) else row[1],
                        'messages': row['messages'] if isinstance(row, dict) else row[2]
                    })
                
                # Get top agents (from thread metadata)
                sql, params = convert_sql_placeholders('''
                    SELECT 
                        location as agent,
                        COUNT(*) as usage_count
                    FROM sessions.threads
                    WHERE team_id = %s
                      AND created_at >= NOW() - INTERVAL '%s days'
                      AND location IS NOT NULL
                    GROUP BY location
                    ORDER BY usage_count DESC
                    LIMIT 10
                ''', [team_id, days])
                
                cursor.execute(sql, params)
                top_agents = []
                for row in cursor.fetchall():
                    top_agents.append({
                        'agent': row['agent'] if isinstance(row, dict) else row[0],
                        'usage_count': row['usage_count'] if isinstance(row, dict) else row[1]
                    })
        
        return jsonify({
            'success': True,
            'team_id': team_id,
            'timeframe_days': days,
            'total_threads': thread_count,
            'total_messages': message_count,
            'avg_messages_per_thread': round(avg_messages, 1),
            'daily_activity': daily_activity,
            'top_agents': top_agents
        }), 200
        
    except Exception as e:
        print(f"❌ Get Team ID analytics error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/team-ids/export', methods=['GET'])
@require_auth
def export_team_ids_csv():
    """
    Export all Team IDs to CSV
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders('''
                    SELECT 
                        username as team_id,
                        email,
                        is_active,
                        created_at,
                        last_active,
                        data_access_scope,
                        usage_limit_daily
                    FROM ai_infrastructure.users
                    WHERE parent_user_id = %s AND is_sub_user = TRUE
                    ORDER BY created_at DESC
                ''', [user_id])
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
        
        # Generate CSV
        import io
        import csv
        from flask import make_response
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['team_id', 'email', 'is_active', 'created_at', 'last_active', 'data_access_scope', 'usage_limit_daily'])
        
        # Data rows
        for row in rows:
            writer.writerow([
                row['team_id'] if isinstance(row, dict) else row[0],
                row['email'] if isinstance(row, dict) else row[1],
                row['is_active'] if isinstance(row, dict) else row[2],
                (row['created_at'] if isinstance(row, dict) else row[3]).isoformat() if (row['created_at'] if isinstance(row, dict) else row[3]) else '',
                (row['last_active'] if isinstance(row, dict) else row[4]).isoformat() if (row['last_active'] if isinstance(row, dict) else row[4]) else '',
                row['data_access_scope'] if isinstance(row, dict) else row[5],
                row['usage_limit_daily'] if isinstance(row, dict) else row[6]
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=team_ids_export.csv'
        
        print(f"✅ Exported {len(rows)} Team IDs to CSV for user {user_id}")
        
        return response
        
    except Exception as e:
        print(f"❌ Export Team IDs error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/team-ids/import', methods=['POST'])
@require_auth
def import_team_ids_csv():
    """
    Import Team IDs from CSV file
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        user_id = request.user['user_id']
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        # Read CSV
        import csv
        import io
        import bcrypt
        
        stream = io.StringIO(file.stream.read().decode('utf-8'), newline=None)
        csv_reader = csv.DictReader(stream)
        
        imported = 0
        failed = 0
        errors = []
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                for i, row in enumerate(csv_reader, start=2):
                    try:
                        team_id = row.get('team_id', '').strip()
                        email = row.get('email', f"{team_id.lower()}@team.local").strip()
                        password = row.get('password', '').strip()
                        
                        if not team_id or len(team_id) < 2:
                            raise ValueError('Team ID must be at least 2 characters')
                        
                        # Check if already exists
                        sql, params = convert_sql_placeholders('''
                            SELECT id FROM ai_infrastructure.users
                            WHERE username = %s AND parent_user_id = %s
                        ''', [team_id, user_id])
                        
                        cursor.execute(sql, params)
                        if cursor.fetchone():
                            raise ValueError(f"Team ID '{team_id}' already exists")
                        
                        # Hash password
                        if password:
                            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        else:
                            import secrets
                            random_password = secrets.token_urlsafe(16)
                            password_hash = bcrypt.hashpw(random_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        
                        # Insert
                        sql, params = convert_sql_placeholders('''
                            INSERT INTO ai_infrastructure.users (
                                username, email, password_hash, role,
                                parent_user_id, is_sub_user, display_name, is_active
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ''', [team_id, email, password_hash, 'user', user_id, True, team_id, True])
                        
                        cursor.execute(sql, params)
                        imported += 1
                        
                    except Exception as e:
                        failed += 1
                        errors.append(f"Row {i}: {str(e)}")
                        print(f"❌ Import error on row {i}: {e}")
                
                conn.commit()
        
        print(f"✅ Imported {imported} Team IDs (failed: {failed}) for user {user_id}")
        
        return jsonify({
            'success': True,
            'imported': imported,
            'failed': failed,
            'errors': errors
        }), 200
        
    except Exception as e:
        print(f"❌ Import Team IDs error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/revoke-tokens', methods=['POST'])
@require_auth
def revoke_tokens():
    """
    Revoke OAuth tokens and COMPLETELY RESET user for re-authentication
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        import requests
        
        user_id = request.user['user_id']
        user_email = request.user.get('email', 'unknown')
        data = request.get_json() or {}
        platform = data.get('platform', 'google')
        complete_reset = data.get('complete_reset', True)
        
        print(f'🔄 [REVOKE TOKENS] User {user_id} ({user_email}) revoking {platform} tokens')
        print(f'   Complete Reset Mode: {complete_reset}')
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Get existing tokens BEFORE deleting (needed for provider revocation)
                sql, params = convert_sql_placeholders('''
                    SELECT access_token, refresh_token
                    FROM ai_infrastructure.oauth_tokens
                    WHERE user_id = %s AND platform = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (user_id, platform))
                
                cursor.execute(sql, params)
                token_row = cursor.fetchone()
                
                # ====================================================================
                # STEP 1: Revoke tokens with OAuth provider
                # ====================================================================
                revocation_status = {'provider_revoked': False, 'error': None}
                
                if token_row:
                    access_token = token_row['access_token']
                    refresh_token = token_row['refresh_token']
                    
                    if platform == 'google':
                        try:
                            print(f'🗑️ [REVOKE TOKENS] Revoking Google token via API...')
                            
                            token_to_revoke = refresh_token if refresh_token else access_token
                            
                            revoke_url = f'https://oauth2.googleapis.com/revoke'
                            response = requests.post(
                                revoke_url,
                                params={'token': token_to_revoke},
                                headers={'Content-Type': 'application/x-www-form-urlencoded'}
                            )
                            
                            if response.status_code == 200:
                                print(f'✅ [REVOKE TOKENS] Google token revoked successfully')
                                revocation_status['provider_revoked'] = True
                            else:
                                print(f'⚠️ [REVOKE TOKENS] Google revocation returned {response.status_code}')
                                revocation_status['error'] = f'HTTP {response.status_code}'
                        
                        except Exception as e:
                            print(f'⚠️ [REVOKE TOKENS] Google revocation failed: {e}')
                            revocation_status['error'] = str(e)
                    
                    elif platform == 'microsoft':
                        print(f'ℹ️ [REVOKE TOKENS] Microsoft token revocation via API not implemented')
                        revocation_status['provider_revoked'] = False
                        revocation_status['error'] = 'API revocation not implemented for Microsoft'
                else:
                    print(f'⚠️ [REVOKE TOKENS] No tokens found for user {user_id} on platform {platform}')
                
                # ====================================================================
                # STEP 2: Choose reset mode
                # ====================================================================
                if complete_reset:
                    print(f'🗑️ [COMPLETE RESET] Deleting user {user_id} completely from system...')
                    
                    # Delete ALL OAuth tokens (all platforms)
                    sql, params = convert_sql_placeholders(
                        'DELETE FROM ai_infrastructure.oauth_tokens WHERE user_id = %s',
                        (user_id,)
                    )
                    cursor.execute(sql, params)
                    tokens_deleted = cursor.rowcount
                    print(f'   ✅ Deleted {tokens_deleted} OAuth tokens')
                    
                    # Delete FROM ai_infrastructure.user_platform_credentials (if exists)
                    try:
                        sql, params = convert_sql_placeholders(
                            'DELETE FROM ai_infrastructure.user_platform_credentials WHERE user_id = %s',
                            (user_id,)
                        )
                        cursor.execute(sql, params)
                        creds_deleted = cursor.rowcount
                        print(f'   ✅ Deleted {creds_deleted} platform credentials')
                    except Exception as e:
                        print(f'   ⚠️ No user_platform_credentials table or error: {e}')
                    
                    # Delete user FROM ai_infrastructure.users table
                    sql, params = convert_sql_placeholders(
                        'DELETE FROM ai_infrastructure.users WHERE id = %s',
                        (user_id,)
                    )
                    cursor.execute(sql, params)
                    user_deleted = cursor.rowcount
                    print(f'   ✅ Deleted user record ({user_deleted} row)')
                    
                    conn.commit()
                    
                    print(f'✅ [COMPLETE RESET] User {user_id} completely removed from system')
                    
                    response_data = {
                        'success': True,
                        'message': f'User account completely reset',
                        'complete_reset': True,
                        'tokens_deleted': tokens_deleted,
                        'user_deleted': user_deleted,
                        'provider_revoked': revocation_status['provider_revoked'],
                        'next_step': f'Redirect to /api/auth/{platform}/login to re-register'
                    }
                
                else:
                    print(f'🔄 [NORMAL RESET] Clearing tokens but keeping user account...')
                    
                    # Delete tokens for specific platform only
                    sql, params = convert_sql_placeholders('''
                        DELETE FROM ai_infrastructure.oauth_tokens
                        WHERE user_id = %s AND platform = %s
                    ''', (user_id, platform))
                    
                    cursor.execute(sql, params)
                    deleted_count = cursor.rowcount
                    
                    # Update user flags
                    if platform == 'google':
                        sql, params = convert_sql_placeholders(
                            'UPDATE ai_infrastructure.users SET has_google_oauth = 0 WHERE id = %s',
                            (user_id,)
                        )
                        cursor.execute(sql, params)
                    elif platform == 'microsoft':
                        sql, params = convert_sql_placeholders(
                            'UPDATE ai_infrastructure.users SET has_microsoft_oauth = 0 WHERE id = %s',
                            (user_id,)
                        )
                        cursor.execute(sql, params)
                    
                    conn.commit()
                    
                    print(f'✅ [NORMAL RESET] Deleted {deleted_count} tokens for {platform}')
                    
                    response_data = {
                        'success': True,
                        'message': f'{platform.capitalize()} tokens revoked',
                        'complete_reset': False,
                        'deleted_count': deleted_count,
                        'provider_revoked': revocation_status['provider_revoked'],
                        'revocation_error': revocation_status['error']
                    }
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f'❌ [REVOKE TOKENS] Error: {e}')
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/credentials/<platform>', methods=['GET'])
@require_auth
def get_platform_credentials(platform):
    """
    Get ALL stored credentials for a platform (masked for display)
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        print(f"🔍 [GET CREDENTIALS] Platform: {platform}")
        
        if not hasattr(request, 'user'):
            print("❌ [GET CREDENTIALS] request.user not set by @require_auth")
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = request.user.get('user_id') or request.user.get('id')
        if not user_id:
            print(f"❌ [GET CREDENTIALS] No user_id in request.user: {request.user}")
            return jsonify({
                'success': False,
                'error': 'User ID not found'
            }), 401
        
        print(f"✅ [GET CREDENTIALS] User ID: {user_id}")
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                cursor.execute("""
                    SELECT 
                        id,
                        credential_key,
                        credential_value,
                        credential_type,
                        metadata,
                        is_active,
                        created_at
                    FROM ai_infrastructure.user_platform_credentials
                    WHERE user_id = %s AND platform = %s
                    ORDER BY is_active DESC, created_at DESC
                """, (user_id, platform))
                
                rows = cursor.fetchall()
        
        print(f"✅ [GET CREDENTIALS] Found {len(rows)} credential(s) for platform {platform}")
        
        if not rows:
            return jsonify({
                'success': True,
                'has_credentials': False,
                'credentials': []
            })
        
        # Mask credentials for display
        from AI_infrastructure.auth.credential_encryptor import get_encryptor
        encryptor = get_encryptor()
        
        credentials_list = []
        for row in rows:
            cred_id, cred_key, cred_value, cred_type, metadata, is_active, created_at = row
            
            # Extract account name from metadata
            account_name = None
            if metadata:
                account_name = (
                    metadata.get('email') or 
                    metadata.get('account_name') or 
                    metadata.get('username') or
                    metadata.get('display_name')
                )
            
            masked_value = encryptor.mask_credential(cred_value) if cred_value else None
            
            credentials_list.append({
                'id': cred_id,
                'credential_key': cred_key,
                'credential_value_masked': masked_value,
                'credential_type': cred_type,
                'account_name': account_name,
                'is_active': is_active,
                'created_at': created_at.isoformat() if created_at else None,
                'metadata': metadata
            })
        
        return jsonify({
            'success': True,
            'has_credentials': True,
            'credentials': credentials_list
        })
        
    except Exception as e:
        print(f"❌ Get credentials error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/credentials/test', methods=['POST'])
@require_auth
def test_credentials():
    """
    Test platform credentials with real API call
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    try:
        data = request.get_json()
        user_id = request.user.get('user_id')
        
        platform = data.get('platform')
        credentials = data.get('credentials', {})
        settings = data.get('settings', {})
        
        if not platform:
            return jsonify({
                'success': False,
                'error': 'Platform not specified'
            }), 400
        
        if not credentials:
            return jsonify({
                'success': False,
                'error': 'Credentials not provided'
            }), 400
        
        # Import credential tester
        from auth.credential_tester import CredentialTester
        from auth.credential_encryptor import get_encryptor
        
        # Decrypt credentials if encrypted
        encryptor = get_encryptor()
        decrypted_credentials = encryptor.decrypt_dict(credentials)
        
        # Test credentials
        tester = CredentialTester()
        result = tester.test_credential(platform, decrypted_credentials, settings)
        
        # Add timestamp
        from datetime import datetime
        result['tested_at'] = datetime.now().isoformat()
        result['platform'] = platform
        result['user_id'] = user_id
        
        print(f"{'✅' if result['success'] else '❌'} [CREDENTIAL TEST] User {user_id} tested {platform}: {result['message']}")
        
        # Update last_tested timestamp in database
        if result['success']:
            with get_database_connection('ai_infrastructure') as conn:
                with conn.cursor() as cursor:
                    
                    cursor.execute('''
                        UPDATE ai_infrastructure.user_platform_credentials
                        SET last_tested_at = NOW(),
                            updated_at = NOW()
                        WHERE user_id = %s AND platform = %s
                    ''', (user_id, platform))
                    
                    conn.commit()
        
        return jsonify(result)
    
    except Exception as e:
        print(f'❌ [TEST CREDENTIALS] Error: {e}')
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Credential test failed'
        }), 500


@auth_bp.route('/preferences', methods=['GET'])
@require_auth
def get_user_preferences():
    """
    GET /api/auth/preferences
    Get user preferences and settings
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    user_id = request.user['user_id']
    
    try:
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                sql, params = convert_sql_placeholders(
                    'SELECT * FROM ai_infrastructure.user_preferences WHERE user_id = %s',
                    (user_id,)
                )
                cursor.execute(sql, params)
                row = cursor.fetchone()
                
                if not row:
                    # Return default preferences if none exist
                    return jsonify({
                        'success': True,
                        'preferences': {
                            'user_id': user_id,
                            'communication_style': 'professional',
                            'detail_level': 'standard',
                            'auth_platform': 'auto',
                            'preferred_tools': None,
                            'custom_preferences': None,
                            'nickname': '',
                            'ai_model': 'claude-sonnet-4-5-20250929',
                            'ai_temperature': 1.0,
                            'ai_top_p': 1.0,
                            'ai_max_tokens': 4096,
                            'ai_thinking_enabled': 0,
                            'ai_thinking_budget': 10000,
                            'ai_streaming_enabled': 1
                        }
                    })
                
                # Convert row to dict
                if isinstance(row, dict):
                    prefs = row
                else:
                    prefs = {
                        'user_id': row[0],
                        'communication_style': row[1],
                        'detail_level': row[2],
                        'auth_platform': row[3],
                        'preferred_tools': row[4],
                        'custom_preferences': row[5],
                        'created_at': row[6].isoformat() if row[6] else None,
                        'updated_at': row[7].isoformat() if row[7] else None,
                        'nickname': row[8],
                        'detected_country': row[9],
                        'detected_city': row[10],
                        'detected_timezone': row[11],
                        'detected_ip_address': row[12],
                        'manual_location_override': row[13],
                        'manual_timezone_override': row[14],
                        'use_manual_location': row[15],
                        'use_manual_timezone': row[16],
                        'last_location_check': row[17].isoformat() if row[17] else None,
                        'ai_memories': row[18],
                        'memory_updated_at': row[19].isoformat() if row[19] else None,
                        'ai_model': row[20],
                        'ai_temperature': float(row[21]) if row[21] else 1.0,
                        'ai_top_p': float(row[22]) if row[22] else 1.0,
                        'ai_max_tokens': int(row[23]) if row[23] else 4096,
                        'ai_thinking_enabled': int(row[24]) if row[24] else 0,
                        'ai_thinking_budget': int(row[25]) if row[25] else 10000,
                        'ai_streaming_enabled': int(row[26]) if row[26] else 1
                    }
                
                return jsonify({
                    'success': True,
                    'preferences': prefs
                })
    
    except Exception as e:
        print(f'❌ [GET PREFERENCES] Error for user {user_id}: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/preferences', methods=['PUT'])
@require_auth
def update_user_preferences():
    """
    PUT /api/auth/preferences
    Update user preferences and settings
    
    REFACTORED: 2026-01-01
    - Converted to context manager pattern
    """
    user_id = request.user['user_id']
    data = request.get_json()
    
    try:
        # Build UPDATE query dynamically based on provided fields
        allowed_fields = [
            'communication_style', 'detail_level', 'auth_platform',
            'preferred_tools', 'custom_preferences', 'nickname',
            'manual_location_override', 'manual_timezone_override',
            'use_manual_location', 'use_manual_timezone',
            'ai_model', 'ai_temperature', 'ai_top_p', 'ai_max_tokens',
            'ai_thinking_enabled', 'ai_thinking_budget', 'ai_streaming_enabled'
        ]
        
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])
        
        if not updates:
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        # Add updated_at
        updates.append("updated_at = NOW()")
        values.append(user_id)
        
        with get_database_connection('ai_infrastructure') as conn:
            with conn.cursor() as cursor:
                
                # Check if preferences exist
                sql_check, params_check = convert_sql_placeholders(
                    'SELECT user_id FROM ai_infrastructure.user_preferences WHERE user_id = %s',
                    (user_id,)
                )
                cursor.execute(sql_check, params_check)
                exists = cursor.fetchone()
                
                if exists:
                    # UPDATE
                    sql = f"UPDATE ai_infrastructure.user_preferences SET {', '.join(updates)} WHERE user_id = %s"
                    sql, params = convert_sql_placeholders(sql, tuple(values))
                    cursor.execute(sql, params)
                else:
                    # INSERT with defaults
                    field_names = ['user_id'] + [f.split(' = ')[0] for f in updates if f != "updated_at = NOW()"]
                    placeholders = ['%s'] * len(field_names)
                    sql = f"INSERT INTO ai_infrastructure.user_preferences ({', '.join(field_names)}) VALUES ({', '.join(placeholders)})"
                    insert_values = [user_id] + [v for i, v in enumerate(values) if i < len(values) - 1]
                    sql, params = convert_sql_placeholders(sql, tuple(insert_values))
                    cursor.execute(sql, params)
                
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Preferences updated successfully'
                })
    
    except Exception as e:
        print(f'❌ [UPDATE PREFERENCES] Error for user {user_id}: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# SESSION MANAGEMENT - Get active sessions
# ============================================================

@auth_bp.route('/sessions', methods=['GET'])
@require_auth
def get_active_sessions():
    """
    Get all active sessions for the current user
    
    ✅ NO DATABASE OPERATIONS - Returns mock data
    """
    try:
        user_id = request.user.get('user_id')
        user_agent = request.headers.get('User-Agent', '')
        
        sessions = [
            {
                'id': 'session_current',
                'browser': 'Current Session',
                'os': parse_os_from_ua(user_agent),
                'device_type': 'desktop',
                'device_info': {
                    'browser': parse_browser_from_ua(user_agent),
                    'os': parse_os_from_ua(user_agent),
                    'device_type': 'desktop'
                },
                'ip_address': request.remote_addr,
                'user_agent': user_agent,
                'is_current': True,
                'created_at': None,
                'last_activity': None
            }
        ]
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    
    except Exception as e:
        user_id = request.user.get('user_id', 'unknown')
        print(f'❌ [GET SESSIONS] Error for user {user_id}: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@auth_bp.route('/sessions/<session_id>', methods=['DELETE'])
@require_auth
def revoke_session(session_id):
    """
    Revoke a specific session (logout device)
    
    ✅ NO DATABASE OPERATIONS - Mock implementation
    """
    try:
        user_id = request.user['user_id']
        
        print(f'[REVOKE SESSION] User {user_id} revoked session {session_id}')
        
        return jsonify({
            'success': True,
            'message': f'Session {session_id} revoked successfully'
        })
    
    except Exception as e:
        print(f'❌ [REVOKE SESSION] Error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# NEW TEAMS SYSTEM (Migration 038) — Email + Team Name + Password
# ============================================================================

@auth_bp.route('/teams/create', methods=['POST'])
@require_auth
def create_team():
    """
    Create a new team under the authenticated user.
    Body: { team_name, password, display_name (optional), description (optional), color (optional) }
    """
    import bcrypt
    import re
    try:
        user_id = request.user['user_id']
        data = request.get_json() or {}

        team_name    = (data.get('team_name') or '').strip().lower()
        password     = data.get('password') or data.get('team_password', '')
        display_name = (data.get('display_name') or '').strip()
        description  = (data.get('description') or '').strip()
        color        = (data.get('color') or '#3498db').strip()

        # Validate team_name (alphanumeric + underscore only)
        if not team_name:
            return jsonify({'success': False, 'error': 'team_name is required'}), 400
        if not re.match(r'^[a-z0-9_]{2,50}$', team_name):
            return jsonify({'success': False, 'error': 'team_name must be 2-50 chars, lowercase letters, digits, underscores only'}), 400

        # Validate password
        if not password or len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400

        # Hash password
        team_password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Get parent user's email
        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT email FROM ai_infrastructure.users WHERE id = %s',
                    (user_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return jsonify({'success': False, 'error': 'User not found'}), 404
                parent_email = row[0] if not isinstance(row, dict) else row['email']

            # Insert team
            with conn.cursor() as cursor:
                cursor.execute(
                    convert_sql_placeholders('''
                        INSERT INTO ai_infrastructure.teams
                            (parent_user_id, parent_email, team_name, team_password_hash,
                             display_name, description, color, created_by)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, team_name, display_name, color, created_at
                    '''),
                    (user_id, parent_email, team_name, team_password_hash,
                     display_name or None, description or None, color, user_id)
                )
                team = cursor.fetchone()
            conn.commit()

        if isinstance(team, dict):
            team_id, created_team_name, dn, col, cat = (
                team['id'], team['team_name'], team['display_name'], team['color'], team['created_at']
            )
        else:
            team_id, created_team_name, dn, col, cat = team

        return jsonify({
            'success': True,
            'team': {
                'id': team_id,
                'team_name': created_team_name,
                'display_name': dn,
                'color': col,
                'created_at': str(cat)
            }
        }), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        # Unique constraint violation
        if 'teams_unique_per_email' in str(e) or 'unique' in str(e).lower():
            return jsonify({'success': False, 'error': f'Team name "{team_name}" already exists under your account'}), 409
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/teams', methods=['GET'])
@require_auth
def list_teams():
    """List all teams belonging to the authenticated user."""
    try:
        user_id = request.user['user_id']

        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    convert_sql_placeholders('''
                        SELECT id, team_name, display_name, description, color,
                               member_count, is_active, created_at, updated_at
                        FROM ai_infrastructure.teams
                        WHERE parent_user_id = %s AND is_active = TRUE
                        ORDER BY created_at ASC
                    '''),
                    (user_id,)
                )
                rows = cursor.fetchall()

        teams = []
        for row in rows:
            if isinstance(row, dict):
                teams.append({
                    'id': row['id'],
                    'team_name': row['team_name'],
                    'display_name': row['display_name'],
                    'description': row['description'],
                    'color': row['color'],
                    'member_count': row['member_count'],
                    'is_active': row['is_active'],
                    'created_at': str(row['created_at']),
                    'updated_at': str(row['updated_at'])
                })
            else:
                teams.append({
                    'id': row[0],
                    'team_name': row[1],
                    'display_name': row[2],
                    'description': row[3],
                    'color': row[4],
                    'member_count': row[5],
                    'is_active': row[6],
                    'created_at': str(row[7]),
                    'updated_at': str(row[8])
                })

        return jsonify({'success': True, 'teams': teams, 'total': len(teams)})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/teams/<team_name>', methods=['PUT'])
@require_auth
def update_team(team_name):
    """
    Update a team's display_name, description, or color.
    Cannot change team_name (it's the login identifier).
    Body: { display_name, description, color }
    """
    try:
        user_id = request.user['user_id']
        data = request.get_json() or {}

        display_name = data.get('display_name', '').strip() or None
        description  = data.get('description', '').strip() or None
        color        = data.get('color', '').strip() or None
        new_password = data.get('password') or data.get('team_password', '')

        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Only update fields that were provided
                fields = []
                values = []
                if 'display_name' in data:
                    fields.append('display_name = %s')
                    values.append(display_name)
                if 'description' in data:
                    fields.append('description = %s')
                    values.append(description)
                if 'color' in data:
                    fields.append('color = %s')
                    values.append(color)
                if new_password:
                    import bcrypt as _bcrypt
                    if len(new_password) < 8:
                        return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
                    fields.append('team_password_hash = %s')
                    values.append(_bcrypt.hashpw(new_password.encode('utf-8'), _bcrypt.gensalt()).decode('utf-8'))

                if not fields:
                    return jsonify({'success': False, 'error': 'No fields to update'}), 400

                fields.append('updated_at = NOW()')
                values.extend([user_id, team_name])

                cursor.execute(
                    convert_sql_placeholders(
                        f"UPDATE ai_infrastructure.teams SET {', '.join(fields)} "
                        f"WHERE parent_user_id = %s AND team_name = %s AND is_active = TRUE"
                    ),
                    values
                )
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Team not found or access denied'}), 404
            conn.commit()

        return jsonify({'success': True, 'message': f'Team "{team_name}" updated'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/teams/<team_name>', methods=['DELETE'])
@require_auth
def delete_team(team_name):
    """Soft-delete a team (sets is_active = FALSE)."""
    try:
        user_id = request.user['user_id']

        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    convert_sql_placeholders('''
                        UPDATE ai_infrastructure.teams
                        SET is_active = FALSE, updated_at = NOW()
                        WHERE parent_user_id = %s AND team_name = %s AND is_active = TRUE
                    '''),
                    (user_id, team_name)
                )
                if cursor.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Team not found or access denied'}), 404
            conn.commit()

        return jsonify({'success': True, 'message': f'Team "{team_name}" deleted'})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================================
# TEAM LOGIN ENDPOINT
# ============================================================================

@auth_bp.route('/login/team', methods=['POST'])
def login_team():
    """
    Login as a team.
    Body: { email, team_name, password }

    On success, returns a JWT where:
      - user_id   = parent user's ID  (so ALL credential lookups work automatically)
      - team_id   = teams.id
      - team_name = the team_name string
      - login_mode = 'team'
    """
    import bcrypt
    import jwt as pyjwt
    from datetime import datetime, timedelta
    import json
    try:
        data = request.get_json() or {}
        email     = (data.get('email') or '').strip().lower()
        team_name = (data.get('team_name') or '').strip().lower()
        password  = data.get('password', '')

        if not email or not team_name or not password:
            return jsonify({'success': False, 'error': 'email, team_name and password are required'}), 400

        with get_database_connection() as conn:
            with conn.cursor() as cursor:
                # Look up active team by email + team_name
                cursor.execute(
                    convert_sql_placeholders('''
                        SELECT t.id, t.team_name, t.team_password_hash, t.display_name,
                               t.color, t.parent_user_id,
                               u.username, u.email AS parent_email, u.role,
                               u.organisation_id, u.org_role,
                               COALESCE(u.jwt_version, 1) AS jwt_version,
                               COALESCE(o.plan_tier, 'starter') AS plan_tier
                        FROM ai_infrastructure.teams t
                        JOIN ai_infrastructure.users u ON u.id = t.parent_user_id
                        LEFT JOIN ai_infrastructure.organisations o ON o.id = u.organisation_id
                        WHERE LOWER(t.parent_email) = %s
                          AND t.team_name = %s
                          AND t.is_active = TRUE
                    '''),
                    (email, team_name)
                )
                row = cursor.fetchone()

        if not row:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

        if isinstance(row, dict):
            team_id           = row['id']
            stored_team_name  = row['team_name']
            password_hash     = row['team_password_hash']
            display_name      = row['display_name']
            color             = row['color']
            parent_user_id    = row['parent_user_id']
            username          = row['username']
            parent_email      = row['parent_email']
            role              = row['role']
            organisation_id   = row['organisation_id']
            org_role          = row['org_role']
            jwt_version       = int(row['jwt_version'])
            plan_tier         = row['plan_tier']
        else:
            (team_id, stored_team_name, password_hash, display_name,
             color, parent_user_id, username, parent_email, role,
             organisation_id, org_role, jwt_version, plan_tier) = row

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

        # Build JWT — user_id = parent_user_id so all credential lookups work automatically
        jwt_secret = user_auth_manager.jwt_secret
        exp_time   = datetime.utcnow() + timedelta(days=30)
        token_payload = {
            'user_id':         parent_user_id,   # Parent's ID — inherits all credentials
            'username':        username,
            'email':           parent_email,
            'role':            role,
            'organisation_id': organisation_id,
            'org_role':        org_role,
            'jwt_version':     jwt_version,
            'plan_tier':       plan_tier,
            'team_id':         team_id,
            'team_name':       stored_team_name,
            'team_display_name': display_name or stored_team_name,
            'team_color':      color or '#3498db',
            'login_mode':      'team',
            'exp':             int(exp_time.timestamp())
        }

        token = pyjwt.encode(token_payload, jwt_secret, algorithm='HS256')

        # Store session
        try:
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            with get_database_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        convert_sql_placeholders('''
                            INSERT INTO ai_infrastructure.user_sessions
                                (user_id, token, expires_at, ip_address, user_agent, device_info)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        '''),
                        (parent_user_id, token, exp_time.strftime('%Y-%m-%d %H:%M:%S'),
                         ip_address, user_agent, '{}')
                    )
                conn.commit()
        except Exception as session_err:
            print(f'[TEAM LOGIN] Session store warning: {session_err}')

        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id':            parent_user_id,
                'username':      username,
                'email':         parent_email,
                'role':          role,
                'login_mode':    'team',
                'team_id':       team_id,
                'team_name':     stored_team_name,
                'team_display_name': display_name or stored_team_name,
                'team_color':    color or '#3498db',
                'organisation_id': organisation_id,
                'org_role':      org_role
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def parse_browser_from_ua(user_agent):
    """Extract browser name from User-Agent string"""
    ua = user_agent.lower()
    if 'chrome' in ua and 'edge' not in ua:
        return 'Chrome'
    elif 'firefox' in ua:
        return 'Firefox'
    elif 'safari' in ua and 'chrome' not in ua:
        return 'Safari'
    elif 'edge' in ua or 'edg' in ua:
        return 'Edge'
    elif 'opera' in ua or 'opr' in ua:
        return 'Opera'
    else:
        return 'Unknown'


def parse_os_from_ua(user_agent):
    """Extract OS name from User-Agent string"""
    ua = user_agent.lower()
    if 'windows' in ua:
        return 'Windows'
    elif 'macintosh' in ua or 'mac os' in ua:
        return 'macOS'
    elif 'linux' in ua:
        return 'Linux'
    elif 'android' in ua:
        return 'Android'
    elif 'iphone' in ua or 'ipad' in ua or 'ios' in ua:
        return 'iOS'
    else:
        return 'Unknown'