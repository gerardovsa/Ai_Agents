-- ============================================================================
-- Migration 037: AI Model Catalog
-- Created: March 2026
-- Purpose: DB-driven registry of LLM models across providers.
--          Replaces hardcoded model lists in the frontend and backend.
--          Supports adding new models with zero code changes (just INSERT).
--          Intended to support future polling/refresh from provider APIs.
-- ============================================================================
-- Run twice safely: all operations use IF NOT EXISTS / ON CONFLICT DO NOTHING

-- ----------------------------------------------------------------------------
-- TABLE
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_infrastructure.ai_model_catalog (
    id               SERIAL       PRIMARY KEY,
    provider         VARCHAR(50)  NOT NULL,           -- 'anthropic' | 'openai' | 'deepseek'
    model_id         VARCHAR(200) NOT NULL,           -- exact API value sent in requests
    display_name     VARCHAR(200) NOT NULL,           -- human-readable label shown in UI
    description      TEXT,                            -- short capability summary
    tier             VARCHAR(50)  NOT NULL DEFAULT 'balanced',
                                                      -- 'fast' | 'balanced' | 'powerful' | 'reasoning'
    context_window   INTEGER,                         -- max input tokens
    is_recommended   BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    supports_tools   BOOLEAN      NOT NULL DEFAULT TRUE,  -- function/tool calling
    supports_vision  BOOLEAN      NOT NULL DEFAULT FALSE, -- image inputs
    supports_thinking BOOLEAN     NOT NULL DEFAULT FALSE, -- extended reasoning / interleaved thinking
    sort_order       INTEGER      NOT NULL DEFAULT 100,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (provider, model_id)
);

-- Index for fast per-provider lookups
CREATE INDEX IF NOT EXISTS ai_model_catalog_provider_idx
    ON ai_infrastructure.ai_model_catalog (provider, is_active, sort_order);

-- Auto-update updated_at on row changes
CREATE OR REPLACE FUNCTION ai_infrastructure.update_ai_model_catalog_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_ai_model_catalog_updated_at
    ON ai_infrastructure.ai_model_catalog;

CREATE TRIGGER trg_ai_model_catalog_updated_at
    BEFORE UPDATE ON ai_infrastructure.ai_model_catalog
    FOR EACH ROW EXECUTE FUNCTION ai_infrastructure.update_ai_model_catalog_updated_at();

-- ----------------------------------------------------------------------------
-- SEED DATA — Anthropic models
-- NOTE: model_id is the EXACT string sent to the Anthropic API.
--       claude-sonnet-4-6 and claude-opus-4-6 have NO date suffix — they are
--       aliases that always point to the latest snapshot of that model.
--       claude-haiku-4-5-20251001 uses a dated snapshot in its canonical ID.
--       Source: https://docs.anthropic.com/en/docs/about-claude/models/overview
-- ----------------------------------------------------------------------------
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision, supports_thinking, sort_order)
VALUES
    -- ── Claude Opus 4.6 — MOST POWERFUL ────────────────────────────────────
    ('anthropic', 'claude-opus-4-6',
     'Claude Opus 4.6',
     'Most intelligent Claude model. Best for complex coding, agents, and research tasks.',
     'powerful', 1000000, FALSE, TRUE, TRUE, TRUE, 5),

    -- ── Claude Sonnet 4.6 — RECOMMENDED ────────────────────────────────────
    ('anthropic', 'claude-sonnet-4-6',
     'Claude Sonnet 4.6',
     'Best balance of intelligence, speed, and cost. Recommended for most tasks.',
     'balanced', 1000000, TRUE, TRUE, TRUE, TRUE, 10),

    -- ── Claude Haiku 4.5 ───────────────────────────────────────────────────
    ('anthropic', 'claude-haiku-4-5-20251001',
     'Claude Haiku 4.5',
     'Fastest and most cost-efficient Claude. Great for high-volume tasks.',
     'fast', 200000, FALSE, TRUE, TRUE, TRUE, 30),

    -- ── Claude Sonnet 4.5 ──────────────────────────────────────────────────
    ('anthropic', 'claude-sonnet-4-5-20250929',
     'Claude Sonnet 4.5',
     'Previous Sonnet generation — high quality, proven stable.',
     'balanced', 200000, FALSE, TRUE, TRUE, TRUE, 40),

    -- ── Claude 3.7 Sonnet ──────────────────────────────────────────────────
    ('anthropic', 'claude-3-7-sonnet-20250219',
     'Claude 3.7 Sonnet',
     'Extended thinking pioneer. Great for deep analytical tasks.',
     'powerful', 200000, FALSE, TRUE, TRUE, TRUE, 50),

    -- ── Claude 3.5 Sonnet ──────────────────────────────────────────────────
    ('anthropic', 'claude-3-5-sonnet-20241022',
     'Claude 3.5 Sonnet',
     'Legacy model — kept for compatibility.',
     'balanced', 200000, FALSE, TRUE, TRUE, FALSE, 60)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- SEED DATA — OpenAI models
-- Source: https://developers.openai.com/api/docs/models
-- GPT-5.4 is the current frontier model as of March 2026.
-- ----------------------------------------------------------------------------
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision, supports_thinking, sort_order)
VALUES
    -- ── GPT-5.4 ── CURRENT FRONTIER ────────────────────────────────────────
    ('openai', 'gpt-5.4',
     'GPT-5.4',
     'OpenAI frontier model. Best intelligence at scale for agentic, coding, and professional work.',
     'powerful', 1050000, FALSE, TRUE, TRUE, TRUE, 100),

    -- ── GPT-5.1 ────────────────────────────────────────────────────────────
    ('openai', 'gpt-5.1',
     'GPT-5.1',
     'Best model for coding and agentic tasks. Configurable reasoning effort.',
     'powerful', 400000, FALSE, TRUE, TRUE, TRUE, 105),

    -- ── GPT-5 Mini ─────────────────────────────────────────────────────────
    ('openai', 'gpt-5-mini',
     'GPT-5 Mini',
     'Near-frontier intelligence for cost-sensitive, low-latency, high-volume workloads.',
     'fast', 400000, FALSE, TRUE, TRUE, FALSE, 108),

    -- ── GPT-4o ─────────────────────────────────────────────────────────────
    ('openai', 'gpt-4o',
     'GPT-4o',
     'Versatile multimodal model. Fast, smart, supports vision. Stable legacy choice.',
     'balanced', 128000, FALSE, TRUE, TRUE, FALSE, 110),

    -- ── GPT-4o Mini ────────────────────────────────────────────────────────
    ('openai', 'gpt-4o-mini',
     'GPT-4o Mini',
     'Lightweight GPT-4o variant — very fast and affordable.',
     'fast', 128000, FALSE, TRUE, TRUE, FALSE, 120),

    -- ── o3 ─────────────────────────────────────────────────────────────────
    ('openai', 'o3',
     'OpenAI o3',
     'Powerful reasoning model. Sets a new standard for math, science, coding, and visual reasoning.',
     'reasoning', 200000, FALSE, TRUE, TRUE, TRUE, 130),

    -- ── o4-mini ────────────────────────────────────────────────────────────
    ('openai', 'o4-mini',
     'OpenAI o4-mini',
     'Fast, cost-efficient reasoning. Optimised for coding and visual tasks.',
     'reasoning', 200000, FALSE, TRUE, TRUE, TRUE, 135),

    -- ── o3-mini ────────────────────────────────────────────────────────────
    ('openai', 'o3-mini',
     'OpenAI o3-mini',
     'Fast, affordable reasoning model. Great for STEM tasks.',
     'reasoning', 200000, FALSE, TRUE, FALSE, TRUE, 140),

    -- ── o1 ─────────────────────────────────────────────────────────────────
    ('openai', 'o1',
     'OpenAI o1',
     'Original frontier reasoning model. Deep thinking for hard analytical problems.',
     'reasoning', 200000, FALSE, TRUE, FALSE, TRUE, 150)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- SEED DATA — DeepSeek models
-- ----------------------------------------------------------------------------
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision, supports_thinking, sort_order)
VALUES
    -- ── DeepSeek Chat (V3) ─────────────────────────────────────────────────
    ('deepseek', 'deepseek-chat',
     'DeepSeek Chat (V3)',
     'DeepSeek V3 — fast, cost-efficient, excellent coding and instruction following.',
     'fast', 64000, FALSE, TRUE, FALSE, FALSE, 210),

    -- ── DeepSeek Reasoner (R1) ────────────────────────────────────────────
    ('deepseek', 'deepseek-reasoner',
     'DeepSeek Reasoner (R1)',
     'DeepSeek R1 reasoning model. Matches o1-level performance at a fraction of the cost.',
     'reasoning', 64000, FALSE, TRUE, FALSE, TRUE, 220)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ----------------------------------------------------------------------------
-- Verify
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt FROM ai_infrastructure.ai_model_catalog WHERE is_active = TRUE;
    RAISE NOTICE '[Migration 037] ai_model_catalog: % active models seeded.', cnt;
END $$;
