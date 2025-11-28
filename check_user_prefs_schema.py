"""Check user_preferences table schema in PostgreSQL"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection

def check_schema():
    conn = get_database_connection('ai_infrastructure')
    cursor = conn.cursor()
    
    # Get column info
    cursor.execute("""
        SELECT column_name, data_type, column_default, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'user_preferences'
        ORDER BY ordinal_position
    """)
    
    columns = cursor.fetchall()
    
    print("=" * 80)
    print("CURRENT user_preferences TABLE SCHEMA")
    print("=" * 80)
    print(f"\nTotal columns: {len(columns)}\n")
    
    for i, row in enumerate(columns, 1):
        name = row['column_name']
        dtype = row['data_type']
        default = row['column_default']
        default_str = str(default)[:40] if default else "None"
        print(f"{i:2d}. {name:30s} {dtype:15s} DEFAULT: {default_str}")
    
    conn.close()
    
    # Check for AI settings columns
    print("\n" + "=" * 80)
    print("AI SETTINGS COLUMNS CHECK")
    print("=" * 80)
    
    col_names = [col['column_name'] for col in columns]
    
    ai_columns = {
        'ai_model': 'TEXT',
        'ai_temperature': 'REAL',
        'ai_top_p': 'REAL',
        'ai_max_tokens': 'INTEGER',
        'ai_thinking_enabled': 'INTEGER',
        'ai_thinking_budget': 'INTEGER',
        'ai_streaming_enabled': 'INTEGER'
    }
    
    found = []
    missing = []
    
    for col_name, expected_type in ai_columns.items():
        if col_name in col_names:
            found.append(col_name)
            print(f"✅ FOUND: {col_name}")
        else:
            missing.append(col_name)
            print(f"❌ MISSING: {col_name}")
    
    print(f"\n✅ Found: {len(found)}/{len(ai_columns)}")
    print(f"❌ Missing: {len(missing)}/{len(ai_columns)}")
    
    if len(found) == len(ai_columns):
        print("\n🎉 ALL AI SETTINGS COLUMNS EXIST!")
    else:
        print(f"\n⚠️  {len(missing)} AI SETTINGS COLUMNS ARE MISSING")
        print(f"    Missing: {', '.join(missing)}")

if __name__ == '__main__':
    check_schema()
