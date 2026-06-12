"""
Complete Module Schema Synchronization Script
==============================================

This script fully synchronizes calculator tool parameters from the CORE schema
to the MODULE PLUGIN schema. Unlike the enum-only sync, this does a COMPLETE
parameter replacement to fix:

1. Wrong enum VALUES (e.g., "A4" instead of "270mm x 1000mm - Three Sided")
2. Wrong parameter TYPES (e.g., integer vs string)
3. Wrong parameter NAMES (e.g., "print_sides" vs "sides")
4. Missing descriptions
5. Missing required fields

Strategy:
- Core schema (tools/schemas/calculator_tools.json) = SOURCE OF TRUTH
- Module plugin schema (UI/modules_external/.../calculator_tools.json) = TARGET
- For each matching calculator tool, FULLY REPLACE parameters object

Date: December 11, 2025
Status: PRODUCTION READY
"""

import json
from pathlib import Path

# File paths
CORE_SCHEMA_PATH = Path(__file__).parent / "tools" / "schemas" / "calculator_tools.json"
MODULE_SCHEMA_PATH = Path(__file__).parent / "UI" / "modules_external" / "quote-calculator" / "schema" / "calculator_tools.json"

def load_schema(path):
    """Load JSON schema with UTF-8 encoding"""
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_schema(path, data):
    """Save JSON schema with UTF-8 encoding and proper formatting"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def sync_complete_parameters():
    """
    Fully synchronize calculator parameters from core to module schema
    """
    print("=" * 80)
    print("COMPLETE MODULE SCHEMA SYNCHRONIZATION")
    print("=" * 80)
    print()
    
    # Load schemas
    print(f"📖 Loading core schema: {CORE_SCHEMA_PATH}")
    core_schema = load_schema(CORE_SCHEMA_PATH)
    
    print(f"📖 Loading module schema: {MODULE_SCHEMA_PATH}")
    module_schema = load_schema(MODULE_SCHEMA_PATH)
    
    # Build lookup for core tools
    core_tools = {tool['name']: tool for tool in core_schema['tools']}
    
    print(f"\n✓ Core schema: {len(core_tools)} tools")
    print(f"✓ Module schema: {len(module_schema['tools'])} tools")
    print()
    
    # Track changes
    updated_count = 0
    updated_tools = []
    parameter_changes = []
    
    # Sync each module tool
    for i, module_tool in enumerate(module_schema['tools']):
        tool_name = module_tool['name']
        
        # Check if tool exists in core schema
        if tool_name not in core_tools:
            continue
        
        core_tool = core_tools[tool_name]
        
        # Check if parameters need updating
        core_params = core_tool.get('parameters', {})
        module_params = module_tool.get('parameters', {})
        
        # Skip if both empty
        if not core_params and not module_params:
            continue
        
        # Compare parameters - check if they're different
        params_different = False
        changes_detail = []
        
        if core_params != module_params:
            params_different = True
            
            # Detailed comparison for reporting
            core_props = core_params.get('properties', {})
            module_props = module_params.get('properties', {})
            
            for param_name in set(list(core_props.keys()) + list(module_props.keys())):
                core_param = core_props.get(param_name, {})
                module_param = module_props.get(param_name, {})
                
                if core_param != module_param:
                    # Check what changed
                    if param_name not in module_props:
                        changes_detail.append(f"  + Added parameter: {param_name}")
                    elif param_name not in core_props:
                        changes_detail.append(f"  - Removed parameter: {param_name}")
                    else:
                        # Parameter exists in both - check what's different
                        if core_param.get('type') != module_param.get('type'):
                            changes_detail.append(f"  ~ {param_name}: type changed")
                        if core_param.get('enum') != module_param.get('enum'):
                            core_enum_count = len(core_param.get('enum', []))
                            module_enum_count = len(module_param.get('enum', []))
                            changes_detail.append(f"  ~ {param_name}: enum values changed ({module_enum_count} → {core_enum_count} values)")
                        if core_param.get('description') != module_param.get('description'):
                            changes_detail.append(f"  ~ {param_name}: description updated")
        
        # Update if different
        if params_different:
            # COMPLETE REPLACEMENT of parameters
            module_schema['tools'][i]['parameters'] = core_params
            
            updated_count += 1
            updated_tools.append(tool_name)
            parameter_changes.append({
                'tool': tool_name,
                'changes': changes_detail
            })
            
            print(f"🔄 Updated: {tool_name}")
            for change in changes_detail:
                print(f"   {change}")
            print()
    
    # Save updated module schema
    if updated_count > 0:
        print("=" * 80)
        print(f"💾 Saving updated module schema...")
        save_schema(MODULE_SCHEMA_PATH, module_schema)
        print(f"✅ Module schema updated successfully!")
        print()
        
        # Summary
        print("=" * 80)
        print("SYNCHRONIZATION SUMMARY")
        print("=" * 80)
        print(f"✓ Updated {updated_count} calculator tools")
        print()
        print("Updated tools:")
        for tool_name in updated_tools:
            print(f"  • {tool_name}")
        print()
        
        # Detailed changes
        print("=" * 80)
        print("DETAILED PARAMETER CHANGES")
        print("=" * 80)
        for change_info in parameter_changes:
            print(f"\n📦 {change_info['tool']}:")
            for change in change_info['changes']:
                print(change)
        
        print()
        print("=" * 80)
        print("🎉 SYNC COMPLETE!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Restart BISTART server to load updated schemas")
        print("2. Run tests to verify 100% pass rate")
        print("3. Check calculator_test_dashboard.html for results")
        print()
        
    else:
        print("=" * 80)
        print("✓ No updates needed - schemas already in sync!")
        print("=" * 80)
        print()

if __name__ == "__main__":
    try:
        sync_complete_parameters()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
