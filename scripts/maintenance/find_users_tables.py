"""Find all 'users' tables in Supabase across all schemas"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'AI_infrastructure'))

from shared.db_connection_wrapper import get_connection

conn = get_connection('ai_infrastructure')
cursor = conn.cursor()

# Find all users tables
cursor.execute("""
    SELECT table_schema, table_name, 
           (SELECT COUNT(*) FROM information_schema.columns 
            WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
    FROM information_schema.tables t
    WHERE table_name = 'users'
    ORDER BY table_schema
""")

tables = cursor.fetchall()

print("\n" + "="*70)
print("ALL 'users' TABLES IN SUPABASE")
print("="*70)

for table in tables:
    schema = table[0] if isinstance(table, tuple) else table['table_schema']
    name = table[1] if isinstance(table, tuple) else table['table_name']
    col_count = table[2] if isinstance(table, tuple) else table['column_count']
    
    print(f"\n{schema}.{name} ({col_count} columns)")
    
    # Get columns for this specific schema.table
    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
    """, (schema, name))
    
    cols = cursor.fetchall()
    col_names = [c[0] if isinstance(c, tuple) else c['column_name'] for c in cols]
    
    # Check for permissions column
    has_permissions = 'permissions' in col_names
    
    print(f"  Has 'permissions' column: {has_permissions}")
    
    if not has_permissions:
        print(f"  ⚠️  WARNING: This table is MISSING 'permissions' column!")

print("\n" + "="*70)

# Check current search_path
cursor.execute("SHOW search_path")
search_path = cursor.fetchone()
sp_value = search_path[0] if isinstance(search_path, tuple) else search_path['search_path']

print(f"\nCurrent PostgreSQL search_path: {sp_value}")
print("\n⚠️  If 'auth' schema is in search_path BEFORE 'ai_infrastructure',")
print("   queries for 'users' table will use 'auth.users' (Supabase Auth)")
print("   instead of 'ai_infrastructure.users' (your app users)!")

conn.close()
