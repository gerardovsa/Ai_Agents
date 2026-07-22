-- ============================================================================
-- Migration 056: Partial unique index on active vault rows
-- Created:    2026-07-22
-- Purpose:    Enforce "exactly one ACTIVE credential row per (org, platform)".
--             The existing schema has UNIQUE(organisation_id, platform,
--             display_name) which lets you keep historical/inactive rows
--             but allows multiple active rows for the same (org, platform)
--             if their display_names differ - this is a bug for the
--             resolver, which expects one canonical answer.
--
--             With this partial unique index, the 4-tier
--             org_credentials_loader.resolve_credentials() is guaranteed
--             to find at most one active row per (org, platform), and the
--             seed-vault endpoint's ON CONFLICT (organisation_id, platform)
--             works as written.
--
--             Why a partial index (not a full constraint):
--             - Lets us soft-delete (is_active = FALSE) a row for key
--               rotation or replacement without losing history.
--             - Only enforces uniqueness on the "live" set.
--
-- Idempotent: yes (CREATE UNIQUE INDEX IF NOT EXISTS).
--             The verification block at the end confirms the index was
--             applied; re-running the migration is a no-op.
-- ============================================================================

CREATE UNIQUE INDEX IF NOT EXISTS organisation_platform_credentials_active_unique
    ON ai_infrastructure.organisation_platform_credentials (organisation_id, platform)
    WHERE is_active = TRUE;

-- Verify
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'ai_infrastructure'
          AND tablename  = 'organisation_platform_credentials'
          AND indexname  = 'organisation_platform_credentials_active_unique'
    ) THEN
        RAISE NOTICE 'organisation_platform_credentials_active_unique index present';
    ELSE
        RAISE EXCEPTION 'index organisation_platform_credentials_active_unique missing';
    END IF;
END $$;
