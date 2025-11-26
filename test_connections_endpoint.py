"""
Test Connections API Endpoint
=============================
Tests the /api/connections endpoint to verify it's working correctly.
"""

import requests
import json

# Test configuration
API_BASE_URL = 'http://localhost:5001'
TEST_TOKEN = None  # Will use mock credentials for testing

def test_connections_endpoint():
    """Test the connections endpoint without authentication (should fail gracefully)"""
    print("=" * 60)
    print("TESTING CONNECTIONS API ENDPOINT")
    print("=" * 60)
    
    # Test 1: Access without auth token (should return 401)
    print("\n[TEST 1] Testing endpoint without authentication...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/connections')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ PASS: Endpoint requires authentication (401)")
        else:
            print(f"⚠️  Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    # Test 2: Check if endpoint is registered
    print("\n[TEST 2] Checking if /api/connections endpoint exists...")
    try:
        response = requests.get(f'{API_BASE_URL}/api/connections')
        
        if response.status_code in [200, 401, 403]:
            print("✅ PASS: Endpoint is registered and responding")
        elif response.status_code == 404:
            print("❌ FAIL: Endpoint not found (404)")
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Cannot connect to server. Is it running?")
        print("Run: BISTART")
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    test_connections_endpoint()
