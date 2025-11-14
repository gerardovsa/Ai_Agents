"""
Test OAuth Endpoints on Render Production
==========================================

Tests both Google and Microsoft OAuth flows on the production Render deployment.

Usage:
    python test_oauth_production.py
"""

import requests
import sys
from urllib.parse import urlparse, parse_qs

# Production URLs
RENDER_URL = "https://ai-agents-backend-singapore.onrender.com"
LOCAL_URL = "http://localhost:5001"

def test_health_check(base_url):
    """Test if the server is responding"""
    print(f"\n{'='*60}")
    print(f"HEALTH CHECK: {base_url}")
    print('='*60)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Server is UP")
            print(f"   Status: {response.status_code}")
            try:
                data = response.json()
                print(f"   Response: {data}")
            except:
                print(f"   Response: {response.text[:100]}")
            return True
        else:
            print(f"❌ Server returned: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Server unreachable: {e}")
        return False


def test_google_oauth_redirect(base_url):
    """Test Google OAuth redirect URL generation"""
    print(f"\n{'='*60}")
    print(f"GOOGLE OAUTH: {base_url}")
    print('='*60)
    
    try:
        # Don't follow redirects - we want to inspect the redirect URL
        response = requests.get(
            f"{base_url}/api/auth/google/login",
            allow_redirects=False,
            timeout=10
        )
        
        if response.status_code in [302, 301]:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ OAuth redirect initiated")
            print(f"   Status: {response.status_code}")
            print(f"   Redirect to: {redirect_url[:80]}...")
            
            # Parse the redirect URL to check parameters
            if 'accounts.google.com' in redirect_url:
                print(f"   ✅ Redirecting to Google OAuth")
                
                # Extract redirect_uri parameter
                parsed = urlparse(redirect_url)
                params = parse_qs(parsed.query)
                
                if 'redirect_uri' in params:
                    redirect_uri = params['redirect_uri'][0]
                    print(f"   Redirect URI: {redirect_uri}")
                    
                    # Check if it's using the correct domain
                    if 'onrender.com' in redirect_uri and base_url == RENDER_URL:
                        print(f"   ✅ Using production redirect URI (Render)")
                    elif 'localhost' in redirect_uri and base_url == LOCAL_URL:
                        print(f"   ✅ Using localhost redirect URI (Development)")
                    elif 'localhost' in redirect_uri and base_url == RENDER_URL:
                        print(f"   ⚠️  WARNING: Production using localhost redirect URI!")
                        print(f"   This will cause OAuth failures on Render")
                    else:
                        print(f"   ⚠️  Unexpected redirect URI domain")
                        
                    # Check if HTTPS is used for production
                    if base_url == RENDER_URL and redirect_uri.startswith('http://'):
                        print(f"   ❌ ERROR: Using HTTP instead of HTTPS for production!")
                    elif base_url == RENDER_URL and redirect_uri.startswith('https://'):
                        print(f"   ✅ Using HTTPS for production")
                else:
                    print(f"   ⚠️  No redirect_uri parameter found")
                    
                if 'scope' in params:
                    scopes = params['scope'][0].split(' ')
                    print(f"   Scopes requested: {len(scopes)} scopes")
                    print(f"   Includes: {', '.join(scopes[:3])}...")
                    
                return True
            else:
                print(f"   ❌ Not redirecting to Google OAuth")
                return False
        else:
            print(f"❌ Expected redirect (302), got: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def test_microsoft_oauth_redirect(base_url):
    """Test Microsoft OAuth redirect URL generation"""
    print(f"\n{'='*60}")
    print(f"MICROSOFT OAUTH: {base_url}")
    print('='*60)
    
    try:
        # Don't follow redirects - we want to inspect the redirect URL
        response = requests.get(
            f"{base_url}/api/auth/microsoft/login",
            allow_redirects=False,
            timeout=10
        )
        
        if response.status_code in [302, 301]:
            redirect_url = response.headers.get('Location', '')
            print(f"✅ OAuth redirect initiated")
            print(f"   Status: {response.status_code}")
            print(f"   Redirect to: {redirect_url[:80]}...")
            
            # Parse the redirect URL to check parameters
            if 'login.microsoftonline.com' in redirect_url:
                print(f"   ✅ Redirecting to Microsoft OAuth")
                
                # Extract redirect_uri parameter
                parsed = urlparse(redirect_url)
                params = parse_qs(parsed.query)
                
                if 'redirect_uri' in params:
                    redirect_uri = params['redirect_uri'][0]
                    print(f"   Redirect URI: {redirect_uri}")
                    
                    # Check if it's using the correct domain
                    if 'onrender.com' in redirect_uri and base_url == RENDER_URL:
                        print(f"   ✅ Using production redirect URI (Render)")
                    elif 'localhost' in redirect_uri and base_url == LOCAL_URL:
                        print(f"   ✅ Using localhost redirect URI (Development)")
                    elif 'localhost' in redirect_uri and base_url == RENDER_URL:
                        print(f"   ⚠️  WARNING: Production using localhost redirect URI!")
                        print(f"   This will cause OAuth failures on Render")
                    else:
                        print(f"   ⚠️  Unexpected redirect URI domain")
                        
                    # Check if HTTPS is used for production
                    if base_url == RENDER_URL and redirect_uri.startswith('http://'):
                        print(f"   ❌ ERROR: Using HTTP instead of HTTPS for production!")
                    elif base_url == RENDER_URL and redirect_uri.startswith('https://'):
                        print(f"   ✅ Using HTTPS for production")
                else:
                    print(f"   ⚠️  No redirect_uri parameter found")
                    
                if 'scope' in params:
                    scopes = params['scope'][0].split(' ')
                    print(f"   Scopes requested: {len(scopes)} scopes")
                    print(f"   Includes: {', '.join(scopes[:3])}...")
                    
                return True
            else:
                print(f"   ❌ Not redirecting to Microsoft OAuth")
                return False
        else:
            print(f"❌ Expected redirect (302), got: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False


def test_api_endpoints(base_url):
    """Test basic API endpoints"""
    print(f"\n{'='*60}")
    print(f"API ENDPOINTS: {base_url}")
    print('='*60)
    
    endpoints = [
        "/api/health",
        "/api/auth/status",
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅" if response.status_code in [200, 401] else "❌"
            print(f"{status} {endpoint} → {response.status_code}")
            results.append(response.status_code in [200, 401])
        except Exception as e:
            print(f"❌ {endpoint} → Error: {str(e)[:50]}")
            results.append(False)
    
    return all(results)


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("OAUTH PRODUCTION TEST SUITE")
    print("="*60)
    print(f"Testing deployment at: {RENDER_URL}")
    print(f"Comparing with local: {LOCAL_URL}")
    print("="*60)
    
    results = {}
    
    # Test Production (Render)
    print(f"\n{'#'*60}")
    print("# PRODUCTION TESTS (Render)")
    print('#'*60)
    
    results['render_health'] = test_health_check(RENDER_URL)
    results['render_google'] = test_google_oauth_redirect(RENDER_URL)
    results['render_microsoft'] = test_microsoft_oauth_redirect(RENDER_URL)
    results['render_api'] = test_api_endpoints(RENDER_URL)
    
    # Test Local (if available)
    print(f"\n{'#'*60}")
    print("# LOCAL TESTS (Development)")
    print('#'*60)
    
    local_available = test_health_check(LOCAL_URL)
    
    if local_available:
        results['local_google'] = test_google_oauth_redirect(LOCAL_URL)
        results['local_microsoft'] = test_microsoft_oauth_redirect(LOCAL_URL)
        results['local_api'] = test_api_endpoints(LOCAL_URL)
    else:
        print("\n⚠️  Local server not running - skipping local tests")
        print("   Start with: BISTART")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    print("\nProduction (Render):")
    print(f"  Health Check:     {'✅ PASS' if results.get('render_health') else '❌ FAIL'}")
    print(f"  Google OAuth:     {'✅ PASS' if results.get('render_google') else '❌ FAIL'}")
    print(f"  Microsoft OAuth:  {'✅ PASS' if results.get('render_microsoft') else '❌ FAIL'}")
    print(f"  API Endpoints:    {'✅ PASS' if results.get('render_api') else '❌ FAIL'}")
    
    if local_available:
        print("\nLocal (Development):")
        print(f"  Google OAuth:     {'✅ PASS' if results.get('local_google') else '❌ FAIL'}")
        print(f"  Microsoft OAuth:  {'✅ PASS' if results.get('local_microsoft') else '❌ FAIL'}")
        print(f"  API Endpoints:    {'✅ PASS' if results.get('local_api') else '❌ FAIL'}")
    
    # Overall status
    production_pass = all([
        results.get('render_health'),
        results.get('render_google'),
        results.get('render_microsoft')
    ])
    
    print("\n" + "="*60)
    if production_pass:
        print("🎉 ALL PRODUCTION TESTS PASSED!")
        print("\nNext Steps:")
        print("1. ✅ Code is deployed correctly")
        print("2. ⚠️  Add production redirect URI to Google Cloud Console:")
        print(f"   {RENDER_URL}/api/auth/google/callback")
        print("3. ⚠️  Add production redirect URI to Azure AD:")
        print(f"   {RENDER_URL}/api/auth/microsoft/callback")
        print("4. 🧪 Test OAuth login from browser:")
        print(f"   {RENDER_URL}")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nCheck the detailed output above for specific issues.")
    print("="*60)
    
    return 0 if production_pass else 1


if __name__ == "__main__":
    sys.exit(main())
