"""
Verify Current Thread API and Database Schema

This script checks:
1. Database schema has all required columns
2. API endpoints work correctly
3. Data flows properly through create/update/list operations
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:5001"
USER_ID = 14

def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_create_thread():
    """Test thread creation"""
    print_section("TEST 1: Create Thread")
    
    response = requests.post(
        f"{API_BASE_URL}/api/threads/create",
        json={
            "user_id": USER_ID,
            "title": "Schema Verification Thread",
            "location": "prime"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200 and data.get('success'):
        thread_data = data.get('data', {}).get('thread', data.get('thread', {}))
        thread_id = thread_data.get('id')
        print(f"\n✅ Thread created successfully: {thread_id}")
        return thread_id
    else:
        print(f"\n❌ Failed to create thread")
        return None

def test_update_workflow(thread_id):
    """Test workflow linkage"""
    print_section("TEST 2: Link Workflow to Thread")
    
    response = requests.patch(
        f"{API_BASE_URL}/api/threads/{thread_id}/update",
        json={
            "workflow_id": "test-workflow-456",
            "workflow_name": "Test Workflow ABC"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ Workflow linked successfully")
        return True
    else:
        print(f"\n❌ Failed to link workflow")
        return False

def test_update_synergy(thread_id):
    """Test Synergy linkage"""
    print_section("TEST 3: Link Synergy to Thread")
    
    response = requests.patch(
        f"{API_BASE_URL}/api/threads/{thread_id}/update",
        json={
            "synergy_card_id": "sess_test_verification_123",
            "synergy_card_name": "Test Synergy Session"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ Synergy linked successfully")
        return True
    else:
        print(f"\n❌ Failed to link Synergy")
        return False

def test_list_threads(thread_id):
    """Test thread listing and verify fields"""
    print_section("TEST 4: List Threads and Verify Data")
    
    response = requests.get(f"{API_BASE_URL}/api/threads/list?user_id={USER_ID}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ Failed to list threads: {response.text}")
        return False
    
    data = response.json()
    threads = data.get('data', {}).get('threads', data.get('threads', []))
    
    print(f"Total threads returned: {len(threads)}")
    
    # Find our test thread
    test_thread = None
    for thread in threads:
        if thread.get('id') == thread_id:
            test_thread = thread
            break
    
    if not test_thread:
        print(f"\n❌ Test thread {thread_id} not found in list!")
        print(f"\nFirst thread in list (for debugging):")
        if threads:
            print(json.dumps(threads[0], indent=2))
        return False
    
    print(f"\n✅ Found test thread in list")
    print(f"\nThread data:")
    print(json.dumps(test_thread, indent=2))
    
    # Verify fields
    print(f"\n{'='*80}")
    print("  FIELD VERIFICATION")
    print(f"{'='*80}")
    
    checks = {
        'workflow_id': 'test-workflow-456',
        'workflow_name': 'Test Workflow ABC',
        'synergy_card_id': 'sess_test_verification_123',
        'synergy_card_name': 'Test Synergy Session'
    }
    
    all_passed = True
    for field, expected in checks.items():
        actual = test_thread.get(field)
        status = "✅" if actual == expected else "❌"
        print(f"  {status} {field:20} = {actual} (expected: {expected})")
        if actual != expected:
            all_passed = False
    
    return all_passed

def test_move_thread(thread_id):
    """Test moving thread between locations"""
    print_section("TEST 5: Move Thread to Agent-2")
    
    response = requests.patch(
        f"{API_BASE_URL}/api/threads/{thread_id}/update",
        json={
            "location": "agent-2"
        }
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    if response.status_code == 200:
        print(f"\n✅ Thread moved successfully")
        return True
    else:
        print(f"\n❌ Failed to move thread")
        return False

def test_verify_pills_persist(thread_id):
    """Verify pills persist after move"""
    print_section("TEST 6: Verify Pills Persist After Move")
    
    response = requests.get(f"{API_BASE_URL}/api/threads/list?user_id={USER_ID}")
    
    if response.status_code != 200:
        print(f"❌ Failed to list threads")
        return False
    
    data = response.json()
    threads = data.get('data', {}).get('threads', data.get('threads', []))
    
    test_thread = None
    for thread in threads:
        if thread.get('id') == thread_id:
            test_thread = thread
            break
    
    if not test_thread:
        print(f"❌ Thread not found")
        return False
    
    location = test_thread.get('location')
    workflow_id = test_thread.get('workflow_id')
    synergy_id = test_thread.get('synergy_card_id')
    
    print(f"Location: {location}")
    print(f"Workflow ID: {workflow_id}")
    print(f"Synergy ID: {synergy_id}")
    
    if location == 'agent-2' and workflow_id == 'test-workflow-456' and synergy_id == 'sess_test_verification_123':
        print(f"\n✅ Pills persisted after location change!")
        return True
    else:
        print(f"\n❌ Pills were lost during move")
        return False

def cleanup(thread_id):
    """Clean up test thread"""
    print_section("CLEANUP")
    
    response = requests.delete(f"{API_BASE_URL}/api/threads/{thread_id}")
    
    if response.status_code == 200:
        print(f"✅ Test thread deleted: {thread_id}")
    else:
        print(f"⚠️  Failed to delete thread (may need manual cleanup)")

def main():
    print(f"\n{'='*80}")
    print(f"  THREAD API & SCHEMA VERIFICATION")
    print(f"  Testing: {API_BASE_URL}")
    print(f"  User ID: {USER_ID}")
    print(f"{'='*80}")
    
    # Run tests
    results = {}
    
    # Test 1: Create
    thread_id = test_create_thread()
    results['create'] = thread_id is not None
    
    if not thread_id:
        print("\n❌ Cannot continue without thread ID")
        return
    
    # Test 2: Link Workflow
    results['workflow'] = test_update_workflow(thread_id)
    
    # Test 3: Link Synergy
    results['synergy'] = test_update_synergy(thread_id)
    
    # Test 4: List and Verify
    results['list_verify'] = test_list_threads(thread_id)
    
    # Test 5: Move Thread
    results['move'] = test_move_thread(thread_id)
    
    # Test 6: Verify Pills Persist
    results['pills_persist'] = test_verify_pills_persist(thread_id)
    
    # Cleanup
    cleanup(thread_id)
    
    # Summary
    print(f"\n{'='*80}")
    print(f"  TEST SUMMARY")
    print(f"{'='*80}\n")
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {test}")
    
    passed_count = sum(1 for p in results.values() if p)
    total = len(results)
    
    print(f"\n  Results: {passed_count}/{total} tests passed\n")
    
    if passed_count == total:
        print(f"  🎉 ALL TESTS PASSED - Schema and API working correctly!\n")
    else:
        print(f"  ⚠️  SOME TESTS FAILED - Review errors above\n")
    
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
