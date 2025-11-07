"""
Run Migration 001: Create thread_assignments table

This migration creates the missing thread_assignments table in ai_infrastructure.db.
Without this table, thread assignments are lost on browser refresh.

Usage:
    python run_migration_001.py
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Get database path
root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'
migration_file = root_dir / 'AI_infrastructure' / 'migrations' / '001_create_thread_assignments.sql'

print('='*60)
print('MIGRATION 001: Create thread_assignments table')
print('='*60)
print(f'Database: {db_path}')
print(f'Migration: {migration_file}')
print(f'Time: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('='*60)

# Check if database exists
if not db_path.exists():
    print(f'\n❌ ERROR: Database not found at {db_path}')
    print('   Please create the database first.')
    exit(1)

# Check if migration file exists
if not migration_file.exists():
    print(f'\n❌ ERROR: Migration file not found at {migration_file}')
    exit(1)

# Read migration SQL
print('\n📄 Reading migration file...')
with open(migration_file, 'r', encoding='utf-8') as f:
    migration_sql = f.read()

# Connect to database
print('🔌 Connecting to database...')
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check if table already exists
print('🔍 Checking if thread_assignments table exists...')
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='thread_assignments'
""")
existing = cursor.fetchone()

if existing:
    print('⚠️  Table already exists. Skipping creation.')
    print('   If you want to recreate the table, manually drop it first:')
    print('   DROP TABLE thread_assignments;')
else:
    print('✅ Table does not exist. Creating...')
    
    # Execute migration
    try:
        # Execute the entire SQL script at once (SQLite supports multiple statements)
        print('   Executing migration SQL...')
        cursor.executescript(migration_sql)
        
        conn.commit()
        print('\n✅ Migration completed successfully!')
        
    except Exception as e:
        print(f'\n❌ ERROR: Migration failed: {e}')
        conn.rollback()
        conn.close()
        exit(1)

# Verify table creation
print('\n🔍 Verifying table creation...')
cursor.execute("PRAGMA table_info(thread_assignments)")
columns = cursor.fetchall()

if columns:
    print(f'✅ Table created with {len(columns)} columns:')
    for col in columns:
        print(f'   - {col["name"]} ({col["type"]}) {"NOT NULL" if col["notnull"] else ""} {"PRIMARY KEY" if col["pk"] else ""}')
else:
    print('❌ ERROR: Table not found after creation')
    conn.close()
    exit(1)

# Check indexes
print('\n🔍 Verifying indexes...')
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='index' AND tbl_name='thread_assignments'
""")
indexes = cursor.fetchall()

if indexes:
    print(f'✅ Created {len(indexes)} indexes:')
    for idx in indexes:
        print(f'   - {idx["name"]}')
else:
    print('⚠️  No indexes found (this may be normal if using IF NOT EXISTS)')

# Check triggers
print('\n🔍 Verifying triggers...')
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='trigger' AND tbl_name='thread_assignments'
""")
triggers = cursor.fetchall()

if triggers:
    print(f'✅ Created {len(triggers)} triggers:')
    for trigger in triggers:
        print(f'   - {trigger["name"]}')
else:
    print('⚠️  No triggers found')

# Count existing records
cursor.execute("SELECT COUNT(*) as count FROM thread_assignments")
count = cursor.fetchone()['count']
print(f'\n📊 Current records in thread_assignments: {count}')

# Close connection
conn.close()

print('\n' + '='*60)
print('MIGRATION COMPLETE!')
print('='*60)
print('\n✅ Next steps:')
print('   1. Restart Flask backend: BISTART')
print('   2. Test thread creation and assignment')
print('   3. Refresh browser and verify thread persists')
print('   4. Check Synergy card shows thread ID and agent')
print('\n📝 To verify in database:')
print('   sqlite3 data/ai_infrastructure.db')
print('   SELECT * FROM thread_assignments;')
