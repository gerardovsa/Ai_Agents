"""
ORIGINAL LOCATION: AI_infrastructure/flask_app.py, lines 5094-5129
NAME: /data/.prewarm_complete marker detection + start_semantic_search_initialization call
DATE REMOVED: 2026-07-27
PURPOSE: At gunicorn boot, checks whether startup.sh ran deploy_prewarm.py BEFORE exec gunicorn. If yes (marker present), skips the background-thread prewarm; if no, starts it.

RESTORE: Paste back into flask_app.py at the original location. The marker file path /data/.prewarm_complete is set on line 5104. The call to start_semantic_search_initialization() at line 5129 is part of this block.

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

    # `exec gunicorn`, a marker file /data/.prewarm_complete exists. In that
    # case the HuggingFace model is already in /data/vdb_models/ AND the tool
    # embeddings are already cached in Supabase — workers load them on first
    # chat in <2s. We SKIP the background thread (the user's clock is no
    # longer paying for the prewarm cost).
    #
    # If the marker is absent (local dev, deploy script failed), fall back
    # to the background-thread prewarm + the 503+Retry-After gate in
    # agent_routes_v4.py get_semantic_search(). Deploys never crash-loop
    # because of a prewarm failure.
    _PREWARM_MARKER_PATH = '/data/.prewarm_complete'

    try:
        _marker_present = os.path.isfile(_PREWARM_MARKER_PATH)
    except Exception as _marker_err:
        print(f"[DEPLOY_PREWARM] Marker detection error (non-fatal): {_marker_err}")
        _marker_present = False

    if _marker_present:
        # Trust the marker — the persistent_semantic_search singleton will
        # load instantly from /data/vdb_models/ + Supabase on first call.
        _semantic_search_initialization_complete = True
        _semantic_search_initialization_error = None
        print(f"[DEPLOY_PREWARM] ✓ Marker file detected: {_PREWARM_MARKER_PATH}")
        print("[DEPLOY_PREWARM]   Deploy-time prewarm already completed.")
        print("[DEPLOY_PREWARM]   Skipping background-thread prewarm; workers will")
        print("[DEPLOY_PREWARM]   load embeddings from cache on first chat (<2s).")
        print("[DEPLOY_PREWARM] ✓ Background prewarm thread SKIPPED.\n")
    else:
        # No marker (dev mode or deploy-time prewarm failed). Start the
        # background-thread prewarm; the chat endpoint will return 503 with
        # Retry-After until it completes.
        print("[STARTUP] No deploy-prewarm marker found — starting background-thread prewarm...")
        print("[STARTUP] Server will respond to health checks immediately while embeddings load.")
        print("[STARTUP] Chat endpoint will 503+Retry-After until prewarm completes.\n")
        start_semantic_search_initialization()

# --- ORIGINAL CODE ENDS -------------------------------------------------
