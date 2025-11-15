"""
OAuth Credential Loader for Google Workspace Tools
===================================================
Loads user OAuth credentials from oauth_tokens table in ai_infrastructure.db

This module is used by all Google Workspace tools to get user-specific
credentials instead of using service accounts.
"""

import sqlite3
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from google.oauth2.credentials import Credentials

# Add AI_infrastructure to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))
from shared.database_utils import get_database_connection


def get_oauth_credentials_from_db(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get Google OAuth credentials from oauth_tokens table.
    
    Args:
        user_id: User ID to fetch credentials for
        
    Returns:
        Dict with credential data or None if not found:
        {
            'access_token': str,
            'refresh_token': str,
            'token_type': str,
            'expires_at': str,
            'scope': str
        }
    """
    try:
        # Path to ai_infrastructure.db
        root_dir = Path(__file__).parent.parent
        db_path = root_dir / 'data' / 'ai_infrastructure.db'
        
        if not db_path.exists():
            print(f"⚠️  Database not found: {db_path}")
            return None
        
        print(f"🔍 Loading Google OAuth credentials for user_id={user_id}")
        
        conn = get_database_connection('ai_infrastructure')
        if hasattr(conn, 'row_factory'):  # SQLite
            conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query oauth_tokens table
        cursor.execute("""
            SELECT platform, access_token, refresh_token, 
                   token_type, expires_at, scope,
                   account_identifier, account_name,
                   is_valid, is_active
            FROM oauth_tokens
            WHERE user_id = ? AND platform = 'google'
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            print(f"⚠️  No Google OAuth credentials found for user_id={user_id}")
            return None
        
        # Check if token is marked as invalid/inactive
        is_valid = row['is_valid']
        is_active = row['is_active']
        
        if not is_valid or not is_active:
            print(f"⚠️  Google OAuth credentials exist but marked as invalid/inactive (valid={is_valid}, active={is_active})")
            # Return anyway - let Google API handle expiration/refresh
        
        # Build credential dict
        creds = {
            'access_token': row['access_token'],
            'refresh_token': row['refresh_token'],
            'token_type': row['token_type'] or 'Bearer',
            'expires_at': row['expires_at'],
            'scope': row['scope'],
            'account_identifier': row['account_identifier'],  # Usually email
            'account_name': row['account_name']
        }
        
        account_info = creds.get('account_identifier') or creds.get('account_name') or 'Unknown'
        print(f"✅ Loaded Google OAuth credentials for {account_info}")
        
        return creds
        
    except Exception as e:
        print(f"❌ Error loading OAuth credentials: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_google_credentials_object(cred_dict: Dict[str, Any], scopes: list = None) -> Credentials:
    """
    Create Google OAuth2 Credentials object from credential dict.
    
    Args:
        cred_dict: Credential dict from get_oauth_credentials_from_db()
        scopes: List of OAuth scopes (optional)
        
    Returns:
        google.oauth2.credentials.Credentials object
    """
    # Get OAuth config from environment
    from dotenv import load_dotenv
    env_master = Path(__file__).parent.parent / '.env.master'
    if env_master.exists():
        load_dotenv(env_master, override=False)
    
    client_id = os.getenv('GOOGLE_OAUTH_CLIENT_ID') or os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET') or os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise Exception("❌ Google OAuth client_id/client_secret not found in .env.master")
    
    # Default scopes if not provided
    if scopes is None:
        scopes = [
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/tasks',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/forms.body'
        ]
    
    # Create Credentials object
    credentials = Credentials(
        token=cred_dict['access_token'],
        refresh_token=cred_dict['refresh_token'],
        token_uri='https://oauth2.googleapis.com/token',
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes
    )
    
    return credentials


def build_service_with_oauth(user_id: int, service_name: str, version: str, scopes: list = None):
    """
    Build Google API service with user OAuth credentials.
    
    Args:
        user_id: User ID
        service_name: Google service name ('docs', 'drive', 'gmail', etc.)
        version: API version ('v1', 'v3', etc.)
        scopes: OAuth scopes (optional)
        
    Returns:
        Authenticated Google API service object or None
        
    Example:
        docs_service = build_service_with_oauth(
            user_id=1,
            service_name='docs',
            version='v1'
        )
    """
    from googleapiclient.discovery import build
    
    # Get credentials from database
    cred_dict = get_oauth_credentials_from_db(user_id)
    
    if not cred_dict:
        print(f"⚠️  Cannot build {service_name} service - no OAuth credentials for user_id={user_id}")
        return None
    
    # Create Credentials object
    credentials = create_google_credentials_object(cred_dict, scopes)
    
    # Build service
    service = build(service_name, version, credentials=credentials)
    
    account = cred_dict.get('account_identifier') or 'user'
    print(f"✅ Built {service_name} {version} service for {account}")
    
    return service
