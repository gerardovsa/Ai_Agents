"""
Pinecone Vector Database Tools - Main Module

This module exports all Pinecone tools for the AI_agents tool registry.
Actual implementations are in the pinecone/ subfolder for better organization.

Tools exported (8 total):
1. pinecone_query_vectors - Semantic search
2. pinecone_upsert_vectors - Batch insert/update vectors
3. pinecone_delete_vectors - Delete vectors by ID, filter, or delete_all
4. pinecone_fetch_vectors - Retrieve specific vectors by ID
5. pinecone_update_vector - Modify vector values or metadata
6. pinecone_describe_index_stats - Get database statistics
7. pinecone_list_namespaces - List all namespaces
8. vector_db_upload_document - Full document processing pipeline
"""

# Import all tools from pinecone subfolder
from tools.implementations.pinecone.pinecone_tools import (
    pinecone_query_vectors,
    pinecone_upsert_vectors,
    pinecone_delete_vectors,
    pinecone_fetch_vectors,
    pinecone_update_vector,
    pinecone_describe_index_stats,
    pinecone_list_namespaces,
    vector_db_upload_document,
    PineconeToolsError
)

# Export all tools for registry discovery  
__all__ = [
    'pinecone_query_vectors',
    'pinecone_upsert_vectors',
    'pinecone_delete_vectors',
    'pinecone_fetch_vectors',
    'pinecone_update_vector',
    'pinecone_describe_index_stats',
    'pinecone_list_namespaces',
    'vector_db_upload_document',
    'PineconeToolsError',
    # Deprecated aliases
    'pinecone_explain_strategies',
    'pinecone_query_namespaces',  # Alias for pinecone_list_namespaces
    'pinecone_fetch_by_metadata',
    'pinecone_search_summaries',
    'pinecone_get_vector_details',
    'pinecone_search_and_retrieve'
]


# ============================================================
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
