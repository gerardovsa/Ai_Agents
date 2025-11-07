import sqlite3

# Check sessions.db structure
conn = sqlite3.connect('data/sessions.db')
cursor = conn.cursor()

print("=" * 60)
print("SESSIONS.DB STRUCTURE CHECK")
print("=" * 60)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print(f"\nFound {len(tables)} tables:")
for table in tables:
    print(f"  - {table[0]}")

# Check if users table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
users_table = cursor.fetchone()

if users_table:
    print("\n✅ users table EXISTS")
    
    # Get schema
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("\nColumns:")
    for col in columns:
        print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PRIMARY KEY' if col[5] else ''}")
    
    # Check if user_id=1 exists
    cursor.execute("SELECT id, username, email FROM users WHERE id = 1")
    user_1 = cursor.fetchone()
    
    if user_1:
        print(f"\n✅ User ID 1 EXISTS: username={user_1[1]}, email={user_1[2]}")
        
        # Check metadata
        cursor.execute("SELECT metadata FROM users WHERE id = 1")
        metadata = cursor.fetchone()
        if metadata and metadata[0]:
            print(f"\nMetadata: {metadata[0][:200]}...")
        else:
            print("\n⚠️  Metadata is NULL or empty")
    else:
        print("\n❌ User ID 1 DOES NOT EXIST")
        
        # Show all users
        cursor.execute("SELECT id, username, email FROM users")
        all_users = cursor.fetchall()
        print(f"\nAll users in database ({len(all_users)}):")
        for user in all_users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
else:
    print("\n❌ users table DOES NOT EXIST")

conn.close()

print("\n" + "=" * 60)
