"""
Check what users and credentials exist in the database
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "AI_infrastructure" / "ai_infrastructure.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("👤 USERS IN DATABASE")
print("="*60)

cursor.execute("SELECT id, username, email, role, created_at FROM users")
users = cursor.fetchall()

for user_id, username, email, role, created_at in users:
    print(f"\n User ID: {user_id}")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print(f"   Role: {role}")
    print(f"   Created: {created_at}")
    
    # Check platform credentials
    sql, params = convert_sql_placeholders("""
        SELECT platform, credential_type, credential_key, is_active
        FROM user_platform_credentials
        WHERE user_id = ?
    """, (user_id,))

    cursor.execute(sql, params)
    
    creds = cursor.fetchall()
    if creds:
        print(f"   Platform Credentials:")
        for platform, cred_type, cred_key, is_active in creds:
            active_marker = "" if is_active else ""
            print(f"      {active_marker} {platform} - {cred_type} ({cred_key})")
    else:
        print(f"   ⚠️  No platform credentials")

print("\n" + "="*60)
print("🔑 ALL PLATFORM CREDENTIALS")
print("="*60)

cursor.execute("""
    SELECT u.id, u.username, u.email, upc.platform, upc.credential_type, upc.credential_key, upc.is_active
    FROM users u
    LEFT JOIN user_platform_credentials upc ON u.id = upc.user_id
    ORDER BY u.id, upc.platform
""")

rows = cursor.fetchall()

for user_id, username, email, platform, cred_type, cred_key, is_active in rows:
    if platform:
        active_marker = "" if is_active else ""
        print(f"{active_marker} User {user_id} ({username}) - {platform}: {cred_type}")

conn.close()

print("\n" + "="*60)
print(" Database check complete!")
print("\nTo use these credentials with tools:")
print("1. Start the Flask server: BISTART")
print("2. Send chat request with user_id parameter")
print("3. Tools will automatically get credentials injected")
