"""
Simple OAuth Token Refresh Endpoint
====================================

Lightweight API endpoint that users can call to proactively refresh their tokens.
This runs in the existing Flask app (no Windows Task Scheduler needed).

Usage:
    Frontend calls: POST /api/auth/refresh-tokens
    Response: {"success": true, "refreshed": ["google", "microsoft"]}

Can be triggered:
1. Manually by user (button in UI)
2. Frontend timer (every 45 minutes)
3. Before any tool execution (automatic)
"""

from flask import Blueprint, jsonify, request
from AI_infrastructure.auth.user_auth import require_auth
from AI_infrastructure.auth.credential_injector import (
    create_google_service_with_user_credentials,
    create_microsoft_service_with_user_credentials
)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

refresh_bp = Blueprint('token_refresh', __name__, url_prefix='/api/auth')


@refresh_bp.route('/refresh-tokens', methods=['POST'])
@require_auth
def refresh_user_tokens():
    """
    Proactively refresh user's OAuth tokens
    
    This endpoint triggers the existing proactive refresh logic
    in credential_injector.py for both Google and Microsoft tokens.
    
    Returns:
        JSON with refresh status for each platform
    """
    user_id = request.user_id
    
    result = {
        'success': True,
        'refreshed': [],
        'errors': []
    }
    
    # Try to refresh Google token
    try:
        # This will trigger proactive refresh if token expires soon
        create_google_service_with_user_credentials(user_id, 'gmail', 'v1')
        result['refreshed'].append('google')
        print(f"✅ Google token refreshed/validated for user {user_id}")
    except Exception as e:
        error_msg = str(e)
        if "does not have Google OAuth credentials" not in error_msg:
            result['errors'].append(f"google: {error_msg}")
            print(f"⚠️ Google token refresh failed for user {user_id}: {e}")
    
    # Try to refresh Microsoft token
    try:
        # This will trigger proactive refresh if token expires soon
        create_microsoft_service_with_user_credentials(user_id, 'graph')
        result['refreshed'].append('microsoft')
        print(f"✅ Microsoft token refreshed/validated for user {user_id}")
    except Exception as e:
        error_msg = str(e)
        if "does not have Microsoft OAuth credentials" not in error_msg:
            result['errors'].append(f"microsoft: {error_msg}")
            print(f"⚠️ Microsoft token refresh failed for user {user_id}: {e}")
    
    # Success if at least one platform refreshed
    if not result['refreshed'] and result['errors']:
        result['success'] = False
    
    return jsonify(result), 200 if result['success'] else 500


@refresh_bp.route('/token-status', methods=['GET'])
@require_auth
def get_token_status():
    """
    Get expiry status of user's OAuth tokens
    
    Returns:
        JSON with token expiry times and refresh recommendations
    """
    user_id = request.user_id
    
    from AI_infrastructure.auth.user_auth import UserAuthManager
    from datetime import datetime, timezone
    
    auth_manager = UserAuthManager()
    
    status = {
        'user_id': user_id,
        'tokens': []
    }
    
    # Check Google token
    try:
        google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
        if google_creds:
            from google.oauth2.credentials import Credentials
            creds = Credentials(
                token=google_creds['access_token'],
                refresh_token=google_creds.get('refresh_token'),
                token_uri=google_creds['token_uri'],
                client_id=google_creds['client_id'],
                client_secret=google_creds['client_secret']
            )
            
            if creds.expiry:
                now = datetime.now(timezone.utc)
                time_remaining = (creds.expiry - now).total_seconds()
                
                status['tokens'].append({
                    'platform': 'google',
                    'email': google_creds.get('email'),
                    'expires_at': creds.expiry.isoformat(),
                    'minutes_remaining': int(time_remaining / 60),
                    'should_refresh': time_remaining < 600  # Less than 10 min
                })
    except Exception as e:
        print(f"⚠️ Could not get Google token status: {e}")
    
    # Check Microsoft token
    try:
        ms_creds = auth_manager.get_user_microsoft_oauth_credentials(user_id)
        if ms_creds:
            expires_at = ms_creds.get('expires_at')
            if expires_at:
                if isinstance(expires_at, str):
                    from datetime import datetime
                    expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                else:
                    expires_dt = expires_at
                
                if expires_dt.tzinfo is None:
                    expires_dt = expires_dt.replace(tzinfo=timezone.utc)
                
                now = datetime.now(timezone.utc)
                time_remaining = (expires_dt - now).total_seconds()
                
                status['tokens'].append({
                    'platform': 'microsoft',
                    'email': ms_creds.get('email'),
                    'expires_at': expires_dt.isoformat(),
                    'minutes_remaining': int(time_remaining / 60),
                    'should_refresh': time_remaining < 600  # Less than 10 min
                })
    except Exception as e:
        print(f"⚠️ Could not get Microsoft token status: {e}")
    
    return jsonify(status), 200
