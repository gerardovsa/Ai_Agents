"""
ORIGINAL LOCATION: AI_infrastructure/routes/agent_routes_v4.py, lines 71-138
NAME: _semantic_search_cache + _semantic_search_lock + get_semantic_search()
DATE REMOVED: 2026-07-27
PURPOSE: Module-level cache for the PersistentSemanticToolSearch singleton + lazy getter. The getter gates on is_prewarm_complete() so chat endpoints 503+Retry-After instead of hanging during the prewarm window.

RESTORE: Paste back into agent_routes_v4.py at the original location. Re-import is_prewarm_complete / get_prewarm_error from flask_app (or restore from flask_app__prewarm_classes.py). Re-add the call site that used to live at line 1321.

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

# ============================================================
# 🚀 GLOBAL SEMANTIC SEARCH CACHE (Initialized Once Per Server Start)
# ============================================================
_semantic_search_cache = None
_semantic_search_lock = None

def get_semantic_search(registry):
    """
    Get or create cached PersistentSemanticToolSearch instance.

    This ensures embeddings are loaded ONCE at server startup from Supabase,
    not regenerated on every message or new thread.

    ✅ NO TEMPORAL COUPLING WITH CHAT (July 24, 2026 — user request):
    The flask_app.py background thread `initialize_semantic_search_async`
    runs at gunicorn boot and populates `_semantic_search_cache`. Per user
    directive, the chat endpoint MUST NOT 503 because the semantic-search
    optimisation layer isn't ready. Tool embeddings are a *hint*, not a
    prerequisite — the AI receives the full tool schema regardless.

    If the prewarm is still running (or failed), this function returns
    `None`. The caller (`stream_agent_response`) treats `None` as
    "no suggestions block this round" and proceeds normally. The
    `PrewarmPending` / `PrewarmFailed` sentinels still exist in flask_app
    for diagnostic endpoints but are no longer raised on the chat path.

    Returns:
        PersistentSemanticToolSearch instance if prewarm has completed,
        OR `None` if prewarm hasn't finished yet / failed. Never raises.
    """
    global _semantic_search_cache, _semantic_search_lock

    # ✅ NO-COUPLE GATE: If the background prewarm hasn't finished yet,
    # return None so the chat proceeds without the suggestion block. The
    # prewarm thread still populates the cache the moment it completes —
    # the *next* chat request will pick it up. Import lazily to avoid a
    # circular-import at module-load time (flask_app imports this module).
    from flask_app import is_prewarm_complete, get_prewarm_error
    if not is_prewarm_complete():
        # Surface a one-line log on every call so production grep can
        # confirm the gate is being hit (and how often).
        err = get_prewarm_error()
        if err:
            print(f"[SEMANTIC CACHE] prewarm failed ({err[:80]}) — chat proceeding without suggestion block")
        else:
            print(f"[SEMANTIC CACHE] prewarm not complete — chat proceeding without suggestion block")
        return None

    # Thread-safe initialization
    if _semantic_search_lock is None:
        import threading
        _semantic_search_lock = threading.Lock()

    with _semantic_search_lock:
        if _semantic_search_cache is None:
            try:
                from tools.persistent_semantic_search import PersistentSemanticToolSearch
                cprint("[SEMANTIC CACHE] Initializing persistent semantic search (loads from Supabase)...", Colors.INFO)
                _semantic_search_cache = PersistentSemanticToolSearch(registry)
                cprint(f"[SEMANTIC CACHE] [OK] Loaded {len(_semantic_search_cache.tool_embeddings)} tool embeddings", Colors.SUCCESS)
                cprint(f"[SEMANTIC CACHE] Source: {'Supabase' if _semantic_search_cache.db_available else 'Generated'}", Colors.INFO)
            except Exception as e:
                cprint(f"[SEMANTIC CACHE] [ERROR] Failed to initialize: {e}", Colors.ERROR)
                import traceback
                traceback.print_exc()
                _semantic_search_cache = None

        return _semantic_search_cache

# --- ORIGINAL CODE ENDS -------------------------------------------------
