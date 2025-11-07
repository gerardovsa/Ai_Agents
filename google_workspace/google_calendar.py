"""
Google Calendar API Implementation
Handles calendar events, scheduling, and reminders

Authentication: Uses database OAuth ONLY (oauth_tokens table)
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

HAS_CALENDAR_API = True

def _get_service(user_email=None, _user_id=None, _injected_credentials=None):
    """
    Get authenticated Google Calendar API service using DATABASE OAuth
    
    Args:
        user_email: (Deprecated) Not used
        _user_id: User ID for database OAuth lookup (REQUIRED)
        _injected_credentials: Flag for credential injection (REQUIRED)
    
    Returns:
        Authenticated Calendar service
        
    Raises:
        Exception: If database OAuth credentials not available
    """
    if _user_id and _injected_credentials:
        from AI_infrastructure.auth.credential_injector import create_google_service_with_user_credentials
        return create_google_service_with_user_credentials(
            user_id=_user_id,
            service_name='calendar',
            version='v3'
        )
    
    # No credentials provided - throw clear error
    raise Exception(
        "❌ Google Calendar requires database OAuth!\n\n"
        "File-based OAuth is no longer supported.\n"
        "All credentials must be in: data/ai_infrastructure.db (oauth_tokens table)\n\n"
        "To authenticate:\n"
        "1. Visit: http://localhost:5001/auth/google/login\n"
        "2. Sign in and grant permissions\n"
        "3. Credentials will be saved to database\n\n"
        f"Received: _user_id={_user_id}, _injected_credentials={_injected_credentials}\n"
    )

class GoogleCalendarTools:
    def __init__(self, credentials_path=None, token_path=None, user_email=None,
                 _user_id=None, _injected_credentials=None):
        """
        Initialize Google Calendar API client with DATABASE OAuth
        
        Args:
            credentials_path: (Deprecated) Not used
            token_path: (Deprecated) Not used
            user_email: (Deprecated) Not used
            _user_id: User ID for database OAuth credential lookup (REQUIRED)
            _injected_credentials: Flag to use database OAuth credentials (REQUIRED)
        """
        self.user_email = user_email
        self._user_id = _user_id
        self._injected_credentials = _injected_credentials
        
    def _get_service(self, **kwargs):
        """Get Calendar API service using DATABASE OAuth credentials ONLY"""
        if not self._user_id or not self._injected_credentials:
            raise Exception(
                "❌ Google Calendar OAuth credentials required!\n"
                "File-based OAuth (credentials_desktop.json) is no longer supported.\n"
                "To authenticate, visit: http://localhost:5001/auth/google/login"
            )
        
        from pathlib import Path
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from AI_infrastructure.auth.credential_injector import create_google_service_with_user_credentials
        
        return create_google_service_with_user_credentials(
            user_id=self._user_id,
            service_name='calendar',
            version='v3'
        )
    
    def list_calendars(self, show_hidden=False, **kwargs):
        """List all calendars"""
        service = self._get_service()
        calendars = service.calendarList().list(
            showHidden=show_hidden
        ).execute()
        return calendars.get('items', [])
    
    def create_event(self, calendar_id='primary', **kwargs):
        """Create calendar event"""
        service = self._get_service()
        
        event = {
            'summary': kwargs.get('summary'),
            'description': kwargs.get('description'),
            'start': {
                'dateTime': kwargs.get('start_datetime'),
                'timeZone': kwargs.get('timezone', 'UTC')
            },
            'end': {
                'dateTime': kwargs.get('end_datetime'),
                'timeZone': kwargs.get('timezone', 'UTC')
            }
        }
        
        if kwargs.get('location'):
            event['location'] = kwargs['location']
        
        if kwargs.get('attendees'):
            event['attendees'] = [{'email': email} for email in kwargs['attendees']]
        
        if kwargs.get('reminders'):
            event['reminders'] = kwargs['reminders']
        
        return service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendNotifications=kwargs.get('send_notifications', True)
        ).execute()
    
    def update_event(self, calendar_id='primary', event_id=None, **kwargs):
        """Update calendar event"""
        service = self._get_service()
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        
        # Update fields that are provided
        if kwargs.get('summary'):
            event['summary'] = kwargs['summary']
        if kwargs.get('description'):
            event['description'] = kwargs['description']
        if kwargs.get('start_datetime'):
            event['start']['dateTime'] = kwargs['start_datetime']
        if kwargs.get('end_datetime'):
            event['end']['dateTime'] = kwargs['end_datetime']
        
        return service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event,
            sendNotifications=kwargs.get('send_notifications', True)
        ).execute()
    
    def delete_event(self, calendar_id='primary', event_id=None, send_notifications=True, **kwargs):
        """Delete calendar event"""
        service = self._get_service()
        return service.events().delete(
            calendarId=calendar_id,
            eventId=event_id,
            sendNotifications=send_notifications
        ).execute()
    
    def list_events(self, calendar_id='primary', **kwargs):
        """List events with filters"""
        service = self._get_service()
        return service.events().list(
            calendarId=calendar_id,
            timeMin=kwargs.get('time_min'),
            timeMax=kwargs.get('time_max'),
            maxResults=kwargs.get('max_results', 250),
            singleEvents=kwargs.get('single_events', True),
            orderBy=kwargs.get('order_by', 'startTime'),
            q=kwargs.get('search_query')
        ).execute()
    
    def check_availability(self, time_min, time_max, calendar_ids, timezone='UTC', **kwargs):
        """Check free/busy information"""
        service = self._get_service()
        body = {
            'timeMin': time_min,
            'timeMax': time_max,
            'timeZone': timezone,
            'items': [{'id': cal_id} for cal_id in calendar_ids]
        }
        return service.freebusy().query(body=body).execute()

# Export tool functions
def google_calendar_list_calendars(_user_id=None, _injected_credentials=None, **kwargs):
    tools = GoogleCalendarTools(_user_id=_user_id, _injected_credentials=_injected_credentials)
    return tools.list_calendars(**kwargs)

def google_calendar_create_event(_user_id=None, _injected_credentials=None, **kwargs):
    tools = GoogleCalendarTools(_user_id=_user_id, _injected_credentials=_injected_credentials)
    return tools.create_event(**kwargs)

def google_calendar_update_event(_user_id=None, _injected_credentials=None, **kwargs):
    tools = GoogleCalendarTools(_user_id=_user_id, _injected_credentials=_injected_credentials)
    return tools.update_event(**kwargs)

def google_calendar_delete_event(_user_id=None, _injected_credentials=None, **kwargs):
    tools = GoogleCalendarTools(_user_id=_user_id, _injected_credentials=_injected_credentials)
    return tools.delete_event(**kwargs)

def google_calendar_list_events(_user_id=None, _injected_credentials=None, **kwargs):
    tools = GoogleCalendarTools(_user_id=_user_id, _injected_credentials=_injected_credentials)
    return tools.list_events(**kwargs)

def google_calendar_check_availability(_user_id=None, _injected_credentials=None, **kwargs):
    tools = GoogleCalendarTools(_user_id=_user_id, _injected_credentials=_injected_credentials)
    return tools.check_availability(**kwargs)
