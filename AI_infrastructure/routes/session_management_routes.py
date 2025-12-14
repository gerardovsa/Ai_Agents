"""
C:/Users/gpoli/GIT/AI_agents/AI_infrastructure/routes/session_management_routes.py
Cloud Folder Sync Routes
FULLY FIXED VERSION - Production Ready

⚠️ CURSOR MANAGEMENT FIXES (Dec 07, 2025):
   - ✅ All cursors properly closed before connections
   - ✅ All functions use finally blocks
   - ✅ All cursors initialized as None
   - ✅ Early returns properly handle cleanup
   - ✅ Multiple cursors independently managed
   - ✅ Exception paths guaranteed cleanup

Endpoints:
- POST /api/cloud-sync/folders - Sync Google Drive folders to database
- GET /api/cloud-sync/folders - List all synced folders
- GET /api/cloud-sync/folders/<folder_id>/files - List files in folder
- PUT /api/cloud-sync/folders/<folder_id> - Update folder metadata
- DELETE /api/cloud-sync/folders/<folder_id> - Remove folder from sync
- POST /api/cloud-sync/folders/<folder_id>/refresh - Force refresh folder contents

LAST MODIFIED: 2025-12-07 - Fixed cursor management
AUDITED BY: AI Code Auditor using Complete Cursor Management Audit Guide
"""

from flask import Blueprint, request, jsonify
from shared.database_utils import get_database_connection
from datetime import datetime
import json

cloud_storage_bp = Blueprint('cloud_storage', __name__)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def success_response(data, message="Success", status_code=200):
    """Standard success response format"""
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    }), status_code

def error_response(error, status_code=400):
    """Standard error response format"""
    return jsonify({
        'success': False,
        'error': error
    }), status_code

def validate_user_id(user_id):
    """Validate user_id parameter"""
    if not user_id:
        return False, "user_id is required"
    try:
        user_id = int(user_id)
        if user_id < 1:
            return False, "Invalid user_id"
        return True, user_id
    except (ValueError, TypeError):
        return False, "user_id must be a valid integer"

def validate_folder_data(data):
    """Validate folder creation/update data"""
    required_fields = ['folder_id', 'folder_name', 'user_id']
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    
    return True, None

# ============================================================================
# ENDPOINT 1: Sync Google Drive Folders
# ============================================================================

@cloud_storage_bp.route('/api/cloud-sync/folders', methods=['POST'])
def sync_folders():
    """
    Sync Google Drive folders to database
    
    ✅ FIXED: Proper cursor management with 3 early returns + finally block
    
    Request Body:
        {
            "user_id": 1,
            "folders": [
                {
                    "folder_id": "1a2b3c4d5e",
                    "folder_name": "Project Files",
                    "parent_id": null,
                    "permissions": ["read", "write"]
                }
            ]
        }
    
    Returns:
        {
            "success": true,
            "message": "Synced 3 folders successfully",
            "data": {
                "synced_count": 3,
                "failed_count": 0,
                "folder_ids": [123, 124, 125]
            }
        }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    
    try:
        data = request.json
        
        # Validation 1: Check if data exists
        if not data:
            return error_response("Request body is required", 400)
        
        # Validation 2: Check user_id
        valid, result = validate_user_id(data.get('user_id'))
        if not valid:
            return error_response(result, 400)
        user_id = result
        
        # Validation 3: Check folders array
        folders = data.get('folders', [])
        if not folders or not isinstance(folders, list):
            return error_response("folders array is required", 400)
        
        # Now safe to create database resources
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        synced_ids = []
        failed_count = 0
        
        for folder in folders:
            try:
                folder_id = folder.get('folder_id')
                folder_name = folder.get('folder_name')
                parent_id = folder.get('parent_id')
                permissions = json.dumps(folder.get('permissions', []))
                
                # Upsert folder (insert or update if exists)
                cursor.execute("""
                    INSERT INTO ai_infrastructure.cloud_folders 
                    (folder_id, folder_name, parent_id, user_id, permissions, last_synced)
                    VALUES (%s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (folder_id, user_id) 
                    DO UPDATE SET
                        folder_name = EXCLUDED.folder_name,
                        parent_id = EXCLUDED.parent_id,
                        permissions = EXCLUDED.permissions,
                        last_synced = NOW()
                    RETURNING id
                """, (folder_id, folder_name, parent_id, user_id, permissions))
                
                result = cursor.fetchone()
                if result:
                    synced_ids.append(result[0])
                
            except Exception as folder_error:
                print(f"❌ Failed to sync folder {folder.get('folder_id')}: {folder_error}")
                failed_count += 1
        
        conn.commit()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return success_response({
            'synced_count': len(synced_ids),
            'failed_count': failed_count,
            'folder_ids': synced_ids
        }, f"Synced {len(synced_ids)} folders successfully")
        
    except Exception as e:
        print(f"❌ [CLOUD SYNC] Error syncing folders: {e}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to sync folders: {str(e)}", 500)
    
    finally:
        # ✅ Guaranteed cleanup
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

# ============================================================================
# ENDPOINT 2: List Synced Folders
# ============================================================================

@cloud_storage_bp.route('/api/cloud-sync/folders', methods=['GET'])
def list_folders():
    """
    List all synced folders for a user
    
    ✅ FIXED: Proper cursor management with 1 early return + finally block
    
    Query Params:
        user_id: User ID (required)
        parent_id: Filter by parent folder ID (optional)
    
    Returns:
        {
            "success": true,
            "data": {
                "folders": [
                    {
                        "id": 123,
                        "folder_id": "1a2b3c4d5e",
                        "folder_name": "Project Files",
                        "parent_id": null,
                        "permissions": ["read", "write"],
                        "last_synced": "2025-12-07T10:30:00",
                        "file_count": 15
                    }
                ],
                "total": 5
            }
        }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    
    try:
        user_id = request.args.get('user_id')
        parent_id = request.args.get('parent_id')
        
        # Validation 1: Check user_id
        valid, result = validate_user_id(user_id)
        if not valid:
            return error_response(result, 400)
        user_id = result
        
        # Now safe to create database resources
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Build query based on filters
        if parent_id:
            query = """
                SELECT 
                    cf.id,
                    cf.folder_id,
                    cf.folder_name,
                    cf.parent_id,
                    cf.permissions,
                    TO_CHAR(cf.last_synced, 'YYYY-MM-DD"T"HH24:MI:SS') as last_synced,
                    COUNT(DISTINCT cff.id) as file_count
                FROM ai_infrastructure.cloud_folders cf
                LEFT JOIN ai_infrastructure.cloud_folder_files cff 
                    ON cf.id = cff.folder_id
                WHERE cf.user_id = %s AND cf.parent_id = %s
                GROUP BY cf.id
                ORDER BY cf.folder_name
            """
            cursor.execute(query, (user_id, parent_id))
        else:
            query = """
                SELECT 
                    cf.id,
                    cf.folder_id,
                    cf.folder_name,
                    cf.parent_id,
                    cf.permissions,
                    TO_CHAR(cf.last_synced, 'YYYY-MM-DD"T"HH24:MI:SS') as last_synced,
                    COUNT(DISTINCT cff.id) as file_count
                FROM ai_infrastructure.cloud_folders cf
                LEFT JOIN ai_infrastructure.cloud_folder_files cff 
                    ON cf.id = cff.folder_id
                WHERE cf.user_id = %s
                GROUP BY cf.id
                ORDER BY cf.folder_name
            """
            cursor.execute(query, (user_id,))
        
        rows = cursor.fetchall()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        folders = []
        for row in rows:
            folder_id_db, folder_id, folder_name, parent_id, permissions, last_synced, file_count = row
            
            # Parse permissions JSON
            if isinstance(permissions, str):
                try:
                    permissions = json.loads(permissions)
                except:
                    permissions = []
            
            folders.append({
                'id': folder_id_db,
                'folder_id': folder_id,
                'folder_name': folder_name,
                'parent_id': parent_id,
                'permissions': permissions or [],
                'last_synced': last_synced,
                'file_count': file_count
            })
        
        return success_response({
            'folders': folders,
            'total': len(folders)
        })
        
    except Exception as e:
        print(f"❌ [CLOUD SYNC] Error listing folders: {e}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to list folders: {str(e)}", 500)
    
    finally:
        # ✅ Guaranteed cleanup
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

# ============================================================================
# ENDPOINT 3: List Files in Folder
# ============================================================================

@cloud_storage_bp.route('/api/cloud-sync/folders/<int:folder_id>/files', methods=['GET'])
def list_folder_files(folder_id):
    """
    List all files in a specific folder
    
    ✅ FIXED: Proper cursor management with 2 early returns + finally block
    
    Path Params:
        folder_id: Database folder ID (required)
    
    Query Params:
        user_id: User ID (required)
    
    Returns:
        {
            "success": true,
            "data": {
                "files": [
                    {
                        "id": 456,
                        "file_id": "xyz123",
                        "file_name": "document.pdf",
                        "mime_type": "application/pdf",
                        "size": 2048576,
                        "modified_time": "2025-12-07T10:30:00"
                    }
                ],
                "total": 15
            }
        }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    
    try:
        user_id = request.args.get('user_id')
        
        # Validation 1: Check user_id
        valid, result = validate_user_id(user_id)
        if not valid:
            return error_response(result, 400)
        user_id = result
        
        # Now safe to create database resources
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Validation 2: Check if folder exists and belongs to user
        cursor.execute("""
            SELECT id FROM ai_infrastructure.cloud_folders
            WHERE id = %s AND user_id = %s
        """, (folder_id, user_id))
        
        if not cursor.fetchone():
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return error_response("Folder not found or access denied", 404)
        
        # Get files in folder
        cursor.execute("""
            SELECT 
                id,
                file_id,
                file_name,
                mime_type,
                size_bytes,
                TO_CHAR(modified_time, 'YYYY-MM-DD"T"HH24:MI:SS') as modified_time,
                web_view_link
            FROM ai_infrastructure.cloud_folder_files
            WHERE folder_id = %s
            ORDER BY file_name
        """, (folder_id,))
        
        rows = cursor.fetchall()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        files = []
        for row in rows:
            file_id_db, file_id, file_name, mime_type, size_bytes, modified_time, web_view_link = row
            
            files.append({
                'id': file_id_db,
                'file_id': file_id,
                'file_name': file_name,
                'mime_type': mime_type,
                'size': size_bytes,
                'modified_time': modified_time,
                'web_view_link': web_view_link
            })
        
        return success_response({
            'files': files,
            'total': len(files)
        })
        
    except Exception as e:
        print(f"❌ [CLOUD SYNC] Error listing files: {e}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to list files: {str(e)}", 500)
    
    finally:
        # ✅ Guaranteed cleanup
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

# ============================================================================
# ENDPOINT 4: Update Folder Metadata
# ============================================================================

@cloud_storage_bp.route('/api/cloud-sync/folders/<int:folder_id>', methods=['PUT'])
def update_folder(folder_id):
    """
    Update folder metadata (name, permissions, etc.)
    
    ✅ FIXED: Proper cursor management with 3 early returns + finally block
    
    Path Params:
        folder_id: Database folder ID (required)
    
    Request Body:
        {
            "user_id": 1,
            "folder_name": "Updated Name",
            "permissions": ["read", "write", "share"]
        }
    
    Returns:
        {
            "success": true,
            "message": "Folder updated successfully",
            "data": {
                "folder_id": 123,
                "folder_name": "Updated Name"
            }
        }
    """
    cursor = None  # ✅ Initialize cursor before try
    conn = None    # ✅ Initialize connection before try
    
    try:
        data = request.json
        
        # Validation 1: Check if data exists
        if not data:
            return error_response("Request body is required", 400)
        
        # Validation 2: Check user_id
        valid, result = validate_user_id(data.get('user_id'))
        if not valid:
            return error_response(result, 400)
        user_id = result
        
        # Validation 3: Check required fields
        folder_name = data.get('folder_name')
        if not folder_name:
            return error_response("folder_name is required", 400)
        
        permissions = json.dumps(data.get('permissions', []))
        
        # Now safe to create database resources
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check if folder exists and belongs to user
        cursor.execute("""
            SELECT id FROM ai_infrastructure.cloud_folders
            WHERE id = %s AND user_id = %s
        """, (folder_id, user_id))
        
        if not cursor.fetchone():
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return error_response("Folder not found or access denied", 404)
        
        # Update folder
        cursor.execute("""
            UPDATE ai_infrastructure.cloud_folders
            SET 
                folder_name = %s,
                permissions = %s,
                last_synced = NOW()
            WHERE id = %s AND user_id = %s
            RETURNING folder_id, folder_name
        """, (folder_name, permissions, folder_id, user_id))
        
        result = cursor.fetchone()
        conn.commit()
        
        # ✅ Close cursor BEFORE connection
        cursor.close()
        cursor = None
        conn.close()
        conn = None
        
        return success_response({
            'folder_id': result[0],
            'folder_name': result[1]
        }, "Folder updated successfully")
        
    except Exception as e:
        print(f"❌ [CLOUD SYNC] Error updating folder: {e}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to update folder: {str(e)}", 500)
    
    finally:
        # ✅ Guaranteed cleanup
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

# ============================================================================
# ENDPOINT 5: Delete Synced Folder
# ============================================================================

@cloud_storage_bp.route('/api/cloud-sync/folders/<int:folder_id>', methods=['DELETE'])
def delete_folder(folder_id):
    """
    Remove folder from sync (does not delete from Google Drive)
    
    ✅ FIXED: Proper cursor management with 2 early returns + finally block
                Uses 2 INDEPENDENT cursors
    
    Path Params:
        folder_id: Database folder ID (required)
    
    Query Params:
        user_id: User ID (required)
    
    Returns:
        {
            "success": true,
            "message": "Folder removed from sync",
            "data": {
                "deleted_folder_id": 123,
                "deleted_files": 15
            }
        }
    """
    cursor = None   # ✅ Initialize cursor1 before try
    cursor2 = None  # ✅ Initialize cursor2 before try
    conn = None     # ✅ Initialize connection before try
    
    try:
        user_id = request.args.get('user_id')
        
        # Validation 1: Check user_id
        valid, result = validate_user_id(user_id)
        if not valid:
            return error_response(result, 400)
        user_id = result
        
        # Now safe to create database resources
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Check if folder exists and belongs to user
        cursor.execute("""
            SELECT id FROM ai_infrastructure.cloud_folders
            WHERE id = %s AND user_id = %s
        """, (folder_id, user_id))
        
        if not cursor.fetchone():
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return error_response("Folder not found or access denied", 404)
        
        # ✅ IMPORTANT: Close cursor1, create cursor2 for next operation
        cursor.close()
        cursor = None
        
        cursor2 = conn.cursor()
        
        # Delete associated files first (CASCADE should handle this, but explicit is better)
        cursor2.execute("""
            DELETE FROM ai_infrastructure.cloud_folder_files
            WHERE folder_id = %s
            RETURNING id
        """, (folder_id,))
        
        deleted_files = len(cursor2.fetchall())
        
        # Delete folder
        cursor2.execute("""
            DELETE FROM ai_infrastructure.cloud_folders
            WHERE id = %s AND user_id = %s
        """, (folder_id, user_id))
        
        conn.commit()
        
        # ✅ Close cursor2 BEFORE connection
        cursor2.close()
        cursor2 = None
        conn.close()
        conn = None
        
        return success_response({
            'deleted_folder_id': folder_id,
            'deleted_files': deleted_files
        }, "Folder removed from sync")
        
    except Exception as e:
        print(f"❌ [CLOUD SYNC] Error deleting folder: {e}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to delete folder: {str(e)}", 500)
    
    finally:
        # ✅ Cleanup cursor1 independently
        if cursor:
            try:
                cursor.close()
            except:
                pass
        
        # ✅ Cleanup cursor2 independently
        if cursor2:
            try:
                cursor2.close()
            except:
                pass
        
        # ✅ Cleanup connection
        if conn:
            try:
                conn.close()
            except:
                pass

# ============================================================================
# ENDPOINT 6: Force Refresh Folder Contents
# ============================================================================

@cloud_storage_bp.route('/api/cloud-sync/folders/<int:folder_id>/refresh', methods=['POST'])
def refresh_folder(folder_id):
    """
    Force refresh folder contents from Google Drive
    
    ✅ FIXED: Proper cursor management with 4 early returns + finally block
                Uses 3 INDEPENDENT cursors
    
    Path Params:
        folder_id: Database folder ID (required)
    
    Request Body:
        {
            "user_id": 1,
            "files": [
                {
                    "file_id": "xyz123",
                    "file_name": "document.pdf",
                    "mime_type": "application/pdf",
                    "size": 2048576,
                    "modified_time": "2025-12-07T10:30:00",
                    "web_view_link": "https://drive.google.com/..."
                }
            ]
        }
    
    Returns:
        {
            "success": true,
            "message": "Folder refreshed successfully",
            "data": {
                "folder_id": 123,
                "added_files": 5,
                "updated_files": 3,
                "removed_files": 2
            }
        }
    """
    cursor = None   # ✅ Initialize cursor1 before try
    cursor2 = None  # ✅ Initialize cursor2 before try
    cursor3 = None  # ✅ Initialize cursor3 before try
    conn = None     # ✅ Initialize connection before try
    
    try:
        data = request.json
        
        # Validation 1: Check if data exists
        if not data:
            return error_response("Request body is required", 400)
        
        # Validation 2: Check user_id
        valid, result = validate_user_id(data.get('user_id'))
        if not valid:
            return error_response(result, 400)
        user_id = result
        
        # Validation 3: Check files array
        files = data.get('files', [])
        if not isinstance(files, list):
            return error_response("files must be an array", 400)
        
        # Now safe to create database resources
        conn = get_database_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Validation 4: Check if folder exists and belongs to user
        cursor.execute("""
            SELECT id FROM ai_infrastructure.cloud_folders
            WHERE id = %s AND user_id = %s
        """, (folder_id, user_id))
        
        if not cursor.fetchone():
            # ✅ Close BEFORE early return
            cursor.close()
            cursor = None
            conn.close()
            conn = None
            return error_response("Folder not found or access denied", 404)
        
        # ✅ IMPORTANT: Close cursor1, create cursor2 for next operation
        cursor.close()
        cursor = None
        
        cursor2 = conn.cursor()
        
        # Get current file IDs in database
        cursor2.execute("""
            SELECT file_id FROM ai_infrastructure.cloud_folder_files
            WHERE folder_id = %s
        """, (folder_id,))
        
        existing_file_ids = {row[0] for row in cursor2.fetchall()}
        
        # ✅ IMPORTANT: Close cursor2, create cursor3 for next operation
        cursor2.close()
        cursor2 = None
        
        cursor3 = conn.cursor()
        
        new_file_ids = set()
        added_count = 0
        updated_count = 0
        
        # Upsert files
        for file in files:
            try:
                file_id = file.get('file_id')
                new_file_ids.add(file_id)
                
                cursor3.execute("""
                    INSERT INTO ai_infrastructure.cloud_folder_files
                    (folder_id, file_id, file_name, mime_type, size_bytes, modified_time, web_view_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (folder_id, file_id)
                    DO UPDATE SET
                        file_name = EXCLUDED.file_name,
                        mime_type = EXCLUDED.mime_type,
                        size_bytes = EXCLUDED.size_bytes,
                        modified_time = EXCLUDED.modified_time,
                        web_view_link = EXCLUDED.web_view_link
                    RETURNING (xmax = 0) as is_insert
                """, (
                    folder_id,
                    file_id,
                    file.get('file_name'),
                    file.get('mime_type'),
                    file.get('size'),
                    file.get('modified_time'),
                    file.get('web_view_link')
                ))
                
                result = cursor3.fetchone()
                if result and result[0]:  # is_insert = true
                    added_count += 1
                else:
                    updated_count += 1
                
            except Exception as file_error:
                print(f"❌ Failed to upsert file {file.get('file_id')}: {file_error}")
        
        # Remove files that no longer exist in Google Drive
        removed_file_ids = existing_file_ids - new_file_ids
        removed_count = 0
        
        if removed_file_ids:
            cursor3.execute("""
                DELETE FROM ai_infrastructure.cloud_folder_files
                WHERE folder_id = %s AND file_id = ANY(%s)
            """, (folder_id, list(removed_file_ids)))
            removed_count = cursor3.rowcount
        
        # Update folder's last_synced timestamp
        cursor3.execute("""
            UPDATE ai_infrastructure.cloud_folders
            SET last_synced = NOW()
            WHERE id = %s
        """, (folder_id,))
        
        conn.commit()
        
        # ✅ Close cursor3 BEFORE connection
        cursor3.close()
        cursor3 = None
        conn.close()
        conn = None
        
        return success_response({
            'folder_id': folder_id,
            'added_files': added_count,
            'updated_files': updated_count,
            'removed_files': removed_count
        }, "Folder refreshed successfully")
        
    except Exception as e:
        print(f"❌ [CLOUD SYNC] Error refreshing folder: {e}")
        import traceback
        traceback.print_exc()
        return error_response(f"Failed to refresh folder: {str(e)}", 500)
    
    finally:
        # ✅ Cleanup cursor1 independently
        if cursor:
            try:
                cursor.close()
            except:
                pass
        
        # ✅ Cleanup cursor2 independently
        if cursor2:
            try:
                cursor2.close()
            except:
                pass
        
        # ✅ Cleanup cursor3 independently
        if cursor3:
            try:
                cursor3.close()
            except:
                pass
        
        # ✅ Cleanup connection
        if conn:
            try:
                conn.close()
            except:
                pass

# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

print('✅ Session Management routes loaded')