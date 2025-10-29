#!/usr/bin/env python3
"""
Automatically fix Microsoft Word tools to use credential injection pattern
"""
import re

# Read the file
with open('microsoft_word_tools.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Add **kwargs to all word_ function signatures (if not already present)
def add_kwargs(match):
    func_sig = match.group(0)
    if '**kwargs' in func_sig:
        return func_sig
    # Add **kwargs before the closing ):
    return func_sig.replace('):', ', **kwargs):')

pattern = r'def word_\w+\([^)]*\):'
content = re.sub(pattern, add_kwargs, content)

# Step 2: Replace self.headers with self._get_headers(**kwargs)
content = content.replace('headers=self.headers', 'headers=self._get_headers(**kwargs)')

# Step 3: Replace self.access_token references in Authorization headers
content = re.sub(
    r'"Authorization":\s*f"Bearer\s+\{self\.access_token\}"',
    '"Authorization": self._get_headers(**kwargs)["Authorization"]',
    content
)

# Write back
with open('microsoft_word_tools.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed microsoft_word_tools.py')
print('   - Added **kwargs to all word_ functions')
print('   - Replaced self.headers with self._get_headers(**kwargs)')
print('   - Fixed Authorization header references')
