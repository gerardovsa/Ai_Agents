"""
Check for return statements inside with blocks (connection leak detector)
"""

import re
import os
from pathlib import Path

def check_file_for_returns_in_with_blocks(filepath):
    """Check a file for return statements inside with blocks"""
    leaks = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_with_block = False
    with_block_start = 0
    with_block_indent = 0
    
    for i, line in enumerate(lines, 1):
        # Check for with block start
        if re.match(r'\s*with\s+get_.*connection.*:', line):
            in_with_block = True
            with_block_start = i
            # Calculate indentation level
            with_block_indent = len(line) - len(line.lstrip())
            continue
        
        # If we're in a with block, check for return statements
        if in_with_block:
            current_indent = len(line) - len(line.lstrip())
            
            # If we've dedented back to or beyond with block level, we're out
            if line.strip() and current_indent <= with_block_indent:
                in_with_block = False
                continue
            
            # Check for return statement (but not in comments)
            if re.search(r'^\s*return\s+', line) and not line.strip().startswith('#'):
                leaks.append({
                    'file': filepath,
                    'line': i,
                    'with_start': with_block_start,
                    'code': line.strip()
                })
    
    return leaks


def main():
    """Check all route files"""
    routes_dir = Path('AI_infrastructure/routes')
    
    print("\n[CHECK] Scanning for return statements inside with blocks...")
    print("="*70)
    
    total_leaks = 0
    
    for filepath in routes_dir.glob('*.py'):
        leaks = check_file_for_returns_in_with_blocks(filepath)
        
        if leaks:
            print(f"\n[WARNING] Found {len(leaks)} potential leak(s) in {filepath.name}:")
            for leak in leaks:
                print(f"  Line {leak['line']}: {leak['code']}")
                print(f"    (with block started at line {leak['with_start']})")
            total_leaks += len(leaks)
    
    print("\n" + "="*70)
    if total_leaks == 0:
        print("[OK] No connection leaks detected")
    else:
        print(f"[WARNING] Found {total_leaks} potential connection leak(s)")
        print("\n[FIX] Pattern to fix leaks:")
        print("  1. Initialize result variable BEFORE with block")
        print("  2. Set result inside with block, DON'T return")
        print("  3. Return AFTER with block closes")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
