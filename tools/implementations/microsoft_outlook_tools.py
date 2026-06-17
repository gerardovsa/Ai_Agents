"""
Microsoft 365 Outlook Email Tools
Provides comprehensive email management capabilities via Microsoft Graph API
"""

import os
import requests
import base64
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class MicrosoftOutlookTools:
    """Microsoft 365 Outlook email management tools"""
    
    def __init__(self):
        # Credentials are injected dynamically per-user via credential_injector
        # No need to check environment variables at init time
        self.graph_api_base = 'https://graph.microsoft.com/v1.0'
    
    def _get_headers(self, **kwargs) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
        # Get access token from credential injector
        if '_user_id' in kwargs:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'AI_infrastructure'))
            from auth.credential_injector import get_microsoft_access_token
            access_token = get_microsoft_access_token(**kwargs)
        else:
            raise Exception("No user credentials provided. User must be authenticated.")
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, **kwargs) -> Dict:
        """Make HTTP request to Microsoft Graph API"""
        url = f"{self.graph_api_base}{endpoint}"
        
        print(f"\n[MICROSOFT OUTLOOK] Making {method} request to: {endpoint}")
        if data:
            print(f"[MICROSOFT OUTLOOK] Request data keys: {list(data.keys())}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self._get_headers(**kwargs), params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self._get_headers(**kwargs), json=data, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self._get_headers(**kwargs), json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self._get_headers(**kwargs))
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}'}
            
            print(f"[MICROSOFT OUTLOOK] Response status: {response.status_code}")
            print(f"[MICROSOFT OUTLOOK] Response body length: {len(response.text)}")
            
            response.raise_for_status()
            
            # Some endpoints return 204 No Content or 202 Accepted with empty body
            if response.status_code in (202, 204):
                return {'success': True}
            
            # Some endpoints return empty response on success
            if not response.text or response.text.strip() == '':
                return {'success': True}
            
            try:
                return {'success': True, 'data': response.json()}
            except ValueError as json_error:
                # Response was successful but not JSON (e.g., empty body)
                print(f"[WARNING] Response not JSON: {response.status_code}, body length: {len(response.text)}")
                return {'success': True, 'data': None}
            
        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            try:
                error_data = e.response.json()
                error_msg = error_data.get('error', {}).get('message', str(e))
            except:
                pass
            return {'success': False, 'error': error_msg, 'status_code': e.response.status_code}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def outlook_send_email(self, to: List[str], subject: str, body: str, 
                          body_type: str = 'html', cc: List[str] = None, 
                          bcc: List[str] = None, importance: str = 'normal',
                          attachments: List[Dict] = None, 
                          request_read_receipt: bool = False, **kwargs) -> Dict:
        """
        TEMPORARILY DISABLED: Send an email via Outlook
        
        CURRENT BEHAVIOR: Saves email as draft instead of sending
        This is a temporary measure - the email will be saved to your Outlook Drafts folder
        for manual review and sending.
        """
        
        print(f"\n[MICROSOFT OUTLOOK] outlook_send_email called (SAVING AS DRAFT):")
        print(f"  - To: {to}")
        print(f"  - Subject: {subject}")
        print(f"  - Has credentials in kwargs: {'access_token' in kwargs}")
        if 'access_token' in kwargs:
            token = kwargs['access_token']
            print(f"  - Token length: {len(token) if token else 0}")
        
        # Helper to parse recipients - handle both string and list inputs
        def parse_recipients(recipients):
            if isinstance(recipients, str):
                # Check if it's a string representation of a Python list (e.g., "['email@example.com']")
                if recipients.startswith('[') and recipients.endswith(']'):
                    try:
                        # Try to evaluate it safely as a list
                        import ast
                        evaluated = ast.literal_eval(recipients)
                        if isinstance(evaluated, list):
                            # Recursively parse the evaluated list
                            return parse_recipients(evaluated)
                    except (ValueError, SyntaxError):
                        # If evaluation fails, treat as single email
                        pass
                
                # Normal string - split by comma and clean up
                return [addr.strip() for addr in recipients.split(',') if addr.strip()]
            elif isinstance(recipients, list):
                # If list, flatten and handle string items
                result = []
                for item in recipients:
                    if isinstance(item, str):
                        result.append(item.strip())
                    elif isinstance(item, dict) and 'emailAddress' in item:
                        result.append(item['emailAddress'].get('address', ''))
                return [r for r in result if r]
            return []
        
        # Parse all recipient fields
        to_emails = parse_recipients(to)
        cc_emails = parse_recipients(cc) if cc else []
        bcc_emails = parse_recipients(bcc) if bcc else []
        
        if not to_emails:
            return {'success': False, 'error': 'At least one recipient is required in "to" field'}
        
        # MODIFIED: Create draft instead of sending
        message = {
            'subject': subject,
            'importance': importance,
            'body': {
                'contentType': body_type.upper() if body_type == 'html' else 'Text',
                'content': body
            },
            'toRecipients': [{'emailAddress': {'address': email}} for email in to_emails]
        }
        
        if cc_emails:
            message['ccRecipients'] = [{'emailAddress': {'address': email}} for email in cc_emails]
        
        if bcc_emails:
            message['bccRecipients'] = [{'emailAddress': {'address': email}} for email in bcc_emails]
        
        if request_read_receipt:
            message['isReadReceiptRequested'] = True
        
        if attachments:
            message['attachments'] = []
            for att in attachments:
                message['attachments'].append({
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': att.get('name'),
                    'contentType': att.get('content_type', 'application/octet-stream'),
                    'contentBytes': att.get('content')  # Should be base64 encoded
                })
        
        # MODIFIED: Save as draft instead of sending
        result = self._make_request('POST', '/me/messages', message, **kwargs)
        
        if result['success']:
            draft = result.get('data', {})
            return {
                'success': True,
                'message': f'⚠️ EMAIL SAVED AS DRAFT (not sent) - {len(to_emails)} recipient(s)',
                'note': 'This email was saved to your Outlook Drafts folder for manual review and sending.',
                'recipients': to_emails,
                'draft_id': draft.get('id'),
                'action_required': 'Please open Outlook and send this email manually from your Drafts folder.'
            }
        return result
        
        # COMMENTED OUT: Original send implementation
        # result = self._make_request('POST', '/me/sendMail', {'message': message}, **kwargs)
        # 
        # if result['success']:
        #     return {
        #         'success': True,
        #         'message': f'Email sent to {len(to_emails)} recipient(s)',
        #         'recipients': to_emails
        #     }
        # return result
    
    def outlook_smart_bulk_send_personalized(self, subject_template: str, body_template: str,
                                            recipients: List[Dict], importance: str = 'normal',
                                            delay_seconds: int = 1, **kwargs) -> Dict:
        """Send personalized bulk emails with mail merge"""
        
        results = {
            'success': True,
            'sent': [],
            'failed': [],
            'total': len(recipients)
        }
        
        for idx, recipient in enumerate(recipients):
            email = recipient.get('email')
            merge_fields = recipient.get('merge_fields', {})
            
            # Replace placeholders
            personalized_subject = subject_template
            personalized_body = body_template
            
            for key, value in merge_fields.items():
                placeholder = f'{{{{{key}}}}}'  # {{key}}
                personalized_subject = personalized_subject.replace(placeholder, str(value))
                personalized_body = personalized_body.replace(placeholder, str(value))
            
            # Send email
            send_result = self.outlook_send_email(
                to=[email],
                subject=personalized_subject,
                body=personalized_body,
                importance=importance
            )
            
            if send_result['success']:
                results['sent'].append({'email': email, 'status': 'sent'})
            else:
                results['failed'].append({'email': email, 'error': send_result.get('error')})
            
            # Rate limiting delay
            if idx < len(recipients) - 1:
                time.sleep(delay_seconds)
        
        results['success'] = len(results['failed']) == 0
        results['message'] = f"Sent {len(results['sent'])}/{results['total']} emails"
        
        return results
    
    def outlook_list_messages(self, folder: str = 'inbox', max_results: int = 50,
                             filter: str = None, search: str = None,
                             order_by: str = 'receivedDateTime desc',
                             unread_only: bool = False,
                             page_token: str = None, **kwargs) -> Dict:
        """List messages from a folder

        ✅ Cursor-based pagination via page_token:
           - If page_token is a full https://... URL (Microsoft Graph @odata.nextLink),
             call it as the endpoint directly (bypasses self.graph_api_base prefix).
           - If page_token is a bare $skiptoken value, add it as $skiptoken query param.
           - If page_token is None, fetch the first page.

        Returns dict with `next_page_token` key (None when no more pages).
        """

        # Ensure max_results is an integer (Claude sends strings)
        if isinstance(max_results, str):
            max_results = int(max_results)

        params = {
            '$top': min(max_results, 500),
            '$orderby': order_by,
            '$select': 'id,subject,from,receivedDateTime,isRead,hasAttachments,importance,bodyPreview,conversationId'
        }

        if filter:
            params['$filter'] = filter
        elif unread_only:
            params['$filter'] = 'isRead eq false'

        if search:
            params['$search'] = f'"{search}"'

        endpoint = f'/me/mailFolders/{folder}/messages' if folder else '/me/messages'

        # ✅ Cursor pagination: three branches
        if page_token and page_token.startswith('http'):
            # Full nextLink URL — bypass the graph_api_base prefix that
            # _make_request would otherwise prepend.
            result = self._make_request('GET', page_token, **kwargs)
        elif page_token:
            # Bare $skiptoken value (or other continuation token)
            params['$skiptoken'] = page_token
            result = self._make_request('GET', endpoint, params=params, **kwargs)
        else:
            # First page
            result = self._make_request('GET', endpoint, params=params, **kwargs)

        if result['success']:
            data = result.get('data') or {}
            messages = data.get('value', [])
            return {
                'success': True,
                'count': len(messages),
                'messages': messages,
                # None when @odata.nextLink is absent (end of mailbox).
                'next_page_token': data.get('@odata.nextLink'),
            }
        return result
    
    def outlook_get_message(self, message_id: str, include_attachments: bool = False, **kwargs) -> Dict:
        """Get full message details with COMPLETE body content
        
        ⚠️ RENDER DEPLOYMENT FIX: Strips attachment binary content to prevent timeout
        
        Args:
            message_id: Outlook message ID
            include_attachments: If True, returns attachment METADATA only (no binary content)
        
        Returns:
            {
                'success': True,
                'message': {
                    'id': '...',
                    'subject': '...',
                    'body': {...},
                    'attachments': [{  # Only if include_attachments=True
                        'id': 'att123',
                        'name': 'invoice.pdf',
                        'size': 250000,
                        'contentType': 'application/pdf',
                        'download_url': 'https://...',  # ✅ Download separately
                        'note': 'Use microsoft_outlook_download_attachment to get content'
                    }]
                }
            }
        """
        
        # Build endpoint with explicit field selection to get FULL body content
        # Use $select to ensure we get body, uniqueBody (full content without quoted replies)
        select_fields = 'id,subject,from,toRecipients,ccRecipients,receivedDateTime,sentDateTime,isRead,hasAttachments,importance,body,uniqueBody,bodyPreview'
        
        if include_attachments:
            # 🚀 CRITICAL: Only request attachment METADATA - exclude contentBytes to prevent 1M+ token responses
            # This prevents base64 attachment content from being returned by Microsoft Graph API
            # Note: contentId is not a valid field in Graph API attachment schema (removed)
            attachment_select = '$select=id,name,contentType,size,isInline,lastModifiedDateTime'
            endpoint = f'/me/messages/{message_id}?$select={select_fields}&$expand=attachments({attachment_select})'
        else:
            endpoint = f'/me/messages/{message_id}?$select={select_fields}'
        
        result = self._make_request('GET', endpoint, **kwargs)
        
        if result['success']:
            message_data = result['data']
            
            # 🚀 RENDER FIX: Strip attachment binary content to prevent token overflow
            if include_attachments and 'attachments' in message_data:
                safe_attachments = []
                inline_filtered_count = 0
                
                for att in message_data.get('attachments', []):
                    # 🎯 FILTER: Skip inline attachments (email footers, signature images)
                    # Inline attachments have isInline=True (embedded in HTML body)
                    is_inline = att.get('isInline', False)
                    
                    if is_inline:
                        inline_filtered_count += 1
                        continue  # Skip email footer/signature images
                    
                    safe_att = {
                        'id': att.get('id'),
                        'name': att.get('name'),
                        'contentType': att.get('contentType'),
                        'size': att.get('size'),
                        'isInline': False,  # Guaranteed false at this point
                        'download_url': f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments/{att.get('id')}",
                        'note': '⚠️ Binary content stripped. Use microsoft_outlook_download_attachment to retrieve.'
                    }
                    safe_attachments.append(safe_att)
                
                message_data['attachments'] = safe_attachments
                print(f"🚀 [RENDER FIX] Stripped binary content from {len(safe_attachments)} attachment(s)")
                if inline_filtered_count > 0:
                    print(f"🎯 [INLINE FILTER] Excluded {inline_filtered_count} inline attachment(s) (email footers/signatures)")
            
            # 🔍 DEBUG: Log body content from Microsoft Graph API
            body = message_data.get('body', {})
            body_content = body.get('content', '')
            unique_body = message_data.get('uniqueBody', {})
            unique_body_content = unique_body.get('content', '')
            body_preview = message_data.get('bodyPreview', '')
            
            print(f"\n🔍 [OUTLOOK API DEBUG] Message ID: {message_id}")
            print(f"🔍 [OUTLOOK API DEBUG] Body content length: {len(body_content)}")
            print(f"🔍 [OUTLOOK API DEBUG] UniqueBody content length: {len(unique_body_content)}")
            print(f"🔍 [OUTLOOK API DEBUG] Body preview length: {len(body_preview)}")
            print(f"🔍 [OUTLOOK API DEBUG] Body content type: {body.get('contentType', 'N/A')}")
            print(f"🔍 [OUTLOOK API DEBUG] UniqueBody content type: {unique_body.get('contentType', 'N/A')}")
            
            return {
                'success': True,
                'message': message_data
            }
        return result
    
    def outlook_search_messages(self, query: str, from_email: str = None,
                               has_attachments: bool = None, date_from: str = None,
                               date_to: str = None, max_results: int = 50, **kwargs) -> Dict:
        """Advanced message search"""
        
        # Ensure max_results is an integer (Claude sends strings)
        if isinstance(max_results, str):
            max_results = int(max_results)
        
        filters = []
        
        if from_email:
            filters.append(f"from/emailAddress/address eq '{from_email}'")
        
        if has_attachments is not None:
            filters.append(f"hasAttachments eq {str(has_attachments).lower()}")
        
        if date_from:
            filters.append(f"receivedDateTime ge {date_from}T00:00:00Z")
        
        if date_to:
            filters.append(f"receivedDateTime le {date_to}T23:59:59Z")
        
        params = {
            '$search': f'"{query}"',
            '$top': min(max_results, 500),
            '$select': 'id,subject,from,receivedDateTime,isRead,hasAttachments,importance,bodyPreview'
        }
        
        if filters:
            params['$filter'] = ' and '.join(filters)
        
        result = self._make_request('GET', '/me/messages', params=params, **kwargs)
        
        if result['success']:
            messages = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(messages),
                'query': query,
                'messages': messages
            }
        return result
    
    def outlook_mark_as_read(self, message_ids: List[str], is_read: bool, **kwargs) -> Dict:
        """Mark messages as read or unread"""
        
        results = {'success': True, 'updated': [], 'failed': []}
        
        for msg_id in message_ids:
            result = self._make_request('PATCH', f'/me/messages/{msg_id}', {'isRead': is_read}, **kwargs)
            
            if result['success']:
                results['updated'].append(msg_id)
            else:
                results['failed'].append({'id': msg_id, 'error': result.get('error')})
        
        results['success'] = len(results['failed']) == 0
        results['message'] = f"Updated {len(results['updated'])}/{len(message_ids)} messages"
        
        return results
    
    def outlook_move_message(self, message_ids: List[str], destination_folder: str, **kwargs) -> Dict:
        """Move messages to a folder"""
        
        results = {'success': True, 'moved': [], 'failed': []}
        
        for msg_id in message_ids:
            result = self._make_request('POST', f'/me/messages/{msg_id}/move', 
                                       {'destinationId': destination_folder}, **kwargs)
            
            if result['success']:
                results['moved'].append(msg_id)
            else:
                results['failed'].append({'id': msg_id, 'error': result.get('error')})
        
        results['success'] = len(results['failed']) == 0
        results['message'] = f"Moved {len(results['moved'])}/{len(message_ids)} messages"
        
        return results
    
    def outlook_delete_message(self, message_ids: List[str], permanent: bool = False, **kwargs) -> Dict:
        """Delete messages"""
        
        results = {'success': True, 'deleted': [], 'failed': []}
        
        for msg_id in message_ids:
            if permanent:
                result = self._make_request('DELETE', f'/me/messages/{msg_id}', **kwargs)
            else:
                # Move to deleted items
                deleted_items_result = self._make_request('GET', '/me/mailFolders/deleteditems', **kwargs)
                if deleted_items_result['success']:
                    deleted_folder_id = deleted_items_result['data']['id']
                    result = self._make_request('POST', f'/me/messages/{msg_id}/move',
                                               {'destinationId': deleted_folder_id}, **kwargs)
                else:
                    result = deleted_items_result
            
            if result['success']:
                results['deleted'].append(msg_id)
            else:
                results['failed'].append({'id': msg_id, 'error': result.get('error')})
        
        results['success'] = len(results['failed']) == 0
        results['message'] = f"Deleted {len(results['deleted'])}/{len(message_ids)} messages"
        
        return results
    
    def outlook_create_folder(self, display_name: str, parent_folder: str = None, **kwargs) -> Dict:
        """Create a mail folder"""
        
        data = {'displayName': display_name}
        
        if parent_folder:
            endpoint = f'/me/mailFolders/{parent_folder}/childFolders'
        else:
            endpoint = '/me/mailFolders'
        
        result = self._make_request('POST', endpoint, data, **kwargs)
        
        if result['success']:
            folder = result['data']
            return {
                'success': True,
                'folder_id': folder.get('id'),
                'folder_name': folder.get('displayName'),
                'folder': folder
            }
        return result
    
    def outlook_list_folders(self, **kwargs) -> Dict:
        """List all mail folders"""
        
        result = self._make_request('GET', '/me/mailFolders', **kwargs)
        
        if result['success']:
            folders = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(folders),
                'folders': [{'id': f['id'], 'name': f['displayName'], 
                           'total': f.get('totalItemCount', 0),
                           'unread': f.get('unreadItemCount', 0)} for f in folders]
            }
        return result
    
    def outlook_create_draft(self, to: List[str], subject: str, body: str,
                            body_type: str = 'html', cc: List[str] = None, **kwargs) -> Dict:
        """Create a draft email"""
        
        message = {
            'subject': subject,
            'body': {
                'contentType': body_type.upper() if body_type == 'html' else 'Text',
                'content': body
            },
            'toRecipients': [{'emailAddress': {'address': email}} for email in to]
        }
        
        if cc:
            message['ccRecipients'] = [{'emailAddress': {'address': email}} for email in cc]
        
        result = self._make_request('POST', '/me/messages', message, **kwargs)
        
        if result['success']:
            draft = result['data']
            return {
                'success': True,
                'draft_id': draft.get('id'),
                'message': 'Draft created successfully',
                'draft': draft
            }
        return result
    
    def outlook_send_draft(self, message_id: str, **kwargs) -> Dict:
        """
        DEACTIVATED - This function no longer sends emails.
        Returns draft information for manual sending.
        """
        
        # Get the draft message details instead of sending
        result = self._make_request('GET', f'/me/messages/{message_id}', **kwargs)
        
        if result['success']:
            message_data = result.get('data', {})
            return {
                'success': True,
                'message': '⚠️ EMAIL SAVED AS DRAFT (not sent)',
                'note': 'This email was saved to your Outlook Drafts folder and was NOT sent',
                'action_required': 'Please open Outlook and manually send this draft if needed',
                'message_id': message_id,
                'subject': message_data.get('subject', 'N/A'),
                'to': [r.get('emailAddress', {}).get('address') for r in message_data.get('toRecipients', [])],
                'draft_folder': 'Drafts'
            }
        return result
    
    def outlook_reply_to_message(self, message_id: str, body: str, 
                                reply_all: bool = False, body_type: str = 'html', **kwargs) -> Dict:
        """Create a reply draft (does not send)"""
        
        # Get original message details
        original_result = self._make_request('GET', f'/me/messages/{message_id}', **kwargs)
        
        if not original_result['success']:
            return original_result
        
        original = original_result.get('data', {})
        reply_type = 'Reply All' if reply_all else 'Reply'
        
        # Extract sender email properly
        sender = original.get('from', {})
        sender_email = sender.get('emailAddress', {}) if isinstance(sender, dict) else {}
        
        # Create draft reply message
        draft_message = {
            'subject': f"RE: {original.get('subject', 'No Subject')}",
            'body': {
                'contentType': body_type,
                'content': body
            },
            'toRecipients': [sender_email] if sender_email else []
        }
        
        if reply_all and original.get('toRecipients'):
            draft_message['toRecipients'].extend(original.get('toRecipients', []))
            if original.get('ccRecipients'):
                draft_message['ccRecipients'] = original.get('ccRecipients', [])
        
        # Save as draft instead of sending
        result = self._make_request('POST', '/me/messages', draft_message, **kwargs)
        
        if result['success']:
            draft = result.get('data', {})
            return {
                'success': True,
                'message': f'⚠️ {reply_type.upper()} SAVED AS DRAFT (not sent)',
                'note': f'Reply draft created in Outlook Drafts folder for manual sending',
                'action_required': 'Please open Outlook and send this reply manually from your Drafts folder',
                'draft_id': draft.get('id'),
                'original_message_id': message_id,
                'reply_type': reply_type
            }
        return result
    
    def outlook_forward_message(self, message_id: str, to: List[str], comment: str = None, **kwargs) -> Dict:
        """Create a forward draft (does not send)"""
        
        # Get original message details
        original_result = self._make_request('GET', f'/me/messages/{message_id}', **kwargs)
        
        if not original_result['success']:
            return original_result
        
        original = original_result.get('data', {})
        
        # Parse recipient emails (handle both string and list inputs)
        def parse_recipients(recipients):
            if isinstance(recipients, str):
                return [addr.strip() for addr in recipients.split(',') if addr.strip()]
            elif isinstance(recipients, list):
                result = []
                for item in recipients:
                    if isinstance(item, str):
                        result.append(item.strip())
                    elif isinstance(item, dict) and 'emailAddress' in item:
                        result.append(item['emailAddress'].get('address', ''))
                return [r for r in result if r]
            return []
        
        to_emails = parse_recipients(to)
        
        if not to_emails:
            return {'success': False, 'error': 'At least one recipient is required in "to" field'}
        
        # Create draft forward message
        draft_message = {
            'subject': f"FW: {original.get('subject', 'No Subject')}",
            'body': {
                'contentType': 'html',
                'content': f"{comment or ''}<br><br>---------- Forwarded message ----------<br>{original.get('bodyPreview', '')}"
            },
            'toRecipients': [{'emailAddress': {'address': email}} for email in to_emails]
        }
        
        # Save as draft instead of sending
        result = self._make_request('POST', '/me/messages', draft_message, **kwargs)
        
        if result['success']:
            draft = result.get('data', {})
            return {
                'success': True,
                'message': f'⚠️ FORWARD SAVED AS DRAFT (not sent) - {len(to_emails)} recipient(s)',
                'note': 'Forward draft created in Outlook Drafts folder for manual sending',
                'action_required': 'Please open Outlook and send this forward manually from your Drafts folder',
                'draft_id': draft.get('id'),
                'recipients': to_emails,
                'original_message_id': message_id
            }
        return result
    
    def outlook_add_category(self, message_ids: List[str], categories: List[str], **kwargs) -> Dict:
        """Add categories to messages"""
        
        results = {'success': True, 'updated': [], 'failed': []}
        
        for msg_id in message_ids:
            # Get current categories
            msg_result = self._make_request('GET', f'/me/messages/{msg_id}', **kwargs)
            if not msg_result['success']:
                results['failed'].append({'id': msg_id, 'error': msg_result.get('error')})
                continue
            
            current_categories = msg_result['data'].get('categories', [])
            new_categories = list(set(current_categories + categories))
            
            # Update categories
            update_result = self._make_request('PATCH', f'/me/messages/{msg_id}',
                                              {'categories': new_categories}, **kwargs)
            
            if update_result['success']:
                results['updated'].append(msg_id)
            else:
                results['failed'].append({'id': msg_id, 'error': update_result.get('error')})
        
        results['success'] = len(results['failed']) == 0
        results['message'] = f"Updated {len(results['updated'])}/{len(message_ids)} messages"
        
        return results
    
    def outlook_flag_message(self, message_ids: List[str], flag_status: str, due_date: str = None, **kwargs) -> Dict:
        """Flag messages for follow-up"""
        
        results = {'success': True, 'flagged': [], 'failed': []}
        
        flag_data = {'flag': {'flagStatus': flag_status}}
        
        if due_date and flag_status == 'flagged':
            flag_data['flag']['dueDateTime'] = {
                'dateTime': due_date,
                'timeZone': 'UTC'
            }
        
        for msg_id in message_ids:
            result = self._make_request('PATCH', f'/me/messages/{msg_id}', flag_data, **kwargs)
            
            if result['success']:
                results['flagged'].append(msg_id)
            else:
                results['failed'].append({'id': msg_id, 'error': result.get('error')})
        
        results['success'] = len(results['failed']) == 0
        results['message'] = f"Flagged {len(results['flagged'])}/{len(message_ids)} messages"
        
        return results
    
    def outlook_smart_organize_inbox(self, rules: List[Dict], create_folders: bool = True,
                                    max_messages: int = 100, **kwargs) -> Dict:
        """Smart inbox organization"""
        
        # Get folders first
        folders_result = self.outlook_list_folders()
        if not folders_result['success']:
            return folders_result
        
        existing_folders = {f['name']: f['id'] for f in folders_result['folders']}
        
        # Create missing folders if needed
        folder_map = {}
        for rule in rules:
            folder_name = rule.get('folder')
            if folder_name in existing_folders:
                folder_map[folder_name] = existing_folders[folder_name]
            elif create_folders:
                create_result = self.outlook_create_folder(folder_name)
                if create_result['success']:
                    folder_map[folder_name] = create_result['folder_id']
        
        # Get inbox messages
        messages_result = self.outlook_list_messages(folder='inbox', max_results=max_messages)
        if not messages_result['success']:
            return messages_result
        
        messages = messages_result['messages']
        
        # Apply rules
        organized = {'success': True, 'rules_applied': {}, 'errors': []}
        
        for rule in rules:
            rule_name = rule.get('name')
            folder_name = rule.get('folder')
            from_contains = rule.get('from_contains', [])
            subject_contains = rule.get('subject_contains', [])
            mark_as_read = rule.get('mark_as_read', False)
            
            if folder_name not in folder_map:
                continue
            
            matched_messages = []
            
            for msg in messages:
                from_email = msg.get('from', {}).get('emailAddress', {}).get('address', '').lower()
                subject = msg.get('subject', '').lower()
                
                # Check if message matches rule
                matches = False
                
                for from_pattern in from_contains:
                    if from_pattern.lower() in from_email:
                        matches = True
                        break
                
                for subject_pattern in subject_contains:
                    if subject_pattern.lower() in subject:
                        matches = True
                        break
                
                if matches:
                    matched_messages.append(msg['id'])
            
            if matched_messages:
                # Move messages
                move_result = self.outlook_move_message(matched_messages, folder_map[folder_name])
                
                # Mark as read if specified
                if mark_as_read and move_result['success']:
                    self.outlook_mark_as_read(matched_messages, True)
                
                organized['rules_applied'][rule_name] = {
                    'count': len(matched_messages),
                    'folder': folder_name
                }
        
        return organized
    
    def outlook_smart_email_summary(self, days_back: int = 7, unread_only: bool = True,
                                   group_by: str = 'sender', max_messages: int = 200, **kwargs) -> Dict:
        """Generate email summary"""
        
        # Calculate date filter
        date_from = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        # Get messages
        messages_result = self.outlook_list_messages(
            max_results=max_messages,
            unread_only=unread_only
        )
        
        if not messages_result['success']:
            return messages_result
        
        messages = messages_result['messages']
        
        # Group messages
        summary = {
            'success': True,
            'period': f'Last {days_back} days',
            'total_messages': len(messages),
            'unread_only': unread_only,
            'grouped_by': group_by,
            'groups': {}
        }
        
        for msg in messages:
            if group_by == 'sender':
                key = msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')
            elif group_by == 'importance':
                key = msg.get('importance', 'normal')
            elif group_by == 'date':
                date_str = msg.get('receivedDateTime', '')
                key = date_str.split('T')[0] if date_str else 'Unknown'
            else:
                key = 'Other'
            
            if key not in summary['groups']:
                summary['groups'][key] = {
                    'count': 0,
                    'messages': []
                }
            
            summary['groups'][key]['count'] += 1
            summary['groups'][key]['messages'].append({
                'id': msg.get('id'),
                'subject': msg.get('subject'),
                'date': msg.get('receivedDateTime'),
                'preview': msg.get('bodyPreview', '')[:100]
            })
        
        return summary
    
    def outlook_smart_follow_up_reminder(self, days_without_response: int = 3,
                                        from_important_senders: List[str] = None,
                                        keywords: List[str] = None,
                                        auto_flag: bool = True, **kwargs) -> Dict:
        """Find emails needing follow-up"""
        
        # Get sent emails from X days ago
        date_threshold = (datetime.utcnow() - timedelta(days=days_without_response)).strftime('%Y-%m-%d')
        
        # This would require checking sent items and inbox for response chains
        # Simplified version for now
        
        result = {
            'success': True,
            'message': 'Follow-up reminder feature - placeholder implementation',
            'note': 'Full implementation requires conversation threading analysis'
        }
        
        return result
    
    def outlook_get_attachments(self, message_id: str, download_content: bool = False, **kwargs) -> Dict:
        """Get message attachments"""
        
        result = self._make_request('GET', f'/me/messages/{message_id}/attachments', **kwargs)
        
        if result['success']:
            attachments = result['data'].get('value', [])
            
            attachment_list = []
            for att in attachments:
                att_info = {
                    'id': att.get('id'),
                    'name': att.get('name'),
                    'content_type': att.get('contentType'),
                    'size': att.get('size')
                }
                
                if download_content and att.get('contentBytes'):
                    att_info['content'] = att.get('contentBytes')
                
                attachment_list.append(att_info)
            
            return {
                'success': True,
                'count': len(attachment_list),
                'attachments': attachment_list
            }
        return result
    
    def outlook_download_attachment(self, message_id: str, attachment_id: str, save_to_disk: bool = True, **kwargs) -> Dict:
        """Download specific attachment
        
        ⚠️ IMPORTANT: This tool saves files to disk by default.
        For AI analysis, use microsoft_outlook_process_attachment_for_ai instead!
        
        Args:
            message_id: Outlook message ID
            attachment_id: Attachment ID (will be automatically URL-encoded)
            save_to_disk: If True (default), saves to temp folder and returns path.
                         If False, returns base64 (WARNING: causes token overflow!)
        
        Returns:
            If save_to_disk=True:
                {'success': True, 'file_path': '/path/to/file.pdf', 'name': '...', 'size': 123456}
            If save_to_disk=False:
                {'success': True, 'content': 'base64...', 'name': '...', 'size': 123456}
        """
        # URL-encode the attachment_id to handle special characters like = in Microsoft Graph IDs
        from urllib.parse import quote
        encoded_attachment_id = quote(attachment_id, safe='')
        
        result = self._make_request('GET', f'/me/messages/{message_id}/attachments/{encoded_attachment_id}', **kwargs)
        
        if result['success']:
            import base64
            import tempfile
            import os
            
            attachment = result['data']
            name = attachment.get('name', 'attachment')
            content_type = attachment.get('contentType', 'application/octet-stream')
            size = attachment.get('size', 0)
            content_base64 = attachment.get('contentBytes')
            
            if save_to_disk:
                # Save to temp folder
                temp_dir = tempfile.gettempdir()
                downloads_dir = os.path.join(temp_dir, 'outlook_attachments')
                os.makedirs(downloads_dir, exist_ok=True)
                
                # Generate unique filename
                import time
                timestamp = int(time.time() * 1000)
                file_name = f"{timestamp}_{name}"
                file_path = os.path.join(downloads_dir, file_name)
                
                # Decode and save
                file_bytes = base64.b64decode(content_base64)
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                
                return {
                    'success': True,
                    'file_path': file_path,
                    'name': name,
                    'content_type': content_type,
                    'size': size,
                    'message': f"✅ Attachment saved to: {file_path}"
                }
            else:
                # Return base64 (WARNING: token overflow risk!)
                return {
                    'success': True,
                    'name': name,
                    'content_type': content_type,
                    'size': size,
                    'content': content_base64,  # Base64 encoded
                    'warning': '⚠️ Returning base64 content can cause token overflow! Use save_to_disk=True or microsoft_outlook_process_attachment_for_ai for AI analysis.'
                }
        return result
    
    def outlook_create_inbox_rule(self, display_name: str, conditions: Dict, actions: Dict, **kwargs) -> Dict:
        """
        Create an automatic inbox rule (server-side filtering)
        
        Args:
            display_name: Rule name
            conditions: Rule conditions (e.g., {'fromAddresses': [{'emailAddress': {'address': 'sender@example.com'}}]})
            actions: Actions to perform (e.g., {'moveToFolder': 'folder-id'})
        
        Returns:
            Dict with success status and rule details
        """
        payload = {
            'displayName': display_name,
            'sequence': 1,
            'isEnabled': True,
            'conditions': conditions,
            'actions': actions
        }
        
        result = self._make_request('POST', '/me/mailFolders/inbox/messageRules', data=payload, **kwargs)
        
        if result['success']:
            rule = result['data']
            return {
                'success': True,
                'rule_id': rule.get('id'),
                'display_name': rule.get('displayName'),
                'is_enabled': rule.get('isEnabled'),
                'conditions': rule.get('conditions'),
                'actions': rule.get('actions')
            }
        return result
    
    def outlook_list_inbox_rules(self, **kwargs) -> Dict:
        """
        List all inbox rules configured for the mailbox
        
        Returns:
            Dict with list of rules
        """
        result = self._make_request('GET', '/me/mailFolders/inbox/messageRules', **kwargs)
        
        if result['success']:
            rules = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(rules),
                'rules': [{
                    'rule_id': r.get('id'),
                    'display_name': r.get('displayName'),
                    'sequence': r.get('sequence'),
                    'is_enabled': r.get('isEnabled'),
                    'conditions': r.get('conditions'),
                    'actions': r.get('actions')
                } for r in rules]
            }
        return result


# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS
# ========================================

# Create global instance
microsoft_outlook_tools = MicrosoftOutlookTools()

# Export all functions at module level
# Wrappers handle parameter transformation for registry compatibility

def microsoft_outlook_smart_bulk_send_personalized(**kwargs):
    return microsoft_outlook_tools.outlook_smart_bulk_send_personalized(**kwargs)

def microsoft_outlook_list_messages(**kwargs):
    # Convert string parameters to integers (Claude sends everything as strings in JSON)
    if 'max_results' in kwargs and isinstance(kwargs['max_results'], str):
        kwargs['max_results'] = int(kwargs['max_results'])
    return microsoft_outlook_tools.outlook_list_messages(**kwargs)

def microsoft_outlook_get_message(**kwargs):
    return microsoft_outlook_tools.outlook_get_message(**kwargs)

def microsoft_outlook_search_messages(**kwargs):
    return microsoft_outlook_tools.outlook_search_messages(**kwargs)

def microsoft_outlook_mark_as_read(**kwargs):
    return microsoft_outlook_tools.outlook_mark_as_read(**kwargs)

def microsoft_outlook_move_message(**kwargs):
    return microsoft_outlook_tools.outlook_move_message(**kwargs)

def microsoft_outlook_delete_message(**kwargs):
    return microsoft_outlook_tools.outlook_delete_message(**kwargs)

def microsoft_outlook_create_folder(**kwargs):
    return microsoft_outlook_tools.outlook_create_folder(**kwargs)

def microsoft_outlook_list_folders(**kwargs):
    return microsoft_outlook_tools.outlook_list_folders(**kwargs)

def microsoft_outlook_create_draft(**kwargs):
    return microsoft_outlook_tools.outlook_create_draft(**kwargs)

def microsoft_outlook_send_draft(**kwargs):
    return microsoft_outlook_tools.outlook_send_draft(**kwargs)

def microsoft_outlook_reply_to_message(**kwargs):
    return microsoft_outlook_tools.outlook_reply_to_message(**kwargs)

def microsoft_outlook_forward_message(**kwargs):
    return microsoft_outlook_tools.outlook_forward_message(**kwargs)

def microsoft_outlook_add_category(**kwargs):
    return microsoft_outlook_tools.outlook_add_category(**kwargs)

def microsoft_outlook_flag_message(**kwargs):
    return microsoft_outlook_tools.outlook_flag_message(**kwargs)

def microsoft_outlook_smart_organize_inbox(**kwargs):
    return microsoft_outlook_tools.outlook_smart_organize_inbox(**kwargs)

def microsoft_outlook_smart_email_summary(**kwargs):
    return microsoft_outlook_tools.outlook_smart_email_summary(**kwargs)

def microsoft_outlook_smart_follow_up_reminder(**kwargs):
    return microsoft_outlook_tools.outlook_smart_follow_up_reminder(**kwargs)

def microsoft_outlook_get_attachments(**kwargs):
    return microsoft_outlook_tools.outlook_get_attachments(**kwargs)

def microsoft_outlook_download_attachment(**kwargs):
    return microsoft_outlook_tools.outlook_download_attachment(**kwargs)

def microsoft_outlook_create_inbox_rule(**kwargs):
    return microsoft_outlook_tools.outlook_create_inbox_rule(**kwargs)

def microsoft_outlook_list_inbox_rules(**kwargs):
    return microsoft_outlook_tools.outlook_list_inbox_rules(**kwargs)

def microsoft_outlook_send_email(**kwargs):
    return microsoft_outlook_tools.outlook_send_email(**kwargs)
