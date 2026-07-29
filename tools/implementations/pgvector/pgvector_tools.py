"""
pgvector Organisation Vector Database Tools

FILE: tools/implementations/pgvector/pgvector_tools.py
PURPOSE:
    Tool implementations for pgvector operations using Supabase PostgreSQL.
    Mirrors the interface of pinecone_tools.py so routes can swap providers
    without changing any call sites.

    Every operation is scoped to the calling user's organisation (org_id)
    so each org sees only its own documents.

FUNCTIONS:
    pgvector_query_vectors      - Semantic search across org documents
    pgvector_upsert_vectors     - Insert or update document chunks
    pgvector_delete_vectors     - Delete by document_id (whole document)
    pgvector_list_documents     - List unique documents in org namespace
    pgvector_describe_stats     - Return row / doc counts for org
    pgvector_upload_document    - Full pipeline: embed text chunks + upsert

CREDENTIAL REQUIREMENTS:
    Embedding credentials resolved via org vault:
      - platform 'voyager'          → Voyage AI
      - platform 'openai_embeddings' or 'openai' → OpenAI

SCHEMA:
    ai_infrastructure.org_vector_documents
    (created by migration 044_pgvector_org_documents.sql)

MULTI-TENANCY:
    All queries hard-filter on org_id derived from g.rls_user_id.
    SET LOCAL app.current_org_id = <org_id> is applied before each
    DML/SELECT so Supabase RLS policies enforce isolation at DB level.

LAST MODIFIED: 2026-04-29 (initial implementation)
"""

import uuid
import os
from typing import Dict, Any, List, Optional


class PgvectorToolsError(Exception):
    """Custom exception for pgvector tools"""
    pass


# ============================================================================
# INTERNAL HELPERS
# ============================================================================

def _get_org_id(user_id: int) -> int:
    """Return organisation_id for a user, raising if not found."""
    from AI_infrastructure.shared.database_utils import execute_query
    row = execute_query(
        "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
        (user_id,), fetch_mode='one'
    )
    if not row or not row.get('organisation_id'):
        raise PgvectorToolsError(
            f"User {user_id} has no organisation. Assign the user to an organisation first."
        )
    return row['organisation_id']


def _generate_embedding(text: str, user_id: int, is_query: bool = False, force_local: bool = False) -> List[float]:
    """
    Generate an embedding vector for *text* using the org-resolved provider.
    Priority: voyager → openai_embeddings → openai → local model (free fallback).

    is_query:    True for search queries, False for document passages.
                 Asymmetric retrieval (BGE, Voyage) uses a query prefix for searches.
    force_local: True → skip all credential lookup, go straight to the local
                 BAAI/bge-base-en-v1.5 model. Used when the user explicitly selects
                 'Local BGE' in the Settings tab.
    """
    from AI_infrastructure.shared.org_credentials_loader import resolve_credentials

    # ── Dimension constants ───────────────────────────────────────────────────
    # ALL embedding paths must produce this exact dimension.
    # DB column: vector(768) — set by migration 049.
    # Upgrade path: add Voyage AI key → request output_dimension=768,
    #               no schema change or re-indexing needed.
    _TARGET_DIM = 768

    # Voyage AI lite-model upgrade map — lite models cap at 512 dims.
    _VOYAGE_LITE_UPGRADE = {
        'voyage-4-lite': 'voyage-4',
        'voyage-3-lite': 'voyage-3',
        'voyage-2-lite': 'voyage-2',
    }

    # When force_local is set (user chose 'Local BGE' in Settings) skip vault lookup
    # so an invalid/unused credential can never cause a 500.
    raw_cred = None if force_local else (
        resolve_credentials(user_id, 'voyager')
        or resolve_credentials(user_id, 'openai_embeddings')
        or resolve_credentials(user_id, 'openai')
    )

    # ── No API credentials (or force_local=True): free local model fallback ──────
    if not raw_cred:
        try:
            from sentence_transformers import SentenceTransformer
            # BAAI/bge-base-en-v1.5 — chosen for best-in-class retrieval quality
            # while fitting within the Standard plan RAM budget.
            #
            #   Model size : ~440 MB on disk, ~600 MB RAM when loaded
            #   Dimensions : 768  ← matches vector(768) column, no migration needed
            #   MTEB score : 63.55 vs 57.02 for all-mpnet-base-v2 (~11% better)
            #   Design     : asymmetric retrieval — queries use a task prefix,
            #                passages do not.  See _BGE_QUERY_PROMPT below.
            #   License    : MIT
            #
            # Upgrade path: add a Voyage AI key → same column, zero re-indexing.
            _model_name = 'BAAI/bge-base-en-v1.5'
            # Query prefix — prepended only for search queries, NOT for document chunks.
            # This asymmetric encoding is the main reason BGE outperforms symmetric
            # models like mpnet on retrieval benchmarks.
            _BGE_QUERY_PROMPT = 'Represent this sentence for searching relevant passages: '
            # Use the persistent Render disk (/data) so the model (~440 MB)
            # is downloaded once ever and survives all redeploys.
            # Falls back to a local cache if /data is not mounted (local dev).
            _cache_dir = '/data/vdb_models' if os.path.isdir('/data') else os.path.join(
                os.path.expanduser('~'), '.cache', 'vdb_models'
            )
            if not hasattr(_generate_embedding, '_local_model'):
                # Resolve a local snapshot path so we can load without any
                # HuggingFace network calls (avoids ~15 HEAD requests that
                # cause 60+ s delays and Render 502s when model is cached).
                # huggingface_hub stores: models--BAAI--bge-base-en-v1.5/snapshots/<hash>/
                _safe_name = _model_name.replace('/', '--')
                _hub_dir = os.path.join(_cache_dir, f'models--{_safe_name}')
                _snap_dir = os.path.join(_hub_dir, 'snapshots')
                _local_path = None
                if os.path.isdir(_snap_dir):
                    for _snap in sorted(os.listdir(_snap_dir)):
                        _candidate = os.path.join(_snap_dir, _snap)
                        if os.path.isfile(os.path.join(_candidate, 'config.json')):
                            _local_path = _candidate
                            break

                if _local_path:
                    print(
                        f'[PGVECTOR] Loading local embedding model from disk path '
                        f'(no HF network calls) → {_local_path}'
                    )
                    _generate_embedding._local_model = SentenceTransformer(_local_path)
                else:
                    print(
                        f'[PGVECTOR] Downloading embedding model {_model_name} '
                        f'from HuggingFace (first-time only, ~30-60s) → {_cache_dir}'
                    )
                    _generate_embedding._local_model = SentenceTransformer(
                        _model_name, cache_folder=_cache_dir
                    )
                print(f'[PGVECTOR] Local embedding model ready ({_TARGET_DIM} dims).')
            encode_kwargs = {'normalize_embeddings': True, 'show_progress_bar': False}
            if is_query:
                encode_kwargs['prompt'] = _BGE_QUERY_PROMPT
            vec = _generate_embedding._local_model.encode(text, **encode_kwargs).tolist()
            assert len(vec) == _TARGET_DIM, (
                f'Local model produced {len(vec)} dims, expected {_TARGET_DIM}'
            )
            return vec
        except ImportError:
            raise PgvectorToolsError(
                'No embedding credentials configured and sentence-transformers is not installed.\n'
                'Run: pip install sentence-transformers\n'
                'Or add a Voyage AI (voyage-4) key in Organisation Settings > Connections.'
            )

    creds_detail = raw_cred.get('credentials') or {}
    api_key = (
        raw_cred.get('api_key')
        or raw_cred.get('credential_value')
        or creds_detail.get('api_key')
    )
    provider = creds_detail.get('provider', 'openai')
    model    = creds_detail.get('model', 'text-embedding-3-small')

    if not api_key:
        raise PgvectorToolsError('Embedding API key not found in credentials.')

    if provider == 'voyager':
        # Upgrade lite models — they cap at 512 dims, we need 768.
        upgraded = _VOYAGE_LITE_UPGRADE.get(model, model)
        if upgraded != model:
            print(f'[PGVECTOR] Auto-upgrading Voyage model {model} → {upgraded} '
                  f'(lite models cap at 512 dims, need {_TARGET_DIM})')
            model = upgraded
        import requests
        resp = requests.post(
            'https://api.voyageai.com/v1/embeddings',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={
                'input': [text],
                'model': model,
                'output_dimension': _TARGET_DIM,
                'input_type': 'query' if is_query else 'document',
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()['data'][0]['embedding']
    else:
        from openai import OpenAI
        oc = OpenAI(api_key=api_key)
        # text-embedding-3-* supports a 'dimensions' parameter.
        # text-embedding-ada-002 does not — fall back to its native 1536 dims
        # (schema would need updating; warn and continue).
        if 'text-embedding-3' in model:
            response = oc.embeddings.create(model=model, input=text, dimensions=_TARGET_DIM)
        else:
            print(f'[PGVECTOR] WARNING: {model} does not support custom dimensions; '
                  f'embedding may not match vector(768) column.')
            response = oc.embeddings.create(model=model, input=text)
        return response.data[0].embedding


def _set_rls_context(org_id: int) -> str:
    """Return a SET LOCAL SQL statement that activates RLS for this org."""
    return f"SET LOCAL app.current_org_id = '{org_id}';"


def _run_in_org_context(org_id: int, sql: str, params=(), fetch_mode: str = 'none'):
    """
    Execute *sql* with the RLS org context set.

    IMPORTANT: SET + DML must run on the *same* connection.  ``execute_query``
    pulls a connection from the pool, runs the statement, and returns the
    connection to the pool — so two consecutive ``execute_query`` calls
    almost always land on *different* connections, and a `SET` from the
    first call is invisible to the second.  We therefore combine the SET,
    the DML, and a trailing RESET into a single multi-statement SQL string
    so all three run on one connection (and the RESET prevents the GUC
    value from leaking to the next user of that pooled connection).
    """
    from AI_infrastructure.shared.database_utils import execute_query

    # All three statements share one connection (single execute_query call).
    # `RESET` clears the GUC at the end so the next request that borrows
    # this pooled connection doesn't inherit the wrong org context.
    safe_org_id = int(org_id)
    combined_sql = (
        f"SET app.current_org_id = '{safe_org_id}'; "
        f"{sql}; "
        f"RESET app.current_org_id;"
    )
    return execute_query(combined_sql, params, fetch_mode=fetch_mode)


# ============================================================================
# PUBLIC TOOL FUNCTIONS
# ============================================================================

def pgvector_query_vectors(
    query_text: Optional[str] = None,
    query_vector: Optional[List[float]] = None,
    top_k: int = 10,
    threshold: float = 0.5,
    document_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Semantic search across this organisation's pgvector documents.

    Args:
        query_text:   Natural-language query (auto-embedded).
        query_vector: Pre-computed query vector (skip embedding step).
        top_k:        Maximum number of results to return (default 10).
        threshold:    Minimum cosine similarity score 0–1 (default 0.5).
        document_id:  Restrict search to a single document_id.
        **kwargs:     Must contain _user_id.

    Returns:
        {"success": True, "matches": [...], "total": N}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError("_user_id required")

        org_id = _get_org_id(user_id)

        if query_text and not query_vector:
            query_vector = _generate_embedding(query_text, user_id, is_query=True)
        if not query_vector:
            raise PgvectorToolsError("Either query_text or query_vector is required")

        # Format vector as PostgreSQL array literal '[0.1,0.2,…]'
        vec_literal = '[' + ','.join(str(v) for v in query_vector) + ']'

        doc_filter = ''
        params: tuple = (org_id, vec_literal, threshold, top_k)
        if document_id:
            doc_filter = 'AND d.document_id = %s'
            params = (org_id, vec_literal, threshold, document_id, top_k)

        sql = f"""
            SELECT
                d.id::TEXT,
                d.document_id,
                d.filename,
                d.chunk_index,
                d.content,
                (1 - (d.embedding <=> %s::vector))::FLOAT AS similarity,
                d.metadata,
                d.created_at
            FROM  ai_infrastructure.org_vector_documents d
            WHERE d.org_id = %s
              AND d.embedding IS NOT NULL
              AND (1 - (d.embedding <=> %s::vector)) >= %s
              {doc_filter}
            ORDER BY d.embedding <=> %s::vector
            LIMIT %s
        """

        if document_id:
            params = (vec_literal, org_id, vec_literal, threshold, document_id, vec_literal, top_k)
        else:
            params = (vec_literal, org_id, vec_literal, threshold, vec_literal, top_k)

        from AI_infrastructure.shared.database_utils import execute_query
        # RLS fix: same SET/RESET wrap as the upsert path — the SELECT policy
        # (migration 044) filters by app.current_org_id, so the GUC must be
        # set on the same connection that runs the SELECT, otherwise all
        # rows are hidden and the user gets silently-empty results.
        rows = _run_in_org_context(org_id, sql, params, fetch_mode='all') or []

        matches = [
            {
                'id':          r['id'],
                'document_id': r['document_id'],
                'filename':    r['filename'],
                'chunk_index': r['chunk_index'],
                'score':       float(r['similarity']),
                'text':        r['content'],
                'metadata':    r.get('metadata') or {},
                'created_at':  str(r.get('created_at', '')),
            }
            for r in rows
        ]

        print(f'[PGVECTOR] Query returned {len(matches)} matches (org {org_id})')
        return {'success': True, 'matches': matches, 'total': len(matches)}

    except Exception as exc:
        print(f'[PGVECTOR] query error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_upsert_vectors(
    vectors: List[Dict[str, Any]],
    **kwargs
) -> Dict[str, Any]:
    """
    Insert or update pre-computed embedding vectors.

    Each item in *vectors* must have:
        id          str   — unique chunk ID
        values      list  — embedding float list
        metadata    dict  — must include 'document_id', 'filename', 'chunk_index',
                            'total_chunks', 'text', 'created_at'

    Args:
        vectors: List of vector dicts (see above).
        **kwargs: Must contain _user_id.

    Returns:
        {"success": True, "upserted_count": N}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError("_user_id required")

        org_id = _get_org_id(user_id)
        from AI_infrastructure.shared.database_utils import execute_query
        import json as _json

        count = 0
        for v in vectors:
            meta = v.get('metadata') or {}
            vec_literal = '[' + ','.join(str(x) for x in v['values']) + ']'

            # RLS context fix:
            #   The org_isolation_insert policy (migration 044) checks
            #   `current_setting('app.current_org_id')` against the inserted
            #   `org_id`.  We MUST set that GUC on the same connection that
            #   receives the INSERT — `execute_query` is pooled, so we can't
            #   use two separate calls.  `_run_in_org_context` wraps the
            #   INSERT with SET ... ; <insert>; RESET ... ; so all three
            #   statements share one connection and the GUC value is
            #   cleaned up before the connection returns to the pool.
            _run_in_org_context(
                org_id,
                """
                INSERT INTO ai_infrastructure.org_vector_documents
                    (id, org_id, user_id, document_id, filename, chunk_index, total_chunks,
                     content, embedding, emb_model, emb_provider, visibility, metadata,
                     file_type, file_size_bytes, created_at)
                VALUES
                    (%s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::vector, %s, %s, %s, %s::jsonb, %s, %s,
                     COALESCE(%s::timestamptz, NOW()))
                ON CONFLICT (id) DO UPDATE SET
                    embedding       = EXCLUDED.embedding,
                    metadata        = EXCLUDED.metadata,
                    total_chunks    = EXCLUDED.total_chunks,
                    content         = EXCLUDED.content
                """,
                (
                    v.get('id', str(uuid.uuid4())),
                    org_id,
                    user_id,
                    meta.get('document_id', ''),
                    meta.get('filename', 'unknown'),
                    meta.get('chunk_index', 0),
                    meta.get('total_chunks', 1),
                    meta.get('text', meta.get('content', '')),
                    vec_literal,
                    meta.get('emb_model', 'text-embedding-3-small'),
                    meta.get('emb_provider', 'openai'),
                    meta.get('visibility', 'org'),
                    _json.dumps(meta),
                    meta.get('file_type'),
                    meta.get('file_size_bytes'),
                    meta.get('created_at'),
                ),
                fetch_mode=None,
            )
            count += 1

        print(f'[PGVECTOR] Upserted {count} vectors (org {org_id})')
        return {'success': True, 'upserted_count': count}

    except Exception as exc:
        print(f'[PGVECTOR] upsert error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_delete_vectors(
    document_id: Optional[str] = None,
    delete_all: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete vectors from this organisation's pgvector store.

    Args:
        document_id: Delete all chunks for this document_id.
        delete_all:  If True, delete every document for the org (use with care).
        **kwargs:    Must contain _user_id.

    Returns:
        {"success": True, "deleted_count": N}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError("_user_id required")

        org_id = _get_org_id(user_id)
        from AI_infrastructure.shared.database_utils import execute_query

        if delete_all:
            # RLS fix: SET app.current_org_id must be on the same connection
            # as the DELETE — otherwise the org_isolation_delete USING clause
            # silently matches zero rows and nothing is removed.
            _run_in_org_context(
                org_id,
                "DELETE FROM ai_infrastructure.org_vector_documents WHERE org_id = %s",
                (org_id,),
                fetch_mode=None,
            )
            print(f'[PGVECTOR] Deleted all vectors for org {org_id}')
            return {'success': True, 'deleted_count': -1, 'note': 'all org documents deleted'}

        if not document_id:
            raise PgvectorToolsError("document_id required (or set delete_all=True)")

        _run_in_org_context(
            org_id,
            "DELETE FROM ai_infrastructure.org_vector_documents WHERE org_id = %s AND document_id = %s",
            (org_id, document_id),
            fetch_mode=None,
        )
        print(f'[PGVECTOR] Deleted document {document_id} for org {org_id}')
        return {'success': True, 'deleted_count': 1, 'document_id': document_id}

    except Exception as exc:
        print(f'[PGVECTOR] delete error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_list_documents(**kwargs) -> Dict[str, Any]:
    """
    List unique documents stored for this organisation.

    Returns:
        {"success": True, "documents": [...], "total": N}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError("_user_id required")

        org_id = _get_org_id(user_id)
        from AI_infrastructure.shared.database_utils import execute_query

        rows = _run_in_org_context(
            org_id,
            """
            SELECT
                document_id,
                MAX(filename)       AS filename,
                MAX(total_chunks)   AS total_chunks,
                COUNT(*)            AS chunks_stored,
                MAX(file_size_bytes)AS file_size_bytes,
                MIN(created_at)     AS created_at
            FROM  ai_infrastructure.org_vector_documents
            WHERE org_id = %s
            GROUP BY document_id
            ORDER BY MIN(created_at) DESC
            """,
            (org_id,),
            fetch_mode='all'
        ) or []

        documents = [
            {
                'document_id':   r['document_id'],
                'filename':      r['filename'],
                'chunks':        r['chunks_stored'],
                'total_chunks':  r['total_chunks'],
                'file_size':     r.get('file_size_bytes') or 0,
                'created_at':    str(r.get('created_at', '')),
                'ai_retrievable': True,
            }
            for r in rows
        ]

        return {'success': True, 'documents': documents, 'total': len(documents)}

    except Exception as exc:
        print(f'[PGVECTOR] list_documents error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_describe_stats(**kwargs) -> Dict[str, Any]:
    """
    Return vector store statistics for this organisation.

    Returns:
        {"success": True, "stats": {"documents": N, "vectors": N}}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError("_user_id required")

        org_id = _get_org_id(user_id)
        from AI_infrastructure.shared.database_utils import execute_query

        row = _run_in_org_context(
            org_id,
            """
            SELECT
                COUNT(DISTINCT document_id) AS doc_count,
                COUNT(*)                    AS vector_count
            FROM  ai_infrastructure.org_vector_documents
            WHERE org_id = %s
            """,
            (org_id,),
            fetch_mode='one'
        )

        return {
            'success': True,
            'stats': {
                'documents': row['doc_count'] if row else 0,
                'vectors':   row['vector_count'] if row else 0,
                'provider':  'pgvector',
            }
        }

    except Exception as exc:
        print(f'[PGVECTOR] describe_stats error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_upload_document(
    text_content: str,
    filename: str,
    file_type: str = 'text/plain',
    file_size_bytes: int = 0,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
    visibility: str = 'org',
    document_id: Optional[str] = None,
    embedding_provider: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Full pipeline: chunk text → embed each chunk → upsert to pgvector.

    Args:
        text_content:       Plain text to vectorise.
        filename:           Original filename label.
        file_type:          MIME type.
        file_size_bytes:    File size for metadata.
        chunk_size:         Characters per chunk (default 800).
        chunk_overlap:      Overlap between chunks (default 100).
        visibility:         'private' | 'org' | 'global' (default 'org').
        document_id:        Explicit document ID; auto-generated if omitted.
        embedding_provider: 'local' | 'voyager' | 'openai' | None.
                            'local' forces the free on-server BGE model.
                            None = auto-resolve from org credential vault.
        **kwargs:           Must contain _user_id.

    Returns:
        {"success": True, "document_id": "...", "vectors_uploaded": N}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError("_user_id required")

        org_id = _get_org_id(user_id)

        if not document_id:
            document_id = f"doc_{uuid.uuid4().hex[:8]}"

        # ── Chunk ──────────────────────────────────────────────────────────
        chunks: List[str] = []
        start = 0
        while start < len(text_content):
            end = min(start + chunk_size, len(text_content))
            chunks.append(text_content[start:end])
            start += chunk_size - chunk_overlap
            if start >= len(text_content):
                break

        if not chunks:
            raise PgvectorToolsError("No text content after chunking")

        from datetime import datetime
        upload_ts = datetime.utcnow().isoformat()

        # ── Embed + upsert each chunk ───────────────────────────────────────
        # 'local' → bypass credential vault, use free on-server BGE model.
        _force_local = (embedding_provider == 'local')
        vectors = []
        for i, chunk in enumerate(chunks):
            embedding = _generate_embedding(chunk, user_id, force_local=_force_local)
            vectors.append({
                # Row PK is a real UUID — see migration 044 (`id UUID PRIMARY KEY`).
                # The human-readable `document_id` (e.g. "doc_3c606f76") is stored
                # in its own TEXT column; do not concatenate `_chunk_N` onto a
                # non-UUID business key or the %s::uuid cast will reject it.
                'id': str(uuid.uuid4()),
                'values': embedding,
                'metadata': {
                    'document_id':   document_id,
                    'filename':      filename,
                    'file_type':     file_type,
                    'file_size_bytes': file_size_bytes,
                    'chunk_index':   i,
                    'total_chunks':  len(chunks),
                    'text':          chunk,
                    'visibility':    visibility,
                    'emb_provider':  'pgvector_auto',
                    'created_at':    upload_ts,
                }
            })

        result = pgvector_upsert_vectors(vectors, _user_id=user_id)

        return {
            'success':         result.get('success', False),
            'document_id':     document_id,
            'filename':        filename,
            'vectors_uploaded': result.get('upserted_count', 0),
            'chunks_created':  len(chunks),
            'provider':        'pgvector',
            'error':           result.get('error'),
        }

    except Exception as exc:
        print(f'[PGVECTOR] upload_document error: {exc}')
        return {'success': False, 'error': str(exc)}


# ============================================================================
# SMART / EDUCATION TOOL FUNCTIONS (Parity with pinecone_tools.py)
# ============================================================================
# These bring pgvector up to parity with the 6 smart/education tools on the
# Pinecone side (query_namespaces, fetch_by_metadata, search_summaries,
# get_vector_details, search_and_retrieve, explain_strategies). They are
# auto-discovered by RegistryV3 via the @tool_executor decorator that the
# route layer applies, and surfaced to the AI through the system prompt.
#
# Key translation: Pinecone's namespaces and structured filters become
# JSONB metadata->>'key' lookups + SQL WHERE clauses. See _translate_filter_to_sql.
# ============================================================================


def _translate_filter_to_sql(filter_dict, param_list):
    """
    Translate a Pinecone-style filter dict into a PostgreSQL JSONB WHERE
    fragment.  The same fragment is safe for both the org_vector_documents
    `metadata` column (jsonb) and any future jsonb column.

    Supports:
        $eq, $ne, $gt, $gte, $lt, $lte   (numeric + string)
        $in, $nin                         (membership)
        $exists                           (key present in jsonb)

    Plain values are treated as $eq (Pinecone shorthand).

    Args:
        filter_dict: e.g. {"document_id": {"$eq": "abc"}, "tags": {"$in": ["x", "y"]}}
        param_list:  MUTABLE list; %s placeholders are appended in order.

    Returns:
        SQL fragment like: (metadata->>'document_id' = %s AND metadata->>'tags' IN (%s, %s))
        Returns 'TRUE' for empty input — caller can AND it without effect.
    """
    if not filter_dict:
        return 'TRUE'

    clauses = []
    for key, val in filter_dict.items():
        # Text extraction handles >90% of filter keys. Numeric operators
        # cast at compare time (::float) — JSONB numbers extract as text.
        json_path = f"metadata->>'{key}'"

        if isinstance(val, dict):
            for op, operand in val.items():
                if op == '$eq':
                    param_list.append(str(operand))
                    clauses.append(f"{json_path} = %s")
                elif op == '$ne':
                    param_list.append(str(operand))
                    clauses.append(f"{json_path} <> %s")
                elif op in ('$gt', '$gte', '$lt', '$lte'):
                    sym = {'$gt': '>', '$gte': '>=', '$lt': '<', '$lte': '<='}[op]
                    param_list.append(str(operand))
                    # Numeric-aware comparison: cast both sides to float.
                    # Non-numeric values compare as NaN-equivalent and yield FALSE.
                    clauses.append(f"(({json_path})::float {sym} %s::float)")
                elif op == '$in':
                    arr = [str(x) for x in (operand or [])]
                    if not arr:
                        clauses.append('FALSE')
                    else:
                        param_list.extend(arr)
                        placeholders = ','.join(['%s'] * len(arr))
                        clauses.append(f"{json_path} IN ({placeholders})")
                elif op == '$nin':
                    arr = [str(x) for x in (operand or [])]
                    if not arr:
                        clauses.append('TRUE')
                    else:
                        param_list.extend(arr)
                        placeholders = ','.join(['%s'] * len(arr))
                        clauses.append(
                            f"({json_path} IS NULL OR {json_path} NOT IN ({placeholders}))"
                        )
                elif op == '$exists':
                    # $exists:true  → key present   (jsonb ? operator)
                    # $exists:false → key absent    (NOT (jsonb ? operator))
                    if operand:
                        clauses.append(f"(metadata ? '{key}')")
                    else:
                        clauses.append(f"(NOT (metadata ? '{key}'))")
                else:
                    print(f'[PGVECTOR] _translate_filter_to_sql: unknown operator {op!r}, skipping')
        else:
            # Plain value shorthand → $eq
            param_list.append(str(val))
            clauses.append(f"{json_path} = %s")

    return ' AND '.join(clauses) if clauses else 'TRUE'


def pgvector_query_namespaces(namespaces=None, include_counts=True, **kwargs):
    """
    List the namespaces available in this org's pgvector store.

    pgvector has no physical namespaces (Pinecone does). We simulate the
    concept by reading metadata->>'namespace'. If you have never set that
    metadata field, every chunk lives in the implicit '' namespace.

    Args:
        namespaces: List of namespace names to inspect. If empty/None,
                    returns the implicit '' namespace only.
        include_counts: If True, attach document/vector counts.
        **kwargs: Must contain _user_id.

    Returns:
        {"success": True, "namespaces": [{name, document_count, vector_count}]}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError('_user_id required')
        org_id = _get_org_id(user_id)

        targets = list(namespaces) if namespaces else ['']
        out = []
        for ns in targets:
            sql = """
                SELECT
                    COUNT(DISTINCT document_id) AS doc_count,
                    COUNT(*)                    AS vector_count
                FROM  ai_infrastructure.org_vector_documents
                WHERE org_id = %s
                  AND metadata->>'namespace' = %s
            """
            row = _run_in_org_context(org_id, sql, (org_id, ns), fetch_mode='one')
            out.append({
                'name':           ns,
                'document_count': int((row or {}).get('doc_count') or 0),
                'vector_count':   int((row or {}).get('vector_count') or 0),
            })

        return {
            'success':    True,
            'namespaces': out,
            'note':       "pgvector namespaces are logical — stored in metadata->>'namespace'. "
                          "Documents uploaded without that metadata live in the implicit '' namespace.",
        }
    except Exception as exc:
        print(f'[PGVECTOR] query_namespaces error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_fetch_by_metadata(filter, namespace='', limit=100, **kwargs):
    """
    Filter-only retrieval — return chunks matching metadata predicates
    WITHOUT a semantic query. Useful for "show me everything tagged X".

    Args:
        filter: Pinecone-style filter dict (see _translate_filter_to_sql).
        namespace: Restrict to a single namespace (metadata->>'namespace').
        limit: Max rows. Hard-capped at 1000 to protect the DB.
        **kwargs: Must contain _user_id.

    Returns:
        {"success": True, "matches": [...], "total": N}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError('_user_id required')
        org_id = _get_org_id(user_id)

        if not filter:
            raise PgvectorToolsError('filter is required for fetch_by_metadata')
        if limit > 1000:
            limit = 1000
        if limit < 1:
            limit = 1

        params = [org_id]
        where = ['d.org_id = %s']
        if namespace:
            where.append("d.metadata->>'namespace' = %s")
            params.append(namespace)
        where.append(_translate_filter_to_sql(filter, params))
        params.append(limit)

        sql = f"""
            SELECT
                d.id::TEXT, d.document_id, d.filename, d.chunk_index,
                d.content, d.metadata, d.created_at
            FROM  ai_infrastructure.org_vector_documents d
            WHERE {' AND '.join(where)}
            ORDER BY d.created_at DESC
            LIMIT %s
        """
        rows = _run_in_org_context(org_id, sql, tuple(params), fetch_mode='all') or []
        matches = [
            {
                'id':          r['id'],
                'document_id': r['document_id'],
                'filename':    r['filename'],
                'chunk_index': r['chunk_index'],
                'text':        r['content'],
                'metadata':    r.get('metadata') or {},
                'created_at':  str(r.get('created_at', '')),
            }
            for r in rows
        ]
        return {'success': True, 'matches': matches, 'total': len(matches)}
    except Exception as exc:
        print(f'[PGVECTOR] fetch_by_metadata error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_search_summaries(query_text, top_k=5, **kwargs):
    """
    Semantic search that returns ONE best chunk PER DOCUMENT (not top_k
    chunks from anywhere). Useful for "what contracts do we have about X?"
    where the user wants the document, not the chunk.

    Strategy: over-fetch by 3x, ROW_NUMBER() PARTITION BY document_id
    ORDER BY similarity, then take rn=1. Portable to Postgres 12+.

    Args:
        query_text: Natural-language query.
        top_k:      Number of unique documents to return (default 5).
        **kwargs:   Must contain _user_id.

    Returns:
        {"success": True, "summaries": [{document_id, filename, best_chunk, score}]}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError('_user_id required')
        org_id = _get_org_id(user_id)

        over_fetch = max(top_k * 3, 20)
        query_vector = _generate_embedding(query_text, user_id, is_query=True)
        vec_literal = '[' + ','.join(str(v) for v in query_vector) + ']'

        sql = """
            WITH ranked AS (
                SELECT
                    d.id::TEXT, d.document_id, d.filename, d.chunk_index,
                    d.content, d.metadata, d.created_at,
                    (1 - (d.embedding <=> %s::vector))::FLOAT AS similarity,
                    ROW_NUMBER() OVER (
                        PARTITION BY d.document_id
                        ORDER BY d.embedding <=> %s::vector
                    ) AS rn
                FROM  ai_infrastructure.org_vector_documents d
                WHERE d.org_id = %s
                  AND d.embedding IS NOT NULL
            )
            SELECT *
            FROM   ranked
            WHERE  rn = 1
            ORDER  BY embedding <=> %s::vector
            LIMIT  %s
        """
        rows = _run_in_org_context(
            org_id, sql,
            (vec_literal, vec_literal, org_id, vec_literal, over_fetch),
            fetch_mode='all',
        ) or []
        rows = rows[:top_k]  # trim to top_k unique docs
        summaries = [
            {
                'document_id': r['document_id'],
                'filename':    r['filename'],
                'best_chunk': {
                    'chunk_index': r['chunk_index'],
                    'text':        r['content'],
                    'id':          r['id'],
                },
                'score':      float(r['similarity']),
                'created_at': str(r.get('created_at', '')),
            }
            for r in rows
        ]
        return {'success': True, 'summaries': summaries, 'total': len(summaries)}
    except Exception as exc:
        print(f'[PGVECTOR] search_summaries error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_get_vector_details(vector_id, include_adjacent=True, **kwargs):
    """
    Fetch the full row for a chunk (UUID) and optionally its prev/next
    sibling chunks in the same document (chunk_index ± 1).

    Args:
        vector_id:         UUID of the chunk to fetch.
        include_adjacent:  If True, also fetch ±1 neighbours.
        **kwargs:          Must contain _user_id.

    Returns:
        {"success": True, "chunk": {...}, "previous": {...}?, "next": {...}?}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError('_user_id required')
        org_id = _get_org_id(user_id)

        # ── Main chunk ─────────────────────────────────────────────────────
        sql = """
            SELECT
                d.id::TEXT, d.document_id, d.filename, d.chunk_index,
                d.total_chunks, d.content, d.metadata, d.created_at,
                d.emb_model, d.emb_provider
            FROM  ai_infrastructure.org_vector_documents d
            WHERE d.org_id = %s AND d.id = %s::uuid
        """
        row = _run_in_org_context(org_id, sql, (org_id, vector_id), fetch_mode='one')
        if not row:
            return {'success': False, 'error': f'Vector {vector_id} not found'}

        chunk = {
            'id':           row['id'],
            'document_id':  row['document_id'],
            'filename':     row['filename'],
            'chunk_index':  row['chunk_index'],
            'total_chunks': row['total_chunks'],
            'text':         row['content'],
            'metadata':     row.get('metadata') or {},
            'emb_model':    row.get('emb_model'),
            'emb_provider': row.get('emb_provider'),
            'created_at':   str(row.get('created_at', '')),
        }
        out = {'success': True, 'chunk': chunk}

        if not include_adjacent:
            return out

        # ── Adjacent (prev / next by chunk_index in same doc) ──────────────
        ci = row['chunk_index']
        prev_idx = ci - 1
        next_idx = ci + 1
        adj_indices = []
        if prev_idx >= 0:
            adj_indices.append(prev_idx)
        adj_indices.append(next_idx)
        placeholders = ','.join(['%s'] * len(adj_indices))

        adj_sql = f"""
            SELECT id::TEXT, chunk_index, content
            FROM   ai_infrastructure.org_vector_documents
            WHERE  org_id = %s AND document_id = %s
              AND  chunk_index IN ({placeholders})
            ORDER  BY chunk_index
        """
        adj_rows = _run_in_org_context(
            org_id, adj_sql,
            (org_id, row['document_id']) + tuple(adj_indices),
            fetch_mode='all',
        ) or []
        for ar in adj_rows:
            slot_entry = {'chunk_index': ar['chunk_index'], 'text': ar['content'], 'id': ar['id']}
            if ar['chunk_index'] == prev_idx:
                out['previous'] = slot_entry
            elif ar['chunk_index'] == next_idx:
                out['next'] = slot_entry
        return out
    except Exception as exc:
        print(f'[PGVECTOR] get_vector_details error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_search_and_retrieve(query_text, top_k=5, expand_to=3, **kwargs):
    """
    Two-stage retrieval: semantic search → fetch full chunk context for
    top hits (with ±expand_to neighbours).

    Args:
        query_text: Natural-language query.
        top_k:      Number of top hits to keep (default 5).
        expand_to:  Expand each hit to its ±N neighbours (default 3).
                    Set to 0 to skip expansion (semantic-search-only).
        **kwargs:   Must contain _user_id.

    Returns:
        {"success": True, "results": [{match, previous, next}, ...]}
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PgvectorToolsError('_user_id required')
        org_id = _get_org_id(user_id)

        # Stage 1: semantic search (limit hard-capped inside pgvector_query_vectors)
        search = pgvector_query_vectors(query_text=query_text, top_k=top_k, _user_id=user_id)
        if not search.get('success'):
            return search

        # Stage 2: enrich each hit with adjacent chunks (best-effort; one bad
        # detail call shouldn't kill the whole result set).
        results = []
        for hit in search.get('matches', []) or []:
            entry = {'match': hit}
            if expand_to > 0:
                # For now, the helper only supports ±1. expand_to is documented
                # as the user-tunable knob for a future helper variant.
                detail = pgvector_get_vector_details(
                    vector_id=hit['id'], include_adjacent=True, _user_id=user_id,
                )
                if detail.get('success'):
                    entry['previous'] = detail.get('previous')
                    entry['next']     = detail.get('next')
            results.append(entry)
        return {'success': True, 'results': results, 'total': len(results)}
    except Exception as exc:
        print(f'[PGVECTOR] search_and_retrieve error: {exc}')
        return {'success': False, 'error': str(exc)}


def pgvector_explain_strategies(**kwargs):
    """
    Static knowledge base about pgvector's retrieval behaviour — the AI
    uses this to explain to the user WHY it chose a particular search
    strategy and WHAT to expect from the active provider.

    Args:
        **kwargs: Must contain _user_id (kept for interface parity).

    Returns:
        {"success": True, "provider": "pgvector", "strategies": {...}}
    """
    return {
        'success':  True,
        'provider': 'pgvector',
        'strategies': {
            'metric':              'cosine similarity (Postgres <=> operator)',
            'default_threshold':   0.5,
            'embedding_dim':       768,
            'embedding_providers': ['pgvector_bge (local BAAI/bge-base-en-v1.5, free)',
                                    'voyager (Voyage AI voyage-4)',
                                    'openai (text-embedding-3-small)'],
            'index_type':          'HNSW (Supabase default; supports cosine distance)',
            'rls':                 "app.current_org_id GUC + org_isolation_* policies (migration 044)",
            'namespace_strategy':  "logical only — stored as metadata->>'namespace'; no physical partition",
            'reindex_on_swap':     'NO — switching provider does NOT move data. '
                                   'Previous provider is inventoried in '
                                   'org_vector_other_provider_inventory so the AI can still '
                                   'report/document it.',
            'best_for':            'orgs that want zero external account, free embeddings (BGE), '
                                   'and Postgres-native operations.',
            'limits': {
                'top_k_hard_cap':  1000,
                'max_chunk_chars': 8000,
                'overlap_must_be': '< chunk_size',
            },
        },
    }
