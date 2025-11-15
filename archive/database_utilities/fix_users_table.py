"""
Fix Users Table Schema
Add missing columns: username, last_active, metadata
"""

import sqlite3

DB_PATH = 'data/sessions.db'

print('[INIT] Fixing users table schema...')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get current columns
cursor.execute("PRAGMA table_info(users)")
users_columns = [col[1] for col in cursor.fetchall()]
print(f'[INFO] Current users columns: {users_columns}')

# Add missing columns
missing_columns = {
    'username': 'ALTER TABLE users ADD COLUMN username TEXT',
    'last_active': 'ALTER TABLE users ADD COLUMN last_active TIMESTAMP',
    'metadata': 'ALTER TABLE users ADD COLUMN metadata TEXT DEFAULT "{}"'
}

for col_name, sql in missing_columns.items():
    if col_name not in users_columns:
        print(f'[FIX] Adding {col_name} column to users...')
        cursor.execute(sql)
        print(f'[OK] Added {col_name}')
    else:
        print(f'[SKIP] {col_name} already exists')

# Set default values for existing users
if 'username' not in users_columns:
    print('[FIX] Setting default usernames for existing users...')
    cursor.execute("UPDATE users SET username = 'user_' || id WHERE username IS NULL")
    print('[OK] Default usernames set')

if 'last_active' not in users_columns:
    print('[FIX] Setting last_active for existing users...')
    cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE last_active IS NULL")
    print('[OK] last_active timestamps set')

if 'metadata' not in users_columns:
    print('[FIX] Setting default metadata for existing users...')
    cursor.execute("UPDATE users SET metadata = '{}' WHERE metadata IS NULL")
    print('[OK] Default metadata set')

conn.commit()

# Verify
cursor.execute("PRAGMA table_info(users)")
all_columns = [col[1] for col in cursor.fetchall()]
print(f'\n[VERIFY] All users columns: {all_columns}')

required = ['id', 'email', 'name', 'created_at', 'username', 'last_active', 'metadata']
missing = [col for col in required if col not in all_columns]

if missing:
    print(f'\n[WARNING] Still missing: {missing}')
else:
    print('\n[SUCCESS] All required columns present!')

conn.close()

print('\n[INFO] Users table schema updated')
print('[INFO] Restart Flask: BISTART')
