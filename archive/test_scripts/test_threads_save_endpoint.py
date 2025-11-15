"""
Test the /api/threads/save endpoint to reproduce the error
"""

import requests
import json

# Test data matching what the frontend sends
test_data = {
    "thread_id": 16,  # INTEGER (this is the problem!)
    "title": "Test Thread",
    "messages": [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there"}
    ],
    "agent": "prime",
    "user_id": 14,
    "location": "prime"
}

print("Testing /api/threads/save endpoint...")
print(f"Payload: {json.dumps(test_data, indent=2)}")
print(f"thread_id type: {type(test_data['thread_id'])}")
print()

try:
    response = requests.post(
        'http://localhost:5001/api/threads/save',
        json=test_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print("\nERROR DETAILS:")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2))
        except:
            print(response.text)
    
except Exception as e:
    print(f"Request failed: {e}")
