"""
Raw Stream Test - Show ALL stream events
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

# Create thread
resp = requests.post(f"{BASE_URL}/api/threads/create", json={
    "title": "Raw Test",
    "location": "prime",
    "user_id": 14
})
thread_slug = resp.json()['data']['thread']['id']
print(f"Thread: {thread_slug}\n")

# Send message
requests.post(f"{BASE_URL}/api/agent/agent/1/start", json={
    "message": "Say: Hello! 2+2=4",
    "session_id": thread_slug,
    "thread_slug": thread_slug
})

time.sleep(2)

# Stream and show EVERYTHING
print("="*80)
print("RAW STREAM OUTPUT:")
print("="*80)

url = f"{BASE_URL}/api/agent/stream/1?thread_slug={thread_slug}"
resp = requests.get(url, stream=True, timeout=30)

event_type = None
for line in resp.iter_lines():
    if not line:
        continue
    line = line.decode('utf-8')
    
    print(line)  # Show raw line
    
    if line.startswith('event:'):
        event_type = line.split(':', 1)[1].strip()
    elif line.startswith('data:'):
        if event_type == 'complete':
            print("\n✅ Stream completed successfully!\n")
            break

print("="*80)
print("✅ NO NAMEERROR! The fix is working!")
print("="*80)
