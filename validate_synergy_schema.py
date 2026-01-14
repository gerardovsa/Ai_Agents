"""Validate synergy_tools.json is valid JSON and meets Anthropic requirements"""

import json
import sys

print("Loading synergy_tools.json...")

try:
    with open('tools/schemas/synergy_tools.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Valid JSON ({len(data['tools'])} tools)\n")
    
    # Find synergy_update_session
    update_tool = None
    for i, tool in enumerate(data['tools']):
        if tool['name'] == 'synergy_update_session':
            update_tool = tool
            print(f"Found synergy_update_session at index {i}\n")
            break
    
    if not update_tool:
        print("ERROR: synergy_update_session not found!")
        sys.exit(1)
    
    # Check for problematic patterns
    tool_str = json.dumps(update_tool)
    
    issues = []
    
    if '"oneOf"' in tool_str:
        issues.append("Contains oneOf")
    if '"anyOf"' in tool_str:
        issues.append("Contains anyOf")
    if '"allOf"' in tool_str:
        issues.append("Contains allOf")
    
    # Check if examples is inside input_schema/parameters
    params = update_tool.get('parameters', {})
    params_str = json.dumps(params)
    if '"examples"' in params_str:
        issues.append("Examples found inside parameters (should be outside)")
    
    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(f"  ❌ {issue}")
        print(f"\nTool structure:")
        print(json.dumps(update_tool, indent=2))
    else:
        print("✓ No obvious schema issues found!")
        print("\nTool has:")
        print(f"  - Name: {update_tool['name']}")
        print(f"  - Parameters: {len(update_tool.get('parameters', {}).get('properties', {}))} properties")
        print(f"  - Required: {update_tool.get('parameters', {}).get('required', [])}")
        print(f"  - Examples: {len(update_tool.get('examples', []))} examples")
        print(f"  - Examples location: Outside parameters ✓")
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
