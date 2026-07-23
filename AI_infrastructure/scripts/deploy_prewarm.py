"""
FILE: AI_infrastructure/scripts/deploy_prewarm.py

PURPOSE:
    Deploy-time tool-embedding prewarm. Runs SYNCHRONOUSLY from startup.sh
    BEFORE `exec gunicorn`, so the HuggingFace model + tool embeddings are
    ready before /health returns 200. The first user chat on a fresh deploy
    returns in <2s instead of hanging on a singleton lock for 30-60s.

WHY A SEPARATE SCRIPT (not just in flask_app.py):
    flask_app.py's background-thread prewarm runs AFTER /health returns 200.
    Render routes traffic to the worker as soon as /health is 200. So a
    first-chat request arriving during the 30-60s prewarm window blocks on
    the singleton lock — exactly the 1.4-minute hang that prompted this fix.

    By running the prewarm BEFORE `exec gunicorn`, Render never even starts
    polling /health until the work is done. Render's `healthCheckTimeout`
    (30s) only applies to gunicorn's own readiness after exec, NOT to the
    time spent in this script. So 60-90s first-deploy costs are absorbed
    before the deploy is even considered "in progress".

FAILURE MODE:
    If this script fails (Supabase unreachable, model download blocked),
    it exits 1 but startup.sh continues to start gunicorn. flask_app.py
    detects the missing marker file and falls back to the background-thread
    prewarm + 503+Retry-After gate on the chat endpoint. Deploys never
    crash-loop because of a prewarm failure.

OUTPUTS:
    /data/.prewarm_complete            JSON marker; flask_app.py reads this on import
    /data/vdb_models/...               HuggingFace model cache (persistent across deploys)
    ai_infrastructure.tool_embeddings  Supabase pgvector rows (cached for next deploy)
    ai_infrastructure.tool_embedding_cache  version_hash + total_tools metadata row

AUTHOR: System Integration
DATE: 2026-07-24
"""
import os
import sys
import time
import json

# ---------------------------------------------------------------------------
# sys.path bootstrap so `tools.persistent_semantic_search` resolves regardless
# of CWD or how the script is invoked.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))          # .../AI_infrastructure/scripts
_AI   = os.path.dirname(_HERE)                              # .../AI_infrastructure
_ROOT = os.path.dirname(_AI)                                # repo root (/app on Render)
for _p in (_ROOT, _AI):
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

T0 = time.perf_counter()


def _log(msg: str) -> None:
    """One-line, timestamped, atomic print so Render stdout stays greppable."""
    print(f"[DEPLOY_PREWARM_SCRIPT +{(time.perf_counter() - T0) * 1000:8.1f}ms] {msg}",
          flush=True)


MARKER_PATH = '/data/.prewarm_complete'


def _write_marker(tool_count: int, version_hash: str,
                  db_available: bool, source: str) -> bool:
    """Write a JSON marker so flask_app.py workers can skip the background prewarm."""
    try:
        os.makedirs(os.path.dirname(MARKER_PATH), exist_ok=True)
        payload = {
            'completed_at':  time.time(),
            'tools_indexed': tool_count,
            'version_hash':  version_hash,
            'db_available':  db_available,
            'source':        source,           # 'supabase_cache' | 'fresh_generation'
            'pid':           os.getpid(),
        }
        with open(MARKER_PATH, 'w', encoding='utf-8') as f:
            json.dump(payload, f, indent=2)
        _log(f"  Marker written: {MARKER_PATH}")
        return True
    except Exception as e:
        _log(f"  WARNING: failed to write marker file: {e}")
        return False


def main() -> int:
    _log("=" * 70)
    _log("DEPLOY-TIME TOOL EMBEDDING PREWARM")
    _log("Runs synchronously from startup.sh BEFORE gunicorn starts.")
    _log("=" * 70)

    # ----------------------------------------------------------------- #
    # STEP 1/4 — Load RegistryV3 so we know what tools to embed.        #
    # ----------------------------------------------------------------- #
    _log("STEP 1/4 - Loading RegistryV3 (registers all @tool_executor-decorated tools)")
    try:
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()
    except Exception as e:
        _log(f"FAILED: RegistryV3 load failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    _log(f"  OK: {len(registry.tools)} tools registered")

    # ----------------------------------------------------------------- #
    # STEP 2/4 — Initialize PersistentSemanticToolSearch.               #
    #                                                                     #
    # This is where the time goes:                                       #
    #   - First deploy:   downloads HuggingFace model (~440 MB), then    #
    #                    generates + stores embeddings in Supabase.      #
    #                    Wall-clock: 30-90s.                             #
    #   - Subsequent:     model already in /data/vdb_models/, embeddings #
    #                    already in Supabase. Loads in ~5-15s.           #
    # ----------------------------------------------------------------- #
    _log("STEP 2/4 - Initializing PersistentSemanticToolSearch")
    _log("          First deploy:    30-90s (HuggingFace model download + embed)")
    _log("          Subsequent:      5-15s (model + embeddings cached)")
    try:
        from tools.persistent_semantic_search import PersistentSemanticToolSearch
        search = PersistentSemanticToolSearch(registry)
    except Exception as e:
        _log(f"FAILED: PersistentSemanticToolSearch init failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if not search.available:
        _log("FAILED: search.available=False - model failed to load")
        return 1

    source = 'supabase_cache' if search.db_available else 'fresh_generation'
    _log(f"  OK: {len(search.tool_embeddings)} tool embeddings loaded")
    _log(f"  OK: Version hash: {(search.version_hash or 'NONE')[:16]}")
    _log(f"  OK: Source: {source}")

    # ----------------------------------------------------------------- #
    # STEP 3/4 — Write the marker file so flask_app.py can detect this.  #
    # ----------------------------------------------------------------- #
    _log("STEP 3/4 - Writing deploy-prewarm marker file")
    _write_marker(
        tool_count=len(search.tool_embeddings),
        version_hash=search.version_hash or '',
        db_available=search.db_available,
        source=source,
    )

    # ----------------------------------------------------------------- #
    # STEP 4/4 — Done.                                                   #
    # ----------------------------------------------------------------- #
    elapsed = time.perf_counter() - T0
    _log("STEP 4/4 - DEPLOY-TIME PREWARM COMPLETE")
    _log(f"          Total time: {elapsed:.1f}s")
    _log("          First user chat will return immediately (no singleton lock-wait).")
    _log("=" * 70)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        _log("Interrupted")
        sys.exit(130)
    except Exception as e:
        _log(f"FAILED: top-level prewarm failure: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
