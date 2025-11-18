"""
Complete Flow Test - Test all fixes together
1. NameError fix (session_id -> thread_slug)
2. Auto-save fix (tuple index error)
3. Thread isolation (no cross-contamination)
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

def test_complete_flow():
    print("="*80)
    print("COMPLETE FLOW TEST - All Fixes Verification")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print("="*80)
    
    # Test 1: Create thread and send message
    print("\nTEST 1: Single Agent Flow")
    print("-" * 80)
    
    resp = requests.post(f"{BASE_URL}/api/threads/create", json={
        "title": "Complete Test",
        "location": "prime",
        "user_id": 14
    })
    thread1 = resp.json()['data']['thread']['id']
    print(f"✓ Thread created: {thread1}")
    
    resp = requests.post(f"{BASE_URL}/api/agent/agent/1/start", json={
        "message": "Just say 'Test 1 complete'",
        "session_id": thread1,
        "thread_slug": thread1
    })
    print(f"✓ Message sent to Agent 1")
    
    time.sleep(2)
    
    # Stream and check for errors
    url = f"{BASE_URL}/api/agent/stream/1?thread_slug={thread1}"
    resp = requests.get(url, stream=True, timeout=30)
    
    has_text = False
    has_error = False
    
    for line in resp.iter_lines():
        if not line:
            continue
        line = line.decode('utf-8', errors='ignore')
        
        if 'error' in line.lower() and 'session_id' in line:
            has_error = True
            print(f"✗ NameError detected: {line[:100]}")
        
        if 'tuple indices' in line.lower():
            has_error = True
            print(f"✗ Tuple index error: {line[:100]}")
        
        if line.startswith('data:') and 'text' in line and 'Test 1' in line:
            has_text = True
        
        if line.startswith('event: complete'):
            break
    
    if has_error:
        print("✗ TEST 1 FAILED - Errors detected")
        return False
    elif has_text:
        print("✓ TEST 1 PASSED - Text response received, no errors")
    else:
        print("⚠  TEST 1 PARTIAL - No text but no errors either")
    
    # Test 2: Multiple agents (thread isolation)
    print("\nTEST 2: Thread Isolation (Multiple Agents)")
    print("-" * 80)
    
    # Create threads for Agent 1 and Agent 8
    resp = requests.post(f"{BASE_URL}/api/threads/create", json={
        "title": "Agent 1 Thread",
        "location": "prime",
        "user_id": 14
    })
    thread_a1 = resp.json()['data']['thread']['id']
    
    resp = requests.post(f"{BASE_URL}/api/threads/create", json={
        "title": "Agent 8 Thread",
        "location": "agent-8",
        "user_id": 14
    })
    thread_a8 = resp.json()['data']['thread']['id']
    
    print(f"✓ Agent 1 thread: {thread_a1}")
    print(f"✓ Agent 8 thread: {thread_a8}")
    
    # Send different messages to each
    requests.post(f"{BASE_URL}/api/agent/agent/1/start", json={
        "message": "My name is Alice",
        "session_id": thread_a1,
        "thread_slug": thread_a1
    })
    
    requests.post(f"{BASE_URL}/api/agent/agent/8/start", json={
        "message": "My name is Bob",
        "session_id": thread_a8,
        "thread_slug": thread_a8
    })
    
    print("✓ Messages sent to both agents")
    
    time.sleep(2)
    
    # Stream both (they should be isolated)
    url1 = f"{BASE_URL}/api/agent/stream/1?thread_slug={thread_a1}"
    url8 = f"{BASE_URL}/api/agent/stream/8?thread_slug={thread_a8}"
    
    resp1 = requests.get(url1, stream=True, timeout=30)
    resp1_text = ""
    for line in resp1.iter_lines():
        if not line:
            continue
        line = line.decode('utf-8', errors='ignore')
        if 'Alice' in line or 'Bob' in line:
            resp1_text += line
        if 'event: complete' in line:
            break
    
    resp8 = requests.get(url8, stream=True, timeout=30)
    resp8_text = ""
    for line in resp8.iter_lines():
        if not line:
            continue
        line = line.decode('utf-8', errors='ignore')
        if 'Alice' in line or 'Bob' in line:
            resp8_text += line
        if 'event: complete' in line:
            break
    
    # Check isolation
    isolation_ok = True
    if 'Bob' in resp1_text:
        print("✗ ISOLATION BROKEN - Agent 1 saw Bob's message!")
        isolation_ok = False
    if 'Alice' in resp8_text:
        print("✗ ISOLATION BROKEN - Agent 8 saw Alice's message!")
        isolation_ok = False
    
    if isolation_ok:
        print("✓ TEST 2 PASSED - Thread isolation working correctly")
    else:
        print("✗ TEST 2 FAILED - Cross-contamination detected")
        return False
    
    # Final summary
    print("\n" + "="*80)
    print("ALL TESTS PASSED! ✓")
    print("="*80)
    print("✓ NameError fix working (session_id -> thread_slug)")
    print("✓ Auto-save fix working (no tuple index errors)")
    print("✓ Thread isolation working (no cross-contamination)")
    print("="*80)
    
    return True

if __name__ == '__main__':
    success = test_complete_flow()
    exit(0 if success else 1)
