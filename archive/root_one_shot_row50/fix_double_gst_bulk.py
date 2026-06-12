"""
Bulk Fix Script for Shopify Calculator Double GST Issues

This script automatically fixes the double GST application bug in 21 Shopify calculators.

ISSUE: Calculators apply GST twice: (subtotal * 1.1) * 1.1 = 21% tax instead of 10%
FIX: Apply GST once: subtotal * 1.1 = 10% tax (correct)

AFFECTED: 21 calculator files
IMPACT: Reduces customer prices by ~9-10%

USAGE:
    python fix_double_gst_bulk.py --dry-run  # Preview changes
    python fix_double_gst_bulk.py --apply    # Apply fixes

LAST MODIFIED: 2026-01-03 - Initial creation
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# Base directory for Shopify calculators
BASE_DIR = Path("UI/modules_external/quote-calculator/backend/shopify_calculators")

# Files to fix with line numbers where double GST occurs
FILES_TO_FIX = [
    ("PremiumBookmarks_Shopify_Calculator.py", 110),
    ("LuxuryClassicPullUpBanners_Shopify_Calculator.py", 98),
    ("NotepadsA4_Shopify_Calculator.py", 129),
    ("NotepadsA5_Shopify_Calculator.py", 124),
    ("NotepadsA6_Shopify_Calculator.py", 124),
    ("PrintedLetterheads_Shopify_Calculator.py", 136),
    ("WithComplimentsSlips_Shopify_Calculator.py", 124),
    ("StrutCardsA3_Shopify_Calculator.py", 113),
    ("StrutCardsA4_Shopify_Calculator.py", 113),
    ("SelfieFrames_Shopify_Calculator.py", 104),
    ("StackableCubes_Shopify_Calculator.py", 104),
    ("CustomVinylStickers_Shopify_Calculator.py", 102),
    ("CustomPosterPrinting_Shopify_Calculator.py", 106),
    ("SpiralBoundBooks_Shopify_Calculator.py", 106),
    ("BollardSigns_Shopify_Calculator.py", 117),
    ("ConstructionSigns_Shopify_Calculator.py", 116),
    ("ElectionSigns_Shopify_Calculator.py", 128),
    ("MetalFaceA_Frame_Shopify_Calculator.py", 114),
    ("MetalFaceA-Frame_Shopify_Calculator.py", 114),
    ("CorfluteInsertA_Frame_Shopify_Calculator.py", 115),
    ("CorfluteInsertA-Frame_Shopify_Calculator.py", 113),
]

# Special case: PremiumBusinessCards has different variable names
PREMIUM_BUSINESS_CARDS = ("PremiumBusinessCards_Shopify_Calculator.py", 244)

# Patterns to find and replace
PATTERN_DOUBLE_GST = re.compile(
    r'total_price\s*=\s*\(\s*subtotal_with_increase\s*\*\s*GST_RATE\s*\)\s*\*\s*GST_RATE(\s*\+\s*SURCHARGE)?'
)

PATTERN_PREMIUM_CARDS = re.compile(
    r'total_price\s*=\s*subtotal_after_first_gst\s*\*\s*gst_rate'
)


def read_file(filepath: Path) -> List[str]:
    """Read file and return lines"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()


def write_file(filepath: Path, lines: List[str]) -> None:
    """Write lines to file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def fix_double_gst_standard(line: str) -> Tuple[str, bool]:
    """
    Fix standard double GST pattern
    
    Before: total_price = (subtotal_with_increase * GST_RATE) * GST_RATE + SURCHARGE
    After:  total_price = subtotal_with_increase * GST_RATE + SURCHARGE
    """
    match = PATTERN_DOUBLE_GST.search(line)
    if match:
        surcharge = match.group(1) or ""  # Preserve SURCHARGE if present
        new_line = line.replace(
            match.group(0),
            f"total_price = subtotal_with_increase * GST_RATE{surcharge}"
        )
        return new_line, True
    return line, False


def fix_premium_business_cards(line: str) -> Tuple[str, bool]:
    """
    Fix PremiumBusinessCards special case
    
    Before: total_price = subtotal_after_first_gst * gst_rate
    After:  total_price = subtotal_after_first_gst  # Already has GST applied
    """
    match = PATTERN_PREMIUM_CARDS.search(line)
    if match:
        indent = line[:len(line) - len(line.lstrip())]
        new_line = f"{indent}total_price = subtotal_after_first_gst  # Already has GST applied (removed double GST)\n"
        return new_line, True
    return line, False


def fix_file(filepath: Path, is_premium_cards: bool = False) -> Tuple[bool, str]:
    """
    Fix double GST in a single file
    
    Returns:
        (success, message)
    """
    try:
        lines = read_file(filepath)
        fixed_lines = []
        changes_made = False
        
        for line_num, line in enumerate(lines, 1):
            if is_premium_cards:
                new_line, changed = fix_premium_business_cards(line)
            else:
                new_line, changed = fix_double_gst_standard(line)
            
            fixed_lines.append(new_line)
            
            if changed:
                changes_made = True
                print(f"  Line {line_num}:")
                print(f"    Before: {line.strip()}")
                print(f"    After:  {new_line.strip()}")
        
        if changes_made:
            return True, "Fixed"
        else:
            return False, "No changes needed (pattern not found)"
    
    except Exception as e:
        return False, f"Error: {str(e)}"


def preview_fixes() -> None:
    """Preview all fixes without applying them"""
    print("=" * 80)
    print("PREVIEW MODE - No files will be modified")
    print("=" * 80)
    print()
    
    total_files = len(FILES_TO_FIX) + 1  # +1 for PremiumBusinessCards
    fixed_count = 0
    
    # Fix standard files
    for filename, line_num in FILES_TO_FIX:
        filepath = BASE_DIR / filename
        print(f"Checking: {filename} (line ~{line_num})")
        
        if not filepath.exists():
            print(f"  ⚠️  File not found: {filepath}")
            continue
        
        success, message = fix_file(filepath, is_premium_cards=False)
        if success:
            fixed_count += 1
            print(f"  ✅ {message}")
        else:
            print(f"  ℹ️  {message}")
        print()
    
    # Fix PremiumBusinessCards special case
    filename, line_num = PREMIUM_BUSINESS_CARDS
    filepath = BASE_DIR / filename
    print(f"Checking: {filename} (line ~{line_num}) - SPECIAL CASE")
    
    if filepath.exists():
        success, message = fix_file(filepath, is_premium_cards=True)
        if success:
            fixed_count += 1
            print(f"  ✅ {message}")
        else:
            print(f"  ℹ️  {message}")
    else:
        print(f"  ⚠️  File not found: {filepath}")
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
    
    total_files = len(FILES_TO_FIX) + 1
    fixed_count = 0
    errors = []
    
    # Fix standard files
    for filename, line_num in FILES_TO_FIX:
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
            
            for line in original_lines:
                new_line, changed = fix_double_gst_standard(line)
                fixed_lines.append(new_line)
                if changed:
                    changes_made = True
            
            # Write if changed
            if changes_made:
                write_file(filepath, fixed_lines)
                fixed_count += 1
                print(f"  ✅ Fixed and saved")
            else:
                print(f"  ℹ️  No changes needed")
        
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Error: {error_msg}")
            errors.append((filename, error_msg))
        
        print()
    
    # Fix PremiumBusinessCards special case
    filename, line_num = PREMIUM_BUSINESS_CARDS
    filepath = BASE_DIR / filename
    print(f"Fixing: {filename} - SPECIAL CASE")
    
    if filepath.exists():
        try:
            original_lines = read_file(filepath)
            fixed_lines = []
            changes_made = False
            
            for line in original_lines:
                new_line, changed = fix_premium_business_cards(line)
                fixed_lines.append(new_line)
                if changed:
                    changes_made = True
            
            if changes_made:
                write_file(filepath, fixed_lines)
                fixed_count += 1
                print(f"  ✅ Fixed and saved")
            else:
                print(f"  ℹ️  No changes needed")
        
        except Exception as e:
            error_msg = str(e)
            print(f"  ❌ Error: {error_msg}")
            errors.append((filename, error_msg))
    else:
        error_msg = "File not found"
        print(f"  ❌ {error_msg}")
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
        print("  python fix_double_gst_bulk.py --dry-run   # Preview changes")
        print("  python fix_double_gst_bulk.py --apply     # Apply fixes")
        sys.exit(1)
    
    mode = sys.argv[1]
    
    if mode == "--dry-run":
        preview_fixes()
    elif mode == "--apply":
        confirm = input("This will modify 22 calculator files. Continue? (yes/no): ")
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
