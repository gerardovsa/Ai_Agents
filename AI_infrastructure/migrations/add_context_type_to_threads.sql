-- Migration: Add context_type column to sessions.threads table
-- Date: 2025-12-01
-- Purpose: Support email context and other context types for AI threads

-- Add context_type column (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'sessions' 
        AND table_name = 'threads' 
        AND column_name = 'context_type'
    ) THEN
        ALTER TABLE sessions.threads 
        ADD COLUMN context_type VARCHAR(50);
        
        COMMENT ON COLUMN sessions.threads.context_type IS 'Type of context: email, task, general, etc.';
    END IF;
END $$;

-- Update existing threads to have 'general' context type
UPDATE sessions.threads 
SET context_type = 'general' 
WHERE context_type IS NULL;

-- Create index for faster filtering by context type
CREATE INDEX IF NOT EXISTS idx_threads_context_type 
ON sessions.threads(context_type);

-- Example metadata structure for email context:
-- {
--   "email_id": "gmail_19ad7ccb11495963",
--   "email_subject": "Q4 Budget Review",
--   "email_from": "john@example.com",
--   "email_to": "me@company.com",
--   "email_date": "2025-12-01T10:30:00",
--   "email_provider": "gmail",
--   "email_has_attachments": true,
--   "email_attachment_count": 2,
--   "action_requested": "summarize"
-- }

COMMENT ON TABLE sessions.threads IS 'AI conversation threads with support for email context, task context, and general conversations';
