#!/usr/bin/env python
"""
Add **kwargs support to all Microsoft tool methods that don't have it
This ensures all methods can accept credential injection parameters
"""

import re
from pathlib import Path

# List of Microsoft tool files to fix
MICROSOFT_FILES = [
    'microsoft_calendar_tools.py',
    'microsoft_excel_tools.py',
    'microsoft_forms_tools.py',
    'microsoft_onedrive_tools.py',
    'microsoft_onenote_tools.py',
    'microsoft_outlook_tools.py',
    'microsoft_sharepoint_tools.py',
    'microsoft_teams_tools.py',
    'microsoft_todo_tools.py',
    'microsoft_word_tools.py',
]

TOOLS_DIR = Path(__file__).parent / 'tools' / 'implementations'

def add_kwargs_to_file(file_path):
    """Add **kwargs to method signatures that don't have it"""
    print(f"\nProcessing: {file_path.name}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to find method definitions without **kwargs
    # Matches: def method_name(self, ...) without **kwargs
    pattern = r'(    def \w+\(self[^)]*?)(\) -> |\):)'
    
    def replacer(match):
        sig = match.group(1)
        closing = match.group(2)
        
        # Skip if already has **kwargs
        if '**kwargs' in sig:
            return match.group(0)
        
        # Skip if it's __init__ or other special methods
        if '__' in sig:
            return match.group(0)
        
        # Add **kwargs before the closing
        return sig + ', **kwargs' + closing
    
    content = re.sub(pattern, replacer, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Count changes
        original_count = len(re.findall(r'    def \w+\(self[^)]*?\)(?!\s*\))', original_content))
        new_content_checks = len(re.findall(r'    def \w+\(self.*?\*\*kwargs', content))
        print(f"  Status: UPDATED - Added **kwargs to methods")
        return True
    else:
        print(f"  Status: No changes needed")
        return False

# Process all Microsoft tool files
fixed_count = 0
for filename in MICROSOFT_FILES:
    file_path = TOOLS_DIR / filename
    if file_path.exists():
        if add_kwargs_to_file(file_path):
            fixed_count += 1
    else:
        print(f"\nWarning: File not found: {file_path}")

print(f"\n{'='*60}")
print(f"Summary: Updated {fixed_count}/{len(MICROSOFT_FILES)} Microsoft tool files")
print(f"All methods now support credential injection via **kwargs")
