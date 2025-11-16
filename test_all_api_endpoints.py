"""
Comprehensive API Endpoint Testing Script

Tests all API endpoints to verify:
1. Which database they're using (SQLite vs Supabase)
2. Response status codes
3. Authentication requirements
4. Database connection methods

Usage:
    python test_all_api_endpoints.py
    python test_all_api_endpoints.py --backend http://localhost:5001
    python test_all_api_endpoints.py --backend https://ai-agents-backend-singapore.onrender.com
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple
import argparse

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.RESET}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")


class APITester:
    """Test all API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'auth_required': 0,
            'endpoints': []
        }
        
        # Define all endpoints to test
        self.endpoints = [
            # Health & Info
            {'method': 'GET', 'path': '/health', 'name': 'Health Check', 'auth': False},
            {'method': 'GET', 'path': '/api/info', 'name': 'API Info', 'auth': False},
            
            # Authentication
            {'method': 'POST', 'path': '/api/auth/login', 'name': 'Login', 'auth': False, 
             'body': {'username': 'test', 'password': 'test'}},
            {'method': 'GET', 'path': '/api/auth/verify', 'name': 'Verify Token', 'auth': True},
            {'method': 'GET', 'path': '/api/auth/profile', 'name': 'Get Profile', 'auth': True},
            
            # Threads
            {'method': 'GET', 'path': '/api/threads/list', 'name': 'List Threads', 'auth': True},
            {'method': 'GET', 'path': '/api/threads/stats', 'name': 'Thread Stats', 'auth': True},
            
            # Automation
            {'method': 'GET', 'path': '/api/automation/list', 'name': 'List Automations', 'auth': True},
            
            # Agent
            {'method': 'POST', 'path': '/api/agent/chat', 'name': 'Agent Chat', 'auth': True,
             'body': {'message': 'test', 'user_id': 1}},
            
            # Synergy
            {'method': 'GET', 'path': '/api/synergy/sessions', 'name': 'Synergy Sessions', 'auth': True},
            
            # Internal Docs
            {'method': 'GET', 'path': '/api/internal-docs/list', 'name': 'List Internal Docs', 'auth': True},
            
            # Kanban Analytics
            {'method': 'GET', 'path': '/api/kanban-analytics/health', 'name': 'Kanban Health', 'auth': False},
            
            # InHouse Kanban
            {'method': 'GET', 'path': '/api/inhouse-kanban/health', 'name': 'InHouse Kanban Health', 'auth': False},
            
            # Render
            {'method': 'GET', 'path': '/api/render/services', 'name': 'Render Services', 'auth': True},
        ]
    
    def login(self, username: str = 'printing@inhouseprint.com.au', password: str = 'inhouseprint') -> bool:
        """Attempt to login and get token"""
        print_info(f"Attempting login with username: {username}")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={'username': username, 'password': password},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    print_success(f"Login successful! Token: {self.token[:20]}...")
                    return True
                else:
                    print_error(f"Login failed: {data.get('error', 'Unknown error')}")
            else:
                print_error(f"Login failed with status {response.status_code}")
                
        except Exception as e:
            print_error(f"Login error: {e}")
        
        return False
    
    def test_endpoint(self, endpoint: Dict) -> Dict:
        """Test a single endpoint"""
        method = endpoint['method']
        path = endpoint['path']
        name = endpoint['name']
        requires_auth = endpoint.get('auth', False)
        body = endpoint.get('body', None)
        
        url = f"{self.base_url}{path}"
        headers = {'Content-Type': 'application/json'}
        
        if requires_auth and self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        
        result = {
            'name': name,
            'method': method,
            'path': path,
            'requires_auth': requires_auth,
            'status_code': None,
            'response_time_ms': None,
            'error': None,
            'database_info': None
        }
        
        try:
            start_time = datetime.now()
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=body, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=body, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            result['status_code'] = response.status_code
            result['response_time_ms'] = round(response_time, 2)
            
            # Try to parse response
            try:
                data = response.json()
                # Check for database info in response
                if isinstance(data, dict):
                    if 'database' in data:
                        result['database_info'] = data['database']
                    elif 'db_type' in data:
                        result['database_info'] = data['db_type']
            except:
                pass
            
        except requests.exceptions.Timeout:
            result['error'] = 'Timeout (10s)'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection Error'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def print_result(self, result: Dict):
        """Print test result"""
        name = result['name']
        status = result['status_code']
        time_ms = result['response_time_ms']
        error = result['error']
        
        # Format output
        endpoint_str = f"{result['method']:6} {result['path']:45}"
        
        if error:
            print_error(f"{endpoint_str} | ERROR: {error}")
            self.results['failed'] += 1
        elif status is None:
            print_error(f"{endpoint_str} | NO RESPONSE")
            self.results['failed'] += 1
        elif status == 200:
            db_info = result.get('database_info', 'Unknown')
            print_success(f"{endpoint_str} | {status} | {time_ms}ms | DB: {db_info}")
            self.results['success'] += 1
        elif status == 401:
            print_warning(f"{endpoint_str} | {status} (Auth Required)")
            self.results['auth_required'] += 1
        elif status in [404, 405]:
            print_warning(f"{endpoint_str} | {status} (Not Found/Not Allowed)")
            self.results['failed'] += 1
        elif status == 500:
            print_error(f"{endpoint_str} | {status} (Server Error)")
            self.results['failed'] += 1
        else:
            print_warning(f"{endpoint_str} | {status}")
            self.results['failed'] += 1
        
        self.results['total'] += 1
        self.results['endpoints'].append(result)
    
    def run_tests(self):
        """Run all endpoint tests"""
        print_header("API ENDPOINT TESTING")
        
        print_info(f"Testing backend: {self.base_url}")
        print_info(f"Total endpoints to test: {len(self.endpoints)}\n")
        
        # Try to login first
        print_header("AUTHENTICATION")
        self.login()
        
        # Test all endpoints
        print_header("TESTING ENDPOINTS")
        
        for endpoint in self.endpoints:
            result = self.test_endpoint(endpoint)
            self.print_result(result)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print_header("TEST SUMMARY")
        
        total = self.results['total']
        success = self.results['success']
        failed = self.results['failed']
        auth_req = self.results['auth_required']
        
        print(f"Total Endpoints Tested: {total}")
        print_success(f"Successful (200): {success}")
        print_error(f"Failed (4xx/5xx): {failed}")
        print_warning(f"Auth Required (401): {auth_req}")
        
        success_rate = (success / total * 100) if total > 0 else 0
        print(f"\nSuccess Rate: {Colors.BOLD}{success_rate:.1f}%{Colors.RESET}")
        
        # Database analysis
        print_header("DATABASE ANALYSIS")
        
        sqlite_count = 0
        supabase_count = 0
        unknown_count = 0
        
        for result in self.results['endpoints']:
            db_info = result.get('database_info', 'Unknown')
            if db_info:
                if 'sqlite' in str(db_info).lower():
                    sqlite_count += 1
                elif 'supabase' in str(db_info).lower() or 'postgres' in str(db_info).lower():
                    supabase_count += 1
                else:
                    unknown_count += 1
        
        print(f"SQLite connections: {sqlite_count}")
        print(f"Supabase/PostgreSQL connections: {supabase_count}")
        print(f"Unknown/Not reported: {unknown_count}")
        
        # Save results to file
        self.save_results()
    
    def save_results(self):
        """Save results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"api_test_results_{timestamp}.json"
        
        output = {
            'timestamp': datetime.now().isoformat(),
            'backend_url': self.base_url,
            'summary': {
                'total': self.results['total'],
                'success': self.results['success'],
                'failed': self.results['failed'],
                'auth_required': self.results['auth_required']
            },
            'endpoints': self.results['endpoints']
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print_info(f"\nResults saved to: {filename}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Test AI Agent API endpoints')
    parser.add_argument('--backend', default='http://localhost:5001', 
                       help='Backend URL (default: http://localhost:5001)')
    parser.add_argument('--username', default='printing@inhouseprint.com.au',
                       help='Login username')
    parser.add_argument('--password', default='inhouseprint',
                       help='Login password')
    
    args = parser.parse_args()
    
    tester = APITester(base_url=args.backend)
    tester.run_tests()


if __name__ == '__main__':
    main()
