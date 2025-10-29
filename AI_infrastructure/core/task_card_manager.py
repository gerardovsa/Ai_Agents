"""
Task Card Manager
=================

Creates clean, minimal Google Task cards for Kanban view.
Full details stored in sessions.db, only summary shown in Task.

BEFORE (Too Much Info):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Send test email batch [Session: Email Campaign]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Notes: {
  "session_id": "sess_123...",
  "conversation_summary": "Long text...",
  "tools_used": ["tool1", "tool2"...],
  "created_resources": [{...}, {...}],
  "kanban_column": "in_progress",
  "context": {...},
  ...1000 more characters
}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFTER (Clean & Minimal):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Send test email batch
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Email Campaign
⏱️ Last active: 2h ago
📁 3 docs • 2 steps pending

🔗 sess_20251028_email_camp
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from AI_infrastructure.core.session_database import get_session_db


class TaskCardManager:
    """
    Creates minimal, clean task cards for Google Tasks
    """
    
    def __init__(self):
        self.db = get_session_db()
    
    def create_task_card_content(self, session_id: str) -> Dict[str, str]:
        """
        Create minimal task card content
        
        Returns:
            dict: {'title': '...', 'notes': '...'}
        """
        # Get lightweight summary from database
        summary = self.db.get_session_summary(session_id)
        
        # Build minimal title
        priority_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }.get(summary['priority'], '⚪')
        
        title = f"{priority_emoji} {summary['title']}"
        
        # Build clean notes
        notes = self._format_clean_notes(summary)
        
        return {
            'title': title,
            'notes': notes
        }
    
    def _format_clean_notes(self, summary: Dict) -> str:
        """Format minimal, readable notes"""
        
        # Time since last active
        last_active = datetime.fromisoformat(summary['last_active'])
        time_ago = self._time_ago(last_active)
        
        # Build clean notes
        notes_lines = []
        
        # Project line
        if summary['project_name']:
            notes_lines.append(f"📋 {summary['project_name']}")
        
        # Status line
        status_emoji = {
            'active': '🟢',
            'paused': '⏸️',
            'completed': '✅'
        }.get(summary['status'], '⚪')
        notes_lines.append(f"{status_emoji} {summary['status'].title()} • Last active: {time_ago}")
        
        # Quick stats
        stats = []
        if summary['message_count'] > 0:
            stats.append(f"{summary['message_count']} messages")
        if summary['active_docs'] > 0:
            stats.append(f"{summary['active_docs']} docs")
        if summary['pending_steps'] > 0:
            stats.append(f"{summary['pending_steps']} steps")
        
        if stats:
            notes_lines.append("📊 " + " • ".join(stats))
        
        # Recent activity (last 3)
        if summary['recent_activity']:
            notes_lines.append("")
            notes_lines.append("📝 Recent Activity:")
            for activity in summary['recent_activity'][:3]:
                timestamp = datetime.fromisoformat(activity['timestamp'])
                time_str = self._time_ago(timestamp)
                notes_lines.append(f"  • {activity['description']} ({time_str})")
        
        # Session ID (for linking back to full data)
        notes_lines.append("")
        notes_lines.append(f"🔗 Session: {summary['session_id']}")
        
        # Tags
        if summary['tags']:
            tags = json.loads(summary['tags']) if isinstance(summary['tags'], str) else summary['tags']
            if tags:
                notes_lines.append(f"🏷️ {', '.join(tags)}")
        
        return '\n'.join(notes_lines)
    
    def _time_ago(self, dt: datetime) -> str:
        """Human-readable time ago"""
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        else:
            days = int(seconds / 86400)
            return f"{days}d ago"
    
    def update_task_card(self, session_id: str, google_task_id: str) -> Dict[str, str]:
        """
        Update existing task card with latest info
        
        Returns:
            dict: Updated {'title': '...', 'notes': '...'}
        """
        return self.create_task_card_content(session_id)
    
    def format_kanban_card_preview(self, session_id: str) -> str:
        """
        Format card for terminal/UI display
        
        Returns:
            str: Formatted card text
        """
        summary = self.db.get_session_summary(session_id)
        
        priority_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🔴'
        }.get(summary['priority'], '⚪')
        
        last_active = datetime.fromisoformat(summary['last_active'])
        time_ago = self._time_ago(last_active)
        
        card = f"""
┌─────────────────────────────────────────┐
│ {priority_emoji} {summary['title']:<37} │
├─────────────────────────────────────────┤
│ 📋 {(summary['project_name'] or 'No project'):<38} │
│ ⏱️  Last: {time_ago:<31} │
│ 📊 {summary['message_count']} msgs • {summary['active_docs']} docs • {summary['pending_steps']} steps     │
└─────────────────────────────────────────┘
"""
        return card.strip()


# Example comparison: Full Context vs Clean Card
EXAMPLE_COMPARISON = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPARISON: Full Context (sessions.db) vs Clean Card (Google Tasks)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────────────────────────────────┐
│ FULL CONTEXT (sessions.db) - AI's Memory                           │
└─────────────────────────────────────────────────────────────────────┘

Session ID: sess_20251028_0830_john_email_marketing_campaign
User: john_doe
Title: Email Marketing Campaign
Status: active
Priority: high
Project: Q4 Marketing
Kanban: in_progress
Created: 2025-10-28T08:30:00
Last Active: 2025-10-28T14:45:00

MESSAGES (12 total):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-10-28 08:30:00] User:
"Help me create an email marketing campaign for Q4. We need to reach 
10,000 customers with personalized messages about our new product launch."

[2025-10-28 08:32:15] Assistant:
"I'll help you create a comprehensive email campaign. Let me start by 
creating professional email templates..."
[Tools used: google_docs_smart_create_from_markdown]

[2025-10-28 08:40:22] User:
"These templates look great! Can you make them more personalized?"

[2025-10-28 08:42:10] Assistant:
"Absolutely! I'll add personalization tokens for name, company, and 
purchase history..."

[... 8 more messages with complete conversation ...]

ACTIVITY LOG (50 entries):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2025-10-28 14:45:00] message_added: Assistant message added
[2025-10-28 14:40:00] document_created: Doc created: Customer List Template
[2025-10-28 14:30:00] next_step_added: Next step: Upload customer CSV
[2025-10-28 14:15:00] message_added: User message added
[... 46 more log entries ...]

ACTIVE DOCUMENTS (3):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [Google Doc] Email Templates - Q4 Campaign
   URL: https://docs.google.com/document/d/abc123xyz
   Created: 2025-10-28T08:35:00
   
2. [Google Sheet] Customer Segmentation List
   URL: https://sheets.google.com/spreadsheets/d/xyz789abc
   Created: 2025-10-28T09:15:00
   
3. [Google Doc] Campaign Timeline & Milestones
   URL: https://docs.google.com/document/d/def456ghi
   Created: 2025-10-28T10:30:00

ARCHIVED DOCUMENTS (1):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [Google Doc] Initial Draft (v1)
   Archived: 2025-10-28T09:00:00
   Reason: Superseded by updated version

NEXT STEPS (4 pending):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Review email templates and get feedback
2. Upload customer_list.csv with 10k contacts
3. Send test batch to 10 sample customers
4. Analyze open rates and adjust templates

TAGS: email, marketing, campaign, q4, personalization, bulk_send


┌─────────────────────────────────────────────────────────────────────┐
│ CLEAN CARD (Google Tasks) - User's Kanban View                     │
└─────────────────────────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴 Email Marketing Campaign
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Q4 Marketing
🟢 Active • Last active: 2h ago
📊 12 messages • 3 docs • 4 steps

📝 Recent Activity:
  • Assistant message added (2h ago)
  • Doc created: Customer List Template (3h ago)
  • Next step: Upload customer CSV (4h ago)

🔗 Session: sess_20251028_0830_john_email_marketing_campaign
🏷️ email, marketing, campaign, q4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY DIFFERENCES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FULL CONTEXT (sessions.db):
✅ Complete conversation (every word)
✅ Full activity log (50+ entries)
✅ All document URLs and details
✅ Timestamped events
✅ Searchable, queryable
✅ AI can reference exact messages
✅ No API limits

CLEAN CARD (Google Tasks):
✅ Just the essentials for humans
✅ Quick overview at a glance
✅ Recent activity (last 3)
✅ Summary stats only
✅ Links back to full data via session_id
✅ Clean Kanban visualization
✅ Accessible from any device

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BENEFIT: Best of both worlds!
  • Full data in sessions.db (AI's complete memory)
  • Clean cards in Google Tasks (user-friendly Kanban)
  • Session ID links them together
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def get_task_card_manager() -> TaskCardManager:
    """Get singleton task card manager"""
    return TaskCardManager()
