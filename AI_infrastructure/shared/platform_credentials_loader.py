"""
Platform Credentials Loader - User-Specific API Keys
=====================================================

Loads credentials from ai_infrastructure.user_platform_credentials table.

SUPPORTED PLATFORMS:
- assemblyai: AssemblyAI transcription API
- openai: OpenAI GPT API
- xero_print: Xero API (Print Business)
- xero_vet: Xero API (Veterinary Business)
- stripe: Stripe payment API
- twilio: Twilio SMS/Voice API
- etc.

DATABASE SCHEMA:
----------------
user_platform_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    platform TEXT NOT NULL,
    credential_type TEXT NOT NULL,
    credential_key TEXT NOT NULL,
    credential_value TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    credentials JSONB,
    UNIQUE(user_id, platform)
)

USAGE:
------
# In tool implementation:
from AI_infrastructure.shared.platform_credentials_loader import get_user_credentials

def my_tool(user_id: int, **kwargs):
    creds = get_user_credentials(user_id, 'assemblyai')
    if not creds:
        return {"error": "AssemblyAI credentials not found"}
    
    api_key = creds.get('api_key') or creds.get('credential_value')
    # Use api_key...

CREDENTIAL FORMATS:
-------------------
1. Simple API Key (credential_value):
   credential_value = "your-api-key-here"

2. Complex Credentials (credentials JSONB):
   credentials = {
       "api_key": "your-api-key",
       "base_url": "https://api.example.com",
       "client_id": "your-client-id",
       "client_secret": "your-client-secret"
   }

Author: GitHub Copilot (Claude Sonnet 4.5)
Date: December 5, 2025
"""

import json
from typing import Optional, Dict, Any
from AI_infrastructure.shared.database_utils import get_database_connection


def get_user_credentials(user_id: int, platform: str, bypass_cache: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get user-specific credentials for a platform
    
    Args:
        user_id: User ID from authentication
        platform: Platform name (assemblyai, openai, xero_print, anthropic, etc.)
        bypass_cache: If True, skip cache and force fresh database read (default: False)
    
    Returns:
        Dict with credentials or None if not found
        
    Examples:
        >>> creds = get_user_credentials(1, 'assemblyai')
        >>> api_key = creds.get('api_key')
        
        >>> creds = get_user_credentials(1, 'xero_print')
        >>> client_id = creds['credentials']['client_id']
        
        >>> creds = get_user_credentials(1, 'anthropic', bypass_cache=True)
        >>> # Force fresh read, ignore cache (useful after credential updates)
    """
    # ✅ PERFORMANCE OPTIMIZATION (Dec 2025): Try Redis cache first
    if not bypass_cache:
        try:
            from AI_infrastructure.utils.cache_utils import get_cached_platform_credentials
            cached = get_cached_platform_credentials(user_id, platform)
            if cached:
                print(f"[CREDENTIALS] ⚡ Cache HIT for user_id={user_id}, platform={platform}")
                return cached
        except Exception as e:
            # Silently fail if cache unavailable - fallback to DB
            pass
    else:
        print(f"[CREDENTIALS] 🔄 Cache BYPASS requested for user_id={user_id}, platform={platform}")
    
    print(f"[CREDENTIALS] 🔍 Cache MISS for user_id={user_id}, platform={platform} - fetching from DB")
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                platform,
                credential_type,
                credential_key,
                credential_value,
                credentials,
                metadata
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s 
            AND platform = %s 
            AND is_active = TRUE
            LIMIT 1
        """, (user_id, platform))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            print(f"[CREDENTIALS] No credentials found for user_id={user_id}, platform={platform}")
            return None
        
        # Handle dict cursor (RealDictCursor) from database_utils
        if isinstance(row, dict):
            platform_name = row['platform']
            cred_type = row['credential_type']
            cred_key = row['credential_key']
            cred_value = row['credential_value']
            credentials_json = row['credentials']
            metadata_json = row['metadata']
        else:
            # Fallback for tuple cursor
            platform_name, cred_type, cred_key, cred_value, credentials_json, metadata_json = row
        
        # Build result dict
        result = {
            'platform': platform_name,
            'credential_type': cred_type,
            'credential_key': cred_key,
            'credential_value': cred_value
        }
        
        # Parse JSON fields (psycopg2 returns JSONB as dict, not string)
        if credentials_json:
            if isinstance(credentials_json, str):
                try:
                    result['credentials'] = json.loads(credentials_json) if credentials_json.strip() else {}
                except json.JSONDecodeError:
                    result['credentials'] = {}
            elif isinstance(credentials_json, dict):
                result['credentials'] = credentials_json
            else:
                result['credentials'] = {}
        
        if metadata_json:
            if isinstance(metadata_json, str):
                try:
                    result['metadata'] = json.loads(metadata_json) if metadata_json.strip() else {}
                except json.JSONDecodeError:
                    result['metadata'] = {}
            elif isinstance(metadata_json, dict):
                result['metadata'] = metadata_json
            else:
                result['metadata'] = {}
        
        # Flatten credentials for easy access
        if 'credentials' in result:
            for key, value in result['credentials'].items():
                if key not in result:  # Don't overwrite top-level keys
                    result[key] = value
        
        # ✅ PERFORMANCE OPTIMIZATION (Dec 2025): Cache for future requests
        try:
            from AI_infrastructure.utils.cache_utils import cache_platform_credentials
            cache_platform_credentials(user_id, platform, result, ttl=600)  # 10 minute cache
            print(f"[CREDENTIALS] ⚡ Cached credentials for user_id={user_id}, platform={platform}")
        except Exception as e:
            # Silently fail if cache unavailable
            pass
        
        print(f"[CREDENTIALS] ✅ Loaded credentials for user_id={user_id}, platform={platform}")
        return result
        
    except Exception as e:
        print(f"[CREDENTIALS] ❌ Error loading credentials: {e}")
        return None


def get_assemblyai_key(user_id: int) -> Optional[str]:
    """
    Get AssemblyAI API key for user
    
    Args:
        user_id: User ID from authentication
    
    Returns:
        API key string or None
    """
    creds = get_user_credentials(user_id, 'assemblyai')
    if not creds:
        return None
    
    # Try multiple key names
    return (
        creds.get('api_key') or 
        creds.get('credential_value') or
        creds.get('credentials', {}).get('api_key')
    )


def get_openai_key(user_id: int) -> Optional[str]:
    """
    Get OpenAI API key for user
    
    Args:
        user_id: User ID from authentication
    
    Returns:
        API key string or None
    """
    creds = get_user_credentials(user_id, 'openai')
    if not creds:
        return None
    
    # Try multiple key names
    return (
        creds.get('api_key') or 
        creds.get('credential_value') or
        creds.get('credentials', {}).get('api_key')
    )


def get_xero_credentials(user_id: int, business: str = 'print') -> Optional[Dict[str, str]]:
    """
    Get Xero OAuth credentials for user
    
    Args:
        user_id: User ID from authentication
        business: 'print' or 'vet' (default: 'print')
    
    Returns:
        Dict with client_id, client_secret, base_url or None
    """
    platform = f'xero_{business.lower()}'
    creds = get_user_credentials(user_id, platform)
    
    if not creds:
        return None
    
    # Extract OAuth credentials
    credentials = creds.get('credentials', {})
    return {
        'client_id': credentials.get('client_id', ''),
        'client_secret': credentials.get('client_secret', ''),
        'base_url': credentials.get('base_url', 'https://api.xero.com'),
        'business': credentials.get('business', business.title())
    }


def list_user_platforms(user_id: int, active_only: bool = True) -> list:
    """
    List all platforms user has credentials for
    
    Args:
        user_id: User ID from authentication
        active_only: Only return active credentials (default: True)
    
    Returns:
        List of platform names
    """
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT platform
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s AND is_active = TRUE
                ORDER BY platform
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT platform
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s
                ORDER BY platform
            """, (user_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows:
            print(f"[CREDENTIALS] No platforms found for user_id={user_id}")
            return []
        
        # Handle dict cursor (RealDictCursor) or tuple cursor
        if rows and isinstance(rows[0], dict):
            return [row['platform'] for row in rows]
        else:
            return [row[0] for row in rows]
        
    except Exception as e:
        print(f"[CREDENTIALS] ❌ Error listing platforms: {e}")
        import traceback
        traceback.print_exc()
        return []


def save_user_credentials(
    user_id: int, 
    platform: str, 
    credentials: Dict[str, Any],
    credential_type: str = 'api_key',
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Save or update user credentials for a platform
    
    Args:
        user_id: User ID from authentication
        platform: Platform name (assemblyai, openai, xero_print, etc.)
        credentials: Dict with credential data
        credential_type: 'api_key', 'oauth', 'basic_auth', etc.
        metadata: Optional metadata (description, urls, etc.)
    
    Returns:
        True if successful, False otherwise
    
    Examples:
        >>> save_user_credentials(1, 'assemblyai', {
        ...     'api_key': 'your-key-here'
        ... })
        
        >>> save_user_credentials(1, 'xero_print', {
        ...     'client_id': 'your-client-id',
        ...     'client_secret': 'your-secret',
        ...     'base_url': 'https://api.xero.com'
        ... }, credential_type='oauth', metadata={'business': 'Print'})
    """
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Extract primary credential (for credential_value field)
        primary_key = credentials.get('api_key') or credentials.get('client_id') or ''
        
        # Convert dicts to JSON strings
        credentials_json = json.dumps(credentials)
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Upsert (INSERT or UPDATE)
        cursor.execute("""
            INSERT INTO ai_infrastructure.user_platform_credentials (
                user_id, platform, credential_type, credential_key, 
                credential_value, credentials, metadata, is_active
            )
            VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, TRUE)
            ON CONFLICT (user_id, platform) 
            DO UPDATE SET
                credential_type = EXCLUDED.credential_type,
                credential_key = EXCLUDED.credential_key,
                credential_value = EXCLUDED.credential_value,
                credentials = EXCLUDED.credentials,
                metadata = EXCLUDED.metadata,
                is_active = TRUE,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user_id, 
            platform, 
            credential_type, 
            'primary',  # credential_key
            primary_key,  # credential_value
            credentials_json, 
            metadata_json
        ))
        
        cursor.close()
        conn.commit()
        conn.close()
        
        print(f"[CREDENTIALS] ✅ Saved credentials for user_id={user_id}, platform={platform}")
        return True
        
    except Exception as e:
        print(f"[CREDENTIALS] ❌ Error saving credentials: {e}")
        return False


# Convenience functions for common platforms
def has_assemblyai(user_id: int) -> bool:
    """Check if user has AssemblyAI credentials"""
    return get_assemblyai_key(user_id) is not None


def has_openai(user_id: int) -> bool:
    """Check if user has OpenAI credentials"""
    return get_openai_key(user_id) is not None


def has_xero(user_id: int, business: str = 'print') -> bool:
    """Check if user has Xero credentials"""
    return get_xero_credentials(user_id, business) is not None


if __name__ == '__main__':
    # Test queries
    print("\n=== Platform Credentials Loader Test ===\n")
    
    # Test user_id 1
    user_id = 1
    
    print(f"Testing user_id={user_id}...\n")
    
    # List all platforms
    platforms = list_user_platforms(user_id)
    print(f"✅ User has credentials for {len(platforms)} platforms:")
    for platform in platforms:
        print(f"   - {platform}")
    
    # Test Xero
    xero_creds = get_xero_credentials(user_id, 'print')
    if xero_creds:
        print(f"\n✅ Xero Print credentials:")
        print(f"   Client ID: {xero_creds['client_id'][:20]}...")
        print(f"   Client Secret: {xero_creds['client_secret'][:20]}...")
        print(f"   Base URL: {xero_creds['base_url']}")
    else:
        print("\n❌ No Xero Print credentials found")
    
    # Test AssemblyAI
    assemblyai_key = get_assemblyai_key(user_id)
    if assemblyai_key:
        print(f"\n✅ AssemblyAI API key: {assemblyai_key[:20]}...")
    else:
        print("\n❌ No AssemblyAI credentials found")
    
    # Test OpenAI
    openai_key = get_openai_key(user_id)
    if openai_key:
        print(f"\n✅ OpenAI API key: {openai_key[:20]}...")
    else:
        print("\n❌ No OpenAI credentials found")
    
    print("\n" + "="*50 + "\n")
