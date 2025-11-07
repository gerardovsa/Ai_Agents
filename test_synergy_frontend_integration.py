"""
Test Synergy Frontend-Backend Integration
==========================================
Tests all CRUD operations to verify database persistence.
"""

import requests
import json
import time

API_BASE = 'http://localhost:5001'

def test_create_session():
    """Test POST /api/synergy/create"""
    print("\n1. Testing CREATE SESSION...")
    
    session_data = {
        'title': 'Test Session from Frontend Integration',
        'description': 'Testing database persistence',
        'project_name': 'Test Project',
        'priority': 'high',
        'status': 'active',
        'kanban_column': 'in_progress',
        'tags': ['test', 'integration'],
        'documents': [],
        'links': [],
        'next_steps': [
            {'description': 'First step', 'completed': False},
            {'description': 'Second step', 'completed': False}
        ],
        'checklist': [
            {'item': 'Checklist item 1', 'completed': False}
        ]
    }
    
    response = requests.post(f'{API_BASE}/api/synergy/create', json=session_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            session_id = result.get('session_id')
            print(f"   CREATE: Session created with ID: {session_id}")
            return session_id
        else:
            print(f"   ERROR: {result.get('error')}")
            return None
    else:
        print(f"   ERROR: HTTP {response.status_code}")
        return None


def test_list_sessions():
    """Test GET /api/synergy/list"""
    print("\n2. Testing LIST SESSIONS...")
    
    response = requests.get(f'{API_BASE}/api/synergy/list')
    
    if response.status_code == 200:
        result = response.json()
        count = result.get('count', 0)
        print(f"   LIST: Found {count} sessions in database")
        return True
    else:
        print(f"   ERROR: HTTP {response.status_code}")
        return False


def test_get_session(session_id):
    """Test GET /api/synergy/<id>"""
    print(f"\n3. Testing GET SESSION: {session_id}...")
    
    response = requests.get(f'{API_BASE}/api/synergy/{session_id}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            session = result.get('session')
            print(f"   GET: Retrieved session: {session.get('title')}")
            print(f"        Column: {session.get('kanban_column')}")
            print(f"        Next steps: {len(session.get('next_steps', []))}")
            return session
        else:
            print(f"   ERROR: {result.get('error')}")
            return None
    else:
        print(f"   ERROR: HTTP {response.status_code}")
        return None


def test_update_session(session_id):
    """Test PATCH /api/synergy/<id> with nested updates object"""
    print(f"\n4. Testing UPDATE SESSION (toggle steps): {session_id}...")
    
    # First get current session
    session = test_get_session(session_id)
    if not session:
        return False
    
    # Toggle first step completion
    next_steps = session.get('next_steps', [])
    if next_steps:
        next_steps[0]['completed'] = True
    
    # Send update with nested 'updates' object (like frontend does)
    update_data = {
        'updates': {
            'next_steps': next_steps
        },
        'sync': {
            'google_tasks': False,
            'google_calendar': False
        }
    }
    
    response = requests.patch(f'{API_BASE}/api/synergy/{session_id}', json=update_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   UPDATE: Step toggled successfully")
            
            # Verify the change persisted
            updated_session = test_get_session(session_id)
            if updated_session:
                updated_steps = updated_session.get('next_steps', [])
                if updated_steps and updated_steps[0].get('completed'):
                    print(f"   VERIFY: Step completion persisted in database")
                    return True
                else:
                    print(f"   ERROR: Step completion not persisted")
                    return False
        else:
            print(f"   ERROR: {result.get('error')}")
            return False
    else:
        print(f"   ERROR: HTTP {response.status_code}")
        print(f"   Response: {response.text}")
        return False


def test_move_column(session_id):
    """Test PATCH /api/synergy/<id>/column"""
    print(f"\n5. Testing MOVE TO COLUMN: {session_id}...")
    
    move_data = {
        'kanban_column': 'review',
        'moved_by': 'Test Script'
    }
    
    response = requests.patch(f'{API_BASE}/api/synergy/{session_id}/column', json=move_data)
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   MOVE: Column updated to 'review'")
            
            # Verify the change
            session = test_get_session(session_id)
            if session and session.get('kanban_column') == 'review':
                print(f"   VERIFY: Column change persisted")
                return True
            else:
                print(f"   ERROR: Column change not persisted")
                return False
        else:
            print(f"   ERROR: {result.get('error')}")
            return False
    else:
        print(f"   ERROR: HTTP {response.status_code}")
        return False


def test_delete_session(session_id):
    """Test DELETE /api/synergy/<id>"""
    print(f"\n6. Testing DELETE SESSION: {session_id}...")
    
    response = requests.delete(f'{API_BASE}/api/synergy/{session_id}')
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"   DELETE: Session deleted")
            
            # Verify it's gone
            verify_response = requests.get(f'{API_BASE}/api/synergy/{session_id}')
            if verify_response.status_code == 404:
                print(f"   VERIFY: Session no longer exists in database")
                return True
            else:
                print(f"   ERROR: Session still exists after deletion")
                return False
        else:
            print(f"   ERROR: {result.get('error')}")
            return False
    else:
        print(f"   ERROR: HTTP {response.status_code}")
        return False


def main():
    print("=" * 70)
    print("SYNERGY FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 70)
    print("\nTesting all database persistence operations...")
    
    results = []
    
    # Test 1: Create
    session_id = test_create_session()
    results.append(('CREATE', session_id is not None))
    
    if not session_id:
        print("\n FAILED: Could not create session. Aborting tests.")
        return
    
    # Test 2: List
    results.append(('LIST', test_list_sessions()))
    
    # Test 3: Get
    session = test_get_session(session_id)
    results.append(('GET', session is not None))
    
    # Test 4: Update (toggle steps)
    results.append(('UPDATE', test_update_session(session_id)))
    
    # Test 5: Move column
    results.append(('MOVE', test_move_column(session_id)))
    
    # Test 6: Delete
    results.append(('DELETE', test_delete_session(session_id)))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for operation, success in results:
        status = "PASS" if success else "FAIL"
        symbol = "" if success else ""
        print(f"  {symbol} {operation:15} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print("\n" + "=" * 70)
    print(f"TOTAL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n ALL TESTS PASSED!")
        print("Frontend is fully connected to database!")
    else:
        print(f"\n {total_tests - passed_tests} test(s) failed")
    
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n ERROR: Could not connect to Flask server at http://localhost:5001")
        print("Please ensure the server is running with BISTART")
    except Exception as e:
        print(f"\n ERROR: {e}")
        import traceback
        traceback.print_exc()
