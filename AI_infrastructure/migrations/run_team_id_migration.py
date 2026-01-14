"""
Run Team ID Management Database Migration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from shared.database_utils import get_database_connection

def run_migration():
    """Execute Team ID management migration"""
    print("\n" + "="*60)
    print("🚀 Running Team ID Management Migration")
    print("="*60 + "\n")
    
    migration_file = os.path.join(os.path.dirname(__file__), 'team_id_management_migration.sql')
    
    if not os.path.exists(migration_file):
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    # Read SQL file
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Execute migration
        print("📝 Executing migration SQL...")
        cursor.execute(sql)
        conn.commit()
        
        # Verify columns were added
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns
            WHERE table_schema = 'sessions' 
                AND table_name = 'messages'
                AND column_name IN ('sender_team_id', 'recipient_team_id', 'message_type')
        """)
        
        columns = []
        for row in cursor.fetchall():
            if isinstance(row, dict):
                columns.append(row['column_name'])
            else:
                columns.append(row[0] if len(row) > 0 else str(row))
        
        print("\n✅ Migration completed successfully!")
        print(f"\nAdded columns to sessions.messages table: {', '.join(columns) if columns else 'None (may already exist)'}")
        
        # Verify indexes
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes
            WHERE schemaname = 'sessions'
                AND tablename = 'messages'
                AND indexname LIKE '%team_id%'
        """)
        
        indexes = []
        for row in cursor.fetchall():
            if isinstance(row, dict):
                indexes.append(row['indexname'])
            else:
                indexes.append(row[0] if len(row) > 0 else str(row))
        
        print(f"Created indexes: {', '.join(indexes) if indexes else 'None (may already exist)'}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ TEAM ID MIGRATION COMPLETE")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
