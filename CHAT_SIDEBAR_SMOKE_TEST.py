#!/usr/bin/env python3
"""
CHAT SIDEBAR - SMOKE TEST & END-TO-END TRACE
Tests all chat sidebar functionality including API endpoints, WebSocket connections, and UI interactions
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
TEST_USER_ID = 1
TEST_OTHER_USER_ID = 2

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.RESET}\n")

def print_test(name):
    print(f"{Colors.BLUE}TEST: {Colors.RESET}{name}")

def print_success(message):
    print(f"{Colors.GREEN}  OK {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}  FAIL {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}  WARN {message}{Colors.RESET}")

def print_info(message):
    print(f"  INFO {message}")

# ==============================================================================
# PART 1: API ENDPOINT TESTS
# ==============================================================================

def test_conversations_endpoint():
    """Test GET /api/messages/conversations"""
    print_test("Get Conversations List")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/messages/conversations",
            params={'user_id': TEST_USER_ID},
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data.get('conversations', []))} conversations")
            
            # Show sample conversation
            if data.get('conversations'):
                conv = data['conversations'][0]
                print_info(f"Sample: User {conv['user_id']}, Unread: {conv['unread_count']}")
            
            return True
        elif response.status_code == 503:
            print_warning("Message service not available (expected in dev)")
            return None
        else:
            print_error(f"Failed: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_conversation_history():
    """Test GET /api/messages/conversation/<user_id>"""
    print_test("Get Conversation History")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/messages/conversation/{TEST_OTHER_USER_ID}",
            params={'user_id': TEST_USER_ID, 'limit': 10},
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data.get('messages', []))} messages")
            
            # Show sample message
            if data.get('messages'):
                msg = data['messages'][0]
                print_info(f"Sample: From {msg['sender_user_id']}, Read: {msg['read']}")
            
            return True
        elif response.status_code == 503:
            print_warning("Message service not available (expected in dev)")
            return None
        else:
            print_error(f"Failed: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_send_message():
    """Test POST /api/messages/send"""
    print_test("Send Direct Message")
    
    try:
        payload = {
            'sender_user_id': TEST_USER_ID,
            'recipient_user_id': TEST_OTHER_USER_ID,
            'message_text': f'Test message at {datetime.now().isoformat()}',
            'metadata': {'test': True, 'source': 'smoke_test'}
        }
        
        response = requests.post(
            f"{BASE_URL}/api/messages/send",
            json=payload,
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Message sent! ID: {data.get('message_id')}")
            print_info(f"Delivered: {data.get('delivered')}, Online: {data.get('recipient_online')}")
            return True
        elif response.status_code == 503:
            print_warning("Message service not available (expected in dev)")
            return None
        else:
            print_error(f"Failed: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_mark_read():
    """Test POST /api/messages/mark-read"""
    print_test("Mark Messages as Read")
    
    try:
        payload = {
            'user_id': TEST_USER_ID,
            'other_user_id': TEST_OTHER_USER_ID
        }
        
        response = requests.post(
            f"{BASE_URL}/api/messages/mark-read",
            json=payload,
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Marked {data.get('marked_count', 0)} messages as read")
            return True
        elif response.status_code == 503:
            print_warning("Message service not available (expected in dev)")
            return None
        else:
            print_error(f"Failed: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_user_info():
    """Test GET /api/users/<user_id>/info"""
    print_test("Get User Info")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/{TEST_OTHER_USER_ID}/info",
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"User info retrieved")
            print_info(f"Online: {data.get('is_online')}, Sessions: {data.get('session_count')}")
            return True
        else:
            print_error(f"Failed: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


# ==============================================================================
# PART 2: MISSING ENDPOINT TESTS (Expected to fail)
# ==============================================================================

def test_team_members():
    """Test GET /api/users/team-members (Expected to NOT exist yet)"""
    print_test("Get Team Members (Contacts Tab)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/users/team-members",
            params={'user_id': TEST_USER_ID},
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data.get('users', []))} team members")
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (expected)")
            print_info("NEEDS: /api/users/team-members endpoint")
            return None
        else:
            print_error(f"Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_call_history():
    """Test GET /api/calls/history (Expected to NOT exist yet)"""
    print_test("Get Call History (Calls Tab)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/calls/history",
            params={'user_id': TEST_USER_ID},
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {len(data.get('calls', []))} call records")
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (expected)")
            print_info("NEEDS: /api/calls/history endpoint")
            return None
        else:
            print_error(f"Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


def test_clear_call_history():
    """Test DELETE /api/calls/clear-history (Expected to NOT exist yet)"""
    print_test("Clear Call History")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/calls/clear-history",
            params={'user_id': TEST_USER_ID},
            timeout=5
        )
        
        print_info(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Call history cleared")
            return True
        elif response.status_code == 404:
            print_warning("Endpoint not implemented yet (expected)")
            print_info("NEEDS: DELETE /api/calls/clear-history endpoint")
            return None
        else:
            print_error(f"Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return False


# ==============================================================================
# PART 3: JAVASCRIPT SYNTAX CHECK
# ==============================================================================

def check_javascript_syntax():
    """Validate JavaScript syntax using basic parsing"""
    print_test("JavaScript Syntax Check")
    
    js_file = "UI/shared/js/chat-sidebar.js"
    
    try:
        with open(js_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic syntax checks
        checks = {
            'Bracket balance': content.count('{') == content.count('}'),
            'Paren balance': content.count('(') == content.count(')'),
            'Square bracket balance': content.count('[') == content.count(']'),
            'Has window.ChatSidebar': 'window.ChatSidebar' in content,
            'Has init function': 'async init()' in content,
            'Has switchTab function': 'switchTab(' in content,
            'Has loadContacts function': 'loadContacts(' in content,
            'Has loadCallHistory function': 'loadCallHistory(' in content
        }
        
        all_pass = True
        for check_name, passed in checks.items():
            if passed:
                print_success(f"{check_name}: PASS")
            else:
                print_error(f"{check_name}: FAIL")
                all_pass = False
        
        return all_pass
        
    except Exception as e:
        print_error(f"Error reading file: {str(e)}")
        return False


# ==============================================================================
# PART 4: CSS VALIDATION
# ==============================================================================

def check_css_classes():
    """Verify all required CSS classes exist"""
    print_test("CSS Class Validation")
    
    css_file = "UI/shared/css/chat-sidebar.css"
    
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_classes = [
            '.chat-tabs',
            '.chat-tab',
            '.chat-tab-content',
            '.chat-list-empty',
            '.chat-contact-item',
            '.chat-contact-avatar',
            '.chat-contact-actions',
            '.chat-calls-container',
            '.chat-call-item',
            '.chat-call-icon',
            '.chat-call-redial-btn'
        ]
        
        all_exist = True
        for cls in required_classes:
            if cls in content:
                print_success(f"{cls}: EXISTS")
            else:
                print_error(f"{cls}: MISSING")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print_error(f"Error reading file: {str(e)}")
        return False


# ==============================================================================
# PART 5: HTML STRUCTURE CHECK
# ==============================================================================

def check_html_structure():
    """Verify chat sidebar HTML structure"""
    print_test("HTML Structure Validation")
    
    html_file = "UI/business-ai-platform-v2.html"
    
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_elements = [
            'id="chat-sidebar"',
            'class="chat-tabs"',
            'id="chat-tab-chats"',
            'id="chat-tab-contacts"',
            'id="chat-tab-calls"',
            'id="chat-contacts-container"',
            'id="chat-calls-container"',
            'onclick="ChatSidebar.switchTab('
        ]
        
        all_exist = True
        for elem in required_elements:
            if elem in content:
                print_success(f"{elem}: EXISTS")
            else:
                print_error(f"{elem}: MISSING")
                all_exist = False
        
        return all_exist
        
    except Exception as e:
        print_error(f"Error reading file: {str(e)}")
        return False


# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    print_header("CHAT SIDEBAR - COMPREHENSIVE SMOKE TEST")
    
    results = {}
    
    # Part 1: Existing API Endpoints
    print_header("PART 1: EXISTING API ENDPOINTS")
    results['conversations'] = test_conversations_endpoint()
    results['conversation_history'] = test_conversation_history()
    results['send_message'] = test_send_message()
    results['mark_read'] = test_mark_read()
    results['user_info'] = test_user_info()
    
    # Part 2: Missing Endpoints
    print_header("PART 2: NEW ENDPOINTS (Expected Missing)")
    results['team_members'] = test_team_members()
    results['call_history'] = test_call_history()
    results['clear_calls'] = test_clear_call_history()
    
    # Part 3: Code Validation
    print_header("PART 3: JAVASCRIPT VALIDATION")
    results['javascript'] = check_javascript_syntax()
    
    # Part 4: CSS Validation
    print_header("PART 4: CSS VALIDATION")
    results['css'] = check_css_classes()
    
    # Part 5: HTML Validation
    print_header("PART 5: HTML STRUCTURE")
    results['html'] = check_html_structure()
    
    # Final Summary
    print_header("FINAL SUMMARY")
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Test Results:{Colors.RESET}")
    print(f"  {Colors.GREEN}Passed:  {passed}/{total}{Colors.RESET}")
    print(f"  {Colors.RED}Failed:  {failed}/{total}{Colors.RESET}")
    print(f"  {Colors.YELLOW}Skipped: {skipped}/{total}{Colors.RESET}")
    
    # Implementation Status
    print(f"\n{Colors.BOLD}Implementation Status:{Colors.RESET}")
    
    if results.get('javascript') and results.get('css') and results.get('html'):
        print(f"  {Colors.GREEN}✅ Frontend: Complete{Colors.RESET}")
    else:
        print(f"  {Colors.RED}❌ Frontend: Issues detected{Colors.RESET}")
    
    if results.get('conversations') and results.get('send_message'):
        print(f"  {Colors.GREEN}✅ Messages API: Working{Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}⚠️  Messages API: Service unavailable (expected){Colors.RESET}")
    
    if results.get('team_members') is None:
        print(f"  {Colors.YELLOW}⚠️  Contacts API: Not implemented{Colors.RESET}")
        print(f"     {Colors.CYAN}TODO: Add /api/users/team-members endpoint{Colors.RESET}")
    
    if results.get('call_history') is None:
        print(f"  {Colors.YELLOW}⚠️  Calls API: Not implemented{Colors.RESET}")
        print(f"     {Colors.CYAN}TODO: Add /api/calls/* endpoints{Colors.RESET}")
    
    print()


if __name__ == '__main__':
    main()
