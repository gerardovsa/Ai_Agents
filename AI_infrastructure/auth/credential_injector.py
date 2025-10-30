"""
Credential Injection System for Agent Tools
============================================

Injects user credentials into Google Workspace API calls when agents execute tools.
This allows agents to use the user's Google OAuth tokens stored in the database.

Usage:
    from auth.credential_injector import inject_user_credentials_into_tool
    
    # Before executing a Google tool
    result = inject_user_credentials_into_tool(
        user_id=3,
        tool_name='gmail_send_email',
        tool_function=gmail_send_email,
        tool_params={'to': 'user@example.com', 'subject': 'Test', 'body': 'Hello'}
    )
"""

import os
import sys
from pathlib import Path
from typing import Callable, Dict, Any, Optional

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import from same directory
from .user_auth import UserAuthManager

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    HAS_GOOGLE_LIBS = True
except ImportError:
    HAS_GOOGLE_LIBS = False
    print("⚠️ Google API libraries not available")


# ==================== GOOGLE WORKSPACE CREDENTIAL INJECTION ====================

def create_google_service_with_user_credentials(user_id: int, service_name: str, version: str = 'v1'):
    """
    Create a Google API service using user's OAuth credentials from database
    
    Args:
        user_id: User ID
        service_name: Google service (gmail, calendar, tasks, forms, drive)
        version: API version (default: v1)
    
    Returns:
        Authenticated Google API service object
    """
    if not HAS_GOOGLE_LIBS:
        raise Exception("Google API libraries not available - install google-api-python-client")
    
    # Get user's Google OAuth credentials from database
    auth_manager = UserAuthManager()
    cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
    
    if not cred_dict:
        raise Exception(f"User {user_id} does not have Google OAuth credentials. Please sign in with Google.")
    
    # Create Google OAuth Credentials object
    credentials = Credentials(
        token=cred_dict['access_token'],
        refresh_token=cred_dict.get('refresh_token'),
        token_uri=cred_dict['token_uri'],
        client_id=cred_dict['client_id'],
        client_secret=cred_dict['client_secret'],
        scopes=cred_dict['scopes']
    )
    
    # Build the service
    service = build(service_name, version, credentials=credentials)
    
    print(f"✅ Created {service_name} service for user {user_id}")
    return service


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
            print(f"✅ Tool {tool_name} executed successfully with user credentials")
            return result
        except Exception as e:
            print(f"❌ Tool {tool_name} failed: {e}")
            raise
    
    elif is_microsoft_tool:
        print(f"🔑 Injecting Microsoft credentials for user {user_id} into tool: {tool_name}")
        
        # Add user_id to tool parameters so the tool can retrieve credentials
        tool_params['_user_id'] = user_id
        tool_params['_injected_credentials'] = True
        
        try:
            result = tool_function(**tool_params)
            print(f"✅ Tool {tool_name} executed successfully with user credentials")
            return result
        except Exception as e:
            print(f"❌ Tool {tool_name} failed: {e}")
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


# ==================== MICROSOFT 365 CREDENTIAL INJECTION ====================

def get_microsoft_access_token(user_id: Optional[int] = None, **kwargs) -> str:
    """
    Get Microsoft Graph API access token for a user
    
    Args:
        user_id: User ID (or passed via _user_id in kwargs)
        **kwargs: Tool parameters (may contain _user_id)
    
    Returns:
        Microsoft Graph access token
    """
    # Check if user_id was injected
    if '_user_id' in kwargs:
        user_id = kwargs['_user_id']
    
    if not user_id:
        raise Exception("No user_id provided. User must be authenticated to use Microsoft tools.")
    
    # Get user's Microsoft OAuth credentials from database
    auth_manager = UserAuthManager()
    tokens = auth_manager.get_microsoft_tokens(user_id)
    
    if not tokens:
        raise Exception(f"User {user_id} does not have Microsoft OAuth credentials. Please sign in with Microsoft.")
    
    access_token = tokens.get('access_token')
    if not access_token:
        raise Exception(f"User {user_id} has no valid Microsoft access token. Please re-authenticate.")
    
    print(f"✅ Retrieved Microsoft access token for user {user_id}")
    return access_token


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
    
    # Load config from AI_infrastructure/data/database-config.json
    config_path = Path(__file__).parent.parent / 'data' / 'database-config.json'
    
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
    'inject_user_credentials_into_tool',
    'create_google_service_with_user_credentials',
    'get_user_gmail_service',
    'get_user_calendar_service',
    'get_user_tasks_service',
    'get_user_forms_service',
    'get_user_drive_service',
    'get_microsoft_access_token',
    'get_inhouse_print_db_credentials'
]
