-- Migration: Add Team Messaging Columns
-- Enables private messaging between team members using same user_id
-- Date: 2025-12-17

-- Add display_name columns to messages table
ALTER TABLE ai_infrastructure.messages
ADD COLUMN IF NOT EXISTS sender_display_name TEXT,
ADD COLUMN IF NOT EXISTS recipient_display_name TEXT,
ADD COLUMN IF NOT EXISTS sender_session_token TEXT,
ADD COLUMN IF NOT EXISTS recipient_session_token TEXT,
ADD COLUMN IF NOT EXISTS message_type TEXT DEFAULT 'cross_user';

-- Add comments explaining the columns
COMMENT ON COLUMN ai_infrastructure.messages.sender_display_name IS 'Display name of sender (e.g., "Bob (Mac)") - for team messaging';
COMMENT ON COLUMN ai_infrastructure.messages.recipient_display_name IS 'Display name of recipient (e.g., "Sarah (Windows)") - NULL for broadcast to all team members';
COMMENT ON COLUMN ai_infrastructure.messages.sender_session_token IS 'Session token of sender - for presence tracking';
COMMENT ON COLUMN ai_infrastructure.messages.recipient_session_token IS 'Session token of recipient - for specific session targeting';
COMMENT ON COLUMN ai_infrastructure.messages.message_type IS 'Message type: private (team member to team member), broadcast (to all team), cross_user (different user accounts)';

-- Create indexes for fast filtering
CREATE INDEX IF NOT EXISTS idx_messages_recipient_display 
ON ai_infrastructure.messages(recipient_user_id, recipient_display_name) 
WHERE recipient_display_name IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_messages_team_broadcast 
ON ai_infrastructure.messages(recipient_user_id) 
WHERE recipient_display_name IS NULL AND message_type = 'broadcast';

CREATE INDEX IF NOT EXISTS idx_messages_type 
ON ai_infrastructure.messages(message_type);

-- Verify the columns were added
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_schema = 'ai_infrastructure' 
AND table_name = 'messages' 
AND column_name IN ('sender_display_name', 'recipient_display_name', 
                     'sender_session_token', 'recipient_session_token', 'message_type')
ORDER BY ordinal_position;

-- Show sample query for team conversations
-- (This is just documentation, not executed)
/*
EXAMPLE QUERY: Get team conversations for user_id=5

SELECT 
    CASE 
        WHEN sender_id = 5 THEN recipient_id
        ELSE sender_id
    END as other_user_id,
    
    CASE 
        WHEN sender_id = 5 THEN recipient_display_name
        ELSE sender_display_name
    END as other_display_name,
    
    CASE 
        WHEN sender_id = 5 AND recipient_id = 5 THEN 'team'
        ELSE 'external'
    END as conversation_type,
    
    MAX(created_at) as last_message_time,
    
    COUNT(*) FILTER (
        WHERE recipient_id = 5 
        AND NOT (5 = ANY(read_by))
    ) as unread_count

FROM ai_infrastructure.messages
WHERE sender_id = 5 OR recipient_id = 5
GROUP BY other_user_id, other_display_name, conversation_type
ORDER BY last_message_time DESC;
*/

PRINT 'Migration complete: Team messaging columns added to messages table';
