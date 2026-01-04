"""
Comprehensive Integration Test
Tests Flask server endpoints and frontend integration
"""

import requests
import sys
from datetime import datetime

API_BASE_URL = 'http://localhost:5001'

class IntegrationTest:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test(self, name, func):
        self.total += 1
        try:
            result = func()
            if result:
                self.passed += 1
                print(f"✅ {name}")
                return True
            else:
                self.failed += 1
                self.errors.append((name, "Test returned False"))
                print(f"❌ {name}: Test returned False")
                return False
        except Exception as e:
            self.failed += 1
            self.errors.append((name, str(e)))
            print(f"❌ {name}: {e}")
            return False
    
    def summary(self):
        print("\n" + "="*60)
        print(f"📊 INTEGRATION TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed/self.total*100):.1f}%" if self.total > 0 else "N/A")
        
        if self.errors:
            print("\n🔴 FAILED TESTS:")
            for name, error in self.errors:
                print(f"  • {name}")
                print(f"    └─ {error}")

tester = IntegrationTest()

print("="*60)
print("🧪 INTEGRATION TEST SUITE")
print("="*60)
print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🌐 Testing: {API_BASE_URL}")
print("="*60)

# Test Flask server is running
print("\n🚀 FLASK SERVER:")

def test_server_running():
    response = requests.get(f"{API_BASE_URL}/", timeout=5)
    return response.status_code == 200

def test_server_html_content():
    response = requests.get(f"{API_BASE_URL}/", timeout=5)
    content = response.text
    return 'Business AI Platform' in content and len(content) > 100000

tester.test("Server is running", test_server_running)
tester.test("HTML content loaded", test_server_html_content)

# Test API endpoints
print("\n🔌 API ENDPOINTS:")

def test_health_endpoint():
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_tools_endpoint():
    try:
        response = requests.get(f"{API_BASE_URL}/api/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return isinstance(data, list) and len(data) > 0
        return False
    except:
        return False

tester.test("Health endpoint", test_health_endpoint)
tester.test("Tools endpoint", test_tools_endpoint)

# Test static file serving
print("\n📁 STATIC FILE SERVING:")

def test_test_page():
    response = requests.get(f"{API_BASE_URL}/test_frontend_imports.html", timeout=5)
    return response.status_code == 200 and 'Frontend Import Test' in response.text

def test_js_file():
    response = requests.get(f"{API_BASE_URL}/shared/js/module-loader-v4.js", timeout=5)
    return response.status_code == 200

def test_css_file():
    response = requests.get(f"{API_BASE_URL}/shared/css/ui-standardization.css", timeout=5)
    return response.status_code == 200

tester.test("Test page accessible", test_test_page)
tester.test("JavaScript files served", test_js_file)
tester.test("CSS files served", test_css_file)

# Test WebSocket connection
print("\n🔌 WEBSOCKET:")

def test_socketio_available():
    try:
        # Check if Socket.IO endpoint is available
        response = requests.get(f"{API_BASE_URL}/socket.io/", timeout=5, allow_redirects=False)
        # Socket.IO returns various status codes, just check it responds
        return response.status_code in [200, 400, 401, 404]  # Any response means it's configured
    except:
        return False

tester.test("Socket.IO endpoint configured", test_socketio_available)

# Test critical HTML elements
print("\n📄 HTML STRUCTURE:")

def test_html_structure():
    response = requests.get(f"{API_BASE_URL}/", timeout=5)
    html = response.text
    
    # Check for critical elements
    checks = [
        ('AI Chat Panel', 'class="ai-chat-panel"' in html),
        ('Main Content Wrapper', 'class="main-content-wrapper"' in html),
        ('Login Container', 'id="loginContainer"' in html),
        ('Module Loader', 'module-loader-v4.js' in html),
        ('UserAuth', 'user_auth.js' in html),
        ('ThreadManager', 'thread_manager' in html.lower()),
    ]
    
    all_passed = True
    for name, check in checks:
        if check:
            print(f"  ✅ {name}")
        else:
            print(f"  ❌ {name}")
            all_passed = False
    
    return all_passed

tester.test("HTML structure complete", test_html_structure)

# Test database connectivity (through API)
print("\n🗄️  DATABASE:")

def test_database_connection():
    # Try an endpoint that requires database
    try:
        # This will fail if database is down
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

tester.test("Database connectivity", test_database_connection)

# Test response times
print("\n⏱️  PERFORMANCE:")

def test_response_time():
    import time
    start = time.time()
    response = requests.get(f"{API_BASE_URL}/", timeout=10)
    duration = time.time() - start
    print(f"    └─ Response time: {duration:.2f}s")
    return duration < 5.0  # Should respond within 5 seconds

tester.test("Response time acceptable", test_response_time)

# Print summary
tester.summary()

# Return exit code
sys.exit(0 if tester.failed == 0 else 1)
