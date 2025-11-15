"""
Test empty thread save functionality

Verifies that the /api/threads/save endpoint now accepts threads with no messages.
This was previously causing 400 errors when the frontend created new threads.
"""

import requests
import json

API_BASE = "http://localhost:5001"

def test_empty_thread_save():
    """Test saving a thread with no messages (initial creation)"""
    
    print("Testing empty thread save...")
    print("=" * 70)
    
    # Create a thread with no messages (like the frontend does)
    thread_data = {
        "thread_id": "test-agent-3_test-session-123",
        "title": "Test Empty Thread",
        "messages": [],  # Empty messages array
        "agent": "agent-3",
        "user_id": 14,
        "location": "agent-3"
    }
    
    print(f"Sending request to {API_BASE}/api/threads/save")
    print(f"Payload: {json.dumps(thread_data, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/api/threads/save",
            json=thread_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print()
        
        if response.status_code == 200:
            print("[PASS] SUCCESS: Empty thread saved successfully!")
            result = response.json()
            print(f"   Thread ID: {result.get('thread_id')}")
            print(f"   Message count: {result.get('message_count', 0)}")
            return True
        else:
            print(f"[FAIL] FAILED: Got {response.status_code} status code")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        return False

def test_thread_with_messages():
    """Test saving a thread with messages (normal operation)"""
    
    print("\nTesting thread with messages...")
    print("=" * 70)
    
    # Create a thread with messages
    thread_data = {
        "thread_id": "test-agent-3_test-session-456",
        "title": "Test Thread With Messages",
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
        "agent": "agent-3",
        "user_id": 14,
        "location": "agent-3"
    }
    
    print(f"Sending request to {API_BASE}/api/threads/save")
    print(f"Payload: {json.dumps(thread_data, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/api/threads/save",
            json=thread_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        print()
        
        if response.status_code == 200:
            print("[PASS] SUCCESS: Thread with messages saved successfully!")
            result = response.json()
            print(f"   Thread ID: {result.get('thread_id')}")
            print(f"   Message count: {result.get('message_count', 0)}")
            return True
        else:
            print(f"[FAIL] FAILED: Got {response.status_code} status code")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] ERROR: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EMPTY THREAD SAVE TEST")
    print("=" * 70)
    print()
    
    # Test 1: Empty thread
    test1_passed = test_empty_thread_save()
    
    # Test 2: Thread with messages
    test2_passed = test_thread_with_messages()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Test 1 (Empty thread):        {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"Test 2 (Thread with messages): {'[PASS]' if test2_passed else '[FAIL]'}")
    print()
    
    if test1_passed and test2_passed:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("Empty threads can now be saved successfully.")
    else:
        print("[WARNING] SOME TESTS FAILED")
        print("Check the error messages above for details.")
    
    print("=" * 70)
