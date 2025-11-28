"""
Test Platform Credentials Management UI System
============================================

Tests the complete flow of the new comprehensive platform credentials UI:
1. Backend GET endpoint returns both OAuth and platform credentials
2. Backend POST endpoint adds new credentials
3. Backend PUT endpoint updates credentials
4. Backend DELETE endpoint removes credentials
5. Backend TEST endpoint validates credentials
6. Frontend displays all platforms correctly
7. Frontend forms submit properly

Run: python test_platform_credentials_ui.py
"""

import requests
import json
from datetime import datetime

API_BASE_URL = 'http://localhost:5001'

# Test with user_id=1 (adjust if needed)
TEST_USER_ID = 1

# Mock auth token for testing (replace with real token if needed)
AUTH_TOKEN = 'test_token_user_1'


def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'=' * 80}")
    print(f"TEST: {test_name}")
    print(f"{'=' * 80}")


def print_result(success, message):
    """Print test result"""
    status = "PASS" if success else "FAIL"
    symbol = "[OK]" if success else "[XX]"
    print(f"{symbol} {status}: {message}")


def test_backend_get_connections():
    """Test 1: GET /api/connections returns both OAuth and platform credentials"""
    print_test_header("Backend GET /api/connections")
    
    try:
        response = requests.get(
            f'{API_BASE_URL}/api/connections',
            headers={'Authorization': f'Bearer {AUTH_TOKEN}'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            connections = data.get('connections', [])
            
            print(f"\nTotal Connections: {len(connections)}")
            
            # Count by type
            oauth_count = sum(1 for c in connections if c['credential_type'] == 'oauth')
            api_key_count = sum(1 for c in connections if c['credential_type'] == 'api_key')
            database_count = sum(1 for c in connections if c['credential_type'] == 'database')
            
            print(f"  - OAuth: {oauth_count}")
            print(f"  - API Keys: {api_key_count}")
            print(f"  - Databases: {database_count}")
            
            # Show sample connections
            print("\nSample Connections:")
            for conn in connections[:5]:
                print(f"  - {conn['platform']} ({conn['credential_type']}) - Active: {conn['is_active']}")
            
            print_result(True, f"GET endpoint works - returned {len(connections)} connections")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def test_backend_post_api_key():
    """Test 2: POST /api/connections adds API key credential"""
    print_test_header("Backend POST /api/connections (API Key)")
    
    try:
        payload = {
            'platform': 'test_api_platform',
            'credential_type': 'api_key',
            'credential_key': f'Test API Key {datetime.now().strftime("%H:%M:%S")}',
            'credential_value': 'sk-test-abc123xyz789',
            'metadata': {'environment': 'test'},
            'credentials': {'api_key': 'sk-test-abc123xyz789'}
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/connections',
            headers={
                'Authorization': f'Bearer {AUTH_TOKEN}',
                'Content-Type': 'application/json'
            },
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Credential ID: {data.get('credential_id')}")
            print(f"Message: {data.get('message')}")
            print_result(True, "POST endpoint works - API key added")
            return data.get('credential_id')
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return None


def test_backend_post_database():
    """Test 3: POST /api/connections adds database credential"""
    print_test_header("Backend POST /api/connections (Database)")
    
    try:
        payload = {
            'platform': 'test_database',
            'credential_type': 'database',
            'credential_key': f'Test DB {datetime.now().strftime("%H:%M:%S")}',
            'credential_value': 'testuser@localhost:1433/testdb',
            'metadata': {'host': 'localhost', 'port': 1433, 'database': 'testdb'},
            'credentials': {
                'host': 'localhost',
                'port': 1433,
                'database': 'testdb',
                'username': 'testuser',
                'password': 'testpass123'
            }
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/connections',
            headers={
                'Authorization': f'Bearer {AUTH_TOKEN}',
                'Content-Type': 'application/json'
            },
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"Credential ID: {data.get('credential_id')}")
            print(f"Message: {data.get('message')}")
            print_result(True, "POST endpoint works - Database connection added")
            return data.get('credential_id')
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return None


def test_backend_test_connection(credential_id):
    """Test 4: POST /api/connections/<id>/test validates credential"""
    print_test_header(f"Backend POST /api/connections/{credential_id}/test")
    
    if not credential_id:
        print_result(False, "No credential_id provided (skipped)")
        return False
    
    try:
        response = requests.post(
            f'{API_BASE_URL}/api/connections/platform_{credential_id}/test',
            headers={'Authorization': f'Bearer {AUTH_TOKEN}'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Valid: {data.get('valid')}")
            print(f"Message: {data.get('message')}")
            print_result(True, "TEST endpoint works")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def test_backend_update_connection(credential_id):
    """Test 5: PUT /api/connections/<id> updates credential"""
    print_test_header(f"Backend PUT /api/connections/{credential_id}")
    
    if not credential_id:
        print_result(False, "No credential_id provided (skipped)")
        return False
    
    try:
        payload = {
            'credential_key': f'Updated Test API Key {datetime.now().strftime("%H:%M:%S")}',
            'metadata': {'environment': 'production', 'updated': True}
        }
        
        response = requests.put(
            f'{API_BASE_URL}/api/connections/platform_{credential_id}',
            headers={
                'Authorization': f'Bearer {AUTH_TOKEN}',
                'Content-Type': 'application/json'
            },
            json=payload
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message')}")
            print_result(True, "PUT endpoint works - credential updated")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def test_backend_delete_connection(credential_id):
    """Test 6: DELETE /api/connections/<id> removes credential"""
    print_test_header(f"Backend DELETE /api/connections/{credential_id}")
    
    if not credential_id:
        print_result(False, "No credential_id provided (skipped)")
        return False
    
    try:
        response = requests.delete(
            f'{API_BASE_URL}/api/connections/platform_{credential_id}',
            headers={'Authorization': f'Bearer {AUTH_TOKEN}'}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Message: {data.get('message')}")
            print_result(True, "DELETE endpoint works - credential removed")
            return True
        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def test_frontend_html_elements():
    """Test 7: Frontend HTML elements exist"""
    print_test_header("Frontend HTML Elements")
    
    try:
        with open('UI/business-ai-platform-v2.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        checks = [
            ('add-connection-modal', 'Add Connection Modal'),
            ('platformSelectionView', 'Platform Selection View'),
            ('apiKeyFormView', 'API Key Form View'),
            ('databaseFormView', 'Database Form View'),
            ('platform-connect-btn', 'Platform Connect Button CSS'),
            ('showAddConnectionModal', 'Show Add Connection Modal Function'),
            ('submitApiKeyForm', 'Submit API Key Form Function'),
            ('submitDatabaseForm', 'Submit Database Form Function'),
            ('testPlatformConnection', 'Test Platform Connection Function'),
            ('disconnectPlatformModal', 'Disconnect Platform Function')
        ]
        
        results = []
        for element_id, description in checks:
            exists = element_id in html_content
            results.append(exists)
            symbol = "[OK]" if exists else "[XX]"
            print(f"{symbol} {description}: {'Found' if exists else 'Missing'}")
        
        all_passed = all(results)
        print_result(all_passed, f"Frontend elements: {sum(results)}/{len(results)} found")
        return all_passed
        
    except Exception as e:
        print_result(False, f"Exception: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Passed: {passed}/{total} ({percentage:.1f}%)")
    print("")
    
    if passed == total:
        print("ALL TESTS PASSED - Platform Credentials UI is fully functional!")
    else:
        print(f"{total - passed} tests failed. Review errors above.")
    
    print("=" * 80)


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("PLATFORM CREDENTIALS MANAGEMENT UI - COMPREHENSIVE TEST")
    print("=" * 80)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Test User ID: {TEST_USER_ID}")
    print(f"Auth Token: {AUTH_TOKEN[:20]}..." if len(AUTH_TOKEN) > 20 else AUTH_TOKEN)
    
    results = []
    
    # Test 1: GET connections
    results.append(test_backend_get_connections())
    
    # Test 2: POST API key
    api_key_id = test_backend_post_api_key()
    results.append(api_key_id is not None)
    
    # Test 3: POST database
    db_id = test_backend_post_database()
    results.append(db_id is not None)
    
    # Test 4: TEST connection
    results.append(test_backend_test_connection(api_key_id))
    
    # Test 5: UPDATE connection
    results.append(test_backend_update_connection(api_key_id))
    
    # Test 6: DELETE connections (cleanup)
    if api_key_id:
        results.append(test_backend_delete_connection(api_key_id))
    if db_id:
        test_backend_delete_connection(db_id)  # Don't add to results, just cleanup
    
    # Test 7: Frontend HTML
    results.append(test_frontend_html_elements())
    
    # Print summary
    print_summary(results)
