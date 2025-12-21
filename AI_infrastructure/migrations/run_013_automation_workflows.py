#!/usr/bin/env python3
"""
Migration Runner: Create automation_workflows table
"""
import sys
import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

def run_migration():
    """Run the automation_workflows table migration"""
    print("=" * 70)
    print("AUTOMATION WORKFLOWS TABLE MIGRATION")
    print("=" * 70)
    
    try:
        # Load environment variables
        root_dir = Path(__file__).parent.parent.parent
        env_file = root_dir / '.env.master'
        if env_file.exists():
            load_dotenv(env_file)
        else:
            load_dotenv()
        
        # Get database URL from environment
        db_url = os.getenv('SUPABASE_DB_URL')
        if not db_url:
            print("\n❌ Error: SUPABASE_DB_URL not found in environment")
            print("Please ensure .env.master or .env contains SUPABASE_DB_URL")
            sys.exit(1)
        
        # Connect to database
        print("\n📡 Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        cursor = conn.cursor()
        print("✅ Connected to database")
        
        # Read SQL file
        sql_file = os.path.join(os.path.dirname(__file__), '013_automation_workflows_table.sql')
        
        print("\n📝 Reading SQL migration file...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print("🔧 Executing SQL migration...")
        
        # Execute the migration
        cursor.execute(sql)
        conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("   - Created automation_workflows table")
        print("   - Created 5 indexes (user, slug, category, enabled, updated)")
        print("   - Created updated_at trigger function")
        print("   - Applied auto-update trigger")
        
        # Verify table exists
        print("\n🔍 Verifying table creation...")
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'automation_workflows'
        """)
        result = cursor.fetchone()
        
        if result and result[0] == 1:
            print("🎉 Verification: Table 'automation_workflows' exists!")
            
            # Show table structure
            cursor.execute("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'automation_workflows'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            print("\n📋 Table Structure:")
            for col in columns:
                nullable = "NULL" if col[2] == 'YES' else "NOT NULL"
                print(f"   - {col[0]}: {col[1]} ({nullable})")
        else:
            print("⚠️ Warning: Table verification failed")
        
        cursor.close()
        conn.close()
        print("\n" + "=" * 70)
        print("MIGRATION COMPLETE")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
