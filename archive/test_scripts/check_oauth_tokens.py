"""Check what OAuth tokens exist in the database"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print("="*60)
print(" OAuth Tokens in Database")
print("="*60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all oauth tokens
cursor.execute("""
    SELECT 
        id,
        user_id,
        platform,
        email,
        account_name,
        is_active,
        is_valid,
        created_at,
        LENGTH(access_token) as token_length
    FROM oauth_tokens
    ORDER BY created_at DESC
""")

rows = cursor.fetchall()

print(f"\nFound {len(rows)} OAuth token(s):\n")

for row in rows:
    print(f"ID: {row[0]}")
    print(f"  User ID: {row[1]}")
    print(f"  Platform: {row[2]}")
    print(f"  Email: {row[3]}")
    print(f"  Account Name: {row[4]}")
    print(f"  Active: {row[5]}")
    print(f"  Valid: {row[6]}")
    print(f"  Created: {row[7]}")
    print(f"  Token Length: {row[8]} chars")
    print()

conn.close()

print("="*60)
