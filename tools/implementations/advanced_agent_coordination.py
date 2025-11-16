"""
Advanced Multi-Agent Coordination Tools

Provides tools for:
1. assign_and_activate_agent_with_slugs - Combo tool for multi-slug assignment with UI automation
2. request_update_from_thread - Cross-thread communication initiator
3. respond_to_cross_thread_request - Cross-thread response handler

Functions enable AI to distribute work across 26 agents, coordinate complex projects,
and communicate between threads for updates and information sharing.
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


# NATO alphabet mapping for agent names
NATO_ALPHABET = {
    'Alpha': 1, 'Bravo': 2, 'Charlie': 3, 'Delta': 4, 'Echo': 5, 'Foxtrot': 6,
    'Golf': 7, 'Hotel': 8, 'India': 9, 'Juliet': 10, 'Kilo': 11, 'Lima': 12,
    'Mike': 13, 'November': 14, 'Oscar': 15, 'Papa': 16, 'Quebec': 17,
    'Romeo': 18, 'Sierra': 19, 'Tango': 20, 'Uniform': 21, 'Victor': 22,
    'Whiskey': 23, 'X-ray': 24, 'Yankee': 25, 'Zulu': 26
}

REVERSE_NATO = {v: k for k, v in NATO_ALPHABET.items()}


class AgentCoordinationError(Exception):
    """Custom exception for agent coordination errors"""
    pass


def get_db_connection():
    """Get database connection to sessions.db"""
    root_dir = Path(__file__).parent.parent.parent
    db_path = root_dir / 'data' / 'sessions.db'
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def parse_agent_identifier(agent_id: str) -> str:
    """
    Parse agent identifier and return standardized location string.
    
    Accepts:
    - NATO names: 'Alpha', 'Bravo', etc. -> 'agent-1', 'agent-2', etc.
    - Agent locations: 'agent-1', 'agent-2', etc. -> unchanged
    - Agent numbers: '1', '2', etc. -> 'agent-1', 'agent-2', etc.
    
    Returns:
        Standardized location string like 'agent-1'
    
    Raises:
        AgentCoordinationError: If agent identifier is invalid
    """
    agent_id = str(agent_id).strip()
    
    # Check if NATO alphabet name
    if agent_id in NATO_ALPHABET:
        agent_num = NATO_ALPHABET[agent_id]
        return f'agent-{agent_num}'
    
    # Check if already in agent-N format
    if agent_id.startswith('agent-'):
        try:
            num = int(agent_id.split('-')[1])
            if 1 <= num <= 26:
                return agent_id
        except (ValueError, IndexError):
            pass
    
    # Check if numeric
    try:
        num = int(agent_id)
        if 1 <= num <= 26:
            return f'agent-{num}'
    except ValueError:
        pass
    
    raise AgentCoordinationError(f"Invalid agent identifier: {agent_id}. Use NATO name, 'agent-N', or number 1-26.")


def get_thread_by_location(location: str, user_id: int) -> Optional[Dict[str, Any]]:
    """Get existing thread at specified location"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT thread_id, thread_slug, title, location, 
               workflow_slug, workflow_title,
               internal_doc_slug, internal_doc_title,
               synergy_session_id, created_at, updated_at
        FROM threads
        WHERE location = ? AND user_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
    """, (location, user_id))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None


def assign_and_activate_agent_with_slugs(
    target_agent: str,
    thread_title: str,
    instructions: str,
    slugs: Optional[Dict[str, str]] = None,
    auto_trigger: bool = False,
    open_ui: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    ALL-IN-ONE COMBO TOOL: Assign multiple resource slugs to an agent thread,
    send instructions, and optionally trigger agent activation with automatic UI updates.
    
    Args:
        target_agent: Agent identifier (NATO name, 'agent-N', or number 1-26)
        thread_title: Title for the thread
        instructions: Detailed instructions to send to the agent
        slugs: Optional dict with workflow_slug, internal_doc_slug, synergy_session_id, etc.
        auto_trigger: If True, automatically triggers agent AI processing
        open_ui: If True, returns UI commands for frontend automation
        **kwargs: Includes _user_id, _source_thread_id from context injection
    
    Returns:
        Dict with thread details, assigned slugs, and optional ui_commands array
    
    Raises:
        AgentCoordinationError: If agent identifier invalid or database error
    """
    # Parse agent identifier
    try:
        location = parse_agent_identifier(target_agent)
    except AgentCoordinationError as e:
        return {
            'success': False,
            'error': str(e)
        }
    
    # Get user_id from kwargs (injected by credential_injector)
    user_id = kwargs.get('_user_id')
    if not user_id:
        return {
            'success': False,
            'error': 'user_id required but not provided in context'
        }
    
    source_thread_id = kwargs.get('_source_thread_id')
    slugs = slugs or {}
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if thread exists at this location
        existing_thread = get_thread_by_location(location, user_id)
        
        if existing_thread:
            # Update existing thread
            thread_id = existing_thread['thread_id']
            
            # Build update query dynamically based on provided slugs
            update_fields = ['title = ?', 'updated_at = ?']
            update_values = [thread_title, datetime.now().isoformat()]
            
            if 'workflow_slug' in slugs:
                update_fields.append('workflow_slug = ?')
                update_values.append(slugs['workflow_slug'])
            if 'workflow_title' in slugs:
                update_fields.append('workflow_title = ?')
                update_values.append(slugs['workflow_title'])
            if 'internal_doc_slug' in slugs:
                update_fields.append('internal_doc_slug = ?')
                update_values.append(slugs['internal_doc_slug'])
            if 'internal_doc_title' in slugs:
                update_fields.append('internal_doc_title = ?')
                update_values.append(slugs['internal_doc_title'])
            if 'synergy_session_id' in slugs:
                update_fields.append('synergy_session_id = ?')
                update_values.append(slugs['synergy_session_id'])
            
            update_values.append(thread_id)
            
            cursor.execute(f"""
                UPDATE threads
                SET {', '.join(update_fields)}
                WHERE thread_id = ?
            """, update_values)
            
        else:
            # Create new thread
            thread_id = str(uuid.uuid4())
            thread_slug = f"thread-{uuid.uuid4().hex[:8]}"
            
            cursor.execute("""
                INSERT INTO threads (
                    thread_id, thread_slug, title, location, user_id,
                    workflow_slug, workflow_title,
                    internal_doc_slug, internal_doc_title,
                    synergy_session_id,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                thread_id, thread_slug, thread_title, location, user_id,
                slugs.get('workflow_slug'),
                slugs.get('workflow_title'),
                slugs.get('internal_doc_slug'),
                slugs.get('internal_doc_title'),
                slugs.get('synergy_session_id'),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        # Insert instruction message into thread
        message_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO messages (
                message_id, thread_id, role, content, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            message_id,
            thread_id,
            'user',
            instructions,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        
        # Build response
        result = {
            'success': True,
            'thread_id': thread_id,
            'thread_location': location,
            'thread_title': thread_title,
            'assigned_slugs': {k: v for k, v in slugs.items() if v},
            'message_id': message_id,
            'instruction_sent': True
        }
        
        # Add UI commands if requested
        if open_ui:
            ui_commands = []
            
            # Command 1: Switch to Multi-Agent tab
            ui_commands.append({
                'command': 'switch_tab',
                'tab_name': 'multi-agent'
            })
            
            # Command 2: Open agent column
            agent_num = int(location.split('-')[1])
            ui_commands.append({
                'command': 'open_agent_column',
                'agent_location': location,
                'agent_number': agent_num,
                'agent_name': REVERSE_NATO.get(agent_num, f'Agent {agent_num}'),
                'highlight': True
            })
            
            # Command 3: Show thread info with badges
            ui_commands.append({
                'command': 'show_thread_info',
                'thread_id': thread_id,
                'thread_location': location,
                'badges': {
                    'workflow': slugs.get('workflow_title') if slugs.get('workflow_slug') else None,
                    'internal_doc': slugs.get('internal_doc_title') if slugs.get('internal_doc_slug') else None,
                    'synergy': slugs.get('synergy_session_id') is not None
                }
            })
            
            # Command 4: Trigger agent if auto_trigger=True
            if auto_trigger:
                ui_commands.append({
                    'command': 'trigger_agent_request',
                    'thread_id': thread_id,
                    'agent_location': location,
                    'message_id': message_id
                })
            
            result['ui_commands'] = ui_commands
        
        return result
        
    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'error': f"Failed to assign agent: {str(e)}"
        }
    finally:
        conn.close()


def request_update_from_thread(
    target_thread_id: str,
    request_message: str,
    request_type: str = 'status_update',
    priority: str = 'medium',
    wait_for_response: bool = False,
    timeout_seconds: int = 30,
    **kwargs
) -> Dict[str, Any]:
    """
    Cross-thread communication: Request information from another agent thread.
    
    Creates cross-thread request record, inserts request message into target thread,
    and optionally waits for response with timeout.
    
    Args:
        target_thread_id: Thread ID or agent identifier to request from
        request_message: The request message to send
        request_type: Type of request (status_update, deliverable, question, etc.)
        priority: Priority level (low, medium, high, urgent)
        wait_for_response: If True, polls for response up to timeout_seconds
        timeout_seconds: Max seconds to wait for response if wait_for_response=True
        **kwargs: Includes _user_id, _source_thread_id from context
    
    Returns:
        Dict with request details, status, and optional response if wait_for_response=True
    
    Raises:
        AgentCoordinationError: If target thread not found or database error
    """
    user_id = kwargs.get('_user_id')
    source_thread_id = kwargs.get('_source_thread_id')
    
    if not user_id or not source_thread_id:
        return {
            'success': False,
            'error': 'user_id and source_thread_id required in context'
        }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Parse target if it's an agent identifier
        try:
            target_location = parse_agent_identifier(target_thread_id)
            target_thread = get_thread_by_location(target_location, user_id)
            if not target_thread:
                return {
                    'success': False,
                    'error': f"No thread found at location {target_location}"
                }
            target_thread_id = target_thread['thread_id']
        except AgentCoordinationError:
            # Assume it's already a thread_id
            cursor.execute("SELECT thread_id FROM threads WHERE thread_id = ?", (target_thread_id,))
            if not cursor.fetchone():
                return {
                    'success': False,
                    'error': f"Thread {target_thread_id} not found"
                }
        
        # Create cross-thread request record
        request_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO cross_thread_requests (
                request_id, source_thread_id, target_thread_id,
                request_message, request_type, priority, status,
                created_at, user_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request_id, source_thread_id, target_thread_id,
            request_message, request_type, priority, 'pending',
            datetime.now().isoformat(), user_id
        ))
        
        # Insert request message into target thread
        message_id = str(uuid.uuid4())
        priority_icon = {
            'low': '🔵',
            'medium': '🟡',
            'high': '🟠',
            'urgent': '🔴'
        }.get(priority, '🟡')
        
        formatted_message = f"{priority_icon} **Cross-Thread Request** (ID: {request_id})\n\n{request_message}\n\n*Use `respond_to_cross_thread_request` to respond.*"
        
        cursor.execute("""
            INSERT INTO messages (
                message_id, thread_id, role, content, created_at,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message_id, target_thread_id, 'system', formatted_message,
            datetime.now().isoformat(),
            f'{{"request_id": "{request_id}", "source_thread_id": "{source_thread_id}", "priority": "{priority}"}}'
        ))
        
        conn.commit()
        
        result = {
            'success': True,
            'request_id': request_id,
            'source_thread_id': source_thread_id,
            'target_thread_id': target_thread_id,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        # Add UI commands
        result['ui_commands'] = [
            {
                'command': 'show_cross_thread_request',
                'request_id': request_id,
                'target_thread_id': target_thread_id,
                'priority': priority
            }
        ]
        
        # Wait for response if requested
        if wait_for_response:
            import time
            start_time = time.time()
            
            while (time.time() - start_time) < timeout_seconds:
                cursor.execute("""
                    SELECT status, response_message, responded_at
                    FROM cross_thread_requests
                    WHERE request_id = ?
                """, (request_id,))
                
                row = cursor.fetchone()
                if row and row['status'] == 'completed':
                    result['status'] = 'completed'
                    result['response_message'] = row['response_message']
                    result['responded_at'] = row['responded_at']
                    break
                
                time.sleep(1)
            
            if result['status'] == 'pending':
                result['timeout'] = True
                result['message'] = f"No response received within {timeout_seconds} seconds"
        
        return result
        
    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'error': f"Failed to create cross-thread request: {str(e)}"
        }
    finally:
        conn.close()


def respond_to_cross_thread_request(
    request_id: str,
    response_message: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Respond to a cross-thread request from another agent.
    
    Updates request status to 'completed', stores response message,
    and sends response back to source thread.
    
    Args:
        request_id: The request ID to respond to
        response_message: Your response to the request
        **kwargs: Includes _user_id, _thread_id from context
    
    Returns:
        Dict with response confirmation and UI commands
    
    Raises:
        AgentCoordinationError: If request not found or already completed
    """
    user_id = kwargs.get('_user_id')
    current_thread_id = kwargs.get('_thread_id')
    
    if not user_id:
        return {
            'success': False,
            'error': 'user_id required in context'
        }
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get request details
        cursor.execute("""
            SELECT request_id, source_thread_id, target_thread_id,
                   request_message, status
            FROM cross_thread_requests
            WHERE request_id = ? AND user_id = ?
        """, (request_id, user_id))
        
        row = cursor.fetchone()
        if not row:
            return {
                'success': False,
                'error': f"Request {request_id} not found"
            }
        
        request = dict(row)
        
        if request['status'] == 'completed':
            return {
                'success': False,
                'error': 'Request already completed'
            }
        
        # Update request with response
        responded_at = datetime.now().isoformat()
        cursor.execute("""
            UPDATE cross_thread_requests
            SET status = ?, response_message = ?, responded_at = ?
            WHERE request_id = ?
        """, ('completed', response_message, responded_at, request_id))
        
        # Insert response message into source thread
        message_id = str(uuid.uuid4())
        formatted_response = f"✅ **Response to Request {request_id}**\n\n{response_message}\n\n*Original request: {request['request_message']}*"
        
        cursor.execute("""
            INSERT INTO messages (
                message_id, thread_id, role, content, created_at,
                metadata
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            message_id, request['source_thread_id'], 'system',
            formatted_response, datetime.now().isoformat(),
            f'{{"request_id": "{request_id}", "responding_thread_id": "{current_thread_id}"}}'
        ))
        
        conn.commit()
        
        return {
            'success': True,
            'request_id': request_id,
            'source_thread_id': request['source_thread_id'],
            'response_sent_at': responded_at,
            'ui_commands': [
                {
                    'command': 'notify_thread_response',
                    'source_thread_id': request['source_thread_id'],
                    'request_id': request_id
                }
            ]
        }
        
    except Exception as e:
        conn.rollback()
        return {
            'success': False,
            'error': f"Failed to respond to request: {str(e)}"
        }
    finally:
        conn.close()
