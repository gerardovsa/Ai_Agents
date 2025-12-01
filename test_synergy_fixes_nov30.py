"""
Test Script for Synergy Backend Fixes (Nov 30, 2025)
=====================================================

Tests all 4 critical fixes:
1. synergy_get_session - SQL placeholder fix
2. synergy_update_task - Request validation fix
3. synergy_add_document - normalize_documents error handling
4. synergy_search_sessions - New endpoint implementation

Usage:
    python test_synergy_fixes_nov30.py
"""

import requests
import json
from datetime import datetime

API_BASE = "http://localhost:5001/api/synergy"

def print_test(test_name, passed, details=""):
    """Print formatted test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_get_session():
    """Test Fix #1: synergy_get_session SQL placeholder fix"""
    print("\n" + "="*60)
    print("TEST 1: synergy_get_session (SQL Placeholder Fix)")
    print("="*60)
    
    # First, get a list of sessions to find a valid session_id
    try:
        response = requests.get(f"{API_BASE}/list", timeout=5)
        if response.status_code == 200:
            sessions = response.json()
            if sessions and len(sessions) > 0:
                session_id = sessions[0].get('session_id')
                
                # Now test get_session with the valid ID
                response = requests.get(f"{API_BASE}/{session_id}", timeout=5)
                
                if response.status_code == 200:
                    session = response.json()
                    print_test(
                        "Get Session with SQL placeholders",
                        True,
                        f"Retrieved session: {session.get('title', 'Unknown')}"
                    )
                    return True
                else:
                    print_test(
                        "Get Session",
                        False,
                        f"Status {response.status_code}: {response.text[:200]}"
                    )
                    return False
            else:
                print_test(
                    "Get Session",
                    False,
                    "No sessions available for testing. Create a session first."
                )
                return False
        else:
            print_test(
                "Get Session (list)",
                False,
                f"Failed to list sessions: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_test("Get Session", False, f"Exception: {str(e)}")
        return False

def test_update_task_validation():
    """Test Fix #2: synergy_update_task request validation"""
    print("\n" + "="*60)
    print("TEST 2: synergy_update_task (Request Validation)")
    print("="*60)
    
    # Test with invalid request (should return 400 with validation message)
    try:
        # First, create a test task to update
        response = requests.get(f"{API_BASE}/list", timeout=5)
        if response.status_code != 200:
            print_test(
                "Update Task Validation",
                False,
                "Could not list sessions to find tasks"
            )
            return False
        
        sessions = response.json()
        if not sessions:
            print_test(
                "Update Task Validation",
                False,
                "No sessions available for testing"
            )
            return False
        
        # Get first session with milestones
        session_id = sessions[0].get('session_id')
        response = requests.get(f"{API_BASE}/{session_id}", timeout=5)
        
        if response.status_code == 200:
            session = response.json()
            milestones = session.get('milestones', [])
            
            if milestones and milestones[0].get('tasks'):
                task_id = milestones[0]['tasks'][0].get('task_id')
                
                # Test 1: Empty request body (should fail validation)
                response = requests.patch(
                    f"{API_BASE}/task/{task_id}",
                    json=None,
                    timeout=5
                )
                
                if response.status_code == 400:
                    error_msg = response.json().get('error', '')
                    if 'JSON object' in error_msg or 'Request body' in error_msg:
                        print_test(
                            "Update Task - Empty body validation",
                            True,
                            "Correctly rejected empty request body"
                        )
                    else:
                        print_test(
                            "Update Task - Empty body validation",
                            False,
                            f"Wrong error message: {error_msg}"
                        )
                        return False
                else:
                    print_test(
                        "Update Task - Empty body validation",
                        False,
                        f"Expected 400, got {response.status_code}"
                    )
                    return False
                
                # Test 2: Valid update (should succeed)
                response = requests.patch(
                    f"{API_BASE}/task/{task_id}",
                    json={"priority": "high"},
                    timeout=5
                )
                
                if response.status_code == 200:
                    print_test(
                        "Update Task - Valid request",
                        True,
                        "Successfully updated task with valid data"
                    )
                    return True
                else:
                    print_test(
                        "Update Task - Valid request",
                        False,
                        f"Status {response.status_code}: {response.text[:200]}"
                    )
                    return False
            else:
                print_test(
                    "Update Task Validation",
                    False,
                    "No tasks found in session for testing"
                )
                return False
        else:
            print_test(
                "Update Task Validation",
                False,
                f"Failed to get session: {response.status_code}"
            )
            return False
            
    except Exception as e:
        print_test("Update Task Validation", False, f"Exception: {str(e)}")
        return False

def test_add_document_error_handling():
    """Test Fix #3: synergy_add_document normalize_documents error handling"""
    print("\n" + "="*60)
    print("TEST 3: synergy_add_document (Error Handling)")
    print("="*60)
    
    try:
        # Get a session to test with
        response = requests.get(f"{API_BASE}/list", timeout=5)
        if response.status_code != 200:
            print_test(
                "Add Document Error Handling",
                False,
                "Could not list sessions"
            )
            return False
        
        sessions = response.json()
        if not sessions:
            print_test(
                "Add Document Error Handling",
                False,
                "No sessions available for testing"
            )
            return False
        
        session_id = sessions[0].get('session_id')
        
        # Test 1: Add valid document
        valid_doc = {
            "session_id": session_id,
            "title": "Test Document Fix",
            "url": "https://docs.google.com/document/d/test123",
            "type": "google_doc"
        }
        
        response = requests.post(
            f"{API_BASE}/document",
            json=valid_doc,
            timeout=5
        )
        
        if response.status_code == 200:
            print_test(
                "Add Document - Valid input",
                True,
                "Successfully added document with valid data"
            )
        else:
            print_test(
                "Add Document - Valid input",
                False,
                f"Status {response.status_code}: {response.text[:200]}"
            )
            return False
        
        # Test 2: Update session with invalid document format (should not crash)
        # This tests the normalize_documents error handling in update_session
        response = requests.patch(
            f"{API_BASE}/{session_id}",
            json={
                "documents": "invalid_string_instead_of_array"  # Wrong type
            },
            timeout=5
        )
        
        # Should either succeed with normalization or return error (not crash with 500)
        if response.status_code in [200, 400]:
            print_test(
                "Add Document - Invalid format handling",
                True,
                f"Handled invalid document format gracefully (status {response.status_code})"
            )
            return True
        else:
            print_test(
                "Add Document - Invalid format handling",
                False,
                f"Unexpected status {response.status_code}: {response.text[:200]}"
            )
            return False
            
    except Exception as e:
        print_test("Add Document Error Handling", False, f"Exception: {str(e)}")
        return False

def test_search_sessions():
    """Test Fix #4: synergy_search_sessions new endpoint"""
    print("\n" + "="*60)
    print("TEST 4: synergy_search_sessions (New Endpoint)")
    print("="*60)
    
    try:
        # Test 1: Search by query
        response = requests.get(
            f"{API_BASE}/search",
            params={"query": "test"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_test(
                    "Search Sessions - By query",
                    True,
                    f"Found {result.get('count', 0)} sessions matching 'test'"
                )
            else:
                print_test(
                    "Search Sessions - By query",
                    False,
                    "Response success=false"
                )
                return False
        else:
            print_test(
                "Search Sessions - By query",
                False,
                f"Status {response.status_code}: {response.text[:200]}"
            )
            return False
        
        # Test 2: Search by platform
        response = requests.get(
            f"{API_BASE}/search",
            params={"platform": "gmail"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_test(
                    "Search Sessions - By platform",
                    True,
                    f"Found {result.get('count', 0)} sessions with Gmail"
                )
            else:
                print_test(
                    "Search Sessions - By platform",
                    False,
                    "Response success=false"
                )
                return False
        else:
            print_test(
                "Search Sessions - By platform",
                False,
                f"Status {response.status_code}: {response.text[:200]}"
            )
            return False
        
        # Test 3: Search with filters
        response = requests.get(
            f"{API_BASE}/search",
            params={
                "query": "email",
                "priority": "high",
                "column": "in_progress"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print_test(
                    "Search Sessions - With filters",
                    True,
                    f"Found {result.get('count', 0)} sessions matching filters"
                )
                return True
            else:
                print_test(
                    "Search Sessions - With filters",
                    False,
                    "Response success=false"
                )
                return False
        else:
            print_test(
                "Search Sessions - With filters",
                False,
                f"Status {response.status_code}: {response.text[:200]}"
            )
            return False
        
    except Exception as e:
        print_test("Search Sessions", False, f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🧪 SYNERGY BACKEND FIXES TEST SUITE (Nov 30, 2025)")
    print("="*70)
    print(f"\nAPI Base URL: {API_BASE}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "get_session": test_get_session(),
        "update_task": test_update_task_validation(),
        "add_document": test_add_document_error_handling(),
        "search_sessions": test_search_sessions()
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"RESULT: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    if passed == total:
        print("\n🎉 SUCCESS! All Synergy backend fixes are working correctly!")
        return 0
    else:
        print(f"\n⚠️  WARNING: {total - passed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
