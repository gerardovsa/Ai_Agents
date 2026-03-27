-- Migration 033: Add organisation_id to realtime_messages (GAP-L4)
-- Scopes direct messages and broadcasts to an organisation so users
-- in different orgs cannot see each other's messages.
--
-- Note: realtime_messages is in the ai_infrastructure schema (create_messages_table.sql
-- uses unqualified CREATE TABLE, which lands in ai_infrastructure due to search_path)

DO $$
BEGIN

    -- 1. Add organisation_id column (nullable so existing rows aren't broken)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'realtime_messages'
          AND column_name  = 'organisation_id'
    ) THEN
        ALTER TABLE ai_infrastructure.realtime_messages
            ADD COLUMN organisation_id INTEGER
                REFERENCES ai_infrastructure.organisations(id)
                ON DELETE SET NULL;

        RAISE NOTICE 'Column organisation_id added to realtime_messages';
    ELSE
        RAISE NOTICE 'Column organisation_id already exists on realtime_messages - skipping';
    END IF;

    -- 2. Index for fast per-org message queries
    CREATE INDEX IF NOT EXISTS idx_realtime_messages_org
        ON ai_infrastructure.realtime_messages (organisation_id, created_at DESC);

    -- 3. Backfill: assign existing messages to the sender's organisation
    UPDATE ai_infrastructure.realtime_messages rm
    SET    organisation_id = u.organisation_id
    FROM   ai_infrastructure.users u
    WHERE  rm.sender_user_id  = u.id
      AND  rm.organisation_id IS NULL
      AND  u.organisation_id  IS NOT NULL;

    -- 4. Also add organisation_id to message_reactions for consistent scoping
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'message_reactions'
          AND column_name  = 'organisation_id'
    ) THEN
        ALTER TABLE ai_infrastructure.message_reactions
            ADD COLUMN organisation_id INTEGER
                REFERENCES ai_infrastructure.organisations(id)
                ON DELETE SET NULL;

        -- Backfill via parent message
        UPDATE ai_infrastructure.message_reactions mr
        SET    organisation_id = rm.organisation_id
        FROM   ai_infrastructure.realtime_messages rm
        WHERE  mr.message_id = rm.message_id
          AND  mr.organisation_id IS NULL;

        RAISE NOTICE 'Column organisation_id added to message_reactions and backfilled';
    ELSE
        RAISE NOTICE 'Column organisation_id already exists on message_reactions - skipping';
    END IF;

    RAISE NOTICE 'Migration 033 complete: realtime_messages scoped to organisation';

END $$;
