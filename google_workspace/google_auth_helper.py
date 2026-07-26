"""
FILE: google_workspace/google_auth_helper.py
PURPOSE: Unified Google Workspace API authentication - service-account builders only.

DEPENDENCIES:
- google.oauth2.service_account - Service account authentication
- googleapiclient.discovery.build - Google API client builder
- dotenv - Load service account credentials from .env.master

EXPORTS:
- get_service_account_credentials(scopes) -> service_account.Credentials
- build_gmail_service() -> Resource - Gmail API v1 client (SA)
- build_drive_service(**kwargs) -> Resource - Drive API v3 client (SA)
- build_docs_service(**kwargs) -> Resource - Docs API v1 client (SA)
- build_calendar_service() -> Resource - Calendar API v3 client (SA)
- build_forms_service() -> Resource - Forms API v1 client (SA)
- build_analytics_service() -> Resource - Analytics Data API v1beta client (SA)
- clear_service_cache() -> None

USED BY:
- google_workspace/gmail.py - Gmail functions (SA-only sidecar)
- google_workspace/google_docs.py - Docs chart helpers / SA fallback (SA-only)
- google_workspace/google_drive.py - SA fallback path (SA-only)
- google_workspace/google_calendar.py - SA sidecar (SA-only)
- google_workspace/google_sheets.py - bare SA fallback (SA-only)
- google_workspace/google_slides.py - bare SA fallback (SA-only)
- google_workspace/google_meet.py - SA helpers (SA-only)
- google_workspace/google_analytics.py - SA builders (SA-only)

RELATED FILES:
- AI_infrastructure/auth/credential_injector.py - Canonical user OAuth injector
  (the only path user-context Google tools should take). Tools that need a
  user context MUST call ``get_user_<service>_service(user_id=...)`` from the
  shared injector; they MUST NOT route through this module.
- The parallel user-OAuth loader (the deprecated sibling module previously
  imported by Phase 8 callers) is DEPRECATED (Phase 9). No longer imported
  by this module. Kept as frozen historical code; do not add new callers.

NOTES:
- Phase 9: this helper is now a pure service-account builder.
  All user-OAuth construction has been removed. Callers that need user
  context must route through AI_infrastructure.auth.credential_injector.
- Phase 9: build_drive_service(**kwargs) and build_docs_service(**kwargs)
  accept and IGNORE user-context kwargs (e.g. ``_user_id``,
  ``injected_credentials``) for backwards compatibility with older call
  sites that pass them through. The kwargs are intentionally swallowed —
  this helper has no user OAuth code path.
- AUTHENTICATION: service-account credentials only (from .env.master via
  GOOGLE_APPLICATION_CREDENTIALS or SERVICE_ACCOUNT_* env vars).
- PERFORMANCE: Services are cached per-process after first build.
- MULTI-TENANT: Each Google user is expected to authenticate via OAuth at
  the canonical /api/auth/google/login route. Tokens persist in
  ai_infrastructure.oauth_tokens. This helper does NOT touch user OAuth.

LAST MODIFIED: 2026-07-26 - Phase 9 retirement of parallel user-OAuth loader.
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

# Service account credential cache (process-local)
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


def build_docs_service(**kwargs):
    """Get authenticated Google Docs API service (service-account only).

    Phase 9: this builder is service-account-only. All user-OAuth construction
    has been removed. Tools that need a user context must route through the
    shared injector:

        from AI_infrastructure.auth.credential_injector import get_user_docs_service
        service = get_user_docs_service(user_id=<user_id>)

    Args:
        **kwargs: Accepted and ignored for backwards compatibility with older
            call sites that may pass ``_user_id`` / ``injected_credentials``
            / ``user_id``. They have no effect on this builder.

    Returns:
        Authenticated Docs service (service account credentials).
    """
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


def build_drive_service(**kwargs):
    """Get authenticated Google Drive API service (service-account only).

    Phase 9: this builder is service-account-only. All user-OAuth construction
    has been removed. Tools that need a user context must route through the
    shared injector:

        from AI_infrastructure.auth.credential_injector import get_user_drive_service
        service = get_user_drive_service(user_id=<user_id>)

    Args:
        **kwargs: Accepted and ignored for backwards compatibility with older
            call sites that may pass ``_user_id`` / ``injected_credentials``
            / ``user_id``. They have no effect on this builder.

    Returns:
        Authenticated Drive service (service account credentials).
    """
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
    """Get authenticated Gmail API service (service-account only)."""
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
    """Get authenticated Google Calendar API service (service-account only)."""
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
    """Get authenticated Google Forms API service (service-account only).

    Note: The Forms API cannot be authorized with a plain service account
    without domain-wide delegation. Callers that need a user context must
    route through the shared injector:

        from AI_infrastructure.auth.credential_injector import get_user_forms_service
        service = get_user_forms_service(user_id=<user_id>)
    """
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
    """Get authenticated Google Analytics Data API service (service-account only).

    Analytics is intentionally service-account-only. Do not add user OAuth
    to this helper without a separate product requirement.
    """
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
    """Clear the service cache (useful for credential rotation)."""
    global _SERVICE_CACHE
    _SERVICE_CACHE = {}