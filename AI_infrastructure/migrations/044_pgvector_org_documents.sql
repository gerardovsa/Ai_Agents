-- ============================================================================
-- Migration 044: pgvector Organisation Documents
--
-- PURPOSE:
--   Adds a multi-tenant vector document store inside Supabase PostgreSQL.
--   Uses the pgvector extension already enabled by create_tool_embeddings_tables.py.
--   Every row is scoped to an (org_id, document_id) pair.
--   RLS ensures each org sees only its own rows.
--
-- TABLES CREATED:
--   ai_infrastructure.org_vector_documents - Main chunk + embedding store
--
-- PREREQUISITES:
--   - Migration 036 (organisations table exists)
--   - pgvector extension already enabled (CREATE EXTENSION IF NOT EXISTS vector)
--
-- IDEMPOTENT: Yes — all CREATE statements use IF NOT EXISTS.
-- ============================================================================

-- Ensure pgvector is available
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- Main table: one row per text chunk, with its embedding vector
-- ============================================================================
CREATE TABLE IF NOT EXISTS ai_infrastructure.org_vector_documents (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id          INTEGER     NOT NULL
                                REFERENCES ai_infrastructure.organisations(id)
                                ON DELETE CASCADE,
    user_id         INTEGER     NOT NULL
                                REFERENCES ai_infrastructure.users(id)
                                ON DELETE SET NULL,
    document_id     TEXT        NOT NULL,            -- e.g. "doc_a3f7b291"
    filename        TEXT        NOT NULL,
    chunk_index     INTEGER     NOT NULL DEFAULT 0,
    total_chunks    INTEGER     NOT NULL DEFAULT 1,
    content         TEXT        NOT NULL,            -- raw chunk text
    embedding       vector(1536),                    -- 1536 = OpenAI / Voyage default
    emb_model       TEXT,                            -- e.g. "text-embedding-3-small"
    emb_provider    TEXT        DEFAULT 'openai',    -- 'openai' | 'voyager'
    visibility      TEXT        DEFAULT 'org',       -- 'private' | 'org' | 'global'
    metadata        JSONB       DEFAULT '{}',
    file_type       TEXT,
    file_size_bytes BIGINT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Indexes
-- ============================================================================

-- HNSW index: fast approximate nearest-neighbour search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_org_vec_docs_embedding_hnsw
    ON ai_infrastructure.org_vector_documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Org + document_id lookup (used by list_documents and delete)
CREATE INDEX IF NOT EXISTS idx_org_vec_docs_org_doc
    ON ai_infrastructure.org_vector_documents (org_id, document_id);

-- Filename search
CREATE INDEX IF NOT EXISTS idx_org_vec_docs_filename
    ON ai_infrastructure.org_vector_documents (org_id, filename);

-- ============================================================================
-- Row-Level Security (Supabase RLS)
--
-- The application sets `app.current_org_id` via SET LOCAL before queries
-- so Supabase RLS can filter rows automatically.
-- When using the Python execute_query() helper this is done in the same
-- transaction via:
--   SET LOCAL app.current_org_id = <org_id>;
-- ============================================================================

ALTER TABLE ai_infrastructure.org_vector_documents ENABLE ROW LEVEL SECURITY;

-- Allow SELECT only for rows that belong to the current org context
-- (application must SET LOCAL app.current_org_id = X before querying)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'ai_infrastructure'
          AND tablename  = 'org_vector_documents'
          AND policyname = 'org_isolation_select'
    ) THEN
        CREATE POLICY org_isolation_select
            ON ai_infrastructure.org_vector_documents
            FOR SELECT
            USING (
                org_id = NULLIF(current_setting('app.current_org_id', TRUE), '')::INTEGER
            );
    END IF;
END$$;

-- Allow INSERT for rows that match the current org context
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'ai_infrastructure'
          AND tablename  = 'org_vector_documents'
          AND policyname = 'org_isolation_insert'
    ) THEN
        CREATE POLICY org_isolation_insert
            ON ai_infrastructure.org_vector_documents
            FOR INSERT
            WITH CHECK (
                org_id = NULLIF(current_setting('app.current_org_id', TRUE), '')::INTEGER
            );
    END IF;
END$$;

-- Allow DELETE only for rows that belong to the current org context
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE schemaname = 'ai_infrastructure'
          AND tablename  = 'org_vector_documents'
          AND policyname = 'org_isolation_delete'
    ) THEN
        CREATE POLICY org_isolation_delete
            ON ai_infrastructure.org_vector_documents
            FOR DELETE
            USING (
                org_id = NULLIF(current_setting('app.current_org_id', TRUE), '')::INTEGER
            );
    END IF;
END$$;

-- ============================================================================
-- Helper function: vector similarity search scoped to an org
-- Returns the top-K chunks with their cosine similarity score.
-- ============================================================================
CREATE OR REPLACE FUNCTION ai_infrastructure.pgvector_search(
    p_org_id    INTEGER,
    p_embedding vector,
    p_top_k     INTEGER DEFAULT 10,
    p_threshold FLOAT   DEFAULT 0.5
)
RETURNS TABLE (
    id              UUID,
    document_id     TEXT,
    filename        TEXT,
    chunk_index     INTEGER,
    content         TEXT,
    similarity      FLOAT,
    metadata        JSONB,
    created_at      TIMESTAMPTZ
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        d.id,
        d.document_id,
        d.filename,
        d.chunk_index,
        d.content,
        (1 - (d.embedding <=> p_embedding))::FLOAT AS similarity,
        d.metadata,
        d.created_at
    FROM  ai_infrastructure.org_vector_documents d
    WHERE d.org_id = p_org_id
      AND d.embedding IS NOT NULL
      AND (1 - (d.embedding <=> p_embedding)) >= p_threshold
    ORDER BY d.embedding <=> p_embedding
    LIMIT p_top_k;
$$;

-- ============================================================================
-- Verification
-- ============================================================================
DO $$
DECLARE
    tbl_exists  BOOLEAN;
    idx_count   INTEGER;
    pol_count   INTEGER;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'org_vector_documents'
    ) INTO tbl_exists;

    SELECT COUNT(*) INTO idx_count
    FROM   pg_indexes
    WHERE  schemaname = 'ai_infrastructure'
      AND  tablename  = 'org_vector_documents';

    SELECT COUNT(*) INTO pol_count
    FROM   pg_policies
    WHERE  schemaname = 'ai_infrastructure'
      AND  tablename  = 'org_vector_documents';

    RAISE NOTICE 'Migration 044 complete — table: %, indexes: %, RLS policies: %',
        tbl_exists, idx_count, pol_count;
END$$;
