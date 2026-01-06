"""
Refresh Microsoft OAuth Token
Refreshes expired Microsoft OAuth tokens for active users
"""
from shared.database_utils import convert_sql_placeholders

import sys
import os
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'AI_infrastructure'))

from auth.user_auth import user_auth_manager
from datetime import datetime
import sqlite3

def get_db_connection():
    """Get database connection"""
    root_dir = Path(__file__).parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def refresh_microsoft_token(user_id: int):
    """Refresh Microsoft token for user"""
    
    print(f"\n🔄 Refreshing Microsoft token for user {user_id}...")
    
    # Get current token info
    conn = get_db_connection()
    cursor = conn.cursor()
    sql, params = convert_sql_placeholders('''
        SELECT id, account_name, expires_at, refresh_token 
        FROM oauth_tokens 
        WHERE user_id = ? AND platform = ?
    ''', (user_id, 'microsoft'))

    cursor.execute(sql, params)
    
    token_row = cursor.fetchone()
    
    if not token_row:
        print(f"❌ No Microsoft token found for user {user_id}")
        conn.close()
        return False
    
    token_id = token_row['id']
    account_name = token_row['account_name']
    expires_at = token_row['expires_at']
    refresh_token = token_row['refresh_token']
    
    print(f"   Token ID: {token_id}")
    print(f"   Account: {account_name}")
    print(f"   Expires: {expires_at}")
    
    # Check expiration
    exp_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
    now_dt = datetime.now()
    expired = now_dt > exp_dt
    
    print(f"   Status: {'⚠️ EXPIRED' if expired else '✅ ACTIVE'}")
    
    if not refresh_token:
        print(f"❌ No refresh token available - user must re-authenticate")
        conn.close()
        return False
    
    # Use user_auth_manager to refresh
    try:
        print(f"\n🔄 Requesting new access token from Microsoft...")
        
        # Get Microsoft tokens (this will auto-refresh if expired)
        tokens = user_auth_manager.get_microsoft_tokens(user_id)
        
        if tokens:
            print(f"✅ Token refreshed successfully!")
            print(f"   New expiration: {tokens.get('expires_at', 'N/A')}")
            conn.close()
            return True
        else:
            print(f"❌ Token refresh failed - check logs")
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        conn.close()
        return False

def main():
    """Main entry point"""
    
    print("=" * 70)
    print("MICROSOFT OAUTH TOKEN REFRESH")
    print("=" * 70)
    
    # Get all Microsoft tokens
    conn = get_db_connection()
    cursor = conn.cursor()
    sql, params = convert_sql_placeholders('''
        SELECT user_id, account_name, expires_at
        FROM oauth_tokens
        WHERE platform = ?
        ORDER BY user_id
    ''', ('microsoft',))

    cursor.execute(sql, params)
    
    tokens = cursor.fetchall()
    conn.close()
    
    if not tokens:
        print("\n❌ No Microsoft tokens found in database")
        return
    
    print(f"\nFound {len(tokens)} Microsoft token(s):\n")
    
    for token in tokens:
        user_id = token['user_id']
        account_name = token['account_name'] or 'Unknown'
        expires_at = token['expires_at']
        
        # Check if expired
        exp_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        now_dt = datetime.now()
        expired = now_dt > exp_dt
        
        status = "⚠️ EXPIRED" if expired else "✅ ACTIVE"
        
        print(f"User {user_id}: {account_name}")
        print(f"  Expires: {expires_at} {status}")
        
        if expired:
            print(f"  → Will refresh this token")
    
    print("\n" + "=" * 70)
    
    # Refresh expired tokens
    refreshed = 0
    failed = 0
    
    for token in tokens:
        user_id = token['user_id']
        expires_at = token['expires_at']
        
        # Check if expired
        exp_dt = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')
        now_dt = datetime.now()
        
        if now_dt > exp_dt:
            if refresh_microsoft_token(user_id):
                refreshed += 1
            else:
                failed += 1
    
    print("\n" + "=" * 70)
    print("REFRESH SUMMARY")
    print("=" * 70)
    print(f"✅ Refreshed: {refreshed}")
    print(f"❌ Failed: {failed}")
    print("=" * 70)

if __name__ == '__main__':
    main()
