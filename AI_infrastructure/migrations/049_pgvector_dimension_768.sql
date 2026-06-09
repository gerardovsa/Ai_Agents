-- MIGRATION 049: pgvector embedding dimension 1024 → 768
--
-- REASON:
--   Migration 048 set the column to vector(1024) to match Voyage AI's native dimension.
--   The free local fallback model (all-mpnet-base-v2 / sentence-transformers) produces
--   768-dim vectors natively. Voyage AI supports output_dimension=768, and OpenAI's
--   text-embedding-3-* models support dimensions=768. 768 is therefore the universal
--   dimension that works across all three providers without padding or quality loss.
--
--   Standard Render plan (1 CPU, 2 GB RAM) RAM budget:
--     Flask + gevent + libraries : ~350 MB
--     all-mpnet-base-v2 model    : ~500 MB
--     Headroom                   : ~1150 MB
--   Total: well within 2 GB.
--
-- UPGRADE PATH (Pro plan, 4 GB / 2 CPU):
--   Just add a Voyage AI key in Organisation Settings → Connections.
--   voyage-4 will be called with output_dimension=768 — no column change,
--   no re-indexing of existing documents required.
--
-- IDEMPOTENT: Yes — all statements are safe to re-run.
-- SAFE TO RUN ON EMPTY TABLE: Yes.
-- ============================================================================

-- Step 1: Drop the HNSW index
DROP INDEX IF EXISTS idx_org_vec_docs_embedding_hnsw;

-- Step 2: Drop and recreate the embedding column at vector(768)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'ai_infrastructure'
          AND table_name   = 'org_vector_documents'
          AND column_name  = 'embedding'
    ) THEN
        ALTER TABLE ai_infrastructure.org_vector_documents DROP COLUMN embedding;
        RAISE NOTICE '[049] Dropped old embedding column (was vector(1024))';
    END IF;
END$$;

ALTER TABLE ai_infrastructure.org_vector_documents
    ADD COLUMN IF NOT EXISTS embedding vector(768);

DO $$ BEGIN RAISE NOTICE '[049] embedding column added as vector(768)'; END$$;

-- Step 3: Recreate HNSW cosine-distance index
CREATE INDEX IF NOT EXISTS idx_org_vec_docs_embedding_hnsw
    ON ai_infrastructure.org_vector_documents
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

DO $$ BEGIN RAISE NOTICE '[049] HNSW index recreated for vector(768)'; END$$;
