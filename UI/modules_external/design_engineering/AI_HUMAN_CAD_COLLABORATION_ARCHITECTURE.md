# 🎨 AI-Human CAD Collaboration Platform Architecture

**Real-Time Co-Design System for Design Engineering Module**

---

## 🎯 Core Concept: Shared Visual Workspace

### The Challenge
How can a **human** and an **AI** collaborate on the same CAD design simultaneously, with:
- Real-time visual updates
- Granular changes (not full rewrites)
- Multi-modal input (mouse, voice, gestures)
- AI "seeing" what the user sees
- Pinpoint modifications without breaking the entire design

### The Solution: **Operational Transform + Visual Delta Sync**

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED DESIGN STATE                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │        Canonical JSON Scene Graph (CRDT)             │   │
│  │  {                                                    │   │
│  │    "objects": {                                       │   │
│  │      "beam_001": {                                    │   │
│  │        "type": "t-slot-beam",                         │   │
│  │        "position": [100, 200, 0],                     │   │
│  │        "length": 1800,                                │   │
│  │        "profile": "40x40_standard"                    │   │
│  │      }                                                │   │
│  │    },                                                 │   │
│  │    "version": 47                                      │   │
│  │  }                                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         ↑                                      ↑
         │                                      │
    [WebSocket]                            [WebSocket]
         │                                      │
         ↓                                      ↓
┌─────────────────┐                  ┌─────────────────────┐
│   HUMAN CLIENT  │                  │     AI AGENT        │
│                 │                  │                     │
│  ┌───────────┐  │                  │  ┌──────────────┐  │
│  │  Canvas   │  │                  │  │ Vision Model │  │
│  │  Renderer │←─┼──────────────────┼─→│  (Sees SVG)  │  │
│  └───────────┘  │                  │  └──────────────┘  │
│                 │                  │                     │
│  ┌───────────┐  │                  │  ┌──────────────┐  │
│  │   Mouse   │  │                  │  │   LLM Brain  │  │
│  │   Voice   │  │                  │  │  (Generates  │  │
│  │  Gesture  │  │                  │  │   Changes)   │  │
│  └───────────┘  │                  │  └──────────────┘  │
└─────────────────┘                  └─────────────────────┘
```

---

## 🏗️ System Architecture

### 1. **Scene Graph as Single Source of Truth**

Instead of entire JSON rewrites, we use a **hierarchical scene graph** where every object has a unique ID:

```javascript
// SCENE GRAPH STRUCTURE
{
  "metadata": {
    "version": 47,
    "timestamp": "2025-12-15T10:23:45Z",
    "last_modified_by": "human|ai",
    "dimensions_unit": "mm"
  },
  
  "objects": {
    // Each object has UUID
    "beam_a1b2c3d4": {
      "type": "t-slot-beam",
      "profile": "40x40_standard",
      "position": {"x": 0, "y": 0, "z": 0},
      "rotation": {"x": 0, "y": 0, "z": 0},
      "length": 1800,
      "connections": {
        "start": ["connector_xyz123"],
        "end": ["connector_xyz456"]
      },
      "material": "6061-T6",
      "color": "#A0A0A0",
      "visible": true,
      "locked": false,
      "created_by": "ai",
      "modified_at": "2025-12-15T10:22:15Z"
    },
    
    "connector_xyz123": {
      "type": "corner-bracket",
      "part_number": "CB-40-90",
      "position": {"x": 0, "y": 0, "z": 0},
      "angle": 90,
      "connected_beams": ["beam_a1b2c3d4", "beam_e5f6g7h8"]
    }
  },
  
  "groups": {
    "bed-frame-base": {
      "members": ["beam_a1b2c3d4", "beam_e5f6g7h8", "beam_i9j0k1l2"],
      "locked": false
    }
  },
  
  "constraints": {
    "constraint_001": {
      "type": "parallel",
      "objects": ["beam_a1b2c3d4", "beam_e5f6g7h8"],
      "tolerance": 0.5
    }
  },
  
  "camera": {
    "position": {"x": 1000, "y": 1000, "z": 1000},
    "target": {"x": 0, "y": 0, "z": 0},
    "fov": 45
  },
  
  "selections": {
    "human": ["beam_a1b2c3d4"],  // What user has selected
    "ai": ["connector_xyz123"]    // What AI is "looking at"
  }
}
```

---

### 2. **Granular Updates with JSON Patch (RFC 6902)**

Instead of sending entire JSON, we send **patches**:

```javascript
// USER MOVES BEAM 100mm TO THE RIGHT
// Instead of sending entire object, send patch:
{
  "op": "replace",
  "path": "/objects/beam_a1b2c3d4/position/x",
  "value": 100,
  "actor": "human",
  "timestamp": "2025-12-15T10:23:45.123Z"
}

// AI SUGGESTS CHANGING PROFILE SIZE
{
  "op": "replace",
  "path": "/objects/beam_a1b2c3d4/profile",
  "value": "60x60_heavy",
  "actor": "ai",
  "reason": "Beam deflection exceeds L/240 limit under 200kg load"
}

// AI ADDS NEW SUPPORT BEAM
{
  "op": "add",
  "path": "/objects/beam_new123",
  "value": {
    "type": "t-slot-beam",
    "profile": "40x40_standard",
    "position": {"x": 900, "y": 0, "z": 0},
    "length": 1400,
    "created_by": "ai"
  },
  "actor": "ai",
  "reason": "Adding cross-support to prevent lateral movement"
}
```

**Benefits:**
- ✅ Tiny network payloads (bytes instead of KB)
- ✅ Precise change tracking
- ✅ Easy to undo/redo
- ✅ Conflict resolution possible

---

### 3. **Operational Transformation for Concurrent Edits**

When human and AI edit simultaneously, use **Operational Transform (OT)** to merge changes:

```javascript
// SCENARIO: Both edit at same time

// T=0: Initial state
{ "beam_a1b2c3d4": { "length": 1800, "profile": "40x40" } }

// T=1: User changes length to 2000
// Human patch: {"op": "replace", "path": "/length", "value": 2000}

// T=2: AI changes profile to 60x60 (based on T=0 state)
// AI patch: {"op": "replace", "path": "/profile", "value": "60x60"}

// CONFLICT! Both patches applied to different versions

// OT RESOLUTION:
// 1. Apply human patch first (user priority)
// 2. Transform AI patch to account for human change
// 3. Apply transformed AI patch
// Result: { "length": 2000, "profile": "60x60" }

// AI gets notification:
// "Your profile change was applied, but the user extended the beam to 2000mm"
```

**OT Algorithm:**
```javascript
function transformPatch(patchA, patchB) {
  // If patches affect different paths, no transformation needed
  if (!pathsConflict(patchA.path, patchB.path)) {
    return patchB;
  }
  
  // If both replace same value, user wins
  if (patchA.op === 'replace' && patchB.op === 'replace' && 
      patchA.path === patchB.path) {
    console.log(`Conflict: User change takes precedence`);
    return null; // Discard AI patch
  }
  
  // If AI adds object and user modifies parent, adjust path
  if (patchB.op === 'add' && patchA.path.startsWith(patchB.path)) {
    patchB.path = adjustPathForInsert(patchB.path, patchA);
    return patchB;
  }
  
  return patchB;
}
```

---

### 4. **How AI "Sees" the Design**

AI needs visual understanding, not just JSON. We provide:

#### A. SVG Snapshots
```javascript
// Every time scene updates, generate SVG
function generateSVGForAI(sceneGraph) {
  const svg = `
    <svg width="2000" height="1400" viewBox="0 0 2000 1400">
      <!-- Top view of bed frame -->
      <rect id="beam_a1b2c3d4" x="0" y="0" width="1800" height="40" 
            fill="#A0A0A0" stroke="black" stroke-width="2"/>
      <rect id="beam_e5f6g7h8" x="0" y="1360" width="1800" height="40" 
            fill="#A0A0A0" stroke="black"/>
      <rect id="beam_i9j0k1l2" x="0" y="0" width="40" height="1400" 
            fill="#A0A0A0" stroke="black"/>
      
      <!-- Annotations for AI -->
      <text x="900" y="20" class="ai-label">1800mm</text>
      <circle cx="0" cy="0" r="10" fill="red" class="ai-stress-point"/>
    </svg>
  `;
  
  return {
    svg: svg,
    metadata: {
      objects_visible: 12,
      stress_points: [{"id": "beam_a1b2c3d4", "stress_mpa": 145}],
      warnings: ["Beam deflection 3.2mm exceeds recommended L/500"]
    }
  };
}
```

#### B. Vision Model Integration
```python
# AI agent receives SVG + scene graph
async def ai_analyze_design(svg_snapshot, scene_graph):
    # Use vision model (GPT-4V, Claude Vision) to "see" the design
    vision_response = await vision_model.analyze(
        image=svg_to_png(svg_snapshot),
        prompt=f"""
        Analyze this T-slot aluminum frame design.
        
        Current specifications:
        - Main beams: 40x40mm profile
        - Span: 1800mm
        - Load: 200kg distributed
        
        JSON structure:
        {json.dumps(scene_graph, indent=2)}
        
        Questions:
        1. Do you see any structural weaknesses?
        2. Should any beams be reinforced?
        3. Are connections adequate?
        4. Suggest specific improvements with exact positions.
        """
    )
    
    # Parse AI response into actionable patches
    patches = parse_ai_suggestions(vision_response)
    
    # Example patches:
    return [
        {
            "op": "add",
            "path": "/objects/beam_support_001",
            "value": {
                "type": "t-slot-beam",
                "position": {"x": 900, "y": 0, "z": -600},
                "length": 1400,
                "profile": "40x40_standard",
                "purpose": "cross-support"
            },
            "reason": "Add center support beam to reduce deflection from 3.2mm to 1.1mm"
        },
        {
            "op": "replace",
            "path": "/objects/beam_a1b2c3d4/profile",
            "value": "60x60_standard",
            "reason": "Upgrade main beams to 60x60 for better load distribution"
        }
    ]
```

#### C. 3D Viewport Synchronization
```javascript
// AI can also receive 3D viewport screenshots
function capture3DViewForAI() {
  const canvas = document.getElementById('cad-3d-viewer');
  const screenshot = canvas.toDataURL('image/png');
  
  return {
    image: screenshot,
    camera: scene.camera.position,
    selected_objects: scene.selections.human,
    viewport_mode: '3d-perspective' // or '2d-top', '2d-front', etc.
  };
}
```

---

### 5. **Real-Time Bidirectional Communication**

#### WebSocket Protocol

```javascript
// CLIENT SIDE (Human)
class CADWebSocketClient {
  constructor(designId) {
    this.ws = new WebSocket(`wss://api.yourdomain.com/cad/${designId}`);
    this.sceneGraph = null;
    this.patchQueue = [];
    
    this.ws.onopen = () => {
      console.log('Connected to collaborative CAD session');
      this.requestInitialState();
    };
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };
  }
  
  handleMessage(message) {
    switch (message.type) {
      case 'INITIAL_STATE':
        this.sceneGraph = message.data;
        this.renderScene();
        break;
        
      case 'PATCH':
        // Apply patch from AI or other users
        this.applyPatch(message.patch);
        this.renderScene();
        
        // Show AI's reasoning
        if (message.actor === 'ai' && message.reason) {
          this.showAIExplanation(message.reason, message.patch);
        }
        break;
        
      case 'AI_CURSOR':
        // Show where AI is "looking"
        this.highlightAIFocus(message.object_ids);
        break;
        
      case 'AI_SUGGESTION':
        // AI proposes change but doesn't apply it yet
        this.showSuggestionPreview(message.patches, message.explanation);
        break;
        
      case 'CONFLICT':
        // Simultaneous edit detected
        this.showConflictResolution(message.your_change, message.ai_change);
        break;
    }
  }
  
  // User makes a change
  onUserEditObject(objectId, changes) {
    const patch = {
      op: 'replace',
      path: `/objects/${objectId}`,
      value: Object.assign(this.sceneGraph.objects[objectId], changes),
      actor: 'human',
      timestamp: Date.now()
    };
    
    // Optimistic update
    this.applyPatch(patch);
    this.renderScene();
    
    // Send to server
    this.ws.send(JSON.stringify({
      type: 'PATCH',
      patch: patch
    }));
  }
  
  // User asks AI for help
  requestAIAnalysis(question) {
    const snapshot = this.capture3DView();
    
    this.ws.send(JSON.stringify({
      type: 'AI_REQUEST',
      question: question,
      context: {
        scene_graph: this.sceneGraph,
        svg_snapshot: this.generateSVG(),
        viewport_image: snapshot,
        selected_objects: this.getSelectedObjects()
      }
    }));
  }
}
```

#### Server-Side WebSocket Handler

```python
# SERVER SIDE
import asyncio
from fastapi import WebSocket
import json
from typing import Dict, List

class CADCollaborationServer:
    def __init__(self):
        self.active_sessions: Dict[str, CADSession] = {}
    
    async def handle_connection(self, websocket: WebSocket, design_id: str):
        await websocket.accept()
        
        # Get or create session
        session = self.get_session(design_id)
        session.add_participant(websocket, 'human')
        
        # Send initial state
        await websocket.send_json({
            'type': 'INITIAL_STATE',
            'data': session.scene_graph
        })
        
        try:
            while True:
                message = await websocket.receive_json()
                await self.handle_message(session, websocket, message)
        except WebSocketDisconnect:
            session.remove_participant(websocket)
    
    async def handle_message(self, session, websocket, message):
        if message['type'] == 'PATCH':
            # User made a change
            patch = message['patch']
            
            # Validate patch
            if self.validate_patch(patch, session.scene_graph):
                # Apply to canonical state
                session.apply_patch(patch)
                
                # Broadcast to all participants (including AI)
                await session.broadcast(message, exclude=websocket)
                
                # Trigger AI analysis if needed
                if self.should_trigger_ai(patch):
                    await self.run_ai_analysis(session, patch)
        
        elif message['type'] == 'AI_REQUEST':
            # User explicitly asks AI for help
            await self.run_ai_agent(session, message['question'], message['context'])
    
    async def run_ai_agent(self, session, question, context):
        # AI agent analyzes design
        ai_response = await ai_agent.analyze_design(
            scene_graph=context['scene_graph'],
            svg=context['svg_snapshot'],
            viewport_image=context['viewport_image'],
            question=question
        )
        
        # AI generates patches
        patches = ai_response['patches']
        explanation = ai_response['explanation']
        
        # Send AI suggestions (not auto-applied)
        await session.broadcast({
            'type': 'AI_SUGGESTION',
            'patches': patches,
            'explanation': explanation,
            'preview_svg': ai_response['preview_svg']
        })
    
    async def run_ai_analysis(self, session, triggering_patch):
        # Background AI analysis after user change
        
        # Check structural integrity
        analysis = await structural_analyzer.analyze(session.scene_graph)
        
        if analysis['warnings']:
            # AI found issues
            await session.broadcast({
                'type': 'AI_WARNING',
                'warnings': analysis['warnings'],
                'suggested_fixes': analysis['suggested_patches']
            })
```

---

### 6. **Multi-Modal User Input**

#### A. Mouse/Touch Interactions
```javascript
class CADInteractionHandler {
  constructor(canvas, sceneGraph) {
    this.canvas = canvas;
    this.sceneGraph = sceneGraph;
    this.mode = 'select'; // 'select', 'move', 'rotate', 'scale', 'draw'
    
    this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
    this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
    this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
  }
  
  onMouseDown(event) {
    const point = this.getCanvasPoint(event);
    const object = this.hitTest(point);
    
    if (object) {
      this.selectedObject = object;
      this.dragStart = point;
      
      // Show AI what user is focusing on
      this.sendAIFocusUpdate([object.id]);
    }
  }
  
  onMouseMove(event) {
    if (!this.selectedObject) return;
    
    const point = this.getCanvasPoint(event);
    const delta = {
      x: point.x - this.dragStart.x,
      y: point.y - this.dragStart.y
    };
    
    // Real-time position update
    this.emitPatch({
      op: 'replace',
      path: `/objects/${this.selectedObject.id}/position`,
      value: {
        x: this.selectedObject.position.x + delta.x,
        y: this.selectedObject.position.y + delta.y,
        z: this.selectedObject.position.z
      }
    });
    
    this.dragStart = point;
  }
  
  onMouseUp(event) {
    this.selectedObject = null;
    
    // AI can now analyze the change
    this.requestAIValidation();
  }
}
```

#### B. Voice Commands
```javascript
class VoiceCADController {
  constructor(wsClient) {
    this.ws = wsClient;
    this.recognition = new webkitSpeechRecognition();
    
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    
    this.recognition.onresult = (event) => {
      const transcript = event.results[event.results.length - 1][0].transcript;
      this.processVoiceCommand(transcript);
    };
  }
  
  processVoiceCommand(command) {
    // Parse natural language commands
    const patterns = {
      move: /move (.*?) (up|down|left|right) by (\d+)/i,
      resize: /make (.*?) (longer|shorter) by (\d+)/i,
      add: /add a (.*?) at (.*)/i,
      change: /change (.*?) to (.*)/i
    };
    
    if (patterns.move.test(command)) {
      const [, objectName, direction, amount] = command.match(patterns.move);
      this.executeMoveCommand(objectName, direction, parseInt(amount));
    }
    else if (patterns.resize.test(command)) {
      const [, objectName, operation, amount] = command.match(patterns.resize);
      this.executeResizeCommand(objectName, operation, parseInt(amount));
    }
    // ... more patterns
    else {
      // Send to AI for interpretation
      this.ws.send(JSON.stringify({
        type: 'VOICE_COMMAND',
        command: command
      }));
    }
  }
  
  executeMoveCommand(objectName, direction, amount) {
    const object = this.findObjectByName(objectName);
    if (!object) return;
    
    const delta = {
      'up': {x: 0, y: -amount, z: 0},
      'down': {x: 0, y: amount, z: 0},
      'left': {x: -amount, y: 0, z: 0},
      'right': {x: amount, y: 0, z: 0}
    }[direction];
    
    this.emitPatch({
      op: 'replace',
      path: `/objects/${object.id}/position`,
      value: {
        x: object.position.x + delta.x,
        y: object.position.y + delta.y,
        z: object.position.z + delta.z
      }
    });
  }
}
```

#### C. Gesture Input (Drawing on Canvas)
```javascript
class GestureCADInput {
  constructor(canvas) {
    this.canvas = canvas;
    this.isDrawing = false;
    this.gesturePoints = [];
    
    canvas.addEventListener('pointerdown', this.startGesture.bind(this));
    canvas.addEventListener('pointermove', this.continueGesture.bind(this));
    canvas.addEventListener('pointerup', this.endGesture.bind(this));
  }
  
  startGesture(event) {
    this.isDrawing = true;
    this.gesturePoints = [this.getPoint(event)];
  }
  
  continueGesture(event) {
    if (!this.isDrawing) return;
    this.gesturePoints.push(this.getPoint(event));
    
    // Show gesture path
    this.drawGesturePath();
  }
  
  endGesture(event) {
    this.isDrawing = false;
    
    // Recognize gesture
    const gesture = this.recognizeGesture(this.gesturePoints);
    
    if (gesture.type === 'line') {
      // User drew a line = create beam
      this.createBeam(gesture.start, gesture.end);
    }
    else if (gesture.type === 'circle') {
      // User drew circle = create connection point
      this.createConnector(gesture.center);
    }
    else if (gesture.type === 'cross') {
      // User drew X = delete object at location
      const object = this.hitTest(gesture.center);
      if (object) this.deleteObject(object.id);
    }
    
    this.gesturePoints = [];
  }
  
  recognizeGesture(points) {
    // Simple gesture recognizer
    if (points.length < 3) return {type: 'unknown'};
    
    const start = points[0];
    const end = points[points.length - 1];
    const distance = this.distance(start, end);
    
    // Straight line gesture
    if (this.isLinear(points) && distance > 50) {
      return {
        type: 'line',
        start: start,
        end: end,
        length: distance
      };
    }
    
    // Circular gesture
    if (this.isCircular(points)) {
      return {
        type: 'circle',
        center: this.getCenter(points),
        radius: this.getRadius(points)
      };
    }
    
    return {type: 'unknown'};
  }
}
```

---

### 7. **AI Cursor & Focus Indicators**

Show the user where the AI is "looking" and what it's analyzing:

```javascript
class AIPresenceIndicator {
  constructor(canvas) {
    this.canvas = canvas;
    this.aiCursorPosition = null;
    this.aiFocusedObjects = [];
    this.aiThinkingIndicator = null;
  }
  
  updateAICursor(position) {
    this.aiCursorPosition = position;
    this.render();
  }
  
  updateAIFocus(objectIds) {
    this.aiFocusedObjects = objectIds;
    this.highlightObjects(objectIds, 'ai-focus');
  }
  
  showAIThinking(message) {
    this.aiThinkingIndicator = {
      message: message,
      startTime: Date.now()
    };
    this.render();
  }
  
  render() {
    const ctx = this.canvas.getContext('2d');
    
    // Draw AI cursor (different color than user cursor)
    if (this.aiCursorPosition) {
      ctx.save();
      ctx.fillStyle = '#4CAF50'; // Green for AI
      ctx.beginPath();
      ctx.arc(this.aiCursorPosition.x, this.aiCursorPosition.y, 8, 0, 2 * Math.PI);
      ctx.fill();
      
      // AI label
      ctx.fillStyle = 'white';
      ctx.font = '12px sans-serif';
      ctx.fillText('🤖 AI', this.aiCursorPosition.x + 15, this.aiCursorPosition.y + 5);
      ctx.restore();
    }
    
    // Highlight AI-focused objects
    this.aiFocusedObjects.forEach(objectId => {
      const object = this.sceneGraph.objects[objectId];
      if (!object) return;
      
      ctx.save();
      ctx.strokeStyle = '#4CAF50';
      ctx.lineWidth = 3;
      ctx.setLineDash([5, 5]);
      this.drawObjectOutline(ctx, object);
      ctx.restore();
    });
    
    // AI thinking indicator
    if (this.aiThinkingIndicator) {
      const elapsed = Date.now() - this.aiThinkingIndicator.startTime;
      const dots = '.'.repeat((Math.floor(elapsed / 500) % 3) + 1);
      
      ctx.save();
      ctx.fillStyle = 'rgba(76, 175, 80, 0.9)';
      ctx.fillRect(10, 10, 300, 50);
      
      ctx.fillStyle = 'white';
      ctx.font = '14px sans-serif';
      ctx.fillText(`🤖 AI: ${this.aiThinkingIndicator.message}${dots}`, 20, 35);
      ctx.restore();
    }
  }
}
```

---

### 8. **AI Suggestion Preview System**

Before AI applies changes, show preview:

```javascript
class AISuggestionPreview {
  constructor(sceneGraph, renderer) {
    this.sceneGraph = sceneGraph;
    this.renderer = renderer;
    this.activeSuggestion = null;
  }
  
  showSuggestion(patches, explanation) {
    this.activeSuggestion = {
      patches: patches,
      explanation: explanation,
      previewGraph: this.applyPatchesToCopy(patches)
    };
    
    this.renderPreviewUI();
  }
  
  renderPreviewUI() {
    const modal = document.getElementById('ai-suggestion-modal');
    modal.innerHTML = `
      <div class="ai-suggestion-card">
        <h3>🤖 AI Suggestion</h3>
        <p>${this.activeSuggestion.explanation}</p>
        
        <div class="preview-comparison">
          <div class="preview-before">
            <h4>Current Design</h4>
            <canvas id="preview-before"></canvas>
          </div>
          
          <div class="preview-after">
            <h4>After AI Changes</h4>
            <canvas id="preview-after"></canvas>
          </div>
        </div>
        
        <div class="changes-list">
          <h4>Proposed Changes:</h4>
          <ul>
            ${this.formatPatches(this.activeSuggestion.patches)}
          </ul>
        </div>
        
        <div class="actions">
          <button class="btn-primary" onclick="aiPreview.acceptSuggestion()">
            ✓ Accept
          </button>
          <button class="btn-secondary" onclick="aiPreview.acceptPartial()">
            ⚙️ Accept Some
          </button>
          <button class="btn-danger" onclick="aiPreview.rejectSuggestion()">
            ✗ Reject
          </button>
          <button class="btn-info" onclick="aiPreview.askWhy()">
            ❓ Explain Why
          </button>
        </div>
      </div>
    `;
    
    // Render side-by-side comparison
    this.renderComparison();
    
    modal.style.display = 'block';
  }
  
  renderComparison() {
    // Render current state
    const beforeCanvas = document.getElementById('preview-before');
    this.renderer.render(this.sceneGraph, beforeCanvas);
    
    // Render with AI changes
    const afterCanvas = document.getElementById('preview-after');
    this.renderer.render(this.activeSuggestion.previewGraph, afterCanvas);
    
    // Highlight differences
    this.highlightDifferences(beforeCanvas, afterCanvas);
  }
  
  formatPatches(patches) {
    return patches.map(patch => {
      if (patch.op === 'replace') {
        const objectId = patch.path.split('/')[2];
        const property = patch.path.split('/')[3];
        return `<li>Change ${objectId}'s ${property} to ${patch.value} 
                <br><small>Reason: ${patch.reason}</small></li>`;
      }
      else if (patch.op === 'add') {
        const objectId = patch.path.split('/')[2];
        return `<li>Add new ${patch.value.type}: ${objectId}
                <br><small>Reason: ${patch.reason}</small></li>`;
      }
      else if (patch.op === 'remove') {
        const objectId = patch.path.split('/')[2];
        return `<li>Remove ${objectId}
                <br><small>Reason: ${patch.reason}</small></li>`;
      }
    }).join('');
  }
  
  acceptSuggestion() {
    // Apply all patches
    this.activeSuggestion.patches.forEach(patch => {
      this.ws.send(JSON.stringify({
        type: 'APPLY_AI_SUGGESTION',
        patch: patch
      }));
    });
    
    this.closeSuggestion();
  }
  
  acceptPartial() {
    // Show checklist for user to select which changes to apply
    const checklist = this.activeSuggestion.patches.map((patch, idx) => {
      return `
        <label>
          <input type="checkbox" checked data-patch-idx="${idx}">
          ${this.formatPatch(patch)}
        </label>
      `;
    }).join('');
    
    // ... show UI for partial acceptance
  }
  
  askWhy() {
    // User wants more explanation
    this.ws.send(JSON.stringify({
      type: 'AI_EXPLAIN_MORE',
      suggestion_id: this.activeSuggestion.id
    }));
  }
}
```

---

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
```javascript
// 1. Set up WebSocket infrastructure
// 2. Implement scene graph with UUID system
// 3. Create JSON Patch system
// 4. Build basic renderer
```

### Phase 2: Real-Time Sync (Week 3-4)
```javascript
// 5. Operational transformation for conflicts
// 6. Optimistic updates on client
// 7. Server-side state management
// 8. Rollback/undo system
```

### Phase 3: AI Integration (Week 5-6)
```python
# 9. SVG snapshot generation
# 10. Vision model integration (GPT-4V)
# 11. AI patch generation
# 12. Structural analysis engine
```

### Phase 4: Multi-Modal Input (Week 7-8)
```javascript
// 13. Voice command system
// 14. Gesture recognition
// 15. AI cursor/focus indicators
// 16. Suggestion preview UI
```

---

## 📊 Data Flow Examples

### Example 1: User Drags Beam, AI Validates

```
1. USER: Clicks beam → Drags 100mm right
   ↓
2. CLIENT: Generates patch
   {"op": "replace", "path": "/objects/beam_123/position/x", "value": 100}
   ↓
3. CLIENT: Optimistic update (instant visual feedback)
   ↓
4. WS → SERVER: Send patch
   ↓
5. SERVER: Validate & apply to canonical state
   ↓
6. SERVER → AI: Trigger structural analysis
   ↓
7. AI: Analyze new configuration
   - Calculate deflection: 4.2mm
   - Check safety factor: 2.1x (marginal)
   - Generate suggestion
   ↓
8. AI → SERVER: Patch suggestion
   {"op": "add", "path": "/objects/support_beam_456", "value": {...}}
   ↓
9. SERVER → CLIENT: AI suggestion
   ↓
10. CLIENT: Show preview modal
    "AI suggests adding center support to reduce deflection"
    [Before/After comparison]
    [Accept] [Reject] [Explain Why]
```

### Example 2: Voice Command "Make it stronger"

```
1. USER: "Make the bed frame stronger"
   ↓
2. VOICE SYSTEM: Transcribe → Send to AI
   ↓
3. AI: Interpret intent
   - Context: Looking at beam_123
   - Goal: Increase structural strength
   - Options: Upgrade profile OR add supports
   ↓
4. AI: Generate multiple suggestions
   Option A: Replace 40x40 → 60x60 (+$45)
   Option B: Add 2 cross-supports (+$30)
   Option C: Add vertical legs (+$35)
   ↓
5. AI → CLIENT: Show options with previews
   ↓
6. USER: Selects Option B
   ↓
7. CLIENT → SERVER: Apply selected patches
   ↓
8. EVERYONE: Sees new supports appear in real-time
```

### Example 3: Simultaneous Edit Conflict

```
TIME  | USER                           | AI
------|--------------------------------|--------------------------------
T=0   | Scene: beam length=1800mm      | Scene: beam length=1800mm
      |                                |
T=1   | Drag beam → 2000mm             |
      | Patch: {"length": 2000}        |
      |                                |
T=2   | Send patch to server           | Analyzing stress...
      |                                | Suggests profile change
      |                                | Patch: {"profile": "60x60"}
      |                                |
T=3   | Server receives user patch     | Server receives AI patch
      | Apply: length=2000 ✓           |
      |                                |
T=4   |                                | OT: Transform AI patch
      |                                | AI patch still valid ✓
      |                                | Apply: profile=60x60 ✓
      |                                |
T=5   | ← Server broadcasts merged state
      | Beam: {length: 2000, profile: "60x60"}
      |                                |
T=6   | See AI change + explanation    | ← Server confirms both applied
      | "AI upgraded profile due to    |
      |  increased length"             |
```

---

## 🔒 Conflict Resolution Strategies

### 1. **User Priority (Default)**
```javascript
if (human_patch.timestamp < ai_patch.timestamp + CONFLICT_WINDOW) {
  // User change takes precedence
  apply(human_patch);
  
  // Transform AI patch to account for user change
  const transformed = transform(ai_patch, human_patch);
  if (transformed.is_valid) {
    apply(transformed);
    notify_ai("Your change was adjusted due to user edit");
  } else {
    reject(ai_patch);
    notify_ai("User change conflicts with your suggestion");
  }
}
```

### 2. **Intent Preservation**
```javascript
// AI wanted to reduce stress, user moved beam
// Solution: Apply both but recalculate AI's values

AI intent: "Reduce stress by upgrading profile"
User action: "Made beam 200mm longer"
Resolution: "Upgrade to 80x80 instead of 60x60 to account for new length"
```

### 3. **Ask User When Ambiguous**
```javascript
if (conflict.is_ambiguous) {
  show_dialog({
    title: "Conflicting Changes",
    message: "You moved the beam while AI was upgrading it",
    options: [
      "Keep my change only",
      "Keep AI change only",
      "Merge both changes",
      "Undo both and start over"
    ]
  });
}
```

---

## 🎨 Visual Feedback Examples

### 1. **AI Thinking Animation**
```css
.ai-cursor {
  position: absolute;
  width: 32px;
  height: 32px;
  background: radial-gradient(circle, #4CAF50, transparent);
  animation: ai-pulse 1.5s infinite;
  pointer-events: none;
}

@keyframes ai-pulse {
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 0.4; }
}

.ai-analyzing::after {
  content: '🤖 Analyzing...';
  position: absolute;
  background: rgba(76, 175, 80, 0.9);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
}
```

### 2. **Change Highlight**
```javascript
function highlightChange(objectId, changeType) {
  const element = document.getElementById(objectId);
  
  // Different colors for different actors
  const colors = {
    'human': '#2196F3',  // Blue
    'ai': '#4CAF50',      // Green
    'conflict': '#FF9800' // Orange
  };
  
  // Pulse animation
  element.style.boxShadow = `0 0 20px ${colors[changeType]}`;
  element.style.transition = 'box-shadow 0.5s';
  
  setTimeout(() => {
    element.style.boxShadow = 'none';
  }, 2000);
}
```

### 3. **Diff Visualization**
```javascript
function showDiff(beforeObj, afterObj) {
  const diff = computeDiff(beforeObj, afterObj);
  
  return `
    <div class="diff-viewer">
      ${diff.map(change => `
        <div class="diff-line ${change.type}">
          <span class="diff-type">${change.type}</span>
          <span class="diff-property">${change.property}</span>
          <span class="diff-before">${change.before}</span>
          <span class="diff-arrow">→</span>
          <span class="diff-after">${change.after}</span>
        </div>
      `).join('')}
    </div>
  `;
}
```

---

## 💾 Complete Code Example

Would you like me to generate:

1. **Full WebSocket client/server implementation**
2. **Scene graph manager with OT**
3. **AI vision integration code**
4. **Voice/gesture input handlers**
5. **3D renderer with real-time updates**
6. **Suggestion preview system**

This architecture enables true AI-human collaboration where both can see and modify the same visual design in real-time, with granular changes and intelligent conflict resolution!
