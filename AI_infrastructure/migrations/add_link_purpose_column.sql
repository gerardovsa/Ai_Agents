-- Migration: Add link_purpose column to oauth_tokens table
-- Date: December 2025
-- Purpose: Support primary (login) vs storage-only OAuth account linking
--
-- Architecture:
-- - User logs in with Google OR Microsoft (primary account = full API access)
-- - User can link opposite platform for storage only (Google Drive or OneDrive)
-- - link_purpose='primary' → Full API access (Gmail, Outlook, Calendar, Teams, etc.)
-- - link_purpose='storage' → Storage-only access (Drive or OneDrive only)

-- ✅ IDEMPOTENT: Add link_purpose column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'oauth_tokens'
        AND column_name = 'link_purpose'
    ) THEN
        ALTER TABLE oauth_tokens 
        ADD COLUMN link_purpose TEXT DEFAULT 'primary';
        
        RAISE NOTICE '✅ Added link_purpose column to oauth_tokens table';
    ELSE
        RAISE NOTICE '⏭️ link_purpose column already exists, skipping';
    END IF;
END $$;

-- ✅ BACKFILL: Update existing records to 'primary' (they were all login accounts)
UPDATE oauth_tokens 
SET link_purpose = 'primary' 
WHERE link_purpose IS NULL;

-- ✅ DOCUMENTATION: Add comment for future reference
COMMENT ON COLUMN oauth_tokens.link_purpose IS 
'Purpose of OAuth link: "primary" (full API access for login platform) or "storage" (Drive/OneDrive only for linked platform)';

-- ✅ VALIDATION: Check for any NULL values (should be 0)
DO $$
DECLARE
    null_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO null_count
    FROM oauth_tokens
    WHERE link_purpose IS NULL;
    
    IF null_count > 0 THEN
        RAISE WARNING '⚠️ Found % oauth_tokens records with NULL link_purpose', null_count;
    ELSE
        RAISE NOTICE '✅ All oauth_tokens records have link_purpose set';
    END IF;
END $$;

-- ✅ SUCCESS MESSAGE
DO $$
BEGIN
    RAISE NOTICE '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
    RAISE NOTICE '✅ Migration complete: link_purpose column added';
    RAISE NOTICE '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
    RAISE NOTICE 'Primary accounts (login platform): Full API access';
    RAISE NOTICE 'Storage accounts (linked platform): Drive/OneDrive only';
    RAISE NOTICE '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━';
END $$;
