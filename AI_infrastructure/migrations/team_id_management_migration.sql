-- Team ID Management System - Database Migration
-- Date: December 17, 2025
-- Purpose: Add Team ID routing columns to messages table

-- ============================================
-- ADD TEAM ID COLUMNS TO MESSAGES TABLE
-- ============================================

-- Add sender_team_id column (username of sender)
ALTER TABLE sessions.messages
ADD COLUMN IF NOT EXISTS sender_team_id TEXT;

-- Add recipient_team_id column (username of recipient, NULL for broadcast)
ALTER TABLE sessions.messages
ADD COLUMN IF NOT EXISTS recipient_team_id TEXT;

-- Add message_type column (private, broadcast, cross_user)
ALTER TABLE sessions.messages
ADD COLUMN IF NOT EXISTS message_type TEXT DEFAULT 'private';

-- ============================================
-- CREATE INDEXES FOR FAST MESSAGE FILTERING
-- ============================================

-- Index for filtering by sender
CREATE INDEX IF NOT EXISTS idx_messages_sender_team_id 
ON sessions.messages(sender_team_id);

-- Index for filtering by recipient
CREATE INDEX IF NOT EXISTS idx_messages_recipient_team_id 
ON sessions.messages(recipient_team_id);

-- Composite index for user + team routing
CREATE INDEX IF NOT EXISTS idx_messages_user_team 
ON sessions.messages(user_id, sender_team_id, recipient_team_id);

-- Index for message type filtering
CREATE INDEX IF NOT EXISTS idx_messages_message_type 
ON sessions.messages(message_type);

-- ============================================
-- VERIFY USERS TABLE HAS TEAM ID COLUMNS
-- ============================================

-- Check and add parent_user_id if missing
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'users' 
        AND column_name = 'parent_user_id'
    ) THEN
        ALTER TABLE ai_infrastructure.users 
        ADD COLUMN parent_user_id INTEGER REFERENCES ai_infrastructure.users(id);
        RAISE NOTICE 'Added parent_user_id column';
    END IF;
END $$;

-- Check and add is_sub_user if missing
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'users' 
        AND column_name = 'is_sub_user'
    ) THEN
        ALTER TABLE ai_infrastructure.users 
        ADD COLUMN is_sub_user BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added is_sub_user column';
    END IF;
END $$;

-- Check and add display_name if missing (for backward compatibility)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'ai_infrastructure' 
        AND table_name = 'users' 
        AND column_name = 'display_name'
    ) THEN
        ALTER TABLE ai_infrastructure.users 
        ADD COLUMN display_name TEXT;
        RAISE NOTICE 'Added display_name column';
    END IF;
END $$;

-- ============================================
-- CREATE INDEXES ON USERS TABLE
-- ============================================

-- Index for finding Team IDs by parent user
CREATE INDEX IF NOT EXISTS idx_users_parent_user_id 
ON ai_infrastructure.users(parent_user_id);

-- Index for filtering sub-users
CREATE INDEX IF NOT EXISTS idx_users_is_sub_user 
ON ai_infrastructure.users(is_sub_user);

-- Index for username lookups (Team ID lookups)
CREATE INDEX IF NOT EXISTS idx_users_username 
ON ai_infrastructure.users(username);

-- Composite index for parent + sub-user queries
CREATE INDEX IF NOT EXISTS idx_users_parent_subuser 
ON ai_infrastructure.users(parent_user_id, is_sub_user)
WHERE is_sub_user = TRUE;

-- ============================================
-- VERIFY SCHEMA
-- ============================================

-- Show messages table columns
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'sessions' 
    AND table_name = 'messages'
    AND column_name IN ('sender_team_id', 'recipient_team_id', 'message_type')
ORDER BY ordinal_position;

-- Show users table Team ID columns
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'ai_infrastructure' 
    AND table_name = 'users'
    AND column_name IN ('parent_user_id', 'is_sub_user', 'display_name', 'username')
ORDER BY ordinal_position;

-- ============================================
-- MIGRATION COMPLETE
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ TEAM ID MIGRATION COMPLETE';
    RAISE NOTICE '========================================';
    RAISE NOTICE '';
    RAISE NOTICE 'Added columns to messages table:';
    RAISE NOTICE '  - sender_team_id TEXT';
    RAISE NOTICE '  - recipient_team_id TEXT';
    RAISE NOTICE '  - message_type TEXT';
    RAISE NOTICE '';
    RAISE NOTICE 'Created indexes:';
    RAISE NOTICE '  - idx_messages_sender_team_id';
    RAISE NOTICE '  - idx_messages_recipient_team_id';
    RAISE NOTICE '  - idx_messages_user_team';
    RAISE NOTICE '  - idx_messages_message_type';
    RAISE NOTICE '  - idx_users_parent_user_id';
    RAISE NOTICE '  - idx_users_is_sub_user';
    RAISE NOTICE '  - idx_users_username';
    RAISE NOTICE '  - idx_users_parent_subuser';
    RAISE NOTICE '';
    RAISE NOTICE 'Ready for Team ID Management implementation!';
    RAISE NOTICE '========================================';
END $$;
