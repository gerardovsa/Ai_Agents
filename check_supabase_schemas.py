"""Check all schemas in Supabase PostgreSQL database"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

try:
    print("=" * 80)
    print("SUPABASE DATABASE SCHEMA ANALYSIS")
    print("=" * 80)
    
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Get all schemas
    print("\n1. ALL SCHEMAS:")
    print("-" * 80)
    cursor.execute("""
        SELECT schema_name 
        FROM information_schema.schemata 
        WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
        ORDER BY schema_name
    """)
    schemas = cursor.fetchall()
    print(f"Found {len(schemas)} custom schemas:\n")
    for row in schemas:
        schema_name = row[0] if isinstance(row, tuple) else row['schema_name']
        print(f"  - {schema_name}")
    
    # Get tables in each schema
    print("\n2. TABLES IN EACH SCHEMA:")
    print("-" * 80)
    
    for schema_row in schemas:
        schema_name = schema_row[0] if isinstance(schema_row, tuple) else schema_row['schema_name']
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
            ORDER BY table_name
        """, (schema_name,))
        
        tables = cursor.fetchall()
        
        print(f"\n📁 Schema: {schema_name}")
        if tables:
            print(f"   Tables: {len(tables)}")
            for table_row in tables:
                table_name = table_row[0] if isinstance(table_row, tuple) else table_row['table_name']
                
                # Get column count
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s
                """, (schema_name, table_name))
                col_result = cursor.fetchone()
                col_count = col_result[0] if isinstance(col_result, tuple) else col_result['count']
                
                print(f"   - {table_name} ({col_count} columns)")
        else:
            print(f"   ⚠️  NO TABLES")
    
    # Check for specific ai_infrastructure tables
    print("\n3. REQUIRED AI_INFRASTRUCTURE TABLES CHECK:")
    print("-" * 80)
    
    required_tables = [
        'users',
        'user_sessions',
        'user_gmail_accounts',
        'user_platform_credentials',
        'oauth_tokens',
        'workspaces',
        'scheduled_tasks',
        'automation_executions',
        'thread_assignments',
        'prompt_library'
    ]
    
    for table in required_tables:
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'ai_infrastructure' 
                AND table_name = %s
            )
        """, (table,))
        exists_result = cursor.fetchone()
        exists = exists_result[0] if isinstance(exists_result, tuple) else exists_result['exists']
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
    
    # Check public schema tables
    print("\n4. PUBLIC SCHEMA TABLES:")
    print("-" * 80)
    cursor.execute("""
        SELECT table_name, 
               (SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = t.table_name) as col_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    public_tables = cursor.fetchall()
    
    if public_tables:
        print(f"Found {len(public_tables)} tables in public schema:\n")
        for row in public_tables:
            print(f"  - {row[0]} ({row[1]} columns)")
    else:
        print("  No tables in public schema")
    
    # Get auth schema tables (Supabase default)
    print("\n5. AUTH SCHEMA TABLES (Supabase Auth):")
    print("-" * 80)
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'auth'
        ORDER BY table_name
    """)
    auth_tables = cursor.fetchall()
    
    if auth_tables:
        print(f"Found {len(auth_tables)} auth tables:\n")
        for row in auth_tables:
            print(f"  - {row[0]}")
    else:
        print("  No auth schema found")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    conn.close()
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
