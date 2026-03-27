-- Add token_count column to threads table
-- This tracks cumulative token usage for each conversation thread

-- Migration: add_token_count_to_threads
-- Created: 2025-11-14
-- Purpose: Enable real-time token tracking in UI

-- Add column with default value
ALTER TABLE threads ADD COLUMN token_count INTEGER DEFAULT 0;

-- Create index for efficient queries
CREATE INDEX IF NOT EXISTS idx_threads_token_count ON threads(token_count);

-- Update existing threads to have 0 tokens
UPDATE threads SET token_count = 0 WHERE token_count IS NULL;

-- Verify migration
SELECT COUNT(*) as total_threads, 
       SUM(CASE WHEN token_count IS NOT NULL THEN 1 ELSE 0 END) as threads_with_token_count
FROM threads;
