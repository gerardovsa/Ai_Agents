-- =============================================================================
-- Migration 040: Fix infinite recursion in session_members RLS policies
-- =============================================================================
-- PROBLEM (double recursion identified April 8, 2026):
--
-- Cycle A:
--   SELECT synergy_sessions → synergy_sessions_select USING
--   → queries session_members (visibility='shared' check)
--   → session_members_write (FOR ALL) USING evaluated
--   → queries synergy_sessions → synergy_sessions_select → ♾️
--
-- Cycle B (inside session_members_write itself):
--   session_members_write USING queries session_members sm (role='admin' check)
--   → session_members_write USING evaluated again → ♾️
--
-- FIX:
--   1. session_members_select: direct user_id check (no subquery).
--      Applied April 3 — correct, stays.
--
--   2. session_members_write: replaced with SECURITY DEFINER function.
--      The function runs as postgres (superuser) which bypasses RLS entirely,
--      so it can safely query both synergy_sessions and session_members without
--      triggering any RLS policy evaluation → no recursion possible.
--      Applied April 8 — this is the key fix.
--
-- IDEMPOTENT: Yes — uses CREATE OR REPLACE FUNCTION + DROP POLICY IF EXISTS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- PART 1: session_members_select (SELECT only)
-- Direct user_id check — zero recursion.
-- Applied April 3, confirmed still correct.
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS session_members_select ON synergy_sessions.session_members;

CREATE POLICY session_members_select
    ON synergy_sessions.session_members
    FOR SELECT
    USING (
        user_id = current_setting('app.current_user_id', true)::integer
    );

-- ---------------------------------------------------------------------------
-- PART 2: SECURITY DEFINER helper function
-- Runs as postgres (superuser) → bypasses RLS on all tables → no recursion.
-- Checks whether the current app user owns the session OR is an admin member.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION synergy_sessions.current_user_can_manage_session(p_session_id text)
RETURNS boolean
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
AS $$
DECLARE
    v_result boolean;
BEGIN
    -- Executes as postgres (superuser) — RLS is bypassed here, no recursion risk
    SELECT EXISTS (
        SELECT 1
        FROM synergy_sessions.synergy_sessions s
        WHERE s.session_id = p_session_id
          AND (
              s.owner_user_id = current_setting('app.current_user_id', true)::integer
              OR EXISTS (
                  SELECT 1
                  FROM synergy_sessions.session_members sm
                  WHERE sm.session_id = s.session_id
                    AND sm.user_id = current_setting('app.current_user_id', true)::integer
                    AND sm.role = 'admin'
              )
          )
    ) INTO v_result;

    RETURN COALESCE(v_result, false);
EXCEPTION WHEN OTHERS THEN
    RETURN false;
END;
$$;

-- ---------------------------------------------------------------------------
-- PART 3: session_members_write (FOR ALL)
-- Uses the SECURITY DEFINER function — zero recursion.
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS session_members_write ON synergy_sessions.session_members;

CREATE POLICY session_members_write
    ON synergy_sessions.session_members
    FOR ALL
    USING (synergy_sessions.current_user_can_manage_session(session_id))
    WITH CHECK (synergy_sessions.current_user_can_manage_session(session_id));
