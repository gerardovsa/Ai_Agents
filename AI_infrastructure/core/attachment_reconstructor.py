"""
ATTACHMENT RECONSTRUCTOR
Handles on-demand reconstruction of multimodal content from email attachments

CRITICAL RULES:
1. Base64 data is NEVER stored in database
2. Attachments stored as metadata only (filename, size, attachment_id, download_url)
3. When sending to Claude API, download and convert to base64 on-the-fly
4. After API call completes, base64 data is discarded (ephemeral)

This prevents:
- Database bloat from storing base64
- Message bubbles showing giant unreadable strings
- Token waste in conversation history
- Memory/rendering issues in UI
"""

import re
import base64
import requests
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def has_attachment_references(content: Any) -> bool:
    """
    Check if message content contains attachment ID references
    
    Args:
        content: Message content (string or list of content blocks)
        
    Returns:
        True if attachment IDs are found
    """
    if isinstance(content, str):
        # Look for patterns like "Attachment ID: ANGjdJ77F..."
        return bool(re.search(r'Attachment ID:\s*([A-Za-z0-9_-]+)', content))
    
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                if has_attachment_references(block.get('text', '')):
                    return True
    
    return False


def extract_attachment_ids(content: Any) -> List[Dict[str, str]]:
    """
    Extract attachment metadata from message content
    
    Args:
        content: Message content (string or list of content blocks)
        
    Returns:
        List of {attachment_id, type, filename}
    """
    attachments = []
    
    if isinstance(content, str):
        # Pattern: 🖼️ **Image**: filename.jpg (size)
        #          - Attachment ID: ANGjdJ77F...
        image_pattern = r'🖼️\s*\*\*Image\*\*:\s*([^\n]+)\n.*?Attachment ID:\s*([A-Za-z0-9_-]+)'
        for match in re.finditer(image_pattern, content, re.DOTALL):
            filename = match.group(1).split('(')[0].strip()
            attachment_id = match.group(2).strip()
            attachments.append({
                'attachment_id': attachment_id,
                'type': 'image',
                'filename': filename
            })
        
        # Pattern: 📄 **PDF Document**: filename.pdf (size)
        #          - Attachment ID: ANGjdJ77F...
        pdf_pattern = r'📄\s*\*\*PDF Document\*\*:\s*([^\n]+)\n.*?Attachment ID:\s*([A-Za-z0-9_-]+)'
        for match in re.finditer(pdf_pattern, content, re.DOTALL):
            filename = match.group(1).split('(')[0].strip()
            attachment_id = match.group(2).strip()
            attachments.append({
                'attachment_id': attachment_id,
                'type': 'pdf',
                'filename': filename
            })
    
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get('type') == 'text':
                attachments.extend(extract_attachment_ids(block.get('text', '')))
    
    return attachments


def download_attachment_as_base64(
    attachment_id: str,
    email_id: str,
    user_id: int,
    provider: str = 'gmail'
) -> Optional[Dict[str, Any]]:
    """
    Download email attachment and convert to base64 (ephemeral - not stored)
    
    Args:
        attachment_id: Gmail/Outlook attachment ID
        email_id: Email message ID
        user_id: User ID for authentication
        provider: 'gmail' or 'outlook'
        
    Returns:
        {type: 'base64', media_type: '...', data: '...'} or None if failed
    """
    try:
        # Construct download URL
        if provider == 'gmail':
            url = f"http://localhost:5001/api/gmail/attachment?message_id={email_id}&attachment_id={attachment_id}&user_id={user_id}"
        elif provider == 'outlook':
            url = f"http://localhost:5001/api/outlook/attachment?message_id={email_id}&attachment_id={attachment_id}&user_id={user_id}"
        else:
            logger.error(f"Unknown provider: {provider}")
            return None
        
        # Download attachment
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Get content type from headers
        content_type = response.headers.get('Content-Type', 'application/octet-stream')
        
        # Convert to base64
        file_data = response.content
        base64_data = base64.b64encode(file_data).decode('utf-8')
        
        # Check size limits
        if 'image' in content_type and len(file_data) > 5 * 1024 * 1024:
            logger.warning(f"Image too large: {len(file_data)} bytes (5MB limit)")
            return None
        
        if 'pdf' in content_type and len(file_data) > 4.5 * 1024 * 1024:
            logger.warning(f"PDF too large: {len(file_data)} bytes (4.5MB limit)")
            return None
        
        logger.info(f"✅ Downloaded attachment {attachment_id}: {len(file_data)} bytes")
        
        return {
            'type': 'base64',
            'media_type': content_type,
            'data': base64_data
        }
    
    except Exception as e:
        logger.error(f"Failed to download attachment {attachment_id}: {e}")
        return None


def reconstruct_multimodal_content(
    messages: List[Dict[str, Any]],
    email_id: Optional[str] = None,
    user_id: Optional[int] = None,
    provider: str = 'gmail'
) -> List[Dict[str, Any]]:
    """
    Reconstruct multimodal content from attachment references
    
    This function:
    1. Scans messages for attachment ID references
    2. Downloads attachments on-demand
    3. Converts to base64 (ephemeral - discarded after API call)
    4. Inserts proper image/document blocks for Claude API
    
    Args:
        messages: List of message dicts (role + content)
        email_id: Email message ID (for downloading attachments)
        user_id: User ID (for API authentication)
        provider: 'gmail' or 'outlook'
        
    Returns:
        Messages with multimodal content blocks added
    """
    reconstructed_messages = []
    
    for message in messages:
        role = message.get('role')
        content = message.get('content')
        
        # Skip if no attachment references
        if not has_attachment_references(content):
            reconstructed_messages.append(message)
            continue
        
        # Extract attachment IDs
        attachments = extract_attachment_ids(content)
        
        if not attachments:
            reconstructed_messages.append(message)
            continue
        
        logger.info(f"📎 Found {len(attachments)} attachment(s) in message, reconstructing multimodal content...")
        
        # Build new content blocks
        new_content = []
        
        # Add original text content
        if isinstance(content, str):
            new_content.append({'type': 'text', 'text': content})
        elif isinstance(content, list):
            new_content.extend([b for b in content if isinstance(b, dict)])
        
        # Download and add attachments
        for att in attachments:
            attachment_id = att['attachment_id']
            att_type = att['type']
            filename = att['filename']
            
            # Download attachment as base64 (ephemeral)
            base64_data = download_attachment_as_base64(
                attachment_id=attachment_id,
                email_id=email_id,
                user_id=user_id,
                provider=provider
            )
            
            if not base64_data:
                logger.warning(f"⚠️ Failed to download attachment {attachment_id}, skipping")
                continue
            
            # Add image block
            if att_type == 'image':
                new_content.append({
                    'type': 'image',
                    'source': base64_data
                })
                new_content.append({
                    'type': 'text',
                    'text': f"\n[Image: {filename}]\nPlease analyze this image in context.\n"
                })
                logger.info(f"✅ Added image block for {filename}")
            
            # Add document block
            elif att_type == 'pdf':
                new_content.append({
                    'type': 'document',
                    'source': base64_data
                })
                new_content.append({
                    'type': 'text',
                    'text': f"\n[PDF Document: {filename}]\nPlease analyze this document.\n"
                })
                logger.info(f"✅ Added document block for {filename}")
        
        # Add reconstructed message
        reconstructed_messages.append({
            'role': role,
            'content': new_content
        })
    
    return reconstructed_messages
