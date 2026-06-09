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

from flask import Blueprint, request, jsonify, g
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid
from typing import Dict, Any

# Import authentication decorator
from auth.user_auth import require_auth
from AI_infrastructure.shared.org_credentials_loader import resolve_credentials

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

# Import pgvector tools
try:
    from tools.implementations.pgvector.pgvector_tools import (
        pgvector_upload_document as _pgvec_upload,
        pgvector_list_documents  as _pgvec_list,
        pgvector_query_vectors   as _pgvec_query,
        pgvector_delete_vectors  as _pgvec_delete,
        pgvector_describe_stats  as _pgvec_stats,
    )
    PGVECTOR_TOOLS_AVAILABLE = True
except ImportError:
    PGVECTOR_TOOLS_AVAILABLE = False
    print("⚠️  pgvector tools not available")


def _get_vector_provider(user_id: int) -> str:
    """
    Return the active vector provider for *user_id*'s org.

    Resolution order:
      0. GAP-V9: If the user's org is a personal org (is_personal_org=TRUE) →
         always 'pgvector'. No Pinecone credential lookup is performed — personal
         orgs never have Pinecone configured, so the lookup is a no-op and this
         short-circuit avoids the extra DB round-trip.
      1. If the org has a 'pinecone' credential in the vault → 'pinecone'
      2. If the org has NO pinecone credential but pgvector is available → 'pgvector'
      3. Default → 'pinecone' (backward-compat; caller must handle missing creds)
    """
    # GAP-V9: short-circuit for Solo / personal-org users
    if PGVECTOR_TOOLS_AVAILABLE:
        try:
            from AI_infrastructure.shared.database_utils import execute_query
            row = execute_query(
                """SELECT o.is_personal_org
                   FROM ai_infrastructure.organisations o
                   JOIN ai_infrastructure.users u ON u.organisation_id = o.id
                   WHERE u.id = %s""",
                (user_id,),
                fetch_mode='one'
            )
            if row and row.get('is_personal_org'):
                return 'pgvector'
        except Exception:
            pass  # Non-fatal — fall through to normal resolution

    pin_cred = resolve_credentials(user_id, 'pinecone')
    if pin_cred and (
        pin_cred.get('api_key')
        or pin_cred.get('credential_value')
        or (pin_cred.get('credentials') or {}).get('api_key')
    ):
        return 'pinecone'
    # Default to pgvector — it is the free built-in provider.
    # Never default to 'pinecone' when no credential exists; that would
    # trigger Pinecone/OpenAI client initialisation and crash on httpx incompatibility.
    return 'pgvector'


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
    
    NOTE: Uses shared business-level credentials (user_id=1) for vector database access.
          All users share the same Pinecone index with namespace separation.
    
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
        user_id = g.rls_user_id

        # Respect the provider explicitly selected in the UI (sent as form field).
        # Fall back to auto-detection only when the form field is absent or invalid.
        # This prevents the org-vault Pinecone key (e.g. InHouse Print) from
        # overriding a user's deliberate selection of pgvector.
        _requested = request.form.get('provider', '').strip().lower()
        provider = _requested if _requested in ('pgvector', 'pinecone', 'qdrant') else _get_vector_provider(user_id)

        # Embedding provider explicitly chosen in the UI.
        # 'local' skips the org-vault lookup so an invalid credential never causes a 500.
        _emb_prov = request.form.get('embedding_provider', '').strip().lower()
        embedding_provider = _emb_prov if _emb_prov in ('local', 'voyager', 'openai') else None

        # Get file
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Empty filename'}), 400
        
        owner_user_id = g.rls_user_id
        visibility = request.form.get('visibility', 'org')  # private, org, global
        team_id = request.form.get('team_id', type=int)  # For team visibility
        
        chunk_size = request.form.get('chunk_size', 800, type=int)
        chunk_overlap = request.form.get('chunk_overlap', 100, type=int)
        namespace = request.form.get('namespace', '')
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

        # ── pgvector provider path ────────────────────────────────────────
        if provider == 'pgvector' and PGVECTOR_TOOLS_AVAILABLE:
            file_size = os.path.getsize(file_path)
            pg_result = _pgvec_upload(
                text_content=text_content,
                filename=filename,
                file_type=file_type,
                file_size_bytes=file_size,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                visibility=visibility,
                document_id=document_id,
                embedding_provider=embedding_provider,
                _user_id=user_id,
            )
            if not pg_result.get('success'):
                return jsonify({'success': False, 'error': pg_result.get('error', 'pgvector upload failed')}), 500
            return jsonify({
                'success':          True,
                'document_id':      document_id,
                'filename':         filename,
                'vectors_uploaded': pg_result.get('vectors_uploaded', 0),
                'chunks_created':   pg_result.get('chunks_created', len(chunks)),
                'provider':         'pgvector',
                'ai_retrievable':   enable_ai_retrieval,
                'message':          'Document uploaded to pgvector store successfully',
            })
        # ── End pgvector path ─────────────────────────────────────────────

        # Resolve credentials via org vault (GAP-V2)
        pin_cred = resolve_credentials(user_id, 'pinecone')
        if not pin_cred:
            return jsonify({
                'success': False,
                'error': 'Pinecone credentials not configured. Add Pinecone in Organisation Settings > Connections.'
            }), 503

        emb_cred = (
            resolve_credentials(user_id, 'openai_embeddings')
            or resolve_credentials(user_id, 'openai')
        )
        if not emb_cred:
            return jsonify({
                'success': False,
                'error': 'Embedding credentials not configured. Add OpenAI or Voyager credentials in Organisation Settings > Connections.'
            }), 503

        pin_api_key = pin_cred.get('api_key') or pin_cred.get('credential_value') or (pin_cred.get('credentials') or {}).get('api_key')
        pin_index_name = (pin_cred.get('credentials') or {}).get('index_name') or pin_cred.get('index_name') or os.getenv('PINECONE_INDEX_NAME', 'ai-agents-vectors')
        _emb_creds_detail = emb_cred.get('credentials') or {}
        emb_api_key = emb_cred.get('api_key') or emb_cred.get('credential_value') or _emb_creds_detail.get('api_key')
        emb_provider = _emb_creds_detail.get('provider', 'openai')
        emb_model = _emb_creds_detail.get('model', 'text-embedding-3-small')

        # Derive org-scoped namespace for tenant isolation (GAP-V4)
        if not namespace:
            try:
                from AI_infrastructure.shared.database_utils import execute_query
                org_row = execute_query(
                    "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                    (user_id,), fetch_mode='one'
                )
                org_id = org_row['organisation_id'] if org_row and org_row.get('organisation_id') else None
                namespace = f"org_{org_id}" if org_id else f"user_{user_id}"
            except Exception:
                namespace = f"user_{user_id}"

        # Build provider-aware embedding helper so we don't repeat logic in the loop
        def _generate_embedding(text: str) -> list:
            if emb_provider == 'voyager':
                import requests as _requests
                resp = _requests.post(
                    'https://api.voyageai.com/v1/embeddings',
                    headers={'Authorization': f'Bearer {emb_api_key}', 'Content-Type': 'application/json'},
                    json={'input': [text], 'model': emb_model},
                    timeout=30
                )
                resp.raise_for_status()
                return resp.json()['data'][0]['embedding']
            else:
                _oc = OpenAI(api_key=emb_api_key)
                _resp = _oc.embeddings.create(model=emb_model, input=text)
                return _resp.data[0].embedding

        pinecone_client = Pinecone(api_key=pin_api_key)
        index = pinecone_client.Index(pin_index_name)

        # Prepare vectors with metadata
        vectors = []
        for i, chunk in enumerate(chunks):
            # Generate embedding using configured provider + model
            embedding = _generate_embedding(chunk)
            
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
                'user_id': user_id,  # Authenticated user ID
                
                # ⚡ ACCESS CONTROL METADATA
                'owner_user_id': owner_user_id,  # Who uploaded it
                'visibility': visibility,  # private, team, global
                'team_id': team_id if visibility == 'team' else None,
                'is_public': visibility == 'global'
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
        user_id = g.rls_user_id
        include_metadata = request.args.get('include_metadata', 'true') == 'true'
        include_cloud_links = request.args.get('include_cloud_links', 'true') == 'true'

        documents = []

        # ── pgvector provider path ────────────────────────────────────────
        provider = _get_vector_provider(user_id)
        if provider == 'pgvector' and PGVECTOR_TOOLS_AVAILABLE:
            pg_result = _pgvec_list(_user_id=user_id)
            if pg_result.get('success'):
                documents = pg_result.get('documents', [])
        elif PINECONE_AVAILABLE:
            pin_cred = resolve_credentials(user_id, 'pinecone')
            if pin_cred:
                pin_api_key = (
                    pin_cred.get('api_key')
                    or pin_cred.get('credential_value')
                    or (pin_cred.get('credentials') or {}).get('api_key')
                )
                pin_index_name = (
                    (pin_cred.get('credentials') or {}).get('index_name')
                    or os.getenv('PINECONE_INDEX_NAME', 'ai-agents-vectors')
                )

                # Derive org namespace (same logic as upload_document)
                try:
                    from AI_infrastructure.shared.database_utils import execute_query as _eq
                    org_row = _eq(
                        "SELECT organisation_id FROM ai_infrastructure.users WHERE id = %s",
                        (user_id,), fetch_mode='one'
                    )
                    org_id = org_row['organisation_id'] if org_row and org_row.get('organisation_id') else None
                    namespace = f"org_{org_id}" if org_id else f"user_{user_id}"
                except Exception:
                    namespace = f"user_{user_id}"

                try:
                    pc = Pinecone(api_key=pin_api_key)
                    index = pc.Index(pin_index_name)

                    # Use list() to page through all vector IDs in this org's namespace,
                    # then collect unique document_ids from the IDs (pattern: doc_XXXX_chunk_N)
                    # and fetch a sample vector per doc to get filename from metadata.
                    seen_docs: dict = {}  # document_id -> metadata dict

                    try:
                        for id_batch in index.list(namespace=namespace, limit=1000):
                            # id_batch may be a list of strings or Pinecone ID objects
                            ids = [v if isinstance(v, str) else v.id for v in id_batch]  # type: ignore

                            # Fetch metadata for these IDs (up to 100 at a time)
                            fetch_ids = [i for i in ids if i.rsplit('_chunk_', 1)[0] not in seen_docs][:100]
                            if not fetch_ids:
                                continue
                            fetch_result = index.fetch(ids=fetch_ids, namespace=namespace)
                            vectors_map = fetch_result.get('vectors') or getattr(fetch_result, 'vectors', {})
                            for vid, vec in vectors_map.items():
                                meta = (vec.get('metadata') if isinstance(vec, dict) else getattr(vec, 'metadata', {})) or {}
                                doc_id = meta.get('document_id', vid.rsplit('_chunk_', 1)[0])
                                if doc_id not in seen_docs:
                                    seen_docs[doc_id] = {
                                        'document_id': doc_id,
                                        'filename': meta.get('filename', 'unknown'),
                                        'chunks': meta.get('total_chunks', 1),
                                        'created_at': meta.get('created_at', ''),
                                        'file_size': meta.get('file_size_bytes', 0),
                                        'ai_retrievable': True,
                                    }
                    except Exception as list_err:
                        print(f"⚠️  Pinecone list() not supported, falling back to describe_index_stats: {list_err}")
                        # Fallback: just report vector count for org namespace
                        stats = index.describe_index_stats()
                        ns_stats = (stats.get('namespaces') or getattr(stats, 'namespaces', {})) or {}
                        ns_info = ns_stats.get(namespace) or {}
                        total_vectors = (ns_info.get('vector_count') if isinstance(ns_info, dict) else getattr(ns_info, 'vector_count', 0)) or 0
                        if total_vectors > 0:
                            seen_docs['_unknown_'] = {
                                'document_id': '_unknown_',
                                'filename': f'{total_vectors} vectors (metadata unavailable)',
                                'chunks': total_vectors,
                                'created_at': '',
                                'file_size': 0,
                                'ai_retrievable': True,
                            }

                    documents = list(seen_docs.values())

                except Exception as pc_err:
                    print(f"⚠️  Pinecone list_documents error: {pc_err}")

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
    Get vector database statistics (filtered by visibility)
    
    Query params:
        - user_id: Current user ID for filtering (optional, defaults to 1)
        - username: Current user's username/team_id for filtering (optional)
    
    Returns:
        JSON with stats (documents, vectors, namespaces)
    
    ✅ NO DATABASE OPERATIONS - Safe (uses vector_db_list_namespaces tool)
    """
    try:
        user_id = g.rls_user_id

        # Wrap provider detection: a failure here must never propagate as 500.
        # Unknown / missing credentials always fall back to pgvector.
        try:
            provider = _get_vector_provider(user_id)
        except Exception as e:
            print(f'[VECTOR DB] _get_vector_provider error (defaulting to pgvector): {e}')
            provider = 'pgvector'

        # ── pgvector stats ───────────────────────────────────────────────
        # IMPORTANT: when provider is pgvector, ALWAYS return here.
        # Never fall through to the Pinecone path — that triggers httpx
        # client initialisation which fails with older openai+httpx combos.
        if provider == 'pgvector':
            if PGVECTOR_TOOLS_AVAILABLE:
                pg_result = _pgvec_stats(_user_id=user_id)
                s = pg_result.get('stats', {}) if pg_result.get('success') else {}
            else:
                s = {}
            return jsonify({
                'success': True,
                'stats': {
                    'documents':  s.get('documents', 0),
                    'vectors':    s.get('vectors', 0),
                    'namespaces': 1,
                    'provider':   'pgvector',
                }
            })

        # ── Pinecone stats ───────────────────────────────────────────────
        # Only reached when the org vault has a Pinecone credential.
        if PINECONE_AVAILABLE and VECTOR_TOOLS_AVAILABLE:
            result = vector_db_list_namespaces(_user_id=user_id)
            if result.get('success'):
                namespaces = result.get('namespaces', [])
                total_vectors = sum(ns.get('vector_count', 0) for ns in namespaces)
                return jsonify({
                    'success': True,
                    'stats': {
                        'documents':  'unknown',
                        'vectors':    total_vectors,
                        'namespaces': len(namespaces),
                        'provider':   'pinecone',
                    }
                })

        # Fallback
        return jsonify({
            'success': True,
            'stats': {'documents': 0, 'vectors': 0, 'namespaces': 0}
        })
    
    except Exception as e:
        print(f"❌ Get stats error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@vector_db_bp.route('/api/vector-db/credentials/load', methods=['GET'])
@require_auth
def load_credentials():
    """
    Load vector database credentials for business (user_id=1)
    
    NOTE: Uses shared business-level credentials. All users access the same credentials.
    
    Query params:
        - provider: 'pinecone', 'voyager', 'pgvector', 'qdrant' (optional, defaults to all)
    
    Returns:
        JSON with credentials (API keys masked for security)
    
    FIXED: Dec 9, 2025 - Updated to use actual schema (metadata + credentials columns)
    """
    # GAP-V5: Credentials now managed via Organisation Settings > Connections (org vault).
    # The Settings tab credential form in vector_database.html has been retired.
    return jsonify({
        'success': False,
        'error': 'This endpoint is no longer active. Manage vector database credentials in Organisation Settings > Connections.',
        'redirect': '/settings/organisation/connections'
    }), 410

    cursor = None
    conn = None
    
    try:
        user_id = g.rls_user_id
        provider = request.args.get('provider')  # Optional filter
        
        from shared.database_utils import get_database_connection
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Query using ACTUAL schema columns: metadata + credentials
        if provider:
            cursor.execute('''
                SELECT platform, metadata, credentials, is_active, updated_at
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s AND platform = %s AND is_active = true
                ORDER BY updated_at DESC
                LIMIT 1
            ''', (user_id, provider))
        else:
            # Load all vector DB providers (exclude embedding/SQL providers)
            cursor.execute('''
                SELECT platform, metadata, credentials, is_active, updated_at
                FROM ai_infrastructure.user_platform_credentials
                WHERE user_id = %s 
                  AND platform IN ('pinecone', 'voyager', 'pgvector', 'qdrant')
                  AND is_active = true
                ORDER BY platform, updated_at DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({
                'success': False,
                'error': f'No credentials found for {provider or "vector databases"}',
                'credentials': {}
            }), 404
        
        # Parse and mask credentials
        result = {}
        for row in rows:
            platform_name = row['platform'] if isinstance(row, dict) else row[0]
            metadata_json = row['metadata'] if isinstance(row, dict) else row[1]
            credentials_json = row['credentials'] if isinstance(row, dict) else row[2]
            
            # Parse JSON fields
            import json
            metadata = json.loads(metadata_json) if isinstance(metadata_json, str) else (metadata_json or {})
            credentials = json.loads(credentials_json) if isinstance(credentials_json, str) else (credentials_json or {})
            
            # Mask API key for security (show last 4 chars only)
            if 'api_key' in credentials and credentials['api_key']:
                api_key = credentials['api_key']
                credentials['api_key_masked'] = f"{'*' * (len(api_key) - 4)}{api_key[-4:]}" if len(api_key) > 4 else "****"
                del credentials['api_key']  # Don't send full key to frontend
            
            result[platform_name] = {
                **metadata,
                **credentials,
                'provider': platform_name
            }
        
        # ✅ Close cursor BEFORE conn
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
        return jsonify({
            'success': True,
            'credentials': result,
            'provider': provider if provider else 'all',
            'count': len(result)
        })
    
    except Exception as e:
        print(f"❌ Load credentials error: {str(e)}")
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


@vector_db_bp.route('/api/vector-db/credentials/status', methods=['GET'])
@require_auth
def check_connection_status():
    """
    Test connection to vector database provider
    
    NOTE: Uses shared business-level credentials (user_id=1).
    
    Query params:
        - provider: 'pinecone', 'voyager', 'pgvector', 'qdrant' (required)
    
    Returns:
        JSON with connection status and provider stats
    
    NEW: Dec 9, 2025 - Added connection testing endpoint
    """
    cursor = None
    conn = None

    try:
        user_id = g.rls_user_id
        provider = request.args.get('provider')

        if not provider:
            return jsonify({'success': False, 'error': 'provider parameter required'}), 400

        # Resolve credentials via org vault (GAP-V1/V2)
        cred = resolve_credentials(user_id, provider)

        if not cred:
            return jsonify({
                'success': False,
                'connected': False,
                'error': f'No credentials configured for {provider}. Add them in Organisation Settings > Connections.'
            }), 404

        credentials = cred.get('credentials') or {}
        if not credentials.get('api_key'):
            credentials['api_key'] = cred.get('api_key') or cred.get('credential_value')
        metadata = {}

        # Test connection based on provider
        if provider == 'pinecone':
            if not PINECONE_AVAILABLE:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'error': 'Pinecone library not installed'
                }), 500
            
            api_key = credentials.get('api_key')
            environment = credentials.get('environment') or metadata.get('environment')
            index_name = credentials.get('index_name') or metadata.get('index_name')
            
            if not api_key:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'error': 'API key not found in credentials'
                }), 400
            
            # Test Pinecone connection
            try:
                pc = Pinecone(api_key=api_key)
                index = pc.Index(index_name)
                stats = index.describe_index_stats()
                
                return jsonify({
                    'success': True,
                    'connected': True,
                    'provider': 'pinecone',
                    'index_name': index_name,
                    'environment': environment,
                    'stats': {
                        'total_vectors': stats.get('total_vector_count', 0),
                        'dimensions': stats.get('dimension', 0),
                        'namespaces': len(stats.get('namespaces', {}))
                    }
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'connected': False,
                    'error': f'Connection failed: {str(e)}'
                }), 500
        
        elif provider == 'voyager':
            # Voyager is embedding provider, not vector DB - just check API key exists
            api_key = credentials.get('api_key')
            return jsonify({
                'success': True,
                'connected': bool(api_key),
                'provider': 'voyager',
                'note': 'Voyager is embedding provider (not tested until first use)'
            })
        
        elif provider in ['pgvector', 'qdrant']:
            # Future: Add connection testing for these providers
            return jsonify({
                'success': True,
                'connected': False,
                'provider': provider,
                'note': f'{provider} connection testing not yet implemented'
            })
        
        else:
            return jsonify({
                'success': False,
                'error': f'Unknown provider: {provider}'
            }), 400
    
    except Exception as e:
        print(f"❌ Connection status error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
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


@vector_db_bp.route('/api/vector-db/credentials/save', methods=['POST'])
@require_auth
def save_credentials():
    """
    Save vector database credentials at business level (user_id=1)
    
    NOTE: Saves shared business-level credentials. All users will use these credentials.
    
    Body:
        - provider: 'pinecone', 'voyager', 'pgvector', 'qdrant' (required)
        - credentials: Object with provider-specific fields (required)
        - metadata: Object with additional config (optional)
    
    Example for Pinecone:
    {
      "provider": "pinecone",
      "credentials": {
        "api_key": "pcsk_...",
        "index_name": "my-index",
        "environment": "us-east-1"
      },
      "metadata": {
        "description": "Production vector database",
        "namespace": ""
      }
    }
    
    Returns:
        JSON with success status
    
    UPDATED: Dec 9, 2025 - Fixed to match actual schema
    """
    # GAP-V5: Credentials now managed via Organisation Settings > Connections (org vault).
    # The Settings tab credential form in vector_database.html has been retired.
    return jsonify({
        'success': False,
        'error': 'This endpoint is no longer active. Manage vector database credentials in Organisation Settings > Connections.',
        'redirect': '/settings/organisation/connections'
    }), 410

    cursor = None
    conn = None

    try:
        data = request.get_json()
        user_id = g.rls_user_id

        provider = data.get('provider', '').strip()
        credentials = data.get('credentials', {})
        metadata = data.get('metadata', {})
        
        if not provider or not credentials:
            return jsonify({'success': False, 'error': 'provider and credentials required'}), 400
        
        # Validate provider
        valid_providers = ['pinecone', 'voyager', 'pgvector', 'qdrant']
        if provider not in valid_providers:
            return jsonify({'success': False, 'error': f'Invalid provider. Must be one of: {valid_providers}'}), 400
        
        # Extract primary credential for backward compatibility
        credential_key = f'{provider.upper()}_API_KEY'
        credential_value = credentials.get('api_key') or credentials.get('connection_string') or ''
        
        from shared.database_utils import get_database_connection
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Upsert credentials (update if exists, insert if new)
        import json
        cursor.execute('''
            INSERT INTO ai_infrastructure.user_platform_credentials 
            (user_id, platform, credential_type, credential_key, credential_value, metadata, credentials, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (user_id, platform)
            DO UPDATE SET
                credential_value = EXCLUDED.credential_value,
                metadata = EXCLUDED.metadata,
                credentials = EXCLUDED.credentials,
                updated_at = NOW()
        ''', (
            user_id,
            provider,
            'api_key',
            credential_key,
            credential_value,
            json.dumps(metadata),
            json.dumps(credentials)
        ))
        
        conn.commit()
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        
        print(f"✅ Saved {provider} credentials for user {user_id}")
        return jsonify({
            'success': True,
            'message': f'{provider.title()} credentials saved successfully',
            'provider': provider
        })
    
    except Exception as e:
        if conn:
            try:
                conn.rollback()
            except:
                pass
        print(f"❌ Save credentials error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
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


@vector_db_bp.route('/api/vector-db/embedding-config/get', methods=['GET'])
@require_auth
def get_embedding_config():
    """
    Get embedding model configuration for business (user_id=1)
    
    NOTE: Uses shared business-level embedding config (Voyager AI or OpenAI).
    
    Returns:
        JSON with embedding provider, model, and metadata
    
    FIXED: Fixed nested get_settings() helper function cursor leak
    """
    try:
        user_id = g.rls_user_id

        # Resolve embedding credentials via org vault (GAP-V1/V2)
        voyager_cred = resolve_credentials(user_id, 'voyager')
        if voyager_cred:
            api_key = voyager_cred.get('api_key') or voyager_cred.get('credential_value') or ''
            creds_detail = voyager_cred.get('credentials') or {}
            return jsonify({
                'success': True,
                'config': {
                    'provider': 'voyager',
                    'model': creds_detail.get('model', 'voyage-large-2'),
                    'dimensions': creds_detail.get('dimensions', 1536),
                    'api_key_masked': f"{'*' * max(0, len(api_key) - 4)}{api_key[-4:]}" if len(api_key) > 4 else '****'
                }
            })

        openai_emb_cred = (
            resolve_credentials(user_id, 'openai_embeddings')
            or resolve_credentials(user_id, 'openai')
        )
        if openai_emb_cred:
            api_key = openai_emb_cred.get('api_key') or openai_emb_cred.get('credential_value') or ''
            creds_detail = openai_emb_cred.get('credentials') or {}
            return jsonify({
                'success': True,
                'config': {
                    'provider': 'openai',
                    'model': creds_detail.get('model', 'text-embedding-ada-002'),
                    'dimensions': creds_detail.get('dimensions', 1536),
                    'api_key_masked': f"{'*' * max(0, len(api_key) - 4)}{api_key[-4:]}" if len(api_key) > 4 else '****'
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
    Save embedding model configuration at business level (user_id=1)
    
    NOTE: Saves shared business-level embedding config. All users will use this config.
          Supports Voyager AI and OpenAI embedding providers.
    
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
    # GAP-V5: Embedding config now managed via Organisation Settings > Connections (org vault).
    # The Settings tab embedding form has been retired — configure Voyager or OpenAI credentials
    # directly in Organisation Settings instead.
    return jsonify({
        'success': False,
        'error': 'This endpoint is no longer active. Configure embedding credentials (Voyager AI or OpenAI) in Organisation Settings > Connections.',
        'redirect': '/settings/organisation/connections'
    }), 410

    try:
        data = request.get_json()
        
        user_id = g.rls_user_id
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