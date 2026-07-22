-- ============================================================================
-- Migration 058: viz snapshot notes (human + AI handoff)
-- Created: 2026-07-22
-- Purpose: Free-form notes on a viz snapshot. Authored by humans OR by AI
--          agents to hand off context to other AI agents in future sessions.
--          Four note kinds: 'comment', 'todo', 'handoff', 'data_update'.
-- Idempotent: yes.
-- ============================================================================

CREATE TABLE IF NOT EXISTS sessions.viz_snapshot_notes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id       UUID NOT NULL REFERENCES sessions.viz_snapshots(id) ON DELETE CASCADE,
    author_user_id    INTEGER NOT NULL,
    author_kind       TEXT NOT NULL DEFAULT 'human',
    author_agent_id   TEXT,
    note              TEXT NOT NULL,
    note_kind         TEXT NOT NULL DEFAULT 'comment',
    metadata          JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT viz_snapshot_notes_kind_chk
        CHECK (author_kind IN ('human', 'ai')),
    CONSTRAINT viz_snapshot_notes_note_kind_chk
        CHECK (note_kind IN ('comment', 'todo', 'handoff', 'data_update'))
);

CREATE INDEX IF NOT EXISTS idx_viz_snapshot_notes_snap
    ON sessions.viz_snapshot_notes (snapshot_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_snapshot_notes_author
    ON sessions.viz_snapshot_notes (author_user_id, created_at DESC);

ALTER TABLE sessions.viz_snapshot_notes ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS viz_snapshot_notes_rls ON sessions.viz_snapshot_notes;
CREATE POLICY viz_snapshot_notes_rls ON sessions.viz_snapshot_notes
    USING (EXISTS (
        SELECT 1 FROM sessions.viz_snapshots v
        WHERE v.id = snapshot_id
          AND v.org_id = current_setting('app.org_id', true)::int))
    WITH CHECK (EXISTS (
        SELECT 1 FROM sessions.viz_snapshots v
        WHERE v.id = snapshot_id
          AND v.org_id = current_setting('app.org_id', true)::int));

DO $$
BEGIN
    RAISE NOTICE 'Migration 058 complete: viz_snapshot_notes (human + AI handoff) with RLS';
END $$;