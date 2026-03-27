-- Migration 009: Rename 'prime' location to 'unassigned'
-- Purpose: Separate unassigned state from Prime AI panel state
-- Date: December 27, 2025
-- Idempotent: Can be run multiple times safely

BEGIN;

-- Drop old constraint
ALTER TABLE sessions.threads 
DROP CONSTRAINT IF EXISTS chk_location_valid;

-- Add new constraint with "unassigned"
ALTER TABLE sessions.threads 
ADD CONSTRAINT chk_location_valid 
CHECK (
    location IN (
        'unassigned',
        'prime',
        'prime-loaded',
        'agent-1', 'agent-2', 'agent-3', 'agent-4', 'agent-5',
        'agent-6', 'agent-7', 'agent-8', 'agent-9', 'agent-10',
        'agent-11', 'agent-12', 'agent-13', 'agent-14', 'agent-15',
        'agent-16', 'agent-17', 'agent-18', 'agent-19', 'agent-20',
        'agent-21', 'agent-22', 'agent-23', 'agent-24', 'agent-25',
        'agent-26', 'synergy'
    )
);

-- Update all threads currently at 'prime' to 'unassigned'
UPDATE sessions.threads 
SET location = 'unassigned', updated_at = CURRENT_TIMESTAMP
WHERE location = 'prime';

-- Update relation_threads table
UPDATE sessions.relation_threads 
SET location = 'unassigned'
WHERE location = 'prime';

-- Verify migration
DO $$
DECLARE
    unassigned_count INTEGER;
    prime_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO unassigned_count FROM sessions.threads WHERE location = 'unassigned';
    SELECT COUNT(*) INTO prime_count FROM sessions.threads WHERE location = 'prime';
    
    RAISE NOTICE 'Migration complete: % threads now unassigned, % threads in prime', 
        unassigned_count, prime_count;
END $$;

COMMIT;
