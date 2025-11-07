#!/usr/bin/env python
"""
Fix all Microsoft tool schemas - Convert Format 1 to Format 2 (Anthropic format)
Handles: word, excel, outlook, onedrive, teams, calendar, todo, forms, sharepoint, onenote
"""

import json
import glob
from pathlib import Path

def convert_parameters_to_anthropic_format(params):
    """
    Convert from Format 1 (flat with required property) to Format 2 (Anthropic format)
    
    Format 1: {"param": {"type": "string", "required": true, "description": "..."}}
    Format 2: {"type": "object", "properties": {...}, "required": [...]}
    """
    
    # If already in Format 2, return as-is
    if isinstance(params, dict) and params.get("type") == "object" and "properties" in params:
        return params
    
    # Convert Format 1 to Format 2
    properties = {}
    required = []
    
    if isinstance(params, dict):
        for param_name, param_def in params.items():
            if isinstance(param_def, dict):
                # Extract required flag
                is_required = param_def.pop("required", False)
                
                # Build property
                prop = {
                    "type": param_def.get("type", "string"),
                    "description": param_def.get("description", "")
                }
                
                # Copy other properties
                if "default" in param_def:
                    prop["default"] = param_def["default"]
                if "enum" in param_def:
                    prop["enum"] = param_def["enum"]
                if "items" in param_def:
                    prop["items"] = param_def["items"]
                
                properties[param_name] = prop
                
                if is_required:
                    required.append(param_name)
    
    return {
        "type": "object",
        "properties": properties,
        "required": required
    }

def fix_tool_schema(tool):
    """Fix a single tool schema"""
    if "parameters" in tool:
        tool["parameters"] = convert_parameters_to_anthropic_format(tool["parameters"])
    return tool

def fix_file(filepath):
    """Fix all tools in a file"""
    print(f"Fixing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Fix all tools
    if "tools" in data:
        for tool in data["tools"]:
            fix_tool_schema(tool)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✓ Fixed: {filepath}")

# Find all Microsoft tool schema files
schema_dir = Path("c:\\Users\\gpoli\\GIT\\AI_agents\\tools\\schemas")
microsoft_files = list(schema_dir.glob("microsoft_*.json"))

print(f"Found {len(microsoft_files)} Microsoft schema files\n")

# Fix each file
for filepath in sorted(microsoft_files):
    try:
        fix_file(str(filepath))
    except Exception as e:
        print(f"✗ Error fixing {filepath}: {e}")

print(f"\n✓ All {len(microsoft_files)} Microsoft schemas converted to Anthropic Format!")
