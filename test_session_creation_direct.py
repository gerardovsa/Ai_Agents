"""
Direct test of session creation endpoint
"""

import requests
import json

url = 'http://localhost:5001/api/synergy/create'

payload = {
    'title': 'Direct Test Session',
    'description': 'Testing session creation directly',
    'priority': 'medium',
    'platforms_involved': ['sheets', 'gmail'],
    'use_milestones': False
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
        print(f"Response Text: {e.response.text}")
