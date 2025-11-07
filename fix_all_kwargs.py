#!/usr/bin/env python
"""Fix all tool methods to accept **kwargs for credential injection"""
import re
from pathlib import Path

def fix_file(fp):
    print(f"Fixing: {fp.name}...", end=" ")
    with open(fp, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    new_lines, count = [], 0
    for line in lines:
        if re.match(r'^\s+def \w+\(self', line) and '**kwargs' not in line and ')' in line and '__' not in line.split('def')[1]:
            idx = line.rfind(')')
            before = line[:idx].rstrip()
            if before.endswith('(self'): 
                new_lines.append(line[:idx] + '**kwargs' + line[idx:])
            elif before[-1] not in ',)': 
                new_lines.append(line[:idx] + ', **kwargs' + line[idx:])
                count += 1
            else: 
                new_lines.append(line)
        else: 
            new_lines.append(line)
    new = ''.join(new_lines)
    with open(fp, 'r', encoding='utf-8', errors='replace') as f:
        orig = f.read()
    if new != orig:
        with open(fp, 'w', encoding='utf-8', errors='replace') as f: f.write(new)
        print(f"✅ Fixed")
        return True
    print(f"✓ OK")
    return False

base = Path('c:/Users/gpoli/GIT/AI_agents')
files = [
    'google_workspace/gmail.py', 'google_workspace/google_docs.py',
    'google_workspace/google_forms.py', 'google_workspace/google_drive.py',
    'google_workspace/google_calendar.py', 'google_workspace/google_slides.py',
    'google_workspace/google_meet.py', 'google_workspace/google_tasks.py',
    'tools/implementations/microsoft_calendar_tools.py',
    'tools/implementations/microsoft_excel_tools.py',
    'tools/implementations/microsoft_forms_tools.py',
    'tools/implementations/microsoft_onedrive_tools.py',
    'tools/implementations/microsoft_onenote_tools.py',
    'tools/implementations/microsoft_outlook_tools.py',
    'tools/implementations/microsoft_sharepoint_tools.py',
    'tools/implementations/microsoft_teams_tools.py',
    'tools/implementations/microsoft_todo_tools.py',
    'tools/implementations/microsoft_word_tools.py',
    'tools/implementations/slack.py', 'tools/implementations/stripe.py',
    'tools/implementations/synergy.py', 'tools/implementations/woocommerce.py',
]
fixed, total = 0, 0
print(f"\n{'='*70}\nFIXING ALL TOOLS FOR **kwargs SUPPORT\n{'='*70}\n")
for f in files:
    p = base / f
    if p.exists():
        total += 1
        if fix_file(p): fixed += 1
print(f"\n{'='*70}\nDone: {fixed}/{total} files fixed\n{'='*70}\n")
