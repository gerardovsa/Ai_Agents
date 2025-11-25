"""
FILE: AI_infrastructure/auth/credential_injector.py
PURPOSE: Runtime credential injection system - injects user OAuth tokens into agent tool calls

DEPENDENCIES:
- AI_infrastructure.auth.user_auth.UserAuthManager - Retrieves user OAuth tokens from database
- sqlite3 (built-in) - Direct database access to oauth_tokens table
- typing - Type hints for function signatures

EXPORTS:
- inject_user_credentials_into_tool(user_id, tool_name, tool_function, tool_params) -> Any
  * Main function: Injects OAuth credentials and executes tool with user context
  * Supports: Google Workspace, Microsoft 365, and other OAuth platforms
  * Returns: Tool execution result or error dict

- CredentialInjector class:
  * get_google_credentials(user_id: int) -> dict | None - Get Google OAuth token
  * get_microsoft_credentials(user_id: int) -> dict | None - Get Microsoft OAuth token  
  * inject_credentials(tool_name: str, params: dict, user_id: int) -> dict - Add credentials to params

USED BY:
- tools/registry_v3.py - execute_tool() method injects credentials before tool execution
- AI_infrastructure/core/agent_worker.py - Tool execution in agent processing
- AI_infrastructure/routes/agent_routes_v4.py - Agent tool execution endpoints

RELATED FILES:
- AI_infrastructure/auth/user_auth.py - User authentication and OAuth token storage
- google_workspace/google_auth_helper.py - Google API authentication
- google_workspace/oauth_credential_loader.py - OAuth token to Google credentials converter
- data/ai_infrastructure.db - oauth_tokens table (platform, user_id, access_token, refresh_token)

NOTES:
- ARCHITECTURE: Middleware layer between tool registry and tool implementations
- OAUTH FLOW: Retrieves tokens from oauth_tokens table → Injects into tool params → Tool uses for API calls
- PLATFORM DETECTION: Checks tool name prefix (google_, microsoft_, etc.) to determine credential type
- GOOGLE TOOLS: Adds access_token, refresh_token, token_expiry to kwargs
- MICROSOFT TOOLS: Adds access_token to kwargs
- FALLBACK: If no user credentials found, tools fall back to service account (google) or environment vars
- SECURITY: Credentials never logged or exposed in responses
- DATABASE: Direct access to data/ai_infrastructure.db for real-time token retrieval

USAGE EXAMPLE:
    from auth.credential_injector import inject_user_credentials_into_tool
    
    # Before executing a Google tool
    result = inject_user_credentials_into_tool(
        user_id=3,
        tool_name='gmail_send_email',
        tool_function=gmail_send_email,
        tool_params={'to': 'user@example.com', 'subject': 'Test', 'body': 'Hello'}
    )

LAST MODIFIED: 2025-11-02 - Added OAuth token auto-refresh for Google and Microsoft credentials
"""

import os
import sys
import requests
import sqlite3  # Keep for type hints
from shared.db_connection_wrapper import get_connection
from pathlib import Path
from typing import Callable, Dict, Any, Optional
from datetime import datetime, timedelta

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from same directory
from .user_auth import UserAuthManager

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False
    print("⚠️ Google API libraries not available")


# ==================== GOOGLE WORKSPACE CREDENTIAL INJECTION ====================

def create_google_service_with_user_credentials(user_id: int, service_name: str, version: str = 'v1'):
    """
    Create a Google API service using user's OAuth credentials from oauth_tokens table
    
    Args:
        user_id: User ID
        service_name: Google service (gmail, calendar, tasks, forms, drive, docs, sheets, slides)
        version: API version (default: v1)
    
    Returns:
        Authenticated Google API service object
    
    Raises:
        Exception: If credentials not found or invalid
    """
    if not HAS_GOOGLE_LIBS:
        raise Exception("Google API libraries not available - install google-api-python-client")
    
    # Get user's Google OAuth credentials from oauth_tokens table
    auth_manager = UserAuthManager()
    cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
    
    if not cred_dict:
        raise Exception(
            f"User {user_id} does not have Google OAuth credentials. "
            f"Please sign in with Google at /api/auth/google/login"
        )
    
    # Create Google OAuth Credentials object
    credentials = Credentials(
        token=cred_dict['access_token'],
        refresh_token=cred_dict.get('refresh_token'),
        token_uri=cred_dict['token_uri'],
        client_id=cred_dict['client_id'],
        client_secret=cred_dict['client_secret'],
        scopes=cred_dict['scopes']
    )
    
    # ✅ AUTO-REFRESH: Check if token is expired and refresh if needed
    if credentials.expired and credentials.refresh_token:
        print(f"🔄 Google OAuth token expired for user {user_id}, refreshing...")
        try:
            credentials.refresh(Request())
            print(f"✅ Token refreshed successfully")
            
            # ✅ SAVE REFRESHED TOKEN back to database
            _save_refreshed_google_token(user_id, credentials, cred_dict)
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            raise Exception(f"Failed to refresh Google OAuth token: {e}. User may need to re-authenticate.")
    
    # Build the service
    try:
        service = build(service_name, version, credentials=credentials)
        print(f"✅ Created {service_name} v{version} service for user {user_id}")
        return service
    except Exception as e:
        print(f"❌ Failed to create {service_name} service: {e}")
        raise


def _save_refreshed_google_token(user_id: int, credentials: Credentials, original_cred_dict: dict):
    """
    Save refreshed Google OAuth token back to database
    
    Args:
        user_id: User ID
        credentials: Refreshed Google Credentials object
        original_cred_dict: Original credential dictionary (for metadata)
    """
    # Get database path
    from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
    db_path = get_ai_infrastructure_db_path()
    
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Update access token in oauth_tokens table
        cursor.execute('''
            UPDATE oauth_tokens
            SET access_token = %s, expires_at = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s 
            AND platform = 'google'
        ''', (
            credentials.token,
            credentials.expiry.isoformat() if credentials.expiry else None,
            user_id
        ))
        
        # Update refresh token if changed (Google sometimes returns new refresh token)
        if credentials.refresh_token and credentials.refresh_token != original_cred_dict.get('refresh_token'):
            cursor.execute('''
                UPDATE oauth_tokens
                SET refresh_token = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s 
                AND platform = 'google'
            ''', (credentials.refresh_token, user_id))
        
        conn.commit()
        print(f"✅ Saved refreshed Google token for user {user_id}")
        
    except Exception as e:
        print(f"❌ Failed to save refreshed token: {e}")
        conn.rollback()
    finally:
        conn.close()


def _save_refreshed_microsoft_token(user_id: int, access_token: str, refresh_token: str, expires_at):
    """
    Save refreshed Microsoft OAuth token back to database
    
    Args:
        user_id: User ID
        access_token: New access token
        refresh_token: New refresh token (or existing if unchanged)
        expires_at: Token expiry datetime
    """
    conn = get_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Convert expires_at to ISO string if datetime object
        from datetime import datetime
        if isinstance(expires_at, datetime):
            expires_at_str = expires_at.isoformat()
        else:
            expires_at_str = str(expires_at)
        
        # Update access token in oauth_tokens table
        cursor.execute('''
            UPDATE oauth_tokens
            SET access_token = %s, 
                refresh_token = %s,
                expires_at = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s 
            AND platform = 'microsoft'
        ''', (
            access_token,
            refresh_token,
            expires_at_str,
            user_id
        ))
        
        conn.commit()
        print(f"💾 Saved refreshed Microsoft token for user {user_id} (expires: {expires_at_str})")
        
    except Exception as e:
        print(f"❌ Failed to save refreshed Microsoft token: {e}")
        conn.rollback()
    finally:
        conn.close()


def create_microsoft_service_with_user_credentials(user_id: int, service_type: str = 'graph'):
    """
    Get Microsoft 365 OAuth credentials for API calls with automatic token refresh
    
    Args:
        user_id: User ID
        service_type: Type of Microsoft service (graph, outlook, teams, etc.)
    
    Returns:
        Dict with access_token and headers for Microsoft Graph API
    
    Raises:
        Exception: If credentials not found or invalid
    """
    # Get user's Microsoft OAuth credentials from oauth_tokens table
    auth_manager = UserAuthManager()
    cred_dict = auth_manager.get_user_microsoft_oauth_credentials(user_id)
    
    if not cred_dict:
        raise Exception(
            f"User {user_id} does not have Microsoft OAuth credentials. "
            f"Please sign in with Microsoft at /api/auth/microsoft/login"
        )
    
    # ✅ AUTO-REFRESH: Check if token is expired and refresh if needed
    from datetime import datetime, timezone
    import requests
    
    expires_at = cred_dict.get('expires_at')
    if expires_at:
        # Parse expiry time
        if isinstance(expires_at, str):
            try:
                # Try parsing ISO format: "2025-11-25T02:16:07.123456"
                expires_at_str = expires_at.replace('Z', '+00:00')
                if '.' in expires_at_str:
                    # Has microseconds: "2025-11-25T02:16:07.123456" or "2025-11-25 02:16:07.123456"
                    expires_at_str = expires_at_str.replace(' ', 'T')  # Normalize space to T
                    expires_at = datetime.fromisoformat(expires_at_str)
                else:
                    # No microseconds: "2025-11-25T02:16:07" or "2025-11-25 02:16:07"
                    expires_at_str = expires_at_str.replace(' ', 'T')
                    expires_at = datetime.fromisoformat(expires_at_str)
            except Exception as e:
                print(f"⚠️ Failed to parse expires_at '{expires_at}': {e}")
                expires_at = None
        elif isinstance(expires_at, datetime):
            # Already a datetime object
            pass
        else:
            expires_at = None
        
        # Check if expired (add timezone if naive)
        if expires_at:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            if expires_at <= now:
                print(f"🔄 Microsoft OAuth token expired for user {user_id}, refreshing...")
                
                # Refresh the token
                refresh_token = cred_dict.get('refresh_token')
                if not refresh_token:
                    raise Exception(
                        f"Microsoft OAuth token expired and no refresh token available. "
                        f"User {user_id} needs to re-authenticate."
                    )
                
                try:
                    # Call Microsoft token endpoint to refresh
                    token_url = cred_dict['token_uri']
                    refresh_data = {
                        'client_id': cred_dict['client_id'],
                        'client_secret': cred_dict['client_secret'],
                        'refresh_token': refresh_token,
                        'grant_type': 'refresh_token'
                    }
                    
                    response = requests.post(token_url, data=refresh_data)
                    response.raise_for_status()
                    token_data = response.json()
                    
                    # Update credentials with new token
                    new_access_token = token_data.get('access_token')
                    new_refresh_token = token_data.get('refresh_token', refresh_token)  # Use old if not provided
                    expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
                    
                    from datetime import timedelta
                    new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
                    
                    print(f"✅ Token refreshed successfully for user {user_id}")
                    
                    # ✅ SAVE REFRESHED TOKEN back to database
                    _save_refreshed_microsoft_token(user_id, new_access_token, new_refresh_token, new_expires_at)
                    
                    # Update cred_dict with new token
                    cred_dict['access_token'] = new_access_token
                    cred_dict['refresh_token'] = new_refresh_token
                    cred_dict['expires_at'] = new_expires_at
                    
                except Exception as e:
                    print(f"❌ Token refresh failed: {e}")
                    raise Exception(
                        f"Failed to refresh Microsoft OAuth token: {e}. "
                        f"User may need to re-authenticate."
                    )
    
    # Return credentials dict for Microsoft Graph API calls
    microsoft_service = {
        'access_token': cred_dict['access_token'],
        'refresh_token': cred_dict.get('refresh_token'),
        'token_type': 'Bearer',
        'headers': {
            'Authorization': f"Bearer {cred_dict['access_token']}",
            'Content-Type': 'application/json'
        },
        'graph_url': 'https://graph.microsoft.com/v1.0',
        'expires_at': cred_dict.get('expires_at'),
        'user_id': user_id
    }
    
    print(f"✅ Created Microsoft {service_type} service for user {user_id}")
    return microsoft_service


def inject_user_credentials_into_tool(user_id: int, tool_name: str, 
                                     tool_function: Callable, 
                                     tool_params: Dict[str, Any]) -> Any:
    """
    Execute a tool with injected user credentials
    
    This function intercepts tool calls and injects the appropriate user credentials
    based on the tool type.
    
    Args:
        user_id: Current user ID
        tool_name: Name of the tool being executed
        tool_function: The actual tool function to call
        tool_params: Parameters to pass to the tool
    
    Returns:
        Result from the tool execution
    """
    # Determine if this is a Google Workspace tool
    google_tools_prefixes = ['gmail_', 'google_calendar_', 'google_tasks_', 
                             'google_forms_', 'google_docs_', 'google_sheets_',
                             'google_slides_', 'google_drive_', 'gsheets_']
    
    # Determine if this is a Microsoft 365 tool
    microsoft_tools_prefixes = ['microsoft_', 'outlook_', 'teams_', 'onedrive_', 
                                'sharepoint_', 'onenote_', 'planner_', 'todo_', 'word_']
    
    is_google_tool = any(tool_name.startswith(prefix) for prefix in google_tools_prefixes)
    is_microsoft_tool = any(tool_name.startswith(prefix) for prefix in microsoft_tools_prefixes)
    
    if is_google_tool:
        print(f"🔑 Injecting Google credentials for user {user_id} into tool: {tool_name}")
        
        # Add user_id to tool parameters so the tool can retrieve credentials
        tool_params['_user_id'] = user_id
        tool_params['_injected_credentials'] = True
        
        try:
            result = tool_function(**tool_params)
            print(f" Tool {tool_name} executed successfully with user credentials")
            return result
        except Exception as e:
            print(f" Tool {tool_name} failed: {e}")
            raise
    
    elif is_microsoft_tool:
        print(f"🔑 Injecting Microsoft credentials for user {user_id} into tool: {tool_name}")
        
        # Add user_id to tool parameters so the tool can retrieve credentials
        tool_params['_user_id'] = user_id
        tool_params['_injected_credentials'] = True
        
        try:
            result = tool_function(**tool_params)
            print(f" Tool {tool_name} executed successfully with user credentials")
            return result
        except Exception as e:
            print(f" Tool {tool_name} failed: {e}")
            raise
    
    else:
        # Other tool - execute normally
        return tool_function(**tool_params)


# ==================== HELPER FUNCTIONS FOR TOOL IMPLEMENTATIONS ====================

def get_user_gmail_service(user_id: Optional[int] = None, **kwargs):
    """
    Get Gmail service with user credentials
    Call this from gmail tool implementations
    """
    # Check if user_id was injected
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Gmail tools.")
    
    return create_google_service_with_user_credentials(user_id, 'gmail', 'v1')


def get_user_calendar_service(user_id: Optional[int] = None, **kwargs):
    """Get Calendar service with user credentials"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Calendar tools.")
    
    return create_google_service_with_user_credentials(user_id, 'calendar', 'v3')


def get_user_tasks_service(user_id: Optional[int] = None, **kwargs):
    """Get Tasks service with user credentials"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Tasks tools.")
    
    return create_google_service_with_user_credentials(user_id, 'tasks', 'v1')


def get_user_forms_service(user_id: Optional[int] = None, **kwargs):
    """Get Forms service with user credentials"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Forms tools.")
    
    return create_google_service_with_user_credentials(user_id, 'forms', 'v1')


def get_user_drive_service(user_id: Optional[int] = None, **kwargs):
    """Get Drive service with user credentials"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Drive tools.")
    
    return create_google_service_with_user_credentials(user_id, 'drive', 'v3')


def get_user_docs_service(user_id: Optional[int] = None, **kwargs):
    """Get Docs service with user credentials"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Docs tools.")
    
    return create_google_service_with_user_credentials(user_id, 'docs', 'v1')


def get_user_sheets_service(user_id: Optional[int] = None, **kwargs):
    """Get Sheets service with user credentials"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Sheets tools.")
    
    return create_google_service_with_user_credentials(user_id, 'sheets', 'v4')


def get_user_slides_service(user_id: Optional[int] = None, **kwargs):
    """Get Slides service with user credentials"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Slides tools.")
    
    return create_google_service_with_user_credentials(user_id, 'slides', 'v1')


def get_user_meet_service(user_id: Optional[int] = None, **kwargs):
    """Get Meet service with user credentials (uses Calendar API for meetings)"""
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Meet tools.")
    
    return create_google_service_with_user_credentials(user_id, 'calendar', 'v3')


# ==================== MICROSOFT 365 CREDENTIAL INJECTION ====================

def get_microsoft_access_token(user_id: Optional[int] = None, **kwargs) -> str:
    """
    Get Microsoft Graph API access token for a user
    WITH AUTO-REFRESH if token is expired or expiring soon
    
    Args:
        user_id: User ID (or passed via _user_id in kwargs)
        **kwargs: Tool parameters (may contain _user_id)
    
    Returns:
        Microsoft Graph access token (refreshed if needed)
    """
    # Check if user_id was injected
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Microsoft tools.")
    
    # Get user's Microsoft OAuth credentials from database
    auth_manager = UserAuthManager()
    tokens = auth_manager.get_user_microsoft_oauth_credentials(user_id)
    
    if not tokens:
        raise Exception(f"User {user_id} does not have Microsoft OAuth credentials. Please sign in with Microsoft.")
    
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    expires_at_str = tokens.get('expires_at')
    
    if not access_token:
        raise Exception(f"User {user_id} has no Microsoft access token in database.")
    
    # ✅ AUTO-REFRESH: Check if token is expired or expiring soon (within 5 minutes)
    if expires_at_str:
        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace('Z', '+00:00'))
            now = datetime.utcnow()
            
            # Refresh if expired or expiring in next 5 minutes
            if now >= (expires_at - timedelta(minutes=5)):
                print(f"🔄 Microsoft OAuth token expiring soon for user {user_id}, refreshing...")
                
                if not refresh_token:
                    raise Exception(f"No refresh token available for user {user_id}")
                
                # Refresh the token
                new_access_token = _refresh_microsoft_token(user_id, refresh_token)
                
                if new_access_token:
                    access_token = new_access_token
                    print(f"✅ Microsoft token refreshed successfully")
                else:
                    raise Exception("Token refresh failed")
                    
        except Exception as e:
            print(f"⚠️ Token expiry check/refresh failed: {e}")
            # Continue with existing token - might still work
    
    print(f"✅ Retrieved Microsoft access token for user {user_id}")
    return access_token


def _refresh_microsoft_token(user_id: int, refresh_token: str) -> Optional[str]:
    """
    Refresh Microsoft OAuth access token using refresh token
    
    Args:
        user_id: User ID
        refresh_token: Microsoft refresh token
    
    Returns:
        New access token or None if refresh failed
    """
    # Get Microsoft OAuth config
    client_id = os.getenv('MICROSOFT_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_CLIENT_SECRET')
    tenant_id = os.getenv('MICROSOFT_TENANT_ID', 'common')
    
    if not client_id or not client_secret:
        print("❌ Microsoft OAuth config not found in environment")
        return None
    
    # Microsoft token endpoint
    token_url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    
    # Microsoft scopes (standard set)
    scopes = [
        'https://graph.microsoft.com/User.Read',
        'https://graph.microsoft.com/Mail.ReadWrite',
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/Calendars.ReadWrite',
        'https://graph.microsoft.com/Files.ReadWrite.All',
        'offline_access'
    ]
    
    # Request new token
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'scope': ' '.join(scopes)
    }
    
    try:
        response = requests.post(token_url, data=token_data, timeout=10)
        response.raise_for_status()
        tokens = response.json()
        
        new_access_token = tokens.get('access_token')
        new_refresh_token = tokens.get('refresh_token', refresh_token)  # May not return new one
        expires_in = tokens.get('expires_in', 3600)
        
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # ✅ SAVE REFRESHED TOKEN back to database
        from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
        db_path = get_ai_infrastructure_db_path()
        
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        try:
            # Update access token and expiry in oauth_tokens table
            # FIXED: Use 'microsoft' not 'microsoft365' (matches callback route)
            cursor.execute('''
                UPDATE oauth_tokens
                SET access_token = %s, expires_at = %s,
                    updated_at = CURRENT_TIMESTAMP,
                    last_refreshed_at = CURRENT_TIMESTAMP,
                    error_count = 0,
                    last_error = NULL
                WHERE user_id = %s 
                AND platform = 'microsoft'
            ''', (
                new_access_token,
                expires_at.strftime('%Y-%m-%d %H:%M:%S'),
                user_id
            ))
            
            rows_updated = cursor.rowcount
            
            # Update refresh token if changed
            if new_refresh_token != refresh_token:
                cursor.execute('''
                    UPDATE oauth_tokens
                    SET refresh_token = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s 
                    AND platform = 'microsoft'
                ''', (new_refresh_token, user_id))
            
            if rows_updated == 0:
                print(f"⚠️  No rows updated - user {user_id} may not have microsoft token in database")
            else:
                print(f"✅ Updated {rows_updated} row(s) for user {user_id}")
            
            conn.commit()
            print(f"✅ Saved refreshed Microsoft token for user {user_id}")
            
            return new_access_token
            
        except Exception as db_error:
            print(f"❌ Database error saving token: {db_error}")
            conn.rollback()
            return new_access_token  # Return token even if save failed
        finally:
            conn.close()
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Microsoft token refresh HTTP error: {e}")
        
        # Track refresh failure in database
        try:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
            conn = get_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE oauth_tokens
                SET error_count = error_count + 1,
                    last_error = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND platform = 'microsoft'
            ''', (f"Token refresh failed: {str(e)}", user_id))
            
            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"⚠️  Could not update error count: {db_err}")
        
        return None
    except Exception as e:
        print(f"❌ Microsoft token refresh failed: {e}")
        
        # Track refresh failure in database
        try:
            from AI_infrastructure.utils.db_path_helper import get_ai_infrastructure_db_path
            db_path = get_ai_infrastructure_db_path()
            conn = get_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE oauth_tokens
                SET error_count = error_count + 1,
                    last_error = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND platform = 'microsoft'
            ''', (f"Token refresh exception: {str(e)}", user_id))
            
            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"⚠️  Could not update error count: {db_err}")
        
        return None


def get_microsoft_headers(user_id: Optional[int] = None, **kwargs) -> Dict[str, str]:
    """
    Get Microsoft Graph API headers with Bearer token
    
    Args:
        user_id: User ID (or passed via _user_id in kwargs)
        **kwargs: Tool parameters (may contain _user_id)
    
    Returns:
        Dict with Authorization and Content-Type headers
    """
    # Check if user_id was injected
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Microsoft tools.")
    
    # Get Microsoft service credentials
    microsoft_service = create_microsoft_service_with_user_credentials(user_id, 'graph')
    
    return microsoft_service.get('headers', {})


# ==================== INHOUSE PRINT DATABASE CREDENTIAL INJECTION ====================

def get_inhouse_print_db_credentials(user_id: Optional[int] = None, **kwargs) -> Dict[str, Any]:
    """
    Get InHouse Print SQL Server database credentials
    
    Uses SQL authentication from database-config.json
    No user-specific credentials needed (shared database)
    
    Args:
        user_id: User ID (not used for database - shared access)
        **kwargs: Tool parameters
    
    Returns:
        Dict with server, database, username, password, driver
    """
    import json
    from pathlib import Path
    
    # Load config from data/database-config.json (CORRECT LOCATION)
    config_path = Path(__file__).parent.parent.parent / 'data' / 'database-config.json'
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Parse connection string
        conn_str = config['DatabaseConnections']['Primary']['ConnectionString']
        parts = conn_str.split(';')
        
        server = None
        username = None
        password = None
        database = None
        
        for part in parts:
            if 'data source=' in part.lower():
                server = part.split('=')[1]
            elif 'user id=' in part.lower():
                username = part.split('=')[1]
            elif 'password=' in part.lower():
                password = part.split('=')[1]
            elif 'database=' in part.lower():
                database = part.split('=')[1]
        
        return {
            'server': server or '3.25.76.138\\INHPSQLSERVER',
            'database': database or 'InHousePrint',
            'username': username or 'sa',
            'password': password or '',
            'driver': '{ODBC Driver 17 for SQL Server}',
            'config_path': str(config_path)
        }
        
    except FileNotFoundError:
        # Fallback to hardcoded values (not recommended for production)
        print("⚠️ database-config.json not found, using default credentials")
        return {
            'server': '3.25.76.138\\INHPSQLSERVER',
            'database': 'InHousePrint',
            'username': 'sa',
            'password': 'Jack2011',
            'driver': '{ODBC Driver 17 for SQL Server}'
        }


# ==================== EXPORT FOR TOOL IMPLEMENTATIONS ====================

__all__ = [
    # Core injection functions
    'inject_user_credentials_into_tool',
    'create_google_service_with_user_credentials',
    'create_microsoft_service_with_user_credentials',
    
    # Google Workspace helper functions
    'get_user_gmail_service',
    'get_user_calendar_service',
    'get_user_tasks_service',
    'get_user_forms_service',
    'get_user_drive_service',
    'get_user_docs_service',
    'get_user_sheets_service',
    'get_user_slides_service',
    'get_user_meet_service',
    
    # Microsoft 365 helper functions
    'get_microsoft_access_token',
    'get_microsoft_headers',
    
    # InHouse Print database credentials
    'get_inhouse_print_db_credentials'
]
