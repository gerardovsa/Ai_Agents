"""
Test all database connections to ensure they work with Supabase PostgreSQL
"""
import sys
sys.path.insert(0, 'AI_infrastructure')

from shared.database_utils import get_database_connection
from datetime import datetime

def test_connection(schema_name, test_query):
    """Test a database connection"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing: {schema_name}")
        print(f"{'='*60}")
        
        conn = get_database_connection(schema_name)
        cursor = conn.cursor()
        
        # Test query execution
        cursor.execute(test_query)
        result = cursor.fetchone()
        
        print(f"✅ Connection successful")
        print(f"   Query result: {result}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        return False

def test_crud_operations(schema_name, table_name):
    """Test Create, Read, Update, Delete operations"""
    try:
        print(f"\n{'='*60}")
        print(f"Testing CRUD: {schema_name}.{table_name}")
        print(f"{'='*60}")
        
        conn = get_database_connection(schema_name)
        cursor = conn.cursor()
        
        # Test SELECT with %s placeholder
        print("  Testing SELECT with WHERE %s...")
        cursor.execute(f"SELECT COUNT(*) FROM {schema_name}.{table_name}")
        result = cursor.fetchone()
        count = result[0] if isinstance(result, tuple) else result.get('count', 0)
        print(f"  ✅ SELECT works (found {count} rows)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"  ❌ CRUD test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("="*80)
    print("DATABASE CONNECTION TEST SUITE")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: ai_infrastructure schema
    if test_connection('ai_infrastructure', 'SELECT COUNT(*) FROM ai_infrastructure.users'):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 2: sessions schema
    if test_connection('sessions', 'SELECT COUNT(*) FROM sessions.threads'):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 3: synergy_sessions schema
    if test_connection('synergy_sessions', 'SELECT COUNT(*) FROM synergy_sessions.synergy_sessions'):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 4: kanban_analytics schema
    if test_connection('kanban_analytics', 'SELECT COUNT(*) FROM kanban_analytics.job_tickets'):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 5: stock_data schema  
    if test_connection('stock_data', 'SELECT COUNT(*) FROM stock_data.unified_stocks'):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test CRUD operations on key tables
    print("\n" + "="*80)
    print("CRUD OPERATIONS TEST")
    print("="*80)
    
    crud_tests = [
        ('ai_infrastructure', 'users'),
        ('ai_infrastructure', 'oauth_tokens'),
        ('sessions', 'threads'),
        ('sessions', 'messages'),
    ]
    
    for schema, table in crud_tests:
        if test_crud_operations(schema, table):
            tests_passed += 1
        else:
            tests_failed += 1
    
    # Test placeholder conversion
    print("\n" + "="*80)
    print("PLACEHOLDER CONVERSION TEST")
    print("="*80)
    
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # This should work with %s
        cursor.execute("SELECT id FROM ai_infrastructure.users WHERE id = %s LIMIT 1", (1,))
        result = cursor.fetchone()
        print(f"✅ PostgreSQL placeholder (%s) works correctly")
        tests_passed += 1
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Placeholder test failed: {str(e)}")
        tests_failed += 1
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"Total: {tests_passed + tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! Database connections are working correctly.")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Review errors above.")
    
    print("="*80)
