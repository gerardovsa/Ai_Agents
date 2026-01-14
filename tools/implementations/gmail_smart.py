"""
SMART GMAIL TOOLS - Intelligent Email Operations with Confirmation
===================================================================

These are WRAPPER tools that add intelligence on top of basic Gmail tools:
- Automatic confirmation for large emails
- Token estimation before fetching
- Smart format selection
- Cost-aware operations

These tools use the Universal Confirmation System.
"""

from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Import Gmail basic tools
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'google_workspace'))
from gmail import (
    gmail_get_message,
    gmail_get_message_parsed,
    gmail_get_thread_parsed,
    gmail_list_messages
)

# Import confirmation system
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
from core.confirmation_manager import (
    ConfirmationManager,
    ConfirmationLevel,
    create_email_confirmation
)


def _extract_attachment_metadata(message_payload: Dict) -> List[Dict[str, Any]]:
    """
    Extract attachment metadata from Gmail message payload
    
    Args:
        message_payload: Gmail API message payload
    
    Returns:
        List of {filename, size_bytes, content_type}
    """
    attachments = []
    
    def extract_from_part(part, depth=0):
        if depth > 10:  # Prevent infinite recursion
            return
        
        filename = part.get('filename', '')
        if filename and part.get('body', {}).get('attachmentId'):
            attachments.append({
                'filename': filename,
                'size_bytes': part.get('body', {}).get('size', 0),
                'content_type': part.get('mimeType', 'unknown')
            })
        
        # Recurse into parts
        if 'parts' in part:
            for subpart in part['parts']:
                extract_from_part(subpart, depth + 1)
    
    payload = message_payload.get('payload', {})
    extract_from_part(payload)
    
    return attachments


def _estimate_email_tokens(message_metadata: Dict) -> int:
    """
    Estimate token count for email based on metadata
    
    Estimation logic:
    - Base email (headers, subject): ~500 tokens
    - Body text: sizeEstimate / 4 (rough chars to tokens)
    - Per attachment: 2000 tokens (parsing overhead)
    """
    base_tokens = 500
    
    # Estimate body tokens from size
    size_estimate = message_metadata.get('sizeEstimate', 0)
    body_tokens = size_estimate // 4  # Rough estimate
    
    # Attachment overhead
    payload = message_metadata.get('payload', {})
    attachments = _extract_attachment_metadata({'payload': payload})
    attachment_tokens = len(attachments) * 2000  # 2k per attachment
    
    total = base_tokens + body_tokens + attachment_tokens
    
    return total


def gmail_analyze_email_smart(message_id: str, **kwargs) -> Dict[str, Any]:
    """
    SMART email analysis with automatic confirmation for large content
    
    This is a TWO-PHASE tool:
    - Phase 1: Check metadata and request confirmation if needed
    - Phase 2: Fetch full content if user confirms (via conversation continuation)
    
    Args:
        message_id: Gmail message ID
        **kwargs: Credential injection
    
    Returns:
        - If small: Parsed email content directly
        - If large: Confirmation request for user
    
    Example:
        # AI calls this tool
        result = gmail_analyze_email_smart('msg_123')
        
        # If large email:
        result = {
            'status': 'confirmation_required',
            'confirmation_prompt': '...',
            ...
        }
        
        # User confirms, AI continues:
        # (Conversation history preserved automatically)
        result = gmail_get_message_parsed('msg_123', output_format='pdf')
    """
    # Phase 1: Fetch metadata (lightweight)
    try:
        metadata = gmail_get_message(message_id, format='metadata', **kwargs)
    except Exception as e:
        return {
            'error': True,
            'message': f"Failed to fetch email metadata: {e}"
        }
    
    # Extract key info
    subject = next((h['value'] for h in metadata.get('payload', {}).get('headers', []) 
                    if h['name'].lower() == 'subject'), '(No Subject)')
    from_header = next((h['value'] for h in metadata.get('payload', {}).get('headers', []) 
                        if h['name'].lower() == 'from'), 'Unknown')
    
    # Check attachments
    attachments = _extract_attachment_metadata({'payload': metadata.get('payload', {})})
    has_attachments = len(attachments) > 0
    
    # Calculate size
    size_estimate = metadata.get('sizeEstimate', 0)
    size_mb = size_estimate / (1024 * 1024)
    
    # Estimate tokens
    estimated_tokens = _estimate_email_tokens(metadata)
    
    # Check if confirmation needed
    needs_confirmation = ConfirmationManager.should_confirm(
        tokens=estimated_tokens,
        size_mb=size_mb,
        level=ConfirmationLevel.HIGH if has_attachments else ConfirmationLevel.LOW
    )
    
    if needs_confirmation:
        # Generate confirmation request
        confirmation = create_email_confirmation(
            message_id=message_id,
            subject=subject,
            from_addr=from_header,
            attachments=attachments,
            size_mb=size_mb,
            estimated_tokens=estimated_tokens
        )
        
        return confirmation.to_dict()
    
    else:
        # Small email, fetch directly (no confirmation needed)
        return gmail_get_message_parsed(
            message_id, 
            include_attachments=True,
            output_format='json',
            **kwargs
        )


def gmail_analyze_thread_smart(thread_id: str, max_messages: int = 20, **kwargs) -> Dict[str, Any]:
    """
    SMART thread analysis with automatic confirmation for large threads
    
    Args:
        thread_id: Gmail thread ID
        max_messages: Max messages to analyze
        **kwargs: Credential injection
    
    Returns:
        - If small thread: Timeline directly
        - If large thread: Confirmation request
    
    Example:
        # Small thread (3 messages, no attachments)
        result = gmail_analyze_thread_smart('thread_123')
        # Returns: {thread_id, messages: [...], ...}
        
        # Large thread (10 messages with PDFs)
        result = gmail_analyze_thread_smart('thread_456')
        # Returns: {status: 'confirmation_required', ...}
    """
    # First, get thread timeline (lightweight)
    try:
        timeline = gmail_get_thread_parsed(
            thread_id,
            max_messages=max_messages,
            output_format='json',  # Just timeline, no full content
            **kwargs
        )
    except Exception as e:
        return {
            'error': True,
            'message': f"Failed to fetch thread: {e}"
        }
    
    # Analyze thread complexity
    message_count = timeline.get('message_count', 0)
    estimated_tokens = timeline.get('token_estimate', 0)
    
    # Check if this is a complex thread
    needs_confirmation = ConfirmationManager.should_confirm(
        tokens=estimated_tokens,
        level=ConfirmationLevel.HIGH if message_count > 5 else ConfirmationLevel.LOW
    )
    
    if needs_confirmation:
        # Estimate cost
        cost_usd = (estimated_tokens / 1_000_000) * 3
        
        # Create confirmation
        from core.confirmation_manager import ConfirmationRequest, ConfirmationLevel as CL
        
        confirmation = ConfirmationRequest(
            tool_name="gmail_get_thread_parsed",
            operation_summary=f"Analyze email thread: '{timeline.get('subject', 'Unknown')}'",
            reason=f"Thread has {message_count} messages",
            level=CL.HIGH.value if message_count > 10 else CL.MEDIUM.value,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=cost_usd,
            affected_items=[f"{message_count} email messages"],
            tool_args={
                'thread_id': thread_id,
                'max_messages': max_messages
            },
            options=[
                {
                    "label": "Analyze Full Thread (PDF)",
                    "value": "pdf",
                    "description": f"Convert {message_count} messages to comprehensive PDF (~{estimated_tokens:,} tokens)"
                },
                {
                    "label": "Timeline Only (JSON)",
                    "value": "json",
                    "description": f"Just show conversation timeline (~{estimated_tokens // 10:,} tokens)"
                },
                {
                    "label": "Cancel",
                    "value": "cancel",
                    "description": "Skip this thread"
                }
            ],
            default_option="pdf"
        )
        
        return confirmation.to_dict()
    
    else:
        # Small thread, return timeline
        return timeline


def gmail_search_smart(query: str, max_results: int = 10, **kwargs) -> Dict[str, Any]:
    """
    SMART search that automatically analyzes result complexity
    
    Args:
        query: Search query
        max_results: Max results to return
        **kwargs: Credential injection
    
    Returns:
        Search results with intelligent suggestions
    
    Example:
        result = gmail_search_smart('contract review')
        # Returns: {
        #     'results': [...],
        #     'suggestion': 'Found 5 threads. Use gmail_analyze_thread_smart to read them.'
        # }
    """
    # Perform search
    try:
        results = gmail_list_messages(
            max_results=max_results,
            query=query,
            **kwargs
        )
    except Exception as e:
        return {
            'error': True,
            'message': f"Search failed: {e}"
        }
    
    # Analyze results
    message_count = len(results.get('messages', []))
    
    # Add intelligent suggestions
    suggestion = ""
    if message_count == 0:
        suggestion = "No emails found matching your query."
    elif message_count == 1:
        suggestion = f"Found 1 email. Use gmail_analyze_email_smart('{results['messages'][0]['id']}') to read it."
    elif message_count <= 5:
        suggestion = f"Found {message_count} emails. Use gmail_analyze_email_smart() for individual emails or gmail_analyze_thread_smart() for threads."
    else:
        suggestion = f"Found {message_count} emails. Consider refining your search query or analyzing threads instead of individual emails."
    
    return {
        **results,
        'suggestion': suggestion,
        'next_actions': [
            'gmail_analyze_email_smart(message_id)' if message_count > 0 else None,
            'gmail_analyze_thread_smart(thread_id)' if message_count > 0 else None,
            'gmail_search_smart(query, max_results)' if message_count >= max_results else None
        ]
    }
