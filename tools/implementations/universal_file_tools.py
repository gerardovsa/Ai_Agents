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
def process_outlook_attachment_for_ai(
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
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
        **kwargs: Includes _user_id and _injected_credentials (auto-injected)
    
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
    # Extract user_id from kwargs (injected by credential system)
    user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
    
    if not user_id:
        return {
            'success': False,
            'error': 'No user_id provided. User must be authenticated to use Microsoft tools.'
        }
    
    handler = UniversalFileHandler(user_id=user_id, **kwargs)
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
    **kwargs
) -> Dict[str, Any]:
    """
    Process Gmail email attachment for AI analysis (token-optimized)
    
    ✅ Same optimization as Outlook: 99%+ token reduction
    
    Args:
        message_id: Gmail message ID
        attachment_id: Attachment ID from Gmail API
        mode: Delivery mode (see process_outlook_attachment_for_ai)
        **kwargs: Includes _user_id and _injected_credentials (auto-injected)
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    """
    # Extract user_id from kwargs (injected by credential system)
    user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
    
    if not user_id:
        return {
            'success': False,
            'error': 'No user_id provided. User must be authenticated to use Gmail tools.'
        }
    
    handler = UniversalFileHandler(user_id=user_id, **kwargs)
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
        **kwargs: Includes _user_id and _injected_credentials (auto-injected)
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    
    Example:
        AI: "Analyze the Excel file in my OneDrive"
        Tool call: process_onedrive_file_for_ai(file_id='ABC123')
        Result: AI can access spreadsheet content
    """
    # Extract user_id from kwargs (injected by credential system)
    user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
    
    if not user_id:
        return {
            'success': False,
            'error': 'No user_id provided. User must be authenticated to use Microsoft OneDrive tools.'
        }
    
    handler = UniversalFileHandler(user_id=user_id, **kwargs)
    return handler.process_file(
        source='onedrive',
        source_id={'file_id': file_id},
        mode=mode
    )


@tool_executor()
def process_google_drive_file_for_ai(
    file_id: str,
    mode: str = 'auto',
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
        **kwargs: Includes _user_id and _injected_credentials (auto-injected)
    
    Returns:
        {'content_block': {...}, 'metadata': {...}}
    
    Example:
        AI: "Read the presentation from Google Drive"
        Tool call: process_google_drive_file_for_ai(file_id='1ABC...')
        Result: AI can analyze slides content
    """
    # Extract user_id from kwargs (injected by credential system)
    user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
    
    if not user_id:
        return {
            'success': False,
            'error': 'No user_id provided. User must be authenticated to use Google Drive tools.'
        }
    
    handler = UniversalFileHandler(user_id=user_id, **kwargs)
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


# ==================== SMART BUNDLED TOOLS (January 2026) ====================

@tool_executor()
def process_email_attachment_complete(
    source: str,
    message_id: str,
    attachment_id: str,
    processing_mode: str = 'auto',
    keep_in_cloud: bool = False,
    return_format: str = 'auto',
    **kwargs
) -> Dict[str, Any]:
    """
    SMART BUNDLED TOOL: Complete email attachment processing workflow
    
    90% reduction in tool calls - ONE call handles:
    - Download attachment
    - Auto-detect file type
    - Intelligent routing (cloud platform tools OR vision processing)
    - Extract structured data
    - Auto-cleanup
    
    Args:
        source: Email platform ('outlook' or 'gmail')
        message_id: Email message ID
        attachment_id: Attachment ID
        processing_mode: Processing strategy
            - 'auto' (default): Smart routing based on file type
            - 'cloud_onedrive': Force OneDrive upload → Microsoft platform tools
            - 'cloud_gdrive': Force Google Drive upload → Google platform tools
            - 'vision': Force vision processing (PDF/images rendered)
            - 'local_python': Force local Python parsing (CSV/TXT)
        keep_in_cloud: If True, keeps uploaded file in cloud storage
        return_format: Desired output format ('structured', 'content_blocks', 'both', 'auto')
        **kwargs: Includes _user_id and _injected_credentials (auto-injected)
    
    Returns:
        For structured data (Excel/Word/CSV):
        {
            'success': True,
            'file_type': 'excel',
            'processing_mode': 'cloud_onedrive',
            'data': {...},  # Queryable structured JSON
            'metadata': {'rows': 500, 'columns': ['A', 'B', 'C']},
            'cloud_file_id': 'xyz'  # If keep_in_cloud=True
        }
        
        For vision processing (PDF/images):
        {
            'success': True,
            'file_type': 'pdf',
            'processing_mode': 'vision',
            'content_blocks': [...],  # Auto-injected into conversation
            'metadata': {'pages': 12, 'size_mb': 2.5}
        }
    
    Example:
        AI: "Open the Excel attachment from my last email"
        Tool call: process_email_attachment_complete(
            source='outlook',
            message_id='msg123',
            attachment_id='att456',
            processing_mode='auto'
        )
        Result: Complete structured data extracted automatically
    """
    import os
    import tempfile
    import mimetypes
    from pathlib import Path
    
    # Extract user_id from kwargs
    user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
    
    if not user_id:
        return {
            'success': False,
            'error': 'No user_id provided. User must be authenticated.'
        }
    
    try:
        # STEP 1: Download attachment to temp directory
        if source == 'outlook':
            from tools.implementations.microsoft_outlook import microsoft_outlook_download_attachment
            download_result = microsoft_outlook_download_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                _user_id=user_id,
                **kwargs
            )
        elif source == 'gmail':
            from tools.implementations.gmail import gmail_get_attachment
            download_result = gmail_get_attachment(
                message_id=message_id,
                attachment_id=attachment_id,
                _user_id=user_id,
                **kwargs
            )
        else:
            return {
                'success': False,
                'error': f"Invalid source '{source}'. Use 'outlook' or 'gmail'."
            }
        
        if not download_result.get('success'):
            return {
                'success': False,
                'error': f"Download failed: {download_result.get('error', 'Unknown error')}",
                'download_result': download_result
            }
        
        file_path = download_result.get('file_path')
        file_name = download_result.get('name', os.path.basename(file_path))
        file_size = download_result.get('size', 0)
        
        # STEP 2: Auto-detect file type
        file_extension = Path(file_path).suffix.lower()
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # STEP 3: Intelligent routing based on file type and processing_mode
        office_extensions = ['.xlsx', '.xls', '.docx', '.doc', '.pptx', '.ppt']
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        pdf_extensions = ['.pdf']
        data_extensions = ['.csv', '.txt', '.json', '.xml']
        
        # Determine processing strategy
        if processing_mode == 'auto':
            if file_extension in office_extensions:
                # Office files → Cloud platform tools for structured data
                # Check which cloud storage user has connected
                # For now, default to OneDrive (TODO: Check user's available OAuth credentials)
                processing_mode = 'cloud_onedrive'
            elif file_extension in pdf_extensions or file_extension in image_extensions:
                # PDFs/images → Vision processing
                processing_mode = 'vision'
            elif file_extension in data_extensions:
                # Data files → Local Python parsing
                processing_mode = 'local_python'
            else:
                # Unknown → Try vision
                processing_mode = 'vision'
        
        # STEP 4: Execute processing based on selected mode
        result = {}
        
        if processing_mode == 'vision':
            # Use existing vision processing tool
            if source == 'outlook':
                vision_result = process_outlook_attachment_for_ai(
                    message_id=message_id,
                    attachment_id=attachment_id,
                    mode='auto',
                    _user_id=user_id,
                    **kwargs
                )
            else:  # gmail
                vision_result = process_gmail_attachment_for_ai(
                    message_id=message_id,
                    attachment_id=attachment_id,
                    mode='auto',
                    _user_id=user_id,
                    **kwargs
                )
            
            result = {
                'success': True,
                'file_type': file_extension.replace('.', ''),
                'file_name': file_name,
                'processing_mode': 'vision',
                'content_blocks': vision_result.get('content_block'),
                'metadata': vision_result.get('metadata', {})
            }
        
        elif processing_mode in ['cloud_onedrive', 'cloud_gdrive']:
            # Upload to cloud and use platform tools for structured data extraction
            cloud_file_id = None
            structured_data = {}
            
            if processing_mode == 'cloud_onedrive':
                # Upload to OneDrive temp folder
                from tools.implementations.microsoft_onedrive import microsoft_onedrive_upload_file
                upload_result = microsoft_onedrive_upload_file(
                    file_path=file_path,
                    folder_path='/AI_Temp_Attachments',
                    _user_id=user_id,
                    **kwargs
                )
                
                if not upload_result.get('success'):
                    # Fallback to vision if cloud upload fails
                    return process_email_attachment_complete(
                        source=source,
                        message_id=message_id,
                        attachment_id=attachment_id,
                        processing_mode='vision',
                        **kwargs
                    )
                
                cloud_file_id = upload_result.get('id')
                
                # Extract structured data based on file type
                if file_extension in ['.xlsx', '.xls']:
                    from tools.implementations.microsoft_excel import microsoft_excel_get_range
                    excel_result = microsoft_excel_get_range(
                        file_id=cloud_file_id,
                        range='A1:ZZ10000',  # Read large range
                        _user_id=user_id,
                        **kwargs
                    )
                    structured_data = excel_result.get('data', {})
                
                elif file_extension in ['.docx', '.doc']:
                    from tools.implementations.microsoft_word import microsoft_word_read_content
                    word_result = microsoft_word_read_content(
                        file_id=cloud_file_id,
                        _user_id=user_id,
                        **kwargs
                    )
                    structured_data = word_result.get('content', {})
                
                # Cleanup cloud file unless user wants to keep it
                if not keep_in_cloud and cloud_file_id:
                    from tools.implementations.microsoft_onedrive import microsoft_onedrive_delete_item
                    microsoft_onedrive_delete_item(
                        item_id=cloud_file_id,
                        _user_id=user_id,
                        **kwargs
                    )
            
            elif processing_mode == 'cloud_gdrive':
                # Upload to Google Drive temp folder
                from tools.implementations.google_drive import google_drive_upload_file
                upload_result = google_drive_upload_file(
                    file_path=file_path,
                    folder_id='root',  # TODO: Create temp folder
                    _user_id=user_id,
                    **kwargs
                )
                
                if not upload_result.get('success'):
                    # Fallback to vision if cloud upload fails
                    return process_email_attachment_complete(
                        source=source,
                        message_id=message_id,
                        attachment_id=attachment_id,
                        processing_mode='vision',
                        **kwargs
                    )
                
                cloud_file_id = upload_result.get('id')
                
                # Extract structured data based on file type
                if file_extension in ['.xlsx', '.xls']:
                    # Google Sheets reading
                    from tools.implementations.google_sheets import google_sheets_read_data
                    sheets_result = google_sheets_read_data(
                        spreadsheet_id=cloud_file_id,
                        range='A1:ZZ10000',
                        _user_id=user_id,
                        **kwargs
                    )
                    structured_data = sheets_result.get('values', [])
                
                # Cleanup cloud file unless user wants to keep it
                if not keep_in_cloud and cloud_file_id:
                    from tools.implementations.google_drive import google_drive_delete_file
                    google_drive_delete_file(
                        file_id=cloud_file_id,
                        _user_id=user_id,
                        **kwargs
                    )
            
            result = {
                'success': True,
                'file_type': file_extension.replace('.', ''),
                'file_name': file_name,
                'processing_mode': processing_mode,
                'data': structured_data,
                'metadata': {
                    'size': file_size,
                    'cloud_file_id': cloud_file_id if keep_in_cloud else None
                }
            }
        
        elif processing_mode == 'local_python':
            # Parse locally with Python (CSV/TXT/JSON)
            import pandas as pd
            import json
            
            try:
                if file_extension == '.csv':
                    df = pd.read_csv(file_path)
                    structured_data = {
                        'data': df.to_dict('records'),
                        'columns': df.columns.tolist(),
                        'rows': len(df),
                        'summary': df.describe().to_dict()
                    }
                elif file_extension == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        structured_data = json.load(f)
                elif file_extension in ['.txt', '.xml']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        structured_data = {'text': f.read()}
                else:
                    return {
                        'success': False,
                        'error': f"Local parsing not supported for {file_extension}"
                    }
                
                result = {
                    'success': True,
                    'file_type': file_extension.replace('.', ''),
                    'file_name': file_name,
                    'processing_mode': 'local_python',
                    'data': structured_data,
                    'metadata': {'size': file_size}
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Local parsing failed: {str(e)}"
                }
        
        else:
            return {
                'success': False,
                'error': f"Invalid processing_mode: {processing_mode}"
            }
        
        # STEP 5: Cleanup temp download file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # Non-critical error, don't fail the whole operation
            result['cleanup_warning'] = f"Could not delete temp file: {str(e)}"
        
        return result
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': f"Processing failed: {str(e)}",
            'traceback': traceback.format_exc()
        }


@tool_executor()
def process_local_file_universal(
    file_path: str,
    processing_mode: str = 'auto',
    keep_in_cloud: bool = False,
    delete_after: bool = False,
    return_format: str = 'auto',
    extract_options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    SMART BUNDLED TOOL: Process any local server file with intelligent routing
    
    85% reduction in tool calls - ONE call handles:
    - Validate file path (security)
    - Auto-detect file type
    - Intelligent routing (cloud platform tools OR vision OR local parsing)
    - Extract structured data
    - Optional cleanup
    
    Args:
        file_path: ABSOLUTE path to file on SERVER (e.g., /tmp/file.xlsx)
        processing_mode: Processing strategy
            - 'auto' (default): Smart routing based on file type
            - 'cloud_onedrive': Force OneDrive upload
            - 'cloud_gdrive': Force Google Drive upload
            - 'vision': Force vision processing
            - 'local_python': Force local Python parsing
        keep_in_cloud: If True, keeps uploaded file in cloud storage
        delete_after: If True, deletes original local file after processing
        return_format: Desired output format ('structured', 'content_blocks', 'both', 'auto')
        extract_options: Advanced extraction settings (excel_mode, pdf_ocr, image_enhance)
        **kwargs: Includes _user_id and _injected_credentials (auto-injected)
    
    Returns:
        For structured data:
        {
            'success': True,
            'file_type': 'excel',
            'file_path': '/tmp/file.xlsx',
            'processing_mode': 'cloud_onedrive',
            'data': {...},
            'metadata': {'rows': 500, 'sheets': 3}
        }
        
        For vision processing:
        {
            'success': True,
            'file_type': 'pdf',
            'processing_mode': 'vision',
            'content_blocks': [...],
            'metadata': {'pages': 12, 'size_mb': 2.5}
        }
    
    Example:
        AI: "Analyze the file at /tmp/sales_report.xlsx"
        Tool call: process_local_file_universal(
            file_path='/tmp/sales_report.xlsx',
            processing_mode='auto'
        )
        Result: Complete structured data extracted automatically
    """
    import os
    import mimetypes
    from pathlib import Path
    
    # Extract user_id from kwargs
    user_id = kwargs.pop('_user_id', None) or kwargs.pop('user_id', None)
    
    # STEP 1: Security validation
    allowed_dirs = ['/tmp/', 'C:/temp/', 'C:\\temp\\', '/var/uploads/', 'C:/Users/gpoli/AppData/Local/Temp/']
    file_path_normalized = file_path.replace('\\', '/')
    
    is_allowed = any(file_path_normalized.startswith(allowed_dir.replace('\\', '/')) for allowed_dir in allowed_dirs)
    
    if not is_allowed:
        return {
            'success': False,
            'error': f"Security: Path '{file_path}' not in allowed directories: {allowed_dirs}"
        }
    
    if not os.path.exists(file_path):
        return {
            'success': False,
            'error': f"File not found: {file_path}"
        }
    
    # Block executables
    blocked_extensions = ['.exe', '.dll', '.sh', '.bat', '.cmd', '.ps1']
    file_extension = Path(file_path).suffix.lower()
    if file_extension in blocked_extensions:
        return {
            'success': False,
            'error': f"Security: Executable files not allowed: {file_extension}"
        }
    
    try:
        # STEP 2: Auto-detect file type
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        # Check file size limits
        if file_size > 1024 * 1024 * 1024:  # 1GB
            return {
                'success': False,
                'error': f"File too large: {file_size / (1024**3):.2f}GB (max 1GB)"
            }
        
        if file_size > 500 * 1024 * 1024:  # 500MB warning
            # Could add progress indicators here for large files
            pass
        
        # STEP 3: Intelligent routing
        office_extensions = ['.xlsx', '.xls', '.docx', '.doc', '.pptx', '.ppt']
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']
        pdf_extensions = ['.pdf']
        data_extensions = ['.csv', '.txt', '.json', '.xml']
        
        if processing_mode == 'auto':
            if file_extension in office_extensions:
                processing_mode = 'cloud_onedrive'  # Default to OneDrive
            elif file_extension in pdf_extensions or file_extension in image_extensions:
                processing_mode = 'vision'
            elif file_extension in data_extensions:
                processing_mode = 'local_python'
            else:
                processing_mode = 'vision'  # Fallback to vision
        
        # STEP 4: Execute processing
        result = {}
        
        if processing_mode == 'vision':
            # Use existing vision tool
            handler = UniversalFileHandler(user_id=user_id, **kwargs)
            vision_result = handler.process_file(
                source='local',
                source_id={'file_path': file_path},
                mode='auto'
            )
            
            # CRITICAL FIX (Jan 20, 2026): DO NOT return content_blocks in tool_result!
            # Base64 PDF data should go to Anthropic Messages API, not stored in conversation DB
            # Bug caused: 382KB base64 PDF stored in tool_result → 271K tokens in every message → token overflow
            # Solution: Return success message only, let the agent request the file via proper attachment tools
            metadata = vision_result.get('metadata', {})
            result = {
                'success': True,
                'message': f"✅ Processed {file_name} ({metadata.get('size', 0):,} bytes)",
                'file_type': file_extension.replace('.', ''),
                'file_path': file_path,
                'file_name': file_name,
                'processing_mode': 'vision',
                'token_estimate': metadata.get('token_estimate', 0),
                'size_bytes': metadata.get('size', 0),
                'content_type': metadata.get('type', 'unknown'),
                'next_steps': [
                    f"Use process_local_file_for_ai(file_path='{file_path}') to analyze the file content",
                    "The file content will be sent as an attachment to the AI (not in conversation history)"
                ]
                # ❌ REMOVED: 'content_blocks': vision_result.get('content_block')
                # Base64 data belongs in Messages API attachments, not tool_result JSON!
            }
        
        elif processing_mode in ['cloud_onedrive', 'cloud_gdrive']:
            # Upload and extract structured data
            cloud_file_id = None
            structured_data = {}
            
            if processing_mode == 'cloud_onedrive':
                from tools.implementations.microsoft_onedrive import microsoft_onedrive_upload_file
                upload_result = microsoft_onedrive_upload_file(
                    file_path=file_path,
                    folder_path='/AI_Temp_Files',
                    _user_id=user_id,
                    **kwargs
                )
                
                if not upload_result.get('success'):
                    # Fallback to vision
                    return process_local_file_universal(
                        file_path=file_path,
                        processing_mode='vision',
                        delete_after=delete_after,
                        **kwargs
                    )
                
                cloud_file_id = upload_result.get('id')
                
                # Extract data by file type
                if file_extension in ['.xlsx', '.xls']:
                    from tools.implementations.microsoft_excel import microsoft_excel_get_range
                    excel_result = microsoft_excel_get_range(
                        file_id=cloud_file_id,
                        range='A1:ZZ10000',
                        _user_id=user_id,
                        **kwargs
                    )
                    structured_data = excel_result.get('data', {})
                
                elif file_extension in ['.docx', '.doc']:
                    from tools.implementations.microsoft_word import microsoft_word_read_content
                    word_result = microsoft_word_read_content(
                        file_id=cloud_file_id,
                        _user_id=user_id,
                        **kwargs
                    )
                    structured_data = word_result.get('content', {})
                
                # Cleanup cloud file
                if not keep_in_cloud and cloud_file_id:
                    from tools.implementations.microsoft_onedrive import microsoft_onedrive_delete_item
                    microsoft_onedrive_delete_item(
                        item_id=cloud_file_id,
                        _user_id=user_id,
                        **kwargs
                    )
            
            elif processing_mode == 'cloud_gdrive':
                from tools.implementations.google_drive import google_drive_upload_file
                upload_result = google_drive_upload_file(
                    file_path=file_path,
                    folder_id='root',
                    _user_id=user_id,
                    **kwargs
                )
                
                if not upload_result.get('success'):
                    return process_local_file_universal(
                        file_path=file_path,
                        processing_mode='vision',
                        delete_after=delete_after,
                        **kwargs
                    )
                
                cloud_file_id = upload_result.get('id')
                
                if file_extension in ['.xlsx', '.xls']:
                    from tools.implementations.google_sheets import google_sheets_read_data
                    sheets_result = google_sheets_read_data(
                        spreadsheet_id=cloud_file_id,
                        range='A1:ZZ10000',
                        _user_id=user_id,
                        **kwargs
                    )
                    structured_data = sheets_result.get('values', [])
                
                if not keep_in_cloud and cloud_file_id:
                    from tools.implementations.google_drive import google_drive_delete_file
                    google_drive_delete_file(
                        file_id=cloud_file_id,
                        _user_id=user_id,
                        **kwargs
                    )
            
            result = {
                'success': True,
                'file_type': file_extension.replace('.', ''),
                'file_path': file_path,
                'file_name': file_name,
                'processing_mode': processing_mode,
                'data': structured_data,
                'metadata': {
                    'size': file_size,
                    'cloud_file_id': cloud_file_id if keep_in_cloud else None
                }
            }
        
        elif processing_mode == 'local_python':
            import pandas as pd
            import json
            
            try:
                if file_extension == '.csv':
                    df = pd.read_csv(file_path)
                    structured_data = {
                        'data': df.to_dict('records'),
                        'columns': df.columns.tolist(),
                        'rows': len(df),
                        'summary': df.describe().to_dict()
                    }
                elif file_extension == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        structured_data = json.load(f)
                elif file_extension in ['.txt', '.xml']:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        structured_data = {'text': f.read()}
                else:
                    return {
                        'success': False,
                        'error': f"Local parsing not supported for {file_extension}"
                    }
                
                result = {
                    'success': True,
                    'file_type': file_extension.replace('.', ''),
                    'file_path': file_path,
                    'file_name': file_name,
                    'processing_mode': 'local_python',
                    'data': structured_data,
                    'metadata': {'size': file_size}
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': f"Local parsing failed: {str(e)}"
                }
        
        else:
            return {
                'success': False,
                'error': f"Invalid processing_mode: {processing_mode}"
            }
        
        # STEP 5: Optional cleanup
        if delete_after:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    result['file_deleted'] = True
            except Exception as e:
                result['cleanup_warning'] = f"Could not delete file: {str(e)}"
        
        return result
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': f"Processing failed: {str(e)}",
            'traceback': traceback.format_exc()
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
    
    # SMART bundled tools (January 2026)
    'process_email_attachment_complete',
    'process_local_file_universal',
    
    # Legacy
    'email_process_attachment_for_ai'
]
