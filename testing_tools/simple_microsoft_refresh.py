"""
Simple Microsoft Token Refresh (Direct SQL + Requests)
No dependency on UserAuthManager - uses direct HTTP requests
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
import requests
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import dotenv_values

# Load credentials
env_path = Path(__file__).parent.parent / '.env.master'
config = dotenv_values(env_path)

MICROSOFT_CLIENT_ID = config.get('MICROSOFT_CLIENT_ID')
MICROSOFT_CLIENT_SECRET = config.get('MICROSOFT_CLIENT_SECRET')
MICROSOFT_TENANT_ID = config.get('MICROSOFT_TENANT_ID', 'common')

def get_db_connection():
    """Get database connection"""
    root_dir = Path(__file__).parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    return sqlite3.connect(str(db_path))

def refresh_token_with_microsoft(refresh_token: str):
    """
    Refresh Microsoft access token using refresh token
    
    Args:
        refresh_token: Microsoft refresh token
        
    Returns:
        dict with new access_token, refresh_token, expires_in
    """
    
    token_url = f'https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}/oauth2/v2.0/token'
    
    data = {
        'client_id': MICROSOFT_CLIENT_ID,
        'client_secret': MICROSOFT_CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'scope': 'https://graph.microsoft.com/.default offline_access'
    }
    
    print(f"   Calling: {token_url}")
    print(f"   Client ID: {MICROSOFT_CLIENT_ID[:20]}...")
    
    response = requests.post(token_url, data=data)
    
    if response.status_code == 200:
        tokens = response.json()
        return {
            'success': True,
            'access_token': tokens['access_token'],
            'refresh_token': tokens.get('refresh_token', refresh_token),
            'expires_in': tokens.get('expires_in', 3600)
        }
    else:
        return {
            'success': False,
            'error': response.text
        }

def main():
    """Main entry point"""
    
    print("=" * 70)
    print("SIMPLE MICROSOFT TOKEN REFRESH (Direct HTTP)")
    print("=" * 70)
    
    # Check config
    if not MICROSOFT_CLIENT_ID or not MICROSOFT_CLIENT_SECRET:
        print("\n❌ Microsoft credentials not configured in .env.master")
        print("   Required: MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET")
        return
    
    print(f"\n✅ Microsoft credentials loaded")
    print(f"   Client ID: {MICROSOFT_CLIENT_ID[:20]}...")
    print(f"   Tenant: {MICROSOFT_TENANT_ID}")
    
    # Get expired Microsoft tokens
    conn = get_db_connection()
    cursor = conn.cursor()
    sql, params = convert_sql_placeholders('''
        SELECT id, user_id, account_name, account_identifier, expires_at, refresh_token
        FROM oauth_tokens
        WHERE platform = ?
        ORDER BY user_id
    ''', ('microsoft',))

    cursor.execute(sql, params)
    
    tokens = cursor.fetchall()
    
    if not tokens:
        print("\n❌ No Microsoft tokens found")
        conn.close()
        return
    
    print(f"\nFound {len(tokens)} Microsoft token(s):\n")
    
    refreshed = 0
    failed = 0
    active = 0
    
    for token_row in tokens:
        token_id, user_id, account_name, account_identifier, expires_at, refresh_token = token_row
        
        account = account_name or account_identifier or f"User {user_id}"
        
        print(f"\nUser {user_id}: {account}")
        print(f"  Token ID: {token_id}")
        print(f"  Expires: {expires_at}")
        
        # Check expiration
        exp_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        now_dt = datetime.now()
        expired = now_dt > exp_dt
        
        if not expired:
            print(f"  Status: ✅ ACTIVE (not expired)")
            active += 1
            continue
        
        print(f"  Status: ⚠️ EXPIRED")
        
        if not refresh_token:
            print(f"  ❌ No refresh token - user must re-authenticate")
            failed += 1
            continue
        
        print(f"  🔄 Refreshing token...")
        
        # Refresh token
        result = refresh_token_with_microsoft(refresh_token)
        
        if result['success']:
            # Calculate new expiration
            new_expires_at = (datetime.now() + timedelta(seconds=result['expires_in'])).strftime('%Y-%m-%d %H:%M:%S')
            
            # Update database
            sql, params = convert_sql_placeholders('''
                UPDATE oauth_tokens
                SET access_token = ?,
                    refresh_token = ?,
                    expires_at = ?,
                    last_refreshed_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP,
                    is_valid = 1,
                    is_active = 1,
                    refresh_attempts = 0,
                    last_refresh_error = NULL
                WHERE id = ?
            ''', (
                result['access_token'],
                result['refresh_token'],
                new_expires_at,
                token_id
            ))

            cursor.execute(sql, params)
            
            conn.commit()
            
            print(f"  ✅ Token refreshed successfully!")
            print(f"  New expiration: {new_expires_at}")
            refreshed += 1
        else:
            print(f"  ❌ Refresh failed: {result['error'][:100]}...")
            
            # Update error in database
            sql, params = convert_sql_placeholders('''
                UPDATE oauth_tokens
                SET refresh_attempts = refresh_attempts + 1,
                    last_refresh_error = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (result['error'][:500], token_id))

            cursor.execute(sql, params)
            
            conn.commit()
            failed += 1
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("REFRESH SUMMARY")
    print("=" * 70)
    print(f"✅ Refreshed: {refreshed}")
    print(f"⚠️ Active (not expired): {active}")
    print(f"❌ Failed: {failed}")
    print("=" * 70)

if __name__ == '__main__':
    main()
