"""
Cleanup Legacy Threads Table

Deletes the saved_threads table (old system, no longer used)
Keeps the threads table (current system)
"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'data' / 'sessions.db'

print('='*80)
print('CLEANUP LEGACY THREADS TABLE')
print('='*80)

# Backup first
print('\n[1] Creating backup...')
import shutil
backup_path = db_path.parent / f'sessions_backup_{Path(__file__).stem}.db'
shutil.copy2(db_path, backup_path)
print(f'✅ Backup created: {backup_path}')

# Connect to database
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check if table exists and has data
print('\n[2] Checking saved_threads table...')
cursor.execute("SELECT COUNT(*) as count FROM saved_threads")
count = cursor.fetchone()[0]
print(f'   saved_threads contains: {count} records')

if count > 0:
    print(f'\n   ⚠️  WARNING: Table has {count} records!')
    print(f'   If you proceed, these will be lost.')
    print(f'   (But they are already replaced by threads table)')
else:
    print(f'   ✅ Table is empty (safe to delete)')

# Delete the table
print('\n[3] Deleting saved_threads table...')
try:
    cursor.execute("DROP TABLE IF EXISTS saved_threads")
    conn.commit()
    print('✅ saved_threads table deleted successfully')
except Exception as e:
    print(f'❌ ERROR: {e}')
    conn.rollback()
    conn.close()
    exit(1)

# Verify deletion
print('\n[4] Verifying deletion...')
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='saved_threads'
""")

if cursor.fetchone():
    print('❌ ERROR: Table still exists!')
else:
    print('✅ Table successfully deleted')

# Show remaining tables
print('\n[5] Remaining tables:')
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f'   ✅ {table[0]}: {count} records')

conn.close()

print('\n' + '='*80)
print('CLEANUP COMPLETE')
print('='*80)
print('\n✅ saved_threads table deleted')
print(f'✅ Backup saved: {backup_path.name}')
print('\n📋 Current system uses:')
print('   - threads table (main thread storage)')
print('   - messages table (message storage)')
print('   - users.metadata JSON (thread assignments)')
