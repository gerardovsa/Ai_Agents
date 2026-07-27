"""
ORIGINAL LOCATION: AI_infrastructure/flask_app.py, lines 538-592
NAME: initialize_pgvector_bge_model_async
DATE REMOVED: 2026-07-27
PURPOSE: Background-thread prewarm that loads the 440 MB BGE embedding model used by pgvector document storage. ORTHOGONAL to lazy-tool-load — pgvector is a separate subsystem. Removed here for consistency.

RESTORE: Paste back into flask_app.py. Re-add the call site (formerly at line 5155) wrapped in the same try/except. The pgvector flow needs the preload or pays 30-60s on first upload.

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
# 🚀 BACKGROUND PGVECTOR BGE MODEL PRELOAD (Non-Blocking)
# ============================================================================
# The BAAI/bge-base-en-v1.5 embedding model (~440 MB on disk, 768-dim) is
# downloaded on first call to pgvector_upload_document() / pgvector_query_vectors()
# if it isn't already on /data.  On a fresh deploy with an empty persistent
# disk that first call takes 30-60 s and can hit Render's request timeout,
# surfacing as a 502 to the user (same pattern as the all-MiniLM-L6-v2
# preload via initialize_semantic_search_async above, but for the
# pgvector provider's embedding model).
#
# This preload runs in a daemon thread at startup so the first user upload
# is instant.  Failures here are non-fatal: the model will still load on
# first use, just with the original 30-60 s wait.
#
# Target cache dir matches pgvector_tools.py: /data/vdb_models on Render,
# ~/.cache/vdb_models on local dev.  Subsequent deploys reuse the cached
# snapshot — only the FIRST deploy on a fresh disk pays the download cost.
_pgvector_bge_initialization_complete = False
_pgvector_bge_initialization_error = None

def initialize_pgvector_bge_model_async():
    """Preload the pgvector BGE embedding model in a background thread."""
    global _pgvector_bge_initialization_complete, _pgvector_bge_initialization_error

    try:
        print("\n" + "=" * 80)
        print("[BACKGROUND] PRELOADING PGVECTOR BGE MODEL (BAAI/bge-base-en-v1.5, 768-dim)")
        print("=" * 80)

        from tools.implementations.pgvector import pgvector_tools

        # force_local=True bypasses the org-vault credential lookup so a
        # missing/invalid Voyage or OpenAI key can never cause this preload
        # to 500.  Trivial 1-char input → embedding call is essentially
        # instant; the cost is the one-time model load (~30-60 s on a fresh
        # disk, <1 s on a warm cache).
        vec = pgvector_tools._generate_embedding(".", user_id=1, force_local=True)
        assert len(vec) == 768, f"Expected 768-dim vector from BGE, got {len(vec)}"

        print(f"[BACKGROUND] [OK] BGE model ready — {len(vec)}-dim embeddings available")
        print("=" * 80)
        print("[BACKGROUND] ✅ PGVECTOR BGE MODEL READY — first upload will be instant")
        print("=" * 80 + "\n")

        _pgvector_bge_initialization_complete = True

    except Exception as e:
        print(f"[BACKGROUND] [ERROR] Failed to preload pgvector BGE model: {e}")
        import traceback
        print(traceback.format_exc())
        print("=" * 80 + "\n")
        _pgvector_bge_initialization_error = str(e)
        # Non-fatal: the model will load on first use even if preload fails
        # (the user just pays the 30-60 s download cost on first upload).

# --- ORIGINAL CODE ENDS -------------------------------------------------
