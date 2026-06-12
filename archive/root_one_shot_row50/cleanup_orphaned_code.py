#!/usr/bin/env python3
"""Delete orphaned lines between function closing and next function."""

from pathlib import Path

file_path = Path("UI/modules_internal/agents/agent-js.js")

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find the initMultiAgent function ending
# Pattern: } followed by /** comment at the start of next function
func_end_line = None
next_func_line = None

for i, line in enumerate(lines):
    if line.strip() == '}' and i > 2700 and i < 4000:
        # Check if next non-empty line is /**
        for j in range(i + 1, min(i + 5, len(lines))):
            if lines[j].strip().startswith('/**'):
                func_end_line = i
                next_func_line = j
                break
        if func_end_line:
            break

print(f"initMultiAgent ends at line {func_end_line + 1}")
print(f"Next function starts at line {next_func_line + 1}")

if func_end_line and next_func_line and next_func_line > func_end_line + 1:
    print(f"Orphaned code: lines {func_end_line + 2} to {next_func_line}")
    
    # Keep everything up to and including the function closing brace
    # Then skip to the next function
    new_lines = lines[:func_end_line + 1]  # 0 to func_end_line
    new_lines.extend(lines[next_func_line:])  # next_func_line onward
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Deleted {len(lines) - len(new_lines)} lines")
    print(f"New total: {len(new_lines)} lines")
    print("DONE!")
else:
    print("Could not find orphaned code block")
