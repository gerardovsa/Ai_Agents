"""
Remove Tool Reinforcement Rules from All Tool Schemas

This script removes the embedded "🚨 CRITICAL EXECUTION RULES" from all tool schemas
to reduce token count. The rules are still in the system prompt (tool_usage_system_prompt.md).

Usage:
    python remove_tool_reinforcement.py [--dry-run] [--platform PLATFORM]
    
Examples:
    python remove_tool_reinforcement.py --dry-run  # Preview changes
    python remove_tool_reinforcement.py --platform google  # Remove from Google tools only
    python remove_tool_reinforcement.py  # Remove from all tools

Author: AI Agent Infrastructure Team  
Date: November 2, 2025
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any
import argparse
import sys

# Add parent directory to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))


def remove_reinforcement_from_description(description: str) -> tuple[str, bool]:
    """
    Remove reinforcement rules from tool description
    
    Args:
        description: Tool description (may contain reinforcement rules)
    
    Returns:
        Tuple of (cleaned_description, was_modified)
    """
    # Pattern to match reinforcement rules
    # Matches from "🚨 CRITICAL EXECUTION RULES:" to the end of the example
    patterns = [
        r'🚨 CRITICAL EXECUTION RULES:.*?(?=\n\n[A-Z]|\n\n[a-z]|\Z)',  # Until next section
        r'⚠️ Execute NOW\..*?(?=\n\n[A-Z]|\n\n[a-z]|\Z)',  # Shorter format
    ]
    
    original = description
    
    for pattern in patterns:
        description = re.sub(pattern, '', description, flags=re.DOTALL)
    
    # Clean up extra whitespace
    description = re.sub(r'\n{3,}', '\n\n', description)
    description = description.strip()
    
    was_modified = (original != description)
    
    return description, was_modified


def process_schema_file(schema_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """Process a single schema file and remove reinforcement from all tools"""
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
            'tools_unchanged': 0,
            'tools': []
        }
        
        # Process each tool
        if 'tools' in schema:
            for tool in schema['tools']:
                tool_name = tool.get('name', 'unknown')
                description = tool.get('description', '')
                
                # Remove reinforcement
                cleaned_description, was_modified = remove_reinforcement_from_description(description)
                
                if was_modified:
                    print(f"  ✂️  Removing reinforcement from {tool_name}")
                    tool['description'] = cleaned_description
                    updates['tools_updated'] += 1
                    updates['tools'].append({
                        'name': tool_name,
                        'before_length': len(description),
                        'after_length': len(cleaned_description),
                        'tokens_saved': (len(description) - len(cleaned_description)) // 4  # Rough estimate
                    })
                else:
                    print(f"  ⏭️  Skipping {tool_name} (no reinforcement found)")
                    updates['tools_unchanged'] += 1
        
        # Write back (if not dry run)
        if not dry_run and updates['tools_updated'] > 0:
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)
            print(f"  ✅ Saved {updates['tools_updated']} updates to {schema_path.name}")
        elif dry_run and updates['tools_updated'] > 0:
            print(f"  🔍 DRY RUN: Would update {updates['tools_updated']} tools")
        
        return updates
        
    except Exception as e:
        print(f"  ❌ ERROR processing {schema_path.name}: {e}")
        return {
            'file': schema_path.name,
            'platform': 'error',
            'tools_updated': 0,
            'tools_unchanged': 0,
            'error': str(e)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Remove reinforcement rules from tool schemas'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--platform',
        type=str,
        help='Only process tools for specific platform (e.g., google)'
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
        schema_files = [f for f in schema_files if args.platform in f.name.lower()]
        print(f"   Platform filter: {args.platform}")
    
    print(f"   Found {len(schema_files)} schema files\n")
    
    # Process each file
    all_results = []
    total_updated = 0
    total_unchanged = 0
    total_tokens_saved = 0
    
    for schema_file in sorted(schema_files):
        result = process_schema_file(schema_file, dry_run=args.dry_run)
        all_results.append(result)
        total_updated += result['tools_updated']
        total_unchanged += result['tools_unchanged']
        
        # Calculate tokens saved
        for tool in result.get('tools', []):
            total_tokens_saved += tool.get('tokens_saved', 0)
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Files processed: {len(all_results)}")
    print(f"Tools updated: {total_updated}")
    print(f"Tools unchanged: {total_unchanged}")
    print(f"Estimated tokens saved: ~{total_tokens_saved:,} tokens")
    
    if args.dry_run:
        print("\n💡 This was a DRY RUN. Run without --dry-run to apply changes.")
    else:
        print("\n✅ All reinforcement rules removed successfully!")
        print("\n📝 NOTE: Rules are still enforced via system prompt:")
        print("   AI_infrastructure/prompts/tool_usage_system_prompt.md")
    
    # Show breakdown by platform
    print("\n📋 Breakdown by platform:")
    platform_stats = {}
    for result in all_results:
        platform = result['platform']
        if platform not in platform_stats:
            platform_stats[platform] = {'updated': 0, 'unchanged': 0, 'files': 0}
        platform_stats[platform]['updated'] += result['tools_updated']
        platform_stats[platform]['unchanged'] += result['tools_unchanged']
        platform_stats[platform]['files'] += 1
    
    for platform, stats in sorted(platform_stats.items()):
        print(f"  {platform:20s}: {stats['updated']:3d} cleaned, {stats['unchanged']:3d} unchanged ({stats['files']} files)")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
