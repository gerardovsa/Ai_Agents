"""
Kanban ↔ Google Tasks Bidirectional Sync Manager

Handles synchronization between:
- Kanban board (frontend UI)
- sessions.db (source of truth)
- Google Tasks (mobile/web access)
- Google Calendar (auto-generated events)

Sync Rules:
1. sessions.db is ALWAYS source of truth
2. Kanban updates → sessions.db → Google Tasks → Google Calendar
3. Google Tasks updates → sessions.db → Kanban Board (via WebSocket)
4. Conflicts resolved by "last write wins" with timestamp
"""

from datetime import datetime
import json
from typing import Dict, List, Optional, Any
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KanbanSyncManager:
    """Bidirectional sync between Kanban, Google Tasks, and Calendar"""
    
    def __init__(self):
        """Initialize sync manager with required dependencies"""
        # Import here to avoid circular dependencies
        from AI_infrastructure.core.session_database import get_session_db
        from AI_infrastructure.core.task_card_manager import get_task_card_manager
        
        self.db = get_session_db()
        self.card_mgr = get_task_card_manager()
        
        # Google Tasks and Calendar managers will be initialized lazily
        self._tasks_mgr = None
        self._calendar_mgr = None
        
        logger.info("🔄 KanbanSyncManager initialized")
    
    @property
    def tasks(self):
        """Lazy load Google Tasks manager"""
        if self._tasks_mgr is None:
            try:
                from google_workspace.ai_personal_tasks import (
                    ai_create_task,
                    ai_update_task,
                    ai_complete_task,
                    ai_get_task
                )
                self._tasks_mgr = {
                    'create': ai_create_task,
                    'update': ai_update_task,
                    'complete': ai_complete_task,
                    'get': ai_get_task
                }
                logger.info(" Google Tasks manager loaded")
            except ImportError as e:
                logger.error(f" Failed to load Google Tasks: {e}")
                self._tasks_mgr = None
        return self._tasks_mgr
    
    @property
    def calendar(self):
        """Lazy load Google Calendar manager"""
        if self._calendar_mgr is None:
            try:
                # TODO: Implement Google Calendar integration
                # For now, return mock
                logger.warning("⚠️ Google Calendar integration not yet implemented")
                self._calendar_mgr = None
            except ImportError as e:
                logger.error(f" Failed to load Google Calendar: {e}")
                self._calendar_mgr = None
        return self._calendar_mgr
    
    # ═══════════════════════════════════════════════════════════
    # KANBAN → DATABASE → GOOGLE (User drags card)
    # ═══════════════════════════════════════════════════════════
    
    def sync_kanban_move(
        self, 
        session_id: str, 
        new_column: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        User dragged card in Kanban board
        Flow: Kanban → sessions.db → Google Tasks → Google Calendar
        
        Args:
            session_id: Session identifier
            new_column: New kanban column (backlog/in_progress/review/done)
            user_id: User who made the change
            
        Returns:
            Dict with sync results
        """
        logger.info(f"🔄 Syncing Kanban move: {session_id} → {new_column}")
        
        try:
            # 1. Update database (source of truth)
            self.db.update_session_column(session_id, new_column)
            logger.info(f" Updated database: {session_id} → {new_column}")
            
            # 2. Get session data
            session = self.db.get_session(session_id)
            google_task_id = session.get('google_task_id')
            
            if not google_task_id:
                logger.warning(f"⚠️ No Google Task linked for session {session_id}")
                return {
                    'success': True, 
                    'synced_to': ['database'],
                    'warning': 'No Google Task linked'
                }
            
            # 3. Update Google Task status
            if self.tasks:
                if new_column == 'done':
                    # Mark task as completed
                    result = self.tasks['complete'](google_task_id)
                    if result.get('success'):
                        logger.info(f" Marked Google Task as completed")
                    else:
                        logger.error(f" Failed to complete Google Task: {result.get('error')}")
                else:
                    # Update task (reopen if needed)
                    # Note: Google Tasks API doesn't have explicit "reopen"
                    # We update the status to 'needsAction'
                    pass
            
            # 4. Update task card content with latest info
            if self.tasks:
                card = self.card_mgr.create_task_card_content(session_id)
                self.tasks['update'](
                    task_id=google_task_id,
                    title=card['title'],
                    notes=card['notes']
                )
                logger.info(f" Updated Google Task card content")
            
            # 5. Update last_synced timestamp
            self._update_sync_timestamp(session_id)
            
            # 6. Sync to Calendar if applicable
            calendar_result = None
            if session.get('due_date'):
                calendar_result = self.sync_to_calendar(session_id)
            
            logger.info(f" Sync complete: Kanban → Database → Google Tasks")
            
            return {
                'success': True, 
                'synced_to': ['database', 'google_tasks'],
                'calendar_synced': calendar_result is not None
            }
            
        except Exception as e:
            logger.error(f" Sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ═══════════════════════════════════════════════════════════
    # GOOGLE → DATABASE → KANBAN (User checks off in app)
    # ═══════════════════════════════════════════════════════════
    
    def sync_google_task_update(self, google_task_id: str) -> Dict[str, Any]:
        """
        User updated task in Google Tasks app
        Flow: Google Tasks → sessions.db → Kanban Board (via WebSocket)
        
        Args:
            google_task_id: Google Task identifier
            
        Returns:
            Dict with sync results and session_id for WebSocket push
        """
        logger.info(f"🔄 Syncing Google Task update: {google_task_id}")
        
        try:
            # 1. Get task from Google
            if not self.tasks:
                return {'success': False, 'error': 'Google Tasks not available'}
            
            task_result = self.tasks['get'](google_task_id)
            if not task_result.get('success'):
                return {'success': False, 'error': 'Task not found'}
            
            task = task_result.get('task', {})
            
            # 2. Find session by google_task_id
            session_id = self._find_session_by_task_id(google_task_id)
            if not session_id:
                logger.warning(f"⚠️ No session found for task {google_task_id}")
                return {'success': False, 'error': 'session_not_found'}
            
            # 3. Update database based on task status
            task_status = task.get('status', 'needsAction')
            
            if task_status == 'completed':
                # Move to done column
                self.db.update_session_column(session_id, 'done')
                # TODO: Add update_session_status method to database
                logger.info(f" Moved session to 'done' column")
                
            elif task_status == 'needsAction':
                # Ensure not in done column
                session = self.db.get_session(session_id)
                if session.get('kanban_column') == 'done':
                    self.db.update_session_column(session_id, 'in_progress')
                    logger.info(f"🔄 Moved session back to 'in_progress'")
            
            # 4. Update due date if changed
            if 'due' in task and task['due']:
                # TODO: Add update_session_due_date method to database
                pass
            
            # 5. Update last_synced timestamp
            self._update_sync_timestamp(session_id)
            
            logger.info(f" Sync complete: Google Tasks → Database → Kanban")
            
            return {
                'success': True, 
                'session_id': session_id, 
                'synced_to': ['database', 'kanban'],
                'session': self.db.get_session(session_id)  # For WebSocket push
            }
            
        except Exception as e:
            logger.error(f" Sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ═══════════════════════════════════════════════════════════
    # GOOGLE CALENDAR INTEGRATION (Auto-create events)
    # ═══════════════════════════════════════════════════════════
    
    def sync_to_calendar(self, session_id: str) -> Dict[str, Any]:
        """
        Create/update Google Calendar event from session
        Auto-triggered when due date is set
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with calendar event details
        """
        logger.info(f"📅 Syncing to Google Calendar: {session_id}")
        
        try:
            session = self.db.get_session(session_id)
            
            # Only create calendar event if due date exists
            if not session.get('due_date'):
                logger.info(f"⏭️ No due date, skipping calendar sync")
                return {'success': False, 'reason': 'no_due_date'}
            
            # TODO: Implement Google Calendar integration
            logger.warning("⚠️ Google Calendar integration not yet implemented")
            
            return {
                'success': False,
                'reason': 'not_implemented',
                'message': 'Google Calendar integration coming soon'
            }
            
        except Exception as e:
            logger.error(f" Calendar sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ═══════════════════════════════════════════════════════════
    # BULK SYNC (Initial load or refresh)
    # ═══════════════════════════════════════════════════════════
    
    def sync_all_sessions(self, user_id: str) -> Dict[str, Any]:
        """
        Sync all sessions for a user (initial load or full refresh)
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with sync results
        """
        logger.info(f"🔄 Starting bulk sync for user: {user_id}")
        
        try:
            # Get all active sessions from database
            sessions = self.db.get_user_sessions(user_id, status='active')
            
            synced = []
            errors = []
            
            for session in sessions:
                try:
                    session_id = session['session_id']
                    
                    # Sync to Google Tasks
                    if session.get('google_task_id'):
                        # Update existing task
                        if self.tasks:
                            card = self.card_mgr.create_task_card_content(session_id)
                            self.tasks['update'](
                                task_id=session['google_task_id'],
                                title=card['title'],
                                notes=card['notes']
                            )
                    else:
                        # Create new task
                        result = self.create_google_task_for_session(session_id)
                        if result.get('success'):
                            session['google_task_id'] = result['task_id']
                    
                    # Sync to Calendar if due date exists
                    if session.get('due_date'):
                        self.sync_to_calendar(session_id)
                    
                    synced.append(session_id)
                    
                except Exception as e:
                    logger.error(f" Error syncing {session.get('session_id')}: {e}")
                    errors.append({
                        'session_id': session.get('session_id'),
                        'error': str(e)
                    })
            
            logger.info(f" Bulk sync complete: {len(synced)} synced, {len(errors)} errors")
            
            return {
                'success': True,
                'synced': synced,
                'errors': errors,
                'total': len(sessions)
            }
            
        except Exception as e:
            logger.error(f" Bulk sync failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ═══════════════════════════════════════════════════════════
    # CONFLICT RESOLUTION
    # ═══════════════════════════════════════════════════════════
    
    def resolve_sync_conflict(self, session_id: str) -> Dict[str, Any]:
        """
        Handle case where Kanban and Google Tasks are out of sync
        Rule: Last write wins (check timestamps)
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict with resolution results
        """
        logger.info(f"🔄 Resolving sync conflict for: {session_id}")
        
        try:
            session = self.db.get_session(session_id)
            google_task_id = session.get('google_task_id')
            
            if not google_task_id or not self.tasks:
                return {'success': False, 'error': 'Cannot resolve conflict'}
            
            # Get task from Google
            task_result = self.tasks['get'](google_task_id)
            if not task_result.get('success'):
                return {'success': False, 'error': 'Task not found'}
            
            task = task_result.get('task', {})
            
            # Compare timestamps
            db_timestamp = datetime.fromisoformat(session.get('last_synced_at', '2000-01-01'))
            google_timestamp = datetime.fromisoformat(task.get('updated', '2000-01-01'))
            
            if google_timestamp > db_timestamp:
                # Google Tasks is newer, sync FROM Google
                logger.info(f"🔄 Conflict: Google Tasks is newer, syncing FROM Google")
                return self.sync_google_task_update(google_task_id)
            else:
                # Database is newer, sync TO Google
                logger.info(f"🔄 Conflict: Database is newer, syncing TO Google")
                return self.sync_kanban_move(
                    session_id,
                    session.get('kanban_column', 'in_progress'),
                    session.get('user_id')
                )
                
        except Exception as e:
            logger.error(f" Conflict resolution failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ═══════════════════════════════════════════════════════════
    # HELPER METHODS
    # ═══════════════════════════════════════════════════════════
    
    def create_google_task_for_session(
        self, 
        session_id: str,
        due_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new Google Task from session
        
        Args:
            session_id: Session identifier
            due_date: Optional due date (ISO format)
            
        Returns:
            Dict with task creation results
        """
        logger.info(f"📝 Creating Google Task for session: {session_id}")
        
        try:
            if not self.tasks:
                return {'success': False, 'error': 'Google Tasks not available'}
            
            # Generate clean card content
            card = self.card_mgr.create_task_card_content(session_id)
            session = self.db.get_session(session_id)
            
            # Create task
            result = self.tasks['create'](
                title=card['title'],
                notes=card['notes'],
                due_date=due_date or session.get('due_date')
            )
            
            if result.get('success'):
                task_id = result.get('task', {}).get('id')
                
                # Link in database
                self.db.link_google_task(session_id, task_id)
                
                logger.info(f" Created Google Task: {task_id}")
                
                return {
                    'success': True,
                    'task_id': task_id,
                    'task': result.get('task')
                }
            else:
                logger.error(f" Failed to create task: {result.get('error')}")
                return result
                
        except Exception as e:
            logger.error(f" Task creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_session_by_task_id(self, google_task_id: str) -> Optional[str]:
        """
        Find session_id from google_task_id
        
        Args:
            google_task_id: Google Task identifier
            
        Returns:
            session_id or None
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT session_id FROM sessions 
                    WHERE google_task_id = ?
                """, (google_task_id,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f" Failed to find session: {e}")
            return None
    
    def _update_sync_timestamp(self, session_id: str):
        """
        Update last_synced_at timestamp
        
        Args:
            session_id: Session identifier
        """
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions 
                    SET last_synced_at = ? 
                    WHERE session_id = ?
                """, (datetime.now().isoformat(), session_id))
                conn.commit()
        except Exception as e:
            logger.error(f" Failed to update sync timestamp: {e}")
    
    def _build_calendar_description(self, session: Dict[str, Any]) -> str:
        """
        Build description for calendar event
        
        Args:
            session: Session data dict
            
        Returns:
            Formatted description string
        """
        return f"""
📋 Project: {session.get('project_name', 'N/A')}
🔗 Session: {session.get('session_id')}
📊 {session.get('message_count', 0)} messages • {session.get('active_docs', 0)} docs

🔗 Click to resume: https://ai-platform.com/session/{session.get('session_id')}
        """.strip()
    
    def _priority_to_calendar_color(self, priority: str) -> str:
        """
        Map priority to Google Calendar color ID
        
        Args:
            priority: Priority level (high/medium/low)
            
        Returns:
            Google Calendar color ID
        """
        colors = {
            'high': '11',    # Red
            'medium': '5',   # Yellow
            'low': '10'      # Green
        }
        return colors.get(priority, '9')  # Default blue


# ═══════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════

_sync_manager = None

def get_sync_manager() -> KanbanSyncManager:
    """
    Get singleton sync manager instance
    
    Returns:
        KanbanSyncManager instance
    """
    global _sync_manager
    if _sync_manager is None:
        _sync_manager = KanbanSyncManager()
    return _sync_manager


# ═══════════════════════════════════════════════════════════
# USAGE EXAMPLES
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    """Example usage and testing"""
    
    # Get sync manager
    sync_mgr = get_sync_manager()
    
    print("\n" + "="*60)
    print("KANBAN SYNC MANAGER - USAGE EXAMPLES")
    print("="*60)
    
    # Example 1: Sync Kanban move
    print("\n1. User drags card in Kanban:")
    print("   Result:", sync_mgr.sync_kanban_move(
        session_id='sess_test_123',
        new_column='done',
        user_id='john'
    ))
    
    # Example 2: Sync from Google Tasks
    print("\n2. User checks off task in Google Tasks:")
    print("   Result:", sync_mgr.sync_google_task_update(
        google_task_id='google_task_456'
    ))
    
    # Example 3: Create Google Task for session
    print("\n3. Create Google Task for new session:")
    print("   Result:", sync_mgr.create_google_task_for_session(
        session_id='sess_test_123',
        due_date='2025-11-01'
    ))
    
    # Example 4: Bulk sync all sessions
    print("\n4. Sync all sessions for user:")
    print("   Result:", sync_mgr.sync_all_sessions(user_id='john'))
    
    print("\n" + "="*60)
