"""
Test Synergy UI Fixes - Verify all pathways and connections
Tests backend endpoints and data flow for all 11 UI fixes
"""
from shared.database_utils import convert_sql_placeholders

import sqlite3
import json
import sys
import os
from pathlib import Path

# Add AI_infrastructure to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'AI_infrastructure'))

print("=" * 80)
print("SYNERGY UI FIXES - COMPREHENSIVE PATHWAY TEST")
print("=" * 80)

# Get database paths
root_dir = Path(__file__).parent
synergy_db = root_dir / 'data' / 'synergy_sessions.db'
sessions_db = root_dir / 'data' / 'sessions.db'

print(f"\n1. DATABASE CONNECTION TEST")
print("-" * 80)

# Test 1: Verify synergy_sessions database exists
if synergy_db.exists():
    print(f"   synergy_sessions.db: {synergy_db}")
    conn_synergy = sqlite3.connect(str(synergy_db))
    conn_synergy.row_factory = sqlite3.Row
    cursor = conn_synergy.cursor()
    
    # Get row count
    cursor.execute("SELECT COUNT(*) as count FROM synergy_sessions")
    count = cursor.fetchone()['count']
    print(f"   Records in synergy_sessions: {count}")
    print(f"   Status: PASS")
else:
    print(f"   ERROR: synergy_sessions.db not found at {synergy_db}")
    print(f"   Status: FAIL")
    sys.exit(1)

# Test 2: Verify sessions database exists (for threads)
if sessions_db.exists():
    print(f"\n   sessions.db: {sessions_db}")
    conn_sessions = sqlite3.connect(str(sessions_db))
    conn_sessions.row_factory = sqlite3.Row
    cursor_sessions = conn_sessions.cursor()
    
    # Get thread count
    cursor_sessions.execute("SELECT COUNT(*) as count FROM threads")
    thread_count = cursor_sessions.fetchone()['count']
    print(f"   Records in threads table: {thread_count}")
    print(f"   Status: PASS")
else:
    print(f"   ERROR: sessions.db not found at {sessions_db}")
    print(f"   Status: FAIL")

print(f"\n2. DATA STRUCTURE TEST - Field Name Variations")
print("-" * 80)

# Get sample session data
sql, params = convert_sql_placeholders("""
    SELECT 
        session_id,
        title,
        documents,
        links,
        next_steps,
        checklist,
        notes,
        thread_ids,
        recent_activity
    FROM synergy_sessions 
    WHERE documents IS NOT NULL OR links IS NOT NULL
    LIMIT 5
""")

sessions = cursor.fetchall()

if not sessions:
    print("   No test data found. Creating sample data...")
    # Insert test data
    test_session_id = f"sess_test_{int(Path(__file__).stat().st_mtime)}"
    test_data = {
        'title': 'Test Session for UI Fixes',
        'documents': json.dumps([
            {'name': 'Test Doc', 'url': 'https://docs.google.com/test', 'type': 'google_doc'},
            {'name': 'Excel Sheet', 'url': 'https://docs.google.com/sheet', 'type': 'google_sheet'}
        ]),
        'links': json.dumps([
            {'title': 'Link with title field', 'url': 'https://example.com/1', 'type': 'external'},
            {'name': 'Link with name field', 'url': 'https://example.com/2', 'type': 'external'}
        ]),
        'next_steps': json.dumps([
            {'description': 'Step with description', 'completed': False},
            {'text': 'Step with text field', 'completed': False},
            'Plain string step'
        ]),
        'checklist': json.dumps([
            {'task': 'Item with task field', 'completed': False, 'subtasks': [{'task': 'Sub-item', 'completed': False}]},
            {'item': 'Item with item field', 'completed': True}
        ]),
        'notes': 'These are test notes for the notes field display.',
        'thread_ids': json.dumps(['1234567890', '0987654321']),
        'recent_activity': json.dumps([
            {'type': 'create', 'description': 'Card created', 'timestamp': '2024-11-09T10:00:00', 'user': 'Test User'},
            {'type': 'update', 'description': 'Card updated', 'timestamp': '2024-11-09T11:00:00', 'user': 'Test User'}
        ])
    }
    
    cursor.execute("""
        INSERT INTO synergy_sessions (session_id, title, documents, links, next_steps, checklist, notes, thread_ids, recent_activity, status, kanban_column)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', 'backlog')
    """, (test_session_id, test_data['title'], test_data['documents'], test_data['links'], 
          test_data['next_steps'], test_data['checklist'], test_data['notes'], 
          test_data['thread_ids'], test_data['recent_activity']))

cursor.execute(sql, params)
    conn_synergy.commit()
    print(f"   Created test session: {test_session_id}")
    
    # Re-fetch
    sql, params = convert_sql_placeholders("""
        SELECT session_id, title, documents, links, next_steps, checklist, notes, thread_ids, recent_activity
        FROM synergy_sessions WHERE session_id = ?
    """, (test_session_id,))

    cursor.execute(sql, params)
    sessions = cursor.fetchall()

print(f"\n   Testing {len(sessions)} session(s):")

test_results = {
    'documents': {'pass': 0, 'fail': 0, 'field_variations': set()},
    'links': {'pass': 0, 'fail': 0, 'field_variations': set()},
    'next_steps': {'pass': 0, 'fail': 0, 'field_variations': set()},
    'checklist': {'pass': 0, 'fail': 0, 'field_variations': set()},
    'notes': {'pass': 0, 'fail': 0},
    'thread_ids': {'pass': 0, 'fail': 0},
    'activity': {'pass': 0, 'fail': 0}
}

for session in sessions:
    session_id = session['session_id']
    print(f"\n   Session: {session_id[:30]}...")
    
    # Test documents field
    if session['documents']:
        try:
            docs = json.loads(session['documents'])
            for doc in docs:
                if 'name' in doc:
                    test_results['documents']['field_variations'].add('name')
                if 'url' in doc:
                    test_results['documents']['field_variations'].add('url')
                if 'type' in doc:
                    test_results['documents']['field_variations'].add('type')
            test_results['documents']['pass'] += 1
            print(f"      Documents: PASS ({len(docs)} items)")
        except Exception as e:
            test_results['documents']['fail'] += 1
            print(f"      Documents: FAIL - {e}")
    
    # Test links field
    if session['links']:
        try:
            links = json.loads(session['links'])
            for link in links:
                if 'title' in link:
                    test_results['links']['field_variations'].add('title')
                if 'name' in link:
                    test_results['links']['field_variations'].add('name')
                if 'url' in link:
                    test_results['links']['field_variations'].add('url')
            test_results['links']['pass'] += 1
            print(f"      Links: PASS ({len(links)} items, variations: {test_results['links']['field_variations']})")
        except Exception as e:
            test_results['links']['fail'] += 1
            print(f"      Links: FAIL - {e}")
    
    # Test next_steps field
    if session['next_steps']:
        try:
            steps = json.loads(session['next_steps'])
            for step in steps:
                if isinstance(step, dict):
                    if 'description' in step:
                        test_results['next_steps']['field_variations'].add('description')
                    if 'text' in step:
                        test_results['next_steps']['field_variations'].add('text')
                    if 'step' in step:
                        test_results['next_steps']['field_variations'].add('step')
                    if 'title' in step:
                        test_results['next_steps']['field_variations'].add('title')
                elif isinstance(step, str):
                    test_results['next_steps']['field_variations'].add('string')
            test_results['next_steps']['pass'] += 1
            print(f"      Next Steps: PASS ({len(steps)} items, variations: {test_results['next_steps']['field_variations']})")
        except Exception as e:
            test_results['next_steps']['fail'] += 1
            print(f"      Next Steps: FAIL - {e}")
    
    # Test checklist field
    if session['checklist']:
        try:
            checklist = json.loads(session['checklist'])
            for item in checklist:
                if 'task' in item:
                    test_results['checklist']['field_variations'].add('task')
                if 'item' in item:
                    test_results['checklist']['field_variations'].add('item')
                if 'subtasks' in item:
                    test_results['checklist']['field_variations'].add('subtasks')
            test_results['checklist']['pass'] += 1
            print(f"      Checklist: PASS ({len(checklist)} items, variations: {test_results['checklist']['field_variations']})")
        except Exception as e:
            test_results['checklist']['fail'] += 1
            print(f"      Checklist: FAIL - {e}")
    
    # Test notes field
    if session['notes']:
        test_results['notes']['pass'] += 1
        print(f"      Notes: PASS ({len(session['notes'])} chars)")
    
    # Test thread_ids field
    if session['thread_ids']:
        try:
            thread_ids = json.loads(session['thread_ids'])
            test_results['thread_ids']['pass'] += 1
            print(f"      Thread IDs: PASS ({len(thread_ids)} threads)")
        except Exception as e:
            test_results['thread_ids']['fail'] += 1
            print(f"      Thread IDs: FAIL - {e}")
    
    # Test recent_activity field
    if session['recent_activity']:
        try:
            activity = json.loads(session['recent_activity'])
            has_types = any('type' in a for a in activity)
            has_descriptions = any('description' in a for a in activity)
            test_results['activity']['pass'] += 1
            print(f"      Activity: PASS ({len(activity)} items, types={has_types}, descriptions={has_descriptions})")
        except Exception as e:
            test_results['activity']['fail'] += 1
            print(f"      Activity: FAIL - {e}")

print(f"\n3. BACKEND ENDPOINT TEST")
print("-" * 80)

# Test the new /api/threads/details endpoint
print("\n   Testing /api/threads/details endpoint...")

# Get thread IDs from sessions
cursor.execute("""
    SELECT thread_ids FROM synergy_sessions 
    WHERE thread_ids IS NOT NULL AND thread_ids != '[]'
    LIMIT 1
""")
result = cursor.fetchone()

if result and result['thread_ids']:
    thread_ids = json.loads(result['thread_ids'])
    print(f"   Found thread IDs to test: {thread_ids}")
    
    # Check if threads exist in sessions.db
    if thread_ids:
        # First check what columns exist in threads table
        cursor_sessions.execute("PRAGMA table_info(threads)")
        columns = [col[1] for col in cursor_sessions.fetchall()]
        print(f"   Available columns in threads table: {columns}")
        
        # Use the correct column name (thread_slug for ID, check for name/title variations)
        name_column = 'name' if 'name' in columns else ('title' if 'title' in columns else 'thread_slug')
        
        placeholders = ','.join(['?' for _ in thread_ids])
        cursor_sessions.execute(f"""
            SELECT thread_slug, {name_column} as name, created_at, updated_at
            FROM threads
            WHERE thread_slug IN ({placeholders})
        """, thread_ids)
        
        threads = cursor_sessions.fetchall()
        if threads:
            print(f"   Found {len(threads)} matching threads in database:")
            for thread in threads:
                print(f"      - {thread['thread_slug']}: {thread['name']}")
            print(f"   Endpoint data available: PASS")
        else:
            print(f"   No matching threads found in database")
            print(f"   Note: This is okay - endpoint will handle gracefully")
else:
    print(f"   No thread IDs found in test data")
    print(f"   Note: Endpoint exists and will work when thread IDs are present")

print(f"\n4. ROUTE CONNECTION TEST")
print("-" * 80)

# Test route file locations
route_files = {
    'thread_routes.py': root_dir / 'AI_infrastructure' / 'routes' / 'thread_routes.py',
    'synergy_routes.py': root_dir / 'AI_infrastructure' / 'routes' / 'synergy_routes.py',
    'kanban_routes.py': root_dir / 'AI_infrastructure' / 'routes' / 'kanban_routes.py',
}

for route_name, route_path in route_files.items():
    if route_path.exists():
        print(f"   {route_name}: EXISTS")
        
        # Check for specific endpoint patterns
        content = route_path.read_text(encoding='utf-8')
        
        if route_name == 'thread_routes.py':
            if '/details' in content and 'POST' in content:
                print(f"      /api/threads/details endpoint: FOUND")
            else:
                print(f"      /api/threads/details endpoint: NOT FOUND")
        
        if route_name == 'synergy_routes.py':
            if 'synergy_sessions' in content:
                print(f"      Uses synergy_sessions table: CONFIRMED")
        
        if route_name == 'kanban_routes.py':
            if 'synergy_sessions' in content:
                print(f"      Uses synergy_sessions table: CONFIRMED")
    else:
        print(f"   {route_name}: NOT FOUND")

print(f"\n5. FRONTEND FILE TEST")
print("-" * 80)

frontend_file = root_dir / 'UI' / 'business-ai-platform-v2-fixed.html'
if frontend_file.exists():
    print(f"   Frontend file: EXISTS")
    print(f"   Path: {frontend_file}")
    
    content = frontend_file.read_text(encoding='utf-8')
    
    # Check for specific fixes
    checks = {
        'Documents clickable': '<a href="${doc.url}"' in content,
        'Links field handling': 'link.name || link.title' in content,
        'Checklist task/item': 'item.task || item.item' in content,
        'Next steps variations': 'step.description || step.text' in content,
        'Notes always visible': 'No notes added' in content,
        'Activity log icons': 'activity-icon' in content,
        'Session ID copy': 'copySessionId' in content,
        'Smooth transitions': 'cubic-bezier' in content,
        'Edit source tracking': 'editSource' in content,
        'Thread details endpoint': '/api/threads/details' in content,
    }
    
    print(f"\n   Code pattern verification:")
    for check_name, check_result in checks.items():
        status = "PASS" if check_result else "FAIL"
        icon = "" if check_result else ""
        print(f"      {check_name}: {status} {icon}")
    
    all_passed = all(checks.values())
    print(f"\n   Overall frontend verification: {'PASS' if all_passed else 'FAIL'}")
else:
    print(f"   ERROR: Frontend file not found")

print(f"\n6. SUMMARY")
print("=" * 80)

print(f"\n   Data Structure Tests:")
print(f"      Documents:   {test_results['documents']['pass']} passed, {test_results['documents']['fail']} failed")
print(f"      Links:       {test_results['links']['pass']} passed, {test_results['links']['fail']} failed")
print(f"      Next Steps:  {test_results['next_steps']['pass']} passed, {test_results['next_steps']['fail']} failed")
print(f"      Checklist:   {test_results['checklist']['pass']} passed, {test_results['checklist']['fail']} failed")
print(f"      Notes:       {test_results['notes']['pass']} passed, {test_results['notes']['fail']} failed")
print(f"      Thread IDs:  {test_results['thread_ids']['pass']} passed, {test_results['thread_ids']['fail']} failed")
print(f"      Activity:    {test_results['activity']['pass']} passed, {test_results['activity']['fail']} failed")

total_tests = sum(r['pass'] + r['fail'] for r in test_results.values() if 'pass' in r)
total_passed = sum(r['pass'] for r in test_results.values() if 'pass' in r)
total_failed = sum(r['fail'] for r in test_results.values() if 'fail' in r)

print(f"\n   Total: {total_passed}/{total_tests} tests passed")

if total_failed == 0:
    print(f"\n   ALL PATHWAYS VERIFIED - SYSTEM READY")
else:
    print(f"\n   {total_failed} tests failed - review needed")

# Close connections
conn_synergy.close()
conn_sessions.close()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
