"""
FILE: google_workspace/google_auth_helper.py
PURPOSE: Unified Google Workspace API authentication - handles OAuth and service account credentials

DEPENDENCIES:
- google.oauth2.service_account - Service account authentication (fallback)
- google.oauth2.credentials - OAuth 2.0 user credentials
- googleapiclient.discovery.build - Google API client builder
- google_workspace.oauth_credential_loader.build_service_with_oauth - User OAuth token loader
- dotenv - Load service account credentials from .env.master

EXPORTS:
- build_gmail_service(injected_credentials=None) -> Resource - Gmail API v1 client
- build_drive_service(injected_credentials=None) -> Resource - Drive API v3 client
- build_docs_service(injected_credentials=None) -> Resource - Docs API v1 client
- build_sheets_service(injected_credentials=None) -> Resource - Sheets API v4 client
- build_calendar_service(injected_credentials=None) -> Resource - Calendar API v3 client
- build_forms_service(injected_credentials=None) -> Resource - Forms API v1 client
- build_tasks_service(injected_credentials=None) -> Resource - Tasks API v1 client
- build_slides_service(injected_credentials=None) -> Resource - Slides API v1 client
- build_meet_service(injected_credentials=None) -> Resource - Meet API v2 client
- build_analytics_service(injected_credentials=None) -> Resource - Analytics Reporting API v4 client

USED BY:
- google_workspace/gmail.py - 45 Gmail functions (send, list, search, etc.)
- google_workspace/google_docs.py - 38 Docs functions (create, update, format, etc.)
- google_workspace/google_drive.py - 22 Drive functions (upload, download, share, etc.)
- google_workspace/google_calendar.py - 11 Calendar functions (create event, list, etc.)
- google_workspace/google_sheets.py - Sheets operations (read, write, format)
- google_workspace/google_forms.py - 98 Forms functions (create, list, responses)
- google_workspace/google_tasks.py - 25 Tasks functions (create, list, update)
- google_workspace/google_slides.py - 19 Slides functions (create, update, present)
- google_workspace/google_meet.py - 23 Meet functions (create meeting, manage)
- google_workspace/google_analytics.py - 19 Analytics functions (reports, metrics)

RELATED FILES:
- google_workspace/oauth_credential_loader.py - Converts oauth_tokens DB records to Google credentials
- AI_infrastructure/auth/credential_injector.py - Retrieves user OAuth tokens from database
- data/ai_infrastructure.db - oauth_tokens table (user_id, platform='google', access_token, refresh_token)
- .env.master - Service account credentials (GOOGLE_SERVICE_ACCOUNT_EMAIL, GOOGLE_PRIVATE_KEY)

NOTES:
- AUTHENTICATION PRIORITY:
  1. User OAuth credentials (from injected_credentials param) ← PREFERRED
  2. Service account credentials (from .env.master) ← FALLBACK
- OAUTH FORMAT: injected_credentials = {'access_token': str, 'refresh_token': str, 'token_expiry': str}
- SERVICE ACCOUNT: Requires GOOGLE_SERVICE_ACCOUNT_EMAIL and GOOGLE_PRIVATE_KEY in .env.master
- SCOPES: Each service uses appropriate OAuth scopes (gmail.modify, drive, documents, etc.)
- TOKEN REFRESH: oauth_credential_loader handles automatic token refresh
- PERFORMANCE: Services are built per-request (no caching) to use latest credentials
- ERROR HANDLING: Returns None if authentication fails, tools should handle gracefully
- MULTI-TENANT: Each user's OAuth token used when available, service account shared otherwise

LAST MODIFIED: 2025-11-02 - Enhanced OAuth integration with oauth_tokens database table
"""

import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables from .env.master (if not already loaded)
try:
    from dotenv import load_dotenv
    env_master = Path(__file__).parent.parent / '.env.master'
    if env_master.exists():
        load_dotenv(env_master, override=False)  # Don't override if already set
except ImportError:
    pass  # dotenv not installed, environment should be set externally

# Import OAuth credential loader
try:
    from .oauth_credential_loader import build_service_with_oauth
    HAS_OAUTH_LOADER = True
    print("[OK] OAuth credential loader available - will use user OAuth credentials")
except ImportError as e:
    HAS_OAUTH_LOADER = False
    print(f"[WARN] OAuth credential loader not available - using service account only (error: {e})")

# Service account credential cache
_SERVICE_CACHE = {}

def get_service_account_credentials(scopes):
    """
    Get service account credentials with specified scopes.
    Supports two methods:
    1. Service account JSON file (recommended): GOOGLE_APPLICATION_CREDENTIALS
    2. Individual environment variables: SERVICE_ACCOUNT_EMAIL, etc.
    
    Args:
        scopes: List of OAuth2 scopes needed
        
    Returns:
        google.oauth2.service_account.Credentials object
    """
    
    # Method 1: Try JSON file first (recommended)
    credentials_file = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if credentials_file and os.path.exists(credentials_file):
        print(f"🔑 Using service account from file: {credentials_file}")
        credentials = service_account.Credentials.from_service_account_file(
            credentials_file,
            scopes=scopes
        )
        return credentials
    
    # Method 2: Fall back to individual environment variables (legacy)
    service_account_email = os.getenv('SERVICE_ACCOUNT_EMAIL')
    service_account_private_key = os.getenv('SERVICE_ACCOUNT_PRIVATE_KEY')
    service_account_private_key_id = os.getenv('SERVICE_ACCOUNT_PRIVATE_KEY_ID')
    project_id = os.getenv('SERVICE_ACCOUNT_PROJECT_ID', 'colab-ai-processor')
    
    if not all([service_account_email, service_account_private_key, service_account_private_key_id]):
        raise Exception(
            " Google Workspace service account not configured!\n\n"
            "Option 1 (Recommended): Use service account JSON file\n"
            "  Set: GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json\n"
            "  Example: GOOGLE_APPLICATION_CREDENTIALS=C:\\Users\\gpoli\\GIT\\AI_agents\\vsa-anythingllm-project-ab7c8caf8c47.json\n\n"
            "Option 2: Use individual environment variables\n"
            "  Set: SERVICE_ACCOUNT_EMAIL, SERVICE_ACCOUNT_PRIVATE_KEY, SERVICE_ACCOUNT_PRIVATE_KEY_ID\n"
        )
    
    print(f"🔑 Using service account from environment variables")
    
    # Clean up the private key (handle escaped newlines)
    private_key = service_account_private_key.replace('\\n', '\n')
    
    # Build credentials info
    credentials_info = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": service_account_private_key_id,
        "private_key": private_key,
        "client_email": service_account_email,
        "client_id": "",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{service_account_email}"
    }
    
    # Create credentials from service account info
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=scopes
    )
    
    return credentials


def build_docs_service(user_id=None, injected_credentials=None, _user_id=None, **kwargs):
    """Get authenticated Google Docs API service
    
    Args:
        user_id: User ID for OAuth credentials from database
        injected_credentials: OAuth credentials dict (from database - LEGACY)
        _user_id: Injected user_id from credential_injector (PREFERRED)
        **kwargs: Additional parameters (catches _injected_credentials flag)
    
    Returns:
        Authenticated Docs service using either user OAuth or service account
    """
    # Priority 1: Use _user_id from credential injector (NEW METHOD)
    effective_user_id = _user_id or user_id
    
    if effective_user_id and HAS_OAUTH_LOADER:
        print(f"🔑 [NEW PATH] Building Docs service with user_id={effective_user_id} from oauth_tokens database")
        
        scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive'
        ]
        
        service = build_service_with_oauth(
            user_id=effective_user_id,
            service_name='docs',
            version='v1',
            scopes=scopes
        )
        
        if service:
            print(f"✅ Docs service created with user {effective_user_id}'s OAuth credentials from database")
            return service
        else:
            print(f"⚠️  Failed to load OAuth credentials, falling back to service account")
    
    # Priority 2: Legacy injected credentials (OLD METHOD)
    if user_id and injected_credentials:
        print(f"🔑 [LEGACY PATH] Building Docs service with injected_credentials dict")
        from google.oauth2.credentials import Credentials
        
        scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials(
            token=injected_credentials.get('access_token'),
            refresh_token=injected_credentials.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=injected_credentials.get('client_id'),
            client_secret=injected_credentials.get('client_secret'),
            scopes=scopes
        )
        
        service = build('docs', 'v1', credentials=credentials)
        print(f"✅ Docs service created with user {user_id}'s credentials (legacy path)")
        return service
    
    # Priority 3: Fall back to service account (cached)
    print(f"⚠️  No user OAuth credentials - using service account")
    cache_key = 'docs_v1'
    
    if cache_key in _SERVICE_CACHE:
        return _SERVICE_CACHE[cache_key]
    
    scopes = [
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive'
    ]
    
    credentials = get_service_account_credentials(scopes)
    service = build('docs', 'v1', credentials=credentials)
    
    _SERVICE_CACHE[cache_key] = service
    return service


def build_drive_service(user_id=None, injected_credentials=None):
    """Get authenticated Google Drive API service
    
    Args:
        user_id: User ID for OAuth credentials from database
        injected_credentials: OAuth credentials dict (from database)
    
    Returns:
        Authenticated Drive service using either user OAuth or service account
    """
    # If user credentials provided, use them (don't cache per-user services)
    if user_id and injected_credentials:
        print(f"🔑 Building Drive service with user {user_id}'s OAuth credentials")
        from google.oauth2.credentials import Credentials
        
        scopes = [
            'https://www.googleapis.com/auth/drive'
        ]
        
        credentials = Credentials(
            token=injected_credentials.get('access_token'),
            refresh_token=injected_credentials.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=injected_credentials.get('client_id'),
            client_secret=injected_credentials.get('client_secret'),
            scopes=scopes
        )
        
        service = build('drive', 'v3', credentials=credentials)
        print(f" Drive service created with user {user_id}'s credentials")
        return service
    
    # Fall back to service account (cached)
    cache_key = 'drive_v3'
    
    if cache_key in _SERVICE_CACHE:
        return _SERVICE_CACHE[cache_key]
    
    scopes = [
        'https://www.googleapis.com/auth/drive'
    ]
    
    credentials = get_service_account_credentials(scopes)
    service = build('drive', 'v3', credentials=credentials)
    
    _SERVICE_CACHE[cache_key] = service
    return service


def build_gmail_service():
    """Get authenticated Gmail API service"""
    cache_key = 'gmail_v1'
    
    if cache_key in _SERVICE_CACHE:
        return _SERVICE_CACHE[cache_key]
    
    scopes = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    credentials = get_service_account_credentials(scopes)
    service = build('gmail', 'v1', credentials=credentials)
    
    _SERVICE_CACHE[cache_key] = service
    return service


def build_calendar_service():
    """Get authenticated Google Calendar API service"""
    cache_key = 'calendar_v3'
    
    if cache_key in _SERVICE_CACHE:
        return _SERVICE_CACHE[cache_key]
    
    scopes = [
        'https://www.googleapis.com/auth/calendar'
    ]
    
    credentials = get_service_account_credentials(scopes)
    service = build('calendar', 'v3', credentials=credentials)
    
    _SERVICE_CACHE[cache_key] = service
    return service


def build_forms_service():
    """Get authenticated Google Forms API service"""
    cache_key = 'forms_v1'
    
    if cache_key in _SERVICE_CACHE:
        return _SERVICE_CACHE[cache_key]
    
    scopes = [
        'https://www.googleapis.com/auth/forms.body',
        'https://www.googleapis.com/auth/forms.responses.readonly',
        'https://www.googleapis.com/auth/drive'
    ]
    
    credentials = get_service_account_credentials(scopes)
    service = build('forms', 'v1', credentials=credentials)
    
    _SERVICE_CACHE[cache_key] = service
    return service


def build_analytics_service():
    """Get authenticated Google Analytics Data API service"""
    cache_key = 'analyticsdata_v1beta'
    
    if cache_key in _SERVICE_CACHE:
        return _SERVICE_CACHE[cache_key]
    
    scopes = [
        'https://www.googleapis.com/auth/analytics.readonly'
    ]
    
    credentials = get_service_account_credentials(scopes)
    service = build('analyticsdata', 'v1beta', credentials=credentials)
    
    _SERVICE_CACHE[cache_key] = service
    return service


def clear_service_cache():
    """Clear the service cache (useful for credential rotation)"""
    global _SERVICE_CACHE
    _SERVICE_CACHE = {}


def build_forms_service_with_user_creds(user_id):
    """Build Google Forms service with user's OAuth credentials from database
    
    Args:
        user_id: User ID to load credentials for
    
    Returns:
        Authenticated Google Forms service
    """
    import sys
    from pathlib import Path
    from google.oauth2.credentials import Credentials
    
    # Import user auth manager
    sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
    from auth.user_auth import UserAuthManager
    
    # Get user's Google OAuth credentials
    auth_manager = UserAuthManager()
    cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
    
    if not cred_dict:
        raise Exception(f"User {user_id} does not have Google OAuth credentials. Please sign in with Google at http://localhost:5001/api/auth/google/login?user_id={user_id}")
    
    # Build credentials object
    credentials = Credentials(
        token=cred_dict['access_token'],
        refresh_token=cred_dict.get('refresh_token'),
        token_uri=cred_dict['token_uri'],
        client_id=cred_dict['client_id'],
        client_secret=cred_dict['client_secret'],
        scopes=cred_dict['scopes']
    )
    
    # Build and return service
    service = build('forms', 'v1', credentials=credentials)
    print(f"Google Forms service created with user {user_id}'s OAuth credentials")
    return service


def build_drive_service_with_user_creds(user_id):
    """Build Google Drive service with user's OAuth credentials from database
    
    Args:
        user_id: User ID to load credentials for
    
    Returns:
        Authenticated Google Drive service
    """
    import sys
    from pathlib import Path
    from google.oauth2.credentials import Credentials
    
    # Import user auth manager
    sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
    from auth.user_auth import UserAuthManager
    
    # Get user's Google OAuth credentials
    auth_manager = UserAuthManager()
    cred_dict = auth_manager.get_user_google_oauth_credentials(user_id)
    
    if not cred_dict:
        raise Exception(f"User {user_id} does not have Google OAuth credentials")
    
    # Build credentials object
    credentials = Credentials(
        token=cred_dict['access_token'],
        refresh_token=cred_dict.get('refresh_token'),
        token_uri=cred_dict['token_uri'],
        client_id=cred_dict['client_id'],
        client_secret=cred_dict['client_secret'],
        scopes=cred_dict['scopes']
    )
    
    # Build and return service
    service = build('drive', 'v3', credentials=credentials)
    return service
