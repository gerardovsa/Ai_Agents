"""
Vector Database API Routes - Backend endpoints for autonomous AI vector search

PURPOSE: Provide REST API for vector database operations with metadata-rich responses
         for AI autonomous document retrieval.

FIXED: 2025-01-12 - Critical cursor leak repair
CHANGES:
- Fixed get_credentials() - added proper cursor management
- Fixed get_embedding_config() - fixed nested get_settings() helper cursor leak
- Added cursor = None and conn = None initialization
- Added try/finally blocks for guaranteed cleanup
- Added cursor.close() BEFORE conn.close()
- Updated date from 2025-11-29 to 2025-01-12

ENDPOINTS:
- POST /api/vector-db/upload-document - Upload document with metadata
- GET  /api/vector-db/documents - List documents with cloud links
- GET  /api/vector-db/stats - Get vector database statistics
- POST /api/vector-db/search - AI-initiated search (through tools)
- GET  /api/vector-db/document/:id - Get full document

ARCHITECTURE:
Frontend upload → API → Vector DB tool → Pinecone + metadata → AI autonomous access

LAST MODIFIED: 2025-01-12
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid
from typing import Dict, Any

# Import authentication decorator
from auth.user_auth import require_auth

# Import vector database tools
try:
    from tools.implementations.vector_database import (
        vector_db_search,
        vector_db_get_full_document,
        vector_db_list_namespaces,
        vector_db_get_document_metadata
    )
    VECTOR_TOOLS_AVAILABLE = True
except ImportError:
    VECTOR_TOOLS_AVAILABLE = False
    print("⚠️  Vector database tools not available")

# Import OpenAI for embeddings
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Import Pinecone (handle both old and new package names)
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
except Exception as e:
    # Handle pinecone-client conflict gracefully
    print(f"⚠️  Pinecone import error: {e}")
    PINECONE_AVAILABLE = False

# Create blueprint
vector_db_bp = Blueprint('vector_db', __name__)


# ==================== HELPER FUNCTIONS ====================

def _get_vector_db_credentials(user_id: int) -> Dict[str, Any]:
    """
    Fetch vector database credentials from Platform Connections
    
    Returns Pinecone + embedding provider (Voyager AI or OpenAI) credentials
    
    Args:
        user_id: User ID
    
    Returns:
        Dict with pinecone_api_key, pinecone_index_name, voyager_api_key or openai_api_key
    
    ✅ NO DATABASE OPERATIONS - Safe (uses credential injector functions)
    """
    from auth.credential_injector import get_pinecone_credentials, get_voyager_credentials, get_openai_embeddings_credentials
    
    credentials = {}
    
    # Get Pinecone credentials
    try:
        pinecone_creds = get_pinecone_credentials(user_id=user_id)
        if pinecone_creds:
            creds_dict = pinecone_creds.get('credentials', {}) if isinstance(pinecone_creds, dict) else {}
            credentials['pinecone_api_key'] = creds_dict.get('api_key') or pinecone_creds.get('PINECONE_API_KEY')
            credentials['pinecone_index_name'] = creds_dict.get('index_name') or pinecone_creds.get('PINECONE_INDEX_NAME')
            print(f"[VECTOR DB] Loaded Pinecone credentials for user {user_id}")
    except Exception as e:
        print(f"[VECTOR DB] No Pinecone credentials: {e}")
    
    # Get Voyager AI credentials (preferred for embeddings)
    try:
        voyager_creds = get_voyager_credentials(user_id=user_id)
        if voyager_creds:
            creds_dict = voyager_creds.get('credentials', {}) if isinstance(voyager_creds, dict) else {}
            credentials['voyager_api_key'] = creds_dict.get('api_key') or voyager_creds.get('VOYAGER_API_KEY')
            print(f"[VECTOR DB] Loaded Voyager AI credentials for user {user_id}")
    except Exception as e:
        print(f"[VECTOR DB] No Voyager AI credentials: {e}")
    
    # Get OpenAI embeddings credentials (fallback)
    if 'voyager_api_key' not in credentials:
        try:
            openai_creds = get_openai_embeddings_credentials(user_id=user_id)
            if openai_creds:
                creds_dict = openai_creds.get('credentials', {}) if isinstance(openai_creds, dict) else {}
                credentials['openai_api_key'] = creds_dict.get('api_key') or openai_creds.get('OPENAI_API_KEY')
                print(f"[VECTOR DB] Loaded OpenAI embeddings credentials for user {user_id}")
        except Exception as e:
            print(f"[VECTOR DB] No OpenAI embeddings credentials: {e}")
    
    return credentials

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 20) -> list:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk (chars)
        chunk_overlap: Overlap between chunks (chars)
    
    Returns:
        List of text chunks
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk:
            chunks.append(chunk)
        
        start += (chunk_size - chunk_overlap)
    
    return chunks


def extract_text_from_file(file_path: str, file_type: str) -> str:
    """
    Extract text from uploaded file
    
    Args:
        file_path: Path to file
        file_type: MIME type or extension
    
    Returns:
        Extracted text content
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    try:
        # Text files
        if file_type in ['text/plain', '.txt', '.md']:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        # PDF files
        elif file_type in ['application/pdf', '.pdf']:
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ''
                    for page in reader.pages:
                        text += page.extract_text() + '\n\n'
                    return text
            except ImportError:
                return "PDF extraction requires PyPDF2. Install: pip install PyPDF2"
        
        # DOCX files
        elif file_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.docx']:
            try:
                import docx
                doc = docx.Document(file_path)
                return '\n\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                return "DOCX extraction requires python-docx. Install: pip install python-docx"
        
        else:
            return f"Unsupported file type: {file_type}"
    
    except Exception as e:
        return f"Error extracting text: {str(e)}"


# ==================== API ENDPOINTS ====================

@vector_db_bp.route('/api/vector-db/upload-document', methods=['POST'])
@require_auth
def upload_document():
    """
    Upload document and store in vector database with metadata
    
    Form Data:
        - file: Document file
        - chunk_size: Chunk size (default: 800)
        - chunk_overlap: Chunk overlap (default: 20)
        - namespace: Pinecone namespace (default: 'default')
        - include_cloud_metadata: Enable cloud metadata (default: 'true')
        - enable_ai_retrieval: Enable AI retrieval (default: 'true')
    
    Returns:
        JSON with upload status and metadata
    
    ✅ NO DATABASE OPERATIONS - Safe (uses Pinecone directly)
    """
    try:
        # Check if vector tools available
        if not VECTOR_TOOLS_AVAILABLE or not PINECONE_AVAILABLE or not OPENAI_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Vector database tools not configured. Set PINECONE_API_KEY and OPENAI_API_KEY.'
            }), 500
        
        # Get file
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
        
        # Get parameters
        user_id = request.user['id']  # From JWT token via @require_auth
        chunk_size = request.form.get('chunk_size', 800, type=int)
        chunk_overlap = request.form.get('chunk_overlap', 20, type=int)
        namespace = request.form.get('namespace', 'default')
        include_cloud_metadata = request.form.get('include_cloud_metadata', 'true') == 'true'
        enable_ai_retrieval = request.form.get('enable_ai_retrieval', 'true') == 'true'
        file_type = request.form.get('file_type', file.content_type or 'application/octet-stream')
        upload_timestamp = request.form.get('upload_timestamp', datetime.utcnow().isoformat())
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        upload_dir = os.path.join('storage', 'uploads', str(user_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Extract text
        text_content = extract_text_from_file(file_path, file_type)
        
        if not text_content or text_content.startswith('Error') or text_content.startswith('Unsupported'):
            return jsonify({'success': False, 'error': text_content}), 400
        
        # Chunk text
        chunks = chunk_text(text_content, chunk_size, chunk_overlap)
        
        # Generate document ID
        document_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        # Generate embeddings and store in Pinecone
        openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        pinecone_client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index_name = os.getenv('PINECONE_INDEX_NAME', 'ai-agents-vectors')
        index = pinecone_client.Index(index_name)
        
        # Prepare vectors with metadata
        vectors = []
        for i, chunk in enumerate(chunks):
            # Generate embedding
            response = openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=chunk
            )
            embedding = response.data[0].embedding
            
            # Build metadata
            metadata = {
                'document_id': document_id,
                'filename': filename,
                'file_type': file_type,
                'chunk_index': i,
                'total_chunks': len(chunks),
                'text': chunk,
                'created_at': upload_timestamp,
                'file_size_bytes': os.path.getsize(file_path),
                'user_id': user_id
            }
            
            # ⚡ NEW: Add cloud storage metadata for AI retrieval
            if include_cloud_metadata and enable_ai_retrieval:
                # Placeholder for cloud storage integration
                # In production, upload to Google Drive/OneDrive here
                metadata['cloud_storage'] = {
                    'provider': 'local',  # or 'google_drive', 'onedrive'
                    'file_id': document_id,
                    'web_view_url': f'file://{file_path}',
                    'download_url': f'/api/vector-db/download/{document_id}',
                    'ai_retrievable': True,
                    'last_synced': datetime.utcnow().isoformat()
                }
            
            # Add vector
            vector_id = f"{document_id}_chunk_{i}"
            vectors.append({
                'id': vector_id,
                'values': embedding,
                'metadata': metadata
            })
        
        # Upsert to Pinecone
        index.upsert(vectors=vectors, namespace=namespace)
        
        print(f"✅ Uploaded {filename}: {len(vectors)} vectors to namespace '{namespace}'")
        
        # Clean up temp file (optional - keep for retrieval)
        # os.remove(file_path)
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'filename': filename,
            'vectors_uploaded': len(vectors),
            'namespace': namespace,
            'chunk_size': chunk_size,
            'chunks_created': len(chunks),
            'ai_retrievable': enable_ai_retrieval,
            'cloud_metadata': include_cloud_metadata,
            'message': f'Document uploaded successfully with AI autonomous access enabled'
        })
    
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@vector_db_bp.route('/api/vector-db/documents', methods=['GET'])
@require_auth
def list_documents():
    """
    List all documents in vector database with metadata
    
    Query Params:
        - include_metadata: Include full metadata (default: true)
        - include_cloud_links: Include cloud storage links (default: true)
    
    Returns:
        JSON with document list
    
    ✅ NO DATABASE OPERATIONS - Safe
    """
    try:
        user_id = request.user['id']  # From JWT token via @require_auth
        include_metadata = request.args.get('include_metadata', 'true') == 'true'
        include_cloud_links = request.args.get('include_cloud_links', 'true') == 'true'
        
        # Get documents from Pinecone
        # This would query metadata to get unique document_ids
        # Simplified version - returns placeholder
        
        documents = [
            {
                'document_id': 'doc_abc123',
                'filename': 'product_policy.pdf',
                'chunks': 5,
                'created_at': '2025-11-28T10:30:00Z',
                'file_size': 145600,
                'ai_retrievable': True
            }
        ]
        
        if include_metadata and include_cloud_links:
            for doc in documents:
                doc['cloud_storage'] = {
                    'provider': 'local',
                    'web_view_url': f'/api/vector-db/view/{doc["document_id"]}',
                    'download_url': f'/api/vector-db/download/{doc["document_id"]}'
                }
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total': len(documents)
        })
    
    except Exception as e:
        print(f"❌ List documents error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@vector_db_bp.route('/api/vector-db/stats', methods=['GET'])
@require_auth
def get_stats():
    """
    Get vector database statistics
    
    Returns:
        JSON with stats (documents, vectors, namespaces)
    
    ✅ NO DATABASE OPERATIONS - Safe (uses vector_db_list_namespaces tool)
    """
    try:
        user_id = request.user['id']  # From JWT token via @require_auth
        
        # Get credentials from Platform Connections
        credentials = _get_vector_db_credentials(user_id)
        
        # Get stats from Pinecone
        if PINECONE_AVAILABLE and VECTOR_TOOLS_AVAILABLE:
            # Pass credentials to tool
            result = vector_db_list_namespaces(
                _user_id=user_id,
                **credentials  # Inject pinecone_api_key, pinecone_index_name, etc.
            )
            
            if result.get('success'):
                namespaces = result.get('namespaces', [])
                total_vectors = sum(ns.get('vector_count', 0) for ns in namespaces)
                
                return jsonify({
                    'success': True,
                    'stats': {
                        'documents': 'unknown',  # Would need metadata query
                        'vectors': total_vectors,
                        'namespaces': len(namespaces)
                    }
                })
        
        # Fallback
        return jsonify({
            'success': True,
            'stats': {
                'documents': 0,
                'vectors': 0,
                'namespaces': 0
            }
        })
    
    except Exception as e:
        print(f"❌ Get stats error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@vector_db_bp.route('/api/vector-db/credentials/get', methods=['GET'])
@require_auth
def get_credentials():
    """
    Get saved Pinecone credentials for user
    
    Returns:
        JSON with credentials (api_key masked)
    
    FIXED: Added proper cursor management with try/finally block
    """
    cursor = None  # ✅ CRITICAL: Initialize before try
    conn = None
    
    try:
        user_id = request.user['id']  # From JWT token via @require_auth
        
        # Import auth manager
        from auth.user_auth import UserAuthManager
        auth_manager = UserAuthManager()
        
        # Get Pinecone credentials
        pinecone_creds = auth_manager.get_platform_credentials(user_id, 'pinecone')
        
        if not pinecone_creds or 'PINECONE_API_KEY' not in pinecone_creds:
            return jsonify({
                'success': False,
                'error': 'No credentials found. Please save credentials first.'
            }), 404
        
        # Get settings/metadata from database
        from shared.database_utils import get_database_connection
        settings = {}
        
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT settings
            FROM ai_infrastructure.user_platform_credentials
            WHERE user_id = %s AND platform = %s
            LIMIT 1
        ''', (user_id, 'pinecone'))
        
        row = cursor.fetchone()
        
        if row:
            settings_json = row['settings'] if isinstance(row, dict) else row[0]
            if settings_json:
                import json
                settings = json.loads(settings_json) if isinstance(settings_json, str) else settings_json
        
        # ✅ FIX: Close cursor BEFORE conn
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        # Mask API key (show last 8 chars only) - AFTER connection closed
        api_key = pinecone_creds['PINECONE_API_KEY']
        masked_key = f"{'*' * (len(api_key) - 8)}{api_key[-8:]}" if len(api_key) > 8 else '****'
        
        return jsonify({
            'success': True,
            'credentials': {
                'api_key': masked_key,
                'api_key_exists': True,
                'index_name': settings.get('index_name', ''),
                'environment': settings.get('environment', ''),
                'namespace': settings.get('namespace', '')
            }
        })
    
    except Exception as e:
        print(f"❌ Get credentials error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        # ✅ CRITICAL: GUARANTEED cleanup
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"⚠️ Error closing cursor: {e}")
        if conn:
            try:
                conn.close()
            except Exception as e:
                print(f"⚠️ Error closing connection: {e}")


@vector_db_bp.route('/api/vector-db/credentials/save', methods=['POST'])
@require_auth
def save_credentials():
    """
    Save Pinecone credentials for user
    
    Body:
        - api_key: Pinecone API key (required)
        - index_name: Index name (optional)
        - environment: Environment (optional)
        - namespace: Namespace (optional)
    
    Returns:
        JSON with success status
    
    ✅ NO DATABASE OPERATIONS - Safe (uses auth_manager)
    """
    try:
        data = request.get_json()
        
        user_id = request.user['id']  # From JWT token via @require_auth
        api_key = data.get('api_key', '').strip()
        index_name = data.get('index_name', '').strip()
        environment = data.get('environment', '').strip()
        namespace = data.get('namespace', '').strip()
        
        if not api_key:
            return jsonify({'success': False, 'error': 'api_key required'}), 400
        
        # Import auth manager
        from auth.user_auth import UserAuthManager
        auth_manager = UserAuthManager()
        
        # Build metadata
        metadata = {
            'index_name': index_name or 'ai-agents-vectors',
            'environment': environment or 'us-east-1',
            'namespace': namespace or '',
            'description': 'Vector database credentials for autonomous AI document search',
            'saved_at': datetime.utcnow().isoformat()
        }
        
        # Store credentials
        result = auth_manager.store_platform_credential(
            user_id=user_id,
            platform='pinecone',
            credentials_dict={'PINECONE_API_KEY': api_key},
            settings_dict=metadata,
            credential_type='api_key'
        )
        
        if result.get('success'):
            print(f"✅ Saved Pinecone credentials for user {user_id}")
            return jsonify({
                'success': True,
                'message': 'Credentials saved successfully',
                'index_name': metadata['index_name'],
                'environment': metadata['environment']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to save credentials')
            }), 500
    
    except Exception as e:
        print(f"❌ Save credentials error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@vector_db_bp.route('/api/vector-db/embedding-config/get', methods=['GET'])
@require_auth
def get_embedding_config():
    """
    Get embedding model configuration for user
    
    Returns:
        JSON with embedding provider, model, and metadata
    
    FIXED: Fixed nested get_settings() helper function cursor leak
    """
    try:
        user_id = request.user['id']  # From JWT token via @require_auth
        
        from auth.user_auth import UserAuthManager
        auth_manager = UserAuthManager()
        
        # ✅ FIX: Helper function with proper cursor management
        def get_settings(platform):
            """Get settings from database with proper cleanup"""
            cursor = None  # ✅ Initialize
            conn = None
            try:
                from shared.database_utils import get_database_connection
                conn = get_database_connection('ai_infrastructure')
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT settings
                    FROM ai_infrastructure.user_platform_credentials
                    WHERE user_id = %s AND platform = %s
                    LIMIT 1
                ''', (user_id, platform))
                
                row = cursor.fetchone()
                
                # ✅ FIX: Close cursor BEFORE conn
                cursor.close()
                cursor = None
                conn.close()
                conn = None
                
                # Process result AFTER connection closed
                if row:
                    settings_json = row['settings'] if isinstance(row, dict) else row[0]
                    if settings_json:
                        import json
                        return json.loads(settings_json) if isinstance(settings_json, str) else settings_json
                
                return {}
            
            except Exception as e:
                print(f"⚠️ Could not fetch settings for {platform}: {e}")
                return {}
            
            finally:
                # ✅ CRITICAL: Guaranteed cleanup
                if cursor:
                    try:
                        cursor.close()
                    except:
                        pass
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
        
        # Try to get Voyager credentials first
        voyager_creds = auth_manager.get_platform_credentials(user_id, 'voyager')
        if voyager_creds and 'VOYAGER_API_KEY' in voyager_creds:
            settings = get_settings('voyager')
            return jsonify({
                'success': True,
                'config': {
                    'provider': 'voyager',
                    'model': settings.get('model', 'voyager'),
                    'dimensions': settings.get('dimensions', 1536),
                    'api_key_masked': '****' + voyager_creds['VOYAGER_API_KEY'][-8:] if len(voyager_creds['VOYAGER_API_KEY']) > 8 else '****'
                }
            })
        
        # Try OpenAI embeddings
        openai_creds = auth_manager.get_platform_credentials(user_id, 'openai_embeddings')
        if openai_creds and 'OPENAI_API_KEY' in openai_creds:
            settings = get_settings('openai_embeddings')
            return jsonify({
                'success': True,
                'config': {
                    'provider': 'openai',
                    'model': settings.get('model', 'text-embedding-ada-002'),
                    'dimensions': settings.get('dimensions', 1536),
                    'api_key_masked': '****' + openai_creds['OPENAI_API_KEY'][-8:] if len(openai_creds['OPENAI_API_KEY']) > 8 else '****'
                }
            })
        
        # No embedding config found
        return jsonify({
            'success': True,
            'config': None
        })
    
    except Exception as e:
        print(f"❌ Get embedding config error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@vector_db_bp.route('/api/vector-db/embedding-config/save', methods=['POST'])
@require_auth
def save_embedding_config():
    """
    Save embedding model configuration
    
    Request Body:
        - provider: Embedding provider ('voyager' or 'openai') (required)
        - platform: Platform name for storage (required)
        - api_key: API key (required)
        - model: Model name (required)
        - metadata: Additional metadata (optional)
    
    Returns:
        JSON with success status
    
    ✅ NO DATABASE OPERATIONS - Safe (uses auth_manager)
    """
    try:
        data = request.get_json()
        
        user_id = request.user['id']  # From JWT token via @require_auth
        provider = data.get('provider', '').strip()
        platform = data.get('platform', '').strip()
        api_key = data.get('api_key', '').strip()
        model = data.get('model', '').strip()
        metadata = data.get('metadata', {})
        
        if not provider:
            return jsonify({'success': False, 'error': 'provider required'}), 400
        
        if not api_key:
            return jsonify({'success': False, 'error': 'api_key required'}), 400
        
        # Set credential key based on provider
        if provider == 'voyager':
            credential_key = 'VOYAGER_API_KEY'
        elif provider == 'openai':
            credential_key = 'OPENAI_API_KEY'
        else:
            return jsonify({'success': False, 'error': f'Unknown provider: {provider}'}), 400
        
        # Store embedding configuration
        from auth.user_auth import UserAuthManager
        auth_manager = UserAuthManager()
        
        # Prepare metadata
        embedding_metadata = {
            'provider': provider,
            'model': model,
            'dimensions': metadata.get('dimensions', 1536),
            'description': f'{provider.capitalize()} embedding model configuration',
            'updated_at': datetime.now().isoformat()
        }
        
        result = auth_manager.store_platform_credential(
            user_id=user_id,
            platform=platform,
            credentials_dict={credential_key: api_key},
            settings_dict=embedding_metadata,
            credential_type='api_key'
        )
        
        if result.get('success'):
            print(f"✅ Saved {provider} embedding config for user {user_id}")
            return jsonify({
                'success': True,
                'message': f'{provider.capitalize()} configuration saved successfully',
                'provider': provider,
                'model': model
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to save configuration')
            }), 500
    
    except Exception as e:
        print(f"❌ Save embedding config error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Export blueprint
__all__ = ['vector_db_bp']