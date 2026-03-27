-- Migration: Add message_source column for distinguishing user input from tool results
-- Date: January 13, 2026
-- Purpose: Enhance clarity between user messages and system-generated content

-- ========================================
-- STEP 1: Add message_source column
-- ========================================

ALTER TABLE sessions.messages 
ADD COLUMN IF NOT EXISTS message_source VARCHAR(50) DEFAULT 'user_input';

-- ========================================
-- STEP 2: Add index for performance
-- ========================================

CREATE INDEX IF NOT EXISTS idx_messages_source 
ON sessions.messages(message_source);

-- ========================================
-- STEP 3: Add check constraint for valid values
-- ========================================

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'messages_source_check'
    ) THEN
        ALTER TABLE sessions.messages 
        ADD CONSTRAINT messages_source_check 
        CHECK (message_source IN ('user_input', 'tool_result', 'assistant_output'));
    END IF;
END $$;

-- ========================================
-- STEP 4: Update existing records (backfill)
-- ========================================

-- Tag existing assistant messages
UPDATE sessions.messages 
SET message_source = 'assistant_output'
WHERE role = 'assistant' 
  AND message_source = 'user_input';

-- Tag existing tool_result messages
UPDATE sessions.messages 
SET message_source = 'tool_result'
WHERE role = 'user' 
  AND content::text LIKE '%"type":"tool_result"%'
  AND message_source = 'user_input';

-- ========================================
-- VERIFICATION QUERIES
-- ========================================

-- Check distribution
SELECT message_source, COUNT(*) as count 
FROM sessions.messages 
GROUP BY message_source;

-- Verify constraint
SELECT conname, consrc 
FROM pg_constraint 
WHERE conname = 'messages_source_check';

-- ========================================
-- ROLLBACK (if needed)
-- ========================================

-- To undo this migration:
-- DROP INDEX IF EXISTS idx_messages_source;
-- ALTER TABLE sessions.messages DROP CONSTRAINT IF EXISTS messages_source_check;
-- ALTER TABLE sessions.messages DROP COLUMN IF EXISTS message_source;
