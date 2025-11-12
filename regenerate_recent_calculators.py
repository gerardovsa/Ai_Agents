"""
Regenerate recently added calculators with improved schema (complete option listings)
"""

import subprocess
import sys

# List of calculators added in this session (13-22)
calculators = [
    "Shopify_Saddle_Stitch_Books.json",
    "Shopify_Spiral_Bound_Books.json",
    "Shopify_Bollard_Signs.json",
    "Shopify_Stackable_Cubes.json",
    "Shopify_Election_Signs.json",
    "Shopify_Selfie_Frames.json",
    "Shopify_Construction_Signs.json",
    "Shopify_Strut_Cards_A3.json",
    "Shopify_Strut_Cards_A4.json"
]

print("=" * 80)
print("REGENERATING 9 RECENT CALCULATORS WITH IMPROVED SCHEMA")
print("=" * 80)
print()

success_count = 0
failed = []

for i, calc in enumerate(calculators, 1):
    print(f"[{i}/9] Processing: {calc}")
    
    try:
        # Run the automation script with force flag
        result = subprocess.run(
            ['python', 'scripts\\setup\\add_shopify_calculator.py', '--json', calc, '--force'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and 'Successfully processed' in result.stdout:
            print(f"  SUCCESS: {calc}")
            success_count += 1
        else:
            print(f"  FAILED: {calc}")
            failed.append(calc)
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
    
    except Exception as e:
        print(f"  ERROR: {calc} - {str(e)}")
        failed.append(calc)
    
    print()

print("=" * 80)
print("REGENERATION COMPLETE")
print("=" * 80)
print(f"Success: {success_count}/9")
if failed:
    print(f"Failed: {len(failed)}")
    for calc in failed:
        print(f"  - {calc}")
else:
    print("All calculators regenerated successfully!")
