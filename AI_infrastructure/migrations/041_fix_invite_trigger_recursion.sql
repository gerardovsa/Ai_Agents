-- Migration 041: Fix recursive trigger on org_invitations table
-- Problem: trg_expire_invitations fired on EVERY INSERT/UPDATE on org_invitations,
--          including the UPDATE inside expire_pending_invitations() itself, causing
--          infinite recursion and "stack depth limit exceeded" errors.
-- Fix:     Add WHEN (pg_trigger_depth() = 0) guard so the trigger only fires on
--          top-level INSERT/UPDATE statements, not on recursive calls from within
--          the trigger function.
-- Applied to production: Yes (applied directly in session, March 2026)

-- Drop the old trigger (no recursion guard)
DROP TRIGGER IF EXISTS trg_expire_invitations ON ai_infrastructure.org_invitations;

-- Recreate with recursion guard
CREATE TRIGGER trg_expire_invitations
    AFTER INSERT OR UPDATE ON ai_infrastructure.org_invitations
    FOR EACH STATEMENT
    WHEN (pg_trigger_depth() = 0)
    EXECUTE FUNCTION ai_infrastructure.expire_pending_invitations();
