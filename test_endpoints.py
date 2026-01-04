#!/usr/bin/env python3
"""Test Flask endpoints while server is running."""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def test_connection_stats():
    """Test the admin connection stats endpoint."""
    print("Testing /api/admin/connection-stats...")
    try:
        resp = requests.get(f"{BASE_URL}/api/admin/connection-stats", timeout=5)
        print(f"✅ Status: {resp.status_code}")
        print(f"   Response: {json.dumps(resp.json(), indent=2)}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_health_check():
    """Test basic health check."""
    print("\nTesting health check...")
    try:
        resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"✅ Status: {resp.status_code}")
        print(f"   Response: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == '__main__':
    print("Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    success = True
    success = test_health_check() and success
    success = test_connection_stats() and success
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL ENDPOINT TESTS PASSED")
    else:
        print("❌ SOME ENDPOINT TESTS FAILED")
    print("="*60)
