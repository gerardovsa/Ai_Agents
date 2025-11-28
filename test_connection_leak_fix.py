"""
Test connection leak fix - verify connections are properly returned to pool
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

from shared.database_utils import get_database_connection, get_pool_stats

def test_context_manager():
    """Test that connections are returned when using context manager"""
    print("\n" + "="*70)
    print("TEST 1: Context Manager Connection Return")
    print("="*70)
    
    initial_stats = get_pool_stats()
    print(f"Initial state:")
    print(f"  Acquired: {initial_stats['connections_acquired']}")
    print(f"  Returned: {initial_stats['connections_returned']}")
    print(f"  Leaked: {initial_stats['connections_acquired'] - initial_stats['connections_returned']}")
    
    # Test normal usage
    print("\nOpening connection with context manager...")
    with get_database_connection('sessions') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        print(f"  Query result: {result}")
    
    print("Context manager exited - connection should be returned")
    
    mid_stats = get_pool_stats()
    print(f"\nAfter context manager:")
    print(f"  Acquired: {mid_stats['connections_acquired']}")
    print(f"  Returned: {mid_stats['connections_returned']}")
    print(f"  Leaked: {mid_stats['connections_acquired'] - mid_stats['connections_returned']}")
    
    leaked = mid_stats['connections_acquired'] - mid_stats['connections_returned']
    if leaked == 0:
        print("\n✅ TEST PASSED: No connection leaks")
    else:
        print(f"\n❌ TEST FAILED: {leaked} connection(s) leaked")
    
    return leaked == 0


def test_exception_handling():
    """Test that connections are returned even when exceptions occur"""
    print("\n" + "="*70)
    print("TEST 2: Exception Handling Connection Return")
    print("="*70)
    
    initial_stats = get_pool_stats()
    print(f"Initial state:")
    print(f"  Acquired: {initial_stats['connections_acquired']}")
    print(f"  Returned: {initial_stats['connections_returned']}")
    
    # Test exception handling
    print("\nOpening connection and triggering exception...")
    try:
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            print("  Query executed")
            raise ValueError("Simulated exception")
    except ValueError as e:
        print(f"  Exception caught: {e}")
    
    print("Exception handled - connection should still be returned")
    
    final_stats = get_pool_stats()
    print(f"\nAfter exception handling:")
    print(f"  Acquired: {final_stats['connections_acquired']}")
    print(f"  Returned: {final_stats['connections_returned']}")
    print(f"  Leaked: {final_stats['connections_acquired'] - final_stats['connections_returned']}")
    
    leaked = final_stats['connections_acquired'] - final_stats['connections_returned']
    if leaked == 0:
        print("\n✅ TEST PASSED: No connection leaks after exception")
    else:
        print(f"\n❌ TEST FAILED: {leaked} connection(s) leaked after exception")
    
    return leaked == 0


def test_multiple_connections():
    """Test multiple sequential connections"""
    print("\n" + "="*70)
    print("TEST 3: Multiple Sequential Connections")
    print("="*70)
    
    initial_stats = get_pool_stats()
    print(f"Initial state:")
    print(f"  Acquired: {initial_stats['connections_acquired']}")
    print(f"  Returned: {initial_stats['connections_returned']}")
    
    # Open 5 connections sequentially
    print("\nOpening 5 connections sequentially...")
    for i in range(5):
        with get_database_connection('sessions') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            print(f"  Connection {i+1} used")
    
    print("All connections closed")
    
    final_stats = get_pool_stats()
    print(f"\nAfter 5 connections:")
    print(f"  Acquired: {final_stats['connections_acquired']}")
    print(f"  Returned: {final_stats['connections_returned']}")
    print(f"  Leaked: {final_stats['connections_acquired'] - final_stats['connections_returned']}")
    
    leaked = final_stats['connections_acquired'] - final_stats['connections_returned']
    if leaked == 0:
        print("\n✅ TEST PASSED: All connections returned")
    else:
        print(f"\n❌ TEST FAILED: {leaked} connection(s) leaked")
    
    return leaked == 0


def main():
    print("="*70)
    print("CONNECTION LEAK FIX TEST SUITE")
    print("="*70)
    print("\nTesting DatabaseConnection.__exit__() fix...")
    print("This verifies connections are properly returned to pool")
    
    # Run tests
    test1_pass = test_context_manager()
    test2_pass = test_exception_handling()
    test3_pass = test_multiple_connections()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Test 1 (Context Manager): {'✅ PASSED' if test1_pass else '❌ FAILED'}")
    print(f"Test 2 (Exception Handling): {'✅ PASSED' if test2_pass else '❌ FAILED'}")
    print(f"Test 3 (Multiple Connections): {'✅ PASSED' if test3_pass else '❌ FAILED'}")
    
    all_passed = test1_pass and test2_pass and test3_pass
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - Connection leak fix working!")
    else:
        print("\n⚠️  SOME TESTS FAILED - Review connection handling")
    
    # Final pool stats
    final_stats = get_pool_stats()
    print("\n" + "="*70)
    print("FINAL POOL STATISTICS")
    print("="*70)
    print(f"Pools created: {final_stats['pools_created']}")
    print(f"Connections acquired: {final_stats['connections_acquired']}")
    print(f"Connections returned: {final_stats['connections_returned']}")
    print(f"Leaked connections: {final_stats['connections_acquired'] - final_stats['connections_returned']}")
    print(f"Avg wait time: {final_stats['avg_wait_time']*1000:.2f}ms")
    print("="*70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
