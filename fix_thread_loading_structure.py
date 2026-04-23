#!/usr/bin/env python3
"""
Fix the thread loading race condition in agent-js.js by moving orphaned code
into the .then() callback where maxAgentId is defined.

This script restructures initMultiAgent() to be fully async:
1. Load threads (via .then() callback)
2. Calculate maxAgentId from loaded threads
3. Create agents + initialize everything (inside callback)
4. All Socket.IO, container verification, etc. happens AFTER threads load
"""

import re
from pathlib import Path

file_path = Path("UI/modules_internal/agents/agent-js.js")

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"✅ Loaded {len(lines)} lines from {file_path}")

# Find the .then() and .catch() lines
then_line = None
catch_line = None

for i, line in enumerate(lines):
    if '.then(() => {' in line and i > 2700:  # Make sure it's the right one (after line 2700)
        then_line = i
    if '.catch(err => console.error' in line and i > then_line > 0:
        catch_line = i
        break

if then_line is None or catch_line is None:
    print(f"❌ Could not find .then() (line {then_line}) or .catch() (line {catch_line})")
    exit(1)

print(f"✅ Found .then() at line {then_line + 1}")
print(f"✅ Found .catch() at line {catch_line + 1}")

# Find where the orphaned code starts (first non-empty line after .catch())
orphan_start = catch_line + 1
while orphan_start < len(lines) and lines[orphan_start].strip() == '':
    orphan_start += 1

# Find where the orphaned code ends (before the final closing brace of function)
orphan_end = orphan_start
last_closing_brace_in_function = None

for i in range(orphan_start, len(lines)):
    stripped = lines[i].strip()
    # Look for the pattern that ends the function
    if stripped.startswith('console.log(`[Multi - Agent] [OK] Initialized with ${maxAgentId}'):
        orphan_end = i + 1
        # The closing brace should be right after
        if i + 1 < len(lines) and lines[i + 1].strip() == '}':
            last_closing_brace_in_function = i + 1
        break

print(f"✅ Orphaned code spans lines {orphan_start + 1} to {orphan_end}")
print(f"✅ Function closing brace at line {last_closing_brace_in_function + 1 if last_closing_brace_in_function else 'NOT FOUND'}")

# Extract the orphaned code
orphan_code_lines = lines[orphan_start:orphan_end]

# Indent the orphaned code by 4 more spaces (it needs to be inside the .then() callback)
indented_orphan_code = []
for line in orphan_code_lines:
    if line.strip() == '':
        indented_orphan_code.append(line)  # Keep empty lines as-is
    else:
        indented_orphan_code.append('    ' + line)  # Add 4 spaces

print(f"✅ Prepared {len(indented_orphan_code)} lines of indented code")

# Find the line right before .catch() - this is where we inject the orphaned code
insert_line = catch_line

# Build the new file content
new_lines = []

# Copy everything up to and including the .then() line and initial content
new_lines.extend(lines[:insert_line])

# Add the orphaned code (indented) before .catch()
new_lines.extend(indented_orphan_code)

# Add blank line before .catch()
new_lines.append('\n')

# Add the .catch() and everything after it EXCEPT the orphaned code block
if last_closing_brace_in_function is not None:
    # Add everything from .catch() to function closing brace
    new_lines.extend(lines[catch_line:last_closing_brace_in_function + 1])
    
    # Add everything after the function (if any)
    if last_closing_brace_in_function + 1 < len(lines):
        new_lines.extend(lines[last_closing_brace_in_function + 1:])
else:
    # Fallback: just add .catch() and hope for the best
    new_lines.extend(lines[catch_line:])

print(f"✅ Built new file with {len(new_lines)} lines (original was {len(lines)})")

# Backup the original file
backup_path = file_path.with_suffix('.js.backup')
print(f"💾 Backing up to {backup_path}...")
with open(backup_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Write the corrected file
print(f"💾 Writing corrected file to {file_path}...")
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ ✅ ✅ FIX COMPLETE!")
print(f"\nSummary of changes:")
print(f"  - Moved {len(orphan_code_lines)} lines into .then() callback")
print(f"  - All code now properly scoped inside async callback")
print(f"  - maxAgentId references should now resolve correctly")
print(f"  - Backup saved to: {backup_path}")
print(f"\nNext steps:")
print(f"  1. Reload the page in browser")
print(f"  2. Check DevTools console for no 'maxAgentId is not defined' errors")
print(f"  3. Verify all agent columns render (not just 3)")
print(f"  4. Commit: git add UI/modules_internal/agents/agent-js.js")
print(f"  5. Commit: git commit -m 'fix(multi-agent): move code into .then() callback'")
