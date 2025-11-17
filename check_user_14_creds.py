"""Quick script to check user 14 Microsoft OAuth credentials"""

from AI_infrastructure.shared.database_utils import get_connection

conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

cursor.execute('''
    SELECT 
        user_id, 
        platform, 
        access_token IS NOT NULL as has_token, 
        refresh_token IS NOT NULL as has_refresh, 
        expires_at, 
        is_active,
        LENGTH(access_token) as token_length
    FROM oauth_tokens 
    WHERE user_id = 14
''')

rows = cursor.fetchall()

print('\n=== User 14 OAuth Tokens ===')
if not rows:
    print('  NO CREDENTIALS FOUND')
else:
    for row in rows:
        print(f"\nPlatform: {row['platform']}")
        print(f"  Has Token: {row['has_token']}")
        print(f"  Token Length: {row['token_length']}")
        print(f"  Has Refresh: {row['has_refresh']}")
        print(f"  Expires: {row['expires_at']}")
        print(f"  Active: {row['is_active']}")

conn.close()
