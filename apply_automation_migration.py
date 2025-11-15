"""
Apply Automation Tables Migration to Supabase
==============================================
Creates visual_automations and automation_executions tables
"""

import psycopg2
import os
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for Supabase connection string
    supabase_url = os.getenv('SUPABASE_DB_URL')
    
    if not supabase_url:
        print("❌ ERROR: SUPABASE_DB_URL environment variable not set")
        print("\nPlease set it in your .env file or terminal:")
        print("  $env:SUPABASE_DB_URL = 'postgresql://postgres:[password]@[host]:5432/postgres'")
        return
    
    # Read migration file
    sql_file = Path(__file__).parent / 'supabase_migrations' / '004_automation_tables.sql'
    
    if not sql_file.exists():
        print(f"❌ ERROR: Migration file not found: {sql_file}")
        return
    
    print(f"📄 Reading migration file: {sql_file.name}")
    sql_content = sql_file.read_text(encoding='utf-8')
    
    try:
        # Connect to Supabase PostgreSQL
        print("🔌 Connecting to Supabase...")
        conn = psycopg2.connect(supabase_url)
        cursor = conn.cursor()
        
        # Execute migration
        print("⚙️  Applying migration...")
        cursor.execute(sql_content)
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('visual_automations', 'automation_executions')
            ORDER BY table_name
        """)
        
        tables = cursor.fetchall()
        
        if len(tables) == 2:
            print(f"✅ Successfully created tables:")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print(f"⚠️  Warning: Expected 2 tables, found {len(tables)}")
        
        # Check visual_automations columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'visual_automations'
            ORDER BY ordinal_position
        """)
        
        columns = cursor.fetchall()
        print(f"\n📊 visual_automations has {len(columns)} columns:")
        for col_name, col_type in columns[:10]:  # Show first 10
            print(f"   - {col_name}: {col_type}")
        
        if len(columns) > 10:
            print(f"   ... and {len(columns) - 10} more")
        
        # Commit changes
        conn.commit()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart Flask: BISTART")
        print("   2. Test API: curl http://localhost:5001/api/automation/list -H 'X-User-ID: 1'")
        
    except psycopg2.Error as e:
        print(f"❌ PostgreSQL Error: {e}")
        print(f"\nError code: {e.pgcode}")
        print(f"Error details: {e.pgerror}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
