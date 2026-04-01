-- ============================================================================
-- Migration 039: Add Extended Fields to Organisations Table
-- ============================================================================
-- PURPOSE: Add missing columns to ai_infrastructure.organisations
-- - description: Organisation purpose/notes
-- - visibility: private | unlisted | public (for directory listing)
-- - allowed_domains: TEXT[] for SSO auto-provisioning
-- - ai_provider: Default AI provider (anthropic | openai | deepseek)
-- - ai_model: Default AI model name
-- - ai_max_tokens: Max tokens for AI requests
-- DATE: March 31, 2026
-- ============================================================================

BEGIN;

-- Add description column
ALTER TABLE ai_infrastructure.organisations
ADD COLUMN IF NOT EXISTS description TEXT;

-- Add visibility column (for directory/sharing)
ALTER TABLE ai_infrastructure.organisations
ADD COLUMN IF NOT EXISTS visibility VARCHAR(50) DEFAULT 'private' 
CHECK (visibility IN ('private', 'unlisted', 'public'));

-- Add allowed_domains for SSO auto-provisioning
ALTER TABLE ai_infrastructure.organisations
ADD COLUMN IF NOT EXISTS allowed_domains TEXT[];

-- Add AI configuration columns
ALTER TABLE ai_infrastructure.organisations
ADD COLUMN IF NOT EXISTS ai_provider VARCHAR(50) DEFAULT 'anthropic'
CHECK (ai_provider IN ('anthropic', 'openai', 'deepseek'));

ALTER TABLE ai_infrastructure.organisations
ADD COLUMN IF NOT EXISTS ai_model VARCHAR(255) DEFAULT '';

ALTER TABLE ai_infrastructure.organisations
ADD COLUMN IF NOT EXISTS ai_max_tokens INTEGER DEFAULT 8192 
CHECK (ai_max_tokens >= 1024 AND ai_max_tokens <= 32768);

-- Add comments for clarity
COMMENT ON COLUMN ai_infrastructure.organisations.description IS 
    'Organisation purpose, business type, or internal notes. Free-form text.';

COMMENT ON COLUMN ai_infrastructure.organisations.visibility IS 
    'Directory visibility: private (hidden), unlisted (invite-only), or public (searchable in directory).';

COMMENT ON COLUMN ai_infrastructure.organisations.allowed_domains IS 
    'Email domains allowed for SSO auto-provisioning. E.g. ARRAY[''acme.com'', ''mail.acme.com'']. NULL = no auto-provisioning.';

COMMENT ON COLUMN ai_infrastructure.organisations.ai_provider IS 
    'Default AI provider for this organisation: anthropic (Claude), openai (GPT), or deepseek (DeepSeek).';

COMMENT ON COLUMN ai_infrastructure.organisations.ai_model IS 
    'Default model name for the selected provider. E.g. claude-3-sonnet-20240229, gpt-4-turbo, deepseek-coder-33b.';

COMMENT ON COLUMN ai_infrastructure.organisations.ai_max_tokens IS 
    'Maximum tokens for AI completions (1024–32768). Default is 8192.';

-- Create index on visibility for faster directory lookups
CREATE INDEX IF NOT EXISTS idx_organisations_visibility ON ai_infrastructure.organisations(visibility);

COMMIT;
