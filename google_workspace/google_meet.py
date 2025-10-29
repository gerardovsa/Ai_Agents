"""
Google Meet API Integration
============================

Complete implementation of Google Meet API for AI agents.

Features:
- Meeting scheduling and management
- Space management (for recurring meetings)
- Participant management
- Recording access (read-only)
- Integration with Google Calendar
- SMART bundled tools for complex workflows

Note: Google Meet API is relatively new and has limited functionality.
Most meeting creation is done via Google Calendar with conferencing details.
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Get service account credentials path from environment
CREDENTIALS_FILE = os.getenv(
    'GOOGLE_APPLICATION_CREDENTIALS',
    str(Path(__file__).parent.parent / 'vsa-anythingllm-project-ab7c8caf8c47.json')
)


def _get_meet_service():
    """
    Build and return Google Meet API service.
    Uses service account authentication.
    
    Returns:
        Google Meet service object
    """
    scopes = [
        'https://www.googleapis.com/auth/meetings.space.created',
        'https://www.googleapis.com/auth/meetings.space.readonly'
    ]
    
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=scopes
    )
    
    return build('meet', 'v2', credentials=credentials)


def _get_calendar_service():
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
    
    return build('calendar', 'v3', credentials=credentials)


# ==================== MEETING CREATION (via Calendar) ====================

def google_meet_create_meeting(
    title: str,
    start_time: str,
    duration_minutes: int = 60,
    attendees: Optional[List[str]] = None,
    description: Optional[str] = None,
    calendar_id: str = 'primary'
) -> Dict[str, Any]:
    """
    Create a Google Meet meeting via Google Calendar.
    
    Args:
        title (str): Meeting title
        start_time (str): Start time (ISO format: 2025-10-28T14:00:00)
        duration_minutes (int): Meeting duration in minutes (default: 60)
        attendees (list): List of attendee email addresses
        description (str): Meeting description
        calendar_id (str): Calendar ID (default: 'primary')
        
    Returns:
        dict: {
            'meeting_id': str,
            'meet_link': str,
            'calendar_event_id': str,
            'title': str,
            'start_time': str,
            'end_time': str,
            'attendees': list,
            'status': str
        }
    """
    try:
        calendar_service = _get_calendar_service()
        
        # Parse start time
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Build event
        event = {
            'summary': title,
            'description': description or '',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'UTC'
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        # Add attendees if provided
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        # Create event with conference data
        created_event = calendar_service.events().insert(
            calendarId=calendar_id,
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all' if attendees else 'none'
        ).execute()
        
        # Extract Meet link
        meet_link = None
        if 'conferenceData' in created_event:
            entry_points = created_event['conferenceData'].get('entryPoints', [])
            for entry in entry_points:
                if entry.get('entryPointType') == 'video':
                    meet_link = entry.get('uri')
                    break
        
        print(f"✅ Created Google Meet: {title}")
        print(f"   Meet Link: {meet_link}")
        print(f"   Start: {start_time}")
        
        return {
            'meeting_id': created_event.get('conferenceData', {}).get('conferenceId'),
            'meet_link': meet_link,
            'calendar_event_id': created_event['id'],
            'title': created_event['summary'],
            'start_time': created_event['start'].get('dateTime'),
            'end_time': created_event['end'].get('dateTime'),
            'attendees': [a['email'] for a in created_event.get('attendees', [])],
            'status': created_event['status']
        }
        
    except HttpError as e:
        print(f"❌ Failed to create Meet: {e}")
        raise
    except Exception as e:
        print(f"❌ Error creating Meet: {e}")
        raise


def google_meet_create_instant_meeting(
    title: str = "Quick Meeting",
    duration_minutes: int = 30
) -> Dict[str, Any]:
    """
    Create an instant Google Meet meeting starting now.
    
    Args:
        title (str): Meeting title (default: "Quick Meeting")
        duration_minutes (int): Duration in minutes (default: 30)
        
    Returns:
        dict: Meeting details with Meet link
    """
    try:
        start_time = datetime.utcnow().isoformat() + 'Z'
        
        result = google_meet_create_meeting(
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes
        )
        
        print(f"✅ Instant meeting created: {result['meet_link']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Failed to create instant meeting: {e}")
        raise


def google_meet_schedule_recurring_meeting(
    title: str,
    start_time: str,
    duration_minutes: int,
    frequency: str,
    count: int,
    attendees: Optional[List[str]] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a recurring Google Meet series.
    
    Args:
        title (str): Meeting title
        start_time (str): First meeting start time (ISO format)
        duration_minutes (int): Duration per meeting
        frequency (str): DAILY, WEEKLY, MONTHLY
        count (int): Number of occurrences
        attendees (list): Attendee email addresses
        description (str): Meeting description
        
    Returns:
        dict: Recurring meeting details
    """
    try:
        calendar_service = _get_calendar_service()
        
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # Build recurrence rule
        recurrence_rule = f"RRULE:FREQ={frequency};COUNT={count}"
        
        event = {
            'summary': title,
            'description': description or '',
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'UTC'
            },
            'recurrence': [recurrence_rule],
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-recurring-{int(datetime.now().timestamp())}",
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }
        
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        
        created_event = calendar_service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1,
            sendUpdates='all' if attendees else 'none'
        ).execute()
        
        meet_link = None
        if 'conferenceData' in created_event:
            entry_points = created_event['conferenceData'].get('entryPoints', [])
            for entry in entry_points:
                if entry.get('entryPointType') == 'video':
                    meet_link = entry.get('uri')
                    break
        
        print(f"✅ Created recurring Meet: {title}")
        print(f"   Frequency: {frequency}, Count: {count}")
        print(f"   Meet Link: {meet_link}")
        
        return {
            'meeting_id': created_event.get('conferenceData', {}).get('conferenceId'),
            'meet_link': meet_link,
            'calendar_event_id': created_event['id'],
            'title': created_event['summary'],
            'start_time': created_event['start'].get('dateTime'),
            'recurrence': recurrence_rule,
            'frequency': frequency,
            'count': count,
            'attendees': [a['email'] for a in created_event.get('attendees', [])]
        }
        
    except Exception as e:
        print(f"❌ Failed to create recurring meeting: {e}")
        raise


# ==================== MEETING MANAGEMENT ====================

def google_meet_get_meeting_details(calendar_event_id: str) -> Dict[str, Any]:
    """
    Get details of a Google Meet meeting.
    
    Args:
        calendar_event_id (str): Calendar event ID
        
    Returns:
        dict: Meeting details
    """
    try:
        calendar_service = _get_calendar_service()
        
        event = calendar_service.events().get(
            calendarId='primary',
            eventId=calendar_event_id
        ).execute()
        
        meet_link = None
        meeting_code = None
        if 'conferenceData' in event:
            conference_data = event['conferenceData']
            meeting_code = conference_data.get('conferenceId')
            entry_points = conference_data.get('entryPoints', [])
            for entry in entry_points:
                if entry.get('entryPointType') == 'video':
                    meet_link = entry.get('uri')
                    break
        
        print(f"📅 Retrieved meeting: {event.get('summary')}")
        
        return {
            'calendar_event_id': event['id'],
            'meeting_id': meeting_code,
            'meet_link': meet_link,
            'title': event.get('summary'),
            'description': event.get('description'),
            'start_time': event['start'].get('dateTime'),
            'end_time': event['end'].get('dateTime'),
            'status': event.get('status'),
            'attendees': [
                {
                    'email': a.get('email'),
                    'response_status': a.get('responseStatus')
                }
                for a in event.get('attendees', [])
            ],
            'organizer': event.get('organizer', {}).get('email'),
            'created': event.get('created'),
            'updated': event.get('updated')
        }
        
    except Exception as e:
        print(f"❌ Failed to get meeting details: {e}")
        raise


def google_meet_update_meeting(
    calendar_event_id: str,
    title: Optional[str] = None,
    start_time: Optional[str] = None,
    duration_minutes: Optional[int] = None,
    description: Optional[str] = None,
    add_attendees: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update a Google Meet meeting.
    
    Args:
        calendar_event_id (str): Calendar event ID
        title (str): New title
        start_time (str): New start time (ISO format)
        duration_minutes (int): New duration
        description (str): New description
        add_attendees (list): Additional attendees to add
        
    Returns:
        dict: Updated meeting details
    """
    try:
        calendar_service = _get_calendar_service()
        
        # Get current event
        event = calendar_service.events().get(
            calendarId='primary',
            eventId=calendar_event_id
        ).execute()
        
        # Update fields
        if title:
            event['summary'] = title
        
        if description:
            event['description'] = description
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            if duration_minutes:
                end_dt = start_dt + timedelta(minutes=duration_minutes)
            else:
                # Keep original duration
                original_start = datetime.fromisoformat(event['start']['dateTime'].replace('Z', '+00:00'))
                original_end = datetime.fromisoformat(event['end']['dateTime'].replace('Z', '+00:00'))
                duration = (original_end - original_start).total_seconds() / 60
                end_dt = start_dt + timedelta(minutes=duration)
            
            event['start'] = {'dateTime': start_dt.isoformat(), 'timeZone': 'UTC'}
            event['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': 'UTC'}
        
        if add_attendees:
            existing_attendees = event.get('attendees', [])
            existing_emails = {a.get('email') for a in existing_attendees}
            new_attendees = [{'email': email} for email in add_attendees if email not in existing_emails]
            event['attendees'] = existing_attendees + new_attendees
        
        # Update event
        updated_event = calendar_service.events().update(
            calendarId='primary',
            eventId=calendar_event_id,
            body=event,
            sendUpdates='all'
        ).execute()
        
        print(f"✅ Updated meeting: {updated_event.get('summary')}")
        
        return google_meet_get_meeting_details(calendar_event_id)
        
    except Exception as e:
        print(f"❌ Failed to update meeting: {e}")
        raise


def google_meet_cancel_meeting(calendar_event_id: str, send_updates: bool = True) -> Dict[str, Any]:
    """
    Cancel a Google Meet meeting.
    
    Args:
        calendar_event_id (str): Calendar event ID
        send_updates (bool): Send cancellation emails to attendees (default: True)
        
    Returns:
        dict: Cancellation confirmation
    """
    try:
        calendar_service = _get_calendar_service()
        
        # Get event details first
        event = calendar_service.events().get(
            calendarId='primary',
            eventId=calendar_event_id
        ).execute()
        
        # Delete event
        calendar_service.events().delete(
            calendarId='primary',
            eventId=calendar_event_id,
            sendUpdates='all' if send_updates else 'none'
        ).execute()
        
        print(f"✅ Cancelled meeting: {event.get('summary')}")
        
        return {
            'cancelled': True,
            'calendar_event_id': calendar_event_id,
            'title': event.get('summary'),
            'notifications_sent': send_updates
        }
        
    except Exception as e:
        print(f"❌ Failed to cancel meeting: {e}")
        raise


# ==================== MEETING LISTING ====================

def google_meet_list_upcoming_meetings(max_results: int = 10) -> Dict[str, Any]:
    """
    List upcoming Google Meet meetings.
    
    Args:
        max_results (int): Maximum number of meetings to return (default: 10)
        
    Returns:
        dict: List of upcoming meetings
    """
    try:
        calendar_service = _get_calendar_service()
        
        now = datetime.utcnow().isoformat() + 'Z'
        
        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # Filter only events with Meet links
        meet_meetings = []
        for event in events:
            if 'conferenceData' in event:
                conference_data = event['conferenceData']
                meet_link = None
                for entry in conference_data.get('entryPoints', []):
                    if entry.get('entryPointType') == 'video':
                        meet_link = entry.get('uri')
                        break
                
                if meet_link:
                    meet_meetings.append({
                        'calendar_event_id': event['id'],
                        'meeting_id': conference_data.get('conferenceId'),
                        'meet_link': meet_link,
                        'title': event.get('summary'),
                        'start_time': event['start'].get('dateTime'),
                        'end_time': event['end'].get('dateTime'),
                        'status': event.get('status'),
                        'attendee_count': len(event.get('attendees', []))
                    })
        
        print(f"📅 Found {len(meet_meetings)} upcoming Meet meetings")
        
        return {
            'meetings': meet_meetings,
            'count': len(meet_meetings)
        }
        
    except Exception as e:
        print(f"❌ Failed to list meetings: {e}")
        raise


# ==================== SPACES API (Meeting Rooms) ====================

def google_meet_create_space(display_name: str) -> Dict[str, Any]:
    """
    Create a persistent Google Meet space (meeting room).
    Spaces are reusable meeting links.
    
    Args:
        display_name (str): Display name for the space
        
    Returns:
        dict: Space details with permanent Meet link
    """
    try:
        meet_service = _get_meet_service()
        
        space = {
            'config': {
                'entryPointAccess': 'ALL',
                'accessType': 'OPEN'
            }
        }
        
        created_space = meet_service.spaces().create(body=space).execute()
        
        print(f"✅ Created Meet space: {display_name}")
        print(f"   Space name: {created_space['name']}")
        
        return {
            'space_id': created_space['name'].split('/')[-1],
            'space_name': created_space['name'],
            'meet_link': created_space.get('meetingUri'),
            'meeting_code': created_space.get('meetingCode'),
            'config': created_space.get('config'),
            'created': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create space: {e}")
        raise


def google_meet_get_space(space_id: str) -> Dict[str, Any]:
    """
    Get details of a Google Meet space.
    
    Args:
        space_id (str): Space ID
        
    Returns:
        dict: Space details
    """
    try:
        meet_service = _get_meet_service()
        
        space = meet_service.spaces().get(name=f"spaces/{space_id}").execute()
        
        print(f"📍 Retrieved space: {space['name']}")
        
        return {
            'space_id': space_id,
            'space_name': space['name'],
            'meet_link': space.get('meetingUri'),
            'meeting_code': space.get('meetingCode'),
            'config': space.get('config'),
            'active_conference': space.get('activeConference')
        }
        
    except Exception as e:
        print(f"❌ Failed to get space: {e}")
        raise


# ==================== SMART BULK ACTIONS ====================

def google_meet_create_daily_standup(
    team_name: str,
    start_time: str,
    attendees: List[str],
    duration_minutes: int = 15,
    days_count: int = 30
) -> Dict[str, Any]:
    """
    🎯 SMART: Create a daily standup series with Google Meet.
    
    Creates a recurring daily meeting optimized for standups:
    - Short duration (15 min default)
    - Same time daily
    - Same Meet link for consistency
    - Email reminders to all attendees
    
    Args:
        team_name (str): Team name (e.g., "Engineering Team")
        start_time (str): First standup time (ISO format: 2025-10-28T09:00:00)
        attendees (list): Team member email addresses
        duration_minutes (int): Duration in minutes (default: 15)
        days_count (int): Number of days (default: 30)
        
    Returns:
        dict: Daily standup series details
    """
    try:
        print(f"🎯 Creating daily standup for {team_name}...")
        
        title = f"{team_name} - Daily Standup"
        description = f"""Daily standup meeting for {team_name}

Agenda:
• What did you accomplish yesterday?
• What are you working on today?
• Any blockers or challenges?

Duration: {duration_minutes} minutes
Keep it brief and focused!"""
        
        # Create recurring meeting
        result = google_meet_schedule_recurring_meeting(
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes,
            frequency='DAILY',
            count=days_count,
            attendees=attendees,
            description=description
        )
        
        print(f"✅ Daily standup created successfully!")
        print(f"   Team: {team_name}")
        print(f"   Attendees: {len(attendees)}")
        print(f"   Duration: {duration_minutes} min")
        print(f"   Occurrences: {days_count} days")
        print(f"   Meet Link: {result['meet_link']}")
        
        return {
            **result,
            'type': 'daily_standup',
            'team_name': team_name,
            'setup_complete': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create daily standup: {e}")
        raise


def google_meet_schedule_interview_series(
    candidate_name: str,
    candidate_email: str,
    interviews: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    🎯 SMART: Schedule a complete interview series for a candidate.
    
    Creates multiple interview sessions with different interviewers:
    - Separate Meet links for each interview
    - Coordinated timing between sessions
    - Email invites to all participants
    - Structured interview flow
    
    Args:
        candidate_name (str): Candidate's full name
        candidate_email (str): Candidate's email address
        interviews (list): List of interview dicts with:
            - title (str): Interview type (e.g., "Technical Interview")
            - start_time (str): Start time (ISO format)
            - duration_minutes (int): Duration in minutes
            - interviewers (list): Interviewer email addresses
            - description (str): Optional interview details
            
    Returns:
        dict: Interview series details with all Meet links
    """
    try:
        print(f"🎯 Scheduling interview series for {candidate_name}...")
        
        created_interviews = []
        
        for idx, interview_data in enumerate(interviews, 1):
            title = f"{interview_data['title']} - {candidate_name}"
            
            description = interview_data.get('description', '')
            description += f"\n\nCandidate: {candidate_name}\nInterview {idx}/{len(interviews)}"
            
            attendees = [candidate_email] + interview_data['interviewers']
            
            meeting = google_meet_create_meeting(
                title=title,
                start_time=interview_data['start_time'],
                duration_minutes=interview_data['duration_minutes'],
                attendees=attendees,
                description=description
            )
            
            created_interviews.append({
                'interview_number': idx,
                'type': interview_data['title'],
                'meet_link': meeting['meet_link'],
                'calendar_event_id': meeting['calendar_event_id'],
                'start_time': meeting['start_time'],
                'interviewers': interview_data['interviewers'],
                'duration': interview_data['duration_minutes']
            })
            
            print(f"   ✅ Interview {idx}: {interview_data['title']}")
        
        print(f"✅ Interview series scheduled successfully!")
        print(f"   Candidate: {candidate_name} ({candidate_email})")
        print(f"   Total interviews: {len(created_interviews)}")
        
        return {
            'candidate_name': candidate_name,
            'candidate_email': candidate_email,
            'interviews': created_interviews,
            'total_interviews': len(created_interviews),
            'series_complete': True
        }
        
    except Exception as e:
        print(f"❌ Failed to schedule interview series: {e}")
        raise


def google_meet_create_team_meeting_with_agenda(
    title: str,
    start_time: str,
    duration_minutes: int,
    attendees: List[str],
    agenda_items: List[str],
    preparation_notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    🎯 SMART: Create a structured team meeting with detailed agenda.
    
    Creates a professional meeting with:
    - Formatted agenda in description
    - Time estimates per agenda item
    - Preparation notes for attendees
    - Meet link for remote/hybrid attendance
    
    Args:
        title (str): Meeting title
        start_time (str): Start time (ISO format)
        duration_minutes (int): Total duration in minutes
        attendees (list): Attendee email addresses
        agenda_items (list): List of agenda items (strings)
        preparation_notes (str): Optional preparation instructions
        
    Returns:
        dict: Meeting details with agenda
    """
    try:
        print(f"🎯 Creating team meeting with agenda: {title}...")
        
        # Build formatted agenda
        description = f"**Meeting Agenda**\n\n"
        
        time_per_item = duration_minutes // len(agenda_items) if agenda_items else duration_minutes
        
        for idx, item in enumerate(agenda_items, 1):
            description += f"{idx}. {item} (~{time_per_item} min)\n"
        
        if preparation_notes:
            description += f"\n**Preparation Notes**\n{preparation_notes}\n"
        
        description += f"\n**Meeting Duration:** {duration_minutes} minutes"
        description += f"\n**Total Attendees:** {len(attendees)}"
        
        # Create meeting
        meeting = google_meet_create_meeting(
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes,
            attendees=attendees,
            description=description
        )
        
        print(f"✅ Team meeting created successfully!")
        print(f"   Title: {title}")
        print(f"   Agenda items: {len(agenda_items)}")
        print(f"   Attendees: {len(attendees)}")
        print(f"   Duration: {duration_minutes} min")
        print(f"   Meet Link: {meeting['meet_link']}")
        
        return {
            **meeting,
            'type': 'team_meeting',
            'agenda_items': agenda_items,
            'time_per_item': time_per_item,
            'has_preparation_notes': preparation_notes is not None
        }
        
    except Exception as e:
        print(f"❌ Failed to create team meeting: {e}")
        raise


def google_meet_create_weekly_review(
    team_name: str,
    start_time: str,
    attendees: List[str],
    weeks_count: int = 12,
    duration_minutes: int = 60
) -> Dict[str, Any]:
    """
    🎯 SMART: Create a weekly review/retrospective series.
    
    Creates a recurring weekly meeting for team reviews:
    - Consistent schedule (weekly)
    - Structured retrospective format
    - Same Meet link for all sessions
    - Duration optimized for review meetings
    
    Args:
        team_name (str): Team name
        start_time (str): First review time (ISO format)
        attendees (list): Team member email addresses
        weeks_count (int): Number of weeks (default: 12)
        duration_minutes (int): Duration in minutes (default: 60)
        
    Returns:
        dict: Weekly review series details
    """
    try:
        print(f"🎯 Creating weekly review for {team_name}...")
        
        title = f"{team_name} - Weekly Review"
        
        description = f"""Weekly review and retrospective for {team_name}

**Agenda:**
1. Wins from last week (15 min)
   • What went well?
   • Celebrate successes

2. Challenges and learnings (15 min)
   • What could be improved?
   • What did we learn?

3. Next week's priorities (20 min)
   • Key objectives
   • Resource allocation

4. Process improvements (10 min)
   • Action items from last retro
   • New improvement suggestions

**Duration:** {duration_minutes} minutes
**Format:** Open discussion + action items"""
        
        result = google_meet_schedule_recurring_meeting(
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes,
            frequency='WEEKLY',
            count=weeks_count,
            attendees=attendees,
            description=description
        )
        
        print(f"✅ Weekly review created successfully!")
        print(f"   Team: {team_name}")
        print(f"   Frequency: Weekly for {weeks_count} weeks")
        print(f"   Duration: {duration_minutes} min")
        print(f"   Attendees: {len(attendees)}")
        print(f"   Meet Link: {result['meet_link']}")
        
        return {
            **result,
            'type': 'weekly_review',
            'team_name': team_name,
            'review_format': 'retrospective',
            'setup_complete': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create weekly review: {e}")
        raise


# ==================== HELPER FUNCTIONS ====================

def google_meet_get_join_info(calendar_event_id: str) -> Dict[str, Any]:
    """
    Get quick join information for a meeting.
    
    Args:
        calendar_event_id (str): Calendar event ID
        
    Returns:
        dict: Simple join information
    """
    try:
        details = google_meet_get_meeting_details(calendar_event_id)
        
        return {
            'meet_link': details['meet_link'],
            'meeting_id': details['meeting_id'],
            'title': details['title'],
            'start_time': details['start_time'],
            'time_until_start': _calculate_time_until(details['start_time'])
        }
        
    except Exception as e:
        print(f"❌ Failed to get join info: {e}")
        raise


def _calculate_time_until(start_time: str) -> str:
    """Calculate human-readable time until meeting starts."""
    try:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        now = datetime.now(start_dt.tzinfo)
        delta = start_dt - now
        
        if delta.total_seconds() < 0:
            return "Meeting has started"
        
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        
        if hours > 24:
            days = hours // 24
            return f"In {days} day{'s' if days != 1 else ''}"
        elif hours > 0:
            return f"In {hours} hour{'s' if hours != 1 else ''} {minutes} min"
        else:
            return f"In {minutes} minute{'s' if minutes != 1 else ''}"
            
    except Exception:
        return "Unknown"


# ==================== EXPORTS ====================

__all__ = [
    # Meeting creation
    'google_meet_create_meeting',
    'google_meet_create_instant_meeting',
    'google_meet_schedule_recurring_meeting',
    
    # Meeting management
    'google_meet_get_meeting_details',
    'google_meet_update_meeting',
    'google_meet_cancel_meeting',
    
    # Meeting listing
    'google_meet_list_upcoming_meetings',
    
    # Spaces (persistent rooms)
    'google_meet_create_space',
    'google_meet_get_space',
    
    # SMART bulk actions
    'google_meet_create_daily_standup',
    'google_meet_schedule_interview_series',
    'google_meet_create_team_meeting_with_agenda',
    'google_meet_create_weekly_review',
    
    # Helper functions
    'google_meet_get_join_info'
]


if __name__ == '__main__':
    print("Google Meet API Integration - Testing")
    print("=" * 50)
    
    # Test instant meeting
    print("\n1. Testing instant meeting creation...")
    try:
        meeting = google_meet_create_instant_meeting(
            title="Test Quick Meeting",
            duration_minutes=30
        )
        print(f"   ✅ Success! Join at: {meeting['meet_link']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test upcoming meetings list
    print("\n2. Testing upcoming meetings list...")
    try:
        meetings = google_meet_list_upcoming_meetings(max_results=5)
        print(f"   ✅ Found {meetings['count']} upcoming meetings")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")
