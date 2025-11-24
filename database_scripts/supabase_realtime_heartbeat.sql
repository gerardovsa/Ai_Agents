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


-- ============================================================================
-- THREADS CHANNEL HEARTBEAT FUNCTION
-- ============================================================================
-- This function broadcasts a heartbeat specifically to the threads realtime channel
-- Keeps the 'threads-realtime-channel' subscription alive
CREATE OR REPLACE FUNCTION public.broadcast_threads_heartbeat()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Broadcast heartbeat to threads channel
    PERFORM realtime.send(
        payload := jsonb_build_object(
            'event', 'heartbeat',
            'timestamp', NOW()::text,
            'message', 'Threads channel heartbeat',
            'channel', 'threads-realtime-channel'
        ),
        event := 'heartbeat',
        topic := 'threads-realtime-channel',
        private := false
    );
    
    -- Log the threads heartbeat
    RAISE LOG 'Threads channel heartbeat sent at %', NOW();
    
EXCEPTION
    WHEN OTHERS THEN
        -- Capture errors to prevent cron job from breaking
        RAISE WARNING 'Threads heartbeat broadcast failed: %', SQLERRM;
END;
$$;

-- Grant execute permission to postgres role
GRANT EXECUTE ON FUNCTION public.broadcast_threads_heartbeat() TO postgres;


-- Step 3: Schedule the heartbeat job with pg_cron
-- ============================================================================
-- Schedule heartbeat every minute (every 60 seconds)
-- Cron syntax: '* * * * *' = every minute on minute boundaries
-- NOTE: pg_cron does NOT accept '60 seconds' - must use cron format or 1-59 seconds

-- First, unschedule if it already exists (to avoid duplicates)
SELECT cron.unschedule('realtime-heartbeat-job')
WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'realtime-heartbeat-job'
);

-- Schedule the heartbeat job (every minute)
SELECT cron.schedule(
    'realtime-heartbeat-job',        -- Job name
    '* * * * *',                      -- Every minute (cron format)
    'SELECT public.broadcast_realtime_heartbeat();'
);

-- Schedule the threads heartbeat job (every minute)
-- First, unschedule if it already exists
SELECT cron.unschedule('threads-heartbeat-job')
WHERE EXISTS (
    SELECT 1 FROM cron.job WHERE jobname = 'threads-heartbeat-job'
);

-- Schedule the threads heartbeat
SELECT cron.schedule(
    'threads-heartbeat-job',         -- Job name
    '* * * * *',                      -- Every minute (cron format)
    'SELECT public.broadcast_threads_heartbeat();'
);


-- Step 4: Verify the jobs were scheduled
-- ============================================================================
SELECT 
    jobid,
    jobname,
    schedule,
    command,
    active
FROM cron.job
WHERE jobname IN ('realtime-heartbeat-job', 'threads-heartbeat-job')
ORDER BY jobname;


-- ============================================================================
-- FRONTEND INTEGRATION (JavaScript)
-- ============================================================================
-- Add this to your Supabase connection manager:
--
-- // Subscribe to general heartbeat channel
-- const heartbeatChannel = supabaseClient
--     .channel('heartbeat-channel')
--     .on('broadcast', { event: 'heartbeat' }, (payload) => {
--         console.log('💓 [Supabase] Server heartbeat received:', payload);
--         this.lastHeartbeat = Date.now();
--     })
--     .subscribe();
--
-- // Subscribe to threads channel with heartbeat
-- const threadsChannel = supabaseClient
--     .channel('threads-realtime-channel')
--     .on('postgres_changes', { 
--         event: '*', 
--         schema: 'sessions', 
--         table: 'threads' 
--     }, (payload) => {
--         console.log('🔄 [Threads] Change detected:', payload);
--     })
--     .on('broadcast', { event: 'heartbeat' }, (payload) => {
--         console.log('💓 [Threads] Heartbeat received:', payload);
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

-- View last 10 heartbeat job runs (general heartbeat)
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

-- View last 10 threads heartbeat job runs
SELECT 
    runid,
    jobid,
    job_pid,
    database,
    command,
    status,
    return_message,
    start_time,
    end_time
FROM cron.job_run_details
WHERE jobid = (SELECT jobid FROM cron.job WHERE jobname = 'threads-heartbeat-job')
ORDER BY start_time DESC
LIMIT 10;

-- View all heartbeat job runs (combined)
SELECT 
    j.jobname,
    jrd.status,
    jrd.start_time,
    jrd.end_time,
    jrd.return_message
FROM cron.job_run_details jrd
JOIN cron.job j ON j.jobid = jrd.jobid
WHERE j.jobname IN ('realtime-heartbeat-job', 'threads-heartbeat-job')
ORDER BY jrd.start_time DESC
LIMIT 20;


-- View all active cron jobs
SELECT * FROM cron.job WHERE active = true;


-- Manually test the heartbeat functions
SELECT public.broadcast_realtime_heartbeat();
SELECT public.broadcast_threads_heartbeat();


-- ============================================================================
-- CLEANUP (Run these commands to remove the heartbeat system)
-- ============================================================================

-- Unschedule the jobs
-- SELECT cron.unschedule('realtime-heartbeat-job');
-- SELECT cron.unschedule('threads-heartbeat-job');

-- Drop the functions
-- DROP FUNCTION IF EXISTS public.broadcast_realtime_heartbeat();
-- DROP FUNCTION IF EXISTS public.broadcast_threads_heartbeat();


-- ============================================================================
-- NOTES
-- ============================================================================
-- TWO HEARTBEAT CHANNELS:
-- 1. 'heartbeat-channel' - General keep-alive for all connections
-- 2. 'threads-realtime-channel' - Specific to threads subscription
--
-- BENEFITS:
-- 1. Both channels receive heartbeat broadcasts every 60 seconds
-- 2. Clients subscribe to channels to receive keep-alive pings
-- 3. If no heartbeat received in 90+ seconds, client knows connection is dead
-- 4. Eliminates need for frontend health check pings
-- 5. Server-authoritative connection state (more reliable)
-- 6. Uses Supabase's realtime.send() function (built-in)
-- 7. Replication slot broadcasts changes automatically
-- 8. Minimal overhead (~2 messages per minute total)
--
-- CHANNEL USAGE:
-- - heartbeat-channel: Generic connection health monitoring
-- - threads-realtime-channel: Keeps threads subscription alive
--
-- TROUBLESHOOTING:
-- - Check cron.job_run_details for errors (see monitoring queries above)
-- - Verify pg_cron extension is enabled
-- - Ensure realtime schema exists (it should by default)
-- - Check that realtime.messages table exists
-- - Verify replication slot is active
-- - Test manually: SELECT public.broadcast_threads_heartbeat();
-- ============================================================================
