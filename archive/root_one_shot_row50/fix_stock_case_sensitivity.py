"""
Fix Stock Case-Sensitivity Bugs in Shopify Calculators

This script fixes the case-sensitivity issue where calculators check:
    if "None" in stock:
    
But fail when stock="none" (lowercase), causing incorrect pricing.

ISSUE: Case-sensitive "None" check fails for lowercase "none"
FIX: Add case-insensitive check: if "None" in stock or stock.lower() == "none":

AFFECTED: 2 calculator files
    - SpiralBound_Shopify_Calculator.py (line 301)
    - WireBound_Shopify_Calculator.py (line 414)

USAGE:
    python fix_stock_case_sensitivity.py --dry-run  # Preview changes
    python fix_stock_case_sensitivity.py --apply    # Apply fixes

LAST MODIFIED: 2026-01-03 - Initial creation
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Base directory for Shopify calculators
BASE_DIR = Path("UI/modules_external/quote-calculator/backend/shopify_calculators")

# Files to fix with approximate line numbers
FILES_TO_FIX = [
    ("SpiralBound_Shopify_Calculator.py", 301),
    ("WireBound_Shopify_Calculator.py", 414),
]


def read_file(filepath: Path) -> List[str]:
    """Read file and return lines"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()


def write_file(filepath: Path, lines: List[str]) -> None:
    """Write lines to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def fix_stock_check(line: str) -> Tuple[str, bool]:
    """
    Fix case-sensitive stock check
    
    Before: if "None" in stock:
    After:  if "None" in stock or stock.lower() == "none":
    """
    # Look for the pattern: if "None" in stock:
    if 'if "None" in stock:' in line:
        new_line = line.replace(
            'if "None" in stock:',
            'if "None" in stock or stock.lower() == "none":'
        )
        return new_line, True
    
    # Also check for single quotes
    if "if 'None' in stock:" in line:
        new_line = line.replace(
            "if 'None' in stock:",
            'if "None" in stock or stock.lower() == "none":'
        )
        return new_line, True
    
    return line, False


def fix_file(filepath: Path) -> Tuple[bool, str, List[int]]:
    """
    Fix stock case-sensitivity in a single file
    
    Returns:
        (success, message, list of changed line numbers)
    """
    try:
        lines = read_file(filepath)
        fixed_lines = []
        changes_made = False
        changed_lines = []
        
        for line_num, line in enumerate(lines, 1):
            new_line, changed = fix_stock_check(line)
            fixed_lines.append(new_line)
            
            if changed:
                changes_made = True
                changed_lines.append(line_num)
                print(f"  Line {line_num}:")
                print(f"    Before: {line.strip()}")
                print(f"    After:  {new_line.strip()}")
        
        if changes_made:
            return True, "Fixed", changed_lines
        else:
            return False, "No changes needed (pattern not found)", []
    
    except Exception as e:
        return False, f"Error: {str(e)}", []


def preview_fixes() -> None:
    """Preview all fixes without applying them"""
    print("=" * 80)
    print("PREVIEW MODE - No files will be modified")
    print("=" * 80)
    print()
    
    total_files = len(FILES_TO_FIX)
    fixed_count = 0
    
    for filename, expected_line in FILES_TO_FIX:
        filepath = BASE_DIR / filename
        print(f"Checking: {filename} (expected line ~{expected_line})")
        
        if not filepath.exists():
            print(f"  ⚠️  File not found: {filepath}")
            continue
        
        success, message, changed_lines = fix_file(filepath)
        if success:
            fixed_count += 1
            print(f"  ✅ {message}")
            if changed_lines:
                print(f"  📍 Changed lines: {', '.join(map(str, changed_lines))}")
        else:
            print(f"  ℹ️  {message}")
        print()
    
    print("=" * 80)
    print(f"PREVIEW SUMMARY: {fixed_count}/{total_files} files would be modified")
    print("=" * 80)


def apply_fixes() -> None:
    """Apply all fixes to files"""
    print("=" * 80)
    print("APPLYING FIXES - Files will be modified")
    print("=" * 80)
    print()
    
    total_files = len(FILES_TO_FIX)
    fixed_count = 0
    errors = []
    
    for filename, expected_line in FILES_TO_FIX:
        filepath = BASE_DIR / filename
        print(f"Fixing: {filename}")
        
        if not filepath.exists():
            error_msg = f"File not found: {filepath}"
            print(f"  ❌ {error_msg}")
            errors.append((filename, error_msg))
            continue
        
        try:
            # Read original
            original_lines = read_file(filepath)
            
            # Apply fix
            fixed_lines = []
            changes_made = False
            changed_lines = []
            
            for line_num, line in enumerate(original_lines, 1):
                new_line, changed = fix_stock_check(line)
                fixed_lines.append(new_line)
                if changed:
                    changes_made = True
                    changed_lines.append(line_num)
            
            # Write if changed
            if changes_made:
                write_file(filepath, fixed_lines)
                fixed_count += 1
                print(f"  ✅ Fixed and saved")
                print(f"  📍 Changed lines: {', '.join(map(str, changed_lines))}")
            else:
                print(f"  ℹ️  No changes needed")
        
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Error: {error_msg}")
            errors.append((filename, error_msg))
        
        print()
    
    print("=" * 80)
    print(f"COMPLETED: {fixed_count}/{total_files} files modified")
    print("=" * 80)
    
    if errors:
        print()
        print("ERRORS:")
        for filename, error in errors:
            print(f"  - {filename}: {error}")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python fix_stock_case_sensitivity.py --dry-run   # Preview changes")
        print("  python fix_stock_case_sensitivity.py --apply     # Apply fixes")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "--dry-run":
        preview_fixes()
    elif mode == "--apply":
        confirm = input("This will modify 2 calculator files. Continue? (yes/no): ")
        if confirm.lower() == "yes":
            apply_fixes()
        else:
            print("Cancelled.")
    else:
        print(f"Unknown mode: {mode}")
        print("Use --dry-run or --apply")
        sys.exit(1)


if __name__ == "__main__":
    main()
