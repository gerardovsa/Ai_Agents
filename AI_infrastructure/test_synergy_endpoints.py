"""
Test Script for Synergy Testing Endpoints
==========================================
Verifies the new testing endpoints work correctly.

Usage:
    python test_synergy_endpoints.py
"""

import requests
import json
from datetime import datetime

# Base URL - update if running on different port
BASE_URL = "http://localhost:5000/api/synergy"

def print_header(title):
    """Print formatted test header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(test_name, response):
    """Print formatted test result"""
    status_icon = "✅" if response.status_code < 400 else "❌"
    print(f"\n{status_icon} {test_name}")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response Time: {response.elapsed.total_seconds():.3f}s")
    
    try:
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)[:500]}")
    except:
        print(f"   Response: {response.text[:500]}")

def test_smoke_endpoint():
    """Test the smoke test endpoint"""
    print_header("Smoke Test Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/test/smoke")
        print_result("GET /api/synergy/test/smoke", response)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n   Summary: {data.get('summary', 'N/A')}")
            print(f"   Duration: {data.get('duration_ms', 0):.2f}ms")
            
            # Show test breakdown
            if 'tests' in data:
                print("\n   Test Results:")
                for test_name, test_result in data['tests'].items():
                    status = test_result.get('status', 'UNKNOWN')
                    icon = "✅" if status == "PASS" else "❌"
                    duration = test_result.get('duration_ms', 0)
                    print(f"      {icon} {test_name}: {status} ({duration:.2f}ms)")
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_endpoints_list():
    """Test the endpoints list endpoint"""
    print_header("Endpoints List Test")
    
    try:
        response = requests.get(f"{BASE_URL}/test/endpoints")
        print_result("GET /api/synergy/test/endpoints", response)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n   Total Endpoints: {data.get('endpoint_count', 0)}")
            
            # Show first 10 endpoints
            if 'endpoints' in data:
                print("\n   Sample Endpoints:")
                for endpoint in data['endpoints'][:10]:
                    methods = ', '.join(endpoint.get('methods', []))
                    tested = "✅" if endpoint.get('tested') else "⚠️"
                    print(f"      {tested} {methods:12} {endpoint.get('path', '')}")
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_database_endpoint():
    """Test the database test endpoint"""
    print_header("Database Test Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/test/database")
        print_result("GET /api/synergy/test/database", response)
        
        if response.status_code == 200:
            data = response.json()
            
            # Show test breakdown
            if 'tests' in data:
                print("\n   Database Test Results:")
                for test_name, test_result in data['tests'].items():
                    status = test_result.get('status', 'UNKNOWN')
                    icon = "✅" if status == "PASS" else "❌"
                    duration = test_result.get('duration_ms', 0)
                    print(f"      {icon} {test_name}: {status} ({duration:.2f}ms)")
                    
                    # Show additional details
                    if test_name == 'connection_pool':
                        conn_count = test_result.get('connections_created', 0)
                        print(f"         Connections: {conn_count}")
                    elif test_name == 'query_performance':
                        simple_ms = test_result.get('simple_query_ms', 0)
                        complex_ms = test_result.get('complex_query_ms', 0)
                        print(f"         Simple: {simple_ms:.2f}ms, Complex: {complex_ms:.2f}ms")
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_compile_endpoint():
    """Test the compile test endpoint"""
    print_header("Compile Test Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/test/compile")
        print_result("GET /api/synergy/test/compile", response)
        
        if response.status_code == 200:
            data = response.json()
            
            # Show files tested
            if 'files_tested' in data:
                print("\n   Files Tested:")
                for file_result in data['files_tested']:
                    status = file_result.get('status', 'UNKNOWN')
                    icon = "✅" if status == "PASS" else "❌"
                    filename = file_result.get('file', '')
                    size = file_result.get('size_bytes', 0)
                    print(f"      {icon} {filename} ({size:,} bytes)")
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_health_endpoint():
    """Test the health check endpoint"""
    print_header("Health Check Endpoint")
    
    try:
        response = requests.get(f"{BASE_URL}/test/health")
        print_result("GET /api/synergy/test/health", response)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            icon = "✅" if status == "healthy" else "❌"
            print(f"\n   {icon} System Status: {status}")
            
            # Show system metrics
            if 'system' in data:
                sys = data['system']
                print(f"\n   System Metrics:")
                print(f"      Platform: {sys.get('platform', 'N/A')}")
                print(f"      Python: {sys.get('python_version', 'N/A')}")
                print(f"      CPU: {sys.get('cpu_percent', 0):.1f}% ({sys.get('cpu_count', 0)} cores)")
                print(f"      Memory: {sys.get('memory_percent', 0):.1f}%")
                print(f"      Disk: {sys.get('disk_percent', 0):.1f}%")
            
            # Show database status
            if 'database' in data:
                db_status = data['database'].get('status', 'unknown')
                db_icon = "✅" if db_status == "connected" else "❌"
                print(f"\n   {db_icon} Database: {db_status}")
        
        return response.status_code == 200
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  SYNERGY TESTING ENDPOINTS - VERIFICATION SCRIPT")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)
    
    results = {
        'Smoke Test': test_smoke_endpoint(),
        'Endpoints List': test_endpoints_list(),
        'Database Test': test_database_endpoint(),
        'Compile Test': test_compile_endpoint(),
        'Health Check': test_health_endpoint()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, passed_test in results.items():
        icon = "✅" if passed_test else "❌"
        print(f"   {icon} {test_name}")
    
    print(f"\n   Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n   🎉 All tests passed!")
        return 0
    else:
        print(f"\n   ⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
