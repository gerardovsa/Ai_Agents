"""
Migration 013: Drop thread_assignments table (not needed)
Reason: sessions.threads already has email_thread_id, email_subject, email_participants columns
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.database_utils import get_database_connection

def run_migration():
    """Drop the redundant thread_assignments table."""
    
    # Read SQL file
    sql_file = os.path.join(os.path.dirname(__file__), '013_drop_thread_assignments_table.sql')
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Execute migration
    conn = None
    try:
        conn = get_database_connection()
        cursor = conn.cursor()
        
        print("[Migration 013] Dropping thread_assignments table...")
        cursor.execute(sql)
        conn.commit()
        
        print("✅ Migration 013 completed successfully")
        
        cursor.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"❌ Migration 013 failed: {e}")
        raise
        
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    run_migration()
