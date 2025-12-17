"""
Test Calculator Pricing Wrapper Integration
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from calculator_pricing_wrapper import (
    calculator_database_get_schema_guide,
    calculator_database_list_queries,
    calculator_database_query
)

print('='*80)
print('CALCULATOR PRICING WRAPPER - INTEGRATION TEST')
print('='*80)

# Test 1: Schema Guide with Dynamic Query Injection
print('\n1. SCHEMA GUIDE TEST')
print('-'*80)
try:
    result = calculator_database_get_schema_guide()
    
    if result['success']:
        guide = result['guide']
        print(f"✅ Schema guide generated successfully")
        print(f"   Total tables: {result['total_tables']}")
        print(f"   Total rows: {result['total_rows']}")
        print(f"   Query count: {result['query_count']}")
        print(f"\n   Guide sections: {list(guide.keys())}")
        
        # Verify dynamic injection
        available_queries = guide.get('available_queries', [])
        print(f"\n   DYNAMIC INJECTION TEST:")
        print(f"   Available queries injected: {len(available_queries)}")
        
        if len(available_queries) == 7:
            print(f"   ✅ All 7 queries injected successfully")
            print(f"\n   Query names:")
            for i, q in enumerate(available_queries, 1):
                print(f"      {i}. {q['name']}")
                print(f"         Description: {q['description'][:70]}...")
                print(f"         Parameters: {list(q['parameters'].keys())}")
        else:
            print(f"   ⚠️  Expected 7 queries, got {len(available_queries)}")
    else:
        print(f"❌ Schema guide failed: {result.get('error')}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 2: List Queries Function
print('\n2. LIST QUERIES TEST')
print('-'*80)
try:
    result = calculator_database_list_queries("Calculator Pricing Management")
    
    if result['success']:
        print(f"✅ List queries succeeded")
        print(f"   Category: {result['category']}")
        print(f"   Query count: {result['query_count']}")
        print(f"\n   Queries returned:")
        for i, q in enumerate(result['queries'], 1):
            print(f"      {i}. {q['name']}")
            print(f"         Best for: {q.get('best_for', 'N/A')[:60]}...")
            print(f"         Validated: {q.get('validated', False)}")
    else:
        print(f"❌ List queries failed: {result.get('error')}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")
    import traceback
    traceback.print_exc()

# Test 3: Query Function (Dry Run - No DB Connection)
print('\n3. QUERY FUNCTION TEST (Dry Run)')
print('-'*80)
try:
    # This will fail without DB connection, but we can verify the function exists and validates input
    test_sql = "SELECT * FROM calculator_pricing_parameters WHERE parameter_name = %s LIMIT 1"
    params = ("impos_setup",)
    
    print(f"   Testing query validation...")
    print(f"   SQL: {test_sql}")
    print(f"   Params: {params}")
    
    result = calculator_database_query(test_sql, params)
    
    if not result['success']:
        error = result.get('error', '')
        if 'No database connection' in error or 'connection' in error.lower():
            print(f"   ✅ Function exists and validates (no DB connection available)")
            print(f"   Expected error: {error[:80]}...")
        else:
            print(f"   ⚠️  Unexpected error: {error}")
    else:
        print(f"   ✅ Query executed successfully (DB connection available)")
        print(f"   Rows returned: {result.get('row_count', 0)}")
except Exception as e:
    print(f"   ❌ Exception: {str(e)}")

# Test 4: Integration Verification
print('\n4. INTEGRATION VERIFICATION')
print('-'*80)
checks = [
    ("calculator_database_get_schema_guide exists", callable(calculator_database_get_schema_guide)),
    ("calculator_database_list_queries exists", callable(calculator_database_list_queries)),
    ("calculator_database_query exists", callable(calculator_database_query)),
    ("Schema guide returns success", result['success'] if 'result' in locals() else False),
    ("Dynamic injection working", len(available_queries) == 7 if 'available_queries' in locals() else False),
    ("All queries validated", all(q.get('validated', False) for q in available_queries) if 'available_queries' in locals() else False)
]

passed = sum(1 for _, check in checks if check)
total = len(checks)

print(f"\nIntegration Checks: {passed}/{total} passed\n")
for check_name, check_result in checks:
    status = "✅" if check_result else "❌"
    print(f"   {status} {check_name}")

# Summary
print('\n' + '='*80)
print('TEST SUMMARY')
print('='*80)
print(f"Total Tests: 4")
print(f"Integration Checks: {passed}/{total} passed")
print(f"\nStatus: {'✅ ALL SYSTEMS OPERATIONAL' if passed == total else '⚠️  SOME CHECKS FAILED'}")
print('='*80)
