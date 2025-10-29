"""
Google OAuth 2.0 Authentication Routes
Handles Google Workspace login and account linking
"""

from flask import Blueprint, request, redirect, jsonify, url_for, session
import os
import secrets
import requests
import urllib.parse
from datetime import datetime, timedelta
import jwt
from functools import wraps

google_auth_bp = Blueprint('google_auth', __name__, url_prefix='/api/auth/google')

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:5001/api/auth/google/callback')

# Google OAuth Endpoints
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v2/userinfo'

# Scopes for Google Workspace (FULL READ/WRITE PERMISSIONS)
GOOGLE_SCOPES = [
    'openid',
    'email',
    'profile',
    # Gmail - full access
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    # Drive - full access
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file',
    # Calendar - full access
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    # Sheets - full access
    'https://www.googleapis.com/auth/spreadsheets',
    # Docs - full access
    'https://www.googleapis.com/auth/documents',
    # Forms - create and read
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    # Tasks
    'https://www.googleapis.com/auth/tasks'
]

def get_db_connection():
    """Get database connection"""
    import sqlite3
    # Use the main ai_infrastructure.db database (same as auth system)
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai_infrastructure.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_id_by_email(email):
    """Get user ID by email (primary or alias)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user['id'] if user else None

def init_db():
    """Initialize database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Platform credentials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_platform_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            access_token TEXT,
            refresh_token TEXT,
            token_expiry TIMESTAMP,
            profile_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # User sessions table (for JWT token validation)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on import
init_db()

def generate_jwt_token(user_data):
    """Generate JWT token for user session"""
    payload = {
        'user_id': user_data.get('id'),
        'email': user_data.get('email'),
        'username': user_data.get('username'),
        'exp': datetime.utcnow() + timedelta(days=1)
    }
    secret_key = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    # Store token in user_sessions table for validation
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        expires_at = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO user_sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_data.get('id'), token, expires_at))
        conn.commit()
        conn.close()
        print(f'✅ Stored JWT token in user_sessions')
    except Exception as e:
        print(f'⚠️ Warning: Could not store token in sessions: {e}')
    
    return token

@google_auth_bp.route('/login')
def google_login():
    """Initiate Google OAuth flow"""
    print('🔷 Google OAuth login initiated')
    # Debug: print environment values used for OAuth
    print('DEBUG: GOOGLE_CLIENT_ID=', GOOGLE_CLIENT_ID)
    print('DEBUG: GOOGLE_CLIENT_SECRET set?=', bool(GOOGLE_CLIENT_SECRET))
    print('DEBUG: GOOGLE_REDIRECT_URI=', GOOGLE_REDIRECT_URI)
    
    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    session['google_oauth_state'] = state
    
    # Build authorization URL
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope': ' '.join(GOOGLE_SCOPES),
        'state': state,
        'access_type': 'offline',  # Get refresh token
        'prompt': 'consent'  # Force consent to get refresh token
    }
    
    # Safely build encoded query string
    query = urllib.parse.urlencode(params)
    auth_url = f"{GOOGLE_AUTH_URL}?{query}"

    print(f'🔷 Redirecting to: {auth_url}')
    return redirect(auth_url)

@google_auth_bp.route('/callback')
def google_callback():
    """Handle Google OAuth callback"""
    print('🔷 Google OAuth callback received')
    # Debug: log incoming request info (helps identify redirect mismatch)
    try:
        print('DEBUG: request.url =', request.url)
        print('DEBUG: request.base_url =', request.base_url)
        print('DEBUG: request.args =', dict(request.args))
    except Exception as _:
        # If logging fails for some reason, continue
        pass
    
    # Verify state to prevent CSRF
    state = request.args.get('state')
    stored_state = session.get('google_oauth_state')
    
    if not state or state != stored_state:
        print('❌ Invalid state parameter')
        return redirect('/business-ai-platform-v2.html?error=invalid_state')
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        error = request.args.get('error', 'unknown_error')
        print(f'❌ OAuth error: {error}')
        return redirect(f'http://localhost:5001/?error={error}')
    
    try:
        # Exchange code for tokens
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': GOOGLE_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        print('🔷 Exchanging code for tokens...')
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')  # May be None if already authorized
        expires_in = tokens.get('expires_in', 3600)
        
        # Get user profile
        print('🔷 Fetching user profile...')
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        profile_response.raise_for_status()
        profile = profile_response.json()
        
        email = profile.get('email')
        name = profile.get('name')
        google_id = profile.get('id')
        
        print(f'✅ Google user authenticated: {email}')
        
        # Store or update user in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists (primary email OR alias)
        user_id = get_user_id_by_email(email)
        
        if user_id:
            # Existing user (found via primary or alias)
            cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            username = user['username']
            role = user['role']
            print(f'✅ Existing user found: {username} (ID: {user_id})')
            
            # If this email is not their primary, it's an alias - ensure it's recorded
            if user['email'] != email:
                print(f'📧 Logging in via alias: {email}')
        else:
            # Auto-register new user from Google
            username = email.split('@')[0]  # Use email prefix as username
            print(f'🆕 Auto-registering new user: {username}')
            
            # OAuth users don't have passwords - use placeholder
            cursor.execute(
                'INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)',
                (username, email, 'oauth_google', 'user')
            )
            user_id = cursor.lastrowid
            role = 'user'
            print(f'✅ New user created with ID: {user_id}')
        
        # Store Google credentials using correct schema
        import json
        
        # Store access token
        cursor.execute('''
            INSERT OR REPLACE INTO user_platform_credentials 
            (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, 'google', 'oauth', 'access_token', access_token, 1, json.dumps({
            'expires_in': expires_in,
            'profile': profile,
            'created_at': datetime.utcnow().isoformat()
        })))
        
        # Store refresh token if available
        if refresh_token:
            cursor.execute('''
                INSERT OR REPLACE INTO user_platform_credentials 
                (user_id, platform, credential_type, credential_key, credential_value, is_active, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, 'google', 'oauth', 'refresh_token', refresh_token, 1))
        
        print('✅ Stored Google credentials')
        
        conn.commit()
        conn.close()
        
        # Generate JWT token for session
        jwt_token = generate_jwt_token({
            'id': user_id,
            'username': username or email,
            'email': email,
            'role': role
        })
        
        # Redirect to main app with token
        print(f'✅ Login successful, redirecting with JWT token')
        return redirect(f'http://localhost:5001/?token={jwt_token}')
        
    except Exception as e:
        print(f'❌ Error during Google OAuth: {str(e)}')
        import traceback
        traceback.print_exc()
        return redirect(f'http://localhost:5001/?error=oauth_failed')

@google_auth_bp.route('/link', methods=['POST'])
def link_google_account():
    """Link Google account to existing user (for already logged-in users)"""
    # This would be used if a user is already logged in and wants to link their Google account
    # Similar to the login flow but links to existing session
    return jsonify({'error': 'Not implemented yet'}), 501

@google_auth_bp.route('/status')
def google_status():
    """Check Google OAuth connection status for current user"""
    # Would check if user has valid Google credentials
    return jsonify({'error': 'Not implemented yet'}), 501

@google_auth_bp.route('/config')
def google_config():
    """Public endpoint to check if Google OAuth is configured"""
    is_configured = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    return jsonify({
        'configured': is_configured,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scopes': GOOGLE_SCOPES
    })

@google_auth_bp.route('/refresh', methods=['POST'])
def refresh_google_token():
    """Refresh expired Google access token"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT refresh_token FROM user_platform_credentials 
            WHERE user_id = ? AND platform = ?
        ''', (user_id, 'google'))
        
        result = cursor.fetchone()
        if not result or not result[0]:
            return jsonify({'error': 'No refresh token found'}), 404
        
        refresh_token = result[0]
        
        # Request new access token
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        new_access_token = tokens.get('access_token')
        expires_in = tokens.get('expires_in', 3600)
        token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Update database
        cursor.execute('''
            UPDATE user_platform_credentials 
            SET access_token = ?, token_expiry = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND platform = ?
        ''', (new_access_token, token_expiry, user_id, 'google'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'access_token': new_access_token,
            'expires_in': expires_in
        })
        
    except Exception as e:
        print(f'❌ Error refreshing Google token: {str(e)}')
        return jsonify({'error': str(e)}), 500
