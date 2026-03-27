-- =============================================================================
-- Migration 039: Per-User Module Access
-- Date: March 2026
-- =============================================================================
-- Adds a user_module_access table that lets org admins RESTRICT specific
-- members from modules that the organisation has enabled.
--
-- Semantics (deliberately simple):
--   org enabled  +  no user row              = user CAN access (inherits org)
--   org enabled  +  user is_enabled = FALSE  = user CANNOT access (restricted)
--   org disabled +  any user row             = user CANNOT access (org is ceiling)
--
-- In plain English: admins can only take away, not grant beyond what the org has.
-- =============================================================================

-- ─── Table ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ai_infrastructure.user_module_access (
    user_id         INT          NOT NULL
        REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    organisation_id INT          NOT NULL
        REFERENCES ai_infrastructure.organisations(id) ON DELETE CASCADE,
    module_name     VARCHAR(100) NOT NULL,
    is_enabled      BOOLEAN      NOT NULL DEFAULT FALSE,
    set_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    set_by          INT
        REFERENCES ai_infrastructure.users(id) ON DELETE SET NULL,

    PRIMARY KEY (user_id, module_name)
);

COMMENT ON TABLE ai_infrastructure.user_module_access IS
    'Per-user module restriction overrides.  Only rows with is_enabled=FALSE '
    'are meaningful — they restrict a member from an org-enabled module.  '
    'Absence of a row means the user inherits the org-level setting.';

-- ─── Indexes ──────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_uma_user_id
    ON ai_infrastructure.user_module_access (user_id);

CREATE INDEX IF NOT EXISTS idx_uma_org_id
    ON ai_infrastructure.user_module_access (organisation_id);

CREATE INDEX IF NOT EXISTS idx_uma_module_name
    ON ai_infrastructure.user_module_access (module_name);

-- ─── Verify ───────────────────────────────────────────────────────────────────
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'user_module_access'
    ) THEN
        RAISE NOTICE 'Migration 039: user_module_access table ready.';
    ELSE
        RAISE EXCEPTION 'Migration 039: table creation failed.';
    END IF;
END $$;
