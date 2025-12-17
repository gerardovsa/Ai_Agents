#!/usr/bin/env python3
"""
Migration Runner: Add idempotency_key column and Team ID cascade trigger
Run: python AI_infrastructure/migrations/run_add_idempotency_and_cascade.py
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from AI_infrastructure.shared.database_utils import get_database_connection

def run_migration():
    """Execute migration SQL file"""
    print("\n" + "="*80)
    print("MIGRATION: Add idempotency_key and Team ID cascade trigger")
    print("="*80 + "\n")
    
    # Read SQL file
    sql_file = os.path.join(os.path.dirname(__file__), 'add_idempotency_and_cascade.sql')
    
    with open(sql_file, 'r') as f:
        migration_sql = f.read()
    
    # Execute migration
    try:
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            
            print("Running migration SQL...")
            cursor.execute(migration_sql)
            conn.commit()
            
            print("✅ Migration completed successfully!\n")
            
            # Verification: Check idempotency_key column
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type, 
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'sessions' 
                  AND table_name = 'threads' 
                  AND column_name = 'idempotency_key'
            """)
            
            column_info = cursor.fetchone()
            if column_info:
                col_name = column_info[0] if isinstance(column_info, tuple) else column_info['column_name']
                data_type = column_info[1] if isinstance(column_info, tuple) else column_info['data_type']
                is_null = column_info[2] if isinstance(column_info, tuple) else column_info['is_nullable']
                print("Verification:")
                print(f"  ✅ Column 'idempotency_key' exists: {data_type} (nullable: {is_null})")
            else:
                print("  ❌ Column 'idempotency_key' not found!")
            
            # Verification: Check unique index
            cursor.execute("""
                SELECT indexname 
                FROM pg_indexes
                WHERE tablename = 'threads' 
                  AND indexname = 'idx_threads_idempotency_key'
            """)
            
            index_info = cursor.fetchone()
            if index_info:
                print(f"  ✅ Unique index 'idx_threads_idempotency_key' exists")
            else:
                print("  ❌ Unique index not found!")
            
            # Verification: Check trigger
            cursor.execute("""
                SELECT trigger_name 
                FROM information_schema.triggers
                WHERE trigger_name = 'team_id_cascade_delete'
            """)
            
            trigger_info = cursor.fetchone()
            if trigger_info:
                print(f"  ✅ Trigger 'team_id_cascade_delete' exists")
            else:
                print("  ❌ Trigger not found!")
            
            # Verification: Check trigger function
            cursor.execute("""
                SELECT proname 
                FROM pg_proc
                WHERE proname = 'cascade_team_id_deletion'
            """)
            
            function_info = cursor.fetchone()
            if function_info:
                print(f"  ✅ Function 'cascade_team_id_deletion()' exists")
            else:
                print("  ❌ Function not found!")
            
            # Check thread statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_threads,
                    COUNT(idempotency_key) as threads_with_idempotency,
                    COUNT(team_id) as threads_with_team_id
                FROM sessions.threads
            """)
            
            stats = cursor.fetchone()
            total = stats[0] if isinstance(stats, tuple) else stats['total_threads']
            with_idemp = stats[1] if isinstance(stats, tuple) else stats['threads_with_idempotency']
            with_team = stats[2] if isinstance(stats, tuple) else stats['threads_with_team_id']
            
            print(f"\nThread Statistics:")
            print(f"  Total threads: {total}")
            print(f"  Threads with idempotency_key: {with_idemp}")
            print(f"  Threads with team_id: {with_team}")
            
            cursor.close()
    
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*80)
    print("MIGRATION COMPLETE")
    print("="*80)
    return True

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
