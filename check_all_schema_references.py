"""
Check All Schema References in Supabase
Identifies tables and ensures all queries use proper schema qualification
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv('.env.master')

def check_all_schemas():
    """Check all three schemas and their tables"""
    
    print("=" * 70)
    print("SUPABASE SCHEMA REFERENCE AUDIT")
    print("=" * 70)
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError:
        print("ERROR: psycopg2 not installed")
        return 1
    
    db_url = os.getenv('SUPABASE_DB_URL')
    if not db_url:
        print("ERROR: SUPABASE_DB_URL not set")
        return 1
    
    try:
        conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        
        # Get all schemas
        schemas = ['ai_infrastructure', 'sessions', 'synergy_sessions']
        
        all_tables = {}
        
        for schema_name in schemas:
            print(f"\n{'='*70}")
            print(f"SCHEMA: {schema_name}")
            print(f"{'='*70}")
            
            # Get tables in schema
            cursor.execute("""
                SELECT table_name, 
                       (SELECT COUNT(*) 
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema = %s
                ORDER BY table_name
            """, (schema_name, schema_name))
            
            tables = cursor.fetchall()
            
            if not tables:
                print(f"  ⚠️  No tables found in {schema_name} schema!")
                continue
            
            all_tables[schema_name] = []
            
            for table in tables:
                table_name = table['table_name']
                col_count = table['column_count']
                all_tables[schema_name].append(table_name)
                
                # Get row count
                try:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {schema_name}.{table_name}")
                    row_count = cursor.fetchone()['count']
                except Exception as e:
                    row_count = "ERROR"
                
                print(f"  📊 {table_name}")
                print(f"      Columns: {col_count}")
                print(f"      Rows: {row_count}")
        
        # Check for duplicate table names across schemas
        print(f"\n{'='*70}")
        print("DUPLICATE TABLE ANALYSIS")
        print(f"{'='*70}")
        
        # Flatten all table names
        all_table_names = []
        for schema, tables in all_tables.items():
            for table in tables:
                all_table_names.append((schema, table))
        
        # Find duplicates
        from collections import defaultdict
        table_locations = defaultdict(list)
        for schema, table in all_table_names:
            table_locations[table].append(schema)
        
        duplicates = {table: schemas for table, schemas in table_locations.items() if len(schemas) > 1}
        
        if duplicates:
            print("\n⚠️  DUPLICATE TABLES FOUND:")
            for table, schemas_list in duplicates.items():
                print(f"\n  {table}:")
                for schema in schemas_list:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {schema}.{table}")
                    count = cursor.fetchone()['count']
                    print(f"    - {schema}.{table} ({count} rows)")
        else:
            print("\n✅ No duplicate table names across schemas")
        
        # Check common cross-schema references
        print(f"\n{'='*70}")
        print("COMMON CROSS-SCHEMA REFERENCES TO CHECK")
        print(f"{'='*70}")
        
        # synergy_sessions might reference sessions.threads or sessions.saved_threads
        if 'synergy_sessions' in all_tables:
            print("\n📋 synergy_sessions schema tables:")
            for table in all_tables['synergy_sessions']:
                print(f"  - {table}")
                
                # Get column details
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = 'synergy_sessions' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                columns = cursor.fetchall()
                
                for col in columns:
                    if 'thread' in col['column_name'].lower():
                        print(f"      🔗 {col['column_name']} ({col['data_type']}) - might reference sessions.threads")
                    if 'session' in col['column_name'].lower():
                        print(f"      🔗 {col['column_name']} ({col['data_type']}) - check session references")
        
        # Check if sessions schema has tables that should be in synergy_sessions
        print(f"\n{'='*70}")
        print("POTENTIAL MISPLACED TABLES")
        print(f"{'='*70}")
        
        if 'sessions' in all_tables:
            for table in all_tables['sessions']:
                if 'synergy' in table.lower():
                    cursor.execute(f"SELECT COUNT(*) as count FROM sessions.{table}")
                    count = cursor.fetchone()['count']
                    print(f"\n⚠️  sessions.{table} ({count} rows)")
                    print(f"    Should this be in synergy_sessions schema?")
        
        if 'synergy_sessions' in all_tables:
            for table in all_tables['synergy_sessions']:
                if 'synergy' not in table.lower():
                    cursor.execute(f"SELECT COUNT(*) as count FROM synergy_sessions.{table}")
                    count = cursor.fetchone()['count']
                    print(f"\n⚠️  synergy_sessions.{table} ({count} rows)")
                    print(f"    Should this be in sessions schema?")
        
        cursor.close()
        conn.close()
        
        print(f"\n{'='*70}")
        print("RECOMMENDATIONS")
        print(f"{'='*70}")
        print("\n1. Check synergy route files for unqualified table names")
        print("2. Ensure synergy tables reference sessions.threads correctly")
        print("3. Verify thread_id foreign keys point to correct schema")
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(check_all_schemas())
