"""
Test Query Library Bridge - Verify semantic search discovers queries
"""
import sys
sys.path.insert(0, 'c:/Users/gpoli/GIT/AI_agents')

from tools.registry_v3 import RegistryV3
from tools.intelligent_discovery import SemanticToolSearch

def test_query_discovery():
    print("="*80)
    print("QUERY LIBRARY BRIDGE TEST - Semantic Search Discovery")
    print("="*80)
    
    # Initialize registry (loads bridge automatically)
    print("\n1. Loading Registry V3...")
    registry = RegistryV3()
    
    # Check if query bridge loaded
    query_tools = [name for name in registry.tools.keys() if name.startswith('query_')]
    print(f"   ✓ Loaded {len(query_tools)} virtual query tools")
    
    # Initialize semantic search
    print("\n2. Initializing Semantic Search...")
    semantic = SemanticToolSearch(registry)
    
    if not semantic.available:
        print("   ✗ Semantic search not available (install sentence-transformers)")
        return
    
    print(f"   ✓ Semantic search ready with {len(semantic.tool_embeddings)} tool embeddings")
    
    # Test queries
    test_queries = [
        "sales trend",
        "customer reorder prediction", 
        "production bottleneck",
        "monthly revenue",
        "paper specifications",
        "finishing options",
        "capacity forecast"
    ]
    
    print("\n3. Testing Query Discovery:")
    print("-" * 80)
    
    for query in test_queries:
        print(f"\n📝 Query: '{query}'")
        results = semantic.search(query, top_k=3, similarity_threshold=0.3)
        
        if results:
            for i, result in enumerate(results, 1):
                is_virtual = result.get('is_virtual_tool', False)
                icon = "🔗" if is_virtual else "🔧"
                print(f"   {icon} [{i}] {result['tool_name']}")
                print(f"       Similarity: {result['similarity']:.3f}")
                print(f"       Platform: {result['platform']}")
                if is_virtual:
                    print(f"       Query ID: {result.get('query_id')}")
                    print(f"       Hint: {result.get('execution_hint')}")
                print(f"       Description: {result.get('short_description', '')[:100]}")
        else:
            print("   ✗ No results found")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    
    # Count virtual vs real tools
    virtual_count = sum(1 for r in semantic.tool_metadata.values() if r.get('is_virtual_tool'))
    real_count = len(semantic.tool_metadata) - virtual_count
    
    print(f"\n📊 Statistics:")
    print(f"   Total tools indexed: {len(semantic.tool_metadata)}")
    print(f"   Real tools: {real_count}")
    print(f"   Virtual query tools: {virtual_count}")
    print(f"   Bridge effectiveness: {virtual_count}/60 queries ({virtual_count/60*100:.0f}%)")

if __name__ == "__main__":
    test_query_discovery()
