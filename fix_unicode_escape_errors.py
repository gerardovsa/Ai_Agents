"""
Fix Unicode Escape Errors in Shopify Calculators

Replaces single-backslash Windows paths with raw strings (r"...") 
to prevent Python from interpreting backslashes as escape sequences.
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
        
        # Fix pattern 1: Based on: c:\Users\...
        # Replace with: Based on: r"c:\Users\..."
        content = re.sub(
            r'Based on: (c:\\Users\\[^\n]+)',
            r'Based on: r"\1"',
            content
        )
        
        # Fix pattern 2: CONFIG_FILE = "c:\Users\..."
        # Replace with: CONFIG_FILE = r"c:\Users\..."
        content = re.sub(
            r'CONFIG_FILE = "(c:\\Users\\[^"]+)"',
            r'CONFIG_FILE = r"\1"',
            content
        )
        
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
    print("FIXING UNICODE ESCAPE ERRORS IN SHOPIFY CALCULATORS")
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
        print("\n✅ Files fixed! The calculator wrapper should now load without errors.")
        print("\nYou can test with:")
        print("  BISTART")

if __name__ == "__main__":
    main()
