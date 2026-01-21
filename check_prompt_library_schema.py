"""
Check the actual prompt_library table schema in Supabase
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'AI_infrastructure'))

from shared.database_utils import execute_query

print("\n" + "="*80)
print("CHECKING PROMPT LIBRARY TABLE SCHEMA")
print("="*80 + "\n")

try:
    # Get table schema
    print("1. Checking column definitions...")
    columns = execute_query(
        """
        SELECT column_name, data_type, column_default, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
        AND table_name = 'prompt_library'
        ORDER BY ordinal_position
        """,
        fetch_mode='all'
    )
    
    for col in columns:
        default_val = col['column_default'] or 'None'
        print(f"  {col['column_name']:<20} {col['data_type']:<20} "
              f"default={default_val:<30} nullable={col['is_nullable']}")
    
    # Check if there's a sequence
    print("\n2. Checking for sequences...")
    sequences = execute_query(
        """
        SELECT pg_get_serial_sequence('ai_infrastructure.prompt_library', 'id') as seq_name
        """,
        fetch_mode='one'
    )
    
    if sequences['seq_name']:
        print(f"  ✅ Sequence found: {sequences['seq_name']}")
        
        # Check current sequence value
        seq_info = execute_query(
            f"SELECT last_value FROM {sequences['seq_name']}",
            fetch_mode='one'
        )
        print(f"  Current value: {seq_info['last_value']}")
    else:
        print("  ❌ No sequence found for ID column!")
        print("     This is why the INSERT is failing - ID has no default value.")
    
    # Check existing records
    print("\n3. Checking existing records...")
    count = execute_query(
        "SELECT COUNT(*) as count FROM ai_infrastructure.prompt_library",
        fetch_mode='one'
    )
    print(f"  Total prompts in database: {count['count']}")
    
    if count['count'] > 0:
        # Get max ID
        max_id = execute_query(
            "SELECT MAX(id) as max_id FROM ai_infrastructure.prompt_library",
            fetch_mode='one'
        )
        print(f"  Maximum ID: {max_id['max_id']}")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80 + "\n")
