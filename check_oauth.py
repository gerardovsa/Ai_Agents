"""Check OAuth tokens in database"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
from shared.database_utils import get_database_connection

conn = get_database_connection('ai_infrastructure')
cursor = conn.cursor()

cursor.execute("""
    SELECT user_id, platform, email, is_active, expires_at 
    FROM ai_infrastructure.oauth_tokens 
    WHERE is_active = TRUE 
    ORDER BY user_id, platform
""")

rows = cursor.fetchall()

print('\n📧 Connected Email Accounts:\n')
if rows:
    for r in rows:
        print(f'  User {r["user_id"]}: {r["platform"]} - {r["email"]} (expires: {r["expires_at"]})')
    print(f'\n✅ Total: {len(rows)} active accounts')
else:
    print('  ❌ No OAuth tokens found')
    print('\nTo connect accounts:')
    print('  1. Open Settings → Integrations')
    print('  2. Connect Gmail or Outlook account')
    print('  3. Complete OAuth flow')

cursor.close()
conn.close()
