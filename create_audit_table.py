"""
Create credential_audit_log table in Supabase

Run this script to create the audit logging table in Supabase PostgreSQL.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def create_audit_log_table():
    """Create credential_audit_log table in Supabase"""
    
    print("=" * 70)
    print("CREATING CREDENTIAL AUDIT LOG TABLE IN SUPABASE")
    print("=" * 70)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    try:
        # Drop table if exists (for clean testing)
        print("\n[1/3] Dropping existing table (if exists)...")
        cursor.execute("""
            DROP TABLE IF EXISTS ai_infrastructure.credential_audit_log CASCADE;
        """)
        print("     SUCCESS - Old table dropped (if existed)")
        
        # Create table with PostgreSQL syntax
        print("\n[2/3] Creating credential_audit_log table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_infrastructure.credential_audit_log (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                platform VARCHAR(50) NOT NULL,
                tool_name VARCHAR(100),
                access_type VARCHAR(20) DEFAULT 'read',
                query_executed TEXT,
                ip_address VARCHAR(45),
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("     SUCCESS - Table created")
        
        # Create indexes
        print("\n[3/3] Creating indexes for performance...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_user_id 
            ON ai_infrastructure.credential_audit_log(user_id);
        """)
        print("     SUCCESS - Index on user_id")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_platform 
            ON ai_infrastructure.credential_audit_log(platform);
        """)
        print("     SUCCESS - Index on platform")
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_created_at 
            ON ai_infrastructure.credential_audit_log(created_at DESC);
        """)
        print("     SUCCESS - Index on created_at")
        
        # Commit all changes
        conn.commit()
        
        # Verify table exists
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'ai_infrastructure' 
            AND table_name = 'credential_audit_log'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("\n" + "=" * 70)
        print("TABLE CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nTable: ai_infrastructure.credential_audit_log")
        print(f"Columns: {len(columns)}")
        print("\nSchema:")
        for col_name, data_type in columns:
            print(f"  - {col_name:20} {data_type}")
        
        print("\nIndexes:")
        print("  - idx_audit_user_id (user_id)")
        print("  - idx_audit_platform (platform)")
        print("  - idx_audit_created_at (created_at DESC)")
        
        print("\n✅ Ready for audit logging!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()
    
    return True

if __name__ == '__main__':
    try:
        success = create_audit_log_table()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
