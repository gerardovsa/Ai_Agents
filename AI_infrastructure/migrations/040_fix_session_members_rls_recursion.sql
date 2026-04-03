-- =============================================================================
-- Migration 040: Fix infinite recursion in session_members RLS policies
-- =============================================================================
-- PROBLEM:
--   `session_members_select` policy queries `synergy_sessions` table.
--   `synergy_sessions_select` policy queries `session_members` table (for 'shared' visibility).
--   This creates a mutual dependency → "infinite recursion detected in policy for
--   relation session_members" → 500 error on every Synergy board load.
--
-- FIX:
--   Rewrite `session_members_select` to ONLY check user_id directly — no subquery
--   to synergy_sessions. A user may only see their own membership records.
--   This is sufficient for the synergy_sessions_select visibility check to work:
--   the EXISTS clause just needs to know if the current user IS a member, which
--   is correctly satisfied by returning only that user's own row.
--
--   `session_members_write` already only uses synergy_sessions.owner_user_id for
--   its primary check (not causing additional recursion once select is fixed).
--
-- IDEMPOTENT: Yes — uses DROP POLICY IF EXISTS before CREATE POLICY
-- CREATED: April 3, 2026
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Drop and recreate the SELECT policy on session_members
-- OLD: EXISTS (SELECT 1 FROM synergy_sessions.synergy_sessions s WHERE ...)
--      → triggers synergy_sessions_select → triggers session_members_select → ♾️
-- NEW: user_id = current_user_id (direct check, zero recursion)
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS session_members_select ON synergy_sessions.session_members;

CREATE POLICY session_members_select
    ON synergy_sessions.session_members
    FOR SELECT
    USING (
        -- A user may only read their own membership record.
        -- This breaks the mutual recursion with synergy_sessions_select,
        -- while still satisfying the EXISTS check in that policy for 'shared' sessions.
        user_id = current_setting('app.current_user_id', true)::integer
    );

-- ---------------------------------------------------------------------------
-- Verify: the write policy (session_members_write) does not need changes.
--   Its inner session_members subquery (checking role='admin') now resolves
--   cleanly against the fixed select policy above.
-- ---------------------------------------------------------------------------
