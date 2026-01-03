# 🎨 AI-Human CAD Collaboration Platform

**Real-Time Collaborative Design Engineering with Granular Updates**

> **⚠️ SVG Generation:** When creating technical drawings or schematics, **always follow** `.github/SVG_CAD_GENERATION_RULES.md` for proper title block spacing (title block bottom + 40-60px clearance before content).

---

## 🎯 What Problem Does This Solve?

Traditional CAD systems don't allow **AI and humans to work together on the same visual design simultaneously**. This platform solves:

❌ **Full JSON rewrites** → ✅ Granular JSON Patch updates  
❌ **AI can't "see" designs** → ✅ AI vision integration with SVG snapshots  
❌ **Conflicts when both edit** → ✅ Operational Transformation (OT) for conflict resolution  
❌ **Mouse-only input** → ✅ Multi-modal: Mouse, Voice, Gestures  
❌ **Async feedback loops** → ✅ Real-time WebSocket collaboration  

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                 CANONICAL SCENE GRAPH (Server)               │
│  ┌──────────────────────────────────────────────────────┐   │
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
│           ↑ Patches                  ↑ Patches               │
└───────────┼──────────────────────────┼──────────────────────┘
            │                          │
      [WebSocket]                [WebSocket]
            │                          │
            ↓                          ↓
  ┌─────────────────┐        ┌─────────────────────┐
  │  HUMAN CLIENT   │        │     AI AGENT        │
  │  - Canvas       │        │  - Vision Model     │
  │  - Mouse/Voice  │        │  - LLM Brain        │
  │  - Gestures     │        │  - Structural AI    │
  └─────────────────┘        └─────────────────────┘
```

---

## 📦 Components

### 1. **Operational Transform Engine** (`operational_transform.py`)
Handles concurrent edits from multiple agents.

```python
from operational_transform import SceneGraphManager, Patch, PatchOperation

scene = SceneGraphManager()

# User patch
user_patch = Patch(
    op=PatchOperation.REPLACE,
    path="/objects/beam_001/length",
    value=2000,
    actor=PatchActor.HUMAN
)

# AI patch (concurrent)
ai_patch = Patch(
    op=PatchOperation.REPLACE,
    path="/objects/beam_001/profile",
    value="60x60_heavy",
    actor=PatchActor.AI,
    reason="Increased length requires stronger profile"
)

# Apply with OT conflict resolution
results = scene.apply_patches_with_ot([user_patch, ai_patch])
```

**Key Features:**
- ✅ JSON Patch (RFC 6902) operations
- ✅ Conflict detection and resolution
- ✅ User priority (human changes win)
- ✅ Version control with history
- ✅ Undo/redo support

---

### 2. **WebSocket Collaboration Server** (`websocket_server.py`)
Real-time bidirectional communication.

```bash
# Start server
cd backend
python websocket_server.py

# Server runs on ws://localhost:8000/ws/cad/{session_id}
```

**Message Types:**
- `PATCH` - Apply change to scene
- `AI_REQUEST` - User asks AI question
- `AI_SUGGESTION` - AI proposes changes (not auto-applied)
- `CURSOR_MOVE` - Real-time cursor tracking
- `OBJECT_SELECT` - Selection synchronization

**REST API:**
- `POST /api/sessions/create` - Create new session
- `GET /api/sessions/{id}` - Get session info
- `GET /api/sessions/{id}/state` - Get current scene graph
- `GET /api/sessions/{id}/history` - Get patch history

---

### 3. **WebSocket Client** (`cad-collaboration-client.js`)
Browser client with optimistic updates.

```javascript
// Initialize client
const client = new CADCollaborationClient('session-123', canvasElement);
await client.connect();

// User modifies object
client.modifyObject('beam_001', {
    length: 2000,  // Changed from 1800mm
    profile: '60x60_heavy'  // Upgraded
});

// Ask AI
client.askAI('Is this design structurally sound?');

// Listen for AI suggestions
client.onAISuggestion = (suggestion) => {
    showPreview(suggestion.patches, suggestion.explanation);
};
```

**Features:**
- ✅ Optimistic updates (instant visual feedback)
- ✅ Automatic patch generation
- ✅ Real-time rendering
- ✅ Multi-participant cursors
- ✅ AI focus indicators

---

### 4. **Interaction Handlers** (`cad-interaction-handlers.js`)
Multi-modal input support.

```javascript
const handler = new CADInteractionHandler(client, canvas);

// Mouse/Touch
handler.setMode('select');  // or 'draw-beam', 'gesture'

// Voice
const voice = new VoiceCADController(client);
voice.start();

// Voice commands:
// "Move beam 001 right by 100"
// "Make it stronger"
// "Add a support beam at center"
// "Check the design"
```

**Input Methods:**
- 🖱️ **Mouse** - Click, drag, draw
- ✋ **Touch** - Tablet/mobile support
- 🎤 **Voice** - Natural language commands
- ✍️ **Gestures** - Draw shapes to create objects
- ⌨️ **Keyboard** - Shortcuts and quick actions

---

### 5. **AI Vision Integration** (`ai_vision_integration.py`)
AI "sees" and analyzes designs.

```python
from ai_vision_integration import AIVisionIntegration

vision = AIVisionIntegration(model_type='gpt4v')

# Generate SVG snapshot
svg = vision.generate_svg_snapshot(scene_graph)

# Analyze with vision model
result = await vision.analyze_with_vision_model(
    scene_graph,
    question="Is this bed frame structurally sound?"
)

print(result.warnings)
# ["Beam deflection may exceed L/240 limit"]

print(result.suggestions)
# [{"op": "add", "path": "/objects/support_001", ...}]
```

**Capabilities:**
- 📸 SVG snapshot generation
- 👁️ Vision model integration (GPT-4V, Claude)
- 📊 Structural analysis
- 💡 Actionable suggestions as JSON patches
- 🎨 Annotated visualizations

---

## 🚀 Quick Start

### 1. **Install Dependencies**

```bash
# Python backend
cd backend
pip install fastapi uvicorn websockets pillow cairosvg

# No npm dependencies needed (vanilla JavaScript)
```

### 2. **Start Server**

```bash
cd backend
python websocket_server.py

# Server starts on http://localhost:8000
# WebSocket: ws://localhost:8000/ws/cad/{session_id}
```

### 3. **Open Demo**

```bash
# Open in browser
open cad-collaboration-demo.html

# Or use a local server
python -m http.server 8080
# Then visit: http://localhost:8080/cad-collaboration-demo.html
```

### 4. **Try It Out**

**Create a Beam:**
1. Click "Draw Beam" mode
2. Click and drag on canvas
3. Beam appears in real-time

**Ask AI:**
1. Type in AI panel: "Is this design strong enough?"
2. AI analyzes and responds with suggestions
3. Accept/reject suggestions with preview

**Voice Commands:**
1. Click "Start Voice Input"
2. Say: "Add a support beam at center"
3. AI interprets and executes

**Gestures:**
1. Click "Gesture" mode
2. Draw a line → Creates beam
3. Draw a circle → Creates connector
4. Draw an X → Deletes object

---

## 📐 How It Works

### Granular Updates with JSON Patch

**Traditional Approach (❌ Bad):**
```javascript
// Send entire scene (100KB+)
socket.send(JSON.stringify(sceneGraph));
```

**Our Approach (✅ Good):**
```javascript
// Send tiny patch (100 bytes)
socket.send({
    op: "replace",
    path: "/objects/beam_001/length",
    value: 2000,
    timestamp: "2025-12-15T10:23:45Z"
});
```

**Benefits:**
- 🚀 1000x smaller payloads
- ⚡ Instant updates
- 📝 Perfect change tracking
- ↶ Easy undo/redo
- 🔀 Conflict resolution possible

---

### Operational Transformation

**Scenario:** User and AI edit simultaneously

```javascript
// T=0: beam.length = 1800

// T=1: User changes to 2000
userPatch = {path: "/length", value: 2000}

// T=2: AI changes to 1900 (based on T=0)
aiPatch = {path: "/length", value: 1900}

// CONFLICT!

// OT Resolution:
// 1. Apply user patch first (user priority)
// 2. Discard AI patch (same path, user wins)
// 3. Notify AI: "User changed length while you were analyzing"

// Final: beam.length = 2000 ✓
```

**Strategies:**
- 👤 **User Priority** - Human changes always win
- 🔄 **Transform & Merge** - Adjust AI changes to account for user edits
- ⚠️ **Conflict Warning** - Ask user when ambiguous
- 🎯 **Intent Preservation** - Keep AI's goal even if specifics change

---

### AI Vision Pipeline

**How AI "Sees" the Design:**

```
1. Scene Graph (JSON)
   ↓
2. Generate SVG Snapshot
   ↓
3. Convert to PNG
   ↓
4. Encode as Base64
   ↓
5. Send to Vision Model (GPT-4V)
   ↓
6. Receive Analysis
   ↓
7. Parse into JSON Patches
   ↓
8. Send as Suggestions to User
```

**AI Prompt Example:**
```
You are analyzing this T-slot aluminum frame design.

Current state: 2 beams, 40x40mm, 1800mm span
Load requirement: 200kg distributed

[SVG IMAGE]
[JSON SCENE GRAPH]

Analyze for:
1. Structural integrity
2. Safety factors
3. Deflection limits
4. Cost optimization

Provide suggestions as JSON patches:
{"op": "add", "path": "/objects/support_001", "value": {...}}
```

---

### Multi-Modal Interaction

**Gesture Recognition:**
```javascript
// User draws on canvas
onGestureComplete(points) {
    const gesture = recognizeGesture(points);
    
    if (gesture.type === 'line') {
        // Create beam from line
        createBeam(gesture.start, gesture.end);
    }
    else if (gesture.type === 'circle') {
        // Create connector
        createConnector(gesture.center);
    }
    else if (gesture.type === 'cross') {
        // Delete object
        deleteObjectAt(gesture.center);
    }
}
```

**Voice Commands:**
```javascript
// Speech recognition patterns
patterns = {
    move: /move (.*?) (up|down|left|right) by (\d+)/i,
    resize: /make (.*?) (longer|shorter) by (\d+)/i,
    add: /add a (.*?) at (.*)/i,
    ask: /(?:hey ai|ai) (.+)/i
}

// Example: "Move beam 001 right by 100"
executeCommand('move', ['beam_001', 'right', '100']);
```

---

## 🎯 Use Cases

### 1. **Design Review**
**Scenario:** Engineer creates design, AI validates

```
User: [Draws bed frame structure]
AI:   "I see a 1800mm span with 40x40mm beams. Under 200kg load, 
       deflection will be 4.2mm (L/428), which is acceptable but 
       close to the limit. Consider adding center support."
User: "Add center support"
AI:   [Generates patch, shows preview]
User: [Accepts]
AI:   "New deflection: 1.1mm (L/1636). Much better! ✓"
```

### 2. **Cost Optimization**
```
User: "Make this as cheap as possible while staying safe"
AI:   "Current cost: $245. I can reduce to $180 by:
       - Using 40x40 instead of 60x60 for non-critical beams
       - Optimizing lengths to minimize waste
       - Switching to standard grade where heavy-duty not needed"
User: [Reviews each suggestion]
User: [Accepts 2 of 3]
AI:   "New cost: $195. Savings: $50 (20%)"
```

### 3. **Learning/Training**
```
Student: [Creates unstable structure]
AI:      "This design has a stability issue. The center of gravity 
          is too high and there's no lateral bracing."
Student: "What should I do?"
AI:      [Highlights problem areas in red]
         "Add diagonal braces here and here [shows positions]"
Student: [Adds braces]
AI:      "Much better! Now it's stable. Safety factor improved 
          from 1.2 to 3.5"
```

---

## 🔮 Advanced Features

### Real-Time Collaborative Cursors

```javascript
// Show where each participant is working
renderParticipantCursors() {
    participants.forEach(p => {
        ctx.fillStyle = p.type === 'ai' ? '#4CAF50' : '#2196F3';
        ctx.arc(p.cursor.x, p.cursor.y, 8, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillText(p.name, p.cursor.x + 15, p.cursor.y);
    });
}
```

### AI Focus Indicators

```javascript
// Show what AI is "looking at"
aiFocusedObjects.forEach(objectId => {
    // Green pulsing outline
    ctx.strokeStyle = '#4CAF50';
    ctx.setLineDash([5, 5]);
    ctx.strokeRect(...object.bounds);
    
    // Animate
    animatePulse(objectId);
});
```

### Suggestion Preview System

```javascript
// Before applying AI changes, show preview
showSuggestionPreview(patches, explanation) {
    // Render side-by-side
    renderCurrent(beforeCanvas);
    renderWithPatches(afterCanvas, patches);
    
    // Highlight differences
    highlightDifferences(beforeCanvas, afterCanvas);
    
    // Show UI
    modal.show({
        title: "AI Suggestion",
        explanation: explanation,
        actions: ['Accept', 'Reject', 'Explain Why']
    });
}
```

---

## 📊 Performance

**Payload Sizes:**

| Operation | Full Sync | JSON Patch | Reduction |
|-----------|-----------|------------|-----------|
| Move object | 125 KB | 85 bytes | 99.9% |
| Add object | 125 KB | 320 bytes | 99.7% |
| Change property | 125 KB | 65 bytes | 99.9% |

**Latency:**

| Action | Time |
|--------|------|
| User edit → Local render | 0ms (optimistic) |
| User edit → Server confirm | ~50ms |
| User edit → AI analysis start | ~100ms |
| AI analysis → Suggestion ready | ~2-5s |
| Suggestion accept → Applied | ~50ms |

---

## 🛠️ Customization

### Add Custom Object Types

```python
# In ai_vision_integration.py
def _render_custom_object_svg(self, object_id, obj_data):
    if obj_data['type'] == 'my-custom-part':
        return f'''
        <g id="{object_id}">
            <!-- Custom SVG rendering -->
        </g>
        '''
```

### Add Custom Voice Commands

```javascript
// In cad-interaction-handlers.js
const customPatterns = {
    rotate: /rotate (.*?) by (\d+) degrees/i,
    mirror: /mirror (.*?) (?:across|along) (x|y) axis/i
};
```

### Customize AI Prompts

```python
# In ai_vision_integration.py
def _build_custom_prompt(self, scene_graph, domain):
    if domain == 'furniture':
        return "You are a furniture designer specializing in..."
    elif domain == 'structural':
        return "You are a structural engineer focusing on..."
```

---

## 🧪 Testing

```bash
# Test operational transform
python -m pytest backend/test_operational_transform.py

# Test WebSocket server
python -m pytest backend/test_websocket_server.py

# Test AI vision
python backend/ai_vision_integration.py
```

---

## 📚 API Reference

### Scene Graph Schema

```typescript
interface SceneGraph {
    metadata: {
        version: number;
        created_at: string;
        dimensions_unit: 'mm' | 'inches';
    };
    
    objects: {
        [objectId: string]: CADObject;
    };
    
    groups: {
        [groupId: string]: {
            members: string[];
            locked: boolean;
        };
    };
    
    constraints: {
        [constraintId: string]: Constraint;
    };
    
    camera: {
        position: Vector3;
        target: Vector3;
        fov: number;
    };
    
    selections: {
        human: string[];
        ai: string[];
    };
}
```

### Patch Operations

```typescript
interface Patch {
    op: 'add' | 'remove' | 'replace' | 'move' | 'copy';
    path: string;  // JSON pointer: "/objects/beam_001/length"
    value?: any;
    from?: string;  // For move/copy
    actor: 'human' | 'ai' | 'system';
    timestamp: string;
    reason?: string;
    patch_id: string;
}
```

---

## 🤝 Contributing

**Architecture Decisions:**

1. **Why JSON Patch instead of custom format?**
   - Standard (RFC 6902)
   - Libraries available
   - Human-readable
   - Easy to validate

2. **Why WebSocket instead of HTTP polling?**
   - Real-time updates
   - Lower latency
   - Bi-directional
   - Better for cursors/presence

3. **Why SVG for AI vision instead of screenshots?**
   - Scalable/crisp at any resolution
   - Includes semantic metadata
   - Smaller file size
   - Easy to annotate

4. **Why user priority in conflicts?**
   - Respects human agency
   - AI can re-analyze and re-suggest
   - Less frustrating for users
   - Clearer mental model

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **JSON Patch (RFC 6902)** - Standard for expressing changes
- **Operational Transformation** - Conflict resolution algorithm
- **GPT-4 Vision** - AI visual understanding
- **FastAPI** - WebSocket server framework

---

## 🎨 SVG Technical Drawing Guidelines

When generating SVG schematics or blueprints in AI responses:

**Critical Spacing Rules:**
```
Title Block Height = (Font Size × Lines × 1.5) + 20px
Text Y-Position = Block Top + (Font × 1.2)  
Content Start = Block Bottom + 40-60px clearance
```

**Example:**
```svg
<!-- Title block 90px tall (28px + 14px fonts) -->
<rect x="20" y="20" width="1160" height="90"/>
<text x="600" y="55" font-size="28">Title</text>      <!-- 20 + (28×1.2) -->
<text x="600" y="85" font-size="14">Subtitle</text>   <!-- 55 + 30 -->

<!-- Content starts at y=160 (50px clearance) -->
<text x="150" y="160">Section Heading</text>
<rect x="80" y="180" width="140" height="180"/>
```

**Full reference:** `.github/SVG_CAD_GENERATION_RULES.md`

---

## 📞 Support

For questions or issues:
- Check `AI_HUMAN_CAD_COLLABORATION_ARCHITECTURE.md` for detailed architecture
- Review example code in `backend/` and `*.js` files
- Test with `cad-collaboration-demo.html`

---

**Built with ❤️ for the future of AI-human collaboration**
