"""Find users with Google OAuth credentials"""

import sqlite3

# Connect to database
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

# First, check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Available tables:")
for table in tables:
    print(f"  - {table[0]}")

print("\n" + "="*60)

# Check if oauth_tokens table exists
if any('oauth_tokens' in str(t) for t in tables):
    print("\nChecking oauth_tokens table...")
    cursor.execute("PRAGMA table_info(oauth_tokens)")
    columns = cursor.fetchall()
    print("Columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    print("\n" + "="*60)
    print("\nUsers with Google OAuth:")
    cursor.execute("""
        SELECT user_id, platform, created_at 
        FROM oauth_tokens 
        WHERE platform = 'google' 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    
    if rows:
        print("user_id | platform | created_at")
        print("-" * 60)
        for row in rows:
            print(f"{row[0]:<7} | {row[1]:<8} | {row[2]}")
        print(f"\nTotal Google OAuth users: {len(rows)}")
    else:
        print("No users with Google OAuth credentials found")
        
        # Check all users
        print("\nAll users in oauth_tokens:")
        cursor.execute("SELECT user_id, platform FROM oauth_tokens LIMIT 10")
        all_rows = cursor.fetchall()
        for row in all_rows:
            print(f"  user_id={row[0]}, platform={row[1]}")

else:
    print("\noauth_tokens table not found!")
    
    # Check user_platform_credentials table instead
    if any('user_platform_credentials' in str(t) for t in tables):
        print("\nChecking user_platform_credentials table...")
        cursor.execute("PRAGMA table_info(user_platform_credentials)")
        columns = cursor.fetchall()
        print("Columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        print("\n" + "="*60)
        print("\nUsers with Google credentials:")
        cursor.execute("""
            SELECT user_id, platform, created_at 
            FROM user_platform_credentials 
            WHERE platform = 'google' 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        rows = cursor.fetchall()
        
        if rows:
            print("user_id | platform | created_at")
            print("-" * 60)
            for row in rows:
                print(f"{row[0]:<7} | {row[1]:<8} | {row[2]}")
            print(f"\nTotal Google users: {len(rows)}")
        else:
            print("No users with Google credentials found")

conn.close()
