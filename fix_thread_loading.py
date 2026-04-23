#!/usr/bin/env python3
"""Fix thread loading by moving code into .then() callback."""

from pathlib import Path

path = Path("UI/modules_internal/agents/agent-js.js")
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Loaded {len(lines)} lines")

# Find key lines numbers
then_line = None
catch_line = None
orphan_end = None

for i, line in enumerate(lines):
    if '.then(() => {' in line and i > 2700 and i < 2800:
        then_line = i
    if '.catch(err' in line and i > 2750 and i < 2800:
        catch_line = i
    if 'console.log(`[Multi - Agent] [OK] Initialized with' in line and i > 2800 and i < 4000:
        orphan_end = i + 1

print(f"then_line={then_line + 1}, catch_line={catch_line + 1}, orphan_end={orphan_end}")

if not all([then_line, catch_line, orphan_end]):
    print("ERROR: Could not find key lines")
    exit(1)

# Find the }) line right before .catch()
close_callback_line = None
for i in range(catch_line - 1, then_line, -1):
    if '})' in lines[i]:
        close_callback_line = i
        break

print(f"close_callback_line={close_callback_line + 1}")

# Extract orphaned code (everything after catch until orphan_end)
orphan_start = catch_line + 1
while orphan_start < len(lines) and not lines[orphan_start].strip():
    orphan_start += 1

orphan_code = lines[orphan_start:orphan_end]
print(f"Orphaned code: lines {orphan_start + 1} to {orphan_end}")

# Indent by adding 4 spaces to each line
indented = []
for line in orphan_code:
    if line.strip():
        indented.append('    ' + line)
    else:
        indented.append(line)

# Build new file
new_lines = []
new_lines.extend(lines[:close_callback_line])  # Up to but not including })
new_lines.extend(indented)  # Orphaned code (indented)
new_lines.append('\n')
new_lines.extend(lines[close_callback_line:orphan_start])  # }) through end of catch line
new_lines.extend(lines[orphan_end:])  # Anything after orphan_end

# Backup and write
backup = path.with_suffix('.js.backup')
with open(backup, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print(f"Backed up to {backup}")

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print(f"Wrote fixed file ({len(new_lines)} lines)")
print("DONE!")
