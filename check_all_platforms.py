"""Check all platform credentials"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.db_connection_wrapper import get_connection

conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, user_id, platform, is_active 
    FROM ai_infrastructure.user_platform_credentials 
    WHERE user_id = 1
    ORDER BY platform
""")

rows = cursor.fetchall()

print('All Platform Credentials for User 1:')
print('='*80)

for r in rows:
    print(f'ID: {r["id"]}, Platform: {r["platform"]}, Active: {r["is_active"]}')

cursor.close()
conn.close()
