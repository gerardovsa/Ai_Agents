"""
Database Migration Script - Add Thread Features to 'threads' table
Purpose: Add columns for tags, synergy integration, and branching support
Date: November 7, 2025
"""

import sqlite3
import os
from pathlib import Path

# Database path
ROOT_DIR = Path(__file__).parent
DB_PATH = ROOT_DIR / 'data' / 'sessions.db'

def run_migration():
    """Run database migration to add new thread features"""
    
    print(f"Database path: {DB_PATH}")
    
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return False
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        print("\n🔷 Starting migration...")
        
        # Check if threads table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='threads'
        """)
        if not cursor.fetchone():
            print("❌ 'threads' table not found!")
            conn.close()
            return False
        
        # Get current schema
        cursor.execute("PRAGMA table_info(threads)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"\n📋 Current columns: {len(columns)} total")
        
        # Add new columns
        new_columns = {
            'tags': "TEXT DEFAULT '[]'",
            'synergy_card_id': "TEXT DEFAULT NULL",
            'parent_thread_id': "TEXT DEFAULT NULL",
            'branch_point_message_id': "TEXT DEFAULT NULL",
            'branch_name': "TEXT DEFAULT NULL",
            'summary': "TEXT DEFAULT NULL",
            'summary_generated_at': "TEXT DEFAULT NULL",
            'location': "TEXT DEFAULT 'prime'"
        }
        
        added_count = 0
        print("\n🔧 Adding columns:")
        for col_name, col_def in new_columns.items():
            if col_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE threads ADD COLUMN {col_name} {col_def}")
                    print(f"  ✅ Added column: {col_name}")
                    added_count += 1
                except sqlite3.OperationalError as e:
                    if 'duplicate column name' in str(e).lower():
                        print(f"  ⚠️  Column {col_name} already exists")
                    else:
                        print(f"  ❌ Error adding {col_name}: {e}")
            else:
                print(f"  ℹ️  Column {col_name} already exists")
        
        # Create indexes
        indexes = [
            ('idx_threads_user_id', 'user_id'),
            ('idx_threads_location', 'location'),
            ('idx_threads_created_at', 'created_at'),
            ('idx_threads_synergy_card', 'synergy_card_id'),
            ('idx_threads_parent', 'parent_thread_id'),
            ('idx_threads_thread_slug', 'thread_slug')
        ]
        
        print("\n📊 Creating indexes:")
        index_count = 0
        for idx_name, col_name in indexes:
            try:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} 
                    ON threads({col_name})
                """)
                print(f"  ✅ Created index: {idx_name}")
                index_count += 1
            except sqlite3.OperationalError as e:
                print(f"  ⚠️  Index {idx_name}: {e}")
        
        conn.commit()
        
        # Verify changes
        cursor.execute("PRAGMA table_info(threads)")
        new_columns_list = [row[1] for row in cursor.fetchall()]
        
        # Get indexes
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND tbl_name='threads'
        """)
        indexes_list = [row[0] for row in cursor.fetchall()]
        
        print("\n" + "=" * 60)
        print("📊 MIGRATION SUMMARY")
        print("=" * 60)
        print(f"Columns added: {added_count}")
        print(f"Total columns now: {len(new_columns_list)}")
        print(f"Indexes created: {index_count}")
        print(f"Total indexes: {len(indexes_list)}")
        
        print("\n✅ Final column list:")
        for col in new_columns_list:
            marker = "🆕" if col in new_columns else "  "
            print(f"{marker} {col}")
        
        conn.close()
        
        print(f"\n🎉 Migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🔷 Thread Features Migration")
    print("=" * 60)
    
    success = run_migration()
    
    if success:
        print("\n✅ SUCCESS - Migration completed")
    else:
        print("\n❌ FAILED - Migration failed")
