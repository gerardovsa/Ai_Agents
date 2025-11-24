-- ============================================================================
-- SUPABASE SEARCH SYSTEM - CORE FEATURES ONLY
-- ============================================================================
-- PURPOSE: Add full-text search and AI embeddings to 4 core tables
--          This is a simplified version that avoids JSON validation issues
--
-- FEATURES:
--   - Full-text search (keyword matching, 10-100x faster than ILIKE)
--   - AI embeddings (semantic similarity search with pgvector)
--   - Unified search (search all tables with one query)
--
-- DEPLOYMENT: Run in Supabase Dashboard SQL Editor
-- CREATED: 2025-11-25
-- ============================================================================

-- ============================================================================
-- STEP 1: ENABLE REQUIRED EXTENSIONS
-- ============================================================================

-- AI Embeddings (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- Performance Monitoring (optional)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;


-- ============================================================================
-- STEP 2: FULL-TEXT SEARCH - THREADS TABLE
-- ============================================================================

ALTER TABLE sessions.threads
ADD COLUMN IF NOT EXISTS search_vector tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(thread_slug, '')), 'B')
) STORED;

CREATE INDEX IF NOT EXISTS threads_search_idx 
ON sessions.threads 
USING GIN(search_vector);

CREATE OR REPLACE FUNCTION sessions.search_threads(
    search_query TEXT,
    user_id_param INTEGER,
    result_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    id INTEGER,
    thread_slug TEXT,
    name TEXT,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.thread_slug,
        t.name,
        ts_rank(t.search_vector, websearch_to_tsquery('english', search_query)) as rank
    FROM sessions.threads t
    WHERE t.user_id = user_id_param
        AND t.search_vector @@ websearch_to_tsquery('english', search_query)
    ORDER BY rank DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION sessions.search_threads TO authenticated;


-- ============================================================================
-- STEP 3: FULL-TEXT SEARCH - MESSAGES TABLE
-- ============================================================================

ALTER TABLE sessions.messages
ADD COLUMN IF NOT EXISTS search_vector tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(content, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(role, '')), 'B')
) STORED;

CREATE INDEX IF NOT EXISTS messages_search_idx 
ON sessions.messages 
USING GIN(search_vector);

CREATE OR REPLACE FUNCTION sessions.search_messages(
    search_query TEXT,
    user_id_param INTEGER,
    result_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    message_id INTEGER,
    thread_id INTEGER,
    role TEXT,
    content TEXT,
    created_at TIMESTAMPTZ,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.message_id,
        m.thread_id,
        m.role,
        m.content,
        m.created_at,
        ts_rank(m.search_vector, websearch_to_tsquery('english', search_query)) as rank
    FROM sessions.messages m
    JOIN sessions.threads t ON m.thread_id = t.id
    WHERE t.user_id = user_id_param
        AND m.search_vector @@ websearch_to_tsquery('english', search_query)
    ORDER BY rank DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION sessions.search_messages TO authenticated;


-- ============================================================================
-- STEP 4: FULL-TEXT SEARCH - SYNERGY SESSIONS TABLE
-- ============================================================================

ALTER TABLE synergy_sessions.sessions
ADD COLUMN IF NOT EXISTS search_vector tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(session_title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(status, '')), 'C')
) STORED;

CREATE INDEX IF NOT EXISTS synergy_sessions_search_idx 
ON synergy_sessions.sessions 
USING GIN(search_vector);

CREATE OR REPLACE FUNCTION synergy_sessions.search_sessions(
    search_query TEXT,
    user_id_param INTEGER,
    result_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    session_id INTEGER,
    session_slug TEXT,
    session_title TEXT,
    description TEXT,
    status TEXT,
    created_at TIMESTAMPTZ,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.session_id,
        s.session_slug,
        s.session_title,
        s.description,
        s.status,
        s.created_at,
        ts_rank(s.search_vector, websearch_to_tsquery('english', search_query)) as rank
    FROM synergy_sessions.sessions s
    WHERE s.user_id = user_id_param
        AND s.search_vector @@ websearch_to_tsquery('english', search_query)
    ORDER BY rank DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION synergy_sessions.search_sessions TO authenticated;


-- ============================================================================
-- STEP 5: FULL-TEXT SEARCH - INTERNAL DOCS TABLE
-- ============================================================================

ALTER TABLE ai_infrastructure.internal_docs
ADD COLUMN IF NOT EXISTS search_vector tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(content, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(category, '')), 'C') ||
    setweight(to_tsvector('english', coalesce(tags::text, '')), 'D')
) STORED;

CREATE INDEX IF NOT EXISTS internal_docs_search_idx 
ON ai_infrastructure.internal_docs 
USING GIN(search_vector);

CREATE OR REPLACE FUNCTION ai_infrastructure.search_docs(
    search_query TEXT,
    result_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    doc_id INTEGER,
    title TEXT,
    content TEXT,
    category TEXT,
    tags JSONB,
    created_at TIMESTAMPTZ,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.doc_id,
        d.title,
        d.content,
        d.category,
        d.tags,
        d.created_at,
        ts_rank(d.search_vector, websearch_to_tsquery('english', search_query)) as rank
    FROM ai_infrastructure.internal_docs d
    WHERE d.search_vector @@ websearch_to_tsquery('english', search_query)
    ORDER BY rank DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION ai_infrastructure.search_docs TO authenticated;


-- ============================================================================
-- STEP 6: PGVECTOR - AI EMBEDDINGS FOR SEMANTIC SEARCH
-- ============================================================================

-- Threads embeddings
ALTER TABLE sessions.threads
ADD COLUMN IF NOT EXISTS name_embedding vector(1536);

CREATE INDEX IF NOT EXISTS threads_embedding_idx 
ON sessions.threads 
USING ivfflat (name_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE OR REPLACE FUNCTION sessions.search_similar_threads(
    query_embedding vector(1536),
    user_id_param INTEGER,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    id INTEGER,
    thread_slug TEXT,
    name TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id,
        t.thread_slug,
        t.name,
        1 - (t.name_embedding <=> query_embedding) as similarity
    FROM sessions.threads t
    WHERE t.user_id = user_id_param
        AND t.name_embedding IS NOT NULL
        AND 1 - (t.name_embedding <=> query_embedding) > match_threshold
    ORDER BY t.name_embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION sessions.search_similar_threads TO authenticated;

-- Messages embeddings
ALTER TABLE sessions.messages
ADD COLUMN IF NOT EXISTS content_embedding vector(1536);

CREATE INDEX IF NOT EXISTS messages_embedding_idx 
ON sessions.messages 
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE OR REPLACE FUNCTION sessions.search_similar_messages(
    query_embedding vector(1536),
    user_id_param INTEGER,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 20
)
RETURNS TABLE (
    message_id INTEGER,
    thread_id INTEGER,
    role TEXT,
    content TEXT,
    created_at TIMESTAMPTZ,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.message_id,
        m.thread_id,
        m.role,
        m.content,
        m.created_at,
        1 - (m.content_embedding <=> query_embedding) as similarity
    FROM sessions.messages m
    JOIN sessions.threads t ON m.thread_id = t.id
    WHERE t.user_id = user_id_param
        AND m.content_embedding IS NOT NULL
        AND 1 - (m.content_embedding <=> query_embedding) > match_threshold
    ORDER BY m.content_embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION sessions.search_similar_messages TO authenticated;

-- Synergy Sessions embeddings
ALTER TABLE synergy_sessions.sessions
ADD COLUMN IF NOT EXISTS title_embedding vector(1536);

CREATE INDEX IF NOT EXISTS synergy_sessions_embedding_idx 
ON synergy_sessions.sessions 
USING ivfflat (title_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE OR REPLACE FUNCTION synergy_sessions.search_similar_sessions(
    query_embedding vector(1536),
    user_id_param INTEGER,
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10
)
RETURNS TABLE (
    session_id INTEGER,
    session_slug TEXT,
    session_title TEXT,
    description TEXT,
    status TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.session_id,
        s.session_slug,
        s.session_title,
        s.description,
        s.status,
        1 - (s.title_embedding <=> query_embedding) as similarity
    FROM synergy_sessions.sessions s
    WHERE s.user_id = user_id_param
        AND s.title_embedding IS NOT NULL
        AND 1 - (s.title_embedding <=> query_embedding) > match_threshold
    ORDER BY s.title_embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION synergy_sessions.search_similar_sessions TO authenticated;

-- Internal Docs embeddings
ALTER TABLE ai_infrastructure.internal_docs
ADD COLUMN IF NOT EXISTS content_embedding vector(1536);

CREATE INDEX IF NOT EXISTS internal_docs_embedding_idx 
ON ai_infrastructure.internal_docs 
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

CREATE OR REPLACE FUNCTION ai_infrastructure.search_similar_docs(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 20
)
RETURNS TABLE (
    doc_id INTEGER,
    title TEXT,
    content TEXT,
    category TEXT,
    tags JSONB,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.doc_id,
        d.title,
        d.content,
        d.category,
        d.tags,
        1 - (d.content_embedding <=> query_embedding) as similarity
    FROM ai_infrastructure.internal_docs d
    WHERE d.content_embedding IS NOT NULL
        AND 1 - (d.content_embedding <=> query_embedding) > match_threshold
    ORDER BY d.content_embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION ai_infrastructure.search_similar_docs TO authenticated;


-- ============================================================================
-- STEP 7: UNIFIED SEARCH ACROSS ALL TABLES
-- ============================================================================

CREATE OR REPLACE FUNCTION public.unified_search(
    search_query TEXT,
    user_id_param INTEGER,
    result_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    source TEXT,
    id INTEGER,
    title TEXT,
    content_preview TEXT,
    rank REAL,
    created_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    -- Search threads
    SELECT 
        'thread' as source,
        t.id,
        t.name as title,
        LEFT(t.thread_slug, 100) as content_preview,
        ts_rank(t.search_vector, websearch_to_tsquery('english', search_query)) as rank,
        t.created_at
    FROM sessions.threads t
    WHERE t.user_id = user_id_param
        AND t.search_vector @@ websearch_to_tsquery('english', search_query)
    
    UNION ALL
    
    -- Search messages
    SELECT 
        'message' as source,
        m.message_id as id,
        m.role as title,
        LEFT(m.content, 100) as content_preview,
        ts_rank(m.search_vector, websearch_to_tsquery('english', search_query)) as rank,
        m.created_at
    FROM sessions.messages m
    JOIN sessions.threads t ON m.thread_id = t.id
    WHERE t.user_id = user_id_param
        AND m.search_vector @@ websearch_to_tsquery('english', search_query)
    
    UNION ALL
    
    -- Search Synergy sessions
    SELECT 
        'synergy_session' as source,
        s.session_id as id,
        s.session_title as title,
        LEFT(s.description, 100) as content_preview,
        ts_rank(s.search_vector, websearch_to_tsquery('english', search_query)) as rank,
        s.created_at
    FROM synergy_sessions.sessions s
    WHERE s.user_id = user_id_param
        AND s.search_vector @@ websearch_to_tsquery('english', search_query)
    
    UNION ALL
    
    -- Search internal docs
    SELECT 
        'internal_doc' as source,
        d.doc_id as id,
        d.title,
        LEFT(d.content, 100) as content_preview,
        ts_rank(d.search_vector, websearch_to_tsquery('english', search_query)) as rank,
        d.created_at
    FROM ai_infrastructure.internal_docs d
    WHERE d.search_vector @@ websearch_to_tsquery('english', search_query)
    
    ORDER BY rank DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

GRANT EXECUTE ON FUNCTION public.unified_search TO authenticated;


-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check extensions enabled
SELECT extname, extversion FROM pg_extension 
WHERE extname IN ('vector', 'pg_stat_statements')
ORDER BY extname;

-- Check search columns created
SELECT 
    table_schema,
    table_name,
    column_name
FROM information_schema.columns
WHERE (table_schema = 'sessions' AND table_name IN ('threads', 'messages'))
    OR (table_schema = 'synergy_sessions' AND table_name = 'sessions')
    OR (table_schema = 'ai_infrastructure' AND table_name = 'internal_docs')
    AND (column_name LIKE '%search_vector%' OR column_name LIKE '%embedding%')
ORDER BY table_schema, table_name, column_name;

-- Check indexes created
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE (schemaname = 'sessions' AND tablename IN ('threads', 'messages'))
    OR (schemaname = 'synergy_sessions' AND tablename = 'sessions')
    OR (schemaname = 'ai_infrastructure' AND tablename = 'internal_docs')
    AND (indexname LIKE '%search_idx%' OR indexname LIKE '%embedding_idx%')
ORDER BY schemaname, tablename, indexname;


-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

-- Full-text search examples:
-- SELECT * FROM sessions.search_threads('gmail automation', 1, 10);
-- SELECT * FROM sessions.search_messages('send email', 1, 20);
-- SELECT * FROM synergy_sessions.search_sessions('project', 1, 10);
-- SELECT * FROM ai_infrastructure.search_docs('API authentication', 20);

-- Unified search (all tables at once):
-- SELECT * FROM public.unified_search('gmail', 1, 50);

-- Semantic search (requires embeddings populated first):
-- SELECT * FROM sessions.search_similar_threads('[...]'::vector, 1, 0.7, 10);
-- SELECT * FROM sessions.search_similar_messages('[...]'::vector, 1, 0.7, 20);

-- ============================================================================
-- DONE!
-- ============================================================================
-- All search features are now active.
-- Full-text search is ready to use immediately.
-- Semantic search requires populating embeddings with OpenAI API.
-- ============================================================================
