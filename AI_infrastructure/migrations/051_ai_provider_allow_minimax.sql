-- ============================================================================
-- Migration 051: Allow MiniMax in organisations.ai_provider CHECK constraint
-- Created: June 11, 2026
-- Purpose: Migration 031 added a CHECK constraint on
--          organisations.ai_provider restricting it to:
--              ('anthropic', 'openai', 'deepseek')
--          Migration 050 introduced MiniMax as a fourth provider (in
--          platform_catalog and ai_model_catalog), but did not update that
--          CHECK constraint.  Result: any org trying to save
--          ai_provider = 'MiniMax' via PUT /api/org/info would be rejected
--          at the DB layer even though the Python validator accepted it.
--
--          This migration widens the CHECK constraint to include 'MiniMax'
--          (and any future Anthropic-API-compatible provider we add).  It is
--          a safe widening — no previously-valid value is now invalid.
--
-- Idempotent: drops and re-adds the constraint unconditionally; safe to
--             run multiple times because the new constraint is identical
--             on second+ runs.
-- ============================================================================

DO $$
BEGIN
    -- Drop the old CHECK if it exists
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'chk_organisations_ai_provider'
          AND table_schema    = 'ai_infrastructure'
    ) THEN
        ALTER TABLE ai_infrastructure.organisations
            DROP CONSTRAINT chk_organisations_ai_provider;
        RAISE NOTICE '[Migration 051] Dropped old chk_organisations_ai_provider constraint';
    END IF;

    -- Re-add with MiniMax included
    ALTER TABLE ai_infrastructure.organisations
        ADD CONSTRAINT chk_organisations_ai_provider
        CHECK (ai_provider IN ('anthropic', 'openai', 'deepseek', 'MiniMax'));
    RAISE NOTICE '[Migration 051] Added widened chk_organisations_ai_provider (4 providers)';
END $$;

-- Refresh column comment to reflect the new option
COMMENT ON COLUMN ai_infrastructure.organisations.ai_provider IS
    'AI provider for this org: anthropic | openai | deepseek | MiniMax (default: anthropic)';

-- =========================================================================
-- Verify
-- =========================================================================
DO $$
DECLARE
    constraint_def TEXT;
BEGIN
    SELECT pg_get_constraintdef(c.oid)
    INTO   constraint_def
    FROM   pg_constraint c
    JOIN   pg_namespace n ON n.oid = c.connamespace
    WHERE  c.conname = 'chk_organisations_ai_provider'
      AND  n.nspname = 'ai_infrastructure';

    IF constraint_def LIKE '%MiniMax%' THEN
        RAISE NOTICE '[Migration 051] ✅ Constraint correctly includes MiniMax: %', constraint_def;
    ELSE
        RAISE WARNING '[Migration 051] ❌ Constraint does not include MiniMax: %', constraint_def;
    END IF;
END $$;
