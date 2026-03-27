-- Migration: Add Thread Features (Tags, Synergy, Branching)
-- Date: November 7, 2025
-- Purpose: Add new columns to support thread tagging, synergy integration, and branching

-- Add new columns to saved_threads table
ALTER TABLE saved_threads ADD COLUMN IF NOT EXISTS tags TEXT DEFAULT '[]';
ALTER TABLE saved_threads ADD COLUMN IF NOT EXISTS synergy_card_id TEXT DEFAULT NULL;
ALTER TABLE saved_threads ADD COLUMN IF NOT EXISTS parent_thread_id TEXT DEFAULT NULL;
ALTER TABLE saved_threads ADD COLUMN IF NOT EXISTS branch_point_message_id TEXT DEFAULT NULL;
ALTER TABLE saved_threads ADD COLUMN IF NOT EXISTS branch_name TEXT DEFAULT NULL;
ALTER TABLE saved_threads ADD COLUMN IF NOT EXISTS summary TEXT DEFAULT NULL;
ALTER TABLE saved_threads ADD COLUMN IF NOT EXISTS summary_generated_at TEXT DEFAULT NULL;

-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_saved_threads_user_id ON saved_threads(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_threads_location ON saved_threads(location);
CREATE INDEX IF NOT EXISTS idx_saved_threads_saved_at ON saved_threads(saved_at);
CREATE INDEX IF NOT EXISTS idx_saved_threads_synergy_card ON saved_threads(synergy_card_id);
CREATE INDEX IF NOT EXISTS idx_saved_threads_parent ON saved_threads(parent_thread_id);

-- Optional: Add thread_id column to synergy_sessions for reverse linking
-- (Only if synergy_sessions table exists)
-- ALTER TABLE synergy_sessions ADD COLUMN IF NOT EXISTS thread_id TEXT DEFAULT NULL;
-- CREATE INDEX IF NOT EXISTS idx_synergy_sessions_thread ON synergy_sessions(thread_id);

-- Verify changes
SELECT 
    name,
    type,
    sql
FROM sqlite_master
WHERE tbl_name = 'saved_threads'
ORDER BY type, name;
