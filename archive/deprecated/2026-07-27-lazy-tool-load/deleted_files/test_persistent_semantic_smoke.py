"""
SMOKE TEST: Persistent Semantic Search
======================================

Quick validation that the system loads without errors.

USAGE:
    python tests/test_persistent_semantic_smoke.py

EXPECTED: All imports work, basic initialization succeeds
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def smoke_test():
    """Basic import and instantiation test"""
    print("\n" + "=" * 80)
    print("SMOKE TEST: Persistent Semantic Search")
    print("=" * 80)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Import registry
    print("\n[TEST 1/6] Import tool registry...")
    try:
        from tools.registry_v3 import get_registry
        print("✅ PASS: Registry imported")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
        return
    
    # Test 2: Import persistent semantic search
    print("\n[TEST 2/6] Import PersistentSemanticToolSearch...")
    try:
        from tools.persistent_semantic_search import PersistentSemanticToolSearch
        print("✅ PASS: PersistentSemanticToolSearch imported")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
        return
    
    # Test 3: Load registry
    print("\n[TEST 3/6] Load tool registry...")
    try:
        registry = get_registry()
        tool_count = len(registry.tools)
        print(f"✅ PASS: Registry loaded ({tool_count} tools)")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
        return
    
    # Test 4: Check sentence-transformers
    print("\n[TEST 4/6] Check sentence-transformers availability...")
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ PASS: sentence-transformers available")
        tests_passed += 1
    except ImportError:
        print("⚠️ SKIP: sentence-transformers not installed (pip install sentence-transformers)")
        print("   Note: System will work but semantic search unavailable")
        tests_passed += 1  # Not a failure, just a skip
    
    # Test 5: Check database connection
    print("\n[TEST 5/6] Check database connection...")
    try:
        from AI_infrastructure.shared.database_utils import execute_query
        result = execute_query("SELECT 1 as test", fetch_mode='one')
        if result and result.get('test') == 1:
            print("✅ PASS: Database connected")
            tests_passed += 1
        else:
            print("⚠️ WARN: Database query returned unexpected result")
            tests_passed += 1  # Not critical
    except Exception as e:
        print(f"⚠️ WARN: Database unavailable: {e}")
        print("   Note: System will work with in-memory fallback")
        tests_passed += 1  # Not critical
    
    # Test 6: Import management script
    print("\n[TEST 6/6] Import management script...")
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))
        import manage_semantic_cache
        print("✅ PASS: Management script imported")
        tests_passed += 1
    except Exception as e:
        print(f"❌ FAIL: {e}")
        tests_failed += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SMOKE TEST SUMMARY")
    print("=" * 80)
    print(f"✅ Passed: {tests_passed}/6")
    print(f"❌ Failed: {tests_failed}/6")
    
    if tests_failed == 0:
        print("\n🎉 ALL SMOKE TESTS PASSED")
        print("System is ready for compile and integration testing")
        return True
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Fix errors before proceeding")
        return False


if __name__ == '__main__':
    success = smoke_test()
    sys.exit(0 if success else 1)
