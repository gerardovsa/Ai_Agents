"""
FILE: tools/force_regenerate_embeddings.py
PURPOSE: Force regenerate tool embeddings and store in Supabase

This script manually triggers a full regeneration of all tool embeddings
and stores them in Supabase. Use this when:
- Tools have been added/modified
- You want to refresh the cache
- Cache is corrupted or outdated

USAGE:
    python tools/force_regenerate_embeddings.py

AUTHOR: System
DATE: 2026-01-03
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    """Force regenerate embeddings"""
    print("\n" + "=" * 80)
    print("🔄 FORCE REGENERATE TOOL EMBEDDINGS")
    print("=" * 80)
    
    try:
        # Import dependencies
        print("\n[1/4] Loading tool registry...")
        from tools.registry_v3 import get_registry
        registry = get_registry()
        print(f"✅ Registry loaded: {len(registry.tools)} tools")
        
        # Calculate current version hash
        print("\n[2/4] Calculating version hash...")
        from tools.persistent_semantic_search import PersistentSemanticToolSearch
        search_temp = PersistentSemanticToolSearch.__new__(PersistentSemanticToolSearch)
        search_temp.registry = registry
        current_hash = search_temp._calculate_version_hash()
        print(f"✅ Current version: {current_hash[:16]}...")
        
        # Check existing cache
        print("\n[3/4] Checking existing cache...")
        from AI_infrastructure.shared.database_utils import execute_query
        cache_info = execute_query(
            """
            SELECT version_hash, total_tools, created_at
            FROM ai_infrastructure.tool_embedding_cache
            WHERE cache_key = 'semantic_tool_search'
            """,
            fetch_mode='one'
        )
        
        if cache_info:
            print(f"   Existing cache: {cache_info['version_hash'][:16]}... ({cache_info['total_tools']} tools)")
            print(f"   Created: {cache_info['created_at']}")
            if cache_info['version_hash'] == current_hash:
                print("   ⚠️ WARNING: Cache is already up-to-date!")
                response = input("\n   Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("\n❌ Cancelled by user")
                    return
        else:
            print("   No existing cache found")
        
        # Force regenerate
        print("\n[4/4] Generating embeddings (this takes ~30-60 seconds)...")
        print("=" * 80)
        search = PersistentSemanticToolSearch(registry, force_regenerate=True)
        print("=" * 80)
        
        if not search.available:
            print("\n❌ FAILED: Semantic search not available (sentence-transformers not installed)")
            return
        
        if not search.db_available:
            print("\n❌ FAILED: Database storage failed")
            return
        
        # Verify storage
        print(f"\n✅ SUCCESS!")
        print(f"   Generated: {len(search.tool_embeddings)} embeddings")
        print(f"   Version: {search.version_hash[:16]}...")
        print(f"   Database: {'Connected' if search.db_available else 'Failed'}")
        
        # Show storage info
        cache_info_new = execute_query(
            """
            SELECT version_hash, total_tools, created_at, updated_at
            FROM ai_infrastructure.tool_embedding_cache
            WHERE cache_key = 'semantic_tool_search'
            """,
            fetch_mode='one'
        )
        
        if cache_info_new:
            print(f"\n📊 Cache Info:")
            print(f"   Version: {cache_info_new['version_hash'][:16]}...")
            print(f"   Tools: {cache_info_new['total_tools']}")
            print(f"   Created: {cache_info_new['created_at']}")
            print(f"   Updated: {cache_info_new['updated_at']}")
        
        print("\n" + "=" * 80)
        print("🎉 REGENERATION COMPLETE - Restart Flask server to use new cache")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
