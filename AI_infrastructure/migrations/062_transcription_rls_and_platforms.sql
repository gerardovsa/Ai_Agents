-- ============================================================================
-- Migration 062: Transcription RLS + missing platform_catalog rows
-- Created: 2026-07-26
-- Purpose: Two related fixes the audit found:
--          1) ai_infrastructure.user_transcriptions has no row-level security
--             policy, so any DB user with SELECT on the table sees every
--             user's transcriptions. Enable RLS keyed on the per-user session
--             variable app.user_id (set by rls_session_manager.inject_rls_vars).
--          2) The /api/transcription/engines-status route resolves keys for
--             'deepgram', 'speechmatics', and 'local_whisper', but these
--             platforms are not in ai_infrastructure.platform_catalog. They
--             are missing from the "Add API Key" UI as a result. Insert them
--             so the UI surface matches what the backend can actually use.
--
-- Idempotent: yes (DROP POLICY IF EXISTS, ON CONFLICT DO NOTHING).
-- ============================================================================

-- 1. Enable RLS on user_transcriptions -----------------------------------------
ALTER TABLE ai_infrastructure.user_transcriptions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS user_transcriptions_rls ON ai_infrastructure.user_transcriptions;

CREATE POLICY user_transcriptions_rls ON ai_infrastructure.user_transcriptions
    USING (user_id = NULLIF(current_setting('app.user_id', true), '')::int)
    WITH CHECK (user_id = NULLIF(current_setting('app.user_id', true), '')::int);

-- 2. Seed the three transcription platforms into platform_catalog -------------
-- All three use a single api_key field. local_whisper is auth_type 'none' —
-- it has no key; the row exists so the UI can render a config tile and the
-- backend can look up its display name / icon consistently.
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('deepgram', 'Deepgram', 'fas fa-wave-square', '#13B5EA', 'ai', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"Found in console.deepgram.com"}]',
     'Deepgram speech-to-text (Nova-3 model, streaming + batch).',
     'https://developers.deepgram.com', 14),

    ('speechmatics', 'Speechmatics', 'fas fa-language', '#FF6B35', 'ai', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"Found in portal.speechmatics.com"}]',
     'Speechmatics real-time and batch speech recognition.',
     'https://docs.speechmatics.com', 15),

    ('local_whisper', 'Local Whisper', 'fas fa-microphone-alt', '#6366F1', 'ai', 'none',
     '[]'::jsonb,
     'On-device OpenAI Whisper model (no API key required, requires openai-whisper Python package).',
     'https://github.com/openai/whisper', 16)

ON CONFLICT (platform_name) DO NOTHING;

DO $$
DECLARE
    rls_enabled BOOLEAN;
    platforms_added INTEGER;
BEGIN
    SELECT relrowsecurity
      INTO rls_enabled
      FROM pg_class
     WHERE relname = 'user_transcriptions'
       AND relnamespace = 'ai_infrastructure'::regnamespace;

    SELECT COUNT(*)
      INTO platforms_added
      FROM ai_infrastructure.platform_catalog
     WHERE platform_name IN ('deepgram', 'speechmatics', 'local_whisper');

    IF rls_enabled IS DISTINCT FROM TRUE THEN
        RAISE EXCEPTION 'Migration 062 verification failed: RLS not enabled on user_transcriptions';
    END IF;

    IF platforms_added <> 3 THEN
        RAISE EXCEPTION 'Migration 062 verification failed: expected 3 transcription platforms, found %', platforms_added;
    END IF;

    RAISE NOTICE 'Migration 062 verified: RLS enabled on user_transcriptions; % transcription platforms present', platforms_added;
END $$;