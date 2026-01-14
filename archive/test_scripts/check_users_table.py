"""Check users table schema and existing users"""
import sqlite3
from pathlib import Path

root = Path(__file__).parent
db = root / 'data' / 'ai_infrastructure.db'

conn = sqlite3.connect(str(db))
cur = conn.cursor()

# Get table schema
cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
schema = cur.fetchone()

print("=" * 80)
print("USERS TABLE SCHEMA:")
print("=" * 80)
if schema:
    print(schema[0])
else:
    print("❌ Table 'users' not found!")

print("\n" + "=" * 80)
print("EXISTING USERS:")
print("=" * 80)

# Get all users
try:
    cur.execute("SELECT id, username, email, role FROM users")
    users = cur.fetchall()
    
    if users:
        for user in users:
            print(f"ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}")
    else:
        print("⚠️  No users found in table")
except Exception as e:
    print(f"❌ Error querying users: {e}")

conn.close()

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("=" * 80)
print("If User 1 doesn't exist, create it with:")
print("INSERT INTO users (id, username, email, role) VALUES (1, 'admin', 'admin@example.com', 'owner');")
