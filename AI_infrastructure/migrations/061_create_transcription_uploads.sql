-- ============================================================================
-- Migration 061: Create transcription_uploads table
-- Created: 2026-07-26
-- Purpose: Add a child table to user_transcriptions that records the source
--          audio file (filename, size, mime, original duration, processing
--          time). The save_transcription route already attempts to write to
--          this table, but the table has never existed in any environment,
--          causing the INSERT to silently fail inside a try/except.
--
--          Also enables row-level security so a user can only read/write
--          uploads that belong to a transcription they own.
--
-- Idempotent: yes (CREATE TABLE IF NOT EXISTS, DROP POLICY IF EXISTS).
-- ============================================================================

CREATE TABLE IF NOT EXISTS ai_infrastructure.transcription_uploads (
    id                    SERIAL PRIMARY KEY,
    transcription_id      INTEGER NOT NULL,
    filename              VARCHAR(512),
    file_size             BIGINT,
    file_type             VARCHAR(64),
    mime_type             VARCHAR(128),
    original_duration     DECIMAL(10, 2),
    processing_time_ms    INTEGER,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Foreign key to the parent transcription row. CASCADE because the
    -- parent owns the child record semantically.
    CONSTRAINT fk_transcription_uploads_transcription
        FOREIGN KEY (transcription_id)
        REFERENCES ai_infrastructure.user_transcriptions(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transcription_uploads_transcription_id
    ON ai_infrastructure.transcription_uploads (transcription_id);

-- Grant table-level CRUD to the authenticated role (RLS below narrows visibility).
GRANT SELECT, INSERT, UPDATE, DELETE
    ON ai_infrastructure.transcription_uploads TO authenticated;
GRANT USAGE, SELECT
    ON SEQUENCE ai_infrastructure.transcription_uploads_id_seq TO authenticated;

-- Enable and define row-level security.
ALTER TABLE ai_infrastructure.transcription_uploads ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS transcription_uploads_rls ON ai_infrastructure.transcription_uploads;

-- RLS predicate resolves the upload to its parent transcription, then asserts
-- the parent is owned by the current RLS user. Mirrors the session-var
-- convention used by migration 059: app.user_id is set by
-- AI_infrastructure/shared/rls_session_manager.py via inject_rls_vars(conn).
CREATE POLICY transcription_uploads_rls ON ai_infrastructure.transcription_uploads
    USING (
        EXISTS (
            SELECT 1
            FROM ai_infrastructure.user_transcriptions t
            WHERE t.id = transcription_uploads.transcription_id
              AND t.user_id = NULLIF(current_setting('app.user_id', true), '')::int
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1
            FROM ai_infrastructure.user_transcriptions t
            WHERE t.id = transcription_uploads.transcription_id
              AND t.user_id = NULLIF(current_setting('app.user_id', true), '')::int
        )
    );

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'transcription_uploads'
    ) THEN
        RAISE NOTICE 'Migration 061 verified: transcription_uploads table exists with RLS enabled';
    ELSE
        RAISE EXCEPTION 'Migration 061 verification failed: transcription_uploads table missing';
    END IF;
END $$;