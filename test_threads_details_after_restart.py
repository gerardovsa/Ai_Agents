"""Test /api/threads/details endpoint after Flask restart"""
import requests
import json

# Test data - using real thread IDs from database
thread_ids = ["1762530418975", "1762531251405", "1762533505022"]

print("="*100)
print("TESTING /api/threads/details ENDPOINT AFTER RESTART")
print("="*100)

print(f"\nSending request with thread_ids: {thread_ids}")

try:
    response = requests.post(
        'http://localhost:5001/api/threads/details',
        json={'thread_ids': thread_ids},
        timeout=5
    )
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Response type: {type(data)}")
        
        if isinstance(data, list):
            print(f"Number of threads returned: {len(data)}")
            print("\nThread details:")
            for thread in data:
                print(f"\n  Thread ID: {thread.get('id')}")
                print(f"  Thread Slug: {thread.get('thread_slug')}")
                print(f"  Name: {thread.get('name')}")
                print(f"  Agent ID: {thread.get('agent_id')}")
                print(f"  Agent Name: {thread.get('agent_name')}")
                print(f"  Updated: {thread.get('updated')}")
        elif isinstance(data, dict):
            print(f"⚠️  Response is dict, not list!")
            print(f"Keys: {data.keys()}")
            print(f"Data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Unexpected response type: {type(data)}")
    else:
        print(f"\n❌ ERROR - Status {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR - Flask server not running!")
except Exception as e:
    print(f"\n❌ ERROR: {e}")

print("\n" + "="*100)
