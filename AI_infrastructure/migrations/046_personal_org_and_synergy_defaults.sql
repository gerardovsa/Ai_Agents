-- ============================================================================
-- Migration 046: Personal Org + Synergy default_member_role
-- Date: May 6, 2026
--
-- CHANGES:
--   1. Add is_personal_org BOOLEAN to ai_infrastructure.organisations
--   2. Add default_member_role TEXT CHECK to synergy_sessions.synergy_sessions
--   3. Create helper function ai_infrastructure.create_personal_org()
--      — called by register_user() in user_auth.py for all new registrations
--   4. Backfill personal orgs for all existing users with organisation_id IS NULL
--   5. Auto-enable core modules for each personal org created in backfill
--
-- WHY:
--   Without this migration every solo user has organisation_id = NULL, meaning:
--   - g.rls_organisation_id = NULL in all Flask routes → no org-level isolation
--   - Credential resolution (org_credentials_loader.py) falls through to env vars
--     (Tier 3) instead of the user's own vault (Tier 2)
--   - initModulesFromOrg() never fires (guard checks profile.org_role != null)
--   - Synergy team visibility is meaningless for solo users but still shown in UI
--
-- IDEMPOTENT: Yes — all changes use IF NOT EXISTS / ON CONFLICT / DO NOTHING
-- ============================================================================

-- ============================================================================
-- 1. Add is_personal_org column to organisations
-- ============================================================================
ALTER TABLE ai_infrastructure.organisations
    ADD COLUMN IF NOT EXISTS is_personal_org BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN ai_infrastructure.organisations.is_personal_org IS
    'TRUE = auto-created single-user personal workspace. FALSE = team / enterprise org. '
    'Personal orgs hide team-sharing UI and org-invite features.';

-- ============================================================================
-- 2. Add default_member_role column to synergy_sessions
-- ============================================================================
ALTER TABLE synergy_sessions.synergy_sessions
    ADD COLUMN IF NOT EXISTS default_member_role TEXT DEFAULT 'editor'
        CHECK (default_member_role IN ('viewer', 'editor'));

COMMENT ON COLUMN synergy_sessions.synergy_sessions.default_member_role IS
    'Default access level for team members when visibility = ''team''. '
    '''viewer'' = read-only for team; ''editor'' = full edit for team (default).';

-- ============================================================================
-- 3. Helper function: create_personal_org(p_user_id, p_username, p_display_name)
--    Called by:
--      - This migration's backfill block (step 4)
--      - register_user() in AI_infrastructure/auth/user_auth.py after INSERT INTO users
--
--    Behaviour:
--      - If user already has organisation_id → returns existing org id (idempotent)
--      - Creates new org with is_personal_org = TRUE and plan_tier = 'free'
--      - Sets user.organisation_id + user.org_role = 'owner'
--      - Enables core modules in org_module_access for the new org
-- ============================================================================
CREATE OR REPLACE FUNCTION ai_infrastructure.create_personal_org(
    p_user_id      INT,
    p_username     TEXT,
    p_display_name TEXT DEFAULT NULL
) RETURNS INT
LANGUAGE plpgsql AS $$
DECLARE
    v_org_id       INT;
    v_org_name     TEXT;
    v_slug         TEXT;
    v_display_name TEXT;
BEGIN
    -- Check if user already has an organisation
    SELECT organisation_id INTO v_org_id
    FROM ai_infrastructure.users
    WHERE id = p_user_id;

    IF v_org_id IS NOT NULL THEN
        -- Already assigned — idempotent, nothing to do
        RETURN v_org_id;
    END IF;

    -- Build unique org identifiers
    v_org_name     := 'personal_' || p_username || '_' || p_user_id::TEXT;
    v_slug         := 'personal-' || p_user_id::TEXT;
    v_display_name := COALESCE(p_display_name, p_username || '''s Workspace');

    -- Create the personal org (ON CONFLICT handles duplicate name edge cases)
    INSERT INTO ai_infrastructure.organisations
        (name, slug, display_name, plan_tier, is_personal_org, is_active)
    VALUES
        (v_org_name, v_slug, v_display_name, 'free', TRUE, TRUE)
    ON CONFLICT (name) DO UPDATE SET
        is_personal_org = TRUE,
        is_active       = TRUE
    RETURNING id INTO v_org_id;

    -- Link user to their personal org as owner
    UPDATE ai_infrastructure.users
    SET organisation_id = v_org_id,
        org_role        = 'owner'
    WHERE id = p_user_id
      AND organisation_id IS NULL;   -- Safety: never overwrite an existing assignment

    -- Enable default modules for the personal org
    -- These are the modules personal-org users should have access to out of the box.
    -- 'synergy' is included so the Synergy sidebar button shows immediately.
    INSERT INTO ai_infrastructure.org_module_access
        (organisation_id, module_name, is_enabled, enabled_at, enabled_by)
    SELECT
        v_org_id,
        module_name,
        TRUE,
        NOW(),
        p_user_id
    FROM ai_infrastructure.module_catalog
    WHERE module_name IN (
        'core_chat',
        'documents',
        'prompt_library',
        'notifications',
        'synergy'
    )
    ON CONFLICT (organisation_id, module_name) DO NOTHING;

    RETURN v_org_id;
END;
$$;

COMMENT ON FUNCTION ai_infrastructure.create_personal_org(INT, TEXT, TEXT) IS
    'Creates a personal org for a solo user and links them as owner. '
    'Idempotent — safe to call multiple times for the same user. '
    'Also called from register_user() in user_auth.py.';

-- ============================================================================
-- 4. Backfill personal orgs for all existing solo users
--    Targets: users where organisation_id IS NULL and is_sub_user IS NOT TRUE
--    Sub-users (is_sub_user = TRUE) inherit from their parent user — skip them
-- ============================================================================
DO $$
DECLARE
    r           RECORD;
    v_created   INT := 0;
    v_skipped   INT := 0;
BEGIN
    FOR r IN
        SELECT id, username, email
        FROM ai_infrastructure.users
        WHERE organisation_id IS NULL
          AND (is_sub_user IS NULL OR is_sub_user = FALSE)
        ORDER BY id
    LOOP
        BEGIN
            PERFORM ai_infrastructure.create_personal_org(r.id, r.username, NULL);
            v_created := v_created + 1;
            RAISE NOTICE '[046] Created personal org for user % (%)', r.id, r.username;
        EXCEPTION WHEN OTHERS THEN
            v_skipped := v_skipped + 1;
            RAISE WARNING '[046] Skipped user % (%): %', r.id, r.username, SQLERRM;
        END;
    END LOOP;

    RAISE NOTICE '[046] Backfill complete — orgs created: %, skipped/errors: %',
        v_created, v_skipped;
END;
$$;

-- ============================================================================
-- 5. Verification block
-- ============================================================================
DO $$
DECLARE
    v_has_is_personal_org   BOOLEAN;
    v_has_default_role      BOOLEAN;
    v_fn_exists             BOOLEAN;
    v_users_without_org     INT;
    v_personal_orgs         INT;
BEGIN
    -- Check column exists on organisations
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'organisations'
          AND column_name  = 'is_personal_org'
    ) INTO v_has_is_personal_org;

    -- Check column exists on synergy_sessions
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'synergy_sessions'
          AND table_name   = 'synergy_sessions'
          AND column_name  = 'default_member_role'
    ) INTO v_has_default_role;

    -- Check function exists
    SELECT EXISTS (
        SELECT 1 FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = 'ai_infrastructure'
          AND p.proname = 'create_personal_org'
    ) INTO v_fn_exists;

    -- Check no solo users remain without an org
    SELECT COUNT(*) INTO v_users_without_org
    FROM ai_infrastructure.users
    WHERE organisation_id IS NULL
      AND (is_sub_user IS NULL OR is_sub_user = FALSE);

    -- Count personal orgs created
    SELECT COUNT(*) INTO v_personal_orgs
    FROM ai_infrastructure.organisations
    WHERE is_personal_org = TRUE;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration 046 Verification:';
    RAISE NOTICE '  is_personal_org column on organisations : %', v_has_is_personal_org;
    RAISE NOTICE '  default_member_role column on sessions  : %', v_has_default_role;
    RAISE NOTICE '  create_personal_org() function exists   : %', v_fn_exists;
    RAISE NOTICE '  Solo users still without an org         : %', v_users_without_org;
    RAISE NOTICE '  Total personal orgs in DB               : %', v_personal_orgs;
    RAISE NOTICE '========================================';

    IF v_users_without_org > 0 THEN
        RAISE WARNING '[046] % solo user(s) still have organisation_id = NULL — check logs above',
            v_users_without_org;
    END IF;
END;
$$;
