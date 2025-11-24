-- ============================================================================
-- SUPABASE EXTENSIONS ENHANCEMENT PACK
-- ============================================================================
-- PURPOSE: Add powerful extensions to enhance AI agent platform functionality
--          - Full-Text Search: Fast keyword search across threads/tools
--          - pgvector: AI embeddings for semantic search
--          - pg_jsonschema: Validate tool parameters
--          - Performance monitoring
--
-- CREATED: 2025-11-25
-- DEPLOYMENT: Run in Supabase Dashboard SQL Editor
-- ============================================================================

-- ============================================================================
-- STEP 1: ENABLE EXTENSIONS
-- ============================================================================

-- Full-Text Search (built-in, always available)
-- No extension needed - uses PostgreSQL's native text search

-- AI Embeddings & Semantic Search
DO $$ 
BEGIN
    CREATE EXTENSION IF NOT EXISTS vector;
EXCEPTION 
    WHEN OTHERS THEN 
        RAISE NOTICE 'vector extension not available or already exists';
END $$;

-- JSON Schema Validation
DO $$ 
BEGIN
    CREATE EXTENSION IF NOT EXISTS pg_jsonschema;
EXCEPTION 
    WHEN OTHERS THEN 
        RAISE NOTICE 'pg_jsonschema extension not available - validation will use fallback mode';
END $$;

-- GraphQL API (auto-generated from schema)
DO $$ 
BEGIN
    CREATE EXTENSION IF NOT EXISTS pg_graphql CASCADE;
EXCEPTION 
    WHEN OTHERS THEN 
        RAISE NOTICE 'pg_graphql extension not available or already exists';
END $$;

-- Performance Monitoring
DO $$ 
BEGIN
    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
EXCEPTION 
    WHEN OTHERS THEN 
        RAISE NOTICE 'pg_stat_statements extension not available or already exists';
END $$;

-- Verify extensions installed
SELECT 
    extname as extension_name,
    extversion as version,
    pg_catalog.obj_description(oid, 'pg_extension') as description
FROM pg_extension 
WHERE extname IN ('vector', 'pg_jsonschema', 'pg_graphql', 'pg_stat_statements', 'pg_cron', 'pg_net')
ORDER BY extname;


-- ============================================================================
-- STEP 2: FULL-TEXT SEARCH IMPLEMENTATION
-- ============================================================================
-- Enable fast keyword search across threads using PostgreSQL's native FTS

-- Add search vector column to threads table (CORRECTED COLUMN NAMES)
-- Uses 'name' column (actual thread title) instead of non-existent 'thread_title'
ALTER TABLE sessions.threads
ADD COLUMN IF NOT EXISTS search_vector tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(thread_slug, '')), 'B')
) STORED;

-- Create GIN index for lightning-fast searches (10-100x faster than ILIKE)
CREATE INDEX IF NOT EXISTS threads_search_idx 
ON sessions.threads 
USING GIN(search_vector);

-- Full-text search function (CORRECTED: returns 'id' and 'name', not thread_id/thread_title)
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

-- Grant execute to authenticated users
GRANT EXECUTE ON FUNCTION sessions.search_threads TO authenticated;

-- Test full-text search
-- SELECT * FROM sessions.search_threads('gmail automation', 1, 10);


-- ============================================================================
-- FULL-TEXT SEARCH: MESSAGES TABLE
-- ============================================================================
-- Search across message content for conversations

ALTER TABLE sessions.messages
ADD COLUMN IF NOT EXISTS search_vector tsvector
GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(content, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(role, '')), 'B')
) STORED;

CREATE INDEX IF NOT EXISTS messages_search_idx 
ON sessions.messages 
USING GIN(search_vector);

-- Search messages function
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
-- FULL-TEXT SEARCH: SYNERGY SESSIONS TABLE
-- ============================================================================
-- Search across Synergy collaboration sessions

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

-- Search Synergy sessions function
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
-- FULL-TEXT SEARCH: INTERNAL DOCS TABLE
-- ============================================================================
-- Search across internal documentation

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

-- Search internal docs function
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
-- STEP 3: PGVECTOR - AI EMBEDDINGS FOR SEMANTIC SEARCH
-- ============================================================================
-- Enable semantic search: "send email" matches gmail_send_email, outlook_send, etc.

-- Add embedding column to threads (1536 dimensions for OpenAI text-embedding-3-small)
ALTER TABLE sessions.threads
ADD COLUMN IF NOT EXISTS name_embedding vector(1536);

-- Create index for fast similarity search
CREATE INDEX IF NOT EXISTS threads_embedding_idx 
ON sessions.threads 
USING ivfflat (name_embedding vector_cosine_ops)
WITH (lists = 100);

-- Semantic similarity search function (CORRECTED COLUMN NAMES)
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

-- USAGE EXAMPLE (requires embeddings to be populated first):
-- 1. Generate embedding in Python/JavaScript using OpenAI API
-- 2. Pass embedding to function:
--    SELECT * FROM sessions.search_similar_threads('[0.123, -0.456, ...]'::vector, 1, 0.7, 10);


-- ============================================================================
-- PGVECTOR: MESSAGES TABLE
-- ============================================================================
-- Semantic search for message content

ALTER TABLE sessions.messages
ADD COLUMN IF NOT EXISTS content_embedding vector(1536);

CREATE INDEX IF NOT EXISTS messages_embedding_idx 
ON sessions.messages 
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

-- Semantic search for messages
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


-- ============================================================================
-- PGVECTOR: SYNERGY SESSIONS TABLE
-- ============================================================================
-- Semantic search for Synergy collaboration sessions

ALTER TABLE synergy_sessions.sessions
ADD COLUMN IF NOT EXISTS title_embedding vector(1536);

CREATE INDEX IF NOT EXISTS synergy_sessions_embedding_idx 
ON synergy_sessions.sessions 
USING ivfflat (title_embedding vector_cosine_ops)
WITH (lists = 100);

-- Semantic search for Synergy sessions
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


-- ============================================================================
-- PGVECTOR: INTERNAL DOCS TABLE
-- ============================================================================
-- Semantic search for internal documentation

ALTER TABLE ai_infrastructure.internal_docs
ADD COLUMN IF NOT EXISTS content_embedding vector(1536);

CREATE INDEX IF NOT EXISTS internal_docs_embedding_idx 
ON ai_infrastructure.internal_docs 
USING ivfflat (content_embedding vector_cosine_ops)
WITH (lists = 100);

-- Semantic search for internal docs
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
-- STEP 4: JSON SCHEMA VALIDATION FOR TOOL PARAMETERS
-- ============================================================================
-- Prevent bad tool executions by validating parameters before API calls

-- Example: Validate Gmail send_email parameters
-- Note: This function requires pg_jsonschema extension
-- If extension not available, it does basic validation only
CREATE OR REPLACE FUNCTION public.validate_gmail_params(params JSONB)
RETURNS BOOLEAN AS $$
BEGIN
    -- Check if pg_jsonschema extension is available
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_jsonschema') THEN
        -- Use full JSON schema validation
        RETURN jsonb_matches_schema(
            schema := '{
                "type": "object",
                "required": ["to", "subject", "body"],
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                    "cc": {"type": "array"},
                    "attachments": {"type": "array"}
                }
            }'::jsonb,
            instance := params
        );
    ELSE
        -- Fallback: Basic validation (check required fields exist)
        RETURN (
            params ? 'to' AND
            params ? 'subject' AND
            params ? 'body' AND
            (params->>'to') IS NOT NULL AND
            (params->>'subject') IS NOT NULL AND
            (params->>'body') IS NOT NULL
        );
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        -- If any error occurs, do basic validation
        RETURN (
            params ? 'to' AND
            params ? 'subject' AND
            params ? 'body'
        );
END;
$$ LANGUAGE plpgsql;

-- Test validation
-- SELECT public.validate_gmail_params('{"to": "test@example.com", "subject": "Test", "body": "Hello"}'::JSONB); -- Returns TRUE
-- SELECT public.validate_gmail_params('{"subject": "Missing To"}'::JSONB); -- Returns FALSE


-- ============================================================================
-- STEP 5: WEBHOOK NOTIFICATIONS WITH PG_NET
-- ============================================================================
-- Send webhooks when workflows complete or threads are updated

-- Webhook notification function for workflow completion
CREATE OR REPLACE FUNCTION public.notify_workflow_completion()
RETURNS TRIGGER AS $$
DECLARE
    webhook_url TEXT;
    response_id BIGINT;
BEGIN
    -- Get user's webhook URL (assumes you have a user_settings table)
    -- webhook_url := (SELECT webhook_endpoint FROM user_settings WHERE user_id = NEW.user_id);
    
    -- For demo, use a placeholder URL (replace with actual webhook endpoint)
    webhook_url := 'https://your-webhook-endpoint.com/workflow-complete';
    
    -- Send async HTTP POST request
    IF webhook_url IS NOT NULL THEN
        SELECT net.http_post(
            url := webhook_url,
            headers := jsonb_build_object(
                'Content-Type', 'application/json',
                'X-Workflow-ID', NEW.automation_id
            ),
            body := jsonb_build_object(
                'event', 'workflow_completed',
                'workflow_id', NEW.automation_id,
                'workflow_title', NEW.title,
                'status', NEW.status,
                'timestamp', NOW()
            )
        ) INTO response_id;
        
        RAISE LOG 'Webhook sent for workflow % (response_id: %)', NEW.automation_id, response_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Note: Uncomment to enable webhook trigger (adjust table name if needed)
-- CREATE TRIGGER workflow_completion_webhook
-- AFTER UPDATE ON automation_workflows
-- FOR EACH ROW
-- WHEN (OLD.status != 'completed' AND NEW.status = 'completed')
-- EXECUTE FUNCTION public.notify_workflow_completion();


-- ============================================================================
-- STEP 6: PERFORMANCE MONITORING QUERIES
-- ============================================================================
-- Use pg_stat_statements to find slow queries

-- View slowest queries (requires pg_stat_statements enabled)
-- Note: This view will only work if pg_stat_statements extension is installed
DO $$ 
BEGIN
    -- Only create view if pg_stat_statements exists
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements') THEN
        EXECUTE '
            CREATE OR REPLACE VIEW public.slow_queries AS
            SELECT 
                query,
                calls,
                total_exec_time::numeric(10,2) as total_time_ms,
                mean_exec_time::numeric(10,2) as avg_time_ms,
                max_exec_time::numeric(10,2) as max_time_ms,
                rows as total_rows
            FROM pg_stat_statements
            WHERE query NOT LIKE ''%pg_stat_statements%''
            ORDER BY mean_exec_time DESC
            LIMIT 50
        ';
        RAISE NOTICE 'slow_queries view created successfully';
    ELSE
        RAISE NOTICE 'pg_stat_statements not available - skipping slow_queries view creation';
    END IF;
END $$;

-- Check slow queries (only if pg_stat_statements is available)
-- SELECT * FROM public.slow_queries;


-- ============================================================================
-- MONITORING & VERIFICATION
-- ============================================================================

-- Verify all extensions are enabled
SELECT 
    extname,
    extversion,
    CASE 
        WHEN extname = 'vector' THEN '✅ AI embeddings enabled'
        WHEN extname = 'pg_jsonschema' THEN '✅ JSON validation enabled'
        WHEN extname = 'pg_graphql' THEN '✅ GraphQL API enabled'
        WHEN extname = 'pg_stat_statements' THEN '✅ Performance monitoring enabled'
        WHEN extname = 'pg_cron' THEN '✅ Scheduled jobs enabled'
        WHEN extname = 'pg_net' THEN '✅ HTTP requests enabled'
        ELSE '✅ ' || extname || ' enabled'
    END as status
FROM pg_extension
WHERE extname IN ('vector', 'pg_jsonschema', 'pg_graphql', 'pg_stat_statements', 'pg_cron', 'pg_net')
ORDER BY extname;

-- Check ALL tables have search columns
SELECT 
    table_schema,
    table_name,
    column_name,
    data_type,
    CASE 
        WHEN column_name LIKE '%search_vector%' THEN '✅ Full-text search'
        WHEN column_name LIKE '%embedding%' THEN '✅ Semantic search'
        ELSE ''
    END as feature
FROM information_schema.columns
WHERE (table_schema = 'sessions' AND table_name IN ('threads', 'messages'))
    OR (table_schema = 'synergy_sessions' AND table_name = 'sessions')
    OR (table_schema = 'ai_infrastructure' AND table_name = 'internal_docs')
    AND (column_name LIKE '%search_vector%' OR column_name LIKE '%embedding%')
ORDER BY table_schema, table_name, column_name;

-- Check ALL indexes created
SELECT 
    schemaname,
    tablename,
    indexname,
    CASE 
        WHEN indexname LIKE '%search_idx%' THEN '✅ Full-text search index'
        WHEN indexname LIKE '%embedding_idx%' THEN '✅ Vector similarity index'
        ELSE ''
    END as purpose
FROM pg_indexes
WHERE (schemaname = 'sessions' AND tablename IN ('threads', 'messages'))
    OR (schemaname = 'synergy_sessions' AND tablename = 'sessions')
    OR (schemaname = 'ai_infrastructure' AND tablename = 'internal_docs')
    AND (indexname LIKE '%search_idx%' OR indexname LIKE '%embedding_idx%')
ORDER BY schemaname, tablename, indexname;


-- ============================================================================
-- USAGE EXAMPLES
-- ============================================================================

-- ===========================
-- THREADS SEARCH
-- ===========================
-- Full-text: Search threads by keyword
-- SELECT * FROM sessions.search_threads('email automation', 1, 10);

-- Semantic: Find similar threads by meaning (requires embeddings)
-- SELECT * FROM sessions.search_similar_threads('[...]'::vector, 1, 0.7, 10);


-- ===========================
-- MESSAGES SEARCH
-- ===========================
-- Full-text: Search message content
-- SELECT * FROM sessions.search_messages('gmail send email', 1, 20);

-- Semantic: Find similar messages by meaning
-- SELECT * FROM sessions.search_similar_messages('[...]'::vector, 1, 0.7, 20);


-- ===========================
-- SYNERGY SESSIONS SEARCH
-- ===========================
-- Full-text: Search Synergy sessions
-- SELECT * FROM synergy_sessions.search_sessions('collaboration project', 1, 10);

-- Semantic: Find similar Synergy sessions
-- SELECT * FROM synergy_sessions.search_similar_sessions('[...]'::vector, 1, 0.7, 10);


-- ===========================
-- INTERNAL DOCS SEARCH
-- ===========================
-- Full-text: Search documentation
-- SELECT * FROM ai_infrastructure.search_docs('API authentication', 20);

-- Semantic: Find similar docs by topic
-- SELECT * FROM ai_infrastructure.search_similar_docs('[...]'::vector, 0.7, 20);


-- ===========================
-- UNIFIED SEARCH (ALL TABLES)
-- ===========================
-- Search everything at once for comprehensive results
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
    
    -- Search internal docs (no user filter)
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

-- Example: Search across all tables
-- SELECT * FROM public.unified_search('gmail automation', 1, 20);


-- ===========================
-- OTHER EXAMPLES
-- ===========================
-- Validate tool parameters before execution
-- SELECT public.validate_gmail_params('{"to": "user@example.com", "subject": "Test"}'::JSONB);

-- Check slow queries
-- SELECT * FROM public.slow_queries LIMIT 10;


-- ============================================================================
-- NOTES & RECOMMENDATIONS
-- ============================================================================
-- 
-- ✅ IMPLEMENTED:
-- 1. Full-Text Search - Fast keyword search across ALL tables:
--    - sessions.threads (by name, thread_slug)
--    - sessions.messages (by content, role)
--    - synergy_sessions.sessions (by session_title, description, status)
--    - ai_infrastructure.internal_docs (by title, content, category, tags)
--
-- 2. pgvector - AI embeddings for semantic similarity search:
--    - sessions.threads (name_embedding)
--    - sessions.messages (content_embedding)
--    - synergy_sessions.sessions (title_embedding)
--    - ai_infrastructure.internal_docs (content_embedding)
--
-- 3. Unified Search - Search across all tables with one query
--
-- 4. pg_jsonschema - Validate JSON parameters before tool execution
--
-- 5. pg_stat_statements - Monitor slow queries
--
-- 6. Webhook notifications - Send HTTP POST on workflow completion
--
-- 🔄 NEXT STEPS:
-- 1. Populate embeddings for ALL tables:
--    A. Threads: UPDATE sessions.threads SET name_embedding = '[...]'::vector WHERE id = X
--    B. Messages: UPDATE sessions.messages SET content_embedding = '[...]'::vector WHERE message_id = X
--    C. Synergy Sessions: UPDATE synergy_sessions.sessions SET title_embedding = '[...]'::vector WHERE session_id = X
--    D. Internal Docs: UPDATE ai_infrastructure.internal_docs SET content_embedding = '[...]'::vector WHERE doc_id = X
--    
--    Use OpenAI text-embedding-3-small API (1536 dimensions):
--    ```python
--    import openai
--    response = openai.embeddings.create(
--        model="text-embedding-3-small",
--        input="Your text here"
--    )
--    embedding = response.data[0].embedding
--    ```
--
-- 2. Add search to frontend (4 search types):
--    - Full-text search: sessions.search_threads(), search_messages(), etc.
--    - Semantic search: sessions.search_similar_threads(), search_similar_messages(), etc.
--    - Unified search: public.unified_search() (searches all tables at once)
--    - Faceted search: Filter by source (thread/message/synergy/docs)
--
-- 3. Backend integration examples:
--    A. Flask route for unified search:
--       @app.route('/api/search', methods=['POST'])
--       def unified_search():
--           query = request.json['query']
--           user_id = get_current_user_id()
--           results = db.execute("SELECT * FROM public.unified_search(%s, %s, 50)", (query, user_id))
--           return jsonify(results)
--
--    B. Semantic search with embedding generation:
--       embedding = generate_embedding(user_query)  # OpenAI API
--       results = db.execute("SELECT * FROM sessions.search_similar_threads(%s::vector, %s)", 
--                           (str(embedding), user_id))
--
-- 4. Add parameter validation to tool execution:
--    - Before calling Gmail API, validate with validate_gmail_params()
--    - Create similar validators for other tools (Slack, Stripe, etc.)
--
-- 5. Enable webhook trigger:
--    - Uncomment workflow_completion_webhook trigger
--    - Configure webhook_endpoint in user settings
--
-- 6. Monitor performance:
--    - Query slow_queries view weekly
--    - Add indexes for frequently filtered columns
--    - Monitor search query performance with pg_stat_statements
--
-- 📊 BENEFITS:
-- - Full-text search: 10-100x faster than ILIKE '%keyword%' across 4 tables
-- - Semantic search: Find content by meaning, not exact keywords
-- - Unified search: Single query searches threads, messages, Synergy, docs simultaneously
-- - Cross-table discovery: "email automation" finds threads, messages, AND docs about it
-- - Parameter validation: Prevent bad API calls before execution
-- - Performance monitoring: Identify bottlenecks automatically
-- - Webhooks: Notify external systems without polling
--
-- 🎯 USE CASES:
-- 1. Search bar: User types "gmail" → Finds all Gmail-related threads, messages, docs
-- 2. Message history: "Show me all conversations about Stripe integration"
-- 3. Synergy discovery: "Find collaboration sessions about project Alpha"
-- 4. Documentation lookup: "How do I authenticate with OAuth?"
-- 5. Similar content: "Find threads similar to this one" (semantic embeddings)
-- 6. Cross-reference: Search finds thread, then shows related messages and docs
--
-- 🔒 SECURITY:
-- - All functions use SECURITY DEFINER (run as creator)
-- - GRANT EXECUTE to authenticated role only
-- - Webhook URLs should be validated before use
-- - Consider rate limiting for webhook notifications
--
-- ============================================================================
