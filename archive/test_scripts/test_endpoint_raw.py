"""Test the /api/threads/details endpoint with actual thread IDs"""
import requests
import json

# Get thread IDs that actually have synergy links
thread_ids = ["2", "3", "4", "6", "8"]

print("="*100)
print(f"Testing /api/threads/details with thread_ids: {thread_ids}")
print("="*100)

url = "http://localhost:5001/api/threads/details"
payload = {"thread_ids": thread_ids}

print(f"\nPOST {url}")
print(f"Body: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload)
    
    print(f"\n{'='*100}")
    print(f"Status Code: {response.status_code}")
    print(f"{'='*100}")
    
    print(f"\nResponse Headers:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")
    
    print(f"\nResponse Body:")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
        
        # Check if it's an array
        if isinstance(data, list):
            print(f"\n✅ Response is an ARRAY with {len(data)} items")
        elif isinstance(data, dict):
            print(f"\n❌ Response is a DICT (should be array)")
            print(f"Keys: {list(data.keys())}")
            
            # If it has a 'data' key, check that
            if 'data' in data:
                if isinstance(data['data'], list):
                    print(f"  ✅ data field IS an array with {len(data['data'])} items")
                else:
                    print(f"  ❌ data field is NOT an array: {type(data['data'])}")
    except:
        print(response.text)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*100)
