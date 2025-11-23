"""
Add missing columns to synergy_sessions table
NO MIGRATION - just add columns
"""
import sqlite3
from pathlib import Path
from shared.database_utils import convert_sql_placeholders

root_dir = Path(__file__).parent
db_path = root_dir / 'data' / 'synergy_sessions.db'

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Check current columns
cursor.execute('PRAGMA table_info(synergy_sessions)')
current_columns = [col[1] for col in cursor.fetchall()]

print(f"Current columns in synergy_sessions: {len(current_columns)}")
print(f"  {', '.join(current_columns)}")

# Columns to add
new_columns = [
    ('shared_with_users', 'TEXT', '[]'),  # JSON array of user IDs
    ('owner_user_id', 'INTEGER', '1'),     # Owner user ID (default to 1)
    ('project_name', 'TEXT', 'NULL')       # Project name
]

print(f"\n=== ADDING COLUMNS ===")

for col_name, col_type, default_value in new_columns:
    if col_name not in current_columns:
        try:
            # SQLite doesn't support DEFAULT with ALTER TABLE for TEXT with functions
            # So we add the column, then update all rows
            cursor.execute(f'ALTER TABLE synergy_sessions ADD COLUMN {col_name} {col_type}')
            
            # Set default values
            if default_value != 'NULL':
                cursor.execute(f"UPDATE synergy_sessions SET {col_name} = ?", (default_value,))
            
            conn.commit()
            print(f"  Added: {col_name} ({col_type}) with default: {default_value}")
        except Exception as e:
            print(f"  ERROR adding {col_name}: {e}")
    else:
        print(f"  SKIP: {col_name} already exists")

# Verify
cursor.execute('PRAGMA table_info(synergy_sessions)')
final_columns = cursor.fetchall()

print(f"\n=== FINAL SCHEMA ===")
print(f"Total columns: {len(final_columns)}")
for col in final_columns:
    print(f"  {col[1]:30} {col[2]:10} {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")

conn.close()
print(f"\nDONE - Columns added successfully")
