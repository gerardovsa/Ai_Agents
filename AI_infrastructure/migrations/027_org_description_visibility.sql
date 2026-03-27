-- Migration 027: Add description and visibility columns to organisations table
-- These fields are exposed via the org overview settings panel in the UI.
-- Safe to run multiple times (idempotent).

ALTER TABLE ai_infrastructure.organisations
    ADD COLUMN IF NOT EXISTS description TEXT,
    ADD COLUMN IF NOT EXISTS visibility   VARCHAR(20) DEFAULT 'private';

-- Ensure visibility only accepts known values (backfill NULLs first)
UPDATE ai_infrastructure.organisations
    SET visibility = 'private'
    WHERE visibility IS NULL;

ALTER TABLE ai_infrastructure.organisations
    ALTER COLUMN visibility SET DEFAULT 'private';

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_schema = 'ai_infrastructure'
          AND table_name = 'organisations'
          AND constraint_name = 'chk_organisations_visibility'
    ) THEN
        ALTER TABLE ai_infrastructure.organisations
            ADD CONSTRAINT chk_organisations_visibility
            CHECK (visibility IN ('private', 'unlisted', 'public'));
    END IF;
END$$;

COMMENT ON COLUMN ai_infrastructure.organisations.description IS
    'Optional human-readable description of the organisation.';
COMMENT ON COLUMN ai_infrastructure.organisations.visibility IS
    'Who can discover this org: private (invite-only), unlisted (link-only), public (searchable).';
