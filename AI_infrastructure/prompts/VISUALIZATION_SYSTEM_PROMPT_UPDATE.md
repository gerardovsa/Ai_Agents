# Updated Visualization System Prompt
**Date:** December 5, 2025  
**Purpose:** Add SVG/CAD/LaTeX visualization types to AI agent system prompt

---

## REPLACEMENT SECTION FOR tool_usage_system_prompt.md

**Location:** Lines 1117-1177 (Visual Presentation and Visual Tools section)

**Replace entire section with:**

```markdown
—

### Visual Presentation and Visual Tools

EMOJI RULE: 
DO NOT INCLUDE EMOJIS IN HEADER TEXT = causes rendering errors

Graphs/Charts:
The UI Text message bubbles can render visualizations in the chat
You can use visualizations to show graphs, charts and diagrams this enhances your response
You need to wrap json, mermaid code, SVG, or LaTeX in the delimiters below

#### Charts & Graphs (Use `<PLOTLY>...</PLOTLY>`)
```
When to use:
- Showing trends or comparisons
- Data analysis results
- Performance metrics
- Statistical visualizations
- Financial charts

Built-in capabilities:
- Export: PNG, SVG, JSON, CSV formats
- Fullscreen: Interactive fullscreen view
- Zoom/Pan: Built-in Plotly interactivity
- Responsive: Auto-scales to container
```

**Example:**
```xml
<PLOTLY>
{
  "data": [{"x": [1,2,3], "y": [2,4,6], "type": "bar"}],
  "layout": {"title": "Sample Chart"}
}
</PLOTLY>
```

#### Flowcharts & Diagrams (Use `<MERMAID>...</MERMAID>`)
```
When to use:
- Explaining processes
- System architecture
- Decision trees
- Project timelines (Gantt)
- Sequence diagrams
- Class diagrams (UML)

Built-in capabilities:
- Export: PNG, SVG formats
- Fullscreen: Dedicated fullscreen viewer with zoom/pan
- Themes: Light/dark mode support
- Responsive: Auto-scales to container
```

**Example:**
```xml
<MERMAID>
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
</MERMAID>
```

#### Technical Drawings & CAD (Use `<SVG>`, `<CAD>`, `<SCHEMATIC>`, `<BLUEPRINT>`)
```
When to use:
- Engineering CAD drawings
- Electrical circuit schematics
- Architectural blueprints
- Technical illustrations
- Mechanical diagrams

Built-in capabilities:
- Export: SVG format (reusable in AutoCAD, Illustrator)
- Download: Save SVG file locally
- Copy: Copy SVG code to clipboard
- Fullscreen: Expandable fullscreen view
- Zoom: 150%, 200%, 300% zoom levels
- Responsive: viewBox-based scaling
- Themes: Type-specific professional styling
  * CAD: Gradient blue engineering style
  * SCHEMATIC: Yellow notepad style
  * BLUEPRINT: Dark blue blueprint style
  * MOLECULE: Light blue scientific style
```

**Examples:**
```xml
<CAD>
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <title>Flanged Coupling Assembly</title>
  <desc>Mechanical coupling with dimensions</desc>
  <rect x="50" y="100" width="300" height="100" fill="#e0e0e0" stroke="#333" stroke-width="2"/>
  <circle cx="100" cy="150" r="20" fill="none" stroke="#333" stroke-width="2"/>
  <text x="200" y="50" text-anchor="middle" font-size="16">300mm</text>
</svg>
</CAD>

<SCHEMATIC>
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <title>Arduino Motor Controller</title>
  <desc>L298N H-bridge circuit with Arduino connections</desc>
  <!-- Circuit schematic elements -->
  <line x1="50" y1="150" x2="150" y2="150" stroke="#000" stroke-width="2"/>
  <rect x="150" y="130" width="100" height="40" fill="none" stroke="#000" stroke-width="2"/>
  <text x="200" y="155" text-anchor="middle">L298N</text>
</svg>
</SCHEMATIC>

<BLUEPRINT>
<svg viewBox="0 0 600 400" xmlns="http://www.w3.org/2000/svg">
  <title>Office Floor Plan</title>
  <desc>2,500 sq ft open office layout</desc>
  <!-- Architectural blueprint elements -->
  <rect x="50" y="50" width="500" height="300" fill="none" stroke="#7FDBFF" stroke-width="3"/>
  <text x="300" y="200" text-anchor="middle" fill="#7FDBFF" font-size="24">OPEN OFFICE</text>
  <text x="300" y="230" text-anchor="middle" fill="#7FDBFF" font-size="16">2,500 sq ft</text>
</svg>
</BLUEPRINT>
```

#### Scientific & Mathematical (Use `<MOLECULE>`, `<LATEX>`)
```
When to use:
- Chemical structures and molecular diagrams
- Mathematical equations and formulas
- Scientific notation
- Academic/research content

Built-in capabilities:
- LATEX: KaTeX rendering (instant math typesetting)
- MOLECULE: SVG-based chemical structures
- Export: Download SVG (molecules)
- Copy: Copy code/structure
- Responsive: Auto-scaling
- Professional styling: Academic paper appearance
```

**Examples:**
```xml
<MOLECULE>
<svg viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
  <title>Caffeine Molecule</title>
  <desc>C8H10N4O2 - 1,3,7-trimethylxanthine</desc>
  <!-- Molecular structure with atoms and bonds -->
  <circle cx="150" cy="100" r="15" fill="#4682b4" stroke="#333" stroke-width="2"/>
  <text x="150" y="105" text-anchor="middle" fill="white" font-size="12">C</text>
  <line x1="165" y1="100" x2="200" y2="100" stroke="#333" stroke-width="2"/>
  <circle cx="200" cy="100" r="15" fill="#4682b4" stroke="#333" stroke-width="2"/>
  <text x="200" y="105" text-anchor="middle" fill="white" font-size="12">N</text>
</svg>
</MOLECULE>

<LATEX>
E = mc^2
</LATEX>

<LATEX>
\int_{a}^{b} f(x) \, dx = F(b) - F(a)
</LATEX>

<LATEX>
\frac{\partial u}{\partial t} = \alpha \nabla^2 u
</LATEX>
```

#### Generic SVG (Use `<SVG>...</SVG>`)
```
When to use:
- Custom vector graphics
- Icons and illustrations
- Diagrams not fitting other categories
- Infographics

Built-in capabilities:
- Same as CAD/SCHEMATIC/BLUEPRINT
- Clean white/dark background
- All export/download features
```

**Example:**
```xml
<SVG>
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <title>Custom Icon</title>
  <circle cx="100" cy="100" r="80" fill="#4CAF50"/>
  <text x="100" y="110" text-anchor="middle" fill="white" font-size="40">✓</text>
</svg>
</SVG>
```

#### Tables (Use `<TABLE>...</TABLE>`)
```
When to use:
- Large datasets
- Sortable/filterable data
- Structured information
- Comparison matrices
```

—

### CRITICAL SVG/CAD REQUIREMENTS:

**1. ALWAYS include viewBox attribute:**
```xml
<!-- ✅ CORRECT -->
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">

<!-- ❌ WRONG - No viewBox -->
<svg width="400" height="300">
```

**2. ALWAYS include <title> and <desc> for accessibility:**
```xml
<svg viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <title>Brief title of diagram</title>
  <desc>Detailed description of what the diagram shows</desc>
  <!-- diagram content -->
</svg>
```

**3. NEVER include JavaScript or external resources:**
```xml
<!-- ❌ FORBIDDEN -->
<script>alert('bad')</script>
<foreignObject>...</foreignObject>
<link href="external.css"/>

<!-- ✅ ALLOWED -->
<rect>, <circle>, <line>, <path>, <text>, <g>
```

**4. Use appropriate delimiters:**
- **<CAD>** for mechanical/engineering drawings
- **<SCHEMATIC>** for electrical/electronic circuits
- **<BLUEPRINT>** for architectural plans
- **<MOLECULE>** for chemical structures
- **<LATEX>** for mathematical equations
- **<SVG>** for generic vector graphics

**5. Coordinate system best practices:**
```xml
<!-- Small diagram -->
<svg viewBox="0 0 400 300">

<!-- Large detailed diagram -->
<svg viewBox="0 0 1000 800">

<!-- Portrait orientation -->
<svg viewBox="0 0 300 400">
```

—

### When to Use Each Visualization Type:

**Use PLOTLY when:**
- ✅ Showing data trends, comparisons, metrics
- ✅ Interactive exploration needed (zoom, hover)
- ✅ Statistical or financial visualizations
- ✅ Need export to PNG, SVG, JSON, CSV

**Use MERMAID when:**
- ✅ Explaining processes or workflows
- ✅ System architecture diagrams
- ✅ Decision trees or flowcharts
- ✅ Project timelines (Gantt charts)
- ✅ Sequence diagrams or UML

**Use CAD/SCHEMATIC/BLUEPRINT when:**
- ✅ Technical engineering drawings needed
- ✅ Showing dimensions and measurements
- ✅ Electrical circuit diagrams
- ✅ Architectural floor plans
- ✅ Mechanical assembly drawings

**Use MOLECULE when:**
- ✅ Chemical structures and compounds
- ✅ Molecular diagrams
- ✅ Biochemistry visualizations

**Use LATEX when:**
- ✅ Mathematical equations or formulas
- ✅ Scientific notation
- ✅ Academic/research content
- ✅ Complex mathematical expressions

**Use SVG when:**
- ✅ Custom vector graphics needed
- ✅ Logos, icons, illustrations
- ✅ Infographics
- ✅ Diagrams not fitting other categories

—

### Workflow Example (Multi-Visualization):

**Scenario:** User asks to analyze sales data and explain process

```
1. Execute tools to gather sales data
2. Create PLOTLY chart showing trends
3. Create MERMAID flowchart explaining sales process
4. Provide text analysis alongside visuals
5. User sees both chart AND process diagram inline
```

**Response structure:**
```markdown
Here's your sales analysis:

<PLOTLY>
{"data": [...], "layout": {...}}
</PLOTLY>

The sales process follows this workflow:

<MERMAID>
graph TD
    A[Lead Generation] --> B[Qualification]
    B --> C[Proposal]
    C --> D[Negotiation]
    D --> E[Close]
</MERMAID>

Key insights:
- Q4 sales up 23%
- Process bottleneck at qualification stage
- Recommendation: Increase qualification resources
```

—

### UI Capabilities Summary:

All visualizations support:
- ✅ **Light/Dark Mode** - Automatic theme adaptation
- ✅ **Responsive** - Auto-scales to screen size
- ✅ **Mobile-Friendly** - Touch-optimized controls
- ✅ **Print-Ready** - Proper print styling
- ✅ **Accessibility** - ARIA labels, keyboard navigation

Action buttons (shown on hover):
- 📥 **Export** - Download visualization
- 📋 **Copy** - Copy source code
- ⛶ **Fullscreen** - Expand to fullscreen view
- 🔍 **Zoom** - Zoom in/out (SVG types)
- 🔄 **Refresh** - Re-render (Plotly/Mermaid)

No external tools or manual steps needed - everything renders inline!

—
```

---

## INTEGRATION NOTES

### Files to Update:

**1. System Prompt File:**
- **File:** `AI_infrastructure/prompts/tool_usage_system_prompt.md`
- **Section:** Lines 1117-1177
- **Action:** Replace entire "Visual Presentation and Visual Tools" section

**2. Agent Routes (Runtime Injection):**
- **File:** `AI_infrastructure/routes/agent_routes_v4.py`
- **Location:** Line ~1262 (`system_prompt_continued`)
- **Action:** Add visualization section reference

---

## LIBRARIES USED (No Additional Install Needed)

### Existing Libraries (Already Loaded):
1. **Plotly.js** - Interactive charts
   - Built-in: `Plotly.downloadImage()`, `Plotly.toImage()`
   - Export formats: PNG, SVG
   - No additional packages needed

2. **Mermaid.js** - Flowcharts/diagrams
   - Built-in: `mermaid.render()`
   - Export: SVG extraction from DOM
   - PNG via html2canvas fallback

3. **html2canvas** - DOM to canvas conversion
   - Used as fallback for PNG exports
   - Already included in project

### NEW: Native Browser APIs (No Install):
4. **DOMParser** - SVG parsing/validation
   - Built-in browser API
   - Used for SVG sanitization

5. **KaTeX** - LaTeX math rendering
   - Loaded dynamically on first use (CDN)
   - CSS: `katex@0.16.9/dist/katex.min.css`
   - JS: `katex@0.16.9/dist/katex.min.js`
   - No npm install needed

6. **XMLSerializer** - SVG export
   - Built-in browser API
   - Used for SVG download

---

## ACTION BUTTON INTEGRATION

### Existing Action Bar System:
Located in `visualisation_copy.js` (lines 980-1100)

**Structure:**
```javascript
.viz-action-bar {
    position: absolute;
    top: 10px;
    opacity: 0.3; // Shows on hover
    // Contains action buttons
}

.viz-action-btn {
    width: 28px;
    height: 28px;
    background: #2a2a2a;  // Dark grey
    color: white;
}

.viz-action-btn:hover {
    background: #FF7A00;  // Brand orange
}
```

**Buttons:**
1. **Export** - `data-action="export"` → Export menu (PNG, SVG, JSON, CSV, PDF)
2. **Copy** - `data-action="copy"` → Copy to clipboard
3. **Share** - `data-action="share"` → Native share or download
4. **Fullscreen** - `data-action="view"` → Fullscreen viewer
5. **Analysis** - `data-action="analysis"` → Data analysis (Plotly only)
6. **Plotly** - `data-action="plotly"` → Plotly-specific actions

### SVG/CAD Action Buttons (New):
Same visual style, integrated with existing system:

```javascript
// Control bar structure (from SURGICAL_PATCH.js)
createSVGControls(svgContent, type) {
    const controls = document.createElement('div');
    controls.className = 'svg-control-bar'; // ✅ Matches existing .viz-action-bar style
    
    // Buttons use same .viz-action-btn class
    const downloadBtn = this.createControlButton('📥 Download', ...);
    const copyBtn = this.createControlButton('📋 Copy', ...);
    const zoomBtn = this.createControlButton('🔍 Zoom', ...);
    const fullscreenBtn = this.createControlButton('⛶ Fullscreen', ...);
}
```

**Result:** SVG/CAD visualizations have consistent UI with Plotly/Mermaid.

---

## FULLSCREEN IMPLEMENTATIONS

### Mermaid Fullscreen (Existing):
```javascript
// visualisation_copy.js line ~5980
openMermaidFullscreen(container, content, chartId) {
    // Creates overlay with:
    // - Dark backdrop
    // - Centered diagram
    // - Zoom/pan controls
    // - Close button
    // - Export buttons
}
```

**Features:**
- Dedicated fullscreen viewer
- Zoom in/out buttons
- Pan/drag functionality
- ESC key to close
- Export from fullscreen

### SVG/CAD Fullscreen (New):
```javascript
// From visualization_enhancements.css
.svg-visualization-wrapper.fullscreen {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    width: 100vw; height: 100vh;
    z-index: 9999;
    background: rgba(0, 0, 0, 0.95);
}

// JavaScript toggle
toggleFullscreen(wrapper) {
    wrapper.classList.toggle('fullscreen');
    // Control bar repositions to top-right
    // SVG scales to 95vw x 90vh
}
```

**Features:**
- Same dark backdrop as Mermaid
- Consistent ESC key behavior
- Control bar in top-right corner
- SVG auto-scales to viewport
- Maintains aspect ratio

---

## THEME INTEGRATION

### Light/Dark Mode Detection:
```css
/* From visualization_enhancements.css */
body.dark-mode,
html[data-theme="dark"] {
    --svg-bg-light: var(--svg-bg-dark);
    --svg-border-light: var(--svg-border-dark);
    /* Auto-switches all SVG colors */
}
```

**Auto-adapts:**
- Background colors
- Border colors
- Text colors
- Shadow intensities
- Control button styling

### Type-Specific Themes:
```css
.cad-diagram {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    /* Dark mode: linear-gradient(135deg, #2c3e50 0%, #34495e 100%) */
}

.blueprint-diagram {
    background: #001f3f;  /* Always dark blue */
    color: #7FDBFF;       /* Blueprint cyan */
}
```

---

## AI-PROOF DEFAULTS

### Automatic Fixes for AI Mistakes:

**1. Missing viewBox:**
```css
svg:not([viewBox]) {
    width: 100% !important;
    height: auto !important;
}
```

**2. Absolute dimensions without viewBox:**
```css
svg[width][height]:not([viewBox]) {
    max-width: 100% !important;
    height: auto !important;
}
```

**3. Missing margins:**
```css
.svg-visualization-wrapper:not([style*="margin"]) {
    margin: 2rem auto !important;
}
```

**4. Broken coordinate systems:**
```javascript
enhanceSVGElement(svgElement, type) {
    if (!svgElement.hasAttribute('viewBox')) {
        const width = svgElement.getAttribute('width') || '800';
        const height = svgElement.getAttribute('height') || '600';
        svgElement.setAttribute('viewBox', `0 0 ${width} ${height}`);
    }
}
```

---

## SUMMARY

✅ **6 new visualization types** added (SVG, CAD, SCHEMATIC, BLUEPRINT, MOLECULE, LATEX)  
✅ **Zero breaking changes** - Plotly/Mermaid work exactly as before  
✅ **Consistent UI** - Same action buttons, fullscreen, themes  
✅ **No new libraries** - Uses DOMParser, KaTeX CDN, XMLSerializer  
✅ **AI-proof** - Auto-fixes common mistakes  
✅ **Professional** - Type-specific styling, dark mode support  
✅ **Accessible** - ARIA labels, keyboard navigation, screen reader support  

**Next step:** Replace system prompt section in `tool_usage_system_prompt.md`
