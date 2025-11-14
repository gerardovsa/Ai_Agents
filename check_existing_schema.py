import sqlite3

conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

print("=" * 80)
print("EXISTING DATABASE SCHEMA")
print("=" * 80)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

print(f"\nFound {len(tables)} tables:")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "=" * 80)
print("USERS TABLE SCHEMA")
print("=" * 80)

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("❌ users table does NOT exist")

print("\n" + "=" * 80)
print("OAUTH_TOKENS TABLE SCHEMA")
print("=" * 80)

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='oauth_tokens'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("❌ oauth_tokens table does NOT exist")

print("\n" + "=" * 80)
print("USER_PLATFORM_CREDENTIALS TABLE SCHEMA")
print("=" * 80)

cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='user_platform_credentials'")
result = cursor.fetchone()
if result:
    print(result[0])
else:
    print("❌ user_platform_credentials table does NOT exist")

# Check if there are any existing users
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"\n\n📊 Existing users in database: {user_count}")

if user_count > 0:
    print("\n🔍 Sample users:")
    cursor.execute("SELECT id, username, email, role, created_at FROM users LIMIT 5")
    for row in cursor.fetchall():
        print(f"  ID {row[0]}: {row[1]} ({row[2]}) - Role: {row[3]} - Created: {row[4]}")

conn.close()
