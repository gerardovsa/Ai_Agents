"""
Quick smoke test for thread-local storage functionality
"""
import sys
import threading
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_thread_isolation():
    """Test that thread-local storage is isolated between threads"""
    from tools.registry_v3 import get_registry
    
    results = {'thread1': None, 'thread2': None}
    
    def worker1():
        registry = get_registry()
        registry.set_thread_user_id(14)
        results['thread1'] = registry.get_thread_user_id()
    
    def worker2():
        registry = get_registry()
        registry.set_thread_user_id(99)
        results['thread2'] = registry.get_thread_user_id()
    
    # Start both threads
    t1 = threading.Thread(target=worker1)
    t2 = threading.Thread(target=worker2)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    # Each thread should have its own user_id
    assert results['thread1'] == 14, f"Thread 1 should have user_id=14, got {results['thread1']}"
    assert results['thread2'] == 99, f"Thread 2 should have user_id=99, got {results['thread2']}"
    
    print("✅ Thread isolation test PASSED")

def test_cleanup():
    """Test that cleanup works correctly"""
    from tools.registry_v3 import get_registry
    
    registry = get_registry()
    
    # Set user_id
    registry.set_thread_user_id(42)
    user_id = registry.get_thread_user_id()
    assert user_id == 42, f"Expected 42, got {user_id}"
    
    # Clear user_id
    registry.clear_thread_user_id()
    user_id = registry.get_thread_user_id()
    assert user_id is None, f"Expected None after clear, got {user_id}"
    
    print("✅ Cleanup test PASSED")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("THREAD-LOCAL STORAGE SMOKE TEST")
    print("="*60 + "\n")
    
    print("Test 1: Thread Isolation")
    test_thread_isolation()
    
    print("\nTest 2: Cleanup")
    test_cleanup()
    
    print("\n" + "="*60)
    print("✅ ALL SMOKE TESTS PASSED!")
    print("="*60)
