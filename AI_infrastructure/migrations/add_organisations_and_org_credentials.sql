-- ============================================================================
-- MIGRATION: Organisation Multi-Tenancy + Credential Access Control
-- FILE: AI_infrastructure/migrations/add_organisations_and_org_credentials.sql
-- Date: March 2026
--
-- PURPOSE:
--   1. Create organisations table
--   2. Link users to organisations via organization_id + role
--   3. Create organisation_platform_credentials (org-owned API keys)
--   4. Create credential_access_log (audit trail for reveals)
--   5. Update user_platform_credentials to support org scope
--
-- ROLE HIERARCHY (least → most privileged):
--   viewer < member < manager < admin < owner
--
-- CREDENTIAL ACCESS RULES:
--   - LIST credentials (masked):  manager, admin, owner
--   - ADD / EDIT credential:      admin, owner
--   - DELETE credential:          admin, owner
--   - REVEAL actual key value:    admin, owner + password re-confirmation
--
-- IDEMPOTENT: Safe to run multiple times (all use IF NOT EXISTS / IF EXISTS)
-- ============================================================================

-- ============================================================================
-- STEP 1: ORGANISATIONS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.organisations (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) NOT NULL,
    slug            VARCHAR(100) NOT NULL UNIQUE,    -- URL-safe name e.g. "acme-corp"
    plan_tier       VARCHAR(50)  DEFAULT 'starter',  -- starter | growth | enterprise
    is_active       BOOLEAN      DEFAULT TRUE,

    -- Optional branding / meta
    display_name    VARCHAR(255),
    logo_url        TEXT,
    timezone        VARCHAR(100) DEFAULT 'UTC',
    country_code    VARCHAR(10),

    -- Credential vault password
    -- This is the ADDITIONAL password required to reveal API key values.
    -- Stored as bcrypt hash. NULL means no extra password (rely on role only).
    vault_password_hash TEXT,

    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata        JSONB DEFAULT '{}'::jsonb
);

COMMENT ON TABLE ai_infrastructure.organisations IS
    'Top-level tenant organisations. Each organisation has its own API keys, users, and modules.';
COMMENT ON COLUMN ai_infrastructure.organisations.vault_password_hash IS
    'bcrypt hash of the vault password required to REVEAL (not just list) org API key values. NULL = no extra lock.';
COMMENT ON COLUMN ai_infrastructure.organisations.slug IS
    'URL-safe unique identifier for the org, e.g. acme-corp. Used in subdomains/routing.';

-- ============================================================================
-- STEP 2: ADD ORGANISATION COLUMNS TO USERS TABLE
-- ============================================================================

-- Add organisation_id link
ALTER TABLE ai_infrastructure.users
    ADD COLUMN IF NOT EXISTS organisation_id INTEGER REFERENCES ai_infrastructure.organisations(id) ON DELETE SET NULL;

-- Add role within the organisation
-- viewer  = read-only access
-- member  = standard user, can use tools
-- manager = can view masked credentials, manage threads/workflows
-- admin   = can add/edit/delete credentials (masked), manage members
-- owner   = full access incl. REVEAL credential values + billing
ALTER TABLE ai_infrastructure.users
    ADD COLUMN IF NOT EXISTS org_role VARCHAR(50) DEFAULT 'member';

-- Add constraint to enforce valid roles
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'users_org_role_check'
          AND table_schema = 'ai_infrastructure'
          AND table_name = 'users'
    ) THEN
        ALTER TABLE ai_infrastructure.users
            ADD CONSTRAINT users_org_role_check
            CHECK (org_role IN ('viewer', 'member', 'manager', 'admin', 'owner'));
    END IF;
END $$;

-- Index for org membership lookups
CREATE INDEX IF NOT EXISTS idx_users_organisation_id
    ON ai_infrastructure.users(organisation_id);

CREATE INDEX IF NOT EXISTS idx_users_org_role
    ON ai_infrastructure.users(organisation_id, org_role);

COMMENT ON COLUMN ai_infrastructure.users.organisation_id IS
    'Foreign key to the organisation this user belongs to. NULL = no org (solo/legacy user).';
COMMENT ON COLUMN ai_infrastructure.users.org_role IS
    'Role within the organisation. Hierarchy: viewer < member < manager < admin < owner.';

-- ============================================================================
-- STEP 3: ORGANISATION PLATFORM CREDENTIALS TABLE
--
-- Stores org-level API keys (Anthropic, OpenAI, AusPost, Stripe, etc.)
-- These are shared by ALL members of the organisation.
-- Only admin/owner can add/edit. Only admin/owner + vault password can REVEAL.
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.organisation_platform_credentials (
    id                      SERIAL PRIMARY KEY,
    organisation_id         INTEGER NOT NULL REFERENCES ai_infrastructure.organisations(id) ON DELETE CASCADE,

    -- Which platform / service this key is for
    platform                VARCHAR(100) NOT NULL,   -- anthropic, openai, auspost, stripe, xero, etc.
    display_name            VARCHAR(255),            -- Human label e.g. "Main Anthropic Key"
    environment             VARCHAR(50) DEFAULT 'production',  -- production | staging | test

    -- The actual credential value (single API key scenario)
    -- Stored as plain text or application-encrypted text.
    -- We rely on DB-level RLS + role checks + vault password for protection.
    credential_value        TEXT,

    -- JSON blob for platforms that need multiple fields (client_id, secret, shop_url etc.)
    credentials             JSONB DEFAULT '{}'::jsonb,

    -- Access control flags
    -- Which minimum role can SEE this credential in the list (masked display)
    visible_to_role         VARCHAR(50) DEFAULT 'manager'
        CHECK (visible_to_role IN ('viewer', 'member', 'manager', 'admin', 'owner')),
    -- Which minimum role can REVEAL the actual key (requires vault_password_hash)
    reveal_requires_role    VARCHAR(50) DEFAULT 'admin'
        CHECK (reveal_requires_role IN ('viewer', 'member', 'manager', 'admin', 'owner')),

    -- Metadata
    is_active               BOOLEAN DEFAULT TRUE,
    notes                   TEXT,       -- Internal notes about this key
    last_used_at            TIMESTAMP,
    expires_at              TIMESTAMP,  -- Optional key expiry tracking

    -- Rotation tracking
    rotation_due_at         TIMESTAMP,
    rotation_reminder_sent  BOOLEAN DEFAULT FALSE,

    created_by_user_id      INTEGER REFERENCES ai_infrastructure.users(id) ON DELETE SET NULL,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- A platform can have multiple credentials (e.g. prod + staging Stripe keys).
    -- NULLS NOT DISTINCT: two rows with the same org+platform and NULL display_name
    -- are treated as duplicates (requires PostgreSQL 15+, which Supabase supports).
    UNIQUE NULLS NOT DISTINCT (organisation_id, platform, display_name)
);

COMMENT ON TABLE ai_infrastructure.organisation_platform_credentials IS
    'Organisation-wide API keys shared across all org members. Access is role-gated.
     Listing shows masked values (sk-ant-****...****). Revealing requires admin+ role + vault password.';
COMMENT ON COLUMN ai_infrastructure.organisation_platform_credentials.credential_value IS
    'Single API key string. For multi-field credentials use the credentials JSONB column.';
COMMENT ON COLUMN ai_infrastructure.organisation_platform_credentials.credentials IS
    'Multi-field credentials JSON e.g. {"client_id": "...", "client_secret": "...", "shop_url": "..."}';
COMMENT ON COLUMN ai_infrastructure.organisation_platform_credentials.visible_to_role IS
    'Minimum org_role needed to see this credential exists (masked). Default: manager.';
COMMENT ON COLUMN ai_infrastructure.organisation_platform_credentials.reveal_requires_role IS
    'Minimum org_role needed to reveal the actual key value. Default: admin.
     Reveal endpoint also requires vault password confirmation if set on the org.';

-- Indexes
CREATE INDEX IF NOT EXISTS idx_org_creds_organisation_id
    ON ai_infrastructure.organisation_platform_credentials(organisation_id);

CREATE INDEX IF NOT EXISTS idx_org_creds_platform
    ON ai_infrastructure.organisation_platform_credentials(organisation_id, platform);

CREATE INDEX IF NOT EXISTS idx_org_creds_active
    ON ai_infrastructure.organisation_platform_credentials(organisation_id, is_active);

-- ============================================================================
-- STEP 4: CREDENTIAL ACCESS LOG (Audit Trail)
--
-- Every time someone REVEALS an actual API key value, we log it.
-- Provides full audit trail: who saw what key, when.
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.credential_access_log (
    id                  SERIAL PRIMARY KEY,
    organisation_id     INTEGER NOT NULL REFERENCES ai_infrastructure.organisations(id) ON DELETE CASCADE,
    credential_id       INTEGER REFERENCES ai_infrastructure.organisation_platform_credentials(id) ON DELETE SET NULL,
    user_id             INTEGER NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,

    action              VARCHAR(50) NOT NULL,  -- revealed | listed | added | edited | deleted | vault_password_changed
    platform            VARCHAR(100),
    display_name        VARCHAR(255),

    -- Request context
    ip_address          VARCHAR(45),  -- IPv4 or IPv6
    user_agent          TEXT,

    -- Whether the vault password was used for this action
    vault_password_used BOOLEAN DEFAULT FALSE,

    performed_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes               TEXT
);

COMMENT ON TABLE ai_infrastructure.credential_access_log IS
    'Full audit trail of all credential access events. Immutable log (no updates, no deletes).';
COMMENT ON COLUMN ai_infrastructure.credential_access_log.action IS
    'What happened: revealed | listed | added | edited | deleted | vault_password_changed';

CREATE INDEX IF NOT EXISTS idx_cred_access_log_org
    ON ai_infrastructure.credential_access_log(organisation_id, performed_at DESC);

CREATE INDEX IF NOT EXISTS idx_cred_access_log_user
    ON ai_infrastructure.credential_access_log(user_id, performed_at DESC);

-- ============================================================================
-- STEP 5: UPDATE user_platform_credentials TO SUPPORT ORG SCOPE
--
-- Existing user_platform_credentials are USER-specific (OAuth tokens, personal keys).
-- We add an optional scope column so the same table can hold:
--   scope='user'   → belongs to a specific user only (default, existing behaviour)
--   scope='org'    → DEPRECATED in favour of organisation_platform_credentials
--                    (kept for backward compat only)
-- ============================================================================

ALTER TABLE ai_infrastructure.user_platform_credentials
    ADD COLUMN IF NOT EXISTS scope VARCHAR(20) DEFAULT 'user';

-- Ensure existing rows stay as user-scoped
UPDATE ai_infrastructure.user_platform_credentials
SET scope = 'user'
WHERE scope IS NULL;

COMMENT ON COLUMN ai_infrastructure.user_platform_credentials.scope IS
    'Scope of this credential: "user" = user-specific (OAuth tokens, personal API keys).
     Org-wide keys should now use organisation_platform_credentials table instead.';

-- ============================================================================
-- STEP 6: HELPER POSTGRESQL FUNCTIONS
-- ============================================================================

-- Function: get_role_level
-- Returns numeric hierarchy level for a role name.
-- Higher = more privileged.
CREATE OR REPLACE FUNCTION ai_infrastructure.get_role_level(role_name TEXT)
RETURNS INTEGER AS $$
BEGIN
    RETURN CASE role_name
        WHEN 'viewer'  THEN 1
        WHEN 'member'  THEN 2
        WHEN 'manager' THEN 3
        WHEN 'admin'   THEN 4
        WHEN 'owner'   THEN 5
        ELSE 0
    END;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION ai_infrastructure.get_role_level(TEXT) IS
    'Returns numeric hierarchy value for org_role. viewer=1, member=2, manager=3, admin=4, owner=5.';


-- Function: user_can_list_credential
-- Returns TRUE if the user's role >= the credential's visible_to_role
CREATE OR REPLACE FUNCTION ai_infrastructure.user_can_list_credential(
    p_user_id        INTEGER,
    p_credential_id  INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    v_user_role         TEXT;
    v_visible_to_role   TEXT;
BEGIN
    -- Get user's org role
    SELECT u.org_role INTO v_user_role
    FROM ai_infrastructure.users u
    JOIN ai_infrastructure.organisation_platform_credentials c ON c.organisation_id = u.organisation_id
    WHERE u.id = p_user_id AND c.id = p_credential_id;

    IF v_user_role IS NULL THEN
        RETURN FALSE;  -- User not in same org
    END IF;

    -- Get credential's visibility requirement
    SELECT visible_to_role INTO v_visible_to_role
    FROM ai_infrastructure.organisation_platform_credentials
    WHERE id = p_credential_id;

    RETURN ai_infrastructure.get_role_level(v_user_role) >= ai_infrastructure.get_role_level(v_visible_to_role);
END;
$$ LANGUAGE plpgsql STABLE;


-- Function: user_can_reveal_credential
-- Returns TRUE if user's role >= reveal_requires_role for the credential
CREATE OR REPLACE FUNCTION ai_infrastructure.user_can_reveal_credential(
    p_user_id        INTEGER,
    p_credential_id  INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    v_user_role           TEXT;
    v_reveal_requires_role TEXT;
BEGIN
    SELECT u.org_role INTO v_user_role
    FROM ai_infrastructure.users u
    JOIN ai_infrastructure.organisation_platform_credentials c ON c.organisation_id = u.organisation_id
    WHERE u.id = p_user_id AND c.id = p_credential_id;

    IF v_user_role IS NULL THEN
        RETURN FALSE;
    END IF;

    SELECT reveal_requires_role INTO v_reveal_requires_role
    FROM ai_infrastructure.organisation_platform_credentials
    WHERE id = p_credential_id;

    RETURN ai_infrastructure.get_role_level(v_user_role) >= ai_infrastructure.get_role_level(v_reveal_requires_role);
END;
$$ LANGUAGE plpgsql STABLE;


-- Function: mask_credential
-- Returns a masked version of a credential value for safe display.
-- e.g. "sk-ant-api03-AbCdEfGh..." → "sk-ant-api03-****...****AbCd"
CREATE OR REPLACE FUNCTION ai_infrastructure.mask_credential(plain_value TEXT)
RETURNS TEXT AS $$
DECLARE
    len INTEGER;
BEGIN
    IF plain_value IS NULL OR LENGTH(plain_value) < 12 THEN
        RETURN '****';
    END IF;

    len := LENGTH(plain_value);

    -- Show first 12 chars + **** + last 4 chars
    RETURN SUBSTRING(plain_value FROM 1 FOR 12)
        || '****...****'
        || SUBSTRING(plain_value FROM len - 3 FOR 4);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION ai_infrastructure.mask_credential(TEXT) IS
    'Returns a masked version of an API key for safe display. Shows first 12 and last 4 characters.';


-- ============================================================================
-- STEP 7: ROW-LEVEL SECURITY ON NEW TABLE
-- ============================================================================

ALTER TABLE ai_infrastructure.organisation_platform_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_infrastructure.credential_access_log ENABLE ROW LEVEL SECURITY;

-- The RLS policies rely on the app.current_user_id and app.current_organisation_id
-- session variables being set by the application layer (org_manager.py / rls_session_manager.py)

-- Policy: Users can only list credentials from their own organisation
-- (reveals are handled entirely in the application layer with additional checks)
DROP POLICY IF EXISTS org_creds_same_org ON ai_infrastructure.organisation_platform_credentials;
CREATE POLICY org_creds_same_org
    ON ai_infrastructure.organisation_platform_credentials
    FOR SELECT
    USING (
        organisation_id = current_setting('app.current_organisation_id', true)::integer
    );

DROP POLICY IF EXISTS org_creds_write_own_org ON ai_infrastructure.organisation_platform_credentials;
CREATE POLICY org_creds_write_own_org
    ON ai_infrastructure.organisation_platform_credentials
    FOR ALL
    USING (
        organisation_id = current_setting('app.current_organisation_id', true)::integer
    )
    WITH CHECK (
        organisation_id = current_setting('app.current_organisation_id', true)::integer
    );

-- Policy: Audit log visible only within own org
DROP POLICY IF EXISTS cred_log_same_org ON ai_infrastructure.credential_access_log;
CREATE POLICY cred_log_same_org
    ON ai_infrastructure.credential_access_log
    FOR SELECT
    USING (
        organisation_id = current_setting('app.current_organisation_id', true)::integer
    );


-- ============================================================================
-- STEP 8: SEED DATA — DEFAULT ORGANISATIONS FOR EXISTING USERS
-- ============================================================================

-- Create a default "Platform" org for any existing users that have no org
-- (so legacy single-user setups don't break)
INSERT INTO ai_infrastructure.organisations (name, slug, plan_tier, display_name)
VALUES ('Platform', 'platform', 'enterprise', 'Platform Administration')
ON CONFLICT (slug) DO NOTHING;

-- Link user_id=1 (admin/platform user) to the Platform org as owner
UPDATE ai_infrastructure.users
SET organisation_id = (
        SELECT id FROM ai_infrastructure.organisations WHERE slug = 'platform'
    ),
    org_role = 'owner'
WHERE id = 1
  AND organisation_id IS NULL;


-- ============================================================================
-- VERIFICATION QUERIES (run to confirm migration succeeded)
-- ============================================================================

-- SELECT * FROM ai_infrastructure.organisations;
-- SELECT id, username, email, organisation_id, org_role FROM ai_infrastructure.users;
-- SELECT column_name, data_type FROM information_schema.columns
--   WHERE table_schema='ai_infrastructure' AND table_name='organisation_platform_credentials';
-- SELECT ai_infrastructure.get_role_level('owner');   -- should return 5
-- SELECT ai_infrastructure.mask_credential('sk-ant-api03-AbCdEfGhIjKlMnOp');

-- ============================================================================
-- DONE
-- ============================================================================
