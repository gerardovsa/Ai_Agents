#!/usr/bin/env python3
"""Fix all remaining self.headers references in Excel tools"""

with open('microsoft_excel_tools.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all self.headers with self._get_headers(**kwargs)
content = content.replace('headers=self.headers', 'headers=self._get_headers(**kwargs)')

with open('microsoft_excel_tools.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed all self.headers references')
