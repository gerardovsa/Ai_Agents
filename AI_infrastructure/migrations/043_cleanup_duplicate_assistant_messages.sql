-- Migration 043: Clean up consecutive duplicate assistant messages
-- Created: April 2026
--
-- Root cause: /api/agent/agent/<id>/start used to spawn run_simple_agent_worker
-- in a background thread while /api/agent/stream/<id> also called
-- execute_streaming_request directly. Both paths called Anthropic and saved
-- the response to the DB, producing pairs of consecutive assistant messages.
--
-- For thinking-enabled models the two responses had unique thinking.signature
-- values so the hash-based dedup did not catch them.
--
-- Fix applied in agent_routes_v4.py (Step 6 of /start now just updates status —
-- no worker thread is launched; all AI processing happens in execute_streaming_request).
--
-- This migration removes the historical duplicate messages left in the database.
-- Strategy: keep the FIRST assistant message in each consecutive pair, delete the SECOND,
-- unless only the second has tool_use blocks (in which case keep the second instead).
--
-- Idempotent: safe to run multiple times (uses DELETE ... WHERE id IN).

DO $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN

    -- Step 1: Find the ID of the second message in every consecutive assistant pair
    -- and delete it (unless it has tool_use and the first does not).
    WITH ordered AS (
        SELECT
            m.id,
            m.thread_id,
            m.role,
            m.content,
            m.created_at,
            LAG(m.role)    OVER (PARTITION BY m.thread_id ORDER BY m.created_at, m.id) AS prev_role,
            LAG(m.id)      OVER (PARTITION BY m.thread_id ORDER BY m.created_at, m.id) AS prev_id,
            LAG(m.content) OVER (PARTITION BY m.thread_id ORDER BY m.created_at, m.id) AS prev_content
        FROM sessions.messages m
    ),
    consecutive_pairs AS (
        -- Current message is an assistant that immediately follows another assistant
        SELECT
            id          AS second_id,
            prev_id     AS first_id,
            content     AS second_content,
            prev_content AS first_content
        FROM ordered
        WHERE role = 'assistant' AND prev_role = 'assistant'
    ),
    to_delete AS (
        -- Default: delete the second one.
        -- Exception: if ONLY the second has tool_use blocks, delete the first instead.
        SELECT
            CASE
                WHEN (
                    -- second has tool_use
                    second_content::text LIKE '%"tool_use"%'
                    -- first does NOT have tool_use
                    AND first_content::text NOT LIKE '%"tool_use"%'
                ) THEN first_id
                ELSE second_id
            END AS delete_id
        FROM consecutive_pairs
    )
    DELETE FROM sessions.messages
    WHERE id IN (SELECT delete_id FROM to_delete);

    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'Deleted % duplicate assistant message(s).', deleted_count;

END $$;
