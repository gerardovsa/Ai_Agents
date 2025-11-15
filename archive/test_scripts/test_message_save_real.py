"""Test sending a real message to the API"""

import requests
import json
from datetime import datetime

# Test data
thread_id = "1762614784052"
user_id = 12

messages = [
    {
        "role": "user",
        "content": "THIS IS A REAL TEST MESSAGE FROM PYTHON SCRIPT",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "tool_calls": [],
        "tokens_used": None,
        "response_time_ms": None,
        "metadata": {}
    },
    {
        "role": "assistant",
        "content": "THIS IS THE AI RESPONSE TO THE TEST",
        "timestamp": int(datetime.now().timestamp() * 1000),
        "tool_calls": [],
        "tokens_used": 50,
        "response_time_ms": 1234,
        "metadata": {}
    }
]

url = "http://localhost:5001/api/threads/messages/save"

print("="*60)
print("TESTING MESSAGE SAVE API")
print("="*60)

payload = {
    "thread_id": thread_id,
    "user_id": user_id,
    "messages": messages
}

print("\n📤 SENDING REQUEST:")
print(f"URL: {url}")
print(f"Thread ID: {thread_id}")
print(f"User ID: {user_id}")
print(f"Messages: {len(messages)}")
print(f"\nPayload:")
print(json.dumps(payload, indent=2))

try:
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    
    print(f"\n📥 RESPONSE:")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"\n✅ SUCCESS! Saved {data.get('messages_saved', 0)} messages")
        else:
            print(f"\n❌ FAILED: {data.get('error', 'Unknown error')}")
    else:
        print(f"\n❌ HTTP ERROR: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Now check the database with: python check_messages.py")
print("="*60)
