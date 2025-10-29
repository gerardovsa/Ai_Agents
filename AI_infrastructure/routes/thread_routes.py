"""
Thread Management Routes
Thread/conversation management for all AI agents
"""

from flask import Blueprint, request
import json
from datetime import datetime, timedelta

# Import infrastructure
from core.agent_state_manager import agent_state_manager
from utils.database_helpers import (
    execute_sqlite_query, execute_sqlite_update,
    get_stock_database_path, DatabaseConnectionError
)
from utils.response_helpers import (
    success_response, error_response, list_response,
    deleted_response, updated_response
)

# Create blueprint
thread_bp = Blueprint('threads', __name__, url_prefix='/api/threads')


# ============================================================
# THREAD LISTING & SEARCH
# ============================================================

@thread_bp.route('/list', methods=['GET'])
def list_threads():
    """
    List all conversation threads across all agents
    
    Query params:
        ?agent_id=stock_ai (optional filter)
        ?limit=50 (default 50)
        ?days=30 (show threads from last N days)
    
    Returns list of threads with metadata
    """
    try:
        agent_filter = request.args.get('agent_id')
        limit = int(request.args.get('limit', 50))
        days = int(request.args.get('days', 30))
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        threads = []
        
        # Get threads from agent_state_manager
        for agent_id, sessions in agent_state_manager._agent_states.items():
            # Filter by agent if specified
            if agent_filter and agent_id != agent_filter:
                continue
            
            for session_id, state in sessions.items():
                # Get last activity timestamp
                last_activity = state.get('last_activity')
                
                # Filter by date if we have timestamp
                if last_activity:
                    try:
                        activity_time = datetime.fromisoformat(last_activity)
                        if activity_time < cutoff_date:
                            continue
                    except:
                        pass
                
                # Get agent display name
                agent_name = agent_state_manager._agent_names.get(agent_id, agent_id)
                
                threads.append({
                    'thread_id': f"{agent_id}_{session_id}",
                    'session_id': session_id,
                    'agent_id': agent_id,
                    'agent_name': agent_name,
                    'message_count': len(state['conversation']),
                    'status': state['status'],
                    'created_at': state.get('created_at'),
                    'last_activity': last_activity,
                    'context': state.get('context', {})
                })
        
        # Sort by last activity (most recent first)
        threads.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
        
        # Apply limit
        threads = threads[:limit]
        
        return list_response(threads, message=f"Found {len(threads)} threads")
    
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/search', methods=['GET'])
def search_threads():
    """
    Search threads by message content
    
    Query params:
        ?q=invoice (required - search keyword)
        ?agent_id=stock_ai (optional filter)
        ?limit=20 (default 20)
    
    Searches conversation content for keyword
    """
    try:
        keyword = request.args.get('q', '').strip().lower()
        agent_filter = request.args.get('agent_id')
        limit = int(request.args.get('limit', 20))
        
        if not keyword:
            return error_response("Missing search keyword 'q'", 400)
        
        matching_threads = []
        
        # Search through all agent states
        for agent_id, sessions in agent_state_manager._agent_states.items():
            if agent_filter and agent_id != agent_filter:
                continue
            
            for session_id, state in sessions.items():
                # Search conversation content
                matches = []
                for i, message in enumerate(state['conversation']):
                    content = str(message.get('content', '')).lower()
                    if keyword in content:
                        matches.append({
                            'message_index': i,
                            'role': message.get('role'),
                            'snippet': content[:200]  # First 200 chars
                        })
                
                if matches:
                    agent_name = agent_state_manager._agent_names.get(agent_id, agent_id)
                    
                    matching_threads.append({
                        'thread_id': f"{agent_id}_{session_id}",
                        'session_id': session_id,
                        'agent_id': agent_id,
                        'agent_name': agent_name,
                        'message_count': len(state['conversation']),
                        'match_count': len(matches),
                        'matches': matches[:3],  # First 3 matches
                        'last_activity': state.get('last_activity')
                    })
        
        # Sort by match count (most matches first)
        matching_threads.sort(key=lambda x: x['match_count'], reverse=True)
        
        # Apply limit
        matching_threads = matching_threads[:limit]
        
        return list_response(
            matching_threads,
            message=f"Found {len(matching_threads)} threads matching '{keyword}'"
        )
    
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# THREAD OPERATIONS (CRUD)
# ============================================================

@thread_bp.route('/save', methods=['POST'])
def save_thread():
    """
    Save thread to persistent storage
    
    Request JSON:
    {
        "agent_id": "stock_ai",
        "session_id": "uuid",
        "thread_name": "Invoice Analysis Oct 2025" (optional)
    }
    
    Saves thread to SQLite for long-term storage
    """
    try:
        data = request.json
        agent_id = data.get('agent_id')
        session_id = data.get('session_id')
        thread_name = data.get('thread_name', '')
        
        if not agent_id or not session_id:
            return error_response("Missing agent_id or session_id", 400)
        
        # Get thread state
        state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
        
        if not state['conversation']:
            return error_response("Thread has no messages to save", 400)
        
        # Save to SQLite
        db_path = get_stock_database_path()
        
        # Create threads table if not exists
        create_table_query = """
            CREATE TABLE IF NOT EXISTS saved_threads (
                thread_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                thread_name TEXT,
                conversation TEXT NOT NULL,
                message_count INTEGER,
                context TEXT,
                created_at TEXT,
                saved_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        execute_sqlite_update(db_path, create_table_query, None)
        
        # Insert thread
        thread_id = f"{agent_id}_{session_id}"
        conversation_json = json.dumps(state['conversation'])
        context_json = json.dumps(state.get('context', {}))
        
        insert_query = """
            INSERT OR REPLACE INTO saved_threads 
            (thread_id, agent_id, session_id, thread_name, conversation, 
             message_count, context, created_at, saved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """
        
        params = [
            thread_id,
            agent_id,
            session_id,
            thread_name,
            conversation_json,
            len(state['conversation']),
            context_json,
            state.get('created_at')
        ]
        
        execute_sqlite_update(db_path, insert_query, params)
        
        return success_response({
            'thread_id': thread_id,
            'message_count': len(state['conversation']),
            'saved_at': datetime.now().isoformat()
        }, message="Thread saved successfully")
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/load/<thread_id>', methods=['GET'])
def load_thread(thread_id):
    """
    Load saved thread from persistent storage
    
    Returns thread with full conversation history
    """
    try:
        db_path = get_stock_database_path()
        
        query = """
            SELECT 
                thread_id,
                agent_id,
                session_id,
                thread_name,
                conversation,
                message_count,
                context,
                created_at,
                saved_at
            FROM saved_threads
            WHERE thread_id = ?
        """
        
        results = execute_sqlite_query(db_path, query, [thread_id])
        
        if not results:
            return error_response(f"Thread {thread_id} not found", 404)
        
        thread = results[0]
        
        # Parse JSON fields
        thread['conversation'] = json.loads(thread['conversation'])
        thread['context'] = json.loads(thread.get('context', '{}'))
        
        return success_response(thread, message="Thread loaded successfully")
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """
    Delete saved thread from persistent storage
    
    Also clears from agent_state_manager if active
    """
    try:
        # Parse thread_id (format: "agent_id_session_id")
        parts = thread_id.split('_', 1)
        if len(parts) != 2:
            return error_response("Invalid thread_id format", 400)
        
        agent_id, session_id = parts
        
        # Clear from agent_state_manager if active
        agent_state_manager.clear_conversation(agent_id, session_id)
        
        # Delete from SQLite
        db_path = get_stock_database_path()
        
        delete_query = """
            DELETE FROM saved_threads
            WHERE thread_id = ?
        """
        
        rowcount = execute_sqlite_update(db_path, delete_query, [thread_id])
        
        if rowcount == 0:
            return error_response(f"Thread {thread_id} not found", 404)
        
        return deleted_response(
            message="Thread deleted successfully",
            deleted_count=rowcount
        )
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# THREAD STATISTICS
# ============================================================

@thread_bp.route('/stats', methods=['GET'])
def get_thread_stats():
    """
    Get thread statistics across all agents
    
    Returns:
    {
        "total_threads": 45,
        "total_messages": 1250,
        "by_agent": {
            "stock_ai": {"threads": 20, "messages": 500},
            "data_agent": {"threads": 15, "messages": 450}
        },
        "active_threads": 12,
        "saved_threads": 8
    }
    """
    try:
        stats = {
            'total_threads': 0,
            'total_messages': 0,
            'by_agent': {},
            'active_threads': 0,
            'saved_threads': 0
        }
        
        # Count active threads from agent_state_manager
        for agent_id, sessions in agent_state_manager._agent_states.items():
            agent_thread_count = len(sessions)
            agent_message_count = sum(len(s['conversation']) for s in sessions.values())
            
            stats['by_agent'][agent_id] = {
                'threads': agent_thread_count,
                'messages': agent_message_count,
                'agent_name': agent_state_manager._agent_names.get(agent_id, agent_id)
            }
            
            stats['total_threads'] += agent_thread_count
            stats['total_messages'] += agent_message_count
        
        stats['active_threads'] = stats['total_threads']
        
        # Count saved threads from SQLite
        try:
            db_path = get_stock_database_path()
            
            count_query = """
                SELECT COUNT(*) as count
                FROM saved_threads
            """
            
            results = execute_sqlite_query(db_path, count_query, None)
            if results:
                stats['saved_threads'] = results[0]['count']
        except:
            # Table might not exist yet
            stats['saved_threads'] = 0
        
        return success_response(stats, message="Thread statistics")
    
    except Exception as e:
        return error_response(str(e), 500)


# ============================================================
# AUTO-SAVE & MARK READ
# ============================================================

@thread_bp.route('/autosave', methods=['POST'])
def autosave_thread():
    """
    Auto-save thread during conversation
    
    Request JSON:
    {
        "agent_id": "stock_ai",
        "session_id": "uuid"
    }
    
    Automatically saves thread every N messages
    """
    try:
        data = request.json
        agent_id = data.get('agent_id')
        session_id = data.get('session_id')
        
        if not agent_id or not session_id:
            return error_response("Missing agent_id or session_id", 400)
        
        # Get thread state
        state = agent_state_manager.get_or_create_state(agent_id, session_id, {})
        
        message_count = len(state['conversation'])
        
        # Only auto-save if we have messages
        if message_count == 0:
            return success_response({
                'autosaved': False,
                'reason': 'No messages to save'
            })
        
        # Auto-save every 5 messages
        if message_count % 5 == 0:
            # Save to SQLite
            db_path = get_stock_database_path()
            
            # Ensure table exists
            create_table_query = """
                CREATE TABLE IF NOT EXISTS saved_threads (
                    thread_id TEXT PRIMARY KEY,
                    agent_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    thread_name TEXT,
                    conversation TEXT NOT NULL,
                    message_count INTEGER,
                    context TEXT,
                    created_at TEXT,
                    saved_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """
            execute_sqlite_update(db_path, create_table_query, None)
            
            # Save thread
            thread_id = f"{agent_id}_{session_id}"
            conversation_json = json.dumps(state['conversation'])
            context_json = json.dumps(state.get('context', {}))
            
            insert_query = """
                INSERT OR REPLACE INTO saved_threads 
                (thread_id, agent_id, session_id, thread_name, conversation, 
                 message_count, context, created_at, saved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """
            
            params = [
                thread_id,
                agent_id,
                session_id,
                f"Auto-saved conversation ({message_count} messages)",
                conversation_json,
                message_count,
                context_json,
                state.get('created_at')
            ]
            
            execute_sqlite_update(db_path, insert_query, params)
            
            return success_response({
                'autosaved': True,
                'message_count': message_count,
                'thread_id': thread_id
            }, message="Thread auto-saved")
        
        return success_response({
            'autosaved': False,
            'reason': f"Waiting for milestone ({message_count} messages)"
        })
    
    except Exception as e:
        return error_response(str(e), 500)


@thread_bp.route('/<thread_id>/mark-read', methods=['POST'])
def mark_thread_read(thread_id):
    """
    Mark thread as read
    
    Updates last_read timestamp for thread
    """
    try:
        db_path = get_stock_database_path()
        
        # Ensure table has last_read column
        alter_query = """
            ALTER TABLE saved_threads
            ADD COLUMN last_read TEXT
        """
        
        try:
            execute_sqlite_update(db_path, alter_query, None)
        except:
            # Column might already exist
            pass
        
        # Update last_read
        update_query = """
            UPDATE saved_threads
            SET last_read = datetime('now')
            WHERE thread_id = ?
        """
        
        rowcount = execute_sqlite_update(db_path, update_query, [thread_id])
        
        if rowcount == 0:
            return error_response(f"Thread {thread_id} not found", 404)
        
        return updated_response(
            message="Thread marked as read",
            updated_count=rowcount
        )
    
    except DatabaseConnectionError as e:
        return error_response(f"Database error: {str(e)}", 500)
    except Exception as e:
        return error_response(str(e), 500)
