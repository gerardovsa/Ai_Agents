"""
Google Calendar API Implementation
Handles calendar events, scheduling, and reminders

Authentication: Uses OAuth 2.0 for personal Calendar access
Mode: Supports 'desktop' (local testing) and 'web' (production deployment)
"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

try:
    # Import OAuth manager for personal Calendar access
    from google_workspace.oauth_manager import build_calendar_oauth_service
    HAS_CALENDAR_API = True
except ImportError:
    HAS_CALENDAR_API = False
    print("⚠️ Google Calendar API dependencies not available")

def _get_service(user_email=None):
    """
    Get authenticated Google Calendar API service using OAuth 2.0
    
    Args:
        user_email: Optional user email for multi-user deployments
    
    Returns:
        Authenticated Calendar service
    """
    if not HAS_CALENDAR_API:
        raise Exception("Google Calendar API not available - install google-api-python-client")
    # Use OAuth authentication (personal Calendar access)
    return build_calendar_oauth_service(user_email=user_email)

class GoogleCalendarTools:
    def __init__(self, credentials_path=None, token_path=None, user_email=None):
        """
        Initialize Google Calendar API client
        
        Args:
            credentials_path: Deprecated (OAuth manager handles this)
            token_path: Deprecated (OAuth manager handles this)
            user_email: Optional user email for multi-user deployments
        """
        self.user_email = user_email
        
    def _get_service(self):
        """Get or create Calendar API service using OAuth"""
        return _get_service(user_email=self.user_email)
    
    def list_calendars(self, show_hidden=False):
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
    
    def delete_event(self, calendar_id='primary', event_id=None, send_notifications=True):
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
    
    def check_availability(self, time_min, time_max, calendar_ids, timezone='UTC'):
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
def google_calendar_list_calendars(**kwargs):
    tools = GoogleCalendarTools()
    return tools.list_calendars(**kwargs)

def google_calendar_create_event(**kwargs):
    tools = GoogleCalendarTools()
    return tools.create_event(**kwargs)

def google_calendar_update_event(**kwargs):
    tools = GoogleCalendarTools()
    return tools.update_event(**kwargs)

def google_calendar_delete_event(**kwargs):
    tools = GoogleCalendarTools()
    return tools.delete_event(**kwargs)

def google_calendar_list_events(**kwargs):
    tools = GoogleCalendarTools()
    return tools.list_events(**kwargs)

def google_calendar_check_availability(**kwargs):
    tools = GoogleCalendarTools()
    return tools.check_availability(**kwargs)
