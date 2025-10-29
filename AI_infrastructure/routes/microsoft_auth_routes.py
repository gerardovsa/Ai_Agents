"""
Microsoft 365 Authentication Routes
===================================

User login with Microsoft 365 accounts
"""

from flask import Blueprint, request, jsonify, redirect, url_for, session
from auth.user_auth import user_auth_manager
from Microsoft_365_Connection.microsoft365_oauth_manager import (
    microsoft_oauth_manager,
    get_microsoft_auth_url,
    authenticate_user_with_microsoft
)
import secrets
import logging
import sqlite3
import os
from datetime import datetime, timedelta
import jwt as pyjwt
import sys
sys.path.append('C:/Users/gpoli/GIT/AI_agents/AI_infrastructure')
from utils.email_alias_helpers import get_user_id_by_email, add_email_alias

logger = logging.getLogger(__name__)

microsoft_auth_bp = Blueprint('microsoft_auth', __name__, url_prefix='/api/auth/microsoft')

# ======================================================================
# CONFIGURATION & DIAGNOSTICS
# ======================================================================

@microsoft_auth_bp.route('/config', methods=['GET'])
def get_microsoft_config():
    """
    Get Microsoft OAuth configuration for diagnostics
    
    GET /api/auth/microsoft/config
    
    Returns configuration status and expected redirect URIs
    """
    client_id = os.getenv('MICROSOFT_CLIENT_ID', '')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET', '')
    tenant_id = os.getenv('MICROSOFT_TENANT_ID', 'common')
    
    # Calculate redirect URI
    from flask import request
    redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/callback'
    
    return jsonify({
        'success': True,
        'configured': bool(client_id and client_secret),
        'client_id': client_id[:20] + '...' if client_id else 'NOT SET',
        'client_secret': 'SET' if client_secret else 'NOT SET',
        'tenant_id': tenant_id,
        'redirect_uri': redirect_uri,
        'azure_ad_setup': {
            'portal': 'https://portal.azure.com',
            'required_redirect_uris': [
                'http://localhost:5001/api/auth/microsoft/callback',  # ✅ MUST use localhost (not 127.0.0.1)
            ],
            'for_production': [
                'https://yourdomain.com/api/auth/microsoft/callback'  # ✅ Production MUST use HTTPS
            ],
            'note': 'Azure AD requires: (1) http://localhost for local dev, OR (2) HTTPS for production. http://127.0.0.1 is NOT allowed.',
            'scopes_requested': [
                'openid',
                'profile',
                'email', 
                'User.Read',
                'User.ReadWrite',
                'offline_access'
            ]
        }
    })

# ======================================================================
# DATABASE HELPER FUNCTIONS (Workaround for UserAuthManager import issue)
# ======================================================================

def get_db_connection():
    """Get SQLite database connection"""
    # Use same database as main auth system (ai_infrastructure.db)
    db_path = os.path.join(os.path.dirname(__file__), '..', 'ai_infrastructure.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def db_get_user_by_email(email: str):
    """Get user by email from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"❌ Error getting user by email: {e}")
        return None

def db_get_user_by_id(user_id: int):
    """Get user by ID from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    except Exception as e:
        logger.error(f"❌ Error getting user by ID: {e}")
        return None

def db_create_user(email: str, username: str, role: str = 'user'):
    """Create new user in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # OAuth users don't have passwords - use placeholder
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, 'oauth_microsoft', role, datetime.now().isoformat()))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Created new user: {email} (ID: {user_id})")
        return db_get_user_by_email(email)
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}")
        return None

def db_store_microsoft_tokens(user_id: int, access_token: str, refresh_token: str, expires_in: int, 
                             microsoft_id: str = None, microsoft_email: str = None, display_name: str = None):
    """Store Microsoft OAuth tokens and profile in database using correct schema"""
    try:
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Build metadata with profile info
        metadata = {
            'expires_in': expires_in,
            'created_at': datetime.now().isoformat()
        }
        if microsoft_id:
            metadata['microsoft_id'] = microsoft_id
        if microsoft_email:
            metadata['microsoft_email'] = microsoft_email
        if display_name:
            metadata['display_name'] = display_name
        
        # Store access token with profile metadata
        # ✅ FIX: Use 'microsoft' (not 'microsoft365') to match profile query
        cursor.execute('''
            INSERT OR REPLACE INTO user_platform_credentials 
            (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, 'microsoft', 'oauth', 'access_token', access_token, 1, json.dumps(metadata)))
        
        # Store refresh token if available
        if refresh_token:
            cursor.execute('''
                INSERT OR REPLACE INTO user_platform_credentials 
                (user_id, platform, credential_type, credential_key, credential_value, is_active, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, 'microsoft', 'oauth', 'refresh_token', refresh_token, 1))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Stored Microsoft tokens and profile for user {user_id} ({display_name or microsoft_email})")
        return True
    except Exception as e:
        logger.error(f"❌ Error storing Microsoft tokens: {e}")
        return False

def db_create_jwt_token(user_id: int, email: str):
    """Create JWT token for user session"""
    try:
        # Get JWT secret from environment
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.master')
        load_dotenv(env_path)
        
        jwt_secret = os.getenv('JWT_SECRET', 'your-secret-key-change-this')
        
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = pyjwt.encode(payload, jwt_secret, algorithm='HS256')
        
        # Store token in user_sessions table for validation
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            expires_at = (datetime.utcnow() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO user_sessions (user_id, token, expires_at)
                VALUES (?, ?, ?)
            ''', (user_id, token, expires_at))
            conn.commit()
            conn.close()
            logger.info(f"✅ Stored JWT token in user_sessions")
        except Exception as e:
            logger.warning(f"⚠️ Warning: Could not store token in sessions: {e}")
        
        logger.info(f"✅ Created JWT token for user {user_id}")
        return token
    except Exception as e:
        logger.error(f"❌ Error creating JWT token: {e}")
        return None


@microsoft_auth_bp.route('/login', methods=['GET'])
def microsoft_login():
    """
    Initiate Microsoft 365 OAuth login
    
    GET /api/auth/microsoft/login
    
    Redirects user to Microsoft login page
    """
    try:
        # Check if Microsoft credentials are configured
        if not microsoft_oauth_manager.client_id or not microsoft_oauth_manager.client_secret:
            logger.warning("⚠️ Microsoft 365 credentials not configured")
            return jsonify({
                'success': False,
                'error': 'Microsoft 365 login not configured',
                'setup_required': True,
                'instructions': {
                    'step1': 'Register Azure AD application at https://portal.azure.com',
                    'step2': 'Navigate: Azure Active Directory → App registrations → New registration',
                    'step3': 'Set redirect URI: http://localhost:5001/api/auth/microsoft/callback',
                    'step4': 'Copy Application (client) ID and create Client secret',
                    'step5': 'Update .env.master with MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET',
                    'step6': 'Restart server with BISTART',
                    'documentation': 'See MICROSOFT_365_LOGIN_SETUP_GUIDE.md for details'
                }
            }), 400
        
        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)
        session['microsoft_oauth_state'] = state
        
        # Get redirect URI from config or request
        redirect_uri = request.args.get('redirect_uri')
        if not redirect_uri:
            # Default to callback endpoint
            redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/callback'
        
        # Store original redirect for after login
        return_url = request.args.get('return_url', '/')
        session['microsoft_return_url'] = return_url
        
        # Get Microsoft authorization URL
        auth_url = get_microsoft_auth_url(redirect_uri=redirect_uri, state=state)
        
        logger.info(f"🔷 Initiating Microsoft login (redirect: {redirect_uri})")
        logger.info(f"🔷 Auth URL: {auth_url}")
        logger.info(f"🔷 Client ID being used: {os.getenv('MICROSOFT_CLIENT_ID')}")
        logger.info(f"🔷 Tenant ID: {os.getenv('MICROSOFT_TENANT_ID', 'common')}")
        
        # Redirect directly to Microsoft login page
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"❌ Microsoft login failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/callback', methods=['GET'])
def microsoft_callback():
    """
    Microsoft OAuth callback endpoint
    
    GET /api/auth/microsoft/callback?code=...&state=...
    
    Handles OAuth callback after user authorizes
    """
    try:
        # Verify state for CSRF protection
        state = request.args.get('state')
        stored_state = session.get('microsoft_oauth_state')
        
        if not state or state != stored_state:
            logger.error("❌ Invalid OAuth state (CSRF protection)")
            return jsonify({
                'success': False,
                'error': 'Invalid state parameter (CSRF protection failed)'
            }), 400
        
        # Get authorization code
        code = request.args.get('code')
        error = request.args.get('error')
        
        if error:
            logger.error(f"❌ Microsoft OAuth error: {error}")
            return jsonify({
                'success': False,
                'error': f'Microsoft authorization failed: {error}'
            }), 400
        
        if not code:
            logger.error("❌ No authorization code received")
            return jsonify({
                'success': False,
                'error': 'No authorization code received'
            }), 400
        
        # Exchange code for tokens and get user profile
        redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/callback'
        auth_result = authenticate_user_with_microsoft(code, redirect_uri)
        
        if not auth_result['success']:
            logger.error(f"❌ Authentication failed: {auth_result.get('error')}")
            return jsonify(auth_result), 400
        
        profile = auth_result['profile']
        tokens = auth_result['tokens']
        
        logger.info(f"✅ Microsoft authentication successful: {profile['email']}")
        
        # Check if user exists in database (primary email OR alias)
        user_id = get_user_id_by_email(profile['email'])
        
        if user_id:
            # User exists (found via primary or alias) - log them in
            user = db_get_user_by_id(user_id)  # Get full user object
            if not user:
                user = db_get_user_by_email(profile['email'])  # Fallback
            
            logger.info(f"✅ Existing user found: {user['username']} (ID: {user_id})")
            
            # If logging in via alias
            if user['email'] != profile['email']:
                logger.info(f"📧 Logging in via alias: {profile['email']}")
            
            # Update Microsoft tokens in database (using direct DB function)
            db_store_microsoft_tokens(
                user_id=user['id'],
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token', ''),
                expires_in=tokens.get('expires_in', 3600),
                microsoft_id=profile.get('id'),
                microsoft_email=profile.get('email'),
                display_name=profile.get('display_name')
            )
            
            # Create JWT session token (using direct DB function)
            jwt_token = db_create_jwt_token(user['id'], user['email'])
            
            if not jwt_token:
                logger.error("❌ Failed to create JWT token")
                return jsonify({'success': False, 'error': 'Failed to create session'}), 500
            
            # Redirect to frontend with token
            logger.info(f"✅ Redirecting to frontend with JWT token")
            return redirect(f"http://localhost:5001/?token={jwt_token}")
            
        else:
            # User doesn't exist - auto-register
            logger.info(f"🆕 New user - auto-registering: {profile['email']}")
            
            # Create username from email
            username = profile['email'].split('@')[0]
            
            # Register user (using direct DB function)
            user = db_create_user(
                email=profile['email'],
                username=username,
                role='user'
            )
            
            if not user:
                logger.error(f"❌ User registration failed")
                return jsonify({'success': False, 'error': 'Failed to create user'}), 500
            
            logger.info(f"✅ User created: {user['username']} (ID: {user['id']})")
            
            # Store Microsoft tokens (using direct DB function)
            db_store_microsoft_tokens(
                user_id=user['id'],
                access_token=tokens['access_token'],
                refresh_token=tokens.get('refresh_token', ''),
                expires_in=tokens.get('expires_in', 3600),
                microsoft_id=profile.get('id'),
                microsoft_email=profile.get('email'),
                display_name=profile.get('display_name')
            )
            
            # Create JWT session token (using direct DB function)
            jwt_token = db_create_jwt_token(user['id'], user['email'])
            
            if not jwt_token:
                logger.error("❌ Failed to create JWT token")
                return jsonify({'success': False, 'error': 'Failed to create session'}), 500
            
            # Redirect to frontend with token
            logger.info(f"✅ Redirecting new user to frontend with JWT token")
            return redirect(f"http://localhost:5001/?token={jwt_token}&new_user=true")
    
    except Exception as e:
        logger.error(f"❌ Microsoft callback error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/link', methods=['POST'])
def link_microsoft_account():
    """
    Link Microsoft account to existing user
    
    POST /api/auth/microsoft/link
    Headers: Authorization: Bearer <jwt_token>
    
    Initiates OAuth flow to link Microsoft account
    """
    try:
        # Get current user from JWT
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Missing or invalid authorization header'
            }), 401
        
        jwt_token = auth_header.split(' ')[1]
        user = user_auth_manager.verify_session(jwt_token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Generate state with user ID
        state = secrets.token_urlsafe(32)
        session['microsoft_link_state'] = state
        session['microsoft_link_user_id'] = user['id']
        
        # Get redirect URI
        redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/link-callback'
        
        # Get Microsoft authorization URL
        auth_url = get_microsoft_auth_url(redirect_uri=redirect_uri, state=state)
        
        logger.info(f"🔗 Linking Microsoft account for user: {user['username']}")
        
        return jsonify({
            'success': True,
            'authorization_url': auth_url,
            'message': 'Redirect user to authorization_url to link Microsoft account'
        })
        
    except Exception as e:
        logger.error(f"❌ Microsoft link failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/link-callback', methods=['GET'])
def microsoft_link_callback():
    """
    Microsoft OAuth link callback endpoint
    
    GET /api/auth/microsoft/link-callback?code=...&state=...
    """
    try:
        # Verify state
        state = request.args.get('state')
        stored_state = session.get('microsoft_link_state')
        user_id = session.get('microsoft_link_user_id')
        
        if not state or state != stored_state or not user_id:
            logger.error("❌ Invalid OAuth state for linking")
            return jsonify({
                'success': False,
                'error': 'Invalid state parameter'
            }), 400
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            return jsonify({
                'success': False,
                'error': 'No authorization code received'
            }), 400
        
        # Exchange code for tokens
        redirect_uri = request.url_root.rstrip('/') + '/api/auth/microsoft/link-callback'
        auth_result = authenticate_user_with_microsoft(code, redirect_uri)
        
        if not auth_result['success']:
            return jsonify(auth_result), 400
        
        profile = auth_result['profile']
        tokens = auth_result['tokens']
        
        # Store Microsoft tokens for user
        user_auth_manager.store_microsoft_tokens(
            user_id=user_id,
            access_token=tokens['access_token'],
            refresh_token=tokens['refresh_token'],
            expires_at=tokens['expires_at'],
            microsoft_id=profile['id'],
            microsoft_email=profile['email']
        )
        
        logger.info(f"✅ Microsoft account linked: {profile['email']}")
        
        return redirect('/?microsoft_linked=success')
        
    except Exception as e:
        logger.error(f"❌ Microsoft link callback error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/config', methods=['GET'])
def microsoft_config():
    """
    Check if Microsoft OAuth is configured (public endpoint)
    
    GET /api/auth/microsoft/config
    
    Returns OAuth configuration status
    """
    try:
        configured = bool(
            microsoft_oauth_manager.client_id and 
            microsoft_oauth_manager.client_secret
        )
        
        return jsonify({
            'success': True,
            'configured': configured,
            'client_id': microsoft_oauth_manager.client_id if configured else None,
            'redirect_uri': 'http://localhost:5001/api/auth/microsoft/callback' if configured else None
        })
    except Exception as e:
        logger.error(f"❌ Config check failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@microsoft_auth_bp.route('/status', methods=['GET'])
def microsoft_status():
    """
    Check Microsoft connection status
    
    GET /api/auth/microsoft/status
    Headers: Authorization: Bearer <jwt_token>
    
    Returns Microsoft connection status for current user
    """
    try:
        # Get current user
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Missing authorization header'
            }), 401
        
        jwt_token = auth_header.split(' ')[1]
        user = user_auth_manager.verify_session(jwt_token)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401
        
        # Check Microsoft connection
        microsoft_data = user_auth_manager.get_microsoft_tokens(user['id'])
        
        if microsoft_data:
            # Get profile info from metadata
            microsoft_email = microsoft_data.get('microsoft_email')
            microsoft_id = microsoft_data.get('microsoft_id')
            display_name = microsoft_data.get('display_name', microsoft_email)
            
            return jsonify({
                'success': True,
                'connected': True,
                'microsoft_email': microsoft_email,
                'microsoft_id': microsoft_id,
                'display_name': display_name,
                'avatar_url': f"https://graph.microsoft.com/v1.0/users/{microsoft_id}/photo/$value" if microsoft_id else None,
                'token_expires_at': microsoft_data.get('expires_at'),
                'connected_at': microsoft_data.get('created_at')
            })
        else:
            return jsonify({
                'success': True,
                'connected': False
            })
            
    except Exception as e:
        logger.error(f"❌ Microsoft status check failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
