"""
File Encoding Helpers
Base64 encoding, file validation, media type detection for file uploads

Delivery methods:
  base64 inline  - PDF, JPEG, PNG, GIF, WebP  (Claude-native, up to 5-32 MB)
  text extract   - DOCX, XLSX, PPTX, CSV, TXT, MD, JSON, XML, HTML, code files
                   (uses TextExtractor -- no base64 overhead, up to 20 MB)
"""

import base64
from typing import Tuple, Optional


# Maximum file size default (32 MB)
MAX_FILE_SIZE = 32 * 1024 * 1024

# File types delivered via text extraction rather than base64.
# Processed by AI_infrastructure.core.text_extractor and returned as
# {'type': 'text', 'text': '<markdown content>'} blocks.
TEXT_EXTRACTABLE_TYPES = {
    # Word / document
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/msword',                                                        # .doc
    'application/vnd.oasis.opendocument.text',                                  # .odt
    'application/rtf',                                                           # .rtf
    'text/rtf',
    # Spreadsheet
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',        # .xlsx
    'application/vnd.ms-excel',                                                 # .xls
    'text/csv',
    'application/csv',
    # Presentation
    'application/vnd.openxmlformats-officedocument.presentationml.presentation', # .pptx
    'application/vnd.ms-powerpoint',                                             # .ppt
    # Data / markup
    'application/json',
    'application/xml',
    'text/xml',
    'application/yaml',
    'text/yaml',
    # Plain text and code
    'text/plain',
    'text/markdown',
    'text/html',
    'text/javascript',
    'application/javascript',
    'text/typescript',
    'text/x-python',
    'application/x-python-code',
}

# Per-type upload size limits
_IMAGE_MAX_SIZE = 5 * 1024 * 1024   # 5 MB for images
_TEXT_MAX_SIZE  = 20 * 1024 * 1024  # 20 MB for text-extractable (no base64 stored in DB)


class FileValidationError(Exception):
    """File validation error"""
    pass


def get_max_size_for_type(media_type: str) -> int:
    """Return the maximum allowed upload size for a given MIME type."""
    if media_type and media_type.startswith('image/'):
        return _IMAGE_MAX_SIZE
    if media_type in TEXT_EXTRACTABLE_TYPES:
        return _TEXT_MAX_SIZE
    return MAX_FILE_SIZE  # PDF / unknown


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
    Guess media type from filename extension.
    Covers all Claude-native types plus text-extractable office and code formats.

    Args:
        filename: File name with extension

    Returns:
        MIME type string
    """
    fn = filename.lower()
    ext_map = {
        # Claude-native (base64 inline)
        '.pdf':  'application/pdf',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png':  'image/png',
        '.gif':  'image/gif',
        '.webp': 'image/webp',
        # Office documents (text extraction)
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.doc':  'application/msword',
        '.odt':  'application/vnd.oasis.opendocument.text',
        '.rtf':  'application/rtf',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.xls':  'application/vnd.ms-excel',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.ppt':  'application/vnd.ms-powerpoint',
        # Data / markup
        '.csv':  'text/csv',
        '.json': 'application/json',
        '.xml':  'application/xml',
        '.yaml': 'application/yaml',
        '.yml':  'application/yaml',
        # Text / code
        '.txt':  'text/plain',
        '.md':   'text/markdown',
        '.html': 'text/html',
        '.htm':  'text/html',
        '.js':   'text/javascript',
        '.jsx':  'text/javascript',
        '.ts':   'text/typescript',
        '.tsx':  'text/typescript',
        '.py':   'text/x-python',
        '.css':  'text/plain',
        '.sh':   'text/plain',
    }
    for ext, mime in ext_map.items():
        if fn.endswith(ext):
            return mime
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
    Get Claude API content block type from media type.

    Returns:
      'image'    - sent as base64 image block  (JPEG, PNG, GIF, WebP)
      'document' - sent as base64 document block (PDF)
      'extract'  - text must be extracted first; handled by _build_text_extraction_block()
    """
    if media_type == 'application/pdf':
        return 'document'
    elif media_type and media_type.startswith('image/'):
        return 'image'
    elif media_type in TEXT_EXTRACTABLE_TYPES:
        return 'extract'
    else:
        return 'document'  # unknown binary - best-effort document block


def _build_text_extraction_block(filename: str, data: bytes, media_type: str) -> dict:
    """
    Extract text from an office/text file and return a Claude text content block.
    Uses AI_infrastructure.core.text_extractor.TextExtractor.

    Returns:
        {'type': 'text', 'text': '<markdown-formatted content>'}
    """
    try:
        from AI_infrastructure.core.text_extractor import get_text_extractor
        extractor = get_text_extractor()

        result = extractor.extract_text(
            file_data=data,
            content_type=media_type,
            filename=filename,
            max_chars=50000,
            output_format='markdown'
        )

        if not result['success']:
            raise FileValidationError(
                f"Text extraction failed for '{filename}': {result.get('error', 'unknown error')}"
            )

        word_count = result['metadata'].get('word_count', 0)
        size_kb = len(data) / 1024
        formatted = (
            f"# {filename}\n\n"
            f"**Type:** {media_type}  \n"
            f"**Size:** {size_kb:.1f} KB  \n"
            f"**Words:** {word_count:,}\n\n"
            f"---\n\n"
            f"{result['text']}"
        ).strip()

        print(f"[FileEncoder] Extracted text from {filename}: {word_count:,} words ({size_kb:.0f} KB source)")
        return {'type': 'text', 'text': formatted}

    except FileValidationError:
        raise
    except Exception as e:
        raise FileValidationError(f"Could not extract text from '{filename}': {e}")


def build_content_block(filename: str, data: bytes, media_type: Optional[str] = None) -> dict:
    """
    Build Claude API content block from file data.

    Routing:
      PDF / images           -> base64 inline block (Claude native)
      DOCX/XLSX/CSV/TXT etc. -> text extraction block (no base64 overhead)
      Unknown binary         -> base64 document block (best effort)

    Args:
        filename: File name
        data: Raw file bytes
        media_type: MIME type (will be guessed from extension if None)

    Returns:
        Content block dictionary ready for Claude API
    """
    # Guess media type if not provided
    if not media_type:
        media_type = guess_media_type(filename)

    # Normalise non-standard MIME aliases that some browsers report
    if media_type == 'image/jpg':
        media_type = 'image/jpeg'
    # Browsers often report generic type for known extensions - override with extension
    if media_type in ('application/octet-stream', ''):
        guessed = guess_media_type(filename)
        if guessed != 'application/octet-stream':
            media_type = guessed
            print(f"[FileEncoder] Overrode generic MIME with extension-guessed type: {media_type}")

    # Validate size using per-type limit
    validate_file_size(filename, len(data), max_size=get_max_size_for_type(media_type))

    # Route to appropriate block builder
    block_type = get_content_block_type(media_type)

    if block_type == 'extract':
        return _build_text_extraction_block(filename, data, media_type)

    # Base64 path (image or document)
    encoded_data = encode_bytes_to_base64(data)

    # Build content block - aligned with Anthropic Messages API spec
    # Images: https://docs.anthropic.com/en/docs/build-with-claude/vision
    # PDFs:   https://docs.anthropic.com/en/docs/build-with-claude/pdf-support
    content_block: dict = {
        'type': block_type,
        'source': {
            'type': 'base64',
            'media_type': media_type,
            'data': encoded_data
        }
    }

    # Optional title field for document blocks (improves context for Claude)
    if block_type == 'document' and filename and filename != 'unknown':
        content_block['title'] = filename

    return content_block


def process_file_uploads(files) -> list:
    """
    Process file uploads from Flask request

    Args:
        files: request.files.getlist('files')

    Returns:
        List of content blocks ready for Claude API
        Each block is one of: image, document, or text (extracted)
    """
    content_blocks = []

    for file in files:
        filename = getattr(file, 'filename', 'unknown')
        media_type = getattr(file, 'content_type', None) or ''

        try:
            # Read file bytes
            file_bytes = file.read()

            if not file_bytes:
                print(f"[FileEncoder] WARNING: {filename} is empty -- skipping")
                continue

            # Build content block (routes to extraction or base64 automatically)
            content_block = build_content_block(filename, file_bytes, media_type or None)
            content_blocks.append(content_block)

            print(f"[FileEncoder] Processed {filename}: {len(file_bytes):,} bytes, {media_type}, type={content_block['type']}")

        except FileValidationError as e:
            print(f"[FileEncoder] Validation error for {filename}: {e}")
            raise
        except Exception as e:
            print(f"[FileEncoder] Unexpected error for {filename}: {e}")
            raise FileValidationError(f"Failed to process file '{filename}': {e}")

    return content_blocks