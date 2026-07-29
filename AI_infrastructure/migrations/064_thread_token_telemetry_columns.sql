-- ============================================================================
-- Migration 064: Persist last-token telemetry on sessions.threads
-- Created: 2026-07-29
-- Purpose: The `token_status` SSE event (combined_agent_worker.py:2356)
--          carries {tokens, context_window, pct, model, tier, message_count,
--          thread_id} after every AI turn. Today this lives only in the
--          event stream — on page reload the indicator resets to "0 / 1M"
--          and the next SSE event re-colours it. Persisting the latest tier,
--          model, and pct on the thread row lets the indicator render the
--          correct colour and tooltip on FIRST paint (no flash), and gives
--          the thread-list endpoint a cheap column to project for at-a-glance
--          "context pressure" badges.
--
--          This migration is the DB half of the follow-up tracked in
--          THREAD_MESSAGE_CONSTRUCTION_MASTER_2026_07_29.md §14.1.
--
--          Companion code change: combined_agent_worker.py writes the new
--          columns via UPDATE sessions.threads at the end of every turn
--          (right after the socketio.emit('token_status', ...)).
--
--          Idempotent: every statement is ADD COLUMN IF NOT EXISTS. Safe to
--          re-run. No backfill needed — existing rows will simply have NULL
--          until their next AI turn.
-- ============================================================================

-- ============================================================================
-- 1. ADD COLUMNS
-- ============================================================================

ALTER TABLE sessions.threads
    ADD COLUMN IF NOT EXISTS last_token_tier      TEXT,             -- 'ok' | 'info' | 'warning' | 'critical'
    ADD COLUMN IF NOT EXISTS last_token_model     TEXT,             -- e.g. 'MiniMax-M3', 'claude-sonnet-4-6'
    ADD COLUMN IF NOT EXISTS last_token_pct       NUMERIC(5,2),     -- 0.00 .. 100.00
    ADD COLUMN IF NOT EXISTS last_token_updated_at TIMESTAMPTZ;     -- when the last token_status event fired

-- ============================================================================
-- 2. INDEX for "show me threads in warning/critical tier" queries
--    Partial index — only the small subset of threads that are NOT 'ok' is
--    indexed. Cheaper to maintain, smaller footprint than a full index.
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_threads_last_token_tier_pressure
    ON sessions.threads (last_token_tier, last_token_updated_at DESC)
    WHERE last_token_tier IS NOT NULL
      AND last_token_tier <> 'ok';

-- ============================================================================
-- 3. Defensive CHECK constraint (idempotent — wrap in DO block)
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.check_constraints cc
        JOIN information_schema.constraint_column_usage ccu
              ON cc.constraint_name = ccu.constraint_name
        WHERE ccu.table_schema = 'sessions'
          AND ccu.table_name   = 'threads'
          AND ccu.column_name  = 'last_token_tier'
          AND cc.constraint_name = 'threads_last_token_tier_check'
    ) THEN
        ALTER TABLE sessions.threads
            ADD CONSTRAINT threads_last_token_tier_check
                CHECK (last_token_tier IS NULL OR last_token_tier IN ('ok', 'info', 'warning', 'critical'));
    END IF;
END
$$;

-- ============================================================================
-- 4. VERIFY
-- ============================================================================

DO $$
DECLARE
    v_tier_type       TEXT;
    v_model_type      TEXT;
    v_pct_type        TEXT;
    v_updated_type    TEXT;
    v_index_exists    BOOLEAN;
    v_constraint_ct   INTEGER;
BEGIN
    SELECT data_type INTO v_tier_type
    FROM information_schema.columns
    WHERE table_schema = 'sessions' AND table_name = 'threads' AND column_name = 'last_token_tier';

    SELECT data_type INTO v_model_type
    FROM information_schema.columns
    WHERE table_schema = 'sessions' AND table_name = 'threads' AND column_name = 'last_token_model';

    SELECT data_type INTO v_pct_type
    FROM information_schema.columns
    WHERE table_schema = 'sessions' AND table_name = 'threads' AND column_name = 'last_token_pct';

    SELECT data_type INTO v_updated_type
    FROM information_schema.columns
    WHERE table_schema = 'sessions' AND table_name = 'threads' AND column_name = 'last_token_updated_at';

    SELECT EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'sessions' AND tablename = 'threads'
          AND indexname = 'idx_threads_last_token_tier_pressure'
    ) INTO v_index_exists;

    SELECT COUNT(*) INTO v_constraint_ct
    FROM information_schema.check_constraints cc
    JOIN information_schema.constraint_column_usage ccu
          ON cc.constraint_name = ccu.constraint_name
    WHERE ccu.table_schema = 'sessions'
      AND ccu.table_name   = 'threads'
      AND ccu.column_name  = 'last_token_tier'
      AND cc.constraint_name = 'threads_last_token_tier_check';

    RAISE NOTICE '064_thread_token_telemetry_columns verification:';
    RAISE NOTICE '  last_token_tier       = %', v_tier_type;
    RAISE NOTICE '  last_token_model      = %', v_model_type;
    RAISE NOTICE '  last_token_pct        = %', v_pct_type;
    RAISE NOTICE '  last_token_updated_at = %', v_updated_type;
    RAISE NOTICE '  idx_threads_last_token_tier_pressure exists = %', v_index_exists;
    RAISE NOTICE '  threads_last_token_tier_check constraint   = %', v_constraint_ct;
END
$$;