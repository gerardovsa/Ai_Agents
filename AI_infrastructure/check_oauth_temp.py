import sqlite3

conn = sqlite3.connect('ai_infrastructure.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check user 4's credentials
cursor.execute('''
    SELECT user_id, platform, credential_type, credential_key, is_active, created_at 
    FROM user_platform_credentials 
    WHERE user_id=4 
    ORDER BY created_at DESC
''')

rows = cursor.fetchall()

print('\n=== User 4 Platform Credentials ===')
if rows:
    for row in rows:
        print(f"Platform: {row['platform']}, Type: {row['credential_type']}, Key: {row['credential_key']}, Active: {row['is_active']}, Created: {row['created_at']}")
else:
    print("No credentials found for user 4")

# Check user 4's account info
cursor.execute('SELECT id, username, email, password_hash FROM users WHERE id=4')
user = cursor.fetchone()
if user:
    print(f"\n=== User 4 Info ===")
    print(f"Username: {user['username']}")
    print(f"Email: {user['email']}")
    print(f"Password Hash: {user['password_hash']}")
else:
    print("User 4 not found!")

conn.close()
