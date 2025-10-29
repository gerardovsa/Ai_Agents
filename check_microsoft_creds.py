"""Check Microsoft credentials in database"""
import sqlite3

conn = sqlite3.connect('AI_infrastructure/ai_infrastructure.db')
cursor = conn.cursor()

print("=" * 60)
print("MICROSOFT OAUTH CREDENTIALS CHECK")
print("=" * 60)

# Check all credentials
all_creds = cursor.execute('''
    SELECT user_id, platform, credential_key 
    FROM user_platform_credentials
''').fetchall()

print(f"\nAll credentials in database: {len(all_creds)}")
for cred in all_creds:
    print(f"  - User {cred[0]}: {cred[1]} ({cred[2]})")

# Check specifically for Microsoft
microsoft_creds = cursor.execute('''
    SELECT user_id, platform, credential_key 
    FROM user_platform_credentials 
    WHERE platform LIKE '%microsoft%' OR platform LIKE '%365%'
''').fetchall()

print(f"\nMicrosoft credentials: {len(microsoft_creds)}")
if microsoft_creds:
    for cred in microsoft_creds:
        print(f"  - User {cred[0]}: {cred[1]} ({cred[2]})")
else:
    print("  ❌ None found")
    print("\n  To use Microsoft tools, users need to:")
    print("  1. Sign in with Microsoft via the web UI")
    print("  2. Authorize the application")
    print("  3. OAuth tokens will be stored in database")

conn.close()

print("\n" + "=" * 60)
