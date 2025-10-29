"""
Universal Task Sync Testing Suite
==================================
Comprehensive tests for task sync functionality across:
- Google Tasks
- Microsoft To Do
- Google Calendar

Usage:
    python test_task_sync.py

Prerequisites:
        - synergy_backend.py running on port 5001

Required dependencies:
    - requests
"""

BASE_URL = 'http://localhost:5001'
    - Database migration completed
    - Google/Microsoft OAuth credentials configured
"""

import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = 'http://localhost:4000'
TEST_USER_EMAIL = 'test@example.com'

class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_test(test_name):
    """Print test name"""
    print(f"{Colors.BOLD}Testing: {test_name}{Colors.END}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}[OK] {message}{Colors.END}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}[ERROR] {message}{Colors.END}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.YELLOW}[INFO] {message}{Colors.END}")


# ============================================
# TEST 1: Check Server Health
# ============================================

def test_server_health():
    """Test server and sync service health"""
    print_section("TEST 1: Server Health Check")
    
    # Check main server
    print_test("Main server health")
    try:
        response = requests.get(f'{BASE_URL}/health')
        if response.status_code == 200:
            print_success("Main server is healthy")
        else:
            print_error(f"Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to server. Is synergy_backend.py running?")
        return False
    
    # Check sync service health
    print_test("Sync service health")
    try:
        response = requests.get(f'{BASE_URL}/api/sync/health')
        if response.status_code == 200:
            data = response.json()
            print_success("Sync service is healthy")
            print_info(f"Tools available: {json.dumps(data.get('tools_available', {}), indent=2)}")
            return True
        else:
            print_error(f"Sync service returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Sync service check failed: {e}")
        return False


# ============================================
# TEST 2: Create Kanban Card
# ============================================

def test_create_kanban_card():
    """Test creating a Kanban card"""
    print_section("TEST 2: Create Kanban Card")
    
    print_test("Creating test Kanban card")
    
    card_data = {
        'title': 'Test Task - Universal Sync',
        'description': 'This is a test task for universal sync functionality',
        'priority': 'high',
        'status': 'active',
        'kanban_column': 'backlog',
        'due_date': (datetime.now() + timedelta(days=3)).isoformat(),
        'tags': ['test', 'sync', 'automation'],
        'assignees': ['Test User'],
        'checklist': [
            {'item': 'Test Google Tasks sync', 'completed': False},
            {'item': 'Test Microsoft To Do sync', 'completed': False},
            {'item': 'Test Google Calendar sync', 'completed': False}
        ],
        'reminder_date': (datetime.now() + timedelta(days=2)).isoformat(),
        'reminder_minutes_before': 30,
        'project_name': 'Universal Sync Testing'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/sessions/create', json=card_data)
        if response.status_code == 201:
            data = response.json()
            session_id = data.get('session_id')
            print_success(f"Kanban card created: {session_id}")
            print_info(f"Card data: {json.dumps(data, indent=2)}")
            return session_id
        else:
            print_error(f"Failed to create card: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


# ============================================
# TEST 3: Sync to Google Tasks
# ============================================

def test_sync_to_google_tasks(session_id):
    """Test syncing to Google Tasks"""
    print_section("TEST 3: Sync to Google Tasks")
    
    if not session_id:
        print_error("No session_id provided, skipping test")
        return None
    
    print_test(f"Syncing session {session_id} to Google Tasks")
    
    sync_data = {
        'session_id': session_id,
        'user_email': TEST_USER_EMAIL
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/sync/google-tasks/create', json=sync_data)
        if response.status_code == 201:
            data = response.json()
            print_success("Synced to Google Tasks successfully")
            print_info(f"Google Task ID: {data.get('google_task_id')}")
            if data.get('calendar_event_id'):
                print_info(f"Calendar Event ID: {data.get('calendar_event_id')} (for reminder)")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return data.get('google_task_id')
        else:
            print_error(f"Sync failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


# ============================================
# TEST 4: Sync to Microsoft To Do
# ============================================

def test_sync_to_microsoft_todo(session_id):
    """Test syncing to Microsoft To Do"""
    print_section("TEST 4: Sync to Microsoft To Do")
    
    if not session_id:
        print_error("No session_id provided, skipping test")
        return None
    
    print_test(f"Syncing session {session_id} to Microsoft To Do")
    
    sync_data = {
        'session_id': session_id,
        'user_email': TEST_USER_EMAIL
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/sync/microsoft-todo/create', json=sync_data)
        if response.status_code == 201:
            data = response.json()
            print_success("Synced to Microsoft To Do successfully")
            print_info(f"Microsoft Task ID: {data.get('microsoft_todo_id')}")
            print_info(f"Response: {json.dumps(data, indent=2)}")
            return data.get('microsoft_todo_id')
        else:
            print_error(f"Sync failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


# ============================================
# TEST 5: Bidirectional Sync
# ============================================

def test_bidirectional_sync(session_id):
    """Test bidirectional sync to all platforms"""
    print_section("TEST 5: Bidirectional Sync")
    
    if not session_id:
        print_error("No session_id provided, skipping test")
        return False
    
    print_test(f"Bidirectional sync for session {session_id}")
    
    sync_data = {
        'user_email': TEST_USER_EMAIL,
        'platforms': ['google_tasks', 'microsoft_todo', 'google_calendar']
    }
    
    try:
        response = requests.post(f'{BASE_URL}/api/sync/bidirectional/{session_id}', json=sync_data)
        if response.status_code == 200:
            data = response.json()
            print_success("Bidirectional sync completed")
            print_info(f"Message: {data.get('message')}")
            
            for platform, result in data.get('synced_platforms', {}).items():
                if result.get('success'):
                    print_success(f"  {platform}: {result.get('task_id') or result.get('event_id')}")
                else:
                    print_error(f"  {platform}: {result.get('error')}")
            
            return data.get('success', False)
        else:
            print_error(f"Sync failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Exception: {e}")
        return False


# ============================================
# TEST 6: Get Sync Status
# ============================================

def test_get_sync_status(session_id):
    """Test getting sync status"""
    print_section("TEST 6: Get Sync Status")
    
    if not session_id:
        print_error("No session_id provided, skipping test")
        return None
    
    print_test(f"Getting sync status for session {session_id}")
    
    try:
        response = requests.get(f'{BASE_URL}/api/sync/status/{session_id}')
        if response.status_code == 200:
            data = response.json()
            print_success("Sync status retrieved")
            print_info(f"Session ID: {data.get('session_id')}")
            
            for platform, status in data.get('platforms', {}).items():
                if status.get('synced'):
                    print_success(f"  {platform}: Synced (ID: {status.get('task_id')}, Last: {status.get('last_sync')})")
                else:
                    print_info(f"  {platform}: Not synced")
            
            return data
        else:
            print_error(f"Failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


# ============================================
# TEST 7: List Synced Tasks
# ============================================

def test_list_synced_tasks():
    """Test listing all synced tasks"""
    print_section("TEST 7: List Synced Tasks")
    
    print_test("Getting list of all synced tasks")
    
    try:
        response = requests.get(f'{BASE_URL}/api/sync/list')
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {data.get('total', 0)} synced tasks")
            
            for task in data.get('tasks', [])[:5]:  # Show first 5
                print_info(f"  • {task.get('title')} (ID: {task.get('session_id')})")
                for platform, status in task.get('platforms', {}).items():
                    print_info(f"    - {platform}: {status.get('sync_status')}")
            
            return data
        else:
            print_error(f"Failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


# ============================================
# TEST 8: Recurring Task Sync
# ============================================

def test_recurring_task_sync():
    """Test syncing a recurring task"""
    print_section("TEST 8: Recurring Task Sync")
    
    print_test("Creating recurring task")
    
    card_data = {
        'title': 'Weekly Standup Meeting',
        'description': 'Recurring team standup every Monday and Friday',
        'priority': 'medium',
        'status': 'active',
        'kanban_column': 'in_progress',
        'due_date': datetime.now().isoformat(),
        'recurrence_type': 'weekly',
        'recurrence_pattern': json.dumps({
            'interval': 1,
            'daysOfWeek': ['monday', 'friday']
        }),
        'reminder_minutes_before': 15,
        'project_name': 'Recurring Task Test'
    }
    
    try:
        # Create card
        response = requests.post(f'{BASE_URL}/api/sessions/create', json=card_data)
        if response.status_code != 201:
            print_error(f"Failed to create card: {response.status_code}")
            return None
        
        session_id = response.json().get('session_id')
        print_success(f"Recurring task created: {session_id}")
        
        # Sync to all platforms
        sync_data = {
            'user_email': TEST_USER_EMAIL,
            'platforms': ['google_tasks', 'microsoft_todo', 'google_calendar']
        }
        
        response = requests.post(f'{BASE_URL}/api/sync/bidirectional/{session_id}', json=sync_data)
        if response.status_code == 200:
            data = response.json()
            print_success("Recurring task synced to all platforms")
            
            # Check which platforms support recurrence
            for platform, result in data.get('synced_platforms', {}).items():
                if result.get('success'):
                    print_success(f"  {platform}: Synced successfully")
                    if platform == 'google_tasks':
                        print_info(f"    Note: Google Tasks gets single task with recurrence note")
                    elif platform == 'microsoft_todo':
                        print_info(f"    Note: Microsoft To Do gets native recurring task")
                    elif platform == 'google_calendar':
                        print_info(f"    Note: Google Calendar gets RRULE recurring event")
                else:
                    print_error(f"  {platform}: {result.get('error')}")
            
            return session_id
        else:
            print_error(f"Sync failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Exception: {e}")
        return None


# ============================================
# MAIN TEST RUNNER
# ============================================

def run_all_tests():
    """Run all tests sequentially"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"UNIVERSAL TASK SYNC - COMPREHENSIVE TEST SUITE")
    print(f"{'='*60}{Colors.END}\n")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Test User: {TEST_USER_EMAIL}")
    print_info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Test 1: Server Health
    if not test_server_health():
        print_error("\nServer health check failed. Exiting tests.")
        return
    
    time.sleep(1)
    
    # Test 2: Create Kanban Card
    session_id = test_create_kanban_card()
    if not session_id:
        print_error("\nFailed to create Kanban card. Exiting tests.")
        return
    
    time.sleep(1)
    
    # Test 3: Sync to Google Tasks
    google_task_id = test_sync_to_google_tasks(session_id)
    time.sleep(1)
    
    # Test 4: Sync to Microsoft To Do
    ms_todo_id = test_sync_to_microsoft_todo(session_id)
    time.sleep(1)
    
    # Test 5: Bidirectional Sync
    test_bidirectional_sync(session_id)
    time.sleep(1)
    
    # Test 6: Get Sync Status
    test_get_sync_status(session_id)
    time.sleep(1)
    
    # Test 7: List Synced Tasks
    test_list_synced_tasks()
    time.sleep(1)
    
    # Test 8: Recurring Task Sync
    test_recurring_task_sync()
    
    # Summary
    print_section("TEST SUMMARY")
    print_success("All tests completed!")
    print_info(f"Primary test session: {session_id}")
    if google_task_id:
        print_info(f"Google Task ID: {google_task_id}")
    if ms_todo_id:
        print_info(f"Microsoft To Do ID: {ms_todo_id}")
    
    print(f"\n{Colors.BOLD}Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}\n")


if __name__ == '__main__':
    run_all_tests()
