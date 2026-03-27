-- Migration 036: Platform Catalog + Module Catalog
-- Creates extensible tables so new platforms and modules can be added via
-- database inserts rather than code changes (previously ALLOWED_PLATFORMS was
-- a hardcoded Python set; platform buttons were hardcoded HTML).
--
-- Tables created:
--   ai_infrastructure.platform_catalog  — every connectable external service
--   ai_infrastructure.module_catalog    — every feature module with metadata
--
-- After running, update organisation_credentials_routes.py to query
-- platform_catalog instead of the hardcoded ALLOWED_PLATFORMS set.
--
-- Idempotent: safe to run multiple times.

DO $$
BEGIN

-- =========================================================================
-- 1. platform_catalog
--    One row per connectable platform.  required_fields JSONB drives the
--    dynamic credential form so no HTML changes are needed for new platforms.
-- =========================================================================
CREATE TABLE IF NOT EXISTS ai_infrastructure.platform_catalog (
    platform_name    VARCHAR(100) PRIMARY KEY,
    display_name     VARCHAR(255) NOT NULL,
    icon_class       VARCHAR(100) NOT NULL DEFAULT 'fas fa-plug',
    icon_color       VARCHAR(20)  NOT NULL DEFAULT '#6B7280',
    category         VARCHAR(50)  NOT NULL DEFAULT 'other',
    -- auth_type controls which credential form is shown:
    --   'api_key'           — single secret key field
    --   'oauth2'            — OAuth 2.0 redirect flow
    --   'connection_string' — full connection string (DBs)
    --   'multi_field'       — multiple named fields (see required_fields)
    auth_type        VARCHAR(50)  NOT NULL DEFAULT 'api_key',
    -- JSON array of field descriptors for dynamic form rendering.
    -- Each element: {name, label, type, placeholder, required, help_text}
    required_fields  JSONB        NOT NULL DEFAULT '[]'::jsonb,
    description      TEXT,
    docs_url         TEXT,
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    sort_order       INTEGER      NOT NULL DEFAULT 100,
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_platform_catalog_category
    ON ai_infrastructure.platform_catalog (category)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_platform_catalog_sort
    ON ai_infrastructure.platform_catalog (sort_order);

-- =========================================================================
-- 2. module_catalog
--    One row per feature module.  required_platforms links back to
--    platform_catalog so the UI can show "requires Shopify API key".
-- =========================================================================
CREATE TABLE IF NOT EXISTS ai_infrastructure.module_catalog (
    module_name        VARCHAR(100) PRIMARY KEY,
    display_name       VARCHAR(255) NOT NULL,
    description        TEXT,
    icon_class         VARCHAR(100) NOT NULL DEFAULT 'fas fa-cube',
    icon_color         VARCHAR(20)  NOT NULL DEFAULT '#6B7280',
    category           VARCHAR(50)  NOT NULL DEFAULT 'other',
    -- lowest plan tier at which this module is available
    min_plan_tier      VARCHAR(50)  NOT NULL DEFAULT 'enterprise',
    -- array of platform_name values from platform_catalog
    required_platforms TEXT[]       NOT NULL DEFAULT '{}',
    is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
    sort_order         INTEGER      NOT NULL DEFAULT 100,
    created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_module_catalog_min_plan
    ON ai_infrastructure.module_catalog (min_plan_tier)
    WHERE is_active = TRUE;

-- =========================================================================
-- 3. Seed platform_catalog  (idempotent via ON CONFLICT DO NOTHING)
-- =========================================================================

-- ---- AI Providers --------------------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('anthropic', 'Anthropic Claude', 'fas fa-brain', '#6366f1', 'ai', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"sk-ant-...","required":true,"help_text":"Found in console.anthropic.com"}]',
     'Claude family of large language models by Anthropic.',
     'https://docs.anthropic.com', 10),

    ('openai', 'OpenAI', 'fas fa-robot', '#10a37f', 'ai', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"sk-...","required":true,"help_text":"Found in platform.openai.com/api-keys"}]',
     'GPT-4 and other OpenAI models.',
     'https://platform.openai.com/docs', 11),

    ('deepseek', 'DeepSeek', 'fas fa-search', '#4F46E5', 'ai', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"sk-...","required":true,"help_text":"Found in platform.deepseek.com"}]',
     'DeepSeek language models.',
     'https://platform.deepseek.com/docs', 12),

    ('assemblyai', 'AssemblyAI', 'fas fa-microphone', '#FF6B6B', 'ai', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"Found in app.assemblyai.com"}]',
     'AI-powered speech recognition and audio intelligence.',
     'https://www.assemblyai.com/docs', 13)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- Vector Databases ----------------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('pinecone', 'Pinecone', 'fas fa-database', '#7C3AED', 'vector_db', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"Found in app.pinecone.io"},{"name":"environment","label":"Environment","type":"text","placeholder":"us-east-1-aws","required":false,"help_text":"Your Pinecone environment (optional for new API)"}]',
     'Managed vector database for AI semantic search.',
     'https://docs.pinecone.io', 20),

    ('voyager', 'Voyager AI', 'fas fa-vector-square', '#8B5CF6', 'vector_db', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"Your Voyager AI API key"}]',
     'Embedding and vector search provider.',
     NULL, 21)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- E-commerce ----------------------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('shopify', 'Shopify', 'fab fa-shopify', '#96bf48', 'ecommerce', 'api_key',
     '[{"name":"api_key","label":"Access Token","type":"password","placeholder":"shpat_...","required":true,"help_text":"Admin API access token from your Shopify app"},{"name":"shop_url","label":"Shop URL","type":"text","placeholder":"yourstore.myshopify.com","required":true,"help_text":"Your Shopify store URL (without https://)"}]',
     'Shopify store management — products, orders, customers.',
     'https://shopify.dev/docs/api/admin-rest', 30),

    ('woocommerce', 'WooCommerce', 'fab fa-wordpress', '#96588A', 'ecommerce', 'multi_field',
     '[{"name":"store_url","label":"Store URL","type":"text","placeholder":"https://yourstore.com","required":true,"help_text":"Your WordPress/WooCommerce site URL"},{"name":"consumer_key","label":"Consumer Key","type":"text","placeholder":"ck_...","required":true,"help_text":"WooCommerce REST API consumer key"},{"name":"consumer_secret","label":"Consumer Secret","type":"password","placeholder":"cs_...","required":true,"help_text":"WooCommerce REST API consumer secret"}]',
     'WooCommerce store integration via REST API.',
     'https://woocommerce.github.io/woocommerce-rest-api-docs/', 31)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- Accounting / Finance ------------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('xero', 'Xero', 'fas fa-receipt', '#13B5EA', 'accounting', 'oauth2',
     '[{"name":"client_id","label":"Client ID","type":"text","placeholder":"...","required":true,"help_text":"From developer.xero.com app settings"},{"name":"client_secret","label":"Client Secret","type":"password","placeholder":"...","required":true,"help_text":"From developer.xero.com app settings"}]',
     'Xero cloud accounting — invoices, bills, bank feeds.',
     'https://developer.xero.com/documentation/', 40),

    ('stripe', 'Stripe', 'fab fa-stripe', '#635BFF', 'payment', 'api_key',
     '[{"name":"api_key","label":"Secret Key","type":"password","placeholder":"sk_live_... or sk_test_...","required":true,"help_text":"Stripe secret key from dashboard.stripe.com/apikeys"},{"name":"webhook_secret","label":"Webhook Secret","type":"password","placeholder":"whsec_...","required":false,"help_text":"Webhook signing secret (optional)"}]',
     'Stripe payment processing and billing.',
     'https://stripe.com/docs/api', 41),

    ('paypal', 'PayPal', 'fab fa-paypal', '#00457C', 'payment', 'multi_field',
     '[{"name":"client_id","label":"Client ID","type":"text","placeholder":"...","required":true,"help_text":"From developer.paypal.com app settings"},{"name":"client_secret","label":"Client Secret","type":"password","placeholder":"...","required":true,"help_text":"From developer.paypal.com app settings"}]',
     'PayPal payment processing.',
     'https://developer.paypal.com/docs/', 42)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- Communication / Email -----------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('sendgrid', 'SendGrid', 'fas fa-envelope', '#1A82E2', 'communication', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"SG....","required":true,"help_text":"Found in app.sendgrid.com/settings/api_keys"}]',
     'Transactional email delivery via SendGrid.',
     'https://docs.sendgrid.com/', 50),

    ('twilio', 'Twilio', 'fas fa-phone', '#F22F46', 'communication', 'multi_field',
     '[{"name":"account_sid","label":"Account SID","type":"text","placeholder":"ACxxx...","required":true,"help_text":"From console.twilio.com"},{"name":"auth_token","label":"Auth Token","type":"password","placeholder":"...","required":true,"help_text":"From console.twilio.com"}]',
     'SMS, voice, and messaging via Twilio.',
     'https://www.twilio.com/docs', 51),

    ('hunter', 'Hunter.io', 'fas fa-search', '#E77B00', 'communication', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"Found in hunter.io/api-keys"}]',
     'Email finder and verification by Hunter.io.',
     'https://hunter.io/api-documentation', 52)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- Shipping ------------------------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('auspost', 'Australia Post', 'fas fa-box', '#B00020', 'shipping', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"From developers.auspost.com.au/apis"}]',
     'Australia Post parcel tracking and rate calculation.',
     'https://developers.auspost.com.au/apis/', 60)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- Team / OAuth Providers ----------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('google', 'Google Workspace', 'fab fa-google', '#4285f4', 'team', 'oauth2',
     '[{"name":"client_id","label":"OAuth Client ID","type":"text","placeholder":"...apps.googleusercontent.com","required":true,"help_text":"From console.cloud.google.com"},{"name":"client_secret","label":"OAuth Client Secret","type":"password","placeholder":"...","required":true,"help_text":"From console.cloud.google.com"}]',
     'Google Workspace — Gmail, Drive, Calendar, Meet.',
     'https://developers.google.com/workspace', 70),

    ('microsoft', 'Microsoft 365', 'fab fa-microsoft', '#00a4ef', 'team', 'oauth2',
     '[{"name":"tenant_id","label":"Tenant ID","type":"text","placeholder":"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx","required":true,"help_text":"From portal.azure.com > Azure Active Directory"},{"name":"client_id","label":"App (Client) ID","type":"text","placeholder":"xxxxxxxx-...","required":true,"help_text":"From your Azure App registration"},{"name":"client_secret","label":"Client Secret","type":"password","placeholder":"...","required":true,"help_text":"From Azure App registration > Certificates & secrets"}]',
     'Microsoft 365 — Outlook, Teams, SharePoint via Azure AD.',
     'https://learn.microsoft.com/en-us/graph/', 71),

    ('gmail_oauth', 'Gmail OAuth', 'fas fa-envelope', '#EA4335', 'team', 'oauth2',
     '[{"name":"client_id","label":"OAuth Client ID","type":"text","placeholder":"...apps.googleusercontent.com","required":true,"help_text":"Google Cloud Console OAuth 2.0 credentials"},{"name":"client_secret","label":"OAuth Client Secret","type":"password","placeholder":"...","required":true}]',
     'Individual Gmail OAuth 2.0 integration.',
     'https://developers.google.com/gmail/api', 72),

    ('outlook_oauth', 'Outlook OAuth', 'fas fa-envelope', '#0078D4', 'team', 'oauth2',
     '[{"name":"tenant_id","label":"Tenant ID","type":"text","placeholder":"common","required":false,"help_text":"Leave as ''common'' for personal accounts"},{"name":"client_id","label":"App (Client) ID","type":"text","placeholder":"xxxxxxxx-...","required":true},{"name":"client_secret","label":"Client Secret","type":"password","placeholder":"...","required":true}]',
     'Individual Outlook OAuth 2.0 integration.',
     'https://learn.microsoft.com/en-us/graph/outlook-mail-overview', 73),

    ('kajabi', 'Kajabi', 'fas fa-graduation-cap', '#FFA500', 'team', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"...","required":true,"help_text":"From app.kajabi.com/admin/developer_tools/api_keys"}]',
     'Online course and digital product platform.',
     'https://developers.kajabi.com/', 74)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- Database Platforms --------------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('supabase', 'Supabase', 'fas fa-database', '#3ECF8E', 'database', 'multi_field',
     '[{"name":"url","label":"Project URL","type":"text","placeholder":"https://xxxx.supabase.co","required":true,"help_text":"From supabase.com project settings > API"},{"name":"anon_key","label":"Anon Public Key","type":"password","placeholder":"eyJh...","required":true,"help_text":"Your project anon/public key"},{"name":"service_role_key","label":"Service Role Key","type":"password","placeholder":"eyJh...","required":false,"help_text":"Service role key for admin operations (keep secret)"}]',
     'Supabase managed PostgreSQL database.',
     'https://supabase.com/docs', 80),

    ('supabase_vsa', 'Supabase (VSA)', 'fas fa-database', '#3ECF8E', 'database', 'multi_field',
     '[{"name":"url","label":"Project URL","type":"text","placeholder":"https://xxxx.supabase.co","required":true},{"name":"anon_key","label":"Anon Key","type":"password","placeholder":"eyJh...","required":true},{"name":"service_role_key","label":"Service Role Key","type":"password","placeholder":"eyJh...","required":false}]',
     'Secondary Supabase instance (VSA project).',
     'https://supabase.com/docs', 81),

    ('sql_database', 'SQL Database', 'fas fa-database', '#0078D4', 'database', 'connection_string',
     '[{"name":"connection_string","label":"Connection String","type":"password","placeholder":"Server=host;Database=db;User=user;Password=pass;","required":true,"help_text":"Full ADO.NET or JDBC connection string"}]',
     'Generic SQL database via connection string (SQL Server, MySQL, PostgreSQL).',
     NULL, 82),

    ('inhouseprint_sql', 'InHousePrint SQL', 'fas fa-print', '#FF6B35', 'database', 'connection_string',
     '[{"name":"connection_string","label":"Connection String","type":"password","placeholder":"Server=host;Database=Fred;User=...;Password=...;","required":true,"help_text":"SQL Server connection string for the Fred database"}]',
     'InHousePrint Fred database (SQL Server).',
     NULL, 83)

ON CONFLICT (platform_name) DO NOTHING;

-- ---- Hosting & DevOps ----------------------------------------------------
INSERT INTO ai_infrastructure.platform_catalog
    (platform_name, display_name, icon_class, icon_color, category, auth_type,
     required_fields, description, docs_url, sort_order)
VALUES
    ('render', 'Render', 'fas fa-server', '#46E3B7', 'hosting', 'api_key',
     '[{"name":"api_key","label":"API Key","type":"password","placeholder":"rnd_...","required":true,"help_text":"From dashboard.render.com/u/<username>/account/settings"}]',
     'Render cloud hosting — web services, background workers, databases.',
     'https://render.com/docs/api', 90),

    ('cloudflare', 'Cloudflare', 'fab fa-cloudflare', '#F38020', 'hosting', 'multi_field',
     '[{"name":"api_token","label":"API Token","type":"password","placeholder":"...","required":true,"help_text":"From dash.cloudflare.com/profile/api-tokens"},{"name":"account_id","label":"Account ID","type":"text","placeholder":"...","required":false,"help_text":"Found in the right sidebar of dash.cloudflare.com"}]',
     'Cloudflare CDN, DNS, and Workers.',
     'https://developers.cloudflare.com/', 91)

ON CONFLICT (platform_name) DO NOTHING;

-- =========================================================================
-- 4. Seed module_catalog  (idempotent via ON CONFLICT DO NOTHING)
-- =========================================================================

-- ---- Core modules (free tier) -------------------------------------------
INSERT INTO ai_infrastructure.module_catalog
    (module_name, display_name, description, icon_class, icon_color, category,
     min_plan_tier, required_platforms, sort_order)
VALUES
    ('core_chat',       'AI Chat',          'Multi-model AI chat with conversation history, file attachments, and thread management.',
     'fas fa-comments',    '#4F46E5', 'core',        'free', '{}', 10),

    ('documents',       'Documents',        'Upload, search, and chat with documents using AI-powered analysis.',
     'fas fa-file-alt',    '#6366F1', 'core',        'free', '{}', 11),

    ('prompt_library',  'Prompt Library',   'Save, organise, and share reusable AI prompts across your team.',
     'fas fa-book',        '#8B5CF6', 'core',        'free', '{}', 12),

    ('notifications',   'Notifications',    'In-app notifications, alerts, and activity feed.',
     'fas fa-bell',        '#F59E0B', 'core',        'free', '{}', 13)

ON CONFLICT (module_name) DO NOTHING;

-- ---- Starter tier modules -----------------------------------------------
INSERT INTO ai_infrastructure.module_catalog
    (module_name, display_name, description, icon_class, icon_color, category,
     min_plan_tier, required_platforms, sort_order)
VALUES
    ('universal_search', 'Universal Search',  'Semantic and keyword search across all content and tools.',
     'fas fa-search',      '#10B981', 'productivity', 'starter', '{}', 20),

    ('synergy',           'Synergy',          'Cross-module intelligence and recommendation engine.',
     'fas fa-project-diagram', '#3B82F6', 'productivity', 'starter', '{}', 21),

    ('automation',        'Automation',       'AI-powered workflow automation and scheduled tasks.',
     'fas fa-robot',       '#6366F1', 'productivity', 'starter', '{}', 22),

    ('thread_cards',      'Thread Cards',     'Kanban-style AI conversation and task thread management.',
     'fas fa-th',          '#F59E0B', 'productivity', 'starter', '{}', 23)

ON CONFLICT (module_name) DO NOTHING;

-- ---- Professional tier modules ------------------------------------------
INSERT INTO ai_infrastructure.module_catalog
    (module_name, display_name, description, icon_class, icon_color, category,
     min_plan_tier, required_platforms, sort_order)
VALUES
    ('shopify',             'Shopify',              'Manage products, orders, inventory, and customers via AI.',
     'fab fa-shopify',      '#96bf48', 'ecommerce',    'professional', ARRAY['shopify'], 30),

    ('xero',                'Xero Accounting',      'Manage invoices, bills, bank reconciliation, and reports via AI.',
     'fas fa-receipt',      '#13B5EA', 'finance',      'professional', ARRAY['xero'], 31),

    ('auspost_shipping',    'Australia Post',       'Calculate shipping rates, generate labels, and track parcels.',
     'fas fa-box',          '#B00020', 'logistics',    'professional', ARRAY['auspost'], 32),

    ('stock_management',    'Stock Management',     'Inventory tracking, reorder alerts, and stock level monitoring.',
     'fas fa-boxes',        '#059669', 'operations',   'professional', '{}', 33),

    ('transcription',       'Voice Transcription',  'AI-powered audio transcription and meeting summaries.',
     'fas fa-microphone',   '#FF6B6B', 'productivity', 'professional', ARRAY['assemblyai'], 34),

    ('vector_database',     'Vector Search',        'Semantic search and knowledge base powered by vector embeddings.',
     'fas fa-database',     '#7C3AED', 'ai',           'professional', ARRAY['pinecone'], 35),

    ('customer_reactivation','Customer Reactivation','AI-driven win-back campaigns and churn prediction.',
     'fas fa-user-check',   '#10B981', 'marketing',    'professional', '{}', 36)

ON CONFLICT (module_name) DO NOTHING;

-- ---- Enterprise tier modules --------------------------------------------
INSERT INTO ai_infrastructure.module_catalog
    (module_name, display_name, description, icon_class, icon_color, category,
     min_plan_tier, required_platforms, sort_order)
VALUES
    ('inhouse_print',      'InHouse Print',     'AI tools for the InHousePrint Fred database — job tickets, quotes, history.',
     'fas fa-print',        '#FF6B35', 'operations',  'enterprise', ARRAY['inhouseprint_sql'], 40),

    ('inhouse_kanban',     'InHouse Kanban',    'Kanban board for InHousePrint job workflow management.',
     'fas fa-columns',      '#F97316', 'operations',  'enterprise', ARRAY['inhouseprint_sql'], 41),

    ('quote_calculator',   'Quote Calculator',  'Multi-product quoting engine with custom pricing rules and discount tiers.',
     'fas fa-calculator',   '#0EA5E9', 'operations',  'enterprise', '{}', 42),

    ('database_visualizer','DB Visualizer',     'Visual schema explorer and query builder for connected databases.',
     'fas fa-sitemap',      '#6366F1', 'dev',          'enterprise', '{}', 43),

    ('github',             'GitHub',            'AI-assisted code review, PR summaries, and repository insights.',
     'fab fa-github',       '#333333', 'dev',          'enterprise', '{}', 44),

    ('render_management',  'Render Management', 'Monitor and manage Render deployments, services, and logs via AI.',
     'fas fa-server',       '#46E3B7', 'dev',          'enterprise', ARRAY['render'], 45),

    ('local_filesystem',   'Local Filesystem',  'AI access to local files and directories via secure API bridge.',
     'fas fa-folder-open',  '#D97706', 'dev',          'enterprise', '{}', 46),

    ('woocommerce',        'WooCommerce',       'Manage WooCommerce products, orders, and customers via AI.',
     'fab fa-wordpress',    '#96588A', 'ecommerce',    'enterprise', ARRAY['woocommerce'], 47)

ON CONFLICT (module_name) DO NOTHING;

-- =========================================================================
-- 5. Optional: add foreign key reference in org_module_access
--    (only adds the constraint if it doesn't already exist)
-- =========================================================================
DO $inner$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_schema = 'ai_infrastructure'
          AND table_name        = 'org_module_access'
          AND constraint_name   = 'fk_oma_module_catalog'
    ) THEN
        -- Only add FK if all existing module_names exist in module_catalog
        -- (skip silently if orphaned rows exist to avoid blocking migration)
        BEGIN
            ALTER TABLE ai_infrastructure.org_module_access
                ADD CONSTRAINT fk_oma_module_catalog
                FOREIGN KEY (module_name)
                REFERENCES ai_infrastructure.module_catalog(module_name)
                ON DELETE CASCADE;
            RAISE NOTICE 'Added FK constraint on org_module_access.module_name';
        EXCEPTION WHEN foreign_key_violation OR others THEN
            RAISE NOTICE 'Skipping FK constraint (orphaned module names exist): %', SQLERRM;
        END;
    END IF;
END $inner$;

RAISE NOTICE 'Migration 036 complete: platform_catalog (% rows) + module_catalog (% rows)',
    (SELECT COUNT(*) FROM ai_infrastructure.platform_catalog),
    (SELECT COUNT(*) FROM ai_infrastructure.module_catalog);

END $$;
