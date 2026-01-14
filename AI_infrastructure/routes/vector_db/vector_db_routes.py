"""
Vector Database Routes - Flask API endpoints for vector database management

FILE: AI_infrastructure/routes/vector_db/vector_db_routes.py
PURPOSE: REST API for Pinecone vector database operations

ENDPOINTS:
- POST /api/vector-db/credentials/save - Save Pinecone credentials
- GET /api/vector-db/credentials/get - Retrieve credentials
- POST /api/vector-db/test-connection - Test Pinecone connection
- POST /api/vector-db/embedding-config/save - Save OpenAI embedding config
- POST /api/vector-db/upload-document - Upload and process document
- GET /api/vector-db/stats - Get database statistics
- GET /api/vector-db/documents - List indexed documents
- DELETE /api/vector-db/document/<doc_id> - Delete document

DEPENDENCIES:
- Flask (request, jsonify, Blueprint)
- AI_infrastructure.auth.user_auth (UserAuthManager)
- tools.registry_v3 (RegistryV3)

LAST MODIFIED: 2025-11-25
"""

from flask import Blueprint, request, jsonify
import sys
from pathlib import Path
import json
import os

# Add paths
ai_infra_dir = Path(__file__).parent.parent.parent
if str(ai_infra_dir) not in sys.path:
    sys.path.insert(0, str(ai_infra_dir))

from AI_infrastructure.auth.user_auth import UserAuthManager
from shared.database_utils import get_database_connection

# Create blueprint
vector_db_bp = Blueprint('vector_db', __name__)

print('[VECTOR DB ROUTES] Blueprint created')


@vector_db_bp.route('/api/vector-db/credentials/save', methods=['POST'])
def save_credentials():
    """Save Pinecone credentials for user"""
    try:
        data = request.json
        user_id = data.get('user_id')
        api_key = data.get('api_key')
        index_name = data.get('index_name')
        environment = data.get('environment')
        namespace = data.get('namespace', '')

        if not all([user_id, api_key, index_name, environment]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        auth_manager = UserAuthManager()

        # Store Pinecone credentials
        metadata = {
            'index_name': index_name,
            'environment': environment,
            'namespace': namespace
        }

        result = auth_manager.store_platform_credential(
            user_id=user_id,
            platform='pinecone',
            credential_type='api_key',
            credential_key='PINECONE_API_KEY',
            credential_value=api_key,
            metadata=metadata
        )

        if result.get('success'):
            print(f'[VECTOR DB] Saved Pinecone credentials for user {user_id}')
            return jsonify({
                'success': True,
                'message': 'Credentials saved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to save credentials')
            }), 500

    except Exception as e:
        print(f'[VECTOR DB] Save credentials error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vector_db_bp.route('/api/vector-db/credentials/get', methods=['GET'])
def get_credentials():
    """Retrieve Pinecone credentials for user"""
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id'
            }), 400

        auth_manager = UserAuthManager()
        creds = auth_manager.get_platform_credentials(user_id, 'pinecone')

        if creds:
            # Parse metadata to get index_name, environment, namespace
            conn = get_database_connection('ai_infrastructure')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT metadata FROM user_platform_credentials
                WHERE user_id = %s AND platform = 'pinecone'
                ORDER BY updated_at DESC LIMIT 1
            ''', (user_id,))
            
            row = cursor.fetchone()
            conn.close()

            metadata = {}
            if row and row[0]:
                try:
                    metadata = json.loads(row[0])
                except:
                    pass

            return jsonify({
                'success': True,
                'credentials': {
                    'index_name': metadata.get('index_name', ''),
                    'environment': metadata.get('environment', ''),
                    'namespace': metadata.get('namespace', '')
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No credentials found'
            }), 404

    except Exception as e:
        print(f'[VECTOR DB] Get credentials error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vector_db_bp.route('/api/vector-db/test-connection', methods=['POST'])
def test_connection():
    """Test connection to Pinecone"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id'
            }), 400

        # Import registry to execute pinecone_describe_index_stats tool
        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()

        # Execute describe_index_stats (this will test connection)
        result = registry.execute_tool(
            'pinecone_describe_index_stats',
            _user_id=user_id,
            _injected_credentials=True
        )

        if result.get('success'):
            total_vectors = result.get('total_vector_count', 0)
            namespaces = len(result.get('namespaces', {}))
            
            return jsonify({
                'success': True,
                'message': f'Connected! {total_vectors} vectors across {namespaces} namespaces',
                'stats': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Connection test failed')
            }), 500

    except Exception as e:
        print(f'[VECTOR DB] Test connection error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vector_db_bp.route('/api/vector-db/embedding-config/save', methods=['POST'])
def save_embedding_config():
    """Save OpenAI embedding configuration"""
    try:
        data = request.json
        user_id = data.get('user_id')
        api_key = data.get('api_key')
        model = data.get('model', 'text-embedding-ada-002')

        if not all([user_id, api_key]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400

        auth_manager = UserAuthManager()

        metadata = {'model': model}

        result = auth_manager.store_platform_credential(
            user_id=user_id,
            platform='openai_embeddings',
            credential_type='api_key',
            credential_key='OPENAI_API_KEY',
            credential_value=api_key,
            metadata=metadata
        )

        if result.get('success'):
            print(f'[VECTOR DB] Saved OpenAI embedding config for user {user_id}')
            return jsonify({
                'success': True,
                'message': 'Embedding configuration saved'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to save config')
            }), 500

    except Exception as e:
        print(f'[VECTOR DB] Save embedding config error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vector_db_bp.route('/api/vector-db/upload-document', methods=['POST'])
def upload_document():
    """Upload and process document into vector database"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400

        file = request.files['file']
        user_id = request.form.get('user_id', type=int)
        chunk_size = request.form.get('chunk_size', type=int, default=800)
        chunk_overlap = request.form.get('chunk_overlap', type=int, default=20)
        namespace = request.form.get('namespace', default='')

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id'
            }), 400

        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        try:
            # Import registry to execute document processing tool
            from tools.registry_v3 import RegistryV3
            registry = RegistryV3()

            # Execute vector_db_upload_document tool
            result = registry.execute_tool(
                'vector_db_upload_document',
                file_path=tmp_path,
                filename=file.filename,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                namespace=namespace,
                _user_id=user_id,
                _injected_credentials=True
            )

            if result.get('success'):
                return jsonify({
                    'success': True,
                    'message': 'Document processed successfully',
                    'vectors_uploaded': result.get('vectors_uploaded', 0),
                    'document_id': result.get('document_id')
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Processing failed')
                }), 500

        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except Exception as e:
        print(f'[VECTOR DB] Upload document error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vector_db_bp.route('/api/vector-db/stats', methods=['GET'])
def get_stats():
    """Get vector database statistics"""
    try:
        user_id = request.args.get('user_id', type=int)

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id'
            }), 400

        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()

        result = registry.execute_tool(
            'pinecone_describe_index_stats',
            _user_id=user_id,
            _injected_credentials=True
        )

        if result.get('success'):
            namespaces = result.get('namespaces', {})
            total_vectors = result.get('total_vector_count', 0)

            # Count documents (assuming each document is a namespace or tracked separately)
            # This is simplified - you may want to track documents in a separate table
            document_count = len(namespaces)

            return jsonify({
                'success': True,
                'stats': {
                    'documents': document_count,
                    'vectors': total_vectors,
                    'namespaces': len(namespaces)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to get stats')
            }), 500

    except Exception as e:
        print(f'[VECTOR DB] Get stats error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vector_db_bp.route('/api/vector-db/documents', methods=['GET'])
def list_documents():
    """List indexed documents"""
    try:
        user_id = request.args.get('user_id', type=int)

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id'
            }), 400

        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()

        result = registry.execute_tool(
            'pinecone_list_namespaces',
            _user_id=user_id,
            _injected_credentials=True
        )

        if result.get('success'):
            namespaces = result.get('namespaces', [])
            
            # Convert namespaces to document format
            documents = []
            for ns in namespaces:
                documents.append({
                    'id': ns.get('name'),
                    'name': ns.get('name'),
                    'vector_count': ns.get('vector_count', 0),
                    'created_at': ns.get('created_at', '')
                })

            return jsonify({
                'success': True,
                'documents': documents
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to list documents')
            }), 500

    except Exception as e:
        print(f'[VECTOR DB] List documents error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vector_db_bp.route('/api/vector-db/document/<doc_id>', methods=['DELETE'])
def delete_document(doc_id):
    """Delete document from vector database"""
    try:
        data = request.json
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing user_id'
            }), 400

        from tools.registry_v3 import RegistryV3
        registry = RegistryV3()

        # Delete all vectors in the namespace (document)
        result = registry.execute_tool(
            'pinecone_delete_vectors',
            namespace=doc_id,
            delete_all=True,
            _user_id=user_id,
            _injected_credentials=True
        )

        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Document deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to delete document')
            }), 500

    except Exception as e:
        print(f'[VECTOR DB] Delete document error: {e}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


print('[VECTOR DB ROUTES] Module loaded')
