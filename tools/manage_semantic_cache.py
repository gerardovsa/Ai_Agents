"""
FILE: tools/manage_semantic_cache.py
PURPOSE: Management script for persistent semantic search cache in Supabase

COMMANDS:
    python manage_semantic_cache.py status       # Check cache status
    python manage_semantic_cache.py invalidate   # Clear cache (force regenerate)
    python manage_semantic_cache.py regenerate   # Force regenerate and store
    python manage_semantic_cache.py stats        # Show detailed statistics

USAGE EXAMPLES:
    # Check if cache is valid
    python tools/manage_semantic_cache.py status
    
    # Force regenerate after adding new tools
    python tools/manage_semantic_cache.py regenerate
    
    # Clear cache without regenerating
    python tools/manage_semantic_cache.py invalidate

AUTHOR: System Integration Architect
DATE: 2026-01-02
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.registry_v3 import get_registry
from tools.persistent_semantic_search import PersistentSemanticToolSearch
from AI_infrastructure.shared.database_utils import execute_query


def check_status():
    """Check cache status in Supabase"""
    print("\n" + "=" * 80)
    print("SEMANTIC SEARCH CACHE STATUS")
    print("=" * 80)
    
    try:
        # Get registry to calculate current version hash
        print("\n[1/3] Loading tool registry...")
        registry = get_registry()
        print(f"✅ Registry loaded: {len(registry.tools)} tools")
        
        # Calculate current version hash
        print("\n[2/3] Calculating current version hash...")
        search = PersistentSemanticToolSearch(registry)
        current_hash = search.version_hash
        print(f"✅ Current version: {current_hash[:16]}...")
        
        # Check database cache
        print("\n[3/3] Checking Supabase cache...")
        cache_info = execute_query(
            """
            SELECT version_hash, total_tools, created_at, updated_at
            FROM ai_infrastructure.tool_embedding_cache
            WHERE cache_key = 'semantic_tool_search'
            """,
            fetch_mode='one'
        )
        
        if not cache_info:
            print("❌ NO CACHE FOUND in Supabase")
            print("\n📝 Action Required: Run 'regenerate' command to create cache")
            return
        
        cached_hash = cache_info['version_hash']
        total_tools = cache_info['total_tools']
        created_at = cache_info['created_at']
        updated_at = cache_info['updated_at']
        
        # Check if cache is valid
        if cached_hash == current_hash:
            print(f"✅ CACHE VALID")
            print(f"\n   Version: {cached_hash[:16]}... (matches)")
            print(f"   Tools: {total_tools}")
            print(f"   Created: {created_at}")
            print(f"   Updated: {updated_at}")
            
            # Get embedding count
            count = execute_query(
                "SELECT COUNT(*) as count FROM ai_infrastructure.tool_embeddings WHERE version_hash = %s",
                (cached_hash,),
                fetch_mode='one'
            )
            print(f"   Embeddings in DB: {count['count']}")
            
        else:
            print(f"⚠️ CACHE OUTDATED")
            print(f"\n   Current: {current_hash[:16]}...")
            print(f"   Cached:  {cached_hash[:16]}...")
            print(f"   Tools: {total_tools} (cache) vs {len(registry.tools)} (current)")
            print(f"\n📝 Action Required: Run 'regenerate' command to update cache")
        
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def invalidate_cache():
    """Clear cache from Supabase"""
    print("\n" + "=" * 80)
    print("INVALIDATING SEMANTIC SEARCH CACHE")
    print("=" * 80)
    
    try:
        print("\n⚠️ This will delete all cached embeddings from Supabase")
        confirm = input("Continue? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Cancelled")
            return
        
        # Delete cache metadata
        execute_query("""
            DELETE FROM ai_infrastructure.tool_embedding_cache
            WHERE cache_key = 'semantic_tool_search'
        """)
        print("✅ Deleted cache metadata")
        
        # Delete embeddings
        count = execute_query(
            "SELECT COUNT(*) as count FROM ai_infrastructure.tool_embeddings",
            fetch_mode='one'
        )
        
        execute_query("DELETE FROM ai_infrastructure.tool_embeddings")
        print(f"✅ Deleted {count['count']} embeddings")
        
        print("\n" + "=" * 80)
        print("✅ CACHE INVALIDATED")
        print("=" * 80)
        print("\n📝 Next: Restart Flask server to regenerate cache")
        print("   Or run: python tools/manage_semantic_cache.py regenerate\n")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def regenerate_cache():
    """Force regenerate and store cache"""
    print("\n" + "=" * 80)
    print("REGENERATING SEMANTIC SEARCH CACHE")
    print("=" * 80)
    
    try:
        print("\n[1/3] Loading tool registry...")
        registry = get_registry()
        print(f"✅ Registry loaded: {len(registry.tools)} tools")
        
        print("\n[2/3] Generating embeddings (this takes ~30 seconds)...")
        search = PersistentSemanticToolSearch(registry, force_regenerate=True)
        
        if not search.available:
            print("❌ Semantic search not available (sentence-transformers not installed)")
            return
        
        print(f"✅ Generated {len(search.tool_embeddings)} embeddings")
        
        print("\n[3/3] Verifying storage...")
        if search.db_available:
            print("✅ Embeddings stored in Supabase")
            print(f"   Version: {search.version_hash[:16]}...")
        else:
            print("⚠️ Database storage failed, embeddings generated but not persisted")
        
        print("\n" + "=" * 80)
        print("✅ CACHE REGENERATION COMPLETE")
        print("=" * 80)
        print("\n📝 Next: Restart Flask server to use new cache\n")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def show_stats():
    """Show detailed statistics"""
    print("\n" + "=" * 80)
    print("SEMANTIC SEARCH DETAILED STATISTICS")
    print("=" * 80)
    
    try:
        # Registry stats
        print("\n📦 TOOL REGISTRY")
        registry = get_registry()
        print(f"   Total tools: {len(registry.tools)}")
        
        # Platform breakdown
        platforms = {}
        for tool_name, tool_data in registry.tools.items():
            platform = tool_data.get('platform', 'unknown')
            platforms[platform] = platforms.get(platform, 0) + 1
        
        print(f"   Platforms: {len(platforms)}")
        for platform, count in sorted(platforms.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"      {platform}: {count} tools")
        
        # Cache stats
        print("\n💾 SUPABASE CACHE")
        cache_info = execute_query(
            """
            SELECT version_hash, total_tools, created_at, updated_at
            FROM ai_infrastructure.tool_embedding_cache
            WHERE cache_key = 'semantic_tool_search'
            """,
            fetch_mode='one'
        )
        
        if cache_info:
            print(f"   Status: ACTIVE")
            print(f"   Version: {cache_info['version_hash'][:16]}...")
            print(f"   Tools cached: {cache_info['total_tools']}")
            print(f"   Created: {cache_info['created_at']}")
            print(f"   Updated: {cache_info['updated_at']}")
            
            # Embedding stats
            count = execute_query(
                "SELECT COUNT(*) as count FROM ai_infrastructure.tool_embeddings",
                fetch_mode='one'
            )
            print(f"   Embeddings in DB: {count['count']}")
            
            # Table size
            size = execute_query(
                """
                SELECT pg_size_pretty(pg_total_relation_size('ai_infrastructure.tool_embeddings')) as size
                """,
                fetch_mode='one'
            )
            print(f"   Database size: {size['size']}")
            
        else:
            print(f"   Status: NOT FOUND")
        
        print("\n" + "=" * 80 + "\n")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main CLI handler"""
    if len(sys.argv) < 2:
        print("\n❌ Missing command")
        print("\nUSAGE:")
        print("  python tools/manage_semantic_cache.py <command>")
        print("\nCOMMANDS:")
        print("  status      - Check cache status")
        print("  invalidate  - Clear cache (force regenerate)")
        print("  regenerate  - Force regenerate and store")
        print("  stats       - Show detailed statistics")
        print()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        check_status()
    elif command == 'invalidate':
        invalidate_cache()
    elif command == 'regenerate':
        regenerate_cache()
    elif command == 'stats':
        show_stats()
    else:
        print(f"\n❌ Unknown command: {command}")
        print("\nValid commands: status, invalidate, regenerate, stats\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
