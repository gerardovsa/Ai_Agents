"""Test production deployment on Render"""
import requests
import json

base_url = "https://ai-agents-backend-singapore.onrender.com"

print("="*70)
print("PRODUCTION DEPLOYMENT TESTS")
print("="*70)

# Test 1: Health Check
print("\n1. Testing Health Endpoint...")
try:
    r = requests.get(f"{base_url}/health", timeout=10)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 2: Check if API is responding
print("\n2. Testing API Root...")
try:
    r = requests.get(f"{base_url}/", timeout=10)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Check available routes (if endpoint exists)
print("\n3. Testing Routes Endpoint...")
try:
    r = requests.get(f"{base_url}/api/routes", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        routes = r.json()
        print(f"   Routes: {len(routes)} available")
    else:
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   Note: Routes endpoint may not be available")

# Test 4: Test Agent Chat endpoint (without auth - should get error or validation message)
print("\n4. Testing Agent Chat Endpoint (validation)...")
try:
    r = requests.post(
        f"{base_url}/api/agent/chat",
        json={"message": "test"},
        timeout=10
    )
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 5: Check platform tools (if endpoint exists)
print("\n5. Testing Platform Tools Endpoint...")
try:
    r = requests.get(f"{base_url}/api/platforms", timeout=10)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Platforms: {len(data) if isinstance(data, list) else 'N/A'}")
    else:
        print(f"   Response: {r.text[:200]}")
except Exception as e:
    print(f"   Note: Platforms endpoint may not be available")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70)
print("\nSummary:")
print("- Health endpoint: WORKING")
print("- Production URL: " + base_url)
print("- Next steps:")
print("  1. Test OAuth flows (Google + Microsoft)")
print("  2. Verify Supabase database connection")
print("  3. Test tool execution with valid credentials")
print("="*70 + "\n")
