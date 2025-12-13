#!/usr/bin/env python3
"""
Test the /api/auth/sessions endpoint
"""
import requests
import json
import time

def test_sessions_endpoint():
    """Test GET /api/auth/sessions with Bearer token"""
    
    # Give server a moment to start fully
    time.sleep(2)
    
    url = 'http://localhost:5000/api/auth/sessions'
    headers = {
        'Authorization': 'Bearer test_token_123',
        'Content-Type': 'application/json'
    }
    
    print("Testing GET /api/auth/sessions endpoint...")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print("-" * 60)
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
        
        # Check response structure
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Endpoint returned 200 OK")
            print(f"✓ Response has 'success' key: {'success' in data}")
            print(f"✓ Response has 'sessions' key: {'sessions' in data}")
            
            if 'sessions' in data:
                print(f"✓ Number of sessions: {len(data['sessions'])}")
                if data['sessions']:
                    print(f"✓ First session keys: {list(data['sessions'][0].keys())}")
        else:
            print(f"\n✗ Unexpected status code: {response.status_code}")
    
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Connection error: {e}")
        print("  Make sure Flask server is running on localhost:5000")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == '__main__':
    test_sessions_endpoint()
