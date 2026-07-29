"""
Vector DB Provider Router (Option A: Active + Secondary)

FILE:    AI_infrastructure/shared/vector_db_router.py
PURPOSE: Reads ai_infrastructure.org_vector_provider_config to determine the
         active vector DB provider per org, and reads
         ai_infrastructure.org_vector_other_provider_inventory for read-only
         secondaries. Used by:

         - system_prompt_builder.py     → inject status into the prompt
         - universal_search_routes.py   → fan out to active + secondaries
         - future tools / routes        → disambiguate pgvector_* vs pinecone_*
                                          at dispatch time

CREATED: 2026-07-28 (migration 052)

DESIGN:  Per CLAUDE.md §6 rule 4 ("smallest safe change"), this module is
         intentionally a thin read-only layer. It does NOT mutate the
         config tables — that lives in the upload pipeline / Settings UI.

MULTI-TENANCY:
         Every read is hard-scoped to org_id. There is no "global default"
         — pgvector is the default only at the org-row level (set during
         the migration 052 backfill).

LAST MODIFIED: 2026-07-28
"""

from typing import Dict, Any, List, Optional


# Lazy import — keeps module import cheap (matches the pattern used by
# other shared helpers like org_credentials_loader to avoid circular imports
# during flask_app startup).
def _query(sql: str, params=(), fetch_mode: str = 'one'):
    from AI_infrastructure.shared.database_utils import execute_query
    return execute_query(sql, params, fetch_mode=fetch_mode)


def detect_active_provider(org_id: int) -> str:
    """
    Return the active vector DB provider key for an org.

    Falls back to 'pgvector' if the org has no config row yet (shouldn't
    happen after migration 052 backfill, but defensive so newly created
    orgs in the same transaction window don't crash callers).

    Args:
        org_id: The organisation's integer ID.

    Returns:
        One of: 'pgvector', 'pinecone', 'qdrant'.
    """
    row = _query(
        """
        SELECT active_provider
        FROM   ai_infrastructure.org_vector_provider_config
        WHERE  org_id = %s
        """,
        (org_id,),
        fetch_mode='one',
    )
    return (row or {}).get('active_provider') or 'pgvector'


def detect_embedding_provider(org_id: int) -> str:
    """
    Return the configured embedding provider key for an org.

    Same fallback contract as detect_active_provider — defaults to
    'pgvector_bge' (local BGE model, free).
    """
    row = _query(
        """
        SELECT embedding_provider
        FROM   ai_infrastructure.org_vector_provider_config
        WHERE  org_id = %s
        """,
        (org_id,),
        fetch_mode='one',
    )
    return (row or {}).get('embedding_provider') or 'pgvector_bge'


def get_vector_status(org_id: int) -> Dict[str, Any]:
    """
    Read the v_org_vector_status view (single round-trip; the view
    JSON-aggregates the inventory table for cheap reads).

    Args:
        org_id: The organisation's integer ID.

    Returns:
        {
            'active_provider':    'pgvector',
            'embedding_provider': 'pgvector_bge',
            'other_providers':    [  # jsonb[] — list of dicts
                {'provider': 'pinecone',
                 'document_count': 142,
                 'vector_count':   1240,
                 'last_synced_at': '2026-07-15T...'},
                ...
            ],
            'config_updated_at':  '2026-07-28T...'
        }
    """
    row = _query(
        """
        SELECT active_provider, embedding_provider, other_providers, config_updated_at
        FROM   ai_infrastructure.v_org_vector_status
        WHERE  org_id = %s
        """,
        (org_id,),
        fetch_mode='one',
    )
    if not row:
        return {
            'active_provider':    'pgvector',
            'embedding_provider': 'pgvector_bge',
            'other_providers':    [],
            'config_updated_at':  None,
        }
    return {
        'active_provider':    row['active_provider'],
        'embedding_provider': row['embedding_provider'],
        'other_providers':    row.get('other_providers') or [],
        'config_updated_at':  str(row.get('config_updated_at', '')),
    }


def list_provider_module_name(provider: str) -> str:
    """
    Map a provider key to its tool-name prefix. The registry registers
    tools as '<prefix>_query_vectors', '<prefix>_upsert_vectors', etc.

    Args:
        provider: 'pgvector' | 'pinecone' | 'qdrant'

    Returns:
        Tool-name prefix used in registry.execute_tool(...) calls.
    """
    return {
        'pgvector':  'pgvector',
        'pinecone':  'pinecone',
        'qdrant':    'qdrant',
    }.get(provider, 'pgvector')


def get_vector_db_guidance_text(org_id: int) -> str:
    """
    Produce a compact status string suitable for injection into the
    system prompt. Kept to one short paragraph to minimise prompt bloat.

    Example output (org 1, pgvector active, pinecone secondary):
        Vector DB: pgvector (pgvector_bge embeddings).
        142 docs in pinecone (secondary, read-only).

    Returns an empty string if org_id is None — callers can safely AND it
    onto any prompt without producing a "Vector DB: None" artefact.
    """
    if org_id is None:
        return ''

    try:
        status = get_vector_status(org_id)
    except Exception as exc:
        # Never crash the prompt build because of a vector status read.
        print(f'[VECTOR_ROUTER] get_vector_db_guidance_text: {exc}')
        return ''

    active   = status['active_provider']
    embed    = status['embedding_provider']
    others   = status.get('other_providers') or []

    line = f'Vector DB: {active} ({embed} embeddings).'
    nonzero = [o for o in others if (o.get('document_count') or 0) > 0]
    if nonzero:
        summary = '; '.join(
            f"{o['document_count']} docs in {o['provider']} (secondary, read-only)"
            for o in nonzero
        )
        line += f' {summary}.'
    return line


__all__ = [
    'detect_active_provider',
    'detect_embedding_provider',
    'get_vector_status',
    'list_provider_module_name',
    'get_vector_db_guidance_text',
]