"""
BUSINESS AI PLATFORM V2 - COMPLETE SMOKE TEST
Tests all routes, database connections, and module integrations
"""

import sys
import os
sys.path.insert(0, 'AI_infrastructure')

import requests
import json
from pathlib import Path

# Color output for PowerShell
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.YELLOW}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

def print_section(text):
    print(f"\n{Colors.CYAN}{'-' * 80}{Colors.RESET}")
    print(f"{Colors.WHITE}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'-' * 80}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}   {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}   {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}   {text}{Colors.RESET}")

# Test results tracking
test_results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0
}

# Base URL for Flask server
BASE_URL = "http://localhost:5001"

print_header("BUSINESS AI PLATFORM V2 - COMPLETE SMOKE TEST")

# ============================================================================
# TEST 1: Database Connections
# ============================================================================
print_section("TEST 1: Database Connections (Supabase)")

try:
    from shared.database_utils import get_database_connection, is_using_supabase
    
    print(f"   Database Mode: {'Supabase PostgreSQL' if is_using_supabase() else 'SQLite (Legacy)'}")
    
    if is_using_supabase():
        print_success("Using Supabase PostgreSQL")
        test_results['passed'] += 1
    else:
        print_warning("Using SQLite (should be Supabase in production)")
        test_results['warnings'] += 1
    
    # Test ai_infrastructure schema
    try:
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print_success("ai_infrastructure schema: CONNECTED")
        test_results['passed'] += 1
    except Exception as e:
        print_error(f"ai_infrastructure schema: FAILED - {e}")
        test_results['failed'] += 1
    
    # Test sessions schema
    try:
        conn = get_database_connection('sessions')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print_success("sessions schema: CONNECTED")
        test_results['passed'] += 1
    except Exception as e:
        print_error(f"sessions schema: FAILED - {e}")
        test_results['failed'] += 1
    
    # Test synergy_sessions schema
    try:
        conn = get_database_connection('synergy_sessions')
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print_success("synergy_sessions schema: CONNECTED")
        test_results['passed'] += 1
    except Exception as e:
        print_error(f"synergy_sessions schema: FAILED - {e}")
        test_results['failed'] += 1
        
except Exception as e:
    print_error(f"Database connection test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 2: Flask Server Status
# ============================================================================
print_section("TEST 2: Flask Server Status")

try:
    response = requests.get(f"{BASE_URL}/api/health", timeout=5)
    if response.status_code == 200:
        print_success(f"Flask server: RUNNING on port 5001")
        test_results['passed'] += 1
    else:
        print_error(f"Flask server: UNHEALTHY (status {response.status_code})")
        test_results['failed'] += 1
except requests.exceptions.ConnectionError:
    print_error("Flask server: NOT RUNNING (connection refused)")
    print_warning("Run 'BISTART' to start the server")
    test_results['failed'] += 1
except Exception as e:
    print_error(f"Flask server test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 3: Authentication Routes
# ============================================================================
print_section("TEST 3: Authentication Routes - /api/auth/*")

try:
    response = requests.get(f"{BASE_URL}/api/auth/platforms", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print_success(f"/api/auth/platforms: SUCCESS")
        if isinstance(data, dict) and 'platforms' in data:
            print_success(f"   Found {len(data['platforms'])} platform configurations")
        test_results['passed'] += 1
    else:
        print_error(f"/api/auth/platforms: FAILED (status {response.status_code})")
        test_results['failed'] += 1
except Exception as e:
    print_error(f"Authentication routes test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 4: Thread Management Routes
# ============================================================================
print_section("TEST 4: Thread Management Routes - /api/threads/*")

try:
    # Test list threads
    response = requests.get(f"{BASE_URL}/api/threads/list", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print_success(f"/api/threads/list: SUCCESS")
        if isinstance(data, list):
            print_success(f"   Found {len(data)} threads")
            active_count = sum(1 for t in data if not t.get('archived', False))
            print_success(f"   Active threads: {active_count}")
        test_results['passed'] += 1
    else:
        print_error(f"/api/threads/list: FAILED (status {response.status_code})")
        test_results['failed'] += 1
except Exception as e:
    print_error(f"Thread management routes test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 5: Automation Canvas Routes
# ============================================================================
print_section("TEST 5: Automation Canvas Routes - /api/automation/*")

try:
    response = requests.get(f"{BASE_URL}/api/automation/workflows", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print_success(f"/api/automation/workflows: SUCCESS")
        if isinstance(data, list):
            print_success(f"   Found {len(data)} workflows")
        test_results['passed'] += 1
    else:
        print_error(f"/api/automation/workflows: FAILED (status {response.status_code})")
        test_results['failed'] += 1
except Exception as e:
    print_error(f"Automation routes test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 6: Synergy Dashboard Routes
# ============================================================================
print_section("TEST 6: Synergy Dashboard Routes - /api/kanban/*")

try:
    response = requests.get(f"{BASE_URL}/api/kanban/sessions", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print_success(f"/api/kanban/sessions: SUCCESS")
        if isinstance(data, list):
            print_success(f"   Found {len(data)} Kanban cards")
            # Count by column
            columns = {}
            for card in data:
                col = card.get('column_name', 'unknown')
                columns[col] = columns.get(col, 0) + 1
            for col, count in columns.items():
                print_success(f"   {col}: {count} cards")
        test_results['passed'] += 1
    else:
        print_error(f"/api/kanban/sessions: FAILED (status {response.status_code})")
        test_results['failed'] += 1
except Exception as e:
    print_error(f"Synergy routes test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 7: Agent Routes
# ============================================================================
print_section("TEST 7: AI Agent Routes - /api/agent/*")

try:
    # Test Prime agent status
    response = requests.get(f"{BASE_URL}/api/agent/prime/status", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print_success(f"/api/agent/prime/status: SUCCESS")
        if 'status' in data:
            print_success(f"   Prime status: {data['status']}")
        test_results['passed'] += 1
    else:
        print_error(f"/api/agent/prime/status: FAILED (status {response.status_code})")
        test_results['failed'] += 1
    
    # Test agent-1 status
    response = requests.get(f"{BASE_URL}/api/agent/agent-1/status", timeout=5)
    if response.status_code == 200:
        print_success(f"/api/agent/agent-1/status: SUCCESS")
        test_results['passed'] += 1
    else:
        print_error(f"/api/agent/agent-1/status: FAILED (status {response.status_code})")
        test_results['failed'] += 1
        
except Exception as e:
    print_error(f"Agent routes test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 8: WooCommerce Routes
# ============================================================================
print_section("TEST 8: WooCommerce Routes - /api/woocommerce/*")

try:
    response = requests.get(f"{BASE_URL}/api/woocommerce/orders?limit=5", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print_success(f"/api/woocommerce/orders: SUCCESS")
        if isinstance(data, list):
            print_success(f"   Found {len(data)} orders")
        test_results['passed'] += 1
    elif response.status_code == 404:
        print_warning("/api/woocommerce/orders: NOT CONFIGURED (expected)")
        test_results['warnings'] += 1
    else:
        print_error(f"/api/woocommerce/orders: FAILED (status {response.status_code})")
        test_results['failed'] += 1
except Exception as e:
    print_warning(f"WooCommerce routes test: {e}")
    test_results['warnings'] += 1

# ============================================================================
# TEST 9: Module Discovery
# ============================================================================
print_section("TEST 9: Module Discovery - UI/modules/*")

try:
    from AI_infrastructure.core.module_blueprint_loader import ModuleBlueprintLoader
    
    loader = ModuleBlueprintLoader()
    modules = loader.discover_modules_with_routes()
    
    if modules:
        print_success(f"Found {len(modules)} modules with routes:")
        for module in modules:
            print_success(f"   - {module}")
        test_results['passed'] += 1
    else:
        print_warning("No modules with routes/ folders found")
        test_results['warnings'] += 1
        
except Exception as e:
    print_warning(f"Module discovery test failed: {e}")
    test_results['warnings'] += 1

# ============================================================================
# TEST 10: HTML File Structure
# ============================================================================
print_section("TEST 10: HTML File Structure - business-ai-platform-v2.html")

try:
    html_path = Path("UI/business-ai-platform-v2.html")
    if html_path.exists():
        content = html_path.read_text(encoding='utf-8')
        
        # Check for critical components
        checks = [
            ("Supabase JS library", "<script src=\"https://cdn.jsdelivr.net/npm/@supabase/supabase-js"),
            ("ThreadManager", "ThreadManager"),
            ("AutomationCanvas", "AutomationCanvas"),
            ("SynergyBoard", "SynergyBoard"),
            ("MultiAgent", "MultiAgent"),
            ("window.SUPABASE_URL", "window.SUPABASE_URL"),
            ("window.SUPABASE_ANON_KEY", "window.SUPABASE_ANON_KEY"),
        ]
        
        for name, pattern in checks:
            if pattern in content:
                print_success(f"{name}: FOUND")
                test_results['passed'] += 1
            else:
                print_error(f"{name}: NOT FOUND")
                test_results['failed'] += 1
    else:
        print_error("business-ai-platform-v2.html: NOT FOUND")
        test_results['failed'] += 1
        
except Exception as e:
    print_error(f"HTML structure test failed: {e}")
    test_results['failed'] += 1

# ============================================================================
# TEST 11: Module JavaScript Files
# ============================================================================
print_section("TEST 11: Module JavaScript Files - UI/modules/*")

module_files = [
    ("UI/modules/threads/components/thread_manager.js", "ThreadManager"),
    ("UI/modules/threads/components/user_auth.js", "UserAuth"),
    ("UI/modules/automation/components/automation_canvas.js", "AutomationCanvas"),
    ("UI/modules/synergy/components/synergy_board.js", "SynergyBoard"),
    ("UI/modules/multi_agent/components/multi_agent.js", "MultiAgent"),
]

for file_path, component_name in module_files:
    try:
        path = Path(file_path)
        if path.exists():
            content = path.read_text(encoding='utf-8')
            if component_name in content:
                print_success(f"{file_path}: FOUND ({component_name})")
                test_results['passed'] += 1
            else:
                print_error(f"{file_path}: FOUND but missing {component_name}")
                test_results['failed'] += 1
        else:
            print_error(f"{file_path}: NOT FOUND")
            test_results['failed'] += 1
    except Exception as e:
        print_error(f"{file_path}: ERROR - {e}")
        test_results['failed'] += 1

# ============================================================================
# TEST 12: Database Tables
# ============================================================================
print_section("TEST 12: Database Tables Verification")

tables_to_check = [
    ("ai_infrastructure", "oauth_tokens", "OAuth tokens"),
    ("ai_infrastructure", "automation_workflows", "Automation workflows"),
    ("sessions", "threads", "Thread storage"),
    ("sessions", "messages", "Message storage"),
    ("synergy_sessions", "sessions", "Kanban cards"),
]

for schema, table, description in tables_to_check:
    try:
        conn = get_database_connection(schema)
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
        """, (schema, table))
        
        result = cursor.fetchone()
        
        if result and result[0] > 0:
            # Count rows
            cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
            row_count = cursor.fetchone()[0]
            print_success(f"{schema}.{table} ({description}): EXISTS ({row_count} rows)")
            test_results['passed'] += 1
        else:
            print_error(f"{schema}.{table} ({description}): NOT FOUND")
            test_results['failed'] += 1
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print_error(f"{schema}.{table}: ERROR - {e}")
        test_results['failed'] += 1

# ============================================================================
# SUMMARY
# ============================================================================
print_header("TEST SUMMARY")

total_tests = test_results['passed'] + test_results['failed'] + test_results['warnings']
pass_rate = (test_results['passed'] / total_tests * 100) if total_tests > 0 else 0

print(f"   Total Tests: {total_tests}")
print(f"{Colors.GREEN}   Passed: {test_results['passed']}{Colors.RESET}")
print(f"{Colors.RED}   Failed: {test_results['failed']}{Colors.RESET}")
print(f"{Colors.YELLOW}   Warnings: {test_results['warnings']}{Colors.RESET}")
print(f"\n   Pass Rate: {Colors.GREEN if pass_rate >= 90 else Colors.YELLOW if pass_rate >= 70 else Colors.RED}{pass_rate:.1f}%{Colors.RESET}")

print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

if test_results['failed'] == 0:
    print(f"{Colors.GREEN}ALL CRITICAL TESTS PASSED{Colors.RESET}")
    print(f"{Colors.GREEN}Business AI Platform is ready for use!{Colors.RESET}")
    exit_code = 0
elif test_results['failed'] <= 3:
    print(f"{Colors.YELLOW}SOME TESTS FAILED{Colors.RESET}")
    print(f"{Colors.YELLOW}Platform is mostly functional but needs attention{Colors.RESET}")
    exit_code = 1
else:
    print(f"{Colors.RED}CRITICAL FAILURES DETECTED{Colors.RESET}")
    print(f"{Colors.RED}Platform may not function correctly{Colors.RESET}")
    exit_code = 2

print(f"\n{Colors.CYAN}Next Steps:{Colors.RESET}")
if test_results['failed'] > 0:
    print(f"   1. Review failed tests above")
    print(f"   2. Check Flask server logs for errors")
    print(f"   3. Verify Supabase credentials in .env.master")
    print(f"   4. Re-run: python test_business_ai_platform_complete.py")
else:
    print(f"   1. Open http://localhost:5001/ui/business-ai-platform-v2.html")
    print(f"   2. Test thread creation in AI Prime panel")
    print(f"   3. Test Synergy board card creation")
    print(f"   4. Test Automation canvas workflow creation")

print(f"\n{Colors.CYAN}{'=' * 80}{Colors.RESET}\n")

sys.exit(exit_code)
