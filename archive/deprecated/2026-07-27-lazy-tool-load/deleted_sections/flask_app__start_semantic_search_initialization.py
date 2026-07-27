"""
ORIGINAL LOCATION: AI_infrastructure/flask_app.py, lines 480-490
NAME: start_semantic_search_initialization
DATE REMOVED: 2026-07-27
PURPOSE: Spawns the background thread that calls initialize_semantic_search_async().

RESTORE: Paste back into flask_app.py right after initialize_semantic_search_async(). Re-add the call site (formerly at line 5129).

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

def start_semantic_search_initialization():
    """Start semantic search initialization in background thread"""
    thread = threading.Thread(
        target=initialize_semantic_search_async,
        daemon=True,
        name="SemanticSearchInit"
    )
    thread.start()
    print("[DEPLOY_PREWARM] 🚀 Started in background thread — server will accept requests immediately")
    print("[DEPLOY_PREWARM] 🚀 Chat endpoints will return 503 with Retry-After until this thread completes")
    print("[DEPLOY_PREWARM] 🚀 Follow progress by `grep \"DEPLOY_PREWARM\" render.log`\n")

# --- ORIGINAL CODE ENDS -------------------------------------------------
