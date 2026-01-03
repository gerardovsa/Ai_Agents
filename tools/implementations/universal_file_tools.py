"""
FILE PROCESSING TOOLS - Universal File Processing for AI
=========================================================

Process files from ANY source (email, cloud storage, local) for AI consumption.
Token-optimized to prevent context overflow.

Supported Sources:
- Outlook/Gmail attachments
- OneDrive files
- Google Drive files
- SharePoint files
- Local filesystem
- Direct uploads (bytes)

All tools use the UniversalFileHandler to provide consistent behavior:
- Automatic method selection (direct base64 / Files API / text extraction)
- Token optimization (99%+ reduction vs raw base64)
- Native Anthropic content block format

Usage Pattern (AI calls these):
    process_SOURCENAME_file_for_ai(source_params...)
    → Returns content_block ready for Claude
"""

from typing import Dict, Any, List, Optional
from AI_infrastructure.core.universal_file_handler import UniversalFileHandler
from tools.registry_v3 import tool_executor


# ==================== EMAIL ATTACHMENTS ====================

@tool_executor()
@tool_executor()
def process_outlook_attachment_for_ai(
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    _user_id: Optional[int] = None,
    _injected_credentials: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Process Outlook email attachment for AI analysis (token-optimized)
    
    ✅ Prevents token overflow: 691KB PDF = ~800 tokens (not 230,000!)
    
    Args:
        message_id: Outlook message ID
        attachment_id: Attachment ID from Outlook API
        mode: Delivery mode
            - 'auto' (default): Smart detection based on size/type
            - 'direct': Force base64 content block
            - 'files_api': Force Anthropic Files API upload
            - 'extract': Force text extraction (for DOCX/XLSX/PPTX)
        _user_id: User ID (injected by credential_injector)
        _injected_credentials: Credentials injection flag
    
    Returns:
        {
            'success': True,
            'method': 'direct' | 'files_api' | 'extract',
            'content_block': {'type': 'document', 'source': {...}},
            'metadata': {
                'name': 'report.pdf',
                'size': 707584,
                'token_estimate': 800
            }
        }
    
    Example:
        AI: "Download the PDF from my last email"
        Tool call: process_outlook_attachment_for_ai(msg_id, att_id)
        Result: Content block automatically accessible to AI
        AI: "I can see the Q4 report shows revenue of $2.5M..."
    """
    # Remove user_id from kwargs to avoid "multiple values" error
    kwargs.pop('user_id', None)
    handler = UniversalFileHandler(user_id=_user_id, **kwargs)
    return handler.process_file(
        source='outlook',
        source_id={'message_id': message_id, 'attachment_id': attachment_id},
        mode=mode
    )


@tool_executor()
def process_gmail_attachment_for_ai(
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    _user_id: Optional[int] = None,
    _injected_credentials: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Process Gmail email attachment for AI analysis (token-optimized)
    
    ✅ Same optimization as Outlook: 99%+ token reduction
    
    Args:
        message_id: Gmail message ID
        attachment_id: Attachment ID from Gmail API
        mode: Delivery mode (see process_outlook_attachment_for_ai)
        _user_id: User ID (injected by credential_injector)
        _injected_credentials: Credentials injection flag
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    """
    # Remove user_id from kwargs to avoid "multiple values" error
    kwargs.pop('user_id', None)
    handler = UniversalFileHandler(user_id=_user_id, **kwargs)
    return handler.process_file(
        source='gmail',
        source_id={'message_id': message_id, 'attachment_id': attachment_id},
        mode=mode
    )


# ==================== CLOUD STORAGE ====================

@tool_executor()
def process_onedrive_file_for_ai(
    file_id: str,
    mode: str = 'auto',
    _user_id: Optional[int] = None,
    _injected_credentials: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Process OneDrive file for AI analysis (token-optimized)
    
    Works with:
    - Personal OneDrive files
    - Business/SharePoint files via OneDrive API
    
    Args:
        file_id: OneDrive item ID (from microsoft_onedrive_list_files)
        mode: Delivery mode
            - 'auto': Smart detection
            - 'direct': Base64 content block (< 5MB)
            - 'extract': Text extraction (DOCX/XLSX/PPTX)
        _user_id: User ID (injected by credential_injector)
        _injected_credentials: Credentials injection flag
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    
    Example:
        AI: "Analyze the Excel file in my OneDrive"
        Tool call: process_onedrive_file_for_ai(file_id='ABC123')
        Result: AI can access spreadsheet content
    """
    # Remove user_id from kwargs to avoid "multiple values" error
    kwargs.pop('user_id', None)
    handler = UniversalFileHandler(user_id=_user_id, **kwargs)
    return handler.process_file(
        source='onedrive',
        source_id={'file_id': file_id},
        mode=mode
    )


@tool_executor()
def process_google_drive_file_for_ai(
    file_id: str,
    mode: str = 'auto',
    _user_id: Optional[int] = None,
    _injected_credentials: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Process Google Drive file for AI analysis (token-optimized)
    
    Works with:
    - Google Drive personal files
    - Shared Drive files
    - Google Workspace files (Docs/Sheets/Slides exported)
    
    Args:
        file_id: Google Drive file ID (from google_drive_list_files)
        mode: Delivery mode (see process_onedrive_file_for_ai)
        _user_id: User ID (injected by credential_injector)
        _injected_credentials: Credentials injection flag
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    
    Example:
        AI: "Read the presentation from Google Drive"
        Tool call: process_google_drive_file_for_ai(file_id='1ABC...')
        Result: AI can analyze slides content
    """
    # Remove user_id from kwargs to avoid "multiple values" error
    kwargs.pop('user_id', None)
    handler = UniversalFileHandler(user_id=_user_id, **kwargs)
    return handler.process_file(
        source='google_drive',
        source_id={'file_id': file_id},
        mode=mode
    )


# ==================== LOCAL FILESYSTEM ====================

@tool_executor()
def process_local_file_for_ai(
    file_path: str,
    mode: str = 'auto'
) -> Dict[str, Any]:
    """
    Process local file for AI analysis (token-optimized)
    
    ⚠️ Security: File must be on server filesystem, not user's local machine
    
    Works with:
    - Server-side temp files
    - Uploaded files saved to disk
    - Files in designated upload directories
    
    Args:
        file_path: Absolute path to file on server
            Examples:
            - Windows: C:/temp/uploads/report.pdf
            - Linux: /var/uploads/document.docx
        mode: Delivery mode (see process_onedrive_file_for_ai)
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    
    Example:
        AI: "Analyze the file at C:/temp/uploads/invoice.pdf"
        Tool call: process_local_file_for_ai(file_path='C:/temp/uploads/invoice.pdf')
        Result: AI can read invoice content
    
    Security Notes:
        - Only files on SERVER filesystem (not user's local machine)
        - Path validation recommended in production
        - Consider restricting to specific directories
    """
    handler = UniversalFileHandler()
    return handler.process_file(
        source='local',
        source_id={'file_path': file_path},
        mode=mode
    )


# ==================== DIRECT UPLOAD ====================

@tool_executor()
def process_uploaded_file_for_ai(
    file_data: bytes,
    filename: str,
    content_type: str = 'application/octet-stream',
    mode: str = 'auto'
) -> Dict[str, Any]:
    """
    Process directly uploaded file bytes for AI analysis (token-optimized)
    
    Use when:
    - Receiving file uploads via HTTP POST
    - Processing in-memory file data
    - No intermediate storage needed
    
    Args:
        file_data: Raw file bytes
        filename: Original filename (for type detection)
        content_type: MIME type (e.g., 'application/pdf', 'image/jpeg')
        mode: Delivery mode (see process_onedrive_file_for_ai)
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    
    Example (from Flask route):
        @app.route('/api/analyze-upload', methods=['POST'])
        def analyze_upload():
            file = request.files['document']
            result = process_uploaded_file_for_ai(
                file_data=file.read(),
                filename=file.filename,
                content_type=file.content_type
            )
            return jsonify(result)
    """
    handler = UniversalFileHandler()
    return handler.process_file(
        source='bytes',
        source_id={
            'data': file_data,
            'filename': filename,
            'content_type': content_type
        },
        mode=mode
    )


# ==================== BATCH PROCESSING ====================

@tool_executor()
def process_multiple_files_for_ai(
    files: List[Dict[str, str]],
    mode: str = 'auto'
) -> Dict[str, Any]:
    """
    Process multiple files at once (batch operation)
    
    Optimized for:
    - Email threads with multiple attachments
    - Folder downloads
    - Bulk document analysis
    
    Args:
        files: List of file specifications
            [
                {'source': 'outlook', 'message_id': '...', 'attachment_id': '...'},
                {'source': 'gmail', 'message_id': '...', 'attachment_id': '...'},
                {'source': 'onedrive', 'file_id': '...'},
                {'source': 'local', 'file_path': 'C:/temp/file.pdf'}
            ]
        mode: Delivery mode applied to all files
    
    Returns:
        {
            'success': True,
            'results': [
                {'file': 'report.pdf', 'method': 'direct', ...},
                {'file': 'image.jpg', 'method': 'direct', ...}
            ],
            'total_token_estimate': 1600,
            'content_blocks': [...]  # All content blocks ready for AI
        }
    
    Example:
        AI: "Analyze all attachments from my last 3 emails"
        Tool call: process_multiple_files_for_ai([
            {'source': 'outlook', 'message_id': 'msg1', 'attachment_id': 'att1'},
            {'source': 'outlook', 'message_id': 'msg1', 'attachment_id': 'att2'},
            {'source': 'outlook', 'message_id': 'msg2', 'attachment_id': 'att3'}
        ])
        Result: AI can analyze all 3 attachments together
    """
    handler = UniversalFileHandler()
    return handler.process_batch(files=files, mode=mode)


# ==================== LEGACY COMPATIBILITY ====================
# Aliases for existing tools (backward compatibility)

@tool_executor()
def email_process_attachment_for_ai(
    source: str,
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    _user_id: Optional[int] = None,
    _injected_credentials: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Universal email attachment processor (legacy compatibility)
    
    ⚠️ DEPRECATED: Use source-specific tools instead:
    - process_outlook_attachment_for_ai()
    - process_gmail_attachment_for_ai()
    
    Args:
        source: 'outlook' or 'gmail'
        message_id: Email message ID
        attachment_id: Attachment ID
        mode: Delivery mode
        _user_id: User ID (injected by credential_injector)
        _injected_credentials: Credentials injection flag
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    """
    if source == 'outlook':
        return process_outlook_attachment_for_ai(
            message_id, attachment_id, mode,
            _user_id=_user_id, _injected_credentials=_injected_credentials, **kwargs
        )
    elif source == 'gmail':
        return process_gmail_attachment_for_ai(
            message_id, attachment_id, mode,
            _user_id=_user_id, _injected_credentials=_injected_credentials, **kwargs
        )
    else:
        return {
            'success': False,
            'error': f"Invalid source '{source}'. Use 'outlook' or 'gmail'"
        }


# Export all tools
__all__ = [
    # Email
    'process_outlook_attachment_for_ai',
    'process_gmail_attachment_for_ai',
    
    # Cloud storage
    'process_onedrive_file_for_ai',
    'process_google_drive_file_for_ai',
    
    # Local
    'process_local_file_for_ai',
    
    # Direct upload
    'process_uploaded_file_for_ai',
    
    # Batch
    'process_multiple_files_for_ai',
    
    # Legacy
    'email_process_attachment_for_ai'
]
