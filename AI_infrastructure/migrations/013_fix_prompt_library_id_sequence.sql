-- Migration: Fix prompt_library ID column to use auto-increment sequence
-- Date: January 21, 2026
-- Issue: ID column has no default value, causing INSERT failures
-- Status: IDEMPOTENT - Safe to run multiple times

-- Step 1: Create sequence if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_sequences 
        WHERE schemaname = 'ai_infrastructure' 
        AND sequencename = 'prompt_library_id_seq'
    ) THEN
        CREATE SEQUENCE ai_infrastructure.prompt_library_id_seq;
        RAISE NOTICE 'Created sequence: ai_infrastructure.prompt_library_id_seq';
    ELSE
        RAISE NOTICE 'Sequence already exists: ai_infrastructure.prompt_library_id_seq';
    END IF;
END
$$;

-- Step 2: Set sequence ownership to the id column
ALTER SEQUENCE ai_infrastructure.prompt_library_id_seq 
OWNED BY ai_infrastructure.prompt_library.id;

-- Step 3: Update the sequence value to be higher than current max ID
-- This prevents duplicate key violations
SELECT setval(
    'ai_infrastructure.prompt_library_id_seq', 
    COALESCE((SELECT MAX(id) FROM ai_infrastructure.prompt_library), 0) + 1,
    false  -- Don't immediately consume the value
);

-- Step 4: Set the default value for id column to use the sequence
ALTER TABLE ai_infrastructure.prompt_library 
ALTER COLUMN id SET DEFAULT nextval('ai_infrastructure.prompt_library_id_seq');

-- Verify the fix
DO $$
DECLARE
    default_val text;
    seq_val bigint;
BEGIN
    -- Check default value
    SELECT column_default INTO default_val
    FROM information_schema.columns
    WHERE table_schema = 'ai_infrastructure'
    AND table_name = 'prompt_library'
    AND column_name = 'id';
    
    -- Check sequence value
    SELECT last_value INTO seq_val
    FROM ai_infrastructure.prompt_library_id_seq;
    
    RAISE NOTICE '✅ Migration complete!';
    RAISE NOTICE '   Default for id column: %', default_val;
    RAISE NOTICE '   Sequence current value: %', seq_val;
    RAISE NOTICE '   Next ID will be: %', seq_val + 1;
END
$$;
