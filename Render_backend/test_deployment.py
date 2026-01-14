#!/usr/bin/env python3
"""
Test Deployment - Comprehensive endpoint testing

This script tests all critical endpoints on a deployed Render service
to verify the deployment is working correctly.
"""

import os
import sys
import time
import json
import requests
from pathlib import Path
from dotenv import dotenv_values

def get_service_url():
    """Get service URL from command line or default"""
    if len(sys.argv) > 1:
        return sys.argv[1]
    else:
        # Default service URL
        return "https://ai-agents-backend-2oi8.onrender.com"

def test_health_endpoint(base_url):
    """Test /health endpoint"""
    url = f"{base_url}/health"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"    Health: {data.get('status', 'unknown')}")
            return True, data
        else:
            print(f"    Health endpoint failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"    Health endpoint error: {e}")
        return False, None

def test_api_status(base_url):
    """Test /api/status endpoint"""
    url = f"{base_url}/api/status"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            tools_count = data.get('tools_count', 0)
            print(f"    API Status: {tools_count} tools loaded")
            return True, data
        else:
            print(f"    API status failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"    API status error: {e}")
        return False, None

def test_tool_list(base_url):
    """Test /api/tools endpoint"""
    url = f"{base_url}/api/tools"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"    Tools endpoint: {len(tools)} tools available")
            return True, data
        else:
            print(f"    Tools endpoint failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"    Tools endpoint error: {e}")
        return False, None

def test_cors(base_url):
    """Test CORS headers"""
    url = f"{base_url}/health"
    
    try:
        response = requests.options(url, timeout=10)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
        }
        
        if cors_headers['Access-Control-Allow-Origin']:
            print(f"    CORS configured: {cors_headers['Access-Control-Allow-Origin']}")
            return True, cors_headers
        else:
            print(f"   ⚠️  CORS headers not found")
            return False, None
    except Exception as e:
        print(f"    CORS test error: {e}")
        return False, None

def test_response_time(base_url):
    """Test response time"""
    url = f"{base_url}/health"
    
    try:
        start = time.time()
        response = requests.get(url, timeout=30)
        elapsed = time.time() - start
        
        if response.status_code == 200:
            if elapsed < 1.0:
                print(f"    Response time: {elapsed:.2f}s (excellent)")
            elif elapsed < 3.0:
                print(f"    Response time: {elapsed:.2f}s (good)")
            else:
                print(f"   ⚠️  Response time: {elapsed:.2f}s (slow)")
            
            return True, elapsed
        else:
            print(f"    Response test failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"    Response time error: {e}")
        return False, None

def test_database_connection(base_url):
    """Test database connection via API"""
    url = f"{base_url}/api/status"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            db_status = data.get('database', {}).get('status', 'unknown')
            
            if db_status == 'connected':
                print(f"    Database: Connected")
                return True, data
            else:
                print(f"   ⚠️  Database: {db_status}")
                return False, None
        else:
            print(f"    Database test failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"    Database test error: {e}")
        return False, None

def main():
    print("=" * 70)
    print("🧪 Test Deployed Service")
    print("=" * 70)
    
    # Get service URL
    base_url = get_service_url()
    print(f"\n🌐 Testing service: {base_url}")
    
    # Run tests
    results = []
    
    print("\n1️⃣  Testing health endpoint...")
    success, data = test_health_endpoint(base_url)
    results.append(("Health", success))
    
    print("\n2️⃣  Testing API status...")
    success, data = test_api_status(base_url)
    results.append(("API Status", success))
    
    print("\n3️⃣  Testing tools endpoint...")
    success, data = test_tool_list(base_url)
    results.append(("Tools", success))
    
    print("\n4️⃣  Testing CORS configuration...")
    success, data = test_cors(base_url)
    results.append(("CORS", success))
    
    print("\n5️⃣  Testing response time...")
    success, elapsed = test_response_time(base_url)
    results.append(("Response Time", success))
    
    print("\n6️⃣  Testing database connection...")
    success, data = test_database_connection(base_url)
    results.append(("Database", success))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "" if success else ""
        print(f"   {status} {test_name}")
    
    print(f"\n   {passed}/{total} tests passed")
    
    if passed == total:
        print("\n All tests passed! Deployment is healthy.")
        print("\n📋 Next steps:")
        print("   1. Update OAuth redirect URLs:")
        print("      python Render_backend/update_oauth_redirects.py")
        print("   2. Downgrade to free plan (optional):")
        print("      python Render_backend/downgrade_to_free.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the deployment.")
        print("\n📋 Troubleshooting:")
        print("   1. Check logs: python Render_backend/fetch_logs.py")
        print("   2. View dashboard: https://dashboard.render.com")
        print("   3. Verify environment variables are set")
        return 1

if __name__ == "__main__":
    sys.exit(main())
