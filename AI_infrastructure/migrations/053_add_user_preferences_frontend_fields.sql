-- ============================================================================
-- Migration 053: Add user_preferences columns the frontend has been silently
--                dropping
-- Created: June 15, 2026
-- Purpose: The account profile UI has 5 fields whose values are written by
--          the frontend (via _collectSettingsFromUI / UI_TO_BACKEND_KEY) but
--          for which the user_preferences table has no column. Result: every
--          POST silently loses the value at the backend, and every GET never
--          returns the value to the UI. The user sees the value in local
--          for a moment, then it's gone on reload.
--
--          The 5 columns:
--            1. theme                  — 'dark' | 'light' | 'auto' (Appearance modal)
--            2. enable_notifications   — 0 | 1 (Notifications modal)
--            3. enable_sounds          — 0 | 1 (Notifications modal)
--            4. max_rounds             — int (Round Parameters section, agent loop)
--            5. round_timeout          — int (seconds; Round Parameters section)
--
--          The frontend was already sending these in the POST body; the
--          backend just wasn't storing them. After this migration the
--          POST→DB→GET→UI round-trip is complete and the values survive
--          reload.
--
--          The /api/auth/preferences handler (auth_routes.py:1574) whitelists
--          fields by name, so it also needs to be updated to allow these
--          new columns — see the auth_routes.py change in this same commit.
--
-- Idempotent: ADD COLUMN IF NOT EXISTS for every column. Safe to re-run.
-- ============================================================================

ALTER TABLE ai_infrastructure.user_preferences
    ADD COLUMN IF NOT EXISTS theme                VARCHAR(20)  DEFAULT 'dark',
    ADD COLUMN IF NOT EXISTS enable_notifications INTEGER     DEFAULT 1,
    ADD COLUMN IF NOT EXISTS enable_sounds        INTEGER     DEFAULT 1,
    ADD COLUMN IF NOT EXISTS max_rounds           INTEGER     DEFAULT 20,
    ADD COLUMN IF NOT EXISTS round_timeout        INTEGER     DEFAULT 30;

-- Column comments — keep the schema self-documenting
COMMENT ON COLUMN ai_infrastructure.user_preferences.theme IS
    'UI theme: dark | light | auto (default: dark)';
COMMENT ON COLUMN ai_infrastructure.user_preferences.enable_notifications IS
    '1 = show toast notifications in the UI, 0 = silent (default: 1)';
COMMENT ON COLUMN ai_infrastructure.user_preferences.enable_sounds IS
    '1 = play UI sounds, 0 = muted (default: 1)';
COMMENT ON COLUMN ai_infrastructure.user_preferences.max_rounds IS
    'Maximum tool-calling rounds per agent turn (default: 20)';
COMMENT ON COLUMN ai_infrastructure.user_preferences.round_timeout IS
    'Per-round timeout in seconds (default: 30)';

-- ============================================================================
-- Verify
-- ============================================================================
DO $$
DECLARE
    missing_count INTEGER := 0;
    col_list TEXT;
BEGIN
    SELECT string_agg(column_name, ', ' ORDER BY column_name)
    INTO   col_list
    FROM   information_schema.columns
    WHERE  table_schema = 'ai_infrastructure'
      AND  table_name   = 'user_preferences'
      AND  column_name IN ('theme', 'enable_notifications', 'enable_sounds', 'max_rounds', 'round_timeout');

    IF col_list IS NULL THEN
        RAISE WARNING '[Migration 053] ❌ None of the 5 new columns were added';
    ELSE
        SELECT 5 - array_length(string_to_array(col_list, ', '), 1)
        INTO   missing_count;
        IF missing_count = 0 THEN
            RAISE NOTICE '[Migration 053] ✅ All 5 columns present: %', col_list;
        ELSE
            RAISE WARNING '[Migration 053] ⚠️  % column(s) missing (have: %)', missing_count, col_list;
        END IF;
    END IF;
END $$;
