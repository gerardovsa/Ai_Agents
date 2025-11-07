"""
⚠️⚠️⚠️ DEPRECATED FILE - DO NOT USE ⚠️⚠️⚠️

This file contains DEPRECATED file-based OAuth code that is NO LONGER SUPPORTED.

❌ REMOVED FEATURES:
- credentials_desktop.json - File does not exist in production
- credentials_web.json - File does not exist in production  
- token_*.json files - Not used anymore
- File-based OAuth flows - Completely removed

✅ USE INSTEAD:
All Google Workspace tools now use DATABASE OAuth ONLY.

To authenticate:
1. Visit: http://localhost:5001/auth/google/login
2. Sign in with your Google account
3. Tokens stored in: data/ai_infrastructure.db → oauth_tokens table
4. Tools automatically use database credentials via credential_injector

This file is kept ONLY for historical reference and test script compatibility.
All functions in this file will raise deprecation warnings.

For current OAuth implementation, see:
- AI_infrastructure/routes/google_auth_routes.py (OAuth flow)
- AI_infrastructure/auth/credential_injector.py (Credential injection)
- google_workspace/google_tasks.py (Example of database OAuth usage)
"""

import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv
import warnings

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

#  UNIFIED SCOPES: All services in one OAuth flow
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
    
    # ⚠️ DEPRECATED: File-based OAuth is being phased out
    # Use credential_injector.py for database OAuth instead
    print("⚠️ WARNING: oauth_manager.py file-based OAuth is DEPRECATED")
    print("   Use AI_infrastructure/auth/credential_injector.py instead")
    print("   Database OAuth via oauth_tokens table (no credential files needed)")
    print("   See FIX_13_GOOGLE_WORKSPACE_OAUTH_DATABASE.md for migration guide")
    
    config = {
        'mode': mode,
        'service_name': service_name or 'unified'
    }
    
    if mode == 'desktop':
        # Desktop mode: Single credentials file for all services
        # ⚠️ DEPRECATED: credentials_desktop.json doesn't exist in production
        config['credentials_file'] = os.getenv(
            'GOOGLE_OAUTH_CREDENTIALS_FILE_DESKTOP',
            'credentials_desktop.json'  # ← FILE DOESN'T EXIST - Use database OAuth!
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
        # ⚠️ DEPRECATED: credentials_web.json doesn't exist in production
        config['credentials_file'] = os.getenv(
            'GOOGLE_OAUTH_CREDENTIALS_FILE_WEB',
            'credentials_web.json'  # ← FILE DOESN'T EXIST - Use database OAuth!
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
    ⚠️ DEPRECATED - Use database OAuth instead
    
    This function uses file-based OAuth which is NO LONGER SUPPORTED.
    
    Use instead:
    1. Authenticate via: http://localhost:5001/auth/google/login
    2. Credentials stored in database automatically
    3. Tools use credential_injector for OAuth
    
    Args:
        mode: Ignored - file-based OAuth deprecated
        user_email: Ignored - file-based OAuth deprecated
    
    Returns:
        Raises DeprecationWarning
    """
    warnings.warn(
        "authenticate_all_services() is DEPRECATED. "
        "File-based OAuth (credentials_desktop.json) is no longer supported. "
        "Use database OAuth via: http://localhost:5001/auth/google/login",
        DeprecationWarning,
        stacklevel=2
    )
    raise NotImplementedError(
        "❌ File-based OAuth is no longer supported.\n"
        "To authenticate, visit: http://localhost:5001/auth/google/login"
    )
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
                print(f"    Token loaded successfully")
            except Exception as e:
                print(f"   ⚠️ Failed to load token: {e}")
                credentials = None
        
        # If no valid credentials, do OAuth flow
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print(f"   🔄 Refreshing expired token...")
                try:
                    credentials.refresh(Request())
                    print(f"    Token refreshed successfully")
                except Exception as e:
                    print(f"   ⚠️ Token refresh failed: {e}")
                    credentials = None
            
            if not credentials:
                print(f"\n   🔐 Starting UNIFIED OAuth flow...")
                print(f"   📋 User will grant permission to ALL services at once:")
                print(f"       Gmail (read, send, modify)")
                print(f"       Calendar (read, create, update)")
                print(f"       Tasks (read, create, update)")
                print(f"       Forms (create, read responses)")
                print(f"\n   🌐 Browser will open automatically...\n")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    config['credentials_file'],
                    UNIFIED_SCOPES
                )
                credentials = flow.run_local_server(port=0)
                print(f"\n    Authentication successful!")
                
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
        
        print(f"    Gmail service ready")
        print(f"    Calendar service ready")
        print(f"    Tasks service ready")
        print(f"    Forms service ready")
        print("\n" + "="*70)
        print("🎉 ALL SERVICES AUTHENTICATED SUCCESSFULLY!")
        print("="*70 + "\n")
        
        return services
    
    else:  # web mode
        # Similar implementation for web mode
        raise NotImplementedError("Web mode unified authentication not yet implemented")


def build_oauth_service(service_name: str, mode: Optional[str] = None, user_email: Optional[str] = None):
    """
    ⚠️ DEPRECATED - Use database OAuth instead
    
    This function uses file-based OAuth which is NO LONGER SUPPORTED.
    
    Use instead:
    1. Authenticate via: http://localhost:5001/auth/google/login
    2. Use service-specific functions (e.g. build_gmail_service, build_tasks_service)
    3. Tools automatically use credential_injector
    
    Args:
        service_name: Ignored - file-based OAuth deprecated
        mode: Ignored - file-based OAuth deprecated
        user_email: Ignored - file-based OAuth deprecated
    
    Returns:
        Raises NotImplementedError
    """
    warnings.warn(
        f"build_oauth_service('{service_name}') is DEPRECATED. "
        "File-based OAuth is no longer supported. "
        "Use database OAuth via: http://localhost:5001/auth/google/login",
        DeprecationWarning,
        stacklevel=2
    )
    raise NotImplementedError(
        f"❌ File-based OAuth is no longer supported for {service_name}.\n"
        "To authenticate, visit: http://localhost:5001/auth/google/login"
    )
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
    
    #  FIRST: Check if unified token exists
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
            print(f"    {service_name.title()} service ready (unified auth)")
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
    print(f"    Google {service_name.title()} service ready ({config['mode']} mode)")
    
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
            print(f"    Token loaded successfully")
        except Exception as e:
            print(f"   ⚠️ Failed to load token: {e}")
            credentials = None
    
    # If no valid credentials, do OAuth flow
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print(f"   🔄 Refreshing expired token...")
            try:
                credentials.refresh(Request())
                print(f"    Token refreshed successfully")
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
            print(f"    Authentication successful!")
            
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
        print(f"    Token refreshed and saved")
    
    # Build service
    service = build(service_name, API_VERSIONS[service_name], credentials=credentials)
    return service

# ==================== CONVENIENCE FUNCTIONS ====================
# ⚠️ ALL DEPRECATED - Use database OAuth instead

def build_gmail_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """⚠️ DEPRECATED - Use database OAuth via credential_injector"""
    warnings.warn("build_gmail_oauth_service() is DEPRECATED. Use database OAuth.", DeprecationWarning, stacklevel=2)
    raise NotImplementedError("❌ File-based OAuth is no longer supported. Visit: http://localhost:5001/auth/google/login")

def build_calendar_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """⚠️ DEPRECATED - Use database OAuth via credential_injector"""
    warnings.warn("build_calendar_oauth_service() is DEPRECATED. Use database OAuth.", DeprecationWarning, stacklevel=2)
    raise NotImplementedError("❌ File-based OAuth is no longer supported. Visit: http://localhost:5001/auth/google/login")

def build_forms_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """⚠️ DEPRECATED - Use database OAuth via credential_injector"""
    warnings.warn("build_forms_oauth_service() is DEPRECATED. Use database OAuth.", DeprecationWarning, stacklevel=2)
    raise NotImplementedError("❌ File-based OAuth is no longer supported. Visit: http://localhost:5001/auth/google/login")

def build_drive_oauth_service(mode: Optional[str] = None, user_email: Optional[str] = None):
    """⚠️ DEPRECATED - Use database OAuth via credential_injector"""
    warnings.warn("build_drive_oauth_service() is DEPRECATED. Use database OAuth.", DeprecationWarning, stacklevel=2)
    raise NotImplementedError("❌ File-based OAuth is no longer supported. Visit: http://localhost:5001/auth/google/login")

# ==================== TOKEN MANAGEMENT ====================
# ⚠️ ALL DEPRECATED - Token files no longer used

def check_oauth_status(service_name: str, user_email: Optional[str] = None) -> dict:
    """
    ⚠️ DEPRECATED - Use database OAuth status instead
    
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
        print(f" Unknown service: {service_name}")
        print(f"Available services: {', '.join(SCOPES.keys())}")
        sys.exit(1)
    
    print(f"\n🔧 Testing OAuth for {service_name.title()}...")
    print("=" * 60)
    
    try:
        service = build_oauth_service(service_name, mode='desktop')
        print(f"\n {service_name.title()} OAuth authentication successful!")
        
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
            print(f"    Service initialized successfully")
        elif service_name == 'drive':
            files = service.files().list(pageSize=5).execute()
            print(f"   Recent files: {len(files.get('files', []))}")
        
        print(f"\n All tests passed for {service_name.title()}!")
        
    except Exception as e:
        print(f"\n OAuth test failed: {e}")
        sys.exit(1)
