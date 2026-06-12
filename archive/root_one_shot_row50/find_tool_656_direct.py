"""Find tool 656 by directly loading schemas without full registry"""

import json
import os
from pathlib import Path

schemas_dir = Path('tools/schemas')

all_tools = []

# Load all schema files
for schema_file in sorted(schemas_dir.glob('*.json')):
    try:
        with open(schema_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        tools = data.get('tools', [])
        for tool in tools:
            all_tools.append({
                'name': tool.get('name'),
                'file': schema_file.name,
                'platform': tool.get('platform', 'N/A')
            })
    except Exception as e:
        print(f"Error loading {schema_file.name}: {e}")

print(f"Loaded {len(all_tools)} tools from schemas\n")

if len(all_tools) > 656:
    tool = all_tools[656]
    print(f"Tool at index 656:")
    print(f"  Name: {tool['name']}")
    print(f"  File: {tool['file']}")
    print(f"  Platform: {tool['platform']}")
    
    # Load the full tool definition
    schema_file = schemas_dir / tool['file']
    with open(schema_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for t in data['tools']:
        if t['name'] == tool['name']:
            print(f"\nFull tool definition:")
            print(json.dumps(t, indent=2))
            break
else:
    print(f"Only {len(all_tools)} tools found, cannot access index 656")
