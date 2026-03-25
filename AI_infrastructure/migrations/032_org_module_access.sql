-- Migration 032: Organisation Module Access Control
-- Creates org_module_access (per-org overrides) and plan_modules (plan-tier defaults)
-- Run once in Supabase SQL editor

DO $$
BEGIN

    -- =========================================================
    -- 1. plan_modules: default modules included per plan tier
    -- =========================================================
    CREATE TABLE IF NOT EXISTS ai_infrastructure.plan_modules (
        plan_tier   VARCHAR(50)  NOT NULL,
        module_name VARCHAR(100) NOT NULL,
        PRIMARY KEY (plan_tier, module_name)
    );

    -- =========================================================
    -- 2. org_module_access: per-org overrides (enable/disable)
    --    NULL = use plan defaults; explicit row = explicit override
    -- =========================================================
    CREATE TABLE IF NOT EXISTS ai_infrastructure.org_module_access (
        id              SERIAL      PRIMARY KEY,
        organisation_id INTEGER     NOT NULL
                            REFERENCES ai_infrastructure.organisations(id)
                            ON DELETE CASCADE,
        module_name     VARCHAR(100) NOT NULL,
        is_enabled      BOOLEAN      NOT NULL DEFAULT TRUE,
        enabled_at      TIMESTAMPTZ  DEFAULT NOW(),
        enabled_by      INTEGER      REFERENCES ai_infrastructure.users(id) ON DELETE SET NULL,
        UNIQUE (organisation_id, module_name)
    );

    -- Indexes for fast lookup
    CREATE INDEX IF NOT EXISTS idx_org_module_access_org
        ON ai_infrastructure.org_module_access (organisation_id);

    -- =========================================================
    -- 3. Seed plan_modules defaults (idempotent via ON CONFLICT DO NOTHING)
    -- =========================================================

    -- FREE tier: core only
    INSERT INTO ai_infrastructure.plan_modules (plan_tier, module_name) VALUES
        ('free', 'core_chat'),
        ('free', 'documents'),
        ('free', 'prompt_library'),
        ('free', 'notifications')
    ON CONFLICT DO NOTHING;

    -- STARTER tier: free + search + synergy
    INSERT INTO ai_infrastructure.plan_modules (plan_tier, module_name) VALUES
        ('starter', 'core_chat'),
        ('starter', 'documents'),
        ('starter', 'prompt_library'),
        ('starter', 'notifications'),
        ('starter', 'universal_search'),
        ('starter', 'synergy'),
        ('starter', 'automation'),
        ('starter', 'thread_cards')
    ON CONFLICT DO NOTHING;

    -- PROFESSIONAL tier: starter + integrations
    INSERT INTO ai_infrastructure.plan_modules (plan_tier, module_name) VALUES
        ('professional', 'core_chat'),
        ('professional', 'documents'),
        ('professional', 'prompt_library'),
        ('professional', 'notifications'),
        ('professional', 'universal_search'),
        ('professional', 'synergy'),
        ('professional', 'automation'),
        ('professional', 'thread_cards'),
        ('professional', 'shopify'),
        ('professional', 'xero'),
        ('professional', 'auspost_shipping'),
        ('professional', 'stock_management'),
        ('professional', 'transcription'),
        ('professional', 'vector_database'),
        ('professional', 'customer_reactivation')
    ON CONFLICT DO NOTHING;

    -- ENTERPRISE tier: all modules
    INSERT INTO ai_infrastructure.plan_modules (plan_tier, module_name) VALUES
        ('enterprise', 'core_chat'),
        ('enterprise', 'documents'),
        ('enterprise', 'prompt_library'),
        ('enterprise', 'notifications'),
        ('enterprise', 'universal_search'),
        ('enterprise', 'synergy'),
        ('enterprise', 'automation'),
        ('enterprise', 'thread_cards'),
        ('enterprise', 'shopify'),
        ('enterprise', 'xero'),
        ('enterprise', 'auspost_shipping'),
        ('enterprise', 'stock_management'),
        ('enterprise', 'transcription'),
        ('enterprise', 'vector_database'),
        ('enterprise', 'customer_reactivation'),
        ('enterprise', 'inhouse_print'),
        ('enterprise', 'inhouse_kanban'),
        ('enterprise', 'quote_calculator'),
        ('enterprise', 'database_visualizer'),
        ('enterprise', 'github'),
        ('enterprise', 'render_management'),
        ('enterprise', 'local_filesystem'),
        ('enterprise', 'woocommerce')
    ON CONFLICT DO NOTHING;

    RAISE NOTICE 'Migration 032 complete: org_module_access + plan_modules seeded';

END $$;
