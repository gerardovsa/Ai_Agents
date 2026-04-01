"""
Migration 040 — Add missing RLS policies on ai_infrastructure.organisations
============================================================================
The organisations table had RLS enabled but ONLY a service_role bypass policy.
The authenticated role (used by all logged-in Flask requests via SET LOCAL ROLE)
had zero SELECT/INSERT/UPDATE access, causing every /api/org/* route to return
empty results → 404 "Organisation not found".

This migration adds:
 - SELECT policy: members can read their own org (matches app.current_organisation_id)
 - INSERT policy: allow org creation (app layer already gates this)
 - UPDATE policy: admins can update their own org (app layer enforces admin role)

Idempotent: uses CREATE POLICY IF NOT EXISTS (Postgres 15+) or DROP+CREATE pattern.
"""

import os
import sys
import psycopg2

# ── paths ──────────────────────────────────────────────────────────────────────
HERE = os.path.dirname(os.path.abspath(__file__))
AI_INFRA = os.path.dirname(HERE)
REPO_ROOT = os.path.dirname(AI_INFRA)
for p in [AI_INFRA, REPO_ROOT]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Load .env from repo root
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(REPO_ROOT, '.env'))
except ImportError:
    pass

STEPS = [
    # ── SELECT: members can read their own organisation ──────────────────────
    (
        "Drop old SELECT policy if exists",
        """
        DROP POLICY IF EXISTS org_members_select_own_org
          ON ai_infrastructure.organisations;
        """
    ),
    (
        "Create SELECT policy on organisations",
        """
        CREATE POLICY org_members_select_own_org
          ON ai_infrastructure.organisations
          FOR SELECT
          TO public
          USING (
              id = (current_setting('app.current_organisation_id', true)::integer)
          );
        """
    ),
    # ── INSERT: allow org creation (app layer fully controls who can call it) ─
    (
        "Drop old INSERT policy if exists",
        """
        DROP POLICY IF EXISTS org_allow_create
          ON ai_infrastructure.organisations;
        """
    ),
    (
        "Create INSERT policy on organisations",
        """
        CREATE POLICY org_allow_create
          ON ai_infrastructure.organisations
          FOR INSERT
          TO public
          WITH CHECK (true);
        """
    ),
    # ── UPDATE: admins can update their own org ──────────────────────────────
    (
        "Drop old UPDATE policy if exists",
        """
        DROP POLICY IF EXISTS org_admins_update_own_org
          ON ai_infrastructure.organisations;
        """
    ),
    (
        "Create UPDATE policy on organisations",
        """
        CREATE POLICY org_admins_update_own_org
          ON ai_infrastructure.organisations
          FOR UPDATE
          TO public
          USING (
              id = (current_setting('app.current_organisation_id', true)::integer)
          )
          WITH CHECK (
              id = (current_setting('app.current_organisation_id', true)::integer)
          );
        """
    ),
    # ── Verify ───────────────────────────────────────────────────────────────
    (
        "Verify policies exist",
        """
        SELECT policyname, cmd, roles
        FROM pg_policies
        WHERE schemaname = 'ai_infrastructure'
          AND tablename = 'organisations'
        ORDER BY policyname;
        """
    ),
]


def run():
    db_url = (
        os.environ.get('SUPABASE_DB_URL_SESSION')
        or os.environ.get('SUPABASE_DB_URL')
        or os.environ.get('SUPABASE_DB_URL_POOLER')
    )
    if not db_url:
        print("ERROR: No database URL found.")
        sys.exit(1)

    # Use Session Mode (port 5432) — superuser needed for CREATE POLICY
    db_url = db_url.replace(':6543/', ':5432/')
    print(f"Connecting to: {db_url[:50]}...")

    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()

    passed = 0
    failed = 0
    for label, sql in STEPS:
        try:
            cur.execute(sql)
            if cur.description:
                rows = cur.fetchall()
                print(f"  ✅ {label}")
                for row in rows:
                    print(f"      {row}")
            else:
                print(f"  ✅ {label}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {label}: {e}")
            failed += 1

    cur.close()
    conn.close()
    print(f"\nDone: {passed} passed, {failed} failed.")
    if failed:
        sys.exit(1)


if __name__ == '__main__':
    run()
