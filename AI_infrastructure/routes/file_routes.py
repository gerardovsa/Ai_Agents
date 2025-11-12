"""
File Management Routes
Handles file uploads, downloads, and storage
"""

import sys
import os
from flask import Blueprint, request, send_file, jsonify
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.file_storage import (
    get_file_path, delete_file, get_user_storage_usage,
    delete_thread_files, FileStorageError
)
from utils.response_helpers import success_response, error_response

try:
    from config.constants import MAX_USER_STORAGE
except ModuleNotFoundError:
    MAX_USER_STORAGE = 500 * 1024 * 1024  # 500 MB fallback

# Create blueprint
file_bp = Blueprint('files', __name__, url_prefix='/api/files')


@file_bp.route('/<path:file_path>', methods=['GET'])
def serve_file(file_path):
    """
    Serve uploaded file
    
    GET /api/files/user_14/thread_123/invoice.pdf
    
    Returns:
        File download or error
    """
    try:
        # Construct server path
        server_path = f"/uploads/{file_path}"
        
        # Get absolute file path
        abs_path = get_file_path(server_path)
        
        if not abs_path:
            return error_response("File not found", 404)
        
        # Serve file
        return send_file(
            abs_path,
            as_attachment=False,  # Display in browser if possible
            download_name=abs_path.name
        )
    
    except Exception as e:
        return error_response(f"Failed to serve file: {str(e)}", 500)


@file_bp.route('/<path:file_path>/download', methods=['GET'])
def download_file(file_path):
    """
    Force download of file
    
    GET /api/files/user_14/thread_123/invoice.pdf/download
    
    Returns:
        File as attachment
    """
    try:
        # Construct server path
        server_path = f"/uploads/{file_path}"
        
        # Get absolute file path
        abs_path = get_file_path(server_path)
        
        if not abs_path:
            return error_response("File not found", 404)
        
        # Serve file as attachment
        return send_file(
            abs_path,
            as_attachment=True,
            download_name=abs_path.name
        )
    
    except Exception as e:
        return error_response(f"Failed to download file: {str(e)}", 500)


@file_bp.route('/delete', methods=['POST'])
def delete_file_route():
    """
    Delete a file
    
    POST /api/files/delete
    Body: {
        "server_path": "/uploads/user_14/thread_123/invoice.pdf"
    }
    
    Returns:
        Success or error
    """
    try:
        data = request.get_json()
        server_path = data.get('server_path')
        
        if not server_path:
            return error_response("server_path required", 400)
        
        # Delete file
        success = delete_file(server_path)
        
        if not success:
            return error_response("File not found or already deleted", 404)
        
        return success_response({}, message="File deleted successfully")
    
    except Exception as e:
        return error_response(f"Failed to delete file: {str(e)}", 500)


@file_bp.route('/storage/usage', methods=['GET'])
def get_storage_usage():
    """
    Get storage usage for user
    
    GET /api/files/storage/usage?user_id=14
    
    Returns:
        {
            "used_bytes": 245678000,
            "used_mb": 234.2,
            "total_mb": 500,
            "percent_used": 46.84
        }
    """
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return error_response("user_id required", 400)
        
        user_id = int(user_id)
        
        # Get usage
        used_bytes = get_user_storage_usage(user_id)
        used_mb = used_bytes / 1024 / 1024
        total_mb = MAX_USER_STORAGE / 1024 / 1024
        percent_used = (used_bytes / MAX_USER_STORAGE) * 100
        
        return success_response({
            'used_bytes': used_bytes,
            'used_mb': round(used_mb, 2),
            'total_mb': int(total_mb),
            'percent_used': round(percent_used, 2)
        })
    
    except Exception as e:
        return error_response(f"Failed to get storage usage: {str(e)}", 500)


@file_bp.route('/thread/delete', methods=['POST'])
def delete_thread_files_route():
    """
    Delete all files for a thread
    
    POST /api/files/thread/delete
    Body: {
        "user_id": 14,
        "thread_id": "1762851232975"
    }
    
    Returns:
        Number of files deleted
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        thread_id = data.get('thread_id')
        
        if not user_id or not thread_id:
            return error_response("user_id and thread_id required", 400)
        
        # Delete files
        count = delete_thread_files(int(user_id), str(thread_id))
        
        return success_response({
            'deleted_count': count
        }, message=f"Deleted {count} files")
    
    except Exception as e:
        return error_response(f"Failed to delete thread files: {str(e)}", 500)
