"""
Pinecone Tools Package

Exports all Pinecone vector database tool functions for registry loading.
"""

from .pinecone_tools import (
    pinecone_query_vectors,
    pinecone_upsert_vectors,
    pinecone_delete_vectors,
    pinecone_fetch_vectors,
    pinecone_update_vector,
    pinecone_describe_index_stats,
    pinecone_list_namespaces,
    vector_db_upload_document
)

__all__ = [
    'pinecone_query_vectors',
    'pinecone_upsert_vectors',
    'pinecone_delete_vectors',
    'pinecone_fetch_vectors',
    'pinecone_update_vector',
    'pinecone_describe_index_stats',
    'pinecone_list_namespaces',
    'vector_db_upload_document',
    # Deprecated aliases
    'pinecone_explain_strategies',
    'pinecone_query_namespaces',
    'pinecone_fetch_by_metadata',
    'pinecone_search_summaries',
    'pinecone_get_vector_details',
    'pinecone_search_and_retrieve'
]

#  ============================================================
# DEPRECATED TOOL ALIASES (for backwards compatibility)
# ============================================================

def pinecone_explain_strategies(**kwargs):
    """DEPRECATED: Documentation moved to Pinecone UI/docs"""
    return {"success": False, "error": "DEPRECATED: See Pinecone documentation for search strategies"}

def pinecone_query_namespaces(**kwargs):
    """DEPRECATED: Use pinecone_list_namespaces instead"""
    return pinecone_list_namespaces(**kwargs)

def pinecone_fetch_by_metadata(**kwargs):
    """DEPRECATED: Use pinecone_query_vectors with filter parameter instead"""
    return {"success": False, "error": "DEPRECATED: Use pinecone_query_vectors with filter={'your_field': 'value'}"}

def pinecone_search_summaries(**kwargs):
    """DEPRECATED: Use pinecone_query_vectors instead"""
    return pinecone_query_vectors(**kwargs)

def pinecone_get_vector_details(**kwargs):
    """DEPRECATED: Use pinecone_fetch_vectors instead"""
    return pinecone_fetch_vectors(**kwargs)

def pinecone_search_and_retrieve(**kwargs):
    """DEPRECATED: Use pinecone_query_vectors instead"""
    return pinecone_query_vectors(**kwargs)

print('[PINECONE PACKAGE] Initialized with 14 tools (8 active + 6 deprecated aliases)')
