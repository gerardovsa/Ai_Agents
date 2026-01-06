"""
Clean up old 'microsoft365' platform tokens
============================================
from shared.database_utils import convert_sql_placeholders

Removes tokens with platform='microsoft365' (old naming convention)
Keeps only tokens with platform='microsoft' (standardized naming)

This is safe to run - the old microsoft365 tokens are duplicates with less data.
The correct 'microsoft' tokens have full OAuth data with refresh tokens and expiry.
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent.parent.parent / "data" / "ai_infrastructure.db"

print("\n" + "="*70)
print("CLEANUP OLD 'microsoft365' TOKENS")
print("="*70)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Show what will be deleted
print("\n1. TOKENS TO BE DELETED:")
print("-" * 70)
cursor.execute("""
    SELECT 
        id, user_id, account_identifier, created_at, updated_at
    FROM oauth_tokens 
    WHERE platform = 'microsoft365'
    ORDER BY id
""")

rows = cursor.fetchall()

if not rows:
    print("\n✅ No 'microsoft365' tokens found - already clean!")
    conn.close()
    exit(0)

print(f"\nFound {len(rows)} tokens with platform='microsoft365':")
for row in rows:
    print(f"\n  Token ID: {row[0]}")
    print(f"  User ID: {row[1]}")
    print(f"  Account: {row[2] if row[2] else '(empty)'}")
    print(f"  Created: {row[3]}")
    print(f"  Updated: {row[4]}")

# Show what will remain
print("\n\n2. TOKENS THAT WILL REMAIN:")
print("-" * 70)
cursor.execute("""
    SELECT 
        id, user_id, account_identifier, expires_at, created_at, updated_at
    FROM oauth_tokens 
    WHERE platform = 'microsoft'
    ORDER BY id
""")

rows = cursor.fetchall()

if rows:
    print(f"\n{len(rows)} tokens with platform='microsoft' (CORRECT):")
    for row in rows:
        print(f"\n  Token ID: {row[0]}")
        print(f"  User ID: {row[1]}")
        print(f"  Account: {row[2] if row[2] else '(empty)'}")
        print(f"  Expires: {row[3]}")
        print(f"  Created: {row[4]}")
        print(f"  Updated: {row[5]}")
else:
    print("\n⚠️  No 'microsoft' tokens found - this is unusual!")
    print("   Review before deleting microsoft365 tokens")

# Confirm
print("\n\n" + "="*70)
response = input("Delete microsoft365 tokens? (yes/no): ").strip().lower()

if response == 'yes':
    # Backup first
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS _BACKUP_microsoft365_tokens AS
        SELECT * FROM oauth_tokens WHERE platform = 'microsoft365'
    """)
    
    print("\n✅ Backup created: _BACKUP_microsoft365_tokens table")
    
    # Delete
    cursor.execute("DELETE FROM oauth_tokens WHERE platform = 'microsoft365'")
    deleted_count = cursor.rowcount
    
    conn.commit()
    
    print(f"✅ Deleted {deleted_count} tokens with platform='microsoft365'")
    print("\n📋 Summary:")
    print(f"   - Backup table: _BACKUP_microsoft365_tokens")
    print(f"   - Deleted: {deleted_count} tokens")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM oauth_tokens WHERE platform='microsoft365'")
    remaining = cursor.fetchone()[0]
    
    if remaining == 0:
        print(f"   - Remaining microsoft365 tokens: 0 ✅")
        print("\n🎉 Cleanup complete! All microsoft365 tokens removed.")
    else:
        print(f"   - Remaining microsoft365 tokens: {remaining} ⚠️")
        print("\n⚠️  Some tokens were not deleted - check manually")
    
else:
    print("\n❌ Cancelled - no changes made")

conn.close()

print("\n" + "="*70)
