"""
Database Migration Script - Add Thread Features
Purpose: Add columns for tags, synergy integration, and branching support
Date: November 7, 2025
"""

import sqlite3
import os
from pathlib import Path

# Database path
ROOT_DIR = Path(__file__).parent.parent.parent
DB_PATH = ROOT_DIR / 'data' / 'sessions.db'

def run_migration():
    """Run database migration to add new thread features"""
    
    print(f"Database path: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        print("\nStarting migration...")
        
        # Check if saved_threads table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='saved_threads'
        """)
        if not cursor.fetchone():
            print("saved_threads table not found!")
            conn.close()
            return False
        
        # Get current schema
        cursor.execute("PRAGMA table_info(saved_threads)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"\nCurrent columns: {columns}")
        
        # Add new columns
        new_columns = {
            'tags': "TEXT DEFAULT '[]'",
            'synergy_card_id': "TEXT DEFAULT NULL",
            'parent_thread_id': "TEXT DEFAULT NULL",
            'branch_point_message_id': "TEXT DEFAULT NULL",
            'branch_name': "TEXT DEFAULT NULL",
            'summary': "TEXT DEFAULT NULL",
            'summary_generated_at': "TEXT DEFAULT NULL"
        }
        
        added_count = 0
        for col_name, col_def in new_columns.items():
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE saved_threads ADD COLUMN {col_name} {col_def}")
                    print(f"  Added column: {col_name}")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    print(f"  Column {col_name} already exists or error: {e}")
            else:
                print(f"  Column {col_name} already exists")
        
        # Create indexes
        indexes = [
            ('idx_saved_threads_user_id', 'user_id'),
            ('idx_saved_threads_location', 'location'),
            ('idx_saved_threads_saved_at', 'saved_at'),
            ('idx_saved_threads_synergy_card', 'synergy_card_id'),
            ('idx_saved_threads_parent', 'parent_thread_id')
        ]
        
        print("\nCreating indexes...")
        for idx_name, col_name in indexes:
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} 
                    ON saved_threads({col_name})
                """)
                print(f"  Created index: {idx_name}")
            except sqlite3.OperationalError as e:
                print(f"  Index {idx_name} error: {e}")
        
        conn.commit()
        
        # Verify changes
        cursor.execute("PRAGMA table_info(saved_threads)")
        new_columns_list = [row[1] for row in cursor.fetchall()]
        print(f"\nFinal columns: {new_columns_list}")
        
        # Get indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='saved_threads'
        """)
        indexes_list = [row[0] for row in cursor.fetchall()]
        print(f"Indexes: {indexes_list}")
        
        conn.close()
        
        print(f"\nMigration completed successfully!")
        print(f"  Columns added: {added_count}")
        print(f"  Total columns: {len(new_columns_list)}")
        
        return True
        
    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Thread Features Migration")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n SUCCESS - Migration completed")
    else:
        print("\n FAILED - Migration failed")
