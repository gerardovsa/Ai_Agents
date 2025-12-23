import requests
import sys

BASE_URL = "http://localhost:5001"
TEST_USER = 1

print("=" * 70)
print("CHAT SIDEBAR - NEW ENDPOINTS TEST")
print("=" * 70)

# Test 1: Team Members
print("\n[1/3] Testing GET /api/users/team-members")
try:
    r = requests.get(f"{BASE_URL}/api/users/team-members", params={'user_id': TEST_USER}, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"OK - Retrieved {len(data.get('users', []))} team members")
    else:
        print(f"FAIL - {r.text}")
except Exception as e:
    print(f"ERROR - {e}")

# Test 2: Call History
print("\n[2/3] Testing GET /api/calls/history")
try:
    r = requests.get(f"{BASE_URL}/api/calls/history", params={'user_id': TEST_USER}, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"OK - Retrieved {len(data.get('calls', []))} call records")
        print(f"Table created: YES")
    else:
        print(f"FAIL - {r.text}")
except Exception as e:
    print(f"ERROR - {e}")

# Test 3: Clear Call History
print("\n[3/3] Testing DELETE /api/calls/clear-history")
try:
    r = requests.delete(f"{BASE_URL}/api/calls/clear-history", params={'user_id': TEST_USER}, timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"OK - Deleted {data.get('deleted_count', 0)} records")
    else:
        print(f"FAIL - {r.text}")
except Exception as e:
    print(f"ERROR - {e}")

print("\n" + "=" * 70)
print("ALL NEW ENDPOINTS TESTED")
print("=" * 70)
