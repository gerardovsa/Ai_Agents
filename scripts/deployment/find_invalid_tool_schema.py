"""Find and identify invalid tool schema causing production error"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'AI_infrastructure'))

from tools.registry_v3 import RegistryV3

print("="*70)
print("TOOL SCHEMA VALIDATION")
print("="*70)

# Load registry
registry = RegistryV3()

# Get Anthropic-formatted tools
anthropic_tools = registry.get_anthropic_tools()

print(f"\nTotal tools loaded: {len(anthropic_tools)}")
print(f"Looking for tool #507...")

# Check tool #507
if len(anthropic_tools) >= 508:
    tool_507 = anthropic_tools[507]
    
    print(f"\n{'='*70}")
    print(f"TOOL #507 DETAILS")
    print(f"{'='*70}")
    print(f"Name: {tool_507.get('name', 'UNKNOWN')}")
    print(f"Description: {tool_507.get('description', 'N/A')[:100]}...")
    
    # Check input_schema
    if 'input_schema' in tool_507:
        schema = tool_507['input_schema']
        print(f"\nInput Schema Type: {schema.get('type', 'MISSING')}")
        print(f"Has 'properties': {'properties' in schema}")
        print(f"Has 'required': {'required' in schema}")
        
        # Check for common issues
        issues = []
        
        if schema.get('type') != 'object':
            issues.append(f"Invalid type: {schema.get('type')}")
        
        if 'properties' not in schema:
            issues.append("Missing 'properties' field")
        
        if 'properties' in schema:
            props = schema['properties']
            print(f"Properties count: {len(props)}")
            
            # Check each property
            for prop_name, prop_def in props.items():
                if not isinstance(prop_def, dict):
                    issues.append(f"Property '{prop_name}' is not a dict: {type(prop_def)}")
                elif 'type' not in prop_def and 'anyOf' not in prop_def and 'oneOf' not in prop_def:
                    issues.append(f"Property '{prop_name}' missing type definition")
        
        if issues:
            print(f"\n{'='*70}")
            print("ISSUES FOUND:")
            print(f"{'='*70}")
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
        else:
            print("\nNo obvious issues found in tool #507")
            print("Checking for 'custom' namespace issue...")
            
            # Check if tool has 'custom' field
            if 'custom' in tool_507:
                print(f"WARNING: Tool has 'custom' field: {tool_507['custom']}")
                issues.append("Unexpected 'custom' field in tool definition")
    else:
        print("\nERROR: Tool #507 has no 'input_schema' field!")
        issues = ["Missing 'input_schema' field"]
    
    # Print full tool for debugging
    if issues:
        print(f"\n{'='*70}")
        print("FULL TOOL DEFINITION (for debugging):")
        print(f"{'='*70}")
        import json
        print(json.dumps(tool_507, indent=2)[:2000])
else:
    print(f"\nERROR: Only {len(anthropic_tools)} tools loaded, cannot access tool #507")

# Also check for any tools with invalid schemas
print(f"\n\n{'='*70}")
print("SCANNING ALL TOOLS FOR SCHEMA ISSUES")
print(f"{'='*70}")

invalid_tools = []

for i, tool in enumerate(anthropic_tools):
    issues = []
    
    # Check basic structure
    if 'name' not in tool:
        issues.append("Missing 'name'")
    if 'description' not in tool:
        issues.append("Missing 'description'")
    if 'input_schema' not in tool:
        issues.append("Missing 'input_schema'")
    elif not isinstance(tool['input_schema'], dict):
        issues.append(f"input_schema is not dict: {type(tool['input_schema'])}")
    else:
        schema = tool['input_schema']
        if schema.get('type') != 'object':
            issues.append(f"Invalid schema type: {schema.get('type')}")
        if 'properties' not in schema:
            issues.append("Missing 'properties'")
    
    # Check for unexpected fields
    expected_fields = {'name', 'description', 'input_schema'}
    unexpected = set(tool.keys()) - expected_fields
    if unexpected:
        issues.append(f"Unexpected fields: {unexpected}")
    
    if issues:
        invalid_tools.append({
            'index': i,
            'name': tool.get('name', 'UNKNOWN'),
            'issues': issues
        })

if invalid_tools:
    print(f"\nFound {len(invalid_tools)} tools with issues:\n")
    for tool in invalid_tools[:20]:  # Show first 20
        print(f"Tool #{tool['index']}: {tool['name']}")
        for issue in tool['issues']:
            print(f"  - {issue}")
        print()
else:
    print("\nAll tools appear to have valid schemas!")

print(f"\n{'='*70}")
print("SCAN COMPLETE")
print(f"{'='*70}\n")
