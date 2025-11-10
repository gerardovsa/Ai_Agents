"""
Authentication Routes
====================

User login, registration, and Gmail OAuth integration
"""

from flask import Blueprint, request, jsonify
from auth.user_auth import user_auth_manager, require_auth


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
    """
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        primary_gmail = data.get('primary_gmail', email)
        role = data.get('role', 'user')  #  NEW: Support admin role
        
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
            role=role  #  Pass role
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        print(f" Registration error: {e}")
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
        print(f" Gmail link error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/gmail-accounts', methods=['GET'])
@require_auth
def get_gmail_accounts():
    """
    Get all Gmail accounts linked to user
    
    GET /api/auth/gmail-accounts
    Headers: Authorization: Bearer <token>
    
    DEPRECATED: Gmail accounts now in oauth_tokens table (ai_infrastructure.db)
    Returns empty list for backward compatibility
    """
    try:
        user_id = request.user['user_id']
        # DEPRECATED: user_gmail_accounts table removed 2025-11-10
        # Gmail OAuth tokens now in oauth_tokens table
        accounts = []  # Return empty list instead of querying deleted table
        
        return jsonify({
            'success': True,
            'accounts': accounts
        })
        
    except Exception as e:
        print(f" Get Gmail accounts error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """
    Get user profile with all linked accounts
    
    GET /api/auth/profile
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = request.user['user_id']
        
        # DEPRECATED: Gmail accounts now in oauth_tokens table
        # Return empty list for backward compatibility
        gmail_accounts = []  # user_gmail_accounts table removed 2025-11-10
        
        # Get workspace
        workspace_id = user_auth_manager.get_user_workspace(user_id)
        
        # Determine authentication platform based on password_hash
        import sqlite3
        import os
        from pathlib import Path
        
        # Use centralized database path
        root_dir = Path(__file__).parent.parent.parent
        db_path = root_dir / 'data' / 'ai_infrastructure.db'
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        
        auth_platform = None
        if user_row and user_row['password_hash']:
            password_hash = user_row['password_hash']
            if password_hash == 'oauth_google':
                auth_platform = 'google'
            elif password_hash == 'oauth_microsoft' or password_hash == 'OAUTH_USER_NO_PASSWORD':
                # Support both 'oauth_microsoft' (new) and 'OAUTH_USER_NO_PASSWORD' (legacy)
                # Check OAuth tokens to determine which platform
                cursor.execute('''
                    SELECT platform FROM oauth_tokens 
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY created_at DESC LIMIT 1
                ''', (user_id,))
                token_row = cursor.fetchone()
                if token_row:
                    auth_platform = token_row['platform']  # 'google' or 'microsoft'
                else:
                    # Default to microsoft for OAUTH_USER_NO_PASSWORD
                    auth_platform = 'microsoft'
        
        #  Check if user has active OAuth tokens in user_platform_credentials
        #  CRITICAL FIX: Check OAuth credentials for ALL users, not just OAuth-created accounts
        # Local accounts (admin) can have linked OAuth credentials too!
        google_oauth_connected = False
        microsoft_oauth_connected = False
        
        # Always check for Google OAuth tokens (regardless of auth_platform)
        # ✅ FIX: Check oauth_tokens table (where Google/Microsoft OAuth actually stores tokens)
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM oauth_tokens 
            WHERE user_id = ? 
            AND platform = 'google' 
            AND access_token IS NOT NULL
            AND (is_active = 1 OR is_active IS NULL)
            AND (expires_at IS NULL OR expires_at > datetime('now'))
        ''', (user_id,))
        result = cursor.fetchone()
        google_oauth_connected = result['count'] > 0 if result else False
        
        # Always check for Microsoft OAuth tokens (regardless of auth_platform)
        # ✅ FIX: Check oauth_tokens table (where Google/Microsoft OAuth actually stores tokens)
        cursor.execute('''
            SELECT COUNT(*) as count 
            FROM oauth_tokens 
            WHERE user_id = ? 
            AND (platform = 'microsoft' OR platform = 'microsoft365')
            AND access_token IS NOT NULL
            AND (is_active = 1 OR is_active IS NULL)
            AND (expires_at IS NULL OR expires_at > datetime('now'))
        ''', (user_id,))
        result = cursor.fetchone()
        microsoft_oauth_connected = result['count'] > 0 if result else False
        
        conn.close()
        
        return jsonify({
            'success': True,
            'profile': {
                **request.user,
                'id': request.user['user_id'],  # ✅ FIX: Add 'id' alias for frontend compatibility
                'gmail_accounts': gmail_accounts,
                'workspace_id': workspace_id,
                'auth_platform': auth_platform,  # 'google' | 'microsoft' | None
                'google_oauth_connected': google_oauth_connected,  #  NEW: Token status
                'microsoft_oauth_connected': microsoft_oauth_connected  #  NEW: Token status
            }
        })
        
    except Exception as e:
        print(f" Get profile error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/api/auth/credentials/check', methods=['GET'])
@require_auth
def check_credentials():
    """
    Check if user has Google OAuth credentials connected
    
    GET /api/auth/credentials/check
    Headers: Authorization: Bearer <token>
    """
    try:
        user_id = request.user['user_id']
        
        # Check if user has active Google credentials
        from ..auth import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM user_platform_credentials
            WHERE user_id = ? 
            AND platform = 'google'
            AND credential_type = 'oauth'
            AND credential_key = 'access_token'
            AND is_active = 1
        ''', (user_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        has_google_oauth = result['count'] > 0
        
        return jsonify({
            'success': True,
            'has_google_oauth': has_google_oauth
        })
        
    except Exception as e:
        print(f" Check credentials error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/revoke-tokens', methods=['POST'])
@require_auth
def revoke_tokens():
    """
    Revoke OAuth tokens and COMPLETELY RESET user for re-authentication
    
    POST /api/auth/revoke-tokens
    Body: { 
        "platform": "google" | "microsoft",
        "complete_reset": true  // Optional: completely remove user from system
    }
    
    COMPLETE RESET MODE (complete_reset=true):
    1. Revoke tokens with OAuth provider (Google/Microsoft API)
    2. Delete ALL OAuth tokens for user
    3. Delete user from users table
    4. Clear all user data
    5. Force fresh registration on next OAuth
    
    NORMAL MODE (complete_reset=false):
    1. Revoke tokens with OAuth provider
    2. Delete tokens from database
    3. Update user flags
    """
    try:
        import sqlite3
        from pathlib import Path
        import requests
        
        user_id = request.user['user_id']
        user_email = request.user.get('email', 'unknown')
        data = request.get_json() or {}
        platform = data.get('platform', 'google')
        complete_reset = data.get('complete_reset', True)  # Default to TRUE for complete reset
        
        print(f'🔄 [REVOKE TOKENS] User {user_id} ({user_email}) revoking {platform} tokens')
        print(f'   Complete Reset Mode: {complete_reset}')
        
        # Connect to database
        root_dir = Path(__file__).parent.parent.parent
        db_path = root_dir / 'data' / 'ai_infrastructure.db'
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get existing tokens BEFORE deleting (needed for provider revocation)
        cursor.execute('''
            SELECT access_token, refresh_token
            FROM oauth_tokens
            WHERE user_id = ? AND platform = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (user_id, platform))
        
        token_row = cursor.fetchone()
        
        # ====================================================================
        # STEP 1: Revoke tokens with OAuth provider
        # ====================================================================
        revocation_status = {'provider_revoked': False, 'error': None}
        
        if token_row:
            access_token = token_row['access_token']
            refresh_token = token_row['refresh_token']
            
            if platform == 'google':
                # Revoke Google tokens via API
                try:
                    print(f'🗑️ [REVOKE TOKENS] Revoking Google token via API...')
                    
                    # Revoke refresh token (this also invalidates access token)
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
                print(f'   (Using prompt=consent parameter instead)')
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
            cursor.execute('DELETE FROM oauth_tokens WHERE user_id = ?', (user_id,))
            tokens_deleted = cursor.rowcount
            print(f'   ✅ Deleted {tokens_deleted} OAuth tokens')
            
            # Delete from user_platform_credentials (if exists)
            try:
                cursor.execute('DELETE FROM user_platform_credentials WHERE user_id = ?', (user_id,))
                creds_deleted = cursor.rowcount
                print(f'   ✅ Deleted {creds_deleted} platform credentials')
            except Exception as e:
                print(f'   ⚠️ No user_platform_credentials table or error: {e}')
            
            # Delete user from users table
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            user_deleted = cursor.rowcount
            print(f'   ✅ Deleted user record ({user_deleted} row)')
            
            conn.commit()
            conn.close()
            
            print(f'✅ [COMPLETE RESET] User {user_id} completely removed from system')
            print(f'   Next OAuth login will create fresh user account')
            
            return jsonify({
                'success': True,
                'message': f'User account completely reset',
                'complete_reset': True,
                'tokens_deleted': tokens_deleted,
                'user_deleted': user_deleted,
                'provider_revoked': revocation_status['provider_revoked'],
                'next_step': f'Redirect to /api/auth/{platform}/login to re-register'
            })
        
        else:
            print(f'🔄 [NORMAL RESET] Clearing tokens but keeping user account...')
            
            # Delete tokens for specific platform only
            cursor.execute('''
                DELETE FROM oauth_tokens
                WHERE user_id = ? AND platform = ?
            ''', (user_id, platform))
            
            deleted_count = cursor.rowcount
            
            # Update user flags
            if platform == 'google':
                cursor.execute('UPDATE users SET has_google_oauth = 0 WHERE id = ?', (user_id,))
            elif platform == 'microsoft':
                cursor.execute('UPDATE users SET has_microsoft_oauth = 0 WHERE id = ?', (user_id,))
            
            conn.commit()
            conn.close()
            
            print(f'✅ [NORMAL RESET] Deleted {deleted_count} tokens for {platform}')
            
            return jsonify({
                'success': True,
                'message': f'{platform.capitalize()} tokens revoked',
                'complete_reset': False,
                'deleted_count': deleted_count,
                'provider_revoked': revocation_status['provider_revoked'],
                'revocation_error': revocation_status['error']
            })
        
    except Exception as e:
        print(f'❌ [REVOKE TOKENS] Error: {e}')
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

