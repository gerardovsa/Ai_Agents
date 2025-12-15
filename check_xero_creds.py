"""Check Xero credentials in Supabase"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.db_connection_wrapper import get_connection
import json

conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, user_id, platform, is_active, credentials 
    FROM ai_infrastructure.user_platform_credentials 
    WHERE platform IN ('xero_print', 'xero_pub', 'xero_signs') 
    ORDER BY platform
""")

rows = cursor.fetchall()

print('Xero Credentials in Supabase:')
print('='*80)

for r in rows:
    # psycopg returns dict-like rows
    print(f'ID: {r["id"]}, User: {r["user_id"]}, Platform: {r["platform"]}, Active: {r["is_active"]}')
    creds = r["credentials"]
    if creds:
        print(f'  Credentials keys: {list(creds.keys())}')
        print(f'  Has client_id: {"client_id" in creds}')
        print(f'  Has client_secret: {"client_secret" in creds}')
        if 'client_id' in creds:
            print(f'  client_id: {creds["client_id"][:20]}...' if len(creds['client_id']) > 20 else f'  client_id: {creds["client_id"]}')
        print(f'  Full JSON:\n{json.dumps(creds, indent=2)}')
    else:
        print('  Credentials: NULL')
    print('-'*80)

cursor.close()
conn.close()
