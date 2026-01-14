"""
Fix cursor leaks in synergy_routes.py by converting:
    cursor = conn.cursor()
to:
    with conn.cursor() as cursor:
"""

import re
from pathlib import Path

# Read the file
file_path = Path(__file__).parent / 'routes' / 'synergy_routes.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match cursor = conn.cursor() followed by code blocks
# We need to find the cursor assignment and add proper indentation to the following code
pattern = r'(\s+)(cursor = conn\.cursor\(\))\n'

def fix_cursor_context(match):
    indent = match.group(1)
    # Return with proper context manager
    return f'{indent}with conn.cursor() as cursor:  # ✅ Fixed cursor leak\n{indent}    '

# Replace all occurrences
fixed_content = re.sub(pattern, fix_cursor_context, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print(f"✅ Fixed cursor leaks in {file_path}")
print(f"   Total fixes applied: {len(re.findall(pattern, content))}")
