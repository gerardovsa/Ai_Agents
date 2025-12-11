"""
Test that semantic search embeddings are cached and not recomputed on every message.

Expected behavior:
- First call: "Initializing semantic search (ONE-TIME OPERATION)"
- Subsequent calls: Should use cached instance (no re-initialization message)
"""

import sys
from pathlib import Path
import time

# Add paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "tools"))
sys.path.insert(0, str(root_dir / "AI_infrastructure"))

from tools.registry_v3 import RegistryV3
from AI_infrastructure.routes.agent_routes_v4 import get_semantic_search

print("=" * 80)
print("🧪 SEMANTIC SEARCH CACHING TEST")
print("=" * 80)

# Initialize registry
print("\n[1] Creating registry...")
registry = RegistryV3()
print(f"    ✅ Registry loaded with {len(registry.tools)} tools")

# First call - should initialize embeddings
print("\n[2] First call to get_semantic_search()...")
start_time = time.time()
semantic_search_1 = get_semantic_search(registry)
elapsed_1 = time.time() - start_time
print(f"    ✅ First call completed in {elapsed_1:.2f}s")
print(f"    ✅ Embeddings computed: {len(semantic_search_1.tool_embeddings) if semantic_search_1 else 0}")

# Second call - should use cached instance (fast)
print("\n[3] Second call to get_semantic_search()...")
start_time = time.time()
semantic_search_2 = get_semantic_search(registry)
elapsed_2 = time.time() - start_time
print(f"    ✅ Second call completed in {elapsed_2:.2f}s")

# Third call - should use cached instance (fast)
print("\n[4] Third call to get_semantic_search()...")
start_time = time.time()
semantic_search_3 = get_semantic_search(registry)
elapsed_3 = time.time() - start_time
print(f"    ✅ Third call completed in {elapsed_3:.2f}s")

# Verify caching
print("\n" + "=" * 80)
print("📊 CACHING VERIFICATION")
print("=" * 80)

same_instance = (semantic_search_1 is semantic_search_2 is semantic_search_3)
print(f"✅ All calls returned SAME instance: {same_instance}")

speed_improvement = elapsed_1 / elapsed_2 if elapsed_2 > 0 else float('inf')
print(f"✅ Speed improvement (1st vs 2nd call): {speed_improvement:.1f}x faster")

if elapsed_2 < 0.1 and elapsed_3 < 0.1:
    print(f"✅ Subsequent calls are INSTANT (<0.1s): {elapsed_2:.4f}s, {elapsed_3:.4f}s")
    print("\n🎉 SUCCESS: Semantic search is properly cached!")
else:
    print(f"⚠️  WARNING: Subsequent calls are slow: {elapsed_2:.4f}s, {elapsed_3:.4f}s")
    print("   This might indicate re-computation is happening.")

# Test actual search functionality
if semantic_search_1 and semantic_search_1.available:
    print("\n" + "=" * 80)
    print("🔍 SEARCH FUNCTIONALITY TEST")
    print("=" * 80)
    
    test_queries = [
        "send email in Gmail",
        "create spreadsheet in Google Sheets",
        "schedule meeting in Outlook"
    ]
    
    for query in test_queries:
        results = semantic_search_1.search(query, top_k=3)
        print(f"\nQuery: '{query}'")
        if results:
            for i, tool in enumerate(results, 1):
                print(f"  {i}. {tool['tool_name']} [{tool['platform']}] - {tool['similarity']:.1%}")
        else:
            print("  No matches found")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)
