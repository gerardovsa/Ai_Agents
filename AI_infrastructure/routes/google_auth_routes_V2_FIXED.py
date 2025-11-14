"""
Google OAuth 2.0 Authentication Routes - V2 FIXED VERSION
Writes to oauth_tokens table (not user_platform_credentials)
Uses correct 24-column schema
Aligned with V2 architecture and database consolidation
Clean, maintainable code

LOADS FROM .env.master FILE (not .env or environment variables)
"""

from flask import Blueprint, request, redirect, jsonify, url_for, session
import os
import secrets
import requests
import urllib.parse
from datetime import datetime, timedelta
import jwt
import json
from functools import wraps
from pathlib import Path
from dotenv import dotenv_values

google_auth_bp = Blueprint('google_auth', __name__, url_prefix='/api/auth/google')

# Load credentials from .env.master (local dev) or OS environment (Render)
_ENV_MASTER_PATH = Path(__file__).parent.parent.parent / '.env.master'
if _ENV_MASTER_PATH.exists():
    _config = dotenv_values(_ENV_MASTER_PATH)
else:
    # On Render, use OS environment variables
    _config = {}

# Google OAuth Configuration - Priority: OS env > .env.master
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID') or _config.get('GOOGLE_OAUTH_CLIENT_ID') or _config.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET') or _config.get('GOOGLE_OAUTH_CLIENT_SECRET') or _config.get('GOOGLE_CLIENT_SECRET')

# CRITICAL: Redirect URI must be set dynamically based on environment
# On Render, use HTTPS. Locally, use HTTP.
# Priority: OS env (Render) > .env.master (local) > None (will build dynamically)
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI') or _config.get('GOOGLE_REDIRECT_URI')

def _ensure_https_redirect_uri(base_uri=None, path='/api/auth/google/callback'):
    """Ensure redirect URI uses HTTPS on Render, HTTP locally"""
    if base_uri:
        return base_uri
    
    # Build from request
    from flask import request
    if request:
        base_url = request.url_root.rstrip('/')
        # Force HTTPS on Render
        if 'onrender.com' in request.host or os.getenv('RENDER') == 'true':
            base_url = base_url.replace('http://', 'https://')
        return base_url + path
    
    # Fallback for local development
    return f'http://localhost:5001{path}'

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

# ============================================================================
# DATABASE FUNCTIONS
# ============================================================================

def get_db_connection():
    """Get database connection to ai_infrastructure.db in data/ folder (CORRECT LOCATION)"""
    import sqlite3
    from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
    # CORRECT: Use centralized helper (supports Render /data mount)
    db_path = get_ai_infrastructure_db_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    print(f'🔷 [DB CONNECTION] Using: {db_path}')  # Debug log
    return conn

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
    
    # NEW: oauth_tokens table (24 columns - consolidated schema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS oauth_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            access_token TEXT NOT NULL,
            refresh_token TEXT,
            token_type TEXT DEFAULT 'Bearer',
            expires_at TIMESTAMP,
            scopes TEXT,
            is_valid INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            auto_refresh_enabled INTEGER DEFAULT 1,
            last_refreshed_at TIMESTAMP,
            error_count INTEGER DEFAULT 0,
            last_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            email TEXT,
            profile_name TEXT,
            profile_picture_url TEXT,
            profile_data TEXT,
            granted_scopes TEXT,
            auth_method TEXT DEFAULT 'oauth2',
            metadata TEXT,
            UNIQUE(user_id, platform),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
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
    print('Database tables initialized')

# Initialize database on import
init_db()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_by_email(email):
    """Get user by email (primary or alias)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, role FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email_from_user_id(user_id):
    """Get user by user_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(email, username=None):
    """Create new user from OAuth login"""
    if not username:
        username = email.split('@')[0]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, role) 
        VALUES (?, ?, ?, ?)
    ''', (username, email, 'oauth_google', 'user'))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    print(f'Created new user: {username} (ID: {user_id})')
    return user_id

def generate_jwt_token(user_data):
    """Generate JWT token for user session"""
    payload = {
        'user_id': user_data.get('id'),
        'email': user_data.get('email'),
        'username': user_data.get('username'),
        'exp': int((datetime.utcnow() + timedelta(days=7)).timestamp())  # 7-day expiry as Unix timestamp
    }
    
    secret_key = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    # Store token in user_sessions table
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        expires_at = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute('''
            INSERT INTO user_sessions (user_id, token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_data.get('id'), token, expires_at))
        
        conn.commit()
        conn.close()
        print(f'JWT token created for user {user_data.get("id")}')
    except Exception as e:
        print(f'⚠️  Could not store JWT in sessions: {e}')
    
    return token

# ============================================================================
# OAUTH ROUTES
# ============================================================================

@google_auth_bp.route('/login')
def google_login():
    """
    Initiate Google OAuth flow
    
    Flow:
    1. Check if user already has valid tokens (skip OAuth if yes)
    2. Generate CSRF state token
    3. Build Google authorization URL with all scopes
    4. Redirect user to Google consent screen
    """
    print('🔷 [GOOGLE OAUTH] Login initiated')
    print(f'   CLIENT_ID: {GOOGLE_CLIENT_ID[:20]}...')
    print(f'   REDIRECT_URI: {GOOGLE_REDIRECT_URI}')
    print(f'   SCOPES: {len(GOOGLE_SCOPES)} scopes requested')
    
    # ====================================================================
    # CHECK IF USER ALREADY HAS VALID TOKENS
    # ====================================================================
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        jwt_token = auth_header.split(' ')[1]
        secret_key = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        
        try:
            payload = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            # Check if this user has valid Google OAuth tokens
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT access_token, refresh_token, expires_at, is_valid
                FROM oauth_tokens
                WHERE user_id = ? AND platform = ? AND is_active = 1
            ''', (user_id, 'google'))
            
            token_row = cursor.fetchone()
            conn.close()
            
            if token_row and token_row['is_valid']:
                expires_at = datetime.strptime(token_row['expires_at'], '%Y-%m-%d %H:%M:%S')
                
                # If token is still valid (not expired), skip OAuth
                if datetime.utcnow() < expires_at:
                    print('✅ [GOOGLE OAUTH] User already has valid tokens - skipping OAuth')
                    frontend_url = request.url_root.rstrip('/')
                    if 'onrender.com' in request.host or os.getenv('RENDER') == 'true':
                        frontend_url = frontend_url.replace('http://', 'https://')
                    return redirect(f'{frontend_url}/?token={jwt_token}&platform=google&status=already_connected')
                
                # If token expired but we have refresh_token, auto-refresh
                if token_row['refresh_token']:
                    print('🔄 [GOOGLE OAUTH] Token expired but refresh_token available - auto-refreshing...')
                    # Auto-refresh will happen in background, continue to OAuth for now
        
        except jwt.InvalidTokenError:
            print('⚠️  [GOOGLE OAUTH] Invalid JWT - proceeding with OAuth')
    
    # ====================================================================
    # PROCEED WITH OAUTH FLOW
    # ====================================================================
    # Generate CSRF protection state
    state = secrets.token_urlsafe(32)
    session['google_oauth_state'] = state
    
    # Check if force_consent is requested (for re-authentication)
    force_consent = request.args.get('force_consent', 'false').lower() == 'true'
    prompt = 'consent' if force_consent else 'select_account'
    
    # CRITICAL: Get redirect URI dynamically based on environment
    # Priority: OS env var > .env.master > auto-detect from request
    # Use env var first, then build dynamically with HTTPS on Render
    redirect_uri = _ensure_https_redirect_uri(GOOGLE_REDIRECT_URI)
    
    print(f'🔷 [GOOGLE OAUTH] Using redirect URI: {redirect_uri}')
    
    # Build authorization URL
    params = {
        'client_id': GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(GOOGLE_SCOPES),
        'state': state,
        'access_type': 'offline',  # Request refresh token
        'prompt': prompt  # 'select_account' (default) or 'consent' (force re-consent)
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"
    print(f'🔷 [GOOGLE OAUTH] Redirecting to Google... (force_consent={force_consent}, prompt={prompt})')
    
    return redirect(auth_url)

@google_auth_bp.route('/callback')
def google_callback():
    """
    Handle Google OAuth callback
    
    Flow:
    1. Verify CSRF state
    2. Exchange authorization code for tokens
    3. Fetch user profile
    4. Create or update user in database
    5. Store tokens in oauth_tokens table (24 columns)
    6. Generate JWT session token
    7. Redirect to app with JWT
    """
    print('🔷 [GOOGLE OAUTH] Callback received')
    
    # Verify CSRF state
    state = request.args.get('state')
    stored_state = session.get('google_oauth_state')
    
    # Build frontend URL based on environment
    frontend_url = request.url_root.rstrip('/')
    if 'onrender.com' in request.host or os.getenv('RENDER') == 'true':
        frontend_url = frontend_url.replace('http://', 'https://')
    
    if not state or state != stored_state:
        print(' [GOOGLE OAUTH] Invalid state - CSRF check failed')
        return redirect(f'{frontend_url}/?error=invalid_state')
    
    # Get authorization code
    code = request.args.get('code')
    if not code:
        error = request.args.get('error', 'unknown_error')
        print(f' [GOOGLE OAUTH] No authorization code: {error}')
        return redirect(f'{frontend_url}/?error={error}')
    
    try:
        # ====================================================================
        # STEP 1: Exchange code for tokens
        # ====================================================================
        print('🔷 [GOOGLE OAUTH] Exchanging code for tokens...')
        
        # CRITICAL: Use same redirect URI as in /login route
        # Use env var first, then build dynamically with HTTPS on Render
        redirect_uri = _ensure_https_redirect_uri(GOOGLE_REDIRECT_URI)
        
        print(f'🔷 [GOOGLE OAUTH] Using redirect URI for token exchange: {redirect_uri}')
        
        token_data = {
            'code': code,
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')  # May be None if already authorized
        expires_in = tokens.get('expires_in', 3600)
        token_type = tokens.get('token_type', 'Bearer')
        granted_scopes = tokens.get('scope', ' '.join(GOOGLE_SCOPES))
        
        # Calculate expiration timestamp
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f'[GOOGLE OAUTH] Tokens received:')
        print(f'   Access Token: {access_token[:20]}...')
        print(f'   Refresh Token: {"Present" if refresh_token else "None (reauth may be needed)"}')
        print(f'   Expires In: {expires_in} seconds')
        print(f'   Expires At: {expires_at}')
        
        # ====================================================================
        # STEP 2: Fetch user profile
        # ====================================================================
        print('🔷 [GOOGLE OAUTH] Fetching user profile...')
        
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        profile_response.raise_for_status()
        profile = profile_response.json()
        
        email = profile.get('email')
        name = profile.get('name')
        picture = profile.get('picture')
        google_id = profile.get('id')
        
        print(f'[GOOGLE OAUTH] User profile fetched:')
        print(f'   Email: {email}')
        print(f'   Name: {name}')
        print(f'   Google ID: {google_id}')
        
        # ====================================================================
        # STEP 3: Create or get user
        # ====================================================================
        user = get_user_by_email(email)
        
        if user:
            user_id = user['id']
            print(f'[GOOGLE OAUTH] Existing user found: {user["username"]} (ID: {user_id})')
        else:
            user_id = create_user(email, email.split('@')[0])
            user = get_user_by_email(email)
            print(f'[GOOGLE OAUTH] New user created: {user["username"]} (ID: {user_id})')
        
        # ====================================================================
        # STEP 4: Store or update tokens in oauth_tokens table
        # ====================================================================
        print('🔷 [GOOGLE OAUTH] Storing tokens in oauth_tokens table...')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if token exists for this user+platform
        cursor.execute('SELECT id FROM oauth_tokens WHERE user_id = ? AND platform = ?', (user_id, 'google'))
        existing = cursor.fetchone()
        
        if existing:
            # UPDATE existing token
            print(f'   Updating existing token for user {user_id}')
            cursor.execute('''
                UPDATE oauth_tokens SET
                    access_token = ?,
                    refresh_token = COALESCE(?, refresh_token),
                    token_type = ?,
                    expires_at = ?,
                    scope = ?,
                    is_valid = 1,
                    is_active = 1,
                    auto_refresh_enabled = 1,
                    last_refreshed_at = ?,
                    refresh_attempts = 0,
                    last_refresh_error = NULL,
                    updated_at = CURRENT_TIMESTAMP,
                    granted_scopes = ?,
                    metadata = ?
                WHERE user_id = ? AND platform = ?
            ''', (
                access_token,
                refresh_token,
                token_type,
                expires_at,
                ' '.join(GOOGLE_SCOPES),
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                granted_scopes,
                json.dumps({
                    'google_id': google_id,
                    'email': email,
                    'name': name,
                    'picture': picture,
                    'profile': profile,
                    'authorized_at': datetime.utcnow().isoformat(),
                    'client_id': GOOGLE_CLIENT_ID[:20] + '...'
                }),
                user_id,
                'google'
            ))
        else:
            # INSERT new token
            print(f'   Creating new token for user {user_id}')
            cursor.execute('''
                INSERT INTO oauth_tokens (
                user_id,
                platform,
                access_token,
                refresh_token,
                token_type,
                expires_at,
                scope,
                is_valid,
                is_active,
                auto_refresh_enabled,
                last_refreshed_at,
                refresh_attempts,
                last_refresh_error,
                granted_scopes,
                metadata,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (
            user_id,                              # user_id
            'google',                             # platform
            access_token,                         # access_token
            refresh_token,                        # refresh_token (may be None)
            token_type,                           # token_type ('Bearer')
            expires_at,                           # expires_at (calculated timestamp)
            ' '.join(GOOGLE_SCOPES),             # scope (requested scopes)
            1,                                    # is_valid (1 = valid)
            1,                                    # is_active (1 = active)
            1,                                    # auto_refresh_enabled (1 = enabled)
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),  # last_refreshed_at
            0,                                    # refresh_attempts (0 = no errors)
            None,                                 # last_refresh_error (NULL)
            granted_scopes,                       # granted_scopes (actual scopes granted)
            json.dumps({                          # metadata (additional info)
                'google_id': google_id,
                'email': email,
                'name': name,
                'picture': picture,
                'profile': profile,
                'authorized_at': datetime.utcnow().isoformat(),
                'client_id': GOOGLE_CLIENT_ID[:20] + '...'
            })
        ))
        
        conn.commit()
        
        # Update has_google_oauth flag
        cursor.execute('''
            UPDATE users
            SET has_google_oauth = 1
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        print('[GOOGLE OAUTH] Tokens stored successfully in oauth_tokens table!')
        print(f'   Table: oauth_tokens')
        print(f'   User ID: {user_id}')
        print(f'   Platform: google')
        print(f'   Email: {email}')
        print(f'   All 24 columns populated ')
        print(f'✅ [GOOGLE OAUTH] Updated has_google_oauth flag for user {user_id}')
        
        # ====================================================================
        # STEP 5: Generate JWT session token
        # ====================================================================
        jwt_token = generate_jwt_token({
            'id': user_id,
            'username': user['username'],
            'email': email,
            'role': user['role']
        })
        
        print('[GOOGLE OAUTH] JWT session token generated')
        
        # ====================================================================
        # STEP 6: Redirect to app with JWT token
        # ====================================================================
        print('[GOOGLE OAUTH] OAuth flow complete - redirecting to app')
        
        # CRITICAL: Redirect to correct frontend URL based on environment
        frontend_url = request.url_root.rstrip('/')
        if 'onrender.com' in request.host:
            frontend_url = frontend_url.replace('http://', 'https://')
        
        return redirect(f'{frontend_url}/?token={jwt_token}&platform=google&status=connected')
        
    except requests.exceptions.HTTPError as e:
        print(f' [GOOGLE OAUTH] HTTP error: {str(e)}')
        print(f'   Response: {e.response.text if hasattr(e, "response") else "No response"}')
        
        frontend_url = request.url_root.rstrip('/')
        if 'onrender.com' in request.host:
            frontend_url = frontend_url.replace('http://', 'https://')
        
        return redirect(f'{frontend_url}/?error=http_error')
    
    except Exception as e:
        print(f' [GOOGLE OAUTH] Unexpected error: {str(e)}')
        import traceback
        traceback.print_exc()
        
        frontend_url = request.url_root.rstrip('/')
        if 'onrender.com' in request.host:
            frontend_url = frontend_url.replace('http://', 'https://')
        
        return redirect(f'{frontend_url}/?error=oauth_failed')

@google_auth_bp.route('/status')
def google_status():
    """
    Check Google OAuth connection status for current user
    
    Returns:
    {
        "connected": true/false,
        "email": "user@example.com",
        "profile_name": "User Name",
        "expires_at": "2025-10-31 12:00:00",
        "is_valid": true/false,
        "last_refreshed_at": "2025-10-30 10:00:00"
    }
    """
    try:
        # Get user ID from JWT token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'connected': False, 'error': 'No auth token'}), 401
        
        jwt_token = auth_header.split(' ')[1]
        secret_key = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
        
        try:
            payload = jwt.decode(jwt_token, secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'connected': False, 'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'connected': False, 'error': 'Invalid token'}), 401
        
        # Query oauth_tokens table
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                email,
                profile_name,
                profile_picture_url,
                expires_at,
                is_valid,
                is_active,
                last_refreshed_at,
                error_count,
                last_error
            FROM oauth_tokens
            WHERE user_id = ? AND platform = ?
        ''', (user_id, 'google'))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({'connected': False})
        
        return jsonify({
            'connected': True,
            'email': result['email'],
            'profile_name': result['profile_name'],
            'profile_picture_url': result['profile_picture_url'],
            'expires_at': result['expires_at'],
            'is_valid': bool(result['is_valid']),
            'is_active': bool(result['is_active']),
            'last_refreshed_at': result['last_refreshed_at'],
            'error_count': result['error_count'],
            'last_error': result['last_error']
        })
        
    except Exception as e:
        print(f' Error checking Google status: {str(e)}')
        return jsonify({'connected': False, 'error': str(e)}), 500

@google_auth_bp.route('/refresh', methods=['POST'])
def refresh_google_token():
    """
    Refresh expired Google access token using refresh token
    
    Request body:
    {
        "user_id": 1
    }
    
    Returns:
    {
        "success": true,
        "access_token": "ya29...",
        "expires_at": "2025-10-31 12:00:00"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Get refresh token from oauth_tokens table
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT refresh_token, email 
            FROM oauth_tokens 
            WHERE user_id = ? AND platform = ?
        ''', (user_id, 'google'))
        
        result = cursor.fetchone()
        
        if not result:
            return jsonify({'error': 'No Google credentials found'}), 404
        
        refresh_token = result['refresh_token']
        
        if not refresh_token:
            return jsonify({'error': 'No refresh token available - user must reauthorize'}), 400
        
        # Request new access token from Google
        token_data = {
            'client_id': GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token'
        }
        
        print(f'🔷 [GOOGLE OAUTH] Refreshing token for user {user_id}...')
        response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        new_access_token = tokens.get('access_token')
        expires_in = tokens.get('expires_in', 3600)
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Update oauth_tokens table
        cursor.execute('''
            UPDATE oauth_tokens 
            SET 
                access_token = ?,
                expires_at = ?,
                last_refreshed_at = CURRENT_TIMESTAMP,
                is_valid = 1,
                error_count = 0,
                last_error = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND platform = ?
        ''', (new_access_token, expires_at, user_id, 'google'))
        
        conn.commit()
        conn.close()
        
        print(f'[GOOGLE OAUTH] Token refreshed for user {user_id}')
        print(f'   New expires_at: {expires_at}')
        
        return jsonify({
            'success': True,
            'access_token': new_access_token,
            'expires_at': expires_at,
            'expires_in': expires_in
        })
        
    except requests.exceptions.HTTPError as e:
        print(f' [GOOGLE OAUTH] Refresh failed: {str(e)}')
        
        # Mark token as invalid in database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE oauth_tokens 
                SET 
                    is_valid = 0,
                    error_count = error_count + 1,
                    last_error = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND platform = ?
            ''', (str(e), user_id, 'google'))
            conn.commit()
            conn.close()
        except:
            pass
        
        return jsonify({'error': 'Token refresh failed', 'details': str(e)}), 500
    
    except Exception as e:
        print(f' [GOOGLE OAUTH] Unexpected error during refresh: {str(e)}')
        return jsonify({'error': str(e)}), 500

@google_auth_bp.route('/disconnect', methods=['POST'])
def disconnect_google():
    """
    Disconnect Google account (revoke tokens and delete from database)
    
    Request body:
    {
        "user_id": 1
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400
        
        # Get access token to revoke
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT access_token 
            FROM oauth_tokens 
            WHERE user_id = ? AND platform = ?
        ''', (user_id, 'google'))
        
        result = cursor.fetchone()
        
        if result and result['access_token']:
            # Revoke token with Google
            try:
                revoke_url = f"https://oauth2.googleapis.com/revoke?token={result['access_token']}"
                requests.post(revoke_url)
                print(f'[GOOGLE OAUTH] Token revoked with Google')
            except:
                print(f'⚠️  [GOOGLE OAUTH] Could not revoke token with Google (may be expired)')
        
        # Delete from database
        cursor.execute('DELETE FROM oauth_tokens WHERE user_id = ? AND platform = ?', (user_id, 'google'))
        conn.commit()
        conn.close()
        
        print(f'[GOOGLE OAUTH] Credentials deleted for user {user_id}')
        
        return jsonify({'success': True, 'message': 'Google account disconnected'})
        
    except Exception as e:
        print(f' [GOOGLE OAUTH] Error disconnecting: {str(e)}')
        return jsonify({'error': str(e)}), 500

@google_auth_bp.route('/config')
def google_config():
    """
    Public endpoint - check if Google OAuth is configured
    
    Returns:
    {
        "configured": true,
        "client_id": "123456...xyz",
        "redirect_uri": os.getenv('GOOGLE_REDIRECT_URI') or "http://localhost:5001/api/auth/google/callback",
        "scopes": ["openid", "email", ...]
    }
    """
    is_configured = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
    
    return jsonify({
        'configured': is_configured,
        'client_id': GOOGLE_CLIENT_ID[:20] + '...' if GOOGLE_CLIENT_ID else None,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'scopes': GOOGLE_SCOPES,
        'scope_count': len(GOOGLE_SCOPES)
    })

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

print('Google OAuth routes loaded (V2 Fixed Version)')
print(f'   - Writes to: oauth_tokens table (24 columns)')
print(f'   - Client ID: {GOOGLE_CLIENT_ID[:20]}...' if GOOGLE_CLIENT_ID else '   - Client ID: NOT SET')
print(f'   - Redirect URI: {GOOGLE_REDIRECT_URI}')
print(f'   - Scopes: {len(GOOGLE_SCOPES)} requested')
