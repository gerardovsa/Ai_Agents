"""
Force delete the 4 unused tables - ensures they stay deleted
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'

tables_to_delete = [
    'account_link_requests',
    'thread_assignments', 
    'user_gmail_accounts',
    'user_platform_credentials'
]

print("=" * 80)
print("FORCE DELETE UNUSED TABLES")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Show current state
print("\nBEFORE:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
before = [t[0] for t in cursor.fetchall()]
print(f"  Total tables: {len(before)}")

# Delete each table
deleted = 0
for table in tables_to_delete:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table}")
        print(f"  ✅ Dropped: {table}")
        deleted += 1
    except Exception as e:
        print(f"  ❌ Error: {table} - {e}")

conn.commit()

# Show after
print("\nAFTER:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
after = [t[0] for t in cursor.fetchall()]
print(f"  Total tables: {len(after)}")

# Verify they're gone
print("\nVERIFICATION:")
for table in tables_to_delete:
    if table in after:
        print(f"  ❌ STILL EXISTS: {table}")
    else:
        print(f"  ✅ DELETED: {table}")

conn.close()

print(f"\n{'=' * 80}")
print(f"✅ Deleted {deleted}/{len(tables_to_delete)} tables")
print("=" * 80)
print("\n⚠️  IMPORTANT: These tables may be recreated on Flask startup")
print("   Files that recreate them:")
print("   - AI_infrastructure/database_toolkit/schema_manager.py")
print("   - AI_infrastructure/routes/account_linking_routes.py")
print("   - AI_infrastructure/auth/user_auth.py")
print("\n   To permanently remove: comment out CREATE TABLE statements in those files")
