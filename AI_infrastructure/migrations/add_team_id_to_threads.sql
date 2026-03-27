-- Migration: Add team_id column to sessions.threads table
-- Date: 2025-12-17
-- Purpose: Enable Team ID tracking for threads

-- Add team_id column
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'sessions' 
        AND table_name = 'threads' 
        AND column_name = 'team_id'
    ) THEN
        ALTER TABLE sessions.threads 
        ADD COLUMN team_id TEXT;
        
        COMMENT ON COLUMN sessions.threads.team_id IS 'Team ID (username) of the sub-user who created this thread';
    END IF;
END $$;

-- Backfill existing threads with team_id from user's username (if is_sub_user = TRUE)
UPDATE sessions.threads t
SET team_id = u.username
FROM ai_infrastructure.users u
WHERE t.user_id = u.id 
  AND u.is_sub_user = TRUE
  AND t.team_id IS NULL;

-- Create index for filtering by team_id
CREATE INDEX IF NOT EXISTS idx_threads_team_id 
ON sessions.threads(team_id)
WHERE team_id IS NOT NULL;

-- Create composite index for user_id + team_id queries
CREATE INDEX IF NOT EXISTS idx_threads_user_team 
ON sessions.threads(user_id, team_id)
WHERE team_id IS NOT NULL;

-- Verification query
SELECT 
    COUNT(*) as total_threads,
    COUNT(team_id) as threads_with_team_id,
    COUNT(DISTINCT team_id) as unique_team_ids
FROM sessions.threads;
