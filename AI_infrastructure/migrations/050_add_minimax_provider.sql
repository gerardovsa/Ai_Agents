-- ============================================================================
-- Migration 050: MiniMax AI Provider
-- Created: June 10, 2026
-- Purpose: Add MiniMax as a fourth AI provider alongside Anthropic, OpenAI,
--          and DeepSeek.  MiniMax exposes an Anthropic-compatible endpoint
--          (https://api.minimax.io/anthropic) and an OpenAI-compatible
--          endpoint (https://api.minimax.io/v1).  We use the Anthropic-
--          compatible path because it natively supports interleaved thinking,
--          tool use, and the same content-block shape as Claude.
--
-- References:
--   - https://platform.minimax.io/docs
--   - https://www.minimax.io/models/text/m3
--
-- Idempotent: safe to run multiple times.  All INSERTs use ON CONFLICT DO NOTHING.
-- ============================================================================

-- =========================================================================
-- 1. Add MiniMax to platform_catalog  (drives Add-Connection modal in UI)
-- =========================================================================
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('MiniMax', 'MiniMax', 'fas fa-bolt', '#FF6A00', 'ai', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"eyJ...","required":true,"help_text":"Get your key from platform.minimax.io/user-center/payment/token-plan"},{"name":"base_url","label":"Base URL (optional)","type":"text","placeholder":"https://api.minimax.io/anthropic","required":false,"help_text":"Override only if you proxy the API. Default: https://api.minimax.io/anthropic"}]',
     'MiniMax M-series models (M3, M2.7, M2.5, M2.1, M2). Frontier 1M-context coding model with interleaved thinking and tool use.',
     'https://platform.minimax.io/docs', 14)

ON CONFLICT (platform_name) DO NOTHING;

-- =========================================================================
-- 2. Seed ai_model_catalog  with every supported MiniMax model
--    All models support tool use.  Only M3 supports vision, video input,
--    and Interleaved Thinking.  M2.7/M2.5/M2.1/M2 are text-only.
-- =========================================================================

-- ── MiniMax-M3 ── Frontier 1M-context multimodal coding model ───────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision,
     supports_thinking, sort_order)
VALUES
    ('MiniMax', 'MiniMax-M3',
     'MiniMax-M3',
     'Frontier multimodal coding model with 1M-token context, agentic reasoning, tool use, and Interleaved Thinking.',
     'powerful', 1000000, TRUE, TRUE, TRUE, TRUE, 230)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ── MiniMax-M2.7 ─────────────────────────────────────────────────────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision,
     supports_thinking, sort_order)
VALUES
    ('MiniMax', 'MiniMax-M2.7',
     'MiniMax-M2.7',
     'M-series model with recursive self-improvement. ~60 tps output.',
     'balanced', 204800, FALSE, TRUE, FALSE, FALSE, 235),
    ('MiniMax', 'MiniMax-M2.7-highspeed',
     'MiniMax-M2.7 Highspeed',
     'M2.7 with faster output (~100 tps). Same quality, more agile.',
     'fast', 204800, FALSE, TRUE, FALSE, FALSE, 236)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ── MiniMax-M2.5 ─────────────────────────────────────────────────────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision,
     supports_thinking, sort_order)
VALUES
    ('MiniMax', 'MiniMax-M2.5',
     'MiniMax-M2.5',
     'Peak performance, ultimate value, masters complex tasks. ~60 tps.',
     'balanced', 204800, FALSE, TRUE, FALSE, FALSE, 240),
    ('MiniMax', 'MiniMax-M2.5-highspeed',
     'MiniMax-M2.5 Highspeed',
     'M2.5 with faster output (~100 tps). Same quality, more agile.',
     'fast', 204800, FALSE, TRUE, FALSE, FALSE, 241)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ── MiniMax-M2.1 ─────────────────────────────────────────────────────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision,
     supports_thinking, sort_order)
VALUES
    ('MiniMax', 'MiniMax-M2.1',
     'MiniMax-M2.1',
     'Powerful multi-language programming with comprehensively enhanced experience. ~60 tps.',
     'balanced', 204800, FALSE, TRUE, FALSE, FALSE, 245),
    ('MiniMax', 'MiniMax-M2.1-highspeed',
     'MiniMax-M2.1 Highspeed',
     'Faster and more agile M2.1 variant. ~100 tps.',
     'fast', 204800, FALSE, TRUE, FALSE, FALSE, 246)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ── MiniMax-M2 ───────────────────────────────────────────────────────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision,
     supports_thinking, sort_order)
VALUES
    ('MiniMax', 'MiniMax-M2',
     'MiniMax-M2',
     'Agentic capabilities, advanced reasoning.',
     'balanced', 204800, FALSE, TRUE, FALSE, FALSE, 250)

ON CONFLICT (provider, model_id) DO NOTHING;

-- ── M2-her ── Dialogue / role-play model ─────────────────────────────────
INSERT INTO ai_infrastructure.ai_model_catalog
    (provider, model_id, display_name, description, tier,
     context_window, is_recommended, supports_tools, supports_vision,
     supports_thinking, sort_order)
VALUES
    ('MiniMax', 'M2-her',
     'MiniMax M2-her',
     'Designed for dialogue scenarios, supports role-playing and multi-turn conversations.',
     'fast', 65536, FALSE, TRUE, FALSE, FALSE, 255)

ON CONFLICT (provider, model_id) DO NOTHING;

-- =========================================================================
-- 3. Verify
-- =========================================================================
DO $$
DECLARE
    cnt INTEGER;
BEGIN
    SELECT COUNT(*) INTO cnt
    FROM ai_infrastructure.ai_model_catalog
    WHERE provider = 'MiniMax' AND is_active = TRUE;
    RAISE NOTICE '[Migration 050] MiniMax provider: % active models seeded.', cnt;
END $$;
