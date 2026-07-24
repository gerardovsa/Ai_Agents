"""
FILE: AI_infrastructure/shared/auth_platform_resolver.py
PURPOSE: Resolve the effective auth platform for a user

WHEN TO USE
-----------
Call this any time the chat / system-prompt path needs the user's
authentication platform. It honours the user's explicit choice
("microsoft" / "google") and resolves the special value "auto" by
inspecting ai_infrastructure.oauth_tokens for the user's most-recently
updated active token.

This replaces a duplicated resolution that previously lived only in
routes/auth_routes.py:271-302 and was unreachable from the chat pipeline.
The system prompt and tool filtering at agent_routes_v4.py:1298 used to
read user_preferences.auth_platform literally, which meant "auto" was a
no-op and the AI received both Google and Microsoft tool schemas with no
guidance about which to prefer.

RESOLUTION CONTRACT
-------------------
resolve_auth_platform(user_id, stored_value) returns:

    'google'     — explicit Google lock OR (auto + only-google connected)
    'microsoft'  — explicit Microsoft lock OR (auto + only-microsoft connected)
    None         — auto-detect with no usable signal (no lock, AI gets
                   the "check connected platforms" hint and is free to
                   try either vendor)

The function never raises. DB errors are caught and logged; the
fallback is None (no lock) so the chat pipeline degrades to its
pre-existing soft-hint behaviour rather than 500-ing.

PER-REQUEST CACHE
-----------------
A single chat round-trip may call this twice (once for tool filtering,
once for the system prompt). The module-level _REQUEST_CACHE avoids a
second Supabase round-trip for the same (user_id, stored_value) pair.
The cache is per-process and unbounded; for a typical chat endpoint
this is fine (bounded by concurrent users). Do NOT put it in a global
LRU that could evict a hot entry mid-request.

DEPENDENCIES
------------
- shared.database_utils.execute_query   (Supabase-safe SQL execution)
- utils.logger_config                   ([AUTH_PLATFORM] tag for logs)

LAST MODIFIED: 2026-07-24 - Initial creation; fixes silent "auto" no-op.
"""

import logging
import threading
from typing import Optional

from shared.database_utils import execute_query, is_using_supabase

logger = logging.getLogger(__name__)

# Per-process cache: (user_id, stored_value) -> resolved platform.
# Thread-safe because the chat pipeline runs on a gevent worker pool.
_REQUEST_CACHE: dict = {}
_REQUEST_CACHE_LOCK = threading.Lock()


def _lookup_active_token(user_id: int) -> Optional[str]:
    """
    Query oauth_tokens for the user's most-recently-updated active token.

    Mirrors the freshness check at routes/auth_routes.py:320-324:
        - is_active = TRUE  (or NULL on legacy rows)
        - expires_at IS NULL OR expires_at > NOW()
        - access_token IS NOT NULL

    Returns:
        'google' | 'microsoft' | None

    Note on the platform string: oauth_tokens stores 'microsoft' or
    'microsoft365' interchangeably (see auth_routes.py:331). We
    normalise both to 'microsoft' here.
    """
    bool_true = True if is_using_supabase() else 1
    now_sql = "NOW()" if is_using_supabase() else "datetime('now')"

    try:
        row = execute_query(
            f"""
            SELECT platform
            FROM ai_infrastructure.oauth_tokens
            WHERE user_id = %s
              AND access_token IS NOT NULL
              AND (is_active = %s OR is_active IS NULL)
              AND (expires_at IS NULL OR expires_at > {now_sql})
              AND LOWER(platform) IN ('google', 'microsoft', 'microsoft365')
            ORDER BY updated_at DESC NULLS LAST, created_at DESC
            LIMIT 1
            """,
            (user_id, bool_true),
            fetch_mode='one',
            schema='ai_infrastructure',
        )
    except Exception as e:
        logger.warning(f"[AUTH_PLATFORM] token lookup failed for user_id={user_id}: {e}")
        return None

    if not row:
        return None

    # row is a dict under Supabase (RealDictCursor) or a tuple under SQLite
    platform = row.get('platform') if isinstance(row, dict) else row[0]
    if not platform:
        return None
    normalised = platform.lower()
    if normalised in ('microsoft', 'microsoft365'):
        return 'microsoft'
    if normalised == 'google':
        return 'google'
    return None


def resolve_auth_platform(user_id: Optional[int], stored_value: Optional[str]) -> Optional[str]:
    """
    Resolve the effective auth platform for a user.

    Args:
        user_id: The numeric user id. May be None (returns None).
        stored_value: The raw value from user_preferences.auth_platform.
                      One of: 'auto', 'microsoft', 'google', None, '', or any
                      other string (treated as 'auto').

    Returns:
        'google' | 'microsoft' | None

    Behaviour:
        - Explicit 'google' or 'microsoft' → returned as-is (no DB lookup).
        - 'auto' / None / '' / unknown   → look up oauth_tokens for the user.
                                          Pick the most-recently-updated
                                          active platform. If both vendors
                                          are connected, the most-recent wins.
                                          If no token is found, return None
                                          (the chat pipeline's else-branch
                                          will fire its "auto-detect" hint).
        - Invalid user_id (None / 0)      → return None (no lock).

    Side effects:
        Logs a one-line [AUTH_PLATFORM] message at INFO level for
        observability ("auto → google (token updated 2026-07-24 …)").
    """
    if not user_id:
        return None

    # Normalise the stored value
    if stored_value is None:
        normalised_stored = 'auto'
    else:
        normalised_stored = str(stored_value).strip().lower() or 'auto'

    # Explicit locks pass through
    if normalised_stored in ('google', 'microsoft'):
        return normalised_stored

    # Anything else (including 'auto') triggers a token lookup
    cache_key = (user_id, normalised_stored)
    with _REQUEST_CACHE_LOCK:
        cached = _REQUEST_CACHE.get(cache_key)
        if cached is not None or cache_key in _REQUEST_CACHE:
            # Cache hit (including explicit None misses)
            return cached

    resolved = _lookup_active_token(user_id)

    with _REQUEST_CACHE_LOCK:
        _REQUEST_CACHE[cache_key] = resolved

    if resolved:
        logger.info(f"[AUTH_PLATFORM] user_id={user_id} auto → {resolved}")
    else:
        logger.info(f"[AUTH_PLATFORM] user_id={user_id} auto → None (no active OAuth token)")

    return resolved


def clear_request_cache() -> None:
    """
    Clear the per-process resolution cache.

    Test-only helper. The chat pipeline never needs to call this because
    the cache is per-process and bounded by unique (user_id, stored_value)
    pairs — at most a few entries per concurrent user. Tests that want a
    clean slate between scenarios should call this in setUp/tearDown.
    """
    with _REQUEST_CACHE_LOCK:
        _REQUEST_CACHE.clear()
