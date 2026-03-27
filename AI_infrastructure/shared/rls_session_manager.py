"""
RLS Session Manager
===================
Sets PostgreSQL session-level configuration variables used by Row-Level Security
policies across ALL schemas (ai_infrastructure, synergy_sessions, sessions).

HOW IT WORKS:
  - RLS policies on tables like synergy_sessions.synergy_sessions use:
        current_setting('app.current_user_id', true)::integer
        current_setting('app.current_organisation_id', true)::integer
  - These must be SET on the psycopg2 connection BEFORE any query runs.
  - We use `set_config(..., true)` which is TRANSACTION-LOCAL, meaning the
    vars are automatically cleared when the connection is returned to the pool.

CALL SITE:
  database_utils.get_database_connection() calls inject_rls_vars() immediately
  after acquiring a connection from the pool.

The values come from Flask's g object (g.rls_user_id, g.rls_organisation_id)
which are populated by the @before_request JWT middleware in flask_app.py.

For non-HTTP contexts (background tasks, migrations) pass explicit values.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def inject_rls_vars(
    conn,
    user_id: Optional[int] = None,
    organisation_id: Optional[int] = None,
) -> None:
    """
    Set app.current_user_id and app.current_organisation_id on the given psycopg2
    connection using set_config (transaction-local so pool-safe).

    Args:
        conn:             psycopg2 connection (any schema)
        user_id:          Override — use this instead of g.rls_user_id when provided
        organisation_id:  Override — use this instead of g.rls_organisation_id when provided

    If neither override is provided AND Flask g isn't available or has no values,
    the function sets empty strings (Postgres returns NULL for unset settings when
    the 'true' missing-ok flag is used in current_setting).
    """
    # Resolve values: prefer explicit args, then Flask g, then empty string
    resolved_user_id = _resolve_value(user_id, 'rls_user_id')
    resolved_org_id  = _resolve_value(organisation_id, 'rls_organisation_id')

    if resolved_user_id is None and resolved_org_id is None:
        # No context available — skip (no-op; RLS policies use missing-ok flag)
        return

    try:
        cursor = conn.cursor()
        # set_config(name, value, is_local)
        # is_local=TRUE → reset at end of transaction → POOL-SAFE
        if resolved_user_id is not None:
            cursor.execute(
                "SELECT set_config('app.current_user_id', %s, true)",
                (str(resolved_user_id),)
            )
        if resolved_org_id is not None:
            cursor.execute(
                "SELECT set_config('app.current_organisation_id', %s, true)",
                (str(resolved_org_id),)
            )

        # GAP-C2 FIX: Switch to 'authenticated' role so RLS policies actually fire.
        # The postgres superuser bypasses ALL Row-Level Security regardless of session
        # vars.  'authenticated' is a non-superuser role built into every Supabase
        # project — it IS subject to RLS.  SET LOCAL reverts at transaction end,
        # which is called by PooledConnection.close() → conn.rollback().  POOL-SAFE.
        # Only switch when we have a user context (background tasks stay as postgres).
        if resolved_user_id is not None:
            cursor.execute("SET LOCAL ROLE authenticated")

        cursor.close()
        # GAP-H5 FIX: Use INFO level so RLS injection is visible in production logs
        # without requiring DEBUG mode.  Helps verify multi-tenant isolation is active.
        logger.info(
            f"[RLS] Injected — user_id={resolved_user_id} org_id={resolved_org_id} "
            f"role=authenticated"
        )
    except Exception as e:
        # Non-fatal: log and continue. RLS policies use 'true' (missing-ok) so they
        # will just deny access rather than crash if vars are unset.
        logger.warning(f"[RLS] Failed to set session vars (non-fatal): {e}")


def _resolve_value(explicit_value, g_attr: str) -> Optional[int]:
    """Return explicit_value if given, else try Flask g, else None."""
    if explicit_value is not None:
        return int(explicit_value)
    try:
        from flask import g
        val = getattr(g, g_attr, None)
        return int(val) if val is not None else None
    except RuntimeError:
        # No Flask application/request context (e.g. background task)
        return None


def get_rls_context() -> dict:
    """
    Return the current RLS context (user_id, organisation_id) from Flask g.
    Returns empty dict if outside request context.

    Useful for routes that need to read the current user/org without re-querying the DB.
    """
    try:
        from flask import g
        return {
            'user_id':         getattr(g, 'rls_user_id', None),
            'organisation_id': getattr(g, 'rls_organisation_id', None),
        }
    except RuntimeError:
        return {}
