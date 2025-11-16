"""
Quick test for critical database syntax fixes
"""
import requests

BASE_URL = "http://localhost:5001"
USER_ID = 14

print("=" * 60)
print("CRITICAL FIX VERIFICATION")
print("=" * 60)

# Test 1: Thread List (PRIMARY FIX - cross-database reference)
print("\n[1] Thread List (cross-database ref fix)...")
try:
    r = requests.get(f"{BASE_URL}/api/threads/list", params={'user_id': USER_ID}, timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ PASS - {len(data.get('data', []))} threads loaded")
    else:
        print(f"    ❌ FAIL - Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"    ❌ FAIL - {e}")

# Test 2: Thread Create (import fix + cross-database ref)
print("\n[2] Thread Create (import fix)...")
try:
    r = requests.post(f"{BASE_URL}/api/threads/create", 
                     json={'user_id': USER_ID, 'title': 'Test Thread'}, 
                     timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ PASS - Thread created: {data.get('thread', {}).get('id')}")
    else:
        print(f"    ❌ FAIL - Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"    ❌ FAIL - {e}")

# Test 3: Prompt Library (AUTOINCREMENT fix)
print("\n[3] Prompt Library Quick Actions (AUTOINCREMENT fix)...")
try:
    r = requests.get(f"{BASE_URL}/api/prompts/quick-actions", timeout=5)
    if r.status_code == 200:
        data = r.json()
        count = len(data.get('quick_actions', []))
        print(f"    ✅ PASS - {count} quick actions loaded")
    else:
        print(f"    ❌ FAIL - Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"    ❌ FAIL - {e}")

# Test 4: Stock Management (module loading)
print("\n[4] Stock Management (module blueprint)...")
try:
    r = requests.get(f"{BASE_URL}/api/stock-management/usage-analytics", 
                     params={'days': 30}, 
                     timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ PASS - Stock data loaded")
    else:
        print(f"    ❌ FAIL - Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"    ❌ FAIL - {e}")

# Test 5: Shopify (module loading)
print("\n[5] Shopify Dashboard (module blueprint)...")
try:
    r = requests.get(f"{BASE_URL}/api/shopify/dashboard/metrics", timeout=5)
    if r.status_code == 200:
        data = r.json()
        print(f"    ✅ PASS - Shopify metrics loaded")
    else:
        print(f"    ❌ FAIL - Status {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"    ❌ FAIL - {e}")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
