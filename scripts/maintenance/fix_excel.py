#!/usr/bin/env python3
"""Fix Excel functions to use credential injection"""
import re

with open('microsoft_excel_tools.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace self.headers with self._get_headers(**kwargs)
content = content.replace('headers=self.headers', 'headers=self._get_headers(**kwargs)')

# Replace self.access_token in Authorization headers  
content = re.sub(
    r'"Authorization":\s*f"Bearer\s+\{self\.access_token\}"',
    '"Authorization": self._get_headers(**kwargs)["Authorization"]',
    content
)

# Add **kwargs to excel_ functions (simple approach - add to end of params before ):)
lines = content.split('\n')
new_lines = []
for i, line in enumerate(lines):
    if re.match(r'\s*def excel_\w+\(', line):
        # Check if **kwargs already in this or next few lines
        check_lines = '\n'.join(lines[i:min(i+10, len(lines))])
        if '**kwargs' not in check_lines:
            # Find the closing ) of the function signature
            j = i
            while j < len(lines) and '):' not in lines[j]:
                new_lines.append(lines[j])
                j += 1
            # Add **kwargs before ):
            if j < len(lines):
                new_lines.append(lines[j].replace('):', ', **kwargs):'))
                i = j
                continue
    new_lines.append(line)

content = '\n'.join(new_lines)

with open('microsoft_excel_tools.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed microsoft_excel_tools.py')
