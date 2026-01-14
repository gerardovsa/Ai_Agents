"""
Check Microsoft OAuth Tokens for gerardo@minivetguide.onmicrosoft.com
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent.parent / "data" / "ai_infrastructure.db"

print("\n" + "="*70)
print("MICROSOFT OAUTH TOKEN VERIFICATION")
print("="*70)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check all Microsoft tokens
print("\n1. ALL MICROSOFT TOKENS:")
print("-" * 70)
cursor.execute("""
    SELECT 
        id, user_id, platform, account_name, account_identifier,
        expires_at, is_active, is_valid, created_at, updated_at
    FROM oauth_tokens 
    WHERE platform IN ('microsoft', 'microsoft365')
    ORDER BY updated_at DESC
""")

rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"\nToken ID: {row[0]}")
        print(f"  User ID: {row[1]}")
        print(f"  Platform: {row[2]}")
        print(f"  Account Name: {row[3]}")
        print(f"  Account Identifier: {row[4]}")
        print(f"  Expires At: {row[5]}")
        print(f"  Is Active: {row[6]}")
        print(f"  Is Valid: {row[7]}")
        print(f"  Created: {row[8]}")
        print(f"  Updated: {row[9]}")
else:
    print("\n❌ No Microsoft tokens found in database")

# Check specific account
print("\n\n2. GERARDO@MINIVETGUIDE.ONMICROSOFT.COM TOKEN:")
print("-" * 70)
cursor.execute("""
    SELECT 
        id, user_id, platform, account_name, account_identifier,
        access_token, refresh_token, expires_at, scope,
        is_active, is_valid, metadata, created_at, updated_at
    FROM oauth_tokens 
    WHERE platform IN ('microsoft', 'microsoft365')
    AND (
        LOWER(account_identifier) LIKE '%gerardo%' 
        OR LOWER(account_name) LIKE '%gerardo%'
        OR LOWER(metadata) LIKE '%gerardo%'
        OR LOWER(metadata) LIKE '%minivetguide%'
    )
    ORDER BY updated_at DESC
""")

rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"\n✅ Found token for gerardo@minivetguide.onmicrosoft.com")
        print(f"  Token ID: {row[0]}")
        print(f"  User ID: {row[1]}")
        print(f"  Platform: {row[2]} {'⚠️ (should be microsoft)' if row[2] == 'microsoft365' else '✅'}")
        print(f"  Account Name: {row[3]}")
        print(f"  Account Identifier: {row[4]}")
        print(f"  Has Access Token: {'✅ YES' if row[5] else '❌ NO'}")
        print(f"  Has Refresh Token: {'✅ YES' if row[6] else '❌ NO'}")
        print(f"  Expires At: {row[7]}")
        print(f"  Scope: {row[8]}")
        print(f"  Is Active: {'✅ YES' if row[9] else '❌ NO'}")
        print(f"  Is Valid: {'✅ YES' if row[10] else '❌ NO'}")
        print(f"  Metadata: {row[11][:100] if row[11] else 'None'}...")
        print(f"  Created: {row[12]}")
        print(f"  Updated: {row[13]}")
else:
    print("\n❌ No token found for gerardo@minivetguide.onmicrosoft.com")

# Check user table
print("\n\n3. USER TABLE VERIFICATION:")
print("-" * 70)
cursor.execute("""
    SELECT id, username, email, has_microsoft_oauth, is_active
    FROM users
    ORDER BY id
""")

rows = cursor.fetchall()

if rows:
    for row in rows:
        print(f"\nUser ID: {row[0]}")
        print(f"  Username: {row[1]}")
        print(f"  Email: {row[2]}")
        print(f"  Has Microsoft OAuth: {'✅ YES' if row[3] else '❌ NO'}")
        print(f"  Is Active: {'✅ YES' if row[4] else '❌ NO'}")
else:
    print("\n❌ No users found")

# Check old table
print("\n\n4. OLD user_platform_credentials TABLE:")
print("-" * 70)
cursor.execute("""
    SELECT 
        id, user_id, platform, credential_key, 
        is_active, created_at, updated_at
    FROM user_platform_credentials 
    WHERE platform IN ('microsoft', 'microsoft365')
    ORDER BY updated_at DESC
""")

rows = cursor.fetchall()

if rows:
    print(f"\n⚠️  Found {len(rows)} Microsoft credentials in OLD table (should be migrated to oauth_tokens)")
    for row in rows:
        print(f"\n  ID: {row[0]}")
        print(f"  User ID: {row[1]}")
        print(f"  Platform: {row[2]}")
        print(f"  Credential Key: {row[3]}")
        print(f"  Is Active: {row[4]}")
        print(f"  Created: {row[5]}")
        print(f"  Updated: {row[6]}")
else:
    print("\n✅ No Microsoft credentials in old table (good - all migrated)")

# Summary
print("\n\n" + "="*70)
print("SUMMARY")
print("="*70)

cursor.execute("SELECT COUNT(*) FROM oauth_tokens WHERE platform='microsoft'")
microsoft_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM oauth_tokens WHERE platform='microsoft365'")
microsoft365_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM user_platform_credentials WHERE platform IN ('microsoft', 'microsoft365')")
old_table_count = cursor.fetchone()[0]

print(f"\nOAuth Tokens (CORRECT):")
print(f"  platform='microsoft': {microsoft_count} tokens ✅")
print(f"  platform='microsoft365': {microsoft365_count} tokens {'⚠️ (should be 0)' if microsoft365_count > 0 else '✅'}")

print(f"\nOld Table (DEPRECATED):")
print(f"  user_platform_credentials: {old_table_count} tokens {'⚠️ (should be 0)' if old_table_count > 0 else '✅'}")

if microsoft365_count > 0:
    print("\n⚠️ RECOMMENDATION: Clean up old 'microsoft365' tokens")
    print("   Run: DELETE FROM oauth_tokens WHERE platform='microsoft365';")

if old_table_count > 0:
    print("\n⚠️ RECOMMENDATION: Migrate old credentials to oauth_tokens")
    print("   Or delete if no longer needed")

conn.close()

print("\n" + "="*70)
