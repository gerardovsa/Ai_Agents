"""
Verify Synergy HTML Elements to Database Field Mapping
Checks if all HTML form fields correctly map to database columns
"""

import re
from pathlib import Path

# Database schema from synergy_sessions table
DB_FIELDS = {
    'session_id': 'TEXT PRIMARY KEY',
    'title': 'TEXT NOT NULL',
    'description': 'TEXT',
    'platforms_involved': 'TEXT (JSON)',
    'status': 'TEXT DEFAULT active',
    'priority': 'TEXT DEFAULT medium',
    'kanban_column': 'TEXT DEFAULT backlog',
    'tags': 'TEXT (JSON)',
    'documents': 'TEXT (JSON)',
    'links': 'TEXT (JSON)',
    'next_steps': 'TEXT (JSON)',
    'assignees': 'TEXT (JSON)',
    'recent_activity': 'TEXT (JSON)',
    'checklist': 'TEXT (JSON)',
    'due_date': 'TEXT',
    'created_at': 'TEXT DEFAULT CURRENT_TIMESTAMP',
    'last_active': 'TEXT DEFAULT CURRENT_TIMESTAMP',
    'completed_at': 'TEXT',
    'google_task_id': 'TEXT',
    'google_calendar_id': 'TEXT',
    'microsoft_todo_id': 'TEXT',
    'thread_ids': 'TEXT (JSON)',  # SYNERGY INTEGRATION
    'assigned_agents': 'TEXT (JSON)',  # SYNERGY INTEGRATION
    'project_name': 'TEXT',  # From sessions table (legacy)
    'notes': 'TEXT'  # From sessions table (legacy)
}

# Expected HTML form field IDs
HTML_FORM_FIELDS = {
    'edit-session-id': 'session_id',
    'edit-title': 'title',
    'edit-description': 'description',
    'edit-project': 'project_name',
    'edit-priority': 'priority',
    'edit-status': 'status',
    'edit-column': 'kanban_column',
    'edit-due-date': 'due_date',
    'edit-due-time': 'due_date (time component)',
    'edit-assignees': 'assignees (JSON)',
    'edit-tags': 'tags (JSON)',
    'edit-thread-ids': 'thread_ids (JSON)',  # CRITICAL: Synergy integration
    'edit-assigned-agents': 'assigned_agents (JSON)',  # CRITICAL: Synergy integration
    'edit-notes': 'notes',
    'documents-list': 'documents (JSON)',
    'links-list': 'links (JSON)',
    'next-steps-list': 'next_steps (JSON)',
    'checklist-list': 'checklist (JSON)',
    'sync-google-tasks': 'google_task_id',
    'sync-google-calendar': 'google_calendar_id'
}

# Read HTML file
html_path = Path('UI/business-ai-platform-v2.html')
html_content = html_path.read_text(encoding='utf-8')

print("="*100)
print("SYNERGY HTML TO DATABASE MAPPING VERIFICATION")
print("="*100)

# 1. CHECK EDIT MODAL FORM FIELDS
print("\n1. EDIT MODAL FORM FIELDS:")
print("-"*100)

missing_fields = []
found_fields = []

for field_id, db_mapping in HTML_FORM_FIELDS.items():
    # Search for the field ID in HTML
    pattern = rf'id="{field_id}"'
    matches = re.findall(pattern, html_content)
    
    if matches:
        found_fields.append((field_id, db_mapping, len(matches)))
        print(f"✅ {field_id:<30} → {db_mapping:<40} ({len(matches)} occurrences)")
    else:
        missing_fields.append((field_id, db_mapping))
        print(f"❌ {field_id:<30} → {db_mapping:<40} MISSING!")

# 2. CHECK openEditModal POPULATION
print("\n2. openEditModal() FIELD POPULATION:")
print("-"*100)

# Extract openEditModal function
open_modal_match = re.search(r'openEditModal\(session\)\s*{(.*?)\n\s{12}closeEditModal', 
                              html_content, re.DOTALL)

if open_modal_match:
    open_modal_code = open_modal_match.group(1)
    
    # Check each field gets populated
    population_checks = {
        'edit-session-id': r"getElementById\('edit-session-id'\)\.value = session\.session_id",
        'edit-title': r"getElementById\('edit-title'\)\.value = session\.title",
        'edit-description': r"getElementById\('edit-description'\)\.value = session\.description",
        'edit-project': r"getElementById\('edit-project'\)\.value = session\.project_name",
        'edit-priority': r"getElementById\('edit-priority'\)\.value = session\.priority",
        'edit-status': r"getElementById\('edit-status'\)\.value = session\.status",
        'edit-column': r"getElementById\('edit-column'\)\.value = session\.kanban_column",
        'edit-tags': r"getElementById\('edit-tags'\)\.value = tags",
        'edit-assignees': r"getElementById\('edit-assignees'\)\.value = assignees",
        'edit-thread-ids': r"getElementById\('edit-thread-ids'\)\.value = threadIds",  # CRITICAL
        'edit-assigned-agents': r"getElementById\('edit-assigned-agents'\)\.value = assignedAgents",  # CRITICAL
        'edit-notes': r"getElementById\('edit-notes'\)\.value = session\.notes",
        'edit-due-date': r"getElementById\('edit-due-date'\)\.value",
        'edit-due-time': r"getElementById\('edit-due-time'\)\.value"
    }
    
    for field_id, pattern in population_checks.items():
        if re.search(pattern, open_modal_code):
            print(f"✅ {field_id:<30} gets populated from session object")
        else:
            print(f"❌ {field_id:<30} NOT populated in openEditModal()")
            
    # Check JSON parsing for critical fields
    print("\n   JSON Field Parsing:")
    json_fields = ['thread_ids', 'assigned_agents', 'tags', 'assignees', 'documents', 'links', 'next_steps']
    for field in json_fields:
        if f'parseJsonField(session.{field}' in open_modal_code:
            print(f"   ✅ {field:<20} parsed with parseJsonField()")
        else:
            print(f"   ⚠️  {field:<20} may not use parseJsonField()")
else:
    print("❌ openEditModal() function not found!")

# 3. CHECK saveCardEdit FUNCTION
print("\n3. saveCardEdit() SAVE LOGIC:")
print("-"*100)

# Extract saveCardEdit function
save_modal_match = re.search(r'saveCardEdit\(\)\s*{(.*?)\n\s{12}[a-z]', 
                              html_content, re.DOTALL)

if save_modal_match:
    save_modal_code = save_modal_match.group(1)
    
    # Check field extraction
    extraction_checks = {
        'session_id': r"getElementById\('edit-session-id'\)\.value",
        'title': r"getElementById\('edit-title'\)\.value",
        'description': r"getElementById\('edit-description'\)\.value",
        'project_name': r"getElementById\('edit-project'\)\.value",
        'priority': r"getElementById\('edit-priority'\)\.value",
        'status': r"getElementById\('edit-status'\)\.value",
        'kanban_column': r"getElementById\('edit-column'\)\.value",
        'tags': r"getElementById\('edit-tags'\)\.value\.split\(','\)",
        'assignees': r"getElementById\('edit-assignees'\)\.value\.split\(','\)",
        'thread_ids': r"getElementById\('edit-thread-ids'\)\.value",  # CRITICAL
        'assigned_agents': r"getElementById\('edit-assigned-agents'\)\.value",  # CRITICAL
        'notes': r"getElementById\('edit-notes'\)\.value"
    }
    
    for db_field, pattern in extraction_checks.items():
        if re.search(pattern, save_modal_code, re.IGNORECASE):
            print(f"✅ {db_field:<30} extracted in saveCardEdit()")
        else:
            print(f"❌ {db_field:<30} NOT extracted in saveCardEdit()")
            
    # Check API call
    if '/api/synergy/' in save_modal_code and 'PATCH' in save_modal_code:
        print("\n   ✅ Makes PATCH request to /api/synergy/<id>")
    else:
        print("\n   ❌ API call to /api/synergy/<id> not found")
else:
    print("❌ saveCardEdit() function not found!")

# 4. CHECK CARD RENDERING
print("\n4. CARD RENDERING (renderCard/renderCardExpanded):")
print("-"*100)

# Check if thread_ids and assigned_agents are rendered
render_checks = {
    'thread_ids display': r'session\.thread_ids.*parseJsonField.*length',
    'assigned_agents display': r'session\.assigned_agents.*parseJsonField.*length',
    'thread badges': r'renderLinkedThreads\(threadIds\)',
    'agent badges': r'agent-name.*escapeHtml\(agent\)',
    'threads section': r'Linked Threads \(',
    'agents section': r'Assigned Agents \('
}

for check_name, pattern in render_checks.items():
    matches = re.findall(pattern, html_content, re.IGNORECASE)
    if matches:
        print(f"✅ {check_name:<30} implemented ({len(matches)} occurrences)")
    else:
        print(f"❌ {check_name:<30} NOT found")

# 5. CHECK DATABASE UPDATE ENDPOINTS
print("\n5. BACKEND API ENDPOINTS (from HTML fetch calls):")
print("-"*100)

api_endpoints = {
    '/api/synergy/list': 'List all Synergy sessions',
    '/api/synergy/create': 'Create new session',
    '/api/synergy/<id>': 'Get/Update/Delete session',
    '/api/synergy/<id>/link-thread': 'Link thread to session (CRITICAL)',
    '/api/synergy/<id>/unlink-thread': 'Unlink thread from session (CRITICAL)',
    '/api/threads/details': 'Get thread details for display (CRITICAL)',
    '/api/threads/save': 'Save thread with synergy_card_id'
}

for endpoint, description in api_endpoints.items():
    # Replace <id> with regex pattern
    pattern = endpoint.replace('<id>', r'[^/]+')
    matches = re.findall(pattern, html_content)
    if matches:
        print(f"✅ {endpoint:<40} → {description} ({len(matches)} calls)")
    else:
        print(f"⚠️  {endpoint:<40} → {description} (not found)")

# 6. CRITICAL SYNERGY INTEGRATION CHECKS
print("\n6. CRITICAL SYNERGY-THREAD INTEGRATION:")
print("-"*100)

critical_checks = [
    ('thread_ids field in edit modal', r'id="edit-thread-ids"'),
    ('assigned_agents field in edit modal', r'id="edit-assigned-agents"'),
    ('thread_ids populated in openEditModal', r"getElementById\('edit-thread-ids'\)\.value = threadIds"),
    ('assigned_agents populated in openEditModal', r"getElementById\('edit-assigned-agents'\)\.value = assignedAgents"),
    ('thread_ids saved in saveCardEdit', r"getElementById\('edit-thread-ids'\)\.value"),
    ('assigned_agents saved in saveCardEdit', r"getElementById\('edit-assigned-agents'\)\.value"),
    ('renderLinkedThreads function exists', r'renderLinkedThreads\(threadIds\)'),
    ('threads displayed in card', r'Linked Threads'),
    ('agents displayed in card', r'Assigned Agents'),
    ('bidirectional sync /link-thread', r'/api/synergy/.*/link-thread'),
    ('bidirectional sync /unlink-thread', r'/api/synergy/.*/unlink-thread')
]

all_passed = True
for check_name, pattern in critical_checks:
    if re.search(pattern, html_content):
        print(f"✅ {check_name}")
    else:
        print(f"❌ {check_name}")
        all_passed = False

# SUMMARY
print("\n" + "="*100)
print("SUMMARY:")
print("="*100)

print(f"\nHTML Form Fields Found: {len(found_fields)}/{len(HTML_FORM_FIELDS)}")
print(f"Missing Form Fields: {len(missing_fields)}")

if missing_fields:
    print("\nMissing Fields:")
    for field_id, db_mapping in missing_fields:
        print(f"  ❌ {field_id} → {db_mapping}")

print(f"\nCritical Integration Checks: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")

print("\n" + "="*100)
print("RECOMMENDATION:")
print("="*100)

if all_passed and len(missing_fields) == 0:
    print("✅ ALL HTML ELEMENTS CORRECTLY MAPPED TO DATABASE")
    print("✅ SYNERGY-THREAD INTEGRATION COMPLETE IN HTML")
    print("✅ Edit modal, card display, and API calls all implemented")
    print("\nNext Step: Verify backend routes handle these fields correctly")
else:
    print("⚠️  ISSUES FOUND - Review missing fields and failed checks above")
    print("\nRequired Actions:")
    if missing_fields:
        print("  1. Add missing form fields to edit modal")
    if not all_passed:
        print("  2. Implement missing integration functions")

print("="*100)
