-- MIGRATION 047: Thread visibility + thread_members
-- Adds per-thread visibility control (personal / team / restricted)
-- Adds thread_members table for restricted-visibility member lists
-- Idempotent: safe to run multiple times

-- 1. Add visibility column to sessions.threads
ALTER TABLE sessions.threads
    ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'personal'
        CHECK (visibility IN ('personal', 'team', 'restricted'));

-- 2. Create thread_members table (for restricted threads)
CREATE TABLE IF NOT EXISTS sessions.thread_members (
    id          SERIAL PRIMARY KEY,
    thread_id   TEXT        NOT NULL REFERENCES sessions.threads(thread_slug) ON DELETE CASCADE,
    user_id     INTEGER     NOT NULL REFERENCES ai_infrastructure.users(id) ON DELETE CASCADE,
    can_write   BOOLEAN     NOT NULL DEFAULT TRUE,
    added_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    added_by    INTEGER     REFERENCES ai_infrastructure.users(id),
    UNIQUE (thread_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_thread_members_thread ON sessions.thread_members(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_members_user   ON sessions.thread_members(user_id);

-- 3. Backfill existing threads as personal (already the default, this is a no-op guard)
UPDATE sessions.threads SET visibility = 'personal' WHERE visibility IS NULL;
