"""Quick API Test - No Emojis"""
import requests
import json

BASE_URL = "http://localhost:5001"

def test_endpoint(method, path, name, auth=False, token=None, body=None):
    url = f"{BASE_URL}{path}"
    headers = {'Content-Type': 'application/json'}
    if auth and token:
        headers['Authorization'] = f"Bearer {token}"
    
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            r = requests.post(url, headers=headers, json=body, timeout=5)
        else:
            return f"{name}: UNSUPPORTED METHOD"
        
        status = r.status_code
        if status == 200:
            return f"[OK  ] {method:6} {path:45} | {status}"
        elif status == 401:
            return f"[AUTH] {method:6} {path:45} | {status} (Auth Required)"
        elif status == 500:
            return f"[FAIL] {method:6} {path:45} | {status} (Server Error)"
        else:
            return f"[WARN] {method:6} {path:45} | {status}"
    except Exception as e:
        return f"[ERR ] {method:6} {path:45} | {str(e)[:30]}"

print("="*80)
print("API ENDPOINT TEST - LOCAL SERVER")
print("="*80)

# Try login first
print("\n1. Authentication:")
try:
    r = requests.post(f"{BASE_URL}/api/auth/login", 
                     json={'username': 'printing@inhouseprint.com.au', 'password': 'inhouseprint'},
                     timeout=5)
    if r.status_code == 200:
        data = r.json()
        token = data.get('token') if data.get('success') else None
        print(f"   Login: {'SUCCESS' if token else 'FAILED'}")
    else:
        token = None
        print(f"   Login: FAILED ({r.status_code})")
except Exception as e:
    token = None
    print(f"   Login: ERROR - {e}")

print("\n2. Core Endpoints:")
endpoints = [
    ('GET', '/health', 'Health Check', False),
    ('GET', '/api/auth/verify', 'Verify Token', True),
    ('GET', '/api/auth/profile', 'Get Profile', True),
    ('GET', '/api/threads/list', 'List Threads', True),
    ('GET', '/api/threads/stats', 'Thread Stats', True),
    ('GET', '/api/automation/list', 'List Automations', True),
    ('GET', '/api/synergy/sessions', 'Synergy Sessions', True),
    ('GET', '/api/internal-docs/list', 'Internal Docs', True),
    ('POST', '/api/agent/chat', 'Agent Chat', True),
]

for method, path, name, auth in endpoints:
    body = {'message': 'test', 'user_id': 1} if path == '/api/agent/chat' else None
    result = test_endpoint(method, path, name, auth, token, body)
    print(f"   {result}")

print("\n" + "="*80)
print("Test Complete")
print("="*80)
