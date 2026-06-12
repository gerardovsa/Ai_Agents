"""
Connection Leak Fix Script - Automated Fix for ALL Connection Leaks

This script finds and fixes ALL instances of:
    conn = get_database_connection(...)
    
And converts them to:
    with get_database_connection(...) as conn:
        
USAGE:
    python fix_connection_leaks.py
"""

import os
import re
from pathlib import Path

def fix_connection_leaks():
    """Fix all connection leaks in route files"""
    
    routes_dir = Path("AI_infrastructure/routes")
    files_fixed = []
    leaks_fixed = 0
    
    # Find all Python files in routes directory
    for filepath in routes_dir.glob("*.py"):
        print(f"\n{'='*80}")
        print(f"Checking: {filepath.name}")
        print(f"{'='*80}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Direct assignment without try/finally (MAJOR LEAK)
        # Example: conn = get_database_connection('sessions')
        pattern1 = r'(\s+)(conn = get_database_connection\([\'"](\w+)[\'"]\))\n(\s+)cursor = conn\.cursor\(\)'
        
        def replace_leak(match):
            indent = match.group(1)
            schema = match.group(3)
            cursor_indent = match.group(4)
            
            # Generate replacement with context manager
            replacement = (
                f"{indent}# ✅ FIX: Use context manager to prevent connection leaks\n"
                f"{indent}with get_database_connection('{schema}') as conn:\n"
                f"{cursor_indent}cursor = conn.cursor()"
            )
            return replacement
        
        content, count1 = re.subn(pattern1, replace_leak, content)
        
        if count1 > 0:
            print(f"  ✅ Fixed {count1} direct connection leaks")
            leaks_fixed += count1
        
        # Pattern 2: Connection assignment in try block (PARTIAL FIX NEEDED)
        pattern2 = r'(\s+)try:\n\s+conn = get_database_connection\([\'"](\w+)[\'"]\)'
        
        def replace_try_leak(match):
            indent = match.group(1)
            schema = match.group(2)
            
            replacement = (
                f"{indent}# ✅ FIX: Use context manager instead of try/finally\n"
                f"{indent}try:\n"
                f"{indent}    with get_database_connection('{schema}') as conn:"
            )
            return replacement
        
        content, count2 = re.subn(pattern2, replace_try_leak, content)
        
        if count2 > 0:
            print(f"  ✅ Fixed {count2} try-block connection leaks")
            leaks_fixed += count2
        
        # Save if changes were made
        if content != original_content:
            # Backup original file
            backup_path = filepath.with_suffix('.py.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            files_fixed.append(filepath.name)
            print(f"  💾 Saved fixed file (backup: {backup_path.name})")
        else:
            print(f"  ✓ No leaks found")
    
    # Summary
    print(f"\n{'='*80}")
    print(f"FIX SUMMARY")
    print(f"{'='*80}")
    print(f"Files checked: {len(list(routes_dir.glob('*.py')))}")
    print(f"Files fixed: {len(files_fixed)}")
    print(f"Total leaks fixed: {leaks_fixed}")
    
    if files_fixed:
        print(f"\nFixed files:")
        for filename in files_fixed:
            print(f"  - {filename}")
    
    print(f"\n{'='*80}")
    print(f"NEXT STEPS:")
    print(f"{'='*80}")
    print(f"1. Review changes in fixed files")
    print(f"2. Restart Flask server: BISTART")
    print(f"3. Test the UI - connection pool should no longer exhaust")
    print(f"4. If issues occur, restore from .backup files")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    fix_connection_leaks()
