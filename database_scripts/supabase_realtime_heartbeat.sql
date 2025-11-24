-- ============================================================================
-- SUPABASE REALTIME HEARTBEAT SYSTEM
-- ============================================================================
-- PURPOSE: Server-side heartbeat that broadcasts presence every 60 seconds
--          to keep Realtime connections alive and prevent false-positive
--          health check failures.
--
-- FEATURES:
--   - Broadcasts to 'heartbeat-channel' every 60 seconds
--   - Uses realtime.send() to trigger replication slot
--   - Clients can subscribe to heartbeat for keep-alive
--   - No frontend health check pings needed
--
-- CREATED: 2025-11-24
-- ============================================================================

-- Step 1: Enable required extensions
-- ============================================================================
-- pg_cron: Schedule recurring jobs
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- pg_net: Make HTTP requests (optional, for debugging)
CREATE EXTENSION IF NOT EXISTS pg_net;


-- Step 2: Create heartbeat broadcast function
-- ============================================================================
-- This function inserts a row into realtime.messages which triggers
-- the replication slot to broadcast the heartbeat to all connected clients
CREATE OR REPLACE FUNCTION public.broadcast_realtime_heartbeat()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Insert heartbeat message into realtime.messages table
    -- This triggers the replication slot to broadcast to clients
    PERFORM realtime.send(
        payload := jsonb_build_object(
            'event', 'heartbeat',
            'timestamp', NOW()::text,
            'message', 'Server heartbeat - connection alive'
        ),
        event := 'heartbeat',
        topic := 'heartbeat-channel',
        private := false
    );
    
    -- Log the heartbeat (optional - remove in production to reduce logs)
    RAISE LOG 'Realtime heartbeat sent at %', NOW();
    
EXCEPTION
    WHEN OTHERS THEN
        -- Capture errors to prevent cron job from breaking
        RAISE WARNING 'Heartbeat broadcast failed: %', SQLERRM;
END;
$$;

-- Grant execute permission to postgres role (required for pg_cron)
GRANT EXECUTE ON FUNCTION public.broadcast_realtime_heartbeat() TO postgres;


-- Step 3: Schedule the heartbeat job with pg_cron
-- ============================================================================
-- Schedule heartbeat every 60 seconds (1 minute)
-- Cron syntax: '60 seconds' or '* * * * *' (every minute)

-- First, unschedule if it already exists (to avoid duplicates)
SELECT cron.unschedule('realtime-heartbeat-job')
WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'realtime-heartbeat-job'
);

-- Schedule the heartbeat job
SELECT cron.schedule(
    'realtime-heartbeat-job',        -- Job name
    '60 seconds',                      -- Every 60 seconds
    'SELECT public.broadcast_realtime_heartbeat();'
);


-- Step 4: Verify the job was scheduled
-- ============================================================================
SELECT 
    jobid,
    schedule,
    command,
    nodename,
    nodeport,
    database,
    username,
    active
FROM cron.job
WHERE jobname = 'realtime-heartbeat-job';


-- ============================================================================
-- FRONTEND INTEGRATION (JavaScript)
-- ============================================================================
-- Add this to your Supabase connection manager:
--
-- // Subscribe to heartbeat channel
-- const heartbeatChannel = supabaseClient
--     .channel('heartbeat-channel')
--     .on('broadcast', { event: 'heartbeat' }, (payload) => {
--         console.log('💓 [Supabase] Server heartbeat received:', payload);
--         this.lastHeartbeat = Date.now();
--     })
--     .subscribe();
--
-- // Check if heartbeat is stale (e.g., no heartbeat in 90 seconds)
-- if (Date.now() - this.lastHeartbeat > 90000) {
--     console.warn('⚠️ [Supabase] Heartbeat stale - connection may be dead');
--     this.reconnect();
-- }
-- ============================================================================


-- ============================================================================
-- MONITORING & DEBUGGING
-- ============================================================================

-- View last 10 heartbeat job runs
SELECT 
    runid,
    jobid,
    job_pid,
    database,
    username,
    command,
    status,
    return_message,
    start_time,
    end_time
FROM cron.job_run_details
WHERE jobid = (SELECT jobid FROM cron.job WHERE jobname = 'realtime-heartbeat-job')
ORDER BY start_time DESC
LIMIT 10;


-- View all active cron jobs
SELECT * FROM cron.job WHERE active = true;


-- Manually test the heartbeat function
SELECT public.broadcast_realtime_heartbeat();


-- ============================================================================
-- CLEANUP (Run these commands to remove the heartbeat system)
-- ============================================================================

-- Unschedule the job
-- SELECT cron.unschedule('realtime-heartbeat-job');

-- Drop the function
-- DROP FUNCTION IF EXISTS public.broadcast_realtime_heartbeat();


-- ============================================================================
-- NOTES
-- ============================================================================
-- 1. The heartbeat broadcasts to 'heartbeat-channel' every 60 seconds
-- 2. Clients subscribe to this channel to receive keep-alive pings
-- 3. If no heartbeat received in 90+ seconds, client knows connection is dead
-- 4. This eliminates need for frontend health check pings
-- 5. Server-authoritative connection state (more reliable)
-- 6. Uses Supabase's realtime.send() function (built-in)
-- 7. Replication slot broadcasts changes automatically
-- 8. Minimal overhead (~1 message per minute per client)
--
-- TROUBLESHOOTING:
-- - Check cron.job_run_details for errors
-- - Verify pg_cron extension is enabled
-- - Ensure realtime schema exists (it should by default)
-- - Check that realtime.messages table exists
-- - Verify replication slot is active
-- ============================================================================
