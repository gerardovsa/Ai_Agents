#!/usr/bin/env python3
"""Find extra closing brace in CSS"""

content = open('UI/modules_external/inhouse-kanban/inhouse-kanban-NEW.css', 'r', encoding='utf-8').read()
lines = content.split('\n')

depth = 0
for i, line in enumerate(lines, 1):
    open_count = line.count('{')
    close_count = line.count('}')
    
    depth += open_count
    depth -= close_count
    
    if depth < 0:
        print(f"Line {i}: Extra closing brace detected (depth: {depth})")
        print(f"Line content: {line}")
        print(f"\nContext (lines {i-3} to {i+3}):")
        for j in range(max(0, i-4), min(len(lines), i+3)):
            marker = ">>>" if j == i-1 else "   "
            print(f"{marker} {j+1:4d}: {lines[j]}")
        break

if depth == 0:
    print("✅ All braces are balanced")
elif depth > 0:
    print(f"Missing {depth} closing brace(s)")
