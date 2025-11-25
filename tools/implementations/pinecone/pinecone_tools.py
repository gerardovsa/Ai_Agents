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

# Add paths
tools_dir = Path(__file__).parent.parent.parent
if str(tools_dir) not in sys.path:
    sys.path.insert(0, str(tools_dir))

from AI_infrastructure.auth.user_auth import UserAuthManager


class PineconeToolsError(Exception):
    """Custom exception for Pinecone tools"""
    pass


def _get_pinecone_client(user_id: int, **kwargs):
    """Get authenticated Pinecone client (NEW JSONB FORMAT)"""
    try:
        from pinecone import Pinecone
        
        # Get credentials from JSONB column
        auth_manager = UserAuthManager()
        creds = auth_manager.get_platform_credentials(user_id, 'pinecone')
        
        if not creds or 'api_key' not in creds:
            raise PineconeToolsError("Pinecone credentials not found. Please configure in Vector DB sidebar.")
        
        # JSONB credentials format:
        # {'api_key': 'pcsk_...', 'index_name': 'inhouseprint', 'environment': 'us-east-1', 'namespace': ''}
        api_key = creds['api_key']
        index_name = creds.get('index_name')
        environment = creds.get('environment', 'us-east-1')
        namespace = creds.get('namespace', '')
        
        if not index_name:
            raise PineconeToolsError("Index name not configured")
        
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
    """Generate embeddings using OpenAI (NEW JSONB FORMAT)"""
    try:
        import openai
        
        # Get OpenAI credentials from JSONB column
        auth_manager = UserAuthManager()
        creds = auth_manager.get_platform_credentials(user_id, 'openai_embeddings')
        
        if not creds or 'api_key' not in creds:
            raise PineconeToolsError("OpenAI embeddings credentials not found. Please configure in Vector DB sidebar.")
        
        # JSONB credentials format:
        # {'api_key': 'sk-proj-...', 'model': 'text-embedding-ada-002', 'dimensions': 1536}
        api_key = creds['api_key']
        model = creds.get('model', 'text-embedding-ada-002')
        
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
        print(f'[PINECONE] Embedding generation error: {e}')
        raise PineconeToolsError(f"Failed to generate embeddings: {str(e)}")


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
        
        # Execute query
        results = index.query(
            vector=query_vector,
            top_k=min(top_k, 100),
            namespace=namespace,
            filter=filter,
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
            index.upsert(vectors=batch, namespace=namespace)
            total_upserted += len(batch)
            print(f'[PINECONE] Upserted batch {i//batch_size + 1}: {len(batch)} vectors')
        
        return {
            'success': True,
            'upserted_count': total_upserted,
            'namespace': namespace
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
        
        if delete_all:
            if not namespace:
                raise PineconeToolsError("namespace required when delete_all=True")
            index.delete(delete_all=True, namespace=namespace)
            print(f'[PINECONE] Deleted all vectors in namespace: {namespace}')
        elif filter:
            index.delete(filter=filter, namespace=namespace)
            print(f'[PINECONE] Deleted vectors matching filter')
        else:
            index.delete(ids=ids, namespace=namespace)
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
        
        results = index.fetch(ids=ids, namespace=namespace)
        
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
        
        update_dict = {'id': id}
        if values:
            update_dict['values'] = values
        if metadata:
            update_dict['set_metadata'] = metadata
        
        index.update(**update_dict, namespace=namespace)
        
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
    **kwargs
) -> Dict[str, Any]:
    """
    Upload and process document into vector database
    
    Handles: PDF, TXT, MD, DOCX
    Pipeline: Extract text → Chunk → Embed → Upsert to Pinecone
    
    Args:
        file_path: Path to document file
        filename: Original filename
        chunk_size: Text chunk size (default: 800)
        chunk_overlap: Chunk overlap (default: 20)
        namespace: Target namespace (default: filename)
        **kwargs: Credential injection
    
    Returns:
        Upload result with vector count
    """
    try:
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
        
        # Generate embeddings for chunks
        vectors = []
        doc_id = hashlib.md5(filename.encode()).hexdigest()[:8]
        
        # Batch embedding generation (500 at a time)
        batch_size = 500
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]
            
            for j, chunk in enumerate(batch_chunks):
                chunk_id = f"{doc_id}_chunk_{i+j}"
                embedding = _get_openai_embeddings(chunk, user_id)
                
                vectors.append({
                    'id': chunk_id,
                    'values': embedding,
                    'metadata': {
                        'text': chunk,
                        'document': filename,
                        'document_id': doc_id,
                        'chunk_index': i+j,
                        'chunk_size': len(chunk)
                    }
                })
            
            print(f'[VECTOR DB] Embedded batch {i//batch_size + 1}: {len(batch_chunks)} chunks')
        
        # Upsert to Pinecone
        target_namespace = namespace or filename
        upsert_result = pinecone_upsert_vectors(
            vectors=vectors,
            namespace=target_namespace,
            **kwargs
        )
        
        if not upsert_result.get('success'):
            raise PineconeToolsError(upsert_result.get('error', 'Upsert failed'))
        
        print(f'[VECTOR DB] Successfully uploaded {len(vectors)} vectors to namespace: {target_namespace}')
        
        return {
            'success': True,
            'vectors_uploaded': len(vectors),
            'document_id': doc_id,
            'namespace': target_namespace,
            'filename': filename
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


print('[PINECONE TOOLS] Module loaded (8 functions)')
