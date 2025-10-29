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
        role = data.get('role', 'user')  # ✅ NEW: Support admin role
        
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
            role=role  # ✅ Pass role
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
        print(f"❌ Gmail link error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@auth_bp.route('/gmail-accounts', methods=['GET'])
@require_auth
def get_gmail_accounts():
    """
    Get all Gmail accounts linked to user
    
    GET /api/auth/gmail-accounts
    Headers: Authorization: Bearer <token>
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
    """
    try:
        user_id = request.user['user_id']
        
        # Get Gmail accounts
        gmail_accounts = user_auth_manager.get_user_gmail_accounts(user_id)
        
        # Get workspace
        workspace_id = user_auth_manager.get_user_workspace(user_id)
        
        # Determine authentication platform based on password_hash
        import sqlite3
        import os
        
        # Use absolute path to database
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, 'ai_infrastructure.db')
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
        user_row = cursor.fetchone()
        
        auth_platform = None
        if user_row and user_row['password_hash']:
            if user_row['password_hash'] == 'oauth_google':
                auth_platform = 'google'
            elif user_row['password_hash'] == 'oauth_microsoft':
                auth_platform = 'microsoft'
        
        # ✅ Check if user has active OAuth tokens in user_platform_credentials
        google_oauth_connected = False
        microsoft_oauth_connected = False
        
        if auth_platform == 'google':
            # Check for Google OAuth tokens (access_token)
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM user_platform_credentials 
                WHERE user_id = ? 
                AND platform = 'google' 
                AND credential_key = 'access_token'
                AND is_active = 1
            ''', (user_id,))
            result = cursor.fetchone()
            google_oauth_connected = result['count'] > 0 if result else False
            
        elif auth_platform == 'microsoft':
            # Check for Microsoft OAuth tokens (access_token)
            # ✅ Check for both 'microsoft' and 'microsoft365' for backwards compatibility
            cursor.execute('''
                SELECT COUNT(*) as count 
                FROM user_platform_credentials 
                WHERE user_id = ? 
                AND (platform = 'microsoft' OR platform = 'microsoft365')
                AND credential_key = 'access_token'
                AND is_active = 1
            ''', (user_id,))
            result = cursor.fetchone()
            microsoft_oauth_connected = result['count'] > 0 if result else False
        
        conn.close()
        
        return jsonify({
            'success': True,
            'profile': {
                **request.user,
                'gmail_accounts': gmail_accounts,
                'workspace_id': workspace_id,
                'auth_platform': auth_platform,  # 'google' | 'microsoft' | None
                'google_oauth_connected': google_oauth_connected,  # ✅ NEW: Token status
                'microsoft_oauth_connected': microsoft_oauth_connected  # ✅ NEW: Token status
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
        print(f"❌ Check credentials error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
