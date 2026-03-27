-- Migration 031: Add per-org AI provider and model columns (GAP-M3)
-- Purpose: Each organisation can choose its own AI provider and model.
--          UnifiedAIClient reads these to route requests to the correct provider.
-- Idempotent: uses ADD COLUMN IF NOT EXISTS.
-- Date: 2026

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'organisations'
          AND column_name  = 'ai_provider'
    ) THEN
        ALTER TABLE ai_infrastructure.organisations
            ADD COLUMN ai_provider VARCHAR(50)  DEFAULT 'anthropic',
            ADD COLUMN ai_model    VARCHAR(100) DEFAULT 'claude-sonnet-4-5-20250929',
            ADD COLUMN ai_max_tokens INTEGER    DEFAULT 8192;
        RAISE NOTICE 'Added ai_provider, ai_model, ai_max_tokens to ai_infrastructure.organisations';
    ELSE
        RAISE NOTICE 'ai_provider already exists on organisations, skipping';
    END IF;
END $$;

-- Constraint: restrict to known providers to prevent arbitrary string injection
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'chk_organisations_ai_provider'
          AND table_schema    = 'ai_infrastructure'
    ) THEN
        ALTER TABLE ai_infrastructure.organisations
            ADD CONSTRAINT chk_organisations_ai_provider
            CHECK (ai_provider IN ('anthropic', 'openai', 'deepseek'));
        RAISE NOTICE 'Added CHECK constraint on ai_provider';
    ELSE
        RAISE NOTICE 'Constraint chk_organisations_ai_provider already exists, skipping';
    END IF;
END $$;

COMMENT ON COLUMN ai_infrastructure.organisations.ai_provider IS
    'AI provider for this org: anthropic | openai | deepseek (default: anthropic)';
COMMENT ON COLUMN ai_infrastructure.organisations.ai_model IS
    'AI model identifier, e.g. claude-sonnet-4-5-20250929 / gpt-4o / deepseek-chat';
COMMENT ON COLUMN ai_infrastructure.organisations.ai_max_tokens IS
    'Max tokens for AI responses (default: 8192)';
