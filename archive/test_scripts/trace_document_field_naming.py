"""
Trace document field naming across the entire system
Find the SOURCE OF TRUTH and inconsistencies
"""
import sqlite3
import json
import os
from shared.database_utils import convert_sql_placeholders

print("=" * 120)
print("DOCUMENT FIELD NAMING - SYSTEM-WIDE ANALYSIS")
print("=" * 120)

# 1. Check database sessions
print("\n1. DATABASE - What's actually stored")
print("-" * 120)

db_path = 'C:\\Users\\gpoli\\GIT\\AI_agents\\data\\synergy_sessions.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT session_id, documents FROM synergy_sessions LIMIT 5")
rows = cursor.fetchall()

for session_id, documents_json in rows:
    documents = json.loads(documents_json)
    if documents:
        first_doc = documents[0]
        keys = list(first_doc.keys())
        has_name = 'name' in first_doc
        has_title = 'title' in first_doc
        
        print(f"\nSession: {session_id[:50]}...")
        print(f"  Keys in JSON: {keys}")
        print(f"  Has 'name': {has_name}")
        print(f"  Has 'title': {has_title}")
        if has_name:
            print(f"  Field used: 'name'")
        elif has_title:
            print(f"  Field used: 'title'")

conn.close()

# 2. Check synergy_routes.py - Backend API
print("\n\n2. BACKEND (synergy_routes.py) - What API returns")
print("-" * 120)

routes_file = 'C:\\Users\\gpoli\\GIT\\AI_agents\\AI_infrastructure\\routes\\synergy_routes.py'
if os.path.exists(routes_file):
    with open(routes_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Look for document field references
    import re
    
    # Find where documents are created/modified
    doc_patterns = [
        r"'name':\s*([^,}]+)",
        r"'title':\s*([^,}]+)",
        r'"name":\s*([^,}]+)',
        r'"title":\s*([^,}]+)',
        r"documents\.append\([^)]+\)",
        r"'documents':\s*\[",
    ]
    
    for pattern in doc_patterns:
        matches = re.findall(pattern, content)
        if matches:
            print(f"\nPattern '{pattern}' found {len(matches)} times")
            for match in matches[:3]:
                print(f"  Example: {str(match)[:80]}")

# 3. Check if there's a schema or model definition
print("\n\n3. LOOKING FOR SCHEMA/MODEL DEFINITIONS")
print("-" * 120)

# Check for any schema files
schema_locations = [
    'AI_infrastructure/models/',
    'AI_infrastructure/schemas/',
    'tools/schemas/synergy_tools.json'
]

for loc in schema_locations:
    full_path = f'C:\\Users\\gpoli\\GIT\\AI_agents\\{loc}'
    if os.path.exists(full_path):
        print(f"\nFound: {loc}")
        if os.path.isfile(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'document' in content.lower():
                    print("  Contains document references")
                    # Look for field definitions
                    if '"name"' in content:
                        print("  Uses 'name' field")
                    if '"title"' in content:
                        print("  Uses 'title' field")

# 4. Check frontend HTML expectations
print("\n\n4. FRONTEND (business-ai-platform-v2.html) - What HTML expects")
print("-" * 120)

html_file = 'C:\\Users\\gpoli\\GIT\\AI_agents\\UI\\business-ai-platform-v2.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Count doc.name vs doc.title references
doc_name_count = html_content.count('doc.name')
doc_title_count = html_content.count('doc.title')

print(f"\n'doc.name' used: {doc_name_count} times")
print(f"'doc.title' used: {doc_title_count} times")

# Find the lines where they're used
import re
name_lines = [m.start() for m in re.finditer(r'doc\.name', html_content)]
title_lines = [m.start() for m in re.finditer(r'doc\.title', html_content)]

print(f"\nLines using 'doc.name': {len(name_lines)} occurrences")
print(f"Lines using 'doc.title': {len(title_lines)} occurrences")

# 5. Summary and recommendation
print("\n\n" + "=" * 120)
print("ANALYSIS SUMMARY")
print("=" * 120)

print("\nINCONSISTENCY FOUND:")
print("  - Some sessions use 'name' field")
print("  - Some sessions use 'title' field")
print("  - HTML uses both 'doc.name' and 'doc.title'")

print("\n\nRECOMMENDATION:")
print("  1. Choose ONE standard field name (suggest: 'title')")
print("  2. Update backend to ALWAYS use that field")
print("  3. Update frontend to ONLY look for that field")
print("  4. Run migration script to normalize existing database records")

print("\n\nNEXT STEPS:")
print("  1. Check synergy creation tools - what field do THEY use?")
print("  2. Standardize on 'title' (more semantic for documents)")
print("  3. Update all code to use 'title' consistently")
print("  4. Add migration to rename 'name' -> 'title' in existing sessions")
