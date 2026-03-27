-- Migration: Add display_name column to users table
-- For multi-person collaboration on shared accounts
-- Date: 2025-12-17

-- Add display_name column to users table
ALTER TABLE ai_infrastructure.users 
ADD COLUMN display_name TEXT;

-- Add comment explaining the column
COMMENT ON COLUMN ai_infrastructure.users.display_name IS 'Display name for multi-person collaboration - shown to other users viewing same agent columns';

-- Optional: Set default display_name from username for existing users
UPDATE ai_infrastructure.users 
SET display_name = username 
WHERE display_name IS NULL AND username IS NOT NULL;

-- Verify the column was added
SELECT column_name, data_type, character_maximum_length 
FROM information_schema.columns 
WHERE table_schema = 'ai_infrastructure' 
AND table_name = 'users' 
AND column_name = 'display_name';
