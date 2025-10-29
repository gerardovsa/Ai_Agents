"""Find which database has the users table with actual data"""
import sqlite3
import os

databases = [
    'AI_infrastructure/data/users.db',
    'AI_infrastructure/ai_infrastructure.db',
    'AI_infrastructure/data/sessions.db',
    'data/sessions.db'
]

print("=" * 60)
print("SEARCHING FOR USERS TABLE")
print("=" * 60)

for db_path in databases:
    if os.path.exists(db_path):
        print(f"\n📁 {db_path}")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            print(f"   Tables: {[t[0] for t in tables]}")
            
            # Check if users table exists
            if any(t[0] == 'users' for t in tables):
                print("   ✅ Has 'users' table!")
                
                # Get user count and sample data
                count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                print(f"   User count: {count}")
                
                if count > 0:
                    users = cursor.execute("SELECT id, username, email FROM users LIMIT 5").fetchall()
                    print(f"   Sample users:")
                    for user in users:
                        print(f"     - ID {user[0]}: {user[1]} ({user[2]})")
            
            # Check for user_platform_credentials
            if any(t[0] == 'user_platform_credentials' for t in tables):
                print("   ✅ Has 'user_platform_credentials' table!")
                count = cursor.execute("SELECT COUNT(*) FROM user_platform_credentials").fetchone()[0]
                print(f"   Credential count: {count}")
                
                if count > 0:
                    creds = cursor.execute("SELECT user_id, platform, credential_type FROM user_platform_credentials LIMIT 3").fetchall()
                    for cred in creds:
                        print(f"     - User {cred[0]}: {cred[1]} ({cred[2]})")
            
            conn.close()
        except Exception as e:
            print(f"   ❌ Error: {e}")
    else:
        print(f"\n📁 {db_path} - NOT FOUND")

print("\n" + "=" * 60)
