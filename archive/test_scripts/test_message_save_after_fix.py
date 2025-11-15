"""Test message save after schema fix"""
import requests
import json

url = "http://localhost:5001/api/threads/messages/save"

payload = {
    "thread_id": "1762664406832",
    "user_id": 12,
    "messages": [
        {
            "role": "user",
            "content": "Test message after schema fix"
        },
        {
            "role": "assistant",
            "content": "Test response after schema fix"
        }
    ]
}

print("=" * 80)
print("TESTING MESSAGE SAVE AFTER SCHEMA FIX")
print("=" * 80)
print(f"\nSending POST to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    result = response.json()
    if result.get('success') and result.get('data', {}).get('messages_saved', 0) > 0:
        print("\n" + "=" * 80)
        print("SUCCESS! Messages saved to database!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("FAILED - Still saving 0 messages")
        print("=" * 80)
        
except Exception as e:
    print(f"\nERROR: {e}")
