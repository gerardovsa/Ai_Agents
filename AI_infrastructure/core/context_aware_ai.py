"""
Context-Aware AI Integration
============================

Integrates all context systems to provide AI with rich awareness:
- User profiles (who)
- Temporal context (when)
- Geographic context (where)
- Memory & history (what was discussed)
- Event triggers (proactive activation)
- Project links (past work)

This module provides the enhanced system prompt that makes AI context-aware.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI_infrastructure.core.context_engine import get_context_engine
from AI_infrastructure.core.event_triggers import get_event_trigger_system
from google_workspace.ai_personal_tasks import (
    ai_check_pending_work,
    ai_list_my_tasks
)


class ContextAwareAI:
    """
    Provides context-aware AI capabilities by integrating:
    - User profile awareness
    - Temporal/geographic awareness  
    - Conversation memory
    - Event-driven activation
    - Project tracking
    """
    
    def __init__(self):
        self.context_engine = get_context_engine()
        self.event_system = get_event_trigger_system()
        
    def build_enhanced_system_prompt(self, user_id: str, ip_address: str = None,
                                    base_prompt: str = "") -> str:
        """
        Build complete system prompt with all context awareness.
        
        Args:
            user_id: User identifier
            ip_address: User's IP address
            base_prompt: Base system prompt to enhance
        
        Returns:
            str: Complete context-aware system prompt
        """
        # Get all context
        user_context = self.context_engine.build_system_prompt_context(user_id, ip_address)
        
        # Get AI's pending work
        try:
            pending_work = ai_check_pending_work()
            ai_tasks_context = self._format_ai_tasks_context(pending_work)
        except Exception as e:
            ai_tasks_context = "**AI Tasks:** Unable to load pending work."
        
        # Get upcoming events for this user
        user_events = self.event_system.get_user_triggers(user_id, active_only=True)
        events_context = self._format_events_context(user_events)
        
        # Build complete prompt
        enhanced_prompt = f"""{base_prompt}

{user_context}

{ai_tasks_context}

{events_context}

**🎯 CONTEXT-AWARE BEHAVIOR:**

Based on the context above, adjust your behavior:

1. **Personalization:**
   - Address user by name when appropriate
   - Reference past conversations to show continuity
   - Use communication style preferences
   - Adapt detail level to user's preference

2. **Temporal Awareness:**
   - Use appropriate greeting for time of day
   - Be concise if outside work hours
   - Consider timezone when scheduling
   - Mention if it's evening ("you may be wrapping up")

3. **Memory Continuity:**
   - Reference relevant past discussions
   - Link to previously completed work
   - Resume ongoing projects seamlessly
   - Show you "remember" user's preferences

4. **Proactive Assistance:**
   - Check your own pending tasks at conversation start
   - Mention upcoming deadlines if relevant
   - Offer to complete unfinished work
   - Suggest next steps based on history

5. **Event Awareness:**
   - Alert user to approaching deadlines
   - Provide briefings/reviews when scheduled
   - Follow up on past commitments
   - Track progress on active projects

**REMEMBER:**
- You are NOT just reactive - you can be proactive based on events
- You have persistent memory through Google Tasks
- You know the user's context (time, location, history)
- You can reference past work and continue projects
- You should feel like a continuous assistant, not a new AI each time
"""
        
        return enhanced_prompt.strip()
    
    def _format_ai_tasks_context(self, pending_work: Dict[str, Any]) -> str:
        """Format AI's pending work for system prompt"""
        if not pending_work.get('success'):
            return "**🤖 Your Pending Work:** Unable to load tasks"
        
        high_priority = pending_work.get('high_priority_count', 0)
        overdue = pending_work.get('overdue_count', 0)
        total = pending_work.get('total_pending', 0)
        
        context = f"""**🤖 YOUR PENDING WORK (AI Tasks):**
- Total pending: {total} tasks
- High priority: {high_priority} tasks
- Overdue: {overdue} tasks"""
        
        # Show top priority tasks
        high_tasks = pending_work.get('high_priority_tasks', [])
        if high_tasks:
            context += "\n- Top priorities:\n"
            for task in high_tasks[:3]:
                title = task.get('title', 'Untitled').replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
                context += f"  • {title}\n"
        
        # Show overdue
        overdue_tasks = pending_work.get('overdue_tasks', [])
        if overdue_tasks:
            context += "- ⚠️ OVERDUE tasks:\n"
            for task in overdue_tasks[:2]:
                title = task.get('title', 'Untitled').replace('🔴 ', '').replace('🟡 ', '').replace('🟢 ', '')
                context += f"  • {title}\n"
        
        if total > 0:
            context += "\n**Action:** Consider mentioning relevant pending work to user if it relates to their request."
        
        return context.strip()
    
    def _format_events_context(self, events: List) -> str:
        """Format upcoming events for system prompt"""
        if not events:
            return "**📅 Upcoming Events:** No scheduled events"
        
        context = "**📅 UPCOMING EVENTS & TRIGGERS:**\n"
        
        for event in events[:5]:  # Show next 5
            time_str = event.scheduled_time.strftime('%Y-%m-%d %H:%M')
            event_type = event.trigger_type.value.replace('_', ' ').title()
            
            payload = event.payload or {}
            message = payload.get('message', '') or payload.get('task_title', '') or 'Scheduled event'
            
            context += f"- {event_type} at {time_str}: {message}\n"
        
        if len(events) > 5:
            context += f"- ...and {len(events) - 5} more events\n"
        
        context += "\n**Action:** Be prepared to handle these events when they trigger."
        
        return context.strip()
    
    def record_conversation(self, user_id: str, conversation_summary: str,
                          topics: List[str], tools_used: List[str],
                          outcome: str = ""):
        """
        Record conversation for future context.
        
        Args:
            user_id: User identifier
            conversation_summary: Brief summary
            topics: List of topics discussed
            tools_used: Tools that were used
            outcome: What was accomplished
        """
        self.context_engine.add_conversation_memory(user_id, {
            'summary': conversation_summary,
            'topics': topics,
            'tools_used': tools_used,
            'outcome': outcome,
            'key_decisions': []
        })
    
    def record_project(self, user_id: str, project_name: str, description: str,
                      links: List[str], tags: List[str] = None):
        """
        Record completed work/project for user.
        
        Args:
            user_id: User identifier
            project_name: Name of work completed
            description: What was done
            links: URLs to Google Docs, Sheets, etc.
            tags: Tags for categorization
        """
        self.context_engine.add_project_link(user_id, {
            'name': project_name,
            'description': description,
            'links': links,
            'tags': tags or [],
            'status': 'completed',
            'created_date': datetime.now().isoformat()
        })
    
    def setup_user_automations(self, user_id: str, preferences: Dict[str, Any]):
        """
        Set up automatic triggers based on user preferences.
        
        Args:
            user_id: User identifier
            preferences: Dict with:
                - daily_briefing: bool
                - briefing_time_hour: int
                - weekly_review: bool
                - review_day: int (0-6)
                - deadline_warnings: bool
                - warning_hours: int
        """
        # Daily briefing
        if preferences.get('daily_briefing', False):
            hour = preferences.get('briefing_time_hour', 8)
            self.event_system.create_daily_briefing(user_id, briefing_time_hour=hour)
            print(f"✅ Set up daily briefing for user {user_id} at {hour}:00")
        
        # Weekly review
        if preferences.get('weekly_review', False):
            day = preferences.get('review_day', 4)  # Default Friday
            hour = preferences.get('review_time_hour', 17)
            self.event_system.create_weekly_review(user_id, day_of_week=day, review_time_hour=hour)
            print(f"✅ Set up weekly review for user {user_id}")
    
    def get_context_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary of all context available for user.
        
        Args:
            user_id: User identifier
        
        Returns:
            dict: Complete context summary
        """
        full_context = self.context_engine.get_full_context(user_id)
        
        # Add AI task status
        try:
            pending_work = ai_check_pending_work()
            full_context['ai_tasks'] = {
                'total_pending': pending_work.get('total_pending', 0),
                'high_priority': pending_work.get('high_priority_count', 0),
                'overdue': pending_work.get('overdue_count', 0)
            }
        except:
            full_context['ai_tasks'] = {'error': 'Unable to load'}
        
        # Add events
        events = self.event_system.get_user_triggers(user_id)
        full_context['upcoming_events'] = len(events)
        
        return full_context


# Singleton instance
context_aware_ai = ContextAwareAI()


def get_context_aware_ai() -> ContextAwareAI:
    """Get singleton context-aware AI instance"""
    return context_aware_ai


# Helper function for agent routes
def enhance_system_prompt_with_context(user_id: str, base_prompt: str,
                                      ip_address: str = None) -> str:
    """
    Quick function to enhance any system prompt with user context.
    
    Args:
        user_id: User identifier from authentication
        base_prompt: Original system prompt
        ip_address: User's IP address
    
    Returns:
        str: Enhanced prompt with full context
    """
    ai = get_context_aware_ai()
    return ai.build_enhanced_system_prompt(user_id, ip_address, base_prompt)
