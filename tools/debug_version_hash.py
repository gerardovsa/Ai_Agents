"""
FILE: tools/debug_version_hash.py
PURPOSE: Debug why tool version hash keeps changing

This script compares the current tool registry with the cached version
to identify which tools are causing the version hash to change.

USAGE:
    python tools/debug_version_hash.py

AUTHOR: System
DATE: 2026-01-03
"""

import sys
import os
from pathlib import Path
import json
import hashlib

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def calculate_tool_hash(tool_name, tool):
    """Calculate hash for a single tool"""
    tool_data = json.dumps({
        'name': tool_name,
        'description': tool.get('description', ''),
        'platform': tool.get('platform', ''),
        'short_description': tool.get('short_description', '')
    }, sort_keys=True)
    return hashlib.sha256(tool_data.encode()).hexdigest()[:8]


def main():
    """Debug version hash changes"""
    print("\n" + "=" * 80)
    print("🔍 DEBUG TOOL VERSION HASH")
    print("=" * 80)
    
    try:
        # Load current registry
        print("\n[1/4] Loading current tool registry...")
        from tools.registry_v3 import get_registry
        registry = get_registry()
        print(f"✅ Registry loaded: {len(registry.tools)} tools")
        
        # Calculate current version hash
        print("\n[2/4] Calculating current version hash...")
        from tools.persistent_semantic_search import PersistentSemanticToolSearch
        search_temp = PersistentSemanticToolSearch.__new__(PersistentSemanticToolSearch)
        search_temp.registry = registry
        current_hash = search_temp._calculate_version_hash()
        print(f"✅ Current version: {current_hash[:16]}...")
        
        # Get cached version
        print("\n[3/4] Loading cached version from Supabase...")
        from AI_infrastructure.shared.database_utils import execute_query
        cache_info = execute_query(
            """
            SELECT version_hash, total_tools, created_at
            FROM ai_infrastructure.tool_embedding_cache
            WHERE cache_key = 'semantic_tool_search'
            """,
            fetch_mode='one'
        )
        
        if not cache_info:
            print("❌ No cached version found in database")
            print("\n💡 TIP: Run force_regenerate_embeddings.py to create initial cache")
            return
        
        cached_hash = cache_info['version_hash']
        print(f"✅ Cached version: {cached_hash[:16]}...")
        print(f"   Created: {cache_info['created_at']}")
        print(f"   Tools: {cache_info['total_tools']}")
        
        # Compare
        print("\n[4/4] Comparing versions...")
        if current_hash == cached_hash:
            print("✅ VERSIONS MATCH! Cache should be loading from database.")
            print("\n💡 If regenerating every time, check Flask logs for other errors.")
        else:
            print("❌ VERSIONS DIFFER! This is why cache is regenerating.")
            print(f"\n   Current:  {current_hash}")
            print(f"   Cached:   {cached_hash}")
            
            # Try to identify which tools changed
            print("\n🔍 Analyzing tool changes...")
            print("   Calculating individual tool hashes (this may take a moment)...")
            
            current_tools = set(registry.tools.keys())
            
            # Get cached tools from database
            cached_tools_data = execute_query(
                """
                SELECT tool_name
                FROM ai_infrastructure.tool_embeddings
                WHERE version_hash = %s
                """,
                (cached_hash,),
                fetch_mode='all'
            )
            
            if cached_tools_data:
                cached_tools = set(row['tool_name'] for row in cached_tools_data)
                
                # Find differences
                new_tools = current_tools - cached_tools
                removed_tools = cached_tools - current_tools
                common_tools = current_tools & cached_tools
                
                print(f"\n📊 Tool Inventory:")
                print(f"   Current tools:  {len(current_tools)}")
                print(f"   Cached tools:   {len(cached_tools)}")
                print(f"   Common tools:   {len(common_tools)}")
                print(f"   New tools:      {len(new_tools)}")
                print(f"   Removed tools:  {len(removed_tools)}")
                
                if new_tools:
                    print(f"\n➕ NEW TOOLS ({len(new_tools)}):")
                    for tool in sorted(list(new_tools)[:20]):  # Show first 20
                        print(f"      + {tool}")
                    if len(new_tools) > 20:
                        print(f"      ... and {len(new_tools) - 20} more")
                
                if removed_tools:
                    print(f"\n➖ REMOVED TOOLS ({len(removed_tools)}):")
                    for tool in sorted(list(removed_tools)[:20]):  # Show first 20
                        print(f"      - {tool}")
                    if len(removed_tools) > 20:
                        print(f"      ... and {len(removed_tools) - 20} more")
                
                # Sample tool definitions to see if metadata changed
                if not new_tools and not removed_tools and len(common_tools) > 0:
                    print("\n🔍 No tools added/removed, but version still differs.")
                    print("   This means tool definitions (description/platform) changed.")
                    print("\n   Sampling 5 tools to show definition format:")
                    for tool_name in sorted(list(common_tools)[:5]):
                        tool = registry.tools[tool_name]
                        print(f"\n   Tool: {tool_name}")
                        print(f"      Description: {tool.get('description', '')[:100]}...")
                        print(f"      Platform: {tool.get('platform', '')}")
                        print(f"      Short desc: {tool.get('short_description', '')[:80]}...")
            else:
                print("   ⚠️ No cached tools found in database")
        
        print("\n" + "=" * 80)
        print("RECOMMENDATIONS:")
        print("=" * 80)
        
        if current_hash != cached_hash:
            print("1. Run: python tools/force_regenerate_embeddings.py")
            print("2. Restart Flask server")
            print("3. Cache will now load instantly from Supabase")
        else:
            print("Cache is up-to-date. Check Flask logs for other issues.")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
