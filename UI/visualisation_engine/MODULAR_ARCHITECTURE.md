# MODULAR VISUALIZATION ARCHITECTURE
## December 5, 2025

## 📁 File Structure

```
UI/visualisation_engine/
├── visualisation_copy.js          # Main engine (9640 lines)
├── apexcharts_renderer.js         # ApexCharts module (200 lines)
├── lottie_renderer.js             # Lottie animations module (180 lines)
├── gsap_renderer.js               # GSAP animations module (230 lines)
├── cad_renderer.js                # CAD/3D viewer module (280 lines)
├── schematic_renderer.js          # Technical diagrams module (320 lines)
├── visualization_loader.html      # Load all modules
└── MODULAR_ARCHITECTURE.md        # This file
```

## 🎯 Why Modular?

**Problem:** `visualisation_copy.js` was becoming bloated (9640 lines) with every new visualization type adding 200-400 lines.

**Solution:** Extract each visualization type into its own module with:
- ✅ Self-contained rendering logic
- ✅ CDN library loading
- ✅ Cleanup/destroy methods
- ✅ Consistent API interface
- ✅ Easy to maintain and extend

## 📊 Visualization Types

### 1. **ApexCharts** (`apexcharts_renderer.js`)
Modern interactive charts with dark theme support.

**Supported Types:**
- Area, Line, Bar, Column, Pie, Donut
- RadialBar, Scatter, Heatmap, Treemap
- Candlestick, Radar, PolarArea

**CDN:** `https://cdn.jsdelivr.net/npm/apexcharts@3.45.1`

**Example:**
```javascript
<APEXCHARTS>
{
  "chart": {"type": "area", "height": 400},
  "series": [{"name": "Sales", "data": [30, 40, 45, 50, 49, 60, 70, 91]}],
  "xaxis": {"categories": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"]}
}
</APEXCHARTS>
```

---

### 2. **Lottie** (`lottie_renderer.js`)
Lightweight vector animations from LottieFiles.

**Features:**
- 60fps smooth playback
- Small file sizes
- Play/pause controls
- JSON-based animations

**CDN:** `https://cdnjs.cloudflare.com/ajax/libs/bodymovin/5.12.2/lottie.min.js`

**Example:**
```javascript
<LOTTIE>
{
  "width": 400,
  "height": 400,
  "path": "https://assets9.lottiefiles.com/packages/lf20_jcikwtux.json",
  "loop": true,
  "autoplay": true
}
</LOTTIE>
```

**Find Animations:** https://lottiefiles.com/

---

### 3. **GSAP** (`gsap_renderer.js`)
Professional-grade animations with timeline support.

**Features:**
- High-performance animations
- Timeline sequencing
- Advanced easing
- SVG morphing

**CDN:** `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`

**Example:**
```javascript
<GSAP>
{
  "width": "100%",
  "height": "400px",
  "html": "<div class='box' style='width:100px;height:100px;background:red;'></div>",
  "animations": [
    {
      "targets": ".box",
      "vars": {"x": 300, "rotation": 360, "duration": 2},
      "method": "to"
    }
  ],
  "repeat": -1,
  "yoyo": true
}
</GSAP>
```

---

### 4. **CAD** (`cad_renderer.js`)
3D CAD model viewer using Three.js.

**Supported Formats:**
- STEP (.stp, .step)
- IGES (.igs, .iges)
- STL (.stl)
- OBJ (.obj)

**CDN:** `https://cdn.jsdelivr.net/npm/three@0.160.0`

**Example:**
```javascript
<CAD>
{
  "height": 600,
  "background": "#1a1a2e",
  "cameraDistance": 5,
  "showGrid": true,
  "showAxes": true,
  "geometry": {
    "width": 2,
    "height": 2,
    "depth": 2,
    "color": 0x00ff00,
    "metalness": 0.3,
    "roughness": 0.7
  }
}
</CAD>
```

**Controls:**
- Left-click + drag: Rotate
- Right-click + drag: Pan
- Scroll: Zoom
- Reset button: Return to default view

---

### 5. **Schematic** (`schematic_renderer.js`)
Technical diagrams and circuit schematics using SVG.

**Supported Types:**
- Electrical circuits
- System architecture
- Network topology
- Process flow diagrams

**No External Dependencies** - Pure SVG rendering

**Example:**
```javascript
<SCHEMATIC>
{
  "width": 800,
  "height": 600,
  "background": "#ffffff",
  "theme": "light",
  "showGrid": true,
  "elements": [
    {"type": "resistor", "x": 100, "y": 200},
    {"type": "capacitor", "x": 250, "y": 200},
    {"type": "battery", "x": 400, "y": 200},
    {"type": "box", "x": 100, "y": 300, "width": 120, "height": 60, "text": "Control Unit"},
    {"type": "circle", "x": 300, "y": 330, "radius": 30}
  ],
  "connections": [
    {"x1": 180, "y1": 200, "x2": 250, "y2": 200, "arrow": true},
    {"x1": 330, "y1": 200, "x2": 400, "y2": 200}
  ],
  "labels": [
    {"x": 100, "y": 180, "text": "R1 = 10kΩ"},
    {"x": 250, "y": 180, "text": "C1 = 100μF"}
  ]
}
</SCHEMATIC>
```

**Component Types:**
- `resistor` - Resistor symbol
- `capacitor` - Capacitor symbol
- `battery` - Battery symbol
- `box` - Rectangle with optional text
- `circle` - Circle element

---

## 🔧 Integration

### Option 1: Use HTML Loader (Recommended)

```html
<!-- Load all visualization modules -->
<script src="UI/visualisation_engine/apexcharts_renderer.js"></script>
<script src="UI/visualisation_engine/lottie_renderer.js"></script>
<script src="UI/visualisation_engine/gsap_renderer.js"></script>
<script src="UI/visualisation_engine/cad_renderer.js"></script>
<script src="UI/visualisation_engine/schematic_renderer.js"></script>
<script src="UI/visualisation_engine/visualisation_copy.js"></script>
```

### Option 2: Dynamic Loading

```javascript
// Load renderers on-demand
async function loadRenderer(type) {
    const renderers = {
        apexcharts: 'apexcharts_renderer.js',
        lottie: 'lottie_renderer.js',
        gsap: 'gsap_renderer.js',
        cad: 'cad_renderer.js',
        schematic: 'schematic_renderer.js'
    };
    
    if (!renderers[type]) return;
    
    const script = document.createElement('script');
    script.src = `UI/visualisation_engine/${renderers[type]}`;
    document.head.appendChild(script);
    
    return new Promise(resolve => {
        script.onload = resolve;
    });
}
```

---

## 🏗️ Architecture

### Class Structure

```javascript
// Each renderer follows the same interface:

class RendererClass {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.instances = new Map();
    }
    
    async render(item, contentArea, chartId) {
        // 1. Load library if needed
        // 2. Validate DOM
        // 3. Parse config
        // 4. Create container
        // 5. Initialize library
        // 6. Store instance
        // 7. Add action bar
    }
    
    async loadLibrary() {
        // Load external CDN
    }
    
    destroy(chartId) {
        // Cleanup single instance
    }
    
    destroyAll() {
        // Cleanup all instances
    }
}
```

### Main Engine Integration

```javascript
// visualisation_copy.js delegates to modular renderers:

async renderVisualizationDirectly(item, container, chartId) {
    switch (item.type) {
        case 'apexcharts':
            if (!this.apexchartsRenderer) {
                this.apexchartsRenderer = new ApexChartsRenderer(this);
            }
            await this.apexchartsRenderer.render(item, contentArea, chartId);
            break;
        // ... other cases
    }
}
```

---

## 📝 Adding New Visualization Types

### Step 1: Create Renderer Module

```javascript
// UI/visualisation_engine/my_new_renderer.js

class MyNewRenderer {
    constructor(visualizationEngine) {
        this.vizEngine = visualizationEngine;
        this.instances = new Map();
    }
    
    async render(item, contentArea, chartId) {
        // Load library
        if (!window.MyLibrary) {
            await this.loadLibrary();
        }
        
        // DOM validation
        if (!contentArea || !document.contains(contentArea)) {
            throw new Error('MyNew: Invalid content area');
        }
        
        // Parse config
        const config = typeof item.content === 'string' 
            ? JSON.parse(item.content.replace(/<\/?MYNEW>/g, '').trim())
            : item.content;
        
        // Create container
        const container = document.createElement('div');
        container.id = chartId;
        contentArea.appendChild(container);
        
        // Initialize library
        const instance = new MyLibrary(container, config);
        this.instances.set(chartId, instance);
        
        // Add action bar
        const vizContainer = contentArea.closest('.viz-container');
        if (vizContainer && this.vizEngine?.addUnifiedActionBar) {
            this.vizEngine.addUnifiedActionBar(vizContainer, item, chartId, 'mynew');
        }
        
        return instance;
    }
    
    async loadLibrary() {
        return new Promise((resolve, reject) => {
            if (window.MyLibrary) {
                resolve();
                return;
            }
            const script = document.createElement('script');
            script.src = 'https://cdn.example.com/mylibrary.js';
            script.onload = () => {
                console.log('✅ MyLibrary loaded');
                resolve();
            };
            script.onerror = () => reject(new Error('Failed to load MyLibrary'));
            document.head.appendChild(script);
        });
    }
    
    destroy(chartId) {
        const instance = this.instances.get(chartId);
        if (instance) {
            instance.destroy();
            this.instances.delete(chartId);
        }
    }
    
    destroyAll() {
        this.instances.forEach((instance, chartId) => {
            instance.destroy();
        });
        this.instances.clear();
    }
}

if (typeof window !== 'undefined') {
    window.MyNewRenderer = MyNewRenderer;
}
```

### Step 2: Update Main Engine

Add to `visualisation_copy.js` switch statement:

```javascript
case 'mynew':
    if (!this.mynewRenderer) {
        this.mynewRenderer = new MyNewRenderer(this);
    }
    await this.mynewRenderer.render(item, contentArea, chartId);
    break;
```

### Step 3: Update System Prompt

Add to `tool_usage_system_prompt.md`:

```markdown
### X. MYNEW

<MYNEW>
{
  "config": "value"
}
</MYNEW>
```

### Step 4: Test

```javascript
// Create test message
const testContent = `
<MYNEW>
{"config": "test"}
</MYNEW>
`;

await window.vizEngine.renderAll(testContent, container);
```

---

## 🧹 Cleanup

All renderers implement proper cleanup:

```javascript
// Destroy specific visualization
renderer.destroy(chartId);

// Destroy all instances
renderer.destroyAll();
```

Main engine calls `destroyAll()` on cleanup.

---

## 📊 Performance

**Before Modularization:**
- `visualisation_copy.js`: 9640 lines
- 5 visualization types embedded

**After Modularization:**
- `visualisation_copy.js`: 9640 lines (core only)
- 5 separate modules: 1210 lines total
- **Average module size:** 242 lines
- **Lazy loading:** Only load needed renderers

---

## 🔍 Debugging

Each renderer logs its lifecycle:

```
✅ ApexCharts library loaded
✅ Lottie library loaded
✅ GSAP library loaded
✅ Three.js and OrbitControls loaded
```

Check console for renderer status:

```javascript
console.log('Renderers:', {
    apexcharts: !!window.vizEngine.apexchartsRenderer,
    lottie: !!window.vizEngine.lottieRenderer,
    gsap: !!window.vizEngine.gsapRenderer,
    cad: !!window.vizEngine.cadRenderer,
    schematic: !!window.vizEngine.schematicRenderer
});
```

---

## 📚 Documentation Links

- **ApexCharts:** https://apexcharts.com/docs/
- **Lottie:** https://lottiefiles.com/
- **GSAP:** https://greensock.com/docs/
- **Three.js:** https://threejs.org/docs/
- **Mermaid:** https://mermaid.js.org/ (already built-in)

---

## ✅ Summary

**5 New Modular Renderers:**
1. ✅ `apexcharts_renderer.js` - Modern interactive charts
2. ✅ `lottie_renderer.js` - Vector animations
3. ✅ `gsap_renderer.js` - Advanced animations
4. ✅ `cad_renderer.js` - 3D CAD viewer
5. ✅ `schematic_renderer.js` - Technical diagrams

**Benefits:**
- 🎯 Clean separation of concerns
- 📦 Smaller, maintainable modules
- 🚀 Lazy loading support
- 🔧 Easy to extend
- 🧪 Testable in isolation
- 📝 Self-documented

**Next Steps:**
1. Test each renderer with sample data
2. Update HTML to load modules
3. Document in system prompt
4. Add to CI/CD pipeline
