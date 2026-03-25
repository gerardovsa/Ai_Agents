-- Migration 029: Add organisation_id to sessions.threads (GAP-M2)
-- Purpose: Isolate conversation threads by organisation so admin can query
--          all org conversations and RLS can prevent cross-org access.
-- Idempotent: Uses ADD COLUMN IF NOT EXISTS + CREATE OR REPLACE trigger.
-- Date: 2026

DO $$
BEGIN
    -- 1. Add organisation_id column to sessions.threads
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'sessions'
          AND table_name   = 'threads'
          AND column_name  = 'organisation_id'
    ) THEN
        ALTER TABLE sessions.threads
            ADD COLUMN organisation_id INTEGER
                REFERENCES ai_infrastructure.organisations(id)
                ON DELETE SET NULL;
        RAISE NOTICE 'Added organisation_id to sessions.threads';
    ELSE
        RAISE NOTICE 'sessions.threads.organisation_id already exists, skipping';
    END IF;

    -- 2. Backfill from users table (user_id → organisation_id)
    UPDATE sessions.threads t
    SET organisation_id = u.organisation_id
    FROM ai_infrastructure.users u
    WHERE t.user_id = u.id
      AND t.organisation_id IS NULL
      AND u.organisation_id IS NOT NULL;

    RAISE NOTICE 'Backfilled organisation_id from users';

END $$;

-- 3. Index for org-scoped queries
CREATE INDEX IF NOT EXISTS idx_threads_organisation_id
    ON sessions.threads(organisation_id);

-- 4. Trigger: auto-fill organisation_id on INSERT from the user's current org
--    This avoids updating every INSERT call site across thread_routes.py etc.
CREATE OR REPLACE FUNCTION sessions.threads_set_org_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.organisation_id IS NULL AND NEW.user_id IS NOT NULL THEN
        SELECT organisation_id INTO NEW.organisation_id
        FROM ai_infrastructure.users
        WHERE id = NEW.user_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_threads_set_org_id ON sessions.threads;
CREATE TRIGGER trg_threads_set_org_id
    BEFORE INSERT ON sessions.threads
    FOR EACH ROW EXECUTE FUNCTION sessions.threads_set_org_id();

COMMENT ON COLUMN sessions.threads.organisation_id IS
    'FK to ai_infrastructure.organisations — auto-filled by trigger from user. Enables per-org thread isolation.';
