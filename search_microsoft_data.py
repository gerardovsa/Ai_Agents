import sqlite3

conn = sqlite3.connect('data/ai_infrastructure.db')
cursor = conn.cursor()

print("=" * 80)
print("SEARCHING ALL TABLES FOR MICROSOFT DATA")
print("=" * 80)

# Check oauth_tokens with various platform names
platforms_to_check = ['microsoft', 'microsoft_365', 'microsoft365', 'outlook', 'Microsoft', 'MICROSOFT']

for platform in platforms_to_check:
    cursor.execute("SELECT COUNT(*) FROM oauth_tokens WHERE platform = ?", (platform,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"\n✅ Found {count} rows in oauth_tokens with platform='{platform}'")
        cursor.execute("""
            SELECT user_id, email, is_active, expires_at
            FROM oauth_tokens
            WHERE platform = ?
        """, (platform,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"   User ID: {row[0]}, Email: {row[1]}, Active: {row[2]}, Expires: {row[3]}")
    else:
        print(f"❌ No rows in oauth_tokens with platform='{platform}'")

# Check user_platform_credentials
print("\n" + "=" * 80)
print("CHECKING user_platform_credentials TABLE")
print("=" * 80)

for platform in platforms_to_check:
    cursor.execute("SELECT COUNT(*) FROM user_platform_credentials WHERE platform = ?", (platform,))
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"\n✅ Found {count} rows in user_platform_credentials with platform='{platform}'")
        cursor.execute("""
            SELECT user_id, is_active, updated_at
            FROM user_platform_credentials
            WHERE platform = ?
        """, (platform,))
        rows = cursor.fetchall()
        for row in rows:
            print(f"   User ID: {row[0]}, Active: {row[1]}, Updated: {row[2]}")

# Get ALL rows from oauth_tokens to see what platforms exist
print("\n" + "=" * 80)
print("ALL PLATFORMS IN oauth_tokens TABLE")
print("=" * 80)

cursor.execute("SELECT DISTINCT platform, COUNT(*) FROM oauth_tokens GROUP BY platform")
all_platforms = cursor.fetchall()
if all_platforms:
    for plat in all_platforms:
        print(f"  Platform: '{plat[0]}', Count: {plat[1]}")
else:
    print("  (empty table)")

# Get ALL rows from user_platform_credentials
print("\n" + "=" * 80)
print("ALL PLATFORMS IN user_platform_credentials TABLE")
print("=" * 80)

cursor.execute("SELECT DISTINCT platform, COUNT(*) FROM user_platform_credentials GROUP BY platform")
all_platforms2 = cursor.fetchall()
if all_platforms2:
    for plat in all_platforms2:
        print(f"  Platform: '{plat[0]}', Count: {plat[1]}")
else:
    print("  (empty table)")

conn.close()

print("\n" + "=" * 80)
print("SEARCH COMPLETE")
print("=" * 80)
