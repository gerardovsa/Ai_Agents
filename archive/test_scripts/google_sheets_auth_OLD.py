# FILE: auth.py
"""
auth.py
Google Sheets authentication services providing service account credential management,
spreadsheet access validation, and worksheet retrieval by name or GID.

Usage:
    from auth import get_authenticated_gspread_client_sync
    client = get_authenticated_gspread_client_sync()
"""

import os
import time
import gspread
from google.oauth2 import service_account
try:
    from config import DEEPSEEK_API_KEYS  # Use local config (root level)
except ImportError:
    DEEPSEEK_API_KEYS = []  # Fallback if config not available
from datetime import datetime

def get_timestamp():
    """Get current timestamp in HH:MM:SS format - local copy to avoid circular import"""
    return datetime.now().strftime('%H:%M:%S')

def get_api_key_enhanced(key_name):
    """Get API key or environment variable with enhanced error handling"""
    return os.getenv(key_name)

# Original credential cache - unchanged
_CREDENTIAL_CACHE = {'client': None, 'created_at': None, 'last_used': None}

def get_authenticated_gspread_client_sync():
    """ORIGINAL: Multi-user safe Google Sheets client with proper authentication"""
    global _CREDENTIAL_CACHE

    current_time = time.time()

    # Check if we have a valid cached client (10 minutes for multi-user safety)
    if (_CREDENTIAL_CACHE['client'] and
        _CREDENTIAL_CACHE['created_at'] and
        current_time - _CREDENTIAL_CACHE['created_at'] < 600):  # 10 min cache

        _CREDENTIAL_CACHE['last_used'] = current_time
        return _CREDENTIAL_CACHE['client']

    try:
        # Try explicit service account credentials first (ORIGINAL WORKING METHOD)
        service_account_email = get_api_key_enhanced('SERVICE_ACCOUNT_EMAIL')
        service_account_private_key = get_api_key_enhanced('SERVICE_ACCOUNT_PRIVATE_KEY')
        service_account_private_key_id = get_api_key_enhanced('SERVICE_ACCOUNT_PRIVATE_KEY_ID')

        if all([service_account_email, service_account_private_key, service_account_private_key_id]):
            print(f"✅ {get_timestamp()} Using explicit service account credentials")

            # Clean up the private key
            private_key = service_account_private_key.replace('\\n', '\n')

            # Build credentials info manually (ORIGINAL WORKING METHOD)
            credentials_info = {
                "type": "service_account",
                "project_id": "colab-ai-processor",
                "private_key_id": service_account_private_key_id,
                "private_key": private_key,
                "client_email": service_account_email,
                "client_id": "",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": ""
            }

            # Create credentials from service account info (ORIGINAL WORKING METHOD)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            )

            # Authorize with gspread
            client = gspread.authorize(credentials)
            print(f"✅ {get_timestamp()} Service account authentication successful")

        else:
            # Fallback to default service account (ORIGINAL WORKING FALLBACK)
            print(f"⚠️ {get_timestamp()} Missing service account env vars, using default")
            client = gspread.service_account()
            print(f"✅ {get_timestamp()} Default service account authentication successful")

        # Cache the client (KEEP MULTI-USER IMPROVEMENTS)
        _CREDENTIAL_CACHE['client'] = client
        _CREDENTIAL_CACHE['created_at'] = current_time
        _CREDENTIAL_CACHE['last_used'] = current_time

        return client

    except Exception as e:
        print(f"❌ {get_timestamp()} Google Sheets authentication failed: {e}")
        # Clear cache on failure (KEEP IMPROVEMENT)
        _CREDENTIAL_CACHE['client'] = None
        _CREDENTIAL_CACHE['created_at'] = None
        raise ValueError(f"Google Sheets authentication failed: {e}")

def validate_spreadsheet_access(spreadsheet_id):
    """Validate access to specific spreadsheet before processing - unchanged"""
    max_retries = 2

    for attempt in range(max_retries):
        try:
            client = get_authenticated_gspread_client_sync()

            # Test access
            spreadsheet = client.open_by_key(spreadsheet_id)
            _ = spreadsheet.title  # This will fail if no access

            print(f"✅ {get_timestamp()} Validated access to: {spreadsheet.title}")
            return client, spreadsheet

        except Exception as access_error:
            print(f"❌ {get_timestamp()} Access validation failed (attempt {attempt + 1}): {access_error}")

            # Clear cache and retry once
            if attempt < max_retries - 1:
                _CREDENTIAL_CACHE['client'] = None
                _CREDENTIAL_CACHE['created_at'] = None
                time.sleep(1)
                continue
            else:
                raise Exception(f"Cannot access spreadsheet {spreadsheet_id}: {access_error}")

def get_worksheet_by_name_or_gid(spreadsheet, worksheet_identifier):
    """Get worksheet by name or GID with comprehensive error handling"""
    try:
        if not worksheet_identifier:
            print(f"⚠️ No worksheet identifier provided, using first worksheet")
            return spreadsheet.get_worksheet(0)

        # Handle GID format (Sheet_1234567)
        if isinstance(worksheet_identifier, str) and worksheet_identifier.startswith('Sheet_'):
            gid = worksheet_identifier[6:]
            print(f"🔢 Detected GID format: {worksheet_identifier} -> GID: {gid}")

            for worksheet in spreadsheet.worksheets():
                if str(worksheet.id) == gid:
                    print(f"✅ Found worksheet by GID: {worksheet.title} (ID: {worksheet.id})")
                    return worksheet

            print(f"⚠️ No worksheet found with GID {gid}")

        # Try by name
        try:
            worksheet = spreadsheet.worksheet(worksheet_identifier)
            print(f"✅ Found worksheet by name: {worksheet.title}")
            return worksheet
        except Exception as name_error:
            print(f"⚠️ Failed to access by name '{worksheet_identifier}': {name_error}")

        # Try by index if it's a number
        try:
            if str(worksheet_identifier).isdigit():
                index = int(worksheet_identifier)
                worksheet = spreadsheet.get_worksheet(index)
                print(f"✅ Found worksheet by index {index}: {worksheet.title}")
                return worksheet
        except Exception as index_error:
            print(f"⚠️ Failed to access by index: {index_error}")

        # Fallback to first worksheet
        worksheet = spreadsheet.get_worksheet(0)
        print(f"⚠️ Using fallback worksheet: {worksheet.title}")
        return worksheet

    except Exception as e:
        print(f"❌ Error accessing worksheet: {e}")
        raise Exception(f"Could not access any worksheet: {e}")