"""
RUN ALL TESTS: Persistent Semantic Search
=========================================

Runs all test suites in sequence:
1. Smoke Test (imports, basic checks)
2. Compile Test (code structure, methods)
3. Endpoint Test (search functionality)
4. End-to-End Test (full integration)

USAGE:
    python tests/run_all_tests.py

EXPECTED: All tests pass
"""

import sys
import os
from pathlib import Path
import subprocess

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_suite(test_name: str, test_file: str) -> bool:
    """Run a test suite and return success status"""
    print("\n" + "█" * 80)
    print(f"█ {test_name}")
    print("█" * 80)
    
    test_path = Path(__file__).parent / test_file
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=False,
            text=True
        )
        
        success = result.returncode == 0
        
        if success:
            print(f"\n✅ {test_name} PASSED\n")
        else:
            print(f"\n❌ {test_name} FAILED\n")
        
        return success
        
    except Exception as e:
        print(f"\n❌ {test_name} ERROR: {e}\n")
        return False


def main():
    """Run all test suites"""
    print("\n" + "=" * 80)
    print("RUNNING ALL TEST SUITES")
    print("=" * 80)
    print("\nTest suites:")
    print("  1. Smoke Test (quick validation)")
    print("  2. Compile Test (code structure)")
    print("  3. Endpoint Test (search functionality)")
    print("  4. End-to-End Test (full integration)")
    print("\n" + "=" * 80 + "\n")
    
    results = {}
    
    # Run smoke test
    results['Smoke Test'] = run_test_suite(
        "SMOKE TEST",
        "test_persistent_semantic_smoke.py"
    )
    
    # If smoke test fails, stop
    if not results['Smoke Test']:
        print("\n⚠️ SMOKE TEST FAILED - Skipping remaining tests")
        print("Fix import/dependency issues before proceeding\n")
        return False
    
    # Run compile test
    results['Compile Test'] = run_test_suite(
        "COMPILE TEST",
        "test_persistent_semantic_compile.py"
    )
    
    # Run endpoint test
    results['Endpoint Test'] = run_test_suite(
        "ENDPOINT TEST",
        "test_persistent_semantic_endpoint.py"
    )
    
    # Run end-to-end test
    results['E2E Test'] = run_test_suite(
        "END-TO-END TEST",
        "test_persistent_semantic_e2e.py"
    )
    
    # Final summary
    print("\n" + "=" * 80)
    print("FINAL TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    failed_tests = total_tests - passed_tests
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print("\n" + "-" * 80)
    print(f"Total: {passed_tests}/{total_tests} passed")
    print("=" * 80)
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ SYSTEM READY FOR DEPLOYMENT")
        print("\nNext steps:")
        print("  1. Run migration: python AI_infrastructure/migrations/create_tool_embeddings_tables.py")
        print("  2. Restart Flask: python AI_infrastructure/flask_app.py")
        print("  3. Verify: python tools/manage_semantic_cache.py status")
        print()
        return True
    else:
        print(f"\n⚠️ {failed_tests} TEST SUITE(S) FAILED")
        print("\nReview failures above and fix issues before deploying")
        print()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
