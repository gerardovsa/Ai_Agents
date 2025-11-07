"""
OAuth Provider Configuration
Client credentials and endpoints for OAuth authentication

LOADS FROM .env.master FILE (not .env or environment variables)
"""

import os
from pathlib import Path
from dotenv import dotenv_values

# Load OAuth credentials from .env.master (master credentials file)
_ENV_MASTER_PATH = Path(__file__).parent.parent.parent / '.env.master'
_config = dotenv_values(_ENV_MASTER_PATH)

OAUTH_PROVIDERS = {
    'google': {
        'client_id': _config.get('GOOGLE_OAUTH_CLIENT_ID') or _config.get('GOOGLE_CLIENT_ID'),
        'client_secret': _config.get('GOOGLE_OAUTH_CLIENT_SECRET') or _config.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': 'http://localhost:5001/oauth/google/callback',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'auth_uri': 'https://accounts.google.com/o/oauth2/v2/auth',
        'scopes': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/calendar.readonly'
        ]
    },
    'microsoft': {
        'client_id': _config.get('MICROSOFT_CLIENT_ID'),
        'client_secret': _config.get('MICROSOFT_CLIENT_SECRET'),
        'tenant_id': _config.get('MICROSOFT_TENANT_ID', 'common'),
        'redirect_uri': 'http://localhost:5001/oauth/microsoft/callback',
        'token_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'auth_uri': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'scopes': [
            'https://graph.microsoft.com/Mail.Read',
            'https://graph.microsoft.com/Mail.Send',
            'https://graph.microsoft.com/Files.Read.All',
            'https://graph.microsoft.com/Calendars.Read',
            'https://graph.microsoft.com/User.Read',
            'https://graph.microsoft.com/Calendars.ReadWrite'
        ]
    }
}

def get_provider_config(platform):
    """Get OAuth configuration for a specific platform"""
    return OAUTH_PROVIDERS.get(platform)

def get_client_credentials(platform):
    """Get just client_id and client_secret for a platform"""
    config = OAUTH_PROVIDERS.get(platform)
    if config:
        return {
            'client_id': config['client_id'],
            'client_secret': config['client_secret']
        }
    return None
