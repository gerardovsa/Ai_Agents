"""
Microsoft Calendar Tools
Provides calendar management, event scheduling, and meeting coordination via Microsoft Graph API
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

class MicrosoftCalendarTools:
    """Microsoft Calendar (Outlook Calendar) tools"""
    
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
            else:
                return {'success': False, 'error': f'Unsupported HTTP method: {method}'}
            
            response.raise_for_status()
            
            if response.status_code == 204:
                return {'success': True}
            
            return {'success': True, 'data': response.json()}
            
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
    
    def _parse_datetime(self, dt_string: str, timezone: str = 'UTC') -> Dict:
        """Parse datetime string into Graph API format"""
        return {
            'dateTime': dt_string,
            'timeZone': timezone
        }
    
    def calendar_list_events(self, user_id: str, start_date: str = None, end_date: str = None,
                            max_results: int = 50, **kwargs) -> Dict:
        """List calendar events within date range"""
        
        params = {'$top': min(max_results, 100)}
        
        if start_date and end_date:
            params['$filter'] = f"start/dateTime ge '{start_date}' and end/dateTime le '{end_date}'"
        
        result = self._make_request('GET', '/me/calendar/events', params=params, **kwargs)
        
        if result['success']:
            events = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(events),
                'events': [{
                    'id': e.get('id'),
                    'subject': e.get('subject'),
                    'start': e.get('start'),
                    'end': e.get('end'),
                    'location': e.get('location', {}).get('displayName'),
                    'organizer': e.get('organizer', {}).get('emailAddress', {}).get('name'),
                    'attendees_count': len(e.get('attendees', [])),
                    'is_online_meeting': e.get('isOnlineMeeting', False),
                    'web_link': e.get('webLink')
                } for e in events]
            }
        return result
    
    def calendar_create_event(self, user_id: str, subject: str, start_time: str,
                             end_time: str, timezone: str = 'UTC', location: str = None,
                             body: str = None, attendees: List[str] = None,
                             is_online_meeting: bool = False, **kwargs) -> Dict:
        """Create a new calendar event"""
        
        event_data = {
            'subject': subject,
            'start': self._parse_datetime(start_time, timezone),
            'end': self._parse_datetime(end_time, timezone),
            'isOnlineMeeting': is_online_meeting
        }
        
        if location:
            event_data['location'] = {'displayName': location}
        
        if body:
            event_data['body'] = {
                'contentType': 'HTML',
                'content': body
            }
        
        if attendees:
            event_data['attendees'] = [{
                'emailAddress': {'address': email},
                'type': 'required'
            } for email in attendees]
        
        result = self._make_request('POST', '/me/calendar/events', event_data, **kwargs)
        
        if result['success']:
            event = result['data']
            response = {
                'success': True,
                'message': f'Event "{subject}" created successfully',
                'event_id': event.get('id'),
                'web_link': event.get('webLink')
            }
            
            if is_online_meeting:
                response['meeting_link'] = event.get('onlineMeeting', {}).get('joinUrl')
            
            return response
        return result
    
    def calendar_get_event(self, user_id: str, event_id: str, **kwargs) -> Dict:
        """Get details of a specific event"""
        result = self._make_request('GET', f'/me/calendar/events/{event_id}', **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'event': result['data']
            }
        return result
    
    def calendar_update_event(self, user_id: str, event_id: str, updates: Dict, **kwargs) -> Dict:
        """Update an existing event"""
        
        # Parse datetime fields if present
        if 'start_time' in updates:
            updates['start'] = self._parse_datetime(updates.pop('start_time'), 
                                                   updates.pop('timezone', 'UTC'))
        if 'end_time' in updates:
            updates['end'] = self._parse_datetime(updates.pop('end_time'), 
                                                 updates.pop('timezone', 'UTC'))
        
        result = self._make_request('PATCH', f'/me/calendar/events/{event_id}', updates, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Event updated successfully',
                'event': result.get('data', {})
            }
        return result
    
    def calendar_delete_event(self, user_id: str, event_id: str, **kwargs) -> Dict:
        """Delete a calendar event"""
        result = self._make_request('DELETE', f'/me/calendar/events/{event_id}', **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Event deleted successfully'
            }
        return result
    
    def calendar_create_recurring_event(self, user_id: str, subject: str, start_time: str,
                                       end_time: str, recurrence_pattern: Dict,
                                       timezone: str = 'UTC', location: str = None,
                                       attendees: List[str] = None, **kwargs) -> Dict:
        """Create a recurring calendar event"""
        
        event_data = {
            'subject': subject,
            'start': self._parse_datetime(start_time, timezone),
            'end': self._parse_datetime(end_time, timezone),
            'recurrence': recurrence_pattern
        }
        
        if location:
            event_data['location'] = {'displayName': location}
        
        if attendees:
            event_data['attendees'] = [{
                'emailAddress': {'address': email},
                'type': 'required'
            } for email in attendees]
        
        result = self._make_request('POST', '/me/calendar/events', event_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Recurring event "{subject}" created successfully',
                'event_id': result['data'].get('id')
            }
        return result
    
    def calendar_respond_to_event(self, user_id: str, event_id: str, 
                                  response: str, comment: str = None, **kwargs) -> Dict:
        """Respond to meeting invitation (accept/tentative/decline)"""
        
        if response not in ['accept', 'tentativelyAccept', 'decline']:
            return {'success': False, 'error': 'Invalid response type'}
        
        response_data = {}
        if comment:
            response_data['comment'] = comment
        
        result = self._make_request('POST', f'/me/calendar/events/{event_id}/{response}', response_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Event {response}ed successfully'
            }
        return result
    
    def calendar_get_availability(self, user_id: str, attendees: List[str], 
                                  start_time: str, end_time: str,
                                  timezone: str = 'UTC', interval_minutes: int = 30, **kwargs) -> Dict:
        """Get free/busy schedule for attendees"""
        
        schedule_data = {
            'schedules': attendees,
            'startTime': self._parse_datetime(start_time, timezone),
            'endTime': self._parse_datetime(end_time, timezone),
            'availabilityViewInterval': interval_minutes
        }
        
        result = self._make_request('POST', '/me/calendar/getSchedule', schedule_data, **kwargs)
        
        if result['success']:
            schedules = result['data'].get('value', [])
            return {
                'success': True,
                'schedules': [{
                    'attendee': s.get('scheduleId'),
                    'availability': s.get('availabilityView'),
                    'working_hours': s.get('workingHours')
                } for s in schedules]
            }
        return result
    
    def calendar_find_meeting_rooms(self, user_id: str, location: str = None, **kwargs) -> Dict:
        """Find available meeting rooms"""
        
        # List room lists
        result = self._make_request('GET', '/me/findRoomLists', **kwargs)
        
        if result['success']:
            room_lists = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(room_lists),
                'room_lists': [{
                    'name': r.get('name'),
                    'address': r.get('address')
                } for r in room_lists]
            }
        return result
    
    def calendar_book_room(self, user_id: str, room_email: str, event_id: str, **kwargs) -> Dict:
        """Add a meeting room to an event"""
        
        # Get current event
        event_result = self.calendar_get_event(user_id, event_id)
        if not event_result['success']:
            return event_result
        
        event = event_result['event']
        
        # Add room to locations
        locations = event.get('locations', [])
        locations.append({
            'displayName': room_email,
            'locationType': 'conferenceRoom',
            'uniqueId': room_email,
            'uniqueIdType': 'directory'
        })
        
        # Update event
        update_result = self.calendar_update_event(user_id, event_id, {'locations': locations})
        
        if update_result['success']:
            return {
                'success': True,
                'message': f'Room {room_email} booked successfully'
            }
        return update_result
    
    def calendar_list_calendars(self, user_id: str, **kwargs) -> Dict:
        """List all calendars"""
        result = self._make_request('GET', '/me/calendars', **kwargs)
        
        if result['success']:
            calendars = result['data'].get('value', [])
            return {
                'success': True,
                'count': len(calendars),
                'calendars': [{
                    'id': c.get('id'),
                    'name': c.get('name'),
                    'color': c.get('color'),
                    'can_edit': c.get('canEdit'),
                    'is_default': c.get('isDefaultCalendar', False)
                } for c in calendars]
            }
        return result
    
    def calendar_create_calendar(self, user_id: str, name: str, color: str = None, **kwargs) -> Dict:
        """Create a new calendar"""
        
        calendar_data = {'name': name}
        if color:
            calendar_data['color'] = color
        
        result = self._make_request('POST', '/me/calendars', calendar_data, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': f'Calendar "{name}" created successfully',
                'calendar': result['data']
            }
        return result
    
    def calendar_smart_find_meeting_time(self, user_id: str, attendees: List[str],
                                        duration_minutes: int, start_date: str,
                                        end_date: str, timezone: str = 'UTC', **kwargs) -> Dict:
        """AI-powered meeting time finder across attendees"""
        
        meeting_data = {
            'attendees': [
                {'emailAddress': {'address': email}, 'type': 'required'}
                for email in attendees
            ],
            'timeConstraint': {
                'activityDomain': 'work',
                'timeslots': [{
                    'start': self._parse_datetime(start_date, timezone),
                    'end': self._parse_datetime(end_date, timezone)
                }]
            },
            'meetingDuration': f'PT{duration_minutes}M',
            'returnSuggestionReasons': True,
            'minimumAttendeePercentage': 100
        }
        
        result = self._make_request('POST', '/me/findMeetingTimes', meeting_data, **kwargs)
        
        if result['success']:
            suggestions = result['data'].get('meetingTimeSuggestions', [])
            return {
                'success': True,
                'count': len(suggestions),
                'suggestions': [{
                    'confidence': s.get('confidence'),
                    'start': s.get('meetingTimeSlot', {}).get('start'),
                    'end': s.get('meetingTimeSlot', {}).get('end'),
                    'location': s.get('locations', []),
                    'attendee_availability': s.get('attendeeAvailability', [])
                } for s in suggestions]
            }
        return result
    
    def calendar_smart_schedule_series(self, user_id: str, events: List[Dict],
                                      check_conflicts: bool = True, **kwargs) -> Dict:
        """Bulk create events with conflict detection"""
        
        results = {
            'success': True,
            'created': [],
            'conflicts': [],
            'failed': []
        }
        
        for event_data in events:
            subject = event_data['subject']
            start_time = event_data['start_time']
            end_time = event_data['end_time']
            
            # Check for conflicts if enabled
            if check_conflicts:
                conflict_check = self.calendar_list_events(
                    user_id,
                    start_date=start_time,
                    end_date=end_time
                )
                
                if conflict_check['success'] and conflict_check['count'] > 0:
                    results['conflicts'].append({
                        'event': subject,
                        'start': start_time,
                        'conflicts_with': [e['subject'] for e in conflict_check['events']]
                    })
                    continue
            
            # Create event
            create_result = self.calendar_create_event(
                user_id,
                subject,
                start_time,
                end_time,
                timezone=event_data.get('timezone', 'UTC'),
                location=event_data.get('location'),
                body=event_data.get('body'),
                attendees=event_data.get('attendees'),
                is_online_meeting=event_data.get('is_online_meeting', False)
            )
            
            if create_result['success']:
                results['created'].append(subject)
            else:
                results['failed'].append({
                    'event': subject,
                    'error': create_result.get('error')
                })
        
        results['message'] = f"Created {len(results['created'])} events, {len(results['conflicts'])} conflicts, {len(results['failed'])} failed"
        results['success'] = len(results['failed']) == 0
        
        return results
    
    def calendar_smart_conflict_resolver(self, user_id: str, start_date: str, 
                                        end_date: str, auto_resolve: bool = False, **kwargs) -> Dict:
        """Detect and resolve calendar conflicts"""
        
        # Get all events in range
        events_result = self.calendar_list_events(user_id, start_date, end_date)
        
        if not events_result['success']:
            return events_result
        
        events = events_result['events']
        
        # Find overlaps
        conflicts = []
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                start1 = datetime.fromisoformat(event1['start']['dateTime'].replace('Z', '+00:00'))
                end1 = datetime.fromisoformat(event1['end']['dateTime'].replace('Z', '+00:00'))
                start2 = datetime.fromisoformat(event2['start']['dateTime'].replace('Z', '+00:00'))
                end2 = datetime.fromisoformat(event2['end']['dateTime'].replace('Z', '+00:00'))
                
                # Check overlap
                if start1 < end2 and start2 < end1:
                    conflicts.append({
                        'event1': {'id': event1['id'], 'subject': event1['subject'], 'start': event1['start']},
                        'event2': {'id': event2['id'], 'subject': event2['subject'], 'start': event2['start']},
                        'overlap_minutes': int((min(end1, end2) - max(start1, start2)).total_seconds() / 60)
                    })
        
        results = {
            'success': True,
            'conflicts_found': len(conflicts),
            'conflicts': conflicts,
            'resolved': []
        }
        
        # Auto-resolve if requested
        if auto_resolve and conflicts:
            results['message'] = 'Auto-resolve not yet implemented - manual resolution required'
        else:
            results['message'] = f'Found {len(conflicts)} conflicts'
        
        return results
    
    def calendar_get_reminders(self, user_id: str, **kwargs) -> Dict:
        """Get upcoming event reminders"""
        
        # Get events in next 7 days
        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        result = self.calendar_list_events(user_id, start_date, end_date)
        
        if result['success']:
            events = result['data'].get('events', [])
            return {
                'success': True,
                'count': len(events),
                'reminders': events
            }
        return result
    
    def calendar_set_working_hours(self, user_id: str, timezone: str,
                                   work_days: List[str], start_time: str, end_time: str, **kwargs) -> Dict:
        """Set user's working hours"""
        
        mailbox_settings = {
            'workingHours': {
                'daysOfWeek': work_days,
                'startTime': start_time,
                'endTime': end_time,
                'timeZone': {
                    'name': timezone
                }
            }
        }
        
        result = self._make_request('PATCH', '/me/mailboxSettings', mailbox_settings, **kwargs)
        
        if result['success']:
            return {
                'success': True,
                'message': 'Working hours updated successfully',
                'working_hours': mailbox_settings['workingHours']
            }
        return result


# Create global instance
microsoft_calendar_tools = MicrosoftCalendarTools()
