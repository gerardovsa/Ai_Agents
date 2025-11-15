"""
Simple test to verify /api/threads/details endpoint works with real thread_slugs
"""

import requests
import json

# Test with actual thread_slugs from database
thread_slugs = ["1762663889170", "1762664086386", "1762664406832"]

print("Testing /api/threads/details endpoint")
print(f"Thread slugs to test: {thread_slugs}\n")

response = requests.post(
    'http://localhost:5001/api/threads/details',
    json={'thread_ids': thread_slugs},
    headers={'Content-Type': 'application/json'}
)

print(f"Status Code: {response.status_code}")
print(f"\nResponse:")
result = response.json()
print(json.dumps(result, indent=2))

if result.get('success'):
    threads = result.get('data', [])
    print(f"\n✓ SUCCESS: Got {len(threads)} threads")
    for thread in threads:
        print(f"  - {thread.get('name')} (slug: {thread.get('thread_slug')})")
else:
    print(f"\n✗ FAILED: {result.get('error', 'Unknown error')}")
