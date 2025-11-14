"""
Microsoft 365 Authentication Routes (V2 FIXED)
==============================================

FIXED VERSION - Writes to oauth_tokens table with correct schema

CRITICAL CHANGES FROM OLD VERSION:
-  OLD: INSERT INTO user_platform_credentials (credential_type, credential_key, credential_value)
- NEW: INSERT INTO oauth_tokens (access_token, refresh_token, expires_at, email, etc.)

This fixes the OAuth storage problem where credentials were stored in the wrong table
with the wrong schema, preventing tools from finding them.

LOADS FROM .env.master FILE (not .env or environment variables)
"""

from flask import Blueprint, request, jsonify, redirect, url_for, session
from auth.user_auth import user_auth_manager, require_auth

# Add root to path for Microsoft_365_Connection
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Microsoft_365_Connection.microsoft365_oauth_manager import (
    microsoft_oauth_manager,
    get_microsoft_auth_url,
    authenticate_user_with_microsoft
)
import secrets
import logging
import sqlite3
from datetime import datetime, timedelta
import jwt as pyjwt
import json
sys.path.append('C:/Users/gpoli/GIT/AI_agents/AI_infrastructure')
from utils.email_alias_helpers import get_user_id_by_email, add_email_alias
from pathlib import Path
from dotenv import dotenv_values

logger = logging.getLogger(__name__)

microsoft_auth_bp = Blueprint('microsoft_auth', __name__, url_prefix='/api/auth/microsoft')

# Load credentials from .env.master (local dev) or OS environment (Render)
_ENV_MASTER_PATH = Path(__file__).parent.parent.parent / '.env.master'
if _ENV_MASTER_PATH.exists():
    _config = dotenv_values(_ENV_MASTER_PATH)
else:
    # On Render, use OS environment variables
    _config = {}

# Microsoft Graph API scopes - MATCH AZURE APP REGISTRATION (12 scopes granted)
# Updated November 5, 2025 to match actual Azure portal configuration
MICROSOFT_SCOPES = [
    # Authentication & Profile (auto-included by Microsoft)
    'offline_access',              # ✅ Refresh tokens
    
    # User
    'User.Read',                   # ✅ Sign in and read user profile
    'User.ReadWrite',              # ✅ Read and write user profile
    
    # Mail (Outlook)
    'Mail.ReadWrite',              # ✅ Read and write mail (includes Mail.Read)
    'Mail.Send',                   # ✅ Send mail as a user (Delegated)
    'MailboxFolder.Read',          # ✅ Read mailbox folders
    
    # Calendar
    'Calendars.ReadWrite',         # ✅ Read and write calendars (includes Calendars.Read)
    
    # Files (OneDrive, Word, Excel)
    'Files.ReadWrite.All',         # ✅ Full file access (includes Files.Read, Files.Read.All, Files.ReadWrite)
    
    # Tasks (To Do)
    'Tasks.ReadWrite',             # ✅ Read and write tasks
    
    # Teams
    'Team.ReadBasic.All',          # ✅ Read basic team info
    'ChannelMessage.Send'          # ✅ Send channel messages
]

# NOTE: Mail.Send (Application permission) is configured separately in Azure Portal
# and does NOT need to be in this delegated scopes list

# ======================================================================
# DATABASE HELPER FUNCTIONS
# ======================================================================

def get_db_connection():
    """Get SQLite database connection to data/ai_infrastructure.db (CORRECT LOCATION)"""
    from pathlib import Path
    # CORRECT: Use data/ai_infrastructure.db (not AI_infrastructure/ai_infrastructure.db)
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    logger.info(f'🔷 [DB CONNECTION] Using: {db_path}')  # Debug log
    return conn

def init_db():
    """Initialize database with oauth_tokens table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create oauth_tokens table with 24 columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS oauth_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                platform TEXT NOT NULL,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                token_type TEXT DEFAULT 'Bearer',
                expires_at TIMESTAMP,
                scope TEXT,
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
        
        conn.commit()
        conn.close()
        logger.info("Database tables initialized (oauth_tokens)")
    except Exception as e:
        logger.error(f" Error initializing database: {e}")

def get_user_by_email(email: str):
    """Get user by email from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f" Error getting user by email: {e}")
        return None

def get_user_by_id(user_id: int):
    """Get user by ID from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f" Error getting user by ID: {e}")
        return None

def create_user(email: str, username: str, role: str = 'user'):
    """Create new user in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, 'oauth_microsoft', role, datetime.now().isoformat()))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"Created new user: {email} (ID: {user_id})")
        return get_user_by_email(email)
    except Exception as e:
        logger.error(f" Error creating user: {e}")
        return None

def generate_jwt_token(payload: dict):
    """Generate JWT token for user session"""
    try:
        jwt_secret = _config.get('JWT_SECRET', 'your-secret-key-change-this')
        
        # Calculate expiration as Unix timestamp (integer)
        exp_time = datetime.utcnow() + timedelta(hours=24)
        exp_timestamp = int(exp_time.timestamp())
        
        token_payload = {
            'user_id': payload.get('user_id'),
            'email': payload.get('email'),
            'exp': exp_timestamp
        }
        
        token = pyjwt.encode(token_payload, jwt_secret, algorithm='HS256')
        
        # Store token in user_sessions table
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            expires_at = (datetime.utcnow() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (payload['user_id'], token, expires_at))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"⚠️ Could not store token in sessions: {e}")
        
        return token
    except Exception as e:
        logger.error(f" Error creating JWT token: {e}")
        return None

# Initialize database on module load
init_db()

# ======================================================================
# OAUTH ENDPOINTS
# ======================================================================

@microsoft_auth_bp.route('/login', methods=['GET'])
def microsoft_login():
    """
    Initiate Microsoft 365 OAuth login
    
    GET /api/auth/microsoft/login?force_consent=true
    
    Query Parameters:
        force_consent: If 'true', forces consent screen to reappear (for re-authentication)
    
    Redirects user to Microsoft login page
    """
    try:
        # Check if Microsoft credentials are configured
        if not microsoft_oauth_manager.client_id or not microsoft_oauth_manager.client_secret:
            logger.warning("⚠️ Microsoft 365 credentials not configured")
            return jsonify({
                'success': False,
                'error': 'Microsoft 365 login not configured',
                'setup_required': True
            }), 400
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        session['microsoft_oauth_state'] = state
        
        # Get redirect URI from environment variable (CRITICAL: Use HTTPS for Render)
        # request.url_root returns http:// on Render (internal), but Azure needs https://
        # Priority: OS env var > .env.master > fallback (never use fallback on Render!)
        redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI') or _config.get('MICROSOFT_REDIRECT_URI')
        if not redirect_uri:
            # Fallback: build from request, but force HTTPS if on Render
            base_url = request.url_root.rstrip('/')
            if 'onrender.com' in request.host:
                base_url = base_url.replace('http://', 'https://')
            redirect_uri = base_url + '/api/auth/microsoft/callback'
        
        # Store original redirect for after login
        return_url = request.args.get('return_url', '/')
        session['microsoft_return_url'] = return_url
        
        # Check if force_consent is requested (for re-authentication)
        force_consent = request.args.get('force_consent', 'false').lower() == 'true'
        prompt = 'consent' if force_consent else 'select_account'
        
        # Get Microsoft authorization URL with ALL scopes defined above
        auth_url = get_microsoft_auth_url(
            redirect_uri=redirect_uri, 
            state=state, 
            prompt=prompt,
            scopes=MICROSOFT_SCOPES  # ✅ PASS THE SCOPES HERE!
        )
        
        logger.info(f"🔷 Initiating Microsoft login (force_consent={force_consent}, prompt={prompt})")
        logger.info(f"   Redirect URI: {redirect_uri}")
        client_id_display = (os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID', ''))[:20]
        tenant_display = os.getenv('MICROSOFT_TENANT_ID') or _config.get('MICROSOFT_TENANT_ID', 'common')
        logger.info(f"   Client ID: {client_id_display}...")
        logger.info(f"   Tenant: {tenant_display}")
        
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f" Microsoft login failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@microsoft_auth_bp.route('/callback', methods=['GET'])
def microsoft_callback():
    """
    Microsoft OAuth callback endpoint (FIXED VERSION)
    
    GET /api/auth/microsoft/callback?code=...&state=...
    
    NOW WRITES TO: oauth_tokens table with 24 columns
     OLD VERSION: user_platform_credentials table with nested key-value
    """
    try:
        # ====================================================================
        # STEP 1: Verify state for CSRF protection
        # ====================================================================
        state = request.args.get('state')
        stored_state = session.get('microsoft_oauth_state')
        
        if not state or state != stored_state:
            logger.error(" Invalid OAuth state (CSRF protection)")
            return jsonify({
                'success': False,
                'error': 'Invalid state parameter'
            }), 400
        
        # ====================================================================
        # STEP 2: Get authorization code
        # ====================================================================
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            logger.error(f" Microsoft OAuth error: {error}")
            return jsonify({
                'success': False,
                'error': f'Microsoft authorization failed: {error}'
            }), 400
        
        if not code:
            logger.error(" No authorization code received")
            return jsonify({
                'success': False,
                'error': 'No authorization code received'
            }), 400
        
        # ====================================================================
        # STEP 3: Exchange code for tokens
        # ====================================================================
        # Get redirect URI from environment variable (CRITICAL: Use HTTPS for Render)
        redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI') or _config.get('MICROSOFT_REDIRECT_URI')
        if not redirect_uri:
            base_url = request.url_root.rstrip('/')
            if 'onrender.com' in request.host:
                base_url = base_url.replace('http://', 'https://')
            redirect_uri = base_url + '/api/auth/microsoft/callback'
        auth_result = authenticate_user_with_microsoft(code, redirect_uri)
        
        if not auth_result['success']:
            logger.error(f" Authentication failed: {auth_result.get('error')}")
            return jsonify(auth_result), 400
        
        profile = auth_result['profile']
        tokens = auth_result['tokens']
        
        # Extract token information
        access_token = tokens['access_token']
        refresh_token = tokens.get('refresh_token', '')
        token_type = tokens.get('token_type', 'Bearer')
        expires_in = tokens.get('expires_in', 3600)
        
        # Calculate expiration timestamp
        expires_at = (datetime.utcnow() + timedelta(seconds=expires_in)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract profile information
        email = profile.get('email', profile.get('userPrincipalName', ''))
        display_name = profile.get('display_name', profile.get('displayName', ''))
        microsoft_id = profile.get('id', '')
        
        logger.info(f"Microsoft authentication successful: {email}")
        
        # ====================================================================
        # STEP 4: Get or create user
        # ====================================================================
        user_id = get_user_id_by_email(email)
        
        if user_id:
            # Existing user
            user = get_user_by_id(user_id)
            logger.info(f"Existing user found: {user['username']} (ID: {user_id})")
        else:
            # New user - auto-register
            logger.info(f"🆕 New user - auto-registering: {email}")
            username = email.split('@')[0]
            user = create_user(email=email, username=username, role='user')
            
            if not user:
                logger.error(" User registration failed")
                return jsonify({'success': False, 'error': 'Failed to create user'}), 500
            
            user_id = user['id']
            logger.info(f"User created: {user['username']} (ID: {user_id})")
        
        # ====================================================================
        # STEP 5: Store tokens in oauth_tokens table (THE FIX!)
        # ====================================================================
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build granted scopes string
        granted_scopes = ' '.join(MICROSOFT_SCOPES)
        
        # INSERT INTO oauth_tokens (match Google's schema - stores profile in metadata JSON)
        cursor.execute('''
            INSERT OR REPLACE INTO oauth_tokens (
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
                email,
                profile_name,
                error_count,
                last_error,
                created_at,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (
            user_id,                              # user_id
            'microsoft',                          # platform (use 'microsoft' not 'microsoft365')
            access_token,                         # access_token
            refresh_token,                        # refresh_token
            token_type,                           # token_type ('Bearer')
            expires_at,                           # expires_at (timestamp)
            ' '.join(MICROSOFT_SCOPES),          # scope (requested scopes)
            1,                                    # is_valid (1 = valid)
            1,                                    # is_active (1 = active)
            1,                                    # auto_refresh_enabled (1 = enabled)
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),  # last_refreshed_at
            0,                                    # refresh_attempts (0 = no errors)
            None,                                 # last_refresh_error (NULL)
            granted_scopes,                       # granted_scopes (actual scopes)
            json.dumps({                          # metadata (stores profile like Google does)
                'microsoft_id': microsoft_id,
                'email': email,
                'name': display_name,
                'profile': profile,
                'authorized_at': datetime.utcnow().isoformat(),
                'client_id': (os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID', ''))[:20] + '...',
                'tenant_id': os.getenv('MICROSOFT_TENANT_ID') or _config.get('MICROSOFT_TENANT_ID', 'common')
            }),
            email,                                # email (NEW - direct column for status endpoint)
            display_name,                         # profile_name (NEW - direct column for UI display)
            0,                                    # error_count (NEW - initialize to 0)
            None                                  # last_error (NEW - no errors on initial auth)
        ))
        
        conn.commit()
        
        # Update has_microsoft_oauth flag
        cursor.execute('''
            UPDATE users
            SET has_microsoft_oauth = 1
            WHERE id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        print('[MICROSOFT OAUTH] Tokens stored successfully in oauth_tokens table!')
        print(f'   Table: oauth_tokens')
        print(f'   User ID: {user_id}')
        print(f'   Platform: microsoft')
        print(f'   Email: {email}')
        print(f'   All 24 columns populated ')
        print(f'✅ [MICROSOFT OAUTH] Updated has_microsoft_oauth flag for user {user_id}')
        
        # ====================================================================
        # STEP 6: Generate JWT session token
        # ====================================================================
        jwt_token = generate_jwt_token({
            'user_id': user_id,
            'email': email
        })
        
        if not jwt_token:
            logger.error(" Failed to create JWT token")
            return jsonify({'success': False, 'error': 'Failed to create session'}), 500
        
        # ====================================================================
        # STEP 7: Redirect to frontend with token
        # ====================================================================
        return_url = session.get('microsoft_return_url', '/')
        logger.info(f"Redirecting to: {return_url}")
        
        # CRITICAL: Redirect to correct frontend URL based on environment
        frontend_url = request.url_root.rstrip('/')
        if 'onrender.com' in request.host:
            frontend_url = frontend_url.replace('http://', 'https://')
        
        return redirect(f"{frontend_url}{return_url}?token={jwt_token}")
        
    except Exception as e:
        logger.error(f" Microsoft callback failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/status', methods=['GET'])
@require_auth
def microsoft_status():
    """
    Check Microsoft connection status
    
    GET /api/auth/microsoft/status
    Authorization: Bearer <jwt_token>
    
    Returns connection status and token info from oauth_tokens table
    """
    try:
        # Get user_id from request.user (set by @require_auth decorator)
        user_id = request.user.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Query oauth_tokens table
        cursor.execute('''
            SELECT 
                access_token, refresh_token, expires_at, is_valid, is_active,
                email, profile_name, last_refreshed_at, error_count, last_error,
                created_at, updated_at
            FROM oauth_tokens
            WHERE user_id = ? AND platform = ?
        ''', (user_id, 'microsoft'))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return jsonify({
                'success': True,
                'connected': False,
                'message': 'No Microsoft account connected'
            })
        
        # Check if token is expired
        expires_at = datetime.strptime(row['expires_at'], '%Y-%m-%d %H:%M:%S') if row['expires_at'] else None
        is_expired = expires_at and datetime.utcnow() > expires_at
        
        return jsonify({
            'success': True,
            'connected': True,
            'email': row['email'],
            'profile_name': row['profile_name'],
            'is_valid': bool(row['is_valid']),
            'is_active': bool(row['is_active']),
            'expires_at': row['expires_at'],
            'is_expired': is_expired,
            'last_refreshed_at': row['last_refreshed_at'],
            'error_count': row['error_count'],
            'last_error': row['last_error'],
            'connected_since': row['created_at'],
            'last_updated': row['updated_at']
        })
        
    except Exception as e:
        logger.error(f" Status check failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/disconnect', methods=['POST'])
@require_auth
def microsoft_disconnect():
    """
    Disconnect Microsoft account
    
    POST /api/auth/microsoft/disconnect
    Authorization: Bearer <jwt_token>
    
    Revokes tokens and deletes from oauth_tokens table
    """
    try:
        # Get user_id from request.user (set by @require_auth decorator)
        user_id = request.user.get('user_id')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete tokens from oauth_tokens table
        cursor.execute('''
            DELETE FROM oauth_tokens
            WHERE user_id = ? AND platform = ?
        ''', (user_id, 'microsoft'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Microsoft account disconnected for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Microsoft account disconnected'
        })
        
    except Exception as e:
        logger.error(f" Disconnect failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/config', methods=['GET'])
def get_microsoft_config():
    """
    Get Microsoft OAuth configuration for diagnostics
    
    GET /api/auth/microsoft/config
    
    Returns configuration status and expected redirect URIs
    """
    client_id = _config.get('MICROSOFT_CLIENT_ID', '')
    client_secret = _config.get('MICROSOFT_CLIENT_SECRET', '')
    tenant_id = _config.get('MICROSOFT_TENANT_ID', 'common')
    
    # Get redirect URI from environment variable (CRITICAL: Use HTTPS for Render)
    redirect_uri = os.getenv('MICROSOFT_REDIRECT_URI') or _config.get('MICROSOFT_REDIRECT_URI')
    if not redirect_uri:
        base_url = request.url_root.rstrip('/')
        if 'onrender.com' in request.host:
            base_url = base_url.replace('http://', 'https://')
        redirect_uri = base_url + '/api/auth/microsoft/callback'
    
    return jsonify({
        'success': True,
        'configured': bool(client_id and client_secret),
        'client_id': client_id[:20] + '...' if client_id else 'NOT SET',
        'client_secret': 'SET' if client_secret else 'NOT SET',
        'tenant_id': tenant_id,
        'redirect_uri': redirect_uri,
        'scopes_requested': MICROSOFT_SCOPES,
        'table_used': 'oauth_tokens',
        'columns': 24,
        'version': 'V2_FIXED'
    })


# ======================================================================
# STARTUP LOGGING
# ======================================================================
logger.info("="*80)
logger.info("Microsoft OAuth routes loaded (V2 Fixed Version)")
logger.info("   - Writes to: oauth_tokens table (24 columns)")
client_id_check = os.getenv('MICROSOFT_CLIENT_ID') or _config.get('MICROSOFT_CLIENT_ID', 'NOT SET')
redirect_uri_check = os.getenv('MICROSOFT_REDIRECT_URI') or _config.get('MICROSOFT_REDIRECT_URI', 'http://localhost:5001/api/auth/microsoft/callback')
tenant_check = os.getenv('MICROSOFT_TENANT_ID') or _config.get('MICROSOFT_TENANT_ID', 'common')
logger.info(f"   - Client ID: {client_id_check[:20]}...")
logger.info(f"   - Redirect URI: {redirect_uri_check}")
logger.info(f"   - Scopes: {len(MICROSOFT_SCOPES)} requested")
logger.info(f"   - Tenant: {tenant_check}")
logger.info("="*80)
