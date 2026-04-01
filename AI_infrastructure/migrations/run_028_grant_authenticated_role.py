"""
Run Migration 028: Grant Supabase `authenticated` Role Access
=============================================================
Grants SELECT/INSERT/UPDATE/DELETE on all synergy_sessions, ai_infrastructure,
and sessions schema tables to the Supabase `authenticated` role.

WHY THIS MATTERS:
  rls_session_manager.py calls SET LOCAL ROLE authenticated on every DB
  connection that has a logged-in user (g.rls_user_id is set).  If the
  authenticated role has no permissions on a schema, every query made while
  a user is logged in returns "permission denied for table X" → HTTP 500.

NOTE: This runner connects DIRECTLY via psycopg2 as the postgres superuser
(bypassing the Flask connection pool and inject_rls_vars) so it can issue
GRANT statements before the authenticated role has any rights.

IDEMPOTENT: GRANT commands are no-ops if the privilege already exists.
"""
import os
import sys
from pathlib import Path

# Allow direct execution from any directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load .env.master from project root
_root = Path(__file__).parent.parent.parent
load_dotenv(_root / '.env.master', override=True)
load_dotenv(_root / '.env', override=False)  # fallback

import psycopg2


def get_direct_connection():
    """
    Open a direct psycopg2 connection as the postgres superuser.
    Uses SUPABASE_DB_URL (session-mode port 5432) so that SET ROLE and
    multi-statement transactions work correctly.  Falls back to the pooler
    URL if only that is available.
    """
    # Prefer session-mode URL (port 5432) — needed for SET ROLE / GRANT
    url = (
        os.getenv('SUPABASE_DB_URL_SESSION')
        or os.getenv('SUPABASE_DB_URL')
        or os.getenv('SUPABASE_DB_URL_POOLER')
    )
    if not url:
        raise ValueError(
            "No Supabase DB URL found in environment.  "
            "Set SUPABASE_DB_URL or SUPABASE_DB_URL_SESSION."
        )
    return psycopg2.connect(url, sslmode='require', connect_timeout=30)


def run_migration():
    print("=" * 70)
    print("Migration 028: Grant `authenticated` role access to app schemas")
    print("=" * 70)

    # SQL blocks to execute — each is (description, sql)
    steps = [
        # ── ai_infrastructure ──────────────────────────────────────────────
        ("ai_infrastructure: USAGE on schema",
         "GRANT USAGE ON SCHEMA ai_infrastructure TO authenticated"),

        ("ai_infrastructure: DML on all existing tables",
         "GRANT SELECT, INSERT, UPDATE, DELETE "
         "ON ALL TABLES IN SCHEMA ai_infrastructure TO authenticated"),

        ("ai_infrastructure: sequences",
         "GRANT USAGE, SELECT "
         "ON ALL SEQUENCES IN SCHEMA ai_infrastructure TO authenticated"),

        ("ai_infrastructure: default table privileges",
         "ALTER DEFAULT PRIVILEGES IN SCHEMA ai_infrastructure "
         "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated"),

        ("ai_infrastructure: default sequence privileges",
         "ALTER DEFAULT PRIVILEGES IN SCHEMA ai_infrastructure "
         "GRANT USAGE, SELECT ON SEQUENCES TO authenticated"),

        # ── synergy_sessions ───────────────────────────────────────────────
        ("synergy_sessions: USAGE on schema",
         "GRANT USAGE ON SCHEMA synergy_sessions TO authenticated"),

        ("synergy_sessions: DML on all existing tables",
         "GRANT SELECT, INSERT, UPDATE, DELETE "
         "ON ALL TABLES IN SCHEMA synergy_sessions TO authenticated"),

        ("synergy_sessions: sequences",
         "GRANT USAGE, SELECT "
         "ON ALL SEQUENCES IN SCHEMA synergy_sessions TO authenticated"),

        ("synergy_sessions: default table privileges",
         "ALTER DEFAULT PRIVILEGES IN SCHEMA synergy_sessions "
         "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated"),

        ("synergy_sessions: default sequence privileges",
         "ALTER DEFAULT PRIVILEGES IN SCHEMA synergy_sessions "
         "GRANT USAGE, SELECT ON SEQUENCES TO authenticated"),

        # ── sessions ───────────────────────────────────────────────────────
        ("sessions: USAGE on schema",
         "GRANT USAGE ON SCHEMA sessions TO authenticated"),

        ("sessions: DML on all existing tables",
         "GRANT SELECT, INSERT, UPDATE, DELETE "
         "ON ALL TABLES IN SCHEMA sessions TO authenticated"),

        ("sessions: sequences",
         "GRANT USAGE, SELECT "
         "ON ALL SEQUENCES IN SCHEMA sessions TO authenticated"),

        ("sessions: default table privileges",
         "ALTER DEFAULT PRIVILEGES IN SCHEMA sessions "
         "GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated"),

        ("sessions: default sequence privileges",
         "ALTER DEFAULT PRIVILEGES IN SCHEMA sessions "
         "GRANT USAGE, SELECT ON SEQUENCES TO authenticated"),
    ]

    conn = get_direct_connection()
    conn.autocommit = True  # Each GRANT commits immediately

    passed = 0
    failed = 0

    for description, sql in steps:
        print(f"\n  {description} ...", end=" ")
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
            print("OK")
            passed += 1
        except psycopg2.Error as e:
            err = str(e).strip()
            # Some ALTER DEFAULT PRIVILEGES errors are ignorable
            if "already exists" in err.lower():
                print("already exists (OK)")
                passed += 1
            else:
                print(f"ERROR: {err}")
                failed += 1

    conn.close()

    print("\n" + "=" * 70)
    print(f"Done — {passed} steps passed, {failed} steps failed")
    print("=" * 70)

    if failed:
        print("\n⚠️  Some steps failed. Check errors above.")
        print("   You can also paste the SQL below directly into the Supabase SQL editor:")
        _print_raw_sql()
        return False
    else:
        print("\n✅ All grants applied. Synergy sessions should load on next request.")
        return True


def _print_raw_sql():
    """Print the raw SQL for manual execution in Supabase SQL editor."""
    sql = """
-- Paste this in the Supabase SQL editor if the Python runner fails

GRANT USAGE ON SCHEMA ai_infrastructure TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ai_infrastructure TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA ai_infrastructure TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_infrastructure GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_infrastructure GRANT USAGE, SELECT ON SEQUENCES TO authenticated;

GRANT USAGE ON SCHEMA synergy_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA synergy_sessions TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA synergy_sessions TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA synergy_sessions GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA synergy_sessions GRANT USAGE, SELECT ON SEQUENCES TO authenticated;

GRANT USAGE ON SCHEMA sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sessions TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA sessions TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA sessions GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA sessions GRANT USAGE, SELECT ON SEQUENCES TO authenticated;
"""
    print(sql)


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
