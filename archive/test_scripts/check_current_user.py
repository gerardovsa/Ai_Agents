"""Check current user and their OAuth tokens"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print("="*60)
print(" Current Users and Their OAuth Tokens")
print("="*60)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get all users
sql, params = convert_sql_placeholders("""
    SELECT id, username, email, role, is_active
    FROM users
    ORDER BY id
""")

users = cursor.fetchall()

print(f"\nFound {len(users)} user(s):\n")

for user in users:
    user_id, username, email, role, is_active = user
    
    print(f"User ID {user_id}: {username} ({email})")
    print(f"  Role: {role}, Active: {is_active}")
    
    # Check for OAuth tokens
    cursor.execute("""
        SELECT platform, email, is_valid, is_active
        FROM oauth_tokens
        WHERE user_id = ?
    """, (user_id,))

cursor.execute(sql, params)
    
    tokens = cursor.fetchall()
    
    if tokens:
        print(f"  OAuth Tokens:")
        for token in tokens:
            platform, token_email, valid, active = token
            print(f"    - {platform}: {token_email or 'No email'} (Valid: {valid}, Active: {active})")
    else:
        print(f"  No OAuth tokens")
    print()

# Check user_sessions to see who's logged in
cursor.execute("""
    SELECT user_id, COUNT(*) as session_count
    FROM user_sessions
    WHERE expires_at > datetime('now')
    GROUP BY user_id
""")

sessions = cursor.fetchall()

if sessions:
    print("\nActive sessions:")
    for user_id, count in sessions:
        sql, params = convert_sql_placeholders("SELECT username FROM users WHERE id = ?", (user_id,))

        cursor.execute(sql, params)
        username = cursor.fetchone()
        print(f"  User {user_id} ({username[0] if username else 'Unknown'}): {count} session(s)")
else:
    print("\nNo active sessions found")

conn.close()

print("="*60)
