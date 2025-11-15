"""
Test the /api/threads/details endpoint to see the actual error
"""
import requests
import json

print("\n" + "="*80)
print("TESTING /api/threads/details ENDPOINT")
print("="*80)

url = "http://localhost:5001/api/threads/details"
headers = {"Content-Type": "application/json"}

# Test with real thread IDs from the database
payload = {
    "thread_ids": ["1762530418975", "1762531251405"]
}

print(f"\nSending POST to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print(f"\n✅ SUCCESS!")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"\n❌ ERROR!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")

print("\n" + "="*80 + "\n")
