"""
Google Workspace OAuth Manager
===============================
Unified OAuth 2.0 authentication for personal data APIs (Gmail, Calendar, Forms, etc.)

Supports:
- Desktop mode: Browser popup authentication (local testing)
- Web mode: Redirect-based authentication (Render deployment)
- Multi-service: Single OAuth flow for multiple APIs
- Token management: Automatic refresh, caching

Usage:
    # Desktop mode (local testing)
    service = build_oauth_service('gmail', mode='desktop')
    
    # Web mode (Render deployment)
    service = build_oauth_service('gmail', mode='web', user_email='user@example.com')
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables
env_master = Path(__file__).parent.parent / '.env.master'
if env_master.exists():
    load_dotenv(env_master, override=False)

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    HAS_OAUTH_LIBS = True
except ImportError:
    HAS_OAUTH_LIBS = False
    print("⚠️ Google OAuth libraries not available - install google-auth-oauthlib")

# Service cache
_OAUTH_SERVICE_CACHE: Dict[str, any] = {}

# ==================== SCOPES ====================

# Individual service scopes (for reference)
SCOPES = {
    'gmail': [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly'
    ],
    'calendar': [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/calendar.events'
    ],
    'forms': [
        'https://www.googleapis.com/auth/forms.body',
        'https://www.googleapis.com/auth/forms.responses.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ],
    'drive': [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
    ],
    'tasks': [
        'https://www.googleapis.com/auth/tasks'
    ]
}

# ✅ UNIFIED SCOPES: All services in one OAuth flow
UNIFIED_SCOPES = [
    # Gmail
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    # Calendar
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events',
    # Tasks
    'https://www.googleapis.com/auth/tasks',
    # Forms
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/forms.responses.readonly',
    # Drive (for Forms file creation)
    'https://www.googleapis.com/auth/drive.file'
]

# API versions
API_VERSIONS = {
    'gmail': 'v1',
    'calendar': 'v3',
    'forms': 'v1',
    'drive': 'v3'
}

# ==================== ENVIRONMENT CONFIG ====================

def get_oauth_config(service_name: str = None) -> dict:
    """
    Get OAuth configuration from environment variables
    
    Args:
        service_name: Optional specific service ('gmail', 'calendar', etc.)
                     If None, returns unified config for all services
    
    Returns:
        Configuration dict with mode, credentials, and token paths
    """
    mode = os.getenv('GOOGLE_OAUTH_MODE', 'desktop').lower()
    
    config = {
        'mode': mode,
        'service_name': service_name or 'unified'
    }
    
    if mode == 'desktop':
        # Desktop mode: Single credentials file for all services
        config['credentials_file'] = os.getenv(
            'GOOGLE_OAUTH_CREDENTIALS_FILE_DESKTOP',
            'credentials_desktop.json'
        )
        
        if service_name:
            # Service-specific token file
            config['token_file'] = os.getenv(
                f'GOOGLE_{service_name.upper()}_TOKEN_FILE_DESKTOP',
                f'token_{service_name}_desktop.json'
            )
        else:
            # Unified token file for all services
            config['token_file'] = os.getenv(
                'GOOGLE_UNIFIED_TOKEN_FILE_DESKTOP',
                'token_unified_desktop.json'
            )
    else:  # web mode
        config['credentials_file'] = os.getenv(
            'GOOGLE_OAUTH_CREDENTIALS_FILE_WEB',
            'credentials_web.json'
        )
        
        if service_name:
            # Service-specific token file
            config['token_file'] = os.getenv(
                f'GOOGLE_{service_name.upper()}_TOKEN_FILE_WEB',
                f'token_{service_name}_web.json'
            )
        else:
            # Unified token file for all services
            config['token_file'] = os.getenv(
                'GOOGLE_UNIFIED_TOKEN_FILE_WEB',
                'token_unified_web.json'
            )
    
    return config

# ==================== OAUTH SERVICE BUILDERS ====================

def authenticate_all_services(mode: Optional[str] = None, user_email: Optional[str] = None) -> dict:
    """
    🎯 UNIFIED AUTHENTICATION: Authenticate ALL services with ONE browser popup
    
    This is the recommended method for initial setup. User grants permission to
    Gmail, Calendar, Tasks, and Forms all at once, then the same token is used
    for all services.
    
    Args:
        mode: 'desktop' or 'web' (defaults to GOOGLE_OAUTH_MODE env var)
        user_email: User email for multi-user deployments (web mode only)
    
    Returns:
        dict: {
            'gmail': service,
            'calendar': service,
            'tasks': service,
            'forms': service,
            'token_file': 'path/to/token.json'
        }
    
    Example:
        # Desktop mode (local testing) - ONE browser popup for all services
        services = authenticate_all_services(mode='desktop')
        gmail = services['gmail']
        calendar = services['calendar']
        
        # Use them immediately
        profile = gmail.users().getProfile(userId='me').execute()
        calendars = calendar.calendarList().list().execute()
    """
    if not HAS_OAUTH_LIBS:
        raise ImportError("Google OAuth libraries not available - install google-auth-oauthlib")
    
    # Get configuration
    config = get_oauth_config(service_name=None)  # Unified config
    if mode:
        config['mode'] = mode.lower()
    
    print("\n" + "="*70)
    print("🎯 UNIFIED GOOGLE WORKSPACE AUTHENTICATION")
    print("="*70)
    print(f"   Mode: {config['mode']}")
    print(f"   Credentials: {config['credentials_file']}")
    print(f"   Token: {config['token_file']}")
    print(f"   Services: Gmail, Calendar, Tasks, Forms")
    print(f"   Scopes: {len(UNIFIED_SCOPES)} permissions")
    print("="*70)
    
    # Build unified token (works for all services)
    if config['mode'] == 'desktop':
        token_file = config['token_file']
        credentials = None
        
        # Try to load existing token
        if os.path.exists(token_file):
            print(f"   📂 Loading existing unified token...")
            try:
                credentials = Credentials.from_authorized_user_file(token_file, UNIFIED_SCOPES)
                print(f"   ✅ Token loaded successfully")
            except Exception as e:
                print(f"   ⚠️ Failed to load token: {e}")
                credentials = None
        
        # If no valid credentials, do OAuth flow
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print(f"   🔄 Refreshing expired token...")
                try:
                    credentials.refresh(Request())
                    print(f"   ✅ Token refreshed successfully")
                except Exception as e:
                    print(f"   ⚠️ Token refresh failed: {e}")
                    credentials = None
            
            if not credentials:
                print(f"\n   🔐 Starting UNIFIED OAuth flow...")
                print(f"   📋 User will grant permission to ALL services at once:")
                print(f"      ✅ Gmail (read, send, modify)")
                print(f"      ✅ Calendar (read, create, update)")
                print(f"      ✅ Tasks (read, create, update)")
                print(f"      ✅ Forms (create, read responses)")
                print(f"\n   🌐 Browser will open automatically...\n")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config['credentials_file'],
                    UNIFIED_SCOPES
                )
                credentials = flow.run_local_server(port=0)
                print(f"\n   ✅ Authentication successful!")
                
                # Save unified token
                with open(token_file, 'w') as token:
                    token.write(credentials.to_json())
                print(f"   💾 Unified token saved to: {token_file}")
        
        # Build all services with the same credentials
        print(f"\n   🔧 Building services...")
        services = {
            'gmail': build('gmail', 'v1', credentials=credentials),
            'calendar': build('calendar', 'v3', credentials=credentials),
            'tasks': build('tasks', 'v1', credentials=credentials),
            'forms': build('forms', 'v1', credentials=credentials),
            'token_file': token_file
        }
        
        print(f"   ✅ Gmail service ready")
        print(f"   ✅ Calendar service ready")
        print(f"   ✅ Tasks service ready")
        print(f"   ✅ Forms service ready")
        print("\n" + "="*70)
        print("🎉 ALL SERVICES AUTHENTICATED SUCCESSFULLY!")
        print("="*70 + "\n")
        
        return services
    
    else:  # web mode
        # Similar implementation for web mode
        raise NotImplementedError("Web mode unified authentication not yet implemented")


def build_oauth_service(service_name: str, mode: Optional[str] = None, user_email: Optional[str] = None):
    """
    Build OAuth-authenticated Google API service
    
    NOTE: If unified token exists, it will be used automatically!
    This means you only need to authenticate once for all services.
    
    Args:
        service_name: 'gmail', 'calendar', 'forms', 'drive', 'tasks'
        mode: 'desktop' or 'web' (defaults to GOOGLE_OAUTH_MODE env var)
        user_email: User email for multi-user deployments (web mode only)
    
    Returns:
        Authenticated Google API service
    
    Examples:
        # After running authenticate_all_services(), these will use unified token:
        gmail = build_oauth_service('gmail')      # No popup!
        calendar = build_oauth_service('calendar') # No popup!
        tasks = build_oauth_service('tasks')       # No popup!
    """
    if not HAS_OAUTH_LIBS:
        raise ImportError("Google OAuth libraries not available - install google-auth-oauthlib")
    
    # Get configuration
    config = get_oauth_config(service_name)
    if mode:
        config['mode'] = mode.lower()
    
    # Check cache
    cache_key = f"{service_name}_{config['mode']}_{user_email or 'default'}"
    if cache_key in _OAUTH_SERVICE_CACHE:
        print(f"🔄 Using cached {service_name} service ({config['mode']} mode)")
        return _OAUTH_SERVICE_CACHE[cache_key]
    
    # ✅ FIRST: Check if unified token exists
    unified_config = get_oauth_config(service_name=None)
    unified_token_file = unified_config['token_file']
    
    if os.path.exists(unified_token_file):
        print(f"🔑 {service_name.title()}: Using unified token (all services authenticated)")
        try:
            credentials = Credentials.from_authorized_user_file(unified_token_file, UNIFIED_SCOPES)
            
            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                print(f"   🔄 Refreshing expired unified token...")
                credentials.refresh(Request())
                with open(unified_token_file, 'w') as token:
                    token.write(credentials.to_json())
            
            # Build service
            service = build(service_name, API_VERSIONS[service_name], credentials=credentials)
            _OAUTH_SERVICE_CACHE[cache_key] = service
            print(f"   ✅ {service_name.title()} service ready (unified auth)")
            return service
            
        except Exception as e:
            print(f"   ⚠️ Unified token failed: {e}")
            print(f"   → Falling back to service-specific authentication")
    
    # Fallback: Service-specific authentication
    print(f"🔑 Google {service_name.title()} OAuth Mode: {config['mode']}")
    print(f"   Credentials: {config['credentials_file']}")
    print(f"   Token: {config['token_file']}")
    print(f"   Scopes: {SCOPES[service_name]}")
    
    if config['mode'] == 'desktop':
        service = _build_oauth_service_desktop(service_name, config)
    elif config['mode'] == 'web':
        service = _build_oauth_service_web(service_name, config, user_email)
    else:
        raise ValueError(f"Invalid OAuth mode: {config['mode']}. Use 'desktop' or 'web'")
    
    # Cache service
    _OAUTH_SERVICE_CACHE[cache_key] = service
    print(f"   ✅ Google {service_name.title()} service ready ({config['mode']} mode)")
    
    return service


def _build_oauth_service_desktop(service_name: str, config: dict):
    """
    Build OAuth service for desktop mode (local testing)
    Opens browser popup for authentication
    """
    credentials = None
    token_file = config['token_file']
    
    # Try to load existing token
    if os.path.exists(token_file):
        print(f"   📂 Loading existing token from: {token_file}")
        try:
            credentials = Credentials.from_authorized_user_file(token_file, SCOPES[service_name])
            print(f"   ✅ Token loaded successfully")
        except Exception as e:
            print(f"   ⚠️ Failed to load token: {e}")
            credentials = None
    
    # If no valid credentials, do OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print(f"   🔄 Refreshing expired token...")
            try:
                credentials.refresh(Request())
                print(f"   ✅ Token refreshed successfully")
            except Exception as e:
                print(f"   ⚠️ Token refresh failed: {e}")
                credentials = None
        
        if not credentials:
            print(f"   🔐 Starting OAuth flow (browser will open)...")
            flow = InstalledAppFlow.from_client_secrets_file(
                config['credentials_file'],
                SCOPES[service_name]
            )
            credentials = flow.run_local_server(port=0)
            print(f"   ✅ Authentication successful!")
            
            # Save token
            with open(token_file, 'w') as token:
                token.write(credentials.to_json())
            print(f"   💾 Token saved to: {token_file}")
    
    # Build service
    service = build(service_name, API_VERSIONS[service_name], credentials=credentials)
    return service


def _build_oauth_service_web(service_name: str, config: dict, user_email: Optional[str] = None):
    """
    Build OAuth service for web mode (Render deployment)
    Requires pre-authenticated token from OAuth callback
    """
    # For web mode, token must already exist from OAuth callback
    token_file = config['token_file']
    
    # For multi-user, use user-specific token file
    if user_email:
        token_file = token_file.replace('.json', f'_{user_email}.json')
        print(f"   👤 User-specific token: {token_file}")
    
    if not os.path.exists(token_file):
        raise FileNotFoundError(
            f"Token file not found: {token_file}\n"
            f"User must complete OAuth flow first:\n"
            f"Visit: /oauth/{service_name}/start"
        )
    
    # Load token
    print(f"   📂 Loading token from: {token_file}")
    credentials = Credentials.from_authorized_user_file(token_file, SCOPES[service_name])
    
    # Refresh if expired
    if credentials.expired and credentials.refresh_token:
        print(f"   🔄 Refreshing expired token...")
        from google.auth.transport.requests import Request
        credentials.refresh(Request())
        
        # Save refreshed token
        with open(token_file, 'w') as token:
            token.write(credentials.to_json())
        print(f"   ✅ Token refreshed and saved")
    
    # Build service
    service = build(service_name, API_VERSIONS[service_name], credentials=credentials)
    return service

# ==================== CONVENIENCE FUNCTIONS ====================

def build_gmail_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """Build OAuth-authenticated Gmail service"""
    return build_oauth_service('gmail', mode=mode, user_email=user_email)

def build_calendar_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """Build OAuth-authenticated Calendar service"""
    return build_oauth_service('calendar', mode=mode, user_email=user_email)

def build_forms_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """Build OAuth-authenticated Forms service"""
    return build_oauth_service('forms', mode=mode, user_email=user_email)

def build_drive_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """Build OAuth-authenticated Drive service"""
    return build_oauth_service('drive', mode=mode, user_email=user_email)

# ==================== TOKEN MANAGEMENT ====================

def check_oauth_status(service_name: str, user_email: Optional[str] = None) -> dict:
    """
    Check OAuth authentication status for a service
    
    Returns:
        {
            'authenticated': bool,
            'token_file': str,
            'token_exists': bool,
            'token_valid': bool,
            'needs_refresh': bool
        }
    """
    config = get_oauth_config(service_name)
    token_file = config['token_file']
    
    if user_email:
        token_file = token_file.replace('.json', f'_{user_email}.json')
    
    status = {
        'authenticated': False,
        'token_file': token_file,
        'token_exists': os.path.exists(token_file),
        'token_valid': False,
        'needs_refresh': False
    }
    
    if status['token_exists']:
        try:
            credentials = Credentials.from_authorized_user_file(token_file, SCOPES[service_name])
            status['token_valid'] = credentials.valid
            status['needs_refresh'] = credentials.expired and credentials.refresh_token
            status['authenticated'] = credentials.valid or status['needs_refresh']
        except Exception as e:
            print(f"⚠️ Error checking token: {e}")
    
    return status

def clear_oauth_cache():
    """Clear OAuth service cache"""
    global _OAUTH_SERVICE_CACHE
    _OAUTH_SERVICE_CACHE = {}
    print("🧹 OAuth service cache cleared")

# ==================== AUTHENTICATION TESTING ====================

if __name__ == "__main__":
    """Test OAuth authentication"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python oauth_manager.py <service_name>")
        print("Services: gmail, calendar, forms, drive")
        sys.exit(1)
    
    service_name = sys.argv[1].lower()
    
    if service_name not in SCOPES:
        print(f"❌ Unknown service: {service_name}")
        print(f"Available services: {', '.join(SCOPES.keys())}")
        sys.exit(1)
    
    print(f"\n🔧 Testing OAuth for {service_name.title()}...")
    print("=" * 60)
    
    try:
        service = build_oauth_service(service_name, mode='desktop')
        print(f"\n✅ {service_name.title()} OAuth authentication successful!")
        
        # Test API call
        print(f"\n🧪 Testing API call...")
        if service_name == 'gmail':
            profile = service.users().getProfile(userId='me').execute()
            print(f"   Email: {profile['emailAddress']}")
            print(f"   Total messages: {profile['messagesTotal']}")
        elif service_name == 'calendar':
            calendars = service.calendarList().list().execute()
            print(f"   Calendars: {len(calendars.get('items', []))}")
        elif service_name == 'forms':
            # Forms requires a form ID, so just verify service works
            print(f"   ✅ Service initialized successfully")
        elif service_name == 'drive':
            files = service.files().list(pageSize=5).execute()
            print(f"   Recent files: {len(files.get('files', []))}")
        
        print(f"\n✅ All tests passed for {service_name.title()}!")
        
    except Exception as e:
        print(f"\n❌ OAuth test failed: {e}")
        sys.exit(1)
