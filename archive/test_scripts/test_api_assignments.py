"""
Test the thread assignment API endpoint directly
"""

import requests

API_URL = "http://localhost:5001"

print("Testing /api/thread-assignments endpoint (used by frontend)...")
print("="*60)

# Test with user_id=12
response = requests.get(f"{API_URL}/api/thread-assignments?user_id=12")

print(f"Status Code: {response.status_code}")
print(f"Response:")
print(response.json())

print("\n" + "="*60)
print("Testing /api/thread-assignments/list endpoint...")
print("="*60)

# Test with user_id=12
response = requests.get(f"{API_URL}/api/thread-assignments/list?user_id=12")

print(f"Status Code: {response.status_code}")
print(f"Response:")
print(response.json())

print("\n" + "="*60)

# Also test the /api/threads/list endpoint
print("\nTesting /api/threads/list endpoint...")
response2 = requests.get(f"{API_URL}/api/threads/list?user_id=12")

print(f"Status Code: {response2.status_code}")
data = response2.json()
print(f"Threads count: {len(data.get('threads', []))}")
print(f"Assignments in response: {data.get('assignments', {})}")
