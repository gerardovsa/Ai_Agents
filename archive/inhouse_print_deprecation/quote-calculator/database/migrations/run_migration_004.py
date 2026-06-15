"""
Run Migration 004: Create Product Options Tables

Purpose:
    Execute SQL migration to create 4 new tables for product options system:
    - product_options (option definitions)
    - product_option_choices (individual choices with prices)
    - product_option_overrides (customer/time-based price overrides)
    - product_option_history (complete audit trail)

Author: AI Agent
Date: December 17, 2025
"""

import psycopg2
from pathlib import Path

DB_URL = 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

def run_migration():
    """Execute Migration 004 SQL script"""
    print("\n" + "="*80)
    print("MIGRATION 004: CREATE PRODUCT OPTIONS TABLES")
    print("="*80 + "\n")
    
    # Read SQL file
    sql_file = Path(__file__).parent / '004_create_product_options_tables.sql'
    print(f"Reading SQL file: {sql_file.name}")
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"SQL script size: {len(sql)} characters\n")
    
    # Connect and execute
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True  # Required for NOTICE messages
        cur = conn.cursor()
        
        print("Executing SQL migration...\n")
        print("-" * 80)
        
        # Execute and capture NOTICE messages
        cur.execute(sql)
        
        # Fetch any notices
        for notice in conn.notices:
            print(notice.strip())
        
        print("-" * 80)
        
        # Verify tables created
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('product_options', 'product_option_choices', 
                               'product_option_overrides', 'product_option_history')
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        print(f"\n✅ Created {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Verify indexes
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname LIKE 'idx_product_option%'
        """)
        index_count = cur.fetchone()[0]
        print(f"\n✅ Created {index_count} indexes")
        
        # Verify triggers
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.triggers 
            WHERE trigger_schema = 'public' 
            AND (trigger_name LIKE '%product_option%' OR trigger_name LIKE '%choice_price%')
        """)
        trigger_count = cur.fetchone()[0]
        print(f"✅ Created {trigger_count} triggers")
        
        # Verify views
        cur.execute("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'v_%option%'
            ORDER BY table_name
        """)
        views = cur.fetchall()
        print(f"✅ Created {len(views)} views:")
        for view in views:
            print(f"   - {view[0]}")
        
        print("\n" + "="*80)
        print("MIGRATION 004 COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\n✅ Database ready for product options data loading\n")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == '__main__':
    run_migration()
