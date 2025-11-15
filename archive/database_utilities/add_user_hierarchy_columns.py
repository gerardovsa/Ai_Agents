"""
Add parent-child user hierarchy columns to users table

This migration adds the following columns:
1. parent_user_id - Links sub-users to their parent
2. is_sub_user - Boolean flag for sub-users
3. permissions - JSON for granular permissions
4. allowed_tools - JSON list of allowed tool names
5. allowed_agents - JSON list of allowed agent IDs
6. data_access_scope - Scope of data access (own/team/all)
7. usage_limit_daily - Daily API call limit
8. access_start_time - Work hours start (HH:MM)
9. access_end_time - Work hours end (HH:MM)
10. account_expires_at - Account expiry timestamp
"""

import sqlite3
from pathlib import Path
from datetime import datetime

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print("=" * 80)
print("ADDING USER HIERARCHY COLUMNS TO ai_infrastructure.db")
print("=" * 80)
print(f"\nDatabase: {db_path}")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Backup first
backup_path = root_dir / 'data' / f'ai_infrastructure_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
print(f"📦 Creating backup: {backup_path.name}")
import shutil
shutil.copy2(db_path, backup_path)
print("✅ Backup created\n")

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Columns to add with their types and defaults
columns_to_add = [
    ('parent_user_id', 'INTEGER', None, 'Links to parent user (NULL = root user)'),
    ('is_sub_user', 'BOOLEAN DEFAULT 0', None, 'Whether this is a sub-user'),
    ('permissions', 'TEXT', None, 'JSON: Granular tool/agent/data permissions'),
    ('allowed_tools', 'TEXT', None, 'JSON: List of allowed tool names (NULL = all)'),
    ('allowed_agents', 'TEXT', None, 'JSON: List of allowed agent IDs (NULL = all)'),
    ('data_access_scope', "TEXT DEFAULT 'own'", 'own', 'Scope: own/team/department/all'),
    ('usage_limit_daily', 'INTEGER DEFAULT 1000', '1000', 'Max API calls per day'),
    ('access_start_time', 'TEXT', None, 'Work hours start (HH:MM format)'),
    ('access_end_time', 'TEXT', None, 'Work hours end (HH:MM format)'),
    ('account_expires_at', 'TIMESTAMP', None, 'Account expiry date')
]

print("📝 Adding columns:")
print("-" * 80)

added_count = 0
skipped_count = 0

for col_name, col_type, default_val, description in columns_to_add:
    try:
        # Try to add the column
        cursor.execute(f'ALTER TABLE users ADD COLUMN {col_name} {col_type}')
        conn.commit()
        
        status = "✅ ADDED"
        added_count += 1
        
        # Show default value if any
        default_display = f" (default: {default_val})" if default_val else ""
        print(f"{status:15} {col_name:25} - {description}{default_display}")
        
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e).lower():
            status = "⚠️  EXISTS"
            skipped_count += 1
            print(f"{status:15} {col_name:25} - {description}")
        else:
            print(f"❌ ERROR: {col_name} - {e}")
            raise

print("\n" + "=" * 80)
print("MIGRATION SUMMARY")
print("=" * 80)
print(f"\n✅ Columns added:   {added_count}")
print(f"⚠️  Already existed: {skipped_count}")
print(f"📊 Total columns:   {added_count + skipped_count}")

# Verify final schema
cursor.execute("PRAGMA table_info(users)")
all_columns = cursor.fetchall()
print(f"\n📋 Final users table has {len(all_columns)} columns total")

# Check for our new columns
new_column_names = [col[0] for col in columns_to_add]
existing_column_names = [col[1] for col in all_columns]

print("\n🔍 Verification:")
all_present = True
for col_name in new_column_names:
    if col_name in existing_column_names:
        print(f"   ✅ {col_name}")
    else:
        print(f"   ❌ {col_name} - MISSING!")
        all_present = False

if all_present:
    print("\n🎉 SUCCESS! All parent-child hierarchy columns are now present!")
else:
    print("\n⚠️  WARNING: Some columns are missing. Migration may have failed.")

# Set safe defaults for existing users
print("\n" + "=" * 80)
print("SETTING DEFAULTS FOR EXISTING USERS")
print("=" * 80)

cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]

if user_count > 0:
    print(f"\n📊 Updating {user_count} existing users with safe defaults...")
    
    # Set safe defaults (NULL for lists = all allowed)
    cursor.execute("""
        UPDATE users SET
            is_sub_user = 0,
            data_access_scope = 'own',
            usage_limit_daily = 1000
        WHERE is_sub_user IS NULL
    """)
    
    conn.commit()
    print("✅ Defaults applied")
    print("\n   Safe defaults:")
    print("   - is_sub_user = 0 (not a sub-user)")
    print("   - allowed_tools = NULL (all tools allowed)")
    print("   - allowed_agents = NULL (all agents allowed)")
    print("   - data_access_scope = 'own'")
    print("   - usage_limit_daily = 1000")
else:
    print("\n📊 No existing users - defaults will apply to new users")

conn.close()

print("\n" + "=" * 80)
print("MIGRATION COMPLETE!")
print("=" * 80)
print(f"\n✅ Backup saved: {backup_path.name}")
print(f"✅ Database updated: {db_path.name}")
print("\n💡 Next steps:")
print("   1. Restart Flask server to use new schema")
print("   2. Test user creation with new columns")
print("   3. Implement permission checker middleware")
print("   4. Create sub-user management API endpoints")
