"""
Add All Missing Database Columns
Comprehensive fix for threads and thread_assignments tables
"""

import sqlite3

DB_PATH = 'data/sessions.db'

print('[INIT] Adding all missing columns...')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get current threads columns
cursor.execute("PRAGMA table_info(threads)")
threads_columns = [col[1] for col in cursor.fetchall()]
print(f'[INFO] Current threads columns: {threads_columns}')

# Add missing columns to threads table
missing_threads_columns = {
    'name': 'ALTER TABLE threads ADD COLUMN name TEXT',
    'location': 'ALTER TABLE threads ADD COLUMN location TEXT',
    'parent_thread_id': 'ALTER TABLE threads ADD COLUMN parent_thread_id TEXT',
    'branch_point_message_id': 'ALTER TABLE threads ADD COLUMN branch_point_message_id TEXT',
    'branch_name': 'ALTER TABLE threads ADD COLUMN branch_name TEXT'
}

for col_name, sql in missing_threads_columns.items():
    if col_name not in threads_columns:
        print(f'[FIX] Adding {col_name} column to threads...')
        cursor.execute(sql)
        print(f'[OK] Added {col_name}')
    else:
        print(f'[SKIP] {col_name} already exists')

# If 'name' was just added, copy data from 'title' to 'name'
if 'name' not in threads_columns and 'title' in threads_columns:
    print('[FIX] Copying title data to name column...')
    cursor.execute('UPDATE threads SET name = title WHERE name IS NULL')
    print('[OK] Copied title to name')

conn.commit()

# Verify all columns
cursor.execute("PRAGMA table_info(threads)")
all_columns = [col[1] for col in cursor.fetchall()]
print(f'\n[VERIFY] All threads columns: {all_columns}')

# Check if all required columns exist
required = ['thread_slug', 'workspace_id', 'name', 'user_id', 'created_at', 
            'updated_at', 'metadata', 'location', 'tags', 'synergy_card_id',
            'parent_thread_id', 'branch_point_message_id', 'branch_name']
missing = [col for col in required if col not in all_columns]

if missing:
    print(f'\n[WARNING] Still missing: {missing}')
else:
    print('\n[SUCCESS] All required columns present!')

conn.close()

print('\n[INFO] Database schema updated')
print('[INFO] Restart Flask if running: BISTART')
