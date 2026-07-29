-- ============================================================================
-- Migration 052: Vector DB Provider Multi-Tenancy Config (Option A: Active + Secondary)
-- Created: 2026-07-28
-- Purpose: Track which vector DB provider is "active" per org, and inventory
--          read-only data held in other providers, so the AI can correctly
--          route searches and the system prompt can tell the user where
--          their data lives.
-- Idempotent: yes (CREATE TABLE IF NOT EXISTS / DO $$ guards / INSERT ON CONFLICT)
-- ============================================================================

-- One row per org. The "active" provider is the one that receives new
-- uploads and is the default target for semantic search. pgvector is the
-- default (Supabase built-in, free tier, no external account required).
CREATE TABLE IF NOT EXISTS ai_infrastructure.org_vector_provider_config (
    org_id              INTEGER PRIMARY KEY
                            REFERENCES ai_infrastructure.organisations(id)
                            ON DELETE CASCADE,
    active_provider     TEXT NOT NULL DEFAULT 'pgvector'
                            CHECK (active_provider IN ('pgvector', 'pinecone', 'qdrant')),
    embedding_provider  TEXT NOT NULL DEFAULT 'pgvector_bge'
                            CHECK (embedding_provider IN (
                                'pgvector_bge', 'voyager', 'openai', 'pgvector_auto'
                            )),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by_user_id  INTEGER
                            REFERENCES ai_infrastructure.users(id)
                            ON DELETE SET NULL
);

COMMENT ON TABLE ai_infrastructure.org_vector_provider_config IS
    'Active vector DB provider per org (Option A: single active + secondary read-only). '
    'Default is pgvector (Supabase built-in). Changing active_provider does NOT move '
    'existing data — old data stays in the previous provider and is inventoried in '
    'org_vector_other_provider_inventory so the AI can still report/document it.';

-- Per-org inventory of providers that hold data but are NOT the active one.
-- A row here means: this provider has <document_count> documents and
-- <vector_count> vectors for this org, readable but NOT the default search
-- target. Populated by the upload pipeline whenever a new provider is added.
CREATE TABLE IF NOT EXISTS ai_infrastructure.org_vector_other_provider_inventory (
    id                  SERIAL PRIMARY KEY,
    org_id              INTEGER NOT NULL
                            REFERENCES ai_infrastructure.organisations(id)
                            ON DELETE CASCADE,
    provider            TEXT NOT NULL
                            CHECK (provider IN ('pgvector', 'pinecone', 'qdrant')),
    document_count      INTEGER NOT NULL DEFAULT 0
                            CHECK (document_count >= 0),
    vector_count        INTEGER NOT NULL DEFAULT 0
                            CHECK (vector_count >= 0),
    last_synced_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- One row per (org, provider) — UPSERT pattern.
    UNIQUE (org_id, provider)
);

COMMENT ON TABLE ai_infrastructure.org_vector_other_provider_inventory IS
    'Read-only inventory of data held in non-active vector DB providers. '
    'Surfaced in the system prompt so the AI knows data exists in multiple '
    'places and can answer questions like "where is my contract data?".';

-- View for the system prompt builder — joins active provider + inventory
-- in one query so the prompt injection stays cheap.
CREATE OR REPLACE VIEW ai_infrastructure.v_org_vector_status AS
SELECT
    c.org_id,
    c.active_provider,
    c.embedding_provider,
    c.updated_at AS config_updated_at,
    COALESCE(
        (SELECT jsonb_agg(jsonb_build_object(
            'provider',         i.provider,
            'document_count',   i.document_count,
            'vector_count',     i.vector_count,
            'last_synced_at',   i.last_synced_at
        ) ORDER BY i.provider)
        FROM ai_infrastructure.org_vector_other_provider_inventory i
        WHERE i.org_id = c.org_id),
        '[]'::jsonb
    ) AS other_providers
FROM ai_infrastructure.org_vector_provider_config c;

COMMENT ON VIEW ai_infrastructure.v_org_vector_status IS
    'One row per org: active provider + JSON array of other providers with data. '
    'Read by the system prompt builder to inject vector DB status into the prompt.';

-- Backfill: every existing org gets a row with the default active provider.
-- INSERT ... ON CONFLICT DO NOTHING makes this safe to re-run.
INSERT INTO ai_infrastructure.org_vector_provider_config (org_id, active_provider, embedding_provider)
SELECT id, 'pgvector', 'pgvector_bge'
FROM ai_infrastructure.organisations
ON CONFLICT (org_id) DO NOTHING;

-- ============================================================================
-- VERIFY
-- ============================================================================
DO $$
DECLARE
    org_count          INTEGER;
    config_count       INTEGER;
    inventory_count    INTEGER;
    view_exists        BOOLEAN;
BEGIN
    SELECT COUNT(*) INTO org_count FROM ai_infrastructure.organisations;
    SELECT COUNT(*) INTO config_count FROM ai_infrastructure.org_vector_provider_config;
    SELECT COUNT(*) INTO inventory_count FROM ai_infrastructure.org_vector_other_provider_inventory;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.views
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'v_org_vector_status'
    ) INTO view_exists;

    RAISE NOTICE 'Migration 052 complete:';
    RAISE NOTICE '  Tables: org_vector_provider_config (%) rows, org_vector_other_provider_inventory (%) rows',
                 config_count, inventory_count;
    RAISE NOTICE '  View:   v_org_vector_status (%)',
                 CASE WHEN view_exists THEN 'created' ELSE 'MISSING' END;
    RAISE NOTICE '  Backfill: % org rows backfilled (expected %)',
                 config_count, org_count;

    IF config_count < org_count THEN
        RAISE WARNING 'Migration 052: % orgs but only % config rows — some orgs were created without backfill',
                      org_count, config_count;
    END IF;
END $$;
