"""
Verify Complete Database Schema
Checks all tables have all required columns
"""

import sqlite3

DB_PATH = 'data/sessions.db'

# Expected schemas
EXPECTED_SCHEMAS = {
    'threads': [
        'id', 'thread_slug', 'user_id', 'title', 'created_at', 'updated_at',
        'archived', 'tags', 'synergy_card_id', 'metadata', 'workspace_id',
        'name', 'location', 'parent_thread_id', 'branch_point_message_id', 'branch_name'
    ],
    'messages': [
        'id', 'thread_id', 'role', 'content', 'timestamp', 'response_time'
    ],
    'thread_assignments': [
        'id', 'user_id', 'thread_slug', 'location', 'assigned_at', 'updated_at', 'metadata'
    ],
    'users': [
        'id', 'email', 'name', 'created_at', 'username', 'last_active', 'metadata'
    ]
}

print('='*70)
print('DATABASE SCHEMA VERIFICATION')
print('='*70)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

all_valid = True

for table_name, expected_columns in EXPECTED_SCHEMAS.items():
    print(f'\n📋 Checking table: {table_name}')
    print('-'*70)
    
    # Get actual columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    actual_columns = [col[1] for col in cursor.fetchall()]
    
    # Check for missing columns
    missing = [col for col in expected_columns if col not in actual_columns]
    extra = [col for col in actual_columns if col not in expected_columns]
    
    if missing:
        print(f'❌ MISSING: {missing}')
        all_valid = False
    else:
        print(f'✅ All required columns present ({len(actual_columns)} columns)')
    
    if extra:
        print(f'ℹ️  Extra columns (not required but OK): {extra}')
    
    # Show all columns
    print(f'   Columns: {", ".join(actual_columns)}')

conn.close()

print('\n' + '='*70)
if all_valid:
    print('✅ DATABASE SCHEMA: COMPLETE')
    print('✅ All tables have all required columns')
    print('✅ Ready for production use')
else:
    print('❌ DATABASE SCHEMA: INCOMPLETE')
    print('❌ Some required columns are missing')
    print('❌ Run the fix scripts to complete the schema')
print('='*70)
