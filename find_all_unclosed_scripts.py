#!/usr/bin/env python3
"""Find ALL unclosed script tags"""
import re

content = open('UI/business-ai-platform-v2.html', encoding='utf-8').read()
lines = content.split('\n')

depth = 0
unclosed = []

for i, line in enumerate(lines, 1):
    if '<script' in line and not line.strip().endswith('/>'):
        depth += 1
        unclosed.append((i, line.strip()))
    if '</script>' in line:
        depth -= 1
        if unclosed:
            unclosed.pop()

print(f"Script tag depth at end: {depth}")
print(f"\nUnclosed <script> tags:")
for line_num, line_text in unclosed:
    print(f"  Line {line_num}: {line_text[:80]}")
