"""
Simple verification that all Supabase connections work
"""
import sys
import os

# Suppress emoji output by setting encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection

def test_schema(schema_name):
    """Test a single schema connection"""
    try:
        conn = get_database_connection(schema_name)
        cursor = conn.cursor()
        
        # Get table count
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s
        """, (schema_name,))
        
        result = cursor.fetchone()
        table_count = result[0] if isinstance(result, tuple) else result['count']
        
        conn.close()
        
        return True, table_count
    except Exception as e:
        return False, str(e)

print("="*80)
print("SUPABASE CONNECTION VERIFICATION")
print("="*80)

schemas = ['ai_infrastructure', 'sessions', 'synergy_sessions', 'kanban_analytics']

all_passed = True

for schema in schemas:
    success, result = test_schema(schema)
    
    if success:
        print(f"[PASS] {schema:20} - {result} tables")
    else:
        print(f"[FAIL] {schema:20} - ERROR: {result}")
        all_passed = False

print("="*80)

if all_passed:
    print("[SUCCESS] All Supabase connections working!")
    print("          All schemas accessible")
    print("          Ready for production")
else:
    print("[ERROR] Some connections failed - check errors above")

print("="*80)
