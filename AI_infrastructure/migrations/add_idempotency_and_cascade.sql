-- Migration: Add idempotency_key column and Team ID cascade trigger
-- Date: 2025-12-17
-- Purpose: 
--   1. Add idempotency support to prevent duplicate threads on retry
--   2. Auto-cleanup team_id when Team ID user is deleted

-- ============================================================
-- PART 1: Add idempotency_key column
-- ============================================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'sessions' 
        AND table_name = 'threads' 
        AND column_name = 'idempotency_key'
    ) THEN
        ALTER TABLE sessions.threads 
        ADD COLUMN idempotency_key TEXT;
        
        COMMENT ON COLUMN sessions.threads.idempotency_key IS 'Client-generated UUID to prevent duplicate threads on network retry';
    END IF;
END $$;

-- Create unique index on idempotency_key (enforce uniqueness)
CREATE UNIQUE INDEX IF NOT EXISTS idx_threads_idempotency_key 
ON sessions.threads(idempotency_key)
WHERE idempotency_key IS NOT NULL;

-- ============================================================
-- PART 2: Create Team ID cascade trigger
-- ============================================================

-- Create trigger function to handle Team ID deletion
CREATE OR REPLACE FUNCTION cascade_team_id_deletion()
RETURNS TRIGGER AS $$
BEGIN
    -- When a Team ID user is deleted, set their threads' team_id to NULL
    -- This prevents orphaned references to non-existent Team IDs
    IF OLD.is_sub_user = TRUE THEN
        UPDATE sessions.threads
        SET team_id = NULL
        WHERE team_id = OLD.username;
        
        RAISE NOTICE 'Cascade: Set team_id=NULL for % threads owned by deleted Team ID: %', 
            (SELECT COUNT(*) FROM sessions.threads WHERE team_id = OLD.username),
            OLD.username;
    END IF;
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Create trigger (fires BEFORE DELETE on users table)
DROP TRIGGER IF EXISTS team_id_cascade_delete ON ai_infrastructure.users;

CREATE TRIGGER team_id_cascade_delete
BEFORE DELETE ON ai_infrastructure.users
FOR EACH ROW
WHEN (OLD.is_sub_user = TRUE)
EXECUTE FUNCTION cascade_team_id_deletion();

-- ============================================================
-- Verification queries
-- ============================================================

-- Check idempotency_key column exists
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'sessions' 
  AND table_name = 'threads' 
  AND column_name = 'idempotency_key';

-- Check idempotency_key index exists
SELECT 
    indexname, 
    indexdef
FROM pg_indexes
WHERE tablename = 'threads' 
  AND indexname = 'idx_threads_idempotency_key';

-- Check trigger exists
SELECT 
    trigger_name, 
    event_manipulation, 
    event_object_table,
    action_statement
FROM information_schema.triggers
WHERE trigger_name = 'team_id_cascade_delete';

-- Check trigger function exists
SELECT 
    proname as function_name,
    pg_get_functiondef(oid) as function_definition
FROM pg_proc
WHERE proname = 'cascade_team_id_deletion';

COMMENT ON COLUMN sessions.threads.idempotency_key IS 'Client-generated UUID to prevent duplicate threads on network retry. Unique index enforces one thread per key.';
COMMENT ON FUNCTION cascade_team_id_deletion() IS 'Trigger function: Sets threads.team_id=NULL when Team ID user (is_sub_user=TRUE) is deleted';
