"""
OAuth Routes for Google Workspace Integration
==============================================

Handles OAuth 2.0 flow for client authentication
"""

from flask import Blueprint, request, redirect, session, jsonify, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import os
from datetime import datetime
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google_workspace.oauth_manager import UNIFIED_SCOPES, get_oauth_config
from AI_infrastructure.auth.user_auth import user_auth_manager


oauth_bp = Blueprint('oauth', __name__, url_prefix='/api/oauth')


@oauth_bp.route('/workspace/start', methods=['GET'])
def oauth_workspace_start():
    """
    Start OAuth flow for Google Workspace
    
    GET /api/oauth/workspace/start?mode=signin|signup
    
    Initiates OAuth 2.0 flow with unified scopes:
    - Gmail, Calendar, Tasks, Forms
    - Docs, Sheets, Slides, Drive
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
    """
    try:
        # Verify state
        state = request.args.get('state')
        if state != session.get('oauth_state'):
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
        
        # Check if user exists
        # For now, we'll use session to pass data to dashboard
        # In production, store encrypted token in database
        
        session['user_email'] = user_email
        session['oauth_connected'] = True
        session['oauth_token'] = json.dumps(token_data)
        
        # Store token in user's token file (temporary solution)
        token_file = config.get('token_file', 'token_unified_web.json')
        
        # Add user email to token file name for multi-user support
        token_file_user = token_file.replace('.json', f'_{user_email.replace("@", "_at_")}.json')
        
        with open(token_file_user, 'w') as f:
            json.dump(token_data, f, indent=2)
        
        print(f"💾 Token saved: {token_file_user}")
        
        # Redirect to dashboard with success message
        success_msg = f"Google Workspace connected! All services ready."
        return redirect(f'/dashboard?success={success_msg}')
        
    except Exception as e:
        print(f"❌ OAuth callback error: {e}")
        import traceback
        traceback.print_exc()
        return redirect(f'/login?error={str(e)}')


@oauth_bp.route('/status', methods=['GET'])
def oauth_status():
    """
    Check OAuth connection status
    
    GET /api/oauth/status
    
    Returns OAuth connection status for current user
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
