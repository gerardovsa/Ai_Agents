"""
ORIGINAL LOCATION: AI_infrastructure/flask_app.py, lines 514-535
NAME: PrewarmPending / PrewarmFailed / is_prewarm_complete / get_prewarm_error
DATE REMOVED: 2026-07-27
PURPOSE: Sentinel exception classes and gate helpers used by agent_routes_v4.py:get_semantic_search() to surface deploy-prewarm-still-running state as a 503 + Retry-After.

RESTORE: Paste back into flask_app.py in the original order. The two exception classes go first, then the two helpers. The chat endpoint needs them again if you re-enable the prewarm.

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

class PrewarmPending(Exception):
    """Raised by get_semantic_search() when the deploy-time prewarm hasn't finished yet."""
    def __init__(self, retry_after_seconds: int = 5):
        self.retry_after_seconds = retry_after_seconds
        super().__init__(f"Deploy prewarm still running; retry after {retry_after_seconds}s")


class PrewarmFailed(Exception):
    """Raised by get_semantic_search() when the deploy-time prewarm raised an exception."""
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Deploy prewarm failed: {reason}")


def is_prewarm_complete() -> bool:
    """Cheap read of the global prewarm flag without importing anything heavy."""
    return _semantic_search_initialization_complete


def get_prewarm_error() -> Optional[str]:
    """Returns the prewarm error string if the prewarm failed, else None."""
    return _semantic_search_initialization_error

# --- ORIGINAL CODE ENDS -------------------------------------------------
