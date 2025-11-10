"""
Fix Database Schema - Add Missing Columns
Adds metadata and workspace_id columns to threads and thread_assignments tables
"""

import sqlite3
from datetime import datetime

DB_PATH = 'data/sessions.db'

print('[INIT] Fixing database schema...')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check current schema
cursor.execute("PRAGMA table_info(threads)")
threads_columns = [col[1] for col in cursor.fetchall()]
print(f'[INFO] Current threads columns: {threads_columns}')

cursor.execute("PRAGMA table_info(thread_assignments)")
assignments_columns = [col[1] for col in cursor.fetchall()]
print(f'[INFO] Current thread_assignments columns: {assignments_columns}')

# Add missing columns to threads table
if 'metadata' not in threads_columns:
    print('[FIX] Adding metadata column to threads...')
    cursor.execute('ALTER TABLE threads ADD COLUMN metadata TEXT DEFAULT "{}"')
    print('[OK] Added metadata column')
else:
    print('[SKIP] metadata column already exists in threads')

if 'workspace_id' not in threads_columns:
    print('[FIX] Adding workspace_id column to threads...')
    cursor.execute('ALTER TABLE threads ADD COLUMN workspace_id TEXT')
    print('[OK] Added workspace_id column')
else:
    print('[SKIP] workspace_id column already exists in threads')

# Add missing columns to thread_assignments table
if 'metadata' not in assignments_columns:
    print('[FIX] Adding metadata column to thread_assignments...')
    cursor.execute('ALTER TABLE thread_assignments ADD COLUMN metadata TEXT DEFAULT "{}"')
    print('[OK] Added metadata column to thread_assignments')
else:
    print('[SKIP] metadata column already exists in thread_assignments')

conn.commit()

# Verify the changes
cursor.execute("PRAGMA table_info(threads)")
threads_columns = [col[1] for col in cursor.fetchall()]
print(f'\n[VERIFY] Updated threads columns: {threads_columns}')

cursor.execute("PRAGMA table_info(thread_assignments)")
assignments_columns = [col[1] for col in cursor.fetchall()]
print(f'[VERIFY] Updated thread_assignments columns: {assignments_columns}')

conn.close()

print('\n[SUCCESS] Database schema fixed!')
print('[INFO] Restart Flask to apply changes: BISTART')
