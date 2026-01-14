"""
Vector Database Endpoint Smoke Test
Comprehensive end-to-end testing of all vector database endpoints

Tests:
1. Credentials endpoints (load, save, status)
2. Embedding config endpoints (get, save)
3. Stats endpoint
4. Documents endpoint
5. Upload document endpoint (with mock file)
6. Connection validation

Usage:
    python test_vector_db_endpoints.py
"""

import requests
import json
import sys
import os
from datetime import datetime
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:5001"
TEST_USER_ID = 1
TEST_CUSTOMER_ID = 1

# ANSI color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(80)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")

def print_test(test_name):
    print(f"{BOLD}Testing: {test_name}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")

class VectorDBTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
        self.test_credentials = {
            'pinecone_api_key': 'test_key_123',
            'pinecone_environment': 'us-west1-gcp',
            'pinecone_index_name': 'test-index'
        }
        self.test_embedding_config = {
            'provider': 'openai',
            'model': 'text-embedding-ada-002',
            'dimension': 1536
        }

    def test_endpoint(self, method, endpoint, expected_status=200, data=None, files=None, description=""):
        """Generic endpoint tester"""
        url = f"{BASE_URL}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=data)
            elif method.upper() == 'POST':
                if files:
                    response = self.session.post(url, data=data, files=files)
                else:
                    response = self.session.post(url, json=data)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")

            print_info(f"{method} {endpoint}")
            print_info(f"Status: {response.status_code}")

            if response.status_code == expected_status:
                print_success(f"Status code matches expected ({expected_status})")
                self.results['passed'] += 1
                
                try:
                    json_response = response.json()
                    print_info(f"Response: {json.dumps(json_response, indent=2)[:500]}")
                    return True, json_response
                except:
                    print_warning("Response is not JSON")
                    return True, response.text
            else:
                print_error(f"Status code mismatch. Expected {expected_status}, got {response.status_code}")
                print_error(f"Response: {response.text[:500]}")
                self.results['failed'] += 1
                return False, None

        except requests.exceptions.ConnectionError:
            print_error(f"Connection failed - is Flask server running on {BASE_URL}?")
            self.results['failed'] += 1
            return False, None
        except Exception as e:
            print_error(f"Test failed with exception: {str(e)}")
            self.results['failed'] += 1
            return False, None

    def test_credentials_endpoints(self):
        """Test credential management endpoints"""
        print_header("CREDENTIALS ENDPOINTS")

        # Test 1: Load credentials (should work even if empty)
        print_test("Load Credentials")
        success, response = self.test_endpoint(
            'GET',
            f'/api/vector-db/credentials/load?user_id={TEST_USER_ID}',
            expected_status=200,
            description="Load existing credentials"
        )
        print()

        # Test 2: Save credentials
        print_test("Save Credentials")
        success, response = self.test_endpoint(
            'POST',
            '/api/vector-db/credentials/save',
            data={
                'user_id': TEST_USER_ID,
                'customer_id': TEST_CUSTOMER_ID,
                **self.test_credentials
            },
            expected_status=200,
            description="Save test credentials"
        )
        print()

        # Test 3: Check connection status
        print_test("Connection Status")
        success, response = self.test_endpoint(
            'GET',
            f'/api/vector-db/credentials/status?user_id={TEST_USER_ID}',
            expected_status=200,
            description="Check if credentials are valid"
        )
        print()

    def test_embedding_config_endpoints(self):
        """Test embedding configuration endpoints"""
        print_header("EMBEDDING CONFIG ENDPOINTS")

        # Test 1: Get embedding config
        print_test("Get Embedding Config")
        success, response = self.test_endpoint(
            'GET',
            f'/api/vector-db/embedding-config/get?user_id={TEST_USER_ID}',
            expected_status=200,
            description="Load embedding configuration"
        )
        print()

        # Test 2: Save embedding config
        print_test("Save Embedding Config")
        success, response = self.test_endpoint(
            'POST',
            '/api/vector-db/embedding-config/save',
            data={
                'user_id': TEST_USER_ID,
                'customer_id': TEST_CUSTOMER_ID,
                **self.test_embedding_config
            },
            expected_status=200,
            description="Save embedding configuration"
        )
        print()

    def test_stats_endpoint(self):
        """Test stats endpoint"""
        print_header("STATS ENDPOINT")

        print_test("Get Vector DB Stats")
        success, response = self.test_endpoint(
            'GET',
            f'/api/vector-db/stats?user_id={TEST_USER_ID}',
            expected_status=200,
            description="Get vector database statistics"
        )
        
        if success and response:
            stats = response.get('stats', {})
            print_info(f"Documents: {stats.get('documents', 0)}")
            print_info(f"Vectors: {stats.get('vectors', 0)}")
            print_info(f"Namespaces: {stats.get('namespaces', 0)}")
        print()

    def test_documents_endpoint(self):
        """Test documents listing endpoint"""
        print_header("DOCUMENTS ENDPOINT")

        print_test("List Documents")
        success, response = self.test_endpoint(
            'GET',
            f'/api/vector-db/documents?user_id={TEST_USER_ID}',
            expected_status=200,
            description="List all documents in vector DB"
        )
        
        if success and response:
            documents = response.get('documents', [])
            print_info(f"Total documents: {len(documents)}")
            if documents:
                print_info(f"First document: {documents[0].get('filename', 'N/A')}")
        print()

    def test_upload_endpoint(self):
        """Test document upload endpoint"""
        print_header("UPLOAD ENDPOINT")

        print_test("Upload Test Document")
        
        # Create a mock file
        mock_file_content = b"This is a test document for vector database upload testing. It contains sample text that will be processed and embedded."
        mock_file = BytesIO(mock_file_content)
        mock_file.name = 'test_document.txt'

        # Test upload (will likely fail without real credentials, but tests endpoint)
        success, response = self.test_endpoint(
            'POST',
            '/api/vector-db/upload-document',
            data={
                'user_id': TEST_USER_ID,
                'customer_id': TEST_CUSTOMER_ID,
                'chunk_size': 800,
                'chunk_overlap': 20,
                'namespace': 'test',
                'category': 'testing',
                'tags': json.dumps(['test', 'smoke-test']),
                'visibility': 'user'
            },
            files={
                'file': ('test_document.txt', mock_file, 'text/plain')
            },
            expected_status=200,
            description="Upload test document"
        )
        
        if not success:
            print_warning("Upload may fail without valid Pinecone credentials")
        print()

    def test_server_health(self):
        """Test if Flask server is running"""
        print_header("SERVER HEALTH CHECK")
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print_success(f"Flask server is running on {BASE_URL}")
                return True
            else:
                print_warning(f"Server responded with status {response.status_code}")
                return True
        except requests.exceptions.ConnectionError:
            print_error(f"Cannot connect to Flask server on {BASE_URL}")
            print_error("Please start the server with: cd AI_infrastructure && python flask_app.py")
            return False
        except Exception as e:
            print_error(f"Health check failed: {str(e)}")
            return False

    def run_all_tests(self):
        """Run complete test suite"""
        print_header("VECTOR DATABASE ENDPOINT SMOKE TEST")
        print_info(f"Base URL: {BASE_URL}")
        print_info(f"Test User ID: {TEST_USER_ID}")
        print_info(f"Test Customer ID: {TEST_CUSTOMER_ID}")
        print_info(f"Timestamp: {datetime.now().isoformat()}")

        # Check server health first
        if not self.test_server_health():
            print_error("\n❌ Server not available. Aborting tests.")
            return False

        # Run all endpoint tests
        self.test_credentials_endpoints()
        self.test_embedding_config_endpoints()
        self.test_stats_endpoint()
        self.test_documents_endpoint()
        self.test_upload_endpoint()

        # Print summary
        self.print_summary()
        
        return self.results['failed'] == 0

    def print_summary(self):
        """Print test results summary"""
        print_header("TEST SUMMARY")
        
        total = self.results['passed'] + self.results['failed']
        success_rate = (self.results['passed'] / total * 100) if total > 0 else 0
        
        print(f"{GREEN}Passed: {self.results['passed']}{RESET}")
        print(f"{RED}Failed: {self.results['failed']}{RESET}")
        print(f"{YELLOW}Warnings: {self.results['warnings']}{RESET}")
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if self.results['failed'] == 0:
            print(f"\n{GREEN}{BOLD}✓ ALL TESTS PASSED{RESET}")
        else:
            print(f"\n{RED}{BOLD}✗ SOME TESTS FAILED{RESET}")
        
        print()

def main():
    """Main test runner"""
    tester = VectorDBTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
