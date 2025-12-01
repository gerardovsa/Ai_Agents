"""
Document Library Tools - Multi-Provider Implementation

FILE: tools/implementations/document_library_multi_provider.py
PURPOSE: Enhanced document library with support for multiple embedding providers and vector databases

EMBEDDING PROVIDERS SUPPORTED:
- OpenAI (text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large)
- Voyage AI (voyage-2, voyage-large-2)
- Cohere (embed-english-v3.0, embed-multilingual-v3.0)

VECTOR DATABASES SUPPORTED:
- pgvector (PostgreSQL extension) - Direct SQL storage
- Pinecone - External vector index with namespaces

FEATURES:
- Automatic provider detection from user credentials
- Fallback to OpenAI if no provider configured
- Hybrid search combining full-text + semantic
- Cross-provider compatibility (embeddings from one, search in another)

CREDENTIAL INJECTION:
- Requires _user_id and _injected_credentials=True
- Fetches credentials from ai_infrastructure.oauth_tokens (JSONB format)
- Platforms: 'openai', 'voyage', 'cohere', 'pinecone'

FUNCTIONS:
1. document_library_search_fulltext - PostgreSQL full-text search
2. document_library_search_semantic - Multi-provider semantic search
3. document_library_search_hybrid - Combined full-text + semantic
4. document_library_filter_advanced - Elasticsearch-style filtering
5. document_library_get_facets - Aggregation for filter UI
6. document_library_list - List documents with pagination
7. document_library_get - Get single document details
8. document_library_add - Add document to library
9. document_library_get_stats - Get library statistics
10. document_library_get_provider_stats - Get embedding provider usage

LAST MODIFIED: 2025-11-30
"""

import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Custom exception
class DocumentLibraryError(Exception):
    """Raised when document library operations fail"""
    pass

# ============================================================================
# EMBEDDING GENERATION (MULTI-PROVIDER)
# ============================================================================

def _generate_embedding(text: str, provider: str = 'openai', model: str = None, **kwargs) -> List[float]:
    """
    Generate text embedding using configured provider
    
    Args:
        text: Text to embed
        provider: 'openai', 'voyage', or 'cohere'
        model: Specific model name (optional)
        **kwargs: Credential injection
    
    Returns:
        List[float]: Embedding vector
    
    Raises:
        DocumentLibraryError: If embedding generation fails
    """
    user_id = kwargs.get('_user_id')
    
    try:
        # OpenAI embeddings
        if provider == 'openai':
            import openai
            
            # Get OpenAI credentials
            access_token = kwargs.get('access_token')  # Injected by credential_injector
            if not access_token:
                raise DocumentLibraryError("OpenAI access_token not found in credentials")
            
            client = openai.OpenAI(api_key=access_token)
            model = model or 'text-embedding-ada-002'
            
            response = client.embeddings.create(
                input=text,
                model=model
            )
            return response.data[0].embedding
        
        # Voyage AI embeddings
        elif provider == 'voyage':
            import voyageai
            
            # Get Voyage credentials from kwargs
            voyage_token = kwargs.get('voyage_api_key')
            if not voyage_token:
                raise DocumentLibraryError("Voyage API key not found in credentials")
            
            vo = voyageai.Client(api_key=voyage_token)
            model = model or 'voyage-2'
            
            result = vo.embed([text], model=model)
            return result.embeddings[0]
        
        # Cohere embeddings
        elif provider == 'cohere':
            import cohere
            
            # Get Cohere credentials from kwargs
            cohere_token = kwargs.get('cohere_api_key')
            if not cohere_token:
                raise DocumentLibraryError("Cohere API key not found in credentials")
            
            co = cohere.Client(cohere_token)
            model = model or 'embed-english-v3.0'
            
            response = co.embed(
                texts=[text],
                model=model,
                input_type='search_query'
            )
            return response.embeddings[0]
        
        else:
            raise DocumentLibraryError(f"Unsupported embedding provider: {provider}")
    
    except Exception as e:
        raise DocumentLibraryError(f"Failed to generate {provider} embedding: {str(e)}")

def _detect_embedding_provider(**kwargs) -> Dict[str, str]:
    """
    Detect which embedding provider the user has configured
    
    Returns:
        Dict with 'provider' and 'model' keys
    """
    # Check for Voyage AI
    if kwargs.get('voyage_api_key'):
        return {'provider': 'voyage', 'model': 'voyage-2'}
    
    # Check for Cohere
    if kwargs.get('cohere_api_key'):
        return {'provider': 'cohere', 'model': 'embed-english-v3.0'}
    
    # Default to OpenAI (most common)
    if kwargs.get('access_token'):
        return {'provider': 'openai', 'model': 'text-embedding-ada-002'}
    
    raise DocumentLibraryError("No embedding provider credentials found. Configure OpenAI, Voyage, or Cohere.")

def _detect_vector_db(**kwargs) -> str:
    """
    Detect which vector database the user has configured
    
    Returns:
        'pgvector' or 'pinecone'
    """
    if kwargs.get('pinecone_api_key'):
        return 'pinecone'
    
    # Default to pgvector (always available in PostgreSQL)
    return 'pgvector'

# ============================================================================
# SEARCH FUNCTIONS
# ============================================================================

def document_library_search_fulltext(
    query: str,
    limit: int = 10,
    sources: Optional[List[str]] = None,
    file_types: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Full-text search using PostgreSQL GIN indexes
    
    Args:
        query: Search query text
        limit: Max results to return
        sources: Filter by sources (e.g., ['google_drive', 'onedrive'])
        file_types: Filter by file types (e.g., ['document', 'pdf'])
        **kwargs: Credential injection
    
    Returns:
        Dict with 'success', 'results', 'total', 'query'
    """
    user_id = kwargs.get('_user_id')
    
    try:
        # Make API request to backend
        response = requests.post(
            'http://localhost:5001/api/document-library/search/fulltext',
            json={
                'query': query,
                'limit': limit,
                'sources': sources,
                'file_types': file_types,
                'user_id': user_id
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Full-text search failed: {str(e)}")

def document_library_search_semantic(
    query: str,
    limit: int = 10,
    threshold: float = 0.3,
    sources: Optional[List[str]] = None,
    file_types: Optional[List[str]] = None,
    embedding_provider: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Semantic search using multi-provider embeddings
    
    Automatically detects embedding provider from user credentials:
    - Voyage AI (if configured)
    - Cohere (if configured)
    - OpenAI (default/fallback)
    
    Args:
        query: Search query text
        limit: Max results to return
        threshold: Similarity threshold (0.0-1.0)
        sources: Filter by sources
        file_types: Filter by file types
        embedding_provider: Override auto-detection ('openai', 'voyage', 'cohere')
        **kwargs: Credential injection
    
    Returns:
        Dict with 'success', 'results', 'total', 'provider_used', 'vector_db_used'
    """
    user_id = kwargs.get('_user_id')
    
    try:
        # Auto-detect embedding provider if not specified
        if not embedding_provider:
            provider_config = _detect_embedding_provider(**kwargs)
            embedding_provider = provider_config['provider']
            model = provider_config['model']
        else:
            model = None
        
        # Generate query embedding
        query_embedding = _generate_embedding(
            query, 
            provider=embedding_provider,
            model=model,
            **kwargs
        )
        
        # Detect vector database
        vector_db = _detect_vector_db(**kwargs)
        
        # Make API request to backend
        response = requests.post(
            'http://localhost:5001/api/document-library/search/semantic',
            json={
                'query': query,
                'query_embedding': query_embedding,
                'limit': limit,
                'threshold': threshold,
                'sources': sources,
                'file_types': file_types,
                'embedding_provider': embedding_provider,
                'vector_db_provider': vector_db,
                'user_id': user_id
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        result = response.json()
        result['provider_used'] = embedding_provider
        result['vector_db_used'] = vector_db
        return result
    
    except Exception as e:
        raise DocumentLibraryError(f"Semantic search failed: {str(e)}")

def document_library_search_hybrid(
    query: str,
    limit: int = 10,
    fts_weight: float = 0.5,
    semantic_weight: float = 0.5,
    threshold: float = 0.3,
    **kwargs
) -> Dict[str, Any]:
    """
    Hybrid search combining full-text and semantic search with RRF
    
    Uses Reciprocal Rank Fusion algorithm to combine results from:
    - Full-text search (PostgreSQL GIN)
    - Semantic search (multi-provider embeddings)
    
    Args:
        query: Search query text
        limit: Max results to return
        fts_weight: Weight for full-text results (0.0-1.0)
        semantic_weight: Weight for semantic results (0.0-1.0)
        threshold: Semantic similarity threshold
        **kwargs: Credential injection
    
    Returns:
        Dict with 'success', 'results', 'total', 'provider_used', 'search_strategy'
    """
    user_id = kwargs.get('_user_id')
    
    try:
        # Detect embedding provider
        provider_config = _detect_embedding_provider(**kwargs)
        embedding_provider = provider_config['provider']
        model = provider_config['model']
        
        # Generate query embedding
        query_embedding = _generate_embedding(
            query,
            provider=embedding_provider,
            model=model,
            **kwargs
        )
        
        # Detect vector database
        vector_db = _detect_vector_db(**kwargs)
        
        # Make API request to backend
        response = requests.post(
            'http://localhost:5001/api/document-library/search/hybrid',
            json={
                'query': query,
                'query_embedding': query_embedding,
                'limit': limit,
                'fts_weight': fts_weight,
                'semantic_weight': semantic_weight,
                'threshold': threshold,
                'embedding_provider': embedding_provider,
                'vector_db_provider': vector_db,
                'user_id': user_id
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        result = response.json()
        result['provider_used'] = embedding_provider
        result['vector_db_used'] = vector_db
        result['search_strategy'] = 'hybrid_rrf'
        return result
    
    except Exception as e:
        raise DocumentLibraryError(f"Hybrid search failed: {str(e)}")

# ============================================================================
# ADDITIONAL FUNCTIONS (SAME AS BEFORE)
# ============================================================================

def document_library_filter_advanced(
    must: Optional[List[Dict]] = None,
    should: Optional[List[Dict]] = None,
    must_not: Optional[List[Dict]] = None,
    range_filters: Optional[Dict] = None,
    limit: int = 10,
    offset: int = 0,
    **kwargs
) -> Dict[str, Any]:
    """Elasticsearch-style advanced filtering (same as before)"""
    user_id = kwargs.get('_user_id')
    
    try:
        response = requests.post(
            'http://localhost:5001/api/document-library/filter',
            json={
                'must': must or [],
                'should': should or [],
                'must_not': must_not or [],
                'range_filters': range_filters or {},
                'limit': limit,
                'offset': offset,
                'user_id': user_id
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Advanced filter failed: {str(e)}")

def document_library_get_facets(
    sources: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Get aggregated facets for filter UI (same as before)"""
    user_id = kwargs.get('_user_id')
    
    try:
        response = requests.post(
            'http://localhost:5001/api/document-library/facets',
            json={
                'sources': sources,
                'user_id': user_id
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Get facets failed: {str(e)}")

def document_library_list(
    limit: int = 20,
    offset: int = 0,
    sort_by: str = 'indexed_at',
    sort_order: str = 'desc',
    **kwargs
) -> Dict[str, Any]:
    """List documents with pagination (same as before)"""
    user_id = kwargs.get('_user_id')
    
    try:
        response = requests.get(
            'http://localhost:5001/api/document-library/documents',
            params={
                'limit': limit,
                'offset': offset,
                'sort_by': sort_by,
                'sort_order': sort_order,
                'user_id': user_id
            }
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"List documents failed: {str(e)}")

def document_library_get(
    document_id: str,
    **kwargs
) -> Dict[str, Any]:
    """Get single document details (same as before)"""
    user_id = kwargs.get('_user_id')
    
    try:
        response = requests.get(
            f'http://localhost:5001/api/document-library/documents/{document_id}',
            params={'user_id': user_id}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Get document failed: {str(e)}")

def document_library_add(
    document_id: str,
    source: str,
    title: str,
    file_type: Optional[str] = None,
    content_text: Optional[str] = None,
    url: Optional[str] = None,
    tags: Optional[List[str]] = None,
    generate_embedding: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Add document to library with auto-embedding generation
    
    Enhanced to support multi-provider embedding generation
    """
    user_id = kwargs.get('_user_id')
    
    try:
        # Auto-detect embedding provider
        provider_config = _detect_embedding_provider(**kwargs)
        embedding_provider = provider_config['provider']
        model = provider_config['model']
        
        # Detect vector database
        vector_db = _detect_vector_db(**kwargs)
        
        # Generate embedding if content provided
        embedding = None
        if generate_embedding and content_text:
            embedding = _generate_embedding(
                content_text,
                provider=embedding_provider,
                model=model,
                **kwargs
            )
        
        response = requests.post(
            'http://localhost:5001/api/document-library/documents',
            json={
                'document_id': document_id,
                'source': source,
                'title': title,
                'file_type': file_type,
                'content_text': content_text,
                'embedding': embedding,
                'embedding_provider': embedding_provider if embedding else None,
                'vector_db_provider': vector_db,
                'url': url,
                'tags': tags or [],
                'user_id': user_id
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        result = response.json()
        result['provider_used'] = embedding_provider if embedding else None
        result['vector_db_used'] = vector_db
        return result
    
    except Exception as e:
        raise DocumentLibraryError(f"Add document failed: {str(e)}")

def document_library_get_stats(**kwargs) -> Dict[str, Any]:
    """Get library statistics (same as before)"""
    user_id = kwargs.get('_user_id')
    
    try:
        response = requests.get(
            'http://localhost:5001/api/document-library/stats',
            params={'user_id': user_id}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Get stats failed: {str(e)}")

def document_library_get_provider_stats(**kwargs) -> Dict[str, Any]:
    """
    Get embedding provider usage statistics
    
    NEW: Shows which embedding providers and vector databases are being used
    
    Returns:
        Dict with provider breakdown (OpenAI, Voyage, Cohere, Pinecone, pgvector)
    """
    user_id = kwargs.get('_user_id')
    
    try:
        response = requests.get(
            'http://localhost:5001/api/document-library/provider-stats',
            params={'user_id': user_id}
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise DocumentLibraryError(f"Get provider stats failed: {str(e)}")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def format_search_results_for_display(results: Dict[str, Any]) -> str:
    """Format search results for AI agent display"""
    if not results.get('success'):
        return f"❌ Search failed: {results.get('error', 'Unknown error')}"
    
    documents = results.get('results', [])
    total = results.get('total', 0)
    provider = results.get('provider_used', 'unknown')
    vector_db = results.get('vector_db_used', 'unknown')
    
    if not documents:
        return "📭 No documents found matching your search criteria"
    
    output = f"📚 Found {total} document(s) (Provider: {provider}, Vector DB: {vector_db})\n\n"
    
    for i, doc in enumerate(documents, 1):
        output += f"{i}. **{doc.get('title', 'Untitled')}**\n"
        output += f"   Source: {doc.get('source', 'unknown')}\n"
        output += f"   Type: {doc.get('file_type', 'unknown')}\n"
        
        if doc.get('similarity_score'):
            output += f"   Score: {doc['similarity_score']:.2%}\n"
        
        if doc.get('url'):
            output += f"   URL: {doc['url']}\n"
        
        output += "\n"
    
    return output

# Export all tools
__all__ = [
    'document_library_search_fulltext',
    'document_library_search_semantic',
    'document_library_search_hybrid',
    'document_library_filter_advanced',
    'document_library_get_facets',
    'document_library_list',
    'document_library_get',
    'document_library_add',
    'document_library_get_stats',
    'document_library_get_provider_stats',
    'DocumentLibraryError'
]
