"""
EMAIL ATTACHMENT TOOLS - Universal Email Attachment Processing
===============================================================

Unified attachment handling for ALL email platforms (Outlook, Gmail, Exchange).
These tools connect to the UniversalFileHandler to prevent token overflow.

✅ TOKEN OPTIMIZATION:
- Small images (< 5MB): Direct base64 → ~800 tokens/MB
- Large files (5-100MB): Files API → ~50 tokens
- Huge/unsupported (>100MB): Cloud URL → 0 tokens

OLD METHOD (BROKEN):
    outlook_download_attachment(msg_id, att_id)
    → Returns 27k tokens for 82KB PNG
    → Causes token overflow in conversation

NEW METHOD (OPTIMIZED):
    email_process_attachment_for_ai(source='outlook', message_id=..., attachment_id=...)
    → Returns content_block ready for Anthropic
    → 97-99.99% token reduction

USAGE:
    # Single attachment
    result = email_process_attachment_for_ai(
        source='outlook',
        message_id='AAMkAG...',
        attachment_id='AAMkAH...',
        mode='auto'  # Smart detection
    )
    
    # Multiple attachments
    result = email_process_attachments_batch(
        source='gmail',
        attachments=[
            {'message_id': 'msg1', 'attachment_id': 'att1'},
            {'message_id': 'msg1', 'attachment_id': 'att2'}
        ]
    )
"""

from typing import Dict, Any, List, Optional
from AI_infrastructure.core.universal_file_handler import UniversalFileHandler
import base64
import tempfile
import os


def email_process_attachment_for_ai(
    source: str,
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    **kwargs
) -> Dict[str, Any]:
    """
    Process email attachment for AI consumption (Outlook or Gmail)
    
    ✅ OPTIMIZED: Auto-detects best delivery method to prevent token overflow
    
    Args:
        source: Email platform ('outlook' or 'gmail')
        message_id: Email message ID
        attachment_id: Attachment ID from email API
        mode: Delivery mode
            - 'auto' (default): Smart detection based on size/type
            - 'direct': Force base64 content block
            - 'files_api': Force Anthropic Files API upload
            - 'url': Force cloud storage URL
        **kwargs: Additional parameters (user_id, credentials, etc.)
    
    Returns:
        {
            'success': True,
            'method': 'direct' | 'files_api' | 'url',
            'content_block': {...},  # For Anthropic Messages API
            'url': 'https://...',    # For URL method
            'metadata': {
                'name': 'document.pdf',
                'size': 123456,
                'type': 'application/pdf',
                'token_estimate': 800,
                'source': 'outlook'
            }
        }
    
    Example (Outlook):
        # Old method (BROKEN - 27k tokens for 82KB image):
        result = outlook_download_attachment(msg_id, att_id)
        # Returns: {'content': 'iVBORw0KGgo...', 'size': 81991}
        
        # New method (OPTIMIZED - 267 tokens for 82KB image):
        result = email_process_attachment_for_ai('outlook', msg_id, att_id)
        # Returns: {'content_block': {'type': 'image', 'source': {...}}}
    
    Example (Gmail):
        result = email_process_attachment_for_ai('gmail', msg_id, att_id)
        # Auto-detects Gmail API format
    """
    # Validate source
    if source not in ['outlook', 'gmail']:
        return {
            'success': False,
            'error': f"Invalid source '{source}'. Must be 'outlook' or 'gmail'"
        }
    
    # Get user_id from kwargs
    user_id = kwargs.get('_user_id') or kwargs.get('user_id')
    
    # Create handler instance
    handler = UniversalFileHandler(user_id=user_id, **kwargs)
    
    # Build source_id dict for handler
    source_id = {
        'message_id': message_id,
        'attachment_id': attachment_id
    }
    
    # Process through universal handler
    return handler.process_file(
        source=source,
        source_id=source_id,
        mode=mode,
        **kwargs
    )


def email_process_attachments_batch(
    source: str,
    attachments: List[Dict[str, str]],
    mode: str = 'auto',
    **kwargs
) -> Dict[str, Any]:
    """
    Process multiple email attachments at once
    
    Args:
        source: Email platform ('outlook' or 'gmail')
        attachments: List of attachment specs
            [
                {'message_id': 'msg1', 'attachment_id': 'att1'},
                {'message_id': 'msg1', 'attachment_id': 'att2'},
                {'message_id': 'msg2', 'attachment_id': 'att3'}
            ]
        mode: Delivery mode (applied to all)
    
    Returns:
        {
            'success': True,
            'results': [
                {'file': 'image1.png', 'method': 'direct', 'token_estimate': 267},
                {'file': 'doc.pdf', 'method': 'files_api', 'token_estimate': 50}
            ],
            'total_token_estimate': 317,
            'content_blocks': [...]  # Ready for Anthropic API
        }
    
    Example (Sign Doctor email with 2 PNGs):
        attachments = [
            {'message_id': msg_id, 'attachment_id': att1_id},
            {'message_id': msg_id, 'attachment_id': att2_id}
        ]
        result = email_process_attachments_batch('outlook', attachments)
        
        # Before: 59,000 tokens (base64 in conversation)
        # After: 1,600 tokens (content blocks in current message)
        # Savings: 97% token reduction
    """
    # Validate source
    if source not in ['outlook', 'gmail']:
        return {
            'success': False,
            'error': f"Invalid source '{source}'. Must be 'outlook' or 'gmail'"
        }
    
    # Get user_id from kwargs
    user_id = kwargs.get('_user_id') or kwargs.get('user_id')
    
    # Create handler instance
    handler = UniversalFileHandler(user_id=user_id, **kwargs)
    
    # Convert attachment list to handler format
    file_specs = []
    for att in attachments:
        file_specs.append({
            'source': source,
            'source_id': {
                'message_id': att['message_id'],
                'attachment_id': att['attachment_id']
            }
        })
    
    # Process batch through universal handler
    return handler.process_batch(file_specs, mode=mode, **kwargs)


# ==================== SIMPLE DOWNLOAD TO CLOUD HELPERS ====================
def _save_base64_attachment_to_temp(content_b64: str, filename: str) -> str:
    """Decode base64 content and save to a temporary file. Returns local path."""
    try:
        data = base64.b64decode(content_b64)
    except Exception:
        # If it's already bytes-like, try to write directly
        data = content_b64 if isinstance(content_b64, (bytes, bytearray)) else content_b64.encode('utf-8')

    # Preserve extension if present
    _, ext = os.path.splitext(filename or '')
    suffix = ext or ''
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tf.write(data)
    tf.flush()
    tf.close()
    return tf.name


def microsoft_outlook_download_attachment_to_google_drive(
    message_id: str,
    attachment_id: str,
    parent_folder_id: Optional[str] = None,
    _user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Download an Outlook attachment and upload it to Google Drive.

    Returns Google Drive file metadata on success.
    """
    try:
        # Lazy import to avoid circular issues
        from tools.implementations.microsoft_outlook_tools import microsoft_outlook_download_attachment
        from google_workspace.google_drive import google_drive_upload_file

        # Download attachment (base64 content)
        att = microsoft_outlook_download_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            _user_id=_user_id,
            _injected_credentials=True,
            **kwargs
        )

        if not att.get('success'):
            return att

        content_b64 = att.get('content')
        name = att.get('name') or f'{attachment_id}'
        mime_type = att.get('content_type')

        local_path = _save_base64_attachment_to_temp(content_b64, name)

        try:
            file_info = google_drive_upload_file(
                local_path,
                name=name,
                mime_type=mime_type,
                parent_folder_id=parent_folder_id,
                _user_id=_user_id,
                _injected_credentials=True
            )

            # Clean up local temp file
            try:
                os.remove(local_path)
            except Exception:
                pass

            return {'success': True, 'drive_file': file_info}

        except Exception as e:
            # Keep local file for debugging
            return {'success': False, 'error': str(e), 'local_path': local_path}

    except Exception as e:
        return {'success': False, 'error': str(e)}


def microsoft_outlook_download_attachment_to_onedrive(
    message_id: str,
    attachment_id: str,
    onedrive_folder: Optional[str] = None,
    user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Download an Outlook attachment and upload it to OneDrive.

    Returns OneDrive upload result on success.
    """
    try:
        from tools.implementations.microsoft_outlook_tools import microsoft_outlook_download_attachment
        # Use module-level OneDrive uploader
        from tools.implementations import microsoft_onedrive_tools

        att = microsoft_outlook_download_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            _user_id=user_id,
            _injected_credentials=True,
            **kwargs
        )

        if not att.get('success'):
            return att

        content_b64 = att.get('content')
        name = att.get('name') or f'{attachment_id}'

        local_path = _save_base64_attachment_to_temp(content_b64, name)

        try:
            # microsoft_onedrive_tools exposes a module-level function `microsoft_onedrive_upload_file`
            # which maps to the OneDrive uploader implementation
            file_result = microsoft_onedrive_tools.microsoft_onedrive_upload_file(
                local_file_path=local_path,
                onedrive_folder=onedrive_folder,
                new_name=name,
                user_id=user_id,
                **kwargs
            )

            try:
                os.remove(local_path)
            except Exception:
                pass

            return file_result

        except Exception as e:
            return {'success': False, 'error': str(e), 'local_path': local_path}

    except Exception as e:
        return {'success': False, 'error': str(e)}


# ==================== CONVERT & SEND TO AI ====================
def microsoft_outlook_attachment_convert_and_send_to_ai(
    message_id: str,
    attachment_id: str,
    convert_to: str = 'auto',
    _user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Download Outlook attachment, convert to PDF/image, and return Anthropic content block.
    
    Args:
        message_id: Outlook message ID
        attachment_id: Attachment ID
        convert_to: 'auto' (detect), 'pdf', 'image', or 'direct' (no conversion)
        _user_id: User ID for credentials
    
    Returns:
        {
            'success': True,
            'content_block': {...},  # Ready for Anthropic Messages API
            'conversion_method': 'pdf' | 'image' | 'direct',
            'metadata': {...}
        }
    
    Examples:
        # Auto-detect best format
        result = microsoft_outlook_attachment_convert_and_send_to_ai(msg_id, att_id)
        
        # Force PDF conversion for DOCX
        result = microsoft_outlook_attachment_convert_and_send_to_ai(
            msg_id, att_id, convert_to='pdf'
        )
        
        # Force image conversion for better visual analysis
        result = microsoft_outlook_attachment_convert_and_send_to_ai(
            msg_id, att_id, convert_to='image'
        )
    """
    try:
        from tools.implementations.microsoft_outlook_tools import microsoft_outlook_download_attachment
        from AI_infrastructure.core.document_converter import DocumentConverter
        from PIL import Image
        import io
        
        # Download attachment
        att = microsoft_outlook_download_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            _user_id=_user_id,
            _injected_credentials=True,
            **kwargs
        )
        
        if not att.get('success'):
            return att
        
        content_b64 = att.get('content')
        name = att.get('name') or f'{attachment_id}'
        content_type = att.get('content_type') or 'application/octet-stream'
        size = att.get('size') or 0
        
        # Decode attachment data
        try:
            data = base64.b64decode(content_b64)
        except Exception:
            data = content_b64 if isinstance(content_b64, (bytes, bytearray)) else content_b64.encode('utf-8')
        
        converter = DocumentConverter()
        
        # Determine conversion strategy
        if convert_to == 'auto':
            # Auto-detect based on file type
            if content_type in converter.DOCX_TYPES + converter.XLSX_TYPES + converter.PPTX_TYPES:
                convert_to = 'image'  # Visual analysis works better for docs
            elif content_type == 'application/pdf':
                convert_to = 'image'  # Convert PDF pages to images for Sonnet 4.5
            elif content_type.startswith('image/'):
                convert_to = 'direct'  # Already an image
            else:
                convert_to = 'direct'  # Unknown - send as-is
        
        # Perform conversion
        if convert_to == 'pdf':
            result = converter.convert_to_pdf(data, content_type, name)
            if not result.get('success'):
                return result
            
            pdf_file = result['files'][0]
            content_block = {
                'type': 'document',
                'source': {
                    'type': 'base64',
                    'media_type': 'application/pdf',
                    'data': base64.b64encode(pdf_file['data']).decode('utf-8')
                }
            }
            return {
                'success': True,
                'content_block': content_block,
                'conversion_method': 'pdf',
                'metadata': {
                    'original_name': name,
                    'original_type': content_type,
                    'converted_size': pdf_file['size']
                }
            }
        
        elif convert_to == 'image':
            # Convert to images
            if content_type == 'application/pdf':
                # PDF to images (requires pdf2image + poppler)
                try:
                    from pdf2image import convert_from_bytes
                    images = convert_from_bytes(data, dpi=150)
                    
                    content_blocks = []
                    for i, img in enumerate(images):
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        content_blocks.append({
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/png',
                                'data': base64.b64encode(img_bytes.read()).decode('utf-8')
                            }
                        })
                    
                    return {
                        'success': True,
                        'content_blocks': content_blocks,
                        'conversion_method': 'pdf_to_images',
                        'metadata': {
                            'original_name': name,
                            'original_type': content_type,
                            'page_count': len(images)
                        }
                    }
                except ImportError:
                    return {'success': False, 'error': 'pdf2image not installed (requires: pip install pdf2image + poppler)'}
            
            else:
                # Office doc to images
                result = converter.convert_to_images(data, content_type, name, format='png')
                if not result.get('success'):
                    return result
                
                content_blocks = []
                for img_file in result['files']:
                    content_blocks.append({
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/png',
                            'data': base64.b64encode(img_file['data']).decode('utf-8')
                        }
                    })
                
                return {
                    'success': True,
                    'content_blocks': content_blocks,
                    'conversion_method': 'document_to_images',
                    'metadata': {
                        'original_name': name,
                        'original_type': content_type,
                        'image_count': len(content_blocks)
                    }
                }
        
        else:
            # Direct - send as-is
            if content_type.startswith('image/'):
                content_block = {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': content_type,
                        'data': content_b64
                    }
                }
            elif content_type == 'application/pdf':
                content_block = {
                    'type': 'document',
                    'source': {
                        'type': 'base64',
                        'media_type': 'application/pdf',
                        'data': content_b64
                    }
                }
            else:
                # Text or unknown - encode as text
                try:
                    text_content = data.decode('utf-8')
                    content_block = {
                        'type': 'text',
                        'text': f"Attachment: {name}\n\n{text_content}"
                    }
                except Exception:
                    return {'success': False, 'error': f'Cannot convert {content_type} to AI-readable format'}
            
            return {
                'success': True,
                'content_block': content_block,
                'conversion_method': 'direct',
                'metadata': {
                    'original_name': name,
                    'original_type': content_type,
                    'size': size
                }
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


# ==================== OUTLOOK-SPECIFIC WRAPPERS ====================

def microsoft_outlook_process_attachment_for_ai(
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    **kwargs
) -> Dict[str, Any]:
    """
    Process Outlook attachment for AI (Anthropic Claude)
    
    ✅ REPLACES: microsoft_outlook_download_attachment (causes token overflow)
    
    Args:
        message_id: Outlook message ID
        attachment_id: Attachment ID
        mode: 'auto', 'direct', 'files_api', or 'url'
    
    Returns:
        Anthropic-ready content block or URL
    
    Example:
        # Get attachment list first
        attachments = microsoft_outlook_get_attachments(message_id)
        
        # Process for AI (smart method selection)
        for att in attachments:
            result = microsoft_outlook_process_attachment_for_ai(
                message_id=message_id,
                attachment_id=att['id']
            )
            
            if result['method'] == 'direct':
                # Send content_block to Anthropic directly
                content = result['content_block']
            elif result['method'] == 'url':
                # Include URL in message to AI
                url = result['url']
    """
    return email_process_attachment_for_ai(
        source='outlook',
        message_id=message_id,
        attachment_id=attachment_id,
        mode=mode,
        **kwargs
    )


def microsoft_outlook_process_all_attachments(
    message_id: str,
    mode: str = 'auto',
    **kwargs
) -> Dict[str, Any]:
    """
    Process ALL attachments from an Outlook message at once
    
    Args:
        message_id: Outlook message ID
        mode: Delivery mode
    
    Returns:
        Batch processing result with content_blocks ready for Anthropic
    
    Example:
        # Process entire Sign Doctor email
        result = microsoft_outlook_process_all_attachments(msg_id)
        
        print(f"Processed {len(result['results'])} attachments")
        print(f"Total tokens: {result['total_token_estimate']}")
        
        # Send to Anthropic
        content_blocks = result['content_blocks']
    """
    from tools.implementations.microsoft_outlook_tools import microsoft_outlook_get_attachments
    
    # Get user_id
    user_id = kwargs.get('_user_id') or kwargs.get('user_id')
    
    # Get attachment list
    attachments_result = microsoft_outlook_get_attachments(
        message_id=message_id,
        download_content=False,  # Just get metadata
        _user_id=user_id,
        _injected_credentials=True,
        **kwargs
    )
    
    if not attachments_result['success']:
        return attachments_result
    
    # Build attachment list for batch processor
    attachment_specs = []
    for att in attachments_result['attachments']:
        attachment_specs.append({
            'message_id': message_id,
            'attachment_id': att['id']
        })
    
    # Process batch
    return email_process_attachments_batch(
        source='outlook',
        attachments=attachment_specs,
        mode=mode,
        **kwargs
    )


# ==================== GMAIL-SPECIFIC WRAPPERS ====================

def google_gmail_process_attachment_for_ai(
    message_id: str,
    attachment_id: str,
    mode: str = 'auto',
    **kwargs
) -> Dict[str, Any]:
    """
    Process Gmail attachment for AI (Anthropic Claude)
    
    Args:
        message_id: Gmail message ID
        attachment_id: Attachment ID
        mode: 'auto', 'direct', 'files_api', or 'url'
    
    Returns:
        Anthropic-ready content block or URL
    
    Example:
        # Get message first
        message = gmail_get_message(message_id)
        
        # Process attachments
        for att in message['attachments']:
            result = google_gmail_process_attachment_for_ai(
                message_id=message_id,
                attachment_id=att['id']
            )
    """
    return email_process_attachment_for_ai(
        source='gmail',
        message_id=message_id,
        attachment_id=attachment_id,
        mode=mode,
        **kwargs
    )


def google_gmail_process_all_attachments(
    message_id: str,
    mode: str = 'auto',
    **kwargs
) -> Dict[str, Any]:
    """
    Process ALL attachments from a Gmail message at once
    
    Args:
        message_id: Gmail message ID
        mode: Delivery mode
    
    Returns:
        Batch processing result with content_blocks ready for Anthropic
    
    Example:
        result = google_gmail_process_all_attachments(msg_id)
        content_blocks = result['content_blocks']
    """
    try:
        from google_workspace.gmail import GmailManager
        
        # Get user_id
        user_id = kwargs.get('_user_id') or kwargs.get('user_id')
        
        gmail = GmailManager()
        
        # Get message with attachments
        message = gmail.get_message(message_id, user_id=user_id)
        
        if not message.get('attachments'):
            return {
                'success': True,
                'results': [],
                'total_token_estimate': 0,
                'content_blocks': []
            }
        
        # Build attachment list
        attachment_specs = []
        for att in message['attachments']:
            attachment_specs.append({
                'message_id': message_id,
                'attachment_id': att['id']
            })
        
        # Process batch
        return email_process_attachments_batch(
            source='gmail',
            attachments=attachment_specs,
            mode=mode,
            **kwargs
        )
    except Exception as e:
        return {
            'success': False,
            'error': f'Gmail attachment processing error: {str(e)}'
        }


# ==================== LEGACY COMPATIBILITY ====================

def outlook_download_attachment_legacy(
    message_id: str,
    attachment_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    DEPRECATED: Legacy Outlook attachment download
    
    ⚠️ WARNING: This method causes token overflow!
    Use microsoft_outlook_process_attachment_for_ai() instead.
    
    This function is kept for backward compatibility only.
    """
    from tools.implementations.microsoft_outlook_tools import microsoft_outlook_download_attachment
    
    result = microsoft_outlook_download_attachment(
        message_id=message_id,
        attachment_id=attachment_id,
        **kwargs
    )
    
    if result['success']:
        result['warning'] = (
            "⚠️ DEPRECATED: This method returns base64 content which causes token overflow. "
            "Use microsoft_outlook_process_attachment_for_ai() instead for 97-99% token savings."
        )
    
    return result


# ==================== GMAIL ATTACHMENT FUNCTIONS ====================

def gmail_download_attachment_to_google_drive(
    message_id: str,
    attachment_id: str,
    parent_folder_id: Optional[str] = None,
    user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Download a Gmail attachment and upload it to Google Drive.
    
    Args:
        message_id: Gmail message ID
        attachment_id: Attachment ID from Gmail API
        parent_folder_id: Google Drive folder ID (optional)
        user_id: User ID for credentials
        
    Returns:
        Google Drive upload result on success.
        
    Example:
        result = gmail_download_attachment_to_google_drive(
            message_id='17f1234567890abcd',
            attachment_id='ANGjdJ8...',
            parent_folder_id='1a2b3c4d5e'
        )
    """
    try:
        from google_workspace.gmail import gmail_get_attachment
        from google_workspace import google_drive
        
        # Get attachment from Gmail
        att_result = gmail_get_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            _user_id=user_id,
            _injected_credentials=True,
            **kwargs
        )
        
        if not att_result:
            return {'success': False, 'error': 'Failed to download Gmail attachment'}
        
        # Gmail attachment data is in 'data' field as bytes
        content = att_result.get('data')
        size = att_result.get('size', 0)
        
        # Get filename from message metadata
        try:
            from google_workspace.gmail import gmail_get_message
            msg = gmail_get_message(
                message_id=message_id,
                format='metadata',
                _user_id=user_id,
                _injected_credentials=True,
                **kwargs
            )
            
            # Find attachment filename from message parts
            filename = f'attachment_{attachment_id}'
            if msg and 'payload' in msg:
                parts = msg['payload'].get('parts', [])
                for part in parts:
                    if part.get('body', {}).get('attachmentId') == attachment_id:
                        filename = part.get('filename', filename)
                        break
        except Exception as e:
            print(f"⚠️ Could not get filename: {e}")
            filename = f'attachment_{attachment_id}'
        
        # Save to temp file
        local_path = _save_base64_attachment_to_temp(base64.b64encode(content).decode('utf-8'), filename)
        
        try:
            # Upload to Google Drive
            file_result = google_drive.google_drive_upload_file(
                local_file_path=local_path,
                parent_folder_id=parent_folder_id,
                new_name=filename,
                user_id=user_id,
                **kwargs
            )
            
            # Clean up temp file
            try:
                os.remove(local_path)
            except Exception:
                pass
            
            return file_result
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'local_path': local_path}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def gmail_download_attachment_to_onedrive(
    message_id: str,
    attachment_id: str,
    onedrive_folder: Optional[str] = None,
    user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Download a Gmail attachment and upload it to OneDrive.
    
    Args:
        message_id: Gmail message ID
        attachment_id: Attachment ID from Gmail API
        onedrive_folder: OneDrive folder path (optional)
        user_id: User ID for credentials
        
    Returns:
        OneDrive upload result on success.
        
    Example:
        result = gmail_download_attachment_to_onedrive(
            message_id='17f1234567890abcd',
            attachment_id='ANGjdJ8...',
            onedrive_folder='/Documents/Emails'
        )
    """
    try:
        from google_workspace.gmail import gmail_get_attachment, gmail_get_message
        from tools.implementations import microsoft_onedrive_tools
        
        # Get attachment from Gmail
        att_result = gmail_get_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            _user_id=user_id,
            _injected_credentials=True,
            **kwargs
        )
        
        if not att_result:
            return {'success': False, 'error': 'Failed to download Gmail attachment'}
        
        # Gmail attachment data
        content = att_result.get('data')
        size = att_result.get('size', 0)
        
        # Get filename from message metadata
        try:
            msg = gmail_get_message(
                message_id=message_id,
                format='metadata',
                _user_id=user_id,
                _injected_credentials=True,
                **kwargs
            )
            
            filename = f'attachment_{attachment_id}'
            if msg and 'payload' in msg:
                parts = msg['payload'].get('parts', [])
                for part in parts:
                    if part.get('body', {}).get('attachmentId') == attachment_id:
                        filename = part.get('filename', filename)
                        break
        except Exception as e:
            print(f"⚠️ Could not get filename: {e}")
            filename = f'attachment_{attachment_id}'
        
        # Save to temp file
        local_path = _save_base64_attachment_to_temp(base64.b64encode(content).decode('utf-8'), filename)
        
        try:
            # Upload to OneDrive (auto-handles chunked upload for >4MB)
            file_result = microsoft_onedrive_tools.microsoft_onedrive_upload_file(
                local_file_path=local_path,
                onedrive_folder=onedrive_folder,
                new_name=filename,
                user_id=user_id,
                **kwargs
            )
            
            # Clean up temp file
            try:
                os.remove(local_path)
            except Exception:
                pass
            
            return file_result
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'local_path': local_path}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def gmail_attachment_convert_and_send_to_ai(
    message_id: str,
    attachment_id: str,
    convert_to: str = 'auto',
    _user_id: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Download Gmail attachment, convert to PDF/image, and return Anthropic content block.
    
    Args:
        message_id: Gmail message ID
        attachment_id: Attachment ID from Gmail API
        convert_to: 'auto' (detect), 'pdf', 'image', or 'direct' (no conversion)
        _user_id: User ID for credentials
    
    Returns:
        {
            'success': True,
            'content_block': {...},  # Ready for Anthropic Messages API
            'conversion_method': 'pdf' | 'image' | 'direct',
            'metadata': {...}
        }
    
    Examples:
        # Auto-detect best format
        result = gmail_attachment_convert_and_send_to_ai(msg_id, att_id)
        
        # Force PDF conversion
        result = gmail_attachment_convert_and_send_to_ai(
            msg_id, att_id, convert_to='pdf'
        )
        
        # Force image conversion for visual analysis
        result = gmail_attachment_convert_and_send_to_ai(
            msg_id, att_id, convert_to='image'
        )
    """
    try:
        from google_workspace.gmail import gmail_get_attachment, gmail_get_message
        from AI_infrastructure.core.document_converter import DocumentConverter
        from PIL import Image
        import io
        
        # Get attachment from Gmail
        att_result = gmail_get_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
            _user_id=_user_id,
            _injected_credentials=True,
            **kwargs
        )
        
        if not att_result:
            return {'success': False, 'error': 'Failed to download Gmail attachment'}
        
        # Get attachment data
        data = att_result.get('data')  # Gmail returns bytes directly
        size = att_result.get('size', 0)
        
        # Get filename and content type from message metadata
        try:
            msg = gmail_get_message(
                message_id=message_id,
                format='metadata',
                _user_id=_user_id,
                _injected_credentials=True,
                **kwargs
            )
            
            filename = f'attachment_{attachment_id}'
            content_type = 'application/octet-stream'
            
            if msg and 'payload' in msg:
                parts = msg['payload'].get('parts', [])
                for part in parts:
                    if part.get('body', {}).get('attachmentId') == attachment_id:
                        filename = part.get('filename', filename)
                        content_type = part.get('mimeType', content_type)
                        break
        except Exception as e:
            print(f"⚠️ Could not get file metadata: {e}")
            filename = f'attachment_{attachment_id}'
            content_type = 'application/octet-stream'
        
        converter = DocumentConverter()
        
        # Determine conversion strategy (same logic as Outlook version)
        if convert_to == 'auto':
            if content_type in converter.DOCX_TYPES + converter.XLSX_TYPES + converter.PPTX_TYPES:
                convert_to = 'image'
            elif content_type == 'application/pdf':
                convert_to = 'image'
            elif content_type.startswith('image/'):
                convert_to = 'direct'
            else:
                convert_to = 'direct'
        
        # Perform conversion (same as Outlook version)
        if convert_to == 'pdf':
            result = converter.convert_to_pdf(data, content_type, filename)
            if not result.get('success'):
                return result
            
            pdf_file = result['files'][0]
            content_block = {
                'type': 'document',
                'source': {
                    'type': 'base64',
                    'media_type': 'application/pdf',
                    'data': base64.b64encode(pdf_file['data']).decode('utf-8')
                }
            }
            return {
                'success': True,
                'content_block': content_block,
                'conversion_method': 'pdf',
                'metadata': {
                    'original_name': filename,
                    'original_type': content_type,
                    'converted_size': pdf_file['size']
                }
            }
        
        elif convert_to == 'image':
            if content_type == 'application/pdf':
                try:
                    from pdf2image import convert_from_bytes
                    images = convert_from_bytes(data, dpi=150)
                    
                    content_blocks = []
                    for i, img in enumerate(images):
                        img_bytes = io.BytesIO()
                        img.save(img_bytes, format='PNG')
                        img_bytes.seek(0)
                        
                        content_blocks.append({
                            'type': 'image',
                            'source': {
                                'type': 'base64',
                                'media_type': 'image/png',
                                'data': base64.b64encode(img_bytes.read()).decode('utf-8')
                            }
                        })
                    
                    return {
                        'success': True,
                        'content_blocks': content_blocks,
                        'conversion_method': 'pdf_to_images',
                        'metadata': {
                            'original_name': filename,
                            'original_type': content_type,
                            'page_count': len(images)
                        }
                    }
                except ImportError:
                    return {'success': False, 'error': 'pdf2image not installed (requires: pip install pdf2image + poppler)'}
            
            else:
                result = converter.convert_to_images(data, content_type, filename, format='png')
                if not result.get('success'):
                    return result
                
                content_blocks = []
                for img_file in result['files']:
                    content_blocks.append({
                        'type': 'image',
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/png',
                            'data': base64.b64encode(img_file['data']).decode('utf-8')
                        }
                    })
                
                return {
                    'success': True,
                    'content_blocks': content_blocks,
                    'conversion_method': 'document_to_images',
                    'metadata': {
                        'original_name': filename,
                        'original_type': content_type,
                        'image_count': len(content_blocks)
                    }
                }
        
        else:
            # Direct - send as-is
            if content_type.startswith('image/'):
                content_block = {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': content_type,
                        'data': base64.b64encode(data).decode('utf-8')
                    }
                }
            elif content_type == 'application/pdf':
                content_block = {
                    'type': 'document',
                    'source': {
                        'type': 'base64',
                        'media_type': 'application/pdf',
                        'data': base64.b64encode(data).decode('utf-8')
                    }
                }
            else:
                # Text or unknown
                try:
                    text_content = data.decode('utf-8')
                    content_block = {
                        'type': 'text',
                        'text': f"Attachment: {filename}\n\n{text_content}"
                    }
                except Exception:
                    return {'success': False, 'error': f'Cannot convert {content_type} to AI-readable format'}
            
            return {
                'success': True,
                'content_block': content_block,
                'conversion_method': 'direct',
                'metadata': {
                    'original_name': filename,
                    'original_type': content_type,
                    'size': size
                }
            }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
