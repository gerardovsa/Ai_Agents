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

from flask import Blueprint, request, redirect, session, jsonify
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import os
from datetime import datetime, timedelta
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
    Alias for /workspace/start - Start Google OAuth flow (Phase 9: redirect to canonical).

    GET /api/oauth/google/login

    Phase 9: delegate to the canonical /api/auth/google/login route.
    The canonical flow owns the OAuth state, session, and token storage.
    The legacy route remains in place for backwards compatibility with
    existing frontend call sites (e.g. UI/business-ai-platform-v2.html).

    ✅ NO DATABASE OPERATIONS - Safe
    """
    # Phase 9: redirect to the canonical Google OAuth login endpoint.
    # We pass `mode=signin` for behavioural parity with the previous
    # internal redirect, but the canonical endpoint ignores it (the
    # canonical flow does not differentiate signin vs signup).
    return redirect('/api/auth/google/login?mode=signin')


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
    Start OAuth flow for Google Workspace (Phase 9: redirect to canonical).

    GET /api/oauth/workspace/start?mode=signin|signup

    Phase 9: delegate to the canonical /api/auth/google/login endpoint.
    The canonical flow owns the OAuth state, session, and token storage.
    This legacy route is retained for backwards compatibility with
    existing frontend call sites (e.g. UI/modules_internal/components/account_profile.js,
    templates/dashboard.html).

    The `mode` query arg is forwarded for behavioural parity. The canonical
    endpoint does not differentiate signin vs signup, so any value is harmless.

    ✅ NO DATABASE OPERATIONS - Safe
    """
    mode = request.args.get('mode', 'signin')
    print(f"🔐 OAuth flow started: {mode} (delegating to canonical /api/auth/google/login)")
    return redirect(f'/api/auth/google/login?mode={mode}')


@oauth_bp.route('/workspace/callback', methods=['GET'])
def oauth_workspace_callback():
    """
    OAuth callback endpoint (Phase 9: writes to the canonical token table).

    GET /api/oauth/workspace/callback?code=...&state=...

    Exchanges authorization code for access token.
    Phase 9: stores tokens in the canonical `ai_infrastructure.oauth_tokens`
    table (24-column schema) so the shared OAuth injector can read them.
    The route is retained because it is the registered Google redirect URI;
    the destination table is the only thing that changed.

    FIXED: Added proper cursor management with try/finally block.
    """
    cursor = None  # ✅ CRITICAL: Initialize before try
    conn = None    # ✅ CRITICAL: Initialize before try

    try:
        # Verify state — check DB first (canonical flow), then Flask session
        # (legacy flow). The Phase 9 redirect from /workspace/start to the
        # canonical /api/auth/google/login means new flows have state in DB.
        state = request.args.get('state')
        state_valid = False

        try:
            conn_state = get_database_connection('ai_infrastructure')
            cursor_state = conn_state.cursor()
            sql, params = convert_sql_placeholders(
                "SELECT state FROM ai_infrastructure.oauth_states "
                "WHERE state = %s AND platform = 'google' "
                "AND expires_at > CURRENT_TIMESTAMP",
                (state,),
            )
            cursor_state.execute(sql, params)
            db_state_row = cursor_state.fetchone()
            if db_state_row:
                state_valid = True
                # Delete used state (single-use, mirroring canonical)
                del_sql, del_params = convert_sql_placeholders(
                    "DELETE FROM ai_infrastructure.oauth_states WHERE state = %s",
                    (state,),
                )
                cursor_state.execute(del_sql, del_params)
                conn_state.commit()
            cursor_state.close()
            conn_state.close()
        except Exception as db_state_err:
            print(f"⚠️ oauth_workspace_callback: DB state lookup failed ({db_state_err}); "
                  f"falling back to Flask session check")

        # Fallback to Flask session (legacy flow / cached browser state)
        if not state_valid and state and state == session.get('oauth_state'):
            state_valid = True
            session.pop('oauth_state', None)

        if not state_valid:
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

        # Extract user info — try userinfo endpoint first (canonical), then
        # Gmail API fallback (legacy behaviour retained for parity).
        import requests
        user_email = None
        user_name = None
        user_picture = None
        google_id = None

        try:
            resp = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                headers={'Authorization': f'Bearer {credentials.token}'},
            )
            resp.raise_for_status()
            user_info = resp.json()
            user_email = user_info.get('email')
            user_name = user_info.get('name')
            user_picture = user_info.get('picture')
            google_id = user_info.get('id')
        except Exception as e:
            print(f"⚠️ oauth_workspace_callback: userinfo fetch failed ({e}); "
                  f"falling back to Gmail API profile")
            try:
                from googleapiclient.discovery import build
                gmail_service = build('gmail', 'v1', credentials=credentials)
                profile = gmail_service.users().getProfile(userId='me').execute()
                user_email = profile['emailAddress']
            except Exception as e2:
                print(f"❌ Could not get email from Gmail API: {e2}")
                return redirect('/login?error=Could not verify Google account')

        if not user_email:
            return redirect('/login?error=Could not verify Google account')

        print(f"✅ OAuth callback successful: {user_email}")

        # ✅ NOW create database connection (after validations passed)
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()

        # Get or create user — also fetch password_hash for link_purpose
        cursor.execute(
            'SELECT id, password_hash FROM ai_infrastructure.users WHERE email = %s',
            (user_email,),
        )
        user_row = cursor.fetchone()

        user_id = None
        username = None
        password_hash = None

        if user_row:
            user_id = user_row['id'] if isinstance(user_row, dict) else user_row[0]
            password_hash = (
                user_row['password_hash']
                if isinstance(user_row, dict)
                else user_row[1]
            )
            print(f"✅ Found existing user: {user_id}")
        else:
            # Auto-create user if OAuth login
            username = user_email.split('@')[0]
            cursor.execute(
                'INSERT INTO ai_infrastructure.users (username, email, password_hash, role) '
                'VALUES (%s, %s, %s, %s)',
                (username, user_email, 'oauth_google', 'user'),
            )
            user_id = cursor.lastrowid
            password_hash = 'oauth_google'
            print(f"✅ Created new user: {user_id}")

        # Phase 9: link_purpose follows the canonical convention —
        # primary if the user logged in with Google, storage otherwise.
        link_purpose = 'primary' if password_hash == 'oauth_google' else 'storage'

        # ====================================================================
        # PHASE 9: Write to canonical `ai_infrastructure.oauth_tokens`
        # (24-column schema). The tools read from this table; the legacy
        # token store was unreadable by the tool layer. Same INSERT/UPDATE
        # shape as google_auth_routes_V2_FIXED.py callback.
        # ====================================================================
        from shared.database_utils import is_using_supabase
        bool_true = True if is_using_supabase() else 1

        # Compute expiry timestamp
        if credentials.expiry:
            expires_at = credentials.expiry.strftime('%Y-%m-%d %H:%M:%S')
        else:
            expires_at = (
                datetime.utcnow() + timedelta(seconds=3600)
            ).strftime('%Y-%m-%d %H:%M:%S')

        scope_str = ' '.join(credentials.scopes) if credentials.scopes else ''
        granted_scopes = list(credentials.scopes) if credentials.scopes else []

        # Check if token exists for this user+platform
        cursor.execute(
            'SELECT id FROM ai_infrastructure.oauth_tokens '
            'WHERE user_id = %s AND platform = %s',
            (user_id, 'google'),
        )
        existing_token = cursor.fetchone()

        metadata = json.dumps({
            'google_id': google_id,
            'email': user_email,
            'name': user_name,
            'picture': user_picture,
            'authorized_at': datetime.utcnow().isoformat(),
            'client_id': (credentials.client_id or '')[:20] + '...' if credentials.client_id else None,
            'link_purpose': link_purpose,
            'legacy_callback': True,  # Mark provenance for ops debugging
        })

        if existing_token:
            # UPDATE existing token
            sql, params = convert_sql_placeholders('''
                UPDATE ai_infrastructure.oauth_tokens SET
                    access_token = %s,
                    refresh_token = COALESCE(%s, refresh_token),
                    token_type = %s,
                    expires_at = %s,
                    scope = %s,
                    is_valid = %s,
                    is_active = %s,
                    auto_refresh_enabled = %s,
                    last_refreshed_at = %s,
                    refresh_attempts = 0,
                    last_refresh_error = NULL,
                    updated_at = CURRENT_TIMESTAMP,
                    granted_scopes = %s,
                    metadata = %s,
                    link_purpose = %s
                WHERE user_id = %s AND platform = %s
            ''', (
                credentials.token,
                credentials.refresh_token,
                'Bearer',
                expires_at,
                scope_str,
                bool_true,
                bool_true,
                bool_true,
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                granted_scopes,
                metadata,
                link_purpose,
                user_id,
                'google',
            ))
            cursor.execute(sql, params)
        else:
            # INSERT new token (full 24-column schema)
            sql, params = convert_sql_placeholders('''
                INSERT INTO ai_infrastructure.oauth_tokens (
                    user_id, platform,
                    access_token, refresh_token, token_type, expires_at,
                    scope, is_valid, is_active, auto_refresh_enabled,
                    last_refreshed_at, refresh_attempts, last_refresh_error,
                    granted_scopes, metadata, link_purpose,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            ''', (
                user_id,
                'google',
                credentials.token,
                credentials.refresh_token,
                'Bearer',
                expires_at,
                scope_str,
                bool_true,
                bool_true,
                bool_true,
                datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                0,
                None,
                granted_scopes,
                metadata,
                link_purpose,
            ))
            cursor.execute(sql, params)

        # Update has_google_oauth flag (mirrors canonical behaviour)
        flag_sql, flag_params = convert_sql_placeholders(
            'UPDATE ai_infrastructure.users SET has_google_oauth = %s WHERE id = %s',
            (bool_true, user_id),
        )
        cursor.execute(flag_sql, flag_params)

        conn.commit()

        # ✅ FIX: Close cursor BEFORE conn (single close, not duplicate)
        cursor.close()
        cursor = None
        conn.close()
        conn = None

        print(f"✅ Phase 9: stored Google OAuth tokens in oauth_tokens (link_purpose={link_purpose}) "
              f"for user {user_id}")
        
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