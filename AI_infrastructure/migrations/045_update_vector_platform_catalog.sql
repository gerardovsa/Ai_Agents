-- ============================================================================
-- Migration 045: Update Vector DB platform catalog entries
--
-- CHANGES:
--   1. Update 'voyager' entry:  add voyage-4 model options to required_fields
--      and update icon + description to reflect Voyage AI v4 (2026 pricing).
--   2. Update 'pinecone' entry: add index_name field to multi-field form.
--   3. Add 'pgvector' entry:    zero-cost Supabase-native vector store option.
--
-- IDEMPOTENT: Yes — uses ON CONFLICT (platform_name) DO UPDATE.
-- ============================================================================

-- ---- Update Voyager AI with v4 model options --------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order, is_active)
VALUES
    ('voyager', 'Voyage AI', 'fas fa-rocket', '#7C3AED', 'vector_db', 'multi_field',
     '[
       {"name":"api_key","label":"API Key","type":"password",
        "placeholder":"pa-...","required":true,
        "help_text":"Found at dash.voyageai.com — first 200M tokens free"},
       {"name":"model","label":"Embedding Model","type":"select",
        "placeholder":"voyage-4","required":false,
        "options":["voyage-4-lite","voyage-4","voyage-4-large","voyage-context-3","voyage-large-2","voyage-2"],
        "help_text":"voyage-4-lite ($0.02/1M) is ideal for most use cases. voyage-4 ($0.06/1M) for highest accuracy."},
       {"name":"provider","label":"Provider (internal)","type":"hidden",
        "placeholder":"voyager","required":false,
        "help_text":"Internal identifier — do not change"}
     ]',
     'Voyage AI embedding provider — v4 models (2026). 200M free tokens per account. voyage-4-lite recommended for cost efficiency.',
     'https://docs.voyageai.com/docs/pricing', 21, TRUE)
ON CONFLICT (platform_name) DO UPDATE SET
    display_name   = EXCLUDED.display_name,
    icon_class     = EXCLUDED.icon_class,
    icon_color     = EXCLUDED.icon_color,
    required_fields= EXCLUDED.required_fields,
    description    = EXCLUDED.description,
    docs_url       = EXCLUDED.docs_url,
    is_active      = TRUE;

-- ---- Update Pinecone entry: add index_name field ---------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order, is_active)
VALUES
    ('pinecone', 'Pinecone', 'fas fa-database', '#7C3AED', 'vector_db', 'multi_field',
     '[
       {"name":"api_key","label":"API Key","type":"password",
        "placeholder":"pcsk_...","required":true,
        "help_text":"Found at app.pinecone.io — API Keys section"},
       {"name":"index_name","label":"Index Name","type":"text",
        "placeholder":"ai-agents-vectors","required":true,
        "help_text":"The name of your Pinecone index (e.g. my-project-vectors)"},
       {"name":"environment","label":"Region / Cloud","type":"text",
        "placeholder":"us-east-1","required":false,
        "help_text":"Optional — leave blank for serverless indexes (new API)"},
       {"name":"namespace","label":"Default Namespace","type":"text",
        "placeholder":"","required":false,
        "help_text":"Leave blank to auto-derive from your organisation ID (recommended)"}
     ]',
     'Pinecone managed vector database for AI semantic search. Dedicated Read Nodes now GA with up to 97% lower cost at scale.',
     'https://docs.pinecone.io', 20, TRUE)
ON CONFLICT (platform_name) DO UPDATE SET
    display_name   = EXCLUDED.display_name,
    required_fields= EXCLUDED.required_fields,
    description    = EXCLUDED.description,
    is_active      = TRUE;

-- ---- Add pgvector (Supabase-native) ----------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order, is_active)
VALUES
    ('pgvector', 'pgvector (Supabase)', 'fas fa-leaf', '#3ECF8E', 'vector_db', 'api_key',
     '[
       {"name":"api_key","label":"Confirmation Token","type":"password",
        "placeholder":"enabled","required":false,
        "help_text":"pgvector uses your existing Supabase connection — no extra credentials needed. Enter any value to confirm activation."}
     ]',
     'Zero-cost vector search powered by pgvector inside your Supabase PostgreSQL database. No external service required — each org''s documents are isolated by row-level security.',
     'https://supabase.com/docs/guides/ai/vector-columns', 22, TRUE)
ON CONFLICT (platform_name) DO UPDATE SET
    display_name   = EXCLUDED.display_name,
    required_fields= EXCLUDED.required_fields,
    description    = EXCLUDED.description,
    docs_url       = EXCLUDED.docs_url,
    is_active      = TRUE;

-- ---- Verification ----------------------------------------------------------
DO $$
DECLARE
    voyager_model TEXT;
    has_pgvector  BOOLEAN;
    has_index_name BOOLEAN;
BEGIN
    SELECT required_fields::TEXT INTO voyager_model
    FROM ai_infrastructure.platform_catalog
    WHERE platform_name = 'voyager';

    SELECT EXISTS (
        SELECT 1 FROM ai_infrastructure.platform_catalog WHERE platform_name = 'pgvector'
    ) INTO has_pgvector;

    SELECT required_fields::TEXT LIKE '%index_name%' INTO has_index_name
    FROM ai_infrastructure.platform_catalog WHERE platform_name = 'pinecone';

    RAISE NOTICE 'Migration 045 complete — voyager v4 models present: %, pgvector entry: %, pinecone index_name field: %',
        voyager_model LIKE '%voyage-4%', has_pgvector, has_index_name;
END$$;
