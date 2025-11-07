"""
Script to add _user_id and _injected_credentials parameters to all Google Meet functions
and update service builders to support database OAuth
"""

import re

# Read the file
with open(r'C:\Users\gpoli\GIT\AI_agents\google_workspace\google_meet.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Step 1: Update _get_calendar_service to support user OAuth
old_calendar_service = '''def _get_calendar_service():
    """
    Build Google Calendar service for meeting creation.
    Most Meet functionality is via Calendar API.
    
    Returns:
        Google Calendar service object
    """
    scopes = ['https://www.googleapis.com/auth/calendar']
    
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=scopes
    )
    
    return build('calendar', 'v3', credentials=credentials)'''

new_calendar_service = '''def _get_calendar_service(_user_id=None, _injected_credentials=None):
    """
    Build Google Calendar service for meeting creation.
    Most Meet functionality is via Calendar API.
    Supports database OAuth (priority) and service account (fallback).
    
    Args:
        _user_id: User ID for database OAuth credential lookup
        _injected_credentials: Flag to use database OAuth credentials
    
    Returns:
        Google Calendar service object
    """
    # Priority: Database OAuth (if user_id provided)
    if _user_id and _injected_credentials:
        try:
            from AI_infrastructure.auth.credential_injector import create_google_service_with_user_credentials
            return create_google_service_with_user_credentials(
                user_id=_user_id,
                service_name='calendar',
                version='v3'
            )
        except Exception as e:
            print(f"⚠️ Database OAuth failed for Google Meet: {e}, falling back to service account")
    
    # Fallback: Service account
    scopes = ['https://www.googleapis.com/auth/calendar']
    
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=scopes
    )
    
    return build('calendar', 'v3', credentials=credentials)'''

content = content.replace(old_calendar_service, new_calendar_service)

# Step 2: Update function signatures to add _user_id parameters
# All Google Meet functions that need _user_id
function_updates = [
    # Format: (function_name_start, line_pattern_to_replace, new_signature)
    (
        'def google_meet_create_meeting(',
        r'def google_meet_create_meeting\(\s*title: str,\s*start_time: str,\s*duration_minutes: int = 60,\s*attendees: Optional\[List\[str\]\] = None,\s*description: Optional\[str\] = None,\s*calendar_id: str = \'primary\'\s*\)',
        'def google_meet_create_meeting(\n    title: str,\n    start_time: str,\n    duration_minutes: int = 60,\n    attendees: Optional[List[str]] = None,\n    description: Optional[str] = None,\n    calendar_id: str = \'primary\',\n    _user_id: Optional[int] = None,\n    _injected_credentials: bool = None\n)'
    ),
    (
        'def google_meet_create_instant_meeting(',
        r'def google_meet_create_instant_meeting\(\s*title: str = "Quick Meeting",\s*duration_minutes: int = 30\s*\)',
        'def google_meet_create_instant_meeting(\n    title: str = "Quick Meeting",\n    duration_minutes: int = 30,\n    _user_id: Optional[int] = None,\n    _injected_credentials: bool = None\n)'
    ),
    (
        'def google_meet_schedule_recurring_meeting(',
        r'def google_meet_schedule_recurring_meeting\(.*?\) -> Dict\[str, Any\]:',
        'def google_meet_schedule_recurring_meeting(\n    title: str,\n    start_time: str,\n    duration_minutes: int,\n    recurrence_rule: str,\n    end_date: str,\n    attendees: Optional[List[str]] = None,\n    description: Optional[str] = None,\n    _user_id: Optional[int] = None,\n    _injected_credentials: bool = None\n) -> Dict[str, Any]:'
    ),
    (
        'def google_meet_get_meeting_details(calendar_event_id: str)',
        r'def google_meet_get_meeting_details\(calendar_event_id: str\) -> Dict\[str, Any\]:',
        'def google_meet_get_meeting_details(calendar_event_id: str, _user_id: Optional[int] = None, _injected_credentials: bool = None) -> Dict[str, Any]:'
    ),
    (
        'def google_meet_cancel_meeting(calendar_event_id: str, send_updates: bool = True)',
        r'def google_meet_cancel_meeting\(calendar_event_id: str, send_updates: bool = True\) -> Dict\[str, Any\]:',
        'def google_meet_cancel_meeting(calendar_event_id: str, send_updates: bool = True, _user_id: Optional[int] = None, _injected_credentials: bool = None) -> Dict[str, Any]:'
    ),
    (
        'def google_meet_list_upcoming_meetings(max_results: int = 10)',
        r'def google_meet_list_upcoming_meetings\(max_results: int = 10\) -> Dict\[str, Any\]:',
        'def google_meet_list_upcoming_meetings(max_results: int = 10, _user_id: Optional[int] = None, _injected_credentials: bool = None) -> Dict[str, Any]:'
    ),
    (
        'def google_meet_get_join_info(calendar_event_id: str)',
        r'def google_meet_get_join_info\(calendar_event_id: str\) -> Dict\[str, Any\]:',
        'def google_meet_get_join_info(calendar_event_id: str, _user_id: Optional[int] = None, _injected_credentials: bool = None) -> Dict[str, Any]:'
    ),
]

# Apply function signature updates
for func_name, pattern, replacement in function_updates:
    if re.search(pattern, content, re.DOTALL | re.MULTILINE):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.MULTILINE)
        print(f"✅ Updated: {func_name}")
    else:
        print(f"⚠️  Pattern not found: {func_name}")

# Step 3: Update all _get_calendar_service() calls to pass parameters
content = re.sub(
    r'service = _get_calendar_service\(\)',
    'service = _get_calendar_service(_user_id=_user_id, _injected_credentials=_injected_credentials)',
    content
)

# Write updated content
with open(r'C:\Users\gpoli\GIT\AI_agents\google_workspace\google_meet.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Updated Google Meet OAuth support")
print("✅ Updated _get_calendar_service() to support database OAuth")
print("✅ Updated all _get_calendar_service() calls to pass _user_id")
