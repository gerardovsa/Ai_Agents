"""
Test Flask Service Connectivity
"""

import requests
import time

FLASK_URL = "https://inhouseprint-flask.onrender.com"

print("=" * 80)
print("FLASK SERVICE CONNECTIVITY TEST")
print("=" * 80)

# Test 1: Basic connectivity
print(f"\n🔍 Test 1: Basic Connectivity to {FLASK_URL}")
try:
    response = requests.get(FLASK_URL, timeout=30)
    print(f"    Status Code: {response.status_code}")
    print(f"    Response Time: {response.elapsed.total_seconds():.2f}s")
    if response.status_code == 200:
        print(f"    Content Length: {len(response.content)} bytes")
        print(f"   Preview: {response.text[:200]}...")
    else:
        print(f"   Response: {response.text}")
except requests.Timeout:
    print(f"    TIMEOUT after 30s")
    print(f"   ⚠️  Service may be spinning up (free tier sleeps after inactivity)")
    print(f"   💡 Wait 1-2 minutes and try again")
except requests.ConnectionError as e:
    print(f"    CONNECTION ERROR: {e}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 2: Health check endpoint (if exists)
print(f"\n🔍 Test 2: Health Check Endpoint")
try:
    response = requests.get(f"{FLASK_URL}/health", timeout=30)
    print(f"    Status Code: {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"   ⚠️  No /health endpoint: {e}")

# Test 3: Stock API endpoint
print(f"\n🔍 Test 3: Stock API Endpoint")
try:
    response = requests.get(f"{FLASK_URL}/api/stock/master", timeout=30)
    print(f"    Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Data received: {len(data)} records")
    else:
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"    ERROR: {e}")

# Test 4: Root endpoint (what Streamlit sees)
print(f"\n🔍 Test 4: Root Endpoint (What Streamlit Sees)")
try:
    response = requests.get(FLASK_URL, timeout=30)
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print(f"\n   Full Response:")
    print(f"   {response.text[:1000]}")
except Exception as e:
    print(f"    ERROR: {e}")

print("\n" + "=" * 80)
print("CONNECTIVITY TEST COMPLETE")
print("=" * 80)

# Summary
print("\n📊 SUMMARY:")
print("   If all tests pass → Flask is working, check Streamlit env vars")
print("   If timeout → Service sleeping (free tier) or not deployed")
print("   If 404/500 → Flask app has errors, check Render logs")
print("   If connection error → DNS/network issue")
