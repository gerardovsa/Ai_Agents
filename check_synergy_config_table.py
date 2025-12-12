#!/usr/bin/env python3
"""
Check if synergy_sessions.synergy_config table exists
If not, run the migration
"""

import os
import psycopg2
from psycopg2 import sql

# Set connection
db_url = os.environ.get('SUPABASE_DB_URL_POOLER') or 'postgresql://postgres.ryoicrdifiqhqpsnjmdo:inhouseprint@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres'

print("\n" + "="*70)
print("CHECKING SYNERGY CONFIG TABLE")
print("="*70)

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_schema = 'synergy_sessions' 
            AND table_name = 'synergy_config'
        );
    """)
    
    exists = cursor.fetchone()[0]
    
    if exists:
        print("✅ Table synergy_sessions.synergy_config EXISTS")
        
        # Count rows
        cursor.execute("SELECT COUNT(*) FROM synergy_sessions.synergy_config")
        count = cursor.fetchone()[0]
        print(f"   Rows: {count}")
        
        if count > 0:
            # Show sample data
            cursor.execute("SELECT config_id, config_type FROM synergy_sessions.synergy_config LIMIT 5")
            rows = cursor.fetchall()
            print("   Sample configs:")
            for row in rows:
                print(f"     - {row[0]} ({row[1]})")
    else:
        print("❌ Table synergy_sessions.synergy_config DOES NOT EXIST")
        print("\n📋 Need to run migration:")
        print("   File: migrations/add_synergy_config_table.sql")
        print("\n🔧 Would you like to create the table? (Y/N)")
        
        response = input("> ").strip().upper()
        
        if response == 'Y':
            print("\n📥 Reading migration file...")
            with open('migrations/add_synergy_config_table.sql', 'r', encoding='utf-8') as f:
                migration_sql = f.read()
            
            print("🚀 Running migration...")
            cursor.execute(migration_sql)
            conn.commit()
            print("✅ Migration complete!")
            
            # Verify
            cursor.execute("SELECT COUNT(*) FROM synergy_sessions.synergy_config")
            count = cursor.fetchone()[0]
            print(f"✅ Table created with {count} default config rows")
        else:
            print("⏭️  Skipped migration")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

print("="*70 + "\n")
