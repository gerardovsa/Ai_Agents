"""
FILE: AI_infrastructure/routes/thread_assignment_routes.py
PURPOSE: Store thread assignments in users.metadata JSON column and sessions.threads.location

DEPENDENCIES:
- flask - Blueprint routing
- psycopg2 - PostgreSQL database operations (Supabase)
- json - JSON parsing

EXPORTS:
- thread_assignment_bp - Flask Blueprint with thread assignment endpoints

USED BY:
- AI_infrastructure/flask_app.py (register blueprint)
- UI/business-ai-platform-v2.html (AJAX calls from ThreadManager)

RELATED FILES:
- Supabase PostgreSQL (ai_infrastructure.users, sessions.threads)
- UI/business-ai-platform-v2.html (ThreadManager object)

NOTES:
- Stores thread locations in BOTH places:
  1. users.metadata JSON (legacy, backward compatibility)
  2. sessions.threads.location (single source of truth)
- Prime is implicit (any thread not in an agent is in Prime)
- JSON format: {"thread_assignments": {"agent-1": "session-id", ...}}
- CRITICAL: Always cast thread_slug to ::text in PostgreSQL queries

LAST MODIFIED: 2025-11-20 - Removed SQLite, fixed PostgreSQL type casting
"""

from flask import Blueprint, request, jsonify
from pathlib import Path
from shared.database_utils import get_database_connection, get_sessions_connection
import json
import logging

logger = logging.getLogger(__name__)

thread_assignment_bp = Blueprint('thread_assignments', __name__)


def get_db_connection():
    """Get connection to Supabase PostgreSQL (using connection pool)
    
    ✅ CRITICAL: ALL data stored in Supabase PostgreSQL, NOT SQLite!
    This prevents bypassing the pool and leaking connections.
    """
    print('[Thread Assignments] Connecting to Supabase PostgreSQL sessions schema...')
    return get_sessions_connection()


def enforce_thread_assignment_rules(user_id, session_id, location):
    """
    Enforce thread assignment rules in database:
    
    RULES:
    1. Thread can only be in ONE location (Prime OR one agent)
    2. Agent can only have ONE thread
    3. Most recent assignment wins - old assignments are removed
    
    Args:
        user_id: User ID
        session_id: Thread ID to assign
        location: Target location (agent-1, agent-2, etc. or 'prime')
    
    Returns:
        dict: {
            'previous_location': where thread was before,
            'displaced_thread': thread that was kicked out of target location
        }
    """
    conn = None
    previous_location = None
    displaced_thread = None
    
    try:
        conn = get_db_connection()
        # ✅ FIXED: Don't modify isolation_level with pooled connections
        # Use explicit commit() instead of autocommit mode
        cursor = conn.cursor()
        
        # CRITICAL FIX: Ensure user row exists before UPDATE
        cursor.execute("SELECT id FROM ai_infrastructure.users WHERE id = %s", [user_id])
        if not cursor.fetchone():
            logger.info(f"🔧 [FIX] Creating user row for user_id {user_id}")
            cursor.execute("""
                INSERT INTO ai_infrastructure.users (id, username, email, password_hash, created_at, last_active, metadata)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '{}')
            """, [user_id, f'user_{user_id}', f'user_{user_id}@ai-platform.local', 'SYSTEM_USER'])
        
        # Get existing metadata
        cursor.execute("SELECT metadata FROM ai_infrastructure.users WHERE id = %s", [user_id])
        row = cursor.fetchone()
        
        # Parse metadata (PostgreSQL with pooling returns dict-like object)
        metadata_value = row['metadata'] if row else None
        if metadata_value:
            try:
                metadata = json.loads(metadata_value)
            except json.JSONDecodeError:
                metadata = {}
        else:
            metadata = {}
        
        assignments = metadata.get('thread_assignments', {})
        
        # RULE 1: Remove thread from ANY previous location (thread can only be in one place)
        for loc, tid in list(assignments.items()):
            if tid == session_id:
                previous_location = loc
                del assignments[loc]
                logger.info(f"🔄 [RULE 1] Removed thread {session_id} from {loc} (thread can only be in one location)")
        
        # If moving to Prime, we're done (Prime is implicit - not stored in metadata)
        if location == 'prime':
            metadata['thread_assignments'] = assignments
            cursor.execute("""
                UPDATE ai_infrastructure.users 
                SET metadata = %s, last_active = CURRENT_TIMESTAMP
                WHERE id = %s
            """, [json.dumps(metadata), user_id])
            
            # CRITICAL: Also update sessions.threads.location to 'prime'
            cursor.execute("""
                UPDATE sessions.threads 
                SET location = 'prime', updated_at = CURRENT_TIMESTAMP
                WHERE thread_slug = %s::text AND user_id = %s
            """, [str(session_id), user_id])
            conn.commit()
            
            logger.info(f"✅ Thread {session_id} moved to Prime in both metadata and sessions.threads (removed from {previous_location})")
            
            # Return early - finally block will close connection
            return {
                'previous_location': previous_location,
                'displaced_thread': None
            }
        
        # RULE 2: Agent can only have ONE thread - remove existing thread from target location
        if location in assignments:
            displaced_thread = assignments[location]
            del assignments[location]
            logger.info(f"🔄 [RULE 2] Displaced thread {displaced_thread} from {location} (agent can only have one thread)")
        
        # RULE 3: Assign thread to new location (most recent assignment wins)
        assignments[location] = session_id
        logger.info(f"✅ [RULE 3] Assigned thread {session_id} to {location} (most recent assignment)")
        
        # Save back to database (LEGACY metadata - keep for backward compatibility)
        metadata['thread_assignments'] = assignments
        cursor.execute("""
            UPDATE ai_infrastructure.users 
            SET metadata = %s, last_active = CURRENT_TIMESTAMP
            WHERE id = %s
        """, [json.dumps(metadata), user_id])
        
        # CRITICAL: Also update sessions.threads.location (NEW SINGLE SOURCE OF TRUTH)
        cursor.execute("""
            UPDATE sessions.threads 
            SET location = %s, updated_at = CURRENT_TIMESTAMP
            WHERE thread_slug = %s::text AND user_id = %s
        """, [location, str(session_id), user_id])
        conn.commit()
        
        # If thread was displaced, move it to Prime
        if displaced_thread:
            cursor.execute("""
                UPDATE sessions.threads 
                SET location = 'prime', updated_at = CURRENT_TIMESTAMP
                WHERE thread_slug = %s::text AND user_id = %s
            """, [str(displaced_thread), user_id])
            conn.commit()
            logger.info(f"🔄 Moved displaced thread {displaced_thread} to Prime in sessions.threads")
        
        # If thread had a previous location, ensure it's cleared in sessions.threads
        if previous_location and previous_location != location:
            # Already updated above with new location, no additional action needed
            pass
        
        logger.info(f"✅ Updated sessions.threads.location for thread {session_id} → {location}")
        
        return {
            'previous_location': previous_location,
            'displaced_thread': displaced_thread
        }
    finally:
        if conn:
            conn.close()


@thread_assignment_bp.route('/api/thread-assignments', methods=['GET'])
@thread_assignment_bp.route('/api/thread-assignments/list', methods=['GET'])  # Alias for backward compatibility
def get_thread_assignments():
    """
    Get thread assignments for user
    Only returns agent columns (Prime is implicit)
    
    READS FROM: sessions.threads.location (single source of truth)
    
    Query params:
        user_id: User ID (default: 1)
    
    Returns:
        {
            "success": true,
            "assignments": {
                "agent-1": "1762192838469",
                "agent-2": "1762193002345"
            }
        }
    """
    conn = None
    try:
        user_id = request.args.get('user_id', 1, type=int)
        logger.info(f"📥 [Assignment] GET request for user_id: {user_id}")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Read from sessions.threads.location (single source of truth in Supabase)
        # PostgreSQL uses %s for parameters
        # CRITICAL: Include prime-loaded (frontend needs this for page load)
        logger.info(f"🔍 [Assignment] Executing query for user {user_id}")
        cursor.execute("""
            SELECT thread_slug, location 
            FROM sessions.threads 
            WHERE user_id = %s 
              AND location IS NOT NULL 
              AND location != 'prime'
            ORDER BY updated_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        logger.info(f"📊 [Assignment] Query returned {len(rows) if rows else 0} rows")
        
        if not rows:
            logger.info(f"No thread assignments found for user {user_id}")
            return jsonify({
                'success': True,
                'assignments': {}
            })
        
        # Build assignments dict: {"agent-1": "thread_slug", "prime-loaded": "thread_slug", ...}
        assignments = {}
        for row in rows:
            # row is a RealDictRow (dictionary), not a tuple
            thread_slug = str(row['thread_slug'])  # Use dict key access
            location = row['location']
            
            # Include agent locations AND prime-loaded (needed for page load)
            if location and (location.startswith('agent-') or location == 'prime-loaded'):
                assignments[location] = thread_slug
        
        logger.info(f"Loaded {len(assignments)} thread assignments from sessions.threads for user {user_id}")
        
        return jsonify({
            'success': True,
            'assignments': assignments
        })
        
    except Exception as e:
        logger.error(f"❌ [Assignment] Error getting thread assignments")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error message: {str(e)}")
        logger.error(f"   Error repr: {repr(e)}")
        import traceback
        logger.error(f"   Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@thread_assignment_bp.route('/api/thread-assignments', methods=['POST'])
def save_thread_assignments():
    """
    Save thread assignments (batch update)
    Only saves agent columns (Prime not stored)
    
    Request body:
        {
            "user_id": 1,
            "assignments": {
                "agent-1": "session-id-123",
                "agent-2": null
            }
        }
    
    Returns:
        {
            "success": true,
            "saved": true
        }
    """
    conn = None
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        assignments = data.get('assignments', {})
        
        # Filter out 'prime' - we only store agent columns
        agent_assignments = {
            loc: sid for loc, sid in assignments.items() 
            if loc.startswith('agent-')
        }
        
        conn = get_db_connection()
        # ✅ FIXED: Don't modify isolation_level with pooled connections
        # Use explicit commit() instead of autocommit mode
        cursor = conn.cursor()
        
        # CRITICAL FIX: Ensure user row exists before UPDATE
        cursor.execute("SELECT id FROM ai_infrastructure.users WHERE id = %s", [user_id])
        if not cursor.fetchone():
            logger.info(f"🔧 [FIX] Creating user row for user_id {user_id}")
            cursor.execute("""
                INSERT INTO ai_infrastructure.users (id, username, email, password_hash, created_at, last_active, metadata)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, '{}')
            """, [user_id, f'user_{user_id}', f'user_{user_id}@ai-platform.local', 'SYSTEM_USER'])
        
        # Get existing metadata
        cursor.execute("""
            SELECT metadata FROM ai_infrastructure.users WHERE id = %s
        """, [user_id])
        
        row = cursor.fetchone()
        
        # Parse or create metadata (PostgreSQL returns tuple)
        metadata_value = row[0] if row else None
        if metadata_value:
            try:
                metadata = json.loads(metadata_value)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in user {user_id} metadata, resetting")
                metadata = {}
        else:
            metadata = {}
        
        # Update thread assignments
        metadata['thread_assignments'] = agent_assignments
        
        # Save back to database
        cursor.execute("""
            UPDATE ai_infrastructure.users 
            SET metadata = %s, last_active = CURRENT_TIMESTAMP
            WHERE id = %s
        """, [json.dumps(metadata), user_id])
        conn.commit()  # CRITICAL FIX: Commit the transaction
        
        logger.info(f"Saved {len(agent_assignments)} thread assignments for user {user_id}")
        
        return jsonify({
            'success': True,
            'saved': True,
            'count': len(agent_assignments)
        })
        
    except Exception as e:
        logger.error(f"Error saving thread assignments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@thread_assignment_bp.route('/api/thread-assignments/assign', methods=['POST'])
def assign_thread():
    """
    Assign thread to location with strict rule enforcement
    
    Request JSON:
        {
            "user_id": 1,
            "session_id": "1762192838469",
            "location": "agent-1"  // or "prime"
        }
    
    RULES ENFORCED:
    1. Thread can only be in ONE location (Prime OR one agent)
    2. Agent can only have ONE thread
    3. Most recent assignment wins - old assignments auto-removed
    
    Returns:
        {
            "success": true,
            "assignment": {
                "session_id": "1762192838469",
                "location": "agent-1",
                "previous_location": "agent-2",  // where thread was before (or null)
                "displaced_thread": "1762193002345"  // thread kicked out (or null)
            }
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        session_id = data.get('session_id')
        location = data.get('location', 'prime')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'session_id required'
            }), 400
        
        logger.info(f"📌 [ASSIGN] Thread {session_id} → {location} (user {user_id})")
        
        # Enforce rules and get what changed
        result = enforce_thread_assignment_rules(user_id, session_id, location)
        
        return jsonify({
            'success': True,
            'assignment': {
                'session_id': session_id,
                'location': location,
                'previous_location': result['previous_location'],
                'displaced_thread': result['displaced_thread']
            }
        })
        
    except Exception as e:
        import traceback
        logger.error(f"❌ Error assigning thread: {e}")
        logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@thread_assignment_bp.route('/api/agent/threads/<thread_id>/assign', methods=['POST'])
def assign_thread_by_id(thread_id):
    """
    Assign thread to location with strict rule enforcement (frontend-friendly URL)
    This is an alias for /api/thread-assignments/assign with URL path parameter
    
    URL parameter:
        thread_id: Thread ID from URL path
    
    Request JSON:
        {
            "location": "agent-1",  // or "prime"
            "agent_name": "Bravo-2"  // optional, for logging
        }
    
    RULES ENFORCED:
    1. Thread can only be in ONE location (Prime OR one agent)
    2. Agent can only have ONE thread
    3. Most recent assignment wins - old assignments auto-removed
    
    Returns:
        {
            "success": true,
            "assignment": {
                "session_id": "1762192838469",
                "location": "agent-1",
                "previous_location": "agent-2",  // where thread was before (or null)
                "displaced_thread": "1762193002345"  // thread kicked out (or null)
            }
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)
        location = data.get('location', 'prime')
        agent_name = data.get('agent_name', location)
        
        logger.info(f"📌 [ASSIGN] Thread {thread_id} → {location} ({agent_name}) [user {user_id}]")
        
        # Enforce rules and get what changed
        result = enforce_thread_assignment_rules(user_id, thread_id, location)
        
        return jsonify({
            'success': True,
            'assignment': {
                'session_id': thread_id,
                'location': location,
                'previous_location': result['previous_location'],
                'displaced_thread': result['displaced_thread']
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Error assigning thread {thread_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@thread_assignment_bp.route('/api/thread-assignments/clear/<location>', methods=['POST'])
def clear_location(location):
    """
    Clear a specific agent location
    
    URL params:
        location: Agent location (agent-1, agent-2, etc.)
    
    Query params:
        user_id: User ID (default: 1)
    
    Returns:
        {
            "success": true,
            "cleared": "agent-1"
        }
    """
    conn = None
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT metadata FROM ai_infrastructure.users WHERE id = %s", [user_id])
        row = cursor.fetchone()
        
        metadata_value = row[0] if row else None
        if metadata_value:
            try:
                metadata = json.loads(metadata_value)
                assignments = metadata.get('thread_assignments', {})
                
                if location in assignments:
                    previous = assignments[location]
                    del assignments[location]
                    
                    metadata['thread_assignments'] = assignments
                    
                    cursor.execute("""
                        UPDATE ai_infrastructure.users 
                        SET metadata = %s
                        WHERE id = %s
                    """, [json.dumps(metadata), user_id])
                    
                    conn.commit()
                    logger.info(f"Cleared {location} (was {previous})")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in metadata for user {user_id}")
        
        return jsonify({
            'success': True,
            'cleared': location
        })
        
    except Exception as e:
        logger.error(f"Error clearing location: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@thread_assignment_bp.route('/api/thread-assignments/location/<session_id>', methods=['GET'])
def get_thread_location(session_id):
    """
    Find which location a thread is assigned to
    
    URL params:
        session_id: Thread session ID
    
    Query params:
        user_id: User ID (default: 1)
    
    Returns:
        {
            "success": true,
            "session_id": "1762192838469",
            "location": "agent-1"  // or null if not in any agent
        }
    """
    conn = None
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT metadata FROM ai_infrastructure.users WHERE id = %s", [user_id])
        row = cursor.fetchone()
        
        metadata_value = row[0] if row else None
        if metadata_value:
            try:
                metadata = json.loads(metadata_value)
                assignments = metadata.get('thread_assignments', {})
                
                # Find location for this thread
                for location, sid in assignments.items():
                    if sid == session_id:
                        return jsonify({
                            'success': True,
                            'session_id': session_id,
                            'location': location
                        })
            except json.JSONDecodeError:
                pass
        
        # Not found in any agent - means it's in Prime (or unassigned)
        return jsonify({
            'success': True,
            'session_id': session_id,
            'location': None  # null = Prime or unassigned
        })
        
    except Exception as e:
        logger.error(f"Error getting thread location: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


@thread_assignment_bp.route('/api/thread-assignments/validate', methods=['POST'])
def validate_assignments():
    """
    Validate and fix assignment inconsistencies
    (Simple version - just checks for basic issues)
    
    Query params:
        user_id: User ID (default: 1)
    
    Returns:
        {
            "success": true,
            "valid": true,
            "errors": [],
            "fixed": 0
        }
    """
    conn = None
    try:
        user_id = request.args.get('user_id', 1, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT metadata FROM ai_infrastructure.users WHERE id = %s", [user_id])
        row = cursor.fetchone()
        
        errors = []
        fixed = 0
        
        metadata_value = row[0] if row else None
        if metadata_value:
            try:
                metadata = json.loads(metadata_value)
                assignments = metadata.get('thread_assignments', {})
                
                # Check for duplicate thread assignments
                seen = {}
                duplicates = []
                
                for location, session_id in assignments.items():
                    if session_id in seen:
                        duplicates.append(session_id)
                        errors.append(f"Thread {session_id} in multiple locations: {seen[session_id]}, {location}")
                    else:
                        seen[session_id] = location
                
                # Remove duplicates (keep first occurrence)
                if duplicates:
                    for session_id in duplicates:
                        first_location = seen[session_id]
                        for location in list(assignments.keys()):
                            if assignments[location] == session_id and location != first_location:
                                del assignments[location]
                                fixed += 1
                    
                    # Save fixed metadata
                    metadata['thread_assignments'] = assignments
                    cursor.execute("""
                        UPDATE ai_infrastructure.users SET metadata = %s WHERE id = %s
                    """, [json.dumps(metadata), user_id])
                    conn.commit()
                
            except json.JSONDecodeError:
                errors.append("Invalid JSON in metadata")
        
        logger.info(f"Validation complete: {len(errors)} errors, {fixed} fixed")
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'fixed': fixed
        })
        
    except Exception as e:
        logger.error(f"Error validating assignments: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if conn:
            conn.close()


