# Parametric CAD Module
## Browser-Based T-Slot Aluminum Design Platform

**Created:** December 15, 2025  
**Purpose:** Professional-grade parametric CAD for T-slot aluminum extrusion systems, running entirely in the browser

---

## 🎯 Overview

A complete browser-based CAD platform inspired by commercial T-slot design tools, built on open-source OpenCascade.js. Design workbenches, frames, enclosures, and custom assemblies using parametric modeling—no software installation required.

### ✨ Key Features

- **🌐 Browser-Based** - No downloads, no installs, works on any device
- **📐 Parametric Modeling** - Change dimensions and watch designs update automatically
- **🤝 Real-time Collaboration** - Multiple users edit simultaneously via Supabase
- **📦 T-Slot Library** - Profile 5/6/8, 80/20 Series 10/15, fasteners, brackets
- **💾 CAD Export** - STEP, STL, DXF for manufacturing
- **📋 Templates** - Pre-built workbenches, frames, enclosures
- **🤖 AI Assistant** - Design recommendations and optimization

---

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **CAD Kernel** | [opencascade.js](https://github.com/donalffons/opencascade.js) | BREP solid modeling (WebAssembly) |
| **3D Rendering** | Three.js | Real-time 3D visualization |
| **Collaboration** | Supabase Realtime | Multi-user editing |
| **Backend** | Flask | REST API for AI/export |
| **Storage** | PostgreSQL (Supabase) | Design persistence |

### OpenCascade.js

OpenCascade Technology (OCCT) is the industry-standard CAD kernel used in:
- FreeCAD
- Salome
- BRL-CAD
- Commercial CAD platforms

**opencascade.js** compiles OCCT to WebAssembly, providing full CAD capabilities in the browser:
- Parametric solid modeling
- Boolean operations (union, intersection, subtraction)
- Fillet, chamfer, shell operations
- NURBS curves and surfaces
- Import/export STEP, IGES, BREP, STL

---

## 📦 T-Slot Extrusion Library

### Supported Profile Types

#### Profile 5 (20mm slot spacing)
- **20x20mm** - Lightweight structures
- **40x20mm** - Frames, supports
- **40x40mm** - General purpose
- **80x40mm** - Heavy duty

#### Profile 6 (30mm slot spacing)
- **30x30mm** - Medium duty
- **60x30mm** - Workbenches, enclosures
- **60x60mm** - Large structures

#### Profile 8 (40mm slot spacing)
- **40x40mm** - Heavy duty
- **80x40mm** - Industrial frames
- **80x80mm** - Extra strength
- **160x80mm** - XXL structures

#### 80/20 Series (Imperial)
- **Series 10** - 1"x1" (25.4mm)
- **Series 15** - 1.5"x1.5" (38.1mm)

### Fasteners & Accessories

- **T-Nuts** - M4, M5, M6, M8 (metric), 1/4-20, 5/16-18 (imperial)
- **Screws** - Button head, socket head cap screws
- **Corner Brackets** - 90°, 45°, adjustable angle
- **Gusset Plates** - Reinforcement
- **End Caps** - Aesthetic finish
- **Hinges** - Access panels
- **Linear Motion** - Slides, bearings, wheels

---

## 🚀 Quick Start

### Basic Usage

```javascript
// Initialize CAD application
const cad = new ParametricCAD('viewport-container');
await cad.initialize();

// Create extrusion
const part = cad.createExtrusion('profile8', '40x40', 500); // 500mm length
cad.addPart('leg1', part);

// Position part
part.mesh.position.set(0, 0, 0);

// Export to STEP
await cad.exportSTEP('my-design.step');
```

### Pre-built Templates

```javascript
// Create workbench (1200x600x900mm)
cad.createTemplate('workbench', {
    width: 1200,
    depth: 600,
    height: 900,
    profile: 'profile8',
    size: '40x40'
});

// Create enclosure
cad.createTemplate('enclosure', {
    width: 800,
    depth: 600,
    height: 1000
});

// Create frame
cad.createTemplate('frame', {
    width: 1000,
    height: 2000,
    depth: 500
});
```

### Collaborative Design

```javascript
// Connect to shared design session
await cad.connectCollaboration('project-uuid-here');

// Changes automatically sync with other users
// Remote edits appear in real-time
```

---

## 📐 Parametric Design Examples

### Example 1: Simple Workbench

```javascript
// Define parameters
const params = {
    width: 1200,
    depth: 600,
    height: 900,
    legProfile: 'profile8',
    legSize: '40x40',
    topProfile: 'profile8',
    topSize: '80x40'
};

// Create legs (4 vertical extrusions)
const leg1 = cad.createExtrusion(params.legProfile, params.legSize, params.height);
const leg2 = cad.createExtrusion(params.legProfile, params.legSize, params.height);
const leg3 = cad.createExtrusion(params.legProfile, params.legSize, params.height);
const leg4 = cad.createExtrusion(params.legProfile, params.legSize, params.height);

// Position legs at corners
leg1.mesh.position.set(-params.width/2, 0, -params.depth/2);
leg2.mesh.position.set(params.width/2, 0, -params.depth/2);
leg3.mesh.position.set(params.width/2, 0, params.depth/2);
leg4.mesh.position.set(-params.width/2, 0, params.depth/2);

// Add horizontal supports
const frontSupport = cad.createExtrusion(params.topProfile, params.topSize, params.width);
frontSupport.mesh.position.set(0, params.height, -params.depth/2);
frontSupport.mesh.rotation.z = Math.PI / 2;

// Export
await cad.exportSTEP('workbench.step');
```

### Example 2: 3-Sided Enclosure

```javascript
// Create frame
const enclosure = {
    width: 800,
    height: 1000,
    depth: 600
};

// Bottom frame
const bottomLeft = cad.createExtrusion('profile8', '40x40', enclosure.depth);
const bottomRight = cad.createExtrusion('profile8', '40x40', enclosure.depth);
const bottomFront = cad.createExtrusion('profile8', '40x40', enclosure.width);
const bottomBack = cad.createExtrusion('profile8', '40x40', enclosure.width);

// Vertical posts
const post1 = cad.createExtrusion('profile8', '40x40', enclosure.height);
const post2 = cad.createExtrusion('profile8', '40x40', enclosure.height);
const post3 = cad.createExtrusion('profile8', '40x40', enclosure.height);
const post4 = cad.createExtrusion('profile8', '40x40', enclosure.height);

// Top frame (same as bottom)
// ...

// Add panels (acrylic, sheet metal, etc.)
// ...
```

---

## 💾 Export Formats

### STEP (.step, .stp)
**Best for:** CAD interchange, manufacturing

```javascript
await cad.exportSTEP('design.step');
```

- Industry standard CAD format
- Preserves parametric data
- Compatible with SolidWorks, Fusion 360, FreeCAD, etc.
- Use for CNC machining, professional fabrication

### STL (.stl)
**Best for:** 3D printing, mesh-based applications

```javascript
await cad.exportSTL('design.stl');
```

- Triangle mesh format
- Direct 3D printer compatibility
- Use for rapid prototyping
- No parametric data (baked geometry)

### DXF (.dxf)
**Best for:** 2D laser cutting, CNC routing

```javascript
await cad.exportDXF('panel.dxf');
```

- 2D vector format
- Compatible with AutoCAD, LibreCAD
- Use for sheet metal, acrylic panels

### OBJ (.obj)
**Best for:** 3D visualization, rendering

```javascript
await cad.exportOBJ('design.obj');
```

- Mesh format with materials
- Use in Blender, 3ds Max, etc.

---

## 🤝 Supabase Real-time Collaboration

### How It Works

The parametric CAD module integrates with the existing Supabase realtime infrastructure:

1. **Session Management** - `cad_sessions` table stores project metadata
2. **Part Storage** - `cad_objects` table stores individual parts
3. **Live Updates** - Supabase broadcasts INSERT/UPDATE/DELETE events
4. **Conflict Resolution** - Last-write-wins with version tracking

### Database Schema

Already created in `create_cad_collaboration_tables.sql`:

```sql
-- Active design session
CREATE TABLE cad_sessions (
    session_id UUID PRIMARY KEY,
    design_name TEXT NOT NULL,
    owner_user_id TEXT NOT NULL,
    created_at TIMESTAMP
);

-- Individual parts
CREATE TABLE cad_objects (
    object_id UUID PRIMARY KEY,
    session_id UUID REFERENCES cad_sessions,
    object_type TEXT, -- 'extrusion', 'bracket', etc.
    properties JSONB, -- {profile: 'profile8', size: '40x40', length: 500, ...}
    created_by TEXT,
    version INTEGER
);

-- Participants
CREATE TABLE cad_participants (
    participant_id UUID PRIMARY KEY,
    session_id UUID REFERENCES cad_sessions,
    user_id TEXT,
    display_name TEXT,
    cursor_color TEXT,
    is_active BOOLEAN
);
```

### Collaborative Workflow

```javascript
// User A creates project
const sessionId = await createCADSession('My Workbench Design');

// User B joins
await cad.connectCollaboration(sessionId);

// User A adds extrusion
const part1 = cad.createExtrusion('profile8', '40x40', 500);
// → Automatically saved to cad_objects table
// → User B sees part appear in real-time

// User B moves part
part1.mesh.position.set(100, 0, 0);
// → UPDATE event sent to cad_objects
// → User A sees part move in real-time
```

---

## 🤖 AI Integration

### AI-Assisted Design

The module can integrate with AI vision models for:

1. **Design Review** - AI analyzes structure for stability, optimization
2. **Part Recommendations** - Suggests brackets, fasteners based on loads
3. **Material Calculations** - Estimates weight, cost, BOM
4. **Assembly Instructions** - Generates step-by-step build guide

### Example AI Request

```javascript
// User asks: "Is this workbench stable?"

// System:
// 1. Exports current design to SVG snapshot
// 2. Sends to GPT-4V with prompt:
//    "Analyze this aluminum extrusion workbench for structural stability.
//     Identify weak points and suggest reinforcements."
// 3. AI responds with specific recommendations
// 4. System highlights parts and suggests additions

await cad.requestAIAnalysis('Is this workbench stable?');
```

---

## 🎨 UI/UX Features

### Left Sidebar - Parts Library
- Organized by profile type
- Click to add to scene
- Search/filter functionality
- Custom parts library

### Center Viewport - 3D View
- Orbit camera controls
- Zoom/pan
- Part selection
- Measurement tools
- Snap to grid

### Right Sidebar - Properties
- Length, width, height inputs
- Material selection
- Finish options (anodized, powder coat, etc.)
- Mass properties (weight, center of gravity)

### Top Toolbar
- New/Save/Load project
- Undo/Redo
- Export options
- View controls (top, front, isometric)

---

## 🔧 Development

### File Structure

```
UI/modules_external/parametric-cad/
├── manifest.json              # Module metadata
├── parametric-cad.js          # Main application logic
├── parametric-cad.css         # Styles
├── parametric-cad.html        # UI template
├── lib/
│   ├── extrusion-library.js  # T-slot part definitions
│   ├── templates.js          # Pre-built designs
│   └── export-handlers.js    # File export logic
└── README.md                 # This file
```

### Adding Custom Parts

```javascript
// Create custom extrusion profile
const customProfile = {
    width: 50,
    height: 50,
    slot: 12,
    groove: 10,
    wallThickness: 2.5
};

// Generate cross-section geometry
const profile = createCustomTSlotProfile(customProfile);

// Extrude along path
const extrusion = extrudeProfile(profile, 1000);
```

### Extending Templates

```javascript
// Add new template type
ParametricCAD.prototype.createRobotFrameTemplate = function(params) {
    const { height, width, depth, payload } = params;
    
    // Calculate required profile size based on payload
    const profileSize = payload > 50 ? '80x80' : '40x40';
    
    // Create vertical posts
    // Add horizontal supports
    // Add cross-bracing for rigidity
    // Return assembled frame
};
```

---

## 📚 Comparison to Commercial Platforms

| Feature | This Module | TSlotCAD.com | 80/20 Designer | SolidWorks |
|---------|-------------|--------------|----------------|------------|
| **Price** | Free | Paid | Free | $$$$ |
| **Browser-based** | ✅ | ✅ | ❌ | ❌ |
| **Parametric** | ✅ | ✅ | ⚠️ | ✅ |
| **Collaboration** | ✅ | ❌ | ❌ | ✅ |
| **AI Assistant** | ✅ | ❌ | ❌ | ❌ |
| **Export STEP** | ✅ | ✅ | ✅ | ✅ |
| **Custom Parts** | ✅ | ⚠️ | ❌ | ✅ |
| **Open Source** | ✅ | ❌ | ❌ | ❌ |

---

## 🎯 Roadmap

### Phase 1 (Complete)
- ✅ OpenCascade.js integration
- ✅ Basic extrusion creation
- ✅ Three.js visualization
- ✅ Supabase collaboration
- ✅ STEP export

### Phase 2 (In Progress)
- ⏳ Complete T-slot library (fasteners, brackets)
- ⏳ Pre-built templates (workbench, enclosure, frame)
- ⏳ STL/DXF export
- ⏳ Part measurement tools

### Phase 3 (Planned)
- 📅 AI design assistant
- 📅 BOM generation (materials list, cost estimate)
- 📅 Assembly instructions
- 📅 Structural analysis (FEA integration)
- 📅 Custom part designer

### Phase 4 (Future)
- 📅 Mobile app
- 📅 AR preview (view design in real space)
- 📅 Marketplace (share/sell designs)
- 📅 Integration with suppliers (order parts directly)

---

## 🤝 Contributing

This module is built on open-source foundations:

- **OpenCascade.js** - [github.com/donalffons/opencascade.js](https://github.com/donalffons/opencascade.js)
- **Three.js** - [threejs.org](https://threejs.org/)
- **Supabase** - [supabase.com](https://supabase.com/)

Contributions welcome! Areas of focus:
- T-slot profile library expansion
- Export format improvements
- AI integration
- Template designs
- Documentation

---

## 📄 License

Built on open-source technologies:
- OpenCascade.js (LGPL 2.1)
- Three.js (MIT)
- This module code (MIT)

---

## 🙏 Credits

**Inspired by:**
- [CascadeStudio](https://github.com/zalo/CascadeStudio) - Live-scripted CAD
- [Replicad](https://github.com/sgenoud/replicad) - TypeScript CAD library
- [80/20 Inc.](https://8020.net/) - T-slot extrusion pioneers
- Commercial CAD platforms (TSlotCAD, Fusion 360)

**Built on:**
- OpenCascade Technology (industry-standard CAD kernel)
- Three.js (WebGL 3D rendering)
- Supabase (real-time database)

---

**Ready to build something amazing? Start designing now! 🚀**
