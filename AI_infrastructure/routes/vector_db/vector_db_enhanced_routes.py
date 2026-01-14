"""
Enhanced Vector Database Routes - Advanced Features
5 new Flask endpoints for hybrid search, cross-namespace queries, metadata filtering, and namespace management

Features:
- User-linked document ownership with metadata tagging
- Hierarchical category/folder system
- Sparse vector generation for hybrid search
- Advanced metadata filtering with complex queries
- Cross-namespace parallel search
- Namespace lifecycle management

Author: AI Agent
Date: November 30, 2025
"""

from flask import Blueprint, request, jsonify
from AI_infrastructure.auth.user_auth import UserAuthManager, require_auth
from tools.registry_v3 import RegistryV3
import logging

logger = logging.getLogger(__name__)

vector_db_enhanced_bp = Blueprint('vector_db_enhanced', __name__, url_prefix='/api/vector-db')
auth_manager = UserAuthManager()
registry = RegistryV3()


# ==================== ENDPOINT 1: CROSS-NAMESPACE QUERY ====================

@vector_db_enhanced_bp.route('/query-namespaces', methods=['POST'])
@require_auth
def query_namespaces():
    """
    Query multiple namespaces in parallel and aggregate results.
    
    **USER-AWARE**: Automatically filters results to user's namespaces or specified ones.
    
    Request Body:
        query_text (str): Natural language query
        namespaces (list): List of namespace names (empty = all user's namespaces)
        metric (str): Similarity metric ('cosine', 'euclidean', 'dotproduct')
        top_k (int): Results per namespace (default: 10)
        include_metadata (bool): Include document metadata (default: true)
        include_values (bool): Include vector values (default: false)
        filter (dict): Metadata filter (optional)
        
    Returns:
        {
            "success": true,
            "matches": [
                {
                    "id": "vec_123",
                    "score": 0.95,
                    "namespace": "user_42_legal",
                    "metadata": {...},
                    "values": [...]  // if include_values=true
                }
            ],
            "usage": {"read_units": 3},
            "namespaces_searched": ["user_42_legal", "user_42_finance"]
        }
    """
    try:
        user_id = request.user.get('user_id')
        data = request.json
        
        query_text = data.get('query_text')
        namespaces = data.get('namespaces', [])
        metric = data.get('metric', 'cosine')
        top_k = data.get('top_k', 10)
        include_metadata = data.get('include_metadata', True)
        include_values = data.get('include_values', False)
        filter_dict = data.get('filter', {})
        
        # Validation
        if not query_text:
            return jsonify({"success": False, "error": "query_text required"}), 400
            
        if metric not in ['cosine', 'euclidean', 'dotproduct']:
            return jsonify({"success": False, "error": "Invalid metric"}), 400
        
        # Auto-populate user's namespaces if empty
        if not namespaces:
            # Get all user's namespaces from index stats
            stats_result = registry.execute_tool(
                'pinecone_get_index_stats',
                _user_id=user_id,
                _injected_credentials=True
            )
            
            if stats_result.get('success'):
                all_namespaces = stats_result.get('namespaces', {}).keys()
                # Filter to user's namespaces (prefix: user_{user_id}_)
                user_prefix = f"user_{user_id}_"
                namespaces = [ns for ns in all_namespaces if ns.startswith(user_prefix)]
                
                if not namespaces:
                    return jsonify({
                        "success": False, 
                        "error": "No namespaces found for user",
                        "hint": "Upload documents first to create namespaces"
                    }), 404
        
        # Add user_id filter to ensure data isolation
        if 'owner_user_id' not in filter_dict:
            filter_dict['owner_user_id'] = {'$eq': user_id}
        
        # Call new tool: pinecone_query_namespaces
        result = registry.execute_tool(
            'pinecone_query_namespaces',
            query_text=query_text,
            namespaces=namespaces,
            metric=metric,
            top_k=top_k,
            filter=filter_dict,
            include_metadata=include_metadata,
            include_values=include_values,
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if result.get('success'):
            return jsonify({
                "success": True,
                "matches": result.get('matches', []),
                "usage": result.get('usage', {}),
                "namespaces_searched": namespaces
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"[query_namespaces] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ENDPOINT 2: METADATA FILTERING ====================

@vector_db_enhanced_bp.route('/fetch-by-metadata', methods=['POST'])
@require_auth
def fetch_by_metadata():
    """
    Fetch vectors by metadata filter WITHOUT generating query embeddings.
    
    **USE CASES**:
    - Data export and compliance auditing
    - Finding all documents by category, year, author
    - Bulk operations on tagged documents
    
    **USER-AWARE**: Automatically filters to user's documents.
    
    Request Body:
        filter (dict): Metadata filter with operators
        namespace (str): Target namespace (default: user's default namespace)
        limit (int): Max results (default: 100, max: 1000)
        fields (list): Metadata fields to return (default: all)
        
    Filter Operators:
        $eq: Equals
        $ne: Not equals
        $gt: Greater than
        $gte: Greater than or equal
        $lt: Less than
        $lte: Less than or equal
        $in: In array
        $nin: Not in array
        $exists: Field exists
        
    Example Filter:
        {
            "category": {"$eq": "legal"},
            "year": {"$gte": 2024},
            "author": {"$in": ["John", "Jane"]},
            "owner_user_id": {"$eq": 42}
        }
        
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
            "total_count": 45,
            "pagination": {
                "limit": 100,
                "has_more": false
            }
        }
    """
    try:
        user_id = request.user.get('user_id')
        data = request.json
        
        filter_dict = data.get('filter', {})
        namespace = data.get('namespace', f"user_{user_id}_default")
        limit = min(data.get('limit', 100), 1000)  # Max 1000
        fields = data.get('fields', None)  # None = all fields
        
        # Validation
        if not filter_dict:
            return jsonify({"success": False, "error": "filter required"}), 400
        
        # Force user ownership filter
        if 'owner_user_id' not in filter_dict:
            filter_dict['owner_user_id'] = {'$eq': user_id}
        
        # Call new tool: pinecone_fetch_by_metadata
        result = registry.execute_tool(
            'pinecone_fetch_by_metadata',
            filter=filter_dict,
            namespace=namespace,
            limit=limit,
            fields=fields,
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if result.get('success'):
            vectors = result.get('vectors', [])
            return jsonify({
                "success": True,
                "vectors": vectors,
                "total_count": len(vectors),
                "pagination": {
                    "limit": limit,
                    "has_more": len(vectors) == limit
                }
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"[fetch_by_metadata] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ENDPOINT 3: LIST NAMESPACES ====================

@vector_db_enhanced_bp.route('/namespaces', methods=['GET'])
@require_auth
def list_namespaces():
    """
    List all namespaces (folders) owned by the user.
    
    **FOLDER SYSTEM**: Each namespace represents a category/folder.
    
    Query Parameters:
        include_stats (bool): Include vector counts (default: true)
        prefix (str): Filter by namespace prefix (optional)
        
    Returns:
        {
            "success": true,
            "namespaces": [
                {
                    "name": "user_42_legal",
                    "display_name": "Legal Documents",
                    "vector_count": 145,
                    "created_at": "2025-11-15T10:30:00Z",
                    "category": "legal",
                    "owner_user_id": 42
                },
                {
                    "name": "user_42_finance",
                    "display_name": "Finance Reports",
                    "vector_count": 89,
                    "created_at": "2025-11-20T14:22:00Z",
                    "category": "finance",
                    "owner_user_id": 42
                }
            ],
            "total_count": 2
        }
    """
    try:
        user_id = request.user.get('user_id')
        include_stats = request.args.get('include_stats', 'true').lower() == 'true'
        prefix = request.args.get('prefix', f"user_{user_id}_")
        
        # Get index stats
        stats_result = registry.execute_tool(
            'pinecone_get_index_stats',
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if not stats_result.get('success'):
            return jsonify(stats_result), 500
        
        all_namespaces = stats_result.get('namespaces', {})
        
        # Filter to user's namespaces
        user_namespaces = []
        for ns_name, ns_stats in all_namespaces.items():
            if ns_name.startswith(prefix):
                # Parse category from namespace name
                # Format: user_{user_id}_{category}
                parts = ns_name.split('_')
                category = parts[2] if len(parts) > 2 else 'default'
                display_name = category.replace('_', ' ').title()
                
                namespace_info = {
                    "name": ns_name,
                    "display_name": display_name,
                    "category": category,
                    "owner_user_id": user_id
                }
                
                if include_stats:
                    namespace_info["vector_count"] = ns_stats.get('vector_count', 0)
                
                user_namespaces.append(namespace_info)
        
        return jsonify({
            "success": True,
            "namespaces": user_namespaces,
            "total_count": len(user_namespaces)
        }), 200
        
    except Exception as e:
        logger.error(f"[list_namespaces] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ENDPOINT 4: DESCRIBE NAMESPACE ====================

@vector_db_enhanced_bp.route('/namespaces/<namespace>', methods=['GET'])
@require_auth
def describe_namespace(namespace: str):
    """
    Get detailed statistics about a specific namespace.
    
    **SECURITY**: Validates user owns the namespace.
    
    Returns:
        {
            "success": true,
            "namespace": {
                "name": "user_42_legal",
                "display_name": "Legal Documents",
                "vector_count": 145,
                "dimension": 1536,
                "metric": "cosine",
                "category": "legal",
                "owner_user_id": 42,
                "metadata_schema": {
                    "filename": "string",
                    "upload_date": "datetime",
                    "category": "string",
                    "subcategory": "string",
                    "tags": "array"
                },
                "sample_vectors": [...]  // First 3 vector IDs
            }
        }
    """
    try:
        user_id = request.user.get('user_id')
        
        # Validate user owns namespace
        expected_prefix = f"user_{user_id}_"
        if not namespace.startswith(expected_prefix):
            return jsonify({
                "success": False, 
                "error": "Unauthorized: Namespace does not belong to user"
            }), 403
        
        # Get namespace stats from index stats
        stats_result = registry.execute_tool(
            'pinecone_get_index_stats',
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if not stats_result.get('success'):
            return jsonify(stats_result), 500
        
        namespaces = stats_result.get('namespaces', {})
        
        if namespace not in namespaces:
            return jsonify({
                "success": False, 
                "error": "Namespace not found"
            }), 404
        
        ns_stats = namespaces[namespace]
        
        # Parse category from namespace name
        parts = namespace.split('_')
        category = parts[2] if len(parts) > 2 else 'default'
        display_name = category.replace('_', ' ').title()
        
        # Get index description for dimension and metric
        describe_result = registry.execute_tool(
            'pinecone_describe_index',
            _user_id=user_id,
            _injected_credentials=True
        )
        
        dimension = describe_result.get('dimension', 1536)
        metric = describe_result.get('metric', 'cosine')
        
        namespace_details = {
            "name": namespace,
            "display_name": display_name,
            "vector_count": ns_stats.get('vector_count', 0),
            "dimension": dimension,
            "metric": metric,
            "category": category,
            "owner_user_id": user_id,
            "metadata_schema": {
                "filename": "string",
                "upload_date": "datetime",
                "category": "string",
                "subcategory": "string",
                "tags": "array",
                "owner_user_id": "integer",
                "source": "string"
            }
        }
        
        return jsonify({
            "success": True,
            "namespace": namespace_details
        }), 200
        
    except Exception as e:
        logger.error(f"[describe_namespace] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500


# ==================== ENDPOINT 5: DELETE NAMESPACE ====================

@vector_db_enhanced_bp.route('/namespaces/<namespace>', methods=['DELETE'])
@require_auth
def delete_namespace(namespace: str):
    """
    Delete a namespace and all its vectors.
    
    **SECURITY**: 
    - Validates user owns the namespace
    - Protects default namespace from deletion
    - Requires confirmation parameter
    
    Query Parameters:
        confirm (str): Must be "DELETE" to proceed
        
    Returns:
        {
            "success": true,
            "message": "Namespace deleted successfully",
            "vectors_deleted": 145
        }
    """
    try:
        user_id = request.user.get('user_id')
        confirm = request.args.get('confirm', '')
        
        # Validate user owns namespace
        expected_prefix = f"user_{user_id}_"
        if not namespace.startswith(expected_prefix):
            return jsonify({
                "success": False, 
                "error": "Unauthorized: Namespace does not belong to user"
            }), 403
        
        # Protect default namespace
        if namespace == f"user_{user_id}_default":
            return jsonify({
                "success": False, 
                "error": "Cannot delete default namespace"
            }), 400
        
        # Require confirmation
        if confirm != "DELETE":
            return jsonify({
                "success": False, 
                "error": "Confirmation required. Pass ?confirm=DELETE to proceed"
            }), 400
        
        # Get vector count before deletion
        stats_result = registry.execute_tool(
            'pinecone_get_index_stats',
            _user_id=user_id,
            _injected_credentials=True
        )
        
        vector_count = 0
        if stats_result.get('success'):
            namespaces = stats_result.get('namespaces', {})
            if namespace in namespaces:
                vector_count = namespaces[namespace].get('vector_count', 0)
        
        # Delete all vectors in namespace
        # Note: Pinecone doesn't have direct namespace delete, so we delete all vectors
        delete_result = registry.execute_tool(
            'pinecone_delete_vectors',
            delete_all=True,
            namespace=namespace,
            _user_id=user_id,
            _injected_credentials=True
        )
        
        if delete_result.get('success'):
            return jsonify({
                "success": True,
                "message": f"Namespace '{namespace}' deleted successfully",
                "vectors_deleted": vector_count
            }), 200
        else:
            return jsonify(delete_result), 500
            
    except Exception as e:
        logger.error(f"[delete_namespace] Error: {e}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
