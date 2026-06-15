"""
Fix config_manager imports in all Shopify calculators

The calculators were trying to import config_manager from parent.parent.parent/config
but config_manager.py is in the same folder (shopify_calculators/).

This script removes the incorrect sys.path manipulation.
"""

import os
from pathlib import Path

# Get shopify_calculators directory
shopify_dir = Path(__file__).parent / "backend" / "shopify_calculators"

# Pattern to find and remove
patterns_to_remove = [
    'config_dir = Path(__file__).parent.parent.parent / "config"',
    'sys.path.insert(0, str(config_dir))'
]

# Files to fix (all Shopify calculators that import config_manager)
files_to_fix = [
    "ElectionSigns_Shopify_Calculator.py",
    "NotepadsA4_Shopify_Calculator.py",
    "EconomicalBusinessCards_Shopify_Calculator.py",
    "SaddleStitchBooks_Shopify_Calculator.py",
    "StrutCardsA3_Shopify_Calculator.py",
    "WithComplimentsSlips_Shopify_Calculator.py",
    "StrutCardsA4_Shopify_Calculator.py",
    "StackableCubes_Shopify_Calculator.py",
    "SelfieFrames_Shopify_Calculator.py",
    "SpiralBoundBooks_Shopify_Calculator.py",
    "PrintedLetterheads_Shopify_Calculator.py",
    "PremiumBookmarks_Shopify_Calculator.py",
    "NotepadsA5_Shopify_Calculator.py",
    "NotepadsA6_Shopify_Calculator.py",
    "MetalFaceA_Frame_Shopify_Calculator.py",
    "LuxuryClassicPullUpBanners_Shopify_Calculator.py",
    "MetalFaceA-Frame_Shopify_Calculator.py",
    "FoldedFlyers_Shopify_Calculator.py",
    "CustomVinylStickers_Shopify_Calculator.py",
    "CustomPosterPrinting_Shopify_Calculator.py",
    "CorfluteInsertA-Frame_Shopify_Calculator.py",
    "BollardSigns_Shopify_Calculator.py",
    "ConstructionSigns_Shopify_Calculator.py",
    "PremiumBusinessCards_Shopify_Calculator.py",
]

fixed_count = 0
error_count = 0

for filename in files_to_fix:
    filepath = shopify_dir / filename
    
    if not filepath.exists():
        print(f"⚠️  SKIP: {filename} (file not found)")
        continue
    
    try:
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove the incorrect import lines
        new_lines = []
        removed_lines = []
        
        for i, line in enumerate(lines):
            # Check if line contains the incorrect pattern
            should_remove = False
            for pattern in patterns_to_remove:
                if pattern in line:
                    should_remove = True
                    removed_lines.append(f"  Line {i+1}: {line.strip()}")
                    break
            
            if not should_remove:
                new_lines.append(line)
        
        if removed_lines:
            # Write updated file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"✅ FIXED: {filename}")
            for removed in removed_lines:
                print(removed)
            fixed_count += 1
        else:
            print(f"ℹ️  OK: {filename} (no changes needed)")
    
    except Exception as e:
        print(f"❌ ERROR: {filename} - {e}")
        error_count += 1

print(f"\n{'='*60}")
print(f"Summary: {fixed_count} files fixed, {error_count} errors")
print(f"{'='*60}")
print("\nThe calculators now import config_manager from the same directory.")
print("Run test_comprehensive.py to verify all 40 tests pass.")
