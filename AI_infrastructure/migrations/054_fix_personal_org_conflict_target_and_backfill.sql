-- ============================================================================
-- Migration 054: Fix Personal-Org Conflict Target and Complete Backfill
-- Created: 2026-07-20
-- Purpose: Repair migration 046's create_personal_org() helper, which used
--          ON CONFLICT (name) even though organisations is unique on slug.
--          Replace the helper without changing its public signature, then
--          backfill eligible solo users atomically and fail loudly on errors.
-- Depends on: Migration 046
-- Idempotent: Yes -- CREATE OR REPLACE, guarded assignment, and conflict-safe
--             module grants make this migration safe to rerun.
-- ============================================================================

-- ============================================================================
-- 1. Replace the helper while preserving the register_user() call contract
-- ============================================================================
CREATE OR REPLACE FUNCTION ai_infrastructure.create_personal_org(
    p_user_id      INT,
    p_username     TEXT,
    p_display_name TEXT DEFAULT NULL
) RETURNS INT
LANGUAGE plpgsql AS $$
DECLARE
    v_existing_org_id  INT;
    v_org_id           INT;
    v_linked_org_id    INT;
    v_conflicting_id   INT;
    v_org_name         TEXT;
    v_slug             TEXT;
    v_display_name     TEXT;
BEGIN
    -- Serialize concurrent calls for the same user and preserve any existing
    -- organisation assignment. This also makes repeated calls idempotent.
    SELECT organisation_id
    INTO v_existing_org_id
    FROM ai_infrastructure.users
    WHERE id = p_user_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION '[054] Cannot create personal org: user % does not exist',
            p_user_id;
    END IF;

    IF v_existing_org_id IS NOT NULL THEN
        RETURN v_existing_org_id;
    END IF;

    IF p_username IS NULL OR BTRIM(p_username) = '' THEN
        RAISE EXCEPTION '[054] Cannot create personal org for user %: username is empty',
            p_user_id;
    END IF;

    v_org_name     := 'personal_' || p_username || '_' || p_user_id::TEXT;
    v_slug         := 'personal-' || p_user_id::TEXT;
    v_display_name := COALESCE(NULLIF(BTRIM(p_display_name), ''),
                               p_username || '''s Workspace');

    -- organisations.slug is unique; organisations.name is not. Recover an
    -- existing row only when it is the exact personal org expected for this
    -- user. A team/non-personal slug collision must never be adopted.
    INSERT INTO ai_infrastructure.organisations AS existing_org
        (name, slug, display_name, plan_tier, is_personal_org, is_active)
    VALUES
        (v_org_name, v_slug, v_display_name, 'free', TRUE, TRUE)
    ON CONFLICT (slug) DO UPDATE SET
        is_personal_org = TRUE,
        is_active       = TRUE
    WHERE existing_org.name = EXCLUDED.name
      AND existing_org.is_personal_org IS TRUE
    RETURNING existing_org.id INTO v_org_id;

    IF v_org_id IS NULL THEN
        SELECT id
        INTO v_conflicting_id
        FROM ai_infrastructure.organisations
        WHERE slug = v_slug;

        RAISE EXCEPTION
            '[054] Cannot create personal org for user %: slug % belongs to organisation %',
            p_user_id, v_slug, v_conflicting_id;
    END IF;

    UPDATE ai_infrastructure.users
    SET organisation_id = v_org_id,
        org_role        = 'owner'
    WHERE id = p_user_id
      AND organisation_id IS NULL
    RETURNING organisation_id INTO v_linked_org_id;

    IF v_linked_org_id IS NULL OR v_linked_org_id <> v_org_id THEN
        RAISE EXCEPTION
            '[054] Failed to link user % to personal organisation %',
            p_user_id, v_org_id;
    END IF;

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
    'Creates and links a single-user personal workspace using the unique slug. '
    'Idempotent for assigned users and exact personal-org recovery; rejects '
    'non-personal slug collisions.';

-- ============================================================================
-- 2. Backfill every eligible solo user as one atomic statement
--    Intentionally no per-user exception handler: any error aborts the whole
--    DO block instead of silently committing a partial backfill.
-- ============================================================================
DO $$
DECLARE
    r                  RECORD;
    v_target_count     INT := 0;
    v_processed_count  INT := 0;
    v_remaining_count  INT := 0;
BEGIN
    SELECT COUNT(*)
    INTO v_target_count
    FROM ai_infrastructure.users
    WHERE organisation_id IS NULL
      AND (is_sub_user IS NULL OR is_sub_user = FALSE);

    FOR r IN
        SELECT id, username
        FROM ai_infrastructure.users
        WHERE organisation_id IS NULL
          AND (is_sub_user IS NULL OR is_sub_user = FALSE)
        ORDER BY id
    LOOP
        PERFORM ai_infrastructure.create_personal_org(r.id, r.username, NULL);
        v_processed_count := v_processed_count + 1;
    END LOOP;

    SELECT COUNT(*)
    INTO v_remaining_count
    FROM ai_infrastructure.users
    WHERE organisation_id IS NULL
      AND (is_sub_user IS NULL OR is_sub_user = FALSE);

    IF v_remaining_count > 0 THEN
        RAISE EXCEPTION
            '[054] Backfill incomplete: % eligible user(s) still have no organisation',
            v_remaining_count;
    END IF;

    RAISE NOTICE
        '[054] Personal-org backfill complete: % target(s), % processed, % remaining',
        v_target_count, v_processed_count, v_remaining_count;
END;
$$;

-- ============================================================================
-- 3. Fail-loud verification
-- ============================================================================
DO $$
DECLARE
    v_has_personal_column  BOOLEAN;
    v_has_synergy_column   BOOLEAN;
    v_has_helper           BOOLEAN;
    v_helper_uses_slug     BOOLEAN;
    v_remaining_users      INT;
    v_personal_orgs        INT;
    v_core_module_rows     INT;
BEGIN
    SELECT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name = 'organisations'
          AND column_name = 'is_personal_org'
    ) INTO v_has_personal_column;

    SELECT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'synergy_sessions'
          AND table_name = 'synergy_sessions'
          AND column_name = 'default_member_role'
    ) INTO v_has_synergy_column;

    SELECT EXISTS (
        SELECT 1
        FROM pg_proc p
        JOIN pg_namespace n ON n.oid = p.pronamespace
        WHERE n.nspname = 'ai_infrastructure'
          AND p.proname = 'create_personal_org'
    ) INTO v_has_helper;

    SELECT COALESCE(BOOL_OR(
        pg_get_functiondef(p.oid) LIKE '%ON CONFLICT (slug)%'
    ), FALSE)
    INTO v_helper_uses_slug
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'ai_infrastructure'
      AND p.proname = 'create_personal_org';

    SELECT COUNT(*)
    INTO v_remaining_users
    FROM ai_infrastructure.users
    WHERE organisation_id IS NULL
      AND (is_sub_user IS NULL OR is_sub_user = FALSE);

    SELECT COUNT(*)
    INTO v_personal_orgs
    FROM ai_infrastructure.organisations
    WHERE is_personal_org IS TRUE;

    SELECT COUNT(*)
    INTO v_core_module_rows
    FROM ai_infrastructure.org_module_access oma
    JOIN ai_infrastructure.organisations o
      ON o.id = oma.organisation_id
    WHERE o.is_personal_org IS TRUE
      AND oma.is_enabled IS TRUE
      AND oma.module_name IN (
          'core_chat',
          'documents',
          'prompt_library',
          'notifications',
          'synergy'
      );

    IF NOT v_has_personal_column THEN
        RAISE EXCEPTION '[054] Verification failed: is_personal_org is missing';
    END IF;

    IF NOT v_has_synergy_column THEN
        RAISE EXCEPTION '[054] Verification failed: default_member_role is missing';
    END IF;

    IF NOT v_has_helper OR NOT v_helper_uses_slug THEN
        RAISE EXCEPTION '[054] Verification failed: corrected helper is missing';
    END IF;

    IF v_remaining_users > 0 THEN
        RAISE EXCEPTION
            '[054] Verification failed: % eligible user(s) remain unassigned',
            v_remaining_users;
    END IF;

    RAISE NOTICE '========================================';
    RAISE NOTICE 'Migration 054 Verification:';
    RAISE NOTICE '  Corrected helper uses unique slug : %', v_helper_uses_slug;
    RAISE NOTICE '  Eligible users without org        : %', v_remaining_users;
    RAISE NOTICE '  Personal organisations            : %', v_personal_orgs;
    RAISE NOTICE '  Enabled core-module rows          : %', v_core_module_rows;
    RAISE NOTICE '========================================';
END;
$$;
