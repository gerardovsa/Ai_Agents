-- Migration: Optimize Thread Message Queries (Jan 23, 2026)
-- Issue: GET /api/threads/messages/get taking 27-31 seconds
-- Root Cause: Missing indexes on thread_slug and message queries
-- Impact: Connection pool exhaustion (167 connections waiting)

-- ============================================================================
-- ANALYSIS: Slow Query Pattern
-- ============================================================================
-- Query:
--   SELECT m.* FROM sessions.messages m
--   JOIN sessions.threads t ON m.thread_id = t.id
--   WHERE t.thread_slug = '1769090540921'
--   ORDER BY m.created_at ASC
--
-- Problem:
--   1. thread_slug has NO INDEX → Full table scan on threads
--   2. m.thread_id foreign key not indexed → Slow join
--   3. m.created_at not indexed → Slow ORDER BY
--
-- Result: 27-31 second query times for small result sets (6-33 messages)

-- ============================================================================
-- FIX 1: Index on threads.thread_slug (Primary Lookup)
-- ============================================================================
-- This is THE critical index - thread_slug is used in WHERE clause
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_threads_thread_slug 
    ON sessions.threads(thread_slug);

-- Add comment for documentation
COMMENT ON INDEX sessions.idx_threads_thread_slug IS 
    'Optimizes thread lookup by slug (used in /api/threads/messages/get). Jan 23, 2026.';

-- ============================================================================
-- FIX 2: Index on messages.thread_id (Foreign Key Join)
-- ============================================================================
-- Speeds up the JOIN between messages and threads
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_thread_id 
    ON sessions.messages(thread_id);

COMMENT ON INDEX sessions.idx_messages_thread_id IS 
    'Optimizes JOIN with threads table. Jan 23, 2026.';

-- ============================================================================
-- FIX 3: Composite Index for Sorted Message Queries
-- ============================================================================
-- Optimizes: WHERE thread_id = X ORDER BY created_at
-- This is faster than separate indexes for this query pattern
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_thread_created 
    ON sessions.messages(thread_id, created_at);

COMMENT ON INDEX sessions.idx_messages_thread_created IS 
    'Optimizes message queries with ORDER BY created_at. Jan 23, 2026.';

-- ============================================================================
-- FIX 4: Index on threads.id (if not already primary key)
-- ============================================================================
-- Just verify primary key exists (should already be there)
-- This is for the JOIN: m.thread_id = t.id
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE tablename = 'threads' 
        AND schemaname = 'sessions'
        AND indexname LIKE '%pkey%'
    ) THEN
        RAISE NOTICE 'WARNING: threads.id should have primary key index!';
    END IF;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these after migration to verify indexes exist:

-- 1. Check all indexes on threads table
-- SELECT indexname, indexdef FROM pg_indexes 
-- WHERE tablename = 'threads' AND schemaname = 'sessions';

-- 2. Check all indexes on messages table
-- SELECT indexname, indexdef FROM pg_indexes 
-- WHERE tablename = 'messages' AND schemaname = 'sessions';

-- 3. Explain query plan (should show "Index Scan" not "Seq Scan")
-- EXPLAIN ANALYZE
-- SELECT m.* FROM sessions.messages m
-- JOIN sessions.threads t ON m.thread_id = t.id
-- WHERE t.thread_slug = '1769090540921'
-- ORDER BY m.created_at ASC;

-- ============================================================================
-- EXPECTED IMPACT
-- ============================================================================
-- Before: 27-31 seconds for 6-33 messages
-- After:  <100ms for same queries
-- 
-- Connection pool impact:
-- Before: 15 connections held for 30s each = pool exhaustion
-- After:  15 connections held for 0.1s each = no blocking
--
-- This should eliminate "CONNECTION POOL EXHAUSTED" errors

-- ============================================================================
-- NOTES
-- ============================================================================
-- - Using CONCURRENTLY to avoid locking tables during index creation
-- - Safe to run multiple times (IF NOT EXISTS)
-- - Indexes created asynchronously, may take 1-2 minutes on large tables
-- - Monitor with: SELECT * FROM pg_stat_progress_create_index;
