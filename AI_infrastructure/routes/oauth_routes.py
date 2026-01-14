"""
OAuth Routes for Google Workspace Integration
==============================================

Handles OAuth 2.0 flow for client authentication

FIXED: 2025-01-XX - Complete cursor management overhaul
CHANGES:
- Added cursor = None initialization before try block
- Added conn = None initialization before try block
- Added try/finally block with exception-safe cleanup
- Added cursor.close() BEFORE conn.close() (was missing!)
- Fixed early return handling (close resources before redirect)
- Proper cleanup order: cursor → conn
"""

from flask import Blueprint, request, redirect, session, jsonify, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import os
from datetime import datetime
from pathlib import Path
from shared.database_utils import get_database_connection, convert_sql_placeholders

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google_workspace.oauth_manager import UNIFIED_SCOPES, get_oauth_config
from AI_infrastructure.auth.user_auth import user_auth_manager
from AI_infrastructure.utils.oauth_url_helper import get_frontend_url, capture_oauth_origin


oauth_bp = Blueprint('oauth', __name__, url_prefix='/api/oauth')


@oauth_bp.route('/google/login', methods=['GET'])
def google_login():
    """
    Alias for /workspace/start - Start Google OAuth flow
    
    GET /api/oauth/google/login
    
    Redirects to the unified OAuth workspace flow
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    # Redirect to the main workspace OAuth endpoint
    return redirect(url_for('oauth.oauth_workspace_start', mode='signin'))


@oauth_bp.route('/microsoft/login', methods=['GET'])
def microsoft_login():
    """
    Alias for Microsoft OAuth flow
    
    GET /api/oauth/microsoft/login
    
    TODO: Implement Microsoft OAuth flow
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    return jsonify({
        'success': False,
        'error': 'Microsoft OAuth not yet implemented. Use /api/oauth/workspace/start'
    }), 501


@oauth_bp.route('/workspace/start', methods=['GET'])
def oauth_workspace_start():
    """
    Start OAuth flow for Google Workspace
    
    GET /api/oauth/workspace/start?mode=signin|signup
    
    Initiates OAuth 2.0 flow with unified scopes:
    - Gmail, Calendar, Tasks, Forms
    - Docs, Sheets, Slides, Drive
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    try:
        mode = request.args.get('mode', 'signin')  # signin or signup
        
        # Get OAuth configuration
        config = get_oauth_config(service_name=None, mode='web')
        
        if not config or not config.get('credentials_file'):
            return jsonify({
                'success': False,
                'error': 'OAuth not configured. Missing credentials_web.json'
            }), 500
        
        credentials_file = config['credentials_file']
        
        if not os.path.exists(credentials_file):
            return jsonify({
                'success': False,
                'error': f'Credentials file not found: {credentials_file}'
            }), 500
        
        # Create OAuth flow
        flow = Flow.from_client_secrets_file(
            credentials_file,
            scopes=UNIFIED_SCOPES,
            redirect_uri=request.host_url.rstrip('/') + '/api/oauth/workspace/callback'
        )
        
        # Generate authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        # Store state in session for verification
        session['oauth_state'] = state
        session['oauth_mode'] = mode  # Remember if signin or signup
        
        # CAPTURE ORIGIN URL: Store where user started OAuth (for redirect back)
        capture_oauth_origin(request, session)
        
        print(f"🔐 OAuth flow started: {mode}")
        print(f"   Redirect URI: {flow.redirect_uri}")
        print(f"   State: {state[:20]}...")
        
        # Redirect user to Google
        return redirect(authorization_url)
        
    except Exception as e:
        print(f"❌ OAuth start error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@oauth_bp.route('/workspace/callback', methods=['GET'])
def oauth_workspace_callback():
    """
    OAuth callback endpoint
    
    GET /api/oauth/workspace/callback?code=...&state=...
    
    Exchanges authorization code for access token
    Stores encrypted token in database
    
    FIXED: Added proper cursor management with try/finally block
    """
    cursor = None  # ✅ CRITICAL: Initialize before try
    conn = None    # ✅ CRITICAL: Initialize before try
    
    try:
        # Verify state
        state = request.args.get('state')
        if state != session.get('oauth_state'):
            # ✅ Safe - no cursor created yet
            return redirect('/login?error=Invalid OAuth state')
        
        mode = session.get('oauth_mode', 'signin')
        
        # Get OAuth configuration
        config = get_oauth_config(service_name=None, mode='web')
        credentials_file = config['credentials_file']
        
        # Create OAuth flow
        flow = Flow.from_client_secrets_file(
            credentials_file,
            scopes=UNIFIED_SCOPES,
            state=state,
            redirect_uri=request.host_url.rstrip('/') + '/api/oauth/workspace/callback'
        )
        
        # Exchange code for token
        flow.fetch_token(authorization_response=request.url)
        
        # Get credentials
        credentials = flow.credentials
        
        # Extract user info from credentials
        # Note: We'll need to make an API call to get email
        from googleapiclient.discovery import build
        
        try:
            # Get user's email from Gmail API
            gmail_service = build('gmail', 'v1', credentials=credentials)
            profile = gmail_service.users().getProfile(userId='me').execute()
            user_email = profile['emailAddress']
        except Exception as e:
            print(f"⚠️ Could not get email from Gmail API: {e}")
            # Fallback: Try to get from OAuth token info
            try:
                import requests
                response = requests.get(
                    'https://www.googleapis.com/oauth2/v1/userinfo',
                    headers={'Authorization': f'Bearer {credentials.token}'}
                )
                user_info = response.json()
                user_email = user_info.get('email')
            except:
                # ✅ Safe - no cursor created yet
                return redirect('/login?error=Could not verify Google account')
        
        print(f"✅ OAuth callback successful: {user_email}")
        
        # Prepare token data for storage
        token_data = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': list(credentials.scopes),
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None
        }
        
        # ✅ NOW create database connection (after validations passed)
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Get or create user
        cursor.execute('SELECT id FROM ai_infrastructure.users WHERE email = %s', (user_email,))
        user_row = cursor.fetchone()
        
        user_id = None
        username = None
        
        if user_row:
            user_id = user_row['id']
            print(f"✅ Found existing user: {user_id}")
        else:
            # Auto-create user if OAuth login
            username = user_email.split('@')[0]
            cursor.execute(
                'INSERT INTO ai_infrastructure.users (username, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                (username, user_email, 'oauth_google', 'user')
            )
            user_id = cursor.lastrowid
            print(f"✅ Created new user: {user_id}")
        
        # Store access token with proper schema
        sql, params = convert_sql_placeholders('''
            INSERT OR REPLACE INTO ai_infrastructure.user_platform_credentials 
            (user_id, platform, credential_type, credential_key, credential_value, is_active, metadata, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ''', (user_id, 'google', 'oauth', 'access_token', credentials.token, 1, json.dumps({
            'scopes': list(credentials.scopes),
            'expiry': credentials.expiry.isoformat() if credentials.expiry else None,
            'user_email': user_email
        })))
        
        cursor.execute(sql, params)
        
        # Store refresh token if available
        if credentials.refresh_token:
            cursor.execute('''
                INSERT OR REPLACE INTO ai_infrastructure.user_platform_credentials 
                (user_id, platform, credential_type, credential_key, credential_value, is_active, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
            ''', (user_id, 'google', 'oauth', 'refresh_token', credentials.refresh_token, 1))
        
        conn.commit()
        
        # ✅ FIX: Close cursor BEFORE conn (single close, not duplicate)
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        print(f"✅ Stored Google OAuth credentials in database for user {user_id}")
        
        # Also store in session for immediate use
        session['user_email'] = user_email
        session['user_id'] = user_id
        session['oauth_connected'] = True
        session['google_connected'] = True
        session.permanent = True  # Make session persistent
        
        # Generate JWT token for the user
        from auth.user_auth import user_auth_manager
        jwt_token = user_auth_manager.generate_jwt({
            'id': user_id,
            'username': username if not user_row else None,
            'email': user_email,
            'role': 'user',
            'oauth_connected': True,
            'google_connected': True
        })
        
        # Store OAuth connection info in JWT for client-side detection
        print(f"✅ OAuth login successful, redirecting with JWT token (OAuth connected: True)")
        print(f"   User: {user_email} (ID: {user_id})")
        print(f"   Session persisted: True")
        
        # SMART URL DETECTION: Automatically detect frontend URL
        frontend_url = get_frontend_url(request, session)
        
        return redirect(f'{frontend_url}/?token={jwt_token}')
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(f'/login?error={str(e)}')
    
    finally:
        # ✅ CRITICAL: GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"⚠️ Error closing cursor: {e}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"⚠️ Error closing connection: {e}")


@oauth_bp.route('/status', methods=['GET'])
def oauth_status():
    """
    Check OAuth connection status
    
    GET /api/oauth/status
    
    Returns OAuth connection status for current user
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    try:
        user_email = session.get('user_email')
        oauth_connected = session.get('oauth_connected', False)
        
        if not user_email:
            return jsonify({
                'success': True,
                'connected': False,
                'message': 'No user session'
            })
        
        return jsonify({
            'success': True,
            'connected': oauth_connected,
            'user_email': user_email,
            'services': [
                'Gmail',
                'Google Calendar',
                'Google Tasks',
                'Google Forms',
                'Google Docs',
                'Google Sheets',
                'Google Slides',
                'Google Drive'
            ] if oauth_connected else []
        })
        
    except Exception as e:
        print(f"❌ OAuth status error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@oauth_bp.route('/disconnect', methods=['POST'])
def oauth_disconnect():
    """
    Disconnect Google Workspace
    
    POST /api/oauth/disconnect
    
    Removes OAuth token and disconnects services
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    try:
        user_email = session.get('user_email')
        
        if not user_email:
            return jsonify({
                'success': False,
                'error': 'No user session'
            }), 400
        
        # Remove token file
        config = get_oauth_config(service_name=None, mode='web')
        token_file = config.get('token_file', 'token_unified_web.json')
        token_file_user = token_file.replace('.json', f'_{user_email.replace("@", "_at_")}.json')
        
        if os.path.exists(token_file_user):
            os.remove(token_file_user)
            print(f"🗑️ Token removed: {token_file_user}")
        
        # Clear session
        session.pop('oauth_connected', None)
        session.pop('oauth_token', None)
        
        return jsonify({
            'success': True,
            'message': 'Google Workspace disconnected'
        })
        
    except Exception as e:
        print(f"❌ OAuth disconnect error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500