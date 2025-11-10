"""
Delete 4 unused tables from ai_infrastructure.db

Tables to delete:
1. account_link_requests (0 rows, no code references)
2. thread_assignments (0 rows, using JSON instead)
3. user_gmail_accounts (0 rows, migrated to oauth_tokens)
4. user_platform_credentials (0 rows, replaced by oauth_tokens)
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'ai_infrastructure.db'

print("=" * 80)
print("DELETE UNUSED TABLES FROM ai_infrastructure.db")
print("=" * 80)

tables_to_delete = [
    ('account_link_requests', '0 rows, no code references'),
    ('thread_assignments', '0 rows, using JSON metadata instead'),
    ('user_gmail_accounts', '0 rows, migrated to oauth_tokens'),
    ('user_platform_credentials', '0 rows, replaced by oauth_tokens')
]

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check tables before
print("\nBEFORE:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
before_tables = [t[0] for t in cursor.fetchall()]
print(f"  Total tables: {len(before_tables)}")

# Check if tables exist and get row counts
print("\nTables to delete:")
for table_name, reason in tables_to_delete:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  ✓ {table_name}: {count} rows ({reason})")
    except sqlite3.OperationalError:
        print(f"  ✗ {table_name}: NOT FOUND (already deleted?)")

# Delete tables
print(f"\n{'=' * 80}")
print("DELETING TABLES...")
print("=" * 80)

deleted = 0
for table_name, reason in tables_to_delete:
    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        print(f"  ✅ Deleted: {table_name}")
        deleted += 1
    except Exception as e:
        print(f"  ❌ Error deleting {table_name}: {e}")

conn.commit()

# Check tables after
print("\nAFTER:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
after_tables = [t[0] for t in cursor.fetchall()]
print(f"  Total tables: {len(after_tables)}")

# Show remaining tables
print("\nRemaining tables:")
for table in after_tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  - {table}: {count} rows")

# Vacuum to reclaim space
print(f"\n{'=' * 80}")
print("OPTIMIZING DATABASE...")
print("=" * 80)

before_size = db_path.stat().st_size / 1024  # KB

conn.execute("VACUUM")
conn.commit()

after_size = db_path.stat().st_size / 1024  # KB
saved = before_size - after_size

print(f"  Before: {before_size:.2f} KB")
print(f"  After:  {after_size:.2f} KB")
print(f"  Saved:  {saved:.2f} KB")

conn.close()

print(f"\n{'=' * 80}")
print(f"✅ SUCCESS! Deleted {deleted} unused tables")
print("=" * 80)
print("\nSummary:")
print(f"  - Deleted {deleted} tables")
print(f"  - Remaining: {len(after_tables)} tables")
print(f"  - Space saved: {saved:.2f} KB")
print("\nNext step: Create Supabase migration to sync this change")
