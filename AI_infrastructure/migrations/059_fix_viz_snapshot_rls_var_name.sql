-- ============================================================================
-- Migration 059: Fix viz snapshot RLS session-variable name
-- Created: 2026-07-22
-- Purpose: Migration 057/058 referenced current_setting('app.org_id', true) but
--          the session variable set by rls_session_manager.py is
--          'app.current_organisation_id'. With the wrong variable name the RLS
--          policies silently return NULL and deny every row (org_id = NULL is
--          never true). Recreate the policies against the correct var.
--          Idempotent: yes (DROP POLICY IF EXISTS then CREATE).
-- ============================================================================

DROP POLICY IF EXISTS viz_snapshots_rls ON sessions.viz_snapshots;
CREATE POLICY viz_snapshots_rls ON sessions.viz_snapshots
    USING (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int)
    WITH CHECK (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int);

DROP POLICY IF EXISTS viz_snapshot_notes_rls ON sessions.viz_snapshot_notes;
CREATE POLICY viz_snapshot_notes_rls ON sessions.viz_snapshot_notes
    USING (EXISTS (
        SELECT 1 FROM sessions.viz_snapshots v
        WHERE v.id = snapshot_id
          AND v.org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int))
    WITH CHECK (EXISTS (
        SELECT 1 FROM sessions.viz_snapshots v
        WHERE v.id = snapshot_id
          AND v.org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int));

DO $$
BEGIN
    RAISE NOTICE 'Migration 059 complete: viz_snapshots + viz_snapshot_notes RLS now use app.current_organisation_id';
END $$;