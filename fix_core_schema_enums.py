"""
Fix Core Schema Enum Values
============================

PROBLEM: Core schema has enum values that don't match the descriptions!

Example:
description: "Valid options: '270mm W x 1000mm H - Three Sided', '270mm W x 1200mm H - Three Sided'..."
enum: ["A4", "A5", "A6", "DL", "A3", "6pp A4"]  ← WRONG!

This script extracts the CORRECT enum values from descriptions and updates the enum arrays.

Date: December 11, 2025
"""

import json
import re
from pathlib import Path

CORE_SCHEMA_PATH = Path(__file__).parent / "tools" / "schemas" / "calculator_tools.json"

def extract_enum_from_description(description):
    """
    Extract enum values from description text like:
    "Valid options: 'Value 1', 'Value 2', 'Value 3'"
    """
    pattern = r"Valid options: ([^\n]+)"
    match = re.search(pattern, description)
    
    if not match:
        return None
    
    options_text = match.group(1)
    
    # Extract quoted values
    values = re.findall(r"'([^']+)'", options_text)
    
    return values if values else None

def fix_enum_values():
    """Fix enum values in core schema"""
    
    print("=" * 80)
    print("FIXING CORE SCHEMA ENUM VALUES")
    print("=" * 80)
    print()
    
    # Load core schema
    with open(CORE_SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    fixed_count = 0
    fixes_made = []
    
    # Process each tool
    for tool in schema['tools']:
        tool_name = tool['name']
        params = tool.get('parameters', {})
        
        if not params:
            continue
        
        # Check each parameter
        for param_name, param_def in params.items():
            description = param_def.get('description', '')
            current_enum = param_def.get('enum', [])
            
            # Try to extract enum from description
            extracted_enum = extract_enum_from_description(description)
            
            if extracted_enum and extracted_enum != current_enum:
                # Update enum
                param_def['enum'] = extracted_enum
                fixed_count += 1
                
                fixes_made.append({
                    'tool': tool_name,
                    'parameter': param_name,
                    'old_enum': current_enum,
                    'new_enum': extracted_enum
                })
                
                print(f"🔧 Fixed: {tool_name}.{param_name}")
                print(f"   Old ({len(current_enum)} values): {current_enum[:3]}...")
                print(f"   New ({len(extracted_enum)} values): {extracted_enum[:3]}...")
                print()
    
    if fixed_count > 0:
        # Save updated schema
        with open(CORE_SCHEMA_PATH, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"✓ Fixed {fixed_count} parameter enum arrays")
        print()
        
        print("Affected tools:")
        for fix in fixes_made:
            print(f"  • {fix['tool']}.{fix['parameter']}")
        print()
        
        print("=" * 80)
        print("✅ CORE SCHEMA FIXED!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Run: python sync_module_schema_complete.py")
        print("2. Restart: BISTART")
        print("3. Test: Run calculator tests")
        print()
    else:
        print("✓ No fixes needed - enum values already correct!")

if __name__ == "__main__":
    try:
        fix_enum_values()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
