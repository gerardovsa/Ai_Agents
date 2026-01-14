"""
StreamingManager - Two-Way Interaction Framework
=================================================

GLOBAL PLATFORM SERVICE for real-time bidirectional communication between:
- AI agents executing long-running tasks
- Users monitoring progress and providing input
- Multiple concurrent sessions

This is the CORE interaction framework that enables:
✅ Live progress streaming (step-by-step updates)
✅ User input prompts (2FA codes, CAPTCHA solving, choices)
✅ Pause/Resume capability for long-running tasks
✅ Screenshot/action streaming (for computer use tasks)
✅ Multi-participant collaboration (AI + human)
✅ Session state persistence and recovery

Used By:
- Professional Verification Module (credential searches with 2FA)
- Computer Use tasks (browser automation with user oversight)
- Any long-running AI agent task requiring interaction
- Collaborative editing (CAD, documents, etc.)

Architecture:
- WebSocket-based real-time communication
- Session-based state management
- Queue system for async task execution
- User input blocking/resumption pattern
- Screenshot/artifact streaming

Created: December 16, 2025
Author: AI Agent Platform - Two-Way Interaction Framework
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import asyncio
import uuid
import json
import logging
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class SessionState(Enum):
    """Session lifecycle states"""
    CREATED = "created"
    RUNNING = "running"
    WAITING_FOR_INPUT = "waiting_for_input"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageType(Enum):
    """WebSocket message types"""
    # Progress updates
    PROGRESS = "progress"
    STEP_STARTED = "step_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    
    # User input requests
    INPUT_REQUEST = "input_request"
    INPUT_RECEIVED = "input_received"
    
    # Action streaming (computer use)
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    SCREENSHOT = "screenshot"
    
    # Session control
    SESSION_STARTED = "session_started"
    SESSION_PAUSED = "session_paused"
    SESSION_RESUMED = "session_resumed"
    SESSION_COMPLETED = "session_completed"
    SESSION_FAILED = "session_failed"
    
    # Participant management
    PARTICIPANT_JOINED = "participant_joined"
    PARTICIPANT_LEFT = "participant_left"
    
    # General messages
    LOG = "log"
    ERROR = "error"


@dataclass
class ProgressUpdate:
    """Progress update data structure"""
    current_step: int
    total_steps: int
    message: str
    percentage: float = None
    metadata: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.percentage is None and self.total_steps > 0:
            self.percentage = (self.current_step / self.total_steps) * 100
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class InputRequest:
    """User input request data structure"""
    request_id: str
    prompt: str
    input_type: str  # text, password, choice, 2fa_code, captcha, file_upload
    options: List[str] = None  # For choice type
    required: bool = True
    timeout_seconds: int = 300  # 5 minute default
    metadata: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ActionUpdate:
    """Action/operation update (for computer use tasks)"""
    action_id: str
    action_type: str  # screenshot, mouse_move, click, type, bash_command
    status: str  # started, completed, failed
    description: str
    result: Any = None
    screenshot_data: str = None  # Base64 encoded
    metadata: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class StreamingSession:
    """
    Represents a single streaming session with one or more participants.
    
    Each session manages:
    - Task state and progress
    - Connected WebSocket clients
    - User input requests/responses
    - Action history
    - Pause/resume state
    """
    
    def __init__(self, session_id: str, task_name: str, created_by: str):
        self.session_id = session_id
        self.task_name = task_name
        self.created_by = created_by
        self.state = SessionState.CREATED
        
        # Participants
        self.participants: Dict[str, WebSocket] = {}  # participant_id -> websocket
        self.participant_types: Dict[str, str] = {}  # participant_id -> "user"|"ai"|"observer"
        
        # State management
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        
        # Progress tracking
        self.current_step = 0
        self.total_steps = 0
        self.progress_history: List[ProgressUpdate] = []
        
        # User input handling
        self.pending_input_request: Optional[InputRequest] = None
        self.input_response: Optional[Any] = None
        self.input_event = asyncio.Event()  # For blocking until input received
        
        # Pause/resume
        self.pause_event = asyncio.Event()
        self.pause_event.set()  # Not paused initially
        self.pause_reason: Optional[str] = None
        
        # Action history
        self.action_history: List[ActionUpdate] = []
        
        # Task executor
        self.task_coroutine: Optional[Callable] = None
        self.task_result: Any = None
        self.task_error: Optional[Exception] = None
        
        # ✅ AUTO-REGISTER SESSION FOR WEBSOCKET ROUTING
        # This allows Socket.IO handlers in flask_app.py to find this session
        try:
            # Lazy import to avoid circular dependency
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from flask_app import register_streaming_session
            register_streaming_session(session_id, self)
            logger.info(f"[SESSION {session_id}] ✅ Created and registered for WebSocket routing")
        except ImportError as e:
            logger.warning(f"[SESSION {session_id}] ⚠️ Could not register session (flask_app not available): {e}")
    
    async def add_participant(self, websocket: WebSocket, participant_type: str = "user") -> str:
        """Add participant to session"""
        participant_id = str(uuid.uuid4())
        self.participants[participant_id] = websocket
        self.participant_types[participant_type] = participant_type
        self.updated_at = datetime.now()
        
        logger.info(f"[SESSION {self.session_id}] Participant {participant_id} joined as {participant_type}")
        
        # Send initial state
        await websocket.send_json({
            "type": MessageType.SESSION_STARTED.value,
            "session_id": self.session_id,
            "participant_id": participant_id,
            "task_name": self.task_name,
            "state": self.state.value,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "participant_count": len(self.participants)
        })
        
        # Notify others
        await self.broadcast({
            "type": MessageType.PARTICIPANT_JOINED.value,
            "participant_id": participant_id,
            "participant_type": participant_type,
            "participant_count": len(self.participants)
        }, exclude={participant_id})
        
        return participant_id
    
    def remove_participant(self, participant_id: str):
        """Remove participant from session"""
        if participant_id in self.participants:
            del self.participants[participant_id]
            del self.participant_types[participant_id]
            self.updated_at = datetime.now()
            logger.info(f"[SESSION {self.session_id}] Participant {participant_id} left")
    
    async def broadcast(self, message: Dict, exclude: set = None):
        """Send message to all participants except excluded ones"""
        exclude = exclude or set()
        disconnected = []
        
        for pid, ws in self.participants.items():
            if pid in exclude:
                continue
            
            try:
                await ws.send_json(message)
            except Exception as e:
                logger.warning(f"[SESSION {self.session_id}] Failed to send to {pid}: {e}")
                disconnected.append(pid)
        
        # Clean up disconnected participants
        for pid in disconnected:
            self.remove_participant(pid)
    
    async def stream_progress(self, current: int, total: int, message: str, metadata: Dict = None):
        """
        Stream progress update to all participants.
        
        Args:
            current: Current step number (1-indexed)
            total: Total number of steps
            message: Human-readable progress message
            metadata: Optional additional data
        """
        self.current_step = current
        self.total_steps = total
        self.updated_at = datetime.now()
        
        progress = ProgressUpdate(
            current_step=current,
            total_steps=total,
            message=message,
            metadata=metadata
        )
        
        self.progress_history.append(progress)
        
        await self.broadcast({
            "type": MessageType.PROGRESS.value,
            **asdict(progress)
        })
        
        logger.info(f"[SESSION {self.session_id}] Progress: {current}/{total} - {message}")
    
    async def request_user_input(
        self,
        prompt: str,
        input_type: str = "text",
        options: List[str] = None,
        required: bool = True,
        timeout_seconds: int = 300,
        metadata: Dict = None
    ) -> Any:
        """
        Request input from user and block until received.
        
        This is the KEY method for two-way interaction - the AI agent can pause
        its execution and wait for human input (2FA code, CAPTCHA solve, choice, etc.)
        
        Args:
            prompt: Question/instruction for user
            input_type: Type of input (text, password, choice, 2fa_code, captcha)
            options: List of choices (for choice type)
            required: Whether input is required
            timeout_seconds: How long to wait before timing out
            metadata: Additional data (e.g., screenshot of CAPTCHA)
        
        Returns:
            User's input value
        
        Raises:
            TimeoutError: If user doesn't respond within timeout
        """
        request_id = str(uuid.uuid4())
        
        self.state = SessionState.WAITING_FOR_INPUT
        self.pending_input_request = InputRequest(
            request_id=request_id,
            prompt=prompt,
            input_type=input_type,
            options=options,
            required=required,
            timeout_seconds=timeout_seconds,
            metadata=metadata
        )
        self.input_response = None
        self.input_event.clear()
        
        # Broadcast input request
        await self.broadcast({
            "type": MessageType.INPUT_REQUEST.value,
            **asdict(self.pending_input_request)
        })
        
        logger.info(f"[SESSION {self.session_id}] Waiting for user input: {prompt}")
        
        # Wait for input with timeout
        try:
            await asyncio.wait_for(self.input_event.wait(), timeout=timeout_seconds)
            logger.info(f"[SESSION {self.session_id}] Received user input")
            self.state = SessionState.RUNNING
            return self.input_response
        except asyncio.TimeoutError:
            logger.error(f"[SESSION {self.session_id}] Input request timed out")
            self.state = SessionState.FAILED
            raise TimeoutError(f"User input not received within {timeout_seconds} seconds")
    
    async def provide_input(self, input_value: Any, from_participant: str):
        """
        Provide user input response (called from WebSocket handler when user submits).
        
        Args:
            input_value: The user's input
            from_participant: Participant ID who provided input
        """
        if self.pending_input_request is None:
            logger.warning(f"[SESSION {self.session_id}] Received input but no request pending")
            return
        
        self.input_response = input_value
        self.pending_input_request = None
        self.input_event.set()  # Unblock the waiting task
        
        await self.broadcast({
            "type": MessageType.INPUT_RECEIVED.value,
            "from_participant": from_participant,
            "timestamp": datetime.now().isoformat()
        })
    
    async def pause(self, reason: str = None):
        """Pause the session (user-initiated or automatic)"""
        self.pause_event.clear()
        self.state = SessionState.PAUSED
        self.pause_reason = reason
        self.updated_at = datetime.now()
        
        await self.broadcast({
            "type": MessageType.SESSION_PAUSED.value,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"[SESSION {self.session_id}] Paused: {reason}")
    
    async def resume(self):
        """Resume the session"""
        self.pause_event.set()
        self.state = SessionState.RUNNING
        self.pause_reason = None
        self.updated_at = datetime.now()
        
        await self.broadcast({
            "type": MessageType.SESSION_RESUMED.value,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"[SESSION {self.session_id}] Resumed")
    
    async def wait_if_paused(self):
        """
        Check if session is paused and wait until resumed.
        Tasks should call this periodically to respect pause state.
        """
        await self.pause_event.wait()
    
    async def stream_action(
        self,
        action_type: str,
        status: str,
        description: str,
        result: Any = None,
        screenshot_data: str = None,
        metadata: Dict = None
    ):
        """
        Stream action/operation update (for computer use tasks).
        
        Args:
            action_type: Type of action (screenshot, mouse_move, click, type, etc.)
            status: Action status (started, completed, failed)
            description: Human-readable description
            result: Action result data
            screenshot_data: Base64-encoded screenshot
            metadata: Additional data
        """
        action_id = str(uuid.uuid4())
        
        action = ActionUpdate(
            action_id=action_id,
            action_type=action_type,
            status=status,
            description=description,
            result=result,
            screenshot_data=screenshot_data,
            metadata=metadata
        )
        
        self.action_history.append(action)
        
        message_type = (
            MessageType.ACTION_STARTED if status == "started"
            else MessageType.ACTION_COMPLETED if status == "completed"
            else MessageType.STEP_FAILED
        )
        
        await self.broadcast({
            "type": message_type.value,
            **asdict(action)
        })
        
        logger.info(f"[SESSION {self.session_id}] Action {status}: {action_type} - {description}")
    
    async def stream_screenshot(self, screenshot_data: str, description: str, metadata: Dict = None):
        """Stream screenshot to participants"""
        await self.broadcast({
            "type": MessageType.SCREENSHOT.value,
            "screenshot_data": screenshot_data,
            "description": description,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
    
    async def log(self, message: str, level: str = "info", metadata: Dict = None):
        """Send log message to participants"""
        await self.broadcast({
            "type": MessageType.LOG.value,
            "level": level,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
    
    async def complete(self, result: Any = None):
        """Mark session as completed"""
        self.state = SessionState.COMPLETED
        self.completed_at = datetime.now()
        self.task_result = result
        
        await self.broadcast({
            "type": MessageType.SESSION_COMPLETED.value,
            "result": result,
            "duration_seconds": (self.completed_at - self.started_at).total_seconds() if self.started_at else None,
            "timestamp": self.completed_at.isoformat()
        })
        
        logger.info(f"[SESSION {self.session_id}] Completed")
        
        # ✅ AUTO-UNREGISTER SESSION
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from flask_app import unregister_streaming_session
            unregister_streaming_session(self.session_id)
            logger.info(f"[SESSION {self.session_id}] ✅ Unregistered from WebSocket routing")
        except ImportError as e:
            logger.warning(f"[SESSION {self.session_id}] ⚠️ Could not unregister session: {e}")
    
    async def fail(self, error: Exception):
        """Mark session as failed"""
        self.state = SessionState.FAILED
        self.completed_at = datetime.now()
        self.task_error = error
        
        await self.broadcast({
            "type": MessageType.SESSION_FAILED.value,
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": self.completed_at.isoformat()
        })
        
        logger.error(f"[SESSION {self.session_id}] Failed: {error}")
        
        # ✅ AUTO-UNREGISTER SESSION
        try:
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from flask_app import unregister_streaming_session
            unregister_streaming_session(self.session_id)
            logger.info(f"[SESSION {self.session_id}] ✅ Unregistered from WebSocket routing")
        except ImportError as e:
            logger.warning(f"[SESSION {self.session_id}] ⚠️ Could not unregister session: {e}")


class StreamingManager:
    """
    SINGLETON - Global manager for all streaming sessions.
    
    Provides the platform-wide two-way interaction framework.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.sessions: Dict[str, StreamingSession] = {}
        logger.info("[STREAMING_MANAGER] Initialized")
    
    def create_session(self, task_name: str, created_by: str) -> StreamingSession:
        """Create a new streaming session"""
        session_id = str(uuid.uuid4())
        session = StreamingSession(session_id, task_name, created_by)
        self.sessions[session_id] = session
        
        logger.info(f"[STREAMING_MANAGER] Created session {session_id} for task: {task_name}")
        return session
    
    def get_session(self, session_id: str) -> Optional[StreamingSession]:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id: str):
        """Remove session (cleanup after completion)"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"[STREAMING_MANAGER] Removed session {session_id}")
    
    def get_active_sessions(self) -> List[Dict]:
        """Get list of active sessions (for monitoring dashboard)"""
        return [
            {
                "session_id": s.session_id,
                "task_name": s.task_name,
                "state": s.state.value,
                "created_by": s.created_by,
                "created_at": s.created_at.isoformat(),
                "participant_count": len(s.participants),
                "progress": f"{s.current_step}/{s.total_steps}" if s.total_steps > 0 else "N/A"
            }
            for s in self.sessions.values()
        ]
    
    async def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Clean up sessions older than max_age_hours"""
        now = datetime.now()
        to_remove = []
        
        for session_id, session in self.sessions.items():
            age_hours = (now - session.created_at).total_seconds() / 3600
            if age_hours > max_age_hours and session.state in [SessionState.COMPLETED, SessionState.FAILED]:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            self.remove_session(session_id)
        
        if to_remove:
            logger.info(f"[STREAMING_MANAGER] Cleaned up {len(to_remove)} inactive sessions")


# Singleton getter
def get_streaming_manager() -> StreamingManager:
    """Get the global StreamingManager instance"""
    return StreamingManager()


# Example usage pattern
async def example_verification_task(session: StreamingSession, candidate_data: Dict):
    """
    Example: Professional verification task with user interaction
    """
    try:
        session.state = SessionState.RUNNING
        session.started_at = datetime.now()
        
        # Step 1: Parse resume
        await session.wait_if_paused()
        await session.stream_progress(1, 5, "Parsing resume...")
        resume_data = {}  # parse_resume(candidate_data['resume'])
        
        # Step 2: Verify GitHub
        await session.wait_if_paused()
        await session.stream_progress(2, 5, "Verifying GitHub profile...")
        
        # Simulate encountering 2FA
        code = await session.request_user_input(
            prompt="GitHub requires 2FA code. Please enter the code from your authenticator app:",
            input_type="2fa_code",
            timeout_seconds=300
        )
        
        # Continue with the code
        await session.log(f"Received 2FA code, continuing verification...")
        
        # Step 3: Check credential registry (with browser automation)
        await session.wait_if_paused()
        await session.stream_progress(3, 5, "Searching credential registry...")
        
        # Stream browser action
        await session.stream_action(
            action_type="navigate",
            status="started",
            description="Navigating to AHPRA registry search"
        )
        
        # Take screenshot
        screenshot_b64 = "..."  # get screenshot
        await session.stream_screenshot(screenshot_b64, "Registry search form")
        
        await session.stream_action(
            action_type="form_fill",
            status="completed",
            description="Filled in candidate details"
        )
        
        # Step 4: Compile results
        await session.wait_if_paused()
        await session.stream_progress(4, 5, "Compiling verification results...")
        
        # Step 5: Complete
        await session.stream_progress(5, 5, "Verification complete!")
        
        result = {
            "verified": True,
            "risk_score": 15,
            "findings": ["All credentials verified"]
        }
        
        await session.complete(result)
        
    except Exception as e:
        await session.fail(e)
        raise
