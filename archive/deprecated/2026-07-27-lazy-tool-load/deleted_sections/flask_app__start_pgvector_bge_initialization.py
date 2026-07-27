"""
ORIGINAL LOCATION: AI_infrastructure/flask_app.py, lines 594-602
NAME: start_pgvector_bge_initialization
DATE REMOVED: 2026-07-27
PURPOSE: Spawns the background thread that calls initialize_pgvector_bge_model_async().

RESTORE: Paste back into flask_app.py right after initialize_pgvector_bge_model_async().

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

def start_pgvector_bge_initialization():
    """Start pgvector BGE model preload in background thread."""
    thread = threading.Thread(
        target=initialize_pgvector_bge_model_async,
        daemon=True,
        name="PgvectorBgePreload"
    )
    thread.start()
    print("[STARTUP] 🚀 pgvector BGE model preload started in background\n")

# --- ORIGINAL CODE ENDS -------------------------------------------------
