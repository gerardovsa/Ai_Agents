"""
CRITICAL MIGRATION: Add missing OAuth columns to users table
Fixes "no such column: has_microsoft_oauth" error on Render
"""

import sqlite3
from pathlib import Path

def run_migration():
    """Add missing OAuth-related columns to users table"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'ai_infrastructure.db'
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print(f"[MIGRATION] Running users OAuth columns migration on {db_path}")
    
    # Get current users table schema
    cursor.execute("PRAGMA table_info(users)")
    existing_cols = {col[1] for col in cursor.fetchall()}
    
    print(f"[MIGRATION] users table currently has {len(existing_cols)} columns")
    
    # Required columns for OAuth functionality
    required_columns = {
        'has_google_oauth': 'INTEGER DEFAULT 0',  # Boolean 0/1
        'has_microsoft_oauth': 'INTEGER DEFAULT 0',  # Boolean 0/1
        'is_active': 'INTEGER DEFAULT 1',  # Boolean 0/1
    }
    
    added_count = 0
    
    for col_name, col_def in required_columns.items():
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_def}")
                print(f"✅ [MIGRATION] Added users.{col_name} ({col_def})")
                added_count += 1
            except Exception as e:
                print(f"❌ [MIGRATION] Failed to add users.{col_name}: {e}")
        else:
            print(f"⏭️  [MIGRATION] users.{col_name} already exists")
    
    conn.commit()
    conn.close()
    
    if added_count > 0:
        print(f"✅ [MIGRATION] Added {added_count} missing columns to users table")
    else:
        print(f"✅ [MIGRATION] All required columns already exist")
    
    return added_count

if __name__ == '__main__':
    count = run_migration()
    print(f"\n[MIGRATION COMPLETE] Modified {count} columns")
