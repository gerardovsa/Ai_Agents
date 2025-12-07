"""
Microsoft OAuth 2.0 Authentication Routes
Handles Microsoft 365 authentication via Azure AD
"""
from shared.database_utils import convert_sql_placeholders

from flask import Blueprint, request, jsonify, session, redirect
from datetime import datetime, timedelta
import requests
import os
from database import get_db_connection

microsoft_auth_bp = Blueprint('microsoft_auth', __name__)

# Microsoft OAuth Configuration
MICROSOFT_CLIENT_ID = os.getenv('MICROSOFT_CLIENT_ID')
MICROSOFT_CLIENT_SECRET = os.getenv('MICROSOFT_CLIENT_SECRET')
MICROSOFT_TENANT = os.getenv('MICROSOFT_TENANT', 'common')  # 'common', 'organizations', or tenant ID

def get_dynamic_redirect_uri(path='/api/auth/microsoft/callback'):
    """Build redirect URI dynamically from incoming request"""
    # Detect base URL from request
    base_url = request.url_root.rstrip('/')
    
    # Force HTTPS on Render.com
    if 'onrender.com' in request.host or os.getenv('RENDER') == 'true':
        base_url = base_url.replace('http://', 'https://')
    
    return base_url + path

# Microsoft OAuth Endpoints
MICROSOFT_AUTH_URL = f'https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/authorize'
MICROSOFT_TOKEN_URL = f'https://login.microsoftonline.com/{MICROSOFT_TENANT}/oauth2/v2.0/token'
MICROSOFT_GRAPH_URL = 'https://graph.microsoft.com/v1.0'

# Required scopes for Microsoft 365 operations
MICROSOFT_SCOPES = [
    # User & Profile
    'User.Read',                      # Read user profile
    
    # Email (Outlook)
    'Mail.Read',                      # Read emails
    'Mail.Send',                      # Send emails
    'Mail.ReadWrite',                 # Full email access
    'MailboxSettings.ReadWrite',      # Manage mailbox settings and rules
    
    # Teams
    'Team.ReadBasic.All',             # Read basic team info
    'TeamSettings.ReadWrite.All',     # Manage team settings
    'Channel.ReadBasic.All',          # Read channel info
    'ChannelMessage.Send',            # Send channel messages
    'Chat.ReadWrite',                 # Read and send chat messages
    
    # OneDrive & Files
    'Files.ReadWrite.All',            # Full file access in OneDrive
    
    # Calendar
    'Calendars.ReadWrite',            # Full calendar access
    
    # Tasks & To Do
    'Tasks.ReadWrite',                # To Do tasks access
    
    # Planner (requires Groups)
    'Group.ReadWrite.All'             # Planner plans access (via Groups)
]


@microsoft_auth_bp.route('/api/auth/microsoft/login', methods=['GET'])
def microsoft_login():
    """Initiate Microsoft OAuth flow"""
    
    if not MICROSOFT_CLIENT_ID or not MICROSOFT_CLIENT_SECRET:
        return jsonify({
            'success': False,
            'error': 'Microsoft OAuth not configured. Set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET in .env'
        }), 500
    
    # Get user_id from query parameters
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id parameter required'
        }), 400
    
    # Store user_id in session for callback
    session['microsoft_auth_user_id'] = user_id
    
    # Build redirect URI dynamically from current request
    redirect_uri = get_dynamic_redirect_uri()
    
    # Store redirect URI in session for callback verification
    session['microsoft_redirect_uri'] = redirect_uri
    
    print(f"🔄 [Microsoft OAuth] Dynamic redirect URI: {redirect_uri}")
    
    # Build authorization URL
    params = {
        'client_id': MICROSOFT_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': ' '.join(MICROSOFT_SCOPES),
        'response_mode': 'query',
        'state': user_id  # Pass user_id as state for verification
    }
    
    auth_url = f"{MICROSOFT_AUTH_URL}?{'&'.join([f'{k}={v}' for k, v in params.items()])}"
    
    return redirect(auth_url)


@microsoft_auth_bp.route('/api/auth/microsoft/callback', methods=['GET'])
def microsoft_callback():
    """Handle Microsoft OAuth callback"""
    
    # Get authorization code
    code = request.args.get('code')
    error = request.args.get('error')
    state = request.args.get('state')  # user_id
    
    if error:
        return jsonify({
            'success': False,
            'error': f'Authorization failed: {error}',
            'description': request.args.get('error_description')
        }), 400
    
    if not code:
        return jsonify({
            'success': False,
            'error': 'No authorization code received'
        }), 400
    
    # Verify state matches session
    session_user_id = session.get('microsoft_auth_user_id')
    if not session_user_id or session_user_id != state:
        return jsonify({
            'success': False,
            'error': 'Invalid state parameter'
        }), 400
    
    user_id = state
    
    # Get redirect URI from session (set during login)
    redirect_uri = session.get('microsoft_redirect_uri') or get_dynamic_redirect_uri()
    
    print(f"🔄 [Microsoft Callback] Using redirect URI: {redirect_uri}")
    
    # Exchange code for tokens
    token_data = {
        'client_id': MICROSOFT_CLIENT_ID,
        'client_secret': MICROSOFT_CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(MICROSOFT_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        access_token = tokens.get('access_token')
        refresh_token = tokens.get('refresh_token')
        expires_in = tokens.get('expires_in', 3600)  # Default 1 hour
        
        # Get user info from Microsoft Graph
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(f'{MICROSOFT_GRAPH_URL}/me', headers=headers)
        user_response.raise_for_status()
        user_info = user_response.json()
        
        microsoft_user_id = user_info.get('id')
        email = user_info.get('mail') or user_info.get('userPrincipalName')
        display_name = user_info.get('displayName')
        
        # Calculate token expiry
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Store credentials in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if credentials exist
        sql, params = convert_sql_placeholders('''
            SELECT id FROM user_platform_credentials
            WHERE user_id = ? AND platform = ?
        ''', (user_id, 'microsoft'))

        cursor.execute(sql, params)
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing credentials
            sql, params = convert_sql_placeholders('''
                UPDATE user_platform_credentials
                SET access_token = ?,
                    refresh_token = ?,
                    token_expiry = ?,
                    platform_user_id = ?,
                    platform_email = ?,
                    platform_metadata = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND platform = ?
            ''', (access_token, refresh_token, expires_at.isoformat(),
                  microsoft_user_id, email, 
                  f'{{"display_name": "{display_name}", "scopes": {MICROSOFT_SCOPES}}}',
                  user_id, 'microsoft'))
        else:
            # Insert new credentials
            cursor.execute('''
                INSERT INTO user_platform_credentials
                (user_id, platform, access_token, refresh_token, token_expiry,
                 platform_user_id, platform_email, platform_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, 'microsoft', access_token, refresh_token,
                  expires_at.isoformat(), microsoft_user_id, email,
                  f'{{"display_name": "{display_name}", "scopes": {MICROSOFT_SCOPES}}}'))
        
        conn.commit()
        conn.close()
        
        # Clear session
        session.pop('microsoft_auth_user_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Microsoft authentication successful',
            'user': {
                'email': email,
                'display_name': display_name,
                'microsoft_user_id': microsoft_user_id
            },
            'scopes': MICROSOFT_SCOPES,
            'expires_at': expires_at.isoformat()
        })
        
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        try:
            error_data = e.response.json()
            error_msg = error_data.get('error_description', str(e))
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': 'Token exchange failed',
            'details': error_msg
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Authentication failed',
            'details': str(e)
        }), 500


@microsoft_auth_bp.route('/api/auth/microsoft/refresh', methods=['POST'])
def refresh_microsoft_token():
    """Refresh Microsoft access token"""
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id required'
        }), 400
    
    # Get stored credentials
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql, params = convert_sql_placeholders('''
        SELECT refresh_token, platform_user_id, platform_email
        FROM user_platform_credentials
        WHERE user_id = ? AND platform = ?
    ''', (user_id, 'microsoft'))
    cursor.execute(sql, params)
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({
            'success': False,
            'error': 'No Microsoft credentials found for user'
        }), 404
    
    refresh_token = result[0]
    microsoft_user_id = result[1]
    email = result[2]
    
    # Request new tokens
    token_data = {
        'client_id': MICROSOFT_CLIENT_ID,
        'client_secret': MICROSOFT_CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'scope': ' '.join(MICROSOFT_SCOPES)
    }
    
    try:
        response = requests.post(MICROSOFT_TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        new_access_token = tokens.get('access_token')
        new_refresh_token = tokens.get('refresh_token', refresh_token)  # May not return new refresh token
        expires_in = tokens.get('expires_in', 3600)
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql, params = convert_sql_placeholders('''
            UPDATE user_platform_credentials
            SET access_token = ?,
                refresh_token = ?,
                token_expiry = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND platform = ?
        ''', (new_access_token, new_refresh_token, expires_at.isoformat(),
              user_id, 'microsoft'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Token refreshed successfully',
            'access_token': new_access_token,
            'expires_at': expires_at.isoformat()
        })
        
    except requests.exceptions.HTTPError as e:
        error_msg = str(e)
        try:
            error_data = e.response.json()
            error_msg = error_data.get('error_description', str(e))
        except:
            pass
        
        return jsonify({
            'success': False,
            'error': 'Token refresh failed',
            'details': error_msg
        }), 500
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Refresh failed',
            'details': str(e)
        }), 500


@microsoft_auth_bp.route('/api/auth/microsoft/status', methods=['GET'])
def microsoft_auth_status():
    """Check Microsoft authentication status"""
    
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id parameter required'
        }), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql, params = convert_sql_placeholders('''
        SELECT platform_email, platform_user_id, token_expiry, updated_at, platform_metadata
        FROM user_platform_credentials
        WHERE user_id = ? AND platform = ?
    ''', (user_id, 'microsoft'))
    cursor.execute(sql, params)
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({
            'success': True,
            'authenticated': False,
            'message': 'No Microsoft credentials found'
        })
    
    email, microsoft_user_id, token_expiry_str, updated_at, metadata = result
    
    # Check if token is expired
    token_expiry = datetime.fromisoformat(token_expiry_str)
    is_expired = datetime.utcnow() > token_expiry
    
    return jsonify({
        'success': True,
        'authenticated': True,
        'email': email,
        'microsoft_user_id': microsoft_user_id,
        'token_expired': is_expired,
        'token_expiry': token_expiry_str,
        'last_updated': updated_at,
        'metadata': metadata
    })


@microsoft_auth_bp.route('/api/auth/microsoft/revoke', methods=['POST'])
def revoke_microsoft_auth():
    """Revoke Microsoft authentication (remove credentials)"""
    
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'error': 'user_id required'
        }), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql, params = convert_sql_placeholders('''
        DELETE FROM user_platform_credentials
        WHERE user_id = ? AND platform = ?
    ''', (user_id, 'microsoft'))

    
    cursor.execute(sql, params)
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        return jsonify({
            'success': True,
            'message': 'Microsoft authentication revoked successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': 'No Microsoft credentials found to revoke'
        }), 404


# Helper function for tools to get valid access token
def get_microsoft_access_token(user_id):
    """Get valid Microsoft access token for user (auto-refresh if needed)"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    sql, params = convert_sql_placeholders('''
        SELECT access_token, refresh_token, token_expiry
        FROM user_platform_credentials
        WHERE user_id = ? AND platform = ?
    ''', (user_id, 'microsoft'))

    
    cursor.execute(sql, params)
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return {'success': False, 'error': 'No Microsoft credentials found'}
    
    access_token, refresh_token, token_expiry_str = result
    token_expiry = datetime.fromisoformat(token_expiry_str)
    
    # Check if token is expired or expires soon (within 5 minutes)
    if datetime.utcnow() >= (token_expiry - timedelta(minutes=5)):
        # Refresh token
        token_data = {
            'client_id': MICROSOFT_CLIENT_ID,
            'client_secret': MICROSOFT_CLIENT_SECRET,
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'scope': ' '.join(MICROSOFT_SCOPES)
        }
        
        try:
            response = requests.post(MICROSOFT_TOKEN_URL, data=token_data)
            response.raise_for_status()
            tokens = response.json()
            
            new_access_token = tokens.get('access_token')
            new_refresh_token = tokens.get('refresh_token', refresh_token)
            expires_in = tokens.get('expires_in', 3600)
            
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Update database
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE user_platform_credentials
                SET access_token = ?,
                    refresh_token = ?,
                    token_expiry = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND platform = ?
            ''', (new_access_token, new_refresh_token, expires_at.isoformat(),
                  user_id, 'microsoft'))
            
            conn.commit()
            conn.close()
            
            return {'success': True, 'access_token': new_access_token}
            
        except Exception as e:
            return {'success': False, 'error': f'Token refresh failed: {str(e)}'}
    
    return {'success': True, 'access_token': access_token}
