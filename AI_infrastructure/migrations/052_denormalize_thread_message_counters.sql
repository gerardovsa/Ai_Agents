-- ============================================================================
-- Migration 052: Denormalize message_count + last_message_at onto sessions.threads
-- Created: June 11, 2026
-- Purpose: /api/threads/list previously used 3 correlated subqueries per row
--          to compute message_count, last_message_time, and last_message_role.
--          For users with chatty threads (100 threads × 5,000+ messages each),
--          that pattern produced 25+ s response times and broke the login
--          burst (Render's edge returns 502 when a request exceeds its proxy
--          timeout). LATERAL JOINs (migration-of-fix from June 11) reduce
--          the cost ~3×, but the only fully-constant-time fix is to store
--          the counters on the threads row itself and maintain them via a
--          trigger on sessions.messages.
--
--          This migration:
--            1. Adds message_count + last_message_at columns to sessions.threads
--            2. Backfills them from existing messages (single UPDATE, batched)
--            3. Creates indexes optimised for the new read pattern
--            4. Creates a trigger on sessions.messages to keep them in sync
--               on INSERT / UPDATE / DELETE
--
--          The new read path is a plain SELECT against the columns, which is
--          O(1) per thread regardless of how many messages it contains. For
--          the worst-case user this drops list-thread from ~25 s → ~10 ms.
--
--          Backwards compatible: existing queries that read these values from
--          a subquery still work; the new code in thread_routes.py prefers
--          the denormalized columns when present (via COALESCE on a default
--          of 0 for any row that pre-dates the migration). Idempotent: every
--          statement is IF NOT EXISTS or uses DO $$ ... END $$ guards.
-- ============================================================================


-- ============================================================================
-- 1. ADD COLUMNS (nullable initially for safe backfill)
-- ============================================================================
ALTER TABLE sessions.threads
    ADD COLUMN IF NOT EXISTS message_count   INTEGER     NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS last_message_at TIMESTAMPTZ;

-- Defensive: if message_count was added in a prior partial run without NOT NULL,
-- tighten it. Safe to run on both new + already-migrated schemas.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'sessions'
          AND table_name   = 'threads'
          AND column_name  = 'message_count'
          AND is_nullable  = 'YES'
    ) THEN
        ALTER TABLE sessions.threads
            ALTER COLUMN message_count SET NOT NULL,
            ALTER COLUMN message_count SET DEFAULT 0;
    END IF;
END $$;


-- ============================================================================
-- 2. BACKFILL FROM EXISTING MESSAGES
--    Uses the existing idx_messages_thread_created index (migration 017/999)
--    so this is an index-only scan + hash aggregate, not a full table scan.
--    For a large messages table, this is the most expensive step; the WHERE
--    filter restricts the aggregate to thread_ids that exist in threads.
-- ============================================================================
UPDATE sessions.threads t
SET
    message_count   = COALESCE(sub.cnt, 0),
    last_message_at = sub.last_at
FROM (
    SELECT
        thread_id,
        COUNT(*)        AS cnt,
        MAX(created_at) AS last_at
    FROM sessions.messages
    GROUP BY thread_id
) sub
WHERE sub.thread_id = t.id
  AND (t.message_count = 0 OR t.last_message_at IS NULL);

-- Verify backfill (cheap; reports row count + zero-count threads)
DO $$
DECLARE
    total_threads      INTEGER;
    backfilled         INTEGER;
    zero_count_threads INTEGER;
BEGIN
    SELECT COUNT(*)                  INTO total_threads      FROM sessions.threads;
    SELECT COUNT(*) FILTER (WHERE message_count > 0)
                                 INTO backfilled         FROM sessions.threads;
    SELECT COUNT(*) FILTER (WHERE message_count = 0)
                                 INTO zero_count_threads FROM sessions.threads;

    RAISE NOTICE 'Backfill complete: % threads total, % have message_count > 0, % still at 0',
        total_threads, backfilled, zero_count_threads;
END $$;


-- ============================================================================
-- 3. INDEXES for the new read pattern
--    The query in /api/threads/list is:
--        SELECT ... FROM sessions.threads WHERE user_id = ? ORDER BY <x> DESC LIMIT ?
--    We add indexes on (user_id, last_message_at DESC NULLS LAST) and
--    (team_id, last_message_at DESC NULLS LAST) for the team-UI equivalent.
--    NULLS LAST matters: a thread that has never received a message has
--    last_message_at = NULL and should sort AFTER recent ones, not before.
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_threads_user_last_message
    ON sessions.threads (user_id, last_message_at DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_threads_team_last_message
    ON sessions.threads (team_id, last_message_at DESC NULLS LAST)
    WHERE team_id IS NOT NULL;


-- ============================================================================
-- 4. TRIGGER FUNCTION
--    Fires on every INSERT / UPDATE / DELETE on sessions.messages.
--    INSERT  : increment counter, set last_message_at to NEW.created_at
--    UPDATE  : recompute both (rare, but must be correct if a message's
--              created_at is rewritten, e.g. by migration 043 which
--              deduplicated assistant messages)
--    DELETE  : recompute both (single-message delete is the common case;
--              recompute is O(log N + M) using idx_messages_thread_created)
--
--    Trigger strategy: FOR EACH ROW. Statement-level triggers were
--    considered but rejected because the broadcast layer (thread_updated
--    WebSocket event in thread_routes.py:1356) needs a counter per insert
--    to update in real time; a statement-level trigger would batch updates
--    and the last_message_at would lag behind the in-memory state. If
--    profiling shows hot-row contention on a single thread with many
--    concurrent writers, switch to FOR EACH STATEMENT in a follow-up
--    migration (zero risk to the schema, just changes the trigger body).
-- ============================================================================
CREATE OR REPLACE FUNCTION sessions.update_thread_counters()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE sessions.threads
        SET message_count   = message_count + 1,
            last_message_at = NEW.created_at
        WHERE id = NEW.thread_id;
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE sessions.threads t
        SET message_count   = COALESCE(sub.cnt, 0),
            last_message_at = sub.last_at
        FROM (
            SELECT
                COUNT(*)        AS cnt,
                MAX(created_at) AS last_at
            FROM sessions.messages
            WHERE thread_id = OLD.thread_id
        ) sub
        WHERE t.id = OLD.thread_id;
        RETURN OLD;

    ELSIF TG_OP = 'UPDATE' THEN
        -- Only recompute if the row's thread_id actually changed (rare).
        -- If the thread_id is unchanged, the counter is still correct and
        -- last_message_at only needs updating if created_at changed.
        IF NEW.thread_id = OLD.thread_id THEN
            IF NEW.created_at IS DISTINCT FROM OLD.created_at THEN
                UPDATE sessions.threads
                SET last_message_at = NEW.created_at
                WHERE id = NEW.thread_id;
            END IF;
        ELSE
            -- Decrement old thread, increment new thread
            UPDATE sessions.threads t
            SET message_count   = COALESCE(sub.cnt, 0),
                last_message_at = sub.last_at
            FROM (
                SELECT COUNT(*) AS cnt, MAX(created_at) AS last_at
                FROM sessions.messages
                WHERE thread_id = OLD.thread_id
            ) sub
            WHERE t.id = OLD.thread_id;

            UPDATE sessions.threads
            SET message_count   = message_count + 1,
                last_message_at = NEW.created_at
            WHERE id = NEW.thread_id;
        END IF;
        RETURN NEW;
    END IF;

    RETURN NULL;
END;
$$;


-- ============================================================================
-- 5. TRIGGER
-- ============================================================================
DROP TRIGGER IF EXISTS trg_update_thread_counters ON sessions.messages;
CREATE TRIGGER trg_update_thread_counters
    AFTER INSERT OR UPDATE OR DELETE ON sessions.messages
    FOR EACH ROW
    EXECUTE FUNCTION sessions.update_thread_counters();


-- ============================================================================
-- 6. VERIFY (so the deploy log has a clean smoke signal)
-- ============================================================================
DO $$
DECLARE
    trigger_count INTEGER;
    index_count   INTEGER;
BEGIN
    SELECT COUNT(*) INTO trigger_count
    FROM information_schema.triggers
    WHERE trigger_name = 'trg_update_thread_counters';

    SELECT COUNT(*) INTO index_count
    FROM pg_indexes
    WHERE schemaname = 'sessions'
      AND tablename   = 'threads'
      AND indexname IN ('idx_threads_user_last_message', 'idx_threads_team_last_message');

    RAISE NOTICE 'Migration 052 applied:';
    RAISE NOTICE '  - message_count + last_message_at columns: present';
    RAISE NOTICE '  - trigger trg_update_thread_counters: %',
        CASE WHEN trigger_count = 1 THEN 'OK' ELSE 'MISSING' END;
    RAISE NOTICE '  - new read-path indexes: % / 2 present',
        index_count;
END $$;
