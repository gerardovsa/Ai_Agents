-- ============================================================
-- MIGRATION: Create user_transcriptions table
-- Created: December 23, 2025
-- Purpose: Store STT/TTS transcription history per user
-- ============================================================

-- Create user_transcriptions table (IDEMPOTENT)
CREATE TABLE IF NOT EXISTS ai_infrastructure.user_transcriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    source_type VARCHAR(50) NOT NULL DEFAULT 'recording',  -- 'recording', 'upload', 'tts'
    transcript_text TEXT NOT NULL,
    confidence DECIMAL(5, 4),  -- 0.0000 to 1.0000
    language VARCHAR(10),  -- e.g., 'en', 'es', 'fr'
    duration_seconds DECIMAL(10, 2),  -- Duration of audio in seconds
    word_count INTEGER,
    model_used VARCHAR(100),  -- e.g., 'whisper-large-v3', 'google-tts'
    metadata JSONB DEFAULT '{}',  -- Additional metadata (file info, settings, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint (with CASCADE for cleanup)
    CONSTRAINT fk_user_transcriptions_user
        FOREIGN KEY (user_id)
        REFERENCES ai_infrastructure.users(id)
        ON DELETE CASCADE
);

-- Create indexes for performance (IDEMPOTENT)
CREATE INDEX IF NOT EXISTS idx_user_transcriptions_user_id 
    ON ai_infrastructure.user_transcriptions(user_id);

CREATE INDEX IF NOT EXISTS idx_user_transcriptions_created_at 
    ON ai_infrastructure.user_transcriptions(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_user_transcriptions_source_type 
    ON ai_infrastructure.user_transcriptions(source_type);

CREATE INDEX IF NOT EXISTS idx_user_transcriptions_language 
    ON ai_infrastructure.user_transcriptions(language);

-- Create trigger to auto-update updated_at timestamp (IDEMPOTENT)
CREATE OR REPLACE FUNCTION update_user_transcriptions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_user_transcriptions_updated_at 
    ON ai_infrastructure.user_transcriptions;

CREATE TRIGGER trigger_update_user_transcriptions_updated_at
    BEFORE UPDATE ON ai_infrastructure.user_transcriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_user_transcriptions_updated_at();

-- Grant permissions (IDEMPOTENT)
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_infrastructure.user_transcriptions TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE ai_infrastructure.user_transcriptions_id_seq TO authenticated;

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
-- SELECT * FROM ai_infrastructure.user_transcriptions LIMIT 10;
-- SELECT COUNT(*) FROM ai_infrastructure.user_transcriptions;
-- SELECT user_id, COUNT(*), SUM(duration_seconds) 
--   FROM ai_infrastructure.user_transcriptions 
--   GROUP BY user_id;
