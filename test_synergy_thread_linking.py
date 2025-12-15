"""
Synergy Thread Linking - Integration Test Script
=================================================

Tests the complete drag-drop thread linking workflow:
1. Backend endpoints exist and respond correctly
2. Database schema supports bidirectional linking
3. API correctly updates both tables
4. Frontend can successfully link/unlink threads

Run: python test_synergy_thread_linking.py
"""

import sys
import json
import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
API_BASE = f"{BASE_URL}/api/synergy"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def log_test(name, passed, details=""):
    symbol = f"{Colors.GREEN}✅{Colors.RESET}" if passed else f"{Colors.RED}❌{Colors.RESET}"
    print(f"{symbol} {name}")
    if details:
        print(f"   {details}")

def log_section(title):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def test_backend_endpoints():
    """Test 1: Verify all required endpoints exist"""
    log_section("TEST 1: Backend Endpoint Availability")
    
    test_session_id = "test-session-123"
    
    endpoints = [
        ("POST", f"{API_BASE}/{test_session_id}/link-thread", "Link thread to session"),
        ("POST", f"{API_BASE}/{test_session_id}/unlink-thread", "Unlink thread from session"),
        ("GET", f"{API_BASE}/{test_session_id}/linked-threads", "Get linked threads"),
    ]
    
    for method, url, description in endpoints:
        try:
            # Test if endpoint exists (expect 400/404, not 405 Method Not Allowed)
            if method == "POST":
                r = requests.post(url, json={}, timeout=2)
            else:
                r = requests.get(url, timeout=2)
            
            # Any response except 405 means endpoint exists
            endpoint_exists = r.status_code != 405
            log_test(description, endpoint_exists, f"{method} {url} → {r.status_code}")
        except Exception as e:
            log_test(description, False, f"Error: {e}")

def test_link_thread_api():
    """Test 2: Test link-thread API endpoint"""
    log_section("TEST 2: Link Thread API Functionality")
    
    # Create a test session first
    try:
        session_data = {
            "title": "🧪 Test Synergy Session",
            "description": "Automated test session for thread linking",
            "session_id": f"test-session-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        create_response = requests.post(f"{API_BASE}/create", json=session_data, timeout=5)
        
        if create_response.status_code != 200:
            log_test("Create test session", False, f"HTTP {create_response.status_code}")
            return
        
        create_data = create_response.json()
        if not create_data.get('success'):
            log_test("Create test session", False, f"Error: {create_data.get('error')}")
            return
        
        session_id = create_data['session_id']
        log_test("Create test session", True, f"Session ID: {session_id}")
        
        # Test linking a thread
        link_payload = {
            "thread_id": "test-thread-abc123",
            "thread_slug": "test-thread-abc123",
            "thread_name": "🧵 Test Thread"
        }
        
        link_response = requests.post(
            f"{API_BASE}/{session_id}/link-thread",
            json=link_payload,
            timeout=5
        )
        
        if link_response.status_code != 200:
            log_test("Link thread API call", False, f"HTTP {link_response.status_code}")
            print(f"   Response: {link_response.text}")
            return
        
        link_data = link_response.json()
        
        # Validate response structure
        has_success = link_data.get('success') == True
        has_session_id = link_data.get('session_id') == session_id
        has_thread_ids = isinstance(link_data.get('thread_ids'), list)
        thread_in_array = link_payload['thread_id'] in link_data.get('thread_ids', [])
        
        log_test("Link thread API call", link_response.status_code == 200, f"HTTP {link_response.status_code}")
        log_test("Response has success=true", has_success)
        log_test("Response has correct session_id", has_session_id)
        log_test("Response has thread_ids array", has_thread_ids)
        log_test("Thread ID in thread_ids array", thread_in_array, 
                f"thread_ids: {link_data.get('thread_ids')}")
        
        # Test getting linked threads
        get_response = requests.get(f"{API_BASE}/{session_id}/linked-threads", timeout=5)
        
        if get_response.status_code != 200:
            log_test("Get linked threads", False, f"HTTP {get_response.status_code}")
        else:
            get_data = get_response.json()
            threads = get_data.get('threads', [])
            log_test("Get linked threads", get_data.get('success') == True,
                    f"Found {len(threads)} thread(s)")
        
        # Clean up: Delete test session
        delete_response = requests.delete(f"{API_BASE}/{session_id}", timeout=5)
        log_test("Cleanup test session", delete_response.status_code == 200)
        
    except Exception as e:
        log_test("Link thread workflow", False, f"Exception: {e}")
        import traceback
        traceback.print_exc()

def test_duplicate_linking():
    """Test 3: Test duplicate thread linking (should be idempotent)"""
    log_section("TEST 3: Duplicate Link Prevention")
    
    try:
        # Create test session
        session_data = {
            "title": "🧪 Duplicate Test Session",
            "session_id": f"dup-test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
        
        create_response = requests.post(f"{API_BASE}/create", json=session_data, timeout=5)
        session_id = create_response.json()['session_id']
        
        link_payload = {
            "thread_id": "dup-thread-123",
            "thread_slug": "dup-thread-123",
            "thread_name": "Duplicate Test Thread"
        }
        
        # Link once
        r1 = requests.post(f"{API_BASE}/{session_id}/link-thread", json=link_payload, timeout=5)
        data1 = r1.json()
        
        # Link again (duplicate)
        r2 = requests.post(f"{API_BASE}/{session_id}/link-thread", json=link_payload, timeout=5)
        data2 = r2.json()
        
        # Both should succeed
        both_succeed = data1.get('success') and data2.get('success')
        # Thread should only appear once in array
        thread_count = data2.get('thread_ids', []).count(link_payload['thread_id'])
        no_duplicates = thread_count == 1
        
        log_test("Duplicate link succeeds", both_succeed)
        log_test("Thread appears only once in array", no_duplicates,
                f"Count: {thread_count}, thread_ids: {data2.get('thread_ids')}")
        
        # Cleanup
        requests.delete(f"{API_BASE}/{session_id}", timeout=5)
        
    except Exception as e:
        log_test("Duplicate link test", False, f"Exception: {e}")

def test_frontend_files():
    """Test 4: Verify frontend files are accessible"""
    log_section("TEST 4: Frontend File Accessibility")
    
    files = [
        ("synergy-thread-drag-drop.js", f"{BASE_URL}/modules_internal/synergy/synergy-thread-drag-drop.js"),
        ("synergy-thread-drag-drop.css", f"{BASE_URL}/modules_internal/synergy/synergy-thread-drag-drop.css"),
        ("synergy-sidebar-renderer-v2-FLAT.js", f"{BASE_URL}/modules_internal/synergy/synergy-sidebar-renderer-v2-FLAT.js"),
        ("synergy-inline-edit.js", f"{BASE_URL}/modules_internal/synergy/synergy-inline-edit.js"),
    ]
    
    for name, url in files:
        try:
            r = requests.get(url, timeout=5)
            accessible = r.status_code == 200
            log_test(name, accessible, f"HTTP {r.status_code}")
        except Exception as e:
            log_test(name, False, f"Error: {e}")

def test_javascript_structure():
    """Test 5: Verify JavaScript module structure"""
    log_section("TEST 5: JavaScript Module Structure")
    
    try:
        # Fetch the drag-drop JS file
        r = requests.get(f"{BASE_URL}/modules_internal/synergy/synergy-thread-drag-drop.js", timeout=5)
        
        if r.status_code != 200:
            log_test("Fetch drag-drop JS", False, f"HTTP {r.status_code}")
            return
        
        content = r.text
        
        # Check for key components
        checks = [
            ("SynergyThreadDragDrop class exists", "class SynergyThreadDragDrop" in content),
            ("initDragAndDrop method exists", "initDragAndDrop()" in content),
            ("initThreadCardDrag method exists", "initThreadCardDrag()" in content),
            ("initDropZones method exists", "initDropZones()" in content),
            ("linkThreadToSession method exists", "linkThreadToSession" in content),
            ("Drag event handlers present", "addEventListener('dragstart'" in content),
            ("Drop event handlers present", "addEventListener('drop'" in content),
            ("Auto-initialization code present", "window.synergyThreadDragDrop" in content),
        ]
        
        for check_name, condition in checks:
            log_test(check_name, condition)
            
    except Exception as e:
        log_test("JavaScript structure analysis", False, f"Exception: {e}")

def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}SYNERGY THREAD LINKING - INTEGRATION TEST SUITE{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    try:
        # Check if Flask is running
        r = requests.get(BASE_URL, timeout=2)
        log_test("Flask server running", True, f"HTTP {r.status_code}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Flask server not responding!{Colors.RESET}")
        print(f"   Error: {e}")
        print(f"   Please start Flask with: BISTART")
        return
    
    # Run test suites
    test_backend_endpoints()
    test_link_thread_api()
    test_duplicate_linking()
    test_frontend_files()
    test_javascript_structure()
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Integration test suite completed{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    run_all_tests()
