"""
Pinecone Vector Database Tools

FILE: tools/implementations/pinecone/pinecone_tools.py
PURPOSE: Tool implementations for Pinecone vector database operations

FUNCTIONS:
- pinecone_query_vectors: Semantic search in vector DB
- pinecone_upsert_vectors: Add/update vectors
- pinecone_delete_vectors: Remove vectors
- pinecone_fetch_vectors: Get specific vectors
- pinecone_update_vector: Modify vector/metadata
- pinecone_describe_index_stats: Get DB statistics
- pinecone_list_namespaces: List all namespaces
- vector_db_upload_document: Process and upload document

DEPENDENCIES:
- pinecone-client (Python SDK)
- openai (for embeddings)
- PyPDF2 (PDF extraction)
- python-docx (DOCX extraction)

CREDENTIAL INJECTION:
- Requires _user_id and _injected_credentials=True
- Credentials fetched from user_platform_credentials table
- Platform: 'pinecone' and 'openai_embeddings'

LAST MODIFIED: 2025-11-25
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import hashlib
import uuid
import os

# Add paths
tools_dir = Path(__file__).parent.parent.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))


class PineconeToolsError(Exception):
    """Custom exception for Pinecone tools"""
    pass


def _get_pinecone_client(user_id: int, **kwargs):
    """Get authenticated Pinecone client (NEW JSONB FORMAT)"""
    try:
        from pinecone import Pinecone
        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials

        # Resolve credentials via org vault (GAP-V3)
        raw_cred = resolve_credentials(user_id, 'pinecone')
        if not raw_cred:
            raise PineconeToolsError("Pinecone credentials not configured. Add Pinecone in Organisation Settings > Connections.")

        creds = raw_cred.get('credentials') or {}
        if not creds.get('api_key'):
            creds['api_key'] = raw_cred.get('api_key') or raw_cred.get('credential_value')

        if not creds.get('api_key'):
            raise PineconeToolsError("Pinecone credentials not configured. Add Pinecone in Organisation Settings > Connections.")
        
        # JSONB credentials format:
        # {'api_key': 'pcsk_...', 'index_name': 'inhouseprint', 'environment': 'us-east-1', 'namespace': ''}
        api_key = creds['api_key']
        index_name = creds.get('index_name') or os.getenv('PINECONE_INDEX_NAME')
        environment = creds.get('environment', 'us-east-1')

        # GAP-C1 FIX: Always derive namespace from organisation_id for tenant isolation.
        # If the credential has an explicit namespace set (non-empty), use it as-is to
        # preserve any legacy personal-user namespaces.  Otherwise derive from org.
        explicit_namespace = creds.get('namespace', '')
        if explicit_namespace:
            namespace = explicit_namespace
        else:
            try:
                from AI_infrastructure.shared.database_utils import execute_query
                org_row = execute_query(
                    "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                    (user_id,), fetch_mode='one'
                )
                org_id = org_row['organisation_id'] if org_row and org_row.get('organisation_id') else None
            except Exception:
                org_id = None
            namespace = f"org_{org_id}" if org_id else f"user_{user_id}"

        if not index_name:
            raise PineconeToolsError("Pinecone index name not configured. Add it to your Pinecone credentials or set PINECONE_INDEX_NAME env var.")
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        index = pc.Index(index_name)
        
        print(f'[PINECONE] Connected to index: {index_name} (env: {environment}, namespace: {namespace or "default"})')
        
        # Return index and metadata dict (for backward compatibility)
        metadata = {
            'index_name': index_name,
            'environment': environment,
            'namespace': namespace
        }
        return index, metadata
        
    except Exception as e:
        print(f'[PINECONE] Client initialization error: {e}')
        raise PineconeToolsError(f"Failed to connect to Pinecone: {str(e)}")


def _get_openai_embeddings(text: str, user_id: int) -> List[float]:
    """
    Generate embeddings using configured provider (OpenAI or Voyager AI)
    
    Supports multiple providers:
    - OpenAI: text-embedding-ada-002 (1536), text-embedding-3-small (1536), text-embedding-3-large (3072)
    - Voyager AI: voyage-2 (1024), voyage-large-2 (1536), voyage-code-2 (1536)
    """
    try:
        # Resolve embedding credentials via org vault (GAP-V3)
        from AI_infrastructure.shared.org_credentials_loader import resolve_credentials
        raw_cred = (
            resolve_credentials(user_id, 'openai_embeddings')
            or resolve_credentials(user_id, 'openai')
        )

        if not raw_cred:
            raise PineconeToolsError("Embedding credentials not found. Add OpenAI or Voyager credentials in Organisation Settings > Connections.")

        creds = raw_cred.get('credentials') or {}
        if not creds.get('api_key'):
            creds['api_key'] = raw_cred.get('api_key') or raw_cred.get('credential_value')

        if not creds.get('api_key'):
            raise PineconeToolsError("Embedding API key not found in credentials.")

        # JSONB credentials format:
        # {'api_key': 'sk-proj-...', 'provider': 'openai', 'model': 'text-embedding-ada-002', 'dimensions': 1536}
        # OR
        # {'api_key': 'pa-...', 'provider': 'voyager', 'model': 'voyage-2', 'dimensions': 1024}
        api_key = creds['api_key']
        provider = creds.get('provider', 'openai')  # Default to OpenAI for backward compatibility
        model = creds.get('model', 'text-embedding-ada-002')
        
        # Route to appropriate provider
        if provider == 'voyager':
            return _get_voyager_embeddings(text, api_key, model)
        else:
            return _get_openai_embeddings_impl(text, api_key, model)
        
    except Exception as e:
        print(f'[PINECONE] Embedding generation error: {e}')
        raise PineconeToolsError(f"Failed to generate embeddings: {str(e)}")


def _get_openai_embeddings_impl(text: str, api_key: str, model: str) -> List[float]:
    """OpenAI embedding implementation"""
    try:
        import openai
        
        # Generate embedding
        openai.api_key = api_key
        response = openai.embeddings.create(
            model=model,
            input=text
        )
        
        embedding = response.data[0].embedding
        print(f'[PINECONE] Generated OpenAI embedding (model: {model}, dimension: {len(embedding)})')
        return embedding
        
    except Exception as e:
        raise PineconeToolsError(f"OpenAI embedding error: {str(e)}")


def _get_voyager_embeddings(text: str, api_key: str, model: str) -> List[float]:
    """
    Voyager AI embedding implementation
    
    Models:
    - voyage-2: 1024 dimensions, general purpose
    - voyage-large-2: 1536 dimensions, highest quality
    - voyage-code-2: 1536 dimensions, optimized for code
    """
    try:
        import requests
        
        # Voyager AI API endpoint
        url = "https://api.voyageai.com/v1/embeddings"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": [text],  # Voyager accepts array of texts
            "model": model
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        embedding = data['data'][0]['embedding']
        
        print(f'[PINECONE] Generated Voyager AI embedding (model: {model}, dimension: {len(embedding)})')
        return embedding
        
    except Exception as e:
        raise PineconeToolsError(f"Voyager AI embedding error: {str(e)}")


def pinecone_query_vectors(
    query_text: Optional[str] = None,
    query_vector: Optional[List[float]] = None,
    top_k: int = 4,
    namespace: str = '',
    filter: Optional[Dict] = None,
    include_metadata: bool = True,
    include_values: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Query vectors from Pinecone for semantic search
    
    Args:
        query_text: Text to search for (auto-embedded)
        query_vector: Pre-computed query vector
        top_k: Number of results (default: 4)
        namespace: Namespace to query
        filter: Metadata filter
        include_metadata: Include metadata in results
        include_values: Include vector values
        **kwargs: Credential injection (_user_id, _injected_credentials)
    
    Returns:
        Query results with matches
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        # Get query vector
        if query_text:
            query_vector = _get_openai_embeddings(query_text, user_id)
        elif not query_vector:
            raise PineconeToolsError("Either query_text or query_vector required")
        
        # Get Pinecone index
        index, metadata = _get_pinecone_client(user_id, **kwargs)

        # GAP-V4: use org-derived namespace as default if caller passed empty string
        effective_namespace = namespace or metadata.get('namespace', '')

        # GAP-V6: auto-inject org-scoped ownership filter so the AI only sees
        # this org's documents even when the caller doesn't provide a filter.
        # Merge with any explicit caller-supplied filter using $and.
        org_namespace = metadata.get('namespace', '')
        if org_namespace and org_namespace.startswith('org_'):
            org_filter = {'namespace': {'$eq': org_namespace}}
            if filter:
                effective_filter = {'$and': [org_filter, filter]}
            else:
                effective_filter = org_filter
        else:
            effective_filter = filter

        # Execute query
        results = index.query(
            vector=query_vector,
            top_k=min(top_k, 100),
            namespace=effective_namespace,
            filter=effective_filter,
            include_metadata=include_metadata,
            include_values=include_values
        )
        
        matches = []
        for match in results.get('matches', []):
            matches.append({
                'id': match.get('id'),
                'score': match.get('score'),
                'metadata': match.get('metadata', {}),
                'values': match.get('values') if include_values else None
            })
        
        print(f'[PINECONE] Query returned {len(matches)} matches')
        
        return {
            'success': True,
            'matches': matches,
            'query_dimension': len(query_vector)
        }
        
    except Exception as e:
        print(f'[PINECONE] Query error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def pinecone_upsert_vectors(
    vectors: List[Dict[str, Any]],
    namespace: str = '',
    **kwargs
) -> Dict[str, Any]:
    """
    Upsert vectors into Pinecone
    
    Args:
        vectors: List of {id, values, metadata} dicts
        namespace: Target namespace
        **kwargs: Credential injection
    
    Returns:
        Upsert confirmation
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        if not vectors:
            raise PineconeToolsError("vectors list cannot be empty")
        
        index, metadata = _get_pinecone_client(user_id, **kwargs)

        # GAP-V4: use org-derived namespace as default if caller passed empty string
        effective_namespace = namespace or metadata.get('namespace', '')

        # Format vectors for Pinecone
        formatted_vectors = []
        for v in vectors:
            if 'id' not in v or 'values' not in v:
                raise PineconeToolsError("Each vector must have 'id' and 'values'")
            
            formatted_vectors.append({
                'id': str(v['id']),
                'values': v['values'],
                'metadata': v.get('metadata', {})
            })
        
        # Batch upsert (Pinecone recommends batches of 100-1000)
        batch_size = 500
        total_upserted = 0
        
        for i in range(0, len(formatted_vectors), batch_size):
            batch = formatted_vectors[i:i+batch_size]
            index.upsert(vectors=batch, namespace=effective_namespace)
            total_upserted += len(batch)
            print(f'[PINECONE] Upserted batch {i//batch_size + 1}: {len(batch)} vectors')

        return {
            'success': True,
            'upserted_count': total_upserted,
            'namespace': effective_namespace
        }
        
    except Exception as e:
        print(f'[PINECONE] Upsert error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def pinecone_delete_vectors(
    ids: Optional[List[str]] = None,
    delete_all: bool = False,
    namespace: str = '',
    filter: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete vectors from Pinecone
    
    Args:
        ids: Vector IDs to delete
        delete_all: Delete all vectors in namespace
        namespace: Target namespace
        filter: Metadata filter
        **kwargs: Credential injection
    
    Returns:
        Deletion confirmation
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        if not any([ids, delete_all, filter]):
            raise PineconeToolsError("Provide ids, delete_all=True, or filter")
        
        index, metadata = _get_pinecone_client(user_id, **kwargs)

        # GAP-V4: use org-derived namespace as default if caller passed empty string
        effective_namespace = namespace or metadata.get('namespace', '')

        if delete_all:
            if not effective_namespace:
                raise PineconeToolsError("namespace required when delete_all=True")
            index.delete(delete_all=True, namespace=effective_namespace)
            print(f'[PINECONE] Deleted all vectors in namespace: {effective_namespace}')
        elif filter:
            index.delete(filter=filter, namespace=effective_namespace)
            print(f'[PINECONE] Deleted vectors matching filter')
        else:
            index.delete(ids=ids, namespace=effective_namespace)
            print(f'[PINECONE] Deleted {len(ids)} vectors')
        
        return {
            'success': True,
            'message': 'Vectors deleted successfully'
        }
        
    except Exception as e:
        print(f'[PINECONE] Delete error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def pinecone_fetch_vectors(
    ids: List[str],
    namespace: str = '',
    **kwargs
) -> Dict[str, Any]:
    """
    Fetch specific vectors by ID
    
    Args:
        ids: Vector IDs to fetch
        namespace: Namespace to fetch from
        **kwargs: Credential injection
    
    Returns:
        Fetched vectors
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        if not ids:
            raise PineconeToolsError("ids list cannot be empty")
        
        index, metadata = _get_pinecone_client(user_id, **kwargs)

        # GAP-V4: use org-derived namespace as default if caller passed empty string
        effective_namespace = namespace or metadata.get('namespace', '')

        results = index.fetch(ids=ids, namespace=effective_namespace)
        
        vectors = []
        for vec_id, vec_data in results.get('vectors', {}).items():
            vectors.append({
                'id': vec_id,
                'values': vec_data.get('values'),
                'metadata': vec_data.get('metadata', {})
            })
        
        print(f'[PINECONE] Fetched {len(vectors)} vectors')
        
        return {
            'success': True,
            'vectors': vectors
        }
        
    except Exception as e:
        print(f'[PINECONE] Fetch error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def pinecone_update_vector(
    id: str,
    values: Optional[List[float]] = None,
    metadata: Optional[Dict] = None,
    namespace: str = '',
    **kwargs
) -> Dict[str, Any]:
    """
    Update a vector's values or metadata
    
    Args:
        id: Vector ID to update
        values: New vector values (optional)
        metadata: New metadata (merges with existing)
        namespace: Namespace containing vector
        **kwargs: Credential injection
    
    Returns:
        Update confirmation
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        if not any([values, metadata]):
            raise PineconeToolsError("Provide values or metadata to update")
        
        index, metadata_config = _get_pinecone_client(user_id, **kwargs)

        # GAP-V4: use org-derived namespace as default if caller passed empty string
        effective_namespace = namespace or metadata_config.get('namespace', '')

        update_dict = {'id': id}
        if values:
            update_dict['values'] = values
        if metadata:
            update_dict['set_metadata'] = metadata

        index.update(**update_dict, namespace=effective_namespace)
        
        print(f'[PINECONE] Updated vector: {id}')
        
        return {
            'success': True,
            'message': 'Vector updated successfully'
        }
        
    except Exception as e:
        print(f'[PINECONE] Update error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def pinecone_describe_index_stats(
    filter: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Get index statistics
    
    Args:
        filter: Optional metadata filter
        **kwargs: Credential injection
    
    Returns:
        Index stats including total vectors, dimensions, namespaces
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        index, metadata = _get_pinecone_client(user_id, **kwargs)
        
        stats = index.describe_index_stats(filter=filter)
        
        print(f'[PINECONE] Retrieved index stats: {stats.get("total_vector_count", 0)} vectors')
        
        return {
            'success': True,
            'total_vector_count': stats.get('total_vector_count', 0),
            'dimension': stats.get('dimension', 0),
            'index_fullness': stats.get('index_fullness', 0),
            'namespaces': stats.get('namespaces', {})
        }
        
    except Exception as e:
        print(f'[PINECONE] Describe stats error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def pinecone_list_namespaces(**kwargs) -> Dict[str, Any]:
    """
    List all namespaces in index
    
    Args:
        **kwargs: Credential injection
    
    Returns:
        List of namespaces with metadata
    """
    try:
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        # Get stats to list namespaces
        stats_result = pinecone_describe_index_stats(**kwargs)
        
        if not stats_result.get('success'):
            return stats_result
        
        namespaces_data = stats_result.get('namespaces', {})
        
        namespaces = []
        for ns_name, ns_stats in namespaces_data.items():
            namespaces.append({
                'name': ns_name,
                'vector_count': ns_stats.get('vector_count', 0),
                'created_at': ''  # Pinecone doesn't provide timestamp
            })
        
        print(f'[PINECONE] Listed {len(namespaces)} namespaces')
        
        return {
            'success': True,
            'namespaces': namespaces
        }
        
    except Exception as e:
        print(f'[PINECONE] List namespaces error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def vector_db_upload_document(
    file_path: str,
    filename: str,
    chunk_size: int = 800,
    chunk_overlap: int = 20,
    namespace: str = '',
    category: str = 'general',
    subcategory: str = '',
    tags: Optional[List[str]] = None,
    visibility: str = 'user',
    **kwargs
) -> Dict[str, Any]:
    """
    Upload and process document into vector database with HYBRID SEARCH support.
    
    🚀 ENHANCED FEATURES:
    - Sparse vector generation (TF-IDF) for keyword matching
    - User-linked metadata (owner_user_id automatic tagging)
    - Hierarchical categorization (category/subcategory)
    - Tag system for flexible organization
    - Visibility control (user/global/team)
    
    Handles: PDF, TXT, MD, DOCX
    Pipeline: Extract text → Chunk → Dense + Sparse Embed → Upsert to Pinecone
    
    Args:
        file_path: Path to document file
        filename: Original filename
        chunk_size: Text chunk size (default: 800)
        chunk_overlap: Chunk overlap (default: 20)
        namespace: Target namespace (default: user_{user_id}_{category})
        category: Document category (default: 'general')
        subcategory: Document subcategory (optional)
        tags: List of tags for organization (optional)
        visibility: 'user' (private), 'global' (public), 'team' (default: 'user')
        **kwargs: Credential injection
    
    Returns:
        {
            "success": true,
            "vectors_uploaded": 45,
            "document_id": "abc12345",
            "namespace": "user_42_legal",
            "hybrid_search_enabled": true
        }
    """
    try:
        from datetime import datetime
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
        
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("user_id required")
        
        # Extract text from file
        import os
        ext = os.path.splitext(filename)[1].lower()
        
        print(f'[VECTOR DB] Processing document: {filename} ({ext})')
        
        text = _extract_text_from_file(file_path, ext)
        
        if not text:
            raise PineconeToolsError("No text extracted from document")
        
        print(f'[VECTOR DB] Extracted {len(text)} characters')
        
        # Chunk text
        chunks = _chunk_text(text, chunk_size, chunk_overlap)
        print(f'[VECTOR DB] Created {len(chunks)} chunks')
        
        # Generate TF-IDF vectorizer for sparse vectors
        print(f'[VECTOR DB] Generating sparse vectors (TF-IDF)...')
        tfidf = TfidfVectorizer(max_features=100, stop_words='english')
        
        try:
            # Fit TF-IDF on all chunks
            tfidf_matrix = tfidf.fit_transform(chunks)
            has_sparse_vectors = True
        except Exception as tfidf_error:
            print(f'[VECTOR DB] Warning: TF-IDF generation failed, proceeding without sparse vectors: {tfidf_error}')
            has_sparse_vectors = False
        
        # Generate embeddings for chunks
        vectors = []
        doc_id = hashlib.md5(filename.encode()).hexdigest()[:8]
        upload_date = datetime.utcnow().isoformat()
        
        # Auto-generate namespace if not provided — use empty to let upsert derive org namespace (GAP-V4)
        # The category is stored in vector metadata; namespace provides tenant isolation only.
        
        # Batch embedding generation (500 at a time)
        batch_size = 500
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]
            
            for j, chunk in enumerate(batch_chunks):
                chunk_id = f"{doc_id}_chunk_{i+j}"
                
                # Dense embedding (semantic)
                dense_embedding = _get_openai_embeddings(chunk, user_id)
                
                # Build vector object
                vector_obj = {
                    'id': chunk_id,
                    'values': dense_embedding,
                    'metadata': {
                        # Original metadata
                        'text': chunk,
                        'document': filename,
                        'document_id': doc_id,
                        'chunk_index': i+j,
                        'chunk_size': len(chunk),
                        # 🚀 ENHANCED METADATA
                        'owner_user_id': user_id,  # User ownership
                        'category': category,  # Hierarchical categorization
                        'subcategory': subcategory or '',
                        'tags': tags or [],  # Flexible tagging
                        'visibility': visibility,  # Access control
                        'upload_date': upload_date,
                        'file_extension': ext,
                        'source': 'vector_db_upload_document'
                    }
                }
                
                # Add sparse vector if available (HYBRID SEARCH)
                if has_sparse_vectors:
                    sparse_row = tfidf_matrix[i+j]
                    sparse_indices = sparse_row.indices.tolist()
                    sparse_values = sparse_row.data.tolist()
                    
                    if sparse_indices and sparse_values:
                        vector_obj['sparse_values'] = {
                            'indices': sparse_indices,
                            'values': sparse_values
                        }
                
                vectors.append(vector_obj)
            
            print(f'[VECTOR DB] Embedded batch {i//batch_size + 1}: {len(batch_chunks)} chunks')
        
        # Upsert to Pinecone
        upsert_result = pinecone_upsert_vectors(
            vectors=vectors,
            namespace=namespace,
            **kwargs
        )
        
        if not upsert_result.get('success'):
            raise PineconeToolsError(upsert_result.get('error', 'Upsert failed'))
        
        print(f'[VECTOR DB] ✅ Successfully uploaded {len(vectors)} vectors to namespace: {namespace}')
        print(f'[VECTOR DB] 🎯 Hybrid search enabled: {has_sparse_vectors}')
        
        return {
            'success': True,
            'vectors_uploaded': len(vectors),
            'document_id': doc_id,
            'namespace': namespace,
            'filename': filename,
            'hybrid_search_enabled': has_sparse_vectors,
            'metadata': {
                'category': category,
                'subcategory': subcategory,
                'tags': tags,
                'visibility': visibility,
                'owner_user_id': user_id
            }
        }
        
    except Exception as e:
        print(f'[VECTOR DB] Upload document error: {e}')
        return {
            'success': False,
            'error': str(e)
        }


def _extract_text_from_file(file_path: str, ext: str) -> str:
    """Extract text from various file formats"""
    try:
        if ext == '.txt' or ext == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif ext == '.pdf':
            import PyPDF2
            text = ''
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + '\n'
            return text
        
        elif ext == '.docx':
            import docx
            doc = docx.Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
            return text
        
        else:
            raise PineconeToolsError(f"Unsupported file format: {ext}")
    
    except Exception as e:
        raise PineconeToolsError(f"Text extraction failed: {str(e)}")


def _chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk:
            chunks.append(chunk)
        
        start += chunk_size - overlap
    
    return chunks


# ==================== NEW TOOL 1: QUERY NAMESPACES ====================

def pinecone_query_namespaces(
    query_text: str,
    namespaces: List[str],
    metric: str = 'cosine',
    top_k: int = 10,
    filter: Optional[Dict[str, Any]] = None,
    include_metadata: bool = True,
    include_values: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Query multiple namespaces in parallel and aggregate results.
    
    **HYBRID SEARCH**: Automatically generates sparse vectors from query_text for keyword matching.
    
    Args:
        query_text: Natural language query
        namespaces: List of namespace names to search
        metric: Similarity metric ('cosine', 'euclidean', 'dotproduct')
        top_k: Results per namespace
        filter: Metadata filter (optional)
        include_metadata: Include document metadata
        include_values: Include vector values
        **kwargs: Credential injection (_user_id, _injected_credentials)
        
    Returns:
        {
            "success": true,
            "matches": [
                {
                    "id": "vec_123",
                    "score": 0.95,
                    "namespace": "user_42_legal",
                    "metadata": {...}
                }
            ],
            "usage": {"read_units": 3}
        }
    """
    try:
        import os
        from pinecone import Pinecone
        from sklearn.feature_extraction.text import TfidfVectorizer
        import numpy as np
        
        # Get credentials
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("_user_id required")
        
        pinecone_api_key = kwargs.get('pinecone_api_key')
        pinecone_index_name = kwargs.get('pinecone_index_name')
        openai_api_key = kwargs.get('openai_api_key')
        
        if not pinecone_api_key or not pinecone_index_name:
            raise PineconeToolsError("Pinecone credentials required")
        
        if not openai_api_key:
            raise PineconeToolsError("OpenAI API key required for embeddings")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)
        
        # Generate dense embedding (semantic)
        from openai import OpenAI
        client = OpenAI(api_key=openai_api_key)
        
        embedding_response = client.embeddings.create(
            input=query_text,
            model='text-embedding-ada-002'
        )
        dense_vector = embedding_response.data[0].embedding
        
        # Generate sparse vector (keywords) using TF-IDF
        # Simple approach: tokenize query and create sparse representation
        words = query_text.lower().split()
        unique_words = list(set(words))
        
        # Create sparse vector from word positions
        # Note: This is a simplified approach. Production should use proper TF-IDF corpus.
        sparse_indices = [hash(word) % 10000 for word in unique_words]  # Hash to index space
        sparse_values = [1.0 / len(unique_words)] * len(unique_words)  # Equal weight
        
        sparse_vector = {
            'indices': sparse_indices,
            'values': sparse_values
        }
        
        # Query each namespace
        all_matches = []
        total_read_units = 0
        
        for namespace in namespaces:
            try:
                # Query with both dense and sparse vectors (hybrid search)
                query_response = index.query(
                    namespace=namespace,
                    vector=dense_vector,
                    sparse_vector=sparse_vector,  # Hybrid search!
                    top_k=top_k,
                    filter=filter,
                    include_metadata=include_metadata,
                    include_values=include_values
                )
                
                # Add namespace to each match
                for match in query_response.get('matches', []):
                    match['namespace'] = namespace
                    all_matches.append(match)
                
                total_read_units += query_response.get('usage', {}).get('read_units', 0)
                
            except Exception as ns_error:
                # Log error but continue with other namespaces
                print(f"[query_namespaces] Error in namespace '{namespace}': {ns_error}")
                continue
        
        # Sort all matches by score (descending)
        all_matches.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Return top_k across all namespaces
        final_matches = all_matches[:top_k]
        
        return {
            "success": True,
            "matches": final_matches,
            "usage": {"read_units": total_read_units},
            "query_text": query_text,
            "namespaces_searched": namespaces,
            "hybrid_search": True  # Indicates sparse vectors were used
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ==================== NEW TOOL 2: FETCH BY METADATA ====================

def pinecone_fetch_by_metadata(
    filter: Dict[str, Any],
    namespace: str = '',
    limit: int = 100,
    fields: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Fetch vectors by metadata filter WITHOUT generating query embeddings.
    
    **USE CASES**:
    - Data export and compliance auditing
    - Finding all documents by category, year, author
    - Bulk operations on tagged documents
    
    Args:
        filter: Metadata filter with operators ($eq, $ne, $gt, $lt, $in, etc.)
        namespace: Target namespace (default: '' = default namespace)
        limit: Max results (default: 100, max: 1000)
        fields: Metadata fields to return (None = all fields)
        **kwargs: Credential injection (_user_id, _injected_credentials)
        
    Filter Examples:
        {"category": {"$eq": "legal"}}
        {"year": {"$gte": 2024}, "author": {"$in": ["John", "Jane"]}}
        {"tags": {"$in": ["important"]}, "archived": {"$ne": true}}
        
    Returns:
        {
            "success": true,
            "vectors": [
                {
                    "id": "vec_123",
                    "metadata": {...},
                    "namespace": "user_42_legal"
                }
            ],
            "total_count": 45
        }
    """
    try:
        from pinecone import Pinecone
        
        # Get credentials
        user_id = kwargs.get('_user_id')
        if not user_id:
            raise PineconeToolsError("_user_id required")
        
        pinecone_api_key = kwargs.get('pinecone_api_key')
        pinecone_index_name = kwargs.get('pinecone_index_name')
        
        if not pinecone_api_key or not pinecone_index_name:
            raise PineconeToolsError("Pinecone credentials required")
        
        # Initialize Pinecone
        pc = Pinecone(api_key=pinecone_api_key)
        index = pc.Index(pinecone_index_name)
        
        # Clamp limit
        limit = min(limit, 1000)
        
        # Strategy: Use query with zero vector and metadata filter
        # This retrieves vectors based solely on metadata
        dimension = 1536  # Default OpenAI dimension
        
        try:
            # Get index dimension from stats
            stats = index.describe_index_stats()
            dimension = stats.get('dimension', 1536)
        except:
            pass
        
        zero_vector = [0.0] * dimension
        
        # Query with zero vector (no semantic matching, only metadata filter)
        query_response = index.query(
            namespace=namespace,
            vector=zero_vector,
            filter=filter,
            top_k=limit,
            include_metadata=True,
            include_values=False  # We don't need vector values
        )
        
        matches = query_response.get('matches', [])
        
        # Filter fields if specified
        if fields:
            filtered_matches = []
            for match in matches:
                filtered_metadata = {k: v for k, v in match.get('metadata', {}).items() if k in fields}
                filtered_matches.append({
                    "id": match['id'],
                    "metadata": filtered_metadata,
                    "namespace": namespace
                })
            matches = filtered_matches
        else:
            # Add namespace to each match
            for match in matches:
                match['namespace'] = namespace
        
        return {
            "success": True,
            "vectors": matches,
            "total_count": len(matches),
            "filter_applied": filter,
            "namespace": namespace
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


# ==================== SMART VECTOR SEARCH TOOLS (AI-OPTIMIZED) ====================

def pinecone_search_summaries(
    query_text: str,
    top_k: int = 10,
    namespace: Optional[str] = None,
    filter: Optional[Dict[str, Any]] = None,
    include_chunk_preview: bool = True,
    _user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    🎯 SMART SEARCH: Returns document SUMMARIES only (no full vectors)
    
    **Purpose:** Enable AI to efficiently scan vector database without token overload.
    Returns compact list of document names, categories, and preview snippets.
    AI can then use pinecone_get_vector_details() to retrieve specific documents.
    
    **AI Agent Usage Pattern:**
    1. User: "Find contracts about severance"
    2. AI calls: pinecone_search_summaries(query_text="severance agreements", top_k=20)
    3. AI receives: 20 doc summaries (200 tokens vs 5000 tokens for full vectors)
    4. AI analyzes summaries, identifies 3 relevant docs
    5. AI calls: pinecone_get_vector_details(vector_ids=['doc1_chunk0', 'doc2_chunk0', 'doc3_chunk0'])
    6. AI reads full content (only 3 docs, ~800 tokens)
    
    **Result:** 80% token savings, more purposeful retrieval
    
    Args:
        query_text: Search query (e.g., "employment contracts 2024")
        top_k: Number of results (default: 10, max: 100)
        namespace: Folder to search (optional)
        filter: Metadata filter (e.g., {'category': 'legal', 'year': 2024})
        include_chunk_preview: Include 100-char preview of each chunk (default: True)
        _user_id: User ID for credential injection (required)
        
    Returns:
        {
            "success": true,
            "summary_mode": true,
            "query": "severance agreements",
            "results_count": 20,
            "documents": [
                {
                    "vector_id": "doc_abc123_chunk_0",
                    "document_name": "Employment_Contract_2024.pdf",
                    "category": "legal",
                    "subcategory": "contracts",
                    "tags": ["employment", "severance", "2024"],
                    "score": 0.92,
                    "chunk_index": 0,
                    "total_chunks": 15,
                    "preview": "Section 4: Termination. Upon termination of employment, the employee is entitled to...",
                    "metadata": {...}  // Full metadata for filtering
                },
                ...
            ],
            "unique_documents": 8,  // Number of unique docs (vs 20 chunks)
            "grouped_by_document": {
                "Employment_Contract_2024.pdf": {
                    "chunk_count": 5,
                    "best_score": 0.92,
                    "category": "legal",
                    "vector_ids": ["doc_abc123_chunk_0", "doc_abc123_chunk_2", ...]
                },
                ...
            },
            "next_steps": "Use pinecone_get_vector_details(vector_ids=[...]) to retrieve full content of specific documents"
        }
    """
    
    if not _user_id:
        return {"success": False, "error": "User ID required (_user_id parameter)"}
    
    try:
        # Get Pinecone client
        index, config = _get_pinecone_client(_user_id, **kwargs)
        namespace = namespace or config.get('namespace', '')
        
        # Generate embedding for query
        query_vector = _get_openai_embeddings(query_text, _user_id)
        
        # Query Pinecone (fetch more than needed to group by document)
        query_params = {
            'vector': query_vector,
            'top_k': min(top_k * 3, 100),  # Get 3x chunks to ensure good document coverage
            'namespace': namespace,
            'include_metadata': True,
            'include_values': False  # No full vectors needed
        }
        
        if filter:
            query_params['filter'] = filter
        
        print(f'[SMART SEARCH] Querying for summaries: "{query_text}" (top_k={top_k}, namespace={namespace or "default"})')
        results = index.query(**query_params)
        
        # Process results into summaries
        documents = []
        doc_groups = {}  # Group chunks by document
        
        for match in results.get('matches', []):
            vector_id = match['id']
            score = match['score']
            metadata = match.get('metadata', {})
            
            # Extract document info from metadata
            doc_name = metadata.get('document', metadata.get('filename', 'Unknown Document'))
            category = metadata.get('category', 'uncategorized')
            subcategory = metadata.get('subcategory', '')
            tags = metadata.get('tags', [])
            chunk_text = metadata.get('text', '')
            chunk_index = metadata.get('chunk_index', 0)
            total_chunks = metadata.get('total_chunks', 1)
            
            # Create preview (first 150 chars)
            preview = chunk_text[:150] + '...' if len(chunk_text) > 150 else chunk_text
            
            # Build summary object
            doc_summary = {
                "vector_id": vector_id,
                "document_name": doc_name,
                "category": category,
                "subcategory": subcategory,
                "tags": tags,
                "score": round(score, 4),
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "metadata": metadata
            }
            
            if include_chunk_preview:
                doc_summary["preview"] = preview
            
            documents.append(doc_summary)
            
            # Group by document
            if doc_name not in doc_groups:
                doc_groups[doc_name] = {
                    "chunk_count": 0,
                    "best_score": 0,
                    "category": category,
                    "subcategory": subcategory,
                    "tags": tags,
                    "vector_ids": []
                }
            
            doc_groups[doc_name]["chunk_count"] += 1
            doc_groups[doc_name]["best_score"] = max(doc_groups[doc_name]["best_score"], score)
            doc_groups[doc_name]["vector_ids"].append(vector_id)
        
        # Limit to requested top_k (after grouping analysis)
        documents = documents[:top_k]
        
        print(f'[SMART SEARCH] Found {len(documents)} chunks from {len(doc_groups)} unique documents')
        
        return {
            "success": True,
            "summary_mode": True,
            "query": query_text,
            "results_count": len(documents),
            "documents": documents,
            "unique_documents": len(doc_groups),
            "grouped_by_document": doc_groups,
            "next_steps": "Use pinecone_get_vector_details(vector_ids=[...]) to retrieve full content of specific chunks",
            "token_savings": f"~{len(documents) * 400} tokens saved vs full vector retrieval"
        }
        
    except Exception as e:
        print(f'[SMART SEARCH] Error: {e}')
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def pinecone_get_vector_details(
    vector_ids: List[str],
    namespace: Optional[str] = None,
    include_full_text: bool = True,
    _user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    📄 RETRIEVE FULL VECTORS: Get complete content of specific vectors by ID
    
    **Purpose:** After AI reviews summaries from pinecone_search_summaries(),
    retrieve full text content of only the relevant documents.
    
    **AI Agent Usage:**
    1. AI called pinecone_search_summaries() → got 20 doc summaries
    2. AI analyzed summaries, identified 3 relevant documents
    3. AI extracts vector_ids: ['doc_abc_chunk_0', 'doc_abc_chunk_1', 'doc_xyz_chunk_0']
    4. AI calls: pinecone_get_vector_details(vector_ids=['doc_abc_chunk_0', ...])
    5. AI receives full text content (~800 tokens for 3 docs)
    6. AI provides detailed answer to user with quotes from specific sections
    
    Args:
        vector_ids: List of vector IDs to retrieve (from search_summaries results)
        namespace: Folder to search (optional)
        include_full_text: Include complete chunk text (default: True)
        _user_id: User ID for credential injection (required)
        
    Returns:
        {
            "success": true,
            "retrieved_count": 3,
            "vectors": [
                {
                    "id": "doc_abc123_chunk_0",
                    "document_name": "Employment_Contract_2024.pdf",
                    "full_text": "COMPLETE CHUNK TEXT HERE (500-1000 chars)...",
                    "metadata": {
                        "document": "Employment_Contract_2024.pdf",
                        "category": "legal",
                        "chunk_index": 0,
                        "total_chunks": 15,
                        ...
                    },
                    "chunk_info": {
                        "index": 0,
                        "total": 15,
                        "next_chunk_id": "doc_abc123_chunk_1",
                        "prev_chunk_id": null
                    }
                },
                ...
            ],
            "total_text_length": 2847,
            "suggested_next_chunks": ["doc_abc123_chunk_1", "doc_abc123_chunk_2"]  // Adjacent chunks for context
        }
    """
    
    if not _user_id:
        return {"success": False, "error": "User ID required (_user_id parameter)"}
    
    if not vector_ids or len(vector_ids) == 0:
        return {"success": False, "error": "No vector IDs provided"}
    
    try:
        # Get Pinecone client
        index, config = _get_pinecone_client(_user_id, **kwargs)
        namespace = namespace or config.get('namespace', '')
        
        print(f'[VECTOR DETAILS] Fetching {len(vector_ids)} vectors from namespace: {namespace or "default"}')
        
        # Fetch vectors by ID
        fetch_result = index.fetch(ids=vector_ids, namespace=namespace)
        
        if not fetch_result or 'vectors' not in fetch_result:
            return {
                "success": False,
                "error": "No vectors found with provided IDs",
                "requested_ids": vector_ids
            }
        
        vectors_data = fetch_result['vectors']
        
        # Process each vector
        detailed_vectors = []
        total_text_length = 0
        suggested_chunks = set()
        
        for vec_id, vec_data in vectors_data.items():
            metadata = vec_data.get('metadata', {})
            
            # Extract data
            doc_name = metadata.get('document', metadata.get('filename', 'Unknown'))
            full_text = metadata.get('text', '') if include_full_text else '[Text excluded]'
            chunk_index = metadata.get('chunk_index', 0)
            total_chunks = metadata.get('total_chunks', 1)
            
            # Build detailed response
            vector_detail = {
                "id": vec_id,
                "document_name": doc_name,
                "metadata": metadata,
                "chunk_info": {
                    "index": chunk_index,
                    "total": total_chunks
                }
            }
            
            if include_full_text:
                vector_detail["full_text"] = full_text
                total_text_length += len(full_text)
            
            # Suggest adjacent chunks for context
            if chunk_index > 0:
                prev_id = vec_id.rsplit('_', 1)[0] + f'_{chunk_index - 1}'
                vector_detail["chunk_info"]["prev_chunk_id"] = prev_id
                suggested_chunks.add(prev_id)
            else:
                vector_detail["chunk_info"]["prev_chunk_id"] = None
            
            if chunk_index < total_chunks - 1:
                next_id = vec_id.rsplit('_', 1)[0] + f'_{chunk_index + 1}'
                vector_detail["chunk_info"]["next_chunk_id"] = next_id
                suggested_chunks.add(next_id)
            else:
                vector_detail["chunk_info"]["next_chunk_id"] = None
            
            detailed_vectors.append(vector_detail)
        
        # Remove already-fetched chunks from suggestions
        suggested_chunks = list(suggested_chunks - set(vector_ids))
        
        print(f'[VECTOR DETAILS] Retrieved {len(detailed_vectors)} vectors (total text: {total_text_length} chars)')
        
        return {
            "success": True,
            "retrieved_count": len(detailed_vectors),
            "vectors": detailed_vectors,
            "total_text_length": total_text_length,
            "suggested_next_chunks": suggested_chunks[:5] if suggested_chunks else []
        }
        
    except Exception as e:
        print(f'[VECTOR DETAILS] Error: {e}')
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


def pinecone_search_and_retrieve(
    query_text: str,
    max_documents: int = 3,
    chunks_per_document: int = 2,
    namespace: Optional[str] = None,
    filter: Optional[Dict[str, Any]] = None,
    auto_retrieve: bool = True,
    _user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    🚀 SMART SEARCH + RETRIEVE: Two-stage search (summary → selective retrieval)
    
    **Purpose:** Combines search_summaries + get_vector_details in one call.
    Searches, ranks by document relevance, retrieves top N documents automatically.
    
    **AI Agent Usage:**
    When AI needs immediate detailed results without two-step process:
    
    User: "What do my contracts say about severance pay?"
    AI: pinecone_search_and_retrieve(query_text="severance pay", max_documents=3)
    Result: Full text from top 3 most relevant documents (auto-selected)
    
    **Workflow:**
    1. Search vector DB for query (gets 50 chunk summaries)
    2. Group chunks by document, rank by best_score
    3. Select top N documents (max_documents parameter)
    4. Retrieve M chunks per document (chunks_per_document parameter)
    5. Return full text + document structure
    
    Args:
        query_text: Search query
        max_documents: Max documents to retrieve full content (default: 3)
        chunks_per_document: Chunks per document to retrieve (default: 2 = ~1600 chars)
        namespace: Folder to search
        filter: Metadata filter
        auto_retrieve: If False, returns summaries only (default: True)
        _user_id: User ID for credential injection
        
    Returns:
        {
            "success": true,
            "query": "severance pay",
            "search_phase": {
                "total_chunks_found": 45,
                "unique_documents": 12,
                "top_documents": ["Contract_A.pdf", "Contract_B.pdf", "Policy_C.pdf"]
            },
            "retrieval_phase": {
                "documents_retrieved": 3,
                "chunks_retrieved": 6,
                "total_text_length": 4200
            },
            "documents": [
                {
                    "document_name": "Employment_Contract_2024.pdf",
                    "relevance_score": 0.94,
                    "chunks": [
                        {
                            "chunk_index": 0,
                            "score": 0.94,
                            "text": "FULL CHUNK TEXT..."
                        },
                        {
                            "chunk_index": 2,
                            "score": 0.89,
                            "text": "FULL CHUNK TEXT..."
                        }
                    ],
                    "metadata": {...}
                },
                ...
            ]
        }
    """
    
    if not _user_id:
        return {"success": False, "error": "User ID required (_user_id parameter)"}
    
    try:
        print(f'[SMART SEARCH+RETRIEVE] Query: "{query_text}" (max_docs={max_documents}, chunks_per_doc={chunks_per_document})')
        
        # PHASE 1: Search for summaries (get 50 chunks to ensure good document coverage)
        summary_result = pinecone_search_summaries(
            query_text=query_text,
            top_k=50,
            namespace=namespace,
            filter=filter,
            include_chunk_preview=False,  # Don't need previews if auto-retrieving
            _user_id=_user_id,
            **kwargs
        )
        
        if not summary_result.get('success'):
            return summary_result  # Pass through error
        
        # Extract grouped documents
        doc_groups = summary_result.get('grouped_by_document', {})
        
        if not doc_groups:
            return {
                "success": True,
                "query": query_text,
                "message": "No documents found matching query",
                "documents": []
            }
        
        # PHASE 2: Rank documents by best_score and select top N
        ranked_docs = sorted(
            doc_groups.items(),
            key=lambda x: x[1]['best_score'],
            reverse=True
        )[:max_documents]
        
        top_doc_names = [doc[0] for doc in ranked_docs]
        
        print(f'[SMART SEARCH+RETRIEVE] Top {len(top_doc_names)} documents: {top_doc_names}')
        
        if not auto_retrieve:
            # Return summaries only
            return {
                "success": True,
                "query": query_text,
                "auto_retrieve": False,
                "search_phase": {
                    "total_chunks_found": summary_result['results_count'],
                    "unique_documents": len(doc_groups),
                    "top_documents": top_doc_names
                },
                "document_summaries": {
                    doc_name: doc_data for doc_name, doc_data in ranked_docs
                },
                "next_steps": f"Call pinecone_get_vector_details() with vector_ids from top documents"
            }
        
        # PHASE 3: Retrieve full text from top documents
        vector_ids_to_fetch = []
        
        for doc_name, doc_data in ranked_docs:
            # Get top M chunks from this document (sorted by score)
            all_vector_ids = doc_data['vector_ids']
            
            # Fetch chunk scores to sort
            doc_chunks = [
                doc for doc in summary_result['documents']
                if doc['document_name'] == doc_name
            ]
            doc_chunks_sorted = sorted(doc_chunks, key=lambda x: x['score'], reverse=True)
            
            # Take top chunks_per_document
            top_chunk_ids = [chunk['vector_id'] for chunk in doc_chunks_sorted[:chunks_per_document]]
            vector_ids_to_fetch.extend(top_chunk_ids)
        
        print(f'[SMART SEARCH+RETRIEVE] Fetching {len(vector_ids_to_fetch)} chunks from {len(ranked_docs)} documents')
        
        # Retrieve full vectors
        detail_result = pinecone_get_vector_details(
            vector_ids=vector_ids_to_fetch,
            namespace=namespace,
            include_full_text=True,
            _user_id=_user_id,
            **kwargs
        )
        
        if not detail_result.get('success'):
            return detail_result  # Pass through error
        
        # PHASE 4: Organize results by document
        retrieved_vectors = detail_result['vectors']
        
        documents_organized = []
        
        for doc_name, doc_data in ranked_docs:
            # Find chunks for this document
            doc_chunks = [
                vec for vec in retrieved_vectors
                if vec['document_name'] == doc_name
            ]
            
            if doc_chunks:
                documents_organized.append({
                    "document_name": doc_name,
                    "relevance_score": round(doc_data['best_score'], 4),
                    "category": doc_data['category'],
                    "subcategory": doc_data.get('subcategory', ''),
                    "tags": doc_data.get('tags', []),
                    "total_chunks_in_document": doc_data.get('chunk_count', 0),
                    "chunks_retrieved": len(doc_chunks),
                    "chunks": [
                        {
                            "chunk_index": chunk['chunk_info']['index'],
                            "text": chunk['full_text'],
                            "vector_id": chunk['id']
                        }
                        for chunk in sorted(doc_chunks, key=lambda x: x['chunk_info']['index'])
                    ],
                    "metadata": doc_chunks[0]['metadata'] if doc_chunks else {}
                })
        
        print(f'[SMART SEARCH+RETRIEVE] Success: Retrieved {len(documents_organized)} documents with {len(retrieved_vectors)} chunks')
        
        return {
            "success": True,
            "query": query_text,
            "search_phase": {
                "total_chunks_found": summary_result['results_count'],
                "unique_documents": len(doc_groups),
                "top_documents": top_doc_names
            },
            "retrieval_phase": {
                "documents_retrieved": len(documents_organized),
                "chunks_retrieved": len(retrieved_vectors),
                "total_text_length": detail_result['total_text_length']
            },
            "documents": documents_organized
        }
        
    except Exception as e:
        print(f'[SMART SEARCH+RETRIEVE] Error: {e}')
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }


print('[PINECONE TOOLS] Module loaded (13 functions: 10 original + 3 smart search tools)')
