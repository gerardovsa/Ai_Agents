"""
Document Library Tools - AI Agent Access to Advanced Search
=============================================================
Implements AI agent tools for accessing the document library with:
- Full-text search (PostgreSQL)
- Semantic search (pgvector)
- Hybrid search (RRF)
- Advanced filtering (Elasticsearch-style)
- Faceted aggregation
- Document CRUD operations

Dependencies:
- requests (for API calls)
- openai (for embeddings in semantic search)
"""

import requests
from typing import Dict, List, Any, Optional
import json
import os

# Configuration
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5001')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')


class DocumentLibraryError(Exception):
    """Custom exception for document library errors"""
    pass


def _get_auth_headers(**kwargs) -> Dict[str, str]:
    """
    Get authentication headers from injected credentials
    
    Args:
        **kwargs: May contain auth_token from credential injection
    
    Returns:
        Dict with Authorization header
    """
    auth_token = kwargs.get('auth_token')
    if not auth_token:
        raise DocumentLibraryError("Authentication token required")
    
    return {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json'
    }


def _generate_embedding(text: str) -> List[float]:
    """
    Generate OpenAI embeddings for semantic search
    
    Args:
        text: Text to embed
    
    Returns:
        List of 1536 floats (OpenAI embedding)
    """
    try:
        import openai
        openai.api_key = OPENAI_API_KEY
        
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        
        return response.data[0].embedding
    
    except Exception as e:
        raise DocumentLibraryError(f"Failed to generate embedding: {str(e)}")


# ============================================================================
# SEARCH TOOLS
# ============================================================================

def document_library_search_fulltext(
    query: str,
    limit: int = 20,
    offset: int = 0,
    filters: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Full-text search using PostgreSQL to_tsvector and ts_rank
    
    Args:
        query: Search query using PostgreSQL websearch syntax
        limit: Maximum results (default: 20)
        offset: Pagination offset (default: 0)
        filters: Optional filters (source, file_type, user_id)
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success, search_type, query, results (with rank and snippet), count
    
    Raises:
        DocumentLibraryError: If search fails
    
    Examples:
        >>> document_library_search_fulltext("contract agreement", limit=10)
        >>> document_library_search_fulltext("invoice AND pending", filters={"source": "google_drive"})
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        payload = {
            'query': query,
            'limit': limit,
            'offset': offset,
            'filters': filters or {}
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/document-library/search/fulltext',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Full-text search failed: {str(e)}")


def document_library_search_semantic(
    query: str,
    threshold: float = 0.25,
    limit: int = 20,
    filters: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Semantic search using vector similarity (pgvector)
    
    Args:
        query: Natural language search query (will be converted to embeddings)
        threshold: Similarity threshold 0-1 (default: 0.25, lower = more results)
        limit: Maximum results (default: 20)
        filters: Optional filters (source, file_type)
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success, search_type, results (with similarity scores), count
    
    Raises:
        DocumentLibraryError: If search fails or embedding generation fails
    
    Examples:
        >>> document_library_search_semantic("machine learning best practices", threshold=0.3)
        >>> document_library_search_semantic("project management documents", limit=15)
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        # Generate embedding for query
        embedding = _generate_embedding(query)
        
        payload = {
            'query': query,
            'embedding': embedding,
            'threshold': threshold,
            'limit': limit,
            'filters': filters or {}
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/document-library/search/semantic',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Semantic search failed: {str(e)}")


def document_library_search_hybrid(
    query: str,
    limit: int = 20,
    fts_weight: float = 0.5,
    semantic_weight: float = 0.5,
    **kwargs
) -> Dict[str, Any]:
    """
    Hybrid search combining full-text + semantic using Reciprocal Rank Fusion
    
    Args:
        query: Search query for both full-text and semantic search
        limit: Maximum results (default: 20)
        fts_weight: Weight for full-text 0-1 (default: 0.5, higher = prioritize keywords)
        semantic_weight: Weight for semantic 0-1 (default: 0.5, higher = prioritize concepts)
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success, search_type, query, results (with combined_score, fts_rank, semantic_similarity), count
    
    Raises:
        DocumentLibraryError: If search fails
    
    Examples:
        >>> document_library_search_hybrid("quarterly sales performance", fts_weight=0.6, semantic_weight=0.4)
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        # Generate embedding for query
        embedding = _generate_embedding(query)
        
        payload = {
            'query': query,
            'embedding': embedding,
            'limit': limit,
            'fts_weight': fts_weight,
            'semantic_weight': semantic_weight
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/document-library/search/hybrid',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Hybrid search failed: {str(e)}")


# ============================================================================
# FILTERING TOOLS
# ============================================================================

def document_library_filter_advanced(
    must: Optional[List[Dict[str, Any]]] = None,
    should: Optional[List[Dict[str, Any]]] = None,
    must_not: Optional[List[Dict[str, Any]]] = None,
    range_filters: Optional[Dict[str, Dict[str, Any]]] = None,
    limit: int = 20,
    offset: int = 0,
    sort: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Advanced filtering with Elasticsearch-style boolean queries
    
    Args:
        must: List of conditions that MUST match (AND logic)
        should: List of conditions where at least one SHOULD match (OR logic)
        must_not: List of conditions that MUST NOT match (NOT logic)
        range_filters: Dict of field -> {gte, lte, gt, lt} for range queries
        limit: Maximum results (default: 20)
        offset: Pagination offset (default: 0)
        sort: List of {field, order} dicts for sorting
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success, results, count, total, has_more
    
    Raises:
        DocumentLibraryError: If filtering fails
    
    Examples:
        >>> document_library_filter_advanced(
        ...     must=[
        ...         {"field": "source", "operator": "equals", "value": "google_drive"},
        ...         {"field": "file_type", "operator": "equals", "value": "document"}
        ...     ],
        ...     range_filters={
        ...         "created_at": {"gte": "2024-01-01", "lte": "2024-12-31"}
        ...     },
        ...     sort=[{"field": "created_at", "order": "desc"}]
        ... )
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        payload = {
            'must': must or [],
            'should': should or [],
            'must_not': must_not or [],
            'range': range_filters or {},
            'limit': limit,
            'offset': offset,
            'sort': sort or [{'field': 'created_at', 'order': 'desc'}]
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/document-library/filter',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Advanced filtering failed: {str(e)}")


def document_library_get_facets(
    filters: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get faceted aggregation counts for filtering UI
    
    Args:
        filters: Optional filters to apply before aggregation (source, created_after, created_before)
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success and facets (sources, file_types, top_tags, date_distribution)
    
    Raises:
        DocumentLibraryError: If facet aggregation fails
    
    Examples:
        >>> document_library_get_facets()
        >>> document_library_get_facets(filters={"created_after": "2024-01-01"})
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        payload = {
            'filters': filters or {}
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/document-library/facets',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Failed to get facets: {str(e)}")


# ============================================================================
# DOCUMENT CRUD TOOLS
# ============================================================================

def document_library_list(
    limit: int = 20,
    offset: int = 0,
    source: Optional[str] = None,
    file_type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    List documents with basic pagination and filtering
    
    Args:
        limit: Number of documents to return (default: 20)
        offset: Pagination offset (default: 0)
        source: Filter by source (google_drive, onedrive, dropbox, sharepoint, internal)
        file_type: Filter by type (document, spreadsheet, presentation, pdf, image, video, audio, other)
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success, documents array, count
    
    Raises:
        DocumentLibraryError: If listing fails
    
    Examples:
        >>> document_library_list(limit=10)
        >>> document_library_list(source="google_drive", file_type="document")
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if source:
            params['source'] = source
        
        if file_type:
            params['file_type'] = file_type
        
        response = requests.get(
            f'{API_BASE_URL}/api/document-library/documents',
            headers=headers,
            params=params,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Failed to list documents: {str(e)}")


def document_library_get(
    document_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get detailed information about a specific document
    
    Args:
        document_id: Unique document ID
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success and complete document object
    
    Raises:
        DocumentLibraryError: If document not found or retrieval fails
    
    Examples:
        >>> document_library_get("doc_abc123")
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        response = requests.get(
            f'{API_BASE_URL}/api/document-library/documents/{document_id}',
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        if e.response and e.response.status_code == 404:
            raise DocumentLibraryError(f"Document not found: {document_id}")
        raise DocumentLibraryError(f"Failed to get document: {str(e)}")


def document_library_add(
    document_id: str,
    source: str,
    title: str,
    source_id: Optional[str] = None,
    content_preview: Optional[str] = None,
    file_type: str = 'other',
    mime_type: Optional[str] = None,
    file_extension: Optional[str] = None,
    file_size_bytes: int = 0,
    tags: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    description: Optional[str] = None,
    url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Add a new document to the library
    
    Args:
        document_id: Unique document ID
        source: Document source (google_drive, onedrive, dropbox, sharepoint, internal)
        title: Document title
        source_id: Original ID in source system
        content_preview: First 500 chars for search
        file_type: File type (document, spreadsheet, presentation, pdf, image, video, audio, other)
        mime_type: MIME type
        file_extension: File extension
        file_size_bytes: File size in bytes
        tags: Document tags
        categories: Document categories
        description: Document description
        url: URL to access document
        metadata: Additional metadata as dict
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success and created document info
    
    Raises:
        DocumentLibraryError: If document creation fails
    
    Examples:
        >>> document_library_add(
        ...     document_id="gdrive_abc123",
        ...     source="google_drive",
        ...     title="Q4 Sales Report",
        ...     file_type="document",
        ...     tags=["sales", "q4", "2024"]
        ... )
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        payload = {
            'document_id': document_id,
            'source': source,
            'source_id': source_id,
            'title': title,
            'content_preview': content_preview,
            'file_type': file_type,
            'mime_type': mime_type,
            'file_extension': file_extension,
            'file_size_bytes': file_size_bytes,
            'tags': tags or [],
            'categories': categories or [],
            'description': description,
            'url': url,
            'metadata': metadata or {}
        }
        
        response = requests.post(
            f'{API_BASE_URL}/api/document-library/documents',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Failed to add document: {str(e)}")


def document_library_get_stats(**kwargs) -> Dict[str, Any]:
    """
    Get library statistics
    
    Args:
        **kwargs: Credential injection (auth_token)
    
    Returns:
        Dict with success and stats (total_documents, total_sources, total_size_bytes, total_views, unique_creators)
    
    Raises:
        DocumentLibraryError: If stats retrieval fails
    
    Examples:
        >>> document_library_get_stats()
    """
    try:
        headers = _get_auth_headers(**kwargs)
        
        response = requests.get(
            f'{API_BASE_URL}/api/document-library/stats',
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Failed to get stats: {str(e)}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_file_size(bytes_size: int) -> str:
    """Format bytes into human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def format_search_results_for_display(results: List[Dict[str, Any]]) -> str:
    """
    Format search results into readable text for AI agent responses
    
    Args:
        results: List of document results
    
    Returns:
        Formatted string for display
    """
    if not results:
        return "No documents found."
    
    output = []
    for i, doc in enumerate(results, 1):
        title = doc.get('title', 'Untitled')
        source = doc.get('source', 'unknown')
        file_type = doc.get('file_type', 'other')
        
        # Include score if available
        score_info = ""
        if 'rank' in doc:
            score_info = f" (relevance: {doc['rank']:.3f})"
        elif 'similarity' in doc:
            score_info = f" (similarity: {doc['similarity']:.3f})"
        elif 'combined_score' in doc:
            score_info = f" (score: {doc['combined_score']:.3f})"
        
        output.append(f"{i}. {title} [{source}/{file_type}]{score_info}")
        
        # Include snippet if available
        if 'snippet' in doc and doc['snippet']:
            output.append(f"   Preview: {doc['snippet'][:150]}...")
    
    return "\n".join(output)
