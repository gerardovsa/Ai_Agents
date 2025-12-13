"""
Test to verify semantic search embeddings are pre-computed on server startup.

This simulates the FIRST message sent to the agent and measures the time
taken by get_semantic_search(). If embeddings were pre-computed, this should
be INSTANT (<0.1s). If not, it will take ~27 seconds.
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
print("TESTING FIRST MESSAGE SEMANTIC SEARCH SPEED")
print("=" * 80)
print("This simulates what happens when the FIRST user message arrives.")
print("If embeddings were pre-computed on startup, this should be INSTANT.\n")

# Simulate agent route behavior
print("[1] Loading registry (simulating agent route)...")
from tools.registry_v3 import RegistryV3
registry = RegistryV3()
print(f"    [OK] Registry loaded with {len(registry.tools)} tools\n")

# Measure time to get semantic search (should hit cache)
print("[2] Calling get_semantic_search() (FIRST CALL from user message)...")
start_time = time.time()

from AI_infrastructure.routes.agent_routes_v4 import get_semantic_search
semantic_search = get_semantic_search(registry)

get_time = time.time() - start_time

print(f"    [OK] get_semantic_search() completed in {get_time:.4f}s\n")

# Analyze results
print("=" * 80)
print("RESULT ANALYSIS")
print("=" * 80)

if get_time < 1.0:
    print("[SUCCESS] INSTANT! (<1s)")
    print("Embeddings were PRE-COMPUTED on server startup.")
    print("First user message will have ZERO delay!")
elif get_time > 20.0:
    print("[FAILURE] SLOW! (>20s)")
    print("Embeddings are being computed NOW (not pre-computed).")
    print("This means the startup initialization did NOT work.")
else:
    print("[PARTIAL] MEDIUM SPEED (1-20s)")
    print("Embeddings may still be computing from startup thread.")
    print("Try running this test again in a few seconds.")

print("=" * 80)
print(f"Total time: {get_time:.4f}s")
print("=" * 80)

# Verify functionality
if semantic_search and semantic_search.available:
    print(f"\n[OK] Semantic search functional with {len(semantic_search.tool_embeddings)} embeddings")
else:
    print("\n[WARNING] Semantic search not available")
