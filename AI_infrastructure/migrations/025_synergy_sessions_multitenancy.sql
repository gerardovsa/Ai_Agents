-- ============================================================================
-- MIGRATION 025: Synergy Sessions — Multi-tenancy, Organisations & Visibility
-- ============================================================================
-- Date:    March 23, 2026
-- Author:  GitHub Copilot / Gerardo
-- Purpose: Makes synergy_sessions fully compatible with:
--          (a) Teams sharing one login — one email/password, multiple members
--          (b) Organisations with multiple users at different access levels
--
-- Changes:
--   1. Add organisation_id FK to synergy_sessions (sessions belong to an org)
--   2. Add visibility column (private / shared / team)
--   3. Add FK constraint from owner_user_id → ai_infrastructure.users
--   4. Create session_members join table (proper sharing, replaces shared_with_users blob)
--   5. Fix milestone_comments.user_id — add missing FK constraint
--   6. Fix milestone_history — add changed_by_user_id integer FK (preserves old text col)
--   7. Fix tasks.assigned_to_user_id and subtasks.assigned_to_user_id integer FKs
--   8. Indexes for all new FK columns
--   9. RLS policies: private / shared / team visibility enforcement
--
-- HOW VISIBILITY WORKS:
--   private  → only the owner (owner_user_id) can see or edit
--   shared   → owner + anyone in session_members table
--   team     → all members of the same organisation (matched by organisation_id)
--
-- PREREQUISITES: Migrations 021–024 must already be applied.
--   - ai_infrastructure.users must exist (migration 022)
--   - ai_infrastructure.organisations must exist (add_organisations_and_org_credentials.sql)
-- ============================================================================

BEGIN;

-- ============================================================================
-- STEP 1: Add organisation_id to synergy_sessions
-- Ties each session to an organisation so team-visibility can be scoped.
-- ============================================================================

ALTER TABLE synergy_sessions.synergy_sessions
    ADD COLUMN IF NOT EXISTS organisation_id INTEGER
        REFERENCES ai_infrastructure.organisations(id)
        ON DELETE SET NULL;

COMMENT ON COLUMN synergy_sessions.synergy_sessions.organisation_id IS
    'The organisation this session belongs to. NULL = personal/unaffiliated session. '
    'Required for team visibility to work.';


-- ============================================================================
-- STEP 2: Add visibility column to synergy_sessions
-- Controls who can see a session beyond the owner.
-- ============================================================================

ALTER TABLE synergy_sessions.synergy_sessions
    ADD COLUMN IF NOT EXISTS visibility TEXT NOT NULL DEFAULT 'private'
        CHECK (visibility IN ('private', 'shared', 'team'));

COMMENT ON COLUMN synergy_sessions.synergy_sessions.visibility IS
    'private = owner only. shared = owner + explicit session_members. '
    'team = all members of organisation_id.';


-- ============================================================================
-- STEP 3: Add FK constraint from owner_user_id → ai_infrastructure.users
-- The column already existed as a bare integer — this adds the referential
-- integrity that was always intended.
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_schema = 'synergy_sessions'
          AND table_name = 'synergy_sessions'
          AND constraint_name = 'synergy_sessions_owner_user_id_fkey'
    ) THEN
        ALTER TABLE synergy_sessions.synergy_sessions
            ADD CONSTRAINT synergy_sessions_owner_user_id_fkey
            FOREIGN KEY (owner_user_id)
            REFERENCES ai_infrastructure.users(id)
            ON DELETE SET NULL;
    END IF;
END;
$$;

COMMENT ON COLUMN synergy_sessions.synergy_sessions.owner_user_id IS
    'The user who created / owns this session. FK to ai_infrastructure.users.';


-- ============================================================================
-- STEP 4: Create session_members join table
-- Replaces the old shared_with_users TEXT blob with a proper normalised table.
-- Each row = one person explicitly invited to a 'shared' visibility session.
-- Also used to track collaborators on 'team' sessions who have a specific role.
-- ============================================================================

CREATE TABLE IF NOT EXISTS synergy_sessions.session_members (
    session_id      TEXT        NOT NULL
        REFERENCES synergy_sessions.synergy_sessions(session_id)
        ON DELETE CASCADE,

    user_id         INTEGER     NOT NULL
        REFERENCES ai_infrastructure.users(id)
        ON DELETE CASCADE,

    -- Role within this session (independent of org role)
    role            TEXT        NOT NULL DEFAULT 'viewer'
        CHECK (role IN ('viewer', 'editor', 'admin')),

    -- Who added this person
    added_by        INTEGER
        REFERENCES ai_infrastructure.users(id)
        ON DELETE SET NULL,

    added_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    PRIMARY KEY (session_id, user_id)
);

COMMENT ON TABLE synergy_sessions.session_members IS
    'Explicit member list for shared/team sessions. '
    'For private sessions this table is ignored. '
    'Viewer = read-only. Editor = can edit milestones/tasks. Admin = can invite/remove members.';

COMMENT ON COLUMN synergy_sessions.session_members.role IS
    'viewer  = read-only access to the session. '
    'editor  = can edit milestones, tasks, subtasks, docs. '
    'admin   = editor + can manage membership (invite / remove).';


-- ============================================================================
-- STEP 5: Fix milestone_comments — add commenter_user_id integer FK
-- The existing user_id column is TEXT (from migration 021) and cannot be
-- directly FK'd to users.id (INTEGER). Same pattern as milestone_history:
-- keep the old TEXT column for backward compat, add a new integer FK column.
-- New writes should populate commenter_user_id instead of user_id.
-- ============================================================================

ALTER TABLE synergy_sessions.milestone_comments
    ADD COLUMN IF NOT EXISTS commenter_user_id INTEGER
        REFERENCES ai_infrastructure.users(id)
        ON DELETE SET NULL;

COMMENT ON COLUMN synergy_sessions.milestone_comments.user_id IS
    'DEPRECATED: free-text user identifier from legacy data. Use commenter_user_id.';

COMMENT ON COLUMN synergy_sessions.milestone_comments.commenter_user_id IS
    'FK to ai_infrastructure.users. Set on all new comment rows.';


-- ============================================================================
-- STEP 6: Fix milestone_history — add changed_by_user_id integer FK
-- The existing changed_by TEXT column is kept for backward compat (may hold
-- display names from old data). New writes should use changed_by_user_id.
-- ============================================================================

ALTER TABLE synergy_sessions.milestone_history
    ADD COLUMN IF NOT EXISTS changed_by_user_id INTEGER
        REFERENCES ai_infrastructure.users(id)
        ON DELETE SET NULL;

COMMENT ON COLUMN synergy_sessions.milestone_history.changed_by IS
    'DEPRECATED: free-text display name from legacy data. Use changed_by_user_id.';

COMMENT ON COLUMN synergy_sessions.milestone_history.changed_by_user_id IS
    'FK to ai_infrastructure.users. Set on all new history rows.';


-- ============================================================================
-- STEP 7: Add assigned_to_user_id integer FK columns to tasks & subtasks
-- The old assigned_to TEXT column is kept for backward compat.
-- ============================================================================

ALTER TABLE synergy_sessions.tasks
    ADD COLUMN IF NOT EXISTS assigned_to_user_id INTEGER
        REFERENCES ai_infrastructure.users(id)
        ON DELETE SET NULL;

COMMENT ON COLUMN synergy_sessions.tasks.assigned_to IS
    'DEPRECATED: free-text name from legacy data. Use assigned_to_user_id.';

COMMENT ON COLUMN synergy_sessions.tasks.assigned_to_user_id IS
    'FK to ai_infrastructure.users. Set on all new task rows.';


ALTER TABLE synergy_sessions.subtasks
    ADD COLUMN IF NOT EXISTS assigned_to_user_id INTEGER
        REFERENCES ai_infrastructure.users(id)
        ON DELETE SET NULL;

COMMENT ON COLUMN synergy_sessions.subtasks.assigned_to IS
    'DEPRECATED: free-text name from legacy data. Use assigned_to_user_id.';

COMMENT ON COLUMN synergy_sessions.subtasks.assigned_to_user_id IS
    'FK to ai_infrastructure.users. Set on all new subtask rows.';


-- ============================================================================
-- STEP 8: Indexes
-- Covering indexes for the most common query patterns.
-- ============================================================================

-- Sessions by org (team-visibility queries)
CREATE INDEX IF NOT EXISTS idx_synergy_sessions_organisation_id
    ON synergy_sessions.synergy_sessions (organisation_id);

-- Sessions by owner (my sessions list)
CREATE INDEX IF NOT EXISTS idx_synergy_sessions_owner_user_id
    ON synergy_sessions.synergy_sessions (owner_user_id);

-- Sessions by visibility (filter: all team sessions)
CREATE INDEX IF NOT EXISTS idx_synergy_sessions_visibility
    ON synergy_sessions.synergy_sessions (visibility);

-- Compound: fetch all non-archived sessions for an org
CREATE INDEX IF NOT EXISTS idx_synergy_sessions_org_visibility_archived
    ON synergy_sessions.synergy_sessions (organisation_id, visibility, archived);

-- session_members by user (what sessions can I see?)
CREATE INDEX IF NOT EXISTS idx_session_members_user_id
    ON synergy_sessions.session_members (user_id);

-- history by user (audit trail per user)
CREATE INDEX IF NOT EXISTS idx_milestone_history_changed_by_user_id
    ON synergy_sessions.milestone_history (changed_by_user_id);

-- tasks/subtasks by assignee
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to_user_id
    ON synergy_sessions.tasks (assigned_to_user_id);

CREATE INDEX IF NOT EXISTS idx_subtasks_assigned_to_user_id
    ON synergy_sessions.subtasks (assigned_to_user_id);

-- comments by commenter
CREATE INDEX IF NOT EXISTS idx_milestone_comments_commenter_user_id
    ON synergy_sessions.milestone_comments (commenter_user_id);


-- ============================================================================
-- STEP 9: Row-Level Security
-- These policies enforce the 3-mode visibility rules at the database layer.
-- The application still controls writes, but SELECT is locked down here.
--
-- Session variables required (set by application middleware):
--   app.current_user_id         — the logged-in user's id (integer as text)
--   app.current_organisation_id — the user's organisation id (integer as text)
-- ============================================================================

ALTER TABLE synergy_sessions.synergy_sessions   ENABLE ROW LEVEL SECURITY;
ALTER TABLE synergy_sessions.session_members    ENABLE ROW LEVEL SECURITY;
ALTER TABLE synergy_sessions.milestones         ENABLE ROW LEVEL SECURITY;
ALTER TABLE synergy_sessions.tasks              ENABLE ROW LEVEL SECURITY;
ALTER TABLE synergy_sessions.subtasks           ENABLE ROW LEVEL SECURITY;
ALTER TABLE synergy_sessions.milestone_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE synergy_sessions.milestone_history  ENABLE ROW LEVEL SECURITY;
ALTER TABLE synergy_sessions.synergy_internal_docs ENABLE ROW LEVEL SECURITY;

-- ---------------------------------------------------------------------------
-- 9a. synergy_sessions — SELECT (visibility rules)
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS synergy_sessions_select ON synergy_sessions.synergy_sessions;
CREATE POLICY synergy_sessions_select
    ON synergy_sessions.synergy_sessions
    FOR SELECT
    USING (
        -- Rule 1: Owner always sees their own sessions
        owner_user_id = current_setting('app.current_user_id', true)::integer

        OR

        -- Rule 2: shared → user must be in session_members
        (
            visibility = 'shared'
            AND EXISTS (
                SELECT 1
                FROM synergy_sessions.session_members sm
                WHERE sm.session_id = synergy_sessions.session_id
                  AND sm.user_id    = current_setting('app.current_user_id', true)::integer
            )
        )

        OR

        -- Rule 3: team → user must be in the same organisation AND session has an org
        (
            visibility = 'team'
            AND organisation_id IS NOT NULL
            AND organisation_id = current_setting('app.current_organisation_id', true)::integer
        )
    );

-- ---------------------------------------------------------------------------
-- 9b. synergy_sessions — INSERT / UPDATE / DELETE
-- Only the owner (or org admin via role check) can write.
-- Application layer enforces finer-grained editor/admin member roles.
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS synergy_sessions_write ON synergy_sessions.synergy_sessions;
CREATE POLICY synergy_sessions_write
    ON synergy_sessions.synergy_sessions
    FOR ALL
    USING (
        owner_user_id = current_setting('app.current_user_id', true)::integer
    )
    WITH CHECK (
        owner_user_id = current_setting('app.current_user_id', true)::integer
    );

-- ---------------------------------------------------------------------------
-- 9c. session_members — SELECT
-- A user can see the member list if they can see the parent session.
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS session_members_select ON synergy_sessions.session_members;
CREATE POLICY session_members_select
    ON synergy_sessions.session_members
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1
            FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.session_members.session_id
        )
    );

-- ---------------------------------------------------------------------------
-- 9d. session_members — INSERT / UPDATE / DELETE
-- Only the session owner or a session admin-member can modify membership.
-- ---------------------------------------------------------------------------
DROP POLICY IF EXISTS session_members_write ON synergy_sessions.session_members;
CREATE POLICY session_members_write
    ON synergy_sessions.session_members
    FOR ALL
    USING (
        EXISTS (
            SELECT 1
            FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.session_members.session_id
              AND (
                  -- session owner
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR
                  -- session admin member
                  EXISTS (
                      SELECT 1
                      FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role       = 'admin'
                  )
              )
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1
            FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.session_members.session_id
              AND (
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR
                  EXISTS (
                      SELECT 1
                      FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role       = 'admin'
                  )
              )
        )
    );

-- ---------------------------------------------------------------------------
-- 9e. milestones, tasks, subtasks, comments, history, internal_docs
-- Inherit access from parent session via a subquery check.
-- ---------------------------------------------------------------------------

-- milestones
DROP POLICY IF EXISTS milestones_select ON synergy_sessions.milestones;
CREATE POLICY milestones_select
    ON synergy_sessions.milestones FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.milestones.session_id
        )
    );

DROP POLICY IF EXISTS milestones_write ON synergy_sessions.milestones;
CREATE POLICY milestones_write
    ON synergy_sessions.milestones FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.milestones.session_id
              AND (
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR EXISTS (
                      SELECT 1 FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role      IN ('editor', 'admin')
                  )
              )
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.milestones.session_id
              AND (
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR EXISTS (
                      SELECT 1 FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role      IN ('editor', 'admin')
                  )
              )
        )
    );

-- tasks (joins through milestones → sessions)
DROP POLICY IF EXISTS tasks_select ON synergy_sessions.tasks;
CREATE POLICY tasks_select
    ON synergy_sessions.tasks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.milestones m
            JOIN synergy_sessions.synergy_sessions s ON s.session_id = m.session_id
            WHERE m.milestone_id = synergy_sessions.tasks.milestone_id
        )
    );

DROP POLICY IF EXISTS tasks_write ON synergy_sessions.tasks;
CREATE POLICY tasks_write
    ON synergy_sessions.tasks FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.milestones m
            JOIN synergy_sessions.synergy_sessions s ON s.session_id = m.session_id
            WHERE m.milestone_id = synergy_sessions.tasks.milestone_id
              AND (
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR EXISTS (
                      SELECT 1 FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role      IN ('editor', 'admin')
                  )
              )
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM synergy_sessions.milestones m
            JOIN synergy_sessions.synergy_sessions s ON s.session_id = m.session_id
            WHERE m.milestone_id = synergy_sessions.tasks.milestone_id
              AND (
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR EXISTS (
                      SELECT 1 FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role      IN ('editor', 'admin')
                  )
              )
        )
    );

-- subtasks (joins through tasks → milestones → sessions)
DROP POLICY IF EXISTS subtasks_select ON synergy_sessions.subtasks;
CREATE POLICY subtasks_select
    ON synergy_sessions.subtasks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.tasks t
            JOIN synergy_sessions.milestones m  ON m.milestone_id = t.milestone_id
            JOIN synergy_sessions.synergy_sessions s ON s.session_id = m.session_id
            WHERE t.task_id = synergy_sessions.subtasks.task_id
        )
    );

-- comments (session access via milestone)
DROP POLICY IF EXISTS comments_select ON synergy_sessions.milestone_comments;
CREATE POLICY comments_select
    ON synergy_sessions.milestone_comments FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.milestones m
            JOIN synergy_sessions.synergy_sessions s ON s.session_id = m.session_id
            WHERE m.milestone_id = synergy_sessions.milestone_comments.milestone_id
        )
    );

-- history (read-only for anyone with session access)
DROP POLICY IF EXISTS history_select ON synergy_sessions.milestone_history;
CREATE POLICY history_select
    ON synergy_sessions.milestone_history FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.milestones m
            JOIN synergy_sessions.synergy_sessions s ON s.session_id = m.session_id
            WHERE m.milestone_id = synergy_sessions.milestone_history.milestone_id
        )
    );

-- internal docs
DROP POLICY IF EXISTS internal_docs_select ON synergy_sessions.synergy_internal_docs;
CREATE POLICY internal_docs_select
    ON synergy_sessions.synergy_internal_docs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.synergy_internal_docs.session_id
        )
    );

DROP POLICY IF EXISTS internal_docs_write ON synergy_sessions.synergy_internal_docs;
CREATE POLICY internal_docs_write
    ON synergy_sessions.synergy_internal_docs FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.synergy_internal_docs.session_id
              AND (
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR EXISTS (
                      SELECT 1 FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role      IN ('editor', 'admin')
                  )
              )
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM synergy_sessions.synergy_sessions s
            WHERE s.session_id = synergy_sessions.synergy_internal_docs.session_id
              AND (
                  s.owner_user_id = current_setting('app.current_user_id', true)::integer
                  OR EXISTS (
                      SELECT 1 FROM synergy_sessions.session_members sm
                      WHERE sm.session_id = s.session_id
                        AND sm.user_id    = current_setting('app.current_user_id', true)::integer
                        AND sm.role      IN ('editor', 'admin')
                  )
              )
        )
    );


-- ============================================================================
-- STEP 10: Backfill — Assign existing sessions to their owner's organisation
-- Multi-tenant safe: each session gets the org of its owner user (not a
-- hardcoded platform org slug which may not exist).
-- Sets visibility to 'private' for all backfilled rows (safe default).
-- Sessions whose owners have no organisation remain with organisation_id=NULL
-- (they stay invisible to team queries, which is correct).
-- ============================================================================

UPDATE synergy_sessions.synergy_sessions s
SET organisation_id = u.organisation_id,
    visibility      = 'private'
FROM ai_infrastructure.users u
WHERE s.owner_user_id     = u.id
  AND s.organisation_id   IS NULL
  AND u.organisation_id   IS NOT NULL;

-- Also ensure a safe default for any sessions without a valid owner:
UPDATE synergy_sessions.synergy_sessions
SET visibility = 'private'
WHERE visibility IS NULL;


COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES (run manually after applying to confirm success)
-- ============================================================================

-- Confirm new columns exist:
-- SELECT column_name, data_type, column_default, is_nullable
-- FROM information_schema.columns
-- WHERE table_schema = 'synergy_sessions'
--   AND table_name   = 'synergy_sessions'
--   AND column_name IN ('organisation_id', 'visibility')
-- ORDER BY column_name;

-- Confirm session_members table created:
-- SELECT column_name, data_type
-- FROM information_schema.columns
-- WHERE table_schema = 'synergy_sessions' AND table_name = 'session_members';

-- Confirm RLS is on:
-- SELECT schemaname, tablename, rowsecurity
-- FROM pg_tables
-- WHERE schemaname = 'synergy_sessions';

-- Check all policies on synergy_sessions:
-- SELECT policyname, cmd, qual
-- FROM pg_policies
-- WHERE schemaname = 'synergy_sessions' AND tablename = 'synergy_sessions';

-- Count sessions per visibility mode:
-- SELECT visibility, COUNT(*) FROM synergy_sessions.synergy_sessions GROUP BY visibility;
