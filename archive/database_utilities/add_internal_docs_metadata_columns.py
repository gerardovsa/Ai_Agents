"""
Add metadata columns to synergy_internal_docs table

Adds:
- slug (TEXT UNIQUE) - URL-friendly identifier for sharing
- share_url (TEXT) - Full share URL
- description (TEXT) - Document description
- tags (TEXT) - Comma-separated tags
"""

import sqlite3
from pathlib import Path

def add_metadata_columns():
    db_path = Path(__file__).parent / 'data' / 'synergy_sessions.db'
    
    if not db_path.exists():
        print(f'Database not found: {db_path}')
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print('Current table schema:')
    cursor.execute('PRAGMA table_info(synergy_internal_docs)')
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    for col, type_ in columns.items():
        print(f'  {col}: {type_}')
    
    # Add missing columns
    columns_to_add = [
        ('slug', 'TEXT'),
        ('share_url', 'TEXT'),
        ('description', 'TEXT'),
        ('tags', 'TEXT')
    ]
    
    print('\nAdding missing columns...')
    for col_name, col_type in columns_to_add:
        if col_name not in columns:
            try:
                if col_name == 'slug':
                    # slug should be UNIQUE for sharing
                    cursor.execute(f'ALTER TABLE synergy_internal_docs ADD COLUMN {col_name} {col_type} UNIQUE')
                else:
                    cursor.execute(f'ALTER TABLE synergy_internal_docs ADD COLUMN {col_name} {col_type}')
                print(f'  Added: {col_name} ({col_type})')
            except Exception as e:
                print(f'  Failed to add {col_name}: {e}')
        else:
            print(f'  Skipped: {col_name} (already exists)')
    
    conn.commit()
    
    # Show updated schema
    print('\nUpdated table schema:')
    cursor.execute('PRAGMA table_info(synergy_internal_docs)')
    for row in cursor.fetchall():
        print(f'  {row[1]}: {row[2]}')
    
    conn.close()
    print('\nMigration complete!')

if __name__ == '__main__':
    add_metadata_columns()
