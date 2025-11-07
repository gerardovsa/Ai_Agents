"""Check what credentials are in the database"""
import sqlite3
from pathlib import Path
import json

db_path = Path('data/ai_infrastructure.db')
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get all credentials for user 1
cursor.execute('''
    SELECT id, user_id, platform, credential_type, credential_key, 
           credential_value, is_active, created_at 
    FROM user_platform_credentials 
    WHERE user_id = 1
''')
rows = cursor.fetchall()
print(f'Credentials in user_platform_credentials for user 1: {len(rows)} rows\n')
for row in rows:
    print(f'ID: {row["id"]}')
    print(f'  Platform: {row["platform"]}')
    print(f'  Type: {row["credential_type"]}')
    print(f'  Key: {row["credential_key"]}')
    value_preview = row['credential_value'][:50] if row['credential_value'] else None
    print(f'  Value: {value_preview}...')
    print(f'  Active: {row["is_active"]}')
    print()

# Check oauth_tokens table too
print('='*60)
print('Checking oauth_tokens table:')
cursor.execute('PRAGMA table_info(oauth_tokens)')
columns = cursor.fetchall()
for col in columns:
    print(f'  - {col[1]} ({col[2]})')

cursor.execute('SELECT user_id, platform, access_token FROM oauth_tokens WHERE user_id = 1')
rows = cursor.fetchall()
print(f'\nOAuth tokens for user 1 in oauth_tokens: {len(rows)} rows')
for row in rows:
    token_preview = row['access_token'][:20] if row['access_token'] else None
    print(f'  - {row["platform"]}: {token_preview}...')

conn.close()
