"""Test Messages API Response Format"""

import requests
import json

# Test the messages API endpoint
thread_id = "1762614784052"
url = f"http://localhost:5001/api/threads/messages/get?thread_id={thread_id}"

print("=" * 60)
print("Testing Messages API Response Format")
print("=" * 60)

try:
    response = requests.get(url)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n📦 FULL RESPONSE STRUCTURE:")
        print(json.dumps(data, indent=2))
        
        print("\n🔍 KEY ANALYSIS:")
        print(f"  - success: {data.get('success')}")
        print(f"  - message: {data.get('message')}")
        print(f"  - Has 'data' key: {('data' in data)}")
        print(f"  - Has 'messages' key: {('messages' in data)}")
        
        if 'data' in data:
            print(f"\n📊 data structure:")
            print(f"  - Type: {type(data['data'])}")
            if isinstance(data['data'], dict):
                print(f"  - Keys: {list(data['data'].keys())}")
                if 'messages' in data['data']:
                    print(f"  - messages count: {len(data['data']['messages'])}")
                    print(f"  - messages type: {type(data['data']['messages'])}")
            elif isinstance(data['data'], list):
                print(f"  - List length: {len(data['data'])}")
        
        print("\n✅ FRONTEND SHOULD USE:")
        print("  const messages = data.data.messages || data.data || [];")
        
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
