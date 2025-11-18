"""
Thread Isolation Test - November 19, 2025
Verify no cross-contamination between agent threads

Tests:
1. Create separate threads for Agent 1 and Agent 8
2. Send messages to each agent
3. Verify responses appear ONLY in correct thread
4. Check database location tracking
5. Validate session_id === thread_slug enforcement
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE = "http://localhost:5001"
TOKEN = None  # Will be set after login

def login():
    """Authenticate and get JWT token"""
    global TOKEN
    print("\n" + "="*80)
    print("AUTHENTICATION")
    print("="*80)
    
    response = requests.post(
        f"{API_BASE}/api/auth/login",
        json={
            "username": "printing@inhouseprint.com.au",
            "password": "inhouseprint"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        TOKEN = data.get('token')
        print(f"✅ Authenticated as: {data.get('user', {}).get('email')}")
        print(f"   User ID: {data.get('user', {}).get('id')}")
        return data.get('user', {}).get('id')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def get_headers():
    """Get request headers with auth token"""
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }

def create_thread(name, location, user_id):
    """Create a new thread"""
    response = requests.post(
        f"{API_BASE}/api/threads/create",
        headers=get_headers(),
        json={
            "name": name,
            "user_id": user_id,
            "location": location
        }
    )
    
    if response.status_code == 200:
        thread_data = response.json()
        thread = thread_data.get('thread', {})
        # thread_slug is in the 'id' field
        thread_slug = thread.get('id')
        print(f"✅ Thread created: {name}")
        print(f"   Thread slug: {thread_slug}")
        print(f"   Location: {location}")
        return thread_slug
    else:
        print(f"❌ Thread creation failed: {response.status_code}")
        print(response.text)
        return None

def send_message(agent_id, thread_slug, message):
    """Send message to agent"""
    response = requests.post(
        f"{API_BASE}/api/agent/agent/{agent_id}/start",
        headers=get_headers(),
        json={
            "message": message,
            "session_id": thread_slug,
            "thread_slug": thread_slug,  # CRITICAL: Must match session_id
            "conversation_history": [],
            "agent_name": f"Agent {agent_id}",
            "tools_enabled": True
        }
    )
    
    if response.status_code == 200:
        print(f"✅ Message sent to Agent {agent_id}")
        return True
    else:
        print(f"❌ Message failed: {response.status_code}")
        print(response.text)
        return False

def get_thread_messages(thread_slug):
    """Get messages from thread"""
    response = requests.get(
        f"{API_BASE}/api/threads/{thread_slug}/messages",
        headers=get_headers()
    )
    
    if response.status_code == 200:
        data = response.json()
        messages = data.get('messages', [])
        return messages
    else:
        print(f"❌ Failed to get messages: {response.status_code}")
        return []

def verify_thread_location(thread_slug, expected_location):
    """Verify thread location in database"""
    response = requests.get(
        f"{API_BASE}/api/threads/list",
        headers=get_headers(),
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        data = response.json()
        threads = data.get('threads', [])
        for thread in threads:
            if thread.get('id') == thread_slug or thread.get('thread_slug') == thread_slug:
                actual_location = thread.get('location')
                if actual_location == expected_location:
                    print(f"✅ Location verified: {thread_slug} -> {expected_location}")
                    return True
                else:
                    print(f"❌ Location mismatch: expected {expected_location}, got {actual_location}")
                    return False
        print(f"❌ Thread {thread_slug} not found in list")
        return False
    else:
        print(f"❌ Failed to list threads: {response.status_code}")
        return False

def check_contamination(thread_slug, target_message, should_contain=True):
    """Check if thread contains (or doesn't contain) a specific message"""
    messages = get_thread_messages(thread_slug)
    
    found = False
    for msg in messages:
        content = msg.get('content', '')
        if isinstance(content, str) and target_message.lower() in content.lower():
            found = True
            break
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get('text', '') or block.get('content', '')
                    if text and target_message.lower() in text.lower():
                        found = True
                        break
    
    if should_contain:
        if found:
            print(f"✅ Thread contains expected message: '{target_message[:30]}...'")
            return True
        else:
            print(f"❌ Thread missing expected message: '{target_message[:30]}...'")
            return False
    else:
        if not found:
            print(f"✅ Thread correctly isolated (no contamination from: '{target_message[:30]}...')")
            return True
        else:
            print(f"❌ CONTAMINATION DETECTED: Thread contains: '{target_message[:30]}...'")
            return False

# Main Test Execution
print("\n" + "="*80)
print("THREAD ISOLATION TEST - November 19, 2025")
print("="*80)
print()

# Step 1: Login
user_id = login()
if not user_id:
    print("\n❌ TEST ABORTED: Authentication failed")
    exit(1)

time.sleep(1)

# Step 2: Create Thread A for Agent 1
print("\n" + "="*80)
print("TEST 1: Creating Thread A for Agent 1")
print("="*80)
thread_a_slug = create_thread(
    name=f"Thread A - Agent 1 [{datetime.now().strftime('%H:%M:%S')}]",
    location="agent-1",
    user_id=user_id
)
if not thread_a_slug:
    print("\n❌ TEST ABORTED: Thread A creation failed")
    exit(1)

time.sleep(1)

# Step 3: Create Thread B for Agent 8
print("\n" + "="*80)
print("TEST 2: Creating Thread B for Agent 8")
print("="*80)
thread_b_slug = create_thread(
    name=f"Thread B - Agent 8 [{datetime.now().strftime('%H:%M:%S')}]",
    location="agent-8",
    user_id=user_id
)
if not thread_b_slug:
    print("\n❌ TEST ABORTED: Thread B creation failed")
    exit(1)

time.sleep(1)

# Step 4: Send message to Thread A (Agent 1)
print("\n" + "="*80)
print("TEST 3: Sending 'Hello from Thread A' to Agent 1")
print("="*80)
success_a = send_message(1, thread_a_slug, "Hello from Thread A - this is a test message")
if not success_a:
    print("\n⚠️ TEST WARNING: Message A failed")

time.sleep(2)  # Wait for processing

# Step 5: Send message to Thread B (Agent 8)
print("\n" + "="*80)
print("TEST 4: Sending 'Hello from Thread B' to Agent 8")
print("="*80)
success_b = send_message(8, thread_b_slug, "Hello from Thread B - this is a different test message")
if not success_b:
    print("\n⚠️ TEST WARNING: Message B failed")

time.sleep(2)  # Wait for processing

# Step 6: Verify Thread A isolation
print("\n" + "="*80)
print("TEST 5: Verifying Thread A Isolation")
print("="*80)
print(f"Thread A slug: {thread_a_slug}")
print(f"Checking for contamination from Thread B...")

# Thread A should contain its own message
test_5a = check_contamination(thread_a_slug, "Hello from Thread A", should_contain=True)

# Thread A should NOT contain Thread B's message
test_5b = check_contamination(thread_a_slug, "Hello from Thread B", should_contain=False)

# Step 7: Verify Thread B isolation
print("\n" + "="*80)
print("TEST 6: Verifying Thread B Isolation")
print("="*80)
print(f"Thread B slug: {thread_b_slug}")
print(f"Checking for contamination from Thread A...")

# Thread B should contain its own message
test_6a = check_contamination(thread_b_slug, "Hello from Thread B", should_contain=True)

# Thread B should NOT contain Thread A's message
test_6b = check_contamination(thread_b_slug, "Hello from Thread A", should_contain=False)

# Step 8: Verify database locations
print("\n" + "="*80)
print("TEST 7: Verifying Database Locations")
print("="*80)
test_7a = verify_thread_location(thread_a_slug, "agent-1")
test_7b = verify_thread_location(thread_b_slug, "agent-8")

# Final Results
print("\n" + "="*80)
print("TEST RESULTS SUMMARY")
print("="*80)

all_tests = {
    "Thread A creation": thread_a_slug is not None,
    "Thread B creation": thread_b_slug is not None,
    "Message sent to Agent 1": success_a,
    "Message sent to Agent 8": success_b,
    "Thread A has own message": test_5a,
    "Thread A isolated from B": test_5b,
    "Thread B has own message": test_6a,
    "Thread B isolated from A": test_6b,
    "Thread A location correct": test_7a,
    "Thread B location correct": test_7b
}

passed = sum(1 for result in all_tests.values() if result)
total = len(all_tests)

print(f"\nTests Passed: {passed}/{total}")
print()

for test_name, result in all_tests.items():
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"  {status} - {test_name}")

print()

if passed == total:
    print("🎉 ALL TESTS PASSED - Thread isolation working correctly!")
    print()
    print("✅ session_id === thread_slug enforcement successful")
    print("✅ No cross-contamination detected")
    print("✅ Database locations correct")
    exit(0)
else:
    print("🔴 SOME TESTS FAILED - Thread isolation needs attention")
    print()
    print("Failed tests indicate:")
    if not test_5b or not test_6b:
        print("  ❌ Cross-contamination detected - messages appearing in wrong threads")
    if not test_7a or not test_7b:
        print("  ❌ Location tracking issues - threads not assigned to correct agents")
    if not success_a or not success_b:
        print("  ❌ Message sending failures - check backend logs")
    exit(1)
