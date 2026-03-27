-- Migration: Drop thread_assignments table (not needed - sessions.threads already has email columns)
-- Author: GitHub Copilot
-- Date: December 22, 2025
-- Reason: sessions.threads already has email_thread_id, email_subject, email_participants columns

-- Drop table if exists (idempotent)
DROP TABLE IF EXISTS sessions.thread_assignments CASCADE;

-- Verify table dropped
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'sessions' 
        AND table_name = 'thread_assignments'
    ) THEN
        RAISE NOTICE '✅ Table sessions.thread_assignments dropped successfully';
    ELSE
        RAISE EXCEPTION '❌ Failed to drop sessions.thread_assignments table';
    END IF;
END $$;
