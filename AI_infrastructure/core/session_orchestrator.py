"""
Session-Aware AI Orchestrator
==============================

Enables AI to:
1. Track conversation sessions with unique IDs
2. Tag tasks with session context
3. Resume conversations by loading session state
4. Proactively notify users about tasks in specific sessions
5. Use Google Tasks as virtual Kanban board

KEY CONCEPTS:
- Session = Complete conversation context (messages, files, work done, state)
- Tasks linked to sessions allow AI to "remember" what it was working on
- AI can activate specific sessions to continue work
- User sees "Continue conversation about X" instead of starting fresh
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI_infrastructure.core.event_triggers import get_event_trigger_system, TriggerType
from google_workspace.ai_personal_tasks import (
    ai_create_task,
    ai_list_my_tasks,
    ai_update_task,
    ai_complete_task
)


@dataclass
class ConversationSession:
    """
    A complete conversation session with all context
    """
    session_id: str
    user_id: str
    created_at: datetime
    last_active: datetime
    status: str  # 'active', 'paused', 'completed'
    
    # Conversation data
    title: str
    summary: str
    messages: List[Dict[str, Any]]  # All messages in session
    
    # Context
    topics: List[str]
    tools_used: List[str]
    files_attached: List[str]  # Paths/URLs to files
    
    # Work produced
    created_resources: List[Dict[str, str]]  # {type: 'doc', url: '...', title: '...'}
    
    # Task tracking
    associated_tasks: List[str]  # Task IDs in Google Tasks
    next_steps: List[str]
    
    # Kanban state
    kanban_column: str  # 'backlog', 'in_progress', 'review', 'done'
    priority: str  # 'low', 'medium', 'high'
    
    # Metadata
    tags: List[str]
    project_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_active'] = self.last_active.isoformat()
        return data
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ConversationSession':
        """Create from dict"""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['last_active'] = datetime.fromisoformat(data['last_active'])
        return ConversationSession(**data)


class SessionOrchestrator:
    """
    AI Orchestrator that manages conversation sessions and proactive task notifications
    """
    
    def __init__(self):
        # Session storage (in production, use database)
        self.sessions: Dict[str, ConversationSession] = {}
        self.user_sessions: Dict[str, List[str]] = defaultdict(list)  # user_id -> [session_ids]
        
        # Kanban columns
        self.kanban_columns = ['backlog', 'in_progress', 'review', 'done']
        
        # Event system for proactive notifications
        self.event_system = get_event_trigger_system()
        
        print("🎯 Session Orchestrator initialized")
    
    def create_session(self, user_id: str, title: str, initial_message: str = "",
                      project_name: str = None, tags: List[str] = None) -> str:
        """
        Create new conversation session
        
        Args:
            user_id: User identifier
            title: Session title (e.g., "Email Marketing Campaign")
            initial_message: First message in conversation
            project_name: Optional project this session belongs to
            tags: Tags for categorization
        
        Returns:
            str: Session ID
        """
        # Generate session ID
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = f"sess_{timestamp}_{user_id[:8]}_{title[:20].replace(' ', '_').lower()}"
        
        # Create session
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.now(),
            last_active=datetime.now(),
            status='active',
            title=title,
            summary=initial_message[:100] if initial_message else "",
            messages=[{'role': 'user', 'content': initial_message, 'timestamp': datetime.now().isoformat()}] if initial_message else [],
            topics=[],
            tools_used=[],
            files_attached=[],
            created_resources=[],
            associated_tasks=[],
            next_steps=[],
            kanban_column='in_progress',
            priority='medium',
            tags=tags or [],
            project_name=project_name
        )
        
        # Store
        self.sessions[session_id] = session
        self.user_sessions[user_id].append(session_id)
        
        print(f" Created session: {session_id}")
        print(f"   Title: {title}")
        print(f"   User: {user_id}")
        
        return session_id
    
    def add_message_to_session(self, session_id: str, role: str, content: str,
                              tools_used: List[str] = None):
        """
        Add message to session
        
        Args:
            session_id: Session to update
            role: 'user' or 'assistant'
            content: Message content
            tools_used: Tools used in this message (if assistant)
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Add message
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        if tools_used:
            message['tools_used'] = tools_used
        
        session.messages.append(message)
        session.last_active = datetime.now()
        
        # Update tools used
        if tools_used:
            session.tools_used.extend([t for t in tools_used if t not in session.tools_used])
        
        print(f"📝 Added {role} message to session {session_id}")
    
    def create_task_for_session(self, session_id: str, task_title: str,
                               due_date: str = None, priority: str = 'medium',
                               next_steps: List[str] = None) -> str:
        """
        Create Google Task linked to this session
        
        Args:
            session_id: Session this task belongs to
            task_title: Task title
            due_date: ISO format due date
            priority: 'low', 'medium', 'high'
            next_steps: List of action items
        
        Returns:
            str: Task ID from Google Tasks
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Build task title with session context
        priority_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(priority, '🟡')
        full_title = f"{priority_emoji} {task_title} [Session: {session.title}]"
        
        # Build notes with complete session context (JSON payload)
        notes_data = {
            'session_id': session_id,
            'session_title': session.title,
            'project_name': session.project_name,
            'conversation_summary': session.summary,
            'tools_used': session.tools_used,
            'created_resources': session.created_resources,
            'kanban_column': session.kanban_column,
            'priority': priority,
            'tags': session.tags,
            'next_steps': next_steps or session.next_steps,
            'last_active': session.last_active.isoformat(),
            'context': {
                'topics': session.topics,
                'files_attached': session.files_attached,
                'messages_count': len(session.messages)
            }
        }
        
        notes_json = json.dumps(notes_data, indent=2)
        
        # Create task in Google Tasks
        result = ai_create_task(
            title=full_title,
            notes=notes_json,
            due_date=due_date,
            priority=priority
        )
        
        if result.get('success'):
            task_id = result['task']['id']
            
            # Link task to session
            session.associated_tasks.append(task_id)
            
            # Update next steps
            if next_steps:
                session.next_steps = next_steps
            
            print(f" Created task for session {session_id}")
            print(f"   Task: {task_title}")
            print(f"   Task ID: {task_id}")
            print(f"   Due: {due_date or 'No deadline'}")
            
            # Create deadline trigger for proactive notification
            if due_date:
                self._create_session_notification_trigger(
                    session_id=session_id,
                    task_id=task_id,
                    task_title=task_title,
                    deadline=datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                )
            
            return task_id
        else:
            raise Exception(f"Failed to create task: {result.get('error')}")
    
    def _create_session_notification_trigger(self, session_id: str, task_id: str,
                                            task_title: str, deadline: datetime):
        """
        Create trigger to notify user about task in specific session
        
        This is the KEY feature - AI can proactively reach out about tasks
        """
        session = self.sessions[session_id]
        
        # Create deadline trigger (24 hours before)
        trigger_id = self.event_system.create_deadline_trigger(
            user_id=session.user_id,
            task_id=task_id,
            task_title=f"{task_title} (Session: {session.title})",
            deadline=deadline,
            warning_hours=24
        )
        
        print(f"⏰ Set up session notification trigger: {trigger_id}")
        print(f"   Will notify user 24 hours before: {deadline}")
        print(f"   Session: {session.title}")
        print(f"   User can click to resume conversation in context")
    
    def get_session_resume_prompt(self, session_id: str) -> str:
        """
        Generate prompt to resume conversation in this session
        
        This is what AI receives when activating a session
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Build comprehensive context
        prompt = f"""
🔄 **RESUMING CONVERSATION SESSION**

**Session:** {session.title}
**Session ID:** {session_id}
**Status:** {session.status}
**Priority:** {session.priority.upper()}
**Started:** {session.created_at.strftime('%Y-%m-%d %H:%M')}
**Last Active:** {session.last_active.strftime('%Y-%m-%d %H:%M')}

**Project:** {session.project_name or 'N/A'}
**Tags:** {', '.join(session.tags) if session.tags else 'None'}

---

**📋 CONVERSATION SUMMARY:**
{session.summary}

**🔧 TOOLS USED:**
{', '.join(session.tools_used) if session.tools_used else 'None'}

**📁 FILES IN SESSION:**
{', '.join(session.files_attached) if session.files_attached else 'None'}

**📄 CREATED RESOURCES:**
"""
        
        # Add created resources
        if session.created_resources:
            for resource in session.created_resources:
                prompt += f"\n- {resource['type'].title()}: [{resource['title']}]({resource['url']})"
        else:
            prompt += "\nNone"
        
        # Add next steps
        prompt += f"""

**📝 NEXT STEPS:**
"""
        if session.next_steps:
            for i, step in enumerate(session.next_steps, 1):
                prompt += f"\n{i}. {step}"
        else:
            prompt += "\nNo pending steps"
        
        # Add recent messages (last 5)
        prompt += f"""

**💬 RECENT CONVERSATION ({min(5, len(session.messages))} most recent):**
"""
        for msg in session.messages[-5:]:
            role_emoji = '👤' if msg['role'] == 'user' else '🤖'
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M')
            content_preview = msg['content'][:100] + ('...' if len(msg['content']) > 100 else '')
            prompt += f"\n{role_emoji} [{timestamp}] {content_preview}"
        
        # Add instructions
        prompt += f"""

---

**🎯 YOUR ROLE:**
1. Review the session context above
2. Reference previous work and conversation
3. Continue exactly where the conversation left off
4. User should feel like this is a continuous conversation, not a new AI
5. If there are next steps, offer to continue working on them

**⚠️ IMPORTANT:**
- You have FULL CONTEXT of this conversation
- You created the resources listed above
- The user expects you to remember everything from this session
- Be proactive about completing the next steps

**Start your response naturally, showing you remember the context.**
Example: "I'm back to continue our work on {session.title}. Last time, we {session.summary[:50]}... Let's pick up where we left off!"
"""
        
        return prompt.strip()
    
    def get_session_notification_message(self, session_id: str, task_title: str,
                                        deadline: datetime) -> Dict[str, Any]:
        """
        Generate notification message for user about task in session
        
        This is what user sees when AI proactively reaches out
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        # Calculate time until deadline
        time_until = deadline - datetime.now()
        hours_until = int(time_until.total_seconds() / 3600)
        
        return {
            'type': 'session_task_notification',
            'session_id': session_id,
            'session_title': session.title,
            'task_title': task_title,
            'deadline': deadline.isoformat(),
            'hours_until_deadline': hours_until,
            'priority': session.priority,
            'message': f"""
⏰ **Task Reminder: {task_title}**

You have a task due in **{hours_until} hours** in your session:
**"{session.title}"**

**Next Steps:**
{chr(10).join(f'• {step}' for step in session.next_steps) if session.next_steps else '• Review and complete task'}

**Resources Created:**
{chr(10).join(f'• {r["title"]}' for r in session.created_resources) if session.created_resources else '• None'}

📱 **Click to resume conversation and continue working on this task**
""",
            'action': {
                'type': 'resume_session',
                'session_id': session_id,
                'button_text': f'Resume "{session.title}" →'
            }
        }
    
    def get_kanban_board(self, user_id: str) -> Dict[str, List[ConversationSession]]:
        """
        Get user's sessions organized as Kanban board
        
        Returns:
            dict: {column_name: [sessions]}
        """
        board = {column: [] for column in self.kanban_columns}
        
        user_session_ids = self.user_sessions.get(user_id, [])
        
        for session_id in user_session_ids:
            session = self.sessions.get(session_id)
            if session and session.status != 'completed':
                column = session.kanban_column
                if column in board:
                    board[column].append(session)
        
        return board
    
    def move_session_to_column(self, session_id: str, target_column: str):
        """
        Move session to different Kanban column
        
        Args:
            session_id: Session to move
            target_column: 'backlog', 'in_progress', 'review', 'done'
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if target_column not in self.kanban_columns:
            raise ValueError(f"Invalid column: {target_column}")
        
        session = self.sessions[session_id]
        old_column = session.kanban_column
        session.kanban_column = target_column
        
        # If moving to 'done', mark as completed
        if target_column == 'done':
            session.status = 'completed'
            
            # Complete all associated tasks
            for task_id in session.associated_tasks:
                try:
                    ai_complete_task(
                        task_id=task_id,
                        completion_notes=f"Session '{session.title}' completed"
                    )
                except:
                    pass  # Task may already be completed
        
        print(f"📊 Moved session from '{old_column}' → '{target_column}'")
        print(f"   Session: {session.title}")
    
    def get_active_sessions(self, user_id: str, limit: int = 10) -> List[ConversationSession]:
        """
        Get user's active sessions (most recent first)
        """
        user_session_ids = self.user_sessions.get(user_id, [])
        
        active_sessions = [
            self.sessions[sid] for sid in user_session_ids
            if sid in self.sessions and self.sessions[sid].status == 'active'
        ]
        
        # Sort by last active
        active_sessions.sort(key=lambda s: s.last_active, reverse=True)
        
        return active_sessions[:limit]
    
    def search_sessions(self, user_id: str, query: str = None,
                       tags: List[str] = None, project_name: str = None) -> List[ConversationSession]:
        """
        Search user's sessions
        """
        user_session_ids = self.user_sessions.get(user_id, [])
        results = []
        
        for session_id in user_session_ids:
            session = self.sessions.get(session_id)
            if not session:
                continue
            
            # Query match
            if query and query.lower() not in session.title.lower() and query.lower() not in session.summary.lower():
                continue
            
            # Tags match
            if tags and not any(tag in session.tags for tag in tags):
                continue
            
            # Project match
            if project_name and session.project_name != project_name:
                continue
            
            results.append(session)
        
        return results


# Singleton instance
session_orchestrator = SessionOrchestrator()


def get_session_orchestrator() -> SessionOrchestrator:
    """Get singleton session orchestrator instance"""
    return session_orchestrator
