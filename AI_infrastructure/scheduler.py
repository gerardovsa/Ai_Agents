"""
AI Automation Scheduler
========================
Flexible task scheduler for AI agent automation pipeline.

Features:
- Schedule AI agent tasks with cron expressions or datetime
- Link to Synergy sessions, threads, agents, locations
- User-created and AI-created automations
- Webhook triggers and conditional execution
- Approval workflow integration
- Real-time status tracking

Database Schema:
    scheduled_tasks table stores all automation definitions
    task_executions table stores execution history and logs
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import sqlite3  # Keep for type hints
from shared.db_connection_wrapper import get_connection
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests
import sys

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from shared.database_utils import get_database_connection


class AutomationScheduler:
    """
    Flexible automation scheduler for AI agent tasks
    
    Supports:
    - Cron schedules (recurring tasks)
    - One-time datetime triggers
    - Webhook triggers (external events)
    - Conditional triggers (when X happens, do Y)
    - Manual triggers (user/AI requests immediate execution)
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.api_base_url = 'http://localhost:5001'
        self.db_path = Path(__file__).parent.parent / 'data' / 'ai_infrastructure.db'
        self._init_database()
        
    def _init_database(self):
        """Initialize scheduler tables in database"""
        from shared.database_utils import is_using_supabase
        
        # Skip table creation on Supabase - tables already exist (or not needed)
        if is_using_supabase():
            print("✅ [SCHEDULER] Using Supabase - skipping table creation")
            return
        
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Create scheduled_tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scheduled_tasks (
                task_id TEXT PRIMARY KEY,
                task_name TEXT NOT NULL,
                description TEXT,
                created_by TEXT NOT NULL,  -- 'user' or 'ai'
                created_by_user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Schedule Configuration
                trigger_type TEXT NOT NULL,  -- 'cron', 'datetime', 'webhook', 'conditional', 'manual'
                cron_expression TEXT,  -- e.g., '0 9 * * 1-5' (Mon-Fri 9am)
                datetime_trigger TIMESTAMP,  -- One-time execution
                webhook_url TEXT,  -- For external triggers
                condition_config TEXT,  -- JSON: {type, field, operator, value}
                
                -- Execution Configuration
                action_type TEXT NOT NULL,  -- 'resume_session', 'send_message', 'execute_tool', 'run_workflow'
                
                -- Link to Synergy Session
                synergy_session_id TEXT,
                
                -- Link to Thread/Agent
                thread_id TEXT,  -- Specific thread to use
                agent_name TEXT,  -- Which agent to trigger (Prime, Email, Research, etc.)
                location TEXT,  -- dashboard, agent_panel, synergy_sidebar, etc.
                
                -- Action Payload
                action_payload TEXT,  -- JSON with action-specific data
                context_instructions TEXT,  -- Additional instructions for AI
                
                -- Approval Workflow
                requires_approval BOOLEAN DEFAULT 0,
                approval_status TEXT DEFAULT 'pending',  -- 'pending', 'approved', 'rejected'
                approval_note TEXT,
                approved_by_user_id INTEGER,
                approved_at TIMESTAMP,
                
                -- Status & Control
                enabled BOOLEAN DEFAULT 1,
                last_execution_time TIMESTAMP,
                next_execution_time TIMESTAMP,
                execution_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                retry_delay_seconds INTEGER DEFAULT 300,
                
                -- Metadata
                tags TEXT,  -- JSON array of tags
                priority INTEGER DEFAULT 5,  -- 1-10 (10 = highest)
                timeout_seconds INTEGER DEFAULT 300,
                
                FOREIGN KEY (created_by_user_id) REFERENCES users(user_id),
                FOREIGN KEY (synergy_session_id) REFERENCES synergy_sessions(session_id)
            )
        ''')
        
        # Create task_executions table (execution history/logs)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_executions (
                execution_id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status TEXT NOT NULL,  -- 'running', 'completed', 'failed', 'timeout', 'cancelled'
                result_data TEXT,  -- JSON with execution results
                error_message TEXT,
                retry_attempt INTEGER DEFAULT 0,
                execution_duration_ms INTEGER,
                
                FOREIGN KEY (task_id) REFERENCES scheduled_tasks(task_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_enabled ON scheduled_tasks(enabled)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_next_execution ON scheduled_tasks(next_execution_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_synergy ON scheduled_tasks(synergy_session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_thread ON scheduled_tasks(thread_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_task ON task_executions(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_executions_status ON task_executions(status)')
        
        conn.commit()
        conn.close()
        
        logger.info("Scheduler database initialized")
    
    def start(self):
        """Start the scheduler"""
        # Load all active tasks from database
        self._load_active_tasks()
        
        # Start background scheduler
        self.scheduler.start()
        
        # Add periodic task checker (every minute)
        self.scheduler.add_job(
            self._check_pending_approvals,
            'interval',
            minutes=1,
            id='approval_checker'
        )
        
        logger.info("Automation scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Automation scheduler stopped")
    
    def _load_active_tasks(self):
        """Load existing tasks from database on startup"""
        try:
            conn = get_connection('ai_infrastructure')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM ai_infrastructure.scheduled_tasks 
                WHERE is_active = true 
                AND (approval_status = 'approved' OR requires_approval = false)
            ''')
            
            tasks = cursor.fetchall()
            conn.close()
            
            for task in tasks:
                self._schedule_task(dict(task))
            
            logger.info(f"Loaded {len(tasks)} active tasks")
        except Exception as e:
            logger.warning(f"Could not load scheduled tasks (table may not exist): {e}")
            # Non-critical - scheduler can work without persisted tasks
    
    def _schedule_task(self, task: Dict):
        """Schedule a single task based on its trigger type"""
        task_id = task['task_id']
        trigger_type = task['trigger_type']
        
        try:
            if trigger_type == 'cron' and task['cron_expression']:
                # Cron schedule (recurring)
                trigger = CronTrigger.from_crontab(task['cron_expression'])
                self.scheduler.add_job(
                    self._execute_task,
                    trigger,
                    args=[task_id],
                    id=task_id,
                    replace_existing=True,
                    max_instances=1
                )
                logger.info(f"Scheduled cron task: {task['task_name']} ({task['cron_expression']})")
                
            elif trigger_type == 'datetime' and task['datetime_trigger']:
                # One-time datetime trigger
                run_date = datetime.fromisoformat(task['datetime_trigger'])
                if run_date > datetime.now():
                    self.scheduler.add_job(
                        self._execute_task,
                        'date',
                        run_date=run_date,
                        args=[task_id],
                        id=task_id,
                        replace_existing=True
                    )
                    logger.info(f"Scheduled datetime task: {task['task_name']} at {run_date}")
                else:
                    logger.warning(f"Task {task['task_name']} has past trigger time, skipping")
                    
            elif trigger_type == 'conditional':
                # Conditional triggers are checked in periodic checker
                pass
                
            elif trigger_type == 'manual':
                # Manual triggers executed on-demand only
                pass
                
        except Exception as e:
            logger.error(f"Failed to schedule task {task_id}: {e}")
    
    def _execute_task(self, task_id: str):
        """Execute a scheduled task"""
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Get task details
        cursor.execute('SELECT * FROM scheduled_tasks WHERE task_id = %s', (task_id,))
        task = cursor.fetchone()
        
        if not task:
            logger.error(f"Task {task_id} not found")
            conn.close()
            return
        
        task = dict(task)
        
        # Create execution record
        cursor.execute('''
            INSERT INTO task_executions (task_id, status)
            VALUES (%s, 'running')
        ''', (task_id,))
        execution_id = cursor.lastrowid
        conn.commit()
        
        start_time = datetime.now()
        
        try:
            # Execute based on action type
            action_type = task['action_type']
            result = None
            
            if action_type == 'resume_session':
                result = self._execute_resume_session(task)
            elif action_type == 'send_message':
                result = self._execute_send_message(task)
            elif action_type == 'execute_tool':
                result = self._execute_tool(task)
            elif action_type == 'run_workflow':
                result = self._execute_workflow(task)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
            
            # Mark execution as completed
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            cursor.execute('''
                UPDATE task_executions 
                SET status = 'completed', completed_at = %s, result_data = %s, execution_duration_ms = %s
                WHERE execution_id = %s
            ''', (end_time, json.dumps(result), duration_ms, execution_id))
            
            # Update task statistics
            cursor.execute('''
                UPDATE scheduled_tasks 
                SET execution_count = execution_count + 1, last_execution_time = %s,
                    failure_count = 0
                WHERE task_id = %s
            ''', (end_time, task_id))
            
            conn.commit()
            logger.info(f"Task {task['task_name']} executed successfully in {duration_ms}ms")
            
        except Exception as e:
            # Mark execution as failed
            end_time = datetime.now()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            cursor.execute('''
                UPDATE task_executions 
                SET status = 'failed', completed_at = %s, error_message = %s, execution_duration_ms = %s
                WHERE execution_id = %s
            ''', (end_time, str(e), duration_ms, execution_id))
            
            # Update task failure count
            cursor.execute('''
                UPDATE scheduled_tasks 
                SET failure_count = failure_count + 1, last_execution_time = %s
                WHERE task_id = %s
            ''', (end_time, task_id))
            
            conn.commit()
            logger.error(f"Task {task['task_name']} failed: {e}")
            
            # Check if should retry
            if task['failure_count'] + 1 < task['max_retries']:
                # Schedule retry
                retry_time = datetime.now() + timedelta(seconds=task['retry_delay_seconds'])
                self.scheduler.add_job(
                    self._execute_task,
                    'date',
                    run_date=retry_time,
                    args=[task_id],
                    id=f"{task_id}_retry_{task['failure_count'] + 1}"
                )
                logger.info(f"Scheduled retry for {task['task_name']} at {retry_time}")
        
        finally:
            conn.close()
    
    def _execute_resume_session(self, task: Dict) -> Dict:
        """Execute resume_session action"""
        synergy_session_id = task['synergy_session_id']
        thread_id = task['thread_id']
        agent_name = task['agent_name']
        context_instructions = task['context_instructions']
        
        # Call backend API to resume session
        url = f"{self.api_base_url}/api/synergy/{synergy_session_id}/resume"
        
        payload = {
            'thread_id': thread_id,
            'agent_name': agent_name,
            'context_instructions': context_instructions,
            'action_payload': json.loads(task['action_payload']) if task['action_payload'] else {}
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def _execute_send_message(self, task: Dict) -> Dict:
        """Execute send_message action"""
        thread_id = task['thread_id']
        action_payload = json.loads(task['action_payload']) if task['action_payload'] else {}
        
        message = action_payload.get('message', '')
        agent_name = task['agent_name'] or 'Prime Agent'
        
        # Call backend API to send message
        url = f"{self.api_base_url}/api/agent/chat"
        
        payload = {
            'message': message,
            'thread_id': thread_id,
            'agent_name': agent_name,
            'context': action_payload.get('context', {})
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def _execute_tool(self, task: Dict) -> Dict:
        """Execute tool action"""
        action_payload = json.loads(task['action_payload']) if task['action_payload'] else {}
        
        tool_name = action_payload.get('tool_name')
        tool_params = action_payload.get('tool_params', {})
        
        # Call backend API to execute tool
        url = f"{self.api_base_url}/api/tools/execute"
        
        payload = {
            'tool_name': tool_name,
            'parameters': tool_params
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def _execute_workflow(self, task: Dict) -> Dict:
        """Execute workflow action (multiple steps)"""
        action_payload = json.loads(task['action_payload']) if task['action_payload'] else {}
        
        workflow_steps = action_payload.get('steps', [])
        results = []
        
        for step in workflow_steps:
            step_type = step.get('type')
            
            if step_type == 'tool':
                result = self._execute_tool({'action_payload': json.dumps(step)})
            elif step_type == 'message':
                result = self._execute_send_message({'thread_id': task['thread_id'], 'action_payload': json.dumps(step)})
            elif step_type == 'delay':
                import time
                time.sleep(step.get('seconds', 1))
                result = {'status': 'delayed', 'seconds': step.get('seconds')}
            
            results.append(result)
        
        return {'steps_executed': len(results), 'results': results}
    
    def _check_pending_approvals(self):
        """Check for tasks pending approval and notify users"""
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM ai_infrastructure.scheduled_tasks 
            WHERE is_active = true 
            AND requires_approval = true 
            AND approval_status = 'pending'
        ''')
        
        pending_tasks = cursor.fetchall()
        conn.close()
        
        if pending_tasks:
            logger.info(f"Found {len(pending_tasks)} tasks pending approval")
            # TODO: Send notifications to users
    
    def create_task(self, task_data: Dict) -> str:
        """Create a new scheduled task"""
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_data.get('task_name', 'unnamed').replace(' ', '_')}"
        
        # Map to actual Supabase columns
        # Supabase has: user_id, task_name, task_type, schedule_type, schedule_value, 
        #                tool_name, tool_params, is_active, last_run, next_run, 
        #                created_at, updated_at, requires_approval, approval_status, status, description
        
        cursor.execute('''
            INSERT INTO ai_infrastructure.scheduled_tasks (
                user_id, task_name, task_type, schedule_type, schedule_value,
                tool_name, tool_params, is_active, requires_approval, approval_status, 
                status, description
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            task_data.get('created_by_user_id') or task_data.get('user_id', 1),
            task_data.get('task_name'),
            task_data.get('task_type', 'scheduled'),
            task_data.get('schedule_type', 'cron'),
            task_data.get('cron_expression') or task_data.get('schedule_value'),
            task_data.get('action_type') or task_data.get('tool_name'),
            str(task_data.get('action_payload', {})),
            task_data.get('enabled', True),  # Maps to is_active
            task_data.get('requires_approval', False),
            'pending' if task_data.get('requires_approval', False) else 'approved',
            task_data.get('status', 'active'),
            task_data.get('description')
        ))
        
        conn.commit()
        conn.close()
        
        # Schedule the task if approved or doesn't require approval
        if not task_data.get('requires_approval', False):
            self._schedule_task(task_data)
        
        logger.info(f"Created task: {task_id}")
        return task_id
    
    def update_task(self, task_id: str, updates: Dict) -> bool:
        """Update an existing task"""
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        for key, value in updates.items():
            if key not in ['task_id', 'created_at']:
                update_fields.append(f"{key} = %s")
                values.append(value)
        
        if not update_fields:
            conn.close()
            return False
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(task_id)
        
        query = f"UPDATE scheduled_tasks SET {', '.join(update_fields)} WHERE task_id = %s"
        cursor.execute(query, values)
        
        conn.commit()
        conn.close()
        
        # Reschedule task if it's enabled
        if updates.get('enabled', True):
            # Remove old job
            try:
                self.scheduler.remove_job(task_id)
            except:
                pass
            
            # Get updated task and reschedule
            conn = get_connection('ai_infrastructure')
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM scheduled_tasks WHERE task_id = %s', (task_id,))
            task = cursor.fetchone()
            conn.close()
            
            if task:
                self._schedule_task(dict(task))
        
        logger.info(f"Updated task: {task_id}")
        return True
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a scheduled task"""
        # Remove from scheduler
        try:
            self.scheduler.remove_job(task_id)
        except:
            pass
        
        # Delete from database
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM scheduled_tasks WHERE task_id = %s', (task_id,))
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted task: {task_id}")
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        """Get task by ID"""
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM scheduled_tasks WHERE task_id = %s', (task_id,))
        task = cursor.fetchone()
        conn.close()
        
        return dict(task) if task else None
    
    def list_tasks(self, filters: Optional[Dict] = None) -> List[Dict]:
        """List all tasks with optional filters"""
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        query = 'SELECT * FROM scheduled_tasks WHERE 1=1'
        params = []
        
        if filters:
            if 'synergy_session_id' in filters:
                query += ' AND synergy_session_id = %s'
                params.append(filters['synergy_session_id'])
            if 'thread_id' in filters:
                query += ' AND thread_id = %s'
                params.append(filters['thread_id'])
            if 'agent_name' in filters:
                query += ' AND agent_name = %s'
                params.append(filters['agent_name'])
            if 'enabled' in filters:
                query += ' AND enabled = %s'
                params.append(filters['enabled'])
        
        cursor.execute(query, params)
        tasks = cursor.fetchall()
        conn.close()
        
        return [dict(task) for task in tasks]
    
    def get_execution_history(self, task_id: str, limit: int = 50) -> List[Dict]:
        """Get execution history for a task"""
        conn = get_connection('ai_infrastructure')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM task_executions 
            WHERE task_id = %s 
            ORDER BY started_at DESC 
            LIMIT %s
        ''', (task_id, limit))
        
        executions = cursor.fetchall()
        conn.close()
        
        return [dict(execution) for execution in executions]


# Global scheduler instance
_scheduler_instance = None


def get_scheduler() -> AutomationScheduler:
    """Get global scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = AutomationScheduler()
    return _scheduler_instance


def start_scheduler():
    """Start the global scheduler"""
    scheduler = get_scheduler()
    scheduler.start()
    return scheduler


def stop_scheduler():
    """Stop the global scheduler"""
    global _scheduler_instance
    if _scheduler_instance:
        _scheduler_instance.stop()
        _scheduler_instance = None
