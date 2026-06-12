"""Find tool schemas with invalid property names for Claude API"""
import json
import re
import os
from pathlib import Path

# Claude API pattern: only a-z, A-Z, 0-9, _, -, . and max 64 chars
pattern = re.compile(r'^[a-zA-Z0-9_.-]{1,64}$')

schemas_dir = Path('tools/schemas')
invalid_found = []

for schema_file in schemas_dir.glob('*.json'):
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tools = data.get('tools', [])
        
        for tool in tools:
            tool_name = tool.get('name', 'unknown')
            params = tool.get('parameters', {})
            
            # Check if parameters has 'properties' (Format 2)
            properties = params.get('properties', {})
            
            # Also check old format where properties are at params level
            if not properties and params:
                # Old format check
                for key in params.keys():
                    if isinstance(params[key], dict) and 'type' in params[key]:
                        properties[key] = params[key]
            
            for prop_name in properties.keys():
                if not pattern.match(prop_name):
                    invalid_found.append({
                        'file': schema_file.name,
                        'tool': tool_name,
                        'property': prop_name,
                        'issue': 'Invalid characters or length > 64'
                    })
    except Exception as e:
        print(f"Error reading {schema_file.name}: {e}")

print("="*80)
print("INVALID TOOL PROPERTY NAMES")
print("="*80)

if invalid_found:
    print(f"\nFound {len(invalid_found)} invalid property names:\n")
    for item in invalid_found:
        print(f"File: {item['file']}")
        print(f"  Tool: {item['tool']}")
        print(f"  Property: '{item['property']}'")
        print(f"  Issue: {item['issue']}")
        print()
else:
    print("\nNo invalid property names found!")

print("="*80)
