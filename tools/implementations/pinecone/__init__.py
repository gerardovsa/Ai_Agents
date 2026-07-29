"""
Pinecone Tools Package

Exports all Pinecone vector database tool functions for registry loading.
Includes the 8 core tools + 6 smart/education aliases (formerly shadowed
by stub functions in this file - now re-exported from their real homes
in pinecone_tools.py and pinecone_strategies.py).
"""

from .pinecone_tools import (
    # Core (8)
    pinecone_query_vectors,
    pinecone_upsert_vectors,
    pinecone_delete_vectors,
    pinecone_fetch_vectors,
    pinecone_update_vector,
    pinecone_describe_index_stats,
    pinecone_list_namespaces,
    vector_db_upload_document,
    # Smart / higher-level (5)
    pinecone_query_namespaces,
    pinecone_fetch_by_metadata,
    pinecone_search_summaries,
    pinecone_get_vector_details,
    pinecone_search_and_retrieve,
)

# Education tool lives in a separate module
from .pinecone_strategies import (
    pinecone_explain_strategies,
)

__all__ = [
    # Core (8)
    'pinecone_query_vectors',
    'pinecone_upsert_vectors',
    'pinecone_delete_vectors',
    'pinecone_fetch_vectors',
    'pinecone_update_vector',
    'pinecone_describe_index_stats',
    'pinecone_list_namespaces',
    'vector_db_upload_document',
    # Smart / higher-level (6)
    'pinecone_explain_strategies',
    'pinecone_query_namespaces',
    'pinecone_fetch_by_metadata',
    'pinecone_search_summaries',
    'pinecone_get_vector_details',
    'pinecone_search_and_retrieve',
]

print('[PINECONE PACKAGE] Initialized with 14 tools (8 core + 6 smart/education)')
