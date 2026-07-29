"""
Pinecone Vector Database Tools - Main Module

This module exports all Pinecone tools for the AI_agents tool registry.
Actual implementations live in the pinecone/ subfolder for better organization.

Core tools (8):
1. pinecone_query_vectors - Semantic search
2. pinecone_upsert_vectors - Batch insert/update vectors
3. pinecone_delete_vectors - Delete vectors by ID, filter, or delete_all
4. pinecone_fetch_vectors - Retrieve specific vectors by ID
5. pinecone_update_vector - Modify vector values or metadata
6. pinecone_describe_index_stats - Get database statistics
7. pinecone_list_namespaces - List all namespaces
8. vector_db_upload_document - Full document processing pipeline

Smart / higher-level tools (6):
 9. pinecone_query_namespaces        - Cross-namespace parallel search with hybrid dense+sparse
10. pinecone_fetch_by_metadata      - Filter-only retrieval without semantic scoring
11. pinecone_search_summaries       - Two-stage search that groups matches by document
12. pinecone_get_vector_details     - Retrieve full chunk text + adjacency hints by vector ID
13. pinecone_search_and_retrieve    - Two-stage search → chunk retrieval in one call
14. pinecone_explain_strategies     - Education/reference tool for vector DB concepts
"""

# Import all tools from the pinecone subfolder
from tools.implementations.pinecone.pinecone_tools import (
    # Core (8)
    pinecone_query_vectors,
    pinecone_upsert_vectors,
    pinecone_delete_vectors,
    pinecone_fetch_vectors,
    pinecone_update_vector,
    pinecone_describe_index_stats,
    pinecone_list_namespaces,
    vector_db_upload_document,
    PineconeToolsError,
    # Smart / higher-level (5)
    pinecone_query_namespaces,
    pinecone_fetch_by_metadata,
    pinecone_search_summaries,
    pinecone_get_vector_details,
    pinecone_search_and_retrieve,
)

# Education tool lives in a separate module to keep pinecone_tools.py focused on data ops
from tools.implementations.pinecone.pinecone_strategies import (
    pinecone_explain_strategies,
)

# Export all tools for registry discovery
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
    'PineconeToolsError',
    # Smart / higher-level (6)
    'pinecone_explain_strategies',
    'pinecone_query_namespaces',
    'pinecone_fetch_by_metadata',
    'pinecone_search_summaries',
    'pinecone_get_vector_details',
    'pinecone_search_and_retrieve',
]


print('[PINECONE] Loaded 14 tools (8 core + 6 smart/education)')
