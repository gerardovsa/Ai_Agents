"""
Verify prompt_library table schema and count
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

print("\n" + "="*60)
print("Checking prompt_library table...")
print("="*60 + "\n")

try:
    conn = get_database_connection('ai_infrastructure')
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'ai_infrastructure' 
          AND table_name = 'prompt_library'
    """)
    table_info = cur.fetchone()
    
    if table_info:
        schema = table_info[0] if isinstance(table_info, tuple) else table_info['table_schema']
        table = table_info[1] if isinstance(table_info, tuple) else table_info['table_name']
        print(f"✅ Table exists: {schema}.{table}")
    else:
        print("❌ Table does NOT exist in ai_infrastructure schema")
        cur.close()
        conn.close()
        sys.exit(1)
    
    # Check indexes
    cur.execute("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'ai_infrastructure' 
          AND tablename = 'prompt_library'
        ORDER BY indexname
    """)
    indexes = cur.fetchall()
    print(f"\n✅ Indexes found: {len(indexes)}")
    for idx in indexes:
        idx_name = idx[0] if isinstance(idx, tuple) else idx['indexname']
        print(f"   - {idx_name}")
    
    # Check row count
    cur.execute("SELECT COUNT(*) FROM ai_infrastructure.prompt_library")
    result = cur.fetchone()
    count = result[0] if isinstance(result, tuple) else result['count']
    print(f"\n✅ Row count: {count} prompts")
    
    # Check columns
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'ai_infrastructure' 
          AND table_name = 'prompt_library'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print(f"\n✅ Columns ({len(columns)}):")
    for col in columns:
        col_name = col[0] if isinstance(col, tuple) else col['column_name']
        col_type = col[1] if isinstance(col, tuple) else col['data_type']
        print(f"   - {col_name}: {col_type}")
    
    cur.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ Schema verification PASSED")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
