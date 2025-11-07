"""
Test Thread Features Backend Implementation
Tests all new endpoints and features
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def test_create_thread():
    """Test creating a new thread"""
    print("\n" + "="*60)
    print("TEST 1: Create New Thread")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/api/threads/create", json={
        'user_id': 1,
        'agent_id': 'prime',
        'title': 'Test Thread with Tags'
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    return data.get('thread', {}).get('id') if data.get('success') else None


def test_create_branch(parent_id):
    """Test creating a branched thread"""
    print("\n" + "="*60)
    print("TEST 2: Create Branched Thread")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/api/threads/create", json={
        'user_id': 1,
        'agent_id': 'prime',
        'title': 'Branched Thread',
        'parent_thread_id': parent_id,
        'branch_point_message_id': 'msg-123',
        'branch_name': 'Legal Analysis Branch'
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    return data.get('thread', {}).get('id') if data.get('success') else None


def test_save_thread_with_metadata(thread_id):
    """Test saving thread with all new metadata fields"""
    print("\n" + "="*60)
    print("TEST 3: Save Thread with Metadata")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/api/threads/save", json={
        'thread_id': thread_id,
        'title': 'Thread with Full Metadata',
        'messages': [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi there!'}
        ],
        'user_id': 1,
        'location': 'prime',
        'tags': ['feature', 'urgent', 'backend'],
        'synergy_card_id': 'session-test-123',
        'summary': 'This is a test thread with tags and synergy linking'
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    return data.get('success', False)


def test_synergy_sessions():
    """Test Synergy sessions endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Get Synergy Sessions")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/synergy/sessions")
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}...")
    
    return response.status_code == 200


def test_thread_assignment(thread_id):
    """Test thread assignment"""
    print("\n" + "="*60)
    print("TEST 5: Thread Assignment")
    print("="*60)
    
    response = requests.post(f"{BASE_URL}/api/thread-assignments/assign", json={
        'user_id': 1,
        'session_id': thread_id,
        'location': 'agent-1'
    })
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    return data.get('success', False)


if __name__ == '__main__':
    print("="*60)
    print("🔷 THREAD FEATURES BACKEND TEST SUITE")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print("Make sure the Flask server is running!")
    
    try:
        # Test 1: Create thread
        thread_id = test_create_thread()
        if not thread_id:
            print("\n❌ Failed to create thread - aborting tests")
            exit(1)
        
        # Test 2: Create branch
        branch_id = test_create_branch(thread_id)
        
        # Test 3: Save with metadata
        save_success = test_save_thread_with_metadata(thread_id)
        
        # Test 4: Synergy sessions
        synergy_success = test_synergy_sessions()
        
        # Test 5: Thread assignment
        assignment_success = test_thread_assignment(thread_id)
        
        # Summary
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"✅ Create Thread: {'PASS' if thread_id else 'FAIL'}")
        print(f"✅ Create Branch: {'PASS' if branch_id else 'FAIL'}")
        print(f"✅ Save with Metadata: {'PASS' if save_success else 'FAIL'}")
        print(f"✅ Synergy Sessions: {'PASS' if synergy_success else 'FAIL'}")
        print(f"✅ Thread Assignment: {'PASS' if assignment_success else 'FAIL'}")
        
        all_passed = all([thread_id, branch_id, save_success, synergy_success, assignment_success])
        
        if all_passed:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print("\n⚠️  SOME TESTS FAILED")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure Flask is running on port 5001")
        print("Run: BISTART")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
