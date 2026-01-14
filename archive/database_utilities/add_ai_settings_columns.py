"""
Add AI settings columns to user_preferences table
"""
import sqlite3
from pathlib import Path

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'ai_infrastructure.db'

print(f'Database: {db_path}')

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Add AI settings columns
columns_to_add = [
    ('ai_model', 'TEXT', 'claude-sonnet-4-5-20250929'),
    ('ai_temperature', 'REAL', '1.0'),
    ('ai_top_p', 'REAL', '1.0'),
    ('ai_max_tokens', 'INTEGER', '4096'),
    ('ai_thinking_enabled', 'INTEGER', '0'),
    ('ai_thinking_budget', 'INTEGER', '10000'),
    ('ai_streaming_enabled', 'INTEGER', '1')
]

print('\nAdding columns...')
for col_name, col_type, default_val in columns_to_add:
    try:
        if col_type == 'TEXT':
            sql = f'ALTER TABLE user_preferences ADD COLUMN {col_name} {col_type} DEFAULT "{default_val}"'
        else:
            sql = f'ALTER TABLE user_preferences ADD COLUMN {col_name} {col_type} DEFAULT {default_val}'
        cursor.execute(sql)
        print(f'  ✅ Added: {col_name} ({col_type})')
    except sqlite3.OperationalError as e:
        if 'duplicate column name' in str(e):
            print(f'  ⚠️  Exists: {col_name}')
        else:
            print(f'  ❌ Error: {col_name} - {e}')

conn.commit()

# Verify
cursor.execute('PRAGMA table_info(user_preferences)')
all_cols = cursor.fetchall()
print(f'\n✅ Total columns in user_preferences: {len(all_cols)}')

print('\nAll AI settings columns:')
ai_cols = [col for col in all_cols if 'ai_' in col[1]]
for col in ai_cols:
    print(f'  - {col[1]} ({col[2]}) DEFAULT {col[4]}')

conn.close()
print('\n✅ Database schema update complete!')
