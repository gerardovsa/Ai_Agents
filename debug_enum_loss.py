#!/usr/bin/env python
"""Debug where enums are getting lost"""
import json
import os

# Step 1: Load calculator_tools.json directly FROM TOOLS/SCHEMAS (where registry loads from)
json_path = os.path.join(os.path.dirname(__file__), 'tools', 'schemas', 'calculator_tools.json')
with open(json_path, 'r') as f:
    data = json.load(f)

# Find bollard_signs
bollard_tool = None
for tool in data.get('tools', []):
    if tool['name'] == 'calculate_bollard_signs':
        bollard_tool = tool
        break

print('=== STEP 1: calculator_tools.json (SOURCE OF TRUTH) ===')
print(f'Quantity has enum in JSON: {"enum" in bollard_tool["parameters"]["quantity"]}')
if 'enum' in bollard_tool["parameters"]["quantity"]:
    print(f'Quantity enum values: {bollard_tool["parameters"]["quantity"]["enum"][:3]}...')

# Step 2: Check how registry loads it
from tools.registry_v3 import get_registry
registry = get_registry()

print('\n=== STEP 2: registry.tools[calculate_bollard_signs] ===')
if 'calculate_bollard_signs' in registry.tools:
    tool = registry.tools['calculate_bollard_signs']
    params = tool.get('parameters', {})
    props = params.get('properties', params)
    
    if 'quantity' in props:
        print(f'Quantity has enum in registry.tools: {"enum" in props["quantity"]}')
        if 'enum' in props['quantity']:
            print(f'Quantity enum: {props["quantity"]["enum"][:3]}...')
        else:
            print(f'Quantity keys: {list(props["quantity"].keys())}')

# Step 3: Check get_anthropic_tools()
print('\n=== STEP 3: registry.get_anthropic_tools() ===')
anthropic_tools = registry.get_anthropic_tools()
bollard_anthropic = None
for at in anthropic_tools:
    if at.get('name') == 'calculate_bollard_signs':
        bollard_anthropic = at
        break

if bollard_anthropic:
    input_schema = bollard_anthropic.get('input_schema', {})
    props = input_schema.get('properties', {})
    
    if 'quantity' in props:
        print(f'Quantity has enum in Anthropic format: {"enum" in props["quantity"]}')
        if 'enum' in props['quantity']:
            print(f'Quantity enum: {props["quantity"]["enum"][:3]}...')
        else:
            print(f'Quantity keys: {list(props["quantity"].keys())}')
            print(f'Quantity definition: {json.dumps(props["quantity"], indent=2)}')

# Step 4: Check get_tool_schema()
from tools.implementations.meta_tools import get_tool_schema

print('\n=== STEP 4: get_tool_schema() FINAL OUTPUT ===')
result = get_tool_schema('calculate_bollard_signs')
props = result['input_schema']['properties']

print(f'Quantity has enum in final output: {"enum" in props["quantity"]}')
if 'enum' in props['quantity']:
    print(f'Quantity enum: {props["quantity"]["enum"][:3]}...')
else:
    print(f'Quantity keys: {list(props["quantity"].keys())}')
    print(f'Quantity definition: {json.dumps(props["quantity"], indent=2)}')
