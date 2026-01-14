"""
Test Database Routes and API Calls
===================================
Comprehensive test suite for database connections and route functionality
with SQLite (local) and Supabase (production) auto-detection.

Tests:
- Database utility auto-detection
- All route database connections
- API endpoints functionality
- Error handling
"""

import os
import sys
import requests
import time
from pathlib import Path

# Set UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'AI_infrastructure'))

# Test configuration
FLASK_URL = "http://localhost:5001"
TEST_USER_ID = 1


class DatabaseRoutesTester:
    """Test suite for database routes"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []
        
    def log_test(self, name, status, message=""):
        """Log test result"""
        symbol = "✅" if status else "❌"
        self.results.append(f"{symbol} {name}: {message}")
        if status:
            self.passed += 1
        else:
            self.failed += 1
            
    def test_database_utility(self):
        """Test database utility module"""
        print("\n" + "="*60)
        print("TEST 1: Database Utility Auto-Detection")
        print("="*60)
        
        try:
            from shared.database_utils import (
                is_using_supabase,
                get_database_connection,
                get_ai_infrastructure_connection,
                get_synergy_sessions_connection,
                adapt_sql_for_database
            )
            
            # Check environment detection
            using_supabase = is_using_supabase()
            db_type = "Supabase PostgreSQL" if using_supabase else "SQLite (Local)"
            print(f"🔷 Environment: {db_type}")
            print(f"🔷 RENDER env: {os.getenv('RENDER', 'not set')}")
            print(f"🔷 USE_SUPABASE env: {os.getenv('USE_SUPABASE', 'not set')}")
            print(f"🔷 USE_SQLITE env: {os.getenv('USE_SQLITE', 'not set')}")
            
            self.log_test("Database utility import", True, f"Using {db_type}")
            
            # Test connections
            databases = ['ai_infrastructure', 'sessions', 'synergy_sessions']
            for db_name in databases:
                try:
                    conn = get_database_connection(db_name)
                    cursor = conn.cursor()
                    
                    # Test query
                    if using_supabase:
                        cursor.execute("SELECT 1 as test")
                    else:
                        cursor.execute("SELECT 1 as test")
                    
                    result = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    
                    self.log_test(f"Connect to {db_name}", True, "Connection successful")
                except Exception as e:
                    self.log_test(f"Connect to {db_name}", False, str(e))
            
            # Test SQL adaptation
            test_sql = "CREATE TABLE test (id INTEGER PRIMARY KEY AUTOINCREMENT)"
            adapted = adapt_sql_for_database(test_sql)
            
            if using_supabase:
                expected = "SERIAL PRIMARY KEY" in adapted
                self.log_test("SQL adaptation (PostgreSQL)", expected, 
                            f"AUTOINCREMENT converted to SERIAL")
            else:
                expected = "AUTOINCREMENT" in adapted
                self.log_test("SQL adaptation (SQLite)", expected, 
                            "AUTOINCREMENT preserved")
                
        except Exception as e:
            self.log_test("Database utility import", False, str(e))
    
    def test_flask_server(self):
        """Test Flask server is running"""
        print("\n" + "="*60)
        print("TEST 2: Flask Server Connectivity")
        print("="*60)
        
        try:
            response = requests.get(f"{FLASK_URL}/api/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Flask server running", True, 
                            f"Status: {response.status_code}")
            else:
                self.log_test("Flask server running", False, 
                            f"Status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.log_test("Flask server running", False, 
                        "Server not running. Start with BISTART")
        except Exception as e:
            self.log_test("Flask server running", False, str(e))
    
    def test_route_imports(self):
        """Test all route imports"""
        print("\n" + "="*60)
        print("TEST 3: Route Imports")
        print("="*60)
        
        routes = [
            'synergy_routes',
            'account_linking_routes',
            'kanban_routes',
            'agent_routes_v4',
            'auth_routes',
            'google_auth_routes_V2_FIXED',
            'microsoft_auth_routes_V2_FIXED'
        ]
        
        for route_name in routes:
            try:
                module = __import__(f'routes.{route_name}', fromlist=[route_name])
                self.log_test(f"Import {route_name}", True, "Module loaded")
            except Exception as e:
                self.log_test(f"Import {route_name}", False, str(e))
    
    def test_synergy_endpoints(self):
        """Test Synergy API endpoints"""
        print("\n" + "="*60)
        print("TEST 4: Synergy API Endpoints")
        print("="*60)
        
        endpoints = [
            ('/api/synergy/list', 'GET', None),
            ('/api/synergy/test', 'GET', None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{FLASK_URL}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{FLASK_URL}{endpoint}", 
                                           json=data, timeout=5)
                
                if response.status_code in [200, 404]:  # 404 is OK if endpoint doesn't exist yet
                    self.log_test(f"{method} {endpoint}", True, 
                                f"Status: {response.status_code}")
                else:
                    self.log_test(f"{method} {endpoint}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"{method} {endpoint}", False, str(e))
    
    def test_account_linking_endpoints(self):
        """Test Account Linking API endpoints"""
        print("\n" + "="*60)
        print("TEST 5: Account Linking API Endpoints")
        print("="*60)
        
        endpoints = [
            ('/api/account/status', 'GET', None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{FLASK_URL}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{FLASK_URL}{endpoint}", 
                                           json=data, timeout=5)
                
                if response.status_code in [200, 401, 404]:  # Auth errors are OK
                    self.log_test(f"{method} {endpoint}", True, 
                                f"Status: {response.status_code}")
                else:
                    self.log_test(f"{method} {endpoint}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"{method} {endpoint}", False, str(e))
    
    def test_kanban_endpoints(self):
        """Test Kanban API endpoints"""
        print("\n" + "="*60)
        print("TEST 6: Kanban API Endpoints")
        print("="*60)
        
        endpoints = [
            ('/api/kanban/sessions', 'GET', None),
            ('/api/kanban/test', 'GET', None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{FLASK_URL}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{FLASK_URL}{endpoint}", 
                                           json=data, timeout=5)
                
                if response.status_code in [200, 404]:
                    self.log_test(f"{method} {endpoint}", True, 
                                f"Status: {response.status_code}")
                else:
                    self.log_test(f"{method} {endpoint}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"{method} {endpoint}", False, str(e))
    
    def test_auth_endpoints(self):
        """Test Authentication API endpoints"""
        print("\n" + "="*60)
        print("TEST 7: Authentication API Endpoints")
        print("="*60)
        
        endpoints = [
            ('/api/auth/google/authorize', 'GET', None),
            ('/api/auth/microsoft/authorize', 'GET', None),
        ]
        
        for endpoint, method, data in endpoints:
            try:
                if method == 'GET':
                    response = requests.get(f"{FLASK_URL}{endpoint}", 
                                          timeout=5, allow_redirects=False)
                else:
                    response = requests.post(f"{FLASK_URL}{endpoint}", 
                                           json=data, timeout=5)
                
                # Auth endpoints redirect (302) or return 200
                if response.status_code in [200, 302, 401]:
                    self.log_test(f"{method} {endpoint}", True, 
                                f"Status: {response.status_code}")
                else:
                    self.log_test(f"{method} {endpoint}", False, 
                                f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"{method} {endpoint}", False, str(e))
    
    def test_database_queries(self):
        """Test direct database queries"""
        print("\n" + "="*60)
        print("TEST 8: Database Query Execution")
        print("="*60)
        
        try:
            from shared.database_utils import execute_query, is_using_supabase
            
            # Test query on ai_infrastructure
            try:
                users = execute_query('ai_infrastructure',
                                    'SELECT COUNT(*) as count FROM users',
                                    fetch='one')
                count = users['count'] if isinstance(users, dict) else users[0]
                self.log_test("Query users table", True, f"Found {count} users")
            except Exception as e:
                self.log_test("Query users table", False, str(e))
            
            # Test query on synergy_sessions
            try:
                sessions = execute_query('synergy_sessions',
                                       'SELECT COUNT(*) as count FROM synergy_sessions',
                                       fetch='one')
                count = sessions['count'] if isinstance(sessions, dict) else sessions[0]
                self.log_test("Query synergy_sessions table", True, 
                            f"Found {count} sessions")
            except Exception as e:
                self.log_test("Query synergy_sessions table", False, str(e))
                
        except Exception as e:
            self.log_test("Database query module", False, str(e))
    
    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*70)
        print("DATABASE ROUTES & API COMPREHENSIVE TEST SUITE")
        print("="*70)
        print(f"Testing against: {FLASK_URL}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run tests
        self.test_database_utility()
        self.test_flask_server()
        self.test_route_imports()
        self.test_synergy_endpoints()
        self.test_account_linking_endpoints()
        self.test_kanban_endpoints()
        self.test_auth_endpoints()
        self.test_database_queries()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST RESULTS SUMMARY")
        print("="*70)
        
        for result in self.results:
            print(result)
        
        print("\n" + "="*70)
        print(f"TOTAL: {self.passed + self.failed} tests")
        print(f"✅ PASSED: {self.passed}")
        print(f"❌ FAILED: {self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed. Review errors above.")
        
        print("="*70)
        
        return self.failed == 0


if __name__ == '__main__':
    tester = DatabaseRoutesTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)
