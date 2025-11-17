"""Direct database check for user 14 Microsoft credentials"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Load database config
with open('C:/Users/gpoli/GIT/AI_agents/data/database-config.json', 'r') as f:
    db_config = json.load(f)

# Get ai_infrastructure connection
ai_config = db_config['databases']['ai_infrastructure']
conn_str = f"postgresql://{ai_config['user']}:{ai_config['password']}@{ai_config['host']}:{ai_config['port']}/{ai_config['dbname']}"

conn = psycopg2.connect(conn_str)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# Query oauth_tokens for user 14
cursor.execute('''
    SELECT 
        user_id, 
        platform, 
        LENGTH(access_token) as token_length,
        refresh_token IS NOT NULL as has_refresh, 
        expires_at, 
        is_active
    FROM ai_infrastructure.oauth_tokens 
    WHERE user_id = 14
''')

rows = cursor.fetchall()

print('\n=== User 14 OAuth Tokens ===')
if not rows:
    print('  NO CREDENTIALS FOUND')
else:
    for row in rows:
        print(f"\nPlatform: {row['platform']}")
        print(f"  Token Length: {row['token_length']}")
        print(f"  Has Refresh: {row['has_refresh']}")
        print(f"  Expires: {row['expires_at']}")
        print(f"  Active: {row['is_active']}")

conn.close()
print("\n✅ Query complete")
