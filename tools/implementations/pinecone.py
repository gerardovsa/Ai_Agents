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
    'PineconeToolsError'
]
