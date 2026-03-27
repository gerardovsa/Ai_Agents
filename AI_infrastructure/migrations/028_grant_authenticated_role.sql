-- ============================================================
-- Migration 028: Grant Supabase `authenticated` Role Access
-- ============================================================
-- GAP-C2 FIX: The connection pool runs as the `postgres` superuser, which
-- bypasses all Row-Level Security policies regardless of which RLS vars are
-- set.  The fix is to switch the transaction role to `authenticated` (a
-- non-superuser role built into every Supabase project) immediately after
-- injecting the RLS session vars.  RLS policies fire for
-- `authenticated` just as they do for PostgREST-issued requests.
--
-- This migration grants the `authenticated` role the minimum privileges it
-- needs so that the role-switch inside inject_rls_vars() succeeds.
--
-- WHAT THIS DOES:
--   1. Grants USAGE on the application schemas to `authenticated`.
--   2. Grants DML on all current tables in those schemas.
--   3. Grants USAGE/SELECT on sequences (for nextval() in INSERTs).
--   4. Sets DEFAULT PRIVILEGES so future tables are automatically covered.
--
-- IMPORTANT: `authenticated` is subject to RLS.  Tables without RLS policies
-- will have all their rows visible/writable to any authenticated request.
-- For those tables (users, organisations, etc.) the application layer already
-- enforces access control.  Tables with RLS (organisation_platform_credentials,
-- synergy_sessions tables, etc.) will be filtered by the policies.
--
-- IDEMPOTENT: GRANT is idempotent — re-running adds nothing, fails silently.
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- ai_infrastructure schema
-- ────────────────────────────────────────────────────────────
GRANT USAGE ON SCHEMA ai_infrastructure TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE
    ON ALL TABLES IN SCHEMA ai_infrastructure
    TO authenticated;

GRANT USAGE, SELECT
    ON ALL SEQUENCES IN SCHEMA ai_infrastructure
    TO authenticated;

-- Automatically cover tables created in future migrations
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_infrastructure
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA ai_infrastructure
    GRANT USAGE, SELECT ON SEQUENCES TO authenticated;

-- ────────────────────────────────────────────────────────────
-- synergy_sessions schema  (project management / task tracking)
-- ────────────────────────────────────────────────────────────
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.schemata
        WHERE schema_name = 'synergy_sessions'
    ) THEN
        EXECUTE 'GRANT USAGE ON SCHEMA synergy_sessions TO authenticated';
        EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE
                     ON ALL TABLES IN SCHEMA synergy_sessions
                     TO authenticated';
        EXECUTE 'GRANT USAGE, SELECT
                     ON ALL SEQUENCES IN SCHEMA synergy_sessions
                     TO authenticated';
    END IF;
END$$;

ALTER DEFAULT PRIVILEGES IN SCHEMA synergy_sessions
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA synergy_sessions
    GRANT USAGE, SELECT ON SEQUENCES TO authenticated;

-- ────────────────────────────────────────────────────────────
-- sessions schema  (chat threads, messages)
-- ────────────────────────────────────────────────────────────
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.schemata
        WHERE schema_name = 'sessions'
    ) THEN
        EXECUTE 'GRANT USAGE ON SCHEMA sessions TO authenticated';
        EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE
                     ON ALL TABLES IN SCHEMA sessions
                     TO authenticated';
        EXECUTE 'GRANT USAGE, SELECT
                     ON ALL SEQUENCES IN SCHEMA sessions
                     TO authenticated';
    END IF;
END$$;

ALTER DEFAULT PRIVILEGES IN SCHEMA sessions
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;

ALTER DEFAULT PRIVILEGES IN SCHEMA sessions
    GRANT USAGE, SELECT ON SEQUENCES TO authenticated;
