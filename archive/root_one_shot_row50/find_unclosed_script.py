#!/usr/bin/env python3
"""Find unclosed script tag in HTML"""

content = open('UI/business-ai-platform-v2.html', 'r', encoding='utf-8').read()
lines = content.split('\n')

depth = 0
last_open_line = 0
last_open_text = ""

for i, line in enumerate(lines, 1):
    if '<script' in line:
        depth += 1
        last_open_line = i
        last_open_text = line.strip()
    if '</script>' in line:
        depth -= 1
        
    if depth < 0:
        print(f"Line {i}: Extra closing </script> tag")
        print(f"Line content: {line.strip()}")
        break

if depth > 0:
    print(f"Unclosed <script> tag found!")
    print(f"Line {last_open_line}: {last_open_text}")
    print(f"\nShowing context (lines {last_open_line-2} to {last_open_line+10}):")
    for i in range(max(0, last_open_line-3), min(len(lines), last_open_line+10)):
        marker = ">>>" if i == last_open_line-1 else "   "
        print(f"{marker} {i+1:5d}: {lines[i]}")
elif depth == 0:
    print("✅ All <script> tags are balanced")
