"""
ORIGINAL LOCATION: AI_infrastructure/flask_app.py, lines 355-479
NAME: initialize_semantic_search_async
DATE REMOVED: 2026-07-27
PURPOSE: Background-thread prewarm that loads MiniLM + tool embeddings from Supabase.

RESTORE: Paste back into flask_app.py between line 354 and the next function. Restore the globals (line 358-359). Re-add the call site at formerly-line 5129 and the marker-check at line 5094-5129. Restore get_semantic_search() from agent_routes_v4.py__semantic_search_cache.py.

CONTEXT — WHY REMOVED:
Lazy-load refactor: the AI no longer receives proactive semantic tool
suggestions at startup. It sees only the 8 meta-tools and discovers
the remaining 829 tools on demand via search_tools / get_tool_schema /
execute_tool. The background prewarm that loaded MiniLM embeddings was
the silent OOM/SIGTERM trigger on Render (the prewarm held the gevent
worker for 1-3s on first chat while gunicorn's 120s timeout ticked).

This bundle is the rollback recipe. See archive/deprecated/2026-07-27-
lazy-tool-load/ROLLBACK.md for the exact git + cp commands.
"""

# --- ORIGINAL CODE BEGINS -----------------------------------------------

# ============================================================================
# 🚀 BACKGROUND SEMANTIC SEARCH INITIALIZATION (Non-Blocking)
# ============================================================================
_semantic_search_initialization_complete = False
_semantic_search_initialization_error = None

def initialize_semantic_search_async():
    """
    Initialize persistent semantic search in background thread.
    
    This runs AFTER server starts to prevent health check timeouts.
    Uses Supabase persistence - loads instantly if cache exists, regenerates if tools changed.
    """
    global _semantic_search_initialization_complete, _semantic_search_initialization_error
    
    try:
        print("\n" + "=" * 80)
        print("[BACKGROUND] INITIALIZING PERSISTENT SEMANTIC SEARCH (Supabase-backed)")
        print("=" * 80)
        
        # Import registry and semantic search initializer
        from tools.registry_v3 import get_registry
        from AI_infrastructure.routes.agent_routes_v4 import get_semantic_search
        
        # Get singleton registry (NOT a new instance)
        print("[BACKGROUND] Loading tool registry...")
        registry = get_registry()
        print(f"[BACKGROUND] [OK] Registry loaded with {len(registry.tools)} tools")

        # ✅ FIX (June 11, 2026): Disk-backed registry cache on /data
        # Previously: every gunicorn worker recycle re-walked tools/schemas/*.json
        # + every UI/modules_external/*/tools/*.json (3-5 s on cold start).
        # Now: warm starts hit /data/tool_registry_cache/ via a version-hash check
        # (~50 ms). Cold starts (real code change to a schema) detect the hash
        # mismatch and rebuild transparently. Pickling callables is intentionally
        # avoided — implementations are re-imported from disk (safe + fast).
        try:
            from AI_infrastructure.shared.tool_registry_disk_cache import (
                compute_version_hash,
                should_use_disk_cache,
                load_schemas_from_disk,
                save_schemas_to_disk,
            )
            # Compute the hash of what was just loaded by get_registry() (it
            # already populated registry.tools from a Redis cache or fresh read).
            current_hash = compute_version_hash(registry.tools)
            if should_use_disk_cache(current_hash):
                print(f"[BACKGROUND] [DISK_CACHE] Hash {current_hash[:8]} matches /data cache — loading schemas from disk")
                if load_schemas_from_disk(registry):
                    # Implementations must always be re-imported (they are
                    # Python callables, not JSON-serializable, and not in cache).
                    print("[BACKGROUND] [DISK_CACHE] Re-importing implementations + module plugins (fast path)")
                    registry._load_implementations()
                    registry._load_module_plugins()
                    print(f"[BACKGROUND] [OK] Disk-cache fast path: {len(registry.tools)} tools, {len(registry.implementations)} implementations")
                else:
                    # Cache load failed despite hash match — fall back to full rebuild
                    print("[BACKGROUND] [DISK_CACHE] Cache read failed, falling back to full rebuild")
                    registry._load_schemas()
                    registry._load_implementations()
                    registry._load_module_plugins()
                    save_schemas_to_disk(registry)
            else:
                print(f"[BACKGROUND] [DISK_CACHE] Cache miss or hash mismatch — full rebuild")
                registry._load_schemas()
                registry._load_implementations()
                registry._load_module_plugins()
                save_schemas_to_disk(registry)
                print(f"[BACKGROUND] [OK] Reloaded fresh tools: {len(registry.tools)} total")
        except ImportError as e:
            # Disk cache helper not available — fall back to the old Redis path
            print(f"[BACKGROUND] [DISK_CACHE] Helper not available ({e}), using legacy path")
            if registry.redis_manager and registry.redis_manager.connected:
                print("[BACKGROUND] Invalidating stale Redis cache to force fresh tool loading...")
                cache_cleared = registry.invalidate_cache()
                if cache_cleared:
                    print("[BACKGROUND] [OK] Redis cache invalidated - next load will be fresh")
                    registry._load_schemas()
                    registry._load_implementations()
                    registry._load_module_plugins()
                    registry._save_to_cache()
                    print(f"[BACKGROUND] [OK] Reloaded fresh tools: {len(registry.tools)} total")
                else:
                    print("[BACKGROUND] [INFO] Redis cache not available - using fresh load")
        except Exception as e:
            # Defensive: any failure in the disk-cache path must not crash startup
            print(f"[BACKGROUND] [DISK_CACHE] Error: {e}, falling back to fresh load")
            import traceback
            traceback.print_exc()
            registry._load_schemas()
            registry._load_implementations()
            registry._load_module_plugins()
        
        # ✅ DEPLOY-TIME PREWARM (July 24, 2026):
        # Tag every log line with [DEPLOY_PREWARM] so the user can grep
        # `grep -c "DEPLOY_PREWARM" render.log` and confirm the prewarm
        # actually ran as part of the deploy (not lazily on first chat).
        # The previous tag was [BACKGROUND] — easy to miss.
        print("=" * 80)
        print("[DEPLOY_PREWARM] STEP 1/3 — Loading tool registry from disk cache (or fresh rebuild)")
        print("=" * 80)
        semantic_search = get_semantic_search(registry)

        if semantic_search and semantic_search.available:
            source = "Supabase" if semantic_search.db_available else "Generated (Database unavailable)"
            print(f"[DEPLOY_PREWARM] STEP 2/3 — Loaded {len(semantic_search.tool_embeddings)} tool embeddings from {source}")
            print(f"[DEPLOY_PREWARM] STEP 2/3 — Version hash: {semantic_search.version_hash[:16]}...")
            print("=" * 80)
            print(f"[DEPLOY_PREWARM] STEP 3/3 — ✅ DONE. Chat endpoint will be unblocked.")
            print(f"[DEPLOY_PREWARM] STEP 3/3 — Total tools indexed: {len(semantic_search.tool_embeddings)}")
            print("=" * 80 + "\n")
        else:
            print(f"[DEPLOY_PREWARM] STEP 2/3 — ⚠️  Semantic search NOT available (sentence-transformers not installed or HF download failed)")
            print(f"[DEPLOY_PREWARM] STEP 3/3 — ⚠️  Chat endpoint will still respond but tool-selection will fall back to keyword matching")
            print("=" * 80 + "\n")

        _semantic_search_initialization_complete = True
            
    except Exception as e:
        print(f"[DEPLOY_PREWARM] ❌ FAILED: {e}")
        import traceback
        print(traceback.format_exc())
        print("=" * 80 + "\n")
        _semantic_search_initialization_error = str(e)


# --- ORIGINAL CODE ENDS -------------------------------------------------
