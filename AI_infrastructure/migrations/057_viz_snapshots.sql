-- ============================================================================
-- Migration 057: viz snapshots library + Synergy link column + module catalog seed
-- Created: 2026-07-22
-- Purpose: Persist AI-rendered React visualizations. Expose them as a
--          'Visualizations' sidebar module (starter plan). Allow linking into
--          Synergy Kanban sessions (both sides).
-- Idempotent: yes (CREATE TABLE IF NOT EXISTS, ADD COLUMN IF NOT EXISTS,
--             CREATE INDEX IF NOT EXISTS, ON CONFLICT DO NOTHING, DO $$ guards).
-- ============================================================================

CREATE TABLE IF NOT EXISTS sessions.viz_snapshots (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id                INTEGER NOT NULL,
    owner_user_id         INTEGER NOT NULL,
    thread_id             INTEGER REFERENCES sessions.threads(id) ON DELETE SET NULL,
    assistant_message_id  INTEGER REFERENCES sessions.messages(id) ON DELETE SET NULL,
    title                 TEXT NOT NULL,
    viz_type              TEXT NOT NULL DEFAULT 'react',
    jsx_source            TEXT NOT NULL,
    css_source            TEXT,
    uses_lucide           BOOLEAN NOT NULL DEFAULT FALSE,
    uses_recharts         BOOLEAN NOT NULL DEFAULT FALSE,
    uses_tailwind         BOOLEAN NOT NULL DEFAULT FALSE,
    tags                  TEXT[] NOT NULL DEFAULT '{}',
    is_public             BOOLEAN NOT NULL DEFAULT FALSE,
    share_token           TEXT UNIQUE DEFAULT encode(gen_random_bytes(16), 'hex'),
    synergy_session_id    TEXT REFERENCES synergy_sessions.synergy_sessions(session_id) ON DELETE SET NULL,
    thumbnail_png         BYTEA,
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    last_rendered_at      TIMESTAMPTZ,
    render_count          INTEGER NOT NULL DEFAULT 0,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_viz_snapshots_owner
    ON sessions.viz_snapshots (owner_user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_snapshots_org
    ON sessions.viz_snapshots (org_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_viz_snapshots_tags_gin
    ON sessions.viz_snapshots USING GIN (tags);
CREATE INDEX IF NOT EXISTS idx_viz_snapshots_synergy
    ON sessions.viz_snapshots (synergy_session_id)
    WHERE synergy_session_id IS NOT NULL;

ALTER TABLE sessions.viz_snapshots ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS viz_snapshots_rls ON sessions.viz_snapshots;
CREATE POLICY viz_snapshots_rls ON sessions.viz_snapshots
    USING (org_id = current_setting('app.org_id', true)::int)
    WITH CHECK (org_id = current_setting('app.org_id', true)::int);

-- Synergy: per-row JSON list of linked viz snapshots
ALTER TABLE synergy_sessions.synergy_sessions
    ADD COLUMN IF NOT EXISTS linked_viz_snapshots TEXT NOT NULL DEFAULT '[]';

-- Module catalog seed: makes the new sidebar entry auto-available
-- (org_module_access.module_name is FK-constrained to module_catalog,
--  so inserting here is enough — no org-side migration needed.)
INSERT INTO ai_infrastructure.module_catalog
    (module_name, display_name, description, icon_class, icon_color, category,
     min_plan_tier, required_platforms, sort_order)
VALUES
    ('visualizations', 'Visualizations',
     'Save, browse, and re-render AI-built React dashboards and charts.',
     'fas fa-chart-area', '#58a6ff', 'productivity', 'starter', '{}', 25)
ON CONFLICT (module_name) DO NOTHING;

-- Atomic link helper for the route layer's transactional link/unlink.
-- Avoids the read-modify-write race when two viz snapshots are linked at once.
CREATE OR REPLACE FUNCTION sessions.link_viz_to_synergy(p_snapshot_id UUID, p_synergy_session_id TEXT)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_linked JSONB;
BEGIN
    UPDATE sessions.viz_snapshots
       SET synergy_session_id = p_synergy_session_id,
           updated_at = NOW()
     WHERE id = p_snapshot_id;

    SELECT COALESCE(linked_viz_snapshots::jsonb, '[]'::jsonb)
      INTO v_linked
      FROM synergy_sessions.synergy_sessions
     WHERE session_id = p_synergy_session_id;

    v_linked := v_linked || jsonb_build_array(jsonb_build_object('snapshot_id', p_snapshot_id, 'linked_at', NOW()));

    UPDATE synergy_sessions.synergy_sessions
       SET linked_viz_snapshots = v_linked::text,
           updated_at = NOW()
     WHERE session_id = p_synergy_session_id;

    RETURN jsonb_build_object('success', TRUE, 'snapshot_id', p_snapshot_id, 'synergy_session_id', p_synergy_session_id);
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object('success', FALSE, 'error', SQLERRM);
END;
$$;

CREATE OR REPLACE FUNCTION sessions.unlink_viz_from_synergy(p_snapshot_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_synergy_id TEXT;
    v_linked     JSONB;
BEGIN
    SELECT synergy_session_id INTO v_synergy_id
      FROM sessions.viz_snapshots
     WHERE id = p_snapshot_id;

    IF v_synergy_id IS NULL THEN
        RETURN jsonb_build_object('success', TRUE, 'note', 'already_unlinked');
    END IF;

    UPDATE sessions.viz_snapshots
       SET synergy_session_id = NULL,
           updated_at = NOW()
     WHERE id = p_snapshot_id;

    SELECT COALESCE(linked_viz_snapshots::jsonb, '[]'::jsonb)
      INTO v_linked
      FROM synergy_sessions.synergy_sessions
     WHERE session_id = v_synergy_id;

    v_linked := (
        SELECT COALESCE(jsonb_agg(elem), '[]'::jsonb)
          FROM jsonb_array_elements(v_linked) elem
         WHERE (elem->>'snapshot_id') IS DISTINCT FROM p_snapshot_id::text
    );

    UPDATE synergy_sessions.synergy_sessions
       SET linked_viz_snapshots = v_linked::text,
           updated_at = NOW()
     WHERE session_id = v_synergy_id;

    RETURN jsonb_build_object('success', TRUE, 'snapshot_id', p_snapshot_id, 'synergy_session_id', v_synergy_id);
EXCEPTION WHEN OTHERS THEN
    RETURN jsonb_build_object('success', FALSE, 'error', SQLERRM);
END;
$$;

DO $$
BEGIN
    RAISE NOTICE 'Migration 057 complete: viz_snapshots + linked_viz_snapshots column + visualizations module row + link/unlink helpers';
END $$;