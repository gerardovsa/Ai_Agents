import requests
import json

API_BASE = "http://localhost:5001"

# Test thread IDs - both old slug format and new integer format
test_threads = [
    "1765854881504",  # Old timestamp-based slug
    "2031",           # New integer ID
]

print("🧪 Testing Thread Lookup Fix\n")
print("="*60)

for thread_id in test_threads:
    print(f"\n📋 Testing thread_id: {thread_id}")
    print("-"*60)
    
    # Test 1: Get messages
    url = f"{API_BASE}/api/threads/messages/get?thread_id={thread_id}"
    print(f"   GET {url}")
    
    response = requests.get(url)
    print(f"   Status: {response.status_code}")
    
    if response.ok:
        data = response.json()
        if data.get('success'):
            messages = data.get('data', {}).get('messages', [])
            total = data.get('data', {}).get('total', 0)
            print(f"   ✅ SUCCESS: {len(messages)} messages loaded (total: {total})")
            if messages:
                print(f"   First message: {messages[0].get('role')} - {str(messages[0].get('content'))[:50]}...")
        else:
            print(f"   ❌ FAILED: {data.get('error', 'Unknown error')}")
    else:
        print(f"   ❌ HTTP ERROR: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error: {error_data}")
        except:
            print(f"   Error: {response.text[:200]}")

print("\n" + "="*60)
print("✅ Test Complete")
