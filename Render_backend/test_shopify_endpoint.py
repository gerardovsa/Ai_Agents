"""
Test Shopify Dashboard Endpoint and Get Error Details
"""

import requests
import json

FLASK_URL = "https://inhouseprint-flask.onrender.com"

print("=" * 80)
print("TESTING SHOPIFY DASHBOARD ENDPOINT")
print("=" * 80)

print(f"\nURL: {FLASK_URL}/shopify-dashboard")

try:
    response = requests.get(f"{FLASK_URL}/shopify-dashboard", timeout=30)
    print(f"\n Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print(f" SUCCESS! Page loaded successfully")
        print(f"   Content Length: {len(response.content)} bytes")
    else:
        print(f" ERROR! Status {response.status_code}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")
        
        print(f"\nResponse Body:")
        print(response.text[:2000])  # First 2000 characters
        
except requests.Timeout:
    print(f" TIMEOUT after 30s")
except requests.ConnectionError as e:
    print(f" CONNECTION ERROR: {e}")
except Exception as e:
    print(f" ERROR: {e}")

# Also test other working endpoints for comparison
print("\n" + "=" * 80)
print("TESTING OTHER ENDPOINTS (For Comparison)")
print("=" * 80)

endpoints = [
    "/",
    "/stock",
    "/api/stock/master"
]

for endpoint in endpoints:
    try:
        response = requests.get(f"{FLASK_URL}{endpoint}", timeout=10)
        print(f"\n{endpoint}: {response.status_code}")
    except Exception as e:
        print(f"\n{endpoint}: ERROR - {e}")

print("\n" + "=" * 80)
