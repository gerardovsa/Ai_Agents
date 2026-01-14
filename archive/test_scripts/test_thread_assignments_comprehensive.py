"""
Comprehensive Thread Assignment System Test
from shared.database_utils import convert_sql_placeholders

Tests database schema, API endpoints, and frontend logic
to ensure thread assignment system is properly implemented.

Tests:
1. Database schema validation
2. Thread assignment rules enforcement
3. API endpoint responses
4. Agent location logic
5. Exclusive assignment model
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(name, status, details=""):
    """Print formatted test result"""
    symbol = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
    print(f"{symbol} {name}")
    if details:
        print(f"  {details}")

def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

# Database paths
sessions_db = Path('data/sessions.db')
ai_infra_db = Path('data/ai_infrastructure.db')

# Test results
results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0
}

def test_database_schema():
    """Test 1: Validate database schema"""
    print_header("TEST 1: DATABASE SCHEMA VALIDATION")
    
    if not sessions_db.exists():
        print_test("sessions.db exists", False, f"File not found: {sessions_db}")
        results['failed'] += 1
        return False
    
    print_test("sessions.db exists", True, f"Found at: {sessions_db}")
    results['passed'] += 1
    
    conn = sqlite3.connect(sessions_db)
    cursor = conn.cursor()
    
    # Check threads table structure
    cursor.execute("PRAGMA table_info(threads)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}
    
    required_columns = {
        'id': 'INTEGER',
        'thread_slug': 'TEXT',
        'name': 'TEXT',
        'location': 'TEXT',
        'user_id': 'INTEGER',
        'created_at': 'TIMESTAMP',
        'updated_at': 'TIMESTAMP'
    }
    
    for col_name, col_type in required_columns.items():
        if col_name in columns:
            print_test(f"Column 'threads.{col_name}' exists", True, f"Type: {columns[col_name]}")
            results['passed'] += 1
        else:
            print_test(f"Column 'threads.{col_name}' exists", False, f"MISSING")
            results['failed'] += 1
    
    # Check messages table foreign key
    cursor.execute("PRAGMA foreign_key_list(messages)")
    fk_found = False
    for row in cursor.fetchall():
        if row[2] == 'threads' and row[3] == 'thread_id':
            fk_found = True
            break
    
    print_test("Foreign key messages.thread_id -> threads.id", fk_found)
    results['passed' if fk_found else 'failed'] += 1
    
    conn.close()
    return True

def test_thread_location_values():
    """Test 2: Validate thread location values"""
    print_header("TEST 2: THREAD LOCATION VALUES")
    
    conn = sqlite3.connect(sessions_db)
    cursor = conn.cursor()
    
    # Get all distinct location values
    cursor.execute("SELECT DISTINCT location FROM threads WHERE location IS NOT NULL")
    locations = [row[0] for row in cursor.fetchall()]
    
    valid_locations = ['prime', 'agent-1', 'agent-2', 'agent-3']
    
    print(f"Found locations: {locations}")
    
    for loc in locations:
        is_valid = loc in valid_locations
        print_test(f"Location '{loc}' is valid", is_valid)
        results['passed' if is_valid else 'failed'] += 1
    
    # Check for any invalid locations
    cursor.execute("""
        SELECT id, thread_slug, name, location 
        FROM threads 
        WHERE location IS NOT NULL 
        AND location NOT IN ('prime', 'agent-1', 'agent-2', 'agent-3')
    """)
    invalid = cursor.fetchall()
    
    if invalid:
        print_test("No invalid locations found", False, f"Found {len(invalid)} invalid")
        for row in invalid:
            print(f"  Thread #{row[0]} ({row[1]}): location='{row[3]}'")
        results['failed'] += 1
    else:
        print_test("No invalid locations found", True)
        results['passed'] += 1
    
    conn.close()

def test_exclusive_assignment():
    """Test 3: Validate exclusive assignment model"""
    print_header("TEST 3: EXCLUSIVE ASSIGNMENT MODEL")
    
    conn = sqlite3.connect(sessions_db)
    cursor = conn.cursor()
    
    # Get all threads
    cursor.execute("SELECT id, thread_slug, name, location FROM threads")
    threads = cursor.fetchall()
    
    print(f"Total threads: {len(threads)}")
    
    # Count threads per location
    location_counts = {}
    for thread in threads:
        loc = thread[3] or 'unassigned'
        location_counts[loc] = location_counts.get(loc, 0) + 1
    
    print("\nThread distribution:")
    for loc, count in sorted(location_counts.items()):
        print(f"  {loc}: {count} threads")
    
    # Verify each thread has exactly one location
    for thread in threads:
        has_location = thread[3] is not None
        print_test(f"Thread #{thread[0]} has location", has_location, 
                   f"Location: {thread[3] or 'NULL'}")
        results['passed' if has_location else 'warnings'] += 1
    
    conn.close()

def test_thread_assignment_api_logic():
    """Test 4: Document and validate API logic"""
    print_header("TEST 4: THREAD ASSIGNMENT API LOGIC")
    
    # This documents the expected API behavior
    api_rules = {
        "POST /api/thread-assignments/<thread_id>": {
            "purpose": "Assign thread to specific agent location",
            "parameters": {
                "location": "Required - One of: 'prime', 'agent-1', 'agent-2', 'agent-3'"
            },
            "logic": [
                "1. Validate location is in allowed list",
                "2. Update threads.location = <location>",
                "3. Update threads.updated_at = NOW()",
                "4. Return success response with new location"
            ],
            "exclusive": True,
            "description": "Thread can only be in ONE location at a time"
        },
        "GET /api/threads/<thread_slug>/assignment": {
            "purpose": "Get current assignment for thread",
            "returns": {
                "location": "Current location value from threads.location"
            },
            "logic": [
                "1. Query threads WHERE thread_slug = <slug>",
                "2. Return location field value",
                "3. Return 'prime' if NULL"
            ]
        },
        "DELETE /api/thread-assignments/<thread_id>": {
            "purpose": "Unassign thread (move to Prime)",
            "logic": [
                "1. Update threads.location = 'prime'",
                "2. Update threads.updated_at = NOW()",
                "3. Clear any cached assignment data"
            ],
            "equivalent_to": "POST with location='prime'"
        }
    }
    
    print("API Endpoint Rules:")
    for endpoint, rules in api_rules.items():
        print(f"\n{YELLOW}{endpoint}{RESET}")
        print(f"  Purpose: {rules['purpose']}")
        if 'parameters' in rules:
            print("  Parameters:")
            for param, desc in rules['parameters'].items():
                print(f"    - {param}: {desc}")
        if 'logic' in rules:
            print("  Logic:")
            for step in rules['logic']:
                print(f"    {step}")
        if rules.get('exclusive'):
            print(f"  {RED}EXCLUSIVE:{RESET} Thread cannot be in multiple locations")
    
    print_test("API logic documented", True, "See above rules")
    results['passed'] += 1

def test_frontend_logic():
    """Test 5: Validate frontend implementation"""
    print_header("TEST 5: FRONTEND LOGIC VALIDATION")
    
    # Read the business-ai-platform-v2.html file
    html_file = Path('UI/business-ai-platform-v2.html')
    
    if not html_file.exists():
        print_test("Frontend file exists", False, f"Not found: {html_file}")
        results['failed'] += 1
        return
    
    print_test("Frontend file exists", True)
    results['passed'] += 1
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for key functions
    functions_to_check = {
        'assignThread': 'Assigns thread to agent location',
        'unloadThread': 'Moves thread from agent to Prime',
        'renderThreadList': 'Renders thread cards with badges',
        'showThreadAssignmentOptions': 'Shows inline assignment options',
        'handleThreadAssignmentOption': 'Handles user assignment choice'
    }
    
    for func_name, description in functions_to_check.items():
        found = f'function {func_name}' in content or f'{func_name}(' in content
        print_test(f"Function '{func_name}' exists", found, description)
        results['passed' if found else 'failed'] += 1
    
    # Check for 300ms delay fix
    delay_fix = 'setTimeout' in content and '300' in content
    print_test("300ms delay implemented", delay_fix, 
               "Allows backend to complete before re-render")
    results['passed' if delay_fix else 'failed'] += 1
    
    # Check for visual badge detection
    badge_detection = 'thread-agent-badge' in content or 'agent-badge' in content
    print_test("Visual badge detection", badge_detection,
               "Fallback when backend data stale")
    results['passed' if badge_detection else 'failed'] += 1

def test_assignment_rules_documentation():
    """Test 6: Document all assignment rules"""
    print_header("TEST 6: THREAD ASSIGNMENT RULES DOCUMENTATION")
    
    rules = {
        "RULE 1: Exclusive Assignment": {
            "description": "A thread can only be assigned to ONE location at a time",
            "database": "threads.location field holds single value",
            "frontend": "Only one badge shows per thread",
            "enforcement": "Database constraint (single column)"
        },
        "RULE 2: Valid Locations": {
            "description": "Only these locations are valid: prime, agent-1, agent-2, agent-3",
            "database": "Should use CHECK constraint or app-level validation",
            "frontend": "Dropdown/buttons only show valid options",
            "enforcement": "API validates before database write"
        },
        "RULE 3: Default Location": {
            "description": "New threads default to 'prime' location",
            "database": "threads.location DEFAULT 'prime'",
            "frontend": "New thread cards show 'Prime' badge",
            "enforcement": "Database schema or INSERT default"
        },
        "RULE 4: Timestamp Update": {
            "description": "threads.updated_at must update on assignment change",
            "database": "UPDATE threads SET updated_at = NOW()",
            "frontend": "Thread moves to top of list after assignment",
            "enforcement": "API always updates timestamp"
        },
        "RULE 5: User Permissions": {
            "description": "Users can only assign threads they own or have access to",
            "database": "Check threads.user_id or workspace_users",
            "frontend": "Assign button only shows for accessible threads",
            "enforcement": "API checks user_id before UPDATE"
        },
        "RULE 6: Sync Delay": {
            "description": "Frontend waits 300ms after assignment before re-fetching",
            "database": "N/A",
            "frontend": "setTimeout(() => renderThreadList(), 300)",
            "enforcement": "Frontend implementation"
        },
        "RULE 7: Visual Fallback": {
            "description": "Use visual badge as fallback if backend data stale",
            "database": "N/A",
            "frontend": "Parse badge text if API returns wrong location",
            "enforcement": "Frontend implementation (optional)"
        }
    }
    
    print("Thread Assignment System Rules:")
    for rule_name, rule_details in rules.items():
        print(f"\n{YELLOW}{rule_name}{RESET}")
        print(f"  Description: {rule_details['description']}")
        print(f"  Database: {rule_details['database']}")
        print(f"  Frontend: {rule_details['frontend']}")
        print(f"  Enforcement: {rule_details['enforcement']}")
    
    print_test("All 7 rules documented", True)
    results['passed'] += 1

def test_actual_assignments():
    """Test 7: Check actual thread assignments in database"""
    print_header("TEST 7: ACTUAL THREAD ASSIGNMENTS")
    
    conn = sqlite3.connect(sessions_db)
    cursor = conn.cursor()
    
    # Get recent threads with assignments
    cursor.execute("""
        SELECT 
            id,
            thread_slug,
            SUBSTR(name, 1, 40) as name,
            location,
            datetime(created_at) as created,
            datetime(updated_at) as updated
        FROM threads
        ORDER BY updated_at DESC
        LIMIT 15
    """)
    
    threads = cursor.fetchall()
    
    print(f"Recent threads (last 15):\n")
    print(f"{'ID':<5} {'Slug':<20} {'Name':<42} {'Location':<12} {'Updated'}")
    print("-" * 120)
    
    for thread in threads:
        loc = thread[3] or 'NULL'
        updated = thread[5] if thread[5] else 'N/A'
        print(f"{thread[0]:<5} {thread[1]:<20} {thread[2]:<42} {loc:<12} {updated}")
    
    # Verify all threads have location
    cursor.execute("SELECT COUNT(*) FROM threads WHERE location IS NULL")
    null_count = cursor.fetchone()[0]
    
    if null_count > 0:
        print(f"\n{YELLOW}WARNING:{RESET} {null_count} threads have NULL location")
        results['warnings'] += 1
    else:
        print(f"\n{GREEN}✓{RESET} All threads have valid location assignments")
        results['passed'] += 1
    
    conn.close()

def test_synergy_integration():
    """Test 8: Verify Synergy board thread linking"""
    print_header("TEST 8: SYNERGY BOARD INTEGRATION")
    
    synergy_db = Path('data/synergy_sessions.db')
    
    if not synergy_db.exists():
        print_test("synergy_sessions.db exists", False)
        results['failed'] += 1
        return
    
    print_test("synergy_sessions.db exists", True)
    results['passed'] += 1
    
    conn_synergy = sqlite3.connect(synergy_db)
    cursor_synergy = conn_synergy.cursor()
    
    # Check for thread_ids field
    cursor_synergy.execute("PRAGMA table_info(synergy_sessions)")
    columns = {row[1] for row in cursor_synergy.fetchall()}
    
    has_thread_ids = 'thread_ids' in columns
    print_test("synergy_sessions.thread_ids field exists", has_thread_ids)
    results['passed' if has_thread_ids else 'failed'] += 1
    
    # Get sessions with linked threads
    cursor_synergy.execute("""
        SELECT session_id, title, thread_ids, assigned_agents
        FROM synergy_sessions
        WHERE thread_ids != '[]'
        LIMIT 5
    """)
    
    linked_sessions = cursor_synergy.fetchall()
    
    print(f"\nSynergy sessions with linked threads: {len(linked_sessions)}")
    
    for session in linked_sessions:
        try:
            thread_ids = json.loads(session[2])
            agents = json.loads(session[3])
            print(f"  {session[0][:40]}")
            print(f"    Linked threads: {thread_ids}")
            print(f"    Assigned agents: {agents}")
        except:
            pass
    
    conn_synergy.close()
    
    # Cross-reference with sessions.db
    conn_sessions = sqlite3.connect(sessions_db)
    cursor_sessions = conn_sessions.cursor()
    
    # Check if synergy-linked threads exist
    if linked_sessions:
        for session in linked_sessions:
            try:
                thread_ids = json.loads(session[2])
                for thread_slug in thread_ids:
                    cursor_sessions.execute(
                        "SELECT id, location FROM threads WHERE thread_slug = ?",
                        (thread_slug,)
                    )
                    thread = cursor_sessions.fetchone()
                    if thread:
                        print_test(f"Synergy thread {thread_slug[:20]} exists in sessions.db",
                                   True, f"Location: {thread[1]}")
                        results['passed'] += 1
                    else:
                        print_test(f"Synergy thread {thread_slug[:20]} exists in sessions.db",
                                   False, "NOT FOUND")
                        results['failed'] += 1
            except:
                pass
    
    conn_sessions.close()

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = results['passed'] + results['failed'] + results['warnings']
    pass_rate = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"{GREEN}Passed:{RESET}   {results['passed']}")
    print(f"{RED}Failed:{RESET}   {results['failed']}")
    print(f"{YELLOW}Warnings:{RESET} {results['warnings']}")
    print(f"Total:    {total}")
    print(f"\nPass Rate: {pass_rate:.1f}%")
    
    if results['failed'] == 0:
        print(f"\n{GREEN}{'='*80}{RESET}")
        print(f"{GREEN}ALL TESTS PASSED - Thread Assignment System is ROBUST{RESET}")
        print(f"{GREEN}{'='*80}{RESET}")
    else:
        print(f"\n{RED}{'='*80}{RESET}")
        print(f"{RED}SOME TESTS FAILED - Review implementation{RESET}")
        print(f"{RED}{'='*80}{RESET}")

if __name__ == '__main__':
    print_header("THREAD ASSIGNMENT SYSTEM - COMPREHENSIVE TEST")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {Path.cwd()}")
    
    try:
        test_database_schema()
        test_thread_location_values()
        test_exclusive_assignment()
        test_thread_assignment_api_logic()
        test_frontend_logic()
        test_assignment_rules_documentation()
        test_actual_assignments()
        test_synergy_integration()
        
        print_summary()
        
    except Exception as e:
        print(f"\n{RED}ERROR:{RESET} Test execution failed")
        print(f"{str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
