-- ============================================================================
-- Migration 063: viz_data_sources + viz_data_refreshes (Data Source Map)
-- Created: 2026-07-28
-- Purpose: Tier A.3 of the REACT_ENHANCEMENT_TODO roadmap. Capture the tool-
--          call provenance chain that produced each saved viz_snapshot so a
--          chart can be replayed (refresh) or re-linked (re-capture). Adds
--          two tables:
--            * sessions.viz_data_sources  — one row per tool call that
--              contributed data to a snapshot (in invocation order).
--            * sessions.viz_data_refreshes — audit log of refresh attempts
--              and their outcome (snapshot_id, new_snapshot_id, status,
--              diff_summary_json).
--          Also adds viz_snapshots.previous_version_id (self-FK) so a refresh
--          can record its lineage back to the snapshot it cloned from.
--          Idempotent: yes (CREATE TABLE IF NOT EXISTS, ADD COLUMN IF NOT
--          EXISTS, CREATE INDEX IF NOT EXISTS, DROP POLICY IF EXISTS).
-- ============================================================================

-- ----------------------------------------------------------------------------
-- viz_snapshots.previous_version_id — self-FK so refreshes can chain back
-- ----------------------------------------------------------------------------
ALTER TABLE sessions.viz_snapshots
    ADD COLUMN IF NOT EXISTS previous_version_id UUID
    REFERENCES sessions.viz_snapshots(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_viz_snapshots_previous_version
    ON sessions.viz_snapshots(previous_version_id)
    WHERE previous_version_id IS NOT NULL;

-- ----------------------------------------------------------------------------
-- viz_data_sources — one row per tool call that produced data for a snapshot
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions.viz_data_sources (
    id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id      UUID        NOT NULL REFERENCES sessions.viz_snapshots(id) ON DELETE CASCADE,
    org_id           INTEGER     NOT NULL,
    sequence_index   INTEGER     NOT NULL,
    tool_name        TEXT        NOT NULL,
    tool_platform    TEXT        NOT NULL DEFAULT 'unknown',
    arguments_json   JSONB       NOT NULL DEFAULT '{}'::jsonb,
    result_summary   JSONB       NOT NULL DEFAULT '{}'::jsonb,
    result_sha256    TEXT,
    is_read_only     BOOLEAN     NOT NULL DEFAULT TRUE,
    status           TEXT        NOT NULL DEFAULT 'ok'
                               CHECK (status IN ('ok', 'partial', 'failed')),
    captured_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (snapshot_id, sequence_index)
);

CREATE INDEX IF NOT EXISTS idx_viz_data_sources_snapshot_seq
    ON sessions.viz_data_sources(snapshot_id, sequence_index);
CREATE INDEX IF NOT EXISTS idx_viz_data_sources_org_captured
    ON sessions.viz_data_sources(org_id, captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_data_sources_platform
    ON sessions.viz_data_sources(tool_platform, captured_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_data_sources_tool_status
    ON sessions.viz_data_sources(tool_name, status);

ALTER TABLE sessions.viz_data_sources ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS viz_data_sources_rls ON sessions.viz_data_sources;
CREATE POLICY viz_data_sources_rls ON sessions.viz_data_sources
    USING      (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int)
    WITH CHECK (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int);

-- ----------------------------------------------------------------------------
-- viz_data_refreshes — audit log of refresh attempts
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions.viz_data_refreshes (
    id                     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id            UUID        NOT NULL REFERENCES sessions.viz_snapshots(id) ON DELETE CASCADE,
    org_id                 INTEGER     NOT NULL,
    requested_by_user_id   INTEGER     NOT NULL,
    started_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at           TIMESTAMPTZ,
    status                 TEXT        NOT NULL DEFAULT 'in_progress'
                                    CHECK (status IN ('in_progress','succeeded','failed','partial')),
    error_message          TEXT,
    new_snapshot_id        UUID        REFERENCES sessions.viz_snapshots(id) ON DELETE SET NULL,
    diff_summary_json      JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_viz_data_refreshes_snapshot
    ON sessions.viz_data_refreshes(snapshot_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_data_refreshes_org_started
    ON sessions.viz_data_refreshes(org_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_data_refreshes_user_started
    ON sessions.viz_data_refreshes(requested_by_user_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_data_refreshes_status
    ON sessions.viz_data_refreshes(status, started_at DESC);

ALTER TABLE sessions.viz_data_refreshes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS viz_data_refreshes_rls ON sessions.viz_data_refreshes;
CREATE POLICY viz_data_refreshes_rls ON sessions.viz_data_refreshes
    USING      (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int)
    WITH CHECK (org_id = NULLIF(current_setting('app.current_organisation_id', true), '')::int);

-- ============================================================================
-- Verify block — confirm both new tables exist and are RLS-enabled.
-- ============================================================================
DO $$
DECLARE
    src_count INTEGER;
    ref_count INTEGER;
    prev_col_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO src_count
        FROM information_schema.tables
       WHERE table_schema = 'sessions' AND table_name = 'viz_data_sources';
    SELECT COUNT(*) INTO ref_count
        FROM information_schema.tables
       WHERE table_schema = 'sessions' AND table_name = 'viz_data_refreshes';
    SELECT COUNT(*) INTO prev_col_count
        FROM information_schema.columns
       WHERE table_schema = 'sessions'
         AND table_name   = 'viz_snapshots'
         AND column_name  = 'previous_version_id';

    IF src_count <> 1 OR ref_count <> 1 OR prev_col_count <> 1 THEN
        RAISE EXCEPTION 'Migration 063 verify failed: sources=%, refreshes=%, prev_col=%',
            src_count, ref_count, prev_col_count;
    END IF;

    RAISE NOTICE 'Migration 063 complete: viz_data_sources + viz_data_refreshes '
                '(snapshot.previous_version_id column added; RLS enforced)';
END $$;
