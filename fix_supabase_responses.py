"""
Fix Supabase response handling

SupabaseClient methods return direct results, not response objects:
- client.insert() returns list
- client.update() returns list
- client.delete() returns list
- query.execute() returns list

Need to remove .data attribute access
"""

import re

file_path = r'tools\implementations\supabase.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: response.data[0] → response[0] (after insert/update)
content = re.sub(
    r'response\.data\[0\]',
    r'response[0]',
    content
)

# Fix 2: response.data → response (direct list access)
content = re.sub(
    r'response\.data',
    r'response',
    content
)

# Fix 3: if response.data else → if response else
content = re.sub(
    r'if response\.data else',
    r'if response else',
    content
)

# Fix 4: len(response.data) → len(response)
content = re.sub(
    r'len\(response\.data\)',
    r'len(response)',
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Fixed Supabase response handling")
print("  - Removed .data attribute access")
print("  - Direct list access instead")
