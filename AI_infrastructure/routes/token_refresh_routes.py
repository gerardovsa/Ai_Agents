"""
Token Refresh Routes
File: AI_infrastructure/routes/token_refresh_routes.py

Simple OAuth Token Refresh Endpoint (ENHANCED VERSION)
=======================================================

✅ NO CURSOR MANAGEMENT ISSUES - All database operations handled by external classes
✅ ENHANCEMENTS: Logging, error handling, validation, timezone handling

Lightweight API endpoint that users can call to proactively refresh their tokens.
This runs in the existing Flask app (no Windows Task Scheduler needed).

Usage:
    Frontend calls: POST /api/auth/refresh-tokens
    Response: {"success": true, "refreshed": ["google", "microsoft"]}

Can be triggered:
1. Manually by user (button in UI)
2. Frontend timer (every 45 minutes)
3. Before any tool execution (automatic)

NOTE: All database cursor management is handled internally by:
      - credential_injector.py functions
      - UserAuthManager class methods
      This file has ZERO direct database operations.
"""

from flask import Blueprint, jsonify, request
from AI_infrastructure.auth.user_auth import require_auth
from AI_infrastructure.auth.credential_injector import (
    create_google_service_with_user_credentials,
    create_microsoft_service_with_user_credentials
)
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
refresh_bp = Blueprint('token_refresh', __name__, url_prefix='/api/auth')

# ======================================================================
# CONSTANTS
# ======================================================================

# Platforms that support token refresh
SUPPORTED_PLATFORMS = ['google', 'microsoft']

# Minimum time before expiry to trigger refresh (10 minutes)
REFRESH_THRESHOLD_SECONDS = 600

# Error messages that indicate missing credentials (not errors)
MISSING_CREDENTIAL_MESSAGES = [
    "does not have Google OAuth credentials",
    "does not have Microsoft OAuth credentials",
    "No Google credentials found",
    "No Microsoft credentials found"
]

# ======================================================================
# HELPER FUNCTIONS
# ======================================================================

def is_missing_credential_error(error_message: str) -> bool:
    """
    Check if error indicates missing credentials (not an error condition)
    
    Args:
        error_message: Error message string
    
    Returns:
        bool: True if this is a "missing credential" error
    """
    error_lower = error_message.lower()
    return any(msg.lower() in error_lower for msg in MISSING_CREDENTIAL_MESSAGES)


def normalize_datetime_to_utc(dt) -> datetime:
    """
    Normalize datetime to UTC timezone
    
    Args:
        dt: datetime object or ISO string
    
    Returns:
        datetime: UTC datetime with timezone
    """
    # Handle string input
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
    
    # Add UTC timezone if naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt


def format_error_response(message: str, status_code: int = 500) -> tuple:
    """
    Format error response
    
    Args:
        message: Error message
        status_code: HTTP status code
    
    Returns:
        tuple: (response, status_code)
    """
    logger.error(f"Error response: {message} (status: {status_code})")
    return jsonify({
        'success': False,
        'error': message
    }), status_code


def format_success_response(data: Dict[str, Any], status_code: int = 200) -> tuple:
    """
    Format success response
    
    Args:
        data: Response data
        status_code: HTTP status code
    
    Returns:
        tuple: (response, status_code)
    """
    data['success'] = True
    return jsonify(data), status_code


# ======================================================================
# ENDPOINTS
# ======================================================================

@refresh_bp.route('/refresh-tokens', methods=['POST'])
@require_auth
def refresh_user_tokens():
    """
    Proactively refresh user's OAuth tokens
    
    POST /api/auth/refresh-tokens
    
    This endpoint triggers the existing proactive refresh logic
    in credential_injector.py for both Google and Microsoft tokens.
    
    Request:
        Headers:
            Authorization: Bearer <jwt_token>
    
    Response:
        {
            "success": true,
            "refreshed": ["google", "microsoft"],
            "errors": [],
            "skipped": ["platform_name"]
        }
    
    Status Codes:
        200: Success (at least one token refreshed)
        401: Unauthorized (no valid auth token)
        500: Error (all refresh attempts failed)
    
    NOTE: All database operations handled by credential_injector functions.
          No direct cursor management in this file.
    """
    try:
        # Get user_id from require_auth decorator
        user_id = request.user_id
        
        logger.info(f"Token refresh requested for user {user_id}")
        
        result = {
            'refreshed': [],
            'validated': [],
            'errors': [],
            'skipped': []
        }
        
        # ====================================================================
        # REFRESH GOOGLE TOKEN
        # ====================================================================
        # NOTE: create_google_service_with_user_credentials() handles all
        #       database operations internally (cursor management done there)
        try:
            logger.debug(f"Attempting Google token refresh for user {user_id}")
            
            _, refresh_status = create_google_service_with_user_credentials(
                user_id,
                'gmail',
                'v1',
                return_refresh_status=True,
            )

            if refresh_status == 'refreshed':
                result['refreshed'].append('google')
                logger.info(f"✅ Google token refreshed for user {user_id}")
            else:
                result['validated'].append('google')
                logger.info(f"✅ Google token validated for user {user_id} ({refresh_status})")
        
        except Exception as e:
            error_msg = str(e)
            
            if is_missing_credential_error(error_msg):
                # User doesn't have Google credentials - not an error
                result['skipped'].append('google')
                logger.debug(f"Google credentials not configured for user {user_id}")
            else:
                # Actual error occurred
                result['errors'].append({
                    'platform': 'google',
                    'error': error_msg
                })
                logger.warning(f"⚠️ Google token refresh failed for user {user_id}: {e}")
        
        # ====================================================================
        # REFRESH MICROSOFT TOKEN
        # ====================================================================
        # NOTE: create_microsoft_service_with_user_credentials() handles all
        #       database operations internally (cursor management done there)
        try:
            logger.debug(f"Attempting Microsoft token refresh for user {user_id}")
            
            # This will trigger proactive refresh if token expires soon
            create_microsoft_service_with_user_credentials(user_id, 'graph')
            
            result['refreshed'].append('microsoft')
            logger.info(f"✅ Microsoft token refreshed/validated for user {user_id}")
        
        except Exception as e:
            error_msg = str(e)
            
            if is_missing_credential_error(error_msg):
                # User doesn't have Microsoft credentials - not an error
                result['skipped'].append('microsoft')
                logger.debug(f"Microsoft credentials not configured for user {user_id}")
            else:
                # Actual error occurred
                result['errors'].append({
                    'platform': 'microsoft',
                    'error': error_msg
                })
                logger.warning(f"⚠️ Microsoft token refresh failed for user {user_id}: {e}")
        
        # ====================================================================
        # BUILD RESPONSE
        # ====================================================================
        
        # Success if at least one platform refreshed or validated
        if result['refreshed'] or result['validated']:
            logger.info(
                f"Token refresh completed for user {user_id}: "
                f"refreshed={result['refreshed']}, validated={result['validated']}"
            )
            return format_success_response(result, 200)
        
        # All platforms skipped (no credentials configured)
        if result['skipped'] and not result['errors']:
            logger.info(f"No tokens to refresh for user {user_id} (no credentials configured)")
            return format_success_response(result, 200)
        
        # All attempts failed with errors
        logger.error(f"Token refresh failed for user {user_id}: {result['errors']}")
        return format_error_response(
            f"Token refresh failed: {', '.join(e['platform'] for e in result['errors'])}",
            500
        )
    
    except AttributeError as e:
        # request.user_id not set (require_auth decorator failed?)
        logger.error(f"Authentication error in refresh_user_tokens: {e}")
        return format_error_response("Authentication required", 401)
    
    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error in refresh_user_tokens: {e}")
        return format_error_response(f"Internal server error: {str(e)}", 500)


@refresh_bp.route('/token-status', methods=['GET'])
@require_auth
def get_token_status():
    """
    Get expiry status of user's OAuth tokens
    
    GET /api/auth/token-status
    
    Request:
        Headers:
            Authorization: Bearer <jwt_token>
    
    Response:
        {
            "success": true,
            "user_id": 1,
            "tokens": [
                {
                    "platform": "google",
                    "email": "user@example.com",
                    "expires_at": "2025-01-08T15:30:00+00:00",
                    "minutes_remaining": 45,
                    "should_refresh": false
                },
                {
                    "platform": "microsoft",
                    "email": "user@example.com",
                    "expires_at": "2025-01-08T15:00:00+00:00",
                    "minutes_remaining": 15,
                    "should_refresh": false
                }
            ]
        }
    
    Status Codes:
        200: Success
        401: Unauthorized (no valid auth token)
        500: Internal server error
    
    NOTE: All database operations handled by UserAuthManager class.
          No direct cursor management in this file.
    """
    try:
        # Get user_id from require_auth decorator
        user_id = request.user_id
        
        logger.info(f"Token status requested for user {user_id}")
        
        from AI_infrastructure.auth.user_auth import UserAuthManager
        
        # NOTE: UserAuthManager handles all database operations internally
        #       (cursor management done in that class)
        auth_manager = UserAuthManager()
        
        status = {
            'user_id': user_id,
            'tokens': []
        }
        
        # ====================================================================
        # CHECK GOOGLE TOKEN
        # ====================================================================
        # NOTE: get_user_google_oauth_credentials() handles all database
        #       operations internally (cursor management done there)
        try:
            logger.debug(f"Fetching Google token status for user {user_id}")
            
            google_creds = auth_manager.get_user_google_oauth_credentials(user_id)
            
            if google_creds:
                expires_at = google_creds.get('expires_at')
                if expires_at:
                    expiry_utc = normalize_datetime_to_utc(expires_at)
                    now = datetime.now(timezone.utc)
                    time_remaining = (expiry_utc - now).total_seconds()

                    token_info = {
                        'platform': 'google',
                        'email': google_creds.get('email'),
                        'expires_at': expiry_utc.isoformat(),
                        'minutes_remaining': int(time_remaining / 60),
                        'should_refresh': time_remaining < REFRESH_THRESHOLD_SECONDS
                    }

                    status['tokens'].append(token_info)
                    logger.debug(f"Google token for user {user_id}: {int(time_remaining/60)} minutes remaining")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not get Google token status for user {user_id}: {e}")
        
        # ====================================================================
        # CHECK MICROSOFT TOKEN
        # ====================================================================
        # NOTE: get_user_microsoft_oauth_credentials() handles all database
        #       operations internally (cursor management done there)
        try:
            logger.debug(f"Fetching Microsoft token status for user {user_id}")
            
            ms_creds = auth_manager.get_user_microsoft_oauth_credentials(user_id)
            
            if ms_creds:
                expires_at = ms_creds.get('expires_at')
                
                if expires_at:
                    expires_dt = normalize_datetime_to_utc(expires_at)
                    now = datetime.now(timezone.utc)
                    time_remaining = (expires_dt - now).total_seconds()
                    
                    token_info = {
                        'platform': 'microsoft',
                        'email': ms_creds.get('email'),
                        'expires_at': expires_dt.isoformat(),
                        'minutes_remaining': int(time_remaining / 60),
                        'should_refresh': time_remaining < REFRESH_THRESHOLD_SECONDS
                    }
                    
                    status['tokens'].append(token_info)
                    logger.debug(f"Microsoft token for user {user_id}: {int(time_remaining/60)} minutes remaining")
        
        except Exception as e:
            logger.warning(f"⚠️ Could not get Microsoft token status for user {user_id}: {e}")
        
        # ====================================================================
        # BUILD RESPONSE
        # ====================================================================
        
        logger.info(f"Retrieved status for {len(status['tokens'])} tokens for user {user_id}")
        return format_success_response(status, 200)
    
    except AttributeError as e:
        # request.user_id not set (require_auth decorator failed?)
        logger.error(f"Authentication error in get_token_status: {e}")
        return format_error_response("Authentication required", 401)
    
    except Exception as e:
        # Unexpected error
        logger.exception(f"Unexpected error in get_token_status: {e}")
        return format_error_response(f"Internal server error: {str(e)}", 500)


# ======================================================================
# STARTUP LOGGING
# ======================================================================
logger.info("="*80)
logger.info("Token Refresh Routes loaded (Enhanced Version)")
logger.info("   - ✅ NO CURSOR MANAGEMENT ISSUES (no direct DB operations)")
logger.info("   - ✅ All database operations handled by credential_injector & UserAuthManager")
logger.info("   - ✅ Enhanced logging, error handling, and validation")
logger.info(f"   - Endpoints: 2 routes registered")
logger.info(f"   - Supported platforms: {', '.join(SUPPORTED_PLATFORMS)}")
logger.info(f"   - Refresh threshold: {REFRESH_THRESHOLD_SECONDS // 60} minutes")
logger.info("="*80)