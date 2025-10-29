"""
File Encoding Helpers
Base64 encoding, file validation, media type detection for file uploads
"""

import base64
from typing import Tuple, Optional


# Maximum file size (32MB)
MAX_FILE_SIZE = 32 * 1024 * 1024


class FileValidationError(Exception):
    """File validation error"""
    pass


def validate_file_size(filename: str, size: int, max_size: int = MAX_FILE_SIZE):
    """
    Validate file size
    
    Args:
        filename: File name
        size: File size in bytes
        max_size: Maximum allowed size
    
    Raises:
        FileValidationError if file too large
    """
    if size > max_size:
        raise FileValidationError(
            f"File '{filename}' is too large ({size} bytes). "
            f"Maximum size is {max_size} bytes ({max_size / (1024 * 1024):.1f} MB)"
        )


def guess_media_type(filename: str) -> str:
    """
    Guess media type from filename extension
    
    Args:
        filename: File name with extension
    
    Returns:
        MIME type string
    """
    filename_lower = filename.lower()
    
    # PDF
    if filename_lower.endswith('.pdf'):
        return 'application/pdf'
    
    # Images
    if filename_lower.endswith('.jpg') or filename_lower.endswith('.jpeg'):
        return 'image/jpeg'
    if filename_lower.endswith('.png'):
        return 'image/png'
    if filename_lower.endswith('.gif'):
        return 'image/gif'
    if filename_lower.endswith('.webp'):
        return 'image/webp'
    
    # Default
    return 'application/octet-stream'


def encode_bytes_to_base64(data: bytes) -> str:
    """
    Encode bytes to base64 string
    
    Args:
        data: Raw bytes
    
    Returns:
        Base64-encoded string
    """
    try:
        return base64.b64encode(data).decode('utf-8')
    except Exception as e:
        raise FileValidationError(f"Base64 encoding failed: {e}")


def decode_base64_to_bytes(data: str) -> bytes:
    """
    Decode base64 string to bytes
    
    Args:
        data: Base64-encoded string
    
    Returns:
        Raw bytes
    """
    try:
        return base64.b64decode(data)
    except Exception as e:
        raise FileValidationError(f"Base64 decoding failed: {e}")


def get_content_block_type(media_type: str) -> str:
    """
    Get Claude API content block type from media type
    
    Args:
        media_type: MIME type (e.g., 'application/pdf', 'image/jpeg')
    
    Returns:
        Content block type ('document' or 'image')
    """
    if media_type == 'application/pdf':
        return 'document'
    elif media_type.startswith('image/'):
        return 'image'
    else:
        # Default to document for unknown types
        return 'document'


def build_content_block(filename: str, data: bytes, media_type: Optional[str] = None) -> dict:
    """
    Build Claude API content block from file data
    
    Args:
        filename: File name
        data: Raw file bytes
        media_type: MIME type (will be guessed if None)
    
    Returns:
        Content block dictionary ready for Claude API
    """
    # Guess media type if not provided
    if not media_type:
        media_type = guess_media_type(filename)
    
    # Validate size
    validate_file_size(filename, len(data))
    
    # Encode to base64
    encoded_data = encode_bytes_to_base64(data)
    
    # Get block type
    block_type = get_content_block_type(media_type)
    
    # Build content block
    content_block = {
        'type': block_type,
        'source': {
            'type': 'base64',
            'media_type': media_type,
            'data': encoded_data
        }
    }
    
    return content_block


def process_file_uploads(files) -> list:
    """
    Process file uploads from Flask request
    
    Args:
        files: request.files.getlist('files')
    
    Returns:
        List of content blocks ready for Claude API
    """
    content_blocks = []
    
    for file in files:
        filename = getattr(file, 'filename', 'unknown')
        media_type = file.content_type
        
        # Read file bytes
        file_bytes = file.read()
        
        # Build content block
        content_block = build_content_block(filename, file_bytes, media_type)
        content_blocks.append(content_block)
        
        print(f"[FileEncoder] Processed {filename}: {len(file_bytes)} bytes, {media_type}")
    
    return content_blocks
