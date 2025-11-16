"""Test thread endpoints"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

print("\n[TEST 1] Create thread")
thread_data = {
    "user_id": 1,
    "title": "Test Thread",
    "location": "prime"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/threads/create",
        json=thread_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response keys: {result.keys()}")
    thread_id = result.get("data", {}).get("thread", {}).get("id")
    print(f"Thread ID: {thread_id}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

time.sleep(1)

print("\n[TEST 2] Update thread metadata with workflow")
metadata_data = {
    "thread_id": thread_id,
    "workflow_slug": "test-workflow-123",
    "workflow_title": "Test Workflow"
}

try:
    response = requests.post(
        f"{BASE_URL}/api/threads/metadata/update",
        json=metadata_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

time.sleep(1)

print("\n[TEST 3] List threads")
try:
    response = requests.get(
        f"{BASE_URL}/api/threads/list?user_id=1&limit=5",
        timeout=5
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response keys: {result.keys()}")
    
    # Check different possible response structures
    threads = result.get("data", {}).get("threads", result.get("threads", []))
    print(f"Threads found: {len(threads)}")
    
    if threads:
        thread = threads[0]
        print(f"First thread keys: {thread.keys()}")
        print(f"Thread ID field: {thread.get('id', thread.get('thread_slug', 'NONE'))}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✅ All tests passed!")
