-- Migration 001: Create thread_assignments table
-- Date: 2025-11-08
-- Purpose: Store persistent thread-to-agent assignments
-- CRITICAL: Without this table, thread assignments are lost on browser refresh

-- Create thread_assignments table
CREATE TABLE IF NOT EXISTS thread_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,  -- Thread ID (UUID from backend)
    location TEXT NOT NULL,     -- 'prime', 'agent-1', 'agent-2', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, location)  -- One thread per location per user (exclusive assignment)
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_thread_assignments_user 
ON thread_assignments(user_id);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_session 
ON thread_assignments(session_id);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_location 
ON thread_assignments(user_id, location);

-- Create trigger to auto-update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_thread_assignments_timestamp
AFTER UPDATE ON thread_assignments
FOR EACH ROW
BEGIN
    UPDATE thread_assignments 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Insert test data (optional - comment out for production)
-- INSERT OR IGNORE INTO thread_assignments (user_id, session_id, location) 
-- VALUES (1, 'test-thread-prime', 'prime');

-- Verification query
-- SELECT * FROM thread_assignments;
