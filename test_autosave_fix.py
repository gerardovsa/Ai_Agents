"""
Test Auto-Save Fix - Verify no tuple index errors
Created: November 19, 2025
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

print("="*80)
print("AUTO-SAVE FIX TEST")
print("="*80)

# Create thread
print("\n1. Creating thread...")
resp = requests.post(f"{BASE_URL}/api/threads/create", json={
    "title": "Auto-Save Test",
    "location": "prime",
    "user_id": 14
})
thread_slug = resp.json()['data']['thread']['id']
print(f"   Thread: {thread_slug}")

# Send message
print("\n2. Sending message...")
requests.post(f"{BASE_URL}/api/agent/agent/1/start", json={
    "message": "Say hello",
    "session_id": thread_slug,
    "thread_slug": thread_slug
})
print("   Message sent")

# Stream response and watch for auto-save
print("\n3. Streaming response (watching for auto-save)...")
time.sleep(2)

url = f"{BASE_URL}/api/agent/stream/1?thread_slug={thread_slug}"
resp = requests.get(url, stream=True, timeout=30)

autosave_success = False
autosave_error = False

for line in resp.iter_lines():
    if not line:
        continue
    line = line.decode('utf-8', errors='ignore')
    
    # Check for auto-save messages in SSE comments or data
    if 'Auto-Save' in line:
        print(f"   {line}")
        if 'Thread updated' in line:
            autosave_success = True
        if 'Could not determine' in line and 'tuple indices' in line:
            autosave_error = True
    
    if line.startswith('event: complete'):
        break

print("\n" + "="*80)
print("RESULTS:")
print("="*80)

if autosave_error:
    print(" FAILED - Tuple index error still occurring")
    print("   The auto-save location lookup is still broken")
elif autosave_success:
    print(" SUCCESS - Auto-save completed without errors!")
    print("   Thread updated successfully")
else:
    print(" PARTIAL - Stream completed but no auto-save logs seen")
    print("   This is OK if auto-save happens silently")

print("="*80)
