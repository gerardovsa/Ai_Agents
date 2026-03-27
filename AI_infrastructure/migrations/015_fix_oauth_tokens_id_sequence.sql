-- Migration: Fix oauth_tokens ID column to use auto-increment sequence
-- Date: March 24, 2026
-- Issue: oauth_tokens.id has no DEFAULT value (integer not null, no sequence)
--        Causes every new Google/Microsoft OAuth login to fail with NOT NULL violation
--        User is created in ai_infrastructure.users but oauth_tokens INSERT fails
--        → JWT never issued → user redirected to error page, cannot log in
-- Status: IDEMPOTENT - Safe to run multiple times

-- Step 1: Create sequence if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_sequences
        WHERE schemaname = 'ai_infrastructure'
        AND sequencename = 'oauth_tokens_id_seq'
    ) THEN
        CREATE SEQUENCE ai_infrastructure.oauth_tokens_id_seq;
        RAISE NOTICE 'Created sequence: ai_infrastructure.oauth_tokens_id_seq';
    ELSE
        RAISE NOTICE 'Sequence already exists: ai_infrastructure.oauth_tokens_id_seq';
    END IF;
END
$$;

-- Step 2: Attach sequence as the DEFAULT for the id column
ALTER TABLE ai_infrastructure.oauth_tokens
    ALTER COLUMN id SET DEFAULT nextval('ai_infrastructure.oauth_tokens_id_seq');

-- Step 3: Set sequence ownership so it is dropped with the table
ALTER SEQUENCE ai_infrastructure.oauth_tokens_id_seq
OWNED BY ai_infrastructure.oauth_tokens.id;

-- Step 4: Sync sequence to current max id to prevent duplicate key violations
SELECT setval(
    'ai_infrastructure.oauth_tokens_id_seq',
    COALESCE((SELECT MAX(id) FROM ai_infrastructure.oauth_tokens), 0) + 1,
    false  -- false = next call returns this value (not value+1)
);

-- Verification
DO $$
DECLARE
    has_default boolean;
BEGIN
    SELECT column_default IS NOT NULL
    INTO has_default
    FROM information_schema.columns
    WHERE table_schema = 'ai_infrastructure'
      AND table_name   = 'oauth_tokens'
      AND column_name  = 'id';

    IF has_default THEN
        RAISE NOTICE '✅ oauth_tokens.id now has a DEFAULT (sequence attached)';
    ELSE
        RAISE WARNING '❌ oauth_tokens.id still has no DEFAULT – check migration';
    END IF;
END
$$;
