-- ============================================================================
-- MIGRATION 042: Track Email Sent Status on Org Invitations
-- ============================================================================
-- Date:    April 8, 2026
-- Purpose: Track whether invitation email was successfully sent
--          Allows UI to show "Sent Via Gmail" status vs "Send via Gmail" button
-- ============================================================================

BEGIN;

-- Add email_sent tracking columns to org_invitations
ALTER TABLE ai_infrastructure.org_invitations
    ADD COLUMN IF NOT EXISTS email_sent BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS email_sent_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS email_sent_provider VARCHAR(50); -- 'gmail' or 'outlook'

COMMENT ON COLUMN ai_infrastructure.org_invitations.email_sent IS
    'Whether the invitation email was successfully sent to the invited_email address.';

COMMENT ON COLUMN ai_infrastructure.org_invitations.email_sent_at IS
    'Timestamp when the invitation email was most recently sent.';

COMMENT ON COLUMN ai_infrastructure.org_invitations.email_sent_provider IS
    'Email provider used to send the invitation (gmail or outlook).';

-- Create index for finding invites that had email sent
CREATE INDEX IF NOT EXISTS idx_org_invitations_email_sent
    ON ai_infrastructure.org_invitations (organisation_id, email_sent);

COMMIT;
