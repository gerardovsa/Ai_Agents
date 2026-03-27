-- Migration 010: Remove 'prime-loaded' location value
-- Date: December 29, 2025
-- Purpose: Simplify location to just 3 values: 'prime', 'agent-N', 'unassigned'
-- 
-- RATIONALE:
-- - 'prime' = Thread displayed in AI Prime sidebar
-- - 'agent-N' = Thread displayed in Command Center agent column (N = 1-26)
-- - 'unassigned' = Thread not assigned anywhere
-- - Remove 'prime-loaded' (no longer needed - was used to mark auto-load thread)

BEGIN;

-- Step 1: Update any remaining 'prime-loaded' threads to 'prime'
UPDATE sessions.threads
SET location = 'prime', updated_at = CURRENT_TIMESTAMP
WHERE location = 'prime-loaded';

-- Step 2: Drop old constraint
ALTER TABLE sessions.threads DROP CONSTRAINT IF EXISTS chk_location_valid;

-- Step 3: Create new constraint WITHOUT 'prime-loaded'
ALTER TABLE sessions.threads ADD CONSTRAINT chk_location_valid CHECK (
  location = ANY (ARRAY[
    'unassigned'::text,
    'prime'::text,
    'agent-1'::text,
    'agent-2'::text,
    'agent-3'::text,
    'agent-4'::text,
    'agent-5'::text,
    'agent-6'::text,
    'agent-7'::text,
    'agent-8'::text,
    'agent-9'::text,
    'agent-10'::text,
    'agent-11'::text,
    'agent-12'::text,
    'agent-13'::text,
    'agent-14'::text,
    'agent-15'::text,
    'agent-16'::text,
    'agent-17'::text,
    'agent-18'::text,
    'agent-19'::text,
    'agent-20'::text,
    'agent-21'::text,
    'agent-22'::text,
    'agent-23'::text,
    'agent-24'::text,
    'agent-25'::text,
    'agent-26'::text,
    'synergy'::text
  ])
);

-- Step 4: Verify no prime-loaded threads remain
DO $$
DECLARE
  remaining_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO remaining_count
  FROM sessions.threads
  WHERE location = 'prime-loaded';
  
  IF remaining_count > 0 THEN
    RAISE EXCEPTION 'Migration failed: % threads still have location=prime-loaded', remaining_count;
  END IF;
  
  RAISE NOTICE '✅ Migration successful: No prime-loaded threads remain';
  RAISE NOTICE '✅ Valid locations now: prime, agent-1 to agent-26, unassigned, synergy';
END $$;

COMMIT;
