#!/usr/bin/env python3
"""
Fix all Microsoft tool schemas to use consistent 'microsoft_' prefix
This ensures Claude recognizes the tool names correctly
"""

import json
import os
from pathlib import Path

# Mapping of old prefix to new prefix
PREFIX_MAPPINGS = {
    'outlook_': 'microsoft_outlook_',
    'word_': 'microsoft_word_',
    'excel_': 'microsoft_excel_',
    'teams_': 'microsoft_teams_',
    'onedrive_': 'microsoft_onedrive_',
    'calendar_': 'microsoft_calendar_',
    'todo_': 'microsoft_todo_',
    'forms_': 'microsoft_forms_',
    'sharepoint_': 'microsoft_sharepoint_',
    'onenote_': 'microsoft_onenote_',
}

# Get schema directory
schemas_dir = Path(__file__).parent / 'tools' / 'schemas'

def rename_tool_in_schema(schema_file):
    """Rename all tools in a schema file to use microsoft_ prefix"""
    
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # Track changes
    changes = []
    
    # Process each tool
    for tool in schema.get('tools', []):
        old_name = tool.get('name', '')
        new_name = old_name
        
        # Apply prefix mapping
        for old_prefix, new_prefix in PREFIX_MAPPINGS.items():
            if old_name.startswith(old_prefix):
                new_name = new_prefix + old_name[len(old_prefix):]
                break
        
        if new_name != old_name:
            changes.append((old_name, new_name))
            tool['name'] = new_name
            # Also update platform field if it exists
            if 'platform' in tool:
                tool['platform'] = 'microsoft_' + tool['platform'].replace('microsoft_', '')
    
    # Save if changes were made
    if changes:
        with open(schema_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Fixed: {schema_file.name}")
        for old, new in changes:
            print(f"  {old} → {new}")
        return len(changes)
    
    return 0

def main():
    print("="*70)
    print("RENAMING MICROSOFT TOOLS TO USE CONSISTENT 'microsoft_' PREFIX")
    print("="*70)
    
    # Microsoft schema files
    ms_schema_files = [
        'microsoft_outlook_tools.json',
        'microsoft_word_tools.json',
        'microsoft_excel_tools.json',
        'microsoft_teams_tools.json',
        'microsoft_onedrive_tools.json',
        'microsoft_calendar_tools.json',
        'microsoft_todo_tools.json',
        'microsoft_forms_tools.json',
        'microsoft_sharepoint_tools.json',
        'microsoft_onenote_tools.json',
    ]
    
    total_changes = 0
    for schema_filename in ms_schema_files:
        schema_file = schemas_dir / schema_filename
        if schema_file.exists():
            changes = rename_tool_in_schema(schema_file)
            total_changes += changes
        else:
            print(f"✗ NOT FOUND: {schema_filename}")
    
    print("\n" + "="*70)
    print(f"✓ Total tool names renamed: {total_changes}")
    print("="*70)
    print("\nNext steps:")
    print("1. Restart the AI agent to load new schemas")
    print("2. Verify tools are discoverable with new names")
    print("3. Update agent prompt if needed to inform Claude about new names")

if __name__ == '__main__':
    main()
