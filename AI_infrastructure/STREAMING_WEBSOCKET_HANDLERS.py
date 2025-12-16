"""
STREAMING WEBSOCKET HANDLERS
Add this code to flask_app.py for inline interaction system

This implements the /ws/streaming namespace for AI agent inline interaction.
Separate from /ws/synergy (Synergy Board) to avoid conflicts.

Date: December 17, 2025
"""

# ==================== SESSION REGISTRY ====================
# Global registry to track active StreamingManager sessions
# This allows WebSocket messages to route to the correct session

from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Global dictionary: session_id -> StreamingSession instance
streaming_sessions: Dict[str, 'StreamingSession'] = {}


def register_streaming_session(session_id: str, session):
    """
    Register a streaming session for WebSocket message routing.
    Called automatically when StreamingSession is created.
    
    Args:
        session_id: Unique session identifier
        session: StreamingSession instance
    """
    streaming_sessions[session_id] = session
    logger.info(f'[STREAMING] ✅ Registered session: {session_id}')


def unregister_streaming_session(session_id: str):
    """
    Unregister a streaming session.
    Called automatically when StreamingSession closes.
    
    Args:
        session_id: Session identifier to remove
    """
    if session_id in streaming_sessions:
        del streaming_sessions[session_id]
        logger.info(f'[STREAMING] ✅ Unregistered session: {session_id}')


def get_streaming_session(session_id: str):
    """
    Get a streaming session by ID.
    Returns None if session not found.
    
    Args:
        session_id: Session identifier
        
    Returns:
        StreamingSession instance or None
    """
    return streaming_sessions.get(session_id)


# ==================== SOCKET.IO HANDLERS ====================
# Add these handlers to flask_app.py (after existing @socketio.on handlers)

"""
# PASTE THIS INTO flask_app.py (around line 1000+, after /ws/synergy handlers):

# ==================== AGENT STREAMING NAMESPACE ====================
# Dedicated namespace for AI agent inline interaction system
# Used by: agent-interaction-websocket.js (frontend)
# Purpose: Real-time two-way communication (input requests, progress updates)
# Separate from /ws/synergy to avoid conflicts with Synergy Board

@socketio.on('connect', namespace='/ws/streaming')
def handle_streaming_connect():
    '''
    Handle agent streaming connection for inline interaction.
    Each agent gets its own session_id for isolation.
    
    URL format: ws://localhost:5000/ws/streaming?session_id=abc-123
    '''
    from flask import request
    from flask_socketio import join_room, emit
    
    session_id = request.args.get('session_id')
    client_id = request.sid
    
    if not session_id:
        logger.error(f'[STREAMING] ❌ Connection rejected - no session_id')
        return False
    
    # Join session-specific room
    join_room(session_id, namespace='/ws/streaming')
    
    logger.info(f'[STREAMING] ✅ Agent session connected: {session_id} (client: {client_id})')
    
    # Send handshake confirmation to client
    emit('connected', {
        'session_id': session_id,
        'status': 'connected',
        'timestamp': datetime.now().isoformat()
    }, namespace='/ws/streaming')
    
    return True


@socketio.on('disconnect', namespace='/ws/streaming')
def handle_streaming_disconnect():
    '''Handle agent streaming disconnection'''
    from flask import request
    
    client_id = request.sid
    logger.info(f'[STREAMING] 🔌 Client disconnected: {client_id}')


@socketio.on('handshake', namespace='/ws/streaming')
def handle_streaming_handshake(data):
    '''
    Handle initial handshake from agent.
    
    Message format:
    {
        'type': 'handshake',
        'participant': 'user_123',
        'agent_id': 1
    }
    '''
    from flask_socketio import emit
    
    agent_id = data.get('agent_id')
    participant = data.get('participant')
    
    logger.info(f'[STREAMING] 🤝 Handshake from agent {agent_id}: {participant}')
    
    emit('handshake_ack', {
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    }, namespace='/ws/streaming')


@socketio.on('provide_input', namespace='/ws/streaming')
async def handle_streaming_provide_input(data):
    '''
    Handle user input submission from inline interaction bubble.
    This is called when user clicks Submit in the bubble UI.
    
    Message format from frontend:
    {
        'type': 'provide_input',
        'session_id': 'abc-123',
        'request_id': 'req-456',
        'input_value': 'user response',
        'from_participant': 'user_789',
        'timestamp': '2025-12-17T...'
    }
    '''
    from flask_socketio import emit
    
    session_id = data.get('session_id')
    request_id = data.get('request_id')
    input_value = data.get('input_value')
    from_participant = data.get('from_participant', 'unknown')
    
    logger.info(f'[STREAMING] 📥 Input received for session {session_id}: {input_value}')
    
    # Find the StreamingSession instance
    session = get_streaming_session(session_id)
    
    if session:
        try:
            # Provide input to the session (unblocks waiting AI task)
            await session.provide_input(input_value, from_participant)
            
            logger.info(f'[STREAMING] ✅ Input provided to session {session_id}')
            
            # Confirm receipt to client
            emit('input_received', {
                'request_id': request_id,
                'status': 'received',
                'timestamp': datetime.now().isoformat()
            }, room=session_id, namespace='/ws/streaming')
            
        except Exception as e:
            logger.error(f'[STREAMING] ❌ Error providing input: {str(e)}')
            emit('error', {
                'message': f'Error processing input: {str(e)}',
                'request_id': request_id
            }, namespace='/ws/streaming')
    else:
        logger.error(f'[STREAMING] ❌ Session not found: {session_id}')
        emit('error', {
            'message': f'Session {session_id} not found or expired',
            'request_id': request_id
        }, namespace='/ws/streaming')


@socketio.on('ping', namespace='/ws/streaming')
def handle_streaming_ping():
    '''Handle keepalive ping from client'''
    from flask_socketio import emit
    emit('pong', {'timestamp': datetime.now().isoformat()}, namespace='/ws/streaming')


# END OF CODE TO PASTE INTO flask_app.py
'''


# ==================== STREAMING MANAGER INTEGRATION ====================
# Add these methods to StreamingSession class in streaming_manager.py

'''
# PASTE THIS INTO streaming_manager.py - StreamingSession class:

def __init__(self, session_id: str, websocket: WebSocket = None, task_function: Callable = None):
    """
    Initialize streaming session.
    
    Args:
        session_id: Unique session identifier
        websocket: WebSocket connection (optional if using Socket.IO)
        task_function: Async function to execute
    """
    self.session_id = session_id
    self.websocket = websocket
    self.task_function = task_function
    
    # ... existing initialization code ...
    
    # ✅ AUTO-REGISTER SESSION FOR WEBSOCKET ROUTING
    # This allows Socket.IO handlers to find this session
    from flask_app import register_streaming_session
    register_streaming_session(session_id, self)
    
    logger.info(f"[SESSION {session_id}] ✅ Created and registered")


async def close(self):
    """Close session and cleanup resources"""
    
    # ... existing cleanup code ...
    
    # ✅ AUTO-UNREGISTER SESSION
    from flask_app import unregister_streaming_session
    unregister_streaming_session(self.session_id)
    
    logger.info(f"[SESSION {self.session_id}] ✅ Closed and unregistered")
    
    self.state = SessionState.COMPLETED
'''


# ==================== USAGE EXAMPLE ====================
# How to use the streaming system in your AI agent code

'''
from core.streaming_manager import StreamingSession, SessionState

async def example_ai_task_with_interaction():
    """
    Example AI task that requests user input during execution.
    This demonstrates the two-way interaction pattern.
    """
    
    # Create session (auto-registers for WebSocket routing)
    session = StreamingSession(
        session_id=str(uuid.uuid4()),
        task_function=None  # Or pass async function
    )
    
    try:
        # Stream progress to user
        await session.stream_progress("Starting task...", 1, 5)
        
        # Do some work...
        await asyncio.sleep(1)
        
        # Request user input (blocks here until user responds)
        code = await session.request_user_input(
            prompt="Enter your 2FA authentication code",
            input_type="2fa_code",
            required=True,
            timeout_seconds=300
        )
        
        # Continue with user's input
        logger.info(f"Received 2FA code: {code}")
        
        # More progress...
        await session.stream_progress("Authenticating...", 2, 5)
        await asyncio.sleep(1)
        
        # Request choice from user
        choice = await session.request_user_input(
            prompt="Select deployment environment",
            input_type="choice",
            options=["Development", "Staging", "Production"],
            required=True,
            timeout_seconds=120
        )
        
        logger.info(f"User selected: {choice}")
        
        # Final progress
        await session.stream_progress("Completed!", 5, 5)
        
    except TimeoutError:
        logger.error("User input timeout")
        await session.fail("User did not respond in time")
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        await session.fail(str(e))
        
    finally:
        # Cleanup (auto-unregisters)
        await session.close()


# Call from Flask route:
@app.route('/api/agent/start_task', methods=['POST'])
async def start_agent_task():
    """Start an AI agent task with user interaction"""
    
    # Create and run task
    task = asyncio.create_task(example_ai_task_with_interaction())
    
    return jsonify({
        'status': 'started',
        'message': 'Task running - check WebSocket for updates'
    })
'''


# ==================== TESTING ====================
# Test the streaming system end-to-end

'''
# Test in Python:

async def test_streaming():
    """Test the streaming system"""
    
    # Create session
    session_id = str(uuid.uuid4())
    session = StreamingSession(session_id=session_id)
    
    # Simulate AI requesting input
    async def request_input():
        await asyncio.sleep(2)
        result = await session.request_user_input(
            prompt="Enter test value",
            input_type="text",
            timeout_seconds=60
        )
        print(f"✅ Received: {result}")
    
    # Start task
    task = asyncio.create_task(request_input())
    
    # Simulate user providing input (via WebSocket)
    await asyncio.sleep(3)
    await session.provide_input("test response", "user_123")
    
    # Wait for completion
    await task
    await session.close()


# Run test:
if __name__ == '__main__':
    asyncio.run(test_streaming())
'''

"""

print("✅ STREAMING_WEBSOCKET_HANDLERS.py created")
print("")
print("📋 NEXT STEPS:")
print("1. Copy Socket.IO handlers from this file to flask_app.py")
print("2. Copy session registry functions to flask_app.py")
print("3. Update StreamingSession.__init__ and close() methods")
print("4. Restart Flask server")
print("5. Test with: testInteractionBubble(1) in browser console")
print("")
print("📖 See SYNERGY_ROUTES_ANALYSIS.md for full details")
