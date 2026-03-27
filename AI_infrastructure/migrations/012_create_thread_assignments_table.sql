-- Migration: Create thread_assignments table for email-to-thread mapping persistence
-- Author: GitHub Copilot
-- Date: December 22, 2025
-- Purpose: Store which emails are linked to which threads (Fix #4: Email-Thread Persistence)

-- Create table if not exists (idempotent)
CREATE TABLE IF NOT EXISTS sessions.thread_assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    thread_slug VARCHAR(255) NOT NULL,
    email_thread_id VARCHAR(255) NOT NULL,  -- gmail_xxx or outlook_xxx format
    email_subject TEXT,
    email_participants TEXT[],  -- Array of email addresses
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(email_thread_id, user_id),  -- Each email can only be assigned once per user
    
    -- Foreign key to threads table
    CONSTRAINT fk_thread
        FOREIGN KEY (thread_slug)
        REFERENCES sessions.threads(thread_slug)
        ON DELETE CASCADE  -- If thread deleted, remove assignment
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_thread_assignments_user_id 
    ON sessions.thread_assignments(user_id);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_thread_slug 
    ON sessions.thread_assignments(thread_slug);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_email_thread_id 
    ON sessions.thread_assignments(email_thread_id);

CREATE INDEX IF NOT EXISTS idx_thread_assignments_created_at 
    ON sessions.thread_assignments(created_at DESC);

-- Add comment
COMMENT ON TABLE sessions.thread_assignments IS 'Maps email IDs to thread slugs for Communication Hub persistence (survives page refresh)';

-- Verify table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'sessions' 
        AND table_name = 'thread_assignments'
    ) THEN
        RAISE NOTICE '✅ Table sessions.thread_assignments created successfully';
    ELSE
        RAISE EXCEPTION '❌ Failed to create sessions.thread_assignments table';
    END IF;
END $$;
