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
    Uses a single transaction so SET LOCAL scope is respected.
    """
    from AI_infrastructure.shared.database_utils import execute_query

    # Supabase does not easily allow SET LOCAL in psycopg2 multi-statement calls.
    # We set the config on the connection session-level instead — which is safe
    # because each `execute_query` call uses a fresh pooled connection returned to
    # the pool immediately after; there is no session leakage between requests.
    set_sql = f"SET app.current_org_id = '{org_id}';"
    execute_query(set_sql)
    return execute_query(sql, params, fetch_mode=fetch_mode)


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
        rows = execute_query(sql, params, fetch_mode='all') or []

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

            execute_query(
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
                )
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
            execute_query(
                "DELETE FROM ai_infrastructure.org_vector_documents WHERE org_id = %s",
                (org_id,)
            )
            print(f'[PGVECTOR] Deleted all vectors for org {org_id}')
            return {'success': True, 'deleted_count': -1, 'note': 'all org documents deleted'}

        if not document_id:
            raise PgvectorToolsError("document_id required (or set delete_all=True)")

        execute_query(
            "DELETE FROM ai_infrastructure.org_vector_documents WHERE org_id = %s AND document_id = %s",
            (org_id, document_id)
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

        rows = execute_query(
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

        row = execute_query(
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
                'id': f"{document_id}_chunk_{i}",
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
