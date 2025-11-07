"""
Search ai_infrastructure.db for printing@inhouseprint.com.au user
"""

import sqlite3
from pathlib import Path

# Connect to ai_infrastructure.db
root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print(f"Connecting to: {db_path}")
print(f"Database exists: {db_path.exists()}\n")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# List all tables
print("=" * 60)
print("AI_INFRASTRUCTURE.DB TABLES")
print("=" * 60)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table[0]}")

# Check if users table exists
print("\n" + "=" * 60)
print("USERS TABLE STRUCTURE")
print("=" * 60)
try:
    cursor.execute("PRAGMA table_info(users)")
    cols = cursor.fetchall()
    if cols:
        print("\nColumns:")
        for col in cols:
            print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL OK'} - {'PK' if col[5] else ''}")
    else:
        print("  No users table found!")
except Exception as e:
    print(f"  Error: {e}")

# Search for printing@inhouseprint.com.au
print("\n" + "=" * 60)
print("SEARCHING FOR printing@inhouseprint.com.au")
print("=" * 60)
try:
    cursor.execute("""
        SELECT * FROM users 
        WHERE email LIKE '%printing%' 
           OR email LIKE '%inhouseprint%'
    """)
    users = cursor.fetchall()
    
    if users:
        print(f"\nFound {len(users)} matching users:")
        for user in users:
            print(f"  User: {user}")
    else:
        print("\n  NO MATCHING USERS FOUND!")
except Exception as e:
    print(f"  Error: {e}")

# List ALL users
print("\n" + "=" * 60)
print("ALL USERS IN AI_INFRASTRUCTURE.DB")
print("=" * 60)
try:
    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()
    
    print(f"\nTotal users: {len(all_users)}")
    if all_users:
        print("\nAll user records:")
        for user in all_users:
            print(f"\n  User ID: {user[0]}")
            print(f"  Email: {user[1]}")
            print(f"  Name: {user[2]}")
            print(f"  Full record: {user}")
    else:
        print("  NO USERS FOUND!")
except Exception as e:
    print(f"  Error: {e}")

conn.close()

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("\nNEXT STEPS:")
print("1. If NO users found -> Create printing@inhouseprint.com.au user")
print("2. If users exist but NOT printing@ -> Create printing@inhouseprint.com.au user")
print("3. Check sessions.db users table as well")
print("\nWould you like me to create the printing@inhouseprint.com.au user?")
