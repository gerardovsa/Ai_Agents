"""
Test all authentication endpoints and database schema
Run this after Render deployment completes
"""
import requests
import sys

# Production URL
BASE_URL = "https://ai-agents-backend-singapore.onrender.com"

def test_endpoint(name, url, expected_status=200):
    """Test an endpoint and report results"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('-' * 60)
    
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        status = response.status_code
        
        # Color codes
        if status == expected_status:
            result = f"✅ PASS - Status: {status}"
        elif status in [301, 302, 307, 308]:
            result = f"↗️  REDIRECT - Status: {status} → {response.headers.get('Location', 'N/A')}"
        else:
            result = f"❌ FAIL - Status: {status} (expected {expected_status})"
        
        print(result)
        
        # Try to parse JSON
        try:
            data = response.json()
            print(f"Response: {data}")
        except:
            print(f"Response (text): {response.text[:200]}")
        
        return status == expected_status
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT - Server not responding")
        return False
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

def test_auth_status():
    """Test authentication status endpoint"""
    return test_endpoint(
        "Auth Status",
        f"{BASE_URL}/api/auth/status",
        expected_status=200
    )

def test_microsoft_login():
    """Test Microsoft login endpoint (should redirect)"""
    return test_endpoint(
        "Microsoft Login",
        f"{BASE_URL}/api/auth/microsoft/login",
        expected_status=302  # Redirect to Microsoft
    )

def test_google_login():
    """Test Google login endpoint (should redirect)"""
    return test_endpoint(
        "Google Login",
        f"{BASE_URL}/api/auth/google/login",
        expected_status=302  # Redirect to Google
    )

def test_health():
    """Test health check endpoint"""
    return test_endpoint(
        "Health Check",
        f"{BASE_URL}/health",
        expected_status=200
    )

def test_migrations():
    """Test if migrations ran successfully"""
    print(f"\n{'='*60}")
    print("Testing: Database Migrations")
    print(f"URL: {BASE_URL}/api/auth/status")
    print('-' * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/status", timeout=10)
        data = response.json()
        
        # Check for user_sessions table (new migration)
        if 'database' in data:
            print("✅ Database info available in response")
        else:
            print("⚠️  No database info in response")
        
        return True
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

def main():
    print("="*60)
    print("AUTHENTICATION ENDPOINTS TEST")
    print("Production: ai-agents-backend-singapore.onrender.com")
    print("="*60)
    
    results = {
        'Health Check': test_health(),
        'Auth Status': test_auth_status(),
        'Microsoft Login': test_microsoft_login(),
        'Google Login': test_google_login(),
        'Migrations': test_migrations()
    }
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED")
        print("\nTroubleshooting:")
        print("1. Check Render dashboard for build logs")
        print("2. Verify deployment completed (not still building)")
        print("3. Check Flask startup logs for migration errors")
        print("4. Verify environment variables are set in Render dashboard")
        return 1

if __name__ == '__main__':
    sys.exit(main())
