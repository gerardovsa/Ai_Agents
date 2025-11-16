"""
Comprehensive fix for all execute_sqlite_update calls in thread_routes.py
"""

import re

file_path = r'C:\Users\gpoli\GIT\AI_agents\AI_infrastructure\routes\thread_routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# First, ensure all ? are replaced with %s in SQL queries
content = content.replace('= ?', '= %s')
content = content.replace('(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)')

# Save intermediate
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Step 1: Fixed SQL placeholders (? → %s)")

# Reload
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find all execute_sqlite_update calls and their line numbers
updates_found = []
for i, line in enumerate(lines):
    if 'execute_sqlite_update(' in line:
        updates_found.append((i+1, line.strip()))

print(f"\n✅ Step 2: Found {len(updates_found)} execute_sqlite_update calls:")
for line_num, line_content in updates_found:
    print(f"   Line {line_num}: {line_content[:60]}...")

print("\n⚠️  Manual replacement needed - locations identified")
