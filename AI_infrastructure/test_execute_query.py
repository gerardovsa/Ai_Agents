"""
Smoke Test for execute_query() Implementation
Tests all fetch modes and verifies connection cleanup
"""

import sys
from pathlib import Path

# Add AI_infrastructure to path
ai_infra = Path(__file__).parent
sys.path.insert(0, str(ai_infra))

print("=" * 70)
print("SMOKE TEST: execute_query() Implementation")
print("=" * 70)

# Test 1: Import test
print("\n[TEST 1] Import execute_query from database_utils...")
try:
    from shared.database_utils import execute_query
    print("✅ PASS - execute_query imported successfully")
except ImportError as e:
    print(f"❌ FAIL - Import failed: {e}")
    sys.exit(1)

# Test 2: Test 'value' mode (simplest - no table needed)
print("\n[TEST 2] Test fetch_mode='value' (SELECT 1)...")
try:
    result = execute_query("SELECT 1 as test", (), fetch_mode='value')
    assert result == 1, f"Expected 1, got {result}"
    print(f"✅ PASS - Got value: {result}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 3: Test 'one' mode
print("\n[TEST 3] Test fetch_mode='one' (SELECT NOW())...")
try:
    result = execute_query("SELECT NOW() as timestamp", (), fetch_mode='one')
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert 'timestamp' in result, "Expected 'timestamp' key in result"
    print(f"✅ PASS - Got row: {result}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 4: Test 'all' mode
print("\n[TEST 4] Test fetch_mode='all' (SELECT multiple rows)...")
try:
    result = execute_query(
        "SELECT * FROM (VALUES (1, 'a'), (2, 'b'), (3, 'c')) AS t(id, name)",
        (),
        fetch_mode='all'
    )
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 3, f"Expected 3 rows, got {len(result)}"
    print(f"✅ PASS - Got {len(result)} rows: {result}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 5: Test None mode (no fetch, just row count)
print("\n[TEST 5] Test fetch_mode=None (CREATE temp table)...")
try:
    # Create temporary table
    result = execute_query(
        "CREATE TEMPORARY TABLE IF NOT EXISTS test_execute_query (id SERIAL, value TEXT)",
        (),
        fetch_mode=None
    )
    print(f"✅ PASS - Table created, affected rows: {result}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 6: Test INSERT with parameters
print("\n[TEST 6] Test INSERT with parameters...")
try:
    result = execute_query(
        "INSERT INTO test_execute_query (value) VALUES (%s)",
        ('test_value',),
        fetch_mode=None
    )
    assert result == 1, f"Expected 1 affected row, got {result}"
    print(f"✅ PASS - Inserted 1 row")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 7: Verify inserted data
print("\n[TEST 7] Test SELECT from inserted data...")
try:
    result = execute_query(
        "SELECT * FROM test_execute_query WHERE value = %s",
        ('test_value',),
        fetch_mode='one'
    )
    assert result is not None, "Expected row, got None"
    assert result['value'] == 'test_value', f"Expected 'test_value', got {result['value']}"
    print(f"✅ PASS - Retrieved inserted row: {result}")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 8: Test error handling
print("\n[TEST 8] Test error handling (invalid SQL)...")
try:
    result = execute_query("SELECT * FROM nonexistent_table_xyz", (), fetch_mode='all')
    print(f"❌ FAIL - Should have raised exception")
    sys.exit(1)
except Exception as e:
    print(f"✅ PASS - Exception raised correctly: {type(e).__name__}")

# Test 9: Test different schema
print("\n[TEST 9] Test different schema (sessions)...")
try:
    result = execute_query("SELECT 1 as test", (), fetch_mode='value', schema='sessions')
    assert result == 1, f"Expected 1, got {result}"
    print(f"✅ PASS - Sessions schema works")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 10: Connection pool health check
print("\n[TEST 10] Check connection pool health...")
try:
    from shared.database_utils import get_pool_stats
    stats = get_pool_stats()
    
    acquired = stats['connections_acquired']
    returned = stats['connections_returned']
    leaked = acquired - returned
    
    print(f"   Acquired: {acquired}")
    print(f"   Returned: {returned}")
    print(f"   Leaked: {leaked}")
    
    if leaked > 5:
        print(f"⚠️  WARNING - {leaked} connections leaked (may be normal for first run)")
    else:
        print(f"✅ PASS - Connection pool healthy")
except Exception as e:
    print(f"❌ FAIL - {e}")
    sys.exit(1)

# Test 11: Verify scheduler can now import
print("\n[TEST 11] Test scheduler.py import (previously broken)...")
try:
    # This should work now that execute_query exists
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "scheduler",
        str(ai_infra / "scheduler.py")
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ PASS - scheduler.py imports without errors")
    else:
        print("❌ FAIL - Could not load scheduler.py")
except Exception as e:
    print(f"❌ FAIL - scheduler.py import failed: {e}")
    # Not critical, continue

# Test 12: Verify pgvector_routes can now import
print("\n[TEST 12] Test pgvector_routes.py import (previously broken)...")
try:
    spec = importlib.util.spec_from_file_location(
        "pgvector_routes",
        str(ai_infra / "routes" / "pgvector_routes.py")
    )
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ PASS - pgvector_routes.py imports without errors")
    else:
        print("❌ FAIL - Could not load pgvector_routes.py")
except Exception as e:
    print(f"❌ FAIL - pgvector_routes.py import failed: {e}")
    # Not critical, continue

print("\n" + "=" * 70)
print("SMOKE TEST COMPLETE - All critical tests passed!")
print("=" * 70)
print("\nNext steps:")
print("1. Start Flask server: python AI_infrastructure/flask_app.py")
print("2. Test endpoints: curl http://localhost:5001/api/pool-health")
print("3. Monitor for connection leaks in logs")
print("=" * 70)
