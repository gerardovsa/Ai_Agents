"""Check Microsoft OAuth token status for user 14"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'AI_infrastructure'))

from shared.db_connection_wrapper import get_connection
from datetime import datetime, timezone

conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

print("\n" + "="*70)
print("MICROSOFT OAUTH TOKEN STATUS - USER 14")
print("="*70)

cursor.execute("""
    SELECT id, user_id, platform, access_token, refresh_token, expires_at, 
           is_active, is_valid, created_at, updated_at
    FROM ai_infrastructure.oauth_tokens 
    WHERE user_id = 14 AND platform = 'microsoft'
    ORDER BY updated_at DESC 
    LIMIT 1
""")

row = cursor.fetchone()

if not row:
    print("\n❌ NO MICROSOFT OAUTH TOKEN FOUND FOR USER 14!")
    print("\nUser needs to authenticate with Microsoft.")
else:
    token_id = row[0] if isinstance(row, tuple) else row['id']
    user_id = row[1] if isinstance(row, tuple) else row['user_id']
    platform = row[2] if isinstance(row, tuple) else row['platform']
    access_token = row[3] if isinstance(row, tuple) else row['access_token']
    refresh_token = row[4] if isinstance(row, tuple) else row['refresh_token']
    expires_at = row[5] if isinstance(row, tuple) else row['expires_at']
    is_active = row[6] if isinstance(row, tuple) else row['is_active']
    is_valid = row[7] if isinstance(row, tuple) else row['is_valid']
    created_at = row[8] if isinstance(row, tuple) else row['created_at']
    updated_at = row[9] if isinstance(row, tuple) else row['updated_at']
    
    print(f"\n✅ Token Found:")
    print(f"   ID: {token_id}")
    print(f"   User ID: {user_id}")
    print(f"   Platform: {platform}")
    print(f"   Access Token: {access_token[:50]}..." if access_token else "   Access Token: None")
    print(f"   Refresh Token: {refresh_token[:50]}..." if refresh_token else "   Refresh Token: None")
    print(f"   Expires At: {expires_at}")
    print(f"   Is Active: {is_active}")
    print(f"   Is Valid: {is_valid}")
    print(f"   Created At: {created_at}")
    print(f"   Updated At: {updated_at}")
    
    # Check if expired
    if expires_at:
        if isinstance(expires_at, str):
            try:
                expires_dt = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            except:
                expires_dt = None
        else:
            expires_dt = expires_at
        
        if expires_dt:
            if expires_dt.tzinfo is None:
                expires_dt = expires_dt.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            time_diff = expires_dt - now
            
            print(f"\n⏰ Token Status:")
            if time_diff.total_seconds() > 0:
                mins = int(time_diff.total_seconds() / 60)
                print(f"   ✅ VALID - Expires in {mins} minutes")
            else:
                mins_ago = int(abs(time_diff.total_seconds()) / 60)
                print(f"   ❌ EXPIRED - {mins_ago} minutes ago")
                print(f"   🔄 Auto-refresh should trigger on next use")

print("\n" + "="*70)
conn.close()
