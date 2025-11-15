"""
Fix Unicode Escape Errors in Shopify Calculators V2

Replace backslashes with forward slashes in docstrings and double backslashes in strings.
"""

import os
import re
from pathlib import Path

def fix_file(file_path):
    """Fix unicode escape errors in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix pattern 1: Based on: in docstrings - replace backslashes with forward slashes
        content = re.sub(
            r'Based on: r"(c:\\Users\\[^"]+)"',
            lambda m: f'Based on: {m.group(1).replace(chr(92), "/")}',  # chr(92) = backslash
            content
        )
        
        # Also fix if not prefixed with r"
        content = re.sub(
            r'Based on: (c:\\Users\\[^\n"]+)',
            lambda m: f'Based on: {m.group(1).replace(chr(92), "/")}',
            content
        )
        
        # Fix pattern 2: CONFIG_FILE - use raw string properly (already has r")
        # No change needed if already has r", but let's ensure double backslashes if no r"
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed"
        else:
            return False, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Fix all Shopify calculator files"""
    shopify_dir = Path('inhouse_modules/shopify_calculators')
    
    if not shopify_dir.exists():
        print(f"❌ Directory not found: {shopify_dir}")
        return
    
    print("="*80)
    print("FIXING UNICODE ESCAPE ERRORS IN SHOPIFY CALCULATORS (V2 - Forward Slashes)")
    print("="*80)
    
    fixed_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path in shopify_dir.glob('*_Shopify_Calculator.py'):
        success, message = fix_file(file_path)
        
        if success:
            print(f"✅ {file_path.name:<50} {message}")
            fixed_count += 1
        elif "Error" in message:
            print(f"❌ {file_path.name:<50} {message}")
            error_count += 1
        else:
            print(f"⏭️  {file_path.name:<50} {message}")
            skipped_count += 1
    
    print("="*80)
    print(f"SUMMARY: {fixed_count} fixed, {skipped_count} skipped, {error_count} errors")
    print("="*80)
    
    if fixed_count > 0:
        print("\n✅ Files fixed! Backslashes replaced with forward slashes in docstrings.")
        print("\nTest with:")
        print("  python -c \"from inhouse_modules.shopify_calculators.NotepadsA5_Shopify_Calculator import NotepadsA5ShopifyCalculator\"")

if __name__ == "__main__":
    main()
