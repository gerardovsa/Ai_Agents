"""
Google Workspace Authentication Helper
=======================================
Unified authentication for Google Workspace APIs (Docs, Drive, Gmail, Calendar, etc.)
Uses service account credentials from environment variables.
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
            "❌ Google Workspace service account not configured!\n\n"
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


def build_docs_service(user_id=None, injected_credentials=None):
    """Get authenticated Google Docs API service
    
    Args:
        user_id: User ID for OAuth credentials from database
        injected_credentials: OAuth credentials dict (from database)
    
    Returns:
        Authenticated Docs service using either user OAuth or service account
    """
    # If user credentials provided, use them (don't cache per-user services)
    if user_id and injected_credentials:
        print(f"🔑 Building Docs service with user {user_id}'s OAuth credentials")
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
        print(f"✅ Docs service created with user {user_id}'s credentials")
        return service
    
    # Fall back to service account (cached)
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
        print(f"✅ Drive service created with user {user_id}'s credentials")
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
