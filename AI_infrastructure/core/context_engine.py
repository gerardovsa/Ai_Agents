"""
Context Engine - User Profile, Temporal, Geographic & Memory Awareness
=======================================================================

Provides rich context to AI based on:
- User profile (name, role, preferences, history)
- Temporal awareness (timezone, time of day, day of week, season)
- Geographic awareness (location, IP, regional settings)
- Memory building (conversation history, project links, past work)
- Event triggers (deadlines, reminders, scheduled tasks)

This enables the AI to be context-aware and proactive.
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import pytz
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class ContextEngine:
    """
    Central context engine that provides AI with rich awareness of:
    - Who the user is (profile)
    - When it is (time, timezone)
    - Where the user is (location)
    - What was discussed before (memory)
    - What's coming up (events, deadlines)
    """
    
    def __init__(self):
        self.user_profiles = {}
        self.conversation_memory = defaultdict(list)
        self.project_links = defaultdict(list)
        self.user_preferences = {}
        
    def get_full_context(self, user_id: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Get complete context for AI to be aware of user, time, location, memory.
        
        Args:
            user_id: User identifier from authentication
            ip_address: User's IP address (for location inference)
        
        Returns:
            dict: Complete context bundle for AI system prompt
        """
        context = {
            'user_profile': self.get_user_profile(user_id),
            'temporal_context': self.get_temporal_context(user_id),
            'geographic_context': self.get_geographic_context(user_id, ip_address),
            'memory_context': self.get_memory_context(user_id),
            'event_context': self.get_event_context(user_id),
            'project_context': self.get_project_context(user_id),
            'context_timestamp': datetime.utcnow().isoformat()
        }
        
        return context
    
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Load user profile with preferences, role, history.
        
        Returns:
            dict: User profile with name, role, preferences, join date, etc.
        """
        # TODO: Load from database
        # For now, return mock profile
        profile = self.user_profiles.get(user_id, {
            'user_id': user_id,
            'name': 'User',
            'email': f'{user_id}@example.com',
            'role': 'developer',
            'timezone': 'America/New_York',
            'language': 'en',
            'join_date': '2025-01-01',
            'total_conversations': len(self.conversation_memory.get(user_id, [])),
            'preferences': {
                'communication_style': 'professional',
                'detail_level': 'comprehensive',
                'preferred_tools': ['gmail', 'google_docs', 'google_tasks'],
                'notification_hours': {'start': 9, 'end': 18},
                'work_days': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            }
        })
        
        return profile
    
    def get_temporal_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get temporal awareness: timezone, time of day, day of week, season.
        
        Returns:
            dict: Temporal context for AI to be time-aware
        """
        profile = self.get_user_profile(user_id)
        user_tz = pytz.timezone(profile.get('timezone', 'UTC'))
        now = datetime.now(user_tz)
        
        # Determine time of day
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
            greeting = "Good morning"
        elif 12 <= hour < 17:
            time_of_day = "afternoon"
            greeting = "Good afternoon"
        elif 17 <= hour < 21:
            time_of_day = "evening"
            greeting = "Good evening"
        else:
            time_of_day = "night"
            greeting = "Hello"
        
        # Determine work status
        work_hours = profile['preferences']['notification_hours']
        is_work_hours = work_hours['start'] <= hour < work_hours['end']
        
        # Day of week
        day_name = now.strftime('%A').lower()
        is_work_day = day_name in profile['preferences']['work_days']
        
        # Season (Northern Hemisphere)
        month = now.month
        if month in [12, 1, 2]:
            season = "winter"
        elif month in [3, 4, 5]:
            season = "spring"
        elif month in [6, 7, 8]:
            season = "summer"
        else:
            season = "fall"
        
        return {
            'current_datetime': now.isoformat(),
            'timezone': str(user_tz),
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
            'day_of_week': day_name,
            'is_weekend': day_name in ['saturday', 'sunday'],
            'is_work_day': is_work_day,
            'is_work_hours': is_work_hours,
            'time_of_day': time_of_day,
            'greeting': greeting,
            'season': season,
            'week_number': now.isocalendar()[1],
            'day_of_year': now.timetuple().tm_yday
        }
    
    def get_geographic_context(self, user_id: str, ip_address: str = None) -> Dict[str, Any]:
        """
        Get geographic awareness from IP and user profile.
        
        Returns:
            dict: Location, region, language preferences
        """
        profile = self.get_user_profile(user_id)
        
        # TODO: Use IP geolocation service (MaxMind, ipapi.co, etc.)
        # For now, infer from timezone
        context = {
            'timezone': profile.get('timezone', 'UTC'),
            'language': profile.get('language', 'en'),
            'ip_address': ip_address or 'unknown',
            'inferred_region': self._infer_region_from_timezone(profile.get('timezone', 'UTC'))
        }
        
        return context
    
    def _infer_region_from_timezone(self, timezone: str) -> str:
        """Infer geographic region from timezone"""
        if 'America' in timezone:
            return 'Americas'
        elif 'Europe' in timezone:
            return 'Europe'
        elif 'Asia' in timezone:
            return 'Asia'
        elif 'Pacific' in timezone:
            return 'Pacific'
        elif 'Africa' in timezone:
            return 'Africa'
        else:
            return 'Unknown'
    
    def get_memory_context(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """
        Get conversation memory - past discussions, topics, decisions.
        
        Returns:
            dict: Recent conversation summaries and key topics
        """
        conversations = self.conversation_memory.get(user_id, [])
        recent = conversations[-limit:] if len(conversations) > limit else conversations
        
        # Extract key topics from recent conversations
        topics = set()
        for conv in recent:
            topics.update(conv.get('topics', []))
        
        return {
            'total_conversations': len(conversations),
            'recent_conversations': recent,
            'recent_topics': list(topics),
            'has_conversation_history': len(conversations) > 0,
            'last_interaction': conversations[-1]['timestamp'] if conversations else None
        }
    
    def get_event_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get upcoming events, deadlines, reminders from AI's task system.
        
        Returns:
            dict: Upcoming deadlines, pending tasks, scheduled events
        """
        # TODO: Integration with ai_check_pending_work() and Google Calendar
        
        return {
            'has_pending_deadlines': False,
            'upcoming_deadlines': [],
            'overdue_tasks': [],
            'today_tasks': [],
            'this_week_tasks': [],
            'scheduled_reminders': []
        }
    
    def get_project_context(self, user_id: str) -> Dict[str, Any]:
        """
        Get links to past work, active projects, completed projects.
        
        Returns:
            dict: Project history and links to work
        """
        projects = self.project_links.get(user_id, [])
        
        active_projects = [p for p in projects if p.get('status') == 'active']
        completed_projects = [p for p in projects if p.get('status') == 'completed']
        
        return {
            'total_projects': len(projects),
            'active_projects': active_projects,
            'completed_projects': completed_projects[-5:],  # Last 5
            'has_active_work': len(active_projects) > 0
        }
    
    def add_conversation_memory(self, user_id: str, conversation_data: Dict[str, Any]):
        """
        Store conversation for future reference.
        
        Args:
            user_id: User identifier
            conversation_data: Dict with summary, topics, key decisions, timestamp
        """
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []
        
        conversation_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'summary': conversation_data.get('summary', ''),
            'topics': conversation_data.get('topics', []),
            'key_decisions': conversation_data.get('key_decisions', []),
            'tools_used': conversation_data.get('tools_used', []),
            'outcome': conversation_data.get('outcome', '')
        }
        
        self.conversation_memory[user_id].append(conversation_entry)
        
        # Keep only last 100 conversations per user
        if len(self.conversation_memory[user_id]) > 100:
            self.conversation_memory[user_id] = self.conversation_memory[user_id][-100:]
    
    def add_project_link(self, user_id: str, project_data: Dict[str, Any]):
        """
        Store link to work AI has done for user.
        
        Args:
            user_id: User identifier
            project_data: Dict with name, description, links, status, timestamp
        """
        if user_id not in self.project_links:
            self.project_links[user_id] = []
        
        project_entry = {
            'project_id': project_data.get('project_id', f"proj_{len(self.project_links[user_id])}"),
            'name': project_data.get('name', 'Untitled Project'),
            'description': project_data.get('description', ''),
            'created_date': project_data.get('created_date', datetime.utcnow().isoformat()),
            'status': project_data.get('status', 'active'),  # active, completed, archived
            'links': project_data.get('links', []),  # URLs to docs, sheets, etc.
            'tags': project_data.get('tags', []),
            'tasks_completed': project_data.get('tasks_completed', [])
        }
        
        self.project_links[user_id].append(project_entry)
    
    def build_system_prompt_context(self, user_id: str, ip_address: str = None) -> str:
        """
        Build rich context string for AI system prompt.
        
        Args:
            user_id: User identifier
            ip_address: User's IP address
        
        Returns:
            str: Formatted context for system prompt
        """
        context = self.get_full_context(user_id, ip_address)
        
        user = context['user_profile']
        temporal = context['temporal_context']
        memory = context['memory_context']
        projects = context['project_context']
        
        prompt_context = f"""
**🧠 USER CONTEXT & AWARENESS:**

**User Profile:**
- Name: {user['name']}
- Role: {user['role']}
- Timezone: {user['timezone']}
- Total conversations: {user.get('total_conversations', len(self.conversation_memory.get(user_id, [])))}
- Communication style: {user['preferences']['communication_style']}
- Detail preference: {user['preferences']['detail_level']}

**Temporal Awareness:**
- {temporal['greeting']}! It's {temporal['time_of_day']} for the user.
- Current time: {temporal['time']} ({temporal['timezone']})
- Day: {temporal['day_of_week'].title()}, {temporal['date']}
- {'✅ Work hours' if temporal['is_work_hours'] else '⏸️ Outside work hours'}
- {'🏢 Work day' if temporal['is_work_day'] else '🏖️ Weekend/Off day'}
- Season: {temporal['season'].title()}

**Memory & History:**
- {'📚 Has conversation history (' + str(memory['total_conversations']) + ' past conversations)' if memory['has_conversation_history'] else '🆕 New user - first conversation'}
- Recent topics discussed: {', '.join(memory['recent_topics'][:5]) if memory['recent_topics'] else 'None yet'}
- Last interaction: {memory['last_interaction'] or 'Never'}

**Active Projects:**
{'- ' + chr(10).join([f"📁 {p['name']} ({p['status']})" for p in projects['active_projects']]) if projects['active_projects'] else '- No active projects yet'}

**Completed Work:**
{'- ' + chr(10).join([f"✅ {p['name']}" for p in projects['completed_projects']]) if projects['completed_projects'] else '- No completed projects yet'}

**AI Behavior Adjustments:**
- Greeting style: Use "{temporal['greeting']}" appropriate for {temporal['time_of_day']}
- Communication: Use {user['preferences']['communication_style']} tone
- Detail level: Provide {user['preferences']['detail_level']} explanations
- {'⏰ Consider user may be wrapping up work (evening)' if temporal['time_of_day'] == 'evening' else ''}
- {'🌙 User is outside normal hours - keep responses concise' if not temporal['is_work_hours'] else ''}
- {'📝 Reference past conversations to show continuity' if memory['has_conversation_history'] else '🆕 This is a new user - be welcoming and explanatory'}
"""
        
        return prompt_context.strip()


# Singleton instance
context_engine = ContextEngine()


def get_context_engine() -> ContextEngine:
    """Get singleton context engine instance"""
    return context_engine
