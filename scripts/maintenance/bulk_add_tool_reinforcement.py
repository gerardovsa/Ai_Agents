"""
Bulk Add Tool Reinforcement Rules to All Tool Schemas

This script systematically updates all 594 tool schemas with inline execution rules
to prevent the AI from using conversation history or creating fake links.

Usage:
    python bulk_add_tool_reinforcement.py [--dry-run] [--platform PLATFORM]
    
Examples:
    python bulk_add_tool_reinforcement.py --dry-run  # Preview changes
    python bulk_add_tool_reinforcement.py --platform google_workspace  # Update only Google tools
    python bulk_add_tool_reinforcement.py  # Update all tools

Author: AI Agent Infrastructure Team
Date: November 2025
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import argparse
import sys

# Add parent directory to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# Tool classification patterns
CREATE_PATTERNS = ['create', 'add', 'insert', 'upload', 'send', 'post', 'publish']
READ_PATTERNS = ['read', 'get', 'list', 'search', 'find', 'fetch', 'retrieve', 'view']
UPDATE_PATTERNS = ['update', 'edit', 'modify', 'change', 'set', 'patch']
DELETE_PATTERNS = ['delete', 'remove', 'clear', 'destroy']

# Reinforcement templates
CREATE_TEMPLATE = """🚨 CRITICAL EXECUTION RULES:
(1) ALWAYS execute THIS tool NOW - NEVER reference 'I created earlier' or use conversation history
(2) MUST return format: **[Name]** | ID: `[id]` | URL: [full_url] | Link: [title](url)
(3) Use EXACT values from tool response - NEVER make up fake URLs/IDs
(4) If tool fails, say 'Failed to create' - NEVER pretend it succeeded

Example response:
Created: **New Document**
- ID: `abc123`
- URL: https://example.com/doc/abc123
- Link: [New Document](https://example.com/doc/abc123)

"""

READ_TEMPLATE = """🚨 CRITICAL EXECUTION RULES:
(1) Execute THIS tool NOW - NEVER use cached/remembered data from conversation history
(2) MUST cite resource: 'Read X from **[Resource Name]** (ID: `[id]` | URL: [url])'
(3) Use EXACT [id] provided - NEVER substitute with different ID
(4) If tool fails (404/403), say 'Failed to read [resource] ID: [id]' and explain error
(5) NEVER make up data if read fails - acknowledge the failure clearly

Example response:
Read 45 rows from **Sales Spreadsheet**
- ID: `xyz789`
- URL: https://example.com/sheet/xyz789
- Data: [actual data read]

"""

UPDATE_TEMPLATE = """🚨 CRITICAL EXECUTION RULES:
(1) Execute THIS tool NOW - NEVER reference previous edits from conversation history
(2) MUST cite what was updated: 'Updated **[Resource Name]** (ID: `[id]`)'
(3) Use EXACT [id] provided - NEVER make up IDs
(4) If tool fails, say 'Failed to update' and explain why
(5) Show before/after if applicable

Example response:
Updated: **Document Title**
- ID: `abc123`
- URL: https://example.com/doc/abc123
- Changed: [what was changed]

"""

DELETE_TEMPLATE = """🚨 CRITICAL EXECUTION RULES:
(1) Execute THIS tool NOW - NEVER pretend to delete from memory
(2) MUST cite what was deleted: 'Deleted **[Resource Name]** (ID: `[id]`)'
(3) CONFIRM deletion happened - don't assume success
(4) If tool fails, say 'Failed to delete' and explain why

Example response:
✅ Deleted: **Old File**
- ID: `abc123`
- URL: https://example.com/file/abc123 (no longer accessible)

"""


def classify_tool(tool_name: str) -> str:
    """Classify tool as create/read/update/delete based on name"""
    name_lower = tool_name.lower()
    
    if any(pattern in name_lower for pattern in CREATE_PATTERNS):
        return 'create'
    elif any(pattern in name_lower for pattern in UPDATE_PATTERNS):
        return 'update'
    elif any(pattern in name_lower for pattern in DELETE_PATTERNS):
        return 'delete'
    elif any(pattern in name_lower for pattern in READ_PATTERNS):
        return 'read'
    else:
        # Default to read for safety
        return 'read'


def get_reinforcement_template(tool_type: str) -> str:
    """Get the appropriate reinforcement template for tool type"""
    templates = {
        'create': CREATE_TEMPLATE,
        'read': READ_TEMPLATE,
        'update': UPDATE_TEMPLATE,
        'delete': DELETE_TEMPLATE
    }
    return templates.get(tool_type, READ_TEMPLATE)


def update_tool_description(tool: Dict[str, Any]) -> Dict[str, Any]:
    """Add reinforcement rules to tool description"""
    tool_name = tool.get('name', '')
    description = tool.get('description', '')
    
    # Skip if already has reinforcement rules
    if '🚨 CRITICAL EXECUTION RULES' in description:
        return tool
    
    # Classify tool type
    tool_type = classify_tool(tool_name)
    
    # Get appropriate template
    template = get_reinforcement_template(tool_type)
    
    # Prepend template to description
    tool['description'] = template + description
    
    return tool


def process_schema_file(schema_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Process a single schema file and update all tools"""
    print(f"\n📄 Processing: {schema_path.name}")
    
    try:
        # Read schema
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Track changes
        updates = {
            'file': schema_path.name,
            'platform': schema.get('platform', 'unknown'),
            'tools_updated': 0,
            'tools_skipped': 0,
            'tools': []
        }
        
        # Update each tool
        if 'tools' in schema:
            for tool in schema['tools']:
                tool_name = tool.get('name', 'unknown')
                
                # Check if already updated
                if '🚨 CRITICAL EXECUTION RULES' in tool.get('description', ''):
                    print(f"  ⏭️  Skipping {tool_name} (already updated)")
                    updates['tools_skipped'] += 1
                    continue
                
                # Classify and update
                tool_type = classify_tool(tool_name)
                print(f"  ✏️  Updating {tool_name} (type: {tool_type})")
                
                tool = update_tool_description(tool)
                updates['tools_updated'] += 1
                updates['tools'].append({
                    'name': tool_name,
                    'type': tool_type
                })
        
        # Write back (if not dry run)
        if not dry_run and updates['tools_updated'] > 0:
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            print(f"  ✅ Saved {updates['tools_updated']} updates to {schema_path.name}")
        elif dry_run:
            print(f"  🔍 DRY RUN: Would update {updates['tools_updated']} tools")
        
        return updates
        
    except Exception as e:
        print(f"  ❌ ERROR processing {schema_path.name}: {e}")
        return {
            'file': schema_path.name,
            'platform': 'error',
            'tools_updated': 0,
            'tools_skipped': 0,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Bulk add reinforcement rules to tool schemas'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--platform',
        type=str,
        help='Only process tools for specific platform (e.g., google_workspace)'
    )
    parser.add_argument(
        '--schema',
        type=str,
        help='Only process specific schema file (e.g., google_sheets_tools.json)'
    )
    
    args = parser.parse_args()
    
    # Find schema directory
    schemas_dir = project_root / 'tools' / 'schemas'
    
    if not schemas_dir.exists():
        print(f"❌ ERROR: Schema directory not found: {schemas_dir}")
        return 1
    
    print(f"🔍 Scanning: {schemas_dir}")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE UPDATE'}")
    
    # Get schema files
    if args.schema:
        schema_files = [schemas_dir / args.schema]
        if not schema_files[0].exists():
            print(f"❌ ERROR: Schema file not found: {args.schema}")
            return 1
    else:
        schema_files = list(schemas_dir.glob('*.json'))
    
    # Filter by platform if specified
    if args.platform:
        schema_files = [f for f in schema_files if args.platform in f.name]
        print(f"   Platform filter: {args.platform}")
    
    print(f"   Found {len(schema_files)} schema files\n")
    
    # Process each file
    all_results = []
    total_updated = 0
    total_skipped = 0
    
    for schema_file in sorted(schema_files):
        result = process_schema_file(schema_file, dry_run=args.dry_run)
        all_results.append(result)
        total_updated += result['tools_updated']
        total_skipped += result['tools_skipped']
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Files processed: {len(all_results)}")
    print(f"Tools updated: {total_updated}")
    print(f"Tools skipped: {total_skipped}")
    
    if args.dry_run:
        print("\n💡 This was a DRY RUN. Run without --dry-run to apply changes.")
    else:
        print("\n✅ All updates applied successfully!")
    
    # Show breakdown by platform
    print("\n📋 Breakdown by platform:")
    platform_stats = {}
    for result in all_results:
        platform = result['platform']
        if platform not in platform_stats:
            platform_stats[platform] = {'updated': 0, 'skipped': 0, 'files': 0}
        platform_stats[platform]['updated'] += result['tools_updated']
        platform_stats[platform]['skipped'] += result['tools_skipped']
        platform_stats[platform]['files'] += 1
    
    for platform, stats in sorted(platform_stats.items()):
        print(f"  {platform:20s}: {stats['updated']:3d} updated, {stats['skipped']:3d} skipped ({stats['files']} files)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
