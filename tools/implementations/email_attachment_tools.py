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
