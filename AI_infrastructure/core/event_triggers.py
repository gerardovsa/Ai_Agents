"""
Event-Driven AI Activation System
==================================

Enables AI to be proactively activated based on:
- Pending deadlines approaching
- Scheduled reminders
- Task status changes
- Time-based triggers (daily briefings, weekly reviews)
- External events (emails received, calendar invites, etc.)

The AI can initiate conversations autonomously when events occur.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TriggerType(Enum):
    """Types of events that can activate AI"""
    DEADLINE_APPROACHING = "deadline_approaching"
    TASK_OVERDUE = "task_overdue"
    SCHEDULED_REMINDER = "scheduled_reminder"
    DAILY_BRIEFING = "daily_briefing"
    WEEKLY_REVIEW = "weekly_review"
    CALENDAR_EVENT = "calendar_event"
    EMAIL_RECEIVED = "email_received"
    TASK_COMPLETED = "task_completed"
    PROJECT_MILESTONE = "project_milestone"
    CUSTOM = "custom"


@dataclass
class EventTrigger:
    """Represents an event that can activate the AI"""
    trigger_id: str
    trigger_type: TriggerType
    user_id: str
    scheduled_time: datetime
    condition: Optional[Callable] = None  # Function that returns True when trigger should fire
    payload: Optional[Dict[str, Any]] = None  # Additional data for AI context
    recurring: bool = False
    recurrence_pattern: Optional[str] = None  # "daily", "weekly", "monthly"
    activated: bool = False
    last_fired: Optional[datetime] = None


class EventTriggerSystem:
    """
    Monitors events and activates AI when conditions are met.
    
    Example use cases:
    - "Remind me tomorrow at 9am to review the document"
    - "Send me a weekly summary every Friday at 5pm"
    - "Alert me when task X is 1 day overdue"
    - "Give me a morning briefing every work day at 8am"
    """
    
    def __init__(self):
        self.triggers = {}  # trigger_id -> EventTrigger
        self.user_triggers = defaultdict(list)  # user_id -> [trigger_ids]
        self.callbacks = []  # Functions to call when AI should be activated
        
    def create_deadline_trigger(self, user_id: str, task_id: str, task_title: str,
                                deadline: datetime, warning_hours: int = 24) -> str:
        """
        Create trigger that fires when deadline is approaching.
        
        Args:
            user_id: User to notify
            task_id: Task identifier
            task_title: Task name
            deadline: Deadline datetime
            warning_hours: Hours before deadline to trigger (default: 24)
        
        Returns:
            str: Trigger ID
        """
        trigger_time = deadline - timedelta(hours=warning_hours)
        
        trigger = EventTrigger(
            trigger_id=f"deadline_{task_id}_{int(datetime.now().timestamp())}",
            trigger_type=TriggerType.DEADLINE_APPROACHING,
            user_id=user_id,
            scheduled_time=trigger_time,
            payload={
                'task_id': task_id,
                'task_title': task_title,
                'deadline': deadline.isoformat(),
                'hours_until_deadline': warning_hours,
                'message': f"⏰ Reminder: '{task_title}' is due in {warning_hours} hours"
            }
        )
        
        return self._register_trigger(trigger)
    
    def create_overdue_trigger(self, user_id: str, task_id: str, task_title: str,
                               deadline: datetime) -> str:
        """
        Create trigger that fires when task becomes overdue.
        
        Args:
            user_id: User to notify
            task_id: Task identifier
            task_title: Task name
            deadline: Original deadline
        
        Returns:
            str: Trigger ID
        """
        trigger = EventTrigger(
            trigger_id=f"overdue_{task_id}_{int(datetime.now().timestamp())}",
            trigger_type=TriggerType.TASK_OVERDUE,
            user_id=user_id,
            scheduled_time=deadline,
            payload={
                'task_id': task_id,
                'task_title': task_title,
                'deadline': deadline.isoformat(),
                'message': f"🚨 Task overdue: '{task_title}' was due at {deadline.strftime('%Y-%m-%d %H:%M')}"
            }
        )
        
        return self._register_trigger(trigger)
    
    def create_reminder(self, user_id: str, reminder_time: datetime, message: str,
                       recurring: bool = False, recurrence: str = None) -> str:
        """
        Create scheduled reminder.
        
        Args:
            user_id: User to notify
            reminder_time: When to trigger
            message: Reminder message
            recurring: Whether reminder repeats
            recurrence: "daily", "weekly", "monthly"
        
        Returns:
            str: Trigger ID
        
        Example:
            create_reminder(
                user_id="user_123",
                reminder_time=datetime(2025, 10, 30, 9, 0),
                message="Review weekly goals",
                recurring=True,
                recurrence="weekly"
            )
        """
        trigger = EventTrigger(
            trigger_id=f"reminder_{int(datetime.now().timestamp())}",
            trigger_type=TriggerType.SCHEDULED_REMINDER,
            user_id=user_id,
            scheduled_time=reminder_time,
            recurring=recurring,
            recurrence_pattern=recurrence,
            payload={
                'message': message,
                'created_at': datetime.now().isoformat()
            }
        )
        
        return self._register_trigger(trigger)
    
    def create_daily_briefing(self, user_id: str, briefing_time_hour: int = 8,
                             briefing_time_minute: int = 0) -> str:
        """
        Create daily briefing trigger (e.g., 8am every work day).
        
        Args:
            user_id: User to notify
            briefing_time_hour: Hour to trigger (0-23)
            briefing_time_minute: Minute to trigger (0-59)
        
        Returns:
            str: Trigger ID
        """
        # Calculate next briefing time
        now = datetime.now()
        next_briefing = now.replace(hour=briefing_time_hour, minute=briefing_time_minute, second=0, microsecond=0)
        
        if next_briefing <= now:
            next_briefing += timedelta(days=1)
        
        trigger = EventTrigger(
            trigger_id=f"daily_briefing_{user_id}",
            trigger_type=TriggerType.DAILY_BRIEFING,
            user_id=user_id,
            scheduled_time=next_briefing,
            recurring=True,
            recurrence_pattern="daily",
            payload={
                'briefing_type': 'daily',
                'message': '📰 Good morning! Here\'s your daily briefing...'
            }
        )
        
        return self._register_trigger(trigger)
    
    def create_weekly_review(self, user_id: str, day_of_week: int = 4,  # Friday
                            review_time_hour: int = 17) -> str:
        """
        Create weekly review trigger (e.g., Friday 5pm).
        
        Args:
            user_id: User to notify
            day_of_week: Day (0=Monday, 6=Sunday)
            review_time_hour: Hour to trigger
        
        Returns:
            str: Trigger ID
        """
        # Calculate next review time
        now = datetime.now()
        days_ahead = day_of_week - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        
        next_review = now + timedelta(days=days_ahead)
        next_review = next_review.replace(hour=review_time_hour, minute=0, second=0, microsecond=0)
        
        trigger = EventTrigger(
            trigger_id=f"weekly_review_{user_id}",
            trigger_type=TriggerType.WEEKLY_REVIEW,
            user_id=user_id,
            scheduled_time=next_review,
            recurring=True,
            recurrence_pattern="weekly",
            payload={
                'review_type': 'weekly',
                'message': '📊 Weekly review: Let\'s summarize this week\'s accomplishments...'
            }
        )
        
        return self._register_trigger(trigger)
    
    def create_custom_trigger(self, user_id: str, trigger_time: datetime,
                             trigger_name: str, custom_payload: Dict[str, Any]) -> str:
        """
        Create custom trigger with arbitrary payload.
        
        Args:
            user_id: User to notify
            trigger_time: When to trigger
            trigger_name: Name/description
            custom_payload: Custom data for AI
        
        Returns:
            str: Trigger ID
        """
        trigger = EventTrigger(
            trigger_id=f"custom_{int(datetime.now().timestamp())}",
            trigger_type=TriggerType.CUSTOM,
            user_id=user_id,
            scheduled_time=trigger_time,
            payload={
                'name': trigger_name,
                **custom_payload
            }
        )
        
        return self._register_trigger(trigger)
    
    def _register_trigger(self, trigger: EventTrigger) -> str:
        """Register trigger in system"""
        self.triggers[trigger.trigger_id] = trigger
        self.user_triggers[trigger.user_id].append(trigger.trigger_id)
        return trigger.trigger_id
    
    def check_triggers(self) -> List[EventTrigger]:
        """
        Check all triggers and return those that should fire now.
        
        Returns:
            list: Triggers that should activate AI
        """
        now = datetime.now()
        triggers_to_fire = []
        
        for trigger_id, trigger in list(self.triggers.items()):
            if trigger.activated:
                continue
            
            # Check if scheduled time has passed
            if trigger.scheduled_time <= now:
                # Check condition if provided
                if trigger.condition is None or trigger.condition():
                    triggers_to_fire.append(trigger)
                    
                    # Handle recurring triggers
                    if trigger.recurring:
                        self._reschedule_trigger(trigger)
                    else:
                        trigger.activated = True
                    
                    trigger.last_fired = now
        
        return triggers_to_fire
    
    def _reschedule_trigger(self, trigger: EventTrigger):
        """Reschedule recurring trigger for next occurrence"""
        if trigger.recurrence_pattern == "daily":
            trigger.scheduled_time += timedelta(days=1)
        elif trigger.recurrence_pattern == "weekly":
            trigger.scheduled_time += timedelta(weeks=1)
        elif trigger.recurrence_pattern == "monthly":
            # Add one month (approximate)
            trigger.scheduled_time += timedelta(days=30)
    
    def get_user_triggers(self, user_id: str, active_only: bool = True) -> List[EventTrigger]:
        """
        Get all triggers for a user.
        
        Args:
            user_id: User identifier
            active_only: Only return non-activated triggers
        
        Returns:
            list: User's triggers
        """
        trigger_ids = self.user_triggers.get(user_id, [])
        triggers = [self.triggers[tid] for tid in trigger_ids if tid in self.triggers]
        
        if active_only:
            triggers = [t for t in triggers if not t.activated]
        
        return triggers
    
    def cancel_trigger(self, trigger_id: str) -> bool:
        """
        Cancel a trigger.
        
        Args:
            trigger_id: Trigger to cancel
        
        Returns:
            bool: Success
        """
        if trigger_id in self.triggers:
            trigger = self.triggers[trigger_id]
            trigger.activated = True  # Mark as activated to prevent firing
            return True
        return False
    
    def register_callback(self, callback: Callable):
        """
        Register callback function to call when AI should be activated.
        
        Args:
            callback: Function(trigger: EventTrigger) -> None
        
        Example:
            def activate_ai(trigger):
                print(f"AI activated for user {trigger.user_id}")
                # Start AI conversation with context from trigger.payload
            
            event_system.register_callback(activate_ai)
        """
        self.callbacks.append(callback)
    
    async def run_monitor_loop(self, check_interval_seconds: int = 60):
        """
        Run continuous monitoring loop (for background service).
        
        Args:
            check_interval_seconds: How often to check triggers
        """
        print(f"🚀 Event trigger monitor started (checking every {check_interval_seconds}s)")
        
        while True:
            triggered = self.check_triggers()
            
            for trigger in triggered:
                print(f"⚡ Trigger fired: {trigger.trigger_type.value} for user {trigger.user_id}")
                
                # Call all registered callbacks
                for callback in self.callbacks:
                    try:
                        callback(trigger)
                    except Exception as e:
                        print(f" Callback error: {e}")
            
            await asyncio.sleep(check_interval_seconds)
    
    def generate_ai_activation_prompt(self, trigger: EventTrigger) -> str:
        """
        Generate prompt for AI when activated by trigger.
        
        Args:
            trigger: The event that activated AI
        
        Returns:
            str: Prompt to send to AI
        """
        payload = trigger.payload or {}
        
        if trigger.trigger_type == TriggerType.DEADLINE_APPROACHING:
            return f"""
You have been proactively activated due to an upcoming deadline.

**Event:** Deadline Approaching
**Task:** {payload.get('task_title', 'Unknown')}
**Deadline:** {payload.get('deadline', 'Unknown')}
**Time until deadline:** {payload.get('hours_until_deadline', 'Unknown')} hours

**Your role:**
1. Check if task is completed (use ai_list_my_tasks)
2. If not complete, remind user and offer to help
3. Ask if user needs assistance completing the task
4. Update task with reminder sent

**Start your message:**
{payload.get('message', 'Deadline reminder')}
"""
        
        elif trigger.trigger_type == TriggerType.DAILY_BRIEFING:
            return """
You have been activated for the user's daily briefing.

**Event:** Daily Briefing
**Time:** Morning briefing

**Your role:**
1. Check pending work (use ai_check_pending_work)
2. Review today's tasks and deadlines
3. Summarize high-priority items
4. Provide encouraging start-of-day message

**Start your message:**
📰 Good morning! Here's your daily briefing...
"""
        
        elif trigger.trigger_type == TriggerType.WEEKLY_REVIEW:
            return """
You have been activated for the user's weekly review.

**Event:** Weekly Review
**Time:** End of week

**Your role:**
1. Summarize tasks completed this week
2. Review any overdue items
3. Preview next week's priorities
4. Provide accomplishment summary

**Start your message:**
📊 Weekly review: Let's look at this week's progress...
"""
        
        elif trigger.trigger_type == TriggerType.TASK_OVERDUE:
            return f"""
You have been activated because a task is now overdue.

**Event:** Task Overdue
**Task:** {payload.get('task_title', 'Unknown')}
**Was due:** {payload.get('deadline', 'Unknown')}

**Your role:**
1. Alert user about overdue task
2. Ask if task is still relevant
3. Offer to help complete it
4. Suggest rescheduling if needed

**Start your message:**
{payload.get('message', 'Task overdue notification')}
"""
        
        elif trigger.trigger_type == TriggerType.SCHEDULED_REMINDER:
            return f"""
You have been activated for a scheduled reminder.

**Event:** Reminder
**Message:** {payload.get('message', 'Reminder notification')}

**Your role:**
1. Deliver the reminder message
2. Check if user needs any assistance
3. Update reminder status

**Start your message:**
⏰ Reminder: {payload.get('message', 'Scheduled reminder')}
"""
        
        else:
            return f"""
You have been activated by a custom event.

**Event Type:** {trigger.trigger_type.value}
**Payload:** {payload}

**Your role:**
Assess the event and respond appropriately based on the context provided.
"""


# Singleton instance
event_trigger_system = EventTriggerSystem()


def get_event_trigger_system() -> EventTriggerSystem:
    """Get singleton event trigger system instance"""
    return event_trigger_system


# Example usage
if __name__ == "__main__":
    import asyncio
    
    system = get_event_trigger_system()
    
    # Create example triggers
    system.create_deadline_trigger(
        user_id="user_123",
        task_id="task_001",
        task_title="Complete project proposal",
        deadline=datetime.now() + timedelta(hours=25),
        warning_hours=24
    )
    
    system.create_daily_briefing("user_123", briefing_time_hour=8)
    
    system.create_weekly_review("user_123", day_of_week=4, review_time_hour=17)
    
    # Register callback
    def on_trigger(trigger):
        print(f"\n{'='*60}")
        print(f"🤖 AI ACTIVATED!")
        print(f"User: {trigger.user_id}")
        print(f"Event: {trigger.trigger_type.value}")
        print(f"\nPrompt to send to AI:")
        print(system.generate_ai_activation_prompt(trigger))
        print(f"{'='*60}\n")
    
    system.register_callback(on_trigger)
    
    # Run monitor (in production, this would run as background service)
    print("Testing event trigger system...")
    print(f"Active triggers: {len(system.triggers)}")
    
    # Check triggers once
    triggered = system.check_triggers()
    print(f"Triggers fired: {len(triggered)}")
