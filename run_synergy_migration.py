#!/usr/bin/env python3
"""
Execute Synergy Title+Description Migration
Adds title column and due_date fields to milestones, tasks, subtasks tables.
"""
import psycopg2
import sys
from pathlib import Path

# Database connection string from .env
DB_URL = "postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"

# Path to migration SQL file
MIGRATION_FILE = Path(__file__).parent / "data" / "synergy_title_description_migration_FIXED.sql"

def run_migration():
    """Execute the migration SQL script"""
    print("=" * 80)
    print("SYNERGY TITLE+DESCRIPTION MIGRATION")
    print("=" * 80)
    print()
    
    # Read migration SQL
    print(f"📄 Reading migration file: {MIGRATION_FILE}")
    try:
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        print(f"✅ Loaded {len(sql_script)} characters of SQL\n")
    except FileNotFoundError:
        print(f"❌ Migration file not found: {MIGRATION_FILE}")
        sys.exit(1)
    
    # Connect to database
    print(f"🔌 Connecting to Supabase database...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()
        print("✅ Connected successfully\n")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # Execute migration
    print("🚀 Executing migration...")
    print("-" * 80)
    try:
        # Split and execute statements (handle multi-statement SQL)
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        for i, statement in enumerate(statements, 1):
            if not statement:
                continue
                
            # Show first 100 chars of each statement
            preview = statement[:100].replace('\n', ' ')
            print(f"{i}. {preview}...")
            
            cursor.execute(statement)
            
            if cursor.rowcount >= 0:
                print(f"   ✅ Affected {cursor.rowcount} rows")
            else:
                print(f"   ✅ Executed")
        
        # Commit transaction
        conn.commit()
        print("-" * 80)
        print("✅ Migration completed successfully!")
        print()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        sys.exit(1)
    
    # Verify changes
    print("\n📊 VERIFICATION:")
    print("-" * 80)
    
    verify_queries = [
        ("Milestones with title column", 
         "SELECT COUNT(*) FROM synergy_sessions.milestones WHERE title IS NOT NULL"),
        ("Tasks with title column", 
         "SELECT COUNT(*) FROM synergy_sessions.tasks WHERE title IS NOT NULL"),
        ("Subtasks with title column", 
         "SELECT COUNT(*) FROM synergy_sessions.subtasks WHERE title IS NOT NULL"),
        ("Tasks with due_date", 
         "SELECT COUNT(*) FROM synergy_sessions.tasks WHERE due_date IS NOT NULL"),
        ("Subtasks with due_date", 
         "SELECT COUNT(*) FROM synergy_sessions.subtasks WHERE due_date IS NOT NULL"),
    ]
    
    for label, query in verify_queries:
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"✅ {label}: {count}")
        except Exception as e:
            print(f"⚠️ {label}: Could not verify ({e})")
    
    cursor.close()
    conn.close()
    
    print("-" * 80)
    print("\n🎉 MIGRATION COMPLETE!")
    print("\nNext steps:")
    print("1. Deploy backend code to Render (git push)")
    print("2. Test API endpoints with new title+description fields")
    print("3. Verify UI shows separate title and description fields")
    print()

if __name__ == "__main__":
    run_migration()
