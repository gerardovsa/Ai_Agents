"""
Gmail Tool Implementations
==========================

Wrapper functions for Gmail SMART bundled tools and basic operations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from google_workspace import gmail


# ==================== GMAIL SMART BUNDLED TOOLS ====================

def gmail_ai_smart_compose_and_send_impl(prompt, recipients, cc=None, bcc=None,
                                         tone="professional", send_immediately=True,
                                         attachments=None, create_calendar_event=False):
    """
    🤖 SMART TOOL: AI-powered email composition and sending.
    
    Wrapper for gmail.gmail_ai_smart_compose_and_send()
    """
    try:
        # Validate parameters
        if not prompt or not isinstance(prompt, str):
            return {"error": "prompt must be a non-empty string"}
        
        if not recipients or not isinstance(recipients, list):
            return {"error": "recipients must be a list of email addresses"}
        
        if tone not in ["professional", "casual", "formal", "friendly"]:
            return {"error": "tone must be: professional, casual, formal, or friendly"}
        
        # Call Gmail function
        result = gmail.gmail_ai_smart_compose_and_send(
            prompt=prompt,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            tone=tone,
            send_immediately=send_immediately,
            attachments=attachments,
            create_calendar_event=create_calendar_event
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def gmail_smart_bulk_send_personalized_impl(template, recipients_data, subject_template,
                                             cc=None, bcc=None, delay_seconds=2):
    """
    📧 SMART TOOL: Bulk personalized email sending with mail merge.
    
    Wrapper for gmail.gmail_smart_bulk_send_personalized()
    """
    try:
        # Validate parameters
        if not template or not isinstance(template, str):
            return {"error": "template must be a non-empty string"}
        
        if not recipients_data or not isinstance(recipients_data, list):
            return {"error": "recipients_data must be a list of objects"}
        
        if not subject_template or not isinstance(subject_template, str):
            return {"error": "subject_template must be a non-empty string"}
        
        # Validate each recipient has email field
        for recipient in recipients_data:
            if not recipient.get('email'):
                return {"error": f"All recipients must have 'email' field. Missing in: {recipient}"}
        
        # Call Gmail function
        result = gmail.gmail_smart_bulk_send_personalized(
            template=template,
            recipients_data=recipients_data,
            subject_template=subject_template,
            cc=cc,
            bcc=bcc,
            delay_seconds=delay_seconds
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def gmail_smart_bulk_read_summarize_prioritize_impl(query="is:unread", max_messages=50,
                                                     summarize=True, prioritize=True,
                                                     create_spreadsheet=False):
    """
    📖 SMART TOOL: Bulk read, summarize, and prioritize emails.
    
    Wrapper for gmail.gmail_smart_bulk_read_summarize_prioritize()
    """
    try:
        # Validate parameters
        if not isinstance(max_messages, int) or max_messages < 1:
            return {"error": "max_messages must be a positive integer"}
        
        # Call Gmail function
        result = gmail.gmail_smart_bulk_read_summarize_prioritize(
            query=query,
            max_messages=max_messages,
            summarize=summarize,
            prioritize=prioritize,
            create_spreadsheet=create_spreadsheet
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def gmail_smart_auto_reply_draft_creator_impl(message_ids, response_type="acknowledge",
                                               tone="professional", custom_instructions=None,
                                               create_drafts=True):
    """
    💬 SMART TOOL: Auto-generate reply drafts for multiple emails.
    
    Wrapper for gmail.gmail_smart_auto_reply_draft_creator()
    """
    try:
        # Validate parameters
        if not message_ids or not isinstance(message_ids, list):
            return {"error": "message_ids must be a list"}
        
        if response_type not in ["acknowledge", "answer", "decline", "accept", "custom"]:
            return {"error": "response_type must be: acknowledge, answer, decline, accept, or custom"}
        
        if tone not in ["professional", "casual", "formal", "friendly"]:
            return {"error": "tone must be: professional, casual, formal, or friendly"}
        
        # Call Gmail function
        result = gmail.gmail_smart_auto_reply_draft_creator(
            message_ids=message_ids,
            response_type=response_type,
            tone=tone,
            custom_instructions=custom_instructions,
            create_drafts=create_drafts
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def gmail_smart_inbox_organizer_cleaner_impl(action="organize", categories=None,
                                              rules=None, process_existing=True,
                                              archive_older_than_days=None,
                                              delete_spam=False):
    """
    🗂️ SMART TOOL: Organize, clean, and auto-filter inbox.
    
    Wrapper for gmail.gmail_smart_inbox_organizer_cleaner()
    """
    try:
        # Validate parameters
        if action not in ["organize", "cleanup", "auto_filter", "full"]:
            return {"error": "action must be: organize, cleanup, auto_filter, or full"}
        
        if archive_older_than_days is not None:
            if not isinstance(archive_older_than_days, int) or archive_older_than_days < 1:
                return {"error": "archive_older_than_days must be a positive integer"}
        
        # Call Gmail function
        result = gmail.gmail_smart_inbox_organizer_cleaner(
            action=action,
            categories=categories,
            rules=rules,
            process_existing=process_existing,
            archive_older_than_days=archive_older_than_days,
            delete_spam=delete_spam
        )
        
        return {
            "success": True,
            **result
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ==================== BASIC GMAIL TOOLS ====================

def gmail_send_email_impl(to, subject, body, cc=None, bcc=None, attachments=None):
    """Send an email"""
    try:
        result = gmail.gmail_send_email(to, subject, body, cc, bcc, attachments)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_create_draft_impl(to, subject, body, cc=None, bcc=None):
    """Create a draft email"""
    try:
        result = gmail.gmail_create_draft(to, subject, body, cc, bcc)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_send_draft_impl(draft_id):
    """Send an existing draft"""
    try:
        result = gmail.gmail_send_draft(draft_id)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_list_messages_impl(max_results=10, query=None, label_ids=None):
    """List messages"""
    try:
        result = gmail.gmail_list_messages(max_results, query, label_ids)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_get_message_impl(message_id, format='full'):
    """Get a specific message"""
    try:
        result = gmail.gmail_get_message(message_id, format)
        return {"success": True, "message": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_search_messages_impl(query, max_results=10):
    """Search messages"""
    try:
        result = gmail.gmail_search_messages(query, max_results)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_archive_message_impl(message_id):
    """Archive a message"""
    try:
        result = gmail.gmail_archive_message(message_id)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_delete_message_impl(message_id):
    """Delete a message"""
    try:
        result = gmail.gmail_delete_message(message_id)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_mark_as_read_impl(message_id):
    """Mark message as read"""
    try:
        result = gmail.gmail_mark_as_read(message_id)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_mark_as_unread_impl(message_id):
    """Mark message as unread"""
    try:
        result = gmail.gmail_mark_as_unread(message_id)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_list_labels_impl():
    """List all labels"""
    try:
        result = gmail.gmail_list_labels()
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_create_label_impl(name, label_list_visibility='labelShow', message_list_visibility='show'):
    """Create a label"""
    try:
        result = gmail.gmail_create_label(name, label_list_visibility, message_list_visibility)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_create_filter_impl(criteria, action):
    """Create an email filter"""
    try:
        result = gmail.gmail_create_filter(criteria, action)
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def gmail_list_filters_impl():
    """List all filters"""
    try:
        result = gmail.gmail_list_filters()
        return {"success": True, **result}
    except Exception as e:
        return {"success": False, "error": str(e)}
