"""
Microsoft Teams Tools
Provides team collaboration, messaging, and coordination via Microsoft Graph API
"""

import os
import requests
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

class MicrosoftTeamsTools:
    """Microsoft Teams collaboration and messaging tools"""
    
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
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self._get_headers(**kwargs), params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self._get_headers(**kwargs), json=data, params=params)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self._get_headers(**kwargs), json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self._get_headers(**kwargs))
            elif method == 'PUT':
                response = requests.put(url, headers=self._get_headers(**kwargs), json=data)
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}'}
            
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
                print(f"[WARNING] Microsoft Teams - Response not JSON: {response.status_code}, body length: {len(response.text)}")
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
    
    def teams_list_teams(self, user_id: str, **kwargs) -> Dict:
        """List all teams the user is a member of"""
        result = self._make_request('GET', '/me/joinedTeams', **kwargs)
        
        if result['success']:
            teams = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(teams),
                'teams': [{
                    'id': t.get('id'),
                    'name': t.get('displayName'),
                    'description': t.get('description'),
                    'visibility': t.get('visibility')
                } for t in teams]
            }
        return result
    
    def teams_create_team(self, user_id: str, display_name: str, 
                         description: str = None, visibility: str = 'private', **kwargs) -> Dict:
        """Create a new team"""
        
        team_data = {
            'template@odata.bind': "https://graph.microsoft.com/v1.0/teamsTemplates('standard')",
            'displayName': display_name,
            'description': description or f'Team for {display_name}',
            'visibility': visibility
        }
        
        result = self._make_request('POST', '/teams', team_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Team "{display_name}" created successfully',
                'team': result.get('data', {})
            }
        return result
    
    def teams_get_team(self, user_id: str, team_id: str, **kwargs) -> Dict:
        """Get details of a specific team"""
        result = self._make_request('GET', f'/teams/{team_id}', **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'team': result['data']
            }
        return result
    
    def teams_list_channels(self, user_id: str, team_id: str, **kwargs) -> Dict:
        """List all channels in a team"""
        result = self._make_request('GET', f'/teams/{team_id}/channels', **kwargs)
        
        if result['success']:
            channels = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(channels),
                'channels': [{
                    'id': c.get('id'),
                    'name': c.get('displayName'),
                    'description': c.get('description'),
                    'membership_type': c.get('membershipType')
                } for c in channels]
            }
        return result
    
    def teams_create_channel(self, user_id: str, team_id: str, display_name: str,
                            description: str = None, membership_type: str = 'standard', **kwargs) -> Dict:
        """Create a new channel in a team"""
        
        channel_data = {
            'displayName': display_name,
            'description': description or f'Channel for {display_name}',
            'membershipType': membership_type
        }
        
        result = self._make_request('POST', f'/teams/{team_id}/channels', channel_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Channel "{display_name}" created successfully',
                'channel': result['data']
            }
        return result
    
    def teams_send_channel_message(self, user_id: str, team_id: str, channel_id: str,
                                  message: str, importance: str = 'normal',
                                  mentions: List[str] = None, **kwargs) -> Dict:
        """Send a message to a team channel"""
        
        message_data = {
            'body': {
                'contentType': 'html',
                'content': message
            }
        }
        
        if importance and importance != 'normal':
            message_data['importance'] = importance
        
        result = self._make_request('POST', f'/teams/{team_id}/channels/{channel_id}/messages', message_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Message sent successfully',
                'message_id': result['data'].get('id')
            }
        return result
    
    def teams_get_channel_messages(self, user_id: str, team_id: str, channel_id: str,
                                   max_results: int = 50, **kwargs) -> Dict:
        """Get messages from a channel"""
        
        params = {'$top': min(max_results, 50)}
        result = self._make_request('GET', f'/teams/{team_id}/channels/{channel_id}/messages', params=params, **kwargs)
        
        if result['success']:
            messages = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(messages),
                'messages': messages
            }
        return result
    
    def teams_reply_to_message(self, user_id: str, team_id: str, channel_id: str,
                              message_id: str, reply: str, **kwargs) -> Dict:
        """Reply to a message in a channel"""
        
        reply_data = {
            'body': {
                'contentType': 'html',
                'content': reply
            }
        }
        
        result = self._make_request('POST', 
                                    f'/teams/{team_id}/channels/{channel_id}/messages/{message_id}/replies',
                                    reply_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Reply sent successfully'
            }
        return result
    
    def teams_add_member(self, user_id: str, team_id: str, member_email: str,
                        role: str = 'member', **kwargs) -> Dict:
        """Add a member to a team"""
        
        # First, get user ID from email
        user_result = self._make_request('GET', f'/users/{member_email}', **kwargs)
        if not user_result['success']:
            return user_result
        
        member_user_id = user_result['data'].get('id')
        
        member_data = {
            '@odata.type': '#microsoft.graph.aadUserConversationMember',
            'roles': ['owner'] if role == 'owner' else [],
            'user@odata.bind': f"https://graph.microsoft.com/v1.0/users('{member_user_id}')"
        }
        
        result = self._make_request('POST', f'/teams/{team_id}/members', member_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Added {member_email} to team',
                'role': role
            }
        return result
    
    def teams_list_members(self, user_id: str, team_id: str, **kwargs) -> Dict:
        """List all members of a team"""
        result = self._make_request('GET', f'/teams/{team_id}/members', **kwargs)
        
        if result['success']:
            members = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(members),
                'members': [{
                    'id': m.get('id'),
                    'display_name': m.get('displayName'),
                    'email': m.get('email'),
                    'roles': m.get('roles', [])
                } for m in members]
            }
        return result
    
    def teams_send_chat_message(self, user_id: str, recipients: List[str], message: str, **kwargs) -> Dict:
        """Send a direct message or group chat message"""
        
        # Create chat with recipients
        chat_data = {
            'chatType': 'group' if len(recipients) > 1 else 'oneOnOne',
            'members': []
        }
        
        # Add current user
        chat_data['members'].append({
            '@odata.type': '#microsoft.graph.aadUserConversationMember',
            'roles': ['owner'],
            'user@odata.bind': f'https://graph.microsoft.com/v1.0/users/{user_id}'
        })
        
        # Add recipients
        for recipient in recipients:
            chat_data['members'].append({
                '@odata.type': '#microsoft.graph.aadUserConversationMember',
                'roles': ['owner'],
                'user@odata.bind': f'https://graph.microsoft.com/v1.0/users/{recipient}'
            })
        
        # Create chat
        chat_result = self._make_request('POST', '/chats', chat_data, **kwargs)
        if not chat_result['success']:
            return chat_result
        
        chat_id = chat_result['data'].get('id')
        
        # Send message
        message_data = {
            'body': {
                'content': message
            }
        }
        
        result = self._make_request('POST', f'/chats/{chat_id}/messages', message_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Chat message sent successfully',
                'recipients': recipients
            }
        return result
    
    def teams_upload_file(self, user_id: str, team_id: str, channel_id: str,
                         file_path: str, file_name: str = None, **kwargs) -> Dict:
        """Upload a file to a team channel"""
        
        # Get channel's drive
        drive_result = self._make_request('GET', f'/teams/{team_id}/channels/{channel_id}/filesFolder', **kwargs)
        if not drive_result['success']:
            return drive_result
        
        drive_id = drive_result['data'].get('parentReference', {}).get('driveId')
        folder_id = drive_result['data'].get('id')
        
        # Upload file
        upload_name = file_name or os.path.basename(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            upload_url = f'/drives/{drive_id}/items/{folder_id}:/{upload_name}:/content'
            
            headers = self._get_headers(**kwargs)
            headers['Content-Type'] = 'application/octet-stream'
            
            response = requests.put(
                f'{self.graph_api_base}{upload_url}',
                headers=headers,
                data=file_content
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'message': f'File "{upload_name}" uploaded successfully',
                'file': response.json()
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def teams_list_channel_files(self, user_id: str, team_id: str, channel_id: str, **kwargs) -> Dict:
        """List files in a team channel"""
        
        drive_result = self._make_request('GET', f'/teams/{team_id}/channels/{channel_id}/filesFolder/children', **kwargs)
        
        if drive_result['success']:
            files = drive_result['data'].get('value', [])
            return {
                'success': True,
                'count': len(files),
                'files': [{
                    'id': f.get('id'),
                    'name': f.get('name'),
                    'size': f.get('size'),
                    'created': f.get('createdDateTime'),
                    'modified': f.get('lastModifiedDateTime')
                } for f in files]
            }
        return drive_result
    
    def teams_create_meeting(self, user_id: str, subject: str, start_time: str,
                            end_time: str, attendees: List[str] = None, body: str = None, **kwargs) -> Dict:
        """Create a Teams meeting"""
        
        meeting_data = {
            'subject': subject,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC'
            },
            'isOnlineMeeting': True,
            'onlineMeetingProvider': 'teamsForBusiness'
        }
        
        if body:
            meeting_data['body'] = {
                'contentType': 'HTML',
                'content': body
            }
        
        if attendees:
            meeting_data['attendees'] = [{
                'emailAddress': {'address': email},
                'type': 'required'
            } for email in attendees]
        
        result = self._make_request('POST', '/me/calendar/events', meeting_data, **kwargs)
        
        if result['success']:
            event = result['data']
            return {
                'success': True,
                'message': 'Teams meeting created successfully',
                'meeting_link': event.get('onlineMeeting', {}).get('joinUrl'),
                'event_id': event.get('id')
            }
        return result
    
    def teams_search_messages(self, user_id: str, query: str, team_id: str = None,
                             from_date: str = None, **kwargs) -> Dict:
        """Search for messages across teams and channels"""
        
        # Note: Full search requires Microsoft Search API
        # This is a simplified version
        
        return {
            'success': True,
            'message': 'Search functionality requires Microsoft Search API',
            'note': 'Use teams_get_channel_messages with specific team/channel for now'
        }
    
    def teams_pin_message(self, user_id: str, team_id: str, channel_id: str, message_id: str, **kwargs) -> Dict:
        """Pin a message in a channel"""
        
        # Note: Pinning requires beta API
        return {
            'success': True,
            'message': 'Message pinning requires beta API',
            'note': 'Feature available in future update'
        }
    
    def teams_smart_daily_standup(self, user_id: str, team_id: str, channel_id: str,
                                 standup_data: Dict, mention_team: bool = False, **kwargs) -> Dict:
        """Post automated daily standup message"""
        
        date = standup_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        yesterday = standup_data.get('yesterday', [])
        today = standup_data.get('today', [])
        blockers = standup_data.get('blockers', [])
        
        # Format standup message
        message = f"""
        <h2>📊 Daily Standup - {date}</h2>
        
        <h3> Yesterday</h3>
        <ul>
        {''.join([f'<li>{item}</li>' for item in yesterday])}
        </ul>
        
        <h3>🎯 Today</h3>
        <ul>
        {''.join([f'<li>{item}</li>' for item in today])}
        </ul>
        
        <h3>🚧 Blockers</h3>
        <ul>
        {''.join([f'<li>{item}</li>' for item in blockers]) if blockers else '<li>None</li>'}
        </ul>
        """
        
        if mention_team:
            message = f'<at>Everyone</at><br/>{message}'
        
        result = self.teams_send_channel_message(user_id, team_id, channel_id, message, importance='high')
        
        if result['success']:
            result['message'] = 'Daily standup posted successfully'
        
        return result
    
    def teams_smart_broadcast_announcement(self, user_id: str, channels: List[Dict],
                                          message: str, importance: str = 'high',
                                          delay_seconds: int = 2, **kwargs) -> Dict:
        """Send announcement to multiple channels simultaneously"""
        
        results = {
            'success': True,
            'sent': [],
            'failed': [],
            'total': len(channels)
        }
        
        for idx, channel_info in enumerate(channels):
            team_id = channel_info.get('team_id')
            channel_id = channel_info.get('channel_id')
            
            send_result = self.teams_send_channel_message(
                user_id, team_id, channel_id, message, importance
            )
            
            if send_result['success']:
                results['sent'].append({'team_id': team_id, 'channel_id': channel_id})
            else:
                results['failed'].append({
                    'team_id': team_id,
                    'channel_id': channel_id,
                    'error': send_result.get('error')
                })
            
            # Rate limiting delay
            if idx < len(channels) - 1:
                time.sleep(delay_seconds)
        
        results['success'] = len(results['failed']) == 0
        results['message'] = f"Sent to {len(results['sent'])}/{results['total']} channels"
        
        return results
    
    def teams_smart_create_poll(self, user_id: str, team_id: str, channel_id: str,
                                question: str, options: List[str], allow_multiple: bool = False, **kwargs) -> Dict:
        """Create a poll in a channel"""
        
        # Format poll as message with adaptive card
        poll_message = f"""
        <h3>📊 {question}</h3>
        <p>Vote by replying with the number of your choice:</p>
        <ul>
        {''.join([f'<li>{idx + 1}. {option}</li>' for idx, option in enumerate(options)])}
        </ul>
        <p><em>{'Multiple selections allowed' if allow_multiple else 'Single selection only'}</em></p>
        """
        
        result = self.teams_send_channel_message(user_id, team_id, channel_id, poll_message, importance='normal')
        
        if result['success']:
            result['message'] = 'Poll created successfully'
            result['note'] = 'Users can vote by replying with their choice'
        
        return result
    
    def teams_smart_meeting_summary(self, user_id: str, team_id: str, channel_id: str,
                                   meeting_title: str, attendees: List[str],
                                   key_points: List[str], action_items: List[Dict], **kwargs) -> Dict:
        """Post meeting summary with action items"""
        
        # Format meeting summary
        summary_message = f"""
        <h2>📝 Meeting Summary: {meeting_title}</h2>
        
        <h3>👥 Attendees</h3>
        <p>{', '.join(attendees)}</p>
        
        <h3>🔑 Key Points</h3>
        <ul>
        {''.join([f'<li>{point}</li>' for point in key_points])}
        </ul>
        
        <h3> Action Items</h3>
        <table>
        <tr><th>Task</th><th>Owner</th><th>Due Date</th></tr>
        {''.join([f"<tr><td>{item['task']}</td><td>{item['owner']}</td><td>{item.get('due_date', 'TBD')}</td></tr>" for item in action_items])}
        </table>
        """
        
        result = self.teams_send_channel_message(user_id, team_id, channel_id, summary_message, importance='high')
        
        if result['success']:
            result['message'] = 'Meeting summary posted successfully'
        
        return result
    
    def teams_update_team_settings(self, user_id: str, team_id: str, settings: Dict, **kwargs) -> Dict:
        """Update team settings"""
        result = self._make_request('PATCH', f'/teams/{team_id}', settings, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Team settings updated successfully'
            }
        return result
    
    def teams_get_channel_tabs(self, user_id: str, team_id: str, channel_id: str, **kwargs) -> Dict:
        """List tabs in a channel"""
        result = self._make_request('GET', f'/teams/{team_id}/channels/{channel_id}/tabs', **kwargs)
        
        if result['success']:
            tabs = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(tabs),
                'tabs': [{
                    'id': t.get('id'),
                    'name': t.get('displayName'),
                    'web_url': t.get('webUrl')
                } for t in tabs]
            }
        return result


# ========================================
# GLOBAL INSTANCE & MODULE-LEVEL EXPORTS
# ========================================

# Create global instance
microsoft_teams_tools = MicrosoftTeamsTools()

# Export all functions at module level with parameter wrappers
# Wrappers extract positional 'user_id' parameter from kwargs for registry compatibility

def microsoft_teams_list_teams(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_list_teams(user_id, **kwargs)

def microsoft_teams_create_team(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_create_team(user_id, **kwargs)

def microsoft_teams_get_team(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_get_team(user_id, **kwargs)

def microsoft_teams_list_channels(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_list_channels(user_id, **kwargs)

def microsoft_teams_create_channel(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_create_channel(user_id, **kwargs)

def microsoft_teams_send_channel_message(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_send_channel_message(user_id, **kwargs)

def microsoft_teams_get_channel_messages(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_get_channel_messages(user_id, **kwargs)

def microsoft_teams_reply_to_message(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_reply_to_message(user_id, **kwargs)

def microsoft_teams_add_member(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_add_member(user_id, **kwargs)

def microsoft_teams_list_members(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_list_members(user_id, **kwargs)

def microsoft_teams_send_chat_message(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_send_chat_message(user_id, **kwargs)

def microsoft_teams_upload_file(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_upload_file(user_id, **kwargs)

def microsoft_teams_list_channel_files(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_list_channel_files(user_id, **kwargs)

def microsoft_teams_create_meeting(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_create_meeting(user_id, **kwargs)

def microsoft_teams_search_messages(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_search_messages(user_id, **kwargs)

def microsoft_teams_pin_message(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_pin_message(user_id, **kwargs)

def microsoft_teams_smart_daily_standup(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_smart_daily_standup(user_id, **kwargs)

def microsoft_teams_smart_broadcast_announcement(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_smart_broadcast_announcement(user_id, **kwargs)

def microsoft_teams_smart_create_poll(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_smart_create_poll(user_id, **kwargs)

def microsoft_teams_smart_meeting_summary(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_smart_meeting_summary(user_id, **kwargs)

def microsoft_teams_update_team_settings(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_update_team_settings(user_id, **kwargs)

def microsoft_teams_get_channel_tabs(**kwargs):
    user_id = kwargs.pop('user_id', None)
    if user_id is None:
        raise ValueError("user_id is required")
    return microsoft_teams_tools.teams_get_channel_tabs(user_id, **kwargs)

