"""
Check Microsoft tool export naming patterns
"""

import os
import re
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
impl_dir = root_dir / 'tools' / 'implementations'

microsoft_files = [
    'microsoft_calendar_tools.py',
    'microsoft_excel_tools.py',
    'microsoft_forms_tools.py',
    'microsoft_onedrive_tools.py',
    'microsoft_onenote_tools.py',
    'microsoft_outlook_tools.py',
    'microsoft_sharepoint_tools.py',
    'microsoft_teams_tools.py',
    'microsoft_todo_tools.py',
    'microsoft_word_tools.py'
]

print("=" * 80)
print("MICROSOFT TOOL EXPORT NAMING CHECK")
print("=" * 80)

for filename in microsoft_files:
    filepath = impl_dir / filename
    platform = filename.replace('_tools.py', '')
    
    print(f"\n{filename}:")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all module-level exports
    # Pattern: word_create_document = microsoft_word_tools.word_create_document
    pattern = r'^(\w+)\s*=\s*microsoft_\w+_tools\.(\w+)'
    matches = re.findall(pattern, content, re.MULTILINE)
    
    if not matches:
        print("  ❌ NO EXPORTS FOUND")
        continue
    
    correct_count = 0
    incorrect_count = 0
    
    for export_name, method_name in matches[:5]:  # Show first 5
        if export_name.startswith('microsoft_'):
            print(f"  ✅ {export_name}")
            correct_count += 1
        else:
            print(f"  ❌ {export_name} (should be microsoft_{export_name})")
            incorrect_count += 1
    
    if len(matches) > 5:
        print(f"  ... and {len(matches) - 5} more exports")
    
    print(f"  Total: {len(matches)} exports ({correct_count} correct, {incorrect_count} incorrect)")

print("\n" + "=" * 80)
