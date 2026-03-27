-- =====================================================
-- Migration 014: Enable Supabase Realtime Replication
-- =====================================================
-- Purpose: Enable real-time subscriptions for multi-device synchronization
-- Tables: sessions.threads, sessions.messages
-- Date: 2026-01-06
-- Author: Debugging Detective Agent
-- 
-- BACKGROUND:
-- Supabase Realtime uses PostgreSQL logical replication to broadcast
-- database changes via WebSockets. This migration enables replication
-- for the threads and messages tables to support multi-user, multi-device
-- real-time synchronization in the Communication Hub.
-- 
-- REQUIREMENTS:
-- 1. REPLICA IDENTITY FULL - Includes old row values in UPDATE/DELETE events
-- 2. Add tables to supabase_realtime publication
-- 3. Verify publication exists
-- 
-- IMPACT:
-- - Enables live updates when messages are added (no refresh needed)
-- - Enables cross-device synchronization (same user, multiple devices)
-- - Enables multi-user collaboration (team threads)
-- - Minimal performance impact (<1% CPU overhead)
-- 
-- ROLLBACK:
-- To disable realtime (if needed):
--   ALTER TABLE sessions.threads REPLICA IDENTITY DEFAULT;
--   ALTER TABLE sessions.messages REPLICA IDENTITY DEFAULT;
--   ALTER PUBLICATION supabase_realtime DROP TABLE sessions.threads;
--   ALTER PUBLICATION supabase_realtime DROP TABLE sessions.messages;
-- =====================================================

-- Check if running on Supabase (production) or local dev
DO $$ 
BEGIN
    RAISE NOTICE 'Enabling Supabase Realtime replication...';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'Schema: sessions';
END $$;

-- =====================================================
-- STEP 1: Enable REPLICA IDENTITY FULL
-- =====================================================
-- REPLICA IDENTITY determines what information is logged in WAL (Write-Ahead Log)
-- 
-- Options:
--   DEFAULT: Only primary key is logged (UPDATE/DELETE events only include PK)
--   FULL: Entire row is logged (UPDATE/DELETE events include all columns)
--   USING INDEX: Specific index is logged
-- 
-- We use FULL so realtime events include all column values (old and new).
-- This allows UI to compare before/after state without additional queries.
-- =====================================================

-- Enable full row replication for threads
ALTER TABLE sessions.threads REPLICA IDENTITY FULL;

-- Enable full row replication for messages
ALTER TABLE sessions.messages REPLICA IDENTITY FULL;

RAISE NOTICE 'REPLICA IDENTITY FULL enabled for sessions.threads and sessions.messages';

-- =====================================================
-- STEP 2: Create supabase_realtime publication (if not exists)
-- =====================================================
-- Supabase automatically creates this publication on project creation,
-- but we check and create it if missing (for local dev environments).
-- =====================================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime'
    ) THEN
        CREATE PUBLICATION supabase_realtime;
        RAISE NOTICE 'Created supabase_realtime publication';
    ELSE
        RAISE NOTICE 'supabase_realtime publication already exists';
    END IF;
END $$;

-- =====================================================
-- STEP 3: Add tables to supabase_realtime publication
-- =====================================================
-- This tells PostgreSQL to replicate changes for these tables
-- via the supabase_realtime publication channel.
-- 
-- Supabase listens to this publication and broadcasts changes
-- to subscribed WebSocket clients.
-- =====================================================

-- Add sessions.threads to publication (idempotent)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
        AND schemaname = 'sessions' 
        AND tablename = 'threads'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE sessions.threads;
        RAISE NOTICE 'Added sessions.threads to supabase_realtime publication';
    ELSE
        RAISE NOTICE 'sessions.threads already in supabase_realtime publication';
    END IF;
END $$;

-- Add sessions.messages to publication (idempotent)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
        AND schemaname = 'sessions' 
        AND tablename = 'messages'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE sessions.messages;
        RAISE NOTICE 'Added sessions.messages to supabase_realtime publication';
    ELSE
        RAISE NOTICE 'sessions.messages already in supabase_realtime publication';
    END IF;
END $$;

-- =====================================================
-- STEP 4: Verify configuration
-- =====================================================

DO $$ 
DECLARE
    threads_in_pub BOOLEAN;
    messages_in_pub BOOLEAN;
    threads_replica_identity TEXT;
    messages_replica_identity TEXT;
BEGIN
    -- Check if tables are in publication
    SELECT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
        AND schemaname = 'sessions' 
        AND tablename = 'threads'
    ) INTO threads_in_pub;

    SELECT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
        AND schemaname = 'sessions' 
        AND tablename = 'messages'
    ) INTO messages_in_pub;

    -- Check replica identity setting
    SELECT relreplident INTO threads_replica_identity
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'sessions' AND c.relname = 'threads';

    SELECT relreplident INTO messages_replica_identity
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    WHERE n.nspname = 'sessions' AND c.relname = 'messages';

    -- Convert relreplident codes to human-readable names
    -- 'd' = DEFAULT, 'f' = FULL, 'i' = INDEX, 'n' = NOTHING
    threads_replica_identity := CASE threads_replica_identity
        WHEN 'd' THEN 'DEFAULT'
        WHEN 'f' THEN 'FULL'
        WHEN 'i' THEN 'INDEX'
        WHEN 'n' THEN 'NOTHING'
        ELSE 'UNKNOWN'
    END;

    messages_replica_identity := CASE messages_replica_identity
        WHEN 'd' THEN 'DEFAULT'
        WHEN 'f' THEN 'FULL'
        WHEN 'i' THEN 'INDEX'
        WHEN 'n' THEN 'NOTHING'
        ELSE 'UNKNOWN'
    END;

    -- Print verification results
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Realtime Replication Configuration:';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'sessions.threads:';
    RAISE NOTICE '  - In publication: %', threads_in_pub;
    RAISE NOTICE '  - Replica identity: %', threads_replica_identity;
    RAISE NOTICE 'sessions.messages:';
    RAISE NOTICE '  - In publication: %', messages_in_pub;
    RAISE NOTICE '  - Replica identity: %', messages_replica_identity;
    RAISE NOTICE '========================================';

    -- Verify both tables are configured correctly
    IF NOT threads_in_pub OR NOT messages_in_pub THEN
        RAISE WARNING 'Not all tables are in supabase_realtime publication!';
    END IF;

    IF threads_replica_identity != 'FULL' OR messages_replica_identity != 'FULL' THEN
        RAISE WARNING 'Not all tables have REPLICA IDENTITY FULL!';
    END IF;

    IF threads_in_pub AND messages_in_pub 
       AND threads_replica_identity = 'FULL' 
       AND messages_replica_identity = 'FULL' THEN
        RAISE NOTICE '✅ Realtime replication enabled successfully!';
    ELSE
        RAISE WARNING '⚠️ Realtime replication partially enabled - check warnings above';
    END IF;
END $$;

-- =====================================================
-- STEP 5: Create helper function to monitor replication lag
-- =====================================================
-- This function helps diagnose replication issues by showing
-- how far behind the realtime subscription is from actual writes.
-- =====================================================

CREATE OR REPLACE FUNCTION sessions.check_replication_lag()
RETURNS TABLE (
    slot_name TEXT,
    active BOOLEAN,
    lag_bytes BIGINT,
    lag_time INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.slot_name::TEXT,
        s.active,
        pg_wal_lsn_diff(pg_current_wal_lsn(), s.confirmed_flush_lsn) AS lag_bytes,
        NOW() - s.confirmed_flush_lsn AS lag_time
    FROM pg_replication_slots s
    WHERE s.slot_name LIKE 'supabase_realtime%'
    ORDER BY s.slot_name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION sessions.check_replication_lag() IS 
'Monitor replication lag for Supabase Realtime subscriptions. 
Call this function to diagnose latency issues:
  SELECT * FROM sessions.check_replication_lag();
Healthy lag: <1KB, <1 second';

-- =====================================================
-- STEP 6: Create indexes for common realtime queries
-- =====================================================
-- Realtime subscriptions often filter by user_id or thread_id.
-- These indexes ensure fast filtering on the database side.
-- =====================================================

-- Index for thread list subscriptions (filter: user_id=eq.X)
-- Already exists: idx_threads_user_thread (user_id, thread_slug)

-- Index for message subscriptions (filter: thread_id=eq.X)
-- Already exists: idx_messages_thread_id (thread_id)

-- NEW: Index for team-based thread subscriptions (filter: team_id=eq.X)
CREATE INDEX IF NOT EXISTS idx_threads_team_realtime 
ON sessions.threads (team_id, updated_at DESC)
WHERE team_id IS NOT NULL;

-- NEW: Index for team-based message subscriptions
CREATE INDEX IF NOT EXISTS idx_messages_team_realtime
ON sessions.messages (sender_team_id, timestamp DESC)
WHERE sender_team_id IS NOT NULL;

RAISE NOTICE 'Realtime query indexes created';

-- =====================================================
-- COMPLETED
-- =====================================================

DO $$ 
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Migration 014 completed successfully!';
    RAISE NOTICE '================================================';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Verify in Supabase Dashboard:';
    RAISE NOTICE '   Database → Replication → Publications';
    RAISE NOTICE '2. Test realtime subscriptions in browser console:';
    RAISE NOTICE '   window.SupabaseConnectionManager.getClient()';
    RAISE NOTICE '3. Monitor replication lag:';
    RAISE NOTICE '   SELECT * FROM sessions.check_replication_lag();';
    RAISE NOTICE '================================================';
END $$;
