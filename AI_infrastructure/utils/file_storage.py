"""
File Storage Utility
Handles saving, retrieving, and managing uploaded files
"""

import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple
import sys
from pathlib import Path as PathLib

# Add parent directory to path for imports
sys.path.insert(0, str(PathLib(__file__).parent.parent))

try:
    from config.constants import UPLOAD_STORAGE_PATH, MAX_USER_STORAGE
except ModuleNotFoundError:
    # Fallback for when running from different directories
    UPLOAD_STORAGE_PATH = str(PathLib(__file__).parent.parent.parent / 'data' / 'uploads')
    MAX_USER_STORAGE = 500 * 1024 * 1024  # 500 MB


class FileStorageError(Exception):
    """Custom exception for file storage errors"""
    pass


def ensure_upload_directory(user_id: int, thread_id: str) -> Path:
    """
    Ensure upload directory exists for user/thread
    
    Args:
        user_id: User ID
        thread_id: Thread ID
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(UPLOAD_STORAGE_PATH) / f"user_{user_id}" / f"thread_{thread_id}"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_file_hash(file_data: bytes) -> str:
    """
    Calculate SHA256 hash of file data
    
    Args:
        file_data: File bytes
        
    Returns:
        Hex string of hash (first 16 characters)
    """
    return hashlib.sha256(file_data).hexdigest()[:16]


def save_uploaded_file(
    file_data: bytes,
    filename: str,
    content_type: str,
    user_id: int,
    thread_id: str
) -> Dict[str, any]:
    """
    Save uploaded file to storage
    
    Args:
        file_data: File bytes
        filename: Original filename
        content_type: MIME type
        user_id: User ID
        thread_id: Thread ID
        
    Returns:
        Dict with file metadata:
        {
            'filename': 'invoice.pdf',
            'server_path': '/uploads/user_14/thread_123/invoice_abc123.pdf',
            'size': 245678,
            'content_type': 'application/pdf',
            'uploaded_at': '2025-11-11T12:34:56',
            'file_hash': 'abc123...'
        }
        
    Raises:
        FileStorageError: If storage fails or quota exceeded
    """
    # Check user storage quota
    current_usage = get_user_storage_usage(user_id)
    if current_usage + len(file_data) > MAX_USER_STORAGE:
        raise FileStorageError(
            f"Storage quota exceeded. Using {current_usage / 1024 / 1024:.2f} MB of "
            f"{MAX_USER_STORAGE / 1024 / 1024:.2f} MB. Please delete old files."
        )
    
    # Ensure directory exists
    upload_dir = ensure_upload_directory(user_id, thread_id)
    
    # Generate unique filename with timestamp and hash
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_hash = get_file_hash(file_data)
    file_ext = Path(filename).suffix  # Preserve extension
    safe_name = Path(filename).stem[:50]  # Limit filename length
    unique_filename = f"{safe_name}_{timestamp}_{file_hash}{file_ext}"
    
    # Full path
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        with open(file_path, 'wb') as f:
            f.write(file_data)
    except Exception as e:
        raise FileStorageError(f"Failed to save file: {str(e)}")
    
    # Generate relative path for storage in database
    relative_path = f"/uploads/user_{user_id}/thread_{thread_id}/{unique_filename}"
    
    # Return metadata
    return {
        'filename': filename,
        'server_path': relative_path,
        'size': len(file_data),
        'content_type': content_type,
        'uploaded_at': datetime.now().isoformat(),
        'file_hash': file_hash
    }


def get_user_storage_usage(user_id: int) -> int:
    """
    Calculate total storage used by user
    
    Args:
        user_id: User ID
        
    Returns:
        Total bytes used
    """
    user_dir = Path(UPLOAD_STORAGE_PATH) / f"user_{user_id}"
    
    if not user_dir.exists():
        return 0
    
    total_size = 0
    for root, dirs, files in os.walk(user_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except OSError:
                continue  # Skip files we can't access
    
    return total_size


def get_file_path(server_path: str) -> Optional[Path]:
    """
    Convert server path to absolute file path
    
    Args:
        server_path: Relative path like '/uploads/user_14/thread_123/file.pdf'
        
    Returns:
        Absolute Path object, or None if file doesn't exist
    """
    # Remove leading /uploads/ to get relative path
    relative = server_path.replace('/uploads/', '')
    full_path = Path(UPLOAD_STORAGE_PATH) / relative
    
    if full_path.exists() and full_path.is_file():
        return full_path
    
    return None


def delete_file(server_path: str) -> bool:
    """
    Delete file from storage
    
    Args:
        server_path: Relative path like '/uploads/user_14/thread_123/file.pdf'
        
    Returns:
        True if deleted, False if file not found
    """
    file_path = get_file_path(server_path)
    
    if not file_path:
        return False
    
    try:
        file_path.unlink()
        return True
    except OSError:
        return False


def delete_thread_files(user_id: int, thread_id: str) -> int:
    """
    Delete all files for a thread
    
    Args:
        user_id: User ID
        thread_id: Thread ID
        
    Returns:
        Number of files deleted
    """
    thread_dir = Path(UPLOAD_STORAGE_PATH) / f"user_{user_id}" / f"thread_{thread_id}"
    
    if not thread_dir.exists():
        return 0
    
    count = 0
    for file in thread_dir.iterdir():
        if file.is_file():
            try:
                file.unlink()
                count += 1
            except OSError:
                continue
    
    # Remove empty directory
    try:
        thread_dir.rmdir()
    except OSError:
        pass  # Directory not empty or other error
    
    return count
