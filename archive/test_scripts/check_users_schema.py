"""Check users table schema in ai_infrastructure.db"""

import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print("=" * 80)
print("USERS TABLE SCHEMA - AI_INFRASTRUCTURE.DB")
print("=" * 80)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Get table schema
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()

print(f"\n📊 Found {len(columns)} columns:\n")

# Display columns with formatting
print(f"{'Column Name':<30} {'Type':<15} {'Nullable':<10} {'Default':<20}")
print("-" * 80)

for col in columns:
    col_id, name, type_, not_null, default, pk = col
    nullable = "NO" if not_null else "YES"
    default_val = default if default else "(none)"
    
    # Highlight parent-child columns
    if name in ['parent_user_id', 'is_sub_user', 'permissions', 'allowed_tools', 
                'allowed_agents', 'data_access_scope', 'usage_limit_daily',
                'access_start_time', 'access_end_time', 'account_expires_at']:
        print(f"✅ {name:<28} {type_:<15} {nullable:<10} {default_val:<20}")
    else:
        print(f"   {name:<28} {type_:<15} {nullable:<10} {default_val:<20}")

# Check for parent-child specific columns
print("\n" + "=" * 80)
print("PARENT-CHILD USER HIERARCHY STATUS")
print("=" * 80)

parent_child_columns = [
    'parent_user_id',
    'is_sub_user',
    'permissions',
    'allowed_tools',
    'allowed_agents',
    'data_access_scope',
    'usage_limit_daily',
    'access_start_time',
    'access_end_time',
    'account_expires_at'
]

column_names = [col[1] for col in columns]
missing = []
present = []

for col in parent_child_columns:
    if col in column_names:
        present.append(col)
    else:
        missing.append(col)

if present:
    print(f"\n✅ PRESENT ({len(present)} columns):")
    for col in present:
        print(f"   - {col}")

if missing:
    print(f"\n❌ MISSING ({len(missing)} columns):")
    for col in missing:
        print(f"   - {col}")
else:
    print("\n🎉 ALL parent-child hierarchy columns are present!")

# Check if any users exist
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

print(f"\n📊 Total users in database: {user_count}")

if user_count > 0:
    cursor.execute("SELECT id, username, email, role FROM users LIMIT 5")
    print("\n👥 Sample users:")
    for row in cursor.fetchall():
        print(f"   - ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Role: {row[3]}")

conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
