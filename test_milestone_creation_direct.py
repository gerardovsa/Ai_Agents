"""Test milestone creation directly"""

import requests
import json

session_id = 'sess_20251124_1852_test_milestone_creation_fix'
url = f'http://localhost:5001/api/synergy/milestone/create'

payload = {
    "session_id": session_id,
    "milestone_name": "Direct Test Milestone",
    "description": "Testing milestone creation directly",
    "tasks": ["Task 1", "Task 2"],
    "priority": "high"
}

print(f"Testing: POST {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("-" * 70)

try:
    response = requests.post(url, json=payload, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.RequestException as e:
    print(f"ERROR: {e}")
    if hasattr(e, 'response') and e.response is not None:
        print(f"Response Status: {e.response.status_code}")
        print(f"Response Text: {e.response.text}")
