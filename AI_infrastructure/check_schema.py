import sqlite3

conn = sqlite3.connect('ai_infrastructure.db')
cursor = conn.cursor()

# Get users table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
result = cursor.fetchone()
if result:
    print("=== USERS TABLE ===")
    print(result[0])
    print()

# Get user_platform_credentials schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_platform_credentials'")
result = cursor.fetchone()
if result:
    print("=== USER_PLATFORM_CREDENTIALS TABLE ===")
    print(result[0])
    print()

# Get user_sessions schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_sessions'")
result = cursor.fetchone()
if result:
    print("=== USER_SESSIONS TABLE ===")
    print(result[0])
    print()

conn.close()
