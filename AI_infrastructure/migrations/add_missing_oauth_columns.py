"""
Migration: Add missing columns to oauth_tokens table on Render

PROBLEM: Render has old oauth_tokens schema missing columns:
- scope, profile_picture_url, profile_data (and potentially others)

SOLUTION: Add all missing columns with ALTER TABLE
"""

import sqlite3
import os
from pathlib import Path


def add_missing_oauth_columns():
    """Add missing columns to oauth_tokens table if they don't exist"""
    
    # Get database path (Render uses /data, local uses project/data)
    if os.getenv('RENDER') == 'true':
        db_path = '/data/ai_infrastructure.db'
    else:
        root_dir = Path(__file__).parent.parent.parent
        db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    print(f'🔷 [MIGRATION] Checking oauth_tokens schema at: {db_path}')
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute('PRAGMA table_info(oauth_tokens)')
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    print(f'   Existing columns ({len(existing_columns)}): {", ".join(sorted(existing_columns))}')
    
    # Define all required columns with their types and defaults
    required_columns = {
        'scope': 'TEXT',
        'profile_picture_url': 'TEXT',
        'profile_data': 'TEXT',
        'issued_at': 'TIMESTAMP',
        'revoked_at': 'TIMESTAMP',
        'ip_address_granted': 'TEXT',
        'account_identifier': 'TEXT',
        'account_name': 'TEXT',
        'is_primary_account': 'BOOLEAN DEFAULT 0',
        'refresh_attempts': 'INTEGER DEFAULT 0',
        'last_refresh_error': 'TEXT',
        'auto_refresh_enabled': 'BOOLEAN DEFAULT 1',
        'granted_scopes': 'TEXT',
        'email': 'TEXT',
        'profile_name': 'TEXT',
        'error_count': 'INTEGER DEFAULT 0',
        'last_error': 'TEXT'
    }
    
    # Add missing columns
    added_count = 0
    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            try:
                print(f'   Adding column: {column_name} {column_type}')
                cursor.execute(f'ALTER TABLE oauth_tokens ADD COLUMN {column_name} {column_type}')
                conn.commit()
                added_count += 1
                print(f'   ✅ Added: {column_name}')
            except sqlite3.OperationalError as e:
                if 'duplicate column name' in str(e).lower():
                    print(f'   ⚠️  Column {column_name} already exists (race condition)')
                else:
                    print(f'   ❌ Failed to add {column_name}: {e}')
                    raise
    
    conn.close()
    
    if added_count > 0:
        print(f'✅ [MIGRATION] Added {added_count} missing columns to oauth_tokens')
    else:
        print(f'✅ [MIGRATION] oauth_tokens schema is up to date (no columns added)')
    
    return added_count


if __name__ == '__main__':
    add_missing_oauth_columns()
