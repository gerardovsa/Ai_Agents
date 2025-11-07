import sqlite3

# Check users table
conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

print("=" * 80)
print("CHECKING USERS TABLE")
print("=" * 80)
cursor.execute("SELECT id, username, email FROM users")
users = cursor.fetchall()
print(f"\nTotal users: {len(users)}")
for user in users:
    print(f"  User ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")

print("\n" + "=" * 80)
print("CHECKING TABLE SCHEMAS")
print("=" * 80)

# Get user_platform_credentials schema
cursor.execute("PRAGMA table_info(user_platform_credentials)")
columns = cursor.fetchall()
print("\nuser_platform_credentials columns:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

print("\n" + "=" * 80)
print("CHECKING MICROSOFT CREDENTIALS")
print("=" * 80)
cursor.execute("""
    SELECT * FROM user_platform_credentials
    WHERE platform = 'microsoft_365'
""")
creds = cursor.fetchall()
print(f"\nMicrosoft credentials: {len(creds)}")
for cred in creds:
    print(f"  Credential: {cred}")

print("\n" + "=" * 80)
print("CHECKING IF CREDENTIALS MATCH USER")
print("=" * 80)

# Get the user_id from CHATM token generation
microsoft_email = "Gerardo@minivetguide.onmicrosoft.com"
cursor.execute("SELECT id, username, email FROM users WHERE email = ?", (microsoft_email,))
chatm_user = cursor.fetchone()

if chatm_user:
    print(f"\n✅ CHATM User Found:")
    print(f"   User ID: {chatm_user[0]}")
    print(f"   Username: {chatm_user[1]}")
    print(f"   Email: {chatm_user[2]}")
    
    # Check if this user has credentials
    cursor.execute("""
        SELECT * FROM user_platform_credentials
        WHERE user_id = ? AND platform = 'microsoft_365'
    """, (chatm_user[0],))
    user_creds = cursor.fetchone()
    
    if user_creds:
        print(f"\n✅ Credentials Found for CHATM User:")
        print(f"   {user_creds}")
    else:
        print(f"\n❌ NO CREDENTIALS for CHATM User ID {chatm_user[0]}")
        print(f"   Credentials are for different user_id!")
        print(f"\n   Available Microsoft credentials:")
        cursor.execute("""
            SELECT user_id FROM user_platform_credentials
            WHERE platform = 'microsoft_365'
        """)
        all_creds = cursor.fetchall()
        for ac in all_creds:
            print(f"     User ID: {ac[0]}")
else:
    print(f"\n❌ CHATM User NOT Found: {microsoft_email}")
    print(f"   CHATM will create a NEW user, but credentials are for different user!")

conn.close()

print("\n" + "=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)
