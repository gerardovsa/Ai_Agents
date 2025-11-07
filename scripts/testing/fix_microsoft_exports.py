"""
Auto-fix Microsoft tool export naming
Adds microsoft_ prefix to exports that are missing it
"""

import os
import re
from pathlib import Path

root_dir = Path(__file__).parent.parent.parent
impl_dir = root_dir / 'tools' / 'implementations'

files_to_fix = [
    'microsoft_excel_tools.py',
    'microsoft_forms_tools.py',
    'microsoft_onenote_tools.py',
    'microsoft_sharepoint_tools.py'
]

print("=" * 80)
print("FIXING MICROSOFT TOOL EXPORT NAMING")
print("=" * 80)

for filename in files_to_fix:
    filepath = impl_dir / filename
    platform = filename.replace('_tools.py', '')
    
    print(f"\nProcessing {filename}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all incorrect module-level exports
    # Pattern: excel_create_workbook = microsoft_excel_tools.excel_create_workbook
    # Should be: microsoft_excel_create_workbook = microsoft_excel_tools.excel_create_workbook
    
    pattern = r'^([a-z_]+)\s*=\s*(microsoft_\w+_tools\.)([a-z_]+)$'
    
    def replace_export(match):
        export_name = match.group(1)
        class_ref = match.group(2)
        method_name = match.group(3)
        
        # Check if export already has microsoft_ prefix
        if export_name.startswith('microsoft_'):
            return match.group(0)  # No change needed
        
        # Add microsoft_ prefix
        new_export_name = f"microsoft_{export_name}"
        return f"{new_export_name} = {class_ref}{method_name}"
    
    original_content = content
    new_content = re.sub(pattern, replace_export, content, flags=re.MULTILINE)
    
    if new_content != original_content:
        # Count changes
        changes = len(re.findall(pattern, original_content, re.MULTILINE))
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ Fixed {changes} exports")
    else:
        print(f"  ℹ️  No changes needed")

print("\n" + "=" * 80)
print("DONE! Run check_microsoft_exports.py to verify.")
print("=" * 80)
