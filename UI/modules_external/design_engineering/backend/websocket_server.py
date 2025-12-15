"""
WebSocket Collaboration Server
Real-time CAD collaboration between humans and AI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime
import uuid

from operational_transform import (
    Patch, PatchActor, PatchOperation,
    SceneGraphManager, OperationalTransform
)


app = FastAPI(title="CAD Collaboration Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CollaborationSession:
    """
    Manages a single CAD design collaboration session
    Multiple participants (humans + AI) can join
    """
    
    def __init__(self, session_id: str, design_name: str = "Untitled"):
        self.session_id = session_id
        self.design_name = design_name
        self.scene_manager = SceneGraphManager()
        self.participants: Dict[str, WebSocket] = {}  # participant_id -> websocket
        self.participant_types: Dict[str, str] = {}  # participant_id -> "human"|"ai"
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        
        # AI agent state
        self.ai_analyzing = False
        self.ai_focus_objects: List[str] = []
        
    async def add_participant(self, websocket: WebSocket, participant_type: str = "human") -> str:
        """Add participant to session"""
        participant_id = str(uuid.uuid4())
        self.participants[participant_id] = websocket
        self.participant_types[participant_id] = participant_type
        self.last_activity = datetime.now()
        
        # Send initial state
        await websocket.send_json({
            "type": "INITIAL_STATE",
            "data": self.scene_manager.get_state(),
            "session_id": self.session_id,
            "participant_id": participant_id,
            "participant_count": len(self.participants)
        })
        
        # Notify others
        await self.broadcast({
            "type": "PARTICIPANT_JOINED",
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
            self.last_activity = datetime.now()
    
    async def broadcast(self, message: Dict, exclude: Set[str] = None):
        """Send message to all participants except excluded ones"""
        exclude = exclude or set()
        
        disconnected = []
        for pid, ws in self.participants.items():
            if pid in exclude:
                continue
            
            try:
                await ws.send_json(message)
            except:
                disconnected.append(pid)
        
        # Clean up disconnected participants
        for pid in disconnected:
            self.remove_participant(pid)
    
    async def handle_patch(self, participant_id: str, patch_data: Dict):
        """Handle patch from participant"""
        self.last_activity = datetime.now()
        
        # Parse patch
        patch = Patch.from_dict(patch_data)
        
        # Validate and apply
        success, error = self.scene_manager.apply_patch(patch)
        
        if success:
            # Broadcast to all other participants
            await self.broadcast({
                "type": "PATCH",
                "patch": patch.to_dict(),
                "from_participant": participant_id,
                "version": self.scene_manager.version
            }, exclude={participant_id})
            
            # Send confirmation to sender
            await self.participants[participant_id].send_json({
                "type": "PATCH_APPLIED",
                "patch_id": patch.patch_id,
                "version": self.scene_manager.version
            })
            
            # Trigger AI analysis if it's a human change
            if self.participant_types[participant_id] == "human":
                await self.trigger_ai_analysis(patch)
        else:
            # Send error to sender
            await self.participants[participant_id].send_json({
                "type": "PATCH_REJECTED",
                "patch_id": patch.patch_id,
                "error": error
            })
    
    async def trigger_ai_analysis(self, triggering_patch: Patch):
        """
        Trigger AI to analyze design after user change
        This runs in the background
        """
        if self.ai_analyzing:
            return  # AI already analyzing
        
        self.ai_analyzing = True
        
        # Notify all participants
        await self.broadcast({
            "type": "AI_ANALYZING",
            "message": "AI is analyzing your changes..."
        })
        
        # TODO: Actual AI analysis would go here
        # For now, simulate with asyncio.sleep
        await asyncio.sleep(2)
        
        # Example: AI suggests adding a support beam
        ai_suggestion = Patch(
            op=PatchOperation.ADD,
            path=f"/objects/support_beam_{uuid.uuid4().hex[:8]}",
            value={
                "type": "t-slot-beam",
                "profile": "40x40_standard",
                "position": {"x": 900, "y": 0, "z": -600},
                "length": 1400,
                "created_by": "ai"
            },
            actor=PatchActor.AI,
            reason="Adding center support to reduce deflection by 60%"
        )
        
        # Send as suggestion (not auto-applied)
        await self.broadcast({
            "type": "AI_SUGGESTION",
            "patches": [ai_suggestion.to_dict()],
            "explanation": "I noticed the main beam might deflect excessively under load. Consider adding a center support beam.",
            "preview_svg": self._generate_preview_svg([ai_suggestion])
        })
        
        self.ai_analyzing = False
    
    def _generate_preview_svg(self, patches: List[Patch]) -> str:
        """Generate SVG preview with suggested changes"""
        # TODO: Actual SVG generation
        return "<svg>...</svg>"
    
    async def handle_ai_request(self, participant_id: str, request_data: Dict):
        """Handle explicit AI request from user"""
        question = request_data.get("question", "")
        context = request_data.get("context", {})
        
        # Notify all participants
        await self.broadcast({
            "type": "AI_THINKING",
            "message": f"AI is analyzing: {question}"
        })
        
        # TODO: Actual AI agent processing
        # For now, simulate
        await asyncio.sleep(3)
        
        # Example AI response
        response = {
            "type": "AI_RESPONSE",
            "question": question,
            "answer": "Based on my analysis, the structure looks good but could benefit from additional bracing.",
            "patches": [],  # AI-suggested changes
            "references": ["Section 3.2: Structural Load Analysis"]
        }
        
        await self.participants[participant_id].send_json(response)
    
    async def handle_ai_cursor_update(self, object_ids: List[str]):
        """Update where AI is "looking" """
        self.ai_focus_objects = object_ids
        
        await self.broadcast({
            "type": "AI_CURSOR",
            "object_ids": object_ids,
            "timestamp": datetime.now().isoformat()
        })
    
    async def apply_ai_suggestion(self, participant_id: str, patch_ids: List[str]):
        """User accepted AI suggestion"""
        # TODO: Apply the accepted patches
        pass


# Global session manager
class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, CollaborationSession] = {}
    
    def create_session(self, design_name: str = "Untitled") -> str:
        """Create new collaboration session"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = CollaborationSession(session_id, design_name)
        return session_id
    
    def get_session(self, session_id: str) -> CollaborationSession:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    def cleanup_old_sessions(self):
        """Remove inactive sessions"""
        now = datetime.now()
        to_remove = []
        
        for sid, session in self.sessions.items():
            # Remove sessions inactive for > 1 hour
            if (now - session.last_activity).total_seconds() > 3600:
                to_remove.append(sid)
        
        for sid in to_remove:
            del self.sessions[sid]


session_manager = SessionManager()


# WebSocket endpoints

@app.websocket("/ws/cad/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    Main WebSocket endpoint for CAD collaboration
    """
    await websocket.accept()
    
    # Get or create session
    session = session_manager.get_session(session_id)
    if not session:
        await websocket.send_json({
            "type": "ERROR",
            "message": "Session not found"
        })
        await websocket.close()
        return
    
    # Add participant
    participant_id = await session.add_participant(websocket, "human")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "PATCH":
                await session.handle_patch(participant_id, data["patch"])
            
            elif message_type == "AI_REQUEST":
                await session.handle_ai_request(participant_id, data)
            
            elif message_type == "APPLY_AI_SUGGESTION":
                await session.apply_ai_suggestion(participant_id, data["patch_ids"])
            
            elif message_type == "PING":
                await websocket.send_json({"type": "PONG"})
            
            elif message_type == "CURSOR_MOVE":
                # Broadcast cursor position to others
                await session.broadcast({
                    "type": "PARTICIPANT_CURSOR",
                    "participant_id": participant_id,
                    "position": data["position"]
                }, exclude={participant_id})
            
            elif message_type == "OBJECT_SELECT":
                # User selected object
                await session.broadcast({
                    "type": "PARTICIPANT_SELECTION",
                    "participant_id": participant_id,
                    "object_ids": data["object_ids"]
                }, exclude={participant_id})
    
    except WebSocketDisconnect:
        session.remove_participant(participant_id)
        await session.broadcast({
            "type": "PARTICIPANT_LEFT",
            "participant_id": participant_id,
            "participant_count": len(session.participants)
        })


# REST API endpoints

@app.post("/api/sessions/create")
async def create_session(design_name: str = "Untitled"):
    """Create new collaboration session"""
    session_id = session_manager.create_session(design_name)
    return {
        "session_id": session_id,
        "design_name": design_name
    }


@app.get("/api/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    session = session_manager.get_session(session_id)
    if not session:
        return {"error": "Session not found"}, 404
    
    return {
        "session_id": session.session_id,
        "design_name": session.design_name,
        "participant_count": len(session.participants),
        "version": session.scene_manager.version,
        "created_at": session.created_at.isoformat(),
        "last_activity": session.last_activity.isoformat()
    }


@app.get("/api/sessions/{session_id}/state")
async def get_session_state(session_id: str):
    """Get current scene graph state"""
    session = session_manager.get_session(session_id)
    if not session:
        return {"error": "Session not found"}, 404
    
    return {
        "state": session.scene_manager.get_state(),
        "version": session.scene_manager.version
    }


@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str, from_version: int = 0):
    """Get patch history"""
    session = session_manager.get_session(session_id)
    if not session:
        return {"error": "Session not found"}, 404
    
    patches = session.scene_manager.get_diff(from_version)
    
    return {
        "patches": [p.to_dict() for p in patches],
        "current_version": session.scene_manager.version
    }


# Cleanup task
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    async def cleanup_task():
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            session_manager.cleanup_old_sessions()
    
    asyncio.create_task(cleanup_task())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
