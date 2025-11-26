"""Test the actual Flask endpoint to trigger backend logs"""
import requests
import json

print("\nTesting Flask endpoint...")
response = requests.get('http://localhost:5001/api/threads/list?user_id=14')

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Also test with limit parameter
response2 = requests.get('http://localhost:5001/api/threads/list?user_id=14&limit=10')
print(f"\nWith limit=10:")
print(f"Status: {response2.status_code}")
print(f"Response: {json.dumps(response2.json(), indent=2)}")
