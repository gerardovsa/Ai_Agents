-- Migration 030: Add allowed_domains to organisations for SSO auto-provisioning (GAP-M6)
-- Purpose: When a new SSO user logs in via Google/Microsoft, they are automatically
--          added to the matching organisation if their email domain is in allowed_domains.
-- Idempotent: Uses ADD COLUMN IF NOT EXISTS.
-- Date: 2026

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'organisations'
          AND column_name  = 'allowed_domains'
    ) THEN
        ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN allowed_domains TEXT[] DEFAULT '{}';
        RAISE NOTICE 'Added allowed_domains to ai_infrastructure.organisations';
    ELSE
        RAISE NOTICE 'organisations.allowed_domains already exists, skipping';
    END IF;
END $$;

-- Index for fast domain lookup in OAuth callbacks
CREATE INDEX IF NOT EXISTS idx_organisations_allowed_domains
    ON ai_infrastructure.organisations
    USING gin(allowed_domains);

COMMENT ON COLUMN ai_infrastructure.organisations.allowed_domains IS
    'Array of email domains e.g. {"acme.com","acme.io"} — new SSO users with matching domain are auto-provisioned into this org as member.';
