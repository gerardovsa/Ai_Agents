"""
ORIGINAL LOCATION: AI_infrastructure/flask_app.py, lines 5154-5157
NAME: start_pgvector_bge_initialization() call site
DATE REMOVED: 2026-07-27
PURPOSE: Boot-time call to start_pgvector_bge_initialization() (with try/except).

RESTORE: Paste back into flask_app.py at the original location.

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

    try:
        start_pgvector_bge_initialization()
    except Exception as _bge_err:
        print(f"[STARTUP] ⚠️  Failed to start pgvector BGE preload (non-fatal): {_bge_err}")

# --- ORIGINAL CODE ENDS -------------------------------------------------
