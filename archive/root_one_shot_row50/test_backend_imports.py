"""
Backend Import Test Suite
Tests all Python imports, dependencies, and modules from flask_app.py
"""

import sys
import os
from datetime import datetime

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, name):
        self.total += 1
        self.passed += 1
        print(f"✅ {name}")
    
    def add_fail(self, name, error):
        self.total += 1
        self.failed += 1
        self.errors.append((name, str(error)))
        print(f"❌ {name}: {error}")
    
    def summary(self):
        print("\n" + "="*60)
        print(f"📊 TEST SUMMARY")
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

results = TestResult()

print("="*60)
print("🧪 BACKEND IMPORT TEST SUITE")
print("="*60)
print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"🐍 Python: {sys.version.split()[0]}")
print("="*60)

# Core Flask Dependencies
print("\n📦 CORE FLASK DEPENDENCIES:")
tests = [
    ('Flask', 'flask'),
    ('Flask-SocketIO', 'flask_socketio'),
    ('Flask-CORS', 'flask_cors'),
    ('Werkzeug', 'werkzeug'),
]

for name, module in tests:
    try:
        __import__(module)
        results.add_pass(name)
    except Exception as e:
        results.add_fail(name, e)

# Database Dependencies
print("\n🗄️  DATABASE DEPENDENCIES:")
tests = [
    ('psycopg2', 'psycopg2'),
    ('psycopg2.pool', 'psycopg2.pool'),
]

for name, module in tests:
    try:
        __import__(module)
        results.add_pass(name)
    except Exception as e:
        results.add_fail(name, e)

# AI/ML Dependencies
print("\n🤖 AI/ML DEPENDENCIES:")
tests = [
    ('anthropic', 'anthropic'),
    ('openai', 'openai'),
]

for name, module in tests:
    try:
        __import__(module)
        results.add_pass(name)
    except Exception as e:
        results.add_fail(name, e)

# Data Processing
print("\n📊 DATA PROCESSING:")
tests = [
    ('pandas', 'pandas'),
    ('numpy', 'numpy'),
    ('asteval', 'asteval'),
]

for name, module in tests:
    try:
        __import__(module)
        results.add_pass(name)
    except Exception as e:
        results.add_fail(name, e)

# API Integrations
print("\n🔌 API INTEGRATIONS:")
tests = [
    ('xero-python', 'xero_python'),
    ('shopify', 'shopify'),
    ('google-api-python-client', 'googleapiclient'),
    ('requests', 'requests'),
]

for name, module in tests:
    try:
        __import__(module)
        results.add_pass(name)
    except Exception as e:
        results.add_fail(name, e)

# Internal Modules
print("\n🔧 INTERNAL MODULES:")

# Check if key directories exist
directories = [
    ('AI_infrastructure/', 'AI_infrastructure'),
    ('AI_infrastructure/shared/', 'AI_infrastructure/shared'),
    ('AI_infrastructure/tools/', 'AI_infrastructure/tools'),
    ('UI/', 'UI'),
    ('UI/modules_external/', 'UI/modules_external'),
]

for name, path in directories:
    try:
        full_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.exists(full_path):
            results.add_pass(f"Directory: {name}")
        else:
            results.add_fail(f"Directory: {name}", "Directory not found")
    except Exception as e:
        results.add_fail(f"Directory: {name}", e)

# Check key internal modules
internal_modules = [
    ('database_utils', 'AI_infrastructure.shared.database_utils'),
    ('supabase_client', 'AI_infrastructure.shared.supabase_client'),
]

for name, module in internal_modules:
    try:
        __import__(module)
        results.add_pass(f"Internal: {name}")
    except Exception as e:
        results.add_fail(f"Internal: {name}", e)

# Environment Variables
print("\n🔐 ENVIRONMENT VARIABLES:")
env_vars = [
    'SUPABASE_URL',
    'SUPABASE_KEY',
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
]

for var in env_vars:
    try:
        value = os.environ.get(var)
        if value:
            # Show first 10 chars for security
            masked = value[:10] + "..." if len(value) > 10 else value
            results.add_pass(f"ENV: {var} = {masked}")
        else:
            results.add_fail(f"ENV: {var}", "Not set")
    except Exception as e:
        results.add_fail(f"ENV: {var}", e)

# Flask App Configuration
print("\n⚙️  FLASK APP CONFIGURATION:")
try:
    # Try importing flask_app to check configuration
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))
    
    # Check if flask_app.py exists
    flask_path = os.path.join(os.path.dirname(__file__), 'AI_infrastructure', 'flask_app.py')
    if os.path.exists(flask_path):
        results.add_pass("flask_app.py exists")
        
        # Read file and check for key patterns
        with open(flask_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        patterns = {
            'Flask app initialization': '@app.route',
            'SocketIO setup': 'socketio',
            'CORS configuration': 'CORS',
            'Database connection': 'execute_query',
            'Tool registry': 'registry',
        }
        
        for name, pattern in patterns.items():
            if pattern in content:
                results.add_pass(f"Pattern: {name}")
            else:
                results.add_fail(f"Pattern: {name}", "Pattern not found in flask_app.py")
    else:
        results.add_fail("flask_app.py", "File not found")
except Exception as e:
    results.add_fail("Flask App Check", e)

# Check HTML file
print("\n📄 FRONTEND FILES:")
html_path = os.path.join(os.path.dirname(__file__), 'UI', 'business-ai-platform-v2.html')
if os.path.exists(html_path):
    results.add_pass("business-ai-platform-v2.html exists")
    
    # Get file size
    size = os.path.getsize(html_path)
    size_kb = size / 1024
    print(f"   └─ File size: {size_kb:.1f} KB")
    
    # Count lines
    with open(html_path, 'r', encoding='utf-8') as f:
        lines = len(f.readlines())
    print(f"   └─ Total lines: {lines:,}")
    
    if lines > 20000:  # Expected to be large
        results.add_pass("HTML file has expected size")
    else:
        results.add_fail("HTML file size", f"Only {lines} lines, expected >20,000")
else:
    results.add_fail("business-ai-platform-v2.html", "File not found")

# Check CSS file
css_path = os.path.join(os.path.dirname(__file__), 'UI', 'business-ai-platform-v2.css')
if os.path.exists(css_path):
    results.add_pass("business-ai-platform-v2.css exists")
else:
    results.add_fail("business-ai-platform-v2.css", "File not found")

# Print final summary
results.summary()

# Exit with error code if tests failed
sys.exit(0 if results.failed == 0 else 1)
