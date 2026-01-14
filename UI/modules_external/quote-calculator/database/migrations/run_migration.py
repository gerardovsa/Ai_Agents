#!/usr/bin/env python3
"""
Run SQL Migration Script via Python
Executes 001_create_catalog_tables.sql
"""

import psycopg2
from pathlib import Path

# Database configuration - Supabase PostgreSQL
DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

def run_migration():
    """Execute the SQL migration file"""
    
    # Read SQL file
    sql_file = Path(__file__).parent / '001_create_catalog_tables.sql'
    
    print("=" * 80)
    print("CALCULATOR PRICING CATALOG - DATABASE MIGRATION")
    print("=" * 80)
    print(f"\n📄 Reading SQL file: {sql_file.name}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    print(f"✅ Loaded {len(sql_script)} characters of SQL")
    
    # Connect to database
    print(f"\n🔌 Connecting to Supabase PostgreSQL database")
    
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = False  # Use transaction
        cursor = conn.cursor()
        
        print("✅ Connected successfully")
        
        # Execute SQL script
        print("\n🚀 Executing migration...")
        cursor.execute(sql_script)
        
        # Commit transaction
        conn.commit()
        print("✅ Migration executed successfully")
        
        # Verify tables created
        print("\n📊 Verifying tables...")
        cursor.execute("""
            SELECT tablename, 
                   pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables 
            WHERE tablename LIKE 'calculator%'
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        print(f"\n✅ Created {len(tables)} tables:")
        for table_name, size in tables:
            print(f"   - {table_name}: {size}")
        
        # Check sample data
        print("\n📋 Checking sample data...")
        cursor.execute("SELECT COUNT(*) FROM calculator_pricing_parameters;")
        param_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM calculators_registry;")
        calc_count = cursor.fetchone()[0]
        
        print(f"   - Parameters: {param_count}")
        print(f"   - Calculators: {calc_count}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ MIGRATION COMPLETE")
        print("=" * 80)
        print("\n📋 Next Steps:")
        print("   1. Update database password in seeds/load_extracted_data.py")
        print("   2. Run: python seeds/load_extracted_data.py --dry-run")
        print("   3. Run: python seeds/load_extracted_data.py")
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    import sys
    success = run_migration()
    sys.exit(0 if success else 1)
