-- MIGRATION 048: pgvector embedding dimension → 1024
--
-- REASON:
--   Migration 044 created org_vector_documents with vector(1536) matching OpenAI's
--   default. Voyage AI's native dimension is 1024 (voyage-4, voyage-3, voyage-3-large).
--   text-embedding-3-small and text-embedding-3-large also support dimensions=1024.
--   No documents have been successfully uploaded yet, so this is a safe schema change.
--
-- WHAT IT DOES:
--   1. Drops the HNSW index (required before column type change)
--   2. Drops and recreates the embedding column as vector(1024)
--   3. Recreates the HNSW index
--
-- IDEMPOTENT: Yes — column drop uses IF EXISTS; index creation uses IF NOT EXISTS.
-- SAFE TO RUN ON EMPTY TABLE: Yes (no data migration needed).
-- ============================================================================

-- Step 1: Drop the HNSW index (must be removed before changing column type)
DROP INDEX IF EXISTS idx_org_vec_docs_embedding_hnsw;

-- Step 2: Drop and recreate the embedding column at the new dimension
--   Using DROP + ADD (rather than ALTER TYPE) avoids USING clause issues
--   and is safe on an empty table.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'org_vector_documents'
          AND column_name  = 'embedding'
    ) THEN
        ALTER TABLE ai_infrastructure.org_vector_documents DROP COLUMN embedding;
        RAISE NOTICE '[048] Dropped old embedding column (was vector(1536))';
    END IF;
END$$;

ALTER TABLE ai_infrastructure.org_vector_documents
    ADD COLUMN IF NOT EXISTS embedding vector(1024);

DO $$ BEGIN RAISE NOTICE '[048] embedding column added as vector(1024)'; END$$;

-- Step 3: Recreate HNSW cosine-distance index for fast ANN search
CREATE INDEX IF NOT EXISTS idx_org_vec_docs_embedding_hnsw
    ON ai_infrastructure.org_vector_documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

DO $$ BEGIN RAISE NOTICE '[048] HNSW index recreated for vector(1024)'; END$$;
