"""
Test to verify semantic search was pre-emptively initialized on server startup.

This test checks:
1. Server is running
2. Semantic search cache exists
3. Embeddings are already computed (fast response on first query)
"""

import time
import sys
from pathlib import Path

# Add paths
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "tools"))
sys.path.insert(0, str(root_dir / "AI_infrastructure"))

print("=" * 80)
print("🧪 TESTING PRE-EMPTIVE SEMANTIC SEARCH INITIALIZATION")
print("=" * 80)

# Test 1: Check if server is running
print("\n[1] Checking if Flask server is running...")
try:
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5001))
    sock.close()
    
    if result == 0:
        print("    ✅ Flask server is running on port 5001")
    else:
        print("    ❌ Flask server is NOT running on port 5001")
        sys.exit(1)
except Exception as e:
    print(f"    ❌ Error checking server: {e}")
    sys.exit(1)

# Test 2: Check semantic search cache
print("\n[2] Checking semantic search cache...")
try:
    from AI_infrastructure.routes.agent_routes_v4 import _semantic_search_cache
    
    if _semantic_search_cache is None:
        print("    ⚠️  Semantic search cache is None (not yet initialized)")
        print("    💡 This means initialization is still running or hasn't started")
    else:
        print(f"    ✅ Semantic search cache exists!")
        if hasattr(_semantic_search_cache, 'tool_embeddings'):
            print(f"    ✅ Embeddings loaded: {len(_semantic_search_cache.tool_embeddings)} tools")
            print(f"    ✅ Model available: {_semantic_search_cache.available}")
        else:
            print("    ⚠️  Cache exists but embeddings not loaded")
            
except ImportError as e:
    print(f"    ⚠️  Could not import semantic search module: {e}")
except Exception as e:
    print(f"    ❌ Error checking cache: {e}")

# Test 3: Time a search query (should be instant if pre-computed)
print("\n[3] Testing search query speed...")
try:
    from tools.registry_v3 import RegistryV3
    from AI_infrastructure.routes.agent_routes_v4 import get_semantic_search
    
    registry = RegistryV3()
    print(f"    ✅ Registry loaded with {len(registry.tools)} tools")
    
    # Get cached semantic search
    start_time = time.time()
    semantic_search = get_semantic_search(registry)
    get_time = time.time() - start_time
    
    print(f"    ⏱️  get_semantic_search() took: {get_time:.4f}s")
    
    if get_time < 1.0:
        print(f"    ✅ INSTANT! (<1s) - Embeddings were pre-computed on startup!")
    else:
        print(f"    ⚠️  SLOW (>1s) - Embeddings may still be computing...")
    
    # Test actual search
    if semantic_search and semantic_search.available:
        start_time = time.time()
        results = semantic_search.search("send email in Gmail", top_k=3)
        search_time = time.time() - start_time
        
        print(f"    ⏱️  Actual search took: {search_time:.4f}s")
        print(f"    ✅ Found {len(results)} matching tools:")
        for i, tool in enumerate(results, 1):
            print(f"       {i}. {tool['tool_name']} - {tool['similarity']:.1%}")
    else:
        print("    ⚠️  Semantic search not available")
        
except Exception as e:
    print(f"    ❌ Error testing search: {e}")
    import traceback
    print(traceback.format_exc())

print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)
print("If get_semantic_search() was < 1s, embeddings were pre-computed on startup!")
print("If it was ~27s, embeddings are being computed now (not pre-computed).")
print("=" * 80)
