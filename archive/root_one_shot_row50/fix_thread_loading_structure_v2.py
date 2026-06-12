#!/usr/bin/env python3
"""
Fix the thread loading race condition in agent-js.js by moving orphaned code
into the .then() callback where maxAgentId is defined.

IMPROVED approach: Find the }) that CLOSES .then(), then insert code BEFORE it.
"""

import re
from pathlib import Path

file_path = Path("UI/modules_internal/agents/agent-js.js")

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"✅ Loaded {len(lines)} lines from {file_path}")

# Find the .then(() => { line (the opening of the callback)
then_open_line = None
for i, line in enumerate(lines):
    if '.then(() => {' in line and i > 2700:  # after line 2700
        then_open_line = i
        break

if then_open_line is None:
    print("❌ Could not find .then(() => {{ opening")
    exit(1)

print(f"✅ Found .then(() at line {then_open_line + 1}")

# Now find the matching }) that CLOSES this .then() callback
# It should be the first }) at the right indentation level after the .then( open
# Look for }) that's indented 12 spaces (the .then() is 12 spaces, its closing }) is 12 spaces)
brace_count = 1  # We already passed the opening {
then_close_line = None
for i in range(then_open_line + 1, len(lines)):
    line = lines[i]
    # Count braces in this line
    open_braces = line.count('{')
    close_braces = line.count('}')
    
    # Skip if it's in a comment or string
    # Simple heuristic: if line starts with right indent for closure and has })
    brace_count += open_braces - close_braces
    
    # If brace_count reaches -1, we found the closing brace
    if brace_count <= 0:
        # Verify it's actually a }) structure
        stripped = line.strip()
        if '})' in stripped or (stripped == '}' and lines[i+1].strip().startswith('.catch')):
            then_close_line = i
            break

if then_close_line is None:
    print("❌ Could not find closing }) for .then()")
    exit(1)

print(f"✅ Found .then() closing brace at line {then_close_line + 1}")

# Find .catch() line
catch_line = None
for i in range(then_close_line, len(lines)):
    if '.catch(err' in lines[i]:
        catch_line = i
        break

if catch_line is None:
    print("❌ Could not find .catch() after .then()")
    exit(1)

print(f"✅ Found .catch() at line {catch_line + 1}")

# Find the orphaned code start (first non-empty line after .catch())
orphan_start = catch_line + 1
while orphan_start < len(lines) and lines[orphan_start].strip() == '':
    orphan_start += 1

# Find the function ending (the closing }) of initMultiAgent)
# Look for the line with the final console.log that ends the function
orphan_end = orphan_start
for i in range(orphan_start, len(lines)):
    if 'console.log(`[Multi - Agent] [OK] Initialized with ${maxAgentId}' in lines[i]:
        orphan_end = i + 1
        break

print(f"✅ Orphaned code spans lines {orphan_start + 1} to {orphan_end}")

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

# Build the new file
new_lines = []

# Part 1: Everything up to (but NOT including) the }) that closes .then()
new_lines.extend(lines[:then_close_line])

# Part 2: Add the orphaned code (indented)
new_lines.extend(indented_orphan_code)

# Part 3: Add blank line for readability
new_lines.append('\n')

# Part 4: Add the }) that closes .then()
new_lines.append(lines[then_close_line])

# Part 5: Add .catch() and the function closing brace
# Find the function closing brace (should be after the final console.log)
func_close_line = None
for i in range(orphan_end, len(lines)):
    if lines[i].strip() == '}' and i == orphan_end + 1:
        func_close_line = i
        break

if func_close_line is None:
    # Just take everything after orphan_end
    print(f"⚠️ Warning: Could not find function closing brace, using remainder of file")
    new_lines.extend(lines[catch_line:])
else:
    # Add everything from .catch() through function close
    new_lines.extend(lines[catch_line:func_close_line + 1])
    
    # Add anything after the function
    if func_close_line + 1 < len(lines):
        new_lines.extend(lines[func_close_line + 1:])

print(f"✅ Built new file with {len(new_lines)} lines (original was {len(lines)})")

print(f"✅ Structure verification: Has .then() and .catch()")
else:
    print("❌ Structure verification FAILED")

# Backup the original file
backup_path = file_path.with_suffix('.js.backup2')
print(f"💾 Backing up to {backup_path}...")
with open(backup_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Write the corrected file
print(f"💾 Writing corrected file to {file_path}...")
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"\n✅ ✅ ✅ FIX COMPLETE!")
print("\nSummary of changes:")
print(f"  - Moved lines {orphan_start + 1}-{orphan_end} into .then() callback")
print("  - Inserted BEFORE the } that closes .then()")
print("  - All code now properly scoped inside async callback")
print(f"  - Backup saved to: {backup_path}")

